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
- Five deterministic diagnostic policies with shot/evaluation ceilings and an explicit resource ledger.
- At most 256 one-edit repair candidates. Fresh validation samples plus a separately implemented density-matrix check can verify, reject or leave a proposal inconclusive.
- CLI, localhost FastAPI, React/TypeScript/Vite workbench, immutable JSON artifacts, hash verification, report export and append-only human review.
- A six-scene live demo, tamper/restore demonstration and reproducible policy benchmark.

**Qiskit 2.3.1 and Aer 0.17.2 execute locally.** Choose the reference backend (BasicSimulator / DensityMatrix-Kraus plus symmetric readout flips) or AerSimulator density_matrix with explicit gate/readout noise. Reports identify the actual backend; no requested Aer failure silently falls back. Reference remains default to preserve existing experiments. The original cp311 Aer mismatch was fixed by locating and executing a separate matching cp313 installation; see [environment audit](docs/environment-stabilization.md). Fresh isolated installation is still blocked.

The phase policy adds sampled X-parity or analytic Fourier-product-basis witnesses, with basis-gate noise and resource costs. Exact logical attribution still uses privileged simulation. Fixed remains the default policy; phase is an explicit higher-cost option.

## Normal installation path

**Not yet independently verified here.** A project-owned npm lockfile could not be generated: official registry connections are denied with EACCES and offline resolution lacks metadata. No clean-install readiness is claimed. On a machine with permitted official package access, use standard64-bit CPython3.13 and Node24 (24.19.0/npm11.17.0 tested). Python metadata requires3.12+, but the quantum application was executed only on3.13. No Docker or services are needed.

From the repository root, PowerShell:

~~~powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-browser-tested.txt
.venv\Scripts\python -m pip install --no-deps -e .
npm.cmd --prefix web install --package-lock-only
npm.cmd --prefix web ci
npm.cmd --prefix web run check
npm.cmd --prefix web run build
.venv\Scripts\python -m pytest tests -q
.venv\Scripts\python -m scripts.submission_demo --out artifacts/fresh-demo --backend aer
.venv\Scripts\python -m qfault serve
~~~

The npm resolution command must succeed and produce a complete lockfile before ci; preserve and review that generated lockfile. These are pending normal installation commands, not successful commands from this sandbox. They resolve only QFAULT's own manifests; no neighboring repository is used. There is no declared lint command. See [release attempt evidence](docs/release-candidate.md).

Open http://127.0.0.1:8000/. In a second terminal install official browser assets with .venv\Scripts\python -m playwright install chromium, then run .venv\Scripts\python -m scripts.browser_e2e --out artifacts/fresh-browser. The requirements files pin the observed runtime/test/Aer/browser closure; they are not a verified isolated resolver result. Actual local success and installation failure are separated below.

## Development-only fallback in this workspace

From C:\Projects\QFF, PowerShell:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault circuits
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 scripts.submission_demo --out artifacts/my-demo --backend aer
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 pytest tests -q -p no:cacheprovider
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault serve
~~~

Open **http://127.0.0.1:8000/**. The interface is already built locally. Stop the server with Ctrl+C when you start it yourself. It binds only localhost.

The machine-specific launcher uses the existing LibreOffice Python 3.13.15 runtime and reads compatible installed packages from existing local package directories, including only the matching Aer package from a separate user installation. It sets PYTHONDONTWRITEBYTECODE and does not modify those projects. This is an unsupported development-only environment bridge, not an isolated installation or the normal install path. Exact paths and limitations are in scripts/local_bootstrap.py and docs/environment.json.

To check or rebuild the interface with the verified existing tools:

~~~powershell
node scripts/check-web.mjs C:/Projects/Quantum_Simulator/frontend/node_modules
node scripts/build-web.mjs C:/Projects/Quantum_Simulator/frontend/node_modules
~~~

No dependencies need to be downloaded for the current local demonstration. Standalone Playwright1.62.0 with installed Chromium151.0.7922.34 now passes the real browser workflow: configured GHZ4/QFT4 and Bell runs, fault diagnosis, independent repair display, noise/abstention controls, export download/verification, refresh/history, loading, invalid-budget422 display and390px mobile layout. There are no unexpected console/page/request failures. The connected browser remains unavailable; the user's requested local Playwright fallback executed successfully. Screenshots remain local under artifacts/browser-delivery. See [browser evidence](benchmarks/browser-verification.json).

## Repeat the verified browser workflow

Keep the local server running, then execute:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.browser_e2e --out artifacts/my-browser-check
~~~

This separate machine-specific launcher reads installed Playwright packages and uses a cached headless Chromium; it does not alter the quantum server's dependency paths. The script rejects an existing output directory and preserves actual API results, downloaded report, screenshots and a summary. See [browser QA](docs/browser-verification.md).

In a normal environment install the optional browser extra or requirements-browser-tested.txt, install its official Chromium with python -m playwright install chromium, and run python -m scripts.browser_e2e --out artifacts/new-browser-check. Fresh installation of those dependencies/browser is not claimed here.

## CLI workflow

In a normal installed environment, use python -m qfault. Here, prefix the same arguments with the verified PowerShell launcher above.

~~~powershell
python -m qfault circuits
python -m qfault contract bell
python -m qfault run --family bell --scenario remove --policy phase --backend aer --seed 7
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
python -m qfault verify-report investigation-export.json
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

