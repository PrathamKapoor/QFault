# Engineering decisions

### D-001: Independent local repository and verified runtime bridge

- Date / phase / commit: 2026-10-11 / environment discovery and quantum foundation / d1f81b669808550a81eec4519cba4462469f71ed.
- Context: C:/Projects/QFF was empty and outside an existing Git repository. Normal terminal setup failed. Python was absent from PATH and donor virtualenv launchers pointed to an inaccessible Windows Store interpreter.
- Decision: Initialize only QFF, set repository-local PrathamKapoor identity, and run the existing LibreOffice Python 3.13.15 through a read-only dependency bridge. Use per-command safe.directory overrides in this sandbox; never change global Git configuration.
- Why: Enables actual local Qiskit execution without modifying donors, downloading executables or requesting cloud services.
- Alternatives considered: Existing donor interpreter (access denied); old Blender runtime (absent); official download (direct request failed).
- Consequences: Current workspace runs, but isolated installation is not established. Source directories remain read-only. Normal package installation remains documented separately with an explicit verification limitation.
- Files: docs/environment.json, scripts/local_bootstrap.py, scripts/local.ps1, .gitignore.

### D-002: Small native Qiskit circuits and analytic fixed-input contracts

- Date / phase / commit: 2026-10-11 / quantum foundation / d1f81b669808550a81eec4519cba4462469f71ed.
- Context: Circuit correctness requires an explicit specification; sampled distributions cannot establish arbitrary unitary behavior.
- Decision: Native QuantumCircuit templates for Bell, GHZ and QFT; independent analytic target states; 2–5 qubits and 32-operation cap for bounded local execution. Bell uses exactly two qubits by definition.
- Why: Scientifically inspectable calculations and a reproducible small demonstration.
- Alternatives considered: Arbitrary Python uploads (unsafe and unnecessary); donor QFT IR (different wire conventions and extra dependencies).
- Consequences: One-input state correctness only. Computational-basis observability limits are tested and reported.
- Files: qfault/quantum.py, tests/test_quantum.py.
- Package: qiskit 2.3.1, numpy 2.5.2, scipy 1.18.1.
- Why this package: Qiskit is the actual central execution engine; NumPy supports references and SciPy is a Qiskit dependency.
- Packages compared: QFT-Lab IR, pure NumPy donor simulator; rejected as substitutes for native Qiskit execution.

### D-003: Explicit quantum-channel fallback because Aer is unavailable

- Date / phase / commit: 2026-10-11 / noise execution / d1f81b669808550a81eec4519cba4462469f71ed.
- Context: Local Aer 0.17.2 is cp311; accessible Python is cp313. Import fails at controller_wrappers.
- Decision: Ideal sampling via BasicSimulator; gate noise via Qiskit DensityMatrix/Kraus with explicit local depolarizing channels; symmetric readout flips after quantum measurement. Mark Aer unavailable.
- Why: A valid executed fallback is preferable to an unexecuted backend claim.
- Alternatives considered: Reinstalling without compatible network access; falsely labeling fallback output Aer; both rejected.
- Consequences: Aer release gate remains unmet. No hardware claims. Noise configurations and backend identifiers are recorded.
- Files: qfault/quantum.py, docs/methodology.md, README.md.
- Package: No new noise package added.
- Why this package: Existing Qiskit quantum_info supplies actual channels.
- Packages compared: qiskit-aer, mitiq (unavailable / not required for defined fallback).

### D-004: Allowlisted evidence boundary and transparent diagnostic policies

- Date / phase / commit: 2026-10-11 / investigation / d1f81b669808550a81eec4519cba4462469f71ed.
- Context: Injected labels and hidden physical parameters must not drive diagnosis.
- Decision: EvidenceCollector projects only execution ID, validated counts and shots. DiagnosticAnalyst receives the candidate, contract, projection and bounded DiagnosticAccess. Evaluator truth is attached only after prediction_digest is frozen and persisted separately.
- Why: Demonstrable label separation; poisoning irrelevant metadata leaves analyst results unchanged.
- Alternatives considered: Circuit diff against the trusted template (trivializes diagnosis); hidden-noise features (leakage); rejected.
- Consequences: This is an API boundary, not adversarial Python process isolation. No class confidence probability is invented. State probes are explicitly privileged simulator operations.
- Files: qfault/diagnostics.py, qfault/workflow.py, tests/test_investigation.py.

### D-005: Bounded one-edit repair and independent validation

- Date / phase / commit: 2026-10-11 / recovery / d1f81b669808550a81eec4519cba4462469f71ed.
- Context: A satisfying selection score is insufficient proof of recovery.
- Decision: Enumerate at most 256 declared one-edit candidates without a trusted full-circuit replacement. Verify with separate DensityMatrix evolution and fresh seeded counts. Preserve original circuits and require human review.
- Why: Reproducible admissible recovery with explicit rejection/inconclusive outcomes.
- Alternatives considered: Complete reference-circuit substitution (not repair); full QCEC (not integrated); unbounded search (resource risk).
- Consequences: Search is incomplete; fixed-input equivalence only; state correctness and noisy sampled quality are separate.
- Files: qfault/recovery.py, tests/test_investigation.py, tests/test_robustness.py.

### D-006: Immutable file artifacts and hash-bound append-only review

- Date / phase / commit: 2026-10-11 / provenance and persistence / d1f81b669808550a81eec4519cba4462469f71ed.
- Context: A local demo needs raw data, stable relationships, export and tamper detection without a service stack.
- Decision: Exclusive experiment directories, canonical JSON investigation/evaluator documents, SHA-256 manifest and separate immutable human review records bound to the investigation digest.
- Why: Inspectable, reproducible storage is sufficient for the bounded local product.
- Alternatives considered: SQLite (reasonable later); PostgreSQL/Redis/Celery (unnecessary); importing donor ledger (extra dependencies).
- Consequences: No transactional multi-file commit, external signature, deletion-resistant review history or authenticated human identity. Partial writes fail verification.
- Files: qfault/evidence.py, qfault/storage.py, tests/test_storage_api.py.

### D-007: Local API and restrained scientific React interface

- Date / phase / commit: 2026-10-11 / usable workbench / d1f81b669808550a81eec4519cba4462469f71ed.
- Context: Judging needs a usable investigation journey backed by the real core.
- Decision: FastAPI localhost single-process API; React/TypeScript/Vite frontend with actual distributions, hypotheses, recovery, ledger, benchmark, review and JSON export. No external fonts, charts, animations, telemetry or cloud infrastructure.
- Why: Small dependency footprint and direct connection to measured evidence.
- Alternatives considered: Mock dashboard, notebook-only delivery and external deployment; rejected.
- Consequences: Typecheck/build/API integration verified; browser interaction and visual QA unavailable because the browser runtime reports no browsers.
- Files: qfault/api.py, web/src/main.tsx, web/src/styles.css, scripts/build-web.mjs, scripts/check-web.mjs.
- Package: pydantic 2.13.4, fastapi 0.141.1, uvicorn 0.52.4; React/react-dom 19.2.8, Vite 8.2.2, TypeScript 6.0.3; pytest 9.1.1 and httpx 0.28.1 for tests.
- Why this package: Already verified local packages; input validation, localhost delivery and real integration checks.
- Packages compared: Full donor web/platform stacks, chart libraries and orchestration frameworks; unnecessary.

### D-008: Publish fixed-plan wins and the evidence-policy negative result

- Date / phase / commit: 2026-10-11 / frozen benchmark / d1f81b669808550a81eec4519cba4462469f71ed.
- Context: The contribution hypothesis requires actual comparisons with equal resource ceilings and honest losing cases.
- Decision: Freeze 25 family/scenario combinations, seeds 11/29/47, four policies, 6,144-shot/4-evaluation ceilings. Publish all 300 policy results and six separate recovery trials. Repeat independently without tuning.
- Why: Evidence policy achieved 47/75 correct versus fixed 66/75; threshold also 47/75 with fewer shots. No superiority claim is warranted.
- Alternatives considered: Excluding invisible phase/noise cases, tuning on holdout, or reporting only successful repairs; rejected.
- Consequences: Small corpus and clustered repeated seeds limit inference. Wilson intervals are descriptive. Recovery is 6/6 on a selected missing-gate subset, not a broad repair rate. Reproduction matched scientific metrics.
- Files: docs/benchmark-protocol.md, qfault/experiments.py, benchmarks/results.json, benchmarks/reproduction.json.

### D-009: Validate manifest shape before integrity access

- Date / phase / commit: 2026-10-11 / robustness fix / d1f81b669808550a81eec4519cba4462469f71ed.
- Context: Corruption must report failed verification rather than crash.
- Symptom: verify() raised AttributeError for JSON null, array manifests and array artifact maps.
- Root cause: Parsed JSON was assumed to be a dictionary before .get calls; JSON syntax validity did not imply schema validity.
- Decision: Require object-shaped manifest and artifact map before field access, then retain existing failure reporting.
- Why: Smallest fix at the corrupted-data boundary; no assertions weakened.
- Alternatives considered: Catching all exceptions or treating missing keys as success; rejected.
- Consequences: Malformed manifests fail closed with a recorded verification error.
- Regression test: tests/test_storage_api.py::test_malformed_manifest_fails_closed (three failing cases observed before fix, all pass after).
- Files: qfault/storage.py, tests/test_storage_api.py.

### D-010: Record resource kinds and measured/derived provenance separately

- Date / phase / commit: 2026-10-11 / reporting / d1f81b669808550a81eec4519cba4462469f71ed.
- Context: Exact simulator calculations and shot executions are different costs; raw data must remain traceable.
- Decision: Record total evaluations, actual sampled circuit executions, exact-state evaluations, shot sums, operation resources and measured/derived observation records with execution references.
- Why: Prevent a zero-shot classical state calculation from disappearing or being mislabeled as quantum hardware execution.
- Alternatives considered: Shots-only accounting or conflating all evaluations with provider executions; rejected.
- Consequences: Local evaluation costs are not currency or hardware cost estimates.
- Files: qfault/workflow.py, qfault/diagnostics.py, tests/test_investigation.py.

### D-011: Distinguish completed verification from successful verification

- Date / phase / commit: 2026-10-11 / release correctness / d1f81b669808550a81eec4519cba4462469f71ed.
- Context: Supervisor progress must not imply recovery success.
- Symptom: A budget-inconclusive validation could enter a state named VERIFIED.
- Root cause: The transition name described a successful verdict instead of completion of the verification operation.
- Decision: Use VERIFICATION_COMPLETED for the supervisor transition; retain VERIFIED, REJECTED and INCONCLUSIVE only as actual verifier verdicts.
- Why: Prevent misleading workflow status while preserving evidence and rejection behavior.
- Alternatives considered: Skipping inconclusive records; rejected.
- Consequences: Human review can inspect completed unsuccessful verification.
- Regression test: tests/test_investigation.py budget-inconclusive supervisor regression, observed failing before fix.
- Files: qfault/workflow.py, tests/test_investigation.py.

### D-012: Fail closed on corrupt artifacts and bind review membership

- Date / phase / commit: 2026-10-11 / independent release review / d1f81b669808550a81eec4519cba4462469f71ed.
- Context: Static review found artifact-shape failures and undetected review deletion.
- Symptom: Malformed investigation/review JSON caused HTTP 500; deleting a review left verification valid.
- Root cause: Detail loading preceded verification and assumed object shapes; the manifest did not enumerate review records.
- Decision: Verify before load, call integrity verification directly from its endpoint, and bind immutable review envelopes and membership in the manifest. Update the manifest atomically and serialize API review updates.
- Why: Seven regression cases reproduced the findings, then passed after the focused fix.
- Alternatives considered: Narrowing deletion guarantees alone; rejected because a small index fixes the issue.
- Consequences: Supersedes D-006's lack of review-deletion detection relative to an intact manifest. Replacing or rolling back the unsigned manifest remains undetectable without an external anchor. Old local experimental reviews without membership hashes are reported invalid; no silent migration.
- Regression test: tests/test_artifact_corruption.py (six malformed-artifact cases and deleted-review case).
- Files: qfault/storage.py, qfault/api.py, tests/test_artifact_corruption.py.

### D-013: Diagnose Aer as a local ABI mismatch, not Python 3.13 incompatibility

- Date / phase / commit: 2026-10-11 / release stabilization / stabilization commit containing this entry.
- Context: Official Aer 0.17.2 provides cp313 Windows x64 wheels; the previous bridge loaded donor package paths.
- Symptom: ModuleNotFoundError for qiskit_aer.backends.controller_wrappers.
- Root cause: Verified donor WHEEL tag cp311-cp311-win_amd64 and controller_wrappers.cp311-win_amd64.pyd, while accessible Python requires .cp313-win_amd64.pyd. Why that older wheel was originally installed is unknown.
- Decision: Retain the executed reference backend and document the exact mismatch. Do not claim an Aer adapter passed. Attempt fresh venv and official package access before changing dependencies.
- Why: LibreOffice venv creation actually failed on missing venvlauncher.exe/venvwlauncher.exe; official PyPI requests failed EACCES/connection errors. npm registry requests also failed EACCES and offline resolution ENOTCACHED.
- Alternatives considered: Copying donor binaries/node_modules, inventing a lockfile, or claiming all Python 3.13 Aer wheels incompatible; rejected.
- Consequences: Fresh Python/frontend installs and Aer execution remain blocked in this environment. The partial .venv is ignored, not usable. No donor installations are modified.
- Regression test: ABI metadata and failing import/venv/registry probes recorded in docs/environment-stabilization.md.
- Files: docs/environment-stabilization.md, README.md, handoff.md.
- Package: No dependency added or replaced.
- Why this package: Preserve the verified existing Qiskit runtime until isolated packages can be installed.
- Packages compared: Official qiskit-aer 0.17.2 cp313 wheel versus local cp311 wheel; fresh npm resolution versus donor dependency bridge.

### D-014: Contract-defined complementary measurements and a separate policy

- Date / phase / commit: 2026-10-11 / diagnostic evidence / stabilization commit containing this entry.
- Context: Original evaluation reproduced exactly. Z-only measurement triggers miss relative-phase defects; some fixed-policy calibration evidence is collected but ignored in the category decision.
- Decision: Preserve all four original policies. Add phase policy using actual X-all-qubit measurements for Bell/GHZ and analytic Fourier product-phase cancellation followed by H for QFT. Only significant sampled or calibration evidence triggers the existing exact logical/noise discrimination. Calibration-only noise consistency explicitly does not imply task-output degradation.
- Why: Genuine additional measurements address observability; opaque ML or relabeling the original benchmark would not. Global phase leaves probabilities unchanged.
- Alternatives considered: Trusted-circuit diff, classifier using fault labels, changing old thresholds, and claiming tomography; rejected.
- Consequences: Extra shots and basis gates are charged and noisy. Witnesses are incomplete, attribution still uses privileged simulation, and unfunded evidence abstains. Original benchmark remains authoritative and unchanged.
- Regression test: tests/test_phase_measurements.py; nine feature tests failed before implementation, then passed; global-phase and negative repair controls also pass.
- Files: qfault/quantum.py, qfault/diagnostics.py, qfault/workflow.py, tests/test_phase_measurements.py.

### D-015: Freeze holdout and preserve independent validation resources

- Date / phase / commit: 2026-10-11 / evaluation and recovery / stabilization commit containing this entry.
- Context: The existing 75-case benchmark is observed data, and recovery needs samples independent from selection.
- Decision: Commit configs/diagnostic-evaluation.json before implementation; separate development seed 71 from final seeds 103/211, including GHZ4 and QFT2/4. Match 8,192-shot/6-evaluation ceilings across five policies. For phase recovery, reserve two fresh measurement executions and one density-state check before candidate search. Keep fixed as default before opening final results.
- Why: Development phase policy 25/25 versus fixed 22/25 uses more shots/evaluations; this does not establish general superiority or justify hiding the best existing baseline.
- Alternatives considered: Tune on old/final results, ignore basis-gate cost, exhaust validation budget, switch defaults using final accuracy alone; rejected.
- Consequences: All final cases and losing outcomes must be published without tuning. Separate computational-basis and phase-basis recovery qualities prevent a phase repair from looking unchanged solely because Z counts match.
- Regression test: tests/test_policy_evaluation.py; reservation/default regressions in tests/test_phase_measurements.py, each observed failing before fix.
- Files: configs/diagnostic-evaluation.json (frozen commit 1d89eff), qfault/experiments.py, qfault/recovery.py, qfault/cli.py, benchmarks/diagnostic-development.json.

### D-016: Execute the verified cp313 Aer package through an explicit optional adapter

