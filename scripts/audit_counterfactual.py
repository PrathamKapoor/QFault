"""Recount frozen recovery artifacts and reconstruct evidence from counts.

The audit does not import the recovery decision or observation implementations.
Optional replay explicitly executes the integrated engine into new artifacts.
"""
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
from itertools import combinations
import json
from math import log, sqrt
from pathlib import Path
import random
import subprocess

import numpy as np
from qiskit.quantum_info import SparsePauliOp
from qfault.evidence import digest, canonical
from qfault.storage import ArtifactStore, verify_export

ROOT = Path(__file__).resolve().parents[1]
VERIFIED = 'VERIFIED_UNDER_DECLARED_CONTRACT'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def near(a, b, message):
    require(np.allclose(a, b, atol=1e-9, rtol=1e-9), message)


def parity(counts, pauli):
    return sum(v * (-1)**sum(bit == '1' and p != 'I' for bit, p in zip(k, pauli))
               for k, v in counts.items()) / sum(counts.values())


@lru_cache(maxsize=64)
def target_terms(amplitudes):
    # Only the DECLARED target is decomposed. No candidate state is constructed.
    t = np.array([complex(*z) for z in amplitudes]); t /= np.linalg.norm(t)
    d = len(t)
    op = SparsePauliOp.from_operator(np.outer(t, t.conj()))
    terms = {p: float(a.real*d) for p, a in zip(op.paulis.to_labels(), op.coeffs) if set(p) != {'I'}}
    omitted = d*d - 1 - len(terms)
    mass = max(0., d-1-sum(a*a for a in terms.values()))
    return terms, sqrt(omitted*mass), mass


def independent_labels(labels):
    basis = {}
    for label in labels:
        bits = [p in 'XY' for p in label] + [p in 'ZY' for p in label]
        v = sum(int(b) << i for i, b in enumerate(bits))
        while v:
            pivot = v.bit_length()-1
            if pivot not in basis:
                basis[pivot] = v
                break
            v ^= basis[pivot]
    return len(basis) == len(labels)


def evidence_loss(evidence, contract, n, alpha):
    events = evidence['events']
    radius = lambda shots: sqrt(2*log(2/alpha)/shots)
    if contract['kind'] == 'target_state':
        terms, omitted_abs, omitted_sq = target_terms(tuple(tuple(z) for z in contract['amplitudes']))
        estimates, radii = {}, {}
        for ev in events:
            for term in ev['group']['terms']:
                require(all(p == 'I' or p == setting for p, setting in zip(term, ev['group']['setting'])), 'invalid Pauli setting')
                require(term not in estimates, 'repeated target look')
                estimates[term] = parity(ev['counts'], term)
                radii[term] = radius(ev['shots'])
                near([estimates[term], radii[term]],
                     [evidence['expectations'][term]['estimate'], evidence['expectations'][term]['radius']], 'target expectation/radius')
        lo = hi = 1.
        upper = 1.; abs_left, sq_left = omitted_abs, omitted_sq
        stabilizer = len(terms) == 2**n-1 and all(abs(abs(a)-1) < 1e-9 for a in terms.values())
        generators = []
        for p, a in terms.items():
            if p not in estimates:
                abs_left += abs(a); sq_left += a*a
                continue
            b, r = estimates[p], radii[p]
            bl, bu = max(-1., b-r), min(1., b+r)
            lo += min(a*bl, a*bu); hi += max(a*bl, a*bu)
            upper = min(upper, 1-(max(0., abs(b-a)-r)/2)**2)
            if stabilizer:
                gl, gu = (bl, bu) if a > 0 else (-bu, -bl)
                upper = min(upper, (1+gu)/2)
                generators.append((p, gl))
        slack = min(abs_left, sqrt(sq_left*(2**n-1)))
        L, U = max(0., (lo-slack)/2**n), min(1., (hi+slack)/2**n, upper)
        # Exhaustively check small-corpus independent generator sets; not the engine's greedy selector.
        for subset in combinations(generators, n):
            if independent_labels([p for p, _ in subset]):
                L = max(L, 1-sum((1-gl)/2 for _, gl in subset))
        near(evidence['claims'][0]['interval'], [L, U], 'target fidelity bound')
        tol = contract['fidelity_tolerance']
        result = [(1-U)/tol, (1-L)/tol]
    else:
        lows, highs = [], []
        claims = evidence['claims']
        for claim in claims:
            relevant = [ev for ev in events if claim['claim_id'] in ev['group']['claims']]
            require(len(relevant) <= 1, 'repeated non-target look')
            tol = claim['tolerance']
            if not relevant:
                lows.append(0.); highs.append(2/tol)
                continue
            ev = relevant[0]; shots = ev['shots']
            if contract['kind'] == 'pauli_expectations':
                label = claim['pauli']
                require(all(p == 'I' or p == setting for p, setting in zip(label, ev['group']['setting'])), 'invalid Pauli setting')
                value, rad = parity(ev['counts'], label), radius(shots)
                delta = abs(value-claim['expected'])
            else:
                expected = contract['expected_probabilities']
                value = sum(abs(ev['counts'].get(format(i, f'0{n}b'), 0)/shots-expected.get(format(i, f'0{n}b'), 0)) for i in range(2**n))/2
                rad = min(1., sqrt(log((2.**(2**n)-2)/alpha)/(2*shots)))
                delta = value
            near([claim['estimate'], claim['uncertainty_radius']], [value, rad], 'claim estimate/radius')
            near(claim['interval'], [value-rad, value+rad], 'claim interval')
            lows.append(max(0., delta-rad)/tol); highs.append((delta+rad)/tol)
        result = [max(lows), max(highs)]
    near(evidence['loss_interval'], result, 'normalized discrepancy interval')
    return result


