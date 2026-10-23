# Full interactive Vercel deployment

PROPOSED and owner-authorized: preserve the existing engine, contracts, hero and
frozen evidence. Add an opt-in ASGI hosting adapter only; local startup stays unchanged.
Vercel account verified Hobby, hex-sembly; existing trial project preserved. New
qfault project/private Blob store created without upgrades. Original checkout and
its uncommitted operation notes are preserved; work is isolated in feat/vercel-hosting.

1. Verify actual private Blob create/read/ETag-conditional overwrite; reject a stale
   writer. Use the official Blob HTTP protocol with stdlib, no SDK dependency.
   Check origin metadata against downloaded ETag to reject stale cached state.
2. Test first: signed browser-isolated sessions, strict external Host/Origin,
   independent app instances restoring reports, blind lifecycle, lost lease/stale
   writer, corrupt/traversal state, byte limits and storage failures before success.
3. Implement qfault.hosting around create_app(temp root). Private per-browser
   snapshots retain existing canonical JSON documents unchanged. Conditional leases
   serialize session mutations across function instances; commit before returning
   success. Timeouts leave an expiring lease, never a false verification.
4. Add Vercel entrypoint/config/hashed requirements, explicit source upload allowlist,
   hosted privacy notice and documentation. Never upload local runtime data or secrets.
5. Run targeted/full tests, frontend build, actual local hosted-adapter Aer/browser
   tests and two-session/cold-start persistence checks. Preserve scientific source bytes.
6. Deploy a preview, inspect build/runtime and exercise actual deployed workflows.
   Then promote the verified deployment to production and verify its stable URL.
   Record exact deployment/source identity and honest platform limits; no paid plan.

Limits: Vercel function time/payload limits; 32MiB session snapshot, 1,000JSON files,
64 mutating operations per browser session, 30-day signed cookie. No distributed
global rate-limit claim. Losing the cookie loses access; export important reports.
Private storage is free only within Hobby quota; quota exhaustion must fail clearly.

Executed: provider CAS/consistent reads passed; 531 assembled tests passed;
frontend check/build passed; corrected preview passed full API/browser smoke.
Production source502a416 deployed READY with public alias, separate API privacy/
blind/export checks and complete real guided browser workflow passed. Preserve
intermittent production test failures as documented in vercel-hosting.md; do not
claim guaranteed availability or forced cold-start testing. No scientific study
was rerun and no frozen protocol, raw evidence or mathematical policy changed.
