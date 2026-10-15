"""Source-gated external validation, with evaluator truth kept outside QFAULT."""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
from math import pi
from pathlib import Path
import platform
import subprocess
from time import perf_counter

import numpy as np
from qiskit import qasm2
from qiskit.circuit.library import CPhaseGate, CSwapGate, SwapGate
from qiskit.quantum_info import Pauli, Statevector

from qfault.counterfactual import RecoveryRequest, recover
from qfault.evidence import canonical, digest
from qfault.lab import CustomCircuit, LabRequest, investigate_lab
from qfault.quantum import Noise, noisy_density, resources
from qfault.storage import ArtifactStore, verify_export

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / 'configs/external-corpus.json'
PROTOCOL = ROOT / 'configs/external-validation-protocol.json'
POLICIES = {'measurement_distribution': ['fixed', 'complementary_schedule', 'adaptive', 'random'],
            'pauli_expectations': ['fixed', 'complementary_schedule', 'adaptive', 'random'],
            'target_state': ['fixed', 'complementary_schedule', 'coefficient_weighted', 'adaptive_witness', 'random']}
SEEDS = {'development': [1701], 'holdout': [91001, 91002]}
BUDGET = {'batch_shots': 1024, 'max_shots': 12288, 'max_evaluations': 16, 'max_looks': 4, 'alpha_total': .01}
SOURCES = ['qfault/lab.py', 'qfault/target.py', 'qfault/quantum.py', 'qfault/backends.py',
           'qfault/diagnostics.py', 'qfault/counterfactual.py', 'qfault/interventions.py',
           'qfault/recovery_observation.py', 'qfault/qasm_import.py', 'qfault/evidence.py',
           'qfault/storage.py', 'scripts/external_corpus.py', 'scripts/external_validation.py',
           'configs/external-corpus.json', 'pyproject.toml', 'requirements.lock',
           'web/package-lock.json', 'scripts/retrieve_external_sources.py', '.gitattributes']


def git(*args):
    return subprocess.check_output(['git', '-c', 'safe.directory=' + ROOT.as_posix(), *args], cwd=ROOT, text=True).strip()


def source_hashes():
    # Git checkouts may use CRLF. The normalized source digest is portable.
    paths = SOURCES + [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / 'benchmarks/external/qasmbench').rglob('*')) if p.is_file()]
    return {p: hashlib.sha256((ROOT / p).read_bytes().replace(b'\r\n', b'\n')).hexdigest() for p in paths}


def check_source(path, expected):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('External source checksum mismatch: ' + str(path))
    return raw


def exclusive_output(path):
    Path(path).mkdir(parents=True, exist_ok=False)


def reference_contract(source, kind):
    """Trusted oracle is the original QASM, separately parsed before mutation.

    The assumption is correctness of that source and Qiskit's reference semantics,
    not an independently proved algorithm specification or hardware observation.
    """
    native = qasm2.loads(source.decode() if isinstance(source, bytes) else source, include_path=(),
        custom_instructions=(qasm2.CustomInstruction('cswap', 0, 3, CSwapGate, builtin=True),
                             qasm2.CustomInstruction('swap', 0, 2, SwapGate, builtin=True),
                             qasm2.CustomInstruction('cp', 1, 2, CPhaseGate, builtin=True)))
    native.remove_final_measurements(inplace=True)
    state = Statevector.from_instruction(native)
    if kind == 'measurement_distribution':
        return {'kind': kind, 'basis': 'Z', 'expected_probabilities': {
            k: float(v) for k, v in state.probabilities_dict().items() if v > 1e-14}, 'tolerance': .15}
    if kind == 'target_state':
        return {'kind': kind, 'amplitudes': [[float(z.real), float(z.imag)] for z in state.data],
                'fidelity_tolerance': .2, 'provenance': 'Trusted unmodified external QASM, independently parsed with Qiskit before mutation; canonical zero input'}
    if kind != 'pauli_expectations':
        raise ValueError('unsupported contract kind')
    labels = []
    n = native.num_qubits
    for i in range(1, 4**n):
        label = ''.join('IXYZ'[(i >> (2*j)) & 3] for j in range(n))
        value = float(np.real(state.expectation_value(Pauli(label))))
        if abs(value) >= .2:
            labels.append((label, value))
    # Strongest reference Paulis; complementary coverage is not guaranteed.
    selected = sorted(labels, key=lambda x: (-abs(x[1]), x[0]))[:12]
    return {'kind': kind, 'observables': [{'pauli': p, 'expected': v, 'tolerance': .2} for p, v in selected]}


