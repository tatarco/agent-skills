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

## License

MIT
