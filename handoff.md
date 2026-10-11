# QFAULT engineering handoff

## 1. Current Phase

Working local quantum investigation and recovery vertical slice; release verification completed for the available runtime. Overall directive is PARTIALLY COMPLETE. Aer, fresh isolated installation and browser verification prevent claiming every submission gate passed.

## 2. Work Completed

Inspected environment and donor implementations read-only. Built native Qiskit Bell/GHZ/QFT, analytic contracts, valid mutations, explicit channel-noise fallback, finite-shot evidence, bounded diagnosis with abstention, one-edit recovery and independent verification. Added canonical artifacts, integrity checking, review, CLI, localhost API and React workbench. Executed three 306-investigation benchmark runs, multiple demos and real HTTP rehearsal. Fixed all independently reviewed artifact issues; full suite and frontend checks pass.

## 3. Files Changed

New independent repository only: qfault/*.py; tests/*.py; web/index.html, web/package.json, web/src/*; scripts/*; pyproject.toml; requirements-tested.txt; README.md; LICENSE; THIRD_PARTY_NOTICES.md; .gitignore; decisions.md; flow.md; handoff.md; docs/*; benchmarks/*.json. Generated artifacts and web/dist are ignored. No donor source was written by this work.

## 4. Current Architecture / State

CLI/API → RunRequest → investigate → native Qiskit execution → EvidenceCollector → DiagnosticAnalyst/DiagnosticAccess → optional RecoveryPlanner → IndependentVerifier → pending human review → ArtifactStore. See flow.md for real function order. Localhost API serves built React assets and actual benchmark summaries. File storage intentionally replaces unnecessary database infrastructure. Review identity is self-declared; no automatic circuit changes.

## 5. Decisions Made

D-001–012 in decisions.md cover environment bridge, fixed-input contracts, Aer fallback, truth isolation, bounded repair, file persistence, UI/API dependencies, negative benchmark, malformed-manifest fix, provenance/cost records, honest supervisor state and review-membership integrity.

## 6. Requirements and Constraints

Local only; no push/deployment/cloud/paid API/hardware. Repository-local author and committer must remain PrathamKapoor <prathamkapoor027@gmail.com>. Preserve donor/user changes and attribution. Do not fabricate results or claim general unitary correctness/quantum advantage. Maintain decisions/flow/handoff, no artificial stage directories or paper/.tex files. No arbitrary uploaded Python.

## 7. Testing and Verification

Verified PowerShell launcher: powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 pytest tests -q -p no:cacheprovider → 62 passed, one Starlette/httpx deprecation warning (9.92 seconds). TypeScript check and Vite production build passed with commands in README. Real HTTP health, circuits, benchmark/download, missing-gate investigation, verification and report passed; benchmarks/http-smoke.json records responses. CLI commands circuits, contract, run, inspect, analyze, recovery, verify, export, review, verify-repair, demo and benchmark executed successfully. Budget abstention, invalid repair rejection, observationally equivalent faults, noise bias and label exclusion tested.

benchmarks/results.json records final release run at artifacts/release-benchmark: 300 policy cases plus six recovery trials. Scientific metrics match earlier benchmark and reproduction runs. Evidence 47/75, fixed 66/75, random 23/75, threshold 47/75. No false diagnosis among 12 correct cases per policy (Wilson upper 24.2%); six selected repairs verified (Wilson 61.0–100%). Fixed wins accuracy; threshold ties evidence with fewer shots. Raw records remain local and are regenerable; committed summary contains row-level IDs/paths and manifest digests. Demo tamper check was true/false/true. Independent static review found two artifact flaws; seven failing regression cases were observed then passed after fixes. Browser tests and fresh install were not run. See benchmarks/verification.json.

## 8. Known Issues / Risks

Aer cp311 binary cannot load in accessible cp313 runtime. Explicit Qiskit BasicSimulator/DensityMatrix/Kraus fallback works. Machine-specific read-only dependency bridge is not an isolated portable environment. Browser runtime lists no browsers, so interactive/visual QA remains unverified. No npm lockfile or fresh package-install rehearsal. State diagnostics use privileged ideal simulation; fixed-input contract is not full unitary equivalence. Evidence-triggered policy misses phase-only/distribution-preserving defects; some noise is invisible. Small repeated-circuit corpus limits statistics. Repair search is incomplete. File persistence is not a multi-file transaction; failures may leave partial directories. Unsigned manifests can be replaced/rolled back; reviewers are unauthenticated. Historical local reviews created before D-012 fail membership verification instead of being silently migrated.

## 9. Unfinished Work

Compatible isolated Python/Aer setup; portable fresh-install rehearsal; browser journey/visual verification; frontend dependency lockfile. Temporal drift, mitigation, QCEC, ML-DSA, hardware execution and advanced policies are unavailable. Unique gate localization is not established; a repair edit need not identify the injected cause. Do not advertise these as implemented.

## 10. Next Subphase

First establish an isolated compatible runtime and fresh-install demo, then run connected-browser checks through selection, execution, failure, export and review. Next investigate a measurement-based phase-sensitive diagnostic policy on a frozen unseen corpus with matched costs; preserve baseline wins.

## 11. Critical Context

Verified Windows 10.0.26200, Python 3.13.15 (LibreOffice), Qiskit 2.3.1, Node 24.19.0, npm 11.17.0, Git 2.55.0.windows.2; versions and donor revisions in docs/environment.json. No Docker/services required. Normal exec setup failed; Node child-process orchestration enabled local work without downloading executables. scripts/local_bootstrap.py reads packages from C:/Projects/Quantum_Simulator/.venv/Lib/site-packages and C:/study/projects/quanum_ml/.python_lib and disables bytecode writes. Build tools read donor node_modules only. Per-command safe.directory overrides avoid global Git changes.

All donor HEADs remained unchanged; Quantumattack gained two additional dirty file paths during the session (logistic.py and test_statistics.py). QFAULT issued no donor writes and did not revert that concurrent work; other donor status snapshots matched. See docs/source-preservation.json. No direct donor code copied; conceptual adaptations and licenses in docs/reuse-inventory.md and THIRD_PARTY_NOTICES.md.

## 12. Agent Instructions

Read this file, decisions.md and flow.md before further work. Inspect existing artifacts before editing; never overwrite benchmark directories. Run the recorded test/build checks after code changes. Keep predictions frozen before evaluator truth; never expose labels to analyst features. Record failed experiments and negative results. Review file membership is bound in an unsigned manifest; do not claim signing or authenticated approval. Commit locally with the required identity only; no remote operations. Preserve raw artifacts, attribution and all user changes. Update these continuity files with actual evidence.
