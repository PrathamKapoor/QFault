"""Validated presentation inputs, never a separate diagnostic engine."""
import hashlib
import json
from pathlib import Path

from .counterfactual import RecoveryRequest
from .interventions import generate
from .lab import CustomCircuit, LabRequest

ROOT=Path(__file__).resolve().parents[1]


def demo_catalog():
    path=ROOT/'examples/qrng-phase-demo.json'
    if path.stat().st_size>65536:raise ValueError('Demonstration input size exceeds limit')
    data=json.loads(path.read_bytes())
    if not isinstance(data,dict) or type(data.get('schema_version')) is not int or data['schema_version']!=1:
        raise ValueError('Unsupported demonstration input version')
    source_root=(ROOT/'benchmarks/external/qasmbench').resolve()
    source=(source_root/data['source']['path']).resolve()
    if not source.is_relative_to(source_root) or source.is_symlink() or source.stat().st_size>65536:
        raise ValueError('Unsafe demonstration source')
    if hashlib.sha256(source.read_bytes()).hexdigest()!=data['source']['sha256']:
        raise ValueError('Demonstration source digest mismatch')
    for role in ('reference','candidate'):
        circuit=CustomCircuit.model_validate(data[role]['circuit'])
        if circuit.circuit_id!=data[role]['circuit_id']:raise ValueError('Demonstration circuit identity mismatch')
    for spec in data['requests'].values():
        schema=LabRequest if spec['kind']=='investigation' else RecoveryRequest
        request=schema.model_validate(spec['body'])
        if request.circuit.circuit_id!=data['candidate']['circuit_id']:
            raise ValueError('Demonstration request candidate mismatch')
        LabRequest.model_validate(spec['validation_body'])
    recovery=RecoveryRequest.model_validate(data['requests']['recovery']['body'])
    data['preview']=generate(recovery.circuit,recovery.edits,recovery.max_candidates)
    data['preview']['scope']='Structural candidates only; no measurements, ranking, frozen selection or verification has occurred.'
    return data
