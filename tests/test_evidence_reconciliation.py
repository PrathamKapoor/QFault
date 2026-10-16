"""Row partitions must explain every archive omission without invented IDs."""
import copy
from pathlib import Path

import pytest


def reconcile(rows, recovery_rows, reports):
    assert Path('scripts/reconcile_external_evidence.py').exists(), 'reconciliation helper missing'
    from scripts.reconcile_external_evidence import reconcile_rows
    return reconcile_rows(rows, recovery_rows, reports)


@pytest.fixture
def partition():
    rows = [dict(source_path='small/a.qasm', kind='target_state', policy='fixed',
                 variant='clean', seed=1, category='NO_DISCREPANCY',
                 error=None, experiment_id='run-a'),
            dict(source_path='small/qrng.qasm', kind='target_state', policy='fixed',
                 variant='remove_entangler', seed=1, category='UNSUPPORTED',
                 error=None, unsupported='reference contains no two-qubit gate')]
    recovery = [dict(source_path='small/a.qasm', policy='no_repair', variant='clean',
                     seed=1, status='NO_REPAIR_NEEDED', error=None, experiment_id='run-b')]
    reports = [dict(investigation=dict(experiment_id=eid)) for eid in ('run-a', 'run-b')]
    return rows, recovery, reports


def test_partitions_explain_gap_with_concrete_identity_without_fabricated_id(partition):
    result = reconcile(*partition)
    assert result['valid'], result['errors']
    assert result['counts'] == dict(diagnostic_rows=2, recovery_rows=1, total_rows=3,
                                    executed_rows=2, nonexecution_rows=1, reports=2,
                                    unique_row_ids=2, unique_report_ids=2)
    assert result['nonexecution_rows'] == [dict(
        case_key=['small/qrng.qasm', 'target_state', 'fixed', 'remove_entangler', 1],
        row_class='diagnostic', category='UNSUPPORTED',
        reason='reference contains no two-qubit gate')]
    assert result['duplicate_row_ids'] == []
    assert result['duplicate_report_ids'] == []


@pytest.mark.parametrize('change, fragment', [
    ('excluded_id', 'excluded row has experiment_id'),
    ('missing_reason', 'excluded row lacks reason'),
    ('duplicate_id', 'duplicate row experiment_id'),
    ('duplicate_report', 'duplicate export experiment_id'),
    ('missing_export', 'missing export'),
    ('extra_export', 'unmatched export'),
    ('missing_id', 'executed row lacks experiment_id'),
    ('inconsistent_error', 'error/status partition mismatch'),
    ('duplicate_case', 'duplicate case key'),
])
def test_invalid_partition_is_rejected(partition, change, fragment):
    rows, recovery, reports = copy.deepcopy(partition)
    if change == 'excluded_id': rows[1]['experiment_id'] = 'invented'
    elif change == 'missing_reason': rows[1]['unsupported'] = ''
    elif change == 'duplicate_id': recovery[0]['experiment_id'] = 'run-a'
    elif change == 'duplicate_report': reports.append(copy.deepcopy(reports[0]))
    elif change == 'missing_export': reports.pop()
    elif change == 'extra_export': reports.append(dict(investigation=dict(experiment_id='unexpected')))
    elif change == 'missing_id': del rows[0]['experiment_id']
    elif change == 'inconsistent_error': rows[0]['error'] = 'failure while category says executed'
    elif change == 'duplicate_case': rows.append(copy.deepcopy(rows[1]))
    result = reconcile(rows, recovery, reports)
    assert not result['valid']
    assert any(fragment in error for error in result['errors']), result['errors']


def test_execution_errors_are_named_nonexecution_cases(partition):
    rows, recovery, reports = partition
    recovery[0].update(status='ERROR', error='backend unavailable')
    del recovery[0]['experiment_id']
    reports.pop()
    result = reconcile(rows, recovery, reports)
    assert result['valid'], result['errors']
    assert result['nonexecution_rows'][0] == dict(
        case_key=['small/a.qasm', 'pauli_expectations', 'no_repair', 'clean', 1],
        row_class='recovery', category='ERROR', reason='backend unavailable')


def test_frozen_grid_detects_silent_dropped_excluded_case(partition):
    reconcile(*partition)
    from scripts.reconcile_external_evidence import reconcile_rows
    expected = [dict(row_class='diagnostic', case_key=['small/a.qasm', 'target_state', 'fixed', 'clean', 1]),
                dict(row_class='diagnostic', case_key=['small/qrng.qasm', 'target_state', 'fixed', 'remove_entangler', 1]),
                dict(row_class='recovery', case_key=['small/a.qasm', 'pauli_expectations', 'no_repair', 'clean', 1])]
    partition[0].pop()
    result = reconcile_rows(*partition, expected_cases=expected)
    assert not result['valid']
    assert result['missing_cases'] == [expected[1]]
    assert any('missing frozen case' in error for error in result['errors'])


def test_frozen_grid_includes_unsupported_variant_and_target_global_phase():
    from scripts import reconcile_external_evidence as audit
    assert hasattr(audit, 'frozen_case_grid'), 'frozen case grid missing'
    summary = dict(split='holdout', protocol=dict(seeds={'holdout': [7]},
        policies={'measurement_distribution': ['fixed'], 'target_state': ['random']},
        recovery=dict(policies=['no_repair'], variants=['clean'])))
    corpus = dict(entries=[dict(source_path='small/qrng.qasm', status='eligible', split='holdout'),
                           dict(source_path='small/dev.qasm', status='eligible', split='development'),
                           dict(source_path='small/rejected.qasm', status='excluded', split=None)])
    grid = audit.frozen_case_grid(summary, corpus)
    assert len(grid) == 18  # Eight distribution, nine target, one recovery.
    assert dict(row_class='diagnostic', case_key=['small/qrng.qasm', 'target_state', 'random', 'global_phase_contract', 7]) in grid
    assert dict(row_class='diagnostic', case_key=['small/qrng.qasm', 'measurement_distribution', 'fixed', 'remove_entangler', 7]) in grid
    assert {x['case_key'][0] for x in grid} == {'small/qrng.qasm'}
