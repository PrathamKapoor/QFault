"""Explicit input builder for a source-qualified GHZ lesson, not an evaluation."""
import copy,hashlib,json
from pathlib import Path
from qfault.evidence import canonical
from qfault.qasm_import import from_qasm2
from qfault.lab import CustomCircuit,LabRequest
from qfault.counterfactual import RecoveryRequest
ROOT=Path(__file__).resolve().parents[1]

def build_inputs():
    old=json.loads((ROOT/'examples/qrng-phase-demo.json').read_bytes())
    source_path='small/cat_state_n4/cat_state_n4.qasm'
    entry=next(v for v in json.loads((ROOT/'configs/external-corpus.json').read_bytes())['entries'] if v['source_path']==source_path)
    raw=(ROOT/'benchmarks/external/qasmbench'/source_path).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==entry['sha256']
    reference=from_qasm2(raw,name='QASMBench four-qubit cat reference',strip_terminal_measurements=True)
    candidate=CustomCircuit.model_validate({**reference.model_dump(mode='json'),'name':'Cat reference with controlled terminal Z','gates':[*reference.model_dump(mode='json')['gates'],{'name':'z','qubits':[0]}]})
    # Independent analytical GHZ stabilizers, declared before any candidate execution.
    z={'kind':'measurement_distribution','basis':'Z','expected_probabilities':{'0000':.5,'1111':.5},'tolerance':.15}
    phase={'kind':'pauli_expectations','observables':[{'pauli':p,'expected':1.,'tolerance':.2} for p in ('XXXX','IIZZ','IZZI','ZZII')]}
    data=copy.deepcopy(old);data.update(id='qasmbench-cat-phase-v1',title='Entangled correlations and a hidden phase discrepancy',
        scope='Four-qubit GHZ entangling program from the pinned external corpus, input0000. Controlled development demonstration, not a new performance study or repair-rate claim.')
    data['source'].update(path=source_path,sha256=entry['sha256'],url=f"https://github.com/pnnl/QASMBench/blob/{entry['source_repo_sha']}/{source_path}")
    data['reference']={'circuit':reference.model_dump(mode='json'),'circuit_id':reference.circuit_id,
        'contract_provenance':'Analytical GHZ reference: (|0000>+|1111>)/sqrt(2), XXXX=+1 and adjacent ZZ=+1. Source imported separately; expected behavior is not inferred from the mutated candidate.'}
    data['candidate']={'circuit':candidate.model_dump(mode='json'),'circuit_id':candidate.circuit_id,'controlled_mutation':{'operator':'append','gate':{'name':'z','qubits':[0]},'index':4}}
    data['contracts']={'z':z,'complementary':phase}
    for key,spec in data['requests'].items():
        for field in ('body','validation_body'):
            spec[field]['circuit']=candidate.model_dump(mode='json');spec[field]['contract']=z if key=='z' else phase
        schema=LabRequest if spec['kind']=='investigation' else RecoveryRequest
        spec['body']=schema.model_validate(spec['body']).model_dump(mode='json')
        spec['validation_body']=LabRequest.model_validate(spec['validation_body']).model_dump(mode='json')
    return data

if __name__=='__main__':
    destination=ROOT/'examples/cat-phase-demo.json'
    with destination.open('xb') as stream:stream.write(canonical(build_inputs()))
