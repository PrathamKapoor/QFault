# Target-state contracts and adaptive witness selection

> **Historical methodology and evaluation (2026-10-13).** The 2026-10-16
> [audit](information-boundary-audit.md) corrects the basis-noise interpretation:
> fidelity certification requires calibrated Pauli measurements of one common
> state. Current noisy target investigations withhold preanalysis state claims;
> noisy target recovery abstains. Historical symmetric-readout effective-state
> coverage remains separately valid, and frozen results are unchanged. Current
> behavior and new experiments: [external validation](external-validation.md).

Implemented in `qfault/target.py` (contract, catalog, bounds, selection proxy), `qfault/lab.py` (`run_witness_policy`, `target_feasibility`, integration in `investigate_lab`), `qfault/target_corpus.py`, `scripts/evaluate_target.py`, `tests/test_target.py`, `scripts/lab_e2e.py`, and the Custom Circuit Laboratory (`/#/lab`, contract type "Target state"). Pauli/distribution contracts and their `adaptive` planner are unchanged.

## Contract
```json
{"kind": "target_state", "amplitudes": [[0.7071067811865476, 0], [0, 0], [0, 0], [0.7071067811865476, 0]],
 "fidelity_tolerance": 0.2, "provenance": "analytic Bell state"}
```
- `amplitudes`: 4-32 `[re, im]` pairs of strict JSON numbers (strings rejected), length 2^n matching the circuit. Index k is the basis state `format(k, "0nb")` in Qiskit order (rightmost bit = q0), identical to `Statevector`.
- Normalization: accepted only if |‖ψ‖² − 1| ≤ 1e-6; the vector is then divided by its norm (a correction ≤ 5e-7). Larger deviations are rejected, never silently normalized. The UI shows ‖ψ‖² and offers an explicit "Normalize" action.
- Claim: F = ⟨ψ|ρ|ψ⟩ ≥ 1 − `fidelity_tolerance`. F is global-phase invariant by construction. Contract identity is the structural sha256 of the canonical JSON, so two phase-equivalent declarations have different ids but identical behavior (tested).
- Policies: `adaptive_witness` (default), `coefficient_weighted`, `fixed`, `complementary_schedule`, `random`. The Pauli-contract `adaptive` policy is rejected for target contracts and vice versa.

## Two evidence paths (never merged)
- `MEASUREMENT_DERIVED_WITNESS`: a bound [L, U] computed only from sampled Pauli expectations and the declared target. Available in measurement-only mode.
- `SIMULATOR_ASSISTED_EXACT_STATE`: privileged ideal fidelity and gate-noise state fidelity (readout excluded: not a state property). Present only in simulator-assisted mode and listed in `privileged_operations`.

Measurement-only runs are tested with `exact_expectations`, `Statevector.from_instruction` and `noisy_density` all replaced by functions that raise.

## Witness catalog
a_P = Tr(P ρ_t) from `SparsePauliOp.from_operator`, all non-identity terms kept, sorted by |a_P|. Terms omitted by Qiskit's internal cut-off are accounted rigorously: their squared mass is d − 1 − Σa_P² (purity), so their absolute sum is ≤ √(count·mass). Terms are grouped by the existing greedy qubit-wise-commuting `group_paulis` (shared with Pauli contracts). Stabilizer targets are detected (exactly d − 1 terms with |a_P| = 1). Tests verify the reconstruction of ρ_t and of F against `state_fidelity`.

## Bounds (simultaneous on the coverage event)
Given intervals b̂_P ± r_P that all contain the true expectations:
1. Pauli expansion F = (1 + Σ a_P b_P)/d; unmeasured terms bounded by min(Σ|a_P|, √(Σa_P²·(d−1))) using |b| ≤ 1 and purity.
2. Stabilizer targets: F ≥ 1 − Σ_i (1 − ⟨g_i⟩)/2 for commuting generators (I − Σ(I−Q_i) ≤ ΠQ_i). The greedy max-weight independent set is used (optimal for a linear matroid). Also F ≤ (1 + ⟨g⟩)/2 for every measured stabilizer element.
3. Fuchs–van de Graaf for a pure target: |b_P − a_P| ≤ 2D ≤ 2√(1−F), so F ≤ 1 − (|b_P − a_P|/2)².

