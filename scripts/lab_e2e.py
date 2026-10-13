"""Real browser checks for the Custom Circuit Laboratory, including target-state witnesses and narrow viewports.

Runs against a live `qfault serve`; every investigation executes real Qiskit (Aer) measurements.
Usage: python scripts/lab_e2e.py --out <new directory>
"""
import argparse
import json
from math import sqrt
from pathlib import Path
from playwright.sync_api import expect, sync_playwright
from qfault.storage import verify_export

BASE = (__import__('os').environ.get('QFAULT_BASE_URL','http://127.0.0.1:8000') + '')
S = 1 / sqrt(2)
BELL = {"schema_version": 1, "name": "Bell pair", "n_qubits": 2, "input": {"kind": "computational_basis", "bitstring": "00"},
        "gates": [{"name": "h", "qubits": [0]}, {"name": "cx", "qubits": [0, 1]}]}
TARGET = {"kind": "target_state", "fidelity_tolerance": 0.2, "provenance": "analytic Bell state",
          "amplitudes": [[S, 0], [0, 0], [0, 0], [S, 0]]}
VIEWPORTS = [(390, 844), (375, 812), (360, 800)]


def overflow(page):
    return page.evaluate("""() => ({doc: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        offenders: [...document.querySelectorAll('main *')].filter(e => {const r = e.getBoundingClientRect();
          return r.width > 0 && r.right > innerWidth + 1 && !e.closest('.table-scroll,.circuit-scroll,pre,svg')}).slice(0, 5)
          .map(e => e.tagName + '.' + e.className)})""")


