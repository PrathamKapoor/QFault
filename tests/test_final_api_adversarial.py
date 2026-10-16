"""Independent final gate: exact ASGI bytes, real Aer, and disposable artifacts.

Transport-only tests use a collecting ASGI endpoint, not a simulated quantum
backend. Every investigation executed here runs the real Qiskit Aer backend.
"""
import asyncio
import copy
import json
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest
from fastapi.testclient import TestClient
from starlette.requests import ClientDisconnect

from qfault.api import RequestBodyLimit, create_app
from qfault.evidence import canonical, digest
from qfault.storage import ArtifactStore, verify_export
from qfault.workflow import RunRequest, investigate


def transport(headers=(), chunks=(b"{}",), disconnect=False):
    """No HTTP client can normalize headers or synthesize Content-Length here."""
    forwarded, sent = [], []
    messages = [
        {"type": "http.request", "body": part,
         "more_body": i < len(chunks)-1 or disconnect}
        for i, part in enumerate(chunks)
    ]
    if disconnect:
        messages.append({"type": "http.disconnect"})

    async def downstream(scope, receive, send):
        while True:
            message = await receive()
            forwarded.append(message)
            if message["type"] == "http.disconnect" or not message.get("more_body"):
                break
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    async def receive():
        return messages.pop(0) if messages else {"type": "http.disconnect"}

    async def send(message):
        sent.append(message)

    asyncio.run(RequestBodyLimit(downstream)(
        {"type": "http", "path": "/api/experiments", "headers": list(headers)}, receive, send))
    return sent[0]["status"], forwarded


@pytest.mark.parametrize("headers", [(), ((b"content-length", b"65536"),),
    ((b"content-length", b"1"),), ((b"transfer-encoding", b"chunked"),)])
def test_transport_exact_65536_bytes_permitted(headers):
    status, forwarded = transport(headers, (b"{}"+b" "*32766, b" "*32768))
    assert status == 200
    assert sum(len(m.get("body", b"")) for m in forwarded) == 65536


@pytest.mark.parametrize("headers", [(), ((b"content-length", b"65537"),),
    ((b"content-length", b"1"),), ((b"transfer-encoding", b"chunked"),)])
def test_transport_65537_actual_bytes_rejected(headers):
    status, forwarded = transport(headers, (b"x"*32768, b"x"*32769))
    assert status == 413
    assert forwarded == []


@pytest.mark.parametrize("length", [b"bad", b"-1", b"+2", b"2.0", b" 2", b"2 ",
    b"2, 3", b"", b"9"*21, b"\xff"])
def test_transport_malformed_content_length_rejected(length):
    assert transport(((b"content-length", length),))[0] == 400


@pytest.mark.parametrize("lengths", [(b"70000", b"2"), (b"2", b"70000"),
    (b"bad", b"2"), (b"2", b"bad"), (b"3", b"2"), (b"2", b"3")])
def test_transport_conflicting_duplicate_content_lengths_rejected(lengths):
    status, forwarded = transport(tuple((b"content-length", v) for v in lengths))
    assert status == 400
    assert forwarded == []


def test_transport_partial_disconnect_preserved_without_hang():
    status, forwarded = transport((), (b'{"shots":',), disconnect=True)
    assert status == 200  # collecting endpoint only; no JSON parser or science here
    assert forwarded[-1]["type"] == "http.disconnect"


def test_partial_disconnected_api_request_never_creates_investigation(tmp_path):
    messages = [{"type": "http.request", "body": b'{"shots":64', "more_body": True},
                {"type": "http.disconnect"}]
    sent = []

    async def receive():
        return messages.pop(0) if messages else {"type": "http.disconnect"}

    async def send(message):
        sent.append(message)

    async def invoke():
        try:
            await create_app(tmp_path)({"type": "http", "asgi": {"version": "3.0"},
                "http_version": "1.1", "method": "POST", "scheme": "http",
                "path": "/api/experiments", "raw_path": b"/api/experiments", "root_path": "",
                "query_string": b"", "headers": [(b"content-type", b"application/json")],
                "client": ("127.0.0.1", 12345), "server": ("127.0.0.1", 8000)}, receive, send)
        except ClientDisconnect:
            pass

    asyncio.run(invoke())
    assert not any(m.get("status") == 201 for m in sent)
    assert not list(tmp_path.glob("experiment_*"))


@pytest.mark.parametrize("body", [b"{", b"", b"[]", b"null", b'{"shots":NaN}',
    b'{"shots":Infinity}', b'{"shots":-Infinity}', b'{"shots":1e309}',
    b'{"shots":-1e309}', b"["*1100 + b"]"*1100],
    ids=["malformed", "empty", "array", "null", "nan", "infinity", "negative-infinity",
         "overflow", "negative-overflow", "deep"])
def test_invalid_json_input_fails_as_client_error(tmp_path, body):
    response = TestClient(create_app(tmp_path), raise_server_exceptions=False).post(
        "/api/experiments", content=body, headers={"content-type": "application/json"})
    assert response.status_code in {400, 422}, response.text
    assert not list(tmp_path.glob("experiment_*"))


