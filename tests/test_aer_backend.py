"""Real optional Aer executions, not capability flags."""
import numpy as np
import pytest
from qfault.quantum import Circuit,Gate,Noise,benchmark,contract,execute,noisy_density
from qfault.workflow import RunRequest,investigate
pytest.importorskip('qiskit_aer')

@pytest.mark.parametrize('family,n',[('bell',2),('ghz',3),('qft',3)])
def test_aer_seed_accounting_and_probabilities(family,n):
    c=benchmark(family,n)
    first=execute(c,Noise(),4096,19,backend='aer')
    second=execute(c,Noise(),4096,19,backend='aer')
    assert first['output_counts']==second['output_counts']
    assert first['executed_shots']==sum(first['output_counts'].values())==4096
    assert first['backend_name']=='qiskit_aer.AerSimulator/density_matrix'
    assert first['software_versions']['qiskit-aer']=='0.17.2'
    expected=contract(family,n).describe()['expected_probabilities']
    assert sum(abs(first['output_counts'].get(k,0)/4096-p) for k,p in expected.items())/2<.06

def test_aer_bit_order_and_readout():
    c=Circuit(n_qubits=2,gates=(Gate(name='x',qubits=(0,)),))
    assert execute(c,Noise(),128,5,backend='aer')['output_counts']=={'01':128}
    r=execute(c,Noise(readout=.2),8192,5,backend='aer')['output_counts']
    assert abs(r.get('01',0)/8192-.64)<.03

@pytest.mark.parametrize('family,n',[('bell',2),('ghz',3),('qft',3)])
def test_aer_density_matches_kraus(family,n):
    from qfault.backends import aer_simulator
    c=benchmark(family,n);noise=Noise(depolarizing=.17,readout=.2)
    q=c.native();q.save_density_matrix()
    r=aer_simulator(c,noise).run(q,seed_simulator=19).result()
    assert r.success
    np.testing.assert_allclose(r.data(0)['density_matrix'].data,noisy_density(c,noise).data,atol=1e-12)

def test_aer_full_phase_repair_and_noise():
    result=investigate(RunRequest(scenario='phase',policy='phase',backend='aer',max_shots=20000))
    assert result['diagnosis']['category']=='LOGICAL_CIRCUIT_DEFECT'
    assert result['recovery']['status']=='VERIFIED'
    assert all(r['backend_name'].startswith('qiskit_aer.') for r in result['executions'])
    assert sum(r['executed_shots'] for r in result['executions'])==result['cost']['shots']
    noisy=investigate(RunRequest(scenario='readout',policy='phase',backend='aer',recover=False))
    assert noisy['diagnosis']['category']=='NOISE_CONSISTENT_DEGRADATION'