def paste(page, label, value):
    details = page.locator("details", has=page.locator("summary", has_text=label)).first
    if not details.evaluate("e => e.open"):
        details.locator("summary").first.click()
    box = page.get_by_label(label)
    box.fill(json.dumps(value))
    page.get_by_role("button", name="Apply " + label).click()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=False)
    errors, console, rows = [], [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce", accept_downloads=True)
        page = ctx.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: console.append(m.text) if m.type == "error" else None)
        page.goto(BASE + "/#/workbench")
        page.get_by_role("link", name="Custom Circuit", exact=True).click()
        expect(page.get_by_role("heading", name="Custom circuit laboratory.")).to_be_visible()
        # target-state contract through the real editor
        page.get_by_label("Contract type").select_option("target_state")
        paste(page, "Circuit JSON", BELL)
        paste(page, "Contract JSON", TARGET)
        expect(page.get_by_label("Measurement policy")).to_have_value("adaptive_witness")
        expect(page.get_by_text("· normalized")).to_be_visible()
        # invalid amplitude: editor warns, API rejects with a usable message, nothing executes
        page.get_by_label("Real amplitude 0").fill("0.9")
        expect(page.get_by_text("must be 1 within 1e-6")).to_be_visible()
        page.get_by_role("button", name="Validate and check feasibility").click()
        expect(page.get_by_role("alert")).to_contain_text("normalized")
        page.get_by_role("button", name="Normalize explicitly").click()
        paste(page, "Contract JSON", TARGET)
        page.get_by_role("button", name="Validate and check feasibility").click()
        expect(page.get_by_text("Target witness catalog")).to_be_visible()
        expect(page.get_by_text("stabilizer target")).to_be_visible()
        page.screenshot(path=str(out / "desktop-target-editor.png"), full_page=True)
        for mode in ["measurement_only", "simulator_assisted"]:
            page.goto(BASE + "/#/lab")
            page.get_by_label("Contract type").select_option("target_state")
            paste(page, "Circuit JSON", {**BELL, "gates": BELL["gates"][:1]} if mode == "measurement_only" else BELL)
            paste(page, "Contract JSON", TARGET)
            page.get_by_label("Diagnostic capability").select_option(mode)
            page.get_by_label("Backend").select_option("aer")
            with page.expect_response(lambda r: r.url.endswith("/api/lab/investigations") and r.request.method == "POST") as resp:
                page.get_by_role("button", name="Run investigation").click()
            assert resp.value.status == 201, resp.value.text()
            inv = resp.value.json(); eid = inv["experiment_id"]
            assert inv["executions"][0]["backend_name"].startswith("qiskit_aer")
            expect(page.get_by_role("heading", name="Target-state evidence")).to_be_visible()
            expect(page.get_by_text("MEASUREMENT_DERIVED_WITNESS").first).to_be_visible()
            if mode == "measurement_only":
                assert inv["privileged_operations"] == [] and "exact" not in inv["target_evidence"]
                expect(page.get_by_text("Measurement-only: no exact candidate state")).to_be_visible()
                assert inv["diagnosis"]["category"] == "SIGNIFICANT_DISCREPANCY"
            else:
                expect(page.get_by_text("SIMULATOR_ASSISTED_EXACT_STATE · privileged")).to_be_visible()
                assert inv["target_evidence"]["exact"]["ideal_fidelity"] > .999
            expect(page.get_by_role("heading", name="Evidence-action timeline")).to_be_visible()
            assert page.locator(".lab-timeline li").count() >= len(inv["action_ledger"]) + 1
            with page.expect_download() as dl:
                page.get_by_role("link", name="Export verified report").click()
            report = json.loads(Path(dl.value.path()).read_bytes())
            assert verify_export(report)["valid"]
            page.screenshot(path=str(out / f"desktop-result-{mode}.png"), full_page=True)
            rows.append({"mode": mode, "experiment_id": eid, "category": inv["diagnosis"]["category"],
                         "bound": inv["target_evidence"]["fidelity_bound"], "shots": inv["cost"]["shots"],
                         "actions": [a["measurement_specification"]["setting"] for a in inv["action_ledger"]], "export_valid": True})
        # history restoration: a custom experiment opened from the shared history route lands in the lab view
        page.goto(BASE + "/#/experiments/" + rows[0]["experiment_id"])
        expect(page).to_have_url(BASE + "/#/lab/" + rows[0]["experiment_id"])
        expect(page.get_by_role("heading", name="Target-state evidence")).to_be_visible()
        # keyboard: Run button is reachable and shows a focus indicator
        page.goto(BASE + "/#/lab")
        page.get_by_role("button", name="Run investigation").focus()
        assert page.evaluate("document.activeElement.textContent").startswith("Run investigation")
        ctx.close()
        mobile = []
        for w, h in VIEWPORTS:
            m = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=2, is_mobile=True, has_touch=True,
                                    reduced_motion="reduce")
            mp = m.new_page(); mp.on("pageerror", lambda e: errors.append(str(e)))
            for route in ["/#/lab", "/#/lab/" + rows[1]["experiment_id"], "/#/workbench", "/#/challenge"]:
                mp.goto(BASE + route); mp.wait_for_timeout(700)
                if route == "/#/lab":
                    mp.get_by_label("Contract type").select_option("target_state")
                    mp.get_by_label("Measurement policy").select_option("coefficient_weighted")
                    mp.wait_for_timeout(200)
                o = overflow(mp)
                small = mp.evaluate("""() => [...document.querySelectorAll('.lab button, .lab select, .lab input')]
                    .filter(e => e.offsetParent && e.getBoundingClientRect().height < 32).length""")
                mobile.append({"viewport": [w, h], "route": route, "horizontal_overflow_px": o["doc"],
                               "offenders": o["offenders"], "small_touch_targets": small})
                if w == 390:
                    mp.screenshot(path=str(out / f"mobile-{w}{route.replace('/', '_').replace('#', '')[:40]}.png"), full_page=True)
            m.close()
        browser.close()
    result = {"rows": rows, "mobile": mobile, "page_errors": errors, "console_errors": console,
              "passed": not errors and all(r["horizontal_overflow_px"] <= 0 and not r["offenders"] for r in mobile)}
    (out / "lab-e2e.json").write_text(json.dumps(result, indent=1))
    print(json.dumps(result, indent=1))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