- Date / phase / commit: 2026-10-11 / backend conformance / commit containing this entry.
- Context: Further read-only discovery located a different user-package Aer 0.17.2 installation with WHEEL tag cp313-cp313-win_amd64 and controller_wrappers.cp313-win_amd64.pyd.
- Symptom: The original bridge's cp311 Aer could not import on Python 3.13.
- Root cause: D-013's verified ABI mismatch applied to that installation, not every available Aer package.
- Decision: Supersede D-013's Aer-unavailable conclusion. Add lazy qfault.backends adapter and explicit reference/aer request choice. Local bootstrap loads only the matching Aer package by import spec, without inserting its different Qiskit/NumPy environment into sys.path. Keep reference default and frozen reference evaluations.
- Why: Real Bell Aer execution succeeded, eight regression tests passed, and nine paired circuit/noise conformance cases executed both backends. Density differences <=3.34e-16; sampled TV versus analytic noisy distributions <=0.0188 in this small test.
- Alternatives considered: Replacing the reference backend, silently falling back on requested Aer failure, broad user-package sys.path contamination, or renaming .pyd files; rejected.
- Consequences: Aer works locally, but this remains a read-only dependency bridge; fresh isolated Python/frontend installs are still blocked. Explicit logical gates retain per-gate noise semantics, with no transpilation. Aer uses density_matrix and one parallel thread; exported records identify its actual version.
- Regression test: tests/test_aer_backend.py (eight failures before adapter, eight passed after), actual backend comparison script and HTTP/CLI Aer workflows.
- Files: qfault/backends.py, qfault/quantum.py, qfault/workflow.py, qfault/diagnostics.py, qfault/recovery.py, scripts/local_bootstrap.py, scripts/compare_backends.py, benchmarks/backend-conformance.json.
- Package: qiskit-aer==0.17.2 optional extra, psutil 7.2.2 observed.
- Why this package: Actual compatible installed Aer quantum execution and standard noise channels.
- Packages compared: Aer 0.17.2 cp313 versus incompatible cp311 installation; existing BasicSimulator/DensityMatrix remains a valid independent reference.

### D-017: Bind exported reports and correct measurement-boundary validation

- Date / phase / commit: 2026-10-11 / release correctness / commit containing this entry.
- Context: Downloaded reports need standalone verification; independent review found two measurement construction edges outside the frozen corpus.
- Symptom: QFT input 9 on four qubits produced a rotation outside the gate angle bound; adding basis gates to a valid 32-gate submitted circuit exceeded the submitted-circuit length cap.
- Root cause: Unnormalized equivalent Rz angles and reuse of the submitted-circuit length validator for internal analysis circuits.
- Decision: Normalize only out-of-range analysis angles modulo 2π; permit at most 42 gates in private _AnalysisCircuit (32 submitted + at most 10 analysis gates). Preserve the 32-gate submitted input bound. Add verify_export and CLI verify-report that recompute covered hashes rather than trusting embedded success.
- Why: Both boundary regression tests failed before the fix and passed after. Standard frozen corpus uses QFT input 1 and shorter circuits, so its measurements are unchanged and current reproduction confirms original/final metrics.
- Alternatives considered: Relax all submitted bounds, ignore unsupported angle failures, or trust a report's embedded valid flag; rejected.
- Consequences: Signed authenticity remains unavailable. qfault-json-v1 preserves numeric representation: 1 and 1.0 are different canonical values. Rewriting JSON through a tool that changes numeric types may invalidate it.
- Regression test: tests/test_measurement_boundaries.py; five tests/test_export_verification.py; tests/test_phase_truth_isolation.py; CLI valid export exits 0 and tampered export exits 1.
- Files: qfault/quantum.py, qfault/storage.py, qfault/cli.py, tests/test_measurement_boundaries.py, tests/test_export_verification.py.

### D-018: Publish the frozen tradeoff and selected recovery failures

- Date / phase / commit: 2026-10-11 / submission evidence / commit containing this entry.
- Context: The final scenarios were frozen in 1d89eff before phase implementation in 3039215. Final results were generated without further policy tuning.
- Decision: Publish all five policies, confusion matrices, resources and negative cases. Keep fixed default; expose phase as an explicit option. Publish selected recovery 10/12 verified with two inconclusive QFT4 cases and two rejected negative controls.
- Why: Phase 66/68 versus fixed 58/68 costs 487424 versus 348160 shots. Phase misses two QFT2 angle faults, while fixed's exact checks catch those. Higher aggregate category accuracy does not establish a dominant policy.
- Alternatives considered: Change thresholds after final results, omit difficult QFT cases, conflate calibration noise with task failure, or claim 6/6 applies generally; rejected.
- Consequences: Descriptive intervals only; small fixed corpus and privileged simulation limit generalization. Browser and fresh-install gates remain unmet despite actual quantum/HTTP/build evidence.
- Files: benchmarks/diagnostic-final.json, benchmarks/diagnostic-low-shot.json, benchmarks/recovery-stabilization.json, scripts/submission_demo.py, scripts/http_release_smoke.py, docs/diagnostic-findings.md, web/src/main.tsx.

### D-019: Skip out-of-domain repair rotations without weakening input validation

- Date / phase / commit: 2026-10-11 / recovery robustness / commit containing this entry.
- Context: Repair search must enumerate only valid supported edits for every accepted input.
- Symptom: A valid Rz(8π) candidate aborted edit enumeration.
- Root cause: Unconditionally constructing angle+π/4 and angle+π/2 exceeded Gate's existing ±8π domain before any candidate was yielded.
- Decision: Skip only angle edits outside the declared bound. Keep valid negative corrections and all existing assertions.
- Why: tests/test_repair_boundaries.py reproduced the failure before the focused fix and passed after; the frozen corpus has no boundary-angle gate, so its candidate search is unchanged.
- Alternatives considered: Catch all validation errors or weaken Gate bounds; rejected.
- Consequences: Search remains bounded and incomplete; invalid edits are never proposed. Optional-Aer-absence regression also confirms reference execution remains usable and explicit Aer requests fail honestly.
- Regression test: tests/test_repair_boundaries.py; tests/test_aer_absence.py.
- Files: qfault/recovery.py; tests/test_repair_boundaries.py; tests/test_aer_absence.py.

### D-020: Verify the real browser workflow and restore truthful UI configuration

- Date / phase / commit: 2026-10-11 / browser release verification / commit containing this entry.
- Context: Connected-browser discovery was empty, but read-only inspection found installed Playwright1.62.0 and cached Chromium151.0.7922.34.
- Symptom: Computational bitstrings displayed10/11 before00/01; loading history left default controls inconsistent with the recorded run; no qubit selector exposed supported four-qubit configurations.
- Root cause: JavaScript integer-key enumeration order, load setting only results/integrity, and omitted validated qubit state/control.
- Decision: Supersede D-007 and D-018 browser-unavailable outcomes. Use a separate local browser launcher, sort plot keys, restore all saved settings and fetch their contract, and expose the existing supported qubit count. Keep actual scientific decisions and frozen evaluation unchanged.
- Why: Real pre-fix browser assertions reproduced ordering/history defects and missing qubit control; the final six-workflow Aer journey passes with report download verification, independent repair display, loading/error states, refresh and mobile geometry.
- Alternatives considered: Claiming compilation proves browser behavior, mocking successful API responses, or changing application package paths to load Playwright; rejected.
- Consequences: Browser E2E is verified locally, not a fresh installation or exhaustive device matrix. Screenshots remain ignored local evidence. Human review remains pending.
- Regression test: scripts/browser_e2e.py; raw pre-fix browser-regression-before-fix, browser-history-before-fix, browser-qubits-before-fix and passing browser-delivery evidence.
- Files: web/src/main.tsx; scripts/browser_bootstrap.py; scripts/browser_e2e.py; scripts/local_browser.ps1; docs/browser-verification.md; benchmarks/browser-verification.json.
- Package: Optional playwright==1.62.0; observed pyee13.0.1 and greenlet3.5.4 recorded in requirements-browser-tested.txt.
- Why this package: Installed real browser automation executes the entire scientific UI without network downloads.
- Packages compared: Unavailable connected-browser runtime versus installed standalone Playwright/Chromium; the latter actually executed.

### D-021: Align supported Python with tested dependency metadata

- Date / phase / commit: 2026-10-11 / installation compatibility / commit containing this entry.
- Context: Further installer discovery located uv0.12.5 and CPython3.11.16, while actual quantum runtime remains CPython3.13.15.
- Symptom: QFAULT advertised Python>=3.11 despite pinned NumPy2.5.2 and SciPy1.18.1 requiring Python>=3.12.
- Root cause: Project requires-python was not aligned with the actual pinned dependency Requires-Python metadata.
- Decision: Require Python>=3.12; retain tested versions and add metadata compatibility regression. Do not claim execution on untested interpreters. Record uv's failed embedded-interpreter isolation and keep partial attempts ignored.
- Why: The regression fails before the manifest correction and passes afterward. uv also could not find a suitable executable based on LibreOffice's embedded python-core-3.13.15; no fresh install succeeded.
- Alternatives considered: Downgrade scientific packages without revalidation, claim CPython3.11 install support, or fabricate a frontend lockfile; rejected.
- Consequences: Tested runtime is still3.13.15 through the disclosed bridge. Fresh Python/frontend installation and own npm lockfile remain release blockers.
- Regression test: tests/test_dependency_compatibility.py; latest complete suite95 passed,1 warning.
- Files: pyproject.toml; tests/test_dependency_compatibility.py; .gitignore; docs/environment-stabilization.md; benchmarks/delivery-verification.json.
- Package: Existing numpy==2.5.2 and scipy==1.18.1; no scientific dependency replacement.
- Why this package: Preserve executed scientific results and correct the compatibility claim to installed metadata.
- Packages compared: Existing tested pins versus speculative older pins; existing installed uv versus missing stdlib venv launchers.

### D-022: Preserve install failures rather than fabricate a locked release

- Date / phase / commit: 2026-10-11 / submission reproducibility / commit containing this entry.
- Context: Prior HEADee712028 was clean; local operation was verified but independent installs remained unverified.
- Symptom: npm could not generate a lockfile; clean ci/check/build failed in a disposable source copy.
- Root cause: Official registry DNS resolves but HTTPS connect returns EACCES before TLS/authentication. Offline @types/react metadata is unavailable; the configured cache is absent and the standard AppData cache is EPERM. Exact npm ci rejects the missing lockfile. The policy mechanism producing EACCES is not independently identified.
- Decision: Keep PARTIALLY READY status; preserve the working bridges as explicitly development-only. Put one own-manifest normal installation recipe first in README, clearly unverified. Do not author integrity hashes, copy donor dependencies, change registries or elevate permissions.
- Why: Actual online/offline resolution failed again. Standard installed CPython3.11.16 is below the pinned Python minimum; no suitable isolated application environment was available.
- Alternatives considered: Claim bridge success as clean install, speculative package downgrade, or invented lockfile; rejected.
- Consequences: Lockfile, clean Python/frontend install and browser acceptance on that independent build remain submission blockers. Existing local demo remains functional.
- Regression test: Disposable npm resolution/ci/check/build failures, followed by95 passing retained-environment tests and successful retained build/browser execution.
- Files: README.md; docs/release-candidate.md; docs/environment-stabilization.md; benchmarks/release-candidate-verification.json; handoff.md.
- Package: No dependency added/replaced.
- Why this package: Preserve tested scientific versions.
- Packages compared: Existing pinned graph versus unvalidated downgrades; unavailable official online resolution versus genuinely incomplete cache.

### D-023: Publish paired outcomes and expose privileged simulation clearly

- Date / phase / commit: 2026-10-11 / submission evidence audit / commit containing this entry.
- Context: Percentages alone omit paired failures, and exact-state attribution must not appear to be a hardware observable.
- Decision: Add scripts/audit_release.py to match fixed/phase cases, validate raw manifests and export descriptive paired outcomes. Explicitly label higher-cost phase testing and the privileged simulator calculation in the existing UI; no policy or threshold changes.
- Why:68 pairs give56 both correct,10 phase-only correct,2 fixed-only correct and0 neither; all340 raw final records pass integrity verification. Browser label regression fails before the change and full seven-workflow suite passes after it.
- Alternatives considered: Infer statistical superiority from Wilson intervals, hide oracle access, or change defaults; rejected.
- Consequences: Fixed remains default; phase retains higher measured cost. The developer tool still requires ideal-state simulation for attribution and repair, and hashes are unsigned consistency checks.
- Regression test: scripts/browser_e2e.py higher-cost/privileged labels and actual full phase repair; scripts/audit_release.py fails on unmatched truth/manifest mismatch and checks actual recorded artifacts.
- Files: scripts/audit_release.py; scripts/browser_e2e.py; web/src/main.tsx; docs/simulator-information-audit.md; docs/diagnostic-findings.md; benchmarks/paired-policy-audit.json.

### D-024: Recovery reproduction writes only its exclusive output directory

- Date / phase / commit: 2026-10-11 / release integrity fix / commit containing this entry.
- Context: Final diff inspection found an authoritative recovery summary changed after --out reproduction.
- Symptom: New experiment IDs and artifact links appeared in benchmarks/recovery-stabilization.json despite a separate requested output directory; scientific values matched.
- Root cause: scripts/evaluate_recovery.py unconditionally wrote a second summary to that fixed repository path after writing the requested out/summary.json.
- Decision: Remove only the implicit publication line, restore the committed original summary and retain all new reproduction evidence in its new output directory.
- Why: A real12-case regression overwrote a sentinel benchmark and failed before the fix; afterward it preserves the exact bytes and both negative controls remain REJECTED. Full suite96 passed,1 warning.
- Alternatives considered: Ignore metadata-only differences, weaken preservation assertions or suppress recovery runs; rejected.
- Consequences: Reproduction cannot silently publish new results. Any future authoritative publication must be a separate explicitly reviewed operation. No scientific thresholds/results changed; prior summary is restored byte-for-byte as tracked.
- Regression test: tests/test_recovery_output_isolation.py (observed fail, then pass; full integration suite passes).
- Files: scripts/evaluate_recovery.py; tests/test_recovery_output_isolation.py; benchmarks/release-candidate-verification.json; docs/release-candidate.md.

### D-025: Transfer committed history with verified measured evidence

- Date / phase / commit: 2026-10-11 / submission transfer / commit containing this entry.
- Context: One bounded official npm and PyPI probe each still returns connect EACCES; the current source cannot independently resolve dependencies here.
- Decision: Stop network/install retries. Add scripts/package_submission.py to package the clean committed branch as a verified Git bundle, frozen summaries and verified referenced JSON as a CRC-checked ZIP, and optional genuine demo material separately. Bind sizes/SHA256/source commit in an unsigned manifest. Move machine-specific fallback instructions out of README into docs/local-development.md; document normal external installation without a donor dependency path.
- Why: Transfer should preserve history and raw evidence without a second maintained source tree, ignored dependencies or invented lockfile. collect_evidence verifies2432 actual files,10,274,729 uncompressed bytes, including referenced manifests before packaging.
- Alternatives considered: Repeated blocked installs, hand-authored lockfile, copied donor dependencies or source-only transfer losing raw evidence; rejected.
- Consequences: Bundle/source verification does not establish fresh installation. Normal CPython/npm resolution and clean-installed browser acceptance remain externally required. Packaging refuses dirty source and outside-workspace evidence.
- Regression test: tests/test_transfer.py failed before implementation and passes after; outside-artifacts references and changed manifest digests are rejected. Full98 tests pass.
- Files: scripts/package_submission.py; tests/test_transfer.py; docs/transfer.md; docs/local-development.md; README.md; benchmarks/submission-verification.json.
- Package: No dependency added or replaced; stdlib Git/ZIP/SHA256 packaging uses existing ArtifactStore verification.
- Why this package: Avoid additional tooling and preserve scientific pins.
- Packages compared: Existing stdlib/Git versus additional archive/deployment infrastructure; existing tools suffice.

### D-026: Record genuine browser footage without claiming a final narrated video

- Date / phase / commit: 2026-10-11 / judging demonstration / commit containing this entry.
- Context: Installed official Playwright/Chromium can record the currently working scientific UI without registry access.
- Decision: Add optional --record-video to the existing real browser acceptance runner. Keep default behavior and actual assertions. Capture silent unedited WebM, then provide a timed narration/shot guide and organizer-confirmation checklist.
- Why: Seven actual Aer workflows pass with download verification, history restoration, invalid422 and mobile390px checks. The resulting34.64-second VP8 clip is real footage, not a narrated three-minute final submission. Beginning/middle/end frames decode and were visually inspected; full-file re-encoding timed out with the limited installed FFmpeg, so exhaustive playback is not claimed.
- Alternatives considered: Invent a video, synthetic screenshots, mocked successes or delay all demonstration work for registry access; rejected.
- Consequences: A person must record narration, edit/inspect/approve the final video and obtain controlling deadline/eligibility/rules. The public official page contains conflicting October12/October23 submission dates; no organizer response is invented. No submission, publication or message to organizers occurred.
- Regression test: scripts/browser_e2e.py completed all seven genuine workflows with recording enabled; no unexpected console/page/request errors. Valid export exits0; disposable covered alteration exits1. Frozen final340 rows/scientific metrics reproduce unchanged.
- Files: scripts/browser_e2e.py; docs/demo.md; docs/organizer-confirmations.md; benchmarks/submission-verification.json; artifacts/submission-delivery (ignored measured/media outputs).

