"""Run the source-qualified QRNG phase investigation through the loopback API."""
import argparse
import copy
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from qfault.evidence import canonical, digest
from qfault.storage import verify_export
from scripts.external_validation import ROOT, reference_contract, check_source


def example():
    corpus = json.loads((ROOT / 'configs/external-corpus.json').read_text())
    entry = next(e for e in corpus['entries'] if e['source_path'] == 'small/qrng_n4/qrng_n4.qasm')
    raw = check_source(ROOT / 'benchmarks/external/qasmbench' / entry['source_path'], entry['sha256'])
    candidate = copy.deepcopy(entry['circuit'])
    candidate['name'] = 'QASMBench QRNG with controlled terminal Z on qubit 0'
    candidate['gates'].append({'name': 'z', 'qubits': [0]})
    return {'source_path': entry['source_path'], 'source_revision': entry['source_repo_sha'],
            'source_sha256': entry['sha256'], 'reference': entry['circuit'], 'candidate': candidate,
            'distribution': reference_contract(raw, 'measurement_distribution'),
            'complementary': reference_contract(raw, 'pauli_expectations'),
            'scope': 'Canonical zero input; original four-H external circuit unchanged. Terminal Z is a separately declared evaluator-controlled discrepancy. This simple product-state example demonstrates observability, not general recovery performance.'}


def request_json(base, path, body=None):
    request = Request(base + path, data=canonical(body) if body is not None else None,
                      headers={'Content-Type': 'application/json'})
    with urlopen(request, timeout=180) as response:
        return json.load(response)


def run(base, out):
    parsed = urlparse(base)
    if parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost'):
        raise ValueError('demonstration requires the local loopback API')
    out.mkdir(parents=True, exist_ok=False)
    ex = example()
    rows, reports = [], {}
    stages = [('baseline_z', ex['reference'], ex['distribution']),
              ('phase_z', ex['candidate'], ex['distribution']),
              ('phase_complementary', ex['candidate'], ex['complementary'])]
    for name, circuit, contract in stages:
        result = request_json(base, '/api/lab/investigations', {'circuit': circuit, 'contract': contract,
            'diagnostic_mode': 'measurement_only', 'policy': 'fixed', 'backend': 'aer', 'seed': 4191})
        assert result['privileged_operations'] == []
        report = request_json(base, f"/api/experiments/{result['experiment_id']}/report")
        assert verify_export(report)['valid']
        (out / (name + '-report.json')).write_bytes(canonical(report))
        reports[name] = result['experiment_id']
        rows.append({'stage': name, 'experiment_id': result['experiment_id'],
                     'category': result['diagnosis']['category'], 'claims': result['claims'],
                     'attribution': result['diagnosis']['attribution'], 'cost': result['cost'],
                     'measurements': result['action_ledger'], 'export_verified': True})
    result = request_json(base, '/api/lab/recoveries', {'circuit': ex['candidate'], 'contract': ex['complementary'],
        'backend': 'aer', 'selection_policy': 'conservative', 'seed': 4191, 'max_candidates': 32,
        'screen_shots': 2048, 'verification_shots': 4096, 'max_shots': 200000})
    report = request_json(base, f"/api/experiments/{result['experiment_id']}/report")
    assert verify_export(report)['valid'] and not result['privileged_operations']
    (out / 'recovery-report.json').write_bytes(canonical(report))
    reports['recovery'] = result['experiment_id']
    rows.append({'stage': 'measured_recovery', 'experiment_id': result['experiment_id'], 'status': result['status'],
                 'selection': result['selection'], 'verification': result['verification'],
                 'localization': result['localization'], 'cost': result['cost'], 'export_verified': True})
    summary = {'example': ex, 'stages': rows, 'reports': reports,
               'total_shots': sum(r['cost']['shots'] for r in rows),
               'total_executions': sum(r['cost']['evaluations'] for r in rows),
               'interpretation': 'Z-only observations cannot see the terminal relative phase. Complementary X-basis evidence can detect it. Any verified edit restores only this contract and input; causal origin is not established.'}
    summary['digest'] = digest(summary)
    (out / 'summary.json').write_bytes(canonical(summary))
    print(json.dumps({'reports': reports, 'categories': [r.get('category', r.get('status')) for r in rows],
                      'total_shots': summary['total_shots'], 'executions': summary['total_executions']}))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='http://127.0.0.1:8000')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.base.rstrip('/'), args.out)


if __name__ == '__main__': main()
