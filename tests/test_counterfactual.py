import pytest
from qfault.lab import CustomCircuit


def request(kind='pauli_expectations', **kwargs):
    from qfault.counterfactual import RecoveryRequest
    contract = {'kind':kind, 'observables':[{'pauli':'IZ','expected':1,'tolerance':.15}]}
    if kind == 'measurement_distribution':
        contract = {'kind':kind,'expected_probabilities':{'00':1},'tolerance':.15}
    if kind == 'target_state':
        contract = {'kind':kind,'amplitudes':[[1.,0.],[0.,0.],[0.,0.],[0.,0.]],'fidelity_tolerance':.2}
    body = dict(circuit={'schema_version':1,'name':'bit inversion','n_qubits':2,
        'input':{'kind':'computational_basis','bitstring':'00'},'gates':[{'name':'x','qubits':[0]}]},
        contract=contract, backend='aer', screen_shots=2048, verification_shots=4096,
        max_candidates=8, max_shots=150000)
    return RecoveryRequest.model_validate({**body, **kwargs})


def test_generator_is_deterministic_bounded_and_preserves_original():
    from qfault.interventions import generate, EditRestrictions
    c = request().circuit
    before = c.model_dump()
    a = generate(c, EditRestrictions(), 8)
    assert a == generate(c, EditRestrictions(), 8)
    assert len(a['candidates']) == 8
    ids = [x['circuit_id'] for x in a['candidates']]
    assert len(ids) == len(set(ids)) and c.circuit_id not in ids
    for x in a['candidates']:
        assert CustomCircuit.model_validate(x['circuit']).circuit_id == x['circuit_id']
    assert c.model_dump() == before


def test_duplicate_intervention_circuit_preserves_equivalent_edit_locus():
    from qfault.interventions import generate,EditRestrictions
    c=CustomCircuit.model_validate({'schema_version':1,'name':'same operation twice','n_qubits':2,
        'input':{'kind':'computational_basis','bitstring':'00'},
        'gates':[{'name':'x','qubits':[0]},{'name':'x','qubits':[0]}]})
    generated=generate(c,EditRestrictions(operators=('remove',)),8)
    p=next(x for x in generated['candidates'] if x['edit']['operator']=='remove')
    assert p['edit']['index']==0
    assert any(e['index']==1 for e in p['equivalent_edits'])
    assert any(x['reason']=='DUPLICATE_OR_ORIGINAL' and x.get('equivalent_circuit_id')==p['candidate_id'] for x in generated['excluded'])


@pytest.mark.parametrize('kind',['pauli_expectations','measurement_distribution','target_state'])
def test_real_measured_repair_and_fresh_samples(kind, monkeypatch):
    from qfault.counterfactual import recover
    import qfault.lab as lab
    import qfault.quantum as quantum
    def forbidden(*a, **k): raise AssertionError('privileged state accessed')
    monkeypatch.setattr(lab, 'exact_expectations', forbidden)
    monkeypatch.setattr(quantum, 'ideal_state', forbidden)
    # Aer itself simulates a state; prohibit the analysis helper, not the backend's internals.
    monkeypatch.setattr(quantum, 'noisy_density', forbidden)
    r = recover(request(kind))
    assert r['verification']['status'] == 'VERIFIED_UNDER_DECLARED_CONTRACT'
    assert r['verification']['improvement_lower'] > 0
    assert r['localization']['causal_origin'] == 'NOT_IDENTIFIED'
    assert r['privileged_operations'] == []
    assert r['cost']['shots'] == sum(x['executed_shots'] for x in r['executions'])
    assert len({x['seed'] for x in r['executions']}) == len(r['executions'])
    assert r['selection']['frozen_before_verification']


def test_clean_noise_and_budget_abstain():
    from qfault.counterfactual import recover
    base = request()
    clean = base.circuit.model_dump(); clean['gates'] = []
    assert recover(request(circuit=clean))['status'] == 'NO_REPAIR_NEEDED'
    noise = recover(request(circuit=clean,environment={'readout':.35}))
    assert noise['status'] == 'NOISE_CONTROL_ABSTENTION'
    assert noise['selected_candidate'] is None
    low = recover(request(max_shots=128))
    assert low['status'] == 'INSUFFICIENT_BUDGET'
    assert low['cost']['shots'] == 0


def test_export_and_api(tmp_path):
    from fastapi.testclient import TestClient
    from qfault.api import create_app
    from qfault.storage import verify_export
    client = TestClient(create_app(tmp_path))
    response = client.post('/api/lab/recoveries',json=request().model_dump(mode='json'))
    assert response.status_code == 201, response.text
    r = response.json(); eid = r['experiment_id']
    assert client.get('/api/experiments/'+eid).json()['selection'] == r['selection']
    assert verify_export(client.get('/api/experiments/'+eid+'/report').json())['valid']
    replay=client.post('/api/lab/recoveries/'+eid+'/replay').json()
    assert replay['experiment_id']!=eid
    assert [x['output_counts'] for x in replay['executions']]==[x['output_counts'] for x in r['executions']]
    invalid = request().model_dump(mode='json'); invalid['max_candidates'] = 999
    assert client.post('/api/lab/recoveries',json=invalid).status_code == 422


@pytest.mark.parametrize('field,value',[('max_candidates',0),('max_shots',0),('screen_shots',0),
    ('evaluation_truth',{'index':0}),('diagnostic_mode','simulator_assisted')])