def audit_record(record):
    cfg = record['configuration']; contract = cfg['contract']; n = cfg['circuit']['n_qubits']
    count = len(target_terms(tuple(tuple(z) for z in contract['amplitudes']))[0]) if contract['kind'] == 'target_state' else len(contract.get('observables', [0]))
    alpha = cfg['alpha_total']/((cfg['max_candidates']+3)*max(1, count)+1)
    near(record['statistical_design']['alpha_per_interval'], alpha, 'multiplicity allocation')
    executions = record['executions']; index = {ev['execution_id']: ev for ev in executions}
    require(len(index) == len(executions), 'duplicate execution ID')
    require(len({ev['seed'] for ev in executions}) == len(executions), 'repeated seeds')
    require(not record['privileged_operations'], 'privileged operation in measured recovery')
    used_events = set()

    def inspect(evidence, phase, subject):
        if evidence is None:
            return None
        for event in evidence['events']:
            eid = event['execution_id']
            require(eid not in used_events and eid in index, 'measurement samples reused or absent')
            used_events.add(eid); raw = index[eid]
            require(raw['recovery_phase'] == phase and raw['subject_circuit_id'] == subject, 'measurement provenance/phase mismatch')
            require(raw['output_counts'] == event['counts'] and raw['executed_shots'] == event['shots'] == sum(event['counts'].values()), 'count/shot mismatch')
            require(raw['seed'] == event['seed'], 'event seed mismatch')
        return evidence_loss(evidence, contract, n, alpha)

    original = inspect(record['original_evidence'], 'observation', record['circuit_id'])
    candidates = record['ranked_candidates']
    for c in candidates:
        inspect(c['evidence'], 'screening', c['circuit_id'])
    plausible = [c for c in candidates if not any(other['evidence']['loss_interval'][1] < c['evidence']['loss_interval'][0] for other in candidates)]
    require([c['candidate_id'] for c in candidates] == [c['candidate_id'] for c in sorted(candidates, key=lambda c: (c['evidence']['loss_interval'][1], c['candidate_id']))], 'candidate display order')
    require(all(c['plausible'] == (c in plausible) for c in candidates), 'plausible candidate set')
    loci = sorted({e['index'] for c in plausible for e in [c['edit'], *c.get('equivalent_edits', [])]})
    require(loci == record['localization']['plausible_loci'], 'plausible locus set')
    control = record['readout_control']
    if control:
        raw = index[control['execution_id']]; used_events.add(control['execution_id'])
        require(raw['recovery_phase'] == 'control' and control['counts'] == raw['output_counts'], 'control provenance')
        tv = 1-control['counts'].get('0'*n, 0)/control['shots']
        rad = min(1., sqrt(log((2.**(2**n)-2)/alpha)/(2*control['shots'])))
        near([control['tv'], control['radius']], [tv, rad], 'readout control')
        require(control['significant'] == (tv-rad > .1), 'readout decision')
    selected = record['selected_candidate']; improvement = None
    if selected:
        selection = record['selection']; verification = record['verification']
        require(selected == next(c for c in candidates if c['candidate_id'] == selected['candidate_id']), 'selected record differs')
        require(selection['digest'] == digest({k:v for k,v in selection.items() if k != 'digest'}), 'selection binding')
        require(selection['screening_digest'] == digest({'original':record['original_evidence'], 'ranked':candidates}), 'screening binding')
        require(selection['frozen_before_verification'], 'selection not frozen')
        generation_order = {c['candidate_id']:i for i,c in enumerate(record['generation']['candidates'])}
        tested_order = sorted(candidates, key=lambda c:generation_order[c['candidate_id']])
        policy = cfg['selection_policy']
        pool = [c for c in plausible if c['evidence']['loss_interval'][1] < original[0]]
        if policy == 'first_admissible':
            pool = tested_order[:1]
        elif policy == 'random':
            pool = random.Random(cfg['seed'] ^ 0xCAFE).sample(tested_order, 1)
        elif policy == 'point_discrepancy':
            pool = sorted(tested_order, key=lambda c:c['evidence']['point_loss'])[:1]
        require(bool(pool), 'selected candidate without admissible selection pool')
        chosen = min(pool, key=lambda c:(c['resources']['two_qubit_gates'], c['resources']['depth'], c['resources']['gates'], c['candidate_id']))
        require(chosen['candidate_id'] == selected['candidate_id'], 'selection rule differs')
        ol, ou = inspect(verification['original'], 'verification_original', record['circuit_id'])
        cl, cu = inspect(verification['candidate'], 'verification_candidate', selected['circuit_id'])
        improvement = [ol-cu, ou-cl]
        near([verification['improvement_lower'], verification['improvement_upper']], improvement, 'improvement interval')
        verdict = 'INCONCLUSIVE' if ol > ou or cl > cu else VERIFIED if cu <= 1 and ol > cu else 'REJECTED' if cl > 1 or ou < cl else 'INCONCLUSIVE'
        require(record['status'] == verification['status'] == verdict, 'fresh verification decision')
        phases = [ev['recovery_phase'] for ev in executions]
        first_fresh = min(i for i, p in enumerate(phases) if p.startswith('verification_'))
        require(all(not p.startswith('verification_') for p in phases[:first_fresh]) and all(p.startswith('verification_') for p in phases[first_fresh:]), 'screening after confirmation')
    require(used_events == set(index), 'unaccounted executions')
    shots = sum(ev['executed_shots'] for ev in executions)
    require(shots == record['cost']['shots'] <= cfg['max_shots'], 'total shot budget')
    require(len(executions) == record['cost']['evaluations'] <= cfg['max_evaluations'], 'evaluation budget')
    phase_shots = {p:sum(ev['executed_shots'] for ev in executions if ev['recovery_phase'] == p) for p in {ev['recovery_phase'] for ev in executions}}
    require(phase_shots == record['cost']['phase_shots'], 'phase shot ledger')
    require(record['cost']['tested_candidates'] == len(candidates), 'tested candidate accounting')
    require(record['localization']['causal_origin'] == 'NOT_IDENTIFIED', 'unsupported causal claim')
    return {'status': record['status'], 'shots': shots, 'evaluations': len(executions), 'selected': bool(selected),
            'contract_type': contract['kind'], 'plausible_loci': loci, 'plausible_candidates': len(plausible),
            'operation_count': len(cfg['circuit']['gates']), 'improvement_interval': improvement,
            'discrepancy': bool(original and original[0] > 1),
            'eligible': bool(original and original[0] > 1 and control and not control['significant'])}


