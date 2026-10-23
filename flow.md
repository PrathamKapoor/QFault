# QFault runtime and evidence flow

Current implementation: 2026-10-22. Earlier flow records, including retired hero
symbols, are preserved in [flow history](docs/flow-history-20261022.md).
Decisions are append-only in decisions.md. Source paths below are repository-relative.

## 1. Startup and configuration

Subsystem: Local service.
Trigger / when: `python -m qfault serve --port N` after frontend build.
What: Serve the actual workbench and local API.
Why: One local process is sufficient for bounded simulation.
Input / schema / provenance: CLI port; QFAULT_ARTIFACTS, default artifacts/investigations; web/dist.
Ordered calls with actual symbols and paths:
```text
cli.main()                      qfault/cli.py
 └─ api.main(port)              qfault/api.py; probe loopback port and print PID
     └─ create_app()            initialize ArtifactStore, BlindChallenges, local lock
         ├─ LocalRequestBoundary() validate Host/Origin
         ├─ RequestBodyLimit()  count bytes before parsing
         └─ StaticFiles        serve built assets; API routes use shared engine
```
Validation and trust boundary: Loopback bind; localhost/127.0.0.1/::1 authorities; same-origin writes when Origin exists. No proxy hosting/authentication claim. testserver only for explicit test/store app construction.
Output / schema / units: HTTP API and production assets; port integer, PID operating-system identifier.
Persistence / identity / version: Existing artifact root reused; API version 0.1.0; no external service/key required.
Error / timeout / cancellation / recovery behavior: Occupied port exits 2; missing web build returns 503. No backend cancellation endpoint.
Verification commands and tests: tests/test_serve.py, test_local_trust.py; scripts.release_smoke.
Known limitations: Local single-process trust, no multiuser identity or distributed admission.

Operational rehearsal at287dd4fadaacf973aa3eb926e79189f5958b3949: npm --prefix web run build; QFAULT_ARTIFACTS=artifacts/live-judge-investigations; python -m qfault serve --port8000. Frontend/API share http://127.0.0.1:8000/. Root/health and scripts.guided_demo_e2e passed. This reuses cli.main→api.main→create_app above; no separate frontend proxy. Runtime identity is ephemeral handoff context.

## 2. Circuit import and structured validation

Subsystem: Developer input.
Trigger / when: Local conversion, CLI import-qasm, browser JSON Apply or API request.
What: Produce CustomCircuit with supported semantics and optional ImportProvenance.
Why: Avoid hand transcription and silent unsupported operations.
Input / schema / provenance: Local QuantumCircuit or bounded UTF-8 static QASM2, then CustomCircuit schema 1. Source representation/digest, Qiskit version/options and converted ID are recorded.
Ordered calls with actual symbols and paths:
```text
from_qiskit()                   qfault/qasm_import.py; exact built-in gate vocabulary
 ├─ Gate.model_validate()       qfault/quantum.py; arity, wires, finite radians
 └─ CustomCircuit.model_validate() qfault/lab.py; input/qubit/gate limits
cli.main(import-qasm)           qfault/cli.py
 └─ from_qasm2()                qfault/qasm_import.py; explicit transformation permissions
     └─ import_qasm2()          source parsing, ordered translation, full-operator comparison
```
Validation and trust boundary: No Python upload/eval/pickle or user module import. Native H/X/Z/S/Rx/Ry/Rz/CX/CZ/CP/SWAP only. Removal of barriers/terminal measurements opt-in. QASM decomposition opt-in; source definitions/external includes/reset/control flow rejected. Numeric strings/booleans rejected in scientific fields.
Output / schema / units: 2–5 qubits, at most 32 subject gates; angles ±8π radians. Qiskit rightmost bit/Pauli character is q0; amplitude index i is binary i. Global phase recorded, irrelevant to supported state/distribution claims.
Persistence / identity / version: Structural circuit ID excludes name/provenance. Absent provenance omitted from legacy serialization; derived edits retain import ancestry.
Error / timeout / cancellation / recovery behavior: Unsupported native operations identify instruction index; nonzero input preparation occurs once in CustomCircuit.preparation, not conversion. Conversion failure executes no investigation.
Verification commands and tests: test_native_import.py, test_qasm_import.py, test_custom_cli.py, test_strict_scientific_input.py.
Known limitations: Trusted local object conversion is not hostile-Python isolation; successful conversion does not establish independent contract correctness.

## 3. Contract provenance and feasibility

Subsystem: Declared claims.
Trigger / when: Validate before execution/recovery.
What: Validate independent expected behavior and estimate measurable scope under budget.
Why: Candidate-derived expectations are circular.
Input / schema / provenance: PauliContract, DistributionContract or TargetStateContract; reference/user declaration. External evaluation parses a distinct original QASM reference before candidate mutation.
Ordered calls with actual symbols and paths:
```text
LabRequest.valid()              qfault/lab.py
 ├─ check_pair()                match widths/dimensions
 ├─ _check_consistency()        necessary anticommutation/correlation constraints
 └─ feasibility()               plan claims, groups, per-interval alpha/radius
     ├─ plan()/group_paulis()   compatible terms share basis shots
     └─ target_feasibility()    target-only catalog and best affordable bound
api.lab_validate()              qfault/api.py; display feasibility, no execution
```
Validation and trust boundary: Finite values, normalization within declared tolerance, unique labels, bit widths and target dimensions. Pauli consistency checks are necessary, not a general sufficient physical realizability proof. No silent invalid-contract normalization.
Output / schema / units: Claim/group plans, available shots, best-case radii and unresolved limitations; probabilities/expectations dimensionless, infidelity dimensionless.
Persistence / identity / version: Canonical contract digest in investigations/recovery; provenance retained in requests/target declarations. Template contracts are independent analytic definitions.
Error / timeout / cancellation / recovery behavior: Invalid request 422, no quantum execution; valid input can remain infeasible/unresolved.
Verification commands and tests: test_lab.py, test_target.py, test_strict_scientific_input.py.
Known limitations: One input/contract never proves every input, a complete unitary, hardware correctness or cause.

## 4. Template investigations

Subsystem: Controlled Bell/GHZ/QFT workflow.
Trigger / when: CLI run or POST /api/experiments.
What: Execute a controlled scenario, inspect diagnosis, optionally propose simulator-assisted repair.
Why: Retain useful reproducible examples while separating privileged analysis.
Input / schema / provenance: RunRequest; analytic contract; evaluator scenario constructed separately.
Ordered calls with actual symbols and paths:
```text
workflow.investigate()          qfault/workflow.py
 ├─ scenario()/quantum.contract() construct controlled candidate and independent contract
 ├─ quantum.execute()          baseline/candidate measurements
 ├─ EvidenceCollector.collect() qfault/diagnostics.py; allowlisted evidence
 ├─ DiagnosticAnalyst.analyze() / MeasurementOnlyAnalyst.analyze()
 ├─ RecoveryPlanner.propose()   qfault/recovery.py; simulator-assisted path only
 └─ IndependentVerifier.verify() fresh samples and density-matrix check
```
Validation and trust boundary: DiagnosticAccess state probes are privileged simulation. MeasurementPort excludes candidate state/noise/truth. Labels stay outside prediction inputs; evaluator truth is attached after prediction digest.
Output / schema / units: Schema 1 investigation; category, ambiguity, scope, shots/evaluations, exact-state costs and optional verification verdict.
Persistence / identity / version: Supervisor records operation completion separately from VERIFIED success; ArtifactStore separates evaluation.json.
Error / timeout / cancellation / recovery behavior: Invalid input fails before execution; API execution failures retain local failure record and return safe error; no automatic original edit.
Verification commands and tests: test_investigation.py, test_measurement_only.py, test_phase_truth_isolation.py; scripts.browser_e2e.
Known limitations: Historical template success rates use differing actual shot costs; simulator privileges cannot be advertised as measurement-only diagnosis.

