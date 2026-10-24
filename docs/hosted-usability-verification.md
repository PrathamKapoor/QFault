# Verified hosted usability and reliability

Checked2026-10-24. [Open the guided demo](https://qfault.vercel.app/#/demo).
[Machine-readable verification](hosted-usability-verification.json) records exact
sources, scope and observed results. This is an observation record, not a signature,
external timestamp or guarantee of uninterrupted availability.

Deployed source: **d074a9bbd3c2e36379f0b9ea015d219ea5387c49**.
Production: dpl_CPqRmn2QBmWSDCnMTYzdNh8qfF2v, stable alias qfault.vercel.app,
verified READY/source/alias through the authenticated provider API after promotion.
Preview: dpl_BaSeBFZijmcaZtH9ugndNNhpUmDX,
https://qfault-r2wcd40sx-hex-sembly.vercel.app, tested before promotion.
[Exact deployed-source CI40054986316](https://github.com/PrathamKapoor/QFault/actions/runs/40054986316)
completed successfully, checks and browser-smoke. Later documentation and test-driver
changes do not claim to be in that earlier deployed snapshot. Git history and
exact-SHA Actions identify the final documentation commit after this file is written.

## Requested behavior

| Area | Status | Demonstrated behavior |
|---|---|---|
| Results | COMPLETE | Actual verdict/edit/cost/fresh pair/scope before advanced evidence; no selected edit invented for abstention |
| Intervals | COMPLETE | TV[0,1]/Pauli[-1,1] display intersections, raw/tolerance/units retained; invalid/empty/nonfinite explicitly inconsistent; loss never clamped |
| Hosted wording and hierarchy | COMPLETE | Guided primary action, server execution/limits wording; original hero rendering/local wording retained |
| Navigation/history | COMPLETE | Task links retain old routes; completed identities invalidate guarded history, distinct replay records, no fake failures |
| Bounded requests | COMPLETE | Classified deadlines, transient safe-only retry, elapsed states/recovery actions and no automatic scientific POST retry |
| Operation recovery | COMPLETE | Session/request-bound durable IDs, existing result after dropped or held response, early404 unresolved, duplicate suppression |
| Session controls | COMPLETE | Remaining allowance/access, independently verified complete export-all, explicit confirmed/fenced deletion, prospective retention |
| Aggregate admission | COMPLETE | Conditional shared Blob slot; actual concurrent201/503, unadmitted allowance delta0, no queue |
| Storage | COMPLETE | Measured lossless compressed atomic snapshot; original strings/legacy reads preserved; bounded linear restore remains |
| Additional example | COMPLETE | Imported pinned four-qubit cat/GHZ source, independent analytical reference, real Z/phase/fresh recovery |
| Deployment | COMPLETE | Tested preview then independently checked production source/alias and fresh browser/API workflows |

## Actual outcomes

| Workflow | Outcome | Total shots | Fresh original | Fresh candidate |
|---|---|---:|---:|---:|
| QRNG bounded recovery | VERIFIED_UNDER_DECLARED_CONTRACT |77,824|4,096|4,096|
| Entangled cat bounded recovery | VERIFIED_UNDER_DECLARED_CONTRACT |153,600|8,192|8,192|

Both test32generated/32measured edits under their declared budgets. More cat fresh
shots reflect two settings, not a change in verification policy. These controlled
examples do not change published repair rates or establish general superiority.
Z-only agreement remains scoped; complementary evidence detects the phase mismatch.
Noise control abstains; insufficient budget returns a retained record with0shots.
An admitted zero-shot request still consumes one request allowance. A global-busy
unadmitted request does not. Session opening/deletion/reads/validation are exempt.

The production entangling test deliberately pauses a POST before forwarding:
actual status404 leaves pending unresolved and used allowance0. It forwards that
same request once, drops its response, refreshes and restores the original identity.
It separately holds the complementary response after durable completion, recovers
without waiting for timeout, then successfully runs fresh recovery. No computation
is resubmitted. History becomes3records; downloaded complete ZIP verifies; a second
session cannot read its report; confirmed deletion removes only disposable data.

The tiny production admission probe uses two concurrent zero-shot requests in two
fresh sessions. First attempt returns201/503, loser allowance unchanged. Matching
ID returns the same saved result; changed seed with same ID409, another session's
lookup404. Both disposable sessions are deleted. This is not a stress test or proof
of particular provider container scheduling.

## Verification commands and results

```text
python -m pytest tests -q
node --test tests/*.test.mjs
npm --prefix web ci
npm --prefix web run check
npm --prefix web run build
python -m pip check
python -m scripts.aer_smoke
python -m scripts.verify_external_results benchmarks/external-holdout-v1/summary.json
python -m scripts.verify_recovery_archive
python -m scripts.verify_replication
```

Local isolated Windows x86-64 Python3.13.2/Node24.19.0:550passed,1existing
Starlette/httpx warning,143.92s after final backend guard;12Node tests pass after
later frontend-only fixes. Typecheck/build pass in local and VITE_QFAULT_HOSTED=1
configurations; npmci succeeds and reports0advisories. Existing Three chunk warning
remains. Actual Aer Bell smoke00:506,11:518; pipcheck succeeds. pip-audit2.10.0
on the pinned hashed closure/current platform reports no known vulnerabilities;
this is a scoped date-specific advisory result, not proof of universal security.
No application dependencies or lock versions changed.

All three archive verifiers pass:2,206external exports/2,232attempted rows,
310historical recovery exports and72current replication exports. These are old
records independently checked, not newly rerun studies. Frozen protocols,
benchmarks, archives and mathematical engine files remain byte-identical.

Executed against the real preview, then production:

```text
python -m scripts.hosted_smoke --base https://qfault.vercel.app --out NEW_DIRECTORY
python -m scripts.hosted_usability_e2e --base https://qfault.vercel.app --out ANOTHER_NEW_DIRECTORY
python -m scripts.hosted_admission_e2e --base https://qfault.vercel.app --out NEW_RESULT.json
python -m scripts.verify_session_export DOWNLOADED_SESSION.zip
```

The last admission command is operator validation, at most4tiny zero-shot requests;
run in a quiet window, not a load test. The observed run needed only one201/503pair.
No admin token is needed. Real API checks include Aer0.17.2, private context
restoration/export/replay, Host/Origin/body guards and blind diagnose/freeze/reveal.
Real Chromium checks include desktop,390/375/360widths, history/refresh, reduced
motion, no page errors, export membership and session isolation/deletion. Local
keyboard/error/hero seven-width tests also passed. Viewport checks are not native
iOS/Android certification; macOS/ARM and other browsers were not tested here.
Provider context restoration is not a forced container restart.

Raw controlled exports and genuine screenshots are ignored local evidence under
artifacts/usability, not published personal/runtime data. Use the live guide to
create your own verifiable export. Download raw bytes for integrity: reserializing
through JavaScript can turn1.0into1, which qfault-json-v1 intentionally distinguishes.
Stored hashes are unsigned consistency checks, not authenticity guarantees.

## Retained failures and limits

Earlier probes failed on raw-JSON test reserialization, obsolete CTA selectors,
busy-error wording, an empty-error logger and early lookup404. Their fixes retained
all scientific assertions. Actual early-body/stalled-request/stale-error controller
regressions were observed red before fixes. Some local API/Route clients encountered
ECONNRESET; its underlying network cause remains UNKNOWN. A later local private
metadata read also failed with URLError after bounded attempts, while actual cloud
browser/provider workflows and public admission checks passed. Safe GET retry and
durable original-operation lookup handle these cases; no claim of eliminating
transport failures is made. Deliberately paused test interception can log a cleanup
CancelledError when its context closes; completed app assertions/page errors are
reported separately, not relabelled as an application failure or hardware result.

A crash before durable commit may leave UNKNOWN and lose unsaved measurements.
Lease expiry is not proof of no execution and never triggers resubmission.
Global admission assumes the configured300s provider maximum with a330s lease;
no independent hard backend cancellation guarantee. Limits: one active slot,
100admissions/5million reserved shot ceilings per UTCday, no queue. Reservation
ceilings are not measured shots. Global HTTP/read traffic and all provider quota
exhaustion are not prevented; Hobby availability remains bounded, no paid upgrades.

Cookie access30days is not deletion. New snapshots have90day cleanup eligibility;
expired prospective data is purged on access or a bounded explicit operator sweep.
No background cleanup schedule is configured. Legacy records receive no retroactive
deadline. A tiny deletion tombstone fences late writers; downloaded copies remain
yours. Actual disposable legacy-schema read/compressed-update and prospective
cleanup were tested against private storage without touching existing owner data.

[Storage profile](hosted-storage-profile.json):64controlled copies25.9MB become
1.53MB; local restore/save1.38s. Actual1/4copy provider roundtrip/CAS probes pass.
Transfer/restore remain linear with32MiB/1000files/64mutations bounds. Session
traffic normally uses4requests/mutation; the shared coordinator adds6, total10
before bounded consistency/CAS retries. This is not a diverse workload or billing
benchmark, and no multi-object atomicity claim is made.

Existing v0.1.0 release/tag/assets remain unchanged at
b65dcb60fb216e802b2ff7d71a970169a6c059a2 and do not contain this hosted update.
No frozen evaluation, paid service, hardware job, competition submission, new
collaborator, history rewrite or secret rotation occurred.
