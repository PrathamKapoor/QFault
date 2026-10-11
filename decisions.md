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
