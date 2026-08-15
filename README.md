# agent-skills

Installable skills for Claude Code (and compatible agents). Each skill lives in
`skills/<name>/` with a `SKILL.md` entry point.

## Install

```bash
npx skills add tatarco/agent-skills
```

or manually:

```bash
git clone https://github.com/tatarco/agent-skills
cp -R agent-skills/skills/app-carousel ~/.claude/skills/
```

## Skills

### app-carousel

Build a LinkedIn carousel out of **receipts** — drive a live app through a real flow with
Playwright, screenshot each step, redact anything sensitive (in-page blur + an OCR verify
pass that fails loudly on survivors), and compose designed 1080×1350 slides as a PNG set
plus a PDF document post. Full RTL support (Hebrew/Arabic).

```
flow.json → capture.py → redact.py → slides.json + build.py → out/*.png + out/carousel.pdf
```

**Requirements:** `python3`, `playwright` (`pip install playwright && playwright install chromium`),
`Pillow`, `pytesseract`, and `tesseract` on PATH (`brew install tesseract`).

**Never** put credentials in `flow.json` — log in yourself and replay the session via
`storage` (see the skill's SKILL.md).

### typed-phase

A phase in a project is a function. The signature is what goes in, the return value is what
"done" looks like, the test is the acceptance criterion, the PR is the payment milestone, and
a change request is a new ticket. A phase without that signature is a function without types -
the client passes in whatever they want and you are obliged to return something.

Feed it a spec, a thread of client messages, or a rough verbal scope, and it slices the work
into phases typed with six fields: `in`, `out`, `payment`, `done when`, `signed off by`,
`not included`. Anything it cannot type from the input comes back as an explicit question
rather than an invented answer.

Includes the clause most people leave out - a named approver, a deadline, and a default:
*"Dana, within 5 business days. If Dana is unavailable it is approved automatically and payment
is released."* The usual way a phase stalls is not rejection, it is silence.

Deliberately does **not** price anything. Typing a phase and pricing it are different jobs.
`TEMPLATE.md` is the blank, in English and Hebrew.

## License

MIT