### D-027: Keep authoritative summaries only in the source bundle

- Date / phase / commit: 2026-10-11 / portable restore correction / commit containing this entry.
- Context: The first package's bundle cloned to exact HEAD5e18ab9 with102 tracked files and clean status. Package hashes and ZIP CRCs passed, but actual extraction detected a duplicate tracked summary.
- Symptom: Guarded restoration rejected benchmarks/diagnostic-development.json; allowing line-ending-only replacement subsequently made four tracked summaries appear modified.
- Root cause: The evidence ZIP duplicated seven authoritative summary files already in the source bundle. System core.autocrlf=true changed checkout line endings; replacing checkout bytes with original evidence ZIP bytes caused extraction conflicts/dirty source.
- Decision: Supersede D-025 archive membership: retain all authoritative summaries in the committed source bundle only. collect_evidence still reads them to verify all referenced raw records but no longer adds summary paths to the evidence ZIP. Raw evidence count is2425, with7 summaries supplied through source.
- Why: Evidence restoration must not overwrite tracked source; separating ownership avoids normalization changes while preserving every measured record.
- Alternatives considered: Force-overwrite tracked files, normalize scientific artifact bytes or ignore a dirty restored source; rejected.
- Consequences: The first package/source-copy remains a labeled failed-restore audit. Rebuild from clean corrected source and verify restoration without any file overwrite. No authoritative benchmark bytes or scientific logic changed.
- Regression test: tests/test_transfer.py:test_transfer_keeps_authoritative_summaries_in_source_only uses real quantum execution/storage. It failed before the fix; all99 tests pass afterward,1 deprecation warning.
- Files: scripts/package_submission.py; tests/test_transfer.py; docs/transfer.md; flow.md; handoff.md; benchmarks/submission-verification.json.

D-027 verification outcome: corrected source cf23b95e747b7d061323232caf48de071cef8b15 bundles/clones successfully. SHA256/size/CRC checks and guarded extraction restore2425 raw records plus39 demo files without overwriting source. Independent local source copy remains clean at exact HEAD; this is not isolated-install validation. Actual evidence: artifacts/submission-delivery/transfer-verified.json.

### D-028: Deliver real judging footage and keep compliance gates explicit

- Date / phase / commit: 2026-10-11 / final delivery only / commit containing this entry.
- Context: Starting HEADa73fc0a600b97a7b53a41bf4d9d2bb5d951f10f9 and clean main were verified. Product behavior is frozen; no algorithms, policies, thresholds, splits, dependency versions or UI code are changed.
- Decision: Reverify the existing tests, TypeScript/build, Aer demo, seven browser workflows, frozen raw manifests, exported report/tamper rejection and existing bundle/archives. Create genuine slower judging footage and editable narration/timeline documents. Do not repeat blocked package downloads or claim independent installation/narration/eligibility.
- Why:99 tests pass with1 existing deprecation warning; current demo and browser exercise real Aer. All340 frozen manifests pass. Valid/tampered export exit codes are0/1. The original34.64-second clip completes normal-speed Chromium playback with866 video frames, no dropped/corrupted frames and no media errors.
- Symptom: A first slow recording's benchmark hold showed the older75-case table while the final68-case results remained below the viewport.
- Root cause: Minimal scroll-into-view made the final heading visible but did not align the complete final table/chart; full-page screenshot handling did not guarantee the desired recorded viewport.
- Decision on framing: Correct only the delivery capture: explicitly align the final comparison and retain viewport screenshots. Actual decoded corrected-video frames show the intended table/chart. Keep the earlier camera draft as a labeled ignored audit, not the delivered picture cut.
- Alternatives considered: Alter app layout/results, invent terminal footage, synthesize successful measurements or call silent footage a narrated final video; rejected.
- Consequences: Exact voiceover and manual recording steps are provided; a person must record/approve narration. The provisional event page also schedules prompt release22 October18:00 IST and teams of2–4, while conflicting deadlines and workshop-lead/pre-existing-project eligibility remain unresolved. No claim of compliant submission is made.
- Regression test: Existing99-test suite and seven actual browser workflows pass without modification. Genuine video-frame inspection verifies capture framing; no product bug or scientific assertion is weakened.
- Files: README.md; docs/demo.md; docs/video.md; docs/video-timeline.json; docs/organizer-confirmations.md; docs/transfer.md; benchmarks/final-delivery-verification.json; flow.md; handoff.md. Generated recordings and checks remain ignored under artifacts/final-delivery.

D-028 verification outcome: corrected judging picture cut completes176.56-second normal-speed Chromium playback with4414 total frames,2 dropped,0 corrupted, no media/page errors. Representative actual decoded frames and screenshots were inspected. Narration remains unrecorded. Current proofs are benchmarks/final-delivery-verification.json and artifacts/final-delivery/judging-video-final/playback-verification.json.

### D-029: Audit the existing history and prepare the exact authorized publication

- Date / phase / commit: 2026-10-11 / final competition and publication audit / commit containing this entry.
- Context: Clean main at90503efe6576d1fcb080ef92b2c12c34f0fd050b; the user now explicitly authorizes publishing existing history to https://github.com/PrathamKapoor/QTrust.git. QFAULT remains the product; QTrust is the destination repository, separate from historical Q-TRUST.
- Decision: Preserve all history/science, configure only the selected origin and exact local identity, scan tracked files and all local Git objects, and rerun the actual quantum/build/browser/reproduction gates. Correct only public documentation and HTTP-test scope wording.
- Why: GitHub connector verifies PrathamKapoor identity, public QTrust and push/admin permission, with no main branch returned. Local Git HTTPS transport fails to connect. One probe each to official npm/PyPI still returns EACCES, so independent installation remains unverified. No credential or security-policy workaround is used.
- Symptom: Two development-document links fail relative resolution; HTTP summary states no browser is available despite separately passing browser acceptance; local media paths could be mistaken for public clone content.
- Root cause: Links were written relative to the repository rather than their document; HTTP metadata retained an obsolete hard-coded environment conclusion; local-delivery instructions lacked an explicit GitHub-clone boundary.
- Decision on correction: Resolve links relative to docs, scope HTTP metadata to what that script tests, distinguish local-only assets, and put normal installed demo/reproduction commands in README. Preserve historical audit paths, legitimate attribution and unsupported-feature warnings.
- Alternatives considered: Recreate commits through connector APIs (cannot preserve original commit metadata through the exposed interface), replace scientific defaults, fabricate a lockfile, or claim publication from connector permission alone; rejected.
- Consequences: Publication requires a normal verified Git push and matching remote SHA. It does not establish fresh-install readiness, narration or competition eligibility.
- Regression test: The actual pre-fix HTTP summary fails the no-environment-inference check; after correction real HTTP workflows pass and the scope check passes. Relative-link resolution is rechecked. Existing99 tests and seven real browser workflows pass.
- Files: README.md; docs/local-development.md; docs/browser-verification.md; docs/demo.md; docs/video.md; docs/transfer.md; scripts/http_release_smoke.py; docs/publication-audit.md; benchmarks/publication-verification.json; flow.md; handoff.md.

D-029 publication outcome: after reviewed commit27ed91f, the authorized normal push, fetch and ls-remote each failed to connect to github.com:443 (exit128). Independent connector recheck still finds no main; README retrieval returns404 with an empty-repository message. No remote SHA, upstream or successful publication is claimed. The verified committed-source/evidence/media transfer remains available; no transport/security bypass or historical-commit reconstruction was attempted.

### D-030: Stage a cinematic entry around the existing scientific workbench

- Date: 2026-10-12. Starting state: clean main at ea71bd981ee0d6a394b4d26e4a904c92bc4f5ed3. The present assignment authorizes local implementation and commits only; no push.
- Decision: Preserve React 19/Vite 8/TypeScript 6 and every backend/scientific artifact. Use hash routes through the existing FastAPI static mount. Keep one lazily mounted Workbench instance so returning home preserves a draft. Create original asymmetric flattened ribbon geometry, physically reflective dark metal and procedural strip-light PMREM environment, informed by Mental.ai/Vantage without copying their unlicensed source. SAT-SA informs the light sidebar, hierarchy and evidence presentation.
- Components and rights: Adapt the four requested official React Bits components, retaining MIT + Commons Clause terms. Install only three, ogl and development Three types. Official npm access now works; generated lockfile and npm ci succeed. This supersedes the earlier frontend-registry blocker, but not the unverified isolated Python environment. Source revisions/terms are in docs/frontend-sources.md.
- Lifecycle: Hyperspeed and TechText each have a bounded 650ms stage, with session memory, Skip/Escape and reduced-motion fast entry. The hero creates the sculpture and desktop-capability-gated MoltenMetal. Enter locks repeated activation, freezes the sculpture, removes atmosphere, reframes for 470ms, then runs an 850ms static-only PixelSwap with a 1150ms safety deadline. Workbench navigation removes all landing renderers and restores heading focus. No copied live workbench or WebGL scene is used in pixel windows.
- Tradeoffs: DPR caps, lower mobile geometry, visibility/intersection pausing and explicit resource disposal limit cost. WebGL absence uses a clearly identified static SVG. System sans-serif/monospace fonts avoid external font requests. The Three shared chunk remains above Vite's 500kB warning; cold shader compilation in headless software rendering can exceed the intended 1.3-second timer sequence. No FPS or GPU timing guarantee is claimed.
- Verified defects fixed: Saved-run requests could resolve out of order, missing-record errors retained stale outputs, initial API errors were hidden on overview/history, and home navigation discarded drafts. Request generation guards, clearing stale selection, shared alerts and a persistent workspace resolve these; real-response browser regressions cover them. Scientific behavior is unchanged.
- Verification: 99 Python tests pass with one existing Starlette warning; project-owned TypeScript/build pass; seven real Aer browser workflows preserve measurements, phase diagnosis, independent recovery, export hashes, integrity, history and invalid422. Additional responsive, reduced-motion, fallback and navigation evidence is recorded in docs/frontend-verification.md. Genuine screenshots are inspected after waiting for actual GL frames; frozen browser clocks capture short states, never synthetic pixels or science.


### D-031: Rebuild the rejected landing while preserving the accepted workspace

- Date: 2026-10-12. Starting state: clean main at c5fb023a5bbf53a9790548731eebae9b2df7101a. Local changes/commits only.
- Reproduction: Actual baseline screenshots/DOM measurements show a 73%-width stage, 219px wordmark, four crowded closed sweeps and weak neutral reflections. MoltenMetal is mounted but shader alpha, dark palette, extra CSS opacity and vignette suppress its surface. Copy/actions exist but lose hierarchy; the fixed-height clipped root has no supporting public-page sections. Details: docs/landing-recovery.md.
- Decision: Separate readable left typography/actions from a 46%-width right art stage. Replace closed sweeps with original thinner open ribbons/strands and a neutral reflection studio. Add genuine workflow/capability/frozen-evidence sections and working public navigation. Preserve App/main/workbench CSS, quantum APIs, policies and PixelSwap.
- Rendering: Initialize MoltenMetal uniforms before first draw, reuse its capability canvas, retain perceptible violet/graphite folds, provide static shader frames on mobile/reduced-motion/lower-core views, and retain explicit disposal/visibility controls. Darken reflective base tones after inspecting the first rebuilt screenshots. A labelled original SVG remains the no-WebGL fallback.
- Rights/dependencies: Mental.ai/Vantage remain references only; no verified donor license authorizes copying. Adapted React Bits notices remain. No new packages or backend changes. Existing React/Vite and project-owned lockfile remain; Python/Playwright bridge is disclosed.
- Verification: New real-browser regression first fails on missing workflow content, then passes all five requested viewports, CTA hit tests, anchor routing and keyboard footer entry. TypeScript/build, 99 Python tests, seven real Aer workflows and cinematic/reduced-motion/fallback checks pass. Evidence, performance measurement and limits: docs/landing-recovery.md. The user's aesthetic approval remains manual.


### D-032: Replace the isolated oval with a shared diagonal ribbon/typography stage

- Date: 2026-10-12. Starting state: clean main at463c1970922c7f2ba620cd431b7a3023a2782914. The user rejected the previous hero and authorizes only hero art direction, preserving the accepted workspace and transition.
- Confirmed causes: Similar end points and left/right trajectories create an oval envelope despite open paths; camera-facing surfaces and broad reflection cards read as uniform silver; triangle winding faces inward and duplicate profile seams distort shading. Separate text/art stages eliminate the requested spatial relationship. Low spatial shader scale/default fold produces large background streaks. Exact comparison: docs/hero-art-direction.md.
- Decision: Original two broad diagonal ribbons plus two secondary paths, varying width and profile rotation, outward winding and smooth seam normals. UV-aligned micro-roughness/bump and supported physical-material anisotropy add subtle brushing. Neutral strips/fill define graphite metal; violet remains secondary. Identical per-letter word planes surround the canvas, protecting selected letters without hiding the whole name. Copy/actions sit below the shared stage. Remove decorative captions and preserve only meaningful eyebrow/simulator label.
- Scope: React/Vite, backend/science and existing below-hero content stay intact. No new dependency. Mental.ai source was inspected (including the entry engine actually used by NeuralStage), but no verified reuse license permits copying; geometry/materials/composition remain original. Existing React Bits MoltenMetal source/notices remain; only hero props retune its atmosphere. PixelSwap state/timers/implementation remain unchanged; only hero framing at the transition boundary adapts.
- Review: Actual pre-edit, first rebuilt and second rebuilt screenshots were opened. First-pass dark reflections, excessive micro-bump and differing word-plane metrics were corrected. The strengthened browser regression reproduces the absent shared-depth planes before implementation. Its short reframe capture now freezes genuine timers, retaining assertions, and allows actual overview data up to30s under headless load. No scientific output is mocked.
- Evidence: TypeScript/build and99 Python tests pass (one existing warning). Final browser checks, captured visual evidence, measured limits and persistent server details are recorded in docs/hero-art-direction.md and handoff.md after execution. Human visual approval remains outstanding.

### D-033: Make a tall double spiral the hero centerpiece

- The user explicitly supersedes the previous diagonal art direction with a DNA-like metallic spiral. The actual baseline reveals a short, wide path envelope concealed by foreground letters; changing material alone cannot correct that silhouette.
- Original spiral trajectories replace the diagonal paths: two dominant ribbons, two narrow companions and a fine violet filament. Tall central framing weaves through U/L, with A/T retained in front. Copy and actions form one lower-left group. Refined neutral fill and subtler brushing preserve black chrome without coarse texture.
- Preserve workbench, PixelSwap implementation/state/timers, backend, benchmarks, lower sections, MoltenMetal lifecycle and dependency graph. Existing fallback and reduced-motion paths retain the new silhouette. Reference inspection, rights, iterative review and limitations: docs/helix-hero.md. Human visual approval remains pending.


### D034 — Blind observations and bounded measurement capabilities (2026-10-13)

Continue project development on hardening/blind-measurement, preserving main/public snapshot tags. Eligibility and presentation work were explicitly removed from scope by the user. CPython 3.13 installed .[aer,dev,browser] independently; an archived checkout passed npm ci/check/build with the genuine existing lockfile. Keep the bridge only as historical fallback. CI is configured after these successes, without a passing remote badge.

BlindChallenges persists allowlisted public observation/diagnosis/freeze/reveal documents separately from private setup and ArtifactStore investigations. It reuses observe/investigate rather than a second engine. Freeze binds the public diagnosis to its observations and private engine prediction digest; reveal and nested exports verify those bindings. Pre-reveal history/downloads never return hidden metadata. This is not secrecy from local administrators.

MeasurementOnlyAnalyst accepts an analytical target contract, counts, and MeasurementPort with only budgeted measurement/calibration actions. It cannot access candidate state, mutation or noise configuration. Relative phase requires complementary witnesses; a measured discrepancy cannot generally distinguish logical faults from gate noise. Ambiguous attribution is retained, and measurement-only recovery is rejected. Existing simulator-assisted diagnosis/recovery and frozen benchmarks remain authoritative and unchanged. The committed 52-case/four-policy holdout will be run only after implementation freeze; no tuning on its outcomes.


### D035 — Preserve negative holdout findings and measured traceability (2026-10-13)

Protocol was committed before implementation; diagnostics were frozen at f7a832b before the 208-run untouched holdout. No algorithm was tuned afterward. Complementary measurements detect more failures but do not improve strict measurement-only causal classification; retain ambiguity and disable measured recovery. Low configured noise remains undetected and four QFT angle changes preserve the fixed-input state. Publish all rows, matrices and failure IDs separately from the old 68-case evaluation.