## 5. Measurement acquisition and resource accounting

Subsystem: Execution port.
Trigger / when: A funded measurement group/control is selected.
What: Reserve resources, build basis circuit, execute backend, project counts.
Why: Planners must receive only information actually available to them.
Input / schema / provenance: Subject retained privately by _Port; declared noise, backend, shots/seed/settings. PolicyConfig contains only planner settings.
Ordered calls with actual symbols and paths:
```text
_Port.measure()                qfault/lab.py
 ├─ measurement_circuit()/basis_rotation() add real analysis gates
 ├─ ExecutionBudget.reserve()  qfault/diagnostics.py; charge before execution
 ├─ quantum.execute()          qfault/quantum.py
 │   └─ backends.aer_counts()  qfault/backends.py when explicitly selected
 └─ EvidenceCollector.collect() validate counts/shots and allowlist evidence
```
Validation and trust boundary: Exact state/noise implementation may exist inside the simulator, but analyst sees only counts and declared contract. Preparation/subject/analysis gates receive the specified gate-noise model; readout is a separate classical channel.
Output / schema / units: Raw counts, actual shots, execution ID/seed, basis setting/backend version and charged gate/depth/evaluation resources; no currency conversion.
Persistence / identity / version: Execution documents in investigation plus action ledger. Distinct calls have distinct IDs and deterministic distinct seeds.
Error / timeout / cancellation / recovery behavior: Budget fails before job; requested Aer does not silently fall back. In-flight backend jobs are not hard-cancelled.
Verification commands and tests: test_aer_backend.py, test_aer_absence.py, test_measurement_boundaries.py, test_information_boundaries.py; scripts.aer_smoke.
Known limitations: IID stationary samples/model assumptions; backend agreement is not hardware validation or independent vendor proof.

## 6. Distribution and Pauli inference

Subsystem: Sequential finite-shot claims.
Trigger / when: Custom investigation with distribution/Pauli contract.
What: Select bounded looks, update simultaneous intervals, return supported/unresolved verdict.
Why: Adaptive measurement/stopping needs explicit error allocation.
Input / schema / provenance: Contract-only plan, counts port, PolicyConfig; no candidate state.
Ordered calls with actual symbols and paths:
```text
investigate_lab()              qfault/lab.py
 └─ run_policy()
     ├─ alpha_slot()           alpha_total/(claims*looks+1)
     ├─ _Port.measure()        next funded group
     └─ _State.add()/report()   estimates, intervals, claim status
```
Validation and trust boundary: Pauli means lie in [-1,1], Hoeffding radius sqrt(2 log(2/alpha_slot)/N). Distribution TV uses sqrt(log((2^d−2)/alpha_slot)/(2N)), clipped at one, d=2^n outcomes. Prespecified per-group look grid and union bound cover all looks/claims plus one control. Shared-shot observables need no independence from each other for the union bound.
Output / schema / units: NO_SIGNIFICANT_DISCREPANCY, SIGNIFICANT_DISCREPANCY or INSUFFICIENT_EVIDENCE; expectation/TV intervals and exact stopping reason. Alpha is an error ceiling under assumptions, not probability a diagnosis is correct.
Persistence / identity / version: Schema 2 investigation/action ledger. Privileged exact_expectations only runs after measured analysis when explicitly simulator-assisted.
Error / timeout / cancellation / recovery behavior: Unfunded next look stops unresolved; violated claims trigger reserved zero-state readout control. A control cannot exclude all gate/state-dependent noise.
Verification commands and tests: test_lab.py, test_information_boundaries.py, test_identifiability_examples.py.
Known limitations: Incomplete contracts can miss phase errors; necessary physical consistency checks do not prove complete realizability.

## 7. Target-state witnesses

Subsystem: Conditional fidelity bounds.
Trigger / when: TargetStateContract investigation.
What: Expand declared target, measure selected compatible groups, bound fidelity.
Why: Unmeasured terms cannot be treated as known candidate expectations.
Input / schema / provenance: Target amplitudes only for catalog; measured means/radii for candidate. Target vector normalization correction stays within the documented accepted tolerance and norm is recorded.
Ordered calls with actual symbols and paths:
```text
run_witness_policy()           qfault/lab.py
 ├─ target.catalog()           qfault/target.py; target-only coefficients/omitted mass
 ├─ target.bounds()/decide()   rigorous interval and stopping decision
 ├─ target.marginal_gains()    optional plug-in planning proxy
 └─ _Port.measure()            measured groups, never exact candidate state
```
Validation and trust boundary: F=(1+Σa_P b_P)/2^n. Unmeasured/omitted contribution bounded by minimum L1/purity Cauchy–Schwarz slack. Stabilizer generator projector bounds and Fuchs–van de Graaf upper bounds intersect the expansion interval. Alpha is split across all catalog terms × looks plus control. Plug-in point_estimate is heuristic and cannot verify.
Output / schema / units: Conditional [L,U] fidelity, claim status and unmeasured mass. L>U returns unresolved; declared uncalibrated noise withholds state certification.
Persistence / identity / version: Catalog/policy versions and target_evidence retained; historical effective-state interpretations remain separately documented.
Error / timeout / cancellation / recovery behavior: Dense targets/budget exhaustion remain unresolved. No clipping of contradictory intervals into a success. Noisy target recovery abstains without calibrated common-state support.
Verification commands and tests: test_target.py, test_information_boundaries.py; external report verifier and pinned source corpus.
Known limitations: Basis-dependent analysis noise need not represent one physical state; no physical calibration was established. Adaptive order is not uniformly superior.

## 8. Bounded intervention generation

Subsystem: Permitted edits.
Trigger / when: Valid RecoveryRequest.
What: Enumerate deterministic one-edit candidates, exclusions and equivalent structural loci.
Why: Search scope/coverage must be visible rather than implied exhaustive synthesis.
Input / schema / provenance: CustomCircuit; EditRestrictions operators/palette/angles/positions/depth; accepted candidate limit 1–48.
Ordered calls with actual symbols and paths:
```text
interventions.generate()       qfault/interventions.py
 ├─ proposals()                declared operator/location order
 ├─ Gate()/CustomCircuit()     preserve validated size/arity/input semantics
 └─ resources()                qfault/quantum.py; operational resource deltas
```
Validation and trust boundary: At most 4,096 proposals inspected; strict numeric fields; no state/evaluator access. No-ops/structural duplicates/invalid/untested proposals recorded.
Output / schema / units: Candidate IDs, edits, equivalent locations, exclusions/truncation and depth/two-qubit deltas.
Persistence / identity / version: Deterministic structural hashing; imported ancestry retained in derived circuits.
Error / timeout / cancellation / recovery behavior: Unsupported edit settings fail validation. Exhausted search does not become a complete synthesis claim.
Verification commands and tests: test_counterfactual.py, test_repair_boundaries.py, test_strict_scientific_input.py.
Known limitations: Structural hashing is not semantic deduplication; alternative/unsearched restoring edits remain possible.

## 9. Selection and fresh paired recovery verification

