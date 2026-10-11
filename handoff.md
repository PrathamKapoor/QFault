# QFAULT engineering handoff

## 1. Current Phase

Release stabilization and diagnostic evidence are implemented and locally verified. Overall status is PARTIALLY COMPLETE: fresh isolated Python/frontend installation and browser E2E remain blocked. Aer now genuinely executes; the previous Aer-unavailable conclusion is superseded by D-016.

## 2. Work Completed

Continued the existing project without rewrite. Initial branch main at d30535caac17fb55718ac313c3e033dabb631364 was clean. Read decisions/flow/handoff and required docs, inspected implementation, reran62 tests and reproduced the original75-case/policy benchmark. Audited all300 original predictions and their evidence/actions. Preserved authoritative benchmarks/results.json, reproduction.json and demo.json.

Committed disjoint development/final inputs before implementation. Added contract-defined sampled phase witnesses, phase policy, honest unfunded-evidence abstention, reserved independent recovery validation, separate phase qualities and fixed default. Executed development, frozen final, low-shot controls and separate selected recovery/negative controls. Current original/final benchmark reproduction matches scientific metrics without tuning on final results.

Located a matching cp313 Aer0.17.2 installation read-only. Added optional explicit Aer adapter and CLI/API/UI backend choice while retaining reference. Executed real ideal/noisy Bell/GHZ/QFT conformance and saved-density comparisons. Added standalone report verification and boundary regression fixes. Executed Aer judging demo and actual HTTP workflows. UI presents actual bases/counts/hypotheses/costs/recovery and both original/final results. Built and checked TypeScript, generated and visually inspected a standard Matplotlib tradeoff plot. No browser rendering success is claimed.

## 3. Files Changed

Core: qfault/quantum.py, diagnostics.py, recovery.py, workflow.py, experiments.py, storage.py, cli.py, api.py; new backends.py. Interface: web/src/main.tsx. Tests: test_phase_measurements.py, test_policy_evaluation.py, test_export_verification.py, test_aer_backend.py, test_aer_absence.py, test_measurement_boundaries.py, test_phase_truth_isolation.py, test_repair_boundaries.py. Tooling: scripts/audit_diagnostics.py, compare_backends.py, evaluate_recovery.py, submission_demo.py, http_release_smoke.py, plot_policy_tradeoff.py, local_bootstrap.py. Manifests: configs/diagnostic-evaluation.json, pyproject.toml optional Aer extra, requirements-aer-tested.txt. Documentation: README, decisions, flow, this handoff, docs/environment-stabilization.md, diagnostic-findings.md, methodology.md, demo.md, release-gates.md. Actual measured summaries/figure under benchmarks; raw artifacts and built frontend remain ignored.

## 4. Current Architecture / State

CLI/API → RunRequest → investigate → budgeted selected simulator → EvidenceCollector → DiagnosticAnalyst/DiagnosticAccess → bounded RecoveryPlanner → independent DensityMatrix and fresh sampled verifier → pending human review → immutable ArtifactStore. See flow.md for actual functions and order. Phase policy samples a contract basis before privileged state attribution. Optional Aer never silently falls back; reference remains default. One-edit search does not receive mutation parameters or replace a full circuit. Export verification recomputes covered hashes; review remains append-only and self-declared.

The local application is served at http://127.0.0.1:8000/ by the owned process started during this session (inspect artifacts/server-error.log for the current PID before stopping). It serves built React assets and real API responses. Server may need restarting after future code edits; no deployment occurred.

## 5. Decisions Made

D-001–012 retain the original foundation/history. D-013 records the original cp311 mismatch and failed install attempts; D-016 explicitly supersedes its Aer-unavailable outcome after locating cp313. D-014 defines complementary witnesses. D-015 freezes holdout/reserves validation and retains fixed default. D-017 adds exported-report checking and bounded internal analysis circuits. D-018 publishes all frozen negative findings. D-019 skips invalid repair angle edits rather than weakening input validation. Commits1d89eff and3039215 precede final evaluation; subsequent local stabilization commits contain Aer/reporting/docs.

## 6. Requirements and Constraints

Local only; no push, publication, deployment, cloud, paid API or hardware. All new author/committer identities must be PrathamKapoor <prathamkapoor027@gmail.com>, repository-local configuration only. No tool coauthors, generated authorship footers or donor writes. Preserve authoritative experiments, notices and history. No arbitrary Python uploads, paper/research/.tex files, artificial stage directories, fabricated metrics or success claims. Keep decisions/flow/handoff current. Fixed-input states are not general unitary equivalence; unsigned hashes are not PQC signatures or scientific truth.

## 7. Testing and Verification

Initial suite:62 passed,1 warning. Final suite executed using LibreOffice python.exe -B -u scripts/local_bootstrap.py pytest -q -p no:cacheprovider:94 passed,1 Starlette/httpx deprecation warning,6.18s in the first final run; latest exact output is benchmarks/stabilization-verification.json. The PowerShell launcher qfault circuits was executed again successfully. TypeScript check and Vite production build passed using the explicitly disclosed read-only donor node_modules bridge; own fresh frontend installation is not verified.

