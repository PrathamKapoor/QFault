# QFault release verification — session dated 2026-10-23

Implementation source: `97710d834abeef93f0094b169a05d182f22c8434`.
Starting source: `c4be11cded71f7625179f30c2b33b10c3b857d4a` on
`research/external-validation`. This follow-up retains new evidence and adds an
offline verifier; frozen engine sources have not changed. Git history supplies
the final documentation commit. Local machine clock reported 2026-10-22 UTC
during final checks; the session/environment date is 2026-10-23. These are local
observations, not externally authenticated timestamps.

## Scope and results

QFault tests a bounded circuit against an independently declared single-input
contract, measures discrepancies, searches permitted edits, freezes selection,
and checks fresh original/candidate samples. A verified edit establishes the
stated contract and improvement under the declared sampling assumptions. It
does not establish unitary equivalence, hardware correctness or causal origin.

Native QuantumCircuit import and explicit QASM conversion preserve provenance
and reject unsupported semantics. API/CLI use the same engine. Original circuits
remain unchanged. The approved hero/helix and historical scientific records,
worktree, branches and ignored owner data are preserved.

Current-source protocol `current-release-replication-v4`, frozen before execution
in 97710d8, matched **72/72** prescribed scientific projections, **0 errors**,
**2,272,256 shots**, **1,127 executions**. It repeats observed designs/seeds;
this is replication, **not an untouched holdout or new performance claim**.
Counts, requests and fresh-verification intervals are retained and independently
checked by `python -m scripts.verify_replication`. Raw archive SHA-256:
`c648f4c16347306cfd6f3b79e8597681a651deb20d6e20977684990254df2b05`.

The prior external study accounts for all 2,232 attempted rows: 1,962 diagnostic,
270 recovery; 26 explicitly unsupported, 2,206 valid executed exports. There are
nine holdout source programs, not 2,232 independent architecture families.
Conservative recovery verifies 10/90 overall and 10/41 eligible; point ranking
has the same verified yield. Rejected proposals are 8 versus 31, with 5,337,088
versus 5,902,336 shots. These are bounded-policy tradeoffs, not universal repair
accuracy or an advantage over unrelated equivalence/mitigation tasks.

Historical recovery has authentic byte-matched original summary and 310 retained
exports. Conservative: 16/62 verified, 0 rejected proposals, 1,890,304 shots;
point: 16/62, 5 rejected, 1,980,416 shots. Rejected proposals are not falsely
verified repairs. Other historical raw families remain unavailable/unknown as
listed in [evidence availability](evidence-availability.md). The original source
guard still refuses a purported untouched recovery rerun on current code.

Dense-target development study has 16 measured records: all oracle fidelities
fall in the reported intervals; uniform and coefficient allocation each confirm
4/8. No production policy change was justified. The observed three-qubit dense
target's constructed best-case lower bound 0.7823152869 remains below 0.8 at
32,768 shots; that is a concrete limitation, not evidence all methods fail.

## Executed checks

Commands below used isolated CPython **3.13.2 x64**, Windows 10.0.26200,
PowerShell 7.6.6, Node 24.19.0/npm 12.0.2. Qiskit 2.3.1/Aer 0.17.2.
No Linux/macOS/ARM result is inferred from these local tests.

| Check | Actual result / local evidence |
|---|---|
| Fresh hashed installation, editable installation, `python -m pip check` | PASS in `.local/contract-release/python` and separately `fresh-python`; no shared installation changed |
| `python -m pytest tests -q -p no:cacheprovider` final assembled tree | **488 passed**, 46.96 s, one Starlette/httpx deprecation warning |
| Same full suite in fresh clone of 97710d8 | **484 passed**, 59.85 s |
| Same full suite in separately extracted evidence ZIP of 97710d8 | **484 passed**, 50.65 s; module path confirmed extracted files |
| `python -m scripts.aer_smoke` | PASS, Bell counts 00=506/11=518, also in fresh environment |
| `npm --prefix web ci`, `run check`, `run build` | PASS root, fresh clone and extracted ZIP; existing lazy Three chunk size warning remains |
| `python -m pytest tests/test_release_package.py tests/test_replication_verifier.py -q -p no:cacheprovider` | **6 passed**, 8.41 s; corrupt/truncated/unsafe ZIP and altered evidence rejected |
| `scripts.verify_external_results`, `scripts.reconcile_external_evidence` | PASS 2,206 exports / 2,232 rows; no missing/duplicate attempted cases |
| `scripts.audit_counterfactual` against byte-matched local historical summary; `scripts.verify_recovery_archive` | PASS 310 count/interval/cost reconstructions; zero engine replays |
| `scripts.current_release_evaluation --run --out artifacts/contract-release/current-replication-v4` | PASS once at 97710d8; 72 matches, no errors |
| `scripts.verify_replication` | PASS 72 exports, 2,272,256 shots / 1,127 executions; edited-cost test rejects |
| `scripts.judging_demo --out artifacts/contract-release/native-demo` | PASS actual API/Aer stages; raw exports retained locally |
| Ten existing Chromium workflows | PASS release, custom/recovery, external, blind, landing, cinematic, navigation, inspection, seven-template runner; `artifacts/contract-release/browser-*` |
| Final `scripts.release_smoke --base http://127.0.0.1:8000 --out artifacts/contract-release/browser-final` | PASS actual Aer/Chromium/export after final server restart |
| Final `scripts.native_demo_e2e --base http://127.0.0.1:8000 --out artifacts/contract-release/browser-native-assembled` | PASS native ancestry, phase detection, verified fresh recovery/download; 390/375/360 widths, no page errors; tested light-surface text contrast minimum 8.076:1 |

