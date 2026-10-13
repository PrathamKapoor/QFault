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


Submission transfer: scripts/package_submission.py:main requires a clean named branch, then collect_evidence reads the seven frozen summaries, confines raw references to artifacts, checks recorded digests and ArtifactStore.verify, and collects raw JSON evidence; authoritative summaries stay only in the source bundle to avoid tracked-file extraction conflicts. It creates/verifies the Git source bundle, archive writes each ZIP exclusively and checks CRC, then main writes the SHA256/source-commit manifest. Optional repeated --demo directories add only JSON/PNG/WebM material. No installation, cloud upload or scientific decision is performed by this path. docs/transfer.md describes restoring the same committed source and raw evidence on a supported external computer.

Optional browser recording: scripts/browser_e2e.py:main passes --record-video to the existing Playwright context, retains all real interaction/assertions, closes the context to finalize video, and records the actual path/size in summary.json. The silent raw clip is separate from final human narration. ArtifactStore export verification and the CLI tamper control are unchanged.

| Session change | Actual paths | Decisions | Commit |
|---|---|---|---|
| Verified source/evidence transfer and normal-install handoff | scripts/package_submission.py; tests/test_transfer.py; docs/transfer.md; README.md | D-025 | Commit containing this entry |
| Genuine optional browser recording and organizer/narration guide | scripts/browser_e2e.py; docs/demo.md; docs/organizer-confirmations.md; benchmarks/submission-verification.json | D-026 | Commit containing this entry |


Final delivery uses the unchanged investigate/API and browser workflow described above. Genuine judging footage records Bell clean/remove/readout/low-shot phase interactions, the existing Recovery/Report tabs and the frozen final comparison. docs/video-timeline.json and docs/video.md are editing/voiceover instructions, not diagnostic inputs. No narration is generated. Normal-speed Chromium playback checks the real video from beginning to end; package_submission.main binds the final committed source and referenced real media/evidence archives. No installation, external publication or eligibility decision is implied.

| Session change | Actual paths | Decisions | Commit |
|---|---|---|---|
| Final delivery verification, genuine judging picture cut, editable narration and eligibility boundaries | README.md; docs/video.md; docs/video-timeline.json; docs/demo.md; docs/organizer-confirmations.md; docs/transfer.md; benchmarks/final-delivery-verification.json; handoff.md | D-028 | Commit containing this entry |

Publication audit (D-029) leaves the quantum runtime unchanged. scripts/http_release_smoke.py now states that browser coverage is outside its scope; scripts/browser_e2e.py remains the actual browser verifier. docs/publication-audit.md distinguishes connector identity/permission from verified Git transport, and local evidence/media from public clone content. No GitHub API operation recreates historical commits.

## Cinematic frontend lifecycle (D-030)

`web/src/entry.tsx` mounts `App` and the existing/base plus light-workbench CSS. `App` reads the URL hash and listens for hashchange. `/` mounts `Landing`; any workspace route lazy-loads the single `Workbench` exported from main.tsx. After first use that instance remains hidden on home, retaining drafts without keeping decorative renderers alive. Saved experiment hash routes refresh through the unchanged FastAPI `/` static mount.

`Landing` initializes from `useReducedMotion` and sessionStorage. A first visit runs hyperspeed → techtext → hero at bounded 650ms intervals. Skip/Escape goes directly to hero; returning/reduced-motion users start there. Sculpture code is fetched during entry without creating its GL context. Hyperspeed is unmounted/disposed before TechText; TechText's canvas loop is removed before hero.

`Sculpture` calls `createQuantumSculpture` in quantumSculpture.ts. Four original asymmetric diagonal open sweeps use two variable-width ribbons and two secondary paths, plus a thin violet filament; outward triangle winding, joined seam normals and UV-aligned brushed physical materials shape the surface. The bounds-based camera fits their silhouette. A procedural strip-light scene becomes a PMREM reflection environment. ResizeObserver adjusts framing; IntersectionObserver and document visibility pause drawing; pointer input causes restrained parallax. The host's reduced-motion view renders on demand. Destroy disconnects observers/listeners and disposes geometry, materials, PMREM and renderer/context. Failed WebGL creation/context loss selects the explicitly static SVG fallback. A first-frame data marker supports genuine capture checks.

Every supported hero mounts MoltenMetal with graphite/violet colors initialized before its first draw. Mobile, reduced-motion and lower-core views use a static shader frame; desktop animation is throttled and pauses offscreen/when hidden. Its capability canvas is reused, and context/geometry/program are released on removal. `Landing.enter` locks repeated clicks, records the destination, resets scroll to the opening stage, freezes sculpture, removes atmosphere and applies leftward reframe/access composition. After 470ms it mounts PixelSwap, whose two inputs contain only static colors/branding. The actual app is never duplicated. `finish` navigates after completion or the safety timer; reduced motion navigates immediately. Workbench route effects focus `#workspace-heading` and reset scroll. Back/forward do not force another introduction.