Subsystem: Measured recovery.
Trigger / when: POST /api/lab/recoveries or CLI measured-recovery.
What: Observe, screen bounded candidates, freeze selection, collect fresh original/candidate evidence.
Why: Screening success is not independent confirmation.
Input / schema / provenance: RecoveryRequest; declared contract and permitted edits, matched policies/budgets.
Ordered calls with actual symbols and paths:
```text
counterfactual.recover()        qfault/counterfactual.py
 ├─ generate()                 bounded proposals
 ├─ ContractObservation()      qfault/recovery_observation.py; fixed group schedule
 ├─ ExecutionBudget.can()      reserve original/candidate confirmation and possible control
 ├─ ContractObservation.observe() original, control, screening
 ├─ rank()                     retain interval overlap; operational ties use resources
 ├─ selection                  bind IDs, screening digest, order/budget before confirmation
 ├─ ContractObservation.observe() fresh original then fresh selected candidate
 └─ verification_verdict()      candidate upper loss <=1 and original lower > candidate upper
```
Validation and trust boundary: Alpha_total/((C+3)*M+1) covers original, C candidates, fresh pair and control; one prescribed look per group/subject. Fresh counts never reuse screening. No evaluator labels/exact candidate analysis.
Output / schema / units: Schema 3, original/candidate diff, generation coverage, frozen selection, separate verification/abstention/error statuses and phase costs. Worst-claim normalized loss/improvement is dimensionless tolerance units, not automatically TV/fidelity.
Persistence / identity / version: Original immutable; selected circuit exportable. Selection is recorded in-memory order, not external timestamp or crash-durable checkpoint.
Error / timeout / cancellation / recovery behavior: Insufficient reserve prevents measurements; no repair needed, noise-control abstention, no candidate, inconclusive, rejected, timeout/backend error remain distinct. max_seconds is cooperative between jobs.
Verification commands and tests: test_counterfactual.py, test_information_boundaries.py; scripts.audit_counterfactual / verify_recovery_archive; scripts.counterfactual_e2e.
Known limitations: An intervention does not identify the original cause. Zero observed false verification is not a population guarantee.

## 10. Blind observe/diagnose/freeze/reveal

Subsystem: Controlled local challenge.
Trigger / when: Challenge UI and /api/challenges routes.
What: Record observations and prediction before revealing evaluator truth.
Why: Prevent accidental answer leakage through normal API/history/export paths.
Input / schema / provenance: ChallengeRequest and server-selected controlled setup; private engine record separated from participant projection.
Ordered calls with actual symbols and paths:
```text
BlindChallenges.start()        qfault/challenge.py -> workflow.observe()
 └─ diagnose()                 workflow.investigate(initial_records=...)
     └─ freeze()               bind public observations/prediction to engine digest
         └─ reveal()           verify private record and expose evaluator result
```
Validation and trust boundary: OBSERVED→DIAGNOSED→FROZEN→REVEALED only; public allowlists exclude hidden names/seeds/candidate/truth. Reveal verifies bindings; pre-reveal exports remain public-only.
Output / schema / units: Challenge schema 1, measured projections, lifecycle state, frozen prediction and eventual evaluation; costs in shots/evaluations.
Persistence / identity / version: Separate exclusive public/private documents, challenge ID and digests; exported chain independently checked by verify_challenge_export.
Error / timeout / cancellation / recovery behavior: Conflicting/repeated transitions return safe 409; corrupted/unavailable private records do not disclose truth. Reads/admission serialized in local process.
Verification commands and tests: test_blind_challenge.py; scripts.blind_challenge_e2e.
Known limitations: Not secrecy from an administrator, supplied-seed inference protection or authenticated competition infrastructure.

## 11. Persistence, integrity and review

Subsystem: Artifact store.
Trigger / when: Completed execution, load/history/review/export.
What: Preserve canonical scientific documents and separately bound reviews.
Why: Results need inspection beyond one UI session.
Input / schema / provenance: Engine result, experiment ID, self-declared reviewer/reason/action.
Ordered calls with actual symbols and paths:
```text
ArtifactStore.save()           qfault/storage.py; exclusive experiment directory
 ├─ canonical() / digest()     qfault/evidence.py; investigation/evaluator documents
 └─ manifest.json              last completion document, schema 1
ArtifactStore.load()/list()
 └─ verify()                   version support, hashes, membership/reviews
ArtifactStore.review()
 ├─ immutable review envelope  bound to investigation digest
 └─ temporary.replace()        atomic review-index manifest update
```
Validation and trust boundary: Exact experiment ID pattern; manifest membership fixed; supported investigation version/kind pairs 1/template, 2/custom, 3/recovery. Unsupported formats fail explicitly, never migrated silently.
Output / schema / units: investigation.json, evaluation.json, manifest.json and review envelopes; SHA-256 under qfault-json-v1, UTF-8 sorted compact JSON. Integer 1 and float 1.0 can encode differently.
Persistence / identity / version: No record overwrite. Review identity self-declared, membership hash-bound; unrelated files outside manifest are not covered.
Error / timeout / cancellation / recovery behavior: Interrupted multi-file saves can leave partial directories; verification fails closed and history shows corrupt rather than verified. Manual inspection/recovery may be required. Atomic review index does not provide a distributed transaction or external anchor.
Verification commands and tests: test_storage_api.py, test_artifact_corruption.py, test_artifact_versions.py.
Known limitations: A complete replacement/rehash can pass consistency; no signature, trusted timestamp or deletion-resistant external history.

## 12. Export and independent verification

Subsystem: Portable report.
Trigger / when: Download /api/experiments/{id}/report, CLI export/verify-report.
What: Export covered documents; recompute integrity without trusting embedded valid flag.
Why: Another user must inspect evidence offline.
Input / schema / provenance: Stored documents or standalone JSON bundle.
Ordered calls with actual symbols and paths:
```text
ArtifactStore.export()         qfault/storage.py
 └─ verify_export()            schemas, identities, membership, digests/reviews
     └─ verify_challenge_export() public lifecycle and nested revealed record
cli.main(verify-report)        qfault/cli.py; exit 0 valid / 1 invalid or unavailable
```
Validation and trust boundary: Hash consistency only; scientific recount is a separate operation. An embedded verification=true is not trusted.
Output / schema / units: Explicit valid/errors/assurance; JSON report, no archive execution.
Persistence / identity / version: Exclusive CLI export destination; original identity preserved in report.
Error / timeout / cancellation / recovery behavior: Malformed/missing/corrupt/unsupported data fails; no success fallback. Recovery engine limits canonical record size to 16 MiB.
Verification commands and tests: test_export_verification.py, test_artifact_versions.py; qfault verify-report on demonstration export and altered negative control.
Known limitations: Consistency does not prove the contract, physical assumptions or conclusions scientifically valid.

## 13. Replay and new-seed rerun

Subsystem: Repeat execution with traceable ancestry.
Trigger / when: Existing custom/recovery replay route; optional ReplayOptions seed.
What: Create a NEW investigation; keep original unchanged.
Why: Deterministic replay and fresh sampling have different meanings.
Input / schema / provenance: Verified saved request, parent ID, optional strict unsigned 32-bit seed.
Ordered calls with actual symbols and paths:
```text
api.lab_replay()/replay_recovery() qfault/api.py
 ├─ existing()                    verify/load original
 ├─ LabRequest/RecoveryRequest.model_validate() validate saved configuration
 └─ run_lab()/run_recovery()       shared engine/admission
     └─ ArtifactStore.save()       replay.source_experiment_id and semantics recorded
```
Validation and trust boundary: Same seed means deterministic_replay; different explicit seed means new_seed_rerun. New IDs never overwrite parent. BlindChallenges.replay uses its own disclosed controlled lifecycle.
Output / schema / units: New identity and parent link; seed dimensionless integer; same circuit/contract/budget retained.
Persistence / identity / version: All new provenance in covered investigation; old documents untouched.
Error / timeout / cancellation / recovery behavior: Wrong mode/invalid saved request 422 before lock; execution errors use ordinary failure handling.
Verification commands and tests: test_replay_identity.py, test_final_api_adversarial.py; browser history/refresh/replay suites.
Known limitations: Reusing seeds is reproducibility, not independent sampling; different seeds retain simulator bias and shared model assumptions.