Browser is Chromium 151.0.7922.34 / Playwright 1.62.0. Representative actual PNGs
were opened and inspected locally. No new narrated final video is claimed. One
native browser invocation refused an already-existing output directory; its
new-directory rerun passed. No previous evidence was overwritten.

## Security and publication gates

Gitleaks **8.30.1**, official download checksum verified: tracked/intended file
snapshot and all **109** reachable commits scanned with no unclassified leaks.
Reports: `artifacts/contract-release/release-tree-secret-scan.json` and
`release-history-secret-scan-reviewed.json`. Narrow path-and-value rules classify
known api.py source fingerprints, not whole files. The first history invocation
hit Git ownership protection and scanned zero commits; only the reviewed rerun
with command-local safe.directory is counted. Binary archives and arbitrary
ignored personal files are not certified by this text scan. No credential
rotation need was established. Tracked environment secrets, databases, key files,
paper/, research/ and .tex files are absent.

`npm audit`: zero advisories after Vite 8.2.4. Isolated **pip-audit 2.10.0** on
the hashed application closure: no known vulnerabilities after certifi
2026.10.19. Reports are dated scoped checks, not future guarantees. The audit
tool's own isolated dependencies are not application requirements. No external
API/provider credentials or database are required. Required third-party notices
remain, including the separate hero provenance/license boundary.

| Gate | Status at this write | Evidence |
|---|---|---|
| G1 baseline/preservation | PASS | starting SHA above, `docs/implementation-ledger.md`; clean original inventory, refs/worktree preserved |
| G2 install | PASS | fresh hashed environments, pip check, root/clone/extraction npm ci |
| G3 input | PASS | native/strict/endian/replay tests in complete 488 suite; real native browser workflow |
| G4 scientific validity | PASS for documented scope | boundary/interval/control/resource tests, independent raw reconstructions; negative dense result retained |
| G5 recovery | PASS | fresh paired measurements, freeze/diff/abstention tests and actual demo |
| G6 evidence | PASS for advertised available archives | external/historical/current offline verifiers; missing historical families explicit |
| G7 frontend | PASS Windows Chromium | actual workflows/mobile/error states, final live smoke; no cross-browser claim |
| G8 package | PASS on 97710d8; final follow-up verification pending | both modes built/verified; clone and independent extraction install/build/full suite above |
| G9 safety | PASS scoped scan | reviewed history/tree scans, advisories, explicit staging/license review; final staged rescan required |
| G10 GitHub | NOT_RUN | no push yet at write time; verify final server-side SHA and its CI before reporting completion |

## Package and demonstration contract

Both `python -m scripts.package_submission --mode source-only --out NEW_DIRECTORY`
and `--mode evidence-inclusive` were built and passed `--verify` from committed
97710d8. The latter was extracted outside the repository, frontend rebuilt and
all 484 snapshot tests passed using the fresh hashed environment. Initial local
clone hit Git's separate ownership guard for .git; per-process exceptions fixed
the clone without a global configuration change. Source-only intentionally omits
raw report archives and declares incomplete evidence. Full mode independently
checks each advertised available archive. Neither contains Git history or owner
runtime investigations. Checksums provide consistency, not authenticity.

Repeatable pitch/demo: see [judging guide](judging-guide.md). The custom native
phase fixture first passes an inadequate Z-only contract, then detects a phase
discrepancy under independently declared IX, screens edits, freezes selection,
and verifies using 4,096 fresh original plus 4,096 fresh candidate shots. Recovery
cost is 36,864 total shots. Readout noise abstains; inadequate reserve returns
INSUFFICIENT_BUDGET with zero executions. Local simulation consumes resources
without a provider charge. No competition is selected and no submission is made.

Publication is authorized after gates; normal fast-forward integration and push
must preserve the existing main convention and history. Remote/CI observations
will be appended in an ordinary follow-up record; this file cannot contain its
own eventual final hash. Git history is authoritative.

## Follow-up extraction evidence

Evidence follow-up commit: `6998e5959180af6c7224b95cb468fa8dd8ea7503`.
Both `source-package-current` and `evidence-package-current` under
`artifacts/contract-release` were built from its clean committed source and
independently verified before extraction. Full archive has 2,206 external,
310 historical recovery and 72 new replication exports. At the independent
`qfault-evidence-6998e59` temporary extraction, module path confirms local source;
both offline archive verifiers pass. Source-only extraction runs Aer and explicitly
reports missing raw evidence rather than success. All 90 previously tracked
benchmark/config files remain byte-identical to the starting revision.

