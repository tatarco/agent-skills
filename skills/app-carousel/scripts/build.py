#!/usr/bin/env python3
"""Compose slides.json into LinkedIn-ready slides: PNG set + stitched PDF.

Slides are plain HTML screenshotted by Playwright at 1080x1350 — deterministic, no video
renderer in the loop. Fonts are loaded from the network at build time; if you need an exact
face (e.g. Hebrew), point --font-css at a local CSS file so the render never falls back
silently to a font that lacks your script.
"""
import argparse
import base64
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

W, H = 1080, 1350            # LinkedIn's best-performing portrait ratio (4:5)


def data_uri(p):
    p = pathlib.Path(p)
    return f"data:image/{p.suffix.lstrip('.') or 'png'};base64," + \
        base64.b64encode(p.read_bytes()).decode()


def slide_html(s, theme_css, font_css, idx, total):
    kind = s.get("kind", "shot")
    title = s.get("title", "")
    body = s.get("body", "")
    kicker = s.get("kicker", "")
    img = s.get("image")
    notes = s.get("annotations", [])

    pins = "".join(
        f'<div class="pin" style="top:{a["top"]}; {"right" if a.get("side","right")=="right" else "left"}:{a.get("offset","3%")}">'
        f'{a["text"]}</div>'
        for a in notes
    )
    shot = f'<div class="shot"><img src="{data_uri(img)}" />{pins}</div>' if img else ""

    return f"""<!doctype html>
<html dir="{s.get('dir','ltr')}" lang="{s.get('lang','en')}">
<head><meta charset="utf-8"/>
{font_css}
<style>{theme_css}</style>
</head>
<body class="k-{kind}">
  <main>
    {f'<div class="kicker">{kicker}</div>' if kicker else ''}
    {f'<h1>{title}</h1>' if title else ''}
    {f'<p class="body">{body}</p>' if body else ''}
    {shot}
  </main>
  <footer>
    <span class="brand">{s.get('brand','')}</span>
    <span class="pg">{idx}/{total}</span>
  </footer>
</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slides", help="slides.json")
    ap.add_argument("-o", "--out", default="out")
    ap.add_argument("--theme", help="theme.css (defaults to the skill's)")
    ap.add_argument("--font-css", default="", help="path to a local @font-face css (recommended)")
    args = ap.parse_args()

    here = pathlib.Path(__file__).resolve().parent.parent
    spec = json.loads(pathlib.Path(args.slides).read_text())
    slides = spec["slides"]
    theme = pathlib.Path(args.theme or here / "templates" / "theme.css").read_text()
    if spec.get("theme_vars"):
        theme += "\n:root{" + "".join(f"{k}:{v};" for k, v in spec["theme_vars"].items()) + "}"

    font_css = ""
    if args.font_css:
        font_css = f"<style>{pathlib.Path(args.font_css).read_text()}</style>"
    elif spec.get("font_href"):
        font_css = f'<link rel="stylesheet" href="{spec["font_href"]}">'

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    pngs = []

    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_context(viewport={"width": W, "height": H},
                             device_scale_factor=2).new_page()
        for i, s in enumerate(slides, 1):
            page.set_content(slide_html(s, theme, font_css, i, len(slides)),
                             wait_until="networkidle")
            page.wait_for_timeout(500)
            f = out / f"{i:02d}.png"
            page.screenshot(path=str(f))
            pngs.append(f)
            print(f"  slide {i}/{len(slides)}  {s.get('kind','shot'):6s} {f.name}")
        b.close()

    # stitch to a single PDF — this is the "document post", which reaches further than
    # a plain multi-image gallery
    from PIL import Image
    ims = [Image.open(f).convert("RGB") for f in pngs]
    pdf = out / "carousel.pdf"
    ims[0].save(pdf, save_all=True, append_images=ims[1:], resolution=144)

    print(f"\n-> {len(pngs)} PNGs + {pdf}")
    print("   LinkedIn document post: upload carousel.pdf")
    print("   Multi-image post:       upload the PNGs in order")
    return 0


if __name__ == "__main__":
    sys.exit(main())
