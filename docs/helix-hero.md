> **Historical record** (2026-10-12). The double-spiral hero was replaced in D041 ([hero transplant](hero-transplant.md)). Current status: see the repository [README](../README.md) and [release history](release-history.md).

# QFAULT double-spiral hero correction

The user rejected the diagonal ribbon composition at e9827eab18cbcca7a28f3de3283a079099d4b7fe and explicitly requested a DNA-like centerpiece. This supersedes the earlier preference for non-helical open paths. The workbench, PixelSwap implementation and timing, backend contracts, scientific artifacts and lower-page sections are preserved.

## Confirmed baseline

The actual pre-edit browser capture is artifacts/helix-baseline/hero-1440.png. Four diagonal trajectories span about 5.3 units horizontally but only 3.3 vertically. Their shallow stage and foreground A/L/T letters leave a short, partly hidden object above the copy. This explains the separate-object appearance despite shared depth planes. The headline and description/actions also occupy separate columns. The material already has procedural studio reflections, roughness variation and anisotropy; geometry and staging are the primary failures in this revision.

## Original implementation

quantumSculpture.spiral generates a 6.1-unit ascending double spiral with 1.48 turns, opposite phases, a gently varying radius and asymmetric center drift. Two variable-width flattened ribbons establish the silhouette; two thin companion sweeps and a violet filament follow the same rise. No rings, rungs, central core or closed cage is introduced. Existing outward winding, seamless profile normals and tapered edges remain.

The neutral reflection fill is lifted to expose dark faces. Fine longitudinal roughness variation is reduced and the micro-bump amplitude lowered, avoiding coarse surface banding. High metalness, anisotropy, dark graphite tones and restrained violet/blue reflections remain. The sculpture has a fixed diagonal lean with only very slow drift/parallax; reduced-motion users receive the complete still composition.

The canvas occupies a tall central stage crossing the U/L region. A and T are retained in the foreground text plane; other letters sit behind the metal. Identical glyph metrics and the single accessible QFAULT heading remain. The requested headline, description and both actions form one lower-left group. Mobile uses a compact tall spiral above the same copy. The original SVG fallback now follows the double-spiral silhouette.

MoltenMetal's existing restrained graphite/violet shader and lifecycle remain unchanged. Its isolated background capture is included in the review evidence. The existing hyperspeed/name introduction, CTA locking, leftward handoff, PixelSwap, focus restoration and destination mounting are preserved.

## Reference and rights

Mental.ai sculpture.ts, studioEnv.ts, NeuralStage.tsx, Wordmark.tsx, entry.css and tokens.css were inspected from the local reference checkout at 95570b0ab33457b268ea30595fbb3158c3d310cd. NeuralStage actually uses neural.ts; the separate sculpture.ts supplies a useful double-sweep reference. The staging principle is shared typography/canvas depth with selective foreground glyphs; strip reflections reveal curvature against a black environment. No root license authorizing source reuse was found. QFAULT's paths, sweep implementation, studio and fallback remain original; no donor source is copied. Existing React Bits notices remain. No packages were added.

## Review process

The baseline and first reconstructed hero were opened. The first helix was still too far right and substantially concealed by L/T. The second correction moves the stage left, opens the radius, removes L from the foreground plane and lifts the neutral fill. Actual final checks and running-process details are recorded in handoff.md. Screenshots are visual evidence for manual review, not a claim of user approval.

The project-owned frontend dependencies are used. Python/Playwright execution uses the disclosed read-only local dependency bridge. Production Three.js still emits the existing bundle-size warning. Headless rendering does not establish real-device FPS, GPU timing or cross-browser performance.

## Executed checks

- `npm.cmd --prefix web run check`: passed.
- `npm.cmd --prefix web run build`: passed; existing shared Three.js chunk warning (548.54 kB, 136.10 kB gzip).
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 pytest -q`: 99 passed in 111.73 seconds. Existing Starlette/httpx deprecation and an unwritable pytest cache warning; no test failures. An initial invocation incorrectly passed `-m` to the module launcher and failed with `No module named -m`; the corrected command above ran the suite.
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.landing_recovery_e2e --out artifacts/helix-review`: passed at 1920×1080, 1440×900, 1366×768, 768×1024 and 390×844. CTA hit tests, actual keyboard transition and loaded overview passed. Page/console error arrays are empty. Screenshots of every size, full landing, isolated metal/background, reframe and workbench were opened.
- Two cinematic runs (`artifacts/helix-motion`, `artifacts/helix-motion-retry`) reached the workbench, then timed out waiting the default five seconds for actual overview data. The overview flag waits for four real API responses. The API-readiness waits in cinematic_e2e and inspection_smoke now use the same explicit 30-second budget as the landing suite; rendering and transition assertions remain intact.
- The first seven-workflow browser run (`artifacts/helix-science`) received real QFT4 results but timed out waiting five seconds for the Run button to re-enable after history/verification requests. That network-completion assertion now uses 30 seconds too. No scientific assertions or workflows were removed. These timing failures are retained as evidence; final runs are recorded separately.

No backend or benchmark files changed. Final browser outcomes and inspection-server details follow in handoff.md.

The next cinematic run reached and loaded the workbench, verified back/forward/refresh and captured the 1920 hero, then hit the same five-second default on a fresh lazy workbench mount. That asynchronous route assertion also receives an explicit 30-second budget. The screenshot assertions, exact route/focus checks and required real API data remain; this is not a five-second performance guarantee. The failures make the host sensitivity a known limitation rather than an invented smooth-performance claim.

The final scientific command was `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.browser_e2e --out artifacts/helix-science-final`. All seven real Aer workflows passed: clean QFT4/GHZ4/Bell, removed-gate Bell with VERIFIED recovery, readout noise, phase fault with VERIFIED recovery, and 64-shot abstention. Report download/hash verification, refresh/history, sorted bitstrings, frozen benchmark display and mobile geometry passed. No unexpected page, console, HTTP or failed-request errors; the invalid-budget test intentionally produces one HTTP 422 and its browser console message.

Final cinematic command: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local_browser.ps1 scripts.cinematic_e2e --out artifacts/helix-motion-verified`. Passed: Hyperspeed, TechText, rendered sculpture, reframe, PixelSwap, focus restoration, renderer removal, actual loaded workbench, direct routing/back/forward/refresh, five responsive sizes, reduced-motion WebGL still and forced absent-WebGL SVG fallback with working CTA. Page-error array is empty. Reduced-motion and fallback captures were opened. Separate fresh-context observation: hero phase reached in 4.546 seconds; HTML navigation duration 69.6 ms. This is a headless local observation, not a graphics-readiness, FPS or real-device performance guarantee.

Final frontend check/build were repeated successfully after browser verification. `git diff --check` passed. Screenshots for manual review: artifacts/helix-review/hero-1920.png, hero-1440.png, hero-1366.png, hero-390.png, sculpture-closeup.png, background-only.png, full-landing.png, entry-transition.png and workbench.png. Final inspection-server captures are recorded in handoff.md after restart.
