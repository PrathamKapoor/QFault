"""Release smoke test against a running `qfault serve` (default http://127.0.0.1:8000).

Real Chromium, real API, real Qiskit Aer execution; no mocked responses. Checks: health, served landing and
workbench, one Aer custom-circuit investigation, verified export and absence of page errors.
Usage: python -m scripts.release_smoke [--base URL] [--out DIR]
"""
import argparse
import json
import time
import urllib.request
from math import sqrt
from pathlib import Path
from playwright.sync_api import expect, sync_playwright
from qfault.storage import verify_export

S = 1 / sqrt(2)
BELL = {"schema_version": 1, "name": "Bell pair", "n_qubits": 2, "input": {"kind": "computational_basis", "bitstring": "00"},
        "gates": [{"name": "h", "qubits": [0]}, {"name": "cx", "qubits": [0, 1]}]}
TARGET = {"kind": "target_state", "fidelity_tolerance": 0.2, "amplitudes": [[S, 0], [0, 0], [0, 0], [S, 0]]}


def wait_health(base, timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with urllib.request.urlopen(base + "/api/health", timeout=5) as r:
                if r.status == 200:
                    return json.loads(r.read())
        except OSError:
            time.sleep(1)
    raise SystemExit("server did not become healthy within %ss" % timeout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    ap.add_argument("--out")
    a = ap.parse_args()
    health = wait_health(a.base)
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        page = ctx.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(a.base + "/")
        expect(page.locator(".entry__stage canvas[data-engine]")).to_be_attached(timeout=30000)
        engine = page.locator(".entry__stage canvas").get_attribute("data-engine")
        page.get_by_role("button", name="Open workbench", exact=True).first.click()
        expect(page.get_by_role("heading", name="Quantum investigation intelligence.")).to_be_visible(timeout=30000)
        response = ctx.request.post(a.base + "/api/lab/investigations",
                                    data={"circuit": BELL, "contract": TARGET, "backend": "aer"}, timeout=180000)
        assert response.status == 201, response.text()
        inv = response.json()
        assert inv["executions"][0]["backend_name"].startswith("qiskit_aer"), inv["executions"][0]["backend_name"]
        assert inv["diagnosis"]["category"] == "NO_SIGNIFICANT_DISCREPANCY", inv["diagnosis"]["category"]
        report = ctx.request.get(a.base + f"/api/experiments/{inv['experiment_id']}/report").json()
        assert verify_export(report)["valid"]
        page.goto(a.base + "/#/lab/" + inv["experiment_id"])
        expect(page.get_by_role("heading", name="Target-state evidence")).to_be_visible(timeout=30000)
        browser.close()
    assert not errors, errors
    result = {"health": health.get("status"), "qiskit": health.get("qiskit"), "aer": health.get("aer", {}).get("version"),
              "hero_engine": engine, "experiment_id": inv["experiment_id"], "category": inv["diagnosis"]["category"],
              "fidelity_bound": inv["target_evidence"]["fidelity_bound"], "shots": inv["cost"]["shots"], "export_valid": True}
    if a.out:
        Path(a.out).mkdir(parents=True, exist_ok=True)
        (Path(a.out) / "release-smoke.json").write_text(json.dumps(result, indent=1))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
