# Guided investigation and public delivery

Starting source: 9866fdb9ed7f22079f6e96bca18d55f0c7d9e173, clean main,
C:/Projects/QFF. Working branch: feat/guided-demo-release. Existing main and
recovery worktree remain preserved. No applicable AGENTS.md was found.

Baseline observed this session: origin/main matches starting SHA, 0/0; exact-SHA
workflow 39837839971 is completed/success. GitHub releases and remote tags are
empty; three local historical snapshot/checkpoint tags remain unchanged. There
are no public downloadable release packages yet. Existing scripts.external_demo,
judging_demo, external_demo_e2e and native_demo_e2e execute the real core. Existing
public docs/media images and local historical silent recordings are not a new
guided demonstration. Targeted dependency checks: 18 tests passed, one existing
Starlette warning, actual Aer Bell smoke passed. This is not a rerun of the
historical 488-test result.

## Chosen design

Reuse the existing external QRNG reference-relative fixture and ordinary
lab/recovery routes. Add a bounded, validated demonstration-input catalog and an
accessible /demo page. Keep independent reference, controlled candidate and
mutation separate. No stored response advances a live stage. The engine screens,
freezes and freshly confirms inside one synchronous recovery call; UI states this
explicitly and shows the actual returned selection and fresh evidence afterward.

Persist only guide state and returned IDs in session storage. Completed server
records remain immutable. Refresh after an interrupted request reports unknown
completion, never automatic replay. A synchronous request guard prevents double
submissions. Errors remain visible; no cancel claim or fabricated percentages.

Alternative: extend the free-form editor alone (still asks judges to assemble
JSON); separate demo engine or resumable scientific recovery (unnecessary and
risks diverging mathematics). Chosen approach changes presentation and delivery,
not policies, thresholds, source guards or frozen records.

## Ordered checklist

1. [x] Inputs/API: tests first for catalog provenance, independent contracts,
   actual request validation, candidate preview and export verification. Use a
   new examples/ fixture built with existing external/import helpers; existing
   lab/recovery execution remains the only engine. Acceptance: real Aer external
   Z/phase/recovery/noise/budget outcomes and retained import ancestry.
2. [x] Guided UI: failing real-browser test for landing/workbench entry and legal
   stages; implement reference → inadequate Z → complementary evidence → bounded
   edits → screening/freeze/fresh verification → export/check/replay. Acceptance:
   real requests, actual costs, duplicate guard, refresh/navigation, understandable
   errors and negative outcomes; desktop/390/375/360, keyboard and reduced motion.
3. [x] Headlines: independently recount the frozen per-case rows; display equal
   yield, both denominators, rejected proposals and calculated shot reduction
   from /api/research. No copied success constants. Acceptance: browser values
   reconcile with the frozen summary and negative interpretation remains visible.
4. [x] Demonstration delivery: concise guide, three-minute narration table,
   actual silent browser recording, full playback/decoded readability evidence,
   real-engine text fallback and deliberately selected public-safe exports.
   Acceptance: downloadable genuine media clearly labelled silent, script and
   observed outcomes matched; no claim of narration or live recorded evidence.
5. [x] Public packaging: regression tests for portable outer packages and safe
   verification/extraction; clean committed source/evidence modes, checksums,
   public verification summary/setup guide and selected media. Independently
   extract, install locked dependencies, build and run representative checks.
   Acceptance: missing/corrupt/unsafe contents fail; no private runtime sweep.
6. [x] Release: full assembled tests, frontend build, Aer/browser, scans and
   preservation comparison; focused owner commits; safe integration/push and
   exact-SHA CI. First formal release PROPOSED v0.1.0 (matches package metadata;
   unused after inspecting actual tags/releases). Publish reviewed assets, then
   independently download, checksum, verify/extract and check public links/tag.
   Acceptance: all advertised public URLs obtainable; no overwrite/force push.

Every step includes decisions/flow/handoff updates before committing. Record
implementation hashes in the next ordinary documentation commit, without a
self-reference loop. Do not repeat frozen studies for UI/documentation changes.

Completed evidence: [judge release verification](judge-release-verification.md).
The immutable v0.1.0 source/tag is b65dcb60fb216e802b2ff7d71a970169a6c059a2;
this checklist update is a later documentation-only follow-up.
