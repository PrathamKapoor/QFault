# Measured counterfactual recovery

This capability evaluates **edits to a controllable circuit program**, not hidden hardware faults. An edit that improves a finite contract does not identify the original cause. No circuit is changed automatically. Existing simulator-assisted `RecoveryPlanner` and its historical results remain unchanged.

## Architecture and eligibility

`interventions.generate` reuses `Gate`, `CustomCircuit`, input preparation and structural resource counting. Deterministic one-edit removal, replacement, rotation-angle change, qubit reassignment and optional insertion respect a user-declared palette, positions and depth. Structural duplicates and no-ops are excluded. The default operator order is recorded; a truncated search may omit useful later operators. Neither semantic equivalence nor exhaustive synthesis is claimed.

`recovery_observation.ContractObservation` is the extension seam: contract → predetermined grouped settings → counts → simultaneous claim and normalized discrepancy bounds. It reuses lab `plan`, `_State`, rotations, parity extraction, and target `catalog`/`bounds`. It receives a measurement callback, never candidate state, mutation metadata or noise parameters. Distribution, Pauli and pure-target contracts are supported today. Dense targets may remain unresolved when the maximum group count truncates their catalog; omitted terms retain the existing conservative bounds.

`counterfactual.recover` owns the execution configuration and instantiates the existing lab `_Port` with `ExecutionBudget`. Target construction uses the declared target only. No `ideal_state`, candidate `Statevector`, `noisy_density` or exact fidelity call is available to ranking. There is no evaluator-truth parameter. The request rejects privileged mode and truth fields. Exact-state comparison remains available through the existing lab/legacy recovery, separately labelled, not mixed into this measured procedure.

## Statistical protocol

Let C be the candidate ceiling and M the number of contract claims (all catalog Pauli terms for a target). There is **one prespecified look per group per subject**. Every scalar interval uses alpha_total / ((C + 3) M + 1). The subjects are the original screening circuit, up to C screening candidates, and fresh original/candidate confirmation. The additional slot is the readout control. This union bound covers selection among simultaneous screening intervals. Conditional on frozen selection, fresh confirmation receives its own unused samples and allocated error budget; no multiplication by C is required for the single freshly selected candidate. No progressive elimination or repeated refinement is implemented.

Pauli intervals use two-sided Hoeffding for bounded ±1 outcomes. Distribution discrepancies use the lab's multinomial TV bound. Target fidelity bounds reuse the target-only expansion, stabilizer projector and trace-distance bounds. The loss is the maximum across normalized claim discrepancies; target loss is (1 − F) / tolerance. An upper loss ≤ 1 supports every declared claim. Loss intervals are not causal confidence or probabilities. The point-discrepancy baseline uses the existing plug-in completion of unmeasured target terms; this is explicitly heuristic.

Ranking displays increasing upper loss. A candidate is interval-dominated only if another upper bound is strictly below its lower bound. All remaining candidates form the plausible set, including unresolved overlaps. Conservative selection requires its upper loss below the original lower loss; within this set, fewer two-qubit gates, depth, gate count and finally structural ID select the next experiment. This operational tie-break does not resolve the evidential tie or identify a faulty gate.

Before any observation, reserve two complete fresh schedules. Screening cannot spend these shots/evaluations. Selection, ranked-evidence digest and timestamp are frozen in memory before fresh execution and preserved in the final immutable record. This is auditable recorded order, not a crash-durable intermediate checkpoint, signature or external timestamp. Each execution has a distinct deterministic seed; replay reuses those seeds. Distinct seeds do not eliminate shared simulator bias.

Fresh verification requires **both** candidate upper loss ≤ 1 and original lower loss > candidate upper loss. A definite violation or worsening rejects; otherwise abstain. Contradictory intervals cannot verify. The fresh original is essential: the initial discrepancy was itself selected evidence.

Assumptions: stationary independent shots and trustworthy declared expectations. Pauli/target interpretations additionally require calibrated measurement channels; arbitrary basis-dependent errors need not correspond to one underlying state. The zero-state readout control detects some readout inconsistencies and vetoes repair proposals; it does not calibrate every state or diagnose gate noise. Bounds do not protect against unknown drift or model bias. “Verified” covers the declared operational contract and input under these assumptions, not universal state certification or unitary equivalence.

