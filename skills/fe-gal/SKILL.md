---
name: fe-gal
description: "Take a frontend from ugly to genuinely good, and prove it. A verification-first redesign loop: read the brief, commit to one concept, kill the AI tells, then measure the result in a real browser instead of trusting a screenshot. Use when the user says a page looks bad, generic, dated, 'like AI made it', or asks for a redesign, polish pass, or mobile fix."
trigger: /fe-gal
---

# /fe-gal

The process that took a real client site from "it looks like shit, really" to shipped. It is
not a style. It is an order of operations, plus a set of measurements that stop you
believing your own work.

## Usage
```
/fe-gal                     # full pass on the current project
/fe-gal <path or url>       # scope to one page or surface
/fe-gal mobile              # only the small-screen pass  (+ fe-redesign-mobile)
/fe-gal verify              # only the measurement pass, no design changes
/fe-gal components          # only the component-behaviour pass  (+ ux-patterns)
```

---

## 0. THE RULE THAT MATTERS MOST

**Never report a visual result you have not measured in a real browser.**

Most of the wasted effort in a redesign is spent fixing things that were never broken and
shipping things that were. Everything in section 5 exists because each one of those checks
caught a real bug that a screenshot had hidden or invented.

If you only take one thing from this skill, take that.

---

## 1. READ THE ROOM BEFORE TOUCHING CSS

State the design read in one line before writing anything:

> "Reading this as: `<page kind>` for `<audience>`, in a `<vibe>` language, leaning toward `<direction>`."

Then commit to **one** concept and name it. Not "modern and clean" — an actual idea you can
argue for. A concept you can defend produces decisions; a mood board produces mush.

**The concept must come from the subject, not from the category.** If you could guess the
palette from the industry alone, it is the first reflex and it is wrong. If you could guess
it from industry-plus-anti-reference ("athlete site but not dark-and-gold"), that is the
second reflex and it is also wrong. Keep going until neither is guessable.

**Ask what the accent *means*.** An accent that carries information beats one that decorates.
Rationing it is what makes it read as deliberate: if a colour marks gold medals, then an
award and a ranking do not get to borrow it.

---

## 2. THE FIVE THINGS THAT MAKE A PAGE LOOK AI-MADE

Check these first. They account for most of the "this looks generic" reaction.

1. **Flat saturated fills.** A single mid-tone colour across a whole section removes every
   depth cue at once and reads as 2000s wallpaper. Replace with a near-black or near-white
   ground plus a **4–6 step elevation ramp** (3–5 points of lightness apart, each carrying a
   faint hue). On dark surfaces lightness *is* the depth cue; shadows barely register.
2. **A serif display face reached for because the brief felt "premium".** This is the single
   most-tested tell. Default to a heavy sans unless the brand actually names a serif.
3. **Em-dashes in body copy.** Ban them outright. Rewrite the sentence.
4. **The eyebrow on every section.** Tiny uppercase tracked label above each heading. One as
   a deliberate system is voice; on every section it is scaffolding.
5. **Everything the same size.** Nineteen items of equal weight is padding dressed as design.
   Curate: a few get weight, the rest get a line.

Also worth killing on sight: accent side-stripe borders, gradient text, decorative
glassmorphism, `border: 1px` paired with a wide soft `box-shadow`, and card radii above 16px.

---

## 3. BREAK THE RECTANGLE

"Boring" and "too square" usually mean *every block is the same rectangle in the same grid*.
A blanket `border-radius` does not fix it; it just rounds the monotony.

What does: **overlap**. Let a photo bleed off one edge, let a headline cross into an image,
give one section an asymmetric split. One deliberate grid-break beats ten rounded corners.

Two traps, both of which cost real time:
- `inline-size: 100%` on a grid item with a **negative** inline margin resolves against the
  column, so the box drags inward and opens a gap at the far edge. Use `auto` + stretch.
- A grid container's implicit column is `auto`, so it sizes to its **widest child's
  max-content**. One non-wrapping row can drag an entire section wider than the viewport.
  `grid-template-columns: minmax(0, 1fr)` forbids it.

---

## 4. MOTION WITH A REASON

Motion should reveal something, not decorate. Ease-out for entrances, 150–250ms for UI,
`scale(0.97)` for a press, asymmetric timing (fast in, slower out).

- Prefer native `animation-timeline: view()` / `scroll()` over scroll listeners.
- **A reveal must enhance content that is already visible.** Never gate visibility on a
  class-triggered transition: transitions do not advance in hidden tabs or headless
  renderers, and the section ships blank. Always leave a failsafe.
- Feedback must be immediate. If a click waits on the network, change something on the click
  itself, or the control reads as dead.
- Every animation needs a `prefers-reduced-motion` alternative, and "none" is not it.

---

## 5. THE VERIFICATION PASS (do not skip, do not fake)

Serve the site (`python3 -m http.server 8899`) and check each of these. Every one is here
because it caught something real.

**Horizontal overflow — the measurement, not the screenshot.**
`body { overflow-x: hidden }` *hides* overflow, so `scrollWidth` reports clean while content
is silently clipped. Walk the DOM instead:

