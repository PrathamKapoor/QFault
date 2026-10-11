# Implemented runtime flow

Inputs enter qfault/cli.py:main or qfault/api.py:create_app. Both use the same qfault/workflow.py:RunRequest and investigate. The React client in web/src/main.tsx submits validated template settings to POST /api/experiments; it never executes uploaded code. Family/qubit selection fetches the matching /api/contracts/{family}/{qubits} contract. load restores saved run controls and the associated contract; probability keys are sorted in binary order.

1. RunRequest validates family, qubit count, scenario, seeds, shot and evaluation bounds. scenario constructs a benchmark copy, controlled valid mutation and configured noise. Evaluator labels remain outside analyst inputs.
2. quantum.contract supplies an analytic fixed-input state and expected measurement distribution. Supervisor starts REGISTERED. ExecutionBudget reserves each operation before it runs.
3. investigate executes the trusted baseline, then the candidate with quantum.execute. Ideal sampling uses Qiskit BasicSimulator. Depolarizing execution evolves Qiskit DensityMatrix/Kraus channels; readout flips are explicit classical post-measurement noise. Explicit backend=aer instead calls backends.aer_counts / aer_simulator with density_matrix, the same per-logical-gate depolarizing channel and symmetric ReadoutError; requested Aer errors never silently fall back. Raw counts, versions, settings and resources are preserved.
4. EvidenceCollector.collect validates counts and projects MeasuredEvidence. DiagnosticAnalyst.analyze evaluates TV discrepancy and a declared uncertainty bound. DiagnosticAccess offers budgeted ideal-state, complementary phase-basis and readout-calibration probes; it exposes no mutation labels or noise parameters as analyst features. Exact simulator probes are privileged calculations, not hardware measurements.
5. The selected evidence/fixed/random/threshold/phase policy updates supported hypotheses. Ambiguity, insufficient budget and lack of significant evidence remain distinct. Phase uses quantum.measured_circuit and measurement_probabilities from the declared contract. Complementary counts and calibration trigger exact-state discrimination; unfunded required evidence abstains. Fixed remains default. No probability of a fault class is invented.
6. For a supported logical defect and enabled recovery, RecoveryPlanner.propose searches at most 256 admissible one-edit copies. IndependentVerifier.verify checks analytic fixed-input state agreement using DensityMatrix and fresh samples with a different seed. Phase search reserves validation resources first, then validation also executes a fresh complementary basis at seed+10024. Submitted limits remain32 gates; private analysis circuits permit42. It returns VERIFIED, REJECTED or INCONCLUSIVE; no result automatically edits the submitted circuit.
7. Supervisor validates REGISTERED → BASELINED → OBSERVED → DIAGNOSED, optionally RECOVERY_PROPOSED → VERIFICATION_COMPLETED, then AWAITING_HUMAN_REVIEW. Completion of verification does not imply a successful verdict. Review records are separately appended; the recorded original supervisor history is immutable.
8. investigate assembles measured and derived observations, execution references, diagnostic evidence, recovery and actual resource ledger. prediction_digest freezes diagnosis/recovery before evaluator truth is attached. ArtifactStore.save separates evaluation.json from investigation.json in an exclusive directory, then creates a canonical SHA-256 manifest.
9. ArtifactStore.verify checks artifact hashes and review membership/envelope hashes. load fails closed on invalid integrity. review creates an immutable self-declared decision and atomically updates manifest membership; it authenticates no human identity. export includes measurements, separate evaluator truth, review records and integrity status.
10. API responses drive actual distributions, hypotheses, candidate outcomes, circuit text and costs in the UI. The report download exports JSON; storage.verify_export and CLI verify-report recompute its covered hashes without trusting embedded success. /api/benchmark reads the committed measured benchmark summary, with full row download. /api/evaluation reads the separately frozen final results and provides the full measured report. CLI analyze/recovery inspect recorded outputs; run performs the actual computation.

Persistence is an inspectable file store under artifacts/investigations by default. No SQLite or external service is required. The single-process API serializes investigations and review updates. API validation errors return 422, absent investigations 404, concurrent investigations 409. Quantum errors preserve a failure artifact and return a bounded error message. Multi-file crash recovery and every intermediate execution checkpoint are unfinished; incomplete stored directories fail integrity checking.

