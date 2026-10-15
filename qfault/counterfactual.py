"""Bounded measured interventions, exploratory ranking and fresh confirmation.

No evaluator argument and no exact-state path. Execution has the program and declared
environment; ContractObservation receives only measurement callbacks and target claims.
"""
import random
from time import perf_counter
from typing import Literal
from pydantic import Field, model_validator
from .quantum import Strict, Noise
from .lab import CustomCircuit, Contract, TargetStateContract, check_pair, _Port
from .diagnostics import ExecutionBudget, tv_radius
from .evidence import digest, identifier, timestamp, canonical
from .interventions import EditRestrictions, generate
from .recovery_observation import ContractObservation

VERSION = 'measured-intervention-v1'


class RecoveryRequest(Strict):
    circuit: CustomCircuit
    contract: Contract
    backend: Literal['aer','reference'] = 'aer'
    environment: Noise = Noise()
    edits: EditRestrictions = EditRestrictions()
    selection_policy: Literal['conservative','point_discrepancy','first_admissible','random','no_repair'] = 'conservative'
    max_candidates: int = Field(default=12,ge=1,le=48,strict=True)
    screen_shots: int = Field(default=2048,ge=64,le=10000,strict=True)
    verification_shots: int = Field(default=4096,ge=64,le=10000,strict=True)
    max_shots: int = Field(default=200000,ge=128,le=1000000,strict=True)
    max_evaluations: int = Field(default=160,ge=1,le=512,strict=True)
    max_groups: int = Field(default=16,ge=1,le=32,strict=True)
    max_seconds: float = Field(default=120,ge=1,le=300)
    alpha_total: float = Field(default=.01,ge=.00001,le=.1)
    seed: int = Field(default=42,ge=0,lt=2**32,strict=True)

    @model_validator(mode='after')
    def valid(self):
        check_pair(self.circuit,self.contract)
        if self.edits.positions is not None and any(p<0 or p>len(self.circuit.gates) for p in self.edits.positions):
            raise ValueError('edit position outside circuit')
        if any(abs(a)>25.132741228718345 for a in self.edits.angles): raise ValueError('angle outside bounds')
        return self


def rank(candidates):
    """Interval dominance on normalized worst-claim loss; overlaps are unresolved ties.

    Display by conservative upper loss; resource ordering chooses within the plausible
    set for execution only, and never resolves evidential or causal ambiguity.
    """
    ordered = sorted(candidates,key=lambda c:(c['evidence']['loss_interval'][1],c['candidate_id']))
    plausible = [c for c in ordered if not any(d['evidence']['loss_interval'][1] < c['evidence']['loss_interval'][0]
                                              for d in ordered)]
    for i,c in enumerate(ordered):
        c['display_order'] = i+1
        c['plausible'] = c in plausible
    return ordered, plausible


def verification_verdict(original, candidate):
    ol, ou = original['loss_interval']; cl, cu = candidate['loss_interval']
    improvement = ol-cu
    consistent = ol <= ou and cl <= cu
    if not consistent: status = 'INCONCLUSIVE'
    elif cu <= 1 and improvement > 0: status = 'VERIFIED_UNDER_DECLARED_CONTRACT'
    elif cl > 1 or ou < cl: status = 'REJECTED'
    else: status = 'INCONCLUSIVE'
    return {'status':status,'original':original,'candidate':candidate,
            'improvement_lower':improvement,'improvement_upper':ou-cl,
            'contract_satisfied':consistent and cu<=1,'improvement_supported':consistent and improvement>0,
            'bounds_consistent':consistent}


