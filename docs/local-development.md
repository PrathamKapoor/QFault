# Existing machine development fallback

Unsupported for independent installation. This file preserves the verified local commands and machine-specific provenance; normal users should follow README. No donor package directory is modified.

## Development-only fallback in this workspace

From C:\Projects\QFF, PowerShell:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault circuits
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 scripts.submission_demo --out artifacts/my-demo --backend aer
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 pytest tests -q -p no:cacheprovider
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault serve
~~~

Open **http://127.0.0.1:8000/**. The interface is already built locally. Stop the server with Ctrl+C when you start it yourself. It binds only localhost.

The machine-specific launcher uses the existing LibreOffice Python 3.13.15 runtime and reads compatible installed packages from existing local package directories, including only the matching Aer package from a separate user installation. It sets PYTHONDONTWRITEBYTECODE and does not modify those projects. This is an unsupported development-only environment bridge, not an isolated installation or the normal install path. Exact paths and limitations are in scripts/local_bootstrap.py and docs/environment.json.

To check or rebuild the interface with the verified existing tools:

~~~powershell
node scripts/check-web.mjs C:/Projects/Quantum_Simulator/frontend/node_modules
node scripts/build-web.mjs C:/Projects/Quantum_Simulator/frontend/node_modules
~~~

No dependencies need to be downloaded for the current local demonstration. Standalone Playwright1.62.0 with installed Chromium151.0.7922.34 now passes the real browser workflow: configured GHZ4/QFT4 and Bell runs, fault diagnosis, independent repair display, noise/abstention controls, export download/verification, refresh/history, loading, invalid-budget422 display and390px mobile layout. There are no unexpected console/page/request failures. The connected browser remains unavailable; the user's requested local Playwright fallback executed successfully. Screenshots remain local under artifacts/browser-delivery. See [browser evidence](../benchmarks/browser-verification.json).

## Repeat the verified browser workflow

Keep the local server running, then execute:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.browser_e2e --out artifacts/my-browser-check
~~~

This separate machine-specific launcher reads installed Playwright packages and uses a cached headless Chromium; it does not alter the quantum server's dependency paths. The script rejects an existing output directory and preserves actual API results, downloaded report, screenshots and a summary. See [browser QA](browser-verification.md).

In a normal environment install the optional browser extra or requirements-browser-tested.txt, install its official Chromium with python -m playwright install chromium, and run python -m scripts.browser_e2e --out artifacts/new-browser-check. Fresh installation of those dependencies/browser is not claimed here.