def make_cases(entry, contract, seeds):
    reference = entry['circuit']
    gates = reference['gates']
    entangler = next((i for i, g in enumerate(gates) if len(g['qubits']) == 2), None)
    variants = [('clean', gates, {}, None),
                ('remove_first', gates[1:], {}, 0),
                ('remove_entangler', None if entangler is None else gates[:entangler] + gates[entangler+1:], {}, entangler),
                ('readout', gates, {'readout': .12}, None),
                ('gate_noise', gates, {'depolarizing': .03}, None),
                ('mixed', gates[1:], {'readout': .04, 'depolarizing': .01}, 0),
                ('low_shots', gates[1:], {}, 0)]
    if len(gates) < 32:
        variants.append(('terminal_phase', gates + [{'name': 'z', 'qubits': [0]}], {}, len(gates)))
    else:
        # Preserve the unsupported case, never silently shorten the external circuit.
        variants.append(('terminal_phase', None, {}, None))
    if contract['kind'] == 'target_state':
        variants.append(('global_phase_contract', gates, {}, None))
    cases = []
    for variant, candidate, noise, locus in variants:
        for seed in seeds:
            declared = copy.deepcopy(contract)
            if variant == 'global_phase_contract':
                v = np.array([complex(*a) for a in declared['amplitudes']]) * np.exp(2.1j)
                declared['amplitudes'] = [[float(z.real), float(z.imag)] for z in v]
            cases.append({'source_path': entry['source_path'], 'variant': variant, 'seed': seed,
                          'truth_locus': locus, 'contract': declared, 'environment': noise,
                          'circuit': None if candidate is None else {**copy.deepcopy(reference), 'gates': copy.deepcopy(candidate)},
                          'unsupported': ('reference contains no two-qubit gate' if variant == 'remove_entangler' else 'terminal edit would exceed 32-gate schema limit') if candidate is None else None})
    return cases


def evaluator_truth(circuit, contract, environment):
    """Evaluator-only oracle. Never passed to investigate_lab/recover or policies."""
    kind = contract['kind']
    if kind == 'target_state' and any(environment.values()):
        return {'exact_loss': None, 'contract_violated': None, 'oracle_scope': 'uncalibrated analysis channel; no common-state fidelity oracle'}
    rho = noisy_density(circuit.subject(), Noise.model_validate(environment))
    if kind == 'target_state':
        t = np.array([complex(*a) for a in contract['amplitudes']]); t /= np.linalg.norm(t)
        loss = 1 - float(np.real(np.vdot(t, rho.data @ t)))
        tol = contract['fidelity_tolerance']
    elif kind == 'measurement_distribution':
        probabilities = rho.probabilities()
        p = environment.get('readout', 0)
        if p:
            probabilities = np.array([sum(v * p**((i^j).bit_count()) * (1-p)**(circuit.n_qubits-(i^j).bit_count())
                for j, v in enumerate(probabilities)) for i in range(len(probabilities))])
        loss = .5 * sum(abs(v - contract['expected_probabilities'].get(format(i, f'0{circuit.n_qubits}b'), 0))
                         for i, v in enumerate(probabilities))
        tol = contract['tolerance']
    else:
        # Analysis-gate noise depends on the basis; evaluate each operational
        # setting separately, rather than inventing a shared noisy state.
        from qfault.lab import measurement_circuit
        deviations = []
        for obs in contract['observables']:
            label = obs['pauli']; setting = label.replace('I', 'Z')
            analyzed = measurement_circuit(circuit.subject(), setting)
            rr = noisy_density(analyzed, Noise.model_validate(environment))
            z = ''.join('I' if c == 'I' else 'Z' for c in label)
            expectation = float(np.real(rr.expectation_value(Pauli(z))))
            expectation *= (1-2*environment.get('readout', 0))**sum(c != 'I' for c in label)
            deviations.append(abs(expectation-obs['expected']) / obs['tolerance'])
        loss, tol = max(deviations), 1.
    return {'exact_loss': max(0., loss), 'contract_violated': bool(loss > tol + 1e-10),
            'oracle_scope': 'Trusted original reference contract; exact simulated operational expectations evaluated separately from analyst'}


