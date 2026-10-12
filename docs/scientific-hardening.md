# Scientific hardening and submission boundary

## Snapshot and eligibility

Local main started clean at f36665616c2aee95a7b82e764adcf290b9e05468. Public QFault main was checked with git ls-remote at ea71bd981ee0d6a394b4d26e4a904c92bc4f5ed3. Eight frontend commits are local-only. Local snapshot tags preserve both commits; new work is on hardening/blind-measurement. Main is not advanced. No submitted commit has been identified and no submission or push is authorized.

On 2026-10-13 the [official event page](https://qiskitfallfestmpstme.in/) still lists October 12 Stage 1 against a provisional October 22 prompt release/October 23 deadline, teams of two to four, Indian college student eligibility, and Pratham Kapoor as a workshop lead. The linked Unstop page did not supply readable rules. Organizer confirmation remains required for the controlling deadline, prior submission SHA, permitted further development, workshop-lead eligibility, pre-existing-code policy, team roster and deliverables. No controlling interpretation or eligibility claim is made. The user subsequently clarified that this is continued project development, and explicitly dropped eligibility and presentation work. Those questions are outside the current task; no competition eligibility, submission or publication claim is made. No organizer message was sent.

## Minimal design

Keep ordinary investigations backward-compatible. A measurement-only analyst receives an analytical target contract, allowlisted counts and a port exposing only finite-shot complementary-basis/calibration actions. The executor owns the hidden implementation and noise; the analyst has no candidate-state or repair-search capability. Supported discrepancy is distinct from causal attribution. Readout controls can support noise consistency; clean calibration does not rule out gate noise. Otherwise a detected failure remains ambiguous. Recovery is explicitly unavailable in this mode.

Blind challenges persist separate private setup/experiment records and participant-facing observation, diagnosis, freeze and reveal documents. Start performs actual baseline/observation execution. Diagnose reuses those measurements and the existing workflow. Pre-reveal projections exclude scenario, selection seed, noise parameters, actual hidden circuit, circuit-derived identifiers and raw evaluator reports. Declared target diagrams are labelled as targets. A persisted prediction digest must precede reveal; exports/history obey the same boundary. This is a controlled local interface, not secrecy from a server administrator or cryptographic prevention of inference from observed behavior.

The measurement holdout protocol is committed before implementation or execution. New seeds and noise/angle settings probe observability and attribution limits on existing templates. All failures and abstentions remain, measurement and privileged policies are reported separately, and only descriptive paired analysis is planned. Published benchmarks remain frozen. No custom circuits, new agents, cloud services, databases or visual redesign are planned.

## Reproducibility

Standard CPython 3.13 was discovered through py -0p. A new isolated .local/repro-python environment installs .[aer,dev,browser] from pyproject.toml using pip; this is independent of the historical LibreOffice bridge. The existing genuine web/package-lock.json is validated by npm and a separate npm ci in an archived source checkout under .local/repro-source. Actual command outcomes are added after verification; no bridge execution is called an independent install. CI will be added only after those checks pass, and no passing GitHub badge will be invented.


## API contract

POST /api/challenges accepts family, n_qubits, pool (core/extended), diagnostic_mode, measurement_plan, shots, max_shots, max_evaluations, backend and recover. Defaults are measurement_only, complementary, Aer, 2048 shots, 12000-shot/384-evaluation ceilings, no recovery. Optional seed supports reproducible rehearsal; the UI requests a private server seed. Supplying a known seed permits deterministic inference and is not a secrecy guarantee. Core pool: clean/remove/phase/readout/gate; extended adds replace/rewire/mixed and QFT-only angle.

GET /api/challenges returns safe history; GET /api/challenges/<id> restores safe state. POST /diagnose is allowed only from OBSERVED. POST /freeze requires DIAGNOSED and is idempotent after freezing. POST /reveal requires FROZEN and is idempotent after reveal. POST /replay requires REVEALED and starts a new explicitly labelled replay. GET /report and /verification use the same state boundary. Invalid input returns 422; illegal state transitions/duplicate mutations return 409; absent records return 404. Read requests serialize behind mutations to avoid partial snapshots; this also fixes competing history/view reads. Ordinary /api/experiments routes remain separate.

Pre-reveal records omit scenario, mutation, hidden circuit, noise configuration, seed, input/circuit digests and raw private report. They include the declared target, real counts, scientific derived evidence, explicitly labelled privileged insight when enabled, costs, and hashes. Derived evidence or a selected repair can legitimately suggest the hidden scenario; the interface withholds injected metadata rather than making evidence uninformative. No diagnosis reads evaluator truth. Tests patch evaluator classification to fail before freeze and patch exact faulty-state/density and recovery access to fail in measurement-only mode.

Only the public diagnosis/cost/observation chain is freeze-bound; private prediction_digest separately binds its diagnosis/recovery. Revealed nested exports must match both. SHA256 verifies consistency and recorded ordering relative to supplied manifests; administrators can rewrite files and hashes. It is not authentication, an external timestamp, or a proof of scientific correctness.

## Verification before holdout

119 tests, independent pip check, nine real Aer/reference conformance combinations, deterministic Aer Bell smoke, CLI Aer healthy/fault/phase/recovery/noise/abstention and tamper/restore checks, TypeScript/build, seven existing Aer browser workflows and both new blind browser capability flows pass. New browser evidence is under artifacts/hardening-blind-browser-final; desktop configuration/reveal and mobile form images were visually inspected. CI configuration is present but remote execution is unverified. Existing browser scripts contain a historical bridge limitation string; this invocation actually used .local/repro-python and reports its own installed Playwright version. Browser assets were already cached locally; this is not a fresh Chromium download claim.


## Executed holdout and final boundaries

The first and only untouched run used frozen implementation f7a832be853faa263280cc6fe08fddd2becc275f after protocol commit 3dbf423e9d9b133e57738e7ee65236a5a75aa744. All 208 runs completed. Measurement Z and complementary strict category scores are both 16/52; complementary detects more discrepancies (30/52 versus 14/52) and appropriately abstains more (20/52 versus 8/52). Simulator fixed/phase score 32/52 and 38/52. The stronger witness costs 40% more shots. See measurement-holdout-findings.md for all matrices, per-class recall, costs, failures and descriptive paired outcomes. No diagnostic/recovery tuning followed these results.

Final boundary fixes redact executor errors (only ChallengeConflict supplies safe 409 text), bind transferred holdout manifest_sha256 references, and project all raw additional measurement counts through measurement_view. They change transport/evidence access, not diagnostic decisions. Participant counts can now reconcile every charged shot before reveal; actual hidden circuits, seeds and noise metadata remain private. Existing earlier challenge documents lacking the additional count projection still restore, without rewriting their frozen hashes.

Simulator-assisted challenges use the existing phase policy; ordinary investigations retain their existing defaults. Blind runtime_seconds measures the resumed investigate call and excludes the earlier observe call; shot/execution accounting includes both. The normal, non-resumed holdout run-time measurements include initial execution. No exact GPU/FPS or hardware throughput claim is made.

The app is a local, single-worker laboratory. In-process locking supplies coherent reads and rejects duplicate mutations; it is not a distributed transaction mechanism. Interrupted writes fail closed under manifest checks and may require manual record inspection. No authenticated secrecy, external time anchor, hardware execution, measured recovery selection, custom-circuit diagnosis or unseen-architecture generalization is implemented.

The user explicitly removed eligibility/presentation work: no new submission, judging video or narration was produced. Existing CLI demo scripts were used only as real regression checks. No push occurred.


## Changed files

- `.github/workflows/checks.yml`
- `.gitignore`
- `README.md`
- `benchmarks/development-hardening-verification.json`
- `benchmarks/measurement-boundary-holdout-20261013.json`
- `benchmarks/measurement-holdout-protocol.json`
- `decisions.md`
- `docs/measurement-holdout-findings.md`
- `docs/publication-audit.md`
- `docs/release-gates.md`
- `docs/scientific-hardening.md`
- `flow.md`
- `handoff.md`
- `qfault/api.py`
- `qfault/challenge.py`
- `qfault/cli.py`
- `qfault/measurement.py`
- `qfault/storage.py`
- `qfault/workflow.py`
- `scripts/aer_smoke.py`
- `scripts/blind_challenge_e2e.py`
- `scripts/measurement_holdout.py`
- `scripts/package_submission.py`
- `tests/test_blind_challenge.py`
- `tests/test_holdout_protocol.py`
- `tests/test_measurement_only.py`
- `tests/test_transfer.py`
- `web/src/challenge.css`
- `web/src/components/BlindChallenge.tsx`
- `web/src/components/landing/Landing.tsx`
- `web/src/main.tsx`

## Executed command index

All Python commands below ran with .local/repro-python/Scripts/python.exe, a normal isolated CPython installation, not scripts/local.ps1.

- python -m pip install -e ".[aer,dev,browser]"; python -m pip check
- python -m pytest tests -q -p no:cacheprovider (122 passed)
- python -m scripts.aer_smoke
- python -m scripts.compare_backends --out artifacts/hardening-conformance-20261013
- python -m scripts.submission_demo --out artifacts/hardening-cli-regression --backend aer (existing scientific regression only)
- python -m qfault benchmark --out artifacts/hardening-original-reproduction
- python -m qfault evaluate --split final --out artifacts/hardening-final-reproduction
- python -m scripts.evaluate_recovery --out artifacts/hardening-recovery-reproduction
- python -m scripts.measurement_holdout --out artifacts/measurement-boundary-holdout-20261013
- npm.cmd --prefix .local/hardening-source/web ci; run check; run build (independent archived implementation)
- npm.cmd --prefix web run check; npm.cmd --prefix web run build (final source)
- python -m scripts.browser_e2e --out artifacts/hardening-browser-existing
- python -m scripts.blind_challenge_e2e --out artifacts/hardening-blind-browser-final-ledger
- python -m scripts.workspace_navigation_e2e --out artifacts/hardening-workspace-navigation
- python -m scripts.cinematic_e2e --out artifacts/hardening-cinematic
- python -m scripts.http_release_smoke --out artifacts/hardening-http
- python -m scripts.inspection_smoke --out artifacts/hardening-final-inspection
- python -m qfault verify-report artifacts/hardening-blind-browser-final/measurement_only-pre-reveal.json and measurement_only-revealed.json

All new output directories are exclusive. Existing browser scripts have historical bridge strings in limitations; the actual invocation here used isolated CPython, installed Playwright 1.62.0 and cached Chromium 151.0.7922.34. Do not treat a cached browser as a fresh browser download. Source and evidence collector checks are separately recorded in artifacts/hardening-release, including all 3049 referenced raw files and unchanged historical hashes.
