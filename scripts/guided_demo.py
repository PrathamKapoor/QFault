"""Build declared demonstration inputs or execute the same real API workflow."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from time import perf_counter

from qfault.evidence import canonical, digest
from qfault.lab import CustomCircuit, LabRequest
from qfault.counterfactual import RecoveryRequest
from qfault.qasm_import import from_qasm2
from qfault.storage import verify_export
from scripts.external_demo import example, request_json

ROOT=Path(__file__).resolve().parents[1]


def build_inputs():
    """Reference contracts are computed by the existing distinct-source oracle."""
    ex=example()
    raw=(ROOT/'benchmarks/external/qasmbench'/ex['source_path']).read_bytes()
    reference=from_qasm2(raw,name='QASMBench QRNG reference',strip_terminal_measurements=True)
    candidate=CustomCircuit.model_validate({**reference.model_dump(mode='json'),
        'name':'QASMBench QRNG with controlled terminal Z',
        'gates':[g.model_dump(mode='json') for g in reference.gates]+[{'name':'z','qubits':[0]}]})
    common={'circuit':candidate.model_dump(mode='json'),'backend':'aer','seed':4191}
    requests={}
    for key,contract in [('z',ex['distribution']),('phase',ex['complementary'])]:
        body=LabRequest.model_validate({**common,'contract':contract,'policy':'fixed'}).model_dump(mode='json')
        requests[key]={'kind':'investigation','endpoint':'/api/lab/investigations','body':body,'validation_body':body}
    recovery=RecoveryRequest.model_validate({**common,'contract':ex['complementary'],'max_candidates':32}).model_dump(mode='json')
    for key,changes in [('recovery',{}),('noise',{'environment':{'readout':.3}}),
                         ('budget',{'max_shots':128,'screen_shots':64,'verification_shots':64})]:
        body=RecoveryRequest.model_validate({**recovery,**changes}).model_dump(mode='json')
        validation=LabRequest.model_validate({**common,'contract':body['contract'],'environment':body['environment'],
            'policy':'fixed','batch_shots':body['screen_shots'],'max_shots':min(body['max_shots'],100000),
            'max_evaluations':min(body['max_evaluations'],100),'max_looks':1}).model_dump(mode='json')
        requests[key]={'kind':'recovery','endpoint':'/api/lab/recoveries','body':body,'validation_body':validation}
    source={'repository':'https://github.com/pnnl/QASMBench','revision':ex['source_revision'],
        'path':ex['source_path'],'sha256':hashlib.sha256(raw).hexdigest(),
        'url':f"https://github.com/pnnl/QASMBench/blob/{ex['source_revision']}/{ex['source_path']}",
        'license_url':f"https://github.com/pnnl/QASMBench/blob/{ex['source_revision']}/LICENSE"}
    return {'schema_version':1,'id':'qasmbench-qrng-phase-v1','title':'A phase error that Z measurements cannot see',
        'source':source,'reference':{'circuit':reference.model_dump(mode='json'),'circuit_id':reference.circuit_id,
            'contract_provenance':'Trusted original external QASM parsed separately with Qiskit before mutation. Its correctness is an assumption, not independently proved here.'},
        'candidate':{'circuit':candidate.model_dump(mode='json'),'circuit_id':candidate.circuit_id,
            'controlled_mutation':{'operator':'append','gate':{'name':'z','qubits':[0]},'index':4}},
        'contracts':{'z':ex['distribution'],'complementary':ex['complementary']},'requests':requests,
        'scope':'Four-qubit product-state QRNG, computational input 0000. A transparent observability example, not representative recovery accuracy or hardware validation.',
        'feasibility_scope':'Validation previews measurable contract claims. Recovery independently reserves fresh original/candidate and control resources at admission; a valid preview never guarantees a repair.'}


def run(base,out):
    from urllib.parse import urlsplit
    parsed=urlsplit(base)
    if parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost'):
        raise ValueError('Use the running local loopback API')
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    inputs=request_json(base,'/api/guided-demo')
    (out/'demonstration-inputs.json').write_bytes(canonical(inputs))
    rows=[]
    expected={'z':'NO_SIGNIFICANT_DISCREPANCY','phase':'SIGNIFICANT_DISCREPANCY',
        'recovery':'VERIFIED_UNDER_DECLARED_CONTRACT','noise':'NOISE_CONTROL_ABSTENTION','budget':'INSUFFICIENT_BUDGET'}
    for key in expected:
        spec=inputs['requests'][key];start=perf_counter()
        validation=request_json(base,'/api/lab/validate',spec['validation_body'])
        if not validation['valid']:raise ValueError('Demonstration validation failed')
        result=request_json(base,spec['endpoint'],spec['body'])
        report=request_json(base,f"/api/experiments/{result['experiment_id']}/report")
        checked=verify_export(report)
        if not checked['valid']:raise ValueError('Demonstration export failed consistency verification')
        (out/(key+'-report.json')).write_bytes(canonical(report))
        rows.append({'stage':key,'experiment_id':result['experiment_id'],
            'status':result.get('status',result['diagnosis']['category']),'cost':result['cost'],
            'elapsed_seconds':perf_counter()-start,'export_verified':True})
    summary={'schema_version':1,'fixture_id':inputs['id'],'input_digest':digest(inputs),
        'rows':rows,'passed':all(r['status']==expected[r['stage']] for r in rows),
        'scope':'Fresh real execution of declared demonstration inputs; not a frozen performance evaluation or recorded result disguised as live.'}
    (out/'summary.json').write_bytes(canonical(summary));print(json.dumps(summary,indent=2))
    return 0 if summary['passed'] else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',default='http://127.0.0.1:8000')
    parser.add_argument('--out',type=Path)
    parser.add_argument('--write-inputs',type=Path,help='Developer input generation only; no measurements')
    args=parser.parse_args()
    if args.write_inputs:
        args.write_inputs.parent.mkdir(parents=True,exist_ok=True)
        with args.write_inputs.open('xb') as stream:stream.write(canonical(build_inputs()))
        return 0
    if not args.out:parser.error('--out is required for real execution')
    return run(args.base.rstrip('/'),args.out)


if __name__=='__main__':raise SystemExit(main())
