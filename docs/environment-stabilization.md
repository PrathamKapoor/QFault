# Installation and Aer investigation

Date: 2026-10-11. Base commit d30535caac17fb55718ac313c3e033dabb631364, initially clean. Existing suite reran: 62 passed, one Starlette/httpx warning. Original benchmark at artifacts/stabilization-original exactly matches committed policy metrics and selected recovery outcomes.

Accessible runtime: LibreOffice Python 3.13.15, MSC 1944, 64-bit AMD64, extension suffix .cp313-win_amd64.pyd. The bridge's Aer distribution is C:/study/projects/quanum_ml/.python_lib/qiskit_aer-0.17.2.dist-info; WHEEL declares cp311-cp311-win_amd64 and the actual binary is controller_wrappers.cp311-win_amd64.pyd. Import fails ModuleNotFoundError: No module named qiskit_aer.backends.controller_wrappers. Package-path sharing exposes the wrong ABI. The origin of that installation is unverified; no donor packages were changed.

[Official PyPI Aer 0.17.2 files](https://pypi.org/project/qiskit-aer/0.17.2/#files) list qiskit_aer-0.17.2-cp313-cp313-win_amd64.whl, SHA-256 b38c5dfdc6cb2bacac78a47b0df8247123051564007fdecedb8ffbd4256f0f09. This establishes an official compatible wheel exists, not that it was installed or executed here. No arbitrary wheel was downloaded.

Actual attempts:

- LibreOffice python.exe -B -m venv C:/Projects/QFF/.venv: exit 1; missing lib/venv/scripts/nt/venvlauncher.exe and venvwlauncher.exe. Partial directory contains pyvenv.cfg and an empty Scripts directory; it is ignored and unusable.
- Direct official PyPI fetch: EACCES. PowerShell Invoke-WebRequest: Unable to connect to remote server. Compatible-wheel installation and pip conflict checking in isolation could not proceed.
- npm --prefix web install --package-lock-only --ignore-scripts --offline: ENOTCACHED for @types/react metadata.
- Same resolution online with a workspace-local npm cache and no retries: EACCES fetching registry.npmjs.org. No lockfile or fresh node_modules was created. The existing dependency bridge remains an explicitly incomplete release accommodation.
- Node v24.19.0 and npm 11.17.0 verified again. Direct frontend versions remain those actually tested in web/package.json.
- Browser runtime initialized, then reported No browser is available; discovery returned an empty list. No browser E2E, console inspection or screenshots can be claimed. HTTP and build checks are separate evidence.

Later discovery supersedes the earlier Aer-unavailable conclusion (D-016): C:/Users/LENOVO/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0/LocalCache/local-packages/Python313/site-packages contains Aer0.17.2 with cp313-cp313-win_amd64 WHEEL metadata and controller_wrappers.cp313-win_amd64.pyd. Actual AerSimulator Bell execution returned {'11':521,'00':503} at1024 shots, seed7. No installation or binary renaming was needed.

The local bootstrap now loads only that Aer package by import spec, keeping Qiskit2.3.1, NumPy2.5.2, SciPy1.18.1 and psutil7.2.2 from the already verified bridge. It does not add the entire user-package directory, whose separate Qiskit2.5.1 would contaminate version selection. Eight actual Aer regression tests pass. Nine paired Bell/GHZ/QFT ideal/readout/depolarizing comparisons show density differences <=3.34e-16 and sampled TV <=0.0188 against analytic noisy distributions (4096 shots/backend/case). See benchmarks/backend-conformance.json.

qfault.backends is now an explicit optional adapter. Requests choose reference or aer, default reference; failed Aer requests are never silently relabeled as successful reference execution. The reference implementation is retained. Frozen policy results use reference, while benchmarks/submission-demo.json and http-stabilization.json record actual Aer workflows.

Fresh isolated installation remains blocked by the launcher and registry failures above. On an unrestricted machine use a normal CPython3.13 installation, the tested dependency files and official Aer0.17.2 package. Do not use the partial .venv or copy donor node_modules. No browser was available; builds and HTTP checks are not browser E2E.

## Subsequent browser and interpreter findings

The connected-browser runtime again returned No browser is available and discovery []. The user requested standalone Playwright where available. Read-only discovery found installed playwright1.62.0, pyee13.0.1, greenlet3.5.4 and cached Chromium1234 (reported browser151.0.7922.34). Actual headless launch and full UI testing succeeded. Browser E2E is now verified locally; earlier unavailable-browser statements describe the connected runtime and the earlier audit state. scripts/browser_bootstrap.py loads these test dependencies in a separate process, never into the quantum server. benchmarks/browser-verification.json records six actual investigations, clean console/page/request checks, report download/hash checking, refresh/history, desktop/mobile and actual invalid422 display. Screenshots remain artifacts/browser-delivery, ignored by Git.

Installed uv0.12.5 was also inspected/executed without downloads. uv venv --python LibreOffice/program/python.exe --offline --no-python-downloads --cache-dir C:/Projects/QFF/.local/uv-cache C:/Projects/QFF/.venv-isolated failed: Could not find a suitable Python executable for the virtual environment based on the interpreter C:/Program Files/LibreOffice/program/python-core-3.13.15. A retry at a new destination reproduced this error; partial ignored directories were inspected and retained. uv python list --only-installed finds managed CPython3.11.16. Pinned NumPy2.5.2/SciPy1.18.1 metadata requires Python>=3.12, so that interpreter cannot satisfy the verified manifest. Corrected project requires-python from>=3.11 to>=3.12 with a failing-then-passing dependency-range regression. The quantum application still executes Python3.13.15; no isolated installation is claimed. Local/npm cache access remains denied and no own npm lockfile could be validated.