## 14. Corpus, protocol freeze and evaluation

Subsystem: Scientific evaluation.
Trigger / when: Deliberate development/frozen evaluation command, never ordinary user execution.
What: Retain every attempted case, baseline, exclusion, abstention, failure and resource cost.
Why: Headline denominators must reconcile with raw evidence.
Input / schema / provenance: Frozen protocols/corpus, declared contracts from distinct reference sources, seeds/budgets/policies/source hashes. External QASMBench revision and redistribution notices retained.
Ordered calls with actual symbols and paths:
```text
scripts.external_corpus        pinned eligibility inventory
scripts.external_validation    reference_contract() -> candidate -> investigate_lab()/recover()
 └─ scripts.verify_external_results.verify_results() reports, rows and aggregates
     └─ scripts.reconcile_external_evidence.reconcile_rows() every attempted Cartesian case
scripts.current_release_evaluation.freeze() new versioned current-source replication protocol
 └─ run()                      committed sources, exact frozen requests, new exports
     └─ audit_record()          scripts/audit_counterfactual.py; independent recovery interval reconstruction
scripts.verify_replication.verify() scripts/verify_replication.py; offline retained current-source evidence
 ├─ verify_export() qfault/storage.py; schema/membership/document identities
 ├─ normalized() scripts/current_release_evaluation.py; compare frozen scientific projection
 ├─ summary source map equality with frozen protocol; reject inconsistent recorded source identity
 └─ audit_record() scripts/audit_counterfactual.py; reconstruct recovery intervals from counts
```
Validation and trust boundary: Truth stays outside participant policies. Byte hashes and separately named LF-normalized digests retain distinct rules. Old source guards/protocols remain unchanged. Current replication uses observed designs/seeds and is explicitly NOT untouched holdout evidence.
Output / schema / units: Versioned rows, raw exports, source identities, counts, shots/executions/runtime and negative findings; descriptive comparisons across correlated seeds/designs.
Persistence / identity / version: Exclusive output directories; original studies unchanged. Changed scientific sources require new protocol, never editing old fingerprints.
Error / timeout / cancellation / recovery behavior: Source mismatch refuses execution; errors retained as rows. No outcome-based deletion or repeated holdout tuning.
Verification commands and tests: test_external_validation.py, test_external_result_verification.py, test_evidence_reconciliation.py; corresponding scripts.
Known limitations: Nine external holdout programs, repeated mutants/seeds, no population superiority or hardware inference. Qualitative competitor scope is documented separately.

## 15. Evidence acquisition, recount and packages

Subsystem: Reproducibility delivery.
Trigger / when: Explicit source verification/retrieval, historical recount or package command.
What: Provide public-safe evidence and explicitly labelled source/evidence snapshots.
Why: Private ignored investigations cannot silently satisfy public evidence claims.
Input / schema / provenance: Pinned QASM corpus, committed external archive, curated original historical recovery archive and unchanged summary.
Ordered calls with actual symbols and paths:
```text
scripts.retrieve_external_sources.verify_sources()/download_sources() pinned byte verification/retrieval
scripts.verify_recovery_archive.verify() 310 original records, summary bindings and audit_record()
scripts.package_submission.build_package()
 ├─ _git()                     clean named source commit
 ├─ verify_results()/reconcile_rows()/verify_recovery_archive.verify() evidence preflight
 ├─ ls-tree/show               exact committed source bytes; no reachable Git history
 └─ verify_package()           bounded ZIP member/digest checks before atomic directory rename
```
Validation and trust boundary: Retrieval confines paths, source sizes, timeouts and expected digests; never executes downloads. Package excludes paper/research/.tex, runtime/dependencies, unsafe paths/symlinks. Source-only omits raw report archives and reports incomplete evidence.
Output / schema / units: Package schema 1, source ZIP, source commit/mode, member/package SHA-256, byte counts and exact evidence scope. Evidence-inclusive covers explicitly named available studies, not absent historical families.
Persistence / identity / version: Exclusive output under artifacts; temporary sibling then rename; no overwriting source/protocol/history. Historical archive publication date is not its original execution time.
Error / timeout / cancellation / recovery behavior: Dirty source/missing evidence/corruption fails before success manifest. Ordinary exceptions remove temporary output; process crashes can leave unadvertised temporary siblings. Verifier does not extract untrusted members.
Verification commands and tests: test_transfer.py, test_release_package.py, test_recovery_archive.py, test_external_sources.py; package --verify and fresh extraction/install gate.
Known limitations: Unsigned checksums; source-only cannot run omitted evidence checks. Full-current availability is distinct from historical completeness; see docs/evidence-availability.md.

## 16. Frontend navigation, results and failure states

Subsystem: Existing React workbench and approved landing identity.
Trigger / when: Hash navigation, validated form actions, history selection or evidence viewing.
What: Display returned evidence, costs, scope and actionable next steps.
Why: Developers must understand what was measured without inspecting source.
Input / schema / provenance: Backend API JSON only; no competing frontend diagnosis or fabricated fallback.
Ordered calls with actual symbols and paths:
```text
App                            web/src/App.tsx; hash route and persistent workspace
 ├─ Landing                    web/src/components/landing/Landing.tsx
 │   ├─ MentalHero             approved hero/helix composition and cleanup
 │   ├─ PixelSwap              existing handover transition
 │   └─ ResearchEvidence       GET /api/research; recorded summary, no hardcoded metrics
 └─ Workbench                  web/src/main.tsx
     ├─ CustomLab              validated JSON, contract, feasibility -> real investigation
     ├─ MeasuredRecovery       diff, search coverage, selection, fresh verification and export
     └─ BlindChallenge         controlled observe/diagnose/freeze/reveal
```
Validation and trust boundary: Browser displays backend verdicts; request failures remain visible. Busy controls prevent duplicate execution; stale selection response guards preserve current record. Source availability is file presence, not claimed live scientific audit.
Output / schema / units: Plain-language claims/evidence/verdict/cost/scope, raw JSON, diagrams and labelled interval units. Current measured recovery foregrounded; template benchmark history retained.
Persistence / identity / version: Draft workspace preserved across home navigation; hash routes restore saved identities; no server cancellation fiction.
Error / timeout / cancellation / recovery behavior: Loading/empty/error/corrupt states explicit; missing research API returns unavailable without substitute values. Reduced motion/WebGL fallback retain access.
Verification commands and tests: npm check/build; scripts.release_smoke, lab_e2e, counterfactual_e2e, blind_challenge_e2e, external_demo_e2e, cinematic_e2e, landing_recovery_e2e, workspace_navigation_e2e, inspection_smoke.
Known limitations: Single-process synchronous backend; UI stages are measured/known states, not invented percent progress. Actual desktop/mobile browser verification is a separate release gate.

## 17. Failure recovery, demonstration and publication

