import copy
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from qfault.storage import ArtifactStore
from qfault.workflow import investigate,RunRequest
from qfault.api import create_app


def test_store_tamper_and_restore(tmp_path):
    store=ArtifactStore(tmp_path)
    r=investigate(RunRequest(shots=512,recover=False))
    eid=store.save(r)
    assert store.verify(eid)["valid"]
    path=tmp_path/eid/"investigation.json"
    original=path.read_bytes()
    data=json.loads(original)
    data["executions"][0]["output_counts"]["00"]+=1
    path.write_text(json.dumps(data),encoding="utf8")
    assert not store.verify(eid)["valid"]
    path.write_bytes(original)
    assert store.verify(eid)["valid"]
    assert "evaluation_truth" not in store.load(eid)
    with pytest.raises(FileExistsError): store.save(r)


def test_store_rejects_traversal_and_missing(tmp_path):
    store=ArtifactStore(tmp_path)
    with pytest.raises(ValueError): store.load("../elsewhere")
    with pytest.raises(FileNotFoundError): store.load("experiment_"+"a"*32)


def test_review_is_bound_and_append_only(tmp_path):
    store=ArtifactStore(tmp_path)
    eid=store.save(investigate(RunRequest(shots=512,recover=False)))
    store.review(eid,"PrathamKapoor","acknowledge","Checked raw measurements")
    assert store.verify(eid)["valid"]
    assert len(store.load(eid)["human_decisions"])==1
    review=next((tmp_path/eid).glob("review_*.json"))
    data=json.loads(review.read_text())
    data["record"]["reason"]="changed"
    review.write_text(json.dumps(data),encoding="utf8")
    assert not store.verify(eid)["valid"]


def test_api_real_quantum_workflow(tmp_path):
    client=TestClient(create_app(tmp_path))
    assert client.get("/api/health").status_code==200
    assert len(client.get("/api/circuits").json())==3
    assert client.post("/api/experiments",json={"shots":0}).status_code==422
    response=client.post("/api/experiments",json={"family":"bell","scenario":"remove","seed":2})
    assert response.status_code==201,response.text
    r=response.json()
    eid=r["experiment_id"]
    assert r["recovery"]["verification"]["verified_status"]=="VERIFIED"
    assert client.get(f"/api/experiments/{eid}/verification").json()["valid"]
    exported=client.get(f"/api/experiments/{eid}/report")
    assert exported.status_code==200 and "attachment" in exported.headers["content-disposition"]
    assert "investigation" in exported.json()
    assert client.post(f"/api/experiments/{eid}/review",json={"reviewer":"PrathamKapoor","action":"acknowledge","reason":"Reviewed"}).status_code==201
    assert client.get("/api/experiments/experiment_"+"f"*32).status_code==404
    assert client.get("/").status_code==200


def test_invalid_distribution_rejected():
    from qfault.diagnostics import total_variation
    with pytest.raises(ValueError): total_variation({"00":1},1,{"00":.5})


@pytest.mark.parametrize("bad",[None,[],{"artifacts":[]}])
def test_malformed_manifest_fails_closed(tmp_path,bad):
    store=ArtifactStore(tmp_path)
    eid=store.save(investigate(RunRequest(shots=128,recover=False)))
    (tmp_path/eid/"manifest.json").write_text(json.dumps(bad),encoding="utf8")
    assert not store.verify(eid)["valid"]