`Workbench` retains the existing request/API workflow: circuits, history and frozen benchmark/evaluation populate overview; circuit selection fetches the actual contract. `run` POSTs the unchanged RunRequest to `/api/experiments`, then refreshes actual history and integrity. `load` clears stale output and uses loadSequence guards so a late previous response cannot replace a newer saved selection. Shared alerts expose API failures on overview/history as well as investigation. Circuit.tsx draws the actual submitted gates and Z-readout wires; complementary-basis evidence remains separately labelled. Existing evidence/recovery/report/integrity/review actions still use real backend responses and downloads. No diagnostic engine or benchmark method changes.

| Session change | Actual paths | Decisions | Commit |
|---|---|---|---|
| Exact-destination publication audit, normal setup wording, relative-link repair and honest HTTP scope | README.md; docs/publication-audit.md; docs/local-development.md; docs/browser-verification.md; docs/demo.md; docs/video.md; docs/transfer.md; scripts/http_release_smoke.py; benchmarks/publication-verification.json; handoff.md | D-029 | Commit containing this entry |


## Landing visual recovery (D-031)

Landing.tsx renders a separate left copy/brand column and right hero-composition stage, followed by platform, capabilities, frozen scientific evidence and final entry sections. Landing.scrollTo prevents default anchor hash mutation before scrollIntoView, preserving App routing. Header, hero, benchmarks and footer entry all use the existing enter/finish choreography; only static surfaces are passed to PixelSwap. landing.css scopes the expanded public page without changing workbench.css. Responsive styles move copy/actions before the framed sculpture. Sculpture.tsx retains the fallback/cleanup boundary with an original open-path SVG. No public-section metrics feed diagnosis; all workbench actions retain the existing API flow above. Reproduction, actual visual iterations and test commands are in docs/landing-recovery.md.


## Shared hero depth composition (D-032; supersedes D-031 hero placement)

Landing.tsx places hero-eyebrow and identical per-letter word-back/word-front planes inside hero-composition, with Sculpture between the planes. Selected letters in the front plane retain their boxes while other glyphs use visibility:hidden. Both decorative planes are aria-hidden; the existing single QFAULT heading remains semantic. landing-copy contains the unchanged requested headline, corrected supporting sentence, Enter Workbench/Explore the Research and genuine simulator label below this shared stage. Decorative art captions and duplicated hero footer labels are removed. Below-hero public sections and all workbench components remain unchanged.

quantumSculpture.sweep constructs tapered elliptical ribbon profiles along distinct diagonal CatmullRom paths, applies controlled cross-section rotation, winds faces outward and joins normal values at the profile seam. createQuantumSculpture adds deterministic longitudinal brushing through roughness/bump maps and physical-material anisotropy, uses a neutral strip/fill studio with dim accent cards, and preserves the original pause/disposal API. Sculpture.tsx supplies an original diagonal static SVG on absent/lost WebGL. MoltenMetal's existing lifecycle is unchanged; hero props increase spatial detail and use subdued graphite/violet colors to avoid the previous large streaks. Enter/finish and PixelSwap timers/content remain the existing transition; hero CSS alone adapts the leftward handoff. Actual API flows above are unchanged.

## Double-spiral hero composition (D-033; supersedes D-032 trajectories)

quantumSculpture.spiral samples opposite helical phases along a 6.1-unit rising axis; its companion curves follow the same flow at a slightly wider radius. sweep retains tapered flattened profiles, outward triangles and seamless normals. createQuantumSculpture preserves quality tiers, fitted camera, studio baking, texture disposal, observer/visibility pauses and context-loss handling. The tall canvas crosses the shared word planes centrally; Landing.tsx keeps A/T in the foreground. landing-copy now groups headline, description and actions below-left. Sculpture.tsx matches this silhouette in the original SVG fallback. MoltenMetal props and effect code, enter/finish, PixelSwap, workbench mounting and API flows remain unchanged. Details: docs/helix-hero.md.


## Blind and measurement-only development flow (2026-10-13)

Workbench /#/challenge mounts BlindChallenge inside the existing shell; /#/challenges/<id> reloads its saved public state. Existing landing, Pixel Swap and ordinary investigation routes are preserved. POST /api/challenges validates ChallengeRequest, chooses from eligible_pool with a server-held seed and calls workflow.observe for baseline and observed counts. BlindChallenges.start writes private setup and public observed records. diagnose reuses initial_records through workflow.investigate; its public projection excludes hidden circuit, seeds, noise and evaluator truth. Measurement-only dispatch gives MeasurementOnlyAnalyst a MeasurementPort with finite-shot complementary/readout actions. Simulator-assisted dispatch retains DiagnosticAccess and RecoveryPlanner.

