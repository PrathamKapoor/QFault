"""Real native-circuit phase demonstration through the same local API and engine."""
import argparse
import copy
import json
from pathlib import Path
from qiskit import QuantumCircuit
from qfault.qasm_import import from_qiskit
from qfault.evidence import canonical
from qfault.storage import verify_export
from scripts.external_demo import request_json


def example():
    candidate=QuantumCircuit(2);candidate.h(0);candidate.z(0)
    circuit=from_qiskit(candidate,name='Native phase discrepancy').model_dump(mode='json')
    # Independent analytic declaration: the reference behavior is |0>|+>.
    z={'kind':'measurement_distribution','basis':'Z','expected_probabilities':{'00':.5,'01':.5},'tolerance':.2}
    phase={'kind':'pauli_expectations','observables':[{'pauli':'IX','expected':1.,'tolerance':.2}]}
    return circuit,z,phase


def run(base,out):
    from urllib.parse import urlsplit
    parsed=urlsplit(base)
    if parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost'):
        raise ValueError('Use the local loopback API')
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    circuit,z,phase=example();rows=[]
    for name,contract in [('inadequate_z',z),('phase_sensitive',phase)]:
        request={'circuit':circuit,'contract':contract,'backend':'aer','policy':'fixed','seed':7241}
        result=request_json(base,'/api/lab/investigations',request)
        report=request_json(base,f"/api/experiments/{result['experiment_id']}/report")
        assert verify_export(report)['valid']
        (out/(name+'-report.json')).write_bytes(canonical(report))
        rows.append({'stage':name,'status':result['diagnosis']['category'],'cost':result['cost'],'experiment_id':result['experiment_id']})
    recovery={'circuit':circuit,'contract':phase,'backend':'aer','seed':7241,'max_candidates':12}
    for name,changes in [('fresh_recovery',{}),('noise_abstention',{'environment':{'readout':.3}}),
        ('insufficient_budget',{'max_shots':128,'screen_shots':64,'verification_shots':64})]:
        result=request_json(base,'/api/lab/recoveries',{**recovery,**changes})
        report=request_json(base,f"/api/experiments/{result['experiment_id']}/report")
        assert verify_export(report)['valid']
        assert report['investigation']['circuit']==circuit
        (out/(name+'-report.json')).write_bytes(canonical(report))
        rows.append({'stage':name,'status':result['status'],'cost':result['cost'],'experiment_id':result['experiment_id']})
    expected=['NO_SIGNIFICANT_DISCREPANCY','SIGNIFICANT_DISCREPANCY','VERIFIED_UNDER_DECLARED_CONTRACT','NOISE_CONTROL_ABSTENTION','INSUFFICIENT_BUDGET']
    summary={'fixture':'native-phase-demo-v1','seed':7241,'rows':rows,'expected':expected,
        'passed':[r['status'] for r in rows]==expected,
        'scope':'One independent |0>|+> behavior contract; Z-only cannot see relative phase. Fresh repair is not causal identification or full-unitary equivalence.'}
    (out/'summary.json').write_bytes(canonical(summary));print(json.dumps(summary,indent=2))
    return 0 if summary['passed'] else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--base',default='http://127.0.0.1:8000');parser.add_argument('--out',required=True)
    args=parser.parse_args();return run(args.base.rstrip('/'),args.out)


if __name__=='__main__':raise SystemExit(main())