Historical reproductions match 300 original rows, 340 final rows and 12 recovery trials; all 23 frozen summaries stay byte-identical. Preserve raw evidence and extend the existing collector to check new manifest_sha256 references. Redact backend exception text in blind routes and allowlist additional diagnostic/verification counts, so shot cost can be inspected without truth leakage. These post-holdout fixes do not alter diagnostic inputs or decisions. Keep eligibility/presentation excluded per the user's clarification.


### D036 — Custom circuit laboratory with budgeted, sequentially valid evidence planning (2026-10-13)

Added `qfault/lab.py` beside, not replacing, the template workflow. Circuits are validated structured JSON reusing `Gate`; input is a declared computational-basis bitstring whose X preparation is added by the lab and counted. Contracts (Pauli expectations, Z/X/Y distributions) are declared independently of the candidate; Qiskit order (leftmost = highest qubit) is documented and tested. Contradictory Pauli claims are rejected (anticommutation bound and a correlation-polytope LP). Target-state contracts, OpenQASM, measured recovery and gate localization were deliberately not implemented.

Sequential validity: intervals are computed only on a prespecified per-group shot grid and every interval shares a union-bound alpha = alpha_total/(claims x looks + 1), so adaptive choice and stopping cannot inflate error. Detection, attribution, localization and recovery are separate fields; measurement-only attribution is never a unique logical claim. The simulator-assisted path adds one labelled privileged `exact_expectations` operation and uses the same `ExecutionBudget` ledger.

Bug found by test: the correlation-polytope constraint signs were wrong and let a contradictory triple through; fixed, with regression test `test_contradictory_claims_rejected`. Evaluation (docs/custom-circuit-lab.md): adaptive matches the fixed and complementary schedules and beats only random selection; this negative result is retained. Storage reuses ArtifactStore (investigation schema_version 2); old artifacts, the 300/340-row and recovery evaluations, and the 52-case holdout are untouched. No new dependencies (scipy `linprog`, already pinned).


### D037 — Target-state contracts with rigorous witness bounds; regression gaps closed (2026-10-13)

Regression gaps: the full browser suite was rerun. `blind_challenge_e2e` failed intermittently: root cause, the page-load history GET held the API lock and the non-blocking Start returned 409. Mutating challenge routes now wait up to 30 s for in-flight reads (regression test `test_start_waits_for_concurrent_history_read`). The frozen 117-case custom-lab holdout was replicated on Aer without retuning: 113/117 category agreement per policy; all 16 disagreements are near-threshold correct circuits flipping between INSUFFICIENT and NO_DISCREPANCY in both directions; fault and noise detection agree fully. A new `scripts/lab_e2e.py` uses Playwright context viewports (390/375/360) and found clipped long tokens and a crushed table; fixed with wrapping and scrollable tables.

Target state: `TargetStateContract` (strict [re, im] pairs, 1e-6 normalization tolerance, no silent normalization) in new `qfault/target.py`, integrated through the existing Contract union, `plan`/`group_paulis`, `_Port`, `ExecutionBudget` and ArtifactStore; no second engine or ledger. Measured witnesses produce only an F bound (expansion + stabilizer projector + Fuchs–van de Graaf, intersected); exact fidelity is a separately labelled privileged simulator output. Union-bound alpha over all catalog terms x looks + control. `adaptive_witness` uses a plug-in marginal bound-improvement proxy (one-step lookahead was found myopic for stabilizer generators during implementation and replaced before the protocol freeze). Two test-found bugs: string amplitudes were coerced (now strict floats); a wrong expectation in a test (H|00> has F=1/4 with Bell) was corrected, not the engine.

Evaluation protocol frozen at 68f33b4 before the 414-case holdout. Outcome: rigorous coverage (165/165), no false alarms, but adaptive_witness is not uniformly better than a fixed or coefficient-weighted order (slightly worse at the tight budget, slightly better at the ample budget); it clearly beats random and the complementary schedule at the tight budget. Retained as published. Details: docs/target-state-witnesses.md.


### D038 — Counterfactual measured recovery (2026-10-13)

Extend completed target-state e90acf0 in the recovery worktree; preserve checkpoint/target-state-e90acf0 and the original branch. Add deterministic bounded interventions and a contract observation adapter reusing lab grouping, counts and target-only bounds. Single-look multiplicity covers candidates and fresh paired confirmation; explicit reserve prevents screening exhaustion. Interval overlaps retain plausible loci; operational tie-breaking never proves causal origin. Clean and significant readout-control cases abstain. Development point ranking matches conservative verified repairs; retain this negative finding. An adversarial test exposed contradictory bounds being eligible to verify; guard added before final protocol freeze. See docs/counterfactual-recovery.md. Legacy recovery, target decisions, blind isolation and frozen benchmarks unchanged.

### D039 — Preserve the matched-budget negative selection result (2026-10-13)

Committed `configs/counterfactual-protocol.json` and its code/data digests at 5034972 before the 62-case, two-seed Aer holdout. Conservative interval and point discrepancy selection each independently verified 16/62; conservative used 90,112 fewer shots and avoided five rejected noise/repair proposals, at the cost of five additional inconclusive outcomes. Retain both policies in the result: do not claim conservative ranking improves recovery rate. The 14/14 logical-locus set coverage still leaves one non-ambiguous behavior-restoring edit at a different gate, and two intentionally ambiguous alternatives; causal identity remains unestablished. Full rows, class tables and manifests remain in the local holdout output.

### D040 — Integrated release audit corrections (2026-10-13)

Fast-forwarded `hardening/blind-measurement` to the verified descendant recovery commit; kept the recovery branch/checkpoint and local `main`. An independent raw-record verifier rechecked all 310 manifests, reconstructed sampled contract intervals and costs, and replayed 310 stored requests with matching decisions/counts. The audit found one real bounded-budget defect: the preflight reserved fresh confirmation but not the possible readout-control batch. It now reserves both before observation and limits candidate screening accordingly; a regression test reproduces the former failure. A UI interval was ambiguously labelled “Improvement interval”; now it is explicitly the dimensionless reduction in normalized worst-claim discrepancy, not fidelity or total variation. Preserve the original 62-case data and source digest; the final code change postdates that frozen evaluation and does not rewrite its evidence. Details and provenance limits are in `docs/counterfactual-recovery.md` and `handoff.md`.


### D041 — Replace the landing hero with the MENTAL.AI entry composition (2026-10-13)

Repeated original reinterpretations of the reference sculpture were rejected. C:\Projects\DE is the MENTAL.AI checkout (upstream shreshthgod/mental.ai); it has no license file and mixed authorship (PrathamKapoor/shreshthgod). Earlier decisions (D-032/D-033) stopped at that gap; this time the owner confirmed the co-author's permission, so the hero modules are transplanted verbatim with attribution (docs/hero-transplant.md, THIRD_PARTY_NOTICES.md). Geometry, materials, studio environment, camera, timing, word planes and CSS are source values; only framing and branding changed: centred pre-handover framing (no login column), the reference handover reused for Enter Workbench before the unchanged PixelSwap, wordmark scaled x1.35 for six glyphs, reference nav styling on QFAULT links. Tokens/.cta/.label are scoped to `.entry` so the workbench palette is untouched. Hyperspeed, TechText, MoltenMetal and the previous procedural sculpture were deleted after confirming no other importers. Inter is vendored (OFL) instead of adding an npm dependency. Landing browser suites (cinematic_e2e, landing_recovery_e2e, inspection_smoke) were rewritten for the new hero with equivalent or stronger checks (7 viewports, layer order, reduced motion, 2D fallback, handover, GL disposal). No backend, benchmark, schema or science change.


### D042 — Release engineering: locked installs, maintained CI, product README, server diagnostics (2026-10-13)

- CI: the published versions were verified from the official repositories (checkout v7.0.1, setup-python v7.0.0, setup-node v7.1.0; all `node24`, moving `v7` tags exist; only removed input is setup-python `pip-install`, unused here). The runner is pinned to `ubuntu-24.04` instead of `ubuntu-latest` (migrating to Ubuntu 26 from 2026-10-19) until a newer image is tested. Read-only `contents` permission, `persist-credentials: false`, job timeouts and per-ref concurrency were added. The frontend build stays before pytest (the clean-checkout 503 root cause from the first published run). A separate `browser-smoke` job starts a real server and runs `scripts/release_smoke.py` in Chromium; it could not be executed locally on Linux (WSL lacks NSS/ALSA libraries and non-interactive root) and is unvalidated until it runs on GitHub.
- Dependencies: `requirements.lock` is a universal hashed lock produced by `uv pip compile` from `pyproject.toml` (still authoritative) for CPython 3.13 with aer/dev/browser extras. It is consumed by plain `pip --require-hashes`, so users need no new tool. Fresh installs from separate clean clones: Windows CPython 3.13.2 and Linux CPython 3.13.15 (Ubuntu 26.04/WSL2, Node 24.19.0 from a checksum-verified official tarball) resolved identical package sets (Windows adds colorama by marker), passed pip check, the Aer smoke (identical counts) and 243/243 tests after the frontend build. The older `requirements-*-tested.txt` files remain as historical observed closures. macOS is untested and not advertised.
- Frontend bundle: measured, not changed. The landing paints first at ~0.40-0.46 s locally with a 210 KB entry chunk; Grainient (50 KB) and the NeuralStage/Three.js chunk (566 KB uncompressed) load lazily after first paint; a direct workbench route never downloads Three.js.
- Server lifecycle: the server that disappeared during publication (PID 34428) was launched by a different session with output to that session's console; no Application/System crash or WER event exists for python, and no log was written. Cause is undetermined; no application defect is indicated. Findings: a Windows venv `python.exe` is a launcher whose child is the real interpreter (different PID); stopping the launcher also stops the child. `qfault serve` now accepts `--port`, stays bound to 127.0.0.1, prints its PID, and exits with code 2 and a clear message if the port is taken (previously uvicorn reported "startup complete" before failing to bind). Tests: tests/test_serve.py.
- Presentation: README rebuilt as a product page (quick start tested from clean clones, capability table, evidence table with denominators and links, limitations, troubleshooting). The previous README is preserved in docs/release-history.md. Historical documents carry dated banners rather than being rewritten. Screenshots in docs/media were captured by scripts/capture_readme_media.py from the real UI against a throwaway store with genuine Aer runs. The frozen counterfactual summary (SHA-256 8fb0e091...) is now committed byte-identical as benchmarks/counterfactual-recovery-holdout.json so the README can link it.
- Stale UI claim corrected in the frontend only: lab investigations said repair selection from measurements is not implemented, although measured counterfactual recovery exists as a separate action. `qfault/lab.py` is pinned by the frozen counterfactual protocol digest, so the recorded engine message is left unchanged and the UI states the current position, still showing the recorded note.

### D043 — Enforce analyst inputs and calibrated witness interpretation (2026-10-16)

The independent audit reproduced eleven failures before correction. An actual-byte
ASGI request guard now precedes JSON parsing, rejecting oversized chunked/lying
length bodies and malformed lengths. `lab.PolicyConfig` removes candidate,
environment and backend fields from policy inputs; real Aer tests poison exact
candidate helpers and executor truth metadata while exercising diagnosis and
fresh recovery. This hardens a trusted application data flow, not a malicious-code
sandbox.

Qiskit demonstrates that basis-dependent gate noise can make correctly estimated
Bell witness means incompatible with any single state. Incompatible bounds now
remain unresolved. Declared noisy target investigations withhold preanalysis
fidelity certification, and target recovery abstains without calibrated
measurement-channel support. Historical symmetric-readout effective-state results
remain valid within their separately stated interpretation. The audit and five
explicit observability examples are in `docs/information-boundary-audit.md` and
`benchmarks/identifiability-v1.json`. Old frozen results are unchanged; these
scientific corrections intentionally postdate their source fingerprints.

### D044 — Freeze an external, reference-relative evaluation (2026-10-16)

The full pinned QASMBench tree is inventoried. Fourteen canonical sources meet the
static adapter and existing size limits; a deterministic path split reserves nine
for holdout. Contracts derive from separately parsed original source, not mutated
candidates. The importer rejects dynamic/unsupported semantics, records every
transformation and terminal mapping, and verifies complete operator preservation.
Upstream bytes and custom redistribution terms are retained.

Protocol commit `cac14a5` freezes source/dependency/dataset hashes, seeds,
mutations, budgets, comparators and metrics before final outcomes. Existing
policies were not tuned. All 1,962 diagnostic and 270 recovery rows are retained;
the independent report audit checks all 2,206 executed exports. Adaptive Pauli
detects 103/108 versus fixed 102/108; target methods mostly tie. Conservative
recovery verifies 10/41 eligible, rejects eight and makes no noise-only proposals.
Point ranking also verifies ten but rejects 31, including 13 noise-only proposals.
These are descriptive small-circuit results, with repeated seeds and correlated
mutants, not superiority or universal-generalization claims. Raw reports,
architecture results, failures and reproduction live in
`benchmarks/external-holdout-v1/` and `docs/external-validation.md`.

### D045 — Preserve prior work, release boundaries and the existing application (2026-10-16)

The original six reviewed release commits were normally fast-forwarded to public
main `35cbbb9`; both hosted jobs passed in run `38787130996`. All new research
remains local on `research/external-validation`. Original refs, worktrees and
scientific history remain reachable; no force push or rewrite occurred here.

Primary-source comparison finds substantial overlap: Qrep already performs
sampled gate-edit repair and MQT Debugger supports measured runtime assertions.
Muskit is a mutation-testing tool and QCEC supplies a stronger reference-circuit
oracle. Four executed QCEC examples explain task boundaries rather than rank
unmatched tools. No new cryptographic identity system or hardware integration is
justified; unsigned hash consistency remains explicit.

The external QRNG demonstration executes through the existing lab/editor,
complementary measurements, bounded screening, frozen selection and fresh
verification. It retains causal uncertainty and verified exports. The approved
hero, handover, PixelSwap and scientific shell are unchanged. UI additions only
explain calibration-related abstention. Windows and Linux clean-clone locked
installs, frontend checks/builds and 335 Python tests passed; full Windows browser
regressions also passed. Linux browser research coverage and physical hardware
remain separately untested. See `docs/current-state.md`.

### D046 — Reject malformed API inputs before error serialization (2026-10-16)

Final adversarial tests reproduced HTTP 500 responses for nonfinite numbers,
excessive nesting, invalid Unicode and corrupt saved replay requests. The API
now validates bounded JSON before schema parsing and rejects conflicting length
headers. Invalid input returns a client error without executing an investigation.
Replay requests are validated before acquiring the execution lock. Scientific
thresholds, frozen records and the approved frontend are unchanged.

The separate evidence reconciliation checks the complete frozen case grid and
maps 2,232 evaluation rows to 2,206 unique executed exports plus 26 explicitly
unsupported QRNG entangler deletions. It complements payload verification rather
than authenticating authorship or historical execution time.

### D047 — Record the final gate without replacing frozen evidence (2026-10-16)

The adversarial gate independently reconstructed the complete external archive,
validated original/imported full operators, rederived statistical intervals and
executed an outcome-independent subset frozen in a separate commit before its
run. All 72 configurations reproduced, including abstentions and rejections.
Fresh Windows/Linux installations pass 449 tests; ten Windows Chromium suites
pass. The original 88 benchmark/config files remain byte-identical.

`benchmarks/final-adversarial-verification-v1.json` records GO for the documented
bounded simulator scope, exact tested revisions and remaining untested platforms.
Git ordering does not authenticate historical execution timing; physical
calibration and hard backend cancellation remain unestablished. Publication is
still separately authorized; no remote mutation occurred during this gate.

### D-048: Separate source snapshots from explicitly scoped research evidence packages
- Date / phase / commit: 2026-10-22, reproducibility, uncommitted
- Context: The owner requests implementation and release of the actual QFault checkout. The existing package command requires ignored historical runtime files and includes all reachable Git history; the current external study already has a deliberately tracked raw archive.
- Decision: Add build_package and verify_package with source-only/evidence-inclusive modes, committed source snapshots, exclusive atomic completion, bounded archive checks and an explicit evidence availability ledger. Retain collect_evidence for historical verification compatibility. The evidence-inclusive scope is the current external study only; historical availability is stated separately.
- Why: New regression tests failed because the package API was absent, then all seven package/legacy transfer tests passed. The independent external audit verifies 2,206 exports and reconciles all 2,232 attempted rows. The old default must not manufacture missing historical data or copy private runtime directories.
- Alternatives considered: Full Git bundle (unreviewed historical/private content risk); sweeping artifacts (runtime ownership violation); silently dropping missing evidence while claiming complete history (scientifically misleading).
- Consequences: Supersedes D-025/D-027 packaging defaults, not historical archives. Output has no Git history. Full-current evidence does not imply availability of every historical study. Fresh extraction/install remains a separate gate. Current source byte identity is preserved in archive members.
- Files: scripts/package_submission.py, tests/test_release_package.py, docs/evidence-availability.md, docs/implementation-ledger.md, decisions.md, flow.md, handoff.md
- Symptom: Historical packaging fails when referenced ignored files are absent in a fresh clone.
- Root cause: main unconditionally calls collect_evidence for fixed legacy summaries and has no source-only contract.
- Regression test: tests/test_release_package.py (three red failures before implementation; seven targeted package/legacy tests passed afterward).

