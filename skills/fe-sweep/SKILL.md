---
name: fe-sweep
description: Audit a frontend with every frontend skill at once, one agent per lens, then verify the findings in a real browser and execute the fixes. Use when a site "doesn't flow", feels incoherent across screen sizes, or is due a full design and quality pass. Trigger with /fe-sweep.
---

# fe-sweep

Ten lenses over one site, in parallel, then act on what survives.

This exists because a single reviewer finds what that reviewer looks for. Ten
independent ones converge on the real defects — and when six of them
independently name the same thing, that is not taste any more, it is the bug.

## The one rule

**Nothing gets fixed on an agent's say-so.** Roughly a quarter of the findings
will be wrong, stated with exactly the same confidence as the right ones. Every
finding is a claim to check, not a task to do.

## Steps

### 1. Establish ground truth before dispatching anyone

Serve the site and capture the screenshots all agents will share, so they
describe the same render instead of ten different ones:

```bash
cd <site-root> && python3 -m http.server 8899 &
node ~/.claude/skills/fe-sweep/scripts/shots.js http://localhost:8899 <scratch>/shots "/,/page-a/,/page-b/"
```

The size list deliberately covers the awkward middle (600–1024px). That range
is where responsive bugs live and where nobody looks.

Then read the screenshots yourself and form your own view first. You are the
eleventh reviewer, and the only one who will still be here at the end.

### 2. Dispatch one agent per lens, in parallel, in a single message

See `reference/lenses.md` for the lens table and the prompt shape. Every prompt
carries the owner's complaint verbatim and a **"do not re-report" list** of what
is already known — without it, the later agents spend their budget
rediscovering what the first one found.

Do not run them sequentially. Do not merge two lenses into one agent to save
tokens; the independence is the product.

### 3. Verify every finding before acting on it

Check the claim against the code or the browser. Typical yield from ten agents:

- **Real and confirmed** — act on it.
- **Real defect, wrong explanation** — fix the defect, not the story.
- **Already done** — audits routinely "find" work that is already in the file.
- **Simply wrong** — say so out loud rather than silently dropping it.

Say which is which in the write-up. A finding you overruled is information.

### 4. Look for the root cause under the findings

Findings arrive as a list of symptoms. They usually are not one. The question
to ask is *how did this get authored?* — because the same answer explains most
of the list at once:

- A nav whose item set differs between pages was **authored page by page**.
- A hero with four compositions across ten `@media` blocks was **authored
  breakpoint by breakpoint**.

Fixing the symptoms leaves the cause in place and it grows the fifth
composition next month. Fix the authoring: one nav, defined once; one
breakpoint line, chosen deliberately — ideally the same line for everything
that changes, so the design has one place where it reorganises instead of six.

### 5. Execute, then measure what you actually changed

```bash
node ~/.claude/skills/fe-sweep/scripts/measure.js http://localhost:8899 "/,/page-a/,/page-b/"
```

It checks horizontal overflow, permanently-unrevealed content, blank images,
**frames an element fails to fill**, dead anchors, small tap targets, and
whether the nav is the same on every page. Each check is there because that
exact bug got past someone who was looking straight at the page.

Then measure the specific property you changed. Not a proxy for it.
*A photo whose aspect ratio is correct at every width can still be failing to
fill its frame at every width.* Ratio was measured; fill was not; the bug
shipped. If you changed a height, measure the height.

### 6. Distrust your own failing test too

When a check fails, confirm what it is measuring before you "fix" the code.
Two false alarms in one session, both the test's fault, both looking exactly
like a real bug:

- Images reported broken — they were `loading="lazy"` and the check had jumped
  straight to the bottom, so the middle of the page never loaded.
- Still reported broken after that — those ones are zero-size until hover, so
  lazy-loading correctly never fetches them.

A failing check is a claim too.

### 7. Ship

Bump the cache marker (`?v=N`) on every CSS/JS reference in every page, deploy,
and re-run `measure.js` against the **deployed URL**, not localhost. Confirm the
marker changed — that is how you know you are looking at the new code and not a
cached copy of the old one.

## Reporting

Lead with the root cause, not the finding count. Name what you overruled and
why. Name what you changed on your own judgement, so it can be reverted. Name
what the audits found that you cannot fix because it needs the owner — missing
content, unconfirmed rights, decisions that are not yours.
