# Executed browser verification

Status: PASS locally with installed Playwright1.62.0, pyee13.0.1, greenlet3.5.4 and Chromium151.0.7922.34. The unavailable connected-browser runtime is not evidence that installed headless browser testing is impossible. The user requested Playwright; the separate local fallback successfully executed the real application.

## Reproduce

Start the server using README commands. From C:\Projects\QFF:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.browser_e2e --out artifacts/new-browser-check
~~~

Normal environment: python -m scripts.browser_e2e --out artifacts/new-browser-check after installing the optional browser dependencies and official Playwright Chromium. That fresh installation is not verified here. The local launcher reads an existing installation without copying node_modules or changing the application interpreter's dependency selection.

## Actual assertions

- Page and contract render; circuit/qubit choices update the contract and submit the actual requested qubit count.
- Real Aer QFT4/GHZ4 clean and Bell clean, missing-gate, readout-noise and64-shot phase cases execute through the UI's normal POST path.
- Outcome, competing hypotheses, actual circuit text, Z/complementary measurements and independently VERIFIED repair display agree with the real API response. Shots sum to actual execution counts; backend labels identify Aer.
- Report tab downloads the real investigation. storage.verify_export recomputes hashes and passes; exported experiment ID matches the UI run.
- Refresh restores the history list; selecting an investigation restores its real family, qubits, scenario, policy, backend, shots and seed. Recheck integrity displays the real verification result.
- Loading/disabled state is observed in all six workflows; final screenshots wait until completion/integrity verification.
- Both original and frozen comparisons display; original artifacts remain unchanged.
-1600px desktop and390px mobile render. Mobile document width equals390px, so no full-page horizontal overflow is present. Scrollable wide tables remain intentional.
- A real7000-shot request exceeds the fixed12000 budget, returns422 and displays the validation error. This is expected negative evidence, not a mocked server failure.
- No unexpected console errors, page exceptions, failed requests or positive-workflow HTTP errors. The single expected negative422 produces its normal browser console resource error, recorded separately.

benchmarks/browser-verification.json contains experiment identifiers and exact observations. Actual downloaded report, response JSON and screenshots are in artifacts/browser-delivery: evidence-desktop.png, recovery-desktop.png, mobile.png, invalid-input.png. They are deliberately ignored, not committed binary caches. Screenshots were visually inspected.

## Regressions discovered and fixed

JavaScript Object.keys lists integer-like bitstrings10/11 before leading-zero strings00/01. Sort the display keys so plots/tables follow binary order. Loading a saved run previously set only result/integrity, leaving default controls inconsistent with its configuration. Restore the recorded controls and fetch the selected contract. Add the existing supported qubit count to the UI so4-qubit loaded runs cannot masquerade as3-qubit templates. Browser assertions reproduced both ordering/history defects before fixes and passed afterward; unsupported qubit control failed before its implementation. Scientific measurements and frozen policy logic were unchanged.

## Limits

This is a local integration check with existing installed dependencies, not clean-install proof or exhaustive cross-browser/device coverage. No arbitrary JavaScript injects a fake successful experiment, no successful response is mocked, and automated tests never pose as a human approving a repair. Human review remains pending and self-declared. There is no prerecorded demo video. Fresh Python/frontend installation and npm lockfile gates remain blocked.
