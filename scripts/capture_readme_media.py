"""Capture the README screenshots from a running QFAULT server (genuine UI, real Qiskit Aer executions).

Usage: python -m scripts.capture_readme_media --base http://127.0.0.1:8012 --out docs/media
Run against a server with a throwaway store (QFAULT_ARTIFACTS) so captures do not touch real records.
"""
import argparse
from math import sqrt
from pathlib import Path
from playwright.sync_api import expect, sync_playwright

S = 1 / sqrt(2)
BELL = {"schema_version": 1, "name": "Bell pair (missing CX)", "n_qubits": 2,
        "input": {"kind": "computational_basis", "bitstring": "00"}, "gates": [{"name": "h", "qubits": [0]}]}
BELL_TARGET = {"kind": "target_state", "fidelity_tolerance": 0.2, "amplitudes": [[S, 0], [0, 0], [0, 0], [S, 0]],
               "provenance": "analytic Bell state"}
FLIP = {"schema_version": 1, "name": "Measured bit inversion", "n_qubits": 2,
        "input": {"kind": "computational_basis", "bitstring": "00"}, "gates": [{"name": "x", "qubits": [0]}]}
ZERO_TARGET = {"kind": "target_state", "amplitudes": [[1.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]], "fidelity_tolerance": 0.2}


def shot(page, path):
    page.evaluate("document.activeElement && document.activeElement.blur()")
    page.screenshot(path=str(path), type="jpeg", quality=82)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--base", default="http://127.0.0.1:8012"); ap.add_argument("--out", default="docs/media")
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page = ctx.new_page(); errors = []; page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(a.base + "/")
        expect(page.locator(".entry.entry--hero-live .entry__stage canvas[data-engine='webgl']")).to_be_attached(timeout=30000)
        page.mouse.move(1300, 880); page.wait_for_timeout(4500)
        shot(page, out / "qfault-hero.jpg")

        inv = ctx.request.post(a.base + "/api/lab/investigations",
                               data={"circuit": BELL, "contract": BELL_TARGET, "backend": "aer"}, timeout=180000)
        assert inv.status == 201, inv.text(); inv = inv.json()
        assert inv["diagnosis"]["category"] == "SIGNIFICANT_DISCREPANCY"
        page.goto(a.base + "/#/lab/" + inv["experiment_id"])
        expect(page.get_by_role("heading", name="Target-state evidence")).to_be_visible(timeout=30000)
        page.get_by_role("heading", name="Target-state evidence").scroll_into_view_if_needed()
        page.evaluate("window.scrollBy(0, -120)"); page.wait_for_timeout(400)
        shot(page, out / "custom-circuit-lab.jpg")

        rec = ctx.request.post(a.base + "/api/lab/recoveries", data={"circuit": FLIP, "contract": ZERO_TARGET, "backend": "aer"}, timeout=300000)
        assert rec.status == 201, rec.text(); rec = rec.json()
        page.goto(a.base + "/#/lab/recovery/" + rec["experiment_id"])
        expect(page.get_by_role("heading", name="Counterfactual recovery", exact=True)).to_be_visible(timeout=30000)
        page.wait_for_timeout(400)
        shot(page, out / "measured-recovery.jpg")
        assert not errors, errors
        browser.close()
    print({"investigation": inv["experiment_id"], "investigation_category": inv["diagnosis"]["category"],
           "recovery": rec["experiment_id"], "recovery_status": rec["status"]})


if __name__ == "__main__":
    main()
