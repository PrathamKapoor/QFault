# Reviewable public delivery

The first formal release version is v0.1.0, matching project metadata. Historical
local snapshot/checkpoint tags are preserved. A release is complete only after
its public asset bytes, tag source and exact-SHA CI are independently checked.

## What a download contains

Each source/evidence download is a self-contained outer ZIP containing the
original `manifest.json` and `qfault-source.zip`. The manifest names the exact
committed source and hashes every source member. Source-only omits raw report
archives and declares incomplete evidence. Evidence-inclusive verifies external,
historical recovery and current replication archives; other historical families
remain explicitly unavailable. Neither includes full Git history, dependency
directories, owner runtime storage or private recordings.

```powershell
python -m scripts.release_delivery bundle --package artifacts/reviewed-package --out artifacts/reviewed-download.zip
python -m scripts.release_delivery verify --archive artifacts/reviewed-download.zip --out artifacts/new-extraction
```

The verifier bounds outer/inner sizes, rejects duplicate/traversal/symlink or
unexpected members, checks CRC and manifest digests before extraction, and
refuses existing destinations. Extracted `project/` is independently runnable;
`package/` retains manifest/inner ZIP for verification. Use `--sha256` with an
expected checksum when available. Failure returns nonzero without a reviewed
project or success manifest. Temporary cleanup is confined to its newly created,
resolved parent directory. SHA-256/CRC are unsigned consistency checks, not
authenticity guarantees or proof of scientific correctness.

## Deliberate media/evidence selection

`scripts.record_guided_demo` requires clean committed source, records only the
actual browser surface and retains the five controlled preset exports. It checks
actual outcomes and distinct fresh execution IDs. Full normal-speed playback
must end without media errors/corrupted frames; decoded frames are visually
inspected for readability. Captions use actual recorded milestone times.
Footage is silent, with full narration supplied separately. No voiceover is
claimed. Earlier footage remains historical.

`scripts.prepare_release_assets` requires the recording, unchanged media digest,
verified playback and local check record to match the current clean commit. It
selects only fixed controlled report names, rejects human reviews/other requests,
verifies exports and independently reconstructs recovery intervals. It never
sweeps the artifact root. Its public research values come from frozen summaries
and verified membership, not manually copied success constants.
The controlled-report archive retains QASMBench's original license/notice and
QFault's license because exported import provenance contains the source program.

```powershell
python -m scripts.record_guided_demo --base http://127.0.0.1:8000 --out artifacts/new-recording
python -m scripts.prepare_release_assets --tag v0.1.0 --recording artifacts/new-recording --verification artifacts/checked-source.json --out artifacts/new-release
```

The operator's check record contains the exact source commit and actually
executed PASS checks, including full Python suite, Node stage tests, frontend,
Aer/browser and safety review. Fresh extraction/install/build checks follow
package creation. Do not turn an unavailable check into PASS. A later public
documentation commit does not retroactively enter these packages.
Use --packages-root to retain the exact source-only/evidence-inclusive inner
package bytes that were independently extracted and installed, rather than
rebuilding them after setup checks. Their modes, source commit and integrity are
revalidated before bundling.

## Owner publication and independent download

The repository connector does not expose release creation/upload. Publication
uses the [official GitHub release API](https://docs.github.com/en/rest/releases/releases)
and [asset API](https://docs.github.com/en/rest/releases/assets), with the existing
Git credential helper. Credentials remain in process memory, are never printed
or stored in artifacts, and are used only with validated GitHub API/upload hosts.
No new application provider key or external service is required.

Publication preflight checks the clean source, preserved intended origin, owner
login, remote main SHA, successful exact-source CI, reviewed asset allowlist and
unused tag/release. It creates a draft, uploads explicit files, checks remote
membership/size/digests, then publishes. Existing tags/releases/assets are never
moved or overwritten. Interrupted drafts remain inspectable rather than being
silently deleted or replaced.

```powershell
python -m scripts.public_release --publish --tag v0.1.0 --source-commit EXACT_COMMIT --assets artifacts/new-release/assets --download-out artifacts/independent-download
```

The command independently downloads every public asset to a new directory with
bounded HTTPS transfers and GitHub-owned redirects, recomputes checksums, verifies
both package modes and resolves the actual remote tag to the package source.
Upload success alone is not publication proof. Any reader can repeat the public
verification without authentication:

```powershell
python -m scripts.public_release --tag v0.1.0 --download-out artifacts/my-public-verification
```

`SHA256SUMS` lists every reviewed asset except itself to avoid a digest
self-reference. Public assets are source/evidence packages, five controlled
demonstration exports, verification summary, judging/narration guides, silent
WebM and captions. No competition submission, organizer message or paid hardware
operation is part of this workflow.
