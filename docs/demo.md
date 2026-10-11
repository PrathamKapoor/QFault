# Verified judging rehearsal and recording script

The current local rehearsal uses Qiskit2.3.1 and Aer0.17.2. No cloud credentials or network calls are needed after dependencies are present. A genuine silent browser recording now exists at artifacts/submission-delivery/browser-recording/video/browser-workflow.webm. It is raw test footage, not a narrated final submission video. Actual screenshots and responses accompany it.

From the repository root in PowerShell (restricted-machine development bridge only; normal installed environments use python -m):

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

Latest actual output is artifacts/release-candidate/demo/summary.json, with per-scene JSON exports in the same directory. The recorded seed42 and configurations remain unchanged. Latest seven-workflow browser screenshots/exports are artifacts/release-candidate/browser-complete; these include an actual successful full phase-fault recovery. The silent browser recording described below supersedes the earlier no-recording state; a narrated final video remains unfinished. The release paired audit adds56 cases both fixed/phase correct,10 phase-only and2 fixed-only, without a significance claim. See docs/release-candidate.md for exact executed commands and independent-install blockers.

## Recording material and exact shot plan

Latest executed rehearsal: artifacts/submission-delivery/demo/summary.json. Latest recorded browser suite: artifacts/submission-delivery/browser-recording/summary.json, with video/browser-workflow.webm (2,874,466 bytes, VP8,1440×900,34.64 seconds, no audio). Installed Playwright/Chromium recorded genuine inputs and responses; no synthetic console or mocked scientific success. Beginning/middle/end frames were decoded to PNG; all three frames were visually inspected. The earlier stripped-FFmpeg decode did not complete. Subsequent normal-speed Chromium playback reached34.64 seconds with866 total video frames, zero dropped/corrupted frames and no media errors. This fast automated clip is usable source footage, not the complete three-minute judging story.

Actual screenshot assets: browser-recording/evidence-desktop.png, recovery-desktop.png, mobile.png and invalid-input.png under artifacts/submission-delivery. The screenshots and clip remain ignored local deliverables and are included by the transfer packager. No recorded narration or final edited MP4 is claimed.

For a new genuine capture with the current working server:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.browser_e2e --out artifacts/my-recording --record-video
~~~

This is the restricted-machine launcher. In a normal independently installed environment use python -m scripts.browser_e2e with the same arguments. The latter remains unverified here. Recording does not bypass actual scientific assertions.

Use these exact inputs for a slower manual recording: Bell2, Aer, seed42, phase-sensitive policy (explicitly higher-cost),2048 shots/execution. The CLI rehearsal already executed these inputs. For the browser insufficient-evidence shot, select phase fault and64 shots/execution; this actual browser control abstained after128 shots/2 evaluations. The separate CLI control uses remove with4096 total shots/2 evaluations and also abstains. Do not mix these two costs in narration. Human review remains pending.

| Time | Real UI/terminal action and shot | Narration to record |
|---|---|---|
| 0:00–0:25 | Title and contract panel; identify local simulation | A successful quantum job does not establish correct behavior. QFAULT investigates an explicit circuit contract using Qiskit execution evidence. |
| 0:25–0:50 | Bell2, clean, Aer, phase policy, seed42,2048; run and show circuit/counts | This Bell preparation agrees with the supported fixed-input contract. These are actual sampled simulator counts; no defect is invented. |
| 0:50–1:25 | Same settings, missing gate; run; show distributions, competing hypotheses and privileged-calculation label | The evaluator hides the mutation label from diagnosis. Measured disagreement triggers investigation. Exact attribution also uses privileged simulator state, so this is a simulation-backed developer tool. |
| 1:25–1:55 | Scroll to real recovery and fresh verification evidence | A bounded one-edit proposal operates on a copy. Fresh sampled evidence and a separate density-matrix calculation verify this selected recovery. The complete run costs11264 shots; this is not general repair or unitary equivalence. |
| 1:55–2:20 | Readout noise with same settings, then phase fault at64 shots | A logically valid circuit can have noisy output. The noise control gives a noise-consistent explanation. When evidence cannot be funded, QFAULT abstains. |
| 2:20–2:45 | Frozen comparison panel and actual exported report; show CLI verification from the rehearsal | In68 controlled cases fixed gets58 correct and phase-sensitive66, using40% more shots. Two angle faults remain missed; selected recovery is10/12 with two inconclusive. A covered change to a disposable export is rejected. |
| 2:45–3:00 | Limitations and pending human review | The contribution is an auditable investigation workflow with bounded recovery and cost accounting. It is simulation-only; unsigned hashes establish consistency, not physical correctness or authenticity. |

For the integrity shot, run qfault verify-report on artifacts/submission-delivery/demo/hidden_logical_failure.json (actual exit0) and on its disposable tampered-report.json (actual exit1). Prefix with the appropriate installed Python or documented local launcher. Do not edit a benchmark. The current raw clip shows export/verification but not the CLI tamper sequence; record that additional shot honestly. Pause for reading rather than speeding through evidence. Adjust final duration only after organizers confirm the format. Add human narration and inspect the final edited file before claiming the video complete.

## Final judging picture cut

Current silent judging footage: artifacts/final-delivery/judging-video-final/video/qfault-judging-silent.webm (176.56 seconds,1600×1000,13,580,390 bytes). It is genuine continuous browser interaction, with actual Bell healthy/fault/recovery/noise/abstention, full frozen final table/chart and report export. Full normal-speed Chromium playback completes with4414 video frames,2 dropped,0 corrupted and no media/page errors. Representative decoded frames and recorded screenshots were visually inspected. The earlier misframed draft is not the delivered cut.

[Editable voiceover and recording instructions](video.md) and [editable scene timeline](video-timeline.json) accompany it. Narration is NOT recorded; no final narrated video or organizer-compliant duration is claimed. The timeline uses approximate elapsed capture timings and ends at the measured video duration. Current CLI demo and seven-workflow browser acceptance evidence are artifacts/final-delivery/demo/summary.json and browser/summary.json; exact valid/tampered CLI outputs are export-verification.json. No production/scientific implementation changed.
