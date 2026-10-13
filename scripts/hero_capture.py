"""Capture matched hero screenshots and layout measurements for visual comparison.

Usage: python scripts/hero_capture.py --url URL --out DIR --word SEL --stage SEL [--copy SEL] [--settle-ms N]
Records, per viewport: full screenshot, sculpture close-up, bounding boxes of the wordmark, WebGL stage,
copy block and primary CTA, horizontal overflow and the WebGL tier reported by the canvas.
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

VIEWPORTS = [(1920, 1080), (1440, 900), (1366, 768), (768, 1024), (390, 844), (375, 812), (360, 800)]


def box(page, sel):
    if not sel:
        return None
    return page.evaluate("""(s) => { const e = document.querySelector(s); if (!e) return null;
        const r = e.getBoundingClientRect(); return {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height)}; }""", sel)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--word", required=True); ap.add_argument("--stage", required=True)
    ap.add_argument("--copy"); ap.add_argument("--cta")
    ap.add_argument("--settle-ms", type=int, default=6500)
    ap.add_argument("--early-ms", type=int, default=0, help="also capture an early intro frame at this time")
    ap.add_argument("--clear-session", action="store_true")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        for w, h in VIEWPORTS:
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1,
                                      is_mobile=w < 768, has_touch=w < 768)
            page = ctx.new_page(); errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(a.url, wait_until="domcontentloaded")
            if a.early_ms:
                page.wait_for_timeout(a.early_ms)
                page.screenshot(path=str(out / f"{w}x{h}-early.png"))
                page.wait_for_timeout(max(0, a.settle_ms - a.early_ms))
            else:
                page.wait_for_timeout(a.settle_ms)
            page.screenshot(path=str(out / f"{w}x{h}.png"))
            stage = box(page, a.stage)
            if stage and stage["w"] > 0 and stage["h"] > 0 and w >= 1366:
                clip = {"x": max(0, stage["x"]), "y": max(0, stage["y"]),
                        "width": min(stage["w"], w - max(0, stage["x"])), "height": min(stage["h"], h - max(0, stage["y"]))}
                page.screenshot(path=str(out / f"{w}x{h}-sculpture.png"), clip=clip)
            rows.append({"viewport": [w, h], "word": box(page, a.word), "stage": stage, "copy": box(page, a.copy),
                         "cta": box(page, a.cta),
                         "engine": page.evaluate("() => document.querySelector('canvas[data-engine]')?.dataset.engine ?? null"),
                         "overflow_x": page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth"),
                         "errors": errors})
            ctx.close()
        browser.close()
    (out / "measurements.json").write_text(json.dumps(rows, indent=1))
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
