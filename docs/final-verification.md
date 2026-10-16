# Final adversarial publication gate

**GO for the documented bounded simulator scope. No unresolved CRITICAL or HIGH
finding was reproduced. Publication requires the owner's separate authorization.**

The tested implementation is `be64f29fa7e8694bbeddf94329fc0c46c4591617`.
The subsequent verification record and documentation commit adds no scientific
logic. Public main remains `35cbbb9b351ef2ef4e42163b969c5331dc116eba`.
Nothing from this gate was pushed, merged, rebased or force-pushed.

The [machine-readable record](../benchmarks/final-adversarial-verification-v1.json)
contains exact commands, revisions, tool versions, reconciliation identities,
metrics, source digests and new replication outcomes. Large temporary logs,
fresh exports and browser captures remain under `.local/final-gate/`.

## Independent evidence reconciliation

| Partition | Records |
|---|---:|
| Diagnostic rows | 1,962 |
| Recovery rows | 270 |
| Total evaluation rows | 2,232 |
| Unsupported rows without an executed investigation | 26 |
| Executed diagnostic investigations | 1,936 |
| Executed recovery investigations | 270 |
| Unique investigation IDs / exported reports / verified reports | 2,206 each |
| Duplicate IDs, missing exports or omitted frozen cases | 0 |

All 26 exclusions are `small/qrng_n4/qrng_n4.qasm`, variant
`remove_entangler`, seeds `91001` and `91002`, across the protocol's 13
contract/policy combinations. That four-H circuit contains no entangler. These
cases have no investigation ID; the record lists every concrete case key,
category and original reason. No fabricated identifiers are assigned.

`scripts.reconcile_external_evidence` checks the complete Cartesian case grid
from the pinned corpus and protocol, including nonexecuted cases. It rejects
missing rows, duplicate IDs and missing/extra exports. Payload verification
remains the separate `scripts.verify_external_results` command. Independently
recounted actual executions total **11,223**, with **17,438,016 sampled shots**.

## Scientific checks

The audit traced target construction, sampled observation, adaptive planning,
candidate screening, frozen selection and fresh verification. Existing real-Aer
tests poison privileged exact-state helpers and evaluator metadata. The analyst
receives declared contracts and sampled counts; target-only decomposition remains
a permitted trusted input. No candidate-state or hidden-truth leak was found.

Independent reconstruction checked 5,608 distribution/Pauli estimates, 12,035
target witness means/radii, 1,871 intermediate target bounds, 2,466 recovery loss
intervals and all 59 selected fresh comparisons. All **530 checkable target
intervals** contain independently calculated oracle fidelity. All **270 noisy
target rows** withhold common-state certification. Another 512 bounded random
interval trials and explicit omitted-mass cases passed. These checks support
conditional formulas; they do not establish calibrated physical-device behavior.

The simultaneous intervals assume stationary independent shots and the declared
measurement model. Shared-shot Pauli values are covered by union allocation,
without assuming independence between those values. Prespecified look grids
bound adaptive stopping; candidate and fresh-sample allocations include reserved
control costs. Fresh confirmation does not reuse screening samples. A successful
edit verifies the declared contract for its input, not a unique cause or complete
unitary equivalence.

## External results and fresh replication

Pinned QASMBench revision:
`357b942396d5c2b7cbc1c229c585a6ef5ccaebac`. The complete inventory has 252
paths: 132 canonical originals and 120 transpiled variants. Fourteen originals
are eligible, with five development and nine holdout programs. All 14 imported
full operators match independently parsed original QASM; all 53 frozen source
hashes match. Live upstream checks match the pinned source tree and eligible
original bytes. Exclusion reasons remain recorded in the inventory.

The independent recount preserves the original results:

| Task | Result |
|---|---|
| Distribution policies | 70/82 operational violations detected per policy |
| Pauli fixed / adaptive | 102/108 / 103/108 detected |
| Target fixed, weighted, adaptive, complementary / random | 49/58 / 48/58 detected |
| Conservative recovery, 90 cases, 41 eligible | 10 fresh verified, 8 fresh rejected, zero noise-only proposals; 5,337,088 shots |
| Point-discrepancy recovery, same cases | 10 fresh verified, 31 fresh rejected, 13 noise-only proposals; 5,902,336 shots |
| Designated-index plausible-set coverage | 20/28 searched truth-labelled cases |

Detection denominators exclude unsupported/uncheckable cases as documented in
the original tables; abstentions are retained. The full raw recount in the new
record retains all outcomes and circuit-level tables. Zero observed false
violations is not zero population risk. The localization figure is set coverage,
not causal localization. Repeated seeds are not independent architectures.

The new [subset protocol](../configs/final-verification-subset-v1.json) and
[runner](../scripts/replicate_external_subset.py) were committed before fresh
execution. Outcome-independent index arithmetic selects 54 diagnostics and 18
recoveries across every holdout program. **72/72 scientific projections reproduced
exactly; 72 new exports verified; zero errors or divergences.** This consumed
2,272,256 shots and 1,127 backend executions in 53.12 seconds. Original seeds are
reused, so this is reproducibility evidence, not independent performance evidence.

