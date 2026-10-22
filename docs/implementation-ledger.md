# QFault implementation and release ledger

## Baseline — 2026-10-22

- Workspace: `C:/Projects/QFF`; Windows 10.0.26200, x64; PowerShell 7.6.6.
- Starting branch: `research/external-validation`; HEAD `c4be11cded71f7625179f30c2b33b10c3b857d4a`.
- Origin: `https://github.com/PrathamKapoor/QFault.git`; fetched successfully. HEAD is 11 commits ahead / 0 behind `origin/main`. Current branch has no upstream.
- Initial porcelain status and stash list are empty. Linked recovery worktree and all existing branches are preserved. Local main is behind origin/main by six commits.
- Local identity already equals `PrathamKapoor <prathamkapoor027@gmail.com>`; no author/committer environment overrides were returned. Global configuration is unchanged. Git requires the existing per-command `safe.directory` exception because the repository belongs to the former sandbox account.
- No applicable AGENTS.md was found in the workspace or its ancestor directories. Root decisions, flow and handoff records were read in pages. Older handoff paragraphs contradict the latest dated records; they are historical, not current authorization.
- Node 24.19.0 / npm 12.0.2. CPython 3.13 is installed; a fresh isolated hashed installation is in progress in `.local/contract-release/python`.
- Frontend `npm --prefix web ci`, `run check`, `run build`: passed. npm audit reports one high-severity affected direct development dependency, Vite 8.2.2. This is a detected advisory, not evidence of exploitation. The existing lazy Three.js size warning remains.
- Initial pytest attempt raced the ongoing installer and failed `No module named pytest`; this is an incomplete-environment failure, not an application test result.

## Numbered execution checklist

1. Establish baseline and preserve records (G1): inspect refs, ignored artifacts, source paths, locks and existing evidence; record capability verification below. Acceptance: factual baseline and no lost work.
2. Complete fresh locked installation and baseline tests (G2). Acceptance: pip check, existing Python suite, frontend check/build, real Aer smoke; distinguish failures.
3. Repair evidence/package workflow (G6/G8): distinct source-only/full contracts, explicit availability ledger, reviewed snapshot without full Git history, archive verifier and extraction tests. Acceptance: missing evidence fails before a success manifest; source-only clearly discloses omissions; current external raw exports verify.
4. Add bounded native QuantumCircuit conversion and local CLI access (G3). Acceptance: independent Qiskit semantic tests, precise unsupported-operation errors, nonzero input once, import provenance retained through export/replay. No Python upload/eval/pickle route.
5. Verify scientific boundaries, recovery and recorded evaluations (G4/G5/G6). Preserve old protocols and digests; use a new current protocol when source changes require it. Acceptance: independent raw recount, isolation/budget tests, explicit negative findings.
6. Integrate current measured recovery positioning and verify real browser workflows (G7). Preserve hero/transition. Acceptance: desktop/mobile, phase discrepancy, recovery, abstention, blind freeze/reveal, export/history/replay against Aer.
7. Resolve scoped security/dependency findings (G9). Acceptance: current advisory review, tracked/staged/history secret scan with redacted findings, no runtime publication.
8. Finish complete flow records, demo, final checks and package extraction (G1–G9). Acceptance: exact commands/results recorded, outstanding gates explicit.
9. Publish safely to existing QFault destination only after gates pass (G10). Acceptance: owner author/committer, normal integration, remote SHA/sync and exact-SHA CI verified.

## Capability baseline

Statuses below describe inspection evidence before this session's verification.