### D-049: Convert bounded native circuits without silently changing their semantics
- Date / phase / commit: 2026-10-22, circuit import, uncommitted
- Context: The existing static QASM evaluation adapter has no native QuantumCircuit conversion API or ergonomic custom CLI path. The owner explicitly requires both and provenance through replay/export.
- Decision: Add qasm_import.from_qiskit for the exact eleven built-in gates already supported by Gate. No native transpilation runs. Nonzero input preparation remains exclusively in CustomCircuit.preparation. Global phase and indexed source instructions are recorded. Barrier and terminal-measurement removal require explicit options. Add from_qasm2 as an opt-in public wrapper around the unchanged historical adapter, plus import-qasm/lab/measured-recovery CLI commands. CustomCircuit gains optional validated ImportProvenance; absent provenance is excluded from serialization to preserve legacy bytes and IDs.
- Why: Nine native tests and one CLI test failed before implementation. Independent Qiskit complex-state and input preparation checks, precise unsupported semantics and export persistence now pass (11 targeted tests); the broader native/QASM/recovery set passed 61 tests. A CLI feasibility integration initially called the wrong helper signature; inspection confirmed feasibility(circuit, contract, request), and the actual CLI regression passed after correction.
- Alternatives considered: QPY/pickle upload (unsafe/unnecessary); arbitrary Python module loading (unauthorized execution); silent transpilation (changes gate/noise/edit semantics); deriving a contract from the converted candidate (circular).
- Consequences: Supersedes D036's deliberate absence of import, without changing its measured policy. New source hashes invalidate untouched status under old source-pinned protocols; preserve those guards and version current-release verification separately. Provenance describes the original converted input; derived edits retain that ancestry rather than claiming to be the original representation. Native custom instructions, reset, unbound parameters, dynamic control and postmeasurement gates are rejected.
- Files: qfault/qasm_import.py, qfault/lab.py, qfault/cli.py, tests/test_native_import.py, tests/test_custom_cli.py, decisions.md, flow.md, handoff.md, docs/implementation-ledger.md
- Symptom: import-qasm is rejected as an invalid CLI choice; no public native converter exists.
- Root cause: CLI only exposes the template workflow; QASM importer is evaluation-only and CustomCircuit has no import-provenance field.
- Regression test: tests/test_native_import.py; tests/test_custom_cli.py.

### D-050: Reject coercible scientific strings and booleans at schema boundaries
- Date / phase / commit: 2026-10-22, input correctness, uncommitted
- Context: The owner explicitly requires rejecting misleading strings and malformed numerical structures. Eight regression examples were accepted by the existing schemas, including a boolean qubit index and a string probability.
- Decision: Use strict scalar numbers for Gate qubits/angles, Noise, Pauli/distribution values and tolerances, target tolerance, and lab/recovery alpha/time settings. JSON integer numbers remain valid where real values are expected; strings/booleans do not.
- Why: All eight red regression cases demonstrated actual coercion. Validation must precede execution; converting a string to a scientific number silently hides malformed input.
- Alternatives considered: Global strict configuration (would also reject valid JSON array-to-tuple inputs in Python model validation); frontend-only validation (does not protect CLI/API).
- Consequences: Invalid formerly coercible requests now fail validation. Correct numerical requests and historical artifact inspection remain supported. Scientific formulas and threshold values are unchanged; historical source digests are not rewritten.
- Files: qfault/quantum.py, qfault/lab.py, qfault/target.py, qfault/counterfactual.py, tests/test_strict_scientific_input.py, decisions.md, flow.md, handoff.md
- Symptom: Gate qubits [true]/["0"], angle "0.2", and probability "1" pass validation.
- Root cause: Individual Pydantic numerical fields used coercive defaults despite the Strict base class only forbidding extra fields/nonfinite values.
- Regression test: tests/test_strict_scientific_input.py.

### D-051: Patch the two verified dependency advisories without scientific upgrades
- Date / phase / commit: 2026-10-22, dependency safety, uncommitted
- Context: Fresh npm audit reports Vite 8.2.2 affected by six development-server advisories, including high-severity GHSA-587h-7wmj-h5pm. pip-audit 2.10.0 reports certifi 2026.7.22 affected by PYSEC-2026-4320 / GHSA-6q48-6c7w-9gw2.
- Decision: Pin Vite 8.2.4 (same minor) and certifi 2026.10.19 in development extras, regenerate the existing npm/hashed Python locks with official tooling, and leave quantum dependencies unchanged. Install pip-audit separately under ignored .local/contract-release/audit-tools, outside the application closure. Extend strict validation to edit positions/angles after two additional red tests.
- Why: npm registry confirms Vite 8.2.4 MIT and Node ^20.19.0 or >=22.12.0, compatible with actual Node 24.19.0. npm ci/audit/check/build pass with zero reported advisories after the update. pip-audit identifies certifi 2026.10.19 as the fix. The direct development constraint prevents future lock regeneration from restoring the affected trust store.
- Alternatives considered: npm audit fix --force or latest Vite minor (unnecessary broader change); ignore a known advisory because the served application is local (does not satisfy the release scan); downgrade quantum packages (unrelated).
- Consequences: Frozen environment records remain historical. Advisory scans are scoped and date-specific, not a security guarantee. No application dependency on the audit tool is added. Existing Three.js size and Starlette/httpx deprecation warnings remain.
- Files: web/package.json, web/package-lock.json, pyproject.toml, requirements.lock, qfault/interventions.py, tests/test_strict_scientific_input.py, decisions.md, flow.md, handoff.md
- Package: vite 8.2.4 (MIT); certifi 2026.10.19 (MPL-2.0); external audit-only pip-audit 2.10.0 (Apache-2.0).
- Why this package: Retain the existing build tool and TLS trust store with the scoped advisory fixes; pip-audit queries current Python advisories.
- Packages compared: Existing versions (reported affected); Vite 8.3.5 (larger unnecessary upgrade); alternate build/audit stacks (no verified need).

### D-052: Bind replay identity and distinguish new-seed reruns
- Date / phase / commit: 2026-10-22, evidence lifecycle, uncommitted
- Context: Custom/recovery replay already creates a new investigation but does not persist the source identity or provide explicit new-seed semantics. The regression confirms the parent ID is absent.
- Decision: Add ReplayOptions with an optional strict bounded seed to the two existing custom/recovery replay routes. Persist source_experiment_id and deterministic_replay/new_seed_rerun in the new record before ArtifactStore.save. Keep the original immutable and share run_lab/run_recovery admission/error paths.
- Why: Same-seed repeatability is different from a new-seed rerun; both need traceable ancestry. Omitted/empty options preserve existing browser requests.
- Alternatives considered: Reuse the original ID (violates immutable records); silently change seeds (ambiguous scientific meaning); add duplicate execution routes (unnecessary).
- Consequences: New-seed reruns change only the seed, not the declared circuit/contract. Simulator model bias remains shared. No external timestamp or independent physical experiment is claimed. Legacy artifacts are not rewritten.
- Files: qfault/api.py, tests/test_replay_identity.py, decisions.md, flow.md, handoff.md
- Symptom: A replay's replay.source_experiment_id is absent and a requested new seed is ignored by the old route signature.
- Root cause: The routes revalidate the saved request and call run_lab/run_recovery without parent metadata or replay options.
- Regression test: tests/test_replay_identity.py (failed before implementation).

### D-053: Foreground measured recovery with one recorded reporting source
- Date / phase / commit: 2026-10-22, product evidence, uncommitted
- Context: Landing/overview emphasize older 68-case template results despite the complete current external measured-recovery archive. Repeating constants across pages risks drift and obscures denominators/evidence availability.
- Decision: Add GET /api/research derived from the frozen external summary, and reuse ResearchEvidence on landing/overview. Display both policies, overall/eligible denominators, rejected proposals, noise-only proposals, shots, source/protocol and evidence availability. Add a prominent Custom Circuit Laboratory action while preserving template entry and all hero/transition code. Add a tightly scoped Gitleaks allowlist for the exact source-digest false positive.
- Why: The route regression failed 404 before implementation. The independent raw audit checked the underlying external aggregates. Gitleaks 8.30.1 scans 108 historical commits and identifies api.py's recorded 64-hex source fingerprint as a generic key; the field is /provenance/implementation/qfault\\api.py, not a credential. The allowlist matches that exact file and digest-shaped api.py match only.
- Alternatives considered: Hardcode new metrics in components (drift); replace hero/art (no verified need); hide all scanner findings (unsafe); remove historical evidence (violates preservation).
- Consequences: Loading/failure has no fabricated metrics. Availability reports file presence, not a fresh audit on every HTTP request. Historical benchmarks remain explicitly historical. Existing template browser entry remains functional.
- Files: qfault/api.py, web/src/components/ResearchEvidence.tsx, web/src/components/landing/Landing.tsx, web/src/components/Overview.tsx, tests/test_research_summary.py, .gitleaks.toml, decisions.md, flow.md, handoff.md
- Regression test: tests/test_research_summary.py independently reconciles displayed fields with frozen per-case rows.

### D-054: Refuse unsupported artifact schemas independently of valid hashes
- Date / phase / commit: 2026-10-22, evidence verification, uncommitted
- Context: Two regressions show schema_version=999 passes verification when the recorded hashes match; a consistency digest does not authorize interpreting unknown schemas.
- Decision: Add _supported_investigation and enforce manifest schema 1 and the existing template/custom/recovery version-kind pairs in local/export verification. Preserve all old supported artifacts; unsupported records fail explicitly and raw files remain inspectable without migration.
- Why: Both tests failed before the guard, including a rehashed unknown investigation. The owner requires explicit unsupported-schema behavior.
- Alternatives considered: Silently treat every record as the latest format (changes historical scientific meaning); rewrite old records (forbidden); rely on embedded valid=true (not verification).
- Consequences: Hash consistency remains separate from scientific correctness/authenticity. New schemas need an explicit compatibility decision. Existing schema 1 template, 2 custom, 3 recovery records remain supported.
- Files: qfault/storage.py, tests/test_artifact_versions.py, decisions.md, flow.md, handoff.md
- Symptom: Unknown manifest/investigation schema 999 verifies successfully.
- Root cause: Verifiers check digest/canonicalization membership but never inspect schema-version support.
- Regression test: tests/test_artifact_versions.py.

### D-055: Enforce the declared local host and same-origin mutation boundary
- Date / phase / commit: 2026-10-22, local API trust, uncommitted
- Context: The server binds loopback but accepts arbitrary Host values; a regression reproduces HTTP 200 for attacker.example. A local-only trust model needs an explicit browser origin/host boundary.
- Decision: Add LocalRequestBoundary outside the existing byte limiter: require one loopback Host, reject credentials/path/invalid port in authority, and reject state-changing requests with an Origin differing from the actual scheme/Host. CLI clients without Origin remain supported. testserver is allowed only in explicitly constructed test/store applications, not the default served application. Forwarded headers are not trusted by this middleware.
- Why: Browser JSON/CORS constraints alone do not validate the Host used to access a loopback service. The observed arbitrary-host response contradicts the declared local trust boundary.
- Alternatives considered: Authentication/cloud hosting (outside scope); blanket CORS allowance (weakens boundary); shared secret configuration (unnecessary for the specified local workbench).
- Consequences: Default served hosts are localhost, 127.0.0.1 and ::1; command-line/API clients should use those names. Cross-origin mutation returns structured 403, untrusted host 400, before execution. This is not an authenticated multiuser service or malicious-local-process sandbox.
- Files: qfault/api.py, tests/test_local_trust.py, decisions.md, flow.md, handoff.md
- Symptom: Untrusted Host attacker.example is accepted with HTTP 200.
- Root cause: Loopback binding alone does not inspect the HTTP authority or Origin.
- Regression test: tests/test_local_trust.py (failed before implementation).

### D-056: Recover authentic historical measurement evidence without fabricating a rerun
- Date / phase / commit: 2026-10-22, historical evidence, uncommitted
- Context: The preserved recovery worktree contains the original frozen 310 investigations. Its summary is byte-identical to the committed 8fb0e091... digest. The existing independent audit verifies all manifests, count-derived intervals, rows, budgets and policies, with zero replays.
- Decision: Curate exactly those controlled research exports as a small versioned compressed public artifact, with a separate manifest and portable verify_recovery_archive command. No human reviews or ordinary sessions enter it. Evidence-inclusive packaging verifies it; source-only omits report archives. Keep historical summary/protocol bytes and source mismatch guard unchanged. Update the ordinary lab recovery note to point to the separate measured operation, preserving its legacy status.
- Why: This repairs the actual public evidence gap using verified original records rather than fabricated identities. The independent archive verifier reports 310 valid records: conservative 16 verified/62, 0 rejected, 1,890,304 shots; point 16 verified/62, 5 rejected, 1,980,416 shots. This is identical historical evidence, not new performance evidence. The compressed selected archive is 1,057,578 bytes.
- Alternatives considered: Publish entire ignored worktrees (private/unreviewed contents); regenerate old IDs/timestamps (false provenance); leave available verified evidence inaccessible (unnecessary gap); raw uncompressed runtime directories (unnecessary size).
- Consequences: Source-only remains explicitly incomplete. Other historical families remain unavailable where not independently established. The portable verifier reuses independent raw interval reconstruction, never engine ranking/verdict functions. Preserved historical source mismatch is expected. Schema guards require adversarial replay fixtures to use their correct schema 2/3 so the tests continue exercising invalid replay rather than stopping at unrelated version rejection; no rejection assertions were weakened.
- Files: benchmarks/historical-recovery-v1/manifest.json, benchmarks/historical-recovery-v1/reports.jsonl.gz, scripts/verify_recovery_archive.py, tests/test_recovery_archive.py, scripts/package_submission.py, qfault/lab.py, tests/test_final_api_adversarial.py, docs/evidence-availability.md, docs/handoff-history-20261016.md, decisions.md, flow.md, handoff.md

### D-057: Version current-source replication and demonstrate the native measured workflow
- Date / phase / commit: 2026-10-22, current release verification, uncommitted
- Context: Current input/provenance/schema changes intentionally invalidate old source-pinned protocols. The old source guard must remain intact; a practical demonstration must use a custom/imported circuit and honest negative outcomes.
- Decision: Add a separately frozen current-release replication protocol/runner using the prior outcome-independent 72-case subset. It compares complete scientific projections, permitting only the exact enumerated ordinary-lab explanatory-note change. Label reused designs/seeds as deterministic replication, never untouched holdout/new performance evidence. Add a native H(0),Z(0) API/Aer demo with independent analytic Z/IX contracts and noise/budget controls. Replace the root flow with complete current subsystem records while preserving its earlier text separately.
- Why: The actual native demo at seed 7241 produced all five prescribed outcomes: inadequate Z confirmed only its scoped distribution; IX detected discrepancy; bounded recovery freshly verified; readout control abstained; reserve shortage returned insufficient budget without measurements. The new complete suite passed 479 tests. No old protocol/summary was rewritten or retuned.
- Alternatives considered: Disable old guards (invalid provenance); call observed cases untouched (false claim); use a hardcoded live demo response (not execution); leave the runtime flow mixed with retired symbols (misleading documentation).
- Consequences: Freeze and commit sources/protocol before current replication. Source digest rule explicitly replaces CRLF byte pairs with LF and otherwise preserves bytes, separate from historical byte digests. More shots/different seeds do not create new circuit families. Publication still depends on remaining gates. Documentation and demo script are not proof a narrated video exists.
- Files: scripts/current_release_evaluation.py, configs/current-release-replication-v1.json, scripts/judging_demo.py, docs/native-import.md, docs/judging-guide.md, docs/flow-history-20261022.md, README.md, decisions.md, flow.md, handoff.md