Subsystem: Operational release.
Trigger / when: Validation/execution failure, controlled demo, or final publication after gates.
What: Preserve actionable failure evidence, demonstrate real outcomes, publish only verified public-safe source/evidence.
Why: Tests alone do not establish complete user workflow or remote release identity.
Input / schema / provenance: Actual Git state/locks, owner identity, approved public source/evidence, real API/Aer runs.
Ordered calls with actual symbols and paths:
```text
api.run_lab()/run_recovery()    qfault/api.py; one threading lock, finally release
 └─ failures/                  safe local configuration/error record on execution failure
scripts.judging_demo.run()     native phase fixture -> inadequate Z -> IX -> recovery/noise/budget -> exports
scripts.release_smoke          real Chromium/API/Aer/export
git fetch / reviewed commit / normal push / fetch exact remote comparison
```
Validation and trust boundary: One local process; direct CLI processes do not share API lock. No Internet hosting/authentication/hardware claims. No secrets/runtime sessions in staging/packages; license/provenance notices retained.
Output / schema / units: Gate statuses PASS/FAIL/BLOCKED/NOT_RUN with command/date/source/evidence; exact remote SHA and CI result. Demonstration output preserves real costs/uncertainty.
Persistence / identity / version: Focused commits with owner author/committer; no history rewrite/force-push. Next ordinary documentation commit records prior implementation hash. Tests/media records are dated to actual tested source.
Error / timeout / cancellation / recovery behavior: Corrupt/partial artifacts never become verified; concurrent mutations return documented busy response. Backend cooperative limits are not hard cancellation. Failed mandatory gates block release readiness/publication while independent work continues.
Verification commands and tests: Complete pytest, pip check/advisory scan, npm audit/check/build, real browser suites, independent raw recount, package extraction, secret scan, remote SHA/CI checks.
Known limitations: No selected competition, no submission/external messages, no narrated final video unless actually recorded and played back. No guarantee of winning or production readiness.

## Changes in this session (implementation and release 2026-10-22)

| Area | Change | Files | Commit | Decision |
|---|---|---|---|---|
| Baseline/packages | Actual preservation ledger; explicit source/evidence contracts and independent package verifier | docs/implementation-ledger.md; docs/evidence-availability.md; scripts/package_submission.py; tests/test_release_package.py | uncommitted | D-048 |
| Import/CLI | Native and opt-in QASM conversion with retained provenance, shared lab/recovery CLI | qfault/qasm_import.py; qfault/lab.py; qfault/cli.py; tests/test_native_import.py; tests/test_custom_cli.py | uncommitted | D-049 |
| Input | Reject coercible scientific strings/booleans | qfault/quantum.py; qfault/lab.py; qfault/target.py; qfault/counterfactual.py; tests/test_strict_scientific_input.py | uncommitted | D-050 |
| Dependencies | Scoped Vite/certifi advisory fixes; strict edit numerics | web/package.json; web/package-lock.json; pyproject.toml; requirements.lock; qfault/interventions.py | uncommitted | D-051 |
| Replay | New parent-linked records and same/new-seed semantics | qfault/api.py; tests/test_replay_identity.py | uncommitted | D-052 |
| UI/evidence | Shared current summary/denominators, preserved hero; exact scanner false-positive classification | qfault/api.py; web/src/components/ResearchEvidence.tsx; Overview.tsx; landing/Landing.tsx; tests/test_research_summary.py; .gitleaks.toml | uncommitted | D-053 |
| Schemas | Explicit supported version/kind guards | qfault/storage.py; tests/test_artifact_versions.py | uncommitted | D-054 |
| Local trust | Loopback authority and same-origin mutation checks | qfault/api.py; tests/test_local_trust.py | uncommitted | D-055 |
| Historical evidence | Curated exact 310-export archive and portable independent recount, retained historical docs | benchmarks/historical-recovery-v1; scripts/verify_recovery_archive.py; tests/test_recovery_archive.py; tests/test_final_api_adversarial.py; docs/handoff-history-20261016.md; docs/flow-history-20261022.md | uncommitted | D-056 |
| Current verification/demo/docs | New source-pinned replication path, genuine native phase demo, complete current subsystem records | scripts/current_release_evaluation.py; scripts/judging_demo.py; docs/native-import.md; docs/judging-guide.md; README.md; flow.md; decisions.md; handoff.md | uncommitted | D-057 |
| Development/review | Record matched dense-target allocation negative result; safely report malformed ZIP decompression | scripts/dense_target_study.py; tests/test_witness_allocation.py; benchmarks/dense-target-development-v1.json; scripts/package_submission.py; tests/test_release_package.py | uncommitted | D-058 |
| Release scope | Exclude private configuration/research and document no provider dependency; extend qualitative primary-source comparison | .gitignore; README.md; docs/competitor-comparison.md | uncommitted | D-059 |
| Final resource check | Bound standalone report reads; preserve unexecuted protocol drafts and freeze uniquely identified final v3 | qfault/cli.py; tests/test_report_size_limit.py; scripts/current_release_evaluation.py; configs/current-release-replication-v*.json; docs/dense-target-development.md | uncommitted | D-060 |
| Visual accessibility | Correct research metrics/caption contrast specifically on the light overview | web/src/components/ResearchEvidence.css; web/src/components/ResearchEvidence.tsx | uncommitted | D-061 |
| Browser verification | Exercise native provenance through real editor/Aer/recovery/download and inspect corrected mobile contrast | scripts/native_demo_e2e.py; docs/implementation-ledger.md | uncommitted | D-062 |
| Final schema/scan | Require explicit blind schema support and narrowly classify source hashes in versioned protocols | qfault/storage.py; tests/test_artifact_versions.py; scripts/current_release_evaluation.py; configs/current-release-replication-v4.json; .gitleaks.toml | uncommitted | D-063 |
| Current retained evidence | Verify 72 current-source exports, costs and frozen projections before full packaging; record release checks | scripts/verify_replication.py; scripts/package_submission.py; tests/test_replication_verifier.py; benchmarks/current-release-replication-v4; docs/release-verification-20261023.md; root records | uncommitted | D-064 |
| Package description | Scope completeness to explicitly listed available studies; record independently extracted checks | scripts/package_submission.py; docs/release-verification-20261023.md; handoff.md | uncommitted | D-065 |
| Offline source binding | Reject summary fingerprints inconsistent with checked frozen protocol | scripts/verify_replication.py; tests/test_replication_verifier.py; release records | uncommitted | D-066 |
| Offline format boundary | Require literal integer schema versions in package and replication parsers | scripts/package_submission.py; scripts/verify_replication.py; corresponding tests; release records | uncommitted | D-067 |
| Publication | Normal main fast-forward/push, exact remote comparison, fresh GitHub evidence acquisition and exact-SHA CI record | docs/release-verification-20261023.md; docs/implementation-ledger.md; docs/current-state.md; root records | uncommitted | D-068 |

D-048–D-063 and their implementation rows above were committed in
97710d834abeef93f0094b169a05d182f22c8434. Earlier uncommitted labels describe
write time; this follow-up records the known hash without rewriting decisions.
D-064 is committed as 6998e5959180af6c7224b95cb468fa8dd8ea7503.
D-065 is committed as 4cc58de3aff12f27ed1f6dc131507551acf1bc7a.
D-066 is committed as 285939f0b170d953d54600955393d3c90f6558c0.
D-067 is committed as 66db0167fd46ea262bbb22282038fac331707330.
D-068 is committed as 9866fdb9ed7f22079f6e96bca18d55f0c7d9e173.

## Changes in this session (guided demonstration and public delivery)

