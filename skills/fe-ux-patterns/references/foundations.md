# Foundations — the values everything is built from

## Spacing is the most expensive pixel on the screen

A card reads as cheap almost always because of spacing, not colour or font. Four fixes, in order:

1. **Padding** — 8px → 28px. Content pulling away from the edge is what "intentional" looks like.
2. **Element spacing** — 4px → 18px. Avatar, text, image, actions each need their own space.
3. **Line height** — 1.1 suffocates; **1.5–1.6** for body. This alone makes text look designed.
4. **Breathing room** — spread the icon row last; it is the final polish.

**Three kinds of whitespace:** *micro* (padding inside a button), *macro* (margins between
sections), *active* (a deliberately oversized gap that points at what matters). Doubling a
cramped card (16→32 padding, 8→16 gaps) with identical content is the whole difference between
cheap and premium.

## Proximity does the grouping, not dividers

Close things read as related before a single word is read. An evenly-spaced toolbar gives the
eye nowhere to land; group it by function (navigation / actions / settings) and it becomes
scannable with **zero dividers**. Same for forms: name+email tight together = personal info;
card number with a bigger gap above = a separate section. Same for a sidebar: a flat equidistant
list versus the same links grouped by category is a completely different level of clarity.

## Type scale

Never random sizes. A **modular scale** with a fixed ratio: display / heading / body / caption.
One family, four sizes, each with its own size, weight **and** line height. Hierarchy you can
feel. (A golden-ratio scale — 16 / 26 / 42 / 68 at ×1.618 — is one defensible choice; so is a
1.25 or 1.333 scale. The ratio matters less than having one.)

## Spacing scale

One base unit, stacked. 8px is the common choice (8 / 16 / 24 / 40); 4px gives finer control.
Every margin, padding and gap is a multiple. Random spacing feels off for reasons users cannot
name; a grid feels intentional for the same reason.

## Design system, in build order

Tokens → **molecule** (a button) → **organism** (a card) → screen.

**A semantic colour system, not raw hex.** Name by purpose — `background`, `surface`, `brand`,
`success`, `error` — then a 9-step scale from dark to light per hue. One source of truth.

**Palette construction:** one hue varied by lightness (monochromatic), two opposites
(complementary), or three neighbours (analogous). Three techniques, infinite palettes.

**Rule zero when adopting a system into an existing project:** read what the project already
encodes — Tailwind config, CSS custom properties, token files, then the most-reused component —
*before* inventing anything. The decisions usually already exist. Extract them, each with a
one-line reason it exists. Only the gaps deserve a question. Afterwards, a value outside the
system is either an approved extension (written down, with its reason) or it is replaced by the
nearest token.

**One explicit decision per axis, or the design defaults to nothing:**
- *Type* — where the contrast lives.
- *Colour* — one signature, calibrated neutrals.
- *Space* — compression, then release.
- *Finish* — borders, **or** shadows, **or** flat planes. Not all three.

## Border radius is a system

- **Concentric corners.** Inner = outer − padding. 12 outside, 8 padding, 4 inside. Same radius
  inside and out makes the inner corner bulge.
- **Radius follows size.** small 4 / medium 8 / large 16. One scale, every element on it. A chip
  and a modal do not share a corner.
- **Full radius is a shape, not a number.** A pill fits one line — chips, avatars, toggles. On a
  multi-line card it swallows content; give that a real number.
- **A corner implies space beyond it.** A sheet docked to the bottom rounds the top corners and
  zeroes the bottom. Anything touching an edge gets no corner there.
- **Rings invert the formula.** A selection ring 2px outside: outer = inner + gap. 8 in, 10 out.
- **Images:** an edge-to-edge image gets clipped by the card; an inset image subtracts the padding.

## Dark mode

Pure black is a terminal, not dark mode.

- **Start near-black.** Nothing sits lower than `#000`, so every surface fights for one plane.
- **Lightness is the elevation cue.** Shadows are invisible on dark; the higher the surface, the
  lighter it gets. Build a 4–6 step ramp.
- **Never pure white text.** 87% primary / 60% secondary / 38% disabled. Three tiers, one variable.
- **Desaturate the brand colour.** Saturated hues glow past their edges on dark and outshine
  content. Same hue, lighter, less chroma.
- **Hairlines use alpha, not grey.** 1px white at 8% adapts as the surface lightens.
- **Dim photos to ~90% brightness.** Illustrations get a dark variant, not a filter.

## Colour is communication

- **Simultaneous contrast** — the same grey reads dark on light and light on dark. Always judge a
  colour against its real composited background.
- **The pop-out effect** — when everything competes, nothing stands out. Grey everything except
  one element and the eye goes straight there. Ration the accent.
- **Temperature carries meaning** — red = danger/urgency, blue = safe/trustworthy, green =
  go/confirm. The identical button triggers a different decision by hue alone.
- **Prefer OKLCH over hex** when generating: lightness / chroma / hue, so changing one number
  gives a predictable shade, and ten tints and shades fall out of one decision.
- Check contrast **at pick time** with a live ratio badge, not in review.

## Numbers

- **Tabular figures, always**, anywhere numbers stack. Proportional digits give `1` a different
  width from `0` and the column wobbles.
- **Right-align numbers, left-align text.** The eye compares magnitude by the last digit.
- **Abbreviate large values** (1k, 1M) with full precision on hover.
- **Relative for recent, absolute for old.** "2 hours ago" beats a timestamp; last year does not.
- **Keep the currency symbol out of the number column** — align the decimals, not the dollar signs.

## Optical corrections (mathematically wrong, visually essential)

- A play triangle centred to its bounding box looks off; shift it right to the **visual centroid**.
- A circle needs to be **~13% larger** than a square to read as the same size — the eye reads area.
- Nested same-radius corners pinch: inner = outer − gap.
- **Irradiation illusion** — white text on dark looks heavier; drop one font weight in dark mode.
- CSS centres the full line box including space below the baseline; a button label often needs a
  **2px nudge up** to be optically centred.

## Survive real data

A card that looks fine in Figma breaks on the first real user:

- A flex child **will not shrink below its own text**, so a long name shoves the button off the
  card and the ellipsis never fires. `min-width: 0` on the flex child.
- Proportional digits nudge the layout on every update — `font-variant-numeric: tabular-nums`.
- Browsers never break inside a word, so **one long URL stretches the container** until the
  layout gives up. `overflow-wrap: anywhere`.
- Test with: a 40-character name, a URL with no spaces, 247 rows, 0 rows, exactly 1 row.