```js
document.querySelectorAll('body *').forEach(el => {
  const r = el.getBoundingClientRect();
  if (r.width > 0 && r.right > document.documentElement.clientWidth + 1) console.log(el);
});
```

**Use a same-origin iframe at an exact width.** Chrome headless clamps `--window-size` to a
500px minimum and then crops the PNG, which *fabricates* overflow that is not there. Put a
probe page inside the served directory and embed the real page in an `<iframe>` of exactly
360 / 390 / 414 / 768px. A `file://` parent is cross-origin, `contentDocument` is null, and
the probe fails silently — serve the probe from the same origin.

**Neutralise animation before screenshotting.** Headless does not advance CSS transitions
under `--virtual-time-budget`, so revealed sections photograph blank. Inject a stylesheet
into the iframe zeroing durations and adding the revealed class, or pass
`--force-prefers-reduced-motion`.

**Check the interaction actually fires.** Read `getComputedStyle` before and after a real
hover rather than trusting that the selector is right. And when it does not fire, suspect a
**stale stylesheet** before suspecting the CSS.

**Contrast, computed.** Every accent-on-dark and muted-on-tinted pair, against the real
composited background. Body text 4.5:1. White text on a light accent button is the classic
miss.

**Tap targets ≥44px**, added via an invisible `::before` overlay rather than by growing the
visible control.

**Undefined custom properties.** A renamed token leaves silent fallbacks behind:
`grep -o 'var(--[a-z-]*)' | sort -u` against the declared set.

**Every outbound link.** `curl` each one. A 404 is dead; a 403/503 is a bot wall, which is
not the same thing and should be reported as unverified rather than dropped or claimed.

**RTL, if bilingual.** Logical properties everywhere. Gradients are the exception and need an
explicit `[dir="rtl"]` override, because gradient direction is not a logical property.

---

## 6. CACHING WILL LIE TO YOU

The single most expensive bug in this whole process was `Cache-Control: immutable` on a CSS
file whose name never changes. Browsers paired brand-new HTML with the first stylesheet they
ever saw, and it presented as a *taste* problem.

- Content-hashed or content-stable filenames (images, fonts): immutable, one year.
- Files edited in place under the same name (`site.css`, `site.js`): `max-age=0,
  must-revalidate`, plus a `?v=N` bump on every change.
- When an effect "does not work", **bust the cache before debugging the code**.

---

## 7. THIRD PARTIES ARE A LIABILITY

Self-host fonts. A blocked Google Fonts request means the whole design renders in fallback
Helvetica and the user thinks you designed that. The same applies to video posters, embeds
and widgets: fetch once, commit, serve locally.

If content must stay fresh, do the fetch **offline** and commit static files. The visitor's
browser should still make zero third-party requests.

---

## 8. CONTENT IS PART OF THE DESIGN

Real content is the difference between a template and a site. While redesigning, verify what
the page actually claims:

- **Do not invent facts to fill a layout.** If a claim has no source, cut it or mark it.
- **Check for stale claims.** A page describing someone as current when they are not is worse
  than an ugly page.
- **A borrowed quote from a famous stranger is worse than no quote.** The subject's own words
  are always stronger.
- **Do not publish what is not yours to publish.** Article hero images belong to the
  publisher; deal terms belong to both parties. A thumbnail-scale link preview with
  attribution is a different thing from decorative use.
- **The person you are building for knows things you cannot search.** When they contradict
  your research, they are usually right.

---

## 9. WORKING ORDER

1. Design read + concept, one line each.
2. Tokens: ground, elevation ramp, one rationed accent, type scale.
3. Fix the five tells (§2).
4. Structure and grid-breaks (§3).
5. Motion (§4).
6. **Component pass — `ux-patterns`.** Every interactive element gets all its states, and each
   component matches its spec. Run that skill's ship audit. Steps 1–5 stop a page looking
   generic; this one stops it *behaving* like a demo, which is the half users actually hit.
   Dense tables and grids also get `fe-redesign-mobile` here.
7. **Verification pass (§5) — before claiming anything works.**
8. Cache-bust, deploy, re-verify on the deployed URL.

Report honestly: what was measured, what was assumed, what is still unverified. If a screenshot
misled you, say so and correct it in one sentence rather than quietly re-fixing it.

---

## Companion skills

Load alongside, in this order:
- `ux-patterns` — **the component-level reference**: ~50 buildable specs (states, forms, tables,
  toasts, menus, gestures) plus the design laws behind them. This is the one that answers "how
  should this component actually behave"; §2 above answers "why does the page look generic".
- `fe-redesign-mobile` — restructuring a desktop-shaped layout for a phone. Load it for
  `/fe-gal mobile` and any table, grid or dense list.
- `fe-design-taste` — anti-slop rules and the dial system.
- `fe-animations` — easing, timing, gesture detail.
- `impeccable` — production quality bar and the absolute bans.

`/fe-gal` is the loop that sequences them and adds the measurement discipline they assume.
