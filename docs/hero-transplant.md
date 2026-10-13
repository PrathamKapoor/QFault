# MENTAL.AI hero transplant (D041)

## Source and rights
- `C:\Projects\DE` is a local checkout of the MENTAL.AI repository: `upstream` = https://github.com/shreshthgod/mental.ai, `origin` = https://github.com/PrathamKapoor/Vantage-The-Emotional-Signaler.git, branch `feat/on-device-intelligence-product-refinement`, HEAD 06a503b. It was used read-only; its working tree was verified clean before and after (the reference server ran with its Vite cache redirected outside the checkout and `/api` proxied to an unused port).
- There is no LICENSE file in the repository. Commit authorship: PrathamKapoor 24 commits, shreshthgod 11. Per-file history: `neural.ts` 375/552 lines by PrathamKapoor, 177 by shreshthgod; `studioEnv.ts` and `NeuralStage.tsx` entirely by shreshthgod; `Wordmark.tsx`, `Start.tsx`, `entry.css`, `tokens.css` mixed.
- Reuse basis: on 2026-10-13 the QFAULT owner (PrathamKapoor, co-author of MENTAL.AI) confirmed that shreshthgod granted permission to reuse their portions in QFAULT. That confirmation is the basis for verbatim reuse; this document does not independently verify it. Every transplanted file carries an attribution header; THIRD_PARTY_NOTICES.md records the grant.
- Grainient is a React Bits component and stays under the React Bits terms already recorded in docs/licenses/react-bits.md. Inter Variable 5.3.0 font files are vendored under SIL OFL 1.1 (`web/src/components/hero/fonts/OFL-1.1-Inter.txt`).

## What was transplanted (web/src/components/hero)
| QFAULT file | Source | Change |
|---|---|---|
| neural.ts | web/src/components/hero/neural.ts | none (byte-identical after the header) |
| studioEnv.ts | web/src/components/hero/studioEnv.ts | none |
| engine.ts | web/src/components/hero/engine.ts (2D fallback tier) | none |
| NeuralStage.tsx | web/src/components/entry/NeuralStage.tsx | import paths; `import React` for QFAULT's classic-JSX type check |
| motion.ts | web/src/lib/motion.ts | only `useReducedMotion` kept |
| Grainient/ | web/src/components/Grainient | header only |
| Wordmark.tsx | web/src/components/entry/Wordmark.tsx | glyphs QFAULT instead of MENTAL.AI |
| entry.css | web/src/styles/entry.css | none |
| hero-base.css | tokens.css, base.css `.label`, hero.css `.cta` | tokens scoped to `.entry` instead of `:root`; `.label`/`.cta` scoped under `.entry` |
| MentalHero.tsx | web/src/pages/Start.tsx | authentication, login/welcome panels, router and greeting removed; QFAULT copy; field labels reworded |
| hero.css | — | QFAULT adaptations (below) |

Geometry (six strands: three tubes, two ribbons, one emissive wire, the core, the seeded `rand`), materials, PMREM studio environment, lights, ACES tone mapping at exposure 1.08, camera framing, breathing shader, signal bead, parallax, emergence timing, letter poses and timings, layer order and Grainient parameters are the source values.

## QFAULT adaptations (all framing or branding)
1. Composition: QFAULT has no login panel, so the hero keeps the reference's own pre-handover framing (scene centred across the 70/30 grid). Enter Workbench triggers the reference handover (`entry--split`): the scene slides left and the right column shows QFAULT's workspace-access panel; the existing reframe -> PixelSwap -> workbench transition then runs unchanged.
2. Wordmark size: QFAULT has 6 glyphs vs 9. Font size scaled by the measured width ratio (x1.35) so the word spans the same share of the stage (1440: 859 px QFAULT vs 874 px MENTAL.AI on a 905 px stage). Consequence: taller letters (205 px vs 152 px).
3. Navigation: QFAULT links and actions kept; styling taken from the reference nav.css (.nav__wordmark/.nav__link/.nav__cta values).
4. Removed from the landing: Hyperspeed/TechText intro, MoltenMetal background and QFAULT's previous procedural sculpture (files deleted after confirming no other importers). The reference entrance (letters assemble, sculpture at 2 s; immediate on return visits and under reduced motion) replaces them.

## Visual comparison (artifacts/hero-transplant, local, git-ignored)
`reference/` (MENTAL.AI rendered from C:\Projects\DE), `qfault/` (final), `qfault-before/` (previous hero), `qfault-transition/`, `preserved/`; `measurements.json` in each capture folder. Same capture script (`scripts/hero_capture.py`), SwiftShader WebGL, viewports 1920/1440/1366/768/390/375/360.

| 1440x900 | reference (intro framing) | QFAULT |
|---|---|---|
| stage box | x253 w905 h797 | x253 w905 h797 |
| word box | w874 h152 | w859 h205 |
| copy box | x49 | x49 |

Remaining differences: wordmark letters are taller (fixed glyph count); headline copy is QFAULT's; the reference's resting state after its 4.25 s handover is the split layout with a login form, which QFAULT shows only during Enter Workbench; field labels reworded; QFAULT mark kept beside the nav wordmark; mobile nav shows QFAULT's Enter Workbench button instead of the reference MENU toggle. A full-page Playwright capture can freeze the 1200 ms scene transform mid-flight (artifact of the capture resize; normal reloads measure the centred position).

## Lifecycle
Unchanged from the source engine: single rAF loop, paused when the tab is hidden or the canvas is off screen (IntersectionObserver), single static frame under reduced motion, ResizeObserver re-framing, DPR capped at 1.75 (1.25 below 768 px, quality 0.55), full disposal of geometries, materials, PMREM texture and renderer on unmount (verified: no hero canvas remains in the workbench). WebGL failure falls back to the 2D signal-structure engine (`data-engine="fallback-2d"`); the CTA stays available.