| Capability | Status | Implementation evidence | Verification command | Limitation |
|---|---|---|---|---|
| Templates / CLI / API | IMPLEMENTED_NOT_VERIFIED | `workflow.investigate`, `cli.main`, `api.create_app` | `python -m pytest tests/test_investigation.py tests/test_storage_api.py -q` | Template exact-state privileges are separate from measured lab |
| JSON custom lab / contracts / feasibility | IMPLEMENTED_NOT_VERIFIED | `lab.LabRequest`, `investigate_lab`, `feasibility` | `python -m pytest tests/test_lab.py -q` | One computational input, 2–5 qubits, 32 subject gates |
| QASM import | IMPLEMENTED_NOT_VERIFIED | `qasm_import.import_qasm2` | `python -m pytest tests/test_qasm_import.py -q` | Static bounded QASM2, no local CLI path |
| Native QuantumCircuit import | ABSENT | No public converter in inspected package/CLI | New semantic tests required | Existing QASM adapter does not satisfy object conversion |
| Target witnesses | IMPLEMENTED_NOT_VERIFIED | `target.bounds`, `lab.run_witness_policy` | `python -m pytest tests/test_target.py tests/test_information_boundaries.py -q` | Uncalibrated noisy state claims abstain |
| Measured recovery | IMPLEMENTED_NOT_VERIFIED | `counterfactual.recover`, `verification_verdict`, `interventions.generate` | `python -m pytest tests/test_counterfactual.py -q` | Bounded one-edit search; cooperative timeout |
| Blind lifecycle | IMPLEMENTED_NOT_VERIFIED | `challenge.BlindChallenges`, API challenge routes | `python -m pytest tests/test_blind_challenge.py -q` | Local administrator can inspect private files |
| Storage / export / replay | IMPLEMENTED_NOT_VERIFIED | `storage.ArtifactStore`, `verify_export`, API replay routes | `python -m pytest tests/test_export_verification.py tests/test_artifact_corruption.py -q` | Unsigned consistency, no authenticated timestamp |
| ASGI byte cap | IMPLEMENTED_NOT_VERIFIED | `api.RequestBodyLimit` | `python -m pytest tests/test_final_api_adversarial.py -q` | 64 KiB API request cap; local trust model |
| External raw evaluation | IMPLEMENTED_NOT_VERIFIED | `benchmarks/external-holdout-v1`, `verify_external_results`, `reconcile_external_evidence` | `python -m scripts.verify_external_results benchmarks/external-holdout-v1/summary.json` | Repeated seeds/correlated mutants, nine holdout programs |
| Historical untouched recovery run | BLOCKED | `evaluate_counterfactual.run` retains exact source guard | `python -m scripts.evaluate_counterfactual --split holdout --out artifacts/contract-release/historical-check` | Current scientific sources postdate historical protocol; do not bypass guard |
| Submission package | PARTIAL | `scripts/package_submission.py:main` | `python -m scripts.package_submission --out artifacts/contract-release/package` | Requires ignored historical files, bundles full reachable history, omits newer families |
| Frontend build | IMPLEMENTED_AND_VERIFIED | `web/package-lock.json`, existing Vite scripts | `npm --prefix web ci`; `run check`; `run build` | Browser verification pending; development dependency advisory detected |

## Implementation item records

No functional changes yet. Subsequent entries use the owner's fixed item fields.

## Gates

All gates remain NOT_RUN except G1 baseline inspection (partial; final preservation check pending). No release readiness or publication is claimed.

## Verified implementation progress — 2026-10-23

### ID / subsystem: Input and native conversion (D-049/D-050)
Verified starting condition: Native converter absent; CLI rejected import-qasm; eight numerical coercion regressions and two edit coercions accepted invalid input.
What changed: Bounded object/QASM conversion, explicit transformations, retained import source, CLI lab/recovery, strict scalar validation.
Why: Developers can bring a real small circuit without silently accepting unsupported semantics or circular contracts.
How / actual files and symbols: qasm_import.from_qiskit/from_qasm2, lab.ImportProvenance/CustomCircuit, cli.main, Gate/Noise/contract/EditRestrictions fields.
When triggered / call order: Convert -> schema validate -> independent contract -> feasibility -> existing measured engine -> ArtifactStore.
Input -> output / identities / units: Native/QASM -> schema-1 circuit with provenance; original structural ID; radians and Qiskit wire order.
Failure and resource behavior: Indexed unsupported errors; 2–5 qubits/32 gates; no Python upload; measurements/barriers/decomposition opt-in as documented.
Backwards compatibility: Optional absent provenance omitted; legacy circuit IDs/serialized bytes retained; old protocols untouched.
Tests / exact command / actual result: native/QASM/recovery set 61 passed; native+CLI 11 passed; strict/lab/recovery/native set 100 passed. Native real API/Aer/browser import/phase/recovery/export passed, three mobile widths, no page errors.
Documentation / decision IDs: docs/native-import.md; flow.md; D-049/D-050/D-051.
Remaining limitation: Static built-in vocabulary and one declared input; conversion is not contract correctness or causal diagnosis.
Commit: uncommitted.

