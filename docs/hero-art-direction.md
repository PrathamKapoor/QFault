> **Historical record** (2026-10-12). Superseded by D033 and D041 ([hero transplant](hero-transplant.md)). Current status: see the repository [README](../README.md) and [release history](release-history.md).

# Hero art direction correction

The starting state is clean main at `463c1970922c7f2ba620cd431b7a3023a2782914`. The user rejected that hero. This document records the correction; it does not claim user approval. Only the hero, sculpture, fallback and its visual checks change. The workbench, transition engine, backend and scientific artifacts remain outside this change.

## Reference comparison and reproduced causes

The actual local source and fresh browser baseline were inspected before editing. Baseline captures: ignored `artifacts/hero-art-baseline/`. No screenshot attachment is present in this turn's accessible message content; the actual running baseline provides the visual evidence.

The Mental.ai checkout was revisited at revision `95570b0ab33457b268ea30595fbb3158c3d310cd`: sculpture.ts, studioEnv.ts, NeuralStage.tsx, Wordmark.tsx, entry.css and tokens.css, plus neural.ts because NeuralStage actually calls that entry engine. The generic hero sculpture contains rings, but its entry engine uses distinct open strands. These are different implementations; copying the generic ring composition would miss the requested entry reference. No root reuse license was found. The new QFAULT paths, sweep mesh, material textures and composition are original; no reference repository was modified.

| Dimension | Rejected QFAULT hero | Reference technique and correction |
|---|---|---|
| Geometry | Five open paths nevertheless outline the same closed-looking oval | Distinct paths rather than primitive count; replace with two broad diagonal ribbons and two secondary paths |
| Trajectories | Similar top/bottom endpoints, left/right arcs | Separate longitudinal sweeps that fold through depth and extend diagonally |
| Width | Nearly constant broad/narrow profiles | Modulate width along each sweep, retain rounded profile thickness and tapered ends |
| Crossings | Oval envelope with central crossing | Deliberate alternating depth, open ends and negative space along an elongated silhouette |
| Surface shading | Inward triangle winding; profile seam; weak high-frequency roughness | Outward triangle winding, continuous seam normals, UV-aligned brushing, restrained bump and anisotropy |
| Reflections | Broad front-facing cards yield large silver patches | Narrow neutral strips plus dim broad fill preserve graphite surfaces and silver curvature gradients |
| Lighting | Silver body with purple edges | Neutral shaping light, dimmer violet rim and subtle blue studio reflection |
| Framing | Separate right-hand 46%-width stage | Shared typography/art stage with bounds-fitted diagonal geometry; lower copy/actions remain unobstructed |
| Text depth | No intersecting text planes | Identical per-letter back/front planes, selected foreground letters and one semantic QFAULT heading |
| Hierarchy | Independent wordmark and illustration, tiny art captions | One integrated brand/sculpture composition above requested copy/actions; remove decorative jargon |

MoltenMetal was rendering. Its scale3.3, fold default-.2, brighter palette and .48 opacity produced oversized smooth streaks. The revised settings increase spatial detail and change folding, with a darker palette, lower intensity and restrained grain. The actual React Bits shader and source notices remain. No new dependency is required. See frontend-sources.md and licenses/react-bits.md for retained rights.

## Review iterations

The strengthened landing regression first failed on the missing shared back/front text planes (`artifacts/hero-art-red`). Existing checks were retained; selectors were updated to identify the single back plane among decorative duplicates.

The first rebuilt captures (`artifacts/hero-art-first`) were opened. The diagonal silhouette and shared wordmark were present, but dark ribbon surfaces, coarse brushing and text-plane metric differences were rejected during review. Corrections increased neutral fill, reduced bump/anisotropy, aligned both planes with identical letter spans and protected the terminal T in the foreground. Background settings were retuned from faint speck-like folds. Final evidence and commands are recorded after verification below.


## Final verification

