# Cinematic frontend verification — 2026-10-12

This is frontend verification of the existing scientific product. No backend, frozen benchmark, policy, tolerance or scientific artifact was modified. Generated screenshots/raw API records remain local under ignored `artifacts/`; they are not public clone assets.

## Executed commands

From `C:\Projects\QFF`, with the integrated server on port 8000:

```powershell
npm.cmd --prefix web ci
npm.cmd --prefix web run check
npm.cmd --prefix web run build
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 pytest tests -q -p no:cacheprovider
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.browser_e2e --out artifacts/cinematic-science-delivery
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.workspace_navigation_e2e --out artifacts/cinematic-navigation-complete.json
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.cinematic_e2e --out artifacts/cinematic-20261012-delivery
```

- npm ci: 31 packages installed, 32 audited, zero reported vulnerabilities. Genuine npm-generated lockfile and local web/node_modules, no frontend bridge.
- TypeScript: passed. Production Vite build: passed; 100 modules, last observed build 502ms. Shared Three chunk 548.49kB / 136.08kB gzip triggers the retained >500kB warning. Main entry 217.00kB / 70.13kB gzip; workbench and effects split separately. Build duration is not application load performance.
- Python: 99 passed in 16.39s, one existing Starlette TestClient deprecation warning. Python and Playwright still use the explicitly disclosed local bridge, not a fresh isolated installation.
- Seven actual Aer workflows: QFT4/GHZ4/Bell clean, Bell missing-gate repair, readout noise, phase-only repair and 64-shot abstention. Both selected repairs verified independently; noise/insufficient cases propose no repair. Export download verifies, integrity recheck passes, saved settings/history restore, counts preserve binary ordering, frozen 66/68 comparison displays, actual budget error returns 422. No unexpected console/page/request errors; the expected invalid request logs one 422 console message.
- Navigation regressions: GHZ4/1024 draft survives home/back, delayed real response cannot replace a newer selected record, saved route refresh works, absent record clears export/output, overview/history display API failure, mobile navigation Escape returns focus. No page errors. This race check delays a real fetched response; it does not fabricate quantum outputs.
- Cinematic acceptance: first entry stages, genuine GL frame, reframe/PixelSwap, restored focus, renderer removal, direct routes, back/forward/refresh, all five viewport sizes, reduced motion and forced absent WebGL fallback. No page errors. Sizes: 1920×1080, 1440×900, 1366×768, 768×1024 and 390×844; no document-width overflow.

## Captures and visual review

`artifacts/cinematic-20261012-delivery/` contains hyperspeed.png, techtext.png, hero.png, landing-highlight.png, reframe.png, pixel-swap.png, workbench.png, webgl-fallback.png and landing/workbench captures for all five widths. Short-state captures use Playwright's browser clock to freeze genuine application timers/RAF; the reframe capture finishes finite CSS transitions through Playwright's animations-disabled screenshot option. No pixels or scientific content are synthesized. First-frame markers prevent capturing an attached but unpainted GL canvas. Early captures with unpainted scenes were rejected and retained only as ignored drafts.

`artifacts/cinematic-science-delivery/` contains evidence-desktop.png, recovery-desktop.png, mobile.png, invalid-input.png, actual API records, exported report and summary.json. Images were opened and inspected for scene lighting, text overlap, CTA visibility, circuit readability, scientific output and mobile overflow. The targeted fixes enlarged mobile sculpture framing, corrected the mobile wordmark vignette, and delayed overview captures until real data loaded. Every created experiment now updates its saved URL; refresh verifies that identity. Review and integrity continuations also guard the captured selection generation.

The final inspection smoke `scripts/inspection_smoke.py --out artifacts/frontend-inspection` passed after the local implementation commit and persistent server restart. HTTP 200, actual WebGL landing, focused workbench and real Aer missing-gate repair `experiment_6b0df8dfacd047f49b2d76fda979c9c2` (VERIFIED) are recorded in `artifacts/frontend-inspection/summary.json`. No console/page/request errors. Its landing-desktop.png and workbench-desktop.png were opened and visually inspected. Server PID 10032 remains on 127.0.0.1:8000 in persistent terminal session 63723; that session contains stdout/stderr. Process/URL metadata is ignored `.local/frontend-inspection.json`. No disruptive tests followed establishment of this inspection session.

## Performance and limits

A separate, unscreenshoted fresh-context run measured 6.485s to the hero phase with navigation load duration 74.4ms (`artifacts/cinematic-20261012-delivery/summary.json`). Earlier independent runs measured 6.567s and 6.777s. This headless local measurement includes module execution/graphics initialization; it is not FPS, GPU timing or Lighthouse. Screenshot capture can further stall software GL. The sequence's nominal timers total 1.3s but do not guarantee cold graphics initialization duration. Returning/reduced-motion visitors bypass the intro; Skip/Escape and direct workbench routes remain available.

Renderer lifecycle is enforced by stage unmounting, DPR caps, mobile quality reduction, visibility/intersection pauses and disposal. Browser tests verify landing canvases are absent in the workbench; exhaustive GPU leak profiling, hardware-device timing and non-Chromium testing were not performed. The static fallback is explicitly identified and is not claimed as interactive 3D. Human review, scientific generalization, hardware execution and fresh Python installation remain outside this frontend verification.
