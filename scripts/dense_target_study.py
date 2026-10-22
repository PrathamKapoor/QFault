"""Development-only dense witness resource study; no production policy change."""
import argparse
import hashlib
import json
from math import isfinite,log,sqrt
from pathlib import Path

from qiskit.quantum_info import Statevector
from qfault.diagnostics import ExecutionBudget
from qfault.evidence import canonical
from qfault.lab import CustomCircuit,LabRequest,_Port,plan,parity_expectation
from qfault.quantum import Noise
from qfault.target import catalog,bounds,fidelity
from qfault.target_corpus import reference,declare_target,circuit


def allocate(weights,total):
    """Minimize sum w/sqrt(N) with fixed shots, 64<=N<=10000 per group.

    Lagrange multipliers give N proportional to w**(2/3); clipping satisfies
    KKT conditions. Integer rounding uses the largest exact marginal reduction.
    """
    if not weights or any(not isfinite(w) or w<=0 for w in weights) or not len(weights)*64<=total<=len(weights)*10000:
        raise ValueError('infeasible positive weights or bounded shot budget')
    lo,hi=1e-20,1e20
    for _ in range(160):
        multiplier=sqrt(lo*hi)
        sizes=[min(10000.,max(64.,(w/multiplier)**(2/3))) for w in weights]
        if sum(sizes)>total:lo=multiplier
        else:hi=multiplier
    sizes=[int(min(10000.,max(64.,(w/hi)**(2/3)))) for w in weights]
    while sum(sizes)<total:
        index=max((i for i,n in enumerate(sizes) if n<10000),
            key=lambda i:weights[i]*(1/sqrt(sizes[i])-1/sqrt(sizes[i]+1)))
        sizes[index]+=1
    return sizes


def run(out):
    out=Path(out)
    if out.exists():raise FileExistsError('choose a new output')
    bits,gates=reference('rotation_entangler',2) # declared DEVELOPMENT family only
    contract=declare_target('rotation_entangler',2,bits,gates)
    original=CustomCircuit.model_validate(circuit(2,bits,gates,'development reference'))
    request=LabRequest(circuit=original,contract=contract)
    cat=catalog(request.contract.amplitudes);groups=plan(2,request.contract)[1]
    coefficients=dict(cat['terms']);weights=[sum(abs(coefficients[p]) for p in g['terms'])/4 for g in groups]
    slot=.01/(len(cat['terms'])+1);rows=[]
    for total in (8192,32768):
        for seed in (301,302):
            for variant in ('clean','extra_z'):
                subject=original if variant=='clean' else CustomCircuit.model_validate({**original.model_dump(mode='json'),
                    'gates':[g.model_dump(mode='json') for g in original.gates]+[{'name':'z','qubits':[0]}]})
                for policy in ('uniform','coefficient_allocation'):
                    schedule=allocate([1.]*len(groups) if policy=='uniform' else weights,total)
                    records=[];budget=ExecutionBudget(total,len(groups))
                    port=_Port(subject.subject(),Noise(),budget,'aer',seed,records)
                    estimates={};radii={}
                    for group,shots in zip(groups,schedule):
                        ev=port.measure(group['setting'],shots,'dense_development')
                        for term in group['terms']:
                            estimates[term]=parity_expectation(ev['counts'],ev['shots'],term)
                            radii[term]=sqrt(2*log(2/slot)/shots)
                    lower,upper=bounds(cat,estimates,radii)
                    # Evaluator truth is computed only AFTER target-only allocation and measurements.
                    truth=fidelity(request.contract.vector(),Statevector.from_instruction(subject.subject().native()))
                    rows.append({'policy':policy,'budget':total,'seed':seed,'variant':variant,
                        'schedule':schedule,'lower':lower,'upper':upper,'oracle_fidelity':truth,
                        'covered':lower-1e-10<=truth<=upper+1e-10,'confirmed':lower>=.8,
                        'shots':budget.shots,'evaluations':budget.evaluations,'executions':records,
                        'uncertainty_envelope':sum(w*sqrt(2*log(2/slot)/n) for w,n in zip(weights,schedule))})
    result={'name':'dense-target-development-v1','scope':'One previously declared two-qubit development architecture, repeated seeds; NOT holdout/generalization or production-policy evaluation',
        'target':contract,'groups':groups,'alpha_total':.01,'alpha_slot':slot,
        'derivation':'One look for each catalog term plus control slot. Both schedules measure every same qubit-wise group once. Minimize sum_g w_g/sqrt(N_g) at fixed total via N_g proportional to w_g^(2/3), subject to per-job bounds. This minimizes an uncertainty proxy, not necessarily final clipped fidelity interval.',
        'rows':rows,'all_covered':all(r['covered'] for r in rows),
        'decision':'Do not adopt a new production policy from this small development study; report resource/bound tradeoff only.',
        'source_sha256_normalized_lf':hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n',b'\n')).hexdigest()}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('xb') as stream:stream.write(canonical(result))
    print(json.dumps({'rows':len(rows),'all_covered':result['all_covered'],
        'policies':{p:{'confirmed':sum(r['confirmed'] for r in rows if r['policy']==p),
            'cases':sum(r['policy']==p for r in rows)} for p in ('uniform','coefficient_allocation')}}))
    return 0 if result['all_covered'] else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True)
    args=parser.parse_args();return run(args.out)


if __name__=='__main__':raise SystemExit(main())