| Area | Change | Files | Commit | Decision |
|---|---|---|---|---|
| Baseline/design | Verify clean source, exact-SHA CI and absent public releases; choose existing-engine guided workflow and sequential acceptance checklist | docs/judge-delivery-plan.md; root records | uncommitted | D-069 |
| Demonstration inputs | Validate pinned external source, imported ancestry, independent contracts and ordinary real-engine requests; structural preview does not execute | qfault/demo.py; qfault/api.py; scripts/guided_demo.py; examples/qrng-phase-demo.json; tests/test_guided_demo.py | uncommitted | D-070 |
| Guided interface | Add legal stages, real requests, synchronous duplicate gate, ID-only refresh restoration and honest unknown completion; preserve hero | web/src/components/GuidedDemo.tsx; web/src/components/GuidedDemo.css; web/src/guided; web/src/main.tsx; Overview.tsx; landing/Landing.tsx; tests/guided-session.test.mjs; scripts/guided_demo_e2e.py | uncommitted | D-071 |
| Guided accessibility | Keep useful mobile entry, readable aside, stage focus and short control names; verify keyboard/error states and real Aer retry | GuidedDemo.tsx/css; landing/Landing.tsx; landing.css; scripts/guided_accessibility_e2e.py | uncommitted | D-072 |
| Research interpretation | Derive equal yield and relative shot reduction from recorded totals, retain both denominators | qfault/api.py; ResearchEvidence.tsx; tests/test_research_summary.py | uncommitted | D-073 |
| Record lifecycle | Refresh history on entry, independently restore available records and prevent overwriting known stage IDs | web/src/main.tsx; GuidedDemo.tsx; guided browser suites | uncommitted | D-074 |
| Demonstration delivery | Source-bound real silent recording, normal-speed playback/decoded frame checks and actual-time captions; complete narration and setup/fallback guide | scripts/record_guided_demo.py; tests/test_demo_media.py; docs/judging-guide.md; docs/three-minute-demo.md | uncommitted | D-075 |
| Public delivery | Self-contained bounded outer archives, explicit public asset curation, existing-auth draft publication and independent public download/tag checks; extend CI regressions | scripts/release_delivery.py; scripts/prepare_release_assets.py; scripts/public_release.py; release tests; docs/public-release.md; README.md; .github/workflows/checks.yml | uncommitted | D-076 |

## 18. Guided external demonstration inputs and text fallback

Subsystem: Source-qualified presentation inputs.
Trigger / when: GET /api/guided-demo; explicit developer --write-inputs; text demonstration command.
What: Supply declared external reference/candidate/contracts, bounded request presets and unmeasured edit preview.
Why: Judges should execute the existing investigation path without manually constructing JSON.
Input / schema / provenance: examples/qrng-phase-demo.json version1; unchanged pinned QASMBench QRNG bytes, original reference circuit, separate controlled terminal Z; native qasm2-v1 ancestry.
Ordered calls with actual symbols and paths:
```text
scripts.guided_demo.build_inputs()      scripts/guided_demo.py; explicit exclusive developer output
 ├─ external_demo.example()            existing separate-reference contracts
 └─ from_qasm2()                       qfault/qasm_import.py; source representation and identity
api.guided_demo_inputs()               qfault/api.py; GET /api/guided-demo
 └─ demo_catalog()                     qfault/demo.py
     ├─ source byte digest / CustomCircuit identities / LabRequest and RecoveryRequest validation
     └─ interventions.generate()       structural candidate preview only
scripts.guided_demo.run()              same catalog -> lab/validate -> existing execution -> report
 └─ verify_export()                    independent exported-byte consistency check
```
Validation and trust boundary: No upload/Python execution, hidden answer or exact candidate analysis enters policies. Reference correctness/Qiskit semantics are assumptions. Catalog contains inputs, never successful live responses. Validation preview is contract feasibility, not recovery admission or promised detectability.
Output / schema / units: Catalog version1, source/circuit IDs, requests, seed, alpha, shot/evaluation ceilings and candidate exclusions/truncation; text run writes actual reports/summary/costs/elapsed seconds.
Persistence / identity / version: Fixture source controlled; generated input destination exclusive. Runtime outputs exclusive new directory; experiments use existing ArtifactStore identities.
Error / timeout / cancellation / recovery behavior: Invalid/missing input/source returns503 with no execution. Text fallback returns nonzero for unexpected outcomes, preserves actual outputs and never replaces them. Ordinary engine admission/busy/error semantics apply.
Verification commands and tests: tests/test_guided_demo.py; python -m scripts.guided_demo --out NEW_DIRECTORY against actual local Aer server.
Known limitations: Four-qubit product-state example demonstrates phase observability, not general repair performance. Fresh screening/freeze/confirmation remain one synchronous recovery operation; no pause/cancel promise.

## 19. Guided browser execution, restoration and failures

Subsystem: Judge-facing guided experience.
Trigger / when: Landing/overview/sidebar Guided demo opens /demo; explicit stage/scenario execution or replay.
What: Explain and execute the existing declared-contract investigation without JSON assembly.
Why: Judges need a coherent task, observable evidence, honest refusal and reviewable exports.
Input / schema / provenance: GET /api/guided-demo input catalog; actual API results; tab-scoped qfault-guided-demo-v1 IDs and stage state only.
Ordered calls with actual symbols and paths:
```text
Landing.enter('/demo') / Overview / Workbench sidebar
 └─ GuidedDemo()                         web/src/components/GuidedDemo.tsx; retained across navigation
     ├─ readGuide()/canVisit()            web/src/guided/session.ts; no fabricated completed records
     ├─ demoRequest('/api/lab/validate')  web/src/guided/api.ts; feasibility before execution
     ├─ ExecutionGate.run() -> execute()  synchronous admission -> existing investigation/recovery POST
     │   └─ writeGuide()                 returned experiment ID only; existing ArtifactStore owns results
     ├─ Outcome()/RecoveryEvidence()      display returned verdicts, costs, selection/fresh evidence
     ├─ verifyStored()                   GET /api/experiments/{id}/verification
     └─ replay()                         existing recovery replay route; {} or explicit new seed
```
Validation and trust boundary: A measured discrepancy and inspected limits precede recovery; uncertainty remains backend evidence. Stage explanations do not infer a competing diagnosis. Structural previews are not measured candidates. Verify-stored checks server bytes; downloaded bytes use the standalone verifier, not an embedded valid flag.
Output / schema / units: Six guided stages, three accessible scenarios, actual elapsed seconds, shots/executions, normalized loss intervals, selection digest and explicit contract scope. No percentage/cancel fiction.
Persistence / identity / version: ID-only version1 session state; restore actual records from server. Restart archives previous IDs locally and preserves server records. Guide remains mounted across navigation; no implicit execution on mount/refresh.
Restoration uses Promise.allSettled and matches each returned experiment_id to the saved ID; one missing record does not discard valid siblings. Known IDs block implicit reruns. Workbench refreshes /api/experiments on history/overview entry so newly completed guide records are visible without reloading the application.
Error / timeout / cancellation / recovery behavior: Busy409 and backend validation errors remain visible/retryable. Connection loss after submission records unknown completion; history inspection and acknowledgement precede a new guide. Missing/corrupt session or server record never supplies a fallback result. Storage failures warn that exports should be retained.
Verification commands and tests: node --test tests/guided-session.test.mjs (four pass); npm check/build; scripts.guided_demo_e2e against actual Aer backend, including independent downloaded report verification.
Known limitations: Backend progress is synchronous operation-level; no hard cancellation, external timestamp or unique cause claim. Browser acceptance remains a separate executed gate.

## 20. Genuine demonstration recording and playback

