# Evidence availability and reproduction

Initial inspection: 2026-10-22 on `c4be11cded71f7625179f30c2b33b10c3b857d4a`. Updated 2026-10-23 after implementation `97710d834abeef93f0094b169a05d182f22c8434`.

Evidence classes are deliberately separate: historical frozen studies; the current
external study; ordinary user investigations in ignored `artifacts/`. A runtime
directory is never a publication source merely because a summary names it.

| Study | Public summary / protocol | Public raw evidence | Independently checked this session |
|---|---|---|---|
| Original/template diagnosis | `benchmarks/results.json`, `diagnostic-final.json`, `configs/diagnostic-evaluation.json` | Referenced ignored paths; public acquisition UNKNOWN | NOT_RUN |
| Measurement-only holdout | `benchmarks/measurement-boundary-holdout-20261013.json` | Referenced ignored paths; public acquisition UNKNOWN | NOT_RUN |
| Custom lab | `benchmarks/custom-lab-holdout-10240.json` | No public count-level archive established | NOT_RUN |
| Target witnesses | `benchmarks/target-witness-holdout.json`, `configs/target-witness-protocol.json` | No public count-level archive established | NOT_RUN |
| Historical recovery | `benchmarks/counterfactual-recovery-holdout.json`, `configs/counterfactual-protocol.json` | `benchmarks/historical-recovery-v1/reports.jsonl.gz`, versioned public-safe archive selected from the authentic original worktree | 310 manifests/count-based reconstructions verified; original summary byte-identical; no claim of untouched rerun |
| External reference-relative study | `benchmarks/external-holdout-v1/summary.json`, `configs/external-validation-protocol.json` | `benchmarks/external-holdout-v1/reports.jsonl.gz`, committed public-safe evaluation records | 2,206/2,206 exported reports valid; all 2,232 rows accounted for, including 26 unsupported cases |
| Current-source deterministic replication | `benchmarks/current-release-replication-v4/summary.json`, `configs/current-release-replication-v4.json` | `benchmarks/current-release-replication-v4/reports.jsonl.gz` | 72/72 exact prescribed scientific projections, zero errors; 2,272,256 shots and 1,127 executions; independent recovery interval reconstruction |

The current external archive is about 4.65 MB compressed. It contains controlled
research cases already deliberately tracked, rather than owner runtime sessions.
Its summary binds the archive digest. Source includes the independent parsers,
recount and original QASMBench notices. Hashes establish consistency, not identity
of an author, an external timestamp or scientific correctness.

```powershell
python -m scripts.verify_external_results benchmarks/external-holdout-v1/summary.json
python -m scripts.reconcile_external_evidence benchmarks/external-holdout-v1/summary.json benchmarks/external-holdout-v1/reports.jsonl.gz
python -m scripts.verify_recovery_archive
python -m scripts.verify_replication
```

The newly curated historical recovery archive is 1,057,578 compressed bytes and
contains exactly the original 310 exports, with no human reviews or ordinary user
sessions. Its manifest binds the unchanged original summary and archive bytes.
This is new publication of old records, not a new experiment or an independently
authenticated reconstruction of execution time. Other historical results remain
summary-only where the table says so.

Historical results remain frozen and are not new-release performance claims.
Their raw availability must be shown beside any historical headline. A missing
old archive must not be replaced by newly executed records using old identities.

Historical recovery source hashes are byte digests. Reproduce at the recorded
evaluation revision `5034972c3129c18f4f990dfae9993d71086db2fd` in an isolated checkout
with its original protocol, preserving the exact recorded bytes. Windows CRLF
can change a byte digest; a separate diagnostic comparison may replace every
CRLF byte pair with LF and hash the resulting UTF-8 bytes, without changing or
reinterpreting the original digest. Current sources intentionally postdate that
protocol; the original holdout command must continue to refuse them. Historical
environment availability and an exact-byte reproduction remain NOT_RUN here.

Current-source reproduction uses `scripts.current_release_evaluation --run --out
artifacts/new-replication` and frozen v4. It records source 97710d8, LF-normalized
source digests, protocol byte digest and all raw exports. The published gzip is
449,269 bytes, SHA-256 c648f4c16347306cfd6f3b79e8597681a651deb20d6e20977684990254df2b05.
This repeats already observed designs/seeds; it is not a new untouched holdout or
new generalization result. Draft v1–v3 were never executed. A scientific source
change requires a new protocol, never editing old hashes. See external-validation.md
for the original external study and release-verification-20261023.md for this release.

## Package contracts

```powershell
python -m scripts.package_submission --mode source-only --out artifacts/source-package
python -m scripts.package_submission --mode evidence-inclusive --out artifacts/evidence-package
python -m scripts.package_submission --verify artifacts/evidence-package
```

Both modes require clean committed source, use exclusive new outputs and contain
a source ZIP rather than complete Git history. They omit paper/, research/ and
all .tex files. No owner runtime tree or media directory is swept into an archive.
The manifest records exact commit, mode, per-member hashes and package checksum.

Source-only omits all raw report archives and declares `evidence_complete=false`.
Evidence-inclusive verifies external, historical recovery and current replication
archives, report/row bindings and membership before writing any success manifest. Its
`evidence_complete=true` applies only to those explicitly named available studies,
never to unavailable historical families. Both retain historical summaries and
this availability ledger. No fresh-install success is inferred from packaging.

Verify the package before extracting `qfault-source.zip` into a new empty folder.
Follow its README for isolated installation and checks. The verifier reads ZIP
members without extracting, rejects traversal/symlink/duplicate entries, caps
archive expansion and recomputes member/package digests. A source-only archive
cannot run the omitted external report verification until those bytes are
obtained from the same source revision. Checksums are not authenticity guarantees.
