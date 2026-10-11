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

On an unrestricted machine, use a normal CPython 3.13 installation and the README installation procedure, then install the official matching Aer wheel into that environment and validate actual AerSimulator counts, noise and bit ordering before integrating a backend adapter. Do not fix an ABI mismatch by renaming the .pyd. Do not use QFAULT's partial .venv or copy donor node_modules. An Aer execution adapter is deliberately not advertised as implemented.
