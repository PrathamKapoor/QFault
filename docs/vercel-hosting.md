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
public access are separate deployment gates, not yet claimed by this source record.