def source_provenance(protocol, revision):
    result = {}
    for name, expected in protocol['source_sha256'].items():
        current = (ROOT/name).read_bytes()
        blob = subprocess.check_output(['git', '-c', 'safe.directory='+ROOT.as_posix(), 'show', revision+':'+name], cwd=ROOT)
        lf = blob.replace(b'\r\n', b'\n')
        matches = [style for style, b in [('LF', lf), ('CRLF', lf.replace(b'\n', b'\r\n'))] if hashlib.sha256(b).hexdigest() == expected]
        require(bool(matches), 'frozen hash not reproduced from revision: '+name)
        result[name] = {'raw_bytes_match': hashlib.sha256(current).hexdigest() == expected,
            'normalized_source_match': current.replace(b'\r\n', b'\n') == lf,
            'current_lf_sha256': hashlib.sha256(current.replace(b'\r\n', b'\n')).hexdigest(),
            'evaluation_lf_sha256': hashlib.sha256(lf).hexdigest(),
            'evaluation_line_endings': matches}
    return result


def audit(summary_path, output, replay_root=None):
    raw_bytes = summary_path.read_bytes(); frozen = json.loads(raw_bytes)
    root = summary_path.parent/'investigations'; store = ArtifactStore(root)
    provenance = source_provenance(frozen['protocol'], frozen['revision'])
    from qfault.recovery_corpus import cases
    case_list = list(cases('holdout'))
    require(digest(case_list) == frozen['protocol']['cases_sha256'], 'frozen corpus mismatch')
    case_map = {c['case_id']:c for c in case_list}
    require({(r['case_id'],r['policy']) for r in frozen['rows']} == {(c,p) for c in case_map for p in frozen['protocol']['policies']}, 'missing or extra case/policy')
    require(len(frozen['rows']) == len(case_map)*len(frozen['protocol']['policies']), 'duplicate case/policy')
    def declared_subset(declared, actual):
        if isinstance(declared, dict):
            for k,v in declared.items():
                require(k in actual, 'missing declared configuration field')
                declared_subset(v, actual[k])
        elif isinstance(declared, list):
            require(len(declared) == len(actual), 'declared sequence length mismatch')
            for d,a in zip(declared,actual):
                declared_subset(d,a)
        else:
            require(declared == actual, 'configuration differs from frozen case')
    rows, replayed = [], 0
    replay_store = ArtifactStore(replay_root) if replay_root else None
    for row in frozen['rows']:
        eid = row['experiment_id']; bundle = store.export(eid)
        require(verify_export(bundle)['valid'], 'manifest verification: '+eid)
        require(digest(bundle['manifest']) == row['manifest_sha256'], 'summary manifest binding')
        record = bundle['investigation']; audited = audit_record(record)
        case = case_map[row['case_id']]
        for field in ('truth_locus','family','variant'):
            require(row[field] == case[field], 'evaluator label differs from frozen corpus')
        declared_subset(case['request'], record['configuration'])
        require(record['configuration']['selection_policy'] == row['policy'], 'policy differs from raw configuration')
        for field in ('status','selected','eligible','discrepancy','plausible_loci'):
            require(row[field] == audited[field], 'row recount mismatch: '+field)
        require(row['cost']['shots'] == audited['shots'] and row['cost']['evaluations'] == audited['evaluations'], 'summary cost mismatch')
        rows.append({**audited, 'case_id':row['case_id'], 'policy':row['policy'], 'family':row['family'],
                     'variant':row['variant'], 'truth_locus':row['truth_locus']})
        if replay_store:
            from qfault.counterfactual import RecoveryRequest, recover
            replay = recover(RecoveryRequest.model_validate(record['replay']['request']))
            require(replay['status'] == record['status'], 'replay decision differs')
            require([(e['seed'], e['output_counts']) for e in replay['executions']] == [(e['seed'], e['output_counts']) for e in record['executions']], 'replay counts differ')
            replay_id = replay_store.save(replay)
            require(replay_store.verify(replay_id)['valid'], 'replay manifest')
            replayed += 1
    policies = {}
    for policy in sorted({r['policy'] for r in rows}):
        selected = [r for r in rows if r['policy'] == policy]
        groups = {}
        for dimension in ('contract_type','variant','family'):
            groups[dimension] = {value: {'cases': len(part), 'outcomes': dict(Counter(r['status'] for r in part)),
                'shots': sum(r['shots'] for r in part)} for value in sorted({r[dimension] for r in selected})
                for part in [[r for r in selected if r[dimension] == value]]}
        truth = [r for r in selected if r['truth_locus'] is not None]
        searched_truth = [r for r in truth if r['plausible_loci']]
        policies[policy] = {'cases':len(selected), 'outcomes':dict(Counter(r['status'] for r in selected)),
            'shots':sum(r['shots'] for r in selected), 'evaluations':sum(r['evaluations'] for r in selected),
            'proposals':sum(r['selected'] for r in selected), 'eligible':sum(r['eligible'] for r in selected),
            'plausible_locus_size_histogram_all':dict(Counter(len(r['plausible_loci']) for r in selected)),
            'searched_truth_cases':len(searched_truth), 'truth_cases':len(truth),
            'covered_truth_cases':sum(r['truth_locus'] in r['plausible_loci'] for r in truth),
            'searched_truth_locus_size_histogram':dict(Counter(len(r['plausible_loci']) for r in searched_truth)),
            'searched_truth_mean_loci':sum(len(r['plausible_loci']) for r in searched_truth)/max(1,len(searched_truth)),
            'searched_truth_mean_fraction_of_operations':sum(len(r['plausible_loci'])/r['operation_count'] for r in searched_truth)/max(1,len(searched_truth)),
            'breakdowns':groups}
        previous = frozen['summaries'][policy]
        for new, old in [('outcomes','outcomes'),('shots','total_shots'),('evaluations','evaluations'),('proposals','proposals'),('eligible','eligible')]:
            require(policies[policy][new] == previous[old], 'aggregate recount differs: '+policy+'/'+new)
    report = {'source_summary_sha256':hashlib.sha256(raw_bytes).hexdigest(), 'evaluation_revision':frozen['revision'],
        'audit_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'audit_revision':subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'scientific_source_provenance':provenance, 'verified_manifests':len(rows), 'replayed_records':replayed,
        'improvement_units':'Dimensionless reduction in worst-claim discrepancy divided by contract tolerance: [L_original-U_candidate, U_original-L_candidate]. Not fidelity or TV.',
        'policies':policies, 'rows':rows}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as f:
        f.write(canonical(report))
    print(json.dumps({k:v for k,v in report.items() if k not in ('rows','policies')},indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--replay-root', type=Path)
    args = parser.parse_args()
    audit(args.source, args.out, args.replay_root)