def summarize(rows):
    out = {}
    for key in sorted({r['kind'] + '/' + r['policy'] for r in rows}):
        sub = [r for r in rows if r['kind'] + '/' + r['policy'] == key]
        good = [r for r in sub if not r.get('error') and r.get('category') != 'UNSUPPORTED']
        pos = [r for r in good if r.get('contract_violated') is True]
        neg = [r for r in good if r.get('contract_violated') is False]
        detection = lambda rs: sum(r['category'] == 'SIGNIFICANT_DISCREPANCY' for r in rs)
        out[key] = {'runs': len(sub), 'architectures': len({r['source_path'] for r in sub}),
            'observable_violations': len(pos), 'detected_violations': detection(pos),
            'missed_or_unresolved_violations': len(pos)-detection(pos), 'oracle_nonviolations': len(neg),
            'false_alarms': detection(neg), 'unresolved': sum(r['category'] == 'INSUFFICIENT_EVIDENCE' for r in good),
            'uncheckable_model': sum(r.get('contract_violated') is None for r in good),
            'outcomes': dict(Counter(r['category'] for r in sub)),
            'attribution': dict(Counter(r.get('attribution', 'NOT_APPLICABLE') for r in good)),
            'total_shots': sum(r.get('shots', 0) for r in sub),
            'total_executions': sum(r.get('evaluations', 0) for r in sub),
            'runtime_seconds': sum(r.get('runtime_seconds', 0) for r in sub),
            'by_architecture': {p: {'runs': len(rs), 'observable_violations': sum(r.get('contract_violated') is True for r in rs),
                'detected_violations': detection([r for r in rs if r.get('contract_violated') is True]),
                'false_alarms': detection([r for r in rs if r.get('contract_violated') is False]),
                'outcomes': dict(Counter(r['category'] for r in rs)),
                'shots': sum(r.get('shots', 0) for r in rs)}
                for p in sorted({r['source_path'] for r in sub})
                for rs in [[r for r in sub if r['source_path'] == p]]}}
    return out


