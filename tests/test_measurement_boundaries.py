import numpy as np
from qfault.quantum import Contract,Circuit,Gate,measurement_probabilities,measured_circuit

def test_high_qft_input_basis_rotation():
    spec=Contract(family='qft',n_qubits=4,input_basis=9)
    assert measurement_probabilities(spec)['0000']>1-1e-12

def test_maximum_candidate_can_be_measured_without_relaxing_user_limit():
    spec=Contract(family='bell',n_qubits=2)
    c=Circuit(n_qubits=2,gates=(Gate(name='h',qubits=(0,)),)*32)
    rotated=measured_circuit(c,spec)
    assert len(rotated.gates)==34
    assert len(c.gates)==32
    import pytest
    with pytest.raises(ValueError): Circuit(n_qubits=2,gates=rotated.gates)