[L, U] is the intersection, clipped to [0, 1]. Decision: VIOLATED if U < threshold, SATISFIED_WITHIN_TOLERANCE if L ≥ threshold, otherwise UNRESOLVED (`INSUFFICIENT_EVIDENCE`). Individually significant Pauli deviations are reported as `witness_discrepancies`; they do not by themselves decide the contract. A randomized test (300 random targets, states and partial measured subsets) confirms L ≤ F ≤ U whenever the intervals cover.

## Statistics
Hoeffding radius √(2 ln(2/α)/N) for each ±1 parity mean. Intervals are evaluated only on the per-group grid N ∈ {b, 2b, …, Kb}. α = α_total/(m·K + 1), with m = number of catalog terms (all terms that could ever be estimated), K looks and one readout control. The union bound covers every interval the procedure may compute, regardless of adaptive order, stopping, or the correlation between terms sharing shots. Assumption: shots are i.i.d. given the circuit. Readout error and basis-gate noise are part of the observed state: readout flip p maps exactly to a local depolarizing channel λ = 1 − 2p on the measured Paulis, which defines the coverage truth; with gate noise the measured quantity is basis-dependent and coverage is not defined.

## Adaptive witness selection (`adaptive_witness`)
Inputs: the target catalog, the current estimates and radii, looks used, and the remaining budget. The candidate state is never an input. For each open group it computes the plug-in marginal value: the bound when all open groups are projected one look further (measured terms at their estimates, unmeasured terms at their target values) minus the same projection without that group. A one-step projection is myopic: no single stabilizer generator raises L. Direction: raise L while the plug-in fidelity is at or above threshold, otherwise lower U. Ties go to fewer basis gates. The policy stops with `NO_INFORMATIVE_ACTION` if nothing is projected to help. This is a heuristic proxy, not information gain. `test_observed_data_change_the_next_witness` shows that a deviating estimate flips the next choice.

## Evaluation
Protocol `configs/target-witness-protocol.json` (source sha256 digests, splits, seeds, budgets, metrics) was committed (68f33b4) after a single development run and before the holdout. No policy change followed either run.

Holdout: 414 cases (ghz4, star_graph4, clifford_mix3, complex_product3, rotation_entangler3, inverse_echo3, line_graph2; 6 modifications; environments ideal / readout 0.04 / gate depolarizing 0.05; global-phase variants; tight 12288-shot and ample 32768-shot budgets; seeds 7101-7103) × 5 policies, measurement-only, reference backend. Truth classes: 114 logical violations, 132 clean-correct, 168 noise-only (cases are counted per budget, so each budget sees half of each class).

| budget / policy | violations detected (57) | clean confirmed / false alarms (66) | bound coverage | mean width | mean shots |
|---|---|---|---|---|---|
| tight / adaptive_witness | 54 | 51 / 0 | 165/165 | 0.272 | 6134 |
| tight / coefficient_weighted | 54 | 51 / 0 | 165/165 | 0.265 | 6095 |
| tight / fixed | 54 | 51 / 0 | 165/165 | 0.262 | 6095 |
| tight / complementary | 52 | 51 / 0 | 165/165 | 0.310 | 6283 |
| tight / random | 52 | 47 / 0 | 165/165 | 0.377 | 6327 |
| ample / adaptive_witness | 54 | 53 / 0 | 165/165 | 0.210 | 11051 |
| ample / coefficient_weighted | 54 | 51 / 0 | 165/165 | 0.215 | 10962 |
| ample / fixed | 54 | 51 / 0 | 165/165 | 0.214 | 10962 |
| ample / complementary | 54 | 51 / 0 | 165/165 | 0.215 | 11150 |
| ample / random | 53 | 51 / 0 | 165/165 | 0.322 | 11299 |

