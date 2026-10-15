"""The unfamiliar-circuit demo retains the external program and independent oracle."""
from scripts import external_demo


def test_qrng_demo_preserves_source_and_declares_phase_fault_separately():
    example = external_demo.example()
    assert example['source_path'] == 'small/qrng_n4/qrng_n4.qasm'
    assert example['reference']['gates'] == [
        {'name': 'h', 'qubits': [i], 'angle': None} for i in range(4)]
    assert example['candidate']['gates'][:-1] == example['reference']['gates']
    assert example['candidate']['gates'][-1] == {'name': 'z', 'qubits': [0]}
    assert len(example['distribution']['expected_probabilities']) == 16
    assert all(abs(p - 1/16) < 1e-12 for p in example['distribution']['expected_probabilities'].values())
    assert all(o['expected'] > .999999 for o in example['complementary']['observables'])
    assert any(o['pauli'].endswith('X') for o in example['complementary']['observables'])
    assert 'evaluation_truth' not in example
