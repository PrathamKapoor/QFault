# Scientific methods and limits

## Contracts

All circuits start in |0…0>. Bell and GHZ contracts expect (|0…0> + |1…1>)/sqrt(2). QFT includes an X preparation of basis state 1, then forward Fourier transformation, with amplitudes exp(2πiy/2^n)/sqrt(2^n). Qiskit qubit 0 is least significant; displayed bitstrings run from q[n−1] to q[0]. These analytic states are defined independently of circuit construction.

The contract checks one fixed input. A state-fidelity match is not equivalence for all inputs. Computational-basis probability agreement is weaker still: relative phases can differ while counts agree. The phase-control test and benchmark expose this limitation.

## Execution and noise

The default reference backend produces ideal sampled counts with Qiskit BasicSimulator. With gate depolarization, gates evolve a Qiskit DensityMatrix; each k-qubit gate is followed by the Qiskit Kraus channel E(ρ) = (1−p)ρ + p I/2^k on those local wires, retaining correlations on other wires through the channel evolution. This is implemented using identity plus all k-qubit Pauli Kraus operators with appropriate weights. It is a scientifically specified fallback, not Aer.

Symmetric readout noise independently flips each measured bit with probability r using a separately derived RNG seed. This is a classical measurement channel applied to genuine Qiskit-produced measurements. No hidden channel rate is supplied to the analyst. The executor records it for reproducibility and evaluation. Noise rates are constant per investigation. No temporal simulation-time model or forecasting exists.

## Evidence and statistics

Measurement disagreement is total variation: 1/2 Σ|observed_frequency−expected_probability|. For d outcomes and n shots, a conservative multinomial bound uses radius sqrt(log((2^d−2)/α)/(2n)), clipped to one, with α=0.001 per comparison. Significant disagreement requires the lower bound to exceed TV tolerance 0.10. At most ten comparisons are contemplated per investigation, giving a union-bound error ceiling of 0.01 for these comparisons under the independent multinomial model. These are bounds on sampling error, not probabilities of a diagnosis being correct.

Absence of a significant difference is reported as NO_SIGNIFICANT_FAILURE_DETECTED, never proof of correctness. Fewer than 128 shots or a failure-triggered plan without a funded logical diagnostic can abstain. A noise conclusion is consistency with tested noise behavior, not proof of a unique physical cause. Readout probes can flag readout disagreement; gate and readout noise are not fully identifiable in all circuits.

## Diagnosis and recovery

The analyst receives the submitted circuit, contract, allowlisted immutable measurements and bounded diagnostic methods. It does not receive the original trusted circuit, scenario name, mutation position or label. A simulator-only state probe compares actual ideal evolution with the analytic contract; it is a privileged classical simulation, not tomography. Its cost is one exact circuit evaluation and zero shots. A calibration probe consumes 1,024 additional shots.

Recovery enumerates at most 256 one-edit candidates: deletion, insertion/replacement from an H/X/Z/CX palette, valid rewiring, and ±π/4 or ±π/2 corrections to existing supported angles. Not every possible missing operation is recoverable. It stops at a satisfying fixed-input state or the evaluation ceiling. The original circuit remains unchanged. The edit is a recovery explanation, not proof that the injected location was uniquely localized; equivalent fixes can exist.

Independent verification uses Qiskit DensityMatrix evolution rather than the planner's Statevector routine, compares to the analytic state, and executes fresh finite-shot validation at seed +10007. Shared Qiskit dependencies mean this is procedural and numerical independence, not an independent software vendor or full equivalence checker. A logical state pass and distribution upper bound within tolerance are both needed for VERIFIED. Systematic noise can cause a logically repaired candidate to be rejected. Budget exhaustion can leave a candidate INCONCLUSIVE.

## Evaluation

The frozen protocol is benchmark-protocol.md. Policy ceilings are matched; actual consumption is reported. Fixed-plan privileged calculations are not hidden from the cost ledger. Ground truth is evaluated only after prediction_digest is frozen. Some valid mutations are equivalent for the declared input and are not counted as logical failures.

The corpus is small: 25 family/scenario combinations, each at three sampling seeds, repeated for four policies. Wilson intervals are descriptive summaries; seeds repeat a fixed circuit population and are not independent evidence of generalization to unseen algorithms. Configured-noise labels intentionally retain channels that the restricted measurement cannot observe, exposing attribution limits. No parameter optimization used these results.

## Integrity and review

qfault-json-v1 uses UTF-8 JSON, sorted object keys, compact separators, preserved array order and rejection of NaN/Infinity. SHA-256 binds the resulting bytes. This is a project-specific canonicalization, not RFC 8785; numeric 1 and 1.0 are distinct encodings. Manifests cover separate investigation and evaluator documents. Reviews carry their own digests and the investigation digest; the manifest binds review membership and envelope hashes. Deleting or changing a review fails verification relative to the intact manifest. Changing a covered result without updating the manifest fails verification.

An attacker who replaces both artifacts and their manifest can recompute hashes. There is no signature, external trust anchor, deletion-resistant review log or authenticated reviewer identity. Hashes establish consistency, not scientific truth. Human review never applies a circuit edit automatically.

## Complementary measurements and optional Aer

The new phase policy and frozen split are specified in diagnostic-findings.md and configs/diagnostic-evaluation.json. Bell/GHZ analysis applies H to every qubit and compares the full X-measurement distribution (positive GHZ has even product parity). QFT's analytic fixed-basis output is a product of local phases; Rz(-2πk2^j/2^n) followed by H on qubit j cancels those relative phases. Equivalent large angles are normalized modulo2π, which can change only irrelevant global phase. Internal analysis circuits permit32 submitted plus at most10 basis gates; submitted Circuit still caps at32.

Basis construction uses the declared contract only. Genuine finite-shot complementary counts and separately collected calibration can trigger ideal-state attribution. Calibrated error rates and mutation labels remain unavailable as diagnostic features. Tests poison evaluator metadata to verify the API boundary. This is not a hostile-Python security sandbox. Complementary witnesses are incomplete and may miss small angle faults; global phase never counts as failure. Phase recovery reserves fresh Z and complementary samples before candidate search, and independently validates at seed+10007/+10024.

Explicit backend=aer uses AerSimulator(method='density_matrix',max_parallel_threads=1), depolarizing_error(p,k) after each declared k-qubit gate, and symmetric ReadoutError. There is no transpilation, so logical-gate noise placement matches the reference. Simulator seeds reproduce within a backend; distinct samplers need not produce identical counts. Nine paired cases and actual saved-density comparisons are in benchmarks/backend-conformance.json. Failed requested Aer execution is not silently replaced. Frozen policy comparison remains on reference; the separate submission rehearsal executes Aer.

verify_export and qfault verify-report recompute artifact/review hashes and membership. The embedded verification flag is not trusted. Integrity remains unsigned hash consistency; numeric encodings follow qfault-json-v1 exactly, not a cross-language RFC8785 guarantee. Human decisions remain append-only separately bound records.
