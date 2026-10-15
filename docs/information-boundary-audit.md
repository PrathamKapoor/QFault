# Information and statistical boundary audit

This source audit started from `35cbbb9` on `research/external-validation`. It reviewed the complete production modules `quantum`, `backends`, `diagnostics`, `measurement`, `lab`, `target`, `counterfactual`, `recovery_observation`, `interventions`, `recovery`, `workflow`, `challenge`, `storage`, `evidence`, and `api`, with their quantum, measurement, target, recovery, challenge, storage and release-audit tests. New adversarial checks are in [test_information_boundaries.py](../tests/test_information_boundaries.py). Historical benchmark files were read without rewriting them. This is a bounded local source and execution audit, not external scientific validation.

## Confirmed defects and hardening

The request-size dependency trusted `Content-Length`, ran after framework body parsing, and did not count incoming bytes. A valid laboratory request with 70,000 trailing spaces returned HTTP 200 when sent without that header or with a falsely small header. `Content-Length: abc` produced HTTP 500; `-1` was accepted. ASGI middleware now counts actual bytes before JSON parsing: regression tests observe HTTP 413 for oversized bodies, HTTP 400 for malformed lengths, and successful parsing of a valid streamed request. The local API is unauthenticated developer tooling; these controls do not establish an internet service security boundary.

`run_policy` and `run_witness_policy` previously received the complete `LabRequest`, including the candidate program and environment, despite documenting a measurement capability boundary. Current policy code did not consume those fields: no scientific truth leak was demonstrated. A frozen `PolicyConfig` now restricts this argument to policy settings and makes the intended interface enforceable. This remains a Python API boundary: an adversarial Python process can inspect private executor fields and callable closures.

The substantive scientific defect is the interpretation of target witnesses under noisy basis rotations. A common state measured in calibrated Pauli bases is necessary for the fidelity bounds. It cannot generally be recovered by saying that basis-gate noise is simply part of an “observed state.” For the actual Bell preparation `H(0); CX(0,1)` with per-gate depolarizing parameter `p=0.05`, exact Qiskit channel evolution gives subject expectations

\[
\langle XX\rangle=0.95^2,\quad
\langle YY\rangle=-0.95^2,\quad
\langle ZZ\rangle=0.95.
\]

Applying the implemented noisy analysis gates gives measured parity means `XX=0.95^4`, `YY=-0.95^6`, `ZZ=0.95`. These means would reconstruct an operator with eigenvalue approximately `-0.007354`; they are not the expectations of one density matrix. Giving these *exact* means to the bound routine with zero radii produces `L=0.882253125 > U=0.87489953515625`. No sampling interval missed its mean: the measurement model failed. Contradictory bounds now abstain. Laboratory target reports preserve a conditional numerical witness calculation while marking preanalysis fidelity unresolved under declared measurement noise; target recovery abstains with `MEASUREMENT_MODEL_ABSTENTION`. New tests cover both the exact channel counterexample and these abstention paths.

Symmetric independent readout noise alone has a narrower valid interpretation: it multiplies a Pauli of weight `w` by `(1-2p)^w`, equivalent to a common local depolarizing channel. The resulting fidelity belongs to that transformed state, not automatically the state before readout. Historical target evaluation already recognized the gate-noise distinction in [target_corpus.py](../qfault/target_corpus.py): gate-noise rows have `effective_fidelity=None`. Its frozen readout coverage results should not be discarded because of the separate basis-gate defect.

## Information flow

| Path | Legitimate decision information | Privileged boundary |
| --- | --- | --- |
| Template measurement-only | Analytic declared target, validated counts, bounded complementary/control measurement capability | No faulty-state helper or recovery planner; readout consistency is not unique attribution. |
| Custom Pauli/distribution | Declared claims, grouped settings, cumulative validated counts and policy settings | Target expectations are declared independently of the submitted candidate. Program/noise belong to execution. |
| Target witness | Declared pure-target coefficients, sampled parity intervals, bounded measurement settings | Target decomposition is public contract information; candidate-state evolution is privileged. Fidelity interpretation requires calibrated common-state measurements. |
| Counterfactual recovery | Declared one-edit search set, measured screening losses, immutable selected candidate, fresh original/candidate observations | No evaluator argument or exact-state selection. A successful intervention is not a causal fault-location proof. |
| Simulator-assisted | Exact candidate state, target infidelity, candidate-distribution residuals; exact repair search and density verification | Deliberately privileged and separately labelled. It is not hardware-accessible measurement-only evidence. |
| Blind challenge | Allowlisted public measurements/diagnosis/cost, persisted observation → diagnosis → freeze → reveal chain | Actual circuit, injected metadata and evaluator report remain private until reveal. A caller-supplied known seed enables deterministic inference, explicitly documented rehearsal behavior. |

Adversarial tests execute genuine Aer custom diagnosis and fresh recovery for all three contract types while exact candidate-state helpers raise if called. Execution mappings raise if a decision reads injected truth, scenario, mutation, noise configuration, or input digest. Fresh verification execution IDs and seeds differ from screening and observation. These tests establish exercised paths; they do not prove every possible future plugin or Python modification respects the interface.

`EvidenceCollector` validates bitstring width/alphabet, nonnegative integer counts, successful execution and exact shot totals, then projects only execution ID, shots and copied counts. `Strict` forbids unknown fields and nonfinite numeric values. Gate arity, assignments, angle bounds, circuit size, target normalization, and contract/circuit width are checked. Pauli consistency validation supplies necessary pairwise/triple checks, not a full quantum satisfiability solver. Unsigned SHA256 manifests verify consistency relative to the supplied manifest; they neither authenticate data origin nor establish scientific correctness. Local administrators can inspect/rewrite private artifacts and hashes.

