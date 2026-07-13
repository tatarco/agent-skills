---
name: app-carousel
description: Build a LinkedIn carousel out of receipts — drive a live app through a real flow, screenshot it, blur what would leak, and export designed slides as a PNG set plus a PDF document post. Use when the user wants a carousel, a LinkedIn document post, or a swipeable walkthrough of an app or URL.
---

# App → LinkedIn carousel

The slides are **receipts**: real screens of a real app, captured in a real session. That is the
entire advantage over an AI-image carousel, and every rule here protects it.

```
flow.json → capture.py → redact.py → slides.json + build.py → out/*.png + out/carousel.pdf
```

## 1. Capture

```bash
python3 scripts/capture.py flow.json -o shots/
```

**Gated app:** the user logs in themselves, in their own browser. You then lift the session and
replay it — `javascript_tool` → `JSON.stringify(Object.fromEntries(Object.keys(localStorage).map(k=>[k,localStorage.getItem(k)])))`
→ paste into `flow.json` under `"storage"`. Credentials stay with the user; you only ever hold a
session they already created.

Three things that silently give you the wrong screen:

- **Hash routes** do not remount on a hash change — `reload()` after `goto("#/route")`.
- **An iOS user-agent** can serve an "add to home screen" interstitial instead of the app. Use a
  phone-sized viewport with a **desktop UA**.
- **`get_by_text`** matches body copy that merely contains the phrase. Click controls:
  `button:has-text(...)` / `a:has-text(...)`.

**Done when:** every step in `flow.json` produced a shot, and you have **opened each one** and
confirmed it shows the real screen — not a login wall, an empty state, or an interstitial.

## 2. Redact

```bash
python3 scripts/redact.py shots/ -o clean/ --rules rules.json
```

A code, a name, or a figure legible in a published carousel is a **leak**. Redact past the brief:
live venue/discount codes, API keys, customer names, revenue and performance figures.

Blur by **content, not selector** — names, money and dates move around the DOM; their shape does
not. `flow.json` takes `blur_text` (regex, blurs matching leaves in-page before the shot) and
`blur` (CSS selectors). In-page blur is the mechanism; `redact.py`'s OCR pass is the net that
catches what it missed.

**Done when:** `redact.py` exits 0 — it re-OCRs its own output and fails loudly on a survivor.

## 3. Compose

Write `slides.json` (see `templates/slides.json`), then:

```bash
python3 scripts/build.py slides.json -o out/
```

6–12 slides. Slide 1 carries the whole post; the last slide makes one ask. Copy rules, slide
kinds, fonts and RTL: [REFERENCE.md](REFERENCE.md).

**Done when:** `out/01.png … NN.png` and `out/carousel.pdf` exist, and you have **looked at every
slide** — text inside the frame, nothing clipped at an edge, every claim true of the screenshot
beside it.

## 4. Prove

```bash
python3 scripts/redact.py out/ --rules rules.json --verify-only
```

Run this on the **exported slides**. The composer rescales images, and rescaling can make a blur
legible again — so a clean `clean/` proves nothing about `out/`.

**Done when:** every exported slide reports clean.
