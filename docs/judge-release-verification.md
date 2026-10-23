# Judge-facing release verification

Session date: 2026-10-23. Started at clean main
`9866fdb9ed7f22079f6e96bca18d55f0c7d9e173` in C:/Projects/QFF. The immutable
v0.1.0 source/tag/packages identify **b65dcb60fb216e802b2ff7d71a970169a6c059a2**.
This record and the direct README links are a later documentation-only follow-up;
their own commit identity is authoritative in Git history, not embedded in itself.

## Public delivery

[Public release](https://github.com/PrathamKapoor/QFault/releases/tag/v0.1.0).
All nine assets were independently downloaded without authentication, their sizes
and SHA-256 recomputed, both package modes verified and the remote tag resolved to
the exact source above. The source was pushed without force; origin/main matched
with 0 ahead/0 behind before this documentation follow-up. Source CI
[39931840261](https://github.com/PrathamKapoor/QFault/actions/runs/39931840261)
completed successfully for both checks and browser-smoke on Ubuntu 24.04.

| Asset | SHA-256 |
|---|---|
|[Source-only ZIP](https://github.com/PrathamKapoor/QFault/releases/download/v0.1.0/qfault-v0.1.0-source.zip)|9668767d4e44ec584cfa8340f8c64ae7b041663ebd22c6778f46009c37e7f0f3|
|[Evidence-inclusive ZIP](https://github.com/PrathamKapoor/QFault/releases/download/v0.1.0/qfault-v0.1.0-evidence.zip)|8fae342b45eccefc0001b7fa22bc077d121f5aab8dbf8dc7c83989af73bc60d9|
|[Controlled demo exports](https://github.com/PrathamKapoor/QFault/releases/download/v0.1.0/qfault-v0.1.0-demo-evidence.zip)|c63f760e8b80a2fac525185f028b53bd86258baaf0d67da4547bad9de00c7059|
|[Silent recording](https://github.com/PrathamKapoor/QFault/releases/download/v0.1.0/qfault-v0.1.0-guided-demo-silent.webm)|2c1750173e41e700d44200b4fc179f9745f35e89d220f1640d849ed5e54859a2|
|[All asset checksums](https://github.com/PrathamKapoor/QFault/releases/download/v0.1.0/SHA256SUMS)|90602284b4fc5427095b401c7348c7a048393da569d7ec122593465bfb87f78d|

[Public machine-readable checks](https://github.com/PrathamKapoor/QFault/releases/download/v0.1.0/release-verification.json),
[setup/judging guide](https://github.com/PrathamKapoor/QFault/releases/download/v0.1.0/judging-guide.md),
[complete narration](https://github.com/PrathamKapoor/QFault/releases/download/v0.1.0/three-minute-demo.md)
and [actual-time captions](https://github.com/PrathamKapoor/QFault/releases/download/v0.1.0/qfault-v0.1.0-guided-demo-captions.vtt)
are downloadable assets too. Unsigned hashes establish consistency, not authenticity,
trusted timestamps or scientific correctness.

## What the judge can do

Choose Guided demo from the landing page or workbench. Inspect pinned QASMBench
QRNG source, independent reference and imported candidate with controlled terminal
Z. Run Z-only measurements, then complementary X claims, inspect 32 bounded edits,
run screening/freeze/fresh paired verification, download/check the report and create
a distinct same-seed replay or new-seed rerun. Negative demonstrations execute real
noise-control and insufficient-budget cases. No stored success advances a stage.
Original records survive refresh/navigation; interrupted requests remain unknown
until inspected, and synchronous admission suppresses duplicate submissions.

Actual final recording outcomes (seed 4191):

| Stage | Observed verdict | Shots | Executions |
|---|---|---:|---:|
|Z-only|NO_SIGNIFICANT_DISCREPANCY|1024|1|
|Complementary|SIGNIFICANT_DISCREPANCY|2048|2|
|Recovery|VERIFIED_UNDER_DECLARED_CONTRACT|77824|36|
|Noise control|NOISE_CONTROL_ABSTENTION|4096|2|
|Reserve refusal|INSUFFICIENT_BUDGET|0|0|

Fresh confirmation allocated 4,096 shots to each of original/candidate, with distinct
execution membership from screening. The supported improvement interval was
[9.256,10.372] dimensionless contract-tolerance units; it is not fidelity or a fault
probability. Cause remains ambiguous. Full recording 180.12 seconds, 1440×1000,
normal-speed playback ended with 4,874 frames, 0 dropped, 0 corrupt, 0 audio tracks and no errors.
Decoded source/phase/fresh/noise/budget frames were visually inspected. Footage is
silent; narration exists as text only. The text fallback scripts.guided_demo also
executed all five outcomes successfully through the same API/engine.

## Executed checks

Windows x64, CPython 3.13.2, Node 24.19.0/npm 12.0.2:

- `python -m pytest tests -q -p no:cacheprovider`: **514 passed**, 80.42 s,
  one existing Starlette/httpx deprecation warning on the exact release source.
- `node --test tests/guided-session.test.mjs`: **4 passed**.
- Both clean-source packages extracted into independent empty directories with
  separate new virtual environments: hashed Python install, editable no-deps
  install, pip check, npm ci, frontend check/build and actual Aer smoke passed.
  Source-only representative guided/native-import/delivery tests: 22 passed in 33.35 s.
  Evidence-inclusive additionally release-package tests: 28 passed in 38.68 s.
- Publicly downloaded archives were separately extracted again. Imports were
  asserted to resolve inside each downloaded project. Using the already verified
  isolated dependency environments, npm ci/check/build passed again; 22 source
  tests passed in 30.56 s and 28 evidence tests passed in 33.45 s. Downloaded source Aer Bell
  smoke returned 00=506/11=518. Downloaded evidence verifiers returned 2,206 external,
  310 historical recovery and 72 replication reports valid.
- Real guided browser workflow passed source/Z/phase/recovery/export/integrity,
  refresh, distinct replay, history and both abstentions; 18 actual POSTs, no page errors.
  Desktop and 390/375/360 px widths passed. Keyboard/reduced-motion suite passed,
  including explicitly injected HTTP 409/connection failures and real Aer retry.
  No positive quantum result was mocked. Those UI files are identical in the tag.
- Existing full cinematic seven-width hero/transition, navigation and release smoke
  passed. A prior reload missed WebGL; its cause remains UNKNOWN. No hero redesign
  or assertion relaxation was used; the complete stable-build rerun passed.
- Actual initial playback seek failure was isolated to a synthetic HTTP response
  with seekable[0,0]. D-077 changed only the media verifier to decode identical
  bounded bytes as a seekable Blob; full playback then passed. An operator command
  named nonexistent test_evidence_package.py and ran no tests; corrected actual
  test_release_package.py commands passed as counted above.

The existing lazy Three chunk remains 566.56 KB and emits a build-size warning.
Hosted Ubuntu 24.04 jobs passed the locked build/full tests/Aer and actual real
browser suites at the exact source SHA. No fresh macOS/ARM claim is made.

## Evidence, security and preservation

No frozen study was rerun or changed. Benchmark/config bytes, locks and scientific
engine files match the starting revision. Available archives independently verify
2,206 exports across 2,232 external attempted rows (26 nonexecution rows), 310 historical
recovery exports and 72 current replication exports. Other historical raw families
remain unavailable/unknown per [availability ledger](evidence-availability.md).

External protocol external-qasmbench-v1 retains execution revision
6eaeb2ddb83caacbb5fd758776a06bb2632cd916. Conservative and point ranking both
verified 10/90 overall and 10/41 eligible; rejected proposals 8/31, shots 5,337,088/5,902,336,
about 9.6% fewer with equal observed yield. Nine holdout source programs yield small
correlated cases, not population superiority. Current-release-replication-v4 at
97710d834abeef93f0094b169a05d182f22c8434 is 72/72 consistency, not repair accuracy.

Gitleaks 8.30.1 scanned 117 reachable commits/~21.67 MB with no unclassified leaks;
the separately reviewed public asset folder scan also found none. Exact nonsecret
source-fingerprint exclusions remain. Initial Git ownership scan failure was
retried with process-scoped safe.directory, without changing global configuration.
pip-audit 2.10.0 on locked requirements and npm audit found no known scoped advisories.
Tracked/member review found no env/database/private-key/dependency directories or
personal runtime sweep. Ordinary artifacts, original branches/local historical
tags and the separate recovery worktree remain preserved. No dependency changed.
All new implementation authors/committers were checked as the exact owner; no
coauthor/tool trailers were added. QASMBench licenses/notices remain in source and
the deliberately selected controlled-demo archive.

## Gates on the tagged implementation

All rows observed in this 2026-10-23 session, source b65dcb60fb216e802b2ff7d71a970169a6c059a2.
Exact commands/results are above and in the downloadable machine summary.

| Gate | Status | Evidence |
|---|---|---|
|G1 Preservation|PASS|Git baseline/fetch/worktrees; unchanged benchmark/config/core comparison|
|G2 Installation|PASS|Two empty-extraction hashed installs, pip check, npm ci/check/build|
|G3 Inputs|PASS|Full 514 tests and actual imported guide/native import representative tests|
|G4 Science boundaries|PASS|Full suite, retained frozen evidence, independent archive verifiers|
|G5 Recovery|PASS|Real guide selection/fresh paired confirmation and negative controls|
|G6 Evidence|PASS|Public report archives, checked identities/exports/replay; unavailable families explicit|
|G7 Frontend|PASS|Actual desktop/mobile/keyboard/reduced-motion/Aer workflows and hosted browser-smoke|
|G8 Packages|PASS|Both local/public downloads verified, extracted, built and tested|
|G9 Publication safety|PASS|Scoped history/assets/advisory/member review and legal notices|
|G10 GitHub|PASS|Exact owner commits, remote SHA, 0/0 sync, source CI 39931840261 success, public tag/assets redownload|

The final documentation follow-up does not change packages, media, scientific
results or tag. Its actual commit and exact-SHA hosted checks are recorded by
Git/GitHub after publication; no self-referential commit hash is fabricated here.
Remaining scope: local simulator, one declared input/contract, bounded edits,
shared simulator assumptions, cooperative time guards, possibly unresolved dense
targets and ambiguous cause. No hardware, universal equivalence, narrated voiceover,
specific competition eligibility, guaranteed win or paid job is claimed. No
mandatory judge-delivery asset remains blocked.