qfault/experiments.py:benchmark_run executes the frozen corpus through investigate, checks prediction_digest, then consults evaluator_truth. It writes configuration, all raw investigations, row-level summary and SHA-256. CLI demo executes six real investigations and a dedicated tamper/restore control. Neither path fabricates outcomes.

| Session change | Actual paths | Decisions | Commit |
|---|---|---|---|
| Native circuits, contracts, noise and faults | qfault/quantum.py; tests/test_quantum.py | D-001–003 | d1f81b6 |
| Evidence, bounded diagnosis and recovery | qfault/diagnostics.py; qfault/recovery.py; qfault/workflow.py | D-004–005, D-010–011 | d1f81b6 |
| Integrity, review and robustness fixes | qfault/evidence.py; qfault/storage.py; qfault/api.py | D-006, D-009, D-012 | d1f81b6 |
| CLI, API and actual-results interface | qfault/cli.py; web/src; scripts | D-007 | d1f81b6 |
| Frozen comparisons and reproducibility | qfault/experiments.py; benchmarks; docs | D-008 | d1f81b6 |

compare_policies executes a committed development/final/low-shot split through investigate, freezes predictions before evaluator_truth, and persists all rows/actions/manifest hashes. scripts/submission_demo.py executes the Aer judging scenarios and reversible throwaway tamper check. scripts/evaluate_recovery.py separately executes selected repairs and negative controls. scripts/http_release_smoke.py exercises the real running API and production asset delivery, not browser rendering. scripts/plot_policy_tradeoff.py regenerates the standalone measured figure with optional Matplotlib.

| Session change | Actual paths | Decisions | Commit |
|---|---|---|---|
| Frozen development/final inputs and original audit | configs/diagnostic-evaluation.json; scripts/audit_diagnostics.py; benchmarks/policy-audit.json | D-013–015 |1d89eff |
| Complementary measurements, separate phase policy, validation reservation | qfault/quantum.py; diagnostics.py; recovery.py; workflow.py; tests/test_phase_measurements.py | D-014–015 |3039215 |
| Aer adapter, report verification, boundary controls and measured submission evidence | qfault/backends.py; storage.py; CLI/API; web/src/main.tsx; scripts; benchmarks | D-016–019 |dffeb54 |

The separate scripts/browser_bootstrap.py launcher loads installed Playwright for testing without changing the quantum server environment. scripts/browser_e2e.py drives real browser inputs and API calls, downloads a report and verifies it with storage.verify_export, checks refresh/settings, negative422, loading, console and mobile geometry. It writes ignored raw evidence/screenshots; benchmarks/browser-verification.json records the executed summary.

| Session change | Actual paths | Decisions | Commit |
|---|---|---|---|
| Real browser workflow, saved configuration/qubit controls, binary plot order and interpreter requirement | scripts/browser_e2e.py; scripts/browser_bootstrap.py; web/src/main.tsx; pyproject.toml; tests/test_dependency_compatibility.py; benchmarks/delivery-verification.json | D-020–021 | Commit containing this entry |

Submission audit: scripts/audit_release.py reads existing final rows, matches fixed/phase case identities and truth, compares each raw manifest SHA256 to its recorded row digest, calls ArtifactStore.verify and writes an exclusive audit file. It does not call diagnosis or tune a policy. docs/simulator-information-audit.md maps measured, derived, privileged and evaluator-only information.

| Session change | Actual paths | Decisions | Commit |
|---|---|---|---|
| Disposable install audit, paired integrity checks and clearer scientific labels | scripts/audit_release.py; scripts/browser_e2e.py; web/src/main.tsx; docs/release-candidate.md; benchmarks/release-candidate-verification.json | D-022–023 | Commit containing this entry |

scripts/evaluate_recovery.py now writes only the requested exclusive directory and its summary.json; it never implicitly republishes benchmarks/recovery-stabilization.json. D-024 and tests/test_recovery_output_isolation.py document the real-execution preservation regression.