Verified commands from repository root (new output destinations required):

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 pytest -q -p no:cacheprovider
node scripts/check-web.mjs C:/Projects/Quantum_Simulator/frontend/node_modules
node scripts/build-web.mjs C:/Projects/Quantum_Simulator/frontend/node_modules
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault benchmark --out artifacts/new-original
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault evaluate --split final --out artifacts/new-final
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 scripts.evaluate_recovery --out artifacts/new-recovery
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 scripts.compare_backends --out artifacts/new-backends
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 scripts.submission_demo --out artifacts/new-demo --backend aer
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault serve
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 scripts.http_release_smoke --out artifacts/new-http
~~~

Original results reproduce47/75 evidence,66/75 fixed,23/75 random,47/75 threshold; shots/evaluations also match. Final results reproduce34/68 evidence,58/68 fixed,21/68 random,34/68 threshold,66/68 phase. Full confusion matrices/uncertainty/costs and raw paths are in benchmarks/diagnostic-final.json and docs/diagnostic-findings.md; reproduction comparison in benchmarks/stabilization-reproduction.json.

Phase final uses487424 shots/328 evaluations versus fixed348160/272; phase misses both QFT2 angle cases. No false diagnosis among10 evaluator-correct cases (Wilson upper27.8%). Low-shot phase abstains4/4. Selected recovery10/12 verified (Wilson55.2–95.3%), two QFT4 inconclusive; two invalid/noisy proposals rejected. Recovery reproduction retains these outcomes. Actual Aer conformance: nine paired circuit/noise cases, density errors<=3.34e-16, sampled TV<=0.0188. Actual Aer demo has healthy/fault/noise/phase/abstention and true/false/true integrity control. HTTP checks cover page/assets, contracts, both measured summaries, four201 workflows, reloads, valid exports and invalid422 requests. Standalone valid export exits0; tampered export exits1. Browser E2E/screenshots/console/responsive checks remain unavailable.

## 8. Known Issues / Risks

LibreOffice Python3.13.15 lacks venvlauncher.exe/venvwlauncher.exe. Python package network access fails EACCES/connection errors; npm online registry fails EACCES and offline metadata ENOTCACHED. The ignored partial .venv has no usable interpreter; do not treat it as an install. No package-lock.json or own node_modules could be generated/installed. Browser discovery is empty. Exact attempt evidence is docs/environment-stabilization.md.

Current runtime is a machine-specific read-only bridge, not a clean installation. Qiskit2.3.1/NumPy2.5.2/SciPy1.18.1 plus Aer0.17.2 are actually loaded; only Aer is imported from the separate cp313 user package to avoid contaminating other versions. Frontend React19.2.8, Vite8.2.2, TypeScript6.0.3 were checked/built. Fresh transitive resolution remains unknown. Exact-state attribution is privileged; complementary witnesses are incomplete; small repeated-template intervals are descriptive. Four-qubit QFT validation can remain inconclusive at2048 shots. No QCEC, mitigation, temporal forecasting, ML-DSA signing or hardware execution exists. Persistence can retain partial directories after crashes; verification fails closed. Review identity is not authenticated.

## 9. Unfinished Work

Fresh Python/frontend install and lockfile; real browser workflow/console/responsive/export testing; judging visual rehearsal and actual recording. Optional stronger independent scientific validation, larger unseen-circuit corpus, phase-angle detection study and measurement-efficient selection remain separate future work. Do not silently retune frozen final cases or replace losing results.

## 10. Next Subphase

On an unrestricted machine, use normal CPython3.13, install the tested manifests in an isolated environment, generate and validate QFAULT's own npm lockfile, then run complete browser E2E against that installation. This is the most consequential submission-readiness objective. After release gates, design a new prespecified evaluation for incomplete witness/small-angle behavior.

## 11. Critical Context

Original expected HEAD d30535c was verified. Current commits are local on main; inspect git log/status for exact delivery HEAD. Authoritative old summaries remain unchanged. New holdout was frozen before implementation; final results were opened once without tuning, then reproduced. Raw directories include artifacts/stabilization-original, stabilization-current-original, diagnostic-development, diagnostic-final, diagnostic-final-reproduction, diagnostic-low-shot, recovery-stabilization, recovery-reproduction, backend-conformance, submission-rehearsal and http-stabilization. These are ignored but retained locally. Normal fresh-machine commands are documented as unverified installation instructions. No donor implementation copied; prior reuse inventory/THIRD_PARTY_NOTICES remain valid. Deadline supplied by user: October12,2026; not independently reinterpreted as a winning outcome.

## 12. Agent Instructions

Read this file, decisions.md and flow.md completely before edits. Preserve working code/user changes and scientific artifacts. Inspect actual environment; do not assume Aer globally incompatible or installation/browser verified. Use matching ABI, standard package sources and local author identity; never modify global Git or donors. Keep actual output seeds/budgets/backend labels. Do not tune on final results and call them fresh generalization. Run relevant real quantum tests, preserve negative findings, update operational docs, commit locally only and report remaining blocked gates honestly.