### D-058: Retain a negative dense-target development result and close reviewed archive corruption handling
- Date / phase / commit: 2026-10-23, independent verification, uncommitted
- Context: Dense targets remain a concrete limitation; a target-only allocation improvement needs development evidence before adoption. Independent code review found no Critical/Important issue, but reproduced one decompression-error handling defect in package verification.
- Decision: Compare fixed uniform full-group measurement with bounded coefficient-weighted allocation on the existing two-qubit development rotation-entangler design only. Minimize the L1 uncertainty proxy using N_g proportional to w_g^(2/3), with integer budgets/per-job caps. Record all 16 executed cases/raw counts. Do not adopt a production policy: both confirm 4/8, all 16 intervals cover oracle fidelity. Catch zlib.error in package verification after reproducing the exact malformed deflate case in a regression.
- Why: The allocation test failed before implementation and passes against an analytic optimum. Matched-shot/group experiments show a proxy improvement does not establish greater verified yield; repeated seeds are not architectures. Reviewer corruption reproduction was independently reproduced: invalid compressed block plus matching outer checksum raised zlib.error rather than returning invalid.
- Alternatives considered: Tune on holdout or adopt from proxy score alone (invalid evidence); present one small development family as generalization (unsupported); ignore a verifier crash because the outer checksum usually detects corruption (fails corruption contract).
- Consequences: Existing methods remain production baselines. The study is explicitly development, ideal measurement, one architecture, no superiority claim. Package corruption returns invalid without extraction. Current source-pinned protocol is unaffected because only separate study/package scripts changed.
- Files: scripts/dense_target_study.py, tests/test_witness_allocation.py, benchmarks/dense-target-development-v1.json, scripts/package_submission.py, tests/test_release_package.py, decisions.md, flow.md, handoff.md
- Symptom: verify_package raises zlib.error: Error -3 while decompressing data: invalid block type for a malformed deflated ZIP with matching unsigned outer checksum.
- Root cause: Its exception boundary omitted zlib.error raised by zipfile.testzip decompression.
- Regression test: tests/test_release_package.py::test_package_verifier_returns_invalid_for_rehashed_broken_deflate (observed red before fix).

### D-059: Clarify fresh-user safety and extend the primary-source task comparison
- Date / phase / commit: 2026-10-23, release documentation, uncommitted
- Context: The owner requires secrets/private research excluded and related tools compared by actual task rather than unmatched performance numbers. This local workbench needs no provider key/database.
- Decision: Add explicit environment/key/database/private-research ignore patterns without deleting files; state no external key/service requirement. Extend the qualitative comparison with current primary Qiskit Experiments and Mitiq documentation/license links, checked on this date, without installing/copying either. Keep original pinned comparison records unchanged below the new dated section.
- Why: Qiskit Experiments documents characterization/tomography/readout mitigation; Mitiq documents expectation-value mitigation. These overlap with measurement workflows but are different tasks from QFault's finite-contract edit selection/confirmation. Current license texts were read directly, rather than inferred from memory.
- Alternatives considered: Add unused provider configuration (misleading); publish private runtime state to ease setup (forbidden); rank different tasks using published success numbers (unfair).
- Consequences: Ignore patterns do not remove already tracked material; explicit tracked/staged/history scans remain required. No dependency, cloud infrastructure or competition action is introduced. Future upstream changes need a new dated source check.
- Files: .gitignore, README.md, docs/competitor-comparison.md, decisions.md, flow.md, handoff.md

### D-060: Bound standalone report input and preserve superseded unexecuted protocol drafts
- Date / phase / commit: 2026-10-23, final input/resource check, uncommitted
- Context: CLI verify-report reads an entire arbitrary file before parsing. A 16-MiB-plus regression confirms the oversized input reaches JSON parsing instead of an explicit limit. The current-source protocol had been frozen but not executed/committed.
- Decision: Read at most 16 MiB plus one byte and reject oversized reports before parsing/verification. Preserve protocol drafts v1/v2 rather than overwrite them; freeze v3 against final sources and use the filename stem as its unique protocol ID. Expose --protocol so each preserved version retains its own source guard.
- Why: The oversized report test failed with an end-of-file JSON parser error before the bound and passes with the explicit limit afterward. v1 predates this source change; v2 exposed a hardcoded protocol-name oversight before any execution. Neither is performance evidence. A new version avoids rewriting a frozen source record.
- Alternatives considered: Ignore local-file resource limits (contradicts the requested contract); overwrite old fingerprints (forbidden); claim a failed precommit invocation was an evaluated run (false).
- Consequences: Default supported current replication is v3; v1/v2 are superseded unexecuted drafts. Scientific algorithms/thresholds remain unchanged. Report export integrity and gate statuses are unaffected by the new upper bound.
- Files: qfault/cli.py, tests/test_report_size_limit.py, scripts/current_release_evaluation.py, configs/current-release-replication-v1.json, configs/current-release-replication-v2.json, configs/current-release-replication-v3.json, docs/dense-target-development.md, decisions.md, flow.md, handoff.md
- Symptom: Oversized report is fully read and parsed rather than rejected with a resource-limit error.
- Root cause: verify-report uses Path.read_bytes without a bound.
- Regression test: tests/test_report_size_limit.py (red before fix, then nine relevant CLI/export tests passed).

### D-061: Correct measured-evidence contrast on the light workbench
- Date / phase / commit: 2026-10-23, visual verification, uncommitted
- Context: Actual mobile overview screenshot shows the newly reused research component inherits landing colors intended for a dark background; numeric metrics/captions are too pale against white.
- Decision: Scope dark text and readable caption sizing to the research component inside .overview, leaving landing/hero/transition styles unchanged.
- Why: The real browser capture artifacts/contract-release/browser-cinematic/workbench-390.png was opened and shows the defect. Reuse of global research-metrics styles, rather than backend data, causes the contrast issue.
- Alternatives considered: Change the approved global palette/hero (unnecessary); leave a verified accessibility defect (unacceptable).
- Consequences: Only light-workbench evidence styling changes. Rebuild and actual browser/contrast inspection required before completion.
- Files: web/src/components/ResearchEvidence.css, web/src/components/ResearchEvidence.tsx, decisions.md, flow.md, handoff.md
- Symptom: Research figures/captions are faint on the white overview panel.
- Root cause: Landing research-metrics CSS is reused on a light surface without scoped color overrides.
- Regression test: Actual overview desktop/mobile browser capture and computed contrast verification; no trivial implementation-mirroring unit test.

### D-062: Verify native import in the real browser and record scoped contrast evidence
- Date / phase / commit: 2026-10-23, final browser verification, uncommitted
- Context: Native conversion works in Python/API, but the owner requires the real editor/recovery/download path and visual accessibility evidence, not an inferred browser pass.
- Decision: Add native_demo_e2e using the actual declared native fixture, existing JSON editor, feasibility route, Aer investigation/recovery and real downloaded export. Check retained provenance, desktop/mobile layout and computed contrast of the corrected light-surface research metrics/captions. Retain screenshots locally and inspect them.
- Why: The actual run passed: phase discrepancy and verified recovery, source provenance retained, export independently valid, 390/375/360 widths without overflow, no page errors. Minimum tested metric/caption contrast against the actual white panel is 8.076:1. Both corrected overview and recovery mobile captures were opened.
- Alternatives considered: API-only inference or mocked browser results (insufficient); broad interface redesign (not requested).
- Consequences: This is Windows Chromium/Aer evidence for the actual tested source, not all browsers/platforms or every text element. No narrated video claim follows. Existing ten suites also passed before the isolated contrast change.
- Files: scripts/native_demo_e2e.py, docs/implementation-ledger.md, decisions.md, flow.md, handoff.md

### D-063: Apply explicit schema support to blind exports and classify source-fingerprint scan matches
- Date / phase / commit: 2026-10-23, final evidence boundary, uncommitted
- Context: Final schema inspection finds the blind-export verifier dispatch still accepts top-level schema 999. The new real challenge regression reproduces acceptance. Final scanner matches api.py source fingerprints in three unexecuted replication protocol drafts, not credentials.
- Decision: Require integer challenge export schema 1 before chain verification. Preserve draft v3 and freeze final current-source v4 after this guard; all earlier drafts remain unexecuted. Add a narrow Gitleaks exception only for api.py's 64-hex fingerprint in these four explicitly named source protocol versions, in addition to the previous frozen-study exception.
- Why: Unsupported schemas cannot be silently interpreted even when hash membership is valid. The scanner's redacted matches identify api.py keys in source_sha256_normalized_lf; those values are computed source hashes, not provider material.
- Alternatives considered: Accept unknown blind versions (inconsistent with ordinary report rules); broadly ignore config files or generic keys (unsafe); overwrite v3 source fingerprint (forbidden).
- Consequences: No known valid blind export changes. New versions need explicit support. Current supported replication path is v4; v1–v3 are documented unexecuted drafts. No secrets were removed/replaced and no rotation need was established.
- Files: qfault/storage.py, tests/test_artifact_versions.py, scripts/current_release_evaluation.py, configs/current-release-replication-v4.json, .gitleaks.toml, decisions.md, flow.md, handoff.md
- Symptom: A valid blind export with schema_version changed to 999 still verifies true.
- Root cause: Special blind-export dispatch checks chain format/digests but omitted top-level version support.
- Regression test: tests/test_artifact_versions.py::test_unknown_blind_export_version_is_not_silently_reinterpreted (failed before guard).

### D-064: Retain and independently verify current-source replication evidence
- Date / phase / commit: 2026-10-23, release evidence, uncommitted
- Context: D-048–D-063 was committed as 97710d834abeef93f0094b169a05d182f22c8434 with exact owner author and committer. Its frozen v4 replication has executed once; records need portable verification and deliberate publication selection.
- Decision: Retain exactly the 72 generated public-safe exports and original summary in benchmarks/current-release-replication-v4. Add scripts.verify_replication.verify to bind protocol, request/projection identities, membership, counts, costs and verdicts, with independent recovery interval reconstruction. Require this check in evidence-inclusive packaging. Update current release records and historical-document navigation.
- Why: The run matched 72/72 prescribed projections with zero errors, 2,272,256 shots and 1,127 executions. Archive SHA-256 is c648f4c16347306cfd6f3b79e8597681a651deb20d6e20977684990254df2b05. The verifier passes genuine records and rejects edited shot totals. Full assembled suite passes 485 tests; fresh clone and extracted archive each pass their 484-test committed suite.
- Alternatives considered: Leave current records only in ignored storage (not publicly reproducible); call replication an untouched holdout (invalid); change frozen engine sources after execution (invalidates this protocol).
- Consequences: Verification is unsigned consistency/recount, not authentication. Source-only packages omit raw report archives. Historical bytes/protocols remain unchanged. This follows implementation 97710d8 without a self-reference loop; Git history identifies this follow-up whose own hash is unknown at write time.
- Files: scripts/verify_replication.py, scripts/package_submission.py, tests/test_replication_verifier.py, benchmarks/current-release-replication-v4/summary.json, benchmarks/current-release-replication-v4/reports.jsonl.gz, .gitleaks.toml, docs/evidence-availability.md, docs/current-state.md, docs/final-verification.md, docs/release-verification-20261023.md, docs/implementation-ledger.md, README.md, decisions.md, flow.md, handoff.md
- Scanner scope: The retained summary repeats the frozen api.py source fingerprint. A path-and-match constrained exception classifies that exact 64-hex provenance field, without ignoring the file or credential rules. The initial final history invocation hit Git ownership protection and scanned zero commits; rerun with a command-local safe.directory exception is required and its actual scope is recorded separately.
- Failed approach: Piping the staged diff to scanner stdin discards path identity and triggers the known source-fingerprint pattern. Use Gitleaks git --pre-commit --staged to retain paths and apply the narrow rule; do not broaden a global value exception.

### D-065: Describe the exact package evidence scope and record extraction checks
- Date / phase / commit: 2026-10-23, release packaging, uncommitted
- Context: D-064 is committed as 6998e5959180af6c7224b95cb468fa8dd8ea7503. Its two packages verify and extract, but the manifest description still says current external only after historical recovery and current replication were added to the explicit evidence map.
- Decision: Describe completeness as applying to the explicitly listed available studies, excluding other historical families. Record actual clean-source packaging and extraction checks, retaining previous package outputs unchanged.
- Why: Full manifest lists verified external 2,206 exports, historical recovery 310 and current replication 72. Independent extraction verifies both retained archives; source-only Aer works and missing raw evidence correctly returns unavailable. The stale prose should not contradict that explicit map.
- Alternatives considered: Leave misleading scope prose (rejected); imply all historical evidence is complete (false).
- Consequences: No schema, algorithms, evidence bytes or frozen source digests change. The two packages must be built again for this commit; expensive scientific replication is not repeated for a manifest label.
- Files: scripts/package_submission.py, docs/release-verification-20261023.md, decisions.md, flow.md, handoff.md
- Symptom: Package evidence_scope says current external holdout only while the evidence map names three verified archives.
- Root cause: Original narrow description was not updated when archive preflights were extended.
- Regression test: Existing tests/test_release_package.py suite plus actual full/source package manifest inspection; no implementation-mirroring text assertion.

### D-066: Bind the retained summary source fingerprints to the frozen protocol
- Date / phase / commit: 2026-10-23, final independent verification, uncommitted
- Context: D-065 committed as 4cc58de3aff12f27ed1f6dc131507551acf1bc7a. Final adversarial inspection tests whether the offline replication verifier rejects an edited source fingerprint even when raw measurements are unchanged.
- Decision: Require the summary's normalized source fingerprint map to equal the frozen protocol map before accepting exports. Preserve all measured records and frozen engine sources.
- Why: New test changes only qfault/api.py's recorded source hash and initially fails because verify returns valid=true. After explicit comparison, that inconsistent source claim is rejected. The protocol byte digest was already checked, but its source map was not bound to the duplicate summary field.
- Alternatives considered: Treat all summary provenance as unverified metadata (contradicts advertised source bindings); change original summary/protocol (unnecessary and forbidden).
- Consequences: Unsigned commit names still do not prove author identity or authenticity; this closes an internal source-fingerprint inconsistency. No scientific rerun is required because only the independent offline verifier changes.
- Files: scripts/verify_replication.py, tests/test_replication_verifier.py, decisions.md, flow.md, handoff.md, docs/release-verification-20261023.md
- Symptom: An altered summary source hash was accepted despite disagreement with the checked frozen protocol.
- Root cause: The verifier bound the protocol byte digest and scientific projections but omitted equality of the duplicated source fingerprint map.
- Regression test: tests/test_replication_verifier.py::test_replication_source_fingerprints_are_bound_to_frozen_protocol, failed before fix.

### D-067: Require literal integer versions in new offline artifact formats
- Date / phase / commit: 2026-10-23, release input boundary, uncommitted
- Context: D-066 committed as 285939f0b170d953d54600955393d3c90f6558c0. Final malformed-version review of the newly added package/replication verifiers finds Python equality treats JSON true and 1.0 as version 1.
- Decision: Require actual integer schema_version 1 in both new offline formats; reject booleans, floating values and strings. Preserve valid archives and frozen scientific sources.
- Why: Both new malformed-schema regressions failed with valid=true before the type guard. Integer version dispatch must match the existing strict investigation-version boundary.
- Alternatives considered: Accept coercible versions (ambiguous format dispatch); revise version 1 or recorded evidence (unnecessary).
- Consequences: Only malformed new artifact inputs are rejected; no valid result, protocol or source digest changes. Rebuild source packages after this focused verifier fix.
- Files: scripts/package_submission.py, scripts/verify_replication.py, tests/test_release_package.py, tests/test_replication_verifier.py, decisions.md, flow.md, handoff.md, docs/release-verification-20261023.md
- Symptom: JSON schema_version true or 1.0 is accepted as integer version 1.
- Root cause: Numeric equality alone is insufficient because Python bool subclasses int and 1.0 equals 1.
- Regression test: tests/test_release_package.py::test_package_schema_is_an_integer_not_a_coercible_value; tests/test_replication_verifier.py::test_replication_schema_is_an_integer_not_a_coercible_value; both failed before guards.

### D-068: Publish the verified source and record reproducible release evidence
- Date / phase / commit: 2026-10-23, publication, uncommitted
- Context: D-067 is committed as 66db0167fd46ea262bbb22282038fac331707330. All local gates pass for the documented bounded simulator scope. The owner explicitly authorizes publication after those checks.
- Decision: Fast-forward existing main without rewriting history, push to the preserved PrathamKapoor/QFault origin, fetch and compare server-side SHA, clone from GitHub and verify all advertised available evidence. Record exact code/protocol/package/CI identities in this ordinary documentation follow-up. Verify this follow-up's own SHA and CI after pushing; Git history is authoritative for its self-reference.
- Why: Remote main and local HEAD both equal 66db0167fd46ea262bbb22282038fac331707330, ahead/behind 0/0. Fresh GitHub clone verifies 2,206 external, 310 historical recovery and 72 current replication reports. Hosted workflow 39837203909 reports completed/success for that exact SHA. Windows full suite passes 488 tests; independent final extraction passes 9 package/evidence tests and source-only extraction passes 6 package tests plus Aer.
- Alternatives considered: Force push/history rewrite or duplicate repository (unnecessary and unauthorized); stop after local tests (does not satisfy release contract); represent unavailable historical evidence as complete (false).
- Consequences: No scientific changes or rerun. Exact final documentation SHA/CI must be checked after publication. Archived historical limitations, source-only omissions and unsigned consistency limits remain explicit. No competition action, message or hardware job occurs.
- Files: decisions.md, flow.md, handoff.md, docs/implementation-ledger.md, docs/current-state.md, docs/release-verification-20261023.md

