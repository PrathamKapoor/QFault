# External capability comparison

## Additional primary-source check — 2026-10-23

| Tool | Verified documented task | License checked | Relation to QFault |
|---|---|---|---|
| [Qiskit Experiments 0.14.2](https://qiskit-community.github.io/qiskit-experiments/) | Experiment framework, characterization, randomized benchmarking, state tomography and readout mitigation | [Apache 2.0](https://raw.githubusercontent.com/qiskit-community/qiskit-experiments/main/LICENSE.txt) | Substantial overlap in measurement/analysis and experiment records. Its documented calibration/characterization tasks are not a matched bounded gate-edit recovery benchmark. |
| [Mitiq 1.1.0 documentation](https://mitiq.readthedocs.io/en/stable/) | Error mitigation, including the demonstrated zero-noise extrapolation execution workflow | [Current upstream license text: GNU GPL version 3](https://raw.githubusercontent.com/unitaryfoundation/mitiq/main/LICENSE) | Mitigates noisy expectation estimates; that task differs from selecting and freshly verifying an edit against a finite behavioral contract. No performance ranking follows. |

These two tools were source-reviewed, not installed or quantitatively benchmarked.
No code was copied or added as a dependency. The existing pinned Qrep, Debugger,
Muskit and QCEC comparison below retains its checked revisions and limitations.
Current upstream capability/license links can change; the date above records
the scope of this additional check, not a timeless claim.

This is a source-backed scope comparison, not a performance ranking. Sources were retrieved on 2026-10-15 UTC (2026-10-16 IST); the repository commits below freeze the inspected versions. “Not established here” means the inspected evidence does not establish a capability, not that the project lacks it. QFAULT's baseline is commit `35cbbb9b351ef2ef4e42163b969c5331dc116eba`, its [README](../README.md), [custom laboratory](custom-circuit-lab.md), [target witnesses](target-state-witnesses.md), and [measured recovery](counterfactual-recovery.md).

## Documented capabilities and overlap

| Project | Inputs and oracle access | Scope and intervention | Uncertainty and verification | Actual overlap with QFAULT |
|---|---|---|---|---|
| **QFAULT** | Validated 2–5-qubit JSON circuit; declared distribution, Pauli, or target-state contract for one input. Measurement-only mode receives sampled outcomes; simulator-assisted modes have privileged state access. | Detect discrepancies; compare bounded one-edit interventions; template workflows also inject faults/noise. | Conservative finite-shot bounds; unresolved claims and abstentions; measured recovery reserves independent confirmation shots and freshly remeasures the original. This establishes an intervention under a contract, not causal localization or circuit equivalence. | Baseline under study. |
| **Qrep / QRep** | Faulty QASM circuit and oracle/test suite. Paper evaluation uses every computational-basis input with X/Y/Z output measurements. Inspected implementation loads oracle counts from CSV and samples Qulacs. | Gate removal, addition/replacement, parameter optimization, suspiciousness-guided search under time/iteration limits; one modification at a time. Paper includes 2–13-qubit examples. | Inspected scorer uses chi-square threshold 0.01 and Hellinger distance; Qulacs sampling seed is fixed at 42. Passing the supplied test suite terminates search; the paper explicitly limits correctness to that suite. A separate fresh-sample confirmation stage is not established by the inspected path. [Paper §§III–VI][qrep-paper], [execution source][qrep-exec], [search source][qrep-main]. | **Direct overlap:** sampled behavior oracles, bounded gate edits and improvement-driven ranking. Gate-edit repair is prior work; QFAULT's current evidence discipline and narrower one-input contracts must be evaluated on their own merits. |
| **MQT Debugger** | OpenQASM with equality, superposition or entanglement assertions. Equality targets can be vectors or preparation circuits. Simulator debugging exposes statevectors; a separate runtime framework consumes device measurement outcomes and calibration data. | Forward/backward stepping, breakpoints, cone-of-influence, interaction and control-value analysis; assertion refinement. Inspected documentation establishes diagnosis and verification, not a matched automated gate-repair experiment. | Simulator assertions compare state properties; runtime assertions compile to measurement slices with calibration-aware statistical tests, configurable p-value thresholds and estimated shot needs. [Assertions][dbg-assert], [debugging][dbg-debug], [diagnosis][dbg-diag], [refinement][dbg-refine], [runtime verification][dbg-runtime], [debugging paper][dbg-paper], [runtime paper][dbg-runtime-paper]. | **Substantial overlap:** declared properties, diagnostic assistance and measured verification. It would be incorrect to call this tool simulation-only or claim measured assertions are unique to QFAULT. QFAULT adds its particular bounded recovery/report workflow; comparative benefit remains unmeasured. |
| **Muskit** | Sequential Qiskit source, mutation/execution settings, input test cases and specifications listing expected outputs/probabilities. | Generate add/remove/replace gate mutants; select subsets; execute test suites and analyze mutant survival. [README][muskit-readme], [authors' technical report][muskit-paper]. | Repeated test execution; invalid outputs kill mutants, otherwise probability differences are tested against a configured significance level. These are mutation-testing outcomes, not repair certificates. [Specification/oracle documentation][muskit-readme]. | Overlap in gate mutations, sampled distribution testing and fault corpora. Its documented purpose makes it a potential benchmark generator; generated mutants must be filtered for equivalence and contract visibility. Automated restorative repair is not established here. |
| **MQT QCEC** | Two complete circuit descriptions, including a trusted reference; Qiskit circuits or supported QASM inputs. | Full functional equivalence up to global phase; additionally documented partial, parameterized and approximate equivalence modes with restrictions. No repair experiment was performed. | DD construction/alternating checkers can establish equivalence/non-equivalence within numerical semantics; simulation can expose non-equivalence, while ZX rewriting can establish equivalence but be inconclusive. Results include probable/inconclusive outcomes; timeouts and numerical tolerances matter. [Checking methods][qcec-methods], [partial equivalence][qcec-partial], [approximate equivalence][qcec-approx]. | Useful independent oracle when both circuit descriptions exist. Full-unitary checking is a different, generally stronger task than satisfying QFAULT's one-input contract; supplying a reference circuit changes the information available. |
| **QASMBench** | OpenQASM 2 circuit corpus and circuit metrics, with small/medium/large categories. | Benchmark routines across algorithm families; small category is 2–10 qubits, so only a subset fits QFAULT. [Pinned README][qasm-readme], [paper v3][qasm-paper]. | The paper evaluates hardware fidelity through tomography; these are hardware/benchmark results, not a shared diagnosis or recovery score. | External workload source, not a diagnosis or repair competitor. This suite alone supplies neither QFAULT-specific contracts nor labelled fault/control pairs. |

## Version and license record

| Repository | Inspected commit | License at that commit |
|---|---|---|
| [EnautMendi/Qrep](https://github.com/EnautMendi/Qrep) | [`0ca11f2ce6438e51f32020e58b1e2989a52862da`](https://github.com/EnautMendi/Qrep/tree/0ca11f2ce6438e51f32020e58b1e2989a52862da) | [GPL v3 text](https://github.com/EnautMendi/Qrep/blob/0ca11f2ce6438e51f32020e58b1e2989a52862da/LICENSE) |
| [munich-quantum-toolkit/debugger](https://github.com/munich-quantum-toolkit/debugger) | [`3215798849445f3e974ce6589149216b289589cf`](https://github.com/munich-quantum-toolkit/debugger/tree/3215798849445f3e974ce6589149216b289589cf) | [MIT](https://github.com/munich-quantum-toolkit/debugger/blob/3215798849445f3e974ce6589149216b289589cf/LICENSE) |
| [Simula-COMPLEX/muskit](https://github.com/Simula-COMPLEX/muskit) | [`5e697b42c03049cf42fb5aff9a09828c8326a372`](https://github.com/Simula-COMPLEX/muskit/tree/5e697b42c03049cf42fb5aff9a09828c8326a372) | [AGPL v3 text](https://github.com/Simula-COMPLEX/muskit/blob/5e697b42c03049cf42fb5aff9a09828c8326a372/LICENSE) |
| [munich-quantum-toolkit/qcec](https://github.com/munich-quantum-toolkit/qcec) | [`5f0e347db8157caeaed79327dd023f4069873333`](https://github.com/munich-quantum-toolkit/qcec/tree/5f0e347db8157caeaed79327dd023f4069873333) | [MIT](https://github.com/munich-quantum-toolkit/qcec/blob/5f0e347db8157caeaed79327dd023f4069873333/LICENSE) |
| [pnnl/QASMBench](https://github.com/pnnl/QASMBench) | [`357b942396d5c2b7cbc1c229c585a6ef5ccaebac`](https://github.com/pnnl/QASMBench/tree/357b942396d5c2b7cbc1c229c585a6ef5ccaebac) | [Custom Battelle terms](https://github.com/pnnl/QASMBench/blob/357b942396d5c2b7cbc1c229c585a6ef5ccaebac/LICENSE): retain notices/conditions and observe name-use restriction; GitHub reports `NOASSERTION`. |

Commits were resolved through public GitHub repository/commit/tree APIs, then individual files were fetched from commit-addressed raw URLs. Local ignored evidence is under `.local/references/competitors/`: `manifest.json`, per-project API metadata/source snapshots, and the QCEC demonstration artifacts. License descriptions concern inspected repository files; redistribution of individual third-party circuits still requires their provenance review.

## Executed QCEC illustration: stronger reference oracle

An isolated Windows CPython 3.13.2 environment installed binary wheels for `mqt.qcec==3.11.0`, `mqt.core==3.11.0`, `qiskit==2.5.2` and `numpy==2.5.4`; `pip check` passed. The executed QCEC release is [tag v3.11.0, commit `844a67c94159ae97d1c4cc01501fbdd98a84a730`](https://github.com/munich-quantum-toolkit/qcec/tree/844a67c94159ae97d1c4cc01501fbdd98a84a730), distinct from the inspected development commit above. A two-qubit Bell-preparation circuit was supplied as the trusted reference; the construction checker ran serially with a five-second timeout.

| Candidate relative to Bell preparation | Actual QCEC verdict | Exact zero-input interpretation |
|---|---|---|
| Append two cancelling X gates | `equivalent` | Same state and Z probabilities |
| Remove CX | `not_equivalent` | Different state and Z probabilities |
| Append Z to one qubit | `not_equivalent` | Same Z probabilities, orthogonal state |
| Prepend Z before preparation | `not_equivalent` | Same zero-input state, different unitary |

All four assertions passed. The state/probability interpretation uses privileged Qiskit Statevector calculations, not measured QFAULT outcomes. In particular, the last row explains why even a perfect target-state contract for one input cannot substitute for full-unitary equivalence. This is an oracle-boundary demonstration, not an equal-information competitor trial, scalability test or repair ranking.

The tracked [reproduction script](../scripts/compare_qcec_scope.py) and [actual compact record](../benchmarks/qcec-scope-v1.json) contain the complete reference and four candidate QASM inputs, verdicts, source/input SHA-256 values, environment and task/oracle scope. The record's payload digest checks internal consistency; it is not a signature. Timestamps and payload digests can change on rerun; the four verdicts are the expected comparison.

Reproduce from the repository root in PowerShell, without changing QFAULT's dependencies:

```powershell
py -3.13 -m venv .local/qcec-scope-env
& .\.local\qcec-scope-env\Scripts\python.exe -m pip install --only-binary=:all: mqt.qcec==3.11.0 mqt-core==3.11.0 qiskit==2.5.2 numpy==2.5.4 scipy==1.18.1 rustworkx==0.18.1 dill==0.4.1 stevedore==5.9.1 typing-extensions==4.16.0 nanobind-backend==1.0.0
& .\.local\qcec-scope-env\Scripts\python.exe -m pip check
& .\.local\qcec-scope-env\Scripts\python.exe -B scripts/compare_qcec_scope.py --output .local/qcec-scope-rerun.json
```

On Linux/macOS, create the environment with `python3.13 -m venv .local/qcec-scope-env` and replace each PowerShell interpreter invocation with `.local/qcec-scope-env/bin/python`; this demonstration was executed on Windows only. The script refuses existing output files. The release commit above pins source inspection; installation uses the named published wheels, whose download hashes are retained in local `qcec-install.json`.

Additional ignored raw records under `.local/references/competitors/` include `qcec-demo.json` (checker statistics), source snapshots, `source-files.sha256.json`, QASM files, `qcec-install.json`, `qcec-freeze.txt` and `qcec-install.log`. They are supplementary: the tracked script and record suffice to inspect and rerun the demonstration. Qrep, Debugger and Muskit were source-reviewed, not installed or rerun; their published evaluation claims were not reproduced here.
## Why no fair ranking follows

No shared benchmark run with matched information access, fault distribution, budgets, contracts and acceptance rules was completed. QRep's full input coverage differs from QFAULT's single-input contracts; QCEC sees the reference circuit; Debugger's assertions and runtime calibration differ; Muskit measures test-suite quality; QASMBench provides workloads. Shot counts, time budgets, candidate sets and noise conditions are also different. Comparing published success percentages or treating an inconclusive result as failure would manufacture a ranking.

The present evidence supports a narrow positioning: QFAULT integrates small simulated contract investigations, explicit information boundaries, bounded measured intervention screening, independent confirmation and consistency-checkable records. It does not establish novel gate-edit repair, unique measured assertions, superior diagnosis, hardware readiness or a state-of-the-art advantage. A future comparison with QRep would need the same observable oracle, inputs, candidate edits, shot accounting and fresh acceptance test, with adaptation documented separately from the original algorithm.

[qrep-paper]: https://arxiv.org/html/2603.25587v2
[qrep-exec]: https://github.com/EnautMendi/Qrep/blob/0ca11f2ce6438e51f32020e58b1e2989a52862da/circuitExecution.py
[qrep-main]: https://github.com/EnautMendi/Qrep/blob/0ca11f2ce6438e51f32020e58b1e2989a52862da/main.py
[dbg-assert]: https://github.com/munich-quantum-toolkit/debugger/blob/3215798849445f3e974ce6589149216b289589cf/docs/assertions.md
[dbg-debug]: https://github.com/munich-quantum-toolkit/debugger/blob/3215798849445f3e974ce6589149216b289589cf/docs/debugging.md
[dbg-diag]: https://github.com/munich-quantum-toolkit/debugger/blob/3215798849445f3e974ce6589149216b289589cf/docs/diagnosis.md
[dbg-refine]: https://github.com/munich-quantum-toolkit/debugger/blob/3215798849445f3e974ce6589149216b289589cf/docs/assertion_refinement.md
[dbg-runtime]: https://github.com/munich-quantum-toolkit/debugger/blob/3215798849445f3e974ce6589149216b289589cf/docs/runtime_verification.md
[dbg-paper]: https://arxiv.org/abs/2412.12269v1
[dbg-runtime-paper]: https://arxiv.org/abs/2505.03885v1
[muskit-readme]: https://github.com/Simula-COMPLEX/muskit/blob/5e697b42c03049cf42fb5aff9a09828c8326a372/README.md
[muskit-paper]: https://web-backend.simula.no/sites/default/files/publications/files/quantum_mutation_tool_ase_tr.pdf
[qcec-methods]: https://github.com/munich-quantum-toolkit/qcec/blob/5f0e347db8157caeaed79327dd023f4069873333/docs/equivalence_checking.md
[qcec-partial]: https://github.com/munich-quantum-toolkit/qcec/blob/5f0e347db8157caeaed79327dd023f4069873333/docs/partial_equivalence.md
[qcec-approx]: https://github.com/munich-quantum-toolkit/qcec/blob/5f0e347db8157caeaed79327dd023f4069873333/docs/approximate_equivalence_checking.md
[qasm-readme]: https://github.com/pnnl/QASMBench/blob/357b942396d5c2b7cbc1c229c585a6ef5ccaebac/README.md
[qasm-paper]: https://arxiv.org/abs/2005.13018v3