@pytest.mark.parametrize("content_type", [None, "application/problem+json", "text/plain",
    "Application/JSON", "APPLICATION/PROBLEM+JSON", "application/json; charset=utf-8"])
@pytest.mark.parametrize("body", [b'{"shots":NaN}', b'{"shots":1e309}'], ids=["nan", "overflow"])
def test_nonfinite_media_type_variants_fail_as_client_error(tmp_path, content_type, body):
    headers = {"content-type": content_type} if content_type else {}
    response = TestClient(create_app(tmp_path), raise_server_exceptions=False).post(
        "/api/experiments", content=body, headers=headers)
    assert response.status_code in {400, 415, 422}, response.text


@pytest.mark.parametrize("body", [b'"\\ud800"', b'{"family":"\\ud800"}',
    b'{"\\ud800":1}', b'{"family":"\\udc00"}'],
    ids=["root-high-surrogate", "value-high-surrogate", "key-high-surrogate", "value-low-surrogate"])
def test_unpaired_unicode_surrogates_fail_as_client_error(tmp_path, body):
    response = TestClient(create_app(tmp_path), raise_server_exceptions=False).post(
        "/api/experiments", content=body, headers={"content-type": "application/json"})
    assert response.status_code in {400, 422}, response.text


@pytest.mark.parametrize("content_type", ["text/plain", "application/octet-stream"])
def test_invalid_utf8_non_json_body_fails_as_client_error(tmp_path, content_type):
    response = TestClient(create_app(tmp_path), raise_server_exceptions=False).post(
        "/api/experiments", content=b"\xff", headers={"content-type": content_type})
    assert response.status_code in {400, 415, 422}, response.text


def test_exact_65536_json_api_body_executes_real_aer(tmp_path):
    body = canonical({"shots": 64, "max_shots": 128, "max_evaluations": 2,
                      "recover": False, "backend": "aer"})
    body += b" "*(65536-len(body))
    client = TestClient(create_app(tmp_path))
    response = client.post("/api/experiments", content=body, headers={"content-type": "application/json"})
    assert response.status_code == 201, response.text
    assert all("aer" in e["backend_name"].lower() for e in response.json()["executions"])
    assert response.json()["cost"]["shots"] == 128
    assert client.post("/api/experiments", content=body+b" ",
                       headers={"content-type": "application/json"}).status_code == 413


@pytest.mark.parametrize("patch", [{"family": "invalid"}, {"family": "bell", "n_qubits": 3},
    {"shots": True}, {"shots": 0}, {"max_shots": 127, "shots": 64},
    {"max_evaluations": 601}, {"seed": 2**32}, {"unexpected": 1},
    {"diagnostic_mode": "measurement_only", "recover": True}])
def test_api_invalid_run_contracts_and_budgets_fail_before_execution(tmp_path, patch):
    response = TestClient(create_app(tmp_path)).post("/api/experiments", json=patch)
    assert response.status_code == 422
    assert not list(tmp_path.glob("experiment_*"))


def lab_body():
    return {"circuit": {"schema_version": 1, "name": "gate bounds", "n_qubits": 2,
        "input": {"kind": "computational_basis", "bitstring": "00"}, "gates": []},
        "contract": {"kind": "measurement_distribution", "expected_probabilities": {"00": 1},
        "tolerance": .1}, "backend": "aer"}


@pytest.mark.parametrize("change", ["outside_qubit", "gate_arity", "missing_angle",
    "too_many_gates", "contract_width", "bad_probability_sum", "budget"])
def test_api_invalid_custom_circuit_and_contract_rejected(tmp_path, change):
    body = lab_body()
    if change == "outside_qubit": body["circuit"]["gates"] = [{"name": "h", "qubits": [2]}]
    if change == "gate_arity": body["circuit"]["gates"] = [{"name": "cx", "qubits": [0]}]
    if change == "missing_angle": body["circuit"]["gates"] = [{"name": "rx", "qubits": [0]}]
    if change == "too_many_gates": body["circuit"]["gates"] = [{"name": "h", "qubits": [0]}]*33
    if change == "contract_width": body["contract"]["expected_probabilities"] = {"000": 1}
    if change == "bad_probability_sum": body["contract"]["expected_probabilities"] = {"00": .5}
    if change == "budget": body.update(batch_shots=64, max_shots=127)
    assert TestClient(create_app(tmp_path)).post("/api/lab/validate", json=body).status_code == 422


@pytest.mark.parametrize("identifier", ["not-an-id", "experiment_"+"g"*32,
    "experiment_"+"0"*31, "challenge_"+"a"*32])
def test_invalid_artifact_ids_return_client_error(tmp_path, identifier):
    client = TestClient(create_app(tmp_path))
    for suffix in ["", "/report", "/verification"]:
        assert client.get("/api/experiments/"+identifier+suffix).status_code == 422
    assert client.get("/api/experiments/experiment_"+"0"*32).status_code == 404