Final staged scan uses Gitleaks git --pre-commit --staged and reports no leaks.
Piping a diff to stdin loses paths and triggers the already-classified source
fingerprint; that report is not misrepresented as a credential or a clean scan.
The package scope wording is corrected in the next ordinary packaging commit.
No frozen engine source or measured result changes.

Both modes were rebuilt and verified on clean main at
`4cc58de3aff12f27ed1f6dc131507551acf1bc7a`, including all three available archive
families and the corrected scope description. A subsequent adversarial test of
the new offline verifier found an inconsistent duplicated summary source hash
was accepted. D-066 adds equality with the already hash-checked protocol. The
regression failed before the fix, then all seven package/replication tests passed
in 8.08 seconds. Frozen source/protocol/evaluation bytes remain unchanged. Final
history scan before this verifier-only correction covered 111 commits without
unclassified leaks.

Final assembled suite after D-066: **486 passed**, one Starlette/httpx warning,
46.34 seconds. No engine/protocol changes or expensive measurement reruns.

Both exact285939fpackages passed verification; source ZIP SHA-256
27ae4ce5675d82adee92ca49a947f7cdffb3a04d815fe85c960f66e82fde4585;
full ZIP ed238c0c7e4f88b043348d6fed8bec814d25b841a9151b5f8ae74f1ba81b897e.
D-067 additionally rejects boolean/float/string versions in the new offline
formats. Both regressions reproduced acceptance before the strict type guards.
No frozen scientific source, protocol or measured archive changed.

After D-067, all9package/replication tests passed8.96s; final full suite
**488 passed**, one deprecation warning,46.96s. GitHub connector returned no
runs even for the independently known historical SHA; exact-SHA hosted checks
will use GitHub's official public REST API as fallback, not infer success.

## Verified publication and final code packages

Final code: **66db0167fd46ea262bbb22282038fac331707330**, main.
Origin remains https://github.com/PrathamKapoor/QFault.git. Normal fast-forward
integration preserved both original branches and the recovery worktree. Push,
fetch, `rev-parse HEAD origin/main`, `rev-list --left-right --count
HEAD...origin/main` and independent `ls-remote` agree: same SHA, **0/0**.
All new commits have exact owner author and committer, with no trailers.

Fresh clone directly from GitHub obtained this exact source and all approved
archives; each offline verifier passes: 2,206 external, 310 historical recovery,
72 current replication. Public acquisition does not depend on the owner's ignored
runtime directories. Final code history scan covers **113 commits**, no
unclassified leaks; every focused staged diff also passed path-aware scanning.

| Final code package | ZIP bytes | SHA-256 |
|---|---:|---|
| source-package-66db016 | 2,053,192 | ce8c7f027b7e50ca390b4391cb426ca51b5ee7e13ddfcb02682d6babc3d8043e |
| evidence-package-66db016 | 8,001,131 | 928682c7b5b34b17d7e707293c9d5ac34817acef71f85987675679b911e052d9 |

Both manifests/archives verify, then were extracted into separate new directories
outside Git. Full extraction: nine package/replication tests pass in 11.13 s and
72-record verifier passes. Source-only extraction: six package tests pass in
5.52 s and actual Aer smoke passes. Earlier fresh hashed-install, frontend-build
and complete extracted-suite results remain applicable to unchanged application
code/dependencies; only independent verifier guards/tests and records followed.

[Hosted run 39837203909](https://github.com/PrathamKapoor/QFault/actions/runs/39837203909)
reports **completed/success** for exact code SHA 66db016. It executes locked
installation, pip check, npm ci/typecheck/build, full pytest, Aer and real browser
smoke on Ubuntu 24.04. Browser job individually reports success. An initial
individual checks-job response lagged the completed workflow while every step
already reported success; retain the final refreshed exact-SHA observation
rather than interpreting stale API state as a failure or a different SHA pass.
Local JSON record: artifacts/contract-release/ci-66db016.json.

G1–G9 are **PASS** within the explicit local/simulator/evidence scope. G10 is
**PASS for 66db016**: remote identity/sync and exact-SHA workflow verified.
The earlier gate table is a dated prepublication snapshot. This final ordinary
documentation-only follow-up has no scientific changes; its own hash cannot be
embedded in its contents. Its push, remote SHA and workflow must be verified
after commit and reported separately. Git history is authoritative.

Known remaining limits: several historical raw families unavailable; dense
targets unresolved under some budgets; no universal equivalence/causal/hardware
claim; cooperative timeout and single-process local trust boundary; no new
narrated video; macOS/ARM untested. No mandatory code failure remains. Ordinary
runtime records, raw local browser media and dependency environments remain
ignored and were not published.
