# Custom Circuit Laboratory and adaptive evidence planning

Implemented in `qfault/lab.py` (engine), `qfault/lab_corpus.py` (prespecified cases), `scripts/evaluate_lab.py` (policy comparison), `tests/test_lab.py`, `web/src/components/CustomLab.tsx`. Route: `/#/lab`. The Bell/GHZ/QFT workflow, Blind Challenge and all frozen benchmark files are unchanged.

## Input schema (`CustomCircuit`, schema_version 1)
`name` (<=80 printable chars), `n_qubits` 2-5, `input` `{kind: computational_basis, bitstring}`, `gates` (<=32, the existing `Gate` allowlist: h x z s rx ry rz cx cz cp swap; |angle|<=8pi). Unknown fields are rejected (`extra="forbid"`); no code, files, URLs or OpenQASM. Request bodies over 64 KiB return 413.

- **Ordering:** Qiskit order everywhere. The leftmost character of a bitstring or Pauli string is the highest qubit; `XZI` is X on q2, Z on q1, I on q0. Verified against Qiskit `Statevector.expectation_value` in tests.
- **Input preparation:** X gates on qubits whose bit is 1 are prepended by `CustomCircuit.subject()`; they are not part of the submitted gate list and are counted as executed gates.
- **Identity:** `circuit_id = "custom_" + sha256(canonical JSON of n_qubits, input, gates)[:20]`; the name is excluded. Structural only, not an equivalence proof.

## Contracts
`pauli_expectations` (observables with expected in [-1,1] and tolerance in (0,1]) and `measurement_distribution` (basis X/Y/Z, probabilities summing to 1 within 1e-6, never silently normalized). `environment` must be `"ideal"`: contracts describe noiseless behavior; observed deviations may be noise. Contracts are never derived from the candidate. Rejected: duplicates, identity observables, length mismatches, and contradictory claims (anticommuting pairs with <A>^2+<B>^2>1; commuting triples A,B,AB infeasible under the correlation polytope, solved by LP). Target-state contracts are not implemented.

## Measurement
Each qubit-wise-compatible group of observables is one real circuit: prep + submitted gates + basis gates (X: H; Y: rz(-pi/2) then H, S-dagger up to global phase). Parity over the observable support gives +-1 samples. Basis gates experience configured gate noise. Qubit-wise-commuting observables share shots (cluster state: 3 stabilizers -> 2 circuits).

## Statistics
Pauli: two-sided Hoeffding radius sqrt(2 ln(2/a)/N). Distribution: the existing Weissman TV bound (`tv_radius`). Intervals are evaluated only on the prespecified per-group grid N in {b,2b,...,Kb}. a = alpha_total / (n_claims*K + 1) is a union bound over every interval the procedure can compute (claims x looks, plus one readout control), so adaptive selection/stopping cannot inflate the family-wise error beyond alpha_total (default 0.01, i.i.d. shots assumed). Claim states: VIOLATED (|est-exp| - r > tol), SATISFIED_WITHIN_TOLERANCE (|est-exp| + r <= tol), else UNRESOLVED. No calibrated class probabilities are claimed.

## Planner and policies
All policies share one stop rule (all claims resolved / look limit / shot or evaluation budget) and reserve one batch for the readout control. They differ only in selection: `adaptive` (group covering the most unresolved claims, ties to fewer basis gates; never re-measures resolved claims), `fixed` (round robin, declared order), `complementary_schedule` (round robin, fewest non-Z letters first), `random`. The adaptive score is claim coverage, not information gain. The planner receives only a `_Port` exposing counts; measurement-only runs never call `exact_expectations` (enforced by a monkeypatch test).

## Verdicts are separate
Detection (`SIGNIFICANT_DISCREPANCY` / `NO_SIGNIFICANT_DISCREPANCY` / `INSUFFICIENT_EVIDENCE`), attribution (`AMBIGUOUS_LOGICAL_VS_NOISE`, `NOISE_CONSISTENT_NOT_UNIQUE`; simulator-assisted adds `LOGICAL_DEFECT_SUPPORTED_FIXED_INPUT`, `NOISE_CONSISTENT_FIXED_INPUT`, `MIXED`), localization (always `NOT_ESTABLISHED`), recovery (always `UNSUPPORTED`).