def test_busy_execution_returns_409_and_lock_recovers(tmp_path, monkeypatch):
    import qfault.api as api
    entered, release = Event(), Event()
    real_investigate = api.investigate

    def paused_real_execution(request):
        entered.set()
        assert release.wait(10), "test coordination did not release execution"
        return real_investigate(request)

    monkeypatch.setattr(api, "investigate", paused_real_execution)
    client = TestClient(create_app(tmp_path))
    body = {"shots": 64, "max_shots": 128, "max_evaluations": 2, "recover": False, "backend": "aer"}
    with ThreadPoolExecutor(1) as executor:
        first = executor.submit(client.post, "/api/experiments", json=body)
        assert entered.wait(5)
        try:
            assert client.post("/api/experiments", json=body).status_code == 409
            assert client.post("/api/lab/investigations", json=lab_body()).status_code == 409
            assert client.post("/api/lab/recoveries", json=lab_body()).status_code == 409
        finally:
            release.set()
        assert first.result(timeout=20).status_code == 201
    assert client.post("/api/experiments", json=body).status_code == 201


@pytest.fixture(scope="module")
def real_aer_record():
    return investigate(RunRequest(shots=64, max_shots=128, max_evaluations=2,
                                  recover=False, backend="aer"))


@pytest.mark.parametrize("field", ["counts", "execution_status", "candidate", "cost"])
def test_artifact_tampering_covers_science_and_cost(tmp_path, real_aer_record, field):
    store = ArtifactStore(tmp_path)
    eid = store.save(copy.deepcopy(real_aer_record))
    path = tmp_path/eid/"investigation.json"
    data = json.loads(path.read_bytes())
    if field == "counts": data["executions"][0]["output_counts"]["00"] = 999999
    if field == "execution_status": data["executions"][0]["execution_status"] = "FORGED"
    if field == "candidate": data["candidate"]["gates"] = []
    if field == "cost": data["cost"]["shots"] = 0
    path.write_bytes(canonical(data))
    client = TestClient(create_app(tmp_path))
    assert not client.get(f"/api/experiments/{eid}/verification").json()["valid"]
    assert client.get(f"/api/experiments/{eid}").status_code == 422
    assert client.get(f"/api/experiments/{eid}/report").status_code == 422


@pytest.mark.parametrize("change", ["deleted_manifest", "deleted_evaluation", "corrupt_json",
    "truncated_json", "extra_review", "invalid_manifest_membership"])
def test_artifact_missing_and_unindexed_review_fail_closed(tmp_path, real_aer_record, change):
    store = ArtifactStore(tmp_path)
    eid = store.save(copy.deepcopy(real_aer_record))
    folder = tmp_path/eid
    if change == "deleted_manifest": (folder/"manifest.json").unlink()
    if change == "deleted_evaluation": (folder/"evaluation.json").unlink()
    if change == "corrupt_json": (folder/"investigation.json").write_bytes(b"{bad}")
    if change == "truncated_json":
        path = folder/"investigation.json"
        path.write_bytes(path.read_bytes()[:-20])
    if change == "extra_review": (folder/("review_"+"a"*32+".json")).write_bytes(b"{}")
    if change == "invalid_manifest_membership":
        path = folder/"manifest.json"
        value = json.loads(path.read_bytes()); value["artifacts"]["extra.json"] = "0"*64
        path.write_bytes(canonical(value))
    assert not store.verify(eid)["valid"]
    client = TestClient(create_app(tmp_path))
    assert client.get(f"/api/experiments/{eid}").status_code == 422


@pytest.mark.parametrize("key", ["investigation", "evaluation", "manifest", "reviews"])
def test_truncated_export_members_rejected(tmp_path, real_aer_record, key):
    store = ArtifactStore(tmp_path)
    exported = store.export(store.save(copy.deepcopy(real_aer_record)))
    exported.pop(key)
    assert not verify_export(exported)["valid"]


def test_declared_hash_only_limit_allows_complete_rehash_and_unrelated_file(tmp_path, real_aer_record):
    store = ArtifactStore(tmp_path)
    eid = store.save(copy.deepcopy(real_aer_record))
    folder = tmp_path/eid
    (folder/"unindexed-note.txt").write_text("not part of the declared artifact set")
    assert store.verify(eid)["valid"]
    report = store.export(eid)
    report["investigation"]["cost"]["shots"] = 0
    report["manifest"]["artifacts"]["investigation.json"] = digest(report["investigation"])
    verified = verify_export(report)
    assert verified["valid"]
    assert "no external trust anchor" in verified["assurance"]


@pytest.mark.parametrize("kind,route", [("custom_circuit", "investigations"),
    ("counterfactual_recovery", "recoveries")])
@pytest.mark.parametrize("replay", [{"request": {}}, {}, None, {"request": []}])
def test_rehashed_invalid_replay_returns_safe_error(tmp_path, real_aer_record, kind, route, replay):
    # A complete rehash is outside authenticity assurance; safe failure remains necessary.
    record = copy.deepcopy(real_aer_record)
    record.update(investigation_kind=kind, replay=replay)
    store = ArtifactStore(tmp_path)
    eid = store.save(record)
    assert store.verify(eid)["valid"]
    response = TestClient(create_app(tmp_path), raise_server_exceptions=False).post(
        f"/api/lab/{route}/{eid}/replay")
    assert response.status_code == 422, response.text