Paired per case (baseline minus adaptive_witness, bootstrap 95%, n = 207 per budget):
- vs fixed / coefficient_weighted, tight: shots −40 [−168, 59]; width −0.0095 [−0.0151, −0.0044] and −0.0064 [−0.0117, −0.0014]. The baselines give narrower bounds, and 4 cases are decisive only under the baseline. **Adaptive is worse at the tight budget.**
- vs fixed / coefficient_weighted, ample: shots −89 [−411, 218]; width +0.0045 [−0.0002, 0.0109] and +0.0049 [0.0002, 0.0111]; 4 cases decisive only under adaptive. A small gain.
- vs complementary, tight: shots +148 [25, 297], width +0.038 [0.018, 0.059]. Adaptive is better.
- vs random: width +0.11 at both budgets (interval excludes 0). Adaptive is better.
- The action order differs from the fixed order in 120/207 cases, so the policy does adapt; the differences rarely change decisions.

Aer replication (same frozen cases, `benchmarks/target-witness-holdout-aer.json`; agreement in `benchmarks/target-witness-backend-agreement.json`): category agreement 406-412 of 414 per policy (2070 rows, 20 disagreements: 16 noise-only, mostly ghz4 with gate noise near threshold, flipping in both directions; 2 clean; 2 violations). Coverage 165/165 and 0 false alarms for every policy. The qualitative conclusions replicate: adaptive_witness is slightly better at the ample budget (width vs fixed +0.0077 [0.0003, 0.0161]; 6 cases decisive only under adaptive vs 0) and not better at the tight budget (vs fixed −0.0033 [−0.0093, 0.0033]; decisive only adaptive 2 vs baseline 6). On Aer the tight-budget width deficit is not significant; on the reference backend it was.

Post-freeze change: after the holdout ran, only the user-facing recovery message in `qfault/lab.py` was reworded; no decision logic changed, so the source digest of lab.py in the protocol no longer matches HEAD for that reason alone.

## Negative findings
- adaptive_witness is not uniformly better than a simple coefficient-weighted or fixed order: it is slightly worse at the tight budget and slightly better at the ample budget. With 3-19 groups, deterministic heavy-first ordering already captures most of the value. The projection also assumes unmeasured terms match the target, which is optimistic precisely when the state is faulty.
- The dense non-Clifford target (rotation_entangler3, 49 catalog terms in 19 groups) is INSUFFICIENT for every policy and budget even when the circuit is correct; the expansion bound with unmeasured terms is too loose. This is the "no cheap informative witness" case.
- 3 of 57 logical violations per budget are undetected, all of them the dense-target `angle_large` candidate (ideal F = 0.681 vs threshold 0.8): with most terms unmeasured, neither side of the bound resolves.
- Noise-only cases with low noise are mostly not flagged, which is correct when the effective fidelity is above threshold. Noise is never attributed to a cause in measurement-only mode.
- Cases share circuits across seeds and budgets; intervals are descriptive.

## Reproduce
```
.local/repro-python/Scripts/python.exe -m pytest -q
.local/repro-python/Scripts/python.exe scripts/evaluate_target.py --split holdout --out benchmarks/target-witness-holdout.json
.local/repro-python/Scripts/python.exe scripts/evaluate_target.py --split holdout --backend aer --out benchmarks/target-witness-holdout-aer.json
PYTHONPATH=. .local/repro-python/Scripts/python.exe scripts/lab_e2e.py --out <new dir>   # needs a running `qfault serve`
```

## Limitations
Simulation only. One declared input state; not unitary equivalence. Bounds can be very loose for dense targets; an unresolved bound is not certification. i.i.d. shot assumption; conservative union bound. No measured recovery, no gate localization; recovery stays `UNSUPPORTED`. Catalog size up to 4^n − 1 (1023 at n = 5) is bounded by the existing 5-qubit limit; dense 5-qubit targets are infeasible under the evaluation budget cap and abstain.
