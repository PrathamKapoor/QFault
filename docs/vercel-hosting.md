# Interactive Vercel hosting

The optional hosted adapter runs the same Qiskit/Aer engine as local QFault.
Local `python -m qfault serve` keeps its existing localhost-only trust boundary and
filesystem store. Frozen protocols/results and v0.1.0 assets are not modified.

## Architecture and privacy

Vercel serves the built React assets and routes `/api/*` to `api/index.py`.
`RequestBodyLimit` validates actual request bytes before `HostedApp` validates
deployment Host and same-origin writes. Hosted builds initialize a signed,
Secure/HttpOnly/host-only browser cookie before mounting concurrent workbench calls.
Read responses cannot replace that capability. The hero/landing remain unchanged.

Each browser has a private Blob snapshot containing its original JSON artifact
documents, including separate blind exercise state. Each API instance restores a
bounded temporary directory, then runs the unchanged `create_app` and engine.
Mutations acquire an ETag-conditional lease and durably commit the completed
snapshot before returning a result. Other browsers cannot retrieve those IDs.
There is no shared public history or migration/upload of your local investigations.

Reads use private Blob's `cache=0` origin-consistent option and check the returned
ETag against origin metadata. A real provider probe verified create/read, immediate
overwrite/read and stale-writer rejection. An earlier CDN stale read failed closed;
the check was retained. This is a storage consistency guard, not scientific proof.

The cookie is an access capability, not an account or recovery service. Export
important reports before clearing cookies, changing browsers or the 30-day expiry.
Cookie expiry does not claim automatic deletion of stored records. Retained
snapshots remain private; operators manage retention in their own Blob store.

## Operator setup

Use the repository's locked Python/runtime and frontend requirements. Deployment
uses `.python-version`3.13 and nearest `api/pyproject.toml`/`api/uv.lock` for Vercel's
native frozen installer. Every runtime version and wheel/source hash is checked
against unchanged `requirements.lock`, including Aer. Root requirements.txt remains
a hashed pip convenience file; Vercel prefers a native manifest over that wrapper.
No hosting SDK/dependency is added. Build checks TypeScript
then sets the public `VITE_QFAULT_HOSTED=1` feature flag for the frontend build.
Never put provider tokens or signing keys in a `VITE_` variable.

Authenticate using `npm exec --yes --package=vercel@65.2.0 -- vercel login` and
approve the device flow yourself. Inspect `vercel whoami --format json` and existing
projects before linking; preserve unrelated projects. CLI-managed `.vercel/`,
`.env*` and `.local/` stay excluded from Git and source upload.

Create or reuse the intended project. Create a **private** Blob store and connect
it to production/preview. CLI commands after inspecting the intended project:

```text
vercel blob list-stores --json
vercel blob create-store qfault-investigations --access private --yes --environment production --environment preview
vercel env add QFAULT_SESSION_KEY --environment production,preview --sensitive
```

The key must be an independently generated secret of at least32characters. Enter
it securely; do not print, commit, paste into chat or pass through command-line
arguments. Vercel manages `BLOB_READ_WRITE_TOKEN` for the connected private store.
Use the same signing key across deployments if preserving browser access.
Allowed hosts derive from Vercel's deployment/branch/production host variables;
explicit custom hosts can be added with `QFAULT_PUBLIC_HOSTS` (comma-separated).
Do not enable wildcard hosts or disable the local guard globally.

Deploy a reviewed committed source to preview, inspect logs, then test actual live
workflows before production. Use `vercel deploy --yes --no-wait`, then
`vercel inspect DEPLOYMENT_URL`. Promote only the verified source/deployment.
Vercel protection settings may require account access for previews; production
must be checked for the intended judge access rather than assuming it is public.

## Bounds and failures

- Original validated circuit/contract/gate bounds and scientific policies remain.
-64mutating operations per browser session; validation previews do not spend it.
-32MiB/1,000JSON files per session snapshot; API responses at most4MiB.
- Vercel function ceiling300seconds; a crash/timeout can leave a310-second lease.
  No hard in-flight cancellation or crash-resumable scientific selection is claimed.
- Concurrent mutation409; operation ceiling429; unavailable private storage503;
  snapshot/response cap507. No successful saved result before durable commit.
- Losing connectivity leaves completion unknown. Inspect history before retrying.
- Hobby quotas apply. No paid upgrade was enabled. Per-session admission is not
  a global distributed rate limiter; public availability still depends on quota.

