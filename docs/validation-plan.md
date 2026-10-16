# External validation plan

Scope: the research-engineering directive dated 2026-10-16. New research stays
local on `research/external-validation`; only the reviewed six-commit release
may be published. Preserve original history, worktrees, frozen evaluations,
authorship, licences, and the approved frontend.

- [x] Audit refs and ancestry; publish the original reviewed release by normal
  fast-forward. Observe hosted checks against its exact SHA.
- [x] Run the existing Python, TypeScript, build, and Aer baseline.
- [x] Independently trace execution, evidence, diagnosis, target witnesses,
  recovery, storage, replay, blind truth isolation, and API bounds. Record
  confirmed defects separately from assumptions in `information-boundary-audit.md`.
- [x] Reproduce confirmed defects with real integration tests before fixing
  them. Use policy-only configuration objects, enforce actual HTTP body bytes,
  and qualify witness fidelity when measurement-channel assumptions fail.
- [x] Inventory the pinned QASMBench tree completely. Implement a bounded,
  static QASM2 adapter with explicit exclusions, transformation provenance,
  terminal measurement mapping, and operator-equivalence verification. Tests
  must reject dynamic programs and preserve asymmetric qubit ordering.
- [x] Use path-based development/holdout splits before observing diagnostic
  outcomes. Contracts come from the separately parsed, unmodified reference;
  exact-state values are evaluator-only, never policy inputs.
- [x] Run development cases and explicit identifiability counterexamples.
  Compare existing fixed, complementary, adaptive, weighted, and random plans
  with matched information and resource ceilings. Retain negative results.
- [x] Commit the corpus, source digests, protocol, evaluator and tests before
  final holdout. The evaluator refuses dirty or mismatched scientific sources,
  refuses existing output directories, stores raw reports and verifies exports.
- [x] Execute the frozen holdout without tuning. Report architecture and run
  denominators separately, use descriptive family aggregates, and retain all
  exclusions, faults invisible to a contract, unresolved cases and failures.
- [x] Compare conservative, point, and no-repair recovery on the same
  prespecified external cases and bounded candidate sets; verify fresh samples.
- [x] Research Qrep, MQT Debugger, Muskit, QCEC, and QASMBench from pinned
  primary sources. Execute a comparison only where task/oracle differences
  are explicit. No cross-paper success-rate leaderboard.
- [x] Produce an external-circuit investigation, verified export, complete
  ledger and browser inspection using the existing workbench.
- [x] Run full Python, frontend, backend, browser and clean-install checks.
  Update README, decisions, flow, handoff and reproduction guidance with actual
  findings. Commit locally using the existing repository identity.
- [x] Leave the loopback application running; verify PID, health, landing,
  workbench, mobile widths, reduced motion and fallback. Report unresolved
  acceptance criteria explicitly.

Implementation files are limited to the validated importer, external corpus
and evaluator, targeted scientific/API corrections, adversarial tests, compact
evidence, and relevant documentation. No second scientific engine, policy
tuning on holdout, dependency expansion, hardware submission, or frontend
redesign is planned.