Subsystem: Public-safe media preparation.
Trigger / when: Explicit scripts.record_guided_demo --out after committing the assembled source.
What: Record the actual guide, retain controlled exports, verify full silent playback and caption timing.
Why: A judge needs an honest demonstrable fallback, not screenshots or narration claimed as footage.
Input / schema / provenance: Clean Git SHA; loopback API; actual guided UI, source-qualified input catalog and returned experiment IDs.
Ordered calls with actual symbols and paths:
```text
record()                         scripts/record_guided_demo.py; clean-source and loopback checks
 ├─ actual Playwright actions     existing guide -> Z -> phase -> recovery -> export/replay -> noise -> budget
 ├─ keep() -> verify_export()     returned IDs -> actual reports; distinct fresh execution sets checked
 └─ browser context close         flush genuine silent WebM; source/milestone/report metadata
playback()                        browser loads size/hash-checked WebM bytes as a seekable Blob
 ├─ seek/decode captures          source, phase, fresh, noise and budget frames for visual inspection
 ├─ complete normal-speed play    ended/error/frame/corruption/audio-track checks
 └─ captions()/stamp()            WebVTT from actual monotonic milestone offsets
```
Validation and trust boundary: No mocked outcomes, hidden desktop recording, Python upload or voiceover claim. Timed holds pace actual screens, never fabricate engine progress. Caption intervals ordered inside actual duration. Unsigned hashes bind bytes, not authenticity.
Output / schema / units: Silent WebM, captions, actual PNG frames, checked controlled reports, source-bound recording/playback JSON; seconds and actual shot/execution costs.
Persistence / identity / version: Exclusive new directory within artifacts; no overwrite of source or earlier captures. Media SHA and source commit recorded; public selection separate from runtime storage.
Error / timeout / cancellation / recovery behavior: Dirty source or unexpected live verdict fails without a fabricated successful recording. Browser errors/corrupt playback fail the media gate. No hard backend cancellation is claimed.
Verification commands and tests: tests/test_demo_media.py; actual record/playback command and manual decoded-frame inspection before publication.
Known limitations: Narration is supplied as text, footage silent. Pacing can exceed three minutes if actual execution is slow; report observed duration. No competition submission or hardware evidence.

D-069–D-074 implementation commit: db2989b45f48183fdce7ca2980717b8f009758ea.

## 21. Public release packages, curation and verified publication

Subsystem: Reviewable release delivery.
Trigger / when: Explicit operator bundle/verify/prepare/publish or unauthenticated public verification command after gates.
What: Make source, available evidence, controlled demonstration and verified media directly obtainable.
Why: Local artifact paths and an upload response are insufficient public delivery evidence.
Input / schema / provenance: Clean exact source SHA, existing package manifests, actually executed check record, source-bound recording/playback/controlled reports, explicit tag and asset names. No personal runtime sweep.
Ordered calls with actual symbols and paths:
```text
release_delivery.bundle_package()            scripts/release_delivery.py
 ├─ package_submission.verify_package()      unchanged existing member/digest/size checks
 └─ verify_release_archive()                 outer membership/CRC -> inner verify -> optional exclusive extraction
prepare_release_assets.prepare()             scripts/prepare_release_assets.py
 ├─ make_demo_archive()                      source/media/report IDs and request profile -> verify_export/audit_record
 ├─ build_package() or verified package reuse exact source/mode and tested bytes retained
 └─ public summary / docs / media / SHA256SUMS explicit filenames only; research values from frozen records
public_release.publish()                     scripts/public_release.py; --publish is explicit
 ├─ validate_assets()/credential()            reviewed membership/hashes, existing helper in memory only
 ├─ GitHub.request()                          owner/origin/main/source CI and unused release/tag preflight
 ├─ draft create -> explicit uploads          validated GitHub hosts; remote name/size/digest checks
 └─ publish -> verify_public()                new download directory; every remote asset obtained
     ├─ PublicRedirect()/download()           HTTPS GitHub-owned redirects, size/time bounds
     ├─ read_checksums()/validate_assets()    downloaded bytes, both package modes, source/media bindings
     └─ resolve_tag()                         actual remote tag commit, including bounded annotated-tag resolution
```
Validation and trust boundary: Only exactly named public assets can publish. No downloaded script execution, credentials in output, ignored data discovery or tag/release overwrite. Verify does not trust embedded success alone; hashes/actual reports/source bindings are checked. Media playback assertions remain observed evidence, not signatures.
Output / schema / units: Source/evidence outer ZIPs, controlled report ZIP, verification JSON, guide/narration, silent WebM/captions and SHA256SUMS; exact source SHA, byte counts, SHA-256, public URLs and downloaded verification record.
Persistence / identity / version: New artifact/output directories only. Tag names immutable; draft retained on upload failure. Package source may precede final documentation commit; never relabel archives. All new commits retain owner identity; release API does not rewrite source commits.
Observed public instance: v0.1.0 at b65dcb60fb216e802b2ff7d71a970169a6c059a2. Both package modes, five controlled exports, silent180.12s recording, captions, guide/narration, public check JSON and SHA256SUMS were downloaded and verified through verify_public(). Downloaded source/evidence packages were independently extracted, rebuilt and tested (22/28 representative tests). Public links/checksums and source CI are recorded in docs/judge-release-verification.md; later main documentation does not enter these immutable bytes.
Error / timeout / cancellation / recovery behavior: Missing/corrupt/oversized/unsafe members, failed gates, wrong owner/origin/source, pending CI, existing tag/release or download mismatch block success. Temporary extraction confined to newly created resolved parent. Network timeouts/guards do not claim hard cancellation. Partial downloads remain clearly partial, never verified.
Verification commands and tests: targeted release/media suites; complete final pytest/Node/frontend/Aer/browser; independent empty extraction/locked installation; actual public download/checksum/package/tag and final exact-SHA CI checks.
Known limitations: Checksums unsigned; GitHub availability/auth can block publication. No paid service/competition action, no hardware verification, no claim that later documentation is inside an earlier package.

## Changes in this session (media verification correction)

| Area | Change | Files | Commit | Decision |
|---|---|---|---|---|
| Playback | Decode exact bounded local bytes through a Blob so browser seeking works without a synthetic HTTP range server | scripts/record_guided_demo.py; decisions.md; flow.md; handoff.md | uncommitted | D-077 |

## Changes in this session (verified public delivery record)

| Area | Change | Files | Commit | Decision |
|---|---|---|---|---|
| Public delivery | Add verified release/download links, exact-source checksums and observed setup/media/archive/CI results; complete checklist and handoff | README.md; docs/judge-delivery-plan.md; docs/judge-release-verification.md; decisions.md; flow.md; handoff.md | uncommitted; Git history authoritative for this follow-up | D-078 |

Implementation identity follow-up: D-069–D-074/db2989b45f48183fdce7ca2980717b8f009758ea;
D-075–D-076/777f5de157415075fe031f8f045b6c950d6dad3a;
D-077/b65dcb60fb216e802b2ff7d71a970169a6c059a2. Prior decision/change rows remain
append-only historical write-time records; this entry identifies their commits.

## Changes in this session (live judging rehearsal)

| Area | Change | Files | Commit | Decision |
|---|---|---|---|---|
| Local operation | Record combined frontend/API startup and real guided preflight; reuse existing narration | decisions.md; flow.md; handoff.md | uncommitted operational record | D-079 |

## 22. Opt-in hosted session persistence

