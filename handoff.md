ACTIVE 2026-10-24 owner-authorized hosted usability: partial. Starting clean
feat/vercel-hosting0f2da99, upstream0/0 and CI40002926091 success. Original main
and three dirty root docs preserved. Read docs/hosted-usability-ledger.md. A/B/C
implemented with presentation, history, classified requests and durable operation
IDs. Node9tests/typecheck passed;19hosting/operation tests and additional5operation
concurrency tests passed. D controls tests currently red and not part of A–C commit.
Continue D→E→F→G; do not stop at plan. Production remains prior502a416 until gates.
No scientific/frozen source or data changes. D-087–D-090 record current choices.

# QFault handoff — public interactive Vercel delivery

## 1. Current Phase

Full interactive hosting implemented and production browser/API behavior verified,
2026-10-23. Status: complete for deployment, with intermittent probe limitations
below. Deployed source502a416519c2bb1d99265991d4cf5e290e37ba94;
https://qfault.vercel.app/#/demo. Current documentation/test-log follow-up is
uncommitted at write time; Git history identifies its own commit.

## 2. Work Completed

Owner approved Vercel login and full live measurements/private saved reports.
Opt-in hosting adapter wraps the existing scientific API, using signed browser
capabilities, private Blob snapshots, ETag-fenced leases and commit-before-response.
Hosted frontend initializes its cookie before loading workbench requests and
explains report access/limits. Initial read-only import/native dependency selection
failures were corrected without changing the original scientific API or locks.
Actual provider consistency/CAS checks, corrected preview API/browser checks and
production real browser plus separate API privacy/blind checks passed. Public
Vercel login protection disabled only for new qfault project, not unrelated trial.
No paid plan or service enabled. Failed/intermittent probes remain documented.

## 3. Files Changed

Implementation13c121d: qfault/hosting.py, api/index.py, vercel.json,
.python-version, requirements.txt, .vercelignore, .gitignore, hosted UI bootstrap/
notice, tests/test_hosting.py, README/root docs and hosting guides.
Correction502a416: api/index.py scratch bootstrap, api/pyproject.toml/api/uv.lock
with exact original dependency artifacts, tests/test_hosted_entrypoint.py,
scripts/hosted_smoke.py and documentation. Current follow-up: README public link,
hosting guide/plan, root records and bounded safe smoke failure diagnostics.

## 4. Current Architecture / State

Isolated C:/Projects/QFault-Hosting, feat/vercel-hosting, intended origin
https://github.com/PrathamKapoor/QFault. Branch source502a416 pushed and verified
0ahead/0behind before this follow-up. Original C:/Projects/QFF main287dd4f and its
three dirty root operational documents remain preserved. Local combined frontend/
API was started on127.0.0.1:8000; do not kill unknown processes. Existing recovery
worktree and immutable v0.1.0 release/tag/packages remain unchanged.
Vercel Hobby team hex-sembly, project qfault. Private qfault-investigations Blob
store; credentials CLI-managed or ignored local environment, never in Git.
Production dpl_EZyabyX6wKrTcYA8o394twpPqXin READY and stable alias verified.
Corrected preview dpl_jPcZxcUsHbAUrQpP3yRPFhv2vgh9 passed combined smoke.
Promotion created a new asynchronous production deployment, not the preview ID.

## 5. Decisions Made

D-079 preserved local startup notes. D-080 private hosted wrapper; D-081 actual
cache=0 consistent reads; D-082 cookie bootstrap/privacy UI; D-083 initial deployment
setup; D-084 observed import/native-lock fixes; D-085 public access/live smoke;
D-086 safe diagnostic logs and exact public verification scope. Implementation
identities: D-080–083=13c121db7e4b99bc6588203069ae17dfdec49d7a;
D-084–085=502a416519c2bb1d99265991d4cf5e290e37ba94. Append-only history preserved.

## 6. Requirements and Constraints

Exact owner author AND committer required; no coauthors/tool signatures. Preserve
science/protocols/raw evidence/hero, unrelated files and original main dirty docs.
No paid upgrades, secrets in output, force-push, history rewrite, competition
submission or external messages. Never commit paper/, research/ or .tex. Do not
claim old v0.1.0 package includes new hosting. User authorized public hosting.

## 7. Testing and Verification

Windows x86-64 Python3.13.2/Node24.19.0. Full assembled531passed, one existing
Starlette/httpx warning,102.38s;17targeted hosting/entrypoint tests passed36.45s.
Frontend npm ci/check and normal/hosted build passed, existing chunk warning.
Real provider create/read/immediate overwrite/stale ETag rejection passed.
Preview scripts.hosted_smoke all API and guided checks passed.
Production python -m scripts.guided_demo_e2e --base https://qfault.vercel.app
--out artifacts/vercel-production-browser-2 passed:18POSTs, imported circuit,
Z/phase discrepancy, fresh recovery, downloaded export independent verification,
history/refresh/replay, noise abstention, zero-shot budget,390/375/360widths,
no page errors. Production hosted_smoke separate API portion passed in
artifacts/vercel-production-safe-check/api-summary.json: two-browser isolation,
cookie-context restore, export/replay,403Origin/413body and blind lifecycle.
Its subsequent guided repeat failed a preserved-ID locator assertion; earlier
production probes hit ECONNRESET. Retained; no failing assertions weakened or
POST auto-retries. Source CI40001833472 completed success for exact502a416,
checks and browser-smoke. Vercel Linux Python3.13 actual runtime/Aer verified.
No forced provider restart or non-Windows local platform claim. No frozen study
rerun. Final follow-up CI must be checked independently after push.

## 8. Known Issues / Risks

Confirmed: intermittent production probe connection resets and preserved-ID locator
timeout; cause UNKNOWN. Complete separate production browser and API scopes passed.
Browser cookie capability expires30days; clearing/switching browser loses access.
64mutation/32MiB/1000JSON per-session limits; free Hobby quotas apply. No global
rate-limit/account recovery/provider-authenticity/hardware claim. Function300s
limit can leave unknown completion; inspect history before resubmitting. No
provider cold-start was forced. First failed production retained in deployment
history; current stable alias points to corrected production.

## 9. Unfinished Work

Finalize reviewed documentation/log-safety follow-up, safe staged scan, owner commit,
push hosting branch and verify exact remote SHA/CI. Do not merge into original
dirty main automatically or redeploy docs-only changes unnecessarily. Intermittent
probe cause remains unresolved; no scientific decision regression observed.

## 10. Next Subphase

Maintain public demo and inspect retained failures if reproducible. User already has
verified public guided URL. No additional login or paid activation needed.

## 11. Critical Context

Stable site source is502a416 even after later docs commit. Signed cookie/key must
remain stable; never print tokens, keys, cookies or Playwright full request logs.
Runtime ordinary reports remain private in Blob, not Git. artifacts/local probes
are ignored controlled test evidence. Historical releasev0.1.0 sourceb65dcb60fb216e802b2ff7d71a970169a6c059a2
stays immutable. Source integrity differs from authenticity; no universal claims.

## 12. Agent Instructions

Read decisions.md/flow.md/handoff.md fully and verify actual Git state before new
work. Preserve original dirty docs and worktrees. Secrets stay ignored/CLI-managed;
use ordinary authenticated CLI, no credential requests if login works. Verify
production instead of trusting READY, and wait asynchronous alias promotion.
Never auto-retry measurement POSTs. Keep failure/nonzero exit truthful and redact
request headers. Exact source CI must be checked, not inferred from older runs.
