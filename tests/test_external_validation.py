"""External evaluation must keep oracle, denominators and output provenance separate."""
from pathlib import Path

import pytest

from scripts import external_validation as ev


QASM = 'OPENQASM 2.0; include "qelib1.inc"; qreg q[2]; creg c[2]; h q[0]; cx q[0],q[1]; measure q -> c;'


def test_reference_contract_does_not_follow_mutated_candidate():
    contract = ev.reference_contract(QASM, 'measurement_distribution')
    assert contract['expected_probabilities'] == pytest.approx({'00': .5, '11': .5})
    entry = {'source_path': 'independent/bell.qasm', 'circuit': {
        'schema_version': 1, 'name': 'reference', 'n_qubits': 2,
        'input': {'kind': 'computational_basis', 'bitstring': '00'},
        'gates': [{'name': 'h', 'qubits': [0]}, {'name': 'cx', 'qubits': [0, 1]}]}}
    cases = ev.make_cases(entry, contract, [17])
    missing = next(c for c in cases if c['variant'] == 'remove_first')
    assert missing['circuit']['gates'] == [{'name': 'cx', 'qubits': [0, 1]}]
    assert missing['contract'] == contract
    assert missing['truth_locus'] == 0
    assert next(c for c in cases if c['variant'] == 'clean')['circuit'] == entry['circuit']


def test_oracle_keeps_phase_invisibility_separate_from_no_fault():
    from qfault.lab import CustomCircuit
    c = CustomCircuit.model_validate({'schema_version': 1, 'name': 'minus Bell', 'n_qubits': 2,
        'input': {'kind': 'computational_basis', 'bitstring': '00'},
        'gates': [{'name': 'h', 'qubits': [0]}, {'name': 'cx', 'qubits': [0, 1]}, {'name': 'z', 'qubits': [0]}]})
    dist = ev.evaluator_truth(c, ev.reference_contract(QASM, 'measurement_distribution'), {})
    target = ev.evaluator_truth(c, ev.reference_contract(QASM, 'target_state'), {})
    assert dist['contract_violated'] is False
    assert dist['exact_loss'] == pytest.approx(0)
    assert target['contract_violated'] is True
    assert target['exact_loss'] == pytest.approx(1)


def test_summary_reports_seed_runs_and_architectures_separately():
    rows = [{'source_path': p, 'kind': 'measurement_distribution', 'policy': 'fixed', 'variant': 'remove_first',
             'category': 'SIGNIFICANT_DISCREPANCY', 'contract_violated': True, 'shots': 100,
             'evaluations': 1, 'runtime_seconds': .01, 'attribution': 'AMBIGUOUS_LOGICAL_VS_NOISE',
             'error': None} for p in ['a', 'a', 'b', 'b']]
    result = ev.summarize(rows)
    group = result['measurement_distribution/fixed']
    assert group['runs'] == 4 and group['architectures'] == 2
    assert group['observable_violations'] == 4 and group['detected_violations'] == 4
    assert len(group['by_architecture']) == 2
    assert 'wilson95' not in group


def test_exclusive_output_refuses_to_overwrite_evidence(tmp_path):
    out = tmp_path / 'existing'
    out.mkdir()
    with pytest.raises(FileExistsError):
        ev.exclusive_output(out)


def test_source_verification_rejects_modified_benchmark(tmp_path):
    p = tmp_path / 'source.qasm'
    p.write_text(QASM)
    with pytest.raises(ValueError, match='checksum'):
        ev.check_source(p, '0' * 64)


def test_missing_entangler_is_an_unsupported_mutation_not_a_second_first_gate():
    entry = {'source_path': 'product.qasm', 'circuit': {
        'schema_version': 1, 'name': 'product', 'n_qubits': 2,
        'input': {'kind': 'computational_basis', 'bitstring': '00'},
        'gates': [{'name': 'h', 'qubits': [0]}]}}
    contract = ev.reference_contract(QASM, 'measurement_distribution')
    case = next(c for c in ev.make_cases(entry, contract, [17]) if c['variant'] == 'remove_entangler')
    assert case['unsupported'] == 'reference contains no two-qubit gate'
    assert case['circuit'] is None and case['truth_locus'] is None


def test_family_detection_does_not_count_false_alarms_as_true_positives():
    row = {'source_path': 'a', 'kind': 'measurement_distribution', 'policy': 'fixed', 'variant': 'clean',
           'category': 'SIGNIFICANT_DISCREPANCY', 'contract_violated': False, 'shots': 100,
           'evaluations': 1, 'runtime_seconds': .01, 'attribution': 'AMBIGUOUS_LOGICAL_VS_NOISE', 'error': None}
    family = ev.summarize([row])['measurement_distribution/fixed']['by_architecture']['a']
    assert family['detected_violations'] == 0
    assert family['false_alarms'] == 1
