# QFAULT

**Quantum Failure Analysis & Recovery Workbench**

QFAULT investigates an unexpected quantum result, separates supported logical and noise explanations, and tests a bounded repair against a declared contract.

The one-line inference is: **“This result disagrees with the contract; here is the measured evidence, the explanations it supports, and what an independently checked recovery changed.”**

This is working local software with real Qiskit circuits, not a mock dashboard. All execution is simulated. No IBM hardware, paid service, external model, deployment or quantum-advantage claim is involved.

## Implemented

- Bell, GHZ and small QFT templates; 2–5 qubits, Bell restricted to two.
- Analytic fixed-input state contracts, finite-shot sampling, TV disagreement bounds and explicit limitations.
- Valid gate removal/replacement, angle changes and qubit reassignment; phase controls and mixed/noisy scenarios.
- Analyst inputs exclude evaluator truth. Supported diagnoses include noise consistency, logical defects, mixed ambiguity and insufficient evidence.
- Four deterministic diagnostic policies with shot/evaluation ceilings and an explicit resource ledger.
- At most 256 one-edit repair candidates. Fresh validation samples plus a separately implemented density-matrix check can verify, reject or leave a proposal inconclusive.
- CLI, localhost FastAPI, React/TypeScript/Vite workbench, immutable JSON artifacts, hash verification, report export and append-only human review.
- A six-scene live demo, tamper/restore demonstration and reproducible policy benchmark.

Ideal sampling uses **Qiskit 2.3.1 BasicSimulator**. Gate noise uses **Qiskit DensityMatrix/Kraus**, with a classical symmetric readout channel. **Aer is unavailable in the verified environment** because its local binary targets CPython 3.11 and the accessible runtime is 3.13. This fallback is explicit throughout the execution records.

## Run now in this verified workspace

From C:\Projects\QFF, PowerShell:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault circuits
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault demo
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 pytest tests -q -p no:cacheprovider
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault serve
~~~

Open **http://127.0.0.1:8000/**. The interface is already built locally. Stop the server with Ctrl+C when you start it yourself. It binds only localhost.

The machine-specific launcher uses the existing LibreOffice Python 3.13.15 runtime and reads compatible installed packages from two existing local package directories. It sets PYTHONDONTWRITEBYTECODE and does not modify those projects. This is an environment bridge, not an isolated installation. Exact paths and limitations are in scripts/local_bootstrap.py and docs/environment.json.

To check or rebuild the interface with the verified existing tools:

~~~powershell
node scripts/check-web.mjs C:/Projects/Quantum_Simulator/frontend/node_modules
node scripts/build-web.mjs C:/Projects/Quantum_Simulator/frontend/node_modules
~~~

No dependencies need to be downloaded for the current local demonstration. Browser automation could not be executed because no connected browser was available. The frontend typecheck/build and real API integration passed; responsive layouts and interactive UI flows still need browser verification.

## Standard installation on another machine

The following is the standard installation procedure; **a fresh network installation was not rehearsed in this sandbox**. Direct network downloads failed. The exact observed Python dependency closure is requirements-tested.txt; frontend direct versions are in web/package.json.

~~~powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-tested.txt
.venv\Scripts\python -m pip install --no-deps -e .
npm.cmd --prefix web install
npm.cmd --prefix web run check
npm.cmd --prefix web run build
.venv\Scripts\python -m pytest tests -q
.venv\Scripts\python -m qfault demo
.venv\Scripts\python -m qfault serve
~~~

Use CPython 3.13 for the recorded dependency set. No Docker or external services are required. A portable wheel and fresh-install dependency resolution remain release tasks; no npm lockfile is claimed.

## CLI workflow

In a normal installed environment, use python -m qfault. Here, prefix the same arguments with the verified PowerShell launcher above.

~~~powershell
python -m qfault circuits
python -m qfault contract bell
python -m qfault run --family bell --scenario remove --seed 7
python -m qfault run --family ghz --scenario readout
python -m qfault run --family qft --scenario angle --policy fixed
python -m qfault run --scenario remove --max-shots 4096 --max-evaluations 2
~~~

The last command demonstrates budget-driven abstention. RunRequest validates families, bounds, noise scenarios and budgets before execution. No arbitrary Python uploads are executed.

A run prints its real experiment_id. Use that value in the following commands (replace EXPERIMENT_ID):

~~~powershell
python -m qfault inspect EXPERIMENT_ID
python -m qfault analyze EXPERIMENT_ID
python -m qfault recovery EXPERIMENT_ID
python -m qfault verify EXPERIMENT_ID
python -m qfault export EXPERIMENT_ID investigation-export.json
python -m qfault review EXPERIMENT_ID --reviewer PrathamKapoor --reason "Inspected validation evidence"
~~~

analyze and recovery inspect the recorded decisions; they do not silently rerun experiments. The run command performs diagnosis and optional recovery. verify-repair independently tests a validated structured Circuit JSON file:

