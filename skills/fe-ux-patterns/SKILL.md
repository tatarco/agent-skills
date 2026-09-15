---
name: ux-patterns
description: A library of concrete, buildable UX/UI component specs and design laws — spacing, dark mode, radius, motion timing, loading, forms, tables, toasts, dropdowns, modals, search, settings, destructive actions, and ~50 more. Use when building or reviewing ANY interface component, when a UI "looks cheap / feels off / looks AI-made", when deciding how a component should behave in its edge states, or when auditing a screen before shipping. Also loaded by /fe-gal as its component-level reference.
---

# UX patterns

Most "this feels cheap" reactions are not taste problems. They are **missing states** and
**unmade decisions**. This skill is the decision list — roughly fifty components and laws,
each reduced to the handful of rules that separate a shipped component from a demo one.

## How to use it

- **Building a component?** Grep the reference file for its name and follow the spec. Do not
  invent behaviour a spec already fixes.
- **Reviewing a screen?** Run the audit below, then open the specs for the components present.
- **Do not read all four reference files.** Load only the one you need.

| File | Covers |
|---|---|
| `references/foundations.md` | Spacing, whitespace, proximity, type scale, tokens, radius system, dark mode, colour, numbers, optical corrections, real-data robustness |
| `references/motion.md` | Timing numbers, easing, feedback, the loading system, perceived performance, optimistic UI |
| `references/components.md` | ~35 component specs: forms, inputs, buttons, tables, toasts, menus, search, settings, uploads, gestures, collaboration |
| `references/psychology.md` | Serial position, Zeigarnik, peak-end, Fitts, colour meaning, shape, plus the dark patterns to recognise and refuse |

Mobile restructuring of dense desktop layouts has its own skill: **`redesign-for-mobile`**.

## The six laws everything else is a special case of

1. **Every component is a state machine, not a happy path.** Default, hover, focus, active,
   disabled, loading, empty, error, offline, partial. One missing state reads to the user as
   one bug. This single rule fixes more perceived quality than any visual change.
2. **Silence is failure.** Every action gets an answer within 100ms — a press state, a
   checkmark, a count that moves. A control that does nothing on tap reads as broken even when
   the request succeeded.
3. **Severity picks the surface.** Inline for recoverable, toast for transient, banner for
   system-wide, modal only when nothing else can work. Wrong surface = zero attention.
4. **Reversible beats careful.** Undo punishes nobody; "Are you sure?" punishes everyone for
   one person's mistake. Spend friction only where there is genuinely no way back.
5. **A value outside the system is a bug.** A new blue, a 13px, a one-off radius. Either it
   becomes a token with a written reason, or it gets replaced by the nearest existing one.
   Silent invention is how a product stops looking like one product.
6. **Optical, not mathematical.** Centred is what looks centred. Equal is what looks equal.
   Every rule here loses to the eye.

## Ship audit

Run this against a screen before calling it done:

- [ ] Every interactive element has all its states (law 1); loading and empty are designed, not blank
- [ ] Nothing is hidden behind hover only — touch has no hover
- [ ] Focus ring present, 2px + offset, `:focus-visible`, DOM order matches visual order
- [ ] Tap targets ≥44px (pad the hit area, don't grow the icon)
- [ ] Numbers right-aligned with `tabular-nums`; text left
- [ ] Destructive actions are not adjacent to primary ones, and are undoable or typed-to-confirm
- [ ] Errors name the fix, not just the problem; every error has an exit
- [ ] Real data tested: a 40-character name, a long URL, 247 rows, zero rows, one row
- [ ] Timings inside the ranges in `motion.md`; nothing under 300ms shows a loading state
- [ ] Colour is not the only channel for any meaning (icon + text + position)

---
*Distilled from the @designmotionhq UX-pattern reels (Instagram), 2026. Transcripts harvested
locally; the content is folded in here rather than bought as a plugin.*
