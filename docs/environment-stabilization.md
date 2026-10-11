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
