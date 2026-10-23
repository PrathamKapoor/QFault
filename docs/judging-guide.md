# Demonstrating QFault

QFault helps a developer compare a small circuit with independently declared
behavior, inspect measured disagreement, test bounded edits and check a selected
edit using fresh original/candidate measurements. Its contribution is the
integrated workflow and inspectable evidence, not a claim to be the first
quantum debugger, universal repair or hardware validation.

## First screen

Select **Guided demo** on the landing page or workbench. No JSON assembly is
required. The main example imports the pinned four-qubit QASMBench QRNG program.
Source, original reference, controlled terminal-Z candidate and contract provenance
are shown separately. This product-state example demonstrates observability,
not representative recovery accuracy.

Release: [v0.1.0](https://github.com/PrathamKapoor/QFault/releases/tag/v0.1.0).
Asset manifests identify their exact source commit. Later documentation on main
does not change those packages or move the release tag.

## Setup

Use CPython 3.13 and Node 24. No provider key, paid service or database is required.
From a fresh clone or extracted project directory on Windows:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
npm --prefix web ci
npm --prefix web run check
npm --prefix web run build
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m scripts.aer_smoke
.\.venv\Scripts\python.exe -m qfault serve --port 8000
```

On Linux use `python3.13 -m venv .venv` and `.venv/bin/python` for Python commands.
Open <http://127.0.0.1:8000/#/demo>. Keep the terminal running. Choose another free
port if needed and pass that same URL to demonstration tools. Simulation consumes
CPU, memory and runtime without a provider charge. This is a local single-process
workbench, not an unauthenticated Internet service.

## Live investigation

1. **Circuit and reference.** Inspect the unchanged external source and imported
   reference. The controlled candidate appends Z on qubit 0. Contracts come from
   the separately parsed original, whose correctness/Qiskit semantics are assumed.
2. **Z-only measurement.** Inspect feasibility and run the actual request. The
   phase change leaves the 16 computational probabilities unchanged. Supporting
   this distribution does not mean the circuit is universally correct.
3. **Complementary evidence.** Execute the independent X-basis claims. Inspect
   returned discrepancy, intervals, alpha assumptions and actual cost. No exact
   candidate state enters the measured policy.
4. **Bounded interventions.** Inspect operators, palette, 32-candidate ceiling,
   exclusions/truncation and 200,000-shot ceiling. Structural previews have not
   been measured. The complete proposal list is available on demand.
5. **Freeze and verify.** The engine screens edits, freezes selection, then
   freshly measures both original and candidate inside one operation. The UI
   does not pretend to pause it. Inspect the diff, plausible overlaps, selection
   digest and fresh costs. Normalized loss/improvement uses tolerance units.
6. **Inspect and export.** Download the real report and check stored integrity.
   Independently verify downloaded bytes below. Replay/new-seed rerun creates
   another parent-linked investigation, never overwriting the original.

A failed request never advances a success stage. Connection loss after submission
leaves completion unknown; refresh does not cancel or retry it. Inspect history
before explicitly starting a new guide. Completed IDs restore from the server;
one unavailable record does not discard valid siblings.

## Negative demonstrations

**Noise-control abstention:** run the same imported candidate with declared
symmetric readout noise 0.3. The separate zero-state control causes an edit to be
withheld. It does not exclude every gate/state-dependent noise process. Inspect
actual cost and export; this is not a successful repair.

**Insufficient budget:** the 128-shot ceiling cannot cover fresh paired
confirmation plus initial observation and possible control. Admission refuses
with zero shots/executions. Return to the main guide or configure a feasible
budget in the custom laboratory.

## Same-engine text fallback

With the local server running, using the activated environment or its interpreter:

```powershell
python -m scripts.guided_demo --base http://127.0.0.1:8000 --out artifacts/my-guided-demo
python -m qfault verify-report artifacts/my-guided-demo/recovery-report.json
```

The command fetches the same inputs, validates/executes all five real requests and
verifies every exported report. A new output directory is required. Unexpected
outcomes return nonzero and remain recorded. The tiny native H/Z introduction
remains available as `scripts.judging_demo`; it is not the main external example.

If the live backend is unavailable, announce **recorded evidence**, play the
released silent footage with the [complete narration](three-minute-demo.md), then
inspect/verify released demonstration reports. Never call recorded results fresh
execution. Silent footage has no recorded voiceover.

## Interpret the research

The frozen `external-qasmbench-v1` summary drives displayed values. Conservative
and point ranking both verified **10/90 overall and 10/41 eligible**. Rejected
proposals were **8 versus 31**, shots **5,337,088 versus 5,902,336**: approximately
**9.6% fewer shots with equal verified yield**. These are small, correlated
simulated cases from nine holdout source programs. Repeated seeds are not
independent circuit families; rejected proposals are not falsely verified repairs.
No population superiority is established.

The 72/72 replication result checks scientific consistency, not repair accuracy
or a new untouched holdout. It was evaluated at
`97710d834abeef93f0094b169a05d182f22c8434`; current presentation routes postdate
its source guard. Use that recorded commit for its exact rerun, or this release's
offline archive verifiers. Never edit old fingerprints.

## Review downloaded packages

Each outer source/evidence ZIP contains `manifest.json` and `qfault-source.zip`.
Source-only deliberately omits raw report archives and marks evidence incomplete.
Full mode covers the three explicitly available archives; other historical raw
families remain unavailable as documented in `docs/evidence-availability.md`.

Compare assets with `SHA256SUMS`. From installed source, safely verify/extract:

```powershell
python -m scripts.release_delivery verify --archive qfault-v0.1.0-evidence.zip --out reviewed-package
```

The new destination contains `project/` for setup and `package/` retaining
the original manifest/ZIP. Alternatively expand reviewed outer/inner ZIPs into
independent empty directories, follow setup, then run
`scripts.package_submission --verify` against the outer manifest directory.

```powershell
python -m scripts.verify_external_results benchmarks/external-holdout-v1/summary.json
python -m scripts.verify_recovery_archive
python -m scripts.verify_replication
```

Source-only cannot verify raw archives it omits. Unsigned SHA-256/CRC checks
establish consistency, not authenticity, trusted timestamps or scientific truth.
Preserve third-party notices.

The complete Python suite expects the available raw archives, so use the
evidence-inclusive package for that gate. Source-only representative checks are:

```powershell
python -m pytest tests/test_guided_demo.py tests/test_native_import.py tests/test_release_delivery.py -q
python -m scripts.aer_smoke
```

## Limits to say aloud

One input/contract; finite incomplete measurements; bounded edits; ambiguous cause;
IID/stationarity and measurement-model assumptions; cooperative between-job time
guards; local simulation only. Dense targets/inadequate budgets may remain
unresolved. No hardware validation, universal equivalence, guaranteed competition
outcome or specific competition eligibility is claimed.
