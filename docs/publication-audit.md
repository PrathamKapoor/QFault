> **Historical record** (2026-10-13, before publication). Its statements that pushing was not authorized and that public main was behind development are superseded: development history was published to `main` on 2026-10-13 (24f4e61, CI passing). Current status: see the repository [README](../README.md) and [release history](release-history.md).

# Current project-development update (2026-10-13)

Canonical repository: https://github.com/PrathamKapoor/QFault. Public main was verified at ea71bd981ee0d6a394b4d26e4a904c92bc4f5ed3; local main is preserved at f36665616c2aee95a7b82e764adcf290b9e05468. New work is isolated on hardening/blind-measurement with both snapshot tags retained. No push is authorized for this work. The user has dropped competition eligibility and presentation work; this is continued project development. Independent Python/npm installs have now succeeded; see scientific-hardening.md for current evidence. The dated audit below is historical.

# Publication audit

Assessment: 2026-10-11. Starting source:90503efe6576d1fcb080ef92b2c12c34f0fd050b, clean main. Product QFAULT; selected repository PrathamKapoor/QTrust. Publication is **FAILED / environment-blocked**: the connected GitHub account is PrathamKapoor, the destination is public with push/admin permission and no main branch returned, but local Git HTTPS cannot connect to github.com:443. The authorized normal git push -u origin main and subsequent fetch/ls-remote each exited128 because Git could not connect. Connector recheck still returns no main, and README retrieval returns404: This repository is empty. No remote SHA or upstream branch exists to verify. A normal push from a permitted environment and matching remote SHA remain required. No force push or reconstruction of historical commits is authorized.

[Machine-readable executed checks](../benchmarks/publication-verification.json) record this audit. Raw command logs, fresh screenshots and reproduction records are local-only under artifacts/publication-audit. They are not downloadable through a clone.

| Finding | Severity | Evidence | Action / verification |
|---|---|---|---|
| Two broken relative links | MEDIUM | docs/local-development.md resolved targets beneath docs incorrectly | Corrected to ../benchmarks/browser-verification.json and browser-verification.md; local Markdown targets rechecked |
| Local media/raw evidence could be mistaken for clone content | MEDIUM | Ignored artifacts referenced by README and delivery guides | Explicit local-only labels and no public video URL; scripts regenerate new records after installation |
| Obsolete browser-availability statement | LOW | scripts/http_release_smoke.py emitted no browser available despite separately passing browser workflows | HTTP report now scopes browser coverage to a separate runner; actual pre-fix assertion fails and post-fix HTTP check passes |
| Stale no-prerecorded-video sentence | LOW | docs/browser-verification.md contradicted the current real silent footage | Replaced with current local-only silent/narration status |
| README normal reproduction used the local bridge | MEDIUM | Demo/evaluation examples invoked machine-specific launcher | Normal examples now use python -m; development-only provenance remains separate |
| Independent dependency installation unavailable | HIGH, unresolved | One official npm and PyPI HTTPS probe each returns EACCES; no own npm lockfile | Preserve working environment; no invented lockfile or clean-install claim |
| Git publication transport unavailable | BLOCKER for publication, environmental | git ls-remote failed to connect to github.com:443; connector identity/permission works | Exact origin configured; normal push/fetch and remote SHA verification still required |

## Execution evidence

All checks below used the retained environment, not a fresh installation. P denotes the embedded LibreOffice Python3.13.15 executable documented in local-development.md. The frontend override is that document's existing read-only node_modules path.