def frozen_protocol():
    corpus = json.loads(CORPUS.read_text())
    return {'name': 'external-qasmbench-v1', 'source_revision': git('rev-parse', 'HEAD'),
        'source_sha256_normalized_lf': source_hashes(), 'dataset_revision': corpus['source_repo_sha'],
        'corpus_sha256': digest(corpus), 'policies': POLICIES, 'seeds': SEEDS, 'budget': BUDGET,
        'contracts': 'Original QASM parsed independently before mutation; zero input. Qiskit trusted reference oracle. Z distribution tol .15; top12 nonidentity Pauli |expectation|>=.2 tol .2; target infidelity tol .2.',
        'variants': ['clean', 'remove_first', 'remove_entangler', 'readout=.12', 'gate_noise=.03', 'mixed(remove_first, readout=.04, gate=.01)', 'low_shots(64 batch/128 total)', 'terminal_z_q0 (unsupported if 32 gates)', 'target global phase=2.1'],
        'recovery': {'variants': ['clean', 'remove_first', 'terminal_phase', 'readout', 'gate_noise'],
            'contract': 'pauli_expectations', 'policies': ['conservative', 'point_discrepancy', 'no_repair'],
            'max_candidates': 32, 'screen_shots': 2048, 'verification_shots': 4096,
            'max_shots': 200000, 'max_evaluations': 160, 'max_seconds': 120,
            'operators': ['remove', 'replace', 'angle', 'reassign', 'insert'],
            'palette': ['h', 'x', 'z', 'cx', 'cz'], 'angles': [0., pi/2, -pi/2, pi],
            'positions': 'all; no truth locus provided', 'criterion': 'fresh candidate upper normalized loss<=1 and fresh original lower>candidate upper'},
        'measurement_mode': 'measurement_only; no hidden truth or candidate state passed to analyst',
        'statistics': 'Per-investigation alpha=.01, existing union bounds; descriptive run and architecture aggregates only. Seeds are not independent architectures. No population confidence interval, bootstrap, or superiority claim.',
        'success': 'Detection compared against exact operational contract violation. No discrepancy does not establish equivalence. Attribution stays ambiguous. Recovery success covers only declared claims and one input.',
        'time_limit': '120 seconds per recovery, checked between jobs; each diagnostic bounded by 16 executions of at most5 qubits32 gates',
        'artifacts': 'exclusive output; ArtifactStore per run, verified export; reports.jsonl.gz full exports; summary.json including compact per-run outcomes/costs/failure taxonomy',
        'exclusions': corpus['summary'], 'hardware': 'NOT_TESTED',
        'policy_compatibility': 'Template threshold not defined for arbitrary contracts; complementary_schedule is the existing simple predetermined baseline. No invented threshold comparator.'}


def failure_taxonomy(row, result):
    if row.get('unsupported'): return 'UNSUPPORTED_MUTATION'
    if row.get('error'): return 'ENVIRONMENT_OR_EXECUTION_FAILURE'
    if row.get('contract_violated') is None: return 'UNCALIBRATED_MEASUREMENT_MODEL'
    if row['variant'] in ('remove_first', 'remove_entangler', 'terminal_phase', 'mixed') and not row['contract_violated']:
        return 'FAULT_UNOBSERVABLE_OR_WITHIN_CONTRACT_TOLERANCE'
    if row['category'] == 'SIGNIFICANT_DISCREPANCY': return 'DETECTED_CONTRACT_DISCREPANCY'
    if row['contract_violated']:
        return result['diagnosis'].get('stop', {}).get('code', 'FINITE_SHOT_UNRESOLVED')
    return 'NO_FALSE_VIOLATION'


