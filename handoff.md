# QFault engineering handoff — 2026-10-22

## 1. Current Phase

Implementation/release contract: implementation assembled, release gates partial. Started clean on research/external-validation at c4be11cded71f7625179f30c2b33b10c3b857d4a. No publication yet. The full owner contract remains active; do not reduce it to an audit.

## 2. Work Completed

Inspected clean source, refs/worktrees/stashes, correct QFault origin, runtime, locks and historical records. Fetched origin: HEAD 11 ahead/0 behind origin/main, current branch has no upstream. Root records were read in pages. Previous handoff is preserved verbatim in docs/handoff-history-20261016.md; its contradictory older instructions are historical.

Fresh isolated hashed CPython install at .local/contract-release/python, editable install, pip check, npm ci/check/build, baseline 449 tests and Aer smoke passed. First --no-build-isolation editable attempt failed because setuptools was absent; the documented normal build succeeded. No shared installation changed.

Added source/evidence snapshot packages and verifier, native QuantumCircuit conversion/provenance, opt-in QASM CLI conversion, custom lab/recovery CLI, strict numeric validation, parent-linked deterministic/new-seed replay, explicit ordinary/blind schema support and loopback/origin enforcement. Patched verified Vite/certifi advisories through existing locks. Current measured recovery reporting, native demonstration, dense development findings and full current flow are implemented. Work is uncommitted; final package/replication/publication gates are pending.

## 3. Files Changed

Inspect git status/diff for exact current inventory. Core: scripts/package_submission.py; qfault/qasm_import.py, lab.py, quantum.py, target.py, interventions.py, counterfactual.py, cli.py, api.py. New tests: test_release_package.py, test_native_import.py, test_custom_cli.py, test_strict_scientific_input.py, test_replay_identity.py. Locks/manifests: web/package.json/package-lock.json, pyproject.toml, requirements.lock. Records: decisions.md, flow.md, docs/implementation-ledger.md, docs/evidence-availability.md, this handoff and historical handoff copy.

## 4. Current Architecture / State

Local FastAPI + React; API and CLI share the validated engine. Native import accepts exact built-in H/X/Z/S/Rx/Ry/Rz/CX/CZ/CP/SWAP, 2–5 qubits/32 gates; records global phase/source instructions, with lab-only input preparation. No Python upload/eval/pickle. Optional ImportProvenance is excluded when absent, preserving legacy serialization/IDs. Derived edits retain import ancestry. Replay creates a new record linked to its source and declares same/new-seed semantics.

Package modes source-only/evidence-inclusive use clean committed source ZIP without full Git history/private runtime sweep. Complete-current evidence means the external study specifically; historical availability is separate. Actual committed-package extraction is not yet run.

## 5. Decisions Made

D-048–D-063 cover packaging, native/import CLI, strict inputs, dependencies, replay, reporting/contrast, ordinary/blind schema support, local trust, authentic historical evidence, source-pinned replication, negative development findings and browser verification. Append only. Record implementation hash in the next ordinary documentation commit, avoiding self-reference.

## 6. Requirements and Constraints

Current owner authorizes implementation then publication to https://github.com/PrathamKapoor/QFault after gates. Older no-push/QTrust restrictions are superseded authorization, not current instructions. Preserve all refs/worktrees/ignored work. Never stage paper/, research/ or .tex; no force push. Author AND committer: PrathamKapoor <prathamkapoor027@gmail.com>. No competition submission/external messages/paid hardware. Preserve approved hero/transition. One read-only reviewer was dispatched as explicitly required by requesting-code-review; no implementation was delegated.

## 7. Testing and Verification