### ID / subsystem: Evidence packaging and historical recovery (D-048/D-056)
Verified starting condition: Package command unconditionally requires ignored historical files; source bundle contains reachable history. Authentic recovery summary locally found and byte-matched.
What changed: Clean source ZIP modes, bounded independent verifier, curated 310 original controlled exports, portable count-level recount.
Why: Fresh users need explicit public evidence, not a dependency on private owner runtime data.
How / actual files and symbols: package_submission.build_package/verify_package; verify_recovery_archive.verify; benchmarks/historical-recovery-v1.
When triggered / call order: Verify current external/history evidence -> read committed source -> temporary archive/manifest -> verify -> exclusive output rename.
Input -> output / identities / units: Exact source commit and study archives -> versioned ZIP/manifest, byte digests/sizes and explicit scope. Historical summary SHA256 8fb0e091016e5c9106c8ffb73afbcc5e41fe15e9517a566338b9cdfa6d10c957 unchanged.
Failure and resource behavior: Missing/corrupt/unsafe/dirty input refuses success; bounded ZIP members, expansion and paths; malformed deflate now returns invalid.
Backwards compatibility: Legacy collector retained; historical source/protocol/IDs/timestamps unchanged. Source-only explicitly omits report archives.
Tests / exact command / actual result: Package/legacy seven-test set passed; final five package tests passed including truncation/traversal/deflate. scripts.verify_recovery_archive independently verifies all 310; external verifier/reconciler verifies all 2,206 reports/2,232 attempted rows.
Documentation / decision IDs: docs/evidence-availability.md; D-048/D-056/D-058.
Remaining limitation: Other historical families remain summary-only; package extraction/install gate pending until reviewed commit exists.
Commit: uncommitted.

### ID / subsystem: Lifecycle, schema and local boundary (D-052/D-054/D-055/D-060)
Verified starting condition: Replay lacks parent/new-seed semantics; unknown rehashed schema passes; untrusted Host returns 200; CLI reads unbounded report file.
What changed: Parent-linked new records with deterministic/new-seed semantics, supported schema/version-kind guards, loopback/same-origin boundary, 16-MiB standalone report cap.
Why: Evidence meaning and local trust/resource claims must survive actual boundaries.
How / actual files and symbols: api.ReplayOptions/LocalRequestBoundary/run_lab/run_recovery/replay routes; storage._supported_investigation/verify_export; cli.main(verify-report).
When triggered / call order: Local authority/origin -> byte cap/JSON -> validated route -> shared lock/core -> saved record; verify checks supported versions and hashes.
Input -> output / identities / units: Requests/reports -> structured errors or new parent-linked investigation; seeds unsigned 32-bit integers.
Failure and resource behavior: 400 untrusted host, 403 cross-origin mutation, 413 body limit, 422 invalid schema/request; lock release on exceptions; cooperative backend timeouts remain explicitly soft.
Backwards compatibility: Omitted replay options work; old supported records untouched; explicit version fixtures preserve adversarial malformed-replay test intent.
Tests / exact command / actual result: Replay/adversarial 102 passed; schema/store/export 22 passed; local/adversarial/store 110 passed; final report-size/CLI/export nine passed. Red failures observed before fixes.
Documentation / decision IDs: flow.md; D-052/D-054/D-055/D-060.
Remaining limitation: No authenticated multiuser service, external timestamp or hard backend cancellation.
Commit: uncommitted.

### ID / subsystem: Product workflow and demonstration (D-053/D-057/D-061)
Verified starting condition: Landing foregrounds old template figures; reused metric colors are too pale on the actual white mobile overview.
What changed: Shared API-derived measured recovery figures, explicit denominators/cost/evidence, custom circuit action, scoped contrast correction, genuine native phase demo.
Why: Users/judges can understand current measured recovery and honest negative outcomes without reading source.
How / actual files and symbols: api.current_research; ResearchEvidence; Landing/Overview; judging_demo.run; native_demo_e2e.
When triggered / call order: Fetch recorded summary -> show current policies/scope -> validate circuit/contract -> actual Aer -> candidate search/fresh confirmation -> export.
Input -> output / identities / units: Actual frozen summary and backend evidence; no hardcoded success fallback. Original/selected identity, normalized tolerance units and actual shots preserved.
Failure and resource behavior: Unavailable research displays unavailable; no substituted result. Busy/error states use existing shell. No unsupported cancellation or fabricated progress.
Backwards compatibility: Hero/helix/handover/PixelSwap preserved; historical template entry/results retained and labelled.
Tests / exact command / actual result: npm check/build pass. Real native five-stage demo passes; browser native import/validation/phase/recovery/download passes at 1440 and 390/375/360, minimum tested new metric/caption white-surface contrast 8.076:1. Existing ten browser suites passed before the narrowly scoped contrast correction; final native suite verified that correction.
Documentation / decision IDs: docs/judging-guide.md, docs/native-import.md; D-053/D-057/D-061.
Remaining limitation: No newly narrated final video; real local captures exist. Cross-platform/browser/device coverage is not universal.
Commit: uncommitted.