def run(split, out):
    protocol = json.loads(PROTOCOL.read_text()) if split == 'holdout' else frozen_protocol()
    if split == 'holdout':
        if source_hashes() != protocol['source_sha256_normalized_lf']:
            raise RuntimeError('Frozen scientific sources differ; do not run this holdout')
        if git('status', '--porcelain', '--', *SOURCES, 'benchmarks/external/qasmbench', 'configs/external-validation-protocol.json'):
            raise RuntimeError('Commit protocol and scientific sources before final evaluation')
    corpus = json.loads(CORPUS.read_text())
    if digest(corpus) != protocol['corpus_sha256']:
        raise RuntimeError('Frozen corpus mismatch')
    from scripts.retrieve_external_sources import verify_sources
    verify_sources()
    for entry in corpus['entries']:
        if entry['status'] == 'eligible':
            check_source(ROOT / 'benchmarks/external/qasmbench' / entry['source_path'], entry['sha256'])
    exclusive_output(out)
    store = ArtifactStore(out / 'investigations')
    rows, recovery_rows = [], []
    start = perf_counter()
    with gzip.open(out / 'reports.jsonl.gz', 'wb') as archive:
        for entry in corpus['entries']:
            if entry['status'] != 'eligible' or entry['split'] != split: continue
            raw = check_source(ROOT / 'benchmarks/external/qasmbench' / entry['source_path'], entry['sha256'])
            for kind, policies in POLICIES.items():
                declared = reference_contract(raw, kind)
                for case in make_cases(entry, declared, SEEDS[split]):
                    for policy in policies:
                        row = {k: case[k] for k in ['source_path', 'variant', 'seed', 'truth_locus', 'unsupported']}
                        row.update(kind=kind, policy=policy, error=None)
                        if case['unsupported']:
                            row.update(category='UNSUPPORTED', failure_taxonomy='UNSUPPORTED_MUTATION'); rows.append(row); continue
                        result = None
                        try:
                            c = CustomCircuit.model_validate(case['circuit'])
                            truth = evaluator_truth(c, declared, case['environment'])
                            budget = {**BUDGET, **({'batch_shots': 64, 'max_shots': 128} if case['variant'] == 'low_shots' else {})}
                            # Exact truth is deliberately absent from this request and call.
                            result = investigate_lab(LabRequest.model_validate({**budget, 'circuit': case['circuit'],
                                'contract': case['contract'], 'backend': 'aer', 'diagnostic_mode': 'measurement_only',
                                'environment': case['environment'], 'policy': policy, 'seed': case['seed']}))
                            assert not result['privileged_operations']
                            result['evaluation_truth'] = {**truth, 'source_path': case['source_path'], 'variant': case['variant'], 'truth_locus': case['truth_locus']}
                            eid = store.save(result); report = store.export(eid)
                            assert verify_export(report)['valid']
                            archive.write(canonical(report) + b'\n')
                            row.update(truth, experiment_id=eid, manifest_digest=digest(report['manifest']),
                                category=result['diagnosis']['category'], attribution=result['diagnosis']['attribution']['status'],
                                shots=result['cost']['shots'], evaluations=result['cost']['evaluations'],
                                runtime_seconds=result['cost']['runtime_seconds'], basis_gates=result['cost']['basis_gates'],
                                resource_actions=result['cost']['actions'],
                                candidate_resources=resources(c.subject()),
                                shot_weighted_two_qubit_gates=sum(a['shots']*a['resources'].get('two_qubit_gates', 0) for a in result['cost']['actions']),
                                shot_weighted_depth=sum(a['shots']*a['resources'].get('depth', 0) for a in result['cost']['actions']),
                                fidelity_interval=result['target_evidence']['fidelity_bound'] if result['target_evidence'] else None)
                            if kind == 'target_state' and truth['exact_loss'] is not None:
                                lo, hi = row['fidelity_interval']; f = 1-truth['exact_loss']
                                row['fidelity_interval_covers'] = lo-1e-10 <= f <= hi+1e-10
                            row['failure_taxonomy'] = failure_taxonomy(row, result)
                        except Exception as exc:
                            row.update(category='ERROR', error=repr(exc), failure_taxonomy='ENVIRONMENT_OR_EXECUTION_FAILURE')
                        rows.append(row)
                if kind != 'pauli_expectations': continue
                for case in make_cases(entry, declared, SEEDS[split]):
                    if case['variant'] not in protocol['recovery']['variants'] or case['unsupported']: continue
                    for policy in protocol['recovery']['policies']:
                        row = {k: case[k] for k in ['source_path', 'variant', 'seed', 'truth_locus']}
                        row.update(policy=policy, error=None)
                        try:
                            spec = protocol['recovery']
                            request = {k: spec[k] for k in ['max_candidates', 'screen_shots', 'verification_shots', 'max_shots', 'max_evaluations', 'max_seconds']}
                            result = recover(RecoveryRequest.model_validate({**request, 'circuit': case['circuit'], 'contract': declared,
                                'backend': 'aer', 'environment': case['environment'], 'seed': case['seed'], 'selection_policy': policy,
                                'edits': {'operators': spec['operators'], 'palette': spec['palette'], 'angles': spec['angles']}}))
                            assert not result['privileged_operations']
                            result['evaluation_truth'] = {'source_path': case['source_path'], 'variant': case['variant'], 'truth_locus': case['truth_locus']}
                            eid = store.save(result); report = store.export(eid); assert verify_export(report)['valid']
                            archive.write(canonical(report) + b'\n')
                            original, control = result['original_evidence'], result['readout_control']
                            row.update(status=result['status'], experiment_id=eid, manifest_digest=digest(report['manifest']),
                                detected=bool(original and original['loss_interval'][0] > 1),
                                eligible=bool(original and original['loss_interval'][0] > 1 and control and not control['significant']),
                                selected=bool(result['selected_candidate']), plausible_loci=result['localization']['plausible_loci'],
                                true_locus_covered=case['truth_locus'] in result['localization']['plausible_loci'] if case['truth_locus'] is not None else None,
                                plausible_candidates=sum(c['plausible'] for c in result['ranked_candidates']),
                                causal_origin=result['localization']['causal_origin'],
                                cost={k: v for k, v in result['cost'].items() if k != 'actions'},
                                verification_status=result['verification']['status'])
                        except Exception as exc:
                            row.update(status='ERROR', error=repr(exc))
                        recovery_rows.append(row)
            print('completed', entry['source_path'], 'diagnostic', len(rows), 'recovery', len(recovery_rows), flush=True)
    summary = {'protocol': protocol, 'execution_revision': git('rev-parse', 'HEAD'), 'split': split,
        'software': {'python': platform.python_version(), 'qiskit': __import__('qiskit').__version__, 'aer': __import__('qiskit_aer').__version__, 'numpy': np.__version__, 'scipy': __import__('scipy').__version__, 'pydantic': __import__('pydantic').__version__, 'platform': platform.platform()},
        'architecture_count': len({r['source_path'] for r in rows}), 'summaries': summarize(rows),
        'failure_taxonomy': dict(Counter(r['failure_taxonomy'] for r in rows)),
        'recovery_summaries': {p: {'runs': len(rs), 'architectures': len({r['source_path'] for r in rs}),
            'eligible': sum(r.get('eligible', False) for r in rs), 'selected': sum(r.get('selected', False) for r in rs),
            'outcomes': dict(Counter(r['status'] for r in rs)),
            'noise_only_proposals': sum(r.get('selected', False) for r in rs if r['variant'] in ('readout', 'gate_noise')),
            'generated_candidates': sum(r.get('cost', {}).get('generated_candidates', 0) for r in rs),
            'tested_candidates': sum(r.get('cost', {}).get('tested_candidates', 0) for r in rs),
            'shots': sum(r.get('cost', {}).get('shots', 0) for r in rs),
            'executions': sum(r.get('cost', {}).get('evaluations', 0) for r in rs),
            'searched_truth_cases': sum(bool(r.get('plausible_loci')) and r['truth_locus'] is not None for r in rs),
            'true_locus_covered': sum(r.get('true_locus_covered') is True for r in rs)}
            for p in protocol['recovery']['policies'] for rs in [[r for r in recovery_rows if r['policy'] == p]]},
        'rows': rows, 'recovery_rows': recovery_rows,
        'raw_exports': {'file': 'reports.jsonl.gz', 'sha256': hashlib.sha256((out/'reports.jsonl.gz').read_bytes()).hexdigest(), 'count': sum(r.get('error') is None and r.get('category') != 'UNSUPPORTED' for r in rows) + sum(r.get('error') is None for r in recovery_rows)},
        'runtime_seconds': perf_counter()-start,
        'runtime_scope': 'Per-run runtime is engine execution/analysis only; total runtime additionally includes evaluator oracle, preprocessing, artifact verification and archive writes. Depth/gate costs are logical simulated proxies, not device costs.'}
    summary['digest'] = digest(summary)
    (out / 'summary.json').write_bytes(canonical(summary))
    print(json.dumps({'architectures': summary['architecture_count'], 'diagnostic_runs': len(rows), 'recovery_runs': len(recovery_rows), 'seconds': summary['runtime_seconds'], 'failures': sum(bool(r.get('error')) for r in rows + recovery_rows)}), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--split', choices=SEEDS, default='development')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.freeze:
        with PROTOCOL.open('xb') as stream: stream.write(canonical(frozen_protocol()))
        print('Frozen', PROTOCOL.name)
    elif args.out:
        run(args.split, args.out)
    else:
        parser.error('--out is required for execution')


if __name__ == '__main__': main()
