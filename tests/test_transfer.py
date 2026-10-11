"""Transfer evidence must stay inside artifacts and match frozen manifest references."""
import json
import pytest
from scripts.package_submission import collect_evidence
from qfault.workflow import RunRequest,investigate
from qfault.storage import ArtifactStore

def test_transfer_rejects_evidence_outside_artifacts(tmp_path):
    source=tmp_path/'summary.json';source.write_text(json.dumps({'rows':[{'artifact_path':'../private.json'}]}))
    with pytest.raises(ValueError,match='outside artifacts'):collect_evidence(tmp_path,[source])

def test_transfer_rejects_changed_manifest_reference(tmp_path):
    store=ArtifactStore(tmp_path/'artifacts'/'investigations')
    eid=store.save(investigate(RunRequest(shots=128,max_shots=256,max_evaluations=2,recover=False)))
    source=tmp_path/'summary.json';source.write_text(json.dumps({'rows':[{'artifact_path':f'artifacts/investigations/{eid}','manifest_digest':'0'*64}]}))
    with pytest.raises(ValueError,match='manifest digest'):collect_evidence(tmp_path,[source])
