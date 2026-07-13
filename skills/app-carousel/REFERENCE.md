# app-carousel — reference

## Slide kinds

| kind | use | notes |
|---|---|---|
| `cover` | slide 1 | Big type, centred. Lands with zero context. |
| `shot` | the workhorse | A receipt + optional annotation pills. |
| `quote` | a breather | One line, centred. The sentence you want repeated. |
| `cta` | last slide | One ask. |

## slides.json

```jsonc
{
  "kind": "shot",
  "kicker": "THE BUILD",          // small eyebrow
  "title": "What we shipped",
  "body": "Supporting line. <b>bold</b> allowed.",
  "image": "clean/03-detail.png", // a REDACTED shot
  "dir": "rtl", "lang": "he",     // per-slide
  "annotations": [
    { "text": "65 pts", "top": "40%", "side": "right", "offset": "5%" }
  ],
  "brand": "YOUR BRAND"
}
```

Top-level: `font_href` (Google Fonts URL) or `--font-css` (local `@font-face`), and `theme_vars`
to override `templates/theme.css`. Pull the palette from the target app's own code — slides and
product then read as one thing, which is what makes the receipts land.

## Copy

- **Slide 1 is the post.** Open on a problem or a number.
- One idea per slide. Two sentences to explain it means two slides.
- Numbers over adjectives: "65 points for showing up" beats "great rewards".
- The last slide asks for one thing.
- Narrate the tool only when the tool *is* the story.

## Fonts

The renderer is a clean headless Chrome: a font you name but do not ship **falls back silently**
and the slide renders in the wrong face without erroring. Ship it — `font_href`, or `--font-css`
with local woff2 (the only reliable route offline, and for non-Latin scripts).

Confirm the family covers the script. Many popular UI faces carry no Hebrew or Arabic glyphs at
all: Rubik and Heebo do, IBM Plex Mono does not.

## RTL

Set `"dir": "rtl"` per slide, then:

- Hebrew has no uppercase — drop `text-transform` from the kicker.
- Latin brand tokens inside an RTL run reverse. Wrap them: `<span dir="ltr">ACME</span>`.
- `"side": "left"` is the outer edge for annotation pills.

## rules.json

```json
{ "patterns": ["\\b\\d{6}\\b", "(\\+|00)\\d{10,13}", "(Acme|Contoso) Ltd"] }
```

Extends the defaults in `redact.py` (phones, emails, 6-digit codes, percentages, card numbers).
Add the specific names, codes and figures the target app renders.

## Output

- `out/01.png … NN.png` — 1080×1350 @2x
- `out/carousel.pdf` — the document post, which reaches further than a multi-image gallery

LinkedIn allows 300 pages; people stop swiping around 12.
