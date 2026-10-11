import math
import numpy as np
import pytest
from pydantic import ValidationError
from qfault.quantum import benchmark, contract, ideal_state, execute, Noise, mutate, Circuit, Gate

@pytest.mark.parametrize("family,n", [("bell",2),("ghz",3),("ghz",5),("qft",3)])
def test_analytic_state_contract(family,n):
    state = ideal_state(benchmark(family,n))
    expected = contract(family,n).state()
    assert abs(np.vdot(expected,state))**2 > 1-1e-10


def test_bell_finite_shots_and_seed():
    c=benchmark("bell",2)
    a=execute(c,Noise(),1024,7)
    b=execute(c,Noise(),1024,7)
    assert a["output_counts"]==b["output_counts"]
    assert sum(a["output_counts"].values())==1024
    assert set(a["output_counts"]) <= {"00","11"}
    assert abs(a["output_counts"]["00"]/1024-.5)<.08


def test_noise_is_systematic_and_not_removed_by_shots():
    c=benchmark("bell",2)
    a=execute(c,Noise(readout=.2),20000,42)
    off=sum(v for k,v in a["output_counts"].items() if k in {"01","10"})/20000
    assert .29 < off < .35  # 2p(1-p) = .32


def test_depolarization_complete_channel():
    c=Circuit(n_qubits=2,gates=(Gate(name="x",qubits=(0,)),))
    a=execute(c,Noise(depolarizing=1),20000,1)
    assert abs(a["output_counts"].get("00",0)/20000-.5)<.03
    assert abs(a["output_counts"].get("01",0)/20000-.5)<.03
    assert not set(a["output_counts"])-{"00","01"}


def test_removal_changes_state_and_keeps_original():
    c=benchmark("bell",2)
    fault,truth=mutate(c,"remove",1,4)
    assert len(c.gates)==2 and len(fault.gates)==1
    assert abs(np.vdot(contract("bell",2).state(),ideal_state(fault)))**2 < .6
    assert truth["operator"]=="remove"


def test_phase_fault_can_preserve_distribution():
    c=benchmark("bell",2)
    phase=Circuit(n_qubits=2,gates=c.gates+(Gate(name="z",qubits=(0,)),))
    assert np.allclose(abs(ideal_state(c))**2,abs(ideal_state(phase))**2)
    assert abs(np.vdot(ideal_state(c),ideal_state(phase)))**2 < 1e-10

@pytest.mark.parametrize("kwargs",[{"readout":-.1},{"readout":float('nan')},{"depolarizing":1.1}])
def test_invalid_noise(kwargs):
    with pytest.raises(ValidationError): Noise(**kwargs)

@pytest.mark.parametrize("shots",[0,-1,100001])
def test_invalid_shots(shots):
    with pytest.raises(ValueError): execute(benchmark("bell",2),Noise(),shots,1)


def test_invalid_circuit():
    with pytest.raises(ValidationError): Circuit(n_qubits=2,gates=(Gate(name="cx",qubits=(0,0)),))
    with pytest.raises(ValidationError): Circuit(n_qubits=2,gates=(Gate(name="x",qubits=(2,)),))
    with pytest.raises(ValidationError): Gate(name="unsupported",qubits=(0,))