Vercel documents that Hobby private Blob is free within quota and is suspended
rather than charged for excess use. Check the current provider documentation before
changing plans: [pricing](https://vercel.com/docs/vercel-blob/usage-and-pricing),
[runtime](https://vercel.com/docs/functions/runtimes),
[consistent reads](https://vercel.com/changelog/vercel-blob-now-supports-consistent-reads-on-private-storage).

## Verification

The first build succeeded but runtime import failed because importing qfault.api
constructs an unused global local app. The hosted entrypoint now creates that
bootstrap only in temporary storage before importing the unchanged local API.
Actual requests use separate restored private snapshots, not that bootstrap app.
Vercel also preferred the root pyproject over requirements.txt, so the nearest
hosted native lock explicitly includes Aer without changing local dependencies.
Read-only-entrypoint and exact original artifact-hash regressions cover both fixes.
Vercel assigned the first deployment to production automatically; this is recorded
as a failed runtime deployment, not a verified public workbench.

The corrected assembled suite passed531tests, one existing Starlette/httpx deprecation
warning,102.38seconds (initial hosting source:529tests99.07s). Hosting tests include real Aer recovery, separate-instance restore,
two-browser isolation, Origin/Host/body guards, storage failure, leases/quota,
unsafe paths, consistent reads, signed bootstrap, blind freeze/reveal, expired
lease recovery and commit conflicts. These unit transport tests use controlled
storage; the actual private-provider probe is a separate observed check.

Frontend typecheck and normal/hosted builds passed; existing lazy Three chunk
warning remains. Actual preview/production browser, cold-start persistence and
public access are separate deployment gates, recorded below after execution.

## Public deployment verified on 2026-10-23

- Public app: <https://qfault.vercel.app>; guided workflow:
  <https://qfault.vercel.app/#/demo>.
- Exact deployed source: `502a416519c2bb1d99265991d4cf5e290e37ba94`, branch
  `feat/vercel-hosting`. Later documentation/test-log changes are not claimed to
  be in that deployed snapshot. Existing v0.1.0 packages remain unchanged.
- Verified preview: `dpl_jPcZxcUsHbAUrQpP3yRPFhv2vgh9`,
  <https://qfault-an6wooy6v-hex-sembly.vercel.app>.
- Verified production: `dpl_EZyabyX6wKrTcYA8o394twpPqXin`,
  <https://qfault-o64u90pgy-hex-sembly.vercel.app>. CLI promotion created a new
  production deployment asynchronously; READY and stable alias binding were
  checked after it completed. Immediate inspection during promotion still saw the
  old deployment, and was not accepted as proof.
- Actual production Chromium command:
  `python -m scripts.guided_demo_e2e --base https://qfault.vercel.app --out artifacts/vercel-production-browser-2`.
  Passed: 18 actual POSTs, imported external circuit, inadequate Z evidence,
  complementary discrepancy, freshly verified recovery, independently verified
  downloaded export, history/refresh, distinct replay, noise abstention, zero-shot
  budget refusal, mobile widths390/375/360, no page errors.
- Separate production API checks passed in
  `artifacts/vercel-production-safe-check/api-summary.json`: Aer0.17.2,
  private two-browser history, cookie-context restoration, independently verified
  exports, parent-linked replay, Origin403/body413 and blind freeze/reveal.
  This restores browser context; it does not force a provider process restart.
- The same combined smoke passed completely on the corrected preview
  (`artifacts/vercel-corrected-preview/summary.json`). Production attempts also
  recorded intermittent API-client `read ECONNRESET`; a later combined run passed
  its API checks but timed out locating a preserved guide ID. The separate full
  production browser run above passed. These intermittent checks are retained as
  limitations; their cause is UNKNOWN. No measurement POST was automatically
  retried, no failing assertion was removed, and no result was substituted.
- Source CI [40001833472](https://github.com/PrathamKapoor/QFault/actions/runs/40001833472)
  completed successfully for the exact deployed SHA (checks and browser-smoke).

The private provider probe verified create/read/immediate conditional overwrite
and stale-writer rejection. Hosted report storage is durable Blob, not function
scratch. Browser cookies provide access, not an account or administrator secrecy.
No paid upgrades, provider charges or hardware jobs were enabled. Quota exhaustion,
network failures and unknown completion remain possible; inspect history before
resubmitting and export important reports. Deployment runtime is Vercel Linux
Python3.13; local verification was Windows x86-64 Python3.13.2/Node24.19.0.


## Hosted usability and reliability update (2026-10-24)

Implementation starts at0f2da99; deployment remains the older recorded source until
preview and production gates below are executed. Do not relabelv0.1.0 packages.

The first-screen primary action is **Run the guided demo**. The quick QRNG lesson
and separately imported **four-qubit cat/GHZ** lesson both use ordinary validated
engine requests. Reference/candidate identities and independent declared contracts
stay distinct. Result summaries lead with the actual verdict/edit/total and fresh
shots/scope. TV and Pauli intervals display physical-domain intersections only;
advanced inspection retains raw intervals/tolerance/units. Loss/improvement and
stored/exported records are unchanged.

Browser requests share bootstrap/read/validation/execution classes. Bootstrap and
safe reads have20s deadlines and at most3transient attempts (500/1000ms backoff).
Validation has30s, execution280s, no automatic execution retry. Timers/controllers
are cleaned up; timeouts only stop waiting. Invalid schema/auth errors do not
blindly retry. Busy responses remain explicit. Completed IDs invalidate shared
history with newer-response guards; replay retains separate identities.

Hosted execution sends X-QFault-Operation:operation_<32hex>, bound durably to its
browser session, method/path and canonical validated JSON request. GET
/api/operations/{id} returns RUNNING/COMPLETED/FAILED/UNKNOWN and a result identity/
path when available. The guide's **Recover existing operation** looks up the saved
operation after refresh/lost response, then loads the existing result. The generic
session controls can recover the last submitted operation. Same ID/different
request409; another session404. Expired RUNNING stays UNKNOWN, never resubmitted.
Crash before durable result commit can lose unsaved evidence; this is not universal
exactly-once execution. Result files and completion commit together in one snapshot.

**Session controls** show remaining64admitted mutations, access expiry, export and
confirmed deletion. Validation/status/report reads do not spend mutation allowance;
replay/challenge transitions/reviews do. GET /api/session/export returns a complete
ZIP of accessible completed ordinary/public challenge reports with raw manifests
and member hashes,4MiB compressed/32MiB expanded bound. Corrupt/missing required
records refuse a complete export. Independently verify downloaded bytes:

```text
python -m scripts.verify_session_export qfault-session-reports.zip
```

POST /api/session/delete requires explicit confirmation, refuses an active lease,
CAS-removes content, leaves a tiny anti-resurrection tombstone, and expires the
cookie. Client state clears only after confirmed success. If that response is lost,
POST /api/hosted-session with reset:true only opens a new session after checking a
tombstone; it refuses to reset an intact session. Existing reports in other browser
sessions are unaffected. Tests use disposable sessions only.

New snapshots have prospective90day cleanup eligibility metadata. Existing legacy
snapshots without it retain all records and no retroactive expiry. Cookie expiry
is not deletion. Eligible prospective content is purged on access or an explicit
bounded operator sweep; **no background schedule is configured or claimed**.
Operator command, using a private CLI-managed Blob environment and private JSON
array of at most100session IDs:

```text
python -m scripts.cleanup_hosted_sessions --session-list PRIVATE_SESSION_LIST.json
python -m scripts.cleanup_hosted_sessions --session-list PRIVATE_SESSION_LIST.json --apply
```

Default dry run reports counts only. Apply skips legacy and active snapshots, uses
conditional tombstones, never prints session IDs or credentials. Do not feed owner
sessions into disposable tests. An automated legacy-retention migration remains
unauthorized; no existing records were deleted or shortened here.

Aggregate admission uses one shared conditional private Blob record, one active
slot,330s lease versus configured300s function maximum, immediate busy/no queue.
At most100admissions/5million reserved shot ceilings per UTCday; hosted custom
request cap250000shots/160evaluations/120cooperative seconds. Template/challenge
existing600evaluation bound remains. Replay derives the ceiling from its validated
saved request. These are conservative admission reservations, not measured shot
costs. Busy/invalid/cost refusal spends no session allowance. No IP identifiers are
collected. Safety assumes provider function-duration enforcement; no independent
hard backend cancellation is claimed. Reads/bootstrap/HTTP traffic can still
consume provider quotas; this is not comprehensive public denial-of-service
protection. Hobby quota exhaustion fails closed, without paid upgrades.

Storage profile and actual provider evidence: [hosted-storage-profile.json](hosted-storage-profile.json).
Retain atomic bounded snapshots with schema2 length/digest-checked lossless
zlib/base64 wire envelope; legacy schema1 reads supported. Scientific JSON strings
are identical after decode. Transfer and restore still grow linearly, bounded by
32MiB/1000files/64mutations. Controlled64copies shrink25.9MB to1.53MB; this is not
a diverse-workload benchmark. Actual disposable1/4copy provider probes verify
roundtrip/stale-writer rejection; their corrected instrumentation counts failed
conditional PUTs as requests. No multi-object/orphan migration is introduced.

Validation commands include the full Python suite, all Node controller tests,
local/hosted check/build, actual Aer, existing archive verifiers, local guide and
keyboard/mobile/error paths, then actual preview/production scripts.hosted_smoke
and scripts.hosted_usability_e2e. The latter deliberately loses one real response
after durable completion, restores the original operation, runs the entangling
example, verifies export-all/isolation and deletes only its disposable session.
Deployment results and exact source are added after actual execution.
