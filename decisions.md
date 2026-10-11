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