Git ancestry establishes that the original protocol commit precedes the results
commit. It cannot authenticate wall-clock experiment timing or unrecorded private
tuning. The current documentation now distinguishes those assurances.

The competitor comparison remains qualitative. Fresh execution reproduced all
four QCEC verdicts in its isolated QCEC 3.11.0 environment. A complete trusted
reference enables a stronger task than one-input contract verification; no
accuracy, runtime or repair ranking follows. Qrep, MQT Debugger and Muskit were
source-reviewed, not installed for a matched performance study.

## Confirmed defects and minimal corrections

Commit `a7294d414509c8c8b76fd922deaa572d358b12a5` fixes:

- **MEDIUM:** malformed JSON could trigger HTTP 500 during validation/error
  serialization, including nonfinite literals, exponent overflow, excessive
  nesting, lone Unicode surrogates and invalid raw bytes. `RequestBodyLimit`
  now requires finite, UTF-8-compatible JSON within 64 nesting levels after the
  actual 64-KiB byte cap. Invalid bodies return 422 without a quantum execution.
- **MEDIUM:** malformed integrity-consistent custom/recovery replay requests
  could trigger 500. Stored requests are validated before execution and return
  422 when invalid.
- **LOW:** duplicate Content-Length handling depended on header order in direct
  ASGI calls. Every value is validated and disagreement returns 400. Uvicorn also
  rejects malformed framing; the actual streamed byte cap was already intact.

A final two-case red/green check found that non-application `+json` media types
could bypass this guard with UTF-16 bytes. Follow-up commit
`be64f29fa7e8694bbeddf94329fc0c46c4591617` aligns accepted media types with
FastAPI's parser. The final full platform and browser regressions include it.

The 101 new adversarial API tests include genuine Aer boundary-sized requests,
disconnects, bounded invalid inputs, held-lock concurrency, malformed replay and
artifact tampering. No scientific threshold, frozen result or frontend geometry
was changed. The new reconciliation helper adds 13 regression cases.

## Installation, browser and live demonstration

Fresh clones and new virtual environments installed the hashed lock with
`pip install --require-hashes -r requirements.lock`, then the editable project
with `--no-deps`. `pip check`, `npm ci`, TypeScript, production builds, full
pytest, source checks, archive verification and real Aer smoke passed on:

- Windows: Python 3.13.14, Qiskit 2.3.1, Aer 0.17.2, Node 24.19.0;
  **449 passed, zero failed/skipped**, 50.78 seconds.
- Ubuntu 26.04/WSL2: Python 3.13.15, the same Qiskit/Aer/Node versions;
  **449 passed, zero failed/skipped**, 28.49 seconds.

The initial Linux cross-filesystem direct-copy clone failed; a fresh Git transport
clone succeeded. No existing directory was discarded. Linux Chromium was not
run because NSS/NSPR and ALSA system libraries are missing. macOS and physical
hardware remain untested. The public release's two hosted jobs passed at
`35cbbb9`; no hosted research CI result is claimed.

All ten Windows Chromium suites passed against the production-built application
and real API, including a complete rerun after the final API correction.
Required desktop and 390/375/360-pixel viewports, reduced motion,
WebGL fallback, handover/PixelSwap, investigations, blind challenge, target lab,
recovery, history/replay and export were exercised. Actual screenshots were
opened and inspected. The approved hero and scientific workbench are preserved.
Warnings remain the Starlette/httpx deprecation and lazy Three.js bundle advisory.

The QRNG API workflow freshly reproduced its four outcomes using **81,920 shots
and 40 executions**. Four additional replays verified. The rebuilt root service
preserves the original saved recovery and new recovery
`experiment_dc54dc4fa8e94d5492678b275633b235`. Restart, HTTP 200, health, saved
route refresh, navigation, export and six viewport checks passed. Occupied-port
startup exits 2 with a clear message. Concurrent writes return 409.

## Preservation and remaining limits

All **88 original benchmark/config files** match their pre-gate SHA-256 digests
byte-for-byte, including historical and external frozen protocols/results. The
record contains the complete digest map. Existing tags, checkpoints and linked
recovery worktree remain preserved.

No physical calibration, general circuit correctness or universal repair claim
is justified. Only nine small external holdout programs were evaluated. Runtime
limits are cooperative between backend calls, not hard cancellation. Hashes are
unsigned consistency checks: complete replacement and rehash can pass, and
unindexed auxiliary notes are outside the covered export. These are documented
scope limits, not unresolved release blockers.

The local service remains at `http://127.0.0.1:8000/`, launched with
`.local/final-gate/windows-python/Scripts/python.exe -m qfault serve --port 8000`
and `QFAULT_ARTIFACTS=artifacts/external-live/investigations`. PID and health are
recorded in the verification artifact. Request owner authorization before any
normal fast-forward publication; verify hosted checks on that exact revision
after publication.