The final texture pass enables linear filtering, mipmaps and bounded anisotropic texture filtering so micro-roughness remains stable at distance. The complete final capture set is ignored/local `artifacts/hero-art-delivery/`: hero-1920.png, hero-1440.png, hero-1366.png, hero-768.png, hero-390.png, sculpture-closeup.png, background-only.png, full-landing.png, entry-transition.png and workbench.png. These were opened and inspected (including the additional768×1024 view). The sculpture is diagonally elongated, intersects selected wordmark letters, stays framed and leaves actions readable. Background-only capture hides foreground through temporary browser CSS; it confirms actual shader detail without synthesized pixels. Close-up capture hides wordmark/interface overlays to inspect the actual metal. This is internal engineering review, not user approval.

`artifacts/hero-art-motion/` contains genuine Hyperspeed/TechText/hero/reframe/PixelSwap, all responsive captures, forced no-WebGL fallback and reduced-hero.png. Both actual static WebGL canvases are awaited before the reduced-motion capture. Intro/PixelSwap mechanics remain unchanged; only framing at their hero boundary adapts. The first full capture attempt had a timing-sensitive entry/overview readiness failure; the regression now freezes the genuine short reframe with Playwright's clock and awaits actual API readiness for up to30s, retaining all assertions. Final runs pass.

Executed from C:\Projects\QFF against the integrated local server:

```powershell
npm.cmd --prefix web run check
npm.cmd --prefix web run build
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 pytest tests -q -p no:cacheprovider
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.landing_recovery_e2e --out artifacts/hero-art-delivery
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.cinematic_e2e --out artifacts/hero-art-motion
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.browser_e2e --out artifacts/hero-art-science
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.workspace_navigation_e2e --out artifacts/hero-art-navigation.json
```

TypeScript and production build pass. Python99 passed in13.75s, one existing Starlette/httpx deprecation warning. Landing checks pass all five requested sizes, shared depth planes, removed decorative captions, CTA hit testing, keyboard footer entry and scroll links without hash changes. Cinematic checks pass intro rendering, transition, focus, renderer removal, direct workbench/refresh/back/forward, reduced motion and forced absence of WebGL. Navigation regressions pass draft preservation, real-response race handling, missing records, API failures and mobile Escape focus.

Seven actual Aer browser cases pass: QFT4/GHZ4/Bell clean, missing-gate repair, readout noise, phase repair, and64-shot abstention. The two tested repairs verify independently. Export download, integrity recheck, history/settings restoration, binary ordering and frozen benchmark display pass. Invalid budget returns the expected422, distinguished from unexpected console errors. Unexpected console/page/request errors are empty. No scientific successes are mocked.

Fresh headless Chromium observation:4.833s to hero phase, navigation duration162.4ms. This is a local observation including graphics initialization, not an FPS/GPU/Lighthouse score. Shared Three548.54kB (136.10kB gzip) retains Vite's size warning. Device DPR/visibility/reduced-motion/disposal guards remain. Wider hardware/browser profiling and the user's aesthetic approval remain unresolved manual checks. Existing project-owned npm dependencies were used without another fresh installation; Python/Playwright retain the disclosed bridge. No new dependency or backend change.


## Persistent manual inspection

Implementation commit: ba48f0ffa3e8f489a7b6776b58d2862fa699e73b. After committing, the previous owned QFAULT server17868 was stopped and the verified launcher started in persistent terminal session3313, server PID44940. Command from C:\Projects\QFF: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault serve`. URL http://127.0.0.1:8000/; root HTTP200 and healthok verified. Final `scripts/local_browser.ps1 scripts.inspection_smoke --out artifacts/hero-art-inspection` passes actual WebGL hero, entered/focused workbench and real Aer independently VERIFIED recovery experiment_fccf2aa434194cbeaf306a9d1bda8551. Console/page/request errors are empty. Final landing-desktop.png/workbench-desktop.png were opened. Server remains alive for manual inspection; logs are in the persistent terminal session. No disruptive tests followed this smoke.