### D-069: Guide judges through the existing external-circuit workflow
- Date / phase / commit: 2026-10-23, judge-facing experience, uncommitted
- Context: The current clean repository is 9866fdb9ed7f22079f6e96bca18d55f0c7d9e173; its exact-SHA CI succeeds, but GitHub has no releases or downloadable assets. Existing external QRNG and native scripts work, while judges must assemble inputs in the laboratory editor. The owner explicitly requests sequential implementation and public delivery.
- Decision: Work on feat/guided-demo-release without changing existing refs/history. Reuse the pinned external QRNG source, independent reference contracts, native QASM provenance, existing lab/recovery routes and existing candidate generator. Add a validated input catalog and guided /demo page, honest negative demonstrations, session-scoped returned-ID restoration and public package/media delivery. Keep screening/freeze/fresh confirmation one real engine operation, explained as such. Follow docs/judge-delivery-plan.md sequentially.
- Why: Actual baseline checks pass 18 targeted tests and Aer smoke; origin sync is 0/0; remote release/tag lists are empty. The engine already supplies all scientific decisions and returned counts; a second engine or pretend interactive confirmation would undermine the boundary. The skill approval ceremony is not used to ask permission again: the owner's explicit instruction already authorizes implementation and validated publication.
- Alternatives considered: Editor-only instructions (not immediately usable); parallel demonstration engine (divergent science); new resumable recovery protocol (unnecessary scientific/storage change); redesign hero (not authorized by evidence).
- Consequences: Frozen protocols/results/raw evidence remain unchanged. Adding presentation routes changes current source identity but does not authorize relabelling the old source-pinned replication; do not rerun it. Existing local runtime artifacts and recovery worktree stay private/preserved. First formal release v0.1.0 is proposed, not yet created.
- Files: docs/judge-delivery-plan.md, decisions.md, flow.md, handoff.md; implementation paths will be enumerated in the decision accompanying their changes.

### D-070: Expose validated external demonstration inputs without a second engine
- Date / phase / commit: 2026-10-23, guided input contract, uncommitted
- Context: Two new catalog/request integration regressions fail with HTTP404. Judges need the original external source, reference identity, controlled candidate, independent contracts and executable negative controls without assembling JSON.
- Decision: Add examples/qrng-phase-demo.json, built by scripts.guided_demo.build_inputs using external_demo.example and from_qasm2. GET /api/guided-demo calls demo_catalog to check source bytes, circuit identities and request schemas, then returns unmeasured structural candidates from the existing generator. scripts.guided_demo.run is a real-engine text fallback using the same catalog, validation, ordinary execution routes and standalone export verifier.
- Why: The fixture uses the unchanged pinned four-H QRNG source; terminal Z is declared separately. The imported original identity and source representation survive candidate reports. Independent reference behavior is derived from the trusted original source before mutation, not from the candidate. Candidate preview is explicitly not measured/ranked/frozen evidence.
- Alternatives considered: Hardcoded successful responses (false live evidence); importing evaluation scripts into the runtime API (unnecessary coupling); changing the scientific recovery state machine (outside presentation scope).
- Consequences: Feasibility previews cover measurable contract claims using existing LabRequest limits; recovery reserve/admission remains enforced by recover, never guaranteed by the preview. Existing frozen source guards remain intact and current API identity changes are not called a new untouched study. No measurement occurs on catalog GET. Runtime failures return safe503, not substituted examples.
- Files: examples/qrng-phase-demo.json, scripts/guided_demo.py, qfault/demo.py, qfault/api.py, tests/test_guided_demo.py, decisions.md, flow.md, handoff.md
- Regression test: tests/test_guided_demo.py; both tests failed404 before implementation; final actual results recorded after execution.
- Verification: Both real catalog/Aer request tests passed13.48s. Additional corrupt-null/list tests reproduced AttributeError before the object-shape guard; all five guided tests passed13.31s afterward. No scientific engine source or frozen input was altered.

### D-071: Add an accessible guided page with legal stages and preserved identities
- Date / phase / commit: 2026-10-23, guided interface, uncommitted
- Context: The real pre-implementation browser test fails because no Guided demo entry exists. Four state regressions fail because stage/admission/session controls are absent. The catalog already executes all five real Aer outcomes correctly.
- Decision: Add GuidedDemo and scoped styles, a presentation-only session controller, synchronous execution gate and API error wrapper. Link /demo from landing navigation, workbench overview and sidebar without changing the hero/helix. Preserve the guide component across workspace navigation. Store only returned IDs and presentation state, never stored successful responses. Refresh restores server records; interrupted completion is unknown and never automatically retried. Expose genuine source/reference, incomplete/phase-sensitive contracts, edit preview, actual recovery selection/intervals/fresh costs, integrity/export and explicit replay/new-seed rerun.
- Why: All four controller tests pass after observed red failures. TypeScript and production build pass. Existing engine routes validate and execute; a duplicate UI gesture cannot submit duplicate work. Screening/freeze/fresh confirmation remain one synchronous operation, with actual elapsed time and no invented per-job percentage or cancellation.
- Alternatives considered: Automatically replay after refresh (can duplicate work); persist response-shaped success fixtures (could misrepresent live evidence); unmount an active guide on navigation (loses observable completion); change hero composition (unnecessary).
- Consequences: Session storage is local/tab-scoped; server artifacts remain authoritative. Connection loss after submission leaves completion unknown and requires explicit history inspection before a new guide. A new guide never overwrites prior server records. Browser verification and media are still pending, not inferred from build.
- Files: web/src/components/GuidedDemo.tsx, web/src/components/GuidedDemo.css, web/src/guided/session.ts, web/src/guided/api.ts, web/src/main.tsx, web/src/components/Overview.tsx, web/src/components/landing/Landing.tsx, tests/guided-session.test.mjs, scripts/guided_demo_e2e.py, decisions.md, flow.md, handoff.md

### D-072: Correct mobile guide entry and inspect the real keyboard/error journey
- Date / phase / commit: 2026-10-23, guided accessibility, uncommitted
- Context: The actual guided journey passes phase/recovery/export/refresh/replay and both negative controls, but mobile accessibility regression cannot find Guided demo. The existing mobile navigation rule hides every new button except nav-enter; an initial override loses on specificity. A real mobile capture also shows the aside inheriting a two-column definition-list layout that crushes its descriptions.
- Decision: Give the new navigation control a specific mobile selector and keep it visible; retain the original hero’s workbench action. Explicitly label scenario buttons with short accessible names and described-by explanations, focus the current stage on transitions, restore readable stacked aside definitions and disclose long proposal tables on demand. Add real keyboard/reduced-motion checks at1440/390/375/360 and explicit error-only409/connection-abort injections with a genuine Aer retry.
- Why: Mobile entry failed before correction. The corrected accessibility suite passes at all four widths; keyboard stage transition/focus ring and unknown completion after refresh are exercised. The main actual Aer suite passes with verified downloaded report, distinct parent-linked replay and18POSTs. Error injection is labelled and never supplies successful quantum responses.
- Alternatives considered: Redesign hero (unnecessary); claim build proves accessibility (false); hide alternate candidates (would lose uncertainty; retain complete tables under keyboard-accessible details).
- Consequences: Captures remain genuine local evidence. A rejected command-review restart was not bypassed: leave the old test process untouched and use a separately verified-free port/artifact root for refreshed backend checks. No distributed-concurrency claim follows from independent test instances.
- Files: web/src/components/GuidedDemo.tsx, web/src/components/GuidedDemo.css, web/src/components/Overview.tsx, web/src/components/landing/Landing.tsx, web/src/components/landing/landing.css, scripts/guided_accessibility_e2e.py, scripts/guided_demo_e2e.py, decisions.md, flow.md, handoff.md
- Symptom: Guided demo is absent from the mobile accessibility tree; aside values wrap word by word.
- Root cause: .landing-nav nav>button:not(.nav-enter) outranks the first new selector; inherited definition-list grid does not match the guide’s stacked aside design.
- Regression test: scripts.guided_accessibility_e2e mobile entry failed before fix; final four-width keyboard/error suite passed. Actual captures inspected before further layout refinement.
- Retained-interface verification: Actual existing release smoke, cinematic hero/transition seven-width suite and workspace navigation suite pass on the stable assembled build. One earlier cinematic viewport reload did not attach WebGL; cause was not established, no hero code/tolerance was changed, and the full stable-build rerun passed.

### D-073: Derive the judge-safe shot comparison from the recorded summary
- Date / phase / commit: 2026-10-23, research presentation, uncommitted
- Context: Existing reporting has both total shot counts but no explicit relative reduction, and only the first card shows its eligible denominator. User requires equal-yield interpretation, both denominators and approximately9.6% fewer conservative shots.
- Decision: Extend /api/research with equal_verified_yield and relative_shot_reduction computed from the same frozen summary; display both overall/eligible denominators, exact shot totals, formatted reduction and correlated-simulation/no-population-superiority limits in ResearchEvidence.
- Why: The new comparison regression fails on absent comparison before implementation. All seven guided/research tests pass12.39s after the change. Independent external-results verifier freshly checks2,206 exports and2,232 rows without rerunning the frozen study. Recorded totals give565,248/5,902,336 reduction, rounded9.6%.
- Alternatives considered: Copy a9.6% constant into pages (drift); present conditional10/41 alone or replication72/72 as repair accuracy (misleading); new policy/evaluation (unnecessary).
- Consequences: This is descriptive reporting under the existing matched ceilings, not a population or algorithmic-superiority claim. No summary/protocol/raw bytes change.
- Files: qfault/api.py, web/src/components/ResearchEvidence.tsx, tests/test_research_summary.py, decisions.md, flow.md, handoff.md
- Regression test: tests/test_research_summary.py::test_recovery_comparison_keeps_both_denominators_and_uses_recorded_shot_totals, observed missing-field failure then pass.

### D-074: Refresh history after guided execution and restore valid records independently
- Date / phase / commit: 2026-10-23, guided persistence, uncommitted
- Context: A strengthened real browser test before refresh cannot find the just-created recovery in Experiment History. A separate refresh regression with one genuine Z record and one missing phase record loses both visible results and re-enables Z execution.
- Decision: Refresh the existing history list when entering history/overview. Restore saved guide records with allSettled and per-record ID checks, retaining available results while explaining missing ones. A known saved ID cannot be silently overwritten by rerunning its stage; starting a new guide remains explicit.
- Why: Both failures were observed against actual server records before correction. History was fetched only at initial mount; Promise.all discarded valid restored results when any other request failed. These are interface/persistence defects, not scientific engine failures.
- Alternatives considered: Force a page refresh after every run (disruptive); erase missing IDs and rerun automatically (duplicates work and changes evidence); silently hide all restored records (misleading).
- Consequences: Missing/corrupt records remain visible as errors and are never fabricated. Available records remain independently inspectable. Existing immutable server storage and scientific requests are unchanged.
- Files: web/src/main.tsx, web/src/components/GuidedDemo.tsx, scripts/guided_demo_e2e.py, scripts/guided_accessibility_e2e.py, decisions.md, flow.md, handoff.md
- Symptom: Fresh guided investigation absent from history until refresh; a missing sibling hides a valid saved Z result and permits duplicate submission.
- Root cause: History state is loaded only on initial mount; aggregate restoration rejects on the first unavailable record, and admission checked only restored response state rather than known IDs.
- Regression test: scripts.guided_demo_e2e history assertion before reload; scripts.guided_accessibility_e2e partial restore with real Z record and actual404 sibling; both failed before fixes.
- Verification: Both complete browser reruns passed after correction: main recovery858100979dcd45a385840f45db0a749b with distinct replay452431312a284ac68145a5ba80b5f4bc, independently verified download,18POSTs, no page errors; keyboard/mobile/error/partial-restore suite also passed with actual Aer Z record163b5ea0879a4411a8d71d947661a27c. Artifacts: browser-guided-history-fixed and browser-accessibility-restore-fixed under artifacts/judge-delivery.

### D-075: Prepare a source-bound silent demonstration and complete narration
- Date / phase / commit: 2026-10-23, demonstration delivery, uncommitted
- Context: Guided workflow D-069–D-074 is committed as db2989b45f48183fdce7ca2980717b8f009758ea with exact owner author and committer. The real journey works, but no new guided recording or public delivery exists. Owner explicitly permits accurately labelled silent footage with full narration script.
- Decision: Rewrite the current judging guide around the external guided page and real-engine fallback; add a concrete three-minute narration table and record_guided_demo tooling. Recording requires clean committed source and only actual browser/API/Aer operations, retaining checked reports and ordered source-bound milestones. Verify full normal-speed playback, inspect decoded frames and generate captions from actual milestone times. Prepare remaining release tooling before the clean source snapshot, then capture against that exact snapshot.
- Why: Two caption boundary regressions failed before implementation and now pass, including milliseconds/hour rollover, nonfinite/negative and reversed/outside intervals. The recorder reuses the verified live sequence and independently checks downloaded exports/fresh execution membership rather than embedding a success response. No voiceover is claimed.
- Alternatives considered: Synthetic dashboard/video or stored success response (false evidence); call silent capture narrated (false); record against an unidentified dirty tree (not source-bound).
- Consequences: Actual capture/playback/readability remain separate gates pending execution. Three-minute cues are pacing targets, not runtime promises. Only controlled demonstration outputs may enter public assets; ordinary runtime directories remain excluded. Package manifests must identify their actual snapshot, not a later documentation commit.
- Files: docs/judging-guide.md, docs/three-minute-demo.md, scripts/record_guided_demo.py, tests/test_demo_media.py, decisions.md, flow.md, handoff.md
- Regression test: tests/test_demo_media.py, two red missing-feature assertions then2passed0.23s. Full recording/playback not yet run at this write.

### D-076: Deliver bounded public downloads and verify publication from downloaded bytes
- Date / phase / commit: 2026-10-23, public release delivery, uncommitted
- Context: Existing packages and final gate records are local; public GitHub has no release. Owner requests directly obtainable source/evidence packages, checksums, verified silent media and independent download proof. Existing connector has no release upload capability; configured Git authentication was verified read-only as PrathamKapoor.
- Decision: Add release_delivery for self-contained outer ZIPs preserving the existing exact-source manifest/inner ZIP, with bounded verify-before-extract and exclusive destinations. Add prepare_release_assets to select only source-bound controlled reports/media/guides, reuse independently installed package bytes and derive research fields from frozen summaries. Add public_release using the official GitHub release/asset API and existing credential helper, with owner/source/CI/unused-version preflight, draft uploads, explicit allowlist and public redownload/hash/package/tag verification. Extend existing CI with Node stage tests and actual guided browser suites. No dependencies change.
- Why: Seven outer-package regressions, eight checksum/public-selection regressions and two source/media selection regressions failed before their features. Together with caption checks,19targeted tests passed9.52s. Traversal/corruption/false-valid/missing members and existing destinations fail without a reviewed project or overwrite. Source-only remains explicitly incomplete. A valid playback flag cannot override changed media bytes or another source identity.
- Alternatives considered: Install a new GitHub CLI dependency (unnecessary; existing authenticated Git helper works); upload a directory wholesale (privacy risk); publish upload success without redownload (not proof); rebuild tested inner packages invisibly (instead support exact-byte reuse); modify frozen scientific records (forbidden).
- Consequences: Publication occurs only after final local/CI/package/media gates. Existing releases/tags are never overwritten; interrupted drafts remain inspectable. OAuth values stay only in process memory, never logs/artifacts. Public HTTPS downloads have size/time/redirect bounds and distinct new destinations. Unsigned checksums establish consistency, not authenticity. Later documentation commit may differ from package/tag source and must be labelled exactly.
- Files: scripts/release_delivery.py, scripts/prepare_release_assets.py, scripts/public_release.py, tests/test_release_delivery.py, tests/test_public_release.py, tests/test_demo_asset_selection.py, tests/test_research_summary.py, .github/workflows/checks.yml, README.md, docs/public-release.md, decisions.md, flow.md, handoff.md
- Regression test: tests/test_release_delivery.py; tests/test_public_release.py; tests/test_demo_asset_selection.py; source/eligible/shot documentation consistency test. Full final assembled checks and real remote publication remain pending.
- API reference: https://docs.github.com/en/rest/releases/releases and https://docs.github.com/en/rest/releases/assets checked during implementation; existing API2022-11-28 contract and response digest fields retained.