POST diagnose -> DIAGNOSED; POST freeze -> FROZEN with observation/prediction bindings; POST reveal requires FROZEN and independently verifies private artifacts before calling evaluator_truth. Reveal appends truth and replay configuration. Replay creates a new explicitly labelled replay; ordinary history never includes private challenge experiments. Export before reveal is public-only; after reveal it additionally contains the verified private investigation. verify_export dispatches to verify_challenge_export and checks nested prediction consistency. These are unsigned recorded-order checks, not external timestamp/authenticity proofs.

The prespecified scripts.measurement_holdout uses the same investigate path with controlled prepared scenarios, freezes prediction digests before evaluator classification, saves all raw artifacts and retains errors/abstentions. It never overwrites old benchmark files.


Final transport details: ChallengeConflict carries only explicit safe state errors; backend RuntimeError messages become generic 422 responses. Read calls use challenge_action(wait=True) and mutation calls retain nonblocking admission. Public diagnosed documents additionally include measurement_view projections of diagnostic/verification executions, allowing counts to reconcile the full shot ledger before reveal. Old documents restore with an empty optional diagnostic_measurements list; frozen files are never retroactively rewritten. The measurement_holdout result is now committed as a separate benchmark artifact; package_submission.collect_evidence validates its manifest_sha256 references as well as historical manifests.


## Custom circuit laboratory flow (D036)

`POST /api/lab/investigations` (64 KiB body limit via `bounded`) validates `LabRequest` (`CustomCircuit`, `Contract` union, `check_pair`). `feasibility` -> `plan` builds claims and qubit-wise-commuting groups. `investigate_lab` creates an `ExecutionBudget` and a `_Port` that privately holds the subject and simulated environment; `run_policy` receives only the port, repeatedly selects a group, calls `_Port.measure` (budget `reserve` -> `measurement_circuit` -> `execute` -> `EvidenceCollector.collect`), updates `_State` intervals at the `alpha_slot` level and appends an action-ledger entry, then stops with a coded reason. If a claim is violated, one reserved readout-control batch runs. In simulator_assisted mode only, `exact_expectations` runs after sampling and is listed in `privileged_operations`. Results persist through `ArtifactStore.save` (`ground_truth: null`) and are retrieved, verified and exported through the existing `/api/experiments/{id}` routes. `POST /api/lab/investigations/{id}/replay` re-runs the stored request. Errors: pydantic 422 (nothing executed or stored); an execution failure writes a `failures/` artifact and returns a generic 422.


## Target-state witness flow (D037)

`LabRequest` validates `TargetStateContract` (`check_pair` matches 2^n; `default_policy` selects `adaptive_witness`). `feasibility` -> `target_feasibility` builds `catalog(amplitudes)` (cached, target-only), groups via `plan` -> `group_paulis`, and the best-case affordable lower bound. `investigate_lab` routes to `run_witness_policy(contract, contract_id, port, request)`: each step computes `bounds` -> `decide`; stops on decision / looks / budget; otherwise selects a group (`marginal_gains` for `adaptive_witness`, fixed orders or seeded random otherwise), calls `_Port.measure`, updates per-term `parity_expectation` and `hoeffding_radius` at `alpha_slot(len(terms), K, alpha)`, and appends a ledger entry with derived expectations and bounds. A violation triggers the reserved readout control. In simulator_assisted mode only, `exact_expectations` (ideal fidelity) and `noisy_density` (gate-noise state fidelity) fill `target_evidence.exact`. The result adds `target_evidence` and persists through `ArtifactStore`; replay/export/verification reuse the existing routes.


## Counterfactual measured recovery (D038)

CustomLab -> MeasuredRecovery -> POST /api/lab/recoveries validates RecoveryRequest. interventions.generate records bounded one-edit proposals. ContractObservation builds fixed grouped schedules via lab.plan and target.catalog. recover reserves fresh original/candidate shots, executes through lab._Port and ExecutionBudget, checks original discrepancy/readout control, then screens admissible candidates. rank preserves overlapping loss intervals; selection binds evidence before fresh sampling. verification_verdict requires contract satisfaction and fresh supported improvement. ArtifactStore persists schema 3; ordinary experiment retrieval/report/hash verification and the new recovery replay endpoint restore evidence. History dispatch recognizes counterfactual_recovery. No edits apply automatically; no blind evaluator input is accepted.


## Counterfactual recovery freeze and evaluation (D039)

`configs/counterfactual-protocol.json` fixes the case digest, policy set, seeds, execution backend, budgets, source hashes and metrics. Commit 5034972 is the evaluator source revision. `scripts.evaluate_counterfactual --split holdout` refuses changed sources, cases or uncommitted files; it executed 62 cases × 5 policies on Aer, persisted each investigation through `ArtifactStore`, verified exported manifests, then recorded every row and per-variant costs. All 310 runs completed without errors; no holdout tuning followed. The result in `artifacts/recovery-holdout/summary.json` shows matched 16/62 conservative and point repairs; conservative used fewer resources with more abstention. The conservative plausible-locus set covered the designated location in 14/14 logical and 2/2 intentionally ambiguous cases, without establishing a unique cause. No causal fault identity is asserted.
