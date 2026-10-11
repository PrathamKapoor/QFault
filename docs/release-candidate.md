# Submission release candidate checks

Status: PARTIALLY READY. Base HEADee7120286de69f54609e53855a2c09d48a324b2b was clean on main. No scientific algorithm, threshold, default or authoritative result was changed. This release cannot yet claim independent installation.

## Fresh installation attempts

A disposable source copy was created at artifacts/release-candidate/frontend; no working node_modules was removed or copied. Node24.19.0/npm11.17.0, registry https://registry.npmjs.org/, proxy/https-proxy null, strict-ssl true. Direct imports are react, react-dom/client and local CSS. All normal scripts default to web/node_modules; an external path is an explicit development override only.

DNS resolves the official npm registry, but connect to its IPv4 addresses on443 fails EACCES, before TLS/authentication. This is neither a demonstrated TLS failure nor a missing-auth diagnosis. No elevated permission or alternate registry was used. Configured C:/Users/LENOVO/npm-cache is absent; standard AppData/Local/npm-cache cannot be read (EPERM). Workspace-local cache lacks the required metadata. No complete dependency graph can be resolved offline.

Actual commands below ran through installed node.exe and npm-cli.js with a workspace-local cache:

| Command in disposable frontend/web | Actual result |
|---|---|
| npm install --package-lock-only --offline --ignore-scripts --no-audit --no-fund | Exit1; ENOTCACHED @types/react |
| npm install --package-lock-only --ignore-scripts --no-audit --no-fund --fetch-retries=0 --fetch-timeout=5000 | Exit1; EACCES official registry |
| npm ci --offline --ignore-scripts --no-audit --no-fund | Exit1; EUSAGE, lockfile missing |
| npm ci | Exit1; EUSAGE, lockfile missing |
| npm run check | Exit1; local Vite/node_modules absent |
| npm run build | Exit1; local Vite/node_modules absent |
| npm run lint | Not run: no lint command exists |

No lockfile was hand-authored or copied. Full stderr is artifacts/release-candidate/frontend-install.json and npm-ci-exact.json. Independent-build browser testing cannot proceed past this failed dependency gate.

LibreOffice Python3.13.15 remains embedded: sys.prefix==sys.base_prefix; venv/ensurepip modules exist, but usable venv launcher files are missing (prior reproduced failures). Its launcher sets Python home/path internally. The available standard managed CPython3.11.16 supports an isolated probe interpreter, but the venv creation command timed out after15s; it is not a completed install. More decisively,3.11 cannot satisfy QFAULT/NumPy/SciPy Python>=3.12 metadata. uv only reports this installed standard interpreter. No QFAULT dependencies were installed into that probe.

Official PyPI resolves, then HTTPS connect fails EACCES on443. The accessible built-wheel cache contains chess, runningman, docplex and pylatexenc, not the pinned scientific closure; uv cache contains interpreter/sdist metadata rather than a usable installed>=3.12 interpreter. Opaque HTTP cache contents were not claimed complete or converted into unofficial wheels. No standard suitable interpreter or complete isolated dependency install was verified. See local python-runtime.json/python-isolation.json; partial probe is ignored under artifacts.

## Successful checks using retained dependencies

These checks used the documented read-only quantum/frontend/browser bridges. They establish local execution, not fresh installation. Exact outputs: benchmarks/release-candidate-verification.json and artifacts/release-candidate.

~~~powershell
& 'C:/Program Files/LibreOffice/program/python.exe' -B -u scripts/local_bootstrap.py pytest -q -p no:cacheprovider
node scripts/check-web.mjs C:/Projects/Quantum_Simulator/frontend/node_modules
node scripts/build-web.mjs C:/Projects/Quantum_Simulator/frontend/node_modules
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.browser_e2e --out artifacts/release-candidate/browser-complete
~~~

Latest results after the output-isolation regression:96 passed,1 Starlette/httpx deprecation warning (9.59s); TypeScript passed; Vite production build passed. Browser:7 actual Aer workflows, including full phase-defect recovery, no unexpected console/page/request errors, expected invalid-budget422 and390px mobile width. Freshly built assets served from the existing localhost server; no successful response mocked. The pre-fix label assertion failed because higher-cost wording was absent; full browser regression passes after the label fix. Browser screenshots remain local, ignored.

The following science commands were executed with the same LibreOffice python.exe -B -u scripts/local_bootstrap.py prefix; destinations were new:

~~~text
qfault benchmark --out artifacts/release-candidate/original
qfault evaluate --split final --out artifacts/release-candidate/final
scripts.evaluate_recovery --out artifacts/release-candidate/recovery
scripts.compare_backends --out artifacts/release-candidate/conformance
scripts.submission_demo --out artifacts/release-candidate/demo --backend aer
scripts.audit_release --out artifacts/release-candidate/scientific-audit.json
~~~

All exited0. A later final-diff check found evaluate_recovery also rewrote the fixed benchmark summary with new IDs/paths. The original was restored, that implicit publication line removed, and a genuine12-case sentinel regression failed before then passed after the fix. The full suite now includes it; scientific metrics remain unchanged. Original/final per-policy metrics including shots/evaluations/confusion matrices match excluding runtime/IDs. Recovery12 rows match all scientific outcomes/quality/cost fields:10 verified,2 inconclusive,2 negative controls rejected. Nine paired ideal/readout/depolarizing cases executed Aer/reference. The Aer demo preserves healthy/failure/noise/phase/abstention outcomes and integrity true/false/true. Every frozen final raw manifest (340) verifies against its recorded digest.

Paired category outcomes on68 final cases:56 both correct,10 phase-only correct,2 fixed-only correct,0 neither correct. Two fixed-only cases are QFT2 angle faults; phase-only cases are noise scenarios. No significance, hardware-deployability or cost dominance claim follows. See benchmarks/paired-policy-audit.json and docs/simulator-information-audit.md.

## Release blockers

A suitable standard CPython isolated install, npm-generated complete lockfile, successful npm ci/build from that graph, and browser acceptance on that independently installed build remain mandatory. Run the normal README path when official registry access and a standard CPython>=3.12 are available. Do not substitute current bridge success for these gates. No video was recorded; docs/demo.md is the verified three-minute narration script.
