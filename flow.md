# Implemented runtime flow

Inputs enter qfault/cli.py:main or qfault/api.py:create_app. Both use the same qfault/workflow.py:RunRequest and investigate. The React client in web/src/main.tsx submits validated template settings to POST /api/experiments; it never executes uploaded code.

1. RunRequest validates family, qubit count, scenario, seeds, shot and evaluation bounds. scenario constructs a benchmark copy, controlled valid mutation and configured noise. Evaluator labels remain outside analyst inputs.
2. quantum.contract supplies an analytic fixed-input state and expected measurement distribution. Supervisor starts REGISTERED. ExecutionBudget reserves each operation before it runs.
3. investigate executes the trusted baseline, then the candidate with quantum.execute. Ideal sampling uses Qiskit BasicSimulator. Depolarizing execution evolves Qiskit DensityMatrix/Kraus channels; readout flips are explicit classical post-measurement noise. Raw counts, versions, settings and resources are preserved.
4. EvidenceCollector.collect validates counts and projects MeasuredEvidence. DiagnosticAnalyst.analyze evaluates TV discrepancy and a declared uncertainty bound. DiagnosticAccess offers budgeted ideal-state and readout-calibration probes; it exposes no mutation labels or noise parameters as analyst features. Exact simulator probes are privileged calculations, not hardware measurements.
5. The selected evidence/fixed/random/threshold policy updates supported hypotheses. Ambiguity, insufficient budget and lack of significant evidence remain distinct. No probability of a fault class is invented.
6. For a supported logical defect and enabled recovery, RecoveryPlanner.propose searches at most 256 admissible one-edit copies. IndependentVerifier.verify checks analytic fixed-input state agreement using DensityMatrix and fresh samples with a different seed. It returns VERIFIED, REJECTED or INCONCLUSIVE; no result automatically edits the submitted circuit.
7. Supervisor validates REGISTERED → BASELINED → OBSERVED → DIAGNOSED, optionally RECOVERY_PROPOSED → VERIFICATION_COMPLETED, then AWAITING_HUMAN_REVIEW. Completion of verification does not imply a successful verdict. Review records are separately appended; the recorded original supervisor history is immutable.
8. investigate assembles measured and derived observations, execution references, diagnostic evidence, recovery and actual resource ledger. prediction_digest freezes diagnosis/recovery before evaluator truth is attached. ArtifactStore.save separates evaluation.json from investigation.json in an exclusive directory, then creates a canonical SHA-256 manifest.
9. ArtifactStore.verify checks artifact hashes and review membership/envelope hashes. load fails closed on invalid integrity. review creates an immutable self-declared decision and atomically updates manifest membership; it authenticates no human identity. export includes measurements, separate evaluator truth, review records and integrity status.
10. API responses drive actual distributions, hypotheses, candidate outcomes, circuit text and costs in the UI. The report download exports JSON. /api/benchmark reads the committed measured benchmark summary, with full row download. CLI analyze/recovery inspect recorded outputs; run performs the actual computation.

Persistence is an inspectable file store under artifacts/investigations by default. No SQLite or external service is required. The single-process API serializes investigations and review updates. API validation errors return 422, absent investigations 404, concurrent investigations 409. Quantum errors preserve a failure artifact and return a bounded error message. Multi-file crash recovery and every intermediate execution checkpoint are unfinished; incomplete stored directories fail integrity checking.

qfault/experiments.py:benchmark_run executes the frozen corpus through investigate, checks prediction_digest, then consults evaluator_truth. It writes configuration, all raw investigations, row-level summary and SHA-256. CLI demo executes six real investigations and a dedicated tamper/restore control. Neither path fabricates outcomes.

| Session change | Actual paths | Decisions | Commit |
|---|---|---|---|
| Native circuits, contracts, noise and faults | qfault/quantum.py; tests/test_quantum.py | D-001–003 | d1f81b6 |
| Evidence, bounded diagnosis and recovery | qfault/diagnostics.py; qfault/recovery.py; qfault/workflow.py | D-004–005, D-010–011 | d1f81b6 |
| Integrity, review and robustness fixes | qfault/evidence.py; qfault/storage.py; qfault/api.py | D-006, D-009, D-012 | d1f81b6 |
| CLI, API and actual-results interface | qfault/cli.py; web/src; scripts | D-007 | d1f81b6 |
| Frozen comparisons and reproducibility | qfault/experiments.py; benchmarks; docs | D-008 | d1f81b6 |