## Bounds, persistence and interface

2–5 qubits, 32 submitted gates, ≤48 candidates, ≤4096 inspected proposals, ≤32 groups, ≤10,000 shots per group, ≤1,000,000 total shots, ≤512 executions. A 1–300 second guard is checked before every bounded backend call; it cannot interrupt a call already in progress. Artifacts are capped at 16 MiB. API admission shares the existing single-process lock; no distributed concurrency guarantee is claimed.

`POST /api/lab/recoveries` accepts `RecoveryRequest`. `POST /api/lab/recoveries/{id}/replay` repeats the recorded configuration. Retrieve, export and integrity-check through existing `/api/experiments/{id}` routes. Schema 3 records preserve original/candidate circuits, exact edit diffs, exclusions, every execution/count/seed, ranking, frozen selection, fresh evidence and phase costs using `ArtifactStore`. The normal blind challenge is untouched: recovery is not integrated into its private-truth workflow.

In Custom Circuit Laboratory, **Measured recovery** takes the currently edited or saved circuit, contract and environment to `/#/lab/recovery`. Saved results use `/#/lab/recovery/{experiment_id}` and restore through history/refresh. A highlighted position is a proposed edit, not a causal hotspot. The original shell, landing, transition and legacy recovery remain intact.

## Evaluation and provenance

Development: 31 cases × 5 policies, seed 113. Conservative and point ranking both verified 8/31; conservative made 0/14 noise-control proposals, point ranking 2/14 (both rejected). First-admissible verified 2, random 1. These are development observations, not holdout claims. An adversarial test then added a contradictory-interval guard before the holdout freeze; development raw evidence is preserved.

`configs/counterfactual-protocol.json` freezes 62 cases, seeds 731/1297, all requests, scientific source digests, policies, budgets and metrics before holdout execution. `scripts.evaluate_counterfactual` refuses a changed source or corpus and requires committed scientific sources/protocol. Baselines share the same candidate pool, screening schedule and budget ceilings; first/random still incur the shared screening cost, so this compares selection quality rather than their cheapest possible implementations. No-repair deliberately saves the screening/confirmation cost. Existing privileged first-valid recovery is not advertised as an information-matched comparator.

Cases cover Bell, GHZ, QFT, graph/cluster, product, Clifford and non-Clifford target designs; logical phase interventions, clean/readout/gate-noise controls, incomplete distributions, ambiguous repairs and insufficient budgets. This is a bounded design corpus, not evidence of arbitrary architecture generalization. All outcomes, errors, alternative repairing loci and costs are retained. Final holdout findings will be appended after execution; no tuning on those outcomes is permitted.

## Historical target evaluation traceability

Target protocol was committed at `68f33b4`; evaluation ran before/at `ddc8a67`. The diff `ddc8a67..e90acf0 -- qfault/lab.py` changes only the two-line user-facing explanation that recovery is unsupported, clarifying that target contracts are included. No sampling, decision, bound or policy changed. Consequently the original protocol's lab source hash does not match `e90acf0`; this is a genuine provenance mismatch, not repaired retroactively. Historical protocol/raw results are preserved. Recovery's own protocol includes the actual lab bytes used by this branch.

## Reproduction

```powershell
.local/recovery-python/Scripts/python.exe -m pytest -q
npm --prefix web ci
npm --prefix web run check
npm --prefix web run build
.local/recovery-python/Scripts/python.exe -m scripts.evaluate_counterfactual --split holdout --out artifacts/new-recovery-holdout
$env:QFAULT_BASE_URL='http://127.0.0.1:8001'
.local/recovery-python/Scripts/python.exe -m scripts.counterfactual_e2e
```

The browser script uses an exclusive screenshot directory; choose a new output directory for repeat captures. This work extends completed `e90acf061985c41123fa430ef51e7f8ea5b74fbb` in `C:\Projects\QFF-Recovery`, not the obsolete pre-target checkpoint. No push or integration into the original branch is authorized.