def recover(request: RecoveryRequest):
    start = perf_counter()
    observer = ContractObservation(request.circuit.n_qubits,request.contract)
    generated = generate(request.circuit,request.edits,request.max_candidates)
    budget = ExecutionBudget(request.max_shots,request.max_evaluations)
    records, phases = [], []
    # One screening look for original + C candidates; independent original/candidate
    # confirmation, plus one readout interval. Conditional validity after selection
    # holds because verification samples are unused at selection time.
    slot = request.alpha_total / ((request.max_candidates+3)*max(1,observer.interval_count)+1)
    groups = min(len(observer.groups),request.max_groups)
    reserve = 2*groups*request.verification_shots
    reserve_evals = 2*groups
    selected, original, control, selection = None, None, None, None
    verification = {'status':'NOT_EXECUTED'}
    tested, plausible, ranked = [], [], []
    status = 'INSUFFICIENT_BUDGET'
    screen_limit = 0
    uncalibrated_target = isinstance(request.contract, TargetStateContract) and bool(request.environment.readout or request.environment.depolarizing)

    def measure_for(circuit, phase):
        # Unique deterministic seed per execution throughout this investigation.
        def measure(setting, shots, label):
            if perf_counter()-start > request.max_seconds: raise TimeoutError('execution guard reached')
            seed = (request.seed + len(records)*7919) % 2**32
            port = _Port(circuit.subject(),request.environment,budget,request.backend,seed,records)
            ev = port.measure(setting,shots,phase+':'+label)
            records[-1].update(subject_circuit_id=circuit.circuit_id,recovery_phase=phase)
            phases.append({'phase':phase,'execution_id':ev['execution_id'],'shots':shots,
                           'subject_circuit_id':circuit.circuit_id,'setting':setting})
            return ev
        return measure

    try:
        # Protect confirmation AND a possible readout control before observation.
        # Otherwise a large screen batch can exhaust the control budget after
        # observation even though the initial confirmation-only preflight passed.
        if uncalibrated_target:
            status = 'MEASUREMENT_MODEL_ABSTENTION'
            verification = {'status': 'NOT_EXECUTED', 'reason': 'Target fidelity requires calibrated common-state Pauli measurements. Declared readout or analysis-gate noise is uncalibrated; no state certificate or repair is claimed.'}
        elif budget.can(reserve+(groups+1)*request.screen_shots,reserve_evals+groups+1):
            by_shots=max(0,(request.max_shots-reserve-(groups+1)*request.screen_shots)//max(1,groups*request.screen_shots))
            by_evals=max(0,(request.max_evaluations-reserve_evals-groups-1)//max(1,groups))
            screen_limit=min(request.max_candidates,by_shots,by_evals)
            original = observer.observe(measure_for(request.circuit,'observation'),request.screen_shots,slot,request.max_groups)
            status = 'NO_REPAIR_NEEDED' if original['loss_interval'][1]<=1 else 'INSUFFICIENT_EVIDENCE'
            if original['loss_interval'][0] > 1:
                ev = measure_for(request.circuit,'control')(None,request.screen_shots,'readout')
                tv = 1-ev['counts'].get('0'*request.circuit.n_qubits,0)/ev['shots']
                radius = tv_radius(ev['shots'],2**request.circuit.n_qubits,slot)
                control = {**ev,'tv':tv,'radius':radius,'significant':tv-radius>.1}
                status = 'NOISE_CONTROL_ABSTENTION' if control['significant'] else 'NO_ADMISSIBLE_INTERVENTION'
                if not control['significant'] and request.selection_policy != 'no_repair':
                    for proposal in generated['candidates'][:screen_limit]:
                        if not budget.can(reserve+groups*request.screen_shots,reserve_evals+groups): break
                        c = CustomCircuit.model_validate(proposal['circuit'])
                        ev = observer.observe(measure_for(c,'screening'),request.screen_shots,slot,request.max_groups)
                        tested.append({**proposal,'evidence':ev})
                    ranked, plausible = rank(tested)
                    status = 'INSUFFICIENT_EVIDENCE' if tested else ('INSUFFICIENT_BUDGET' if screen_limit==0 and generated['candidates'] else 'NO_ADMISSIBLE_INTERVENTION')
                    pool = [c for c in plausible if c['evidence']['loss_interval'][1]<original['loss_interval'][0]]
                    if request.selection_policy == 'first_admissible': pool = tested[:1]
                    elif request.selection_policy == 'random': pool = random.Random(request.seed ^ 0xCAFE).sample(tested,1) if tested else []
                    elif request.selection_policy == 'point_discrepancy': pool = sorted(tested,key=lambda c:c['evidence']['point_loss'])[:1]
                    if pool:
                        selected = min(pool,key=lambda c:(c['resources']['two_qubit_gates'],c['resources']['depth'],c['resources']['gates'],c['candidate_id']))
                        selection = {'candidate_id':selected['candidate_id'],'policy':request.selection_policy,
                            'frozen_before_verification':True,'created_at':timestamp(),
                            'screening_digest':digest({'original':original,'ranked':ranked}),
                            'plausible_candidate_ids':[c['candidate_id'] for c in plausible],
                            'tie_rule':'Fewest two-qubit gates, depth, gates, then structural ID. Operational choice, not evidential superiority.'}
                        selection['digest'] = digest(selection)
                        fresh_original = observer.observe(measure_for(request.circuit,'verification_original'),request.verification_shots,slot,request.max_groups)
                        fresh_candidate = observer.observe(measure_for(CustomCircuit.model_validate(selected['circuit']),'verification_candidate'),request.verification_shots,slot,request.max_groups)
                        verification = verification_verdict(fresh_original,fresh_candidate)
                        status = verification['status']
                elif request.selection_policy == 'no_repair' and not control['significant']:
                    status = 'NO_REPAIR_CONTROL'
    except TimeoutError:
        status = 'RUNTIME_GUARD_ABSTENTION'
        verification = {'status':'INCONCLUSIVE','reason':'Guard stopped before a complete fresh comparison'}
    loci = sorted({i for c in plausible for i in [c['edit']['index'], *(e['index'] for e in c.get('equivalent_edits',[]))]})
    eid = identifier('experiment')
    for record in records: record['experiment_id'] = eid
    result = {'schema_version':3,'investigation_kind':'counterfactual_recovery','experiment_id':eid,'created_at':timestamp(),
        'configuration':request.model_dump(mode='json'),'circuit':request.circuit.model_dump(mode='json'),
        'circuit_id':request.circuit.circuit_id,'contract':{**request.contract.model_dump(mode='json'),'family':'custom'},
        'status':status,'diagnosis':{'category':status},'original_evidence':original,'readout_control':control,
        'generation':generated,'ranked_candidates':ranked,'selected_candidate':selected,'selection':selection,
        'screening_candidate_limit':screen_limit,
        'verification':verification,'recovery':{'status':status},'privileged_operations':[],
        'localization':{'status':'MULTIPLE_PLAUSIBLE_LOCATIONS' if len(loci)>1 else 'CANDIDATE_LOCATION' if loci else 'NO_LOCATION_DISTINGUISHED',
                        'plausible_loci':loci,'causal_origin':'NOT_IDENTIFIED','scope':'Tested one-edit set only; untested candidates remain possible'},
        'cost':{**budget.report(),'runtime_seconds':perf_counter()-start,'reserved_verification_shots':reserve,
                'phase_shots':{p:sum(x['shots'] for x in phases if x['phase']==p) for p in sorted({x['phase'] for x in phases})},
                'generated_candidates':len(generated['candidates']),'tested_candidates':len(tested)},
        'statistical_design':{'version':VERSION,'alpha_total':request.alpha_total,'alpha_per_interval':slot,
            'rule':'One prespecified look per group/subject; union bound over (C+3)*M+1 intervals. Fresh paired confirmation after frozen selection.',
            'loss':'max normalized claim discrepancy; target state uses infidelity / tolerance; <=1 satisfies contract',
            'comparison_budget':'No repeated refinement; all comparison is from simultaneous single-look screening intervals',
            'ranking':'Interval dominance, display by upper loss; preserve overlaps. Confirm only fresh candidate upper loss <=1 AND fresh original lower > candidate upper.'},
        'limitations':['An improving edit does not identify the original faulty operation.',
            'One declared input and contract only; unmeasured behavior may change.',
            'Simulated executions, i.i.d. stationary shots; no drift or systematic model-error protection.',
            'Gate noise can mimic logical defects; readout control probes only zero-state readout.',
            'Target fidelity interpretation assumes calibrated measurement channels; readout/basis noise can bias witnesses.',
            'Runtime guard checked between bounded jobs; it cannot interrupt an already executing backend job.'],
        'action_ledger':phases,'executions':records,'human_decisions':[],
        'replay':{'request':request.model_dump(mode='json')},
        'integrity':{'algorithm':'sha256','canonicalization':'qfault-json-v1','signing':'UNAVAILABLE'},
        'evaluation_truth':{'kind':'user_supplied_circuit','ground_truth':None}}
    result['prediction_digest'] = digest({'selection':selection,'verification':verification,'localization':result['localization']})
    if len(canonical(result))>16*1024*1024: raise ValueError('recovery artifact exceeds 16 MiB')
    return result