## Independent statistical derivation

For an `m`-outcome multinomial, the implemented radius
`r = min(1, sqrt(log((2^m-2)/alpha)/(2n)))`
follows from `Pr(||p_hat-p||_1 >= epsilon) <= (2^m-2) exp(-n epsilon^2/2)` with `TV=||p_hat-p||_1/2`. Since TV is Lipschitz in its first argument, the target distance is enclosed by `TV(p_hat,q) ± r`. Laboratory distributions correctly use the full `2^n_qubits` alphabet even when the declared target has sparse support. The constant and exponent were checked against [Weissman et al., Theorem 2.1](https://shiftleft.com/mirrors/www.hpl.hp.com/techreports/2003/HPL-2003-97R1.pdf).

For parity outcomes in `{-1,+1}`, Hoeffding gives
`Pr(|b_hat-b| >= r) <= 2 exp(-n r^2/2)`;
therefore `r=sqrt(2 log(2/alpha)/n)`. Qiskit ordering is consistent: the rightmost bit/Pauli character acts on qubit 0. Y analysis uses `Rz(-pi/2)` then H. Simultaneous measurements may correlate Pauli estimates, but union bounds do not require independent intervals.

For `d=2^n_qubits`, a pure target and candidate density matrix satisfy
`F=(1+sum_P a_P b_P)/d`, where the sum excludes identity. Unmeasured terms are bounded by both their coefficient absolute sum and `sqrt(sum_unmeasured a_P^2 * (d-1))`; the candidate purity relation gives `sum_P b_P^2 <= d-1`. Omitted target coefficients are bounded using target purity and Cauchy–Schwarz. For a stabilizer target, commuting generator projectors give `F >= 1-sum_i(1-<g_i>)/2` and every stabilizer element gives `F <= (1+<g>)/2`. Greedy selection of independent generators maximizes this linear lower bound. The [Fuchs–van de Graaf inequality](https://arxiv.org/abs/quant-ph/9712042) gives the additional upper bound `F <= 1-(|b_P-a_P|/2)^2`. All require a common physical candidate state and covering expectation intervals; floating-point coefficient thresholds also limit exact-arithmetic interpretations.

Adaptive laboratory stopping is valid on the prespecified grid of at most K looks per group. For M claims or target Pauli terms, `alpha_slot=alpha_total/(M*K+1)` accounts for every potential term/look interval and one control. Adaptive group choice and early stopping cannot escape their simultaneous coverage event. The projected marginal gain is a heuristic based on plug-in estimates, not expected information gain or a calibrated class probability.

Counterfactual recovery allocates `alpha_total/((C+3)*M+1)`: original plus up to C screening candidates, fresh original and frozen selected candidate, and one readout control. Conditional coverage of fresh samples survives candidate selection because verification samples were unused during selection. A verified repair requires candidate upper loss `<=1` and original lower loss greater than candidate upper loss. These statements assume independent stationary shots and properly calibrated measurement channels; deterministic seed offsets support reproducibility without proving physical independence or absence of drift.

## Frozen error taxonomy

The following are descriptive counts read from frozen results, not new holdout executions or population guarantees.

| Failure class | Evidence in frozen artifacts | Interpretation |
| --- | --- | --- |
| Incomplete phase observability | Measurement Z misses all six relative-phase cases in `measurement-boundary-holdout-20261013.json`; complementary measurements detect their discrepancies. | A missing witness is a structural information limit. |
| Attribution ambiguity | Complementary measurement-only returns ambiguous for all six missing-gate and six phase cases; strict attribution remains 16/52. | Detection does not separate gate noise from logic. |
| Subthreshold/noise ambiguity | Both simulator policies miss all six low-readout and six low-gate-noise labels; phase calls two mixed cases logical-only. | Evaluator labels configured noise even when the evidence cannot establish it at the declared budget/tolerance. |
| Witness miss despite phase schedule | `diagnostic-final.json` retains `qft-2-angle-103` and `qft-2-angle-211`: phase predicts no failure, evaluator identifies a logical defect. | Complementary witnesses are not complete tomography. |
| Contract incompleteness | Conservative counterfactual policy returns `NO_REPAIR_NEEDED` for two incomplete-contract controls. | Satisfying a declared claim does not establish overall correctness. |
| Repair/localization nonidentity | Three of 16 conservative verified interventions act at a different locus from the injected fault; plausible loci retain alternatives. | Improving edits do not uniquely identify the original cause. |
| Budget and cautious abstention | Conservative recovery retains two insufficient-budget and 14 gate-noise insufficient-evidence cases. | Unresolved evidence is not successful repair or proof of no fault. |
| Conditional state interpretation | Target Aer holdout has 1,650 covered effective-state rows and 420 gate-noise rows with coverage undefined. | These are different measurement-model claims; no fidelity coverage claim exists for the gate-noise rows. |

The frozen repetitions share architectures, seeds and budgets. They do not justify independent-circuit inferential intervals, causal claims, hardware performance claims, or unseen-architecture generalization. New tests are regression/audit controls and must not be relabelled as untouched scientific validation.

Local verification: `.local/release-audit-python/Scripts/python.exe -m pytest tests/test_information_boundaries.py -q -p no:cacheprovider` passed all 16 cases after the fixes, with the existing Starlette/httpx deprecation warning. The initial pre-fix run had 11 failures and four passes; adding the second contradictory-bound threshold produced the final 16-case set. No external validation or new holdout score is inferred from this result.
