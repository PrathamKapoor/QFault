# Landing recovery — 2026-10-12

This recovery starts from clean main at `c5fb023a5bbf53a9790548731eebae9b2df7101a`. It supersedes the previous landing's visual-acceptance claim. The workbench, PixelSwap component, backend, contracts, diagnostic policies and frozen benchmark artifacts are unchanged.

## Reproduced causes

The genuine pre-edit captures are in ignored `artifacts/landing-rebuild-baseline/`. `baseline-diagnostics.json` records the actual DOM/canvas geometry. At 1440×900 the visual stage was 1051px wide (73% of the viewport) and the decorative wordmark was 219px. Four similar thick closed sweeps crossed the same central volume and the wordmark; the foreground text clip did not restore readability. Dark metal reflected a predominantly dark/violet studio, leaving narrow highlights and broad featureless surfaces.

MoltenMetal was mounted and rendering on the tested 16-core desktop. It was not a missing component: dark colors, shader alpha (`intensity × .28`), extra CSS opacity `.6` and a strong vignette suppressed its folds. Mobile, reduced-motion and lower-core devices excluded it altogether. Captions were 8–9px and muted. Decorative canvases did not explicitly suppress pointer events.

Hero copy and buttons existed in the baseline; they were visually overwhelmed rather than absent on the inspected desktop. The fixed-height, overflow-hidden root contained only an absolutely positioned hero. There were no workflow, capability or scientific-evidence sections. The mobile artwork preceded the copy in a rigid layout. Navigation lacked the requested public destinations.

The first new regression run, `artifacts/landing-rebuild-red`, failed because the heading “How QFAULT works” did not exist. No tests were weakened to accommodate the new layout.

## Corrected composition

`Landing.tsx` now places stable silver/lilac QFAULT typography and usable copy/actions in the left column, separate from a right-hand stage occupying 46% of desktop width. Large decorative text planes no longer cross the geometry. Mobile presents the explanation/actions first and fits the framed sculpture below them in the opening viewport. Header links scroll to Platform/Research without changing the hash route; Benchmarks enters the existing destination, GitHub opens the actual repository. The final CTA uses the same existing entry choreography.

`quantumSculpture.ts` is original geometry: two tapered flattened open ribbons, three narrower reflective paths and a fine violet filament. Explicit asymmetric control points replace four similar closed sweeps. A neutral procedural reflection studio, graphite/silver physical materials, fine roughness variation and a dim violet rim make metal readable without a purple emissive body. Bounds-based camera fitting preserves the silhouette. The fallback SVG follows the new open-path arrangement and remains explicitly labelled static.

MoltenMetal retains the adapted official React Bits shader and notices. Its supplied palette/alpha/glow now produce perceptible graphite/violet folds; the extra opacity multiplier is removed and the vignette protects text without erasing the stage. Uniforms are initialized from props before the first draw, preventing a white default frame. The capability-probe canvas is reused rather than discarded for a second context. Reduced-motion/mobile/lower-core views render a static shader frame. Animated drawing is capped near 30 requests per second, with lower buffer resolution and existing visibility/intersection cleanup. These are scheduling limits, not measured FPS claims.

Below the hero are the real Execute → Observe → Diagnose → Verify workflow, supported capabilities, and explicitly frozen finite results: phase-sensitive 66/68, fixed 58/68, approximately 40% more phase-sensitive shots, selected recovery 10/12 verified and two inconclusive. Two QFT2 angle-fault failures and the absence of a universal-superiority conclusion are stated. The decorative sculpture is not presented as measurement data.

## Visual review and checks

`artifacts/landing-rebuild-first/` contains the first rebuilt composition. Those images were opened; a further correction darkened the metal base tones and reduced atmosphere opacity from .65 to .48. Final captures in `artifacts/landing-rebuild-final/` were opened and inspected at 1920×1080, 1440×900, 1366×768, 768×1024 and 390×844. The first viewport contains header, readable branding/headline/description/actions and a fully framed sculpture. There is no document-width overflow; button hit tests pass. The background-only capture temporarily hides sculpture/annotations; it confirms visible shader folds. Headless compositor capture with that temporary visibility override clips some unrelated text at the left; ordinary full-composition captures do not show that artifact.

Actual commands from the repository root:

```powershell
npm.cmd --prefix web run check
npm.cmd --prefix web run build
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 pytest tests -q -p no:cacheprovider
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.landing_recovery_e2e --out artifacts/landing-rebuild-final
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.cinematic_e2e --out artifacts/landing-rebuild-cinematic
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.browser_e2e --out artifacts/landing-rebuild-science
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.workspace_navigation_e2e --out artifacts/landing-rebuild-navigation.json
```

TypeScript and production build pass. Python: 99 passed in 18.98s, one existing Starlette/httpx deprecation warning. Seven actual Aer browser workflows pass: QFT4/GHZ4/Bell clean, missing-gate repair, readout noise, phase repair and 64-shot abstention. Both tested repairs independently verify. Export download, integrity recheck, binary ordering, saved/history restoration, frozen benchmark display and invalid-budget 422 pass. The expected invalid-request console message is distinguished from unexpected errors; unexpected page/console/request errors are empty.

Landing regression passes all five sizes, CTA hit testing, actual anchor scrolling without route changes and keyboard activation of the final CTA. Cinematic acceptance passes actual Hyperspeed/TechText frames, reframe, PixelSwap, focus restoration, renderer removal, direct routes/refresh/back/forward, reduced motion and forced absent-WebGL fallback. Short-state screenshots freeze genuine browser timers; no pixels or scientific outputs are fabricated. Full screenshots and metallic close-up, transition, mobile hero/workbench and real recovery captures are retained locally. They are not included as public clone assets.

## Sources and limits

Mental.ai's actual Start/NeuralStage/Wordmark/neural/sculpture/studioEnv/entry/tokens source was revisited at the revision documented in `frontend-sources.md`; no root reuse license was found. No Mental.ai source was copied. Vantage remains an editorial reference. Existing adapted React Bits source and its MIT + Commons Clause notices are retained. No dependency, font package, external script, backend endpoint or scientific artifact was added or changed. Existing project-owned frontend dependencies/lockfile were used; this recovery did not perform another fresh installation. Python and Playwright still use the disclosed local bridge.

The separate fresh-context Chromium run measured 4.234s to hero phase, with navigation load duration 103ms. This includes local headless graphics initialization and is not a hardware/FPS/Lighthouse benchmark. The 548.53kB shared Three chunk (136.09kB gzip) retains Vite's warning. Returning visitors, Skip/Escape, reduced motion and direct workbench navigation bypass the full intro. Broader hardware/browser profiling and the user's aesthetic approval remain manual checks.


## Final persistent inspection

After implementation commit ffbb074ac260def39947af3930ce5b32f72d9f0a, the previous owned QFAULT server was stopped and the verified integrated launcher started in persistent terminal session74655, server PID17868. Working directory C:\Projects\QFF; listening URL http://127.0.0.1:8000/. HTTP root200 and healthok confirmed. The final command `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.inspection_smoke --out artifacts/landing-rebuild-inspection` passed: WebGL landing, workbench, actual Aer experiment_71d1d869cfd442579c43eb08cb67f113 with independently VERIFIED recovery, no console/page/request errors. Final landing-desktop.png and workbench-desktop.png were opened and inspected. Saved-navigation regression also passed all recorded checks with no page errors. The inspection server remains running; logs are in the persistent terminal session. No disruptive tests followed the smoke.
