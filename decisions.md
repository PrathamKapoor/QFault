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
