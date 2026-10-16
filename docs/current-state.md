# Current scientific and release state

Updated 2026-10-16. This index supersedes earlier status snapshots; it does not
rewrite their experiments or erase recorded failures.

| Topic | Current evidence |
|---|---|
| Published release | `35cbbb9b351ef2ef4e42163b969c5331dc116eba`; six reviewed commits published by normal fast-forward. Both [hosted CI jobs](https://github.com/PrathamKapoor/QFault/actions/runs/38787130996) passed. |
| New research | Local `research/external-validation`; scientific corrections, external corpus and results remain unpublished. No history rewrite or force push in this assignment. |
| Information boundaries | [Adversarial audit](information-boundary-audit.md), policy-only configuration, real Aer tests, blind truth projection and fresh-sample checks. Trusted application data-flow boundaries, not a sandbox for malicious Python code. |
| Witness validity | Ideal calibrated common-state measurements support conditional fidelity bounds. Declared uncalibrated readout/analysis noise withholds state certification; distribution/Pauli outcome tests retain their operational scope. |
| External validation | [Pinned protocol, results and reproduction](external-validation.md): nine holdout source programs, 1,962 diagnostic and 270 recovery rows, 2,206 verified raw exports. Small simulated circuits only. |
| Prior work | [Source-backed comparison](competitor-comparison.md), including Qrep's measured repair overlap, MQT Debugger's measured runtime assertions, Muskit and QCEC. No superiority ranking. |
| Observability | [Five explicit examples](../benchmarks/identifiability-v1.json), real reference/Aer counts and exact evaluator proofs; more shots cannot resolve structurally identical observations. |
| Authenticity | Reports provide unsigned SHA-256 consistency. Reviewer names are self-declared. No authenticated author, trusted timestamp or scientific validity proof is supplied. |
| Hardware | NOT TESTED. No credentials inspected and no hardware jobs submitted. |

The README describes current product use. Older release, frontend, environment,
competition and handoff sections are dated history. Statements such as “Aer
unavailable”, “recovery unsupported”, or “publication blocked” in those documents
describe their recorded revisions. Current measured recovery is a separate
laboratory action; it does not run automatically during diagnosis.

Windows clean-clone installation, TypeScript/build, 335 Python tests, source and
all raw report checks, and deterministic Aer smoke passed for the research code.
Full Windows Chromium regressions passed, including the approved hero,
handover/PixelSwap, reduced motion/fallback, existing workbench, blind challenge,
target lab, recovery, history/replay/export, and external QRNG editor workflow.
Linux clean-clone locked installation, frontend check/build, 335 tests, source
checks and Aer smoke also passed on Ubuntu 26.04/WSL2, Python 3.13.15 and Node
24.19.0. Linux research browser coverage and macOS remain untested.
The Linux clean clone also completed 620 development investigations/recoveries
across five programs without execution errors. The final nine-program holdout
was executed on Windows, rather than being claimed as a Linux holdout replication.
The public release's Ubuntu CI is verified, while new local research has no
hosted CI run. Existing warnings are the Starlette/httpx deprecation and the
large lazy Three.js chunk.