| Executed command | Observed outcome |
|---|---|
| P -B -u scripts/local_bootstrap.py pytest -q -p no:cacheprovider |99 passed,1 existing Starlette/httpx deprecation warning; post-correction12.15s |
| node scripts/check-web.mjs with explicit retained dependency override | Exit0 |
| node scripts/build-web.mjs with the same override | Exit0, Vite8.2.2 production build |
| P -B -u scripts/local_bootstrap.py scripts.compare_backends --out artifacts/publication-audit/conformance |9 paired Bell/GHZ/QFT ideal/readout/depolarizing scenarios pass |
| P -B -u scripts/local_bootstrap.py scripts.submission_demo --out artifacts/publication-audit/demo --backend aer |5 real Aer scenes; healthy, logical recovery, noise, phase recovery and abstention; tamper/restore true/false/true |
| P -B -u scripts/browser_bootstrap.py scripts.browser_e2e --out artifacts/publication-audit/browser |7 actual Aer workflows; no unexpected console/page/request errors; history/configuration/export/invalid422/mobile pass |
| P -B -u scripts/local_bootstrap.py scripts.http_release_smoke --out artifacts/publication-audit/http-corrected |4 real HTTP workflows, production assets, valid exports and invalid422 controls pass; corrected scope check passes |
| P -B -u scripts/local_bootstrap.py scripts.audit_release --out artifacts/publication-audit/frozen-audit.json |340 existing frozen manifests verify; paired56 both correct/10 phase-only/2 fixed-only/0 neither |
| P -B -u scripts/local_bootstrap.py qfault benchmark --out artifacts/publication-audit/original |All original scientific row fields and policy metrics excluding incidental metadata/runtime match |
| P -B -u scripts/local_bootstrap.py qfault evaluate --split final --out artifacts/publication-audit/final |All final scientific row fields and policy metrics excluding incidental metadata/runtime match |
| P -B -u scripts/local_bootstrap.py scripts.evaluate_recovery --out artifacts/publication-audit/recovery |All12 scientific rows/interval match:10 verified,2 inconclusive; both negative controls REJECTED |
| P -B -u scripts/local_bootstrap.py qfault verify-report on fresh hidden_logical_failure.json / disposable tampered-report.json |Actual exits0/1; changed count rejected as investigation digest mismatch |
| git fsck --full | Exit0; two dangling development blobs, no corrupt-object error |

## Security and tracked-content review

Custom redacted pattern scan inspected all251 local Git objects, including184 blobs and11 reachable commits. No matching private-key, GitHub-token, AWS-key, credential-URL, JWT or quoted-secret-assignment patterns were found. No tracked historical .env, credential file, personal database, dependency cache, runtime log, submodule or LFS configuration was found. Largest blob is721986 bytes. Commit messages have no tool co-author/generated-by trailers. This is a bounded pattern audit, not a cryptographic proof that all possible secrets are absent; no credential rotation is indicated by its findings. Ignored dependencies/media were not staged.

Placeholder/claim/name searches were inspected in context. Matches are legitimate input placeholders, unavailable-feature warnings, negative scientific claims or source attribution. These are retained. Current source uses real Qiskit execution, candidate mutations and finite-shot records; hidden mutation truth is attached after the prediction digest. Ideal attribution and repair selection still use privileged state simulation, clearly labeled in the UI and reports. No new quantum functionality or threshold changes were made.

## Results and remaining delivery boundaries

Frozen final classification totals remain evidence34/68, fixed58/68, random21/68, threshold34/68, phase66/68. Phase487424 versus fixed348160 shots is40% extra, not resource dominance. Two QFT2 angle faults remain missed by phase. Selected recovery10/12 is not a general repair rate; two QFT4 cases remain inconclusive. Zero observed false diagnoses among10 evaluator-correct cases is not an operational false-positive guarantee.

The genuine176.56-second silent footage remains local-only, unchanged at13580390 bytes (SHA25623bfd3492fd21a1238c0653116dbe0a56d74ff98ee6d5ee67c6239baa1845a7e). Existing complete-playback proof was inspected; no new narrated edit or public media URL exists. See video.md and video-timeline.json for the exact voiceover and recording instructions.

The official event page was rechecked: conflicting deadlines, team rules, workshop-lead status and prompt timing still require organizer confirmation. No competition submission was made. GitHub publication, fresh installation and eligibility are separate gates. See organizer-confirmations.md and transfer.md.

## Transfer after the blocked push

The audited27ed91f source was packaged successfully under artifacts/qfault-publication-transfer with2425 verified raw JSON files and genuine local media. Its manifest identifies that exact historical snapshot. A final package for the clean closing commit is generated separately under artifacts/qfault-publication-final; inspect its manifest for the exact source SHA. Neither package implies successful publication or independent installation. The publication failure log and post-attempt Git checks are artifacts/publication-audit/push-command.json and publication-result.json.