### D-077: Decode the exact recording bytes through a seekable browser Blob
- Date / phase / commit: 2026-10-23, media verification, uncommitted
- Context: D-075/D-076 is committed as 777f5de157415075fe031f8f045b6c950d6dad3a. Its assembled suite passed514tests77.31s. Actual recording completed all five expected live outcomes, but frame seeking timed out in playback verification.
- Decision: Load the already size/hash-checked local WebM bytes into a browser Blob URL before seeking and full normal-speed playback. Keep duration, decoding, frame, silence and playback assertions. Recreate recording/packages from corrected committed source.
- Why: An isolated actual-browser probe of identical15577963bytes found HTTP-route duration180.04seconds but seekable[0,0] and currentTime stayed0 after setting10. A Blob exposed seekable[0,180.04] and currentTime10. The fulfilled route did not implement range responses. No scientific or UI outcome failed.
- Alternatives considered: Implement HTTP Range responses (unneeded for local-byte verification); remove frame checks or call the recording verified (would conceal failure).
- Consequences: Base64/Blob briefly duplicates bounded media in browser memory; existing128MiB limit remains. Old failed verification stays local, never published as success.
- Files: scripts/record_guided_demo.py, decisions.md, flow.md, handoff.md
- Symptom: Page.wait_for_function: Timeout30000ms exceeded while seeking the first decoded frame.
- Root cause: Synthetic fulfilled HTTP media response has a zero-length seekable range despite a known duration; identical bytes are seekable as a Blob.
- Regression test: Actual browser probe and full scripts.record_guided_demo playback on recorded bytes; no fake media fixture or weakened assertion. Existing caption unit tests retained.

### D-078: Publish the verified judge-facing release and preserve its exact source boundary
- Date / phase / commit: 2026-10-23, public delivery verification, uncommitted
- Context: D-069–D-074 are committed as db2989b45f48183fdce7ca2980717b8f009758ea, D-075/D-076 as777f5de157415075fe031f8f045b6c950d6dad3a and D-077 as b65dcb60fb216e802b2ff7d71a970169a6c059a2. Owner authorized publication after validation; no remote release/tag existed at startup.
- Decision: Publish a new v0.1.0 tag/release at the exact clean b65dcb60fb216e802b2ff7d71a970169a6c059a2 snapshot after its local and hosted gates; deliberately upload nine allowlisted assets. Independently download all bytes, recompute checksums, resolve the remote tag, verify/extract both packages and test their downloaded source. Add direct README links and a factual verification record in this later documentation-only commit, without moving the tag or claiming later documentation entered earlier archives.
- Why: Exact-source full suite514passed80.42s; Node4passed; independent hashed installations, frontend checks/build, Aer and22/28representative package tests passed. Actual180.12s silent recording completed normal-speed playback with4874frames, no dropped/corrupt frames/audio/error. Hosted run39931840261 checks/browser-smoke both succeeded. All nine public assets downloaded/verified; source/evidence ZIPs extracted again, frontend rebuilt and22/28tests passed on downloaded source, with all three evidence verifiers valid. Remote tag matches b65dcb60fb216e802b2ff7d71a970169a6c059a2. No frozen science, lock, engine policy or hero identity changed.
- Alternatives considered: Publish local paths/upload-response success only (not independent public proof); move the tag to the later record (invalidates source identity); include ignored runtime directories wholesale (privacy violation); repeatedly amend to embed a commit's own hash (impossible self-reference).
- Consequences: Release assets/tag remain immutable under this workflow. Source-only intentionally omits raw archives; full mode includes only three explicitly available research archives and separate five controlled demo exports. Other historical families remain unavailable/unknown. Video is silent with text narration/captions, not narrated. Current main documentation may postdate the release; Git history and exact-SHA hosted checks identify this follow-up. No mandatory delivery asset is blocked; local simulation/finite contract/ambiguous cause/unsigned-hash limits remain.
- Files: README.md, docs/judge-delivery-plan.md, docs/judge-release-verification.md, decisions.md, flow.md, handoff.md
- Verification: scripts.public_release --publish followed by unauthenticated redownload; scripts.release_delivery verify on both downloaded archives; independent extracted source imports, npm ci/check/build, representative pytest/Aer/evidence commands. Full commands, results, checksums and public links are in docs/judge-release-verification.md. Final documentation-only identity and CI are checked after commit, not fabricated inside it.

### D-079: Start the existing combined workbench for a live judging rehearsal
- Date / phase / commit: 2026-10-23, local demonstration operation, uncommitted
- Context: Owner requests running frontend/backend and a judge walkthrough. Actual checkout remains287dd4fadaacf973aa3eb926e79189f5958b3949. No listeners on8000/8001/8002/5173; frontend package exposes build/check, not a development-server script.
- Decision: Rebuild existing frontend and run documented qfault serve on loopback8000, serving frontend/API together. Use existing QFAULT_ARTIFACTS=artifacts/live-judge-investigations to separate rehearsal records. Keep ordinary server execution running; reuse existing preflight/narration rather than another demo engine/guide.
- Why: Build passed; root200/healthok, Aer0.17.2 importable. Actual browser preflight passed18POSTs, export verification, distinct replay, both negative outcomes and390/375/360 widths with no page errors. Recovery used77824shots. Automatic review rejected the combined hidden-process launch; separate build and ordinary server execution succeeded without stopping other processes.
- Alternatives considered: New frontend dev/proxy infrastructure (unneeded); owner's normal runtime store (less clear separation); retry rejected hidden launcher unchanged (not used).
- Consequences: Runtime availability/PID are ephemeral; recheck later. Rehearsal is not frozen evaluation. No application/dependency/scientific/release asset change or publication needed.
- Files: decisions.md, flow.md, handoff.md

### D-080: Adapt private report persistence and trust boundaries for owner-authorized Vercel hosting
- Date / phase / commit: 2026-10-23, hosted workbench, uncommitted
- Context: Owner explicitly requests Vercel deployment and selects full live measurements/saved reports. Verified owner login and Hobby team hex-sembly; existing trial project preserved. Vercel Functions expose temporary scratch storage, incompatible with relying on the existing local ArtifactStore between requests. This is a verified hosting requirement superseding local-only deployment scope, not a scientific policy change.
- Decision: Add an opt-in HostedApp wrapper and Vercel entrypoint around unchanged create_app. Use private Blob HTTPv12 with ETag-conditional per-session lease/snapshot writes; materialize original canonical documents in a new bounded scratch directory, then persist before responding. Sign host-only browser cookies with an environment secret, isolate history/blind state by session, validate external Host/Origin before internal loopback delegation, preserve body guard and local API. Add hashed-lock requirements.txt and deployment/upload exclusions. Keep limits explicit:32MiB/1000files/64operations/30-day cookie,4MiB response and300s platform ceiling.
- Why: Ten targeted regressions failed before hosting support. Downloaded official vercel-blob0.5.0 MIT wheel was inspected for HTTPv12 protocol; standalone SDK pulls extra httpx2/internal/OIDC packages and lacks conditional put, so stdlib transport avoids a dependency and retains existing lock. Actual private-store consistency/CAS and all workflows remain deployment gates, not assumed passes. New qfault project/store created; no paid upgrade or personal runtime upload.
- Alternatives considered: Static frontend alone (owner chose full interactivity); put artifacts only in /tmp (loses records across instances); expose local guard unchanged (rejects public Host); remove guard globally/shared global history (unsafe); external persistent paid host/database (unneeded if private Blob validates).
- Consequences: New hosted boundary requires independent security/concurrency/cold-start tests. Blob quota suspension returns unavailable, never success. Session cookie is a capability, not account login; clearing it loses access, so exports matter. Cookie expiry does not claim automatic record deletion. Leases expire after310s; no hard cancellation/resumable scientific selection claim. Original checkout/release/frozen sources remain unchanged.
- Files: qfault/hosting.py, api/index.py, vercel.json, requirements.txt, .vercelignore, .gitignore, tests/test_hosting.py, docs/vercel-hosting-plan.md, decisions.md, flow.md, handoff.md

### D-081: Require origin-consistent private reads after actual provider cache failure
- Date / phase / commit: 2026-10-23, hosting verification, uncommitted
- Context: Actual private Blob probe created/read a session but an immediate overwrite returned cached body ETag differing from fresh origin metadata. The guard correctly refused stale state; query nonce and no-cache header alone did not bypass the provider CDN.
- Decision: Use the documented private-storage cache=0 consistent-read option and retain metadata/body ETag checks and conditional writes. No stale-state fallback.
- Why: New transport regression failed before correction. Official July14,2026 changelog and storage SDK release identify cache=0. Actual provider roundtrip, immediate overwrite/read and stale-writer rejection then passed. No user report was lost or falsely verified.
- Alternatives considered: Remove ETag check (unsafe); wait60seconds between UI steps (unusable); new database/provider (unnecessary).
- Consequences: Origin reads consume Hobby transfer/operation quota and can be slower; quota failure remains explicit.
- Files: qfault/hosting.py, tests/test_hosting.py, decisions.md, flow.md, handoff.md
- Symptom: OSError: Current private snapshot not available immediately after overwrite.
- Root cause: Vercel private CDN caches overwritten paths; an arbitrary nonce does not enable origin-consistent reads.
- Regression test: test_private_reads_explicitly_bypass_provider_cdn_after_overwrite; real private-provider probe passes after fix.
- Reference: https://vercel.com/changelog/vercel-blob-now-supports-consistent-reads-on-private-storage

### D-082: Initialize one hosted browser capability before concurrent workbench requests
- Date / phase / commit: 2026-10-23, hosted privacy, uncommitted
- Context: Multiple first-page API requests without a cookie can each mint a session cookie. A delayed read response could replace the cookie that owns a newly saved investigation.
- Decision: Add stateless POST /api/hosted-session in the outer adapter and a hosted-build-only HostedSession gate. Initialize the cookie before mounting workbench request effects. GET responses never set session cookies; nonbrowser first mutations can still create one. Show hosted privacy,30-day cookie access,64-operation ceiling and explicit connection error/retry. Local builds render the original workbench immediately; hero untouched.
- Why: New read-cookie/bootstrap regression failed before change. The session is a capability, not a universal account/login system. Users must know to export before losing cookies. Existing React data access and measured evidence remain unchanged.
- Alternatives considered: Set new cookies on every API response (race); add public shared history (privacy violation); block the landing hero on simulator startup (unnecessary).
- Consequences: Hosted workbench can wait for a cold start; no fake progress or success. Full deployed browser/mobile/refresh/privacy checks remain required.
- Files: qfault/hosting.py, tests/test_hosting.py, web/src/components/HostedSession.tsx, web/src/components/HostedSession.css, web/src/App.tsx, vercel.json, decisions.md, flow.md, handoff.md
- Symptom: Initial read responses include Set-Cookie and hosted bootstrap is absent.
- Root cause: Independent anonymous requests mint unrelated capabilities before a stable browser session exists.
- Regression test: test_bootstrap_cookie_precedes_workbench_and_reads_never_replace_it observed red; hosted actual browser acceptance required after implementation.

### D-083: Pin the hosted runtime and document verified setup before deployment
- Date / phase / commit: 2026-10-23, Vercel delivery, uncommitted
- Context: Owner-authorized full hosting has passed529assembled tests99.07s, targeted real provider consistency/CAS and frontend checks/build. Deployment must exclude secrets/runtime data and retain exact source identity.
- Decision: Pin hosted Python3.13, reuse unchanged hashed requirements.lock through requirements.txt, keep .vercelignore/source exclusions and CLI-managed .vercel ignored, document private session storage/access/quotas and bootstrap flag. Add a README hosting link without changing local setup. Commit reviewed source before preview; inspect and exercise live workflows before promotion.
- Why: CLI-created broad .env* ignore was redundant and would hide a future .env.example; retain existing precise rules and only .vercel/. No new Python/JS dependency is required by the stdlib Blob HTTP adapter. No scientific core, frozen evidence or original dependency lock differs from287dd4f.
- Alternatives considered: Install the umbrella provider SDK (adds unrelated dependencies); mutate existing runtime pins/lock (unnecessary); upload local runtime/environment files (forbidden); call unit tests proof of deployed behavior (false).
- Consequences: Preview/build/runtime/browser validation remain gates; no claim of a public URL yet. Hobby limits remain explicit. Existing trial project untouched; no paid plan or release/tag overwrite.
- Files: .python-version, requirements.txt, .vercelignore, vercel.json, .gitignore, docs/vercel-hosting.md, docs/vercel-hosting-plan.md, README.md, web/src/main.tsx, decisions.md, flow.md, handoff.md

### D-084: Correct the observed Vercel import bootstrap and native dependency selection
- Date / phase / commit: 2026-10-23, deployed runtime correction, uncommitted
- Context: Hosting implementation is13c121db7e4b99bc6588203069ae17dfdec49d7a. Vercel first deployment dpl_2xMKi8zbtUYjBVFPk6Xd1m4naNJw built successfully but runtime logs show OSError:[Errno30]Read-only file system:artifacts during qfault.api module import. Build logs show root pyproject.toml selected instead of requirements.txt; Aer is optional there. CLI automatically assigned first deployment to production; no readiness claim was made.
- Decision: Before legacy API import, create its unused bootstrap store in a managed temporary directory; expose an explicit async ASGI app delegating to the guarded hosted boundary. Add nearest api/pyproject.toml and native api/uv.lock with existing runtime/Aer pins and all original constraints. Verify every resolved version and wheel/source hash against unchanged requirements.lock. Preserve local manifests, scientific sources and all existing release assets.
- Why: Two regressions failed before correction: read-only-project import and missing native hosted lock. They pass after correction; uv0.12.5 resolves24packages from official PyPI. This replaces the unverified assumption in D-083 that Vercel would select the root hashed requirements wrapper. Runtime/remote workflow gates remain pending until redeployment and execution.
- Alternatives considered: Remove the global local app or modify frozen API (unneeded); silently rely on /tmp for saved reports (not done; only unused import bootstrap lives there); force Aer mandatory for local users (breaks optional backend contract); accept fresh unpinned resolution (rejected).
- Consequences: Hosted Python builder uses its supported frozen native lock. Local pip/hash setup stays unchanged. Scratch bootstrap never serves hosted user requests. Public deployment must be independently exercised; no unit pass substitutes for it.
- Files: api/index.py, api/pyproject.toml, api/uv.lock, tests/test_hosted_entrypoint.py, docs/vercel-hosting.md, decisions.md, flow.md, handoff.md
- Symptom: FUNCTION_INVOCATION_FAILED; qfault.api import attempts artifacts/investigations on read-only filesystem. Build installation omits optional Aer.
- Root cause: Existing API app=create_app() runs at import before hosted wrapper; Vercel prioritizes nearest native Python manifest over root requirements.txt.
- Regression test: tests/test_hosted_entrypoint.py; both red then passed. Actual new deployment must be checked next.
- Supersedes: D-083 dependency-selection assumption only; all other source/privacy/exclusion rules remain.

### D-085: Verify public hosted workflows and expose only the intended new project
- Date / phase / commit: 2026-10-23, public hosting validation, uncommitted
- Context: Corrected deployment source passes531tests102.38s and17targeted hosting/entrypoint tests36.45s. Owner explicitly selects the full public interactive app. New qfault project API reports ssoProtection deploymentType all_except_custom_domains; unrelated trial project remains untouched.
- Decision: Disable Vercel deployment-login protection only on qfault for judge access, preserving strict hosted Host/Origin and signed private browser-report sessions. Add scripts.hosted_smoke to test actual public health/Aer, two-browser isolation, context restoration, independent report verification, linked replay, Origin/body guards and blind freeze/reveal, then run existing real guided workflow/mobile checks. Commit exact corrected source before deploying; verify provider results rather than upload/READY alone.
- Why: Initial build READY was not runtime proof; actual browser/runtime logs exposed two corrected integration defects. No paid service, collaborator, local runtime upload or scientific policy change is needed. Unit/store probes and real cloud tests have distinct scopes.
- Alternatives considered: Require judges to join a Vercel team (unnecessary and no collaborators authorized); return a protected or broken link as success (false); mock successful measurements (forbidden).
- Consequences: New qfault site/API public; histories remain separate browser capabilities, not shared public artifacts. Hobby resource/operation quotas apply; no global rate-limit claim. Actual browser-context restore is not claimed as forced cold restart. Existing trial and releasev0.1.0 remain unchanged.
- Files: scripts/hosted_smoke.py, docs/vercel-hosting.md, decisions.md, flow.md, handoff.md
- Package: Hosted manifest reuses qiskit2.3.1,numpy2.5.2,scipy1.18.1,pydantic2.13.4,fastapi0.141.1,uvicorn0.52.4,qiskit-aer0.17.2; no scientific version changes.
- Why this package: Aer must be present for the same measured simulator workflow; native API lock supports Vercel's actual frozen dependency selection.
- Packages compared: Umbrella vercel0.12.0/vercel-blob0.5.0 SDKs unnecessary; stdlib HTTPv12 suffices and real provider CAS/consistent reads passed.