## Persistence and API
Results use the existing `ArtifactStore` (`schema_version` 2 inside investigation.json; manifest format unchanged, old readers and exports verify). `family` is `custom` in history. Routes: `GET /api/lab/examples`, `POST /api/lab/validate`, `POST /api/lab/investigations`, `POST /api/lab/investigations/{id}/replay`; retrieval, verification and export reuse `/api/experiments/{id}[/verification|/report]`. User circuits have `evaluation_truth.ground_truth = null`.

## Evaluation (measurement-only, reference backend, alpha 0.01, batch 1024, 4 looks)
Corpus: cluster, product-phase (|+y>, |-x>, ry), Clifford (H,S,CX), echo (U then U-dagger on one input); modifications: remove first/last gate, extra Z, angle shifts (pi/3, 0.5, 0.25), gate swap; environments ideal / readout 0.15 / gate depolarizing 0.15. Truth label = the candidate's ideal state violates a declared claim beyond tolerance (evaluator side only). Development: 75 cases (cluster3, product3, echo2). Holdout, defined before the policy comparison and not used for tuning: 117 cases (cluster4, cluster5, clifford3, product4, echo3), seeds 9001-9003. The planner was not changed after the holdout run. These cases are not the previously frozen 52-case Bell/GHZ/QFT holdout.

Holdout, max 10240 shots, 117 cases x 4 policies (full rows in `benchmarks/custom-lab-holdout-10240.json`):

| policy | faults detected (of 42) | correct circuits confirmed / insufficient / false alarm (of 45) | noise-only flagged (of 30) | mean shots | budget-exhausted |
|---|---|---|---|---|---|
| fixed | 39 | 33 / 12 / 0 | 30 | 4516 | 0.13 |
| random | 39 | 20 / 25 / 0 | 30 | 5628 | 0.34 |
| complementary | 39 | 33 / 12 / 0 | 30 | 4464 | 0.13 |
| adaptive | 39 | 33 / 12 / 0 | 30 | 4464 | 0.13 |

Paired shots (policy minus adaptive, bootstrap 95%): fixed +53 [18, 96]; random +1164 [893, 1444]; complementary 0 [0, 0]. At 4096 shots all four policies are identical on all 117 cases.

## Negative findings
- Adaptive is not better than the complementary schedule on this corpus and is only ~1% cheaper than fixed; the large gap is to random selection. Coverage-based selection has little to exploit when there are only 1-4 groups.
- 3 of 42 faults are undetected by every policy (small angle shifts the budget cannot resolve at tolerance 0.1) and 12 of 45 correct circuits stay INSUFFICIENT at 10240 shots; the system does not claim success there.
- No measurement-only run attributes a violation to a logical defect; every violation stays ambiguous or noise-consistent, by design.
- Noise-only cases are flagged as discrepancies (30/30): a noisy execution violates the ideal contract, which is correct but is not a circuit defect.
- Rates are descriptive; cases share circuits across 3 seeds, so Wilson intervals are optimistic.

## Reproduce
```
.local/repro-python/Scripts/python.exe -m pytest -q
.local/repro-python/Scripts/python.exe scripts/evaluate_lab.py --split development --out benchmarks/custom-lab-development.json
.local/repro-python/Scripts/python.exe scripts/evaluate_lab.py --split holdout --max-shots 10240 --out benchmarks/custom-lab-holdout-10240.json
.local/repro-python/Scripts/python.exe scripts/evaluate_lab.py --split holdout --max-shots 4096 --out benchmarks/custom-lab-holdout-4096.json
```

## Limitations
Simulation only; no hardware. Fixed computational-basis input, not unitary equivalence. Pauli/distribution claims are incomplete witnesses; a satisfied claim is not correctness. No target-state contract, no measured recovery, no gate localization. i.i.d. shot assumption; conservative union bound. Executions are synchronous: the timeline is a completed history.