~~~powershell
python -m qfault verify-repair candidate.json --family bell --shots 2048 --seed 10007
~~~

Exports refuse to overwrite an existing file. Optional --store precedes the artifact command, for example python -m qfault --store artifacts/custom demo.

## Demo and benchmark

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault demo
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault benchmark --out artifacts/new-benchmark
~~~

The benchmark destination must not already exist; runs never overwrite prior evidence. The live demo executes healthy Bell, missing-gate repair, readout-only control, mixed GHZ, clean QFT and a phase fault under the fixed plan. It then alters a dedicated throwaway result, checks failure, restores the original bytes and checks success. Its measured record is benchmarks/demo.json.

The frozen protocol is docs/benchmark-protocol.md. Actual raw records are under artifacts/release-benchmark/investigations/; the committed row-level summary is benchmarks/results.json. Runs under artifacts/benchmark-reproduction and artifacts/release-benchmark reproduced the scientific metrics; benchmarks/reproduction.json records the comparison. IDs, timestamps, runtimes and associated hashes are intentionally not byte-identical.

| Policy | Correct category | Total shots | Circuit evaluations |
|---|---:|---:|---:|
| Evidence-triggered | 47/75 | 343,040 | 220 |
| Fixed plan | 66/75 | 384,000 | 300 |
| Random admissible | 23/75 | 343,040 | 196 |
| Simple threshold | 47/75 | 307,200 | 186 |

Evidence-triggered accuracy is 62.7% (descriptive Wilson 95% interval 51.4–72.7%); fixed-plan accuracy is 88.0% (78.7–93.6%). Random abstained on 24/75 cases. No false positive occurred on the 12 evaluator-defined correct cases per policy (95% upper bound 24.2%); nine are explicitly clean scenarios, three are equivalent mutations. This does not establish a zero population false-positive rate.

The fixed plan wins on category accuracy; the simple threshold ties the proposed policy using fewer shots. **The proposed policy has no demonstrated superiority.** Measurement-triggered diagnosis misses phase-only and other distribution-preserving faults. Configured noise can be invisible under a uniform QFT output distribution.

All 6 selected Bell/GHZ missing-gate recovery trials verified (Wilson 95% interval 61.0–100%). This is a narrow six-trial corpus, not a general repair-success claim. Original distribution quality ranged from 0.4707 to 0.5000; independently sampled repaired quality ranged from 0.9941 to 0.9985. Quality means 1−TV. Each consumed 7,168 shots; Bell used 28 evaluations and GHZ 61.

## API and data

Actual routes are documented at http://127.0.0.1:8000/docs. They include /api/health, /api/circuits, /api/contracts/{family}/{n}, /api/experiments, experiment detail/verification/report/review, and /api/benchmark plus its report download. Each request executes a bounded local workflow; only one investigation runs at a time in the supported single-process server.

Artifact directories contain investigation.json, separate evaluator-only evaluation.json, manifest.json with review membership hashes and immutable review records. Original submitted circuits are never edited in place. SHA-256 checks detect covered changes relative to the manifest; there is no signed receipt or external trust anchor.

## Scientific and engineering limits

- State contracts cover a single input, not full unitary equivalence. Matching counts cannot certify phases.
- Ideal-state diagnostic probes require privileged local simulation. Hardware tomography, MQT QCEC and IBM hardware execution are not implemented.
- Noise attribution establishes consistency, not unique causal identification. No temporal drift detection or forecasting is implemented.
- Measurement mitigation, ML-DSA signing and authenticated review are unavailable.
- Repair is bounded and incomplete; no successful candidate is guaranteed. Validation can reject an ideal repair under noise or remain inconclusive.
- The small benchmark repeats fixed circuits at three seeds. Its Wilson intervals are descriptive; unseen-circuit generalization and statistical superiority are unestablished.
- A crash during multi-file persistence can leave a partial directory; verification reports it incomplete. Mid-investigation failure checkpointing is limited to API failure records, not every intermediate quantum result.
- The supported server is localhost-only, one process. Browser interaction tests, isolated installation, packaging portability and npm lockfile validation remain unfinished.

## Sources and documents

QFAULT combines evidence/review design lessons from SAT-SA/Closure-Trace, causal-evaluation discipline from QuantumAttack, QFT convention checks from QFT-Lab and shot-versus-bias/resource lessons from Q-TRUST. These are conceptual adaptations; no donor implementation was copied. Existing mutation testing, circuit equivalence and mitigation are prior art. No novelty or quantum-advantage claim is made.

See docs/reuse-inventory.md, docs/prior-art.md, docs/methodology.md and THIRD_PARTY_NOTICES.md for verified sources, revisions, licenses and dependency choices. Product code is MIT licensed.

Operational continuity: decisions.md, flow.md and handoff.md. Reproduction evidence: benchmarks/results.json, benchmarks/reproduction.json, benchmarks/demo.json and local raw artifacts.
