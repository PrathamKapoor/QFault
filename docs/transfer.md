# Portable source and evidence handoff

QFAULT remains PARTIALLY READY. This package transfers the actual committed source and measured evidence; it does not prove a fresh installation. Official npm and PyPI DNS resolve, but one bounded HTTPS probe per source on October11 returned connect EACCES before TLS. Prior offline npm resolution lacked metadata. No registry retry, security-policy change, unofficial mirror or fabricated lockfile is part of this handoff.

## Contents and integrity

From a clean repository with the measured artifacts present, run in the working environment:

~~~powershell
python -m scripts.package_submission --out artifacts/qfault-submission --demo artifacts/submission-delivery/browser-recording --demo artifacts/submission-delivery/demo
~~~

On this restricted machine use the explicitly development-only launcher in [local-development.md](local-development.md) instead of python -m. Output destinations are exclusive; choose a new directory for reruns.

- qfault-source.bundle contains the committed main history, source, manifests, tests, notices and documentation. Git verifies the bundle. It excludes working-tree/private configuration and ignored dependencies.
- qfault-evidence.zip contains the raw JSON evidence referenced by the seven frozen benchmark/demo summaries in the source bundle. Every included investigation is checked against its recorded manifest digest and ArtifactStore.verify before packaging. Original benchmark recovery paths are reconstructed from their recorded experiment identifiers.
- qfault-demo-material.zip contains genuine browser screenshots, responses, silent WebM footage and current CLI demo exports. The intentionally tampered export is a labeled negative control, not a valid investigation.
- manifest.json binds package byte lengths and SHA256 hashes to the exact source commit. ZIP CRC checks detect archive corruption. These are unsigned consistency checks, not proof of authenticity, authorship or scientific truth.

Keep all four files together. Media and archives remain local ignored deliverables, avoiding large redundant binaries in Git. Transfer these files using a user-approved mechanism; no publication or remote upload is performed here. Do not rely on Git alone to carry ignored raw experiments.

## Restore on an unrestricted development computer

Use standard 64-bit CPython3.13 and Node24; the retained runtime was3.13.15 and Node24.19.0/npm11.17.0. Python metadata requires>=3.12, but other interpreters have not been scientifically validated. Do not use embedded LibreOffice Python for fresh-install acceptance.

~~~powershell
Get-FileHash qfault-source.bundle,qfault-evidence.zip,qfault-demo-material.zip -Algorithm SHA256
git clone -b main qfault-source.bundle QFAULT
Expand-Archive qfault-evidence.zip -DestinationPath QFAULT
Expand-Archive qfault-demo-material.zip -DestinationPath QFAULT
cd QFAULT
git rev-parse HEAD
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-browser-tested.txt
.venv/Scripts/python -m pip install --no-deps -e .
npm.cmd --prefix web install --package-lock-only
npm.cmd --prefix web ci
npm.cmd --prefix web run check
npm.cmd --prefix web run build
.venv/Scripts/python -m pytest tests -q
.venv/Scripts/python -m scripts.compare_backends --out artifacts/fresh-conformance
.venv/Scripts/python -m scripts.submission_demo --out artifacts/fresh-demo --backend aer
.venv/Scripts/python -m qfault evaluate --split final --out artifacts/fresh-final
.venv/Scripts/python -m qfault verify-report artifacts/fresh-demo/hidden_logical_failure.json
.venv/Scripts/python -m playwright install chromium
.venv/Scripts/python -m qfault serve
~~~

Compare the hashes and HEAD with manifest.json. The clone's origin is the local bundle, not a published GitHub repository. In a second terminal from QFAULT:

~~~powershell
.venv/Scripts/python -m scripts.browser_e2e --out artifacts/fresh-browser --record-video
~~~

Inspect each actual exit status. Stop if dependency resolution fails; preserve its error. npm must generate the complete lockfile itself, then ci must install from it. Review and commit the valid lockfile only after check/build and the scientific/browser suite pass. The source does not include a valid npm lockfile yet. These normal-install commands are executable instructions, not a claim they succeeded in the restricted environment. No lint script is declared.

## Dependency-path inventory

Normal Python imports use the installed qfault package and its declared dependencies. Normal npm scripts resolve web/node_modules. requirements-tested.txt, requirements-aer-tested.txt and requirements-browser-tested.txt record observed pins; they are not a fresh isolated resolver result.

The following are explicitly local development fallbacks: scripts/local.ps1 and local_bootstrap.py select embedded Python and read-only donor site-packages; browser_bootstrap.py/local_browser.ps1 select the already installed Playwright; web-tools.mjs permits an explicit dependency-directory override used for the retained frontend build. None belongs in the normal install path. No donor modules were copied or modified. Historical environment/reuse documents and verification JSON retain absolute paths as provenance. README normal setup and this transfer recipe require no donor repository.

## Acceptance after transfer

A Git bundle clone alone is source-transfer verification. Fresh-install acceptance additionally requires isolated Python dependency installation, genuine Aer and reference execution, own npm ci/check/build, tests, CLI demo, real API, browser workflow, export verification and tamper rejection. Record exact versions/errors and compare frozen metrics without tuning. Organizer eligibility/deadline and final narrated video approval remain separate external actions; see organizer-confirmations.md and demo.md.

## Actual local transfer validation

The corrected package from cf23b95e747b7d061323232caf48de071cef8b15 was built and Git-verified, cloned to artifacts/transfer-restored, and restored with guarded standard-library ZIP extraction. All package SHA256/lengths and both ZIP CRC checks passed:2425 raw evidence files and39 demo-material files. Existing files were required to match before any write; no source overwrite occurred. The restored clone remained clean with102 tracked files and the exact source HEAD. A global Git-ignore read warning did not prevent cloning/status verification. Evidence: artifacts/submission-delivery/transfer-verified.json; summary: benchmarks/submission-verification.json. This validates transfer only; no dependency installation was performed in that copy.

Final delivery is generated from the final clean committed source into artifacts/qfault-submission. Its manifest, rather than this historical validation hash, is authoritative for that package's exact HEAD. The earlier artifacts/transfer-validation package is retained only as the failed duplicate-summary restore audit; do not use it for submission.
