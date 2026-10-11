# Verified judging rehearsal and recording script

The current local rehearsal uses Qiskit2.3.1 and Aer0.17.2. No cloud credentials or network calls are needed after dependencies are present. This document is a recording script; no prerecorded video has been produced. Actual browser screenshots are retained under artifacts/browser-delivery.

From C:\Projects\QFF in PowerShell:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault serve
~~~

Open http://127.0.0.1:8000/. If the supplied server already owns port8000, use it rather than starting a second instance. The React production build is served by FastAPI. Standalone installed Playwright/Chromium now verifies the real UI scientific workflow as well as HTTP/CLI paths. See benchmarks/browser-verification.json.

Run the complete offline rehearsal in a separate terminal, using a new destination:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 scripts.submission_demo --out artifacts/my-judging-demo --backend aer
~~~

Actual prior output: benchmarks/submission-demo.json; underlying exports and raw investigations: artifacts/submission-rehearsal. The rehearsal executed five scenarios and a throwaway tamper/restore control:

| Scene | Observed conclusion | Recovery | Actual shots / evaluations |
|---|---|---|---|
| Healthy Bell | No significant failure detected | None | 7168 /4 |
| Hidden missing gate | Logical circuit defect | Independently VERIFIED | 11264 /30 |
| Readout-only noise | Noise-consistent degradation | None | 7168 /5 |
| Relative-phase defect | Logical circuit defect | Independently VERIFIED | 11264 /25 |
| Unfunded additional evidence | INSUFFICIENT_EVIDENCE | None | 4096 /2 |

All sampled execution records identify AerSimulator/density_matrix. The original submitted circuit remains unchanged. Verification uses a separate DensityMatrix state calculation and new Z/phase measurement seeds. Human review remains pending; a simulation success does not stand in for an actual person's decision.

## Three-minute narration

0:00–0:25 — Problem: a successful quantum job can return the wrong result. QFAULT asks which measurements disagree with an explicit contract, which explanations remain possible, and whether an admissible recovery survives new evidence. State that this demonstration is local simulation.

0:25–0:50 — Healthy computation: select Bell, clean, phase evidence, Aer. Inspect the declared state and actual counts. No significant failure is reported; that is not universal proof of correctness.

0:50–1:35 — Hidden failure: select Missing gate. The evaluator keeps its mutation label separate; diagnosis consumes submitted circuit, contract and measured evidence. Show competing support labels and actual shot/evaluation costs. The one-edit proposal is a copy, not replacement by the entire trusted reference. Show independent validation and its fresh seed.

1:35–2:05 — Noise control: choose Readout noise. Show the correct ideal state and noise-consistent measured disagreement, with no invented gate repair. If time permits, phase-only mutation demonstrates matching Z probabilities but disagreement in X measurements. Insufficient-budget control demonstrates honest abstention.

2:05–2:30 — Integrity: export the investigation. The rehearsal's dedicated throwaway artifact verifies true, false after covered-count alteration, true after restoring original bytes. This is SHA256 integrity relative to an unsigned manifest, not ML-DSA, authenticity or proof of scientific truth.

2:30–3:00 — Findings and limitations: the original evidence policy loses to fixed and is dominated by threshold on shots/accuracy. The separate frozen phase comparison reaches66/68 versus fixed58/68 with40% more shots and two missed angle faults. Fixed remains default. Across12 selected recovery cases,10 verified and2 were inconclusive. Exact attribution is privileged simulation, witnesses are incomplete, contracts cover one input, and fresh isolated installation/own frontend dependency gates remain unfinished.

## CLI equivalents and export checking

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault run --family bell --scenario remove --policy phase --backend aer
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault verify-report artifacts/submission-rehearsal/hidden_logical_failure.json
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault evaluate --split final --out artifacts/my-final-evaluation
~~~

The existing valid export returns exit0. The deliberately tampered export at artifacts/submission-rehearsal/tampered-export.json returns exit1. Do not alter real user artifacts. All output destinations refuse overwrite.

For an HTTP rehearsal with the server running:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 scripts.http_release_smoke --out artifacts/my-http-check
~~~

benchmarks/http-stabilization.json records actual201 scientific responses, valid exports, reload GETs, production-asset200s and invalid-input422s. This is not browser rendering, console, responsive-layout or download-interaction verification. The separate actual browser workflow is verified in benchmarks/browser-verification.json. A human reviewer must still make their own decision; no test pretends to supply human approval.

## Reproduce actual browser verification

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.browser_e2e --out artifacts/my-browser-demo
~~~

This executed six actual UI-driven Aer investigations, including GHZ4/QFT4 configuration, healthy/faulty/noisy/insufficient Bell controls; it verified the downloaded artifact and checked a genuine budget-validation422. Screenshots and responses remain local and ignored. No mocked success or browser-state injection produces the scientific results. Current browser coverage is Chromium151 at1600px and390px, not every browser/device.

## Submission release rehearsal

Latest actual output is artifacts/release-candidate/demo/summary.json, with per-scene JSON exports in the same directory. The recorded seed42 and configurations remain unchanged. Latest seven-workflow browser screenshots/exports are artifacts/release-candidate/browser-complete; these include an actual successful full phase-fault recovery. Existing narration is still accurate; no video has been recorded. The release paired audit adds56 cases both fixed/phase correct,10 phase-only and2 fixed-only, without a significance claim. See docs/release-candidate.md for exact executed commands and independent-install blockers.