Commands use .local/contract-release/python/Scripts/python.exe.
- Baseline pytest tests -q: 449 passed, Starlette/httpx and unwritable-cache warnings. Subsequently use -p no:cacheprovider.
- scripts.aer_smoke: pass, counts 00=506/11=518.
- npm ci/check/build: pass before/after Vite 8.2.4; lazy Three chunk warning remains.
- Package/legacy transfer: 7 passed after 3 red failures.
- Native/QASM/recovery: 61 passed. Native + CLI: 11 passed after 9 native/1 CLI red cases and correction of wrong feasibility signature.
- Strict/lab/recovery/native/CLI: 100 passed. Two additional edit-restriction cases then failed red; strict/boundary/target set passed 60 after correction.
- Replay/adversarial API: 102 passed after parent-link red regression.
- External verify_results/reconcile: 2,206 reports, 2,232 rows including 26 unsupported; no missing/duplicate cases.
- Historical recovery summary in C:/Projects/QFF-Recovery/artifacts/recovery-holdout is byte-identical to committed summary, SHA256 8fb0e091016e5c9106c8ffb73afbcc5e41fe15e9517a566338b9cdfa6d10c957. scripts.audit_counterfactual independently verified 310 manifests/count-based decisions/costs, replayed_records=0. Report: artifacts/contract-release/historical-recovery-audit.json.
- Old recovery holdout correctly refuses current sources with Frozen recovery sources/cases differ; do not call this the untouched evaluation. Guard unchanged.
- npm audit: affected Vite before, zero advisories after 8.2.4. pip-audit 2.10.0 isolated at .local/contract-release/audit-tools: certifi PYSEC-2026-4320 before, no known advisories after 2026.10.19. Reports: artifacts/contract-release/python-advisories*.json. pip check passed after hashed reinstall.
- GitHub connector confirms authenticated login PrathamKapoor. No credentials printed.
- Latest complete suite before the last blind-schema guard: 483 passed, one Starlette/httpx warning, 44.67 seconds; Aer smoke and pip check passed. Last blind-schema regression failed red, then 13 artifact/blind tests passed after correction. Complete final suite will run on the committed snapshot.
- Ten original Windows Chromium suites passed: release smoke, counterfactual, external editor, blind lifecycle, lab, landing, cinematic, workspace navigation, inspection and seven-template workflow runner. Native import/phase/recovery/download suite also passed at 1440 and 390/375/360 widths; retained provenance, no page errors, new metric/caption contrast minimum 8.076:1. Actual corrected overview/native recovery and preserved hero/fresh verification screenshots were opened.
- Native real API demo at seed 7241 passed five expected stages, with fresh original/candidate 4096 shots each and original preserved. Raw evidence is artifacts/contract-release/native-demo and browser-native-final.
- Dense development study: 16 real Aer cases, one two-qubit development architecture, all intervals cover oracle fidelity, both allocations confirm 4/8. No production method adopted. See docs/dense-target-development.md and benchmarks/dense-target-development-v1.json.
- Current supported protocol is configs/current-release-replication-v4.json. v1–v3 are preserved unexecuted drafts superseded by last resource/schema corrections; none is untouched evidence. Current-source execution refuses uncommitted inputs and awaits implementation commit.
- Gitleaks 8.30.1 reviewed history scan covers all 108 commits. Tree scan found only the same source api.py hash pattern in protocol drafts; the narrowly scoped rules classify these as noncredentials. Final staged/tree scan still pending.
- Fresh package extraction/install, current-source replication and publication remain pending.

## 8. Known Issues / Risks

Confirmed: new package extraction still pending; all historical/source guards preserved. Historical recovery raw evidence is now curated in benchmarks/historical-recovery-v1 (310 exact old exports, 1,057,578 bytes), with portable independent verifier; ordinary user sessions/reviews excluded. Other historical families remain summary-only where unavailable. Timeouts remain cooperative, hashes unsigned, no hardware calibration or causal localization. Linux/macOS/current hosted CI are not claimed from Windows local checks.

## 9. Unfinished Work

Finish reviewed staging/commit under owner identity; run final complete checks and committed v4 replication; verify both package modes and fresh extraction/locked install. Update gate report/next ordinary documentation commit with implementation SHA. Only then integrate normally to established main, push and verify remote SHA/sync and exact-SHA CI. Do not push until mandatory local gates pass.

## 10. Next Subphase

Commit the reviewable implementation, then execute frozen v4 replication and package gates. Server was deliberately restarted after core changes: unified exec session 56464, PID 17752, http://127.0.0.1:8000/, QFAULT_ARTIFACTS=artifacts/contract-release/live. Command: .local/contract-release/python/Scripts/python.exe -m qfault serve --port 8000. Real health/Aer/browser checks passed. Last isolated blind-version guard changes only verification of unsupported input; restart before final live demonstration to include it. Recheck PID before stopping; no unrelated process was stopped.

## 11. Critical Context

Historical full handoff: docs/handoff-history-20261016.md. Latest owner contract wins for authorization. Authentic original recovery worktree and its 310-run evidence are preserved. Research evidence may be deliberately selected; user runtime records stay private. Current external raw archive is already tracked (~4.65 MB). Source-only package omits it explicitly. No new evaluation has run yet and no existing holdout has been retuned.

## 12. Agent Instructions

Read root decisions/flow/handoff, recheck Git and continue without restarting baseline. Keep docs with changes; stage explicit paths. Use per-command git -c safe.directory=C:/Projects/QFF, never global changes. Record blockers honestly; continue independent work. Do not claim readiness/publication without current executed evidence for every mandatory gate.
