"""Deterministically explain every external-study row/export identity.

Membership audit only: run verify_external_results separately for digest and
payload checks. No evaluator import, experiment execution or output mutation.
Recovery's fixed Pauli contract is named explicitly in its concrete case key.
"""
import argparse
from collections import defaultdict
import gzip
import json
from pathlib import Path


def frozen_case_grid(summary, corpus):
    """Expected v1 cases, including mutations that cannot execute.

    Names are the v1 recorded case names, independent of evaluator make_cases.
    Eligibility comes from the frozen inventory, never from observed rows.
    """
    protocol, split = summary['protocol'], summary['split']
    variants = ('clean', 'remove_first', 'remove_entangler', 'readout',
                'gate_noise', 'mixed', 'low_shots', 'terminal_phase')
    expected = []
    for entry in corpus['entries']:
        if entry['status'] != 'eligible' or entry['split'] != split:
            continue
        path = entry['source_path']
        for kind, policies in protocol['policies'].items():
            cases = variants + (('global_phase_contract',) if kind == 'target_state' else ())
            for policy in policies:
                for variant in cases:
                    for seed in protocol['seeds'][split]:
                        expected.append(dict(row_class='diagnostic', case_key=[path, kind, policy, variant, seed]))
        for policy in protocol['recovery']['policies']:
            for variant in protocol['recovery']['variants']:
                for seed in protocol['seeds'][split]:
                    expected.append(dict(row_class='recovery', case_key=[path, 'pauli_expectations', policy, variant, seed]))
    return sorted(expected, key=lambda x: (x['row_class'], x['case_key']))


def reconcile_rows(rows, recovery_rows, reports, *, expected_cases=None):
    errors, exclusions = [], []
    row_ids, report_ids, case_keys = defaultdict(list), defaultdict(list), set()
    executed = 0
    for row_class, group in (('diagnostic', rows), ('recovery', recovery_rows)):
        for index, row in enumerate(group):
            key = [row['source_path'], row.get('kind', 'pauli_expectations'),
                   row['policy'], row['variant'], row['seed']]
            identity = dict(row_class=row_class, case_key=key)
            unique_key = (row_class, *key)
            if unique_key in case_keys:
                errors.append('duplicate case key: ' + json.dumps(identity, sort_keys=True))
            case_keys.add(unique_key)
            status = row.get('category') if row_class == 'diagnostic' else row.get('status')
            error = row.get('error')
            if (status == 'ERROR') != (error is not None):
                errors.append('error/status partition mismatch: ' + json.dumps(identity, sort_keys=True))
            excluded = status in {'UNSUPPORTED', 'ERROR'} or error is not None
            eid = row.get('experiment_id')
            if excluded:
                reason = row.get('unsupported') if status == 'UNSUPPORTED' else error
                if not isinstance(reason, str) or not reason.strip():
                    errors.append('excluded row lacks reason: ' + json.dumps(identity, sort_keys=True))
                if 'experiment_id' in row:
                    errors.append('excluded row has experiment_id: ' + json.dumps(identity, sort_keys=True))
                exclusions.append({**identity, 'category': status, 'reason': reason})
            else:
                executed += 1
                if not isinstance(eid, str) or not eid.strip():
                    errors.append('executed row lacks experiment_id: ' + json.dumps(identity, sort_keys=True))
                else:
                    row_ids[eid].append(identity)
    report_count = 0
    for report_count, report in enumerate(reports, 1):
        report_ids[report['investigation']['experiment_id']].append(report_count)
    duplicates = []
    for eid in sorted(row_ids):
        if len(row_ids[eid]) > 1:
            duplicates.append(dict(experiment_id=eid, cases=row_ids[eid]))
            errors.append('duplicate row experiment_id: ' + eid)
    duplicate_exports = []
    for eid in sorted(report_ids):
        if len(report_ids[eid]) > 1:
            duplicate_exports.append(dict(experiment_id=eid, archive_lines=report_ids[eid]))
            errors.append('duplicate export experiment_id: ' + eid)
    missing = sorted(row_ids.keys() - report_ids.keys())
    extra = sorted(report_ids.keys() - row_ids.keys())
    errors.extend('missing export: ' + eid for eid in missing)
    errors.extend('unmatched export: ' + eid for eid in extra)
    missing_cases, unexpected_cases = [], []
    if expected_cases is not None:
        expected_keys = {(c['row_class'], *c['case_key']) for c in expected_cases}
        for key in sorted(expected_keys - case_keys):
            case = dict(row_class=key[0], case_key=list(key[1:]))
            missing_cases.append(case)
            errors.append('missing frozen case: ' + json.dumps(case, sort_keys=True))
        for key in sorted(case_keys - expected_keys):
            case = dict(row_class=key[0], case_key=list(key[1:]))
            unexpected_cases.append(case)
            errors.append('unexpected frozen case: ' + json.dumps(case, sort_keys=True))
    return dict(valid=not errors, counts=dict(diagnostic_rows=len(rows), recovery_rows=len(recovery_rows),
        total_rows=len(rows) + len(recovery_rows), executed_rows=executed,
        nonexecution_rows=len(exclusions), reports=report_count,
        unique_row_ids=len(row_ids), unique_report_ids=len(report_ids)),
        nonexecution_rows=sorted(exclusions, key=lambda x: (x['case_key'], x['row_class'])),
        duplicate_row_ids=duplicates, duplicate_report_ids=duplicate_exports,
        missing_exports=missing, unmatched_exports=extra,
        missing_cases=missing_cases, unexpected_cases=unexpected_cases, errors=errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('summary', type=Path)
    parser.add_argument('reports', type=Path)
    parser.add_argument('--corpus', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'configs/external-corpus.json')
    args = parser.parse_args()
    try:
        summary = json.loads(args.summary.read_bytes())
        corpus = json.loads(args.corpus.read_bytes())
        expected = frozen_case_grid(summary, corpus)
        with gzip.open(args.reports, 'rb') as stream:
            result = reconcile_rows(summary['rows'], summary['recovery_rows'],
                                    (json.loads(line) for line in stream), expected_cases=expected)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = dict(valid=False, errors=[f'input failure: {type(exc).__name__}: {exc}'])
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