Subsystem: Vercel HTTP boundary and private session snapshots.
Trigger / when: api/index.py receives a hosted API request; local serve unchanged.
What / why: Preserve existing measured workflows across stateless function instances without exposing shared history or losing saved reports.
Input / schema / provenance: Existing JSON requests; configured deployment Host/Origin; signed HttpOnly browser capability; private Blob token and signing key from environment only.
Ordered calls with actual symbols and paths:
```text
RequestBodyLimit() api/index.py -> qfault/api.py; existing actual-byte validation
 └─ HostedApp.__call__() qfault/hosting.py; external host/origin and signed session
     ├─ POST /api/hosted-session initializes cookie before hosted Workbench mounts
     ├─ BlobState.read()/write() private HTTPv12 metadata/body ETag, conditional lease
     ├─ restore() fresh bounded scratch root, validated JSON paths only
     ├─ create_app(root) qfault/api.py; original API/science/storage/blind lifecycle
     └─ snapshot()/BlobState.write() conditional durable completion before response
```
Validation and trust boundary: No local files/runtime sweep. One private session snapshot; external host validated before internal loopback headers. Cookie cannot name another session without valid HMAC. Reads see last committed documents; concurrent mutations conflict. ETag mismatch rejects stale cached bodies/writers. No raw provider error/secrets returned.
Output / schema / units: Existing API evidence/IDs/counts/shot units unchanged; health adds hosting persistence/scope. Private state schema1 with original JSON strings, operations and lease expiry. All API responses no-store; cookie Secure/HttpOnly/SameSite.
Persistence / identity / version: Blob snapshots survive function replacement. Cookie30days,64mutations,1000JSON files/32MiB. Original investigation IDs/digests remain unchanged; no migration of old local records.
Error / timeout / cancellation / recovery behavior: Unavailable storage503, conflicting lease409, operation cap429, response/storage cap507. No success before durable commit. Failed lease release expires after310s with conditional fencing; no claim of in-flight cancellation. Vercel300s timeout may leave unknown completion; inspect history.
Verification commands and tests: tests/test_hosting.py; actual remote Blob CAS/ETag probe; deployed real-browser workflow and separate session isolation/context-restore/export/replay passed. No forced provider restart claim. Detailed source/commands and retained intermittent failures: docs/vercel-hosting.md.
Known limitations: Browser cookie capability, not account recovery; clearing/expiry loses access. Hobby quotas apply, no overage purchase. No distributed global rate-limit or hardware claim.
Origin-consistent reads use the documented private Blob cache=0 option (D-081); nonce/no-cache alone failed a real overwrite probe and were not treated as valid. HostedSession/HostedReportNotice in web/src/components/HostedSession.tsx gate only hosted builds, explain cookie access/limits, and leave local builds/hero unchanged (D-082). GET responses never replace a cookie; first nonbrowser mutation may initialize one. Real provider conditional overwrite/read/stale-writer rejection passed.

## Changes in this session (full Vercel hosting)

| Area | Change | Files | Commit | Decision |
|---|---|---|---|---|
| Hosting | Opt-in private session persistence and guarded ASGI deployment; preserve local engine | qfault/hosting.py; api/index.py; vercel.json; requirements.txt; .vercelignore; tests/test_hosting.py; root docs/plan | uncommitted | D-080 |
| Storage consistency | Origin-consistent cache=0 reads retain ETag checks; actual provider stale-writer rejection verified | qfault/hosting.py; tests/test_hosting.py; docs/vercel-hosting.md | uncommitted | D-081 |
| Hosted session UI | Initialize one capability before workbench effects; hosted-only privacy/connection notice, local/hero unchanged | HostedSession.tsx/css; App.tsx; main.tsx; qfault/hosting.py; tests/test_hosting.py | uncommitted | D-082 |

Hosted import/runtime correction: api/index.py creates an unused legacy API bootstrap
under tempfile before importing qfault.api, then its explicit async app() delegates to
RequestBodyLimit/HostedApp. Per-request private restore remains unchanged. Vercel's
nearest api/pyproject.toml/api/uv.lock pins Aer and all runtime closure artifacts to
the original requirements.lock versions/hashes; no old lock is changed. D-084 records
the actual read-only import failure and root-manifest selection evidence.

scripts.hosted_smoke.run() exercises public HTTPS health/Aer, private two-browser
history, cookie-context restoration, export verification/replay, Origin/body guards
and blind freeze/reveal before invoking guided_demo_e2e.run() for real measured UI.
No credentials/cookies are persisted in its public-safe output. A restored browser
context is explicitly not a forced provider process restart.

Hosted smoke failure path: __main__ in scripts/hosted_smoke.py catches an exception,
records only its bounded first error line in a new output folder, then exits1.
Request headers/cookies from multiline Playwright logs are omitted; no POST retry
or successful evidence is fabricated. Stable public URL uses source502a416,
production dpl_EZyabyX6wKrTcYA8o394twpPqXin, verified after asynchronous promotion.

| Area | Change | Files | Commit | Decision |
|---|---|---|---|---|
| Public verification | Record actual production browser/API scopes, exact deployed source, failed probes and safe diagnostic failure output | scripts/hosted_smoke.py; README.md; docs/vercel-hosting.md; docs/vercel-hosting-plan.md; root documents | uncommitted | D-086 |

Implementation identities: D-080–D-083 correspond to13c121db7e4b99bc6588203069ae17dfdec49d7a;
D-084–D-085 to502a416519c2bb1d99265991d4cf5e290e37ba94. Historical write-time rows
remain unchanged; this follow-up's own identity is authoritative in Git history.

## Changes in this session (hosted usability and reliability)

| Area | Change | Files | Commit | Decision |
|---|---|---|---|---|
| Baseline/design | Record current clean hosting source/CI, preserve original dirty main, and execute dependency-ordered improvements against existing engine | docs/hosted-usability-ledger.md; root records | uncommitted | D-087 |

Result presentation call order: GuidedDemo.Outcome/MeasuredRecovery/CustomLab →
ResultSummary → resultSummary(actual record). Claim tables → ClaimInterval →
displayInterval(raw,metric). No request, storage or decision is changed. TV[0,1]
and Pauli[-1,1] intersections are presentation only; raw evidence remains in details
and unchanged exports. Invalid/empty intersections explicitly say inconsistent.
| Results | Shared compact actual-record summary and physical display domains, complete raw evidence retained | presentation.ts; ResultSummary.tsx; guide/lab/recovery; Node tests | uncommitted | D-088 |

Navigation/history: MentalHero.onEnter → Landing.enter('/demo'); secondary
onWorkbench preserves '/workbench'. Workbench rail groups tasks, legacy URLs stay
accepted. demoRequest completed identity → notifyCompleted → HISTORY_EVENT →
Workbench.refreshHistory/historyLoader → GET /api/experiments. Request generation
prevents stale list replacement; no render-driven polling. Hosted flag only changes
location/limits wording; no hero rendering or backend decisions change.
| Wording/history | Guided primary action, grouped task links and completed-ID history invalidation | main.tsx; hero/Landing/Guide; guided/history.ts; tests/history-state.test.mjs | uncommitted | D-089 |

Hosted execution recovery: demoRequest → jsonRequest(class,deadline,operationId) →
HostedApp.__call__ → read_body/validate_direct/fingerprint → existing requests[ID]
lookup or conditional RUNNING lease write → original create_app route → capture
→ snapshot plus COMPLETED/FAILED commit → response. GET /api/operations/{ID} uses
operation_view and never increments quota; expired RUNNING becomes UNKNOWN in its
view. Matching completed POST materializes original files and loads the same
ArtifactStore identity. Failed durable save records UNKNOWN if conditional release
succeeds; otherwise stored RUNNING expires UNKNOWN. No duplicate POST retry.
Guide.Pending.operationId survives refresh; recover() reads status then the returned
result_path and restores actual IDs/results. Generic last operation ID is stored
without response-shaped evidence. Shared bootstrap/safe read retries only transient
errors at most3attempts,20s each,500/1000ms backoff; validation30s/execution280s,
no retries. Abort only ends browser waiting; timers/listeners clear in finally.
| Operation recovery | Durable fingerprint-bound status/results, explicit unknown lookup and bounded classified client requests | qfault/hosted_operations.py; hosting.py; guided requests/API/session; active components; tests | uncommitted | D-090 |