def test_invalid_and_privileged_fields_rejected(field,value):
    from pydantic import ValidationError
    with pytest.raises(ValidationError): request(**{field:value})


def test_ties_do_not_become_causal_identification():
    from qfault.counterfactual import rank
    rows=[{'candidate_id':str(i),'evidence':{'loss_interval':v}} for i,v in enumerate([[0,.4],[.2,.5],[.8,1.2]])]
    ranked,plausible=rank(rows)
    assert [c['candidate_id'] for c in plausible]==['0','1']
    assert not ranked[2]['plausible']


@pytest.mark.parametrize('original,candidate,status',[
    ([2,3],[0,.8],'VERIFIED_UNDER_DECLARED_CONTRACT'),
    ([2,3],[.8,1.3],'INCONCLUSIVE'),
    ([2,3],[1.1,1.4],'REJECTED'),
    ([.3,.7],[.4,.6],'INCONCLUSIVE'),
    ([0,.2],[.3,.8],'REJECTED')])
def test_confirmation_needs_both_contract_and_fresh_improvement(original,candidate,status):
    from qfault.counterfactual import verification_verdict
    assert verification_verdict({'loss_interval':original},{'loss_interval':candidate})['status']==status


def test_all_edit_operators_validate_and_record_diff():
    from qfault.interventions import generate,EditRestrictions
    c=request().circuit.model_dump(); c['gates']=[{'name':'ry','qubits':[0],'angle':.3}]
    c=CustomCircuit.model_validate(c)
    for op in ['remove','replace','angle','reassign','insert']:
        result=generate(c,EditRestrictions(operators=(op,)),8)
        assert result['candidates']
        for p in result['candidates']:
            assert p['edit']['operator']==op
            assert p['original_circuit_id']==c.circuit_id
            assert p['circuit_id']!=c.circuit_id
            CustomCircuit.model_validate(p['circuit'])


def test_no_admissible_and_gate_noise_never_claims_cause():
    from qfault.counterfactual import recover
    r=recover(request(edits={'operators':[]}))
    assert r['status']=='NO_ADMISSIBLE_INTERVENTION'
    noisy=recover(request(environment={'depolarizing':.1}))
    assert noisy['localization']['causal_origin']=='NOT_IDENTIFIED'


def test_real_ambiguous_edits_retain_both_equivalent_locations():
    from qfault.counterfactual import recover
    c={'schema_version':1,'name':'ambiguous duplicate edits','n_qubits':2,
       'input':{'kind':'computational_basis','bitstring':'00'},
       'gates':[{'name':'x','qubits':[0]},{'name':'x','qubits':[0]}]}
    r=recover(request('measurement_distribution',circuit=c,
        contract={'kind':'measurement_distribution','expected_probabilities':{'01':1.},'tolerance':.15}))
    assert r['status']=='VERIFIED_UNDER_DECLARED_CONTRACT'
    assert r['localization']['plausible_loci']==[0,1]
    assert r['localization']['causal_origin']=='NOT_IDENTIFIED'


def test_preparation_y_parity_and_multiple_claims():
    from qfault.recovery_observation import ContractObservation
    from qfault.lab import PauliContract
    c=PauliContract(kind='pauli_expectations',observables=[{'pauli':'IY','expected':1,'tolerance':.1},
                                                        {'pauli':'ZI','expected':-1,'tolerance':.1}])
    observer=ContractObservation(2,c)
    def measured(setting,shots,label):
        assert setting=='ZY'
        return {'counts':{'10':shots},'shots':shots}
    r=observer.observe(measured,4096,.001)
    assert r['loss_interval'][1]<1
    assert len(r['claims'])==2


def test_reserve_and_no_samples_reused():
    from qfault.counterfactual import recover
    r=recover(request(max_shots=15000))
    assert r['cost']['shots']<=15000
    if r['selected_candidate']:
        assert r['cost']['phase_shots']['verification_original']==4096
        assert r['cost']['phase_shots']['verification_candidate']==4096
    phases={p:{x['execution_id'] for x in r['executions'] if x['recovery_phase']==p}
            for p in r['cost']['phase_shots']}
    assert not phases.get('screening',set()) & phases.get('verification_candidate',set())


def test_incomplete_contract_can_miss_a_phase_fault():
    from qfault.counterfactual import recover
    r=request('measurement_distribution').model_dump(mode='json')
    r['circuit']['gates']=[{'name':'z','qubits':[0]}]
    assert recover(type(request()).model_validate(r))['status']=='NO_REPAIR_NEEDED'


def test_contradictory_bounds_cannot_verify():
    from qfault.counterfactual import verification_verdict
    assert verification_verdict({'loss_interval':[2,3]}, {'loss_interval':[.9,.2]})['status']=='INCONCLUSIVE'


def test_screening_success_can_fail_confirmation(monkeypatch):
    from qfault.counterfactual import recover
    from qfault.lab import _Port
    actual=_Port.measure
    def changed_device(self,setting,shots,label):
        ev=actual(self,setting,shots,label)
        if label.startswith('verification_candidate:'):
            # Deliberate nonstationarity for a rejection test, not evaluation evidence.
            ev['counts']={'01':shots}
        return ev
    monkeypatch.setattr(_Port,'measure',changed_device)
    r=recover(request())
    assert r['selected_candidate'] is not None
    assert r['verification']['status']=='REJECTED'
