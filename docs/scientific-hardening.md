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