### ID / subsystem: Scientific development and source-pinned verification (D-057/D-058/D-060)
Verified starting condition: Old recovery holdout refuses changed sources, correctly; dense targets remain unresolved in published studies.
What changed: Separate current-source 72-case deterministic replication protocol v4; preserved unexecuted v1/v2/v3 drafts; matched dense-target development study with complete raw counts.
Why: Preserve old protocols while verifying current sources, and investigate allocation limitations without tuning/relabeling holdout.
How / actual files and symbols: current_release_evaluation.freeze/run; dense_target_study.allocate/run; target bounds and independent recovery audit.
When triggered / call order: Freeze exact requests/source digests -> commit -> new outputs/recount; development allocation uses only declared target before measurement/evaluator truth.
Input -> output / identities / units: 72 observed prespecified requests -> new exports/projection comparison, explicitly not untouched evidence. Dense study: 16 cases, one architecture, matched shot ceilings/groups and alpha.
Failure and resource behavior: Protocol refuses uncommitted/changed sources; existing byte source guard retained. Errors/divergences stay in rows, never silently dropped.
Backwards compatibility: Every historical protocol/summary remains unchanged. No production policy/threshold update adopted.
Tests / exact command / actual result: Development allocation analytic test passed; 16/16 intervals cover oracle; uniform/coefficient both confirm 4/8. The target-only observed 3-qubit design feasibility lower 0.7823152869 is below threshold 0.8 at 32,768 shots, documenting a bound/budget limitation. Current v4 executed at 97710d834abeef93f0094b169a05d182f22c8434: 72/72 prescribed projections matched, zero errors, 2,272,256 shots, 1,127 executions; retained archive independently verified.
Documentation / decision IDs: docs/dense-target-development.md; D-057/D-058/D-060.
Remaining limitation: Development proxy improvement does not establish generalization or superiority; current-source replication is not a new holdout.
Commit: uncommitted.

### ID / subsystem: Dependency and publication safety (D-051/D-059)
Verified starting condition: npm reports high affected Vite dependency; pip-audit finds certifi advisory; no tracked env/database/private key paths returned.
What changed: Vite 8.2.4, certifi 2026.10.19 with official locks; scoped scanner false-positive classification; private-file ignore rules and no-provider setup documentation.
Why: Resolve detected advisories and keep public source/evidence separate from personal configuration/runtime.
How / actual files and symbols: npm lock generation/ci/audit, uv pip compile hashed lock, isolated pip-audit 2.10.0, official checksum-verified Gitleaks 8.30.1.
When triggered / call order: Install from locks -> scan -> review findings -> targeted update -> recheck -> reviewed staging before publication.
Input -> output / identities / units: Dependency closure and all 108 historical commits -> scoped reports; no credentials printed. api.py source-digest false positive is narrowly allowlisted by file plus exact digest-shaped match.
Failure and resource behavior: Real secret/advisory issue blocks release until resolved; unavailability is not a clean scan.
Backwards compatibility: Quantum dependencies preserved, no cloud/key/database added, global Git config unchanged.
Tests / exact command / actual result: npm audit zero after patch, pip-audit no known vulnerabilities after patch, pip check pass; Gitleaks history reviewed scan no leaks after classifying two occurrences of the same nonsecret source digest. Final staged/tree scan still pending.
Documentation / decision IDs: D-051/D-053/D-059; no rotation need found from examined evidence.
Remaining limitation: Pattern/advisory scans cannot guarantee absence of every secret or vulnerability.
Commit: uncommitted.