The benchmark destination must not already exist; runs never overwrite prior evidence. The legacy qfault demo executes healthy Bell, missing-gate repair, readout-only control, mixed GHZ, clean QFT and a phase fault under the fixed plan. It then alters a dedicated throwaway result, checks failure, restores the original bytes and checks success. Its historical measured record is benchmarks/demo.json. The new scripts.submission_demo rehearsal uses actual Aer, complementary phase evidence and fresh Z/phase repair validation; its measured output is benchmarks/submission-demo.json. Use a new destination each time. See [judging script](docs/demo.md).

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

## Frozen diagnostic comparison

The original benchmark above remains unchanged. A separate configuration was committed before implementation; development seed71 and final seeds103/211 are disjoint. The final reference-backend corpus has68 cases/policy and equal8192-shot/6-evaluation ceilings. All metrics reproduced on the current release without replacing authoritative artifacts.

| Policy | Correct | Actual shots | Evaluations |
|---|---:|---:|---:|
| Original evidence | 34/68 | 303,104 | 184 |
| Fixed | 58/68 | 348,160 | 272 |
| Random | 21/68 | 303,104 | 171 |
| Threshold | 34/68 | 278,528 | 162 |
| Phase evidence | 66/68 | 487,424 | 328 |

Phase accuracy has descriptive Wilson95% interval89.9–99.2%; fixed75.0–91.8%. Phase costs40% more shots and still misses two QFT2 angle faults; fixed catches those with unconditional exact-state checks. Zero false diagnoses among10 evaluator-correct cases has Wilson upper27.8%. No statistical superiority or unseen-algorithm guarantee is claimed. Paired outcomes:56 both correct,10 phase-only correct,2 fixed-only correct,0 both wrong; these are descriptive, not a significance claim. See [paired raw-artifact audit](benchmarks/paired-policy-audit.json). See [findings and confusion matrices](docs/diagnostic-findings.md), [measured tradeoff](benchmarks/policy-tradeoff.svg) and [raw-linked final summary](benchmarks/diagnostic-final.json).

Selected recovery now covers12 missing-gate/phase trials:10 verified,2 QFT4 inconclusive, plus2 rejected negative controls. Wilson95% interval55.2–95.3% applies only to this selected corpus. Validation uses independent DensityMatrix evolution and new Z/phase samples; total11264 shots/case. The original6/6 finding remains narrow.

Verified local reproduction commands (new destinations required):

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault evaluate --split development --out artifacts/new-development
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault evaluate --split final --out artifacts/new-final
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault evaluate --split low_shot_control --out artifacts/new-low-shot
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 scripts.evaluate_recovery --out artifacts/new-recovery
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 scripts.compare_backends --out artifacts/new-backend-check
~~~

In a normal installed environment replace the PowerShell prefix with python -m. Optional plotting: install a compatible Matplotlib (3.10.3 executed here) and run python scripts/plot_policy_tradeoff.py. Plotting is not a runtime dependency. See [release gates](docs/release-gates.md) for incomplete installation checks and verified browser scope.

## API and data

Actual routes are documented at http://127.0.0.1:8000/docs. They include /api/health, /api/circuits, /api/contracts/{family}/{n}, /api/experiments, experiment detail/verification/report/review, /api/benchmark plus its report download, and /api/evaluation with the frozen final report. Each request executes a bounded local workflow; only one investigation runs at a time in the supported single-process server.

Artifact directories contain investigation.json, separate evaluator-only evaluation.json, manifest.json with review membership hashes and immutable review records. Original submitted circuits are never edited in place. SHA-256 checks detect covered changes relative to the manifest; there is no signed receipt or external trust anchor.

## Scientific and engineering limits

- State contracts cover a single input, not full unitary equivalence. Matching counts cannot certify phases. Complementary witnesses can reveal some relative phases but remain incomplete.
- Ideal-state diagnostic probes require privileged local simulation. Hardware tomography, MQT QCEC and IBM hardware execution are not implemented.
- Noise attribution establishes consistency, not unique causal identification. No temporal drift detection or forecasting is implemented.
- Measurement mitigation, ML-DSA signing and authenticated review are unavailable.
- Repair is bounded and incomplete; no successful candidate is guaranteed. Validation can reject an ideal repair under noise or remain inconclusive.
- The small benchmark repeats fixed circuits at three seeds. Its Wilson intervals are descriptive; unseen-circuit generalization and statistical superiority are unestablished.
- A crash during multi-file persistence can leave a partial directory; verification reports it incomplete. Mid-investigation failure checkpointing is limited to API failure records, not every intermediate quantum result.
- The supported server is localhost-only, one process. Isolated installation, packaging portability and npm lockfile validation remain unfinished. Browser coverage is limited to the tested Chromium desktop/mobile sizes.

## Sources and documents

QFAULT combines evidence/review design lessons from SAT-SA/Closure-Trace, causal-evaluation discipline from QuantumAttack, QFT convention checks from QFT-Lab and shot-versus-bias/resource lessons from Q-TRUST. These are conceptual adaptations; no donor implementation was copied. Existing mutation testing, circuit equivalence and mitigation are prior art. No novelty or quantum-advantage claim is made.

See docs/reuse-inventory.md, docs/prior-art.md, docs/methodology.md and THIRD_PARTY_NOTICES.md for verified sources, revisions, licenses and dependency choices. Product code is MIT licensed.

Current release checks and exact failures: [release candidate audit](docs/release-candidate.md). The required privileged calculations are mapped in [simulator information audit](docs/simulator-information-audit.md).

Operational continuity: decisions.md, flow.md and handoff.md. Reproduction evidence: benchmarks/results.json, benchmarks/reproduction.json, benchmarks/demo.json and local raw artifacts.
