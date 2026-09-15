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

### money-audit

Pull a household's real bank, card and loan data into a local SQLite snapshot through an
open-banking aggregator, attribute every account to a person, and investigate it in SQL:
debt and its true interest rate, idle cash sitting next to expensive credit, recurring
charges, PayPal billing agreements, duplicated insurance.

Two traps are documented because both produce confidently wrong numbers: a revolving card
that reports as **many monthly snapshots of itself** (summing them multiplied one debt by
10x), and bilingual owner strings that silently drop whole cards from a total. The
verification protocol - re-derive every finding independently, and check the mailbox before
calling any merchant a scam - is the point of the skill, not the pipeline.

It is not free: an aggregator subscription (~ILS 49/mo in Israel, PSD2 AISP elsewhere) plus
real model time. A two-person, nine-institution audit ran ~2,000 assistant turns.

```bash
cp -R agent-skills/skills/money-audit ~/.claude/skills/
```

Pairs with `subscription-audit`, which cancels what this finds and claims the refunds.

Write-up: https://gal.tidhar.org.il/blog/money-audit/

### subscription-audit

Audit a family member's mailbox, app stores and invoice PDFs for recurring charges they no
longer want or never knew about, then cancel them and claim refunds. Ranks senders by
frequency instead of reading anyone's mail, harvests and parses invoice PDFs (the amounts
are almost never in the email body), and drives the real account pages to cancel.

Finds the things people miss: fleeceware billed **weekly**, the same product subscribed to
twice, "continuation discounts" that expire and double the price, geo-dead features
(US-only roadside assistance sold in Israel), zero-usage subscriptions, and charges folded
into a phone bill that have nothing to do with phone service.

Two rules are baked in: **nothing is cancelled without item-by-item approval**, and the
agent never claims to *be* the account holder when talking to support.

```bash
cp -R agent-skills/skills/subscription-audit ~/.claude/skills/
```

Requires the [gmail skill](https://github.com/tatarco/gmail-skill) for mailbox access and a
browser-automation skill for the account pages.

Write-up: https://gal.tidhar.org.il/blog/subscription-audit/

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

Every phase also gets a **risk class** - `fixed`, `metered`, `gated`, `best-effort` or
`not-a-build` - because the class decides what you can safely commit to. A phase that cannot be
typed at all is not a build phase; the skill splits it into a short gate whose deliverable is the
missing information, and the real phase behind it.

Deliberately does **not** price anything. Typing a phase and pricing it are different jobs.
`TEMPLATE.md` is the blank, in English and Hebrew.

## License

MIT

### fe-gal

Take a frontend from ugly to genuinely good, and prove it. Concept first, kill the AI
tells, then measure the result in a real browser instead of trusting a screenshot.
Pairs with `fe-ux-patterns` (component-level reference) and `fe-redesign-mobile`.

### fe-ux-patterns

~50 concrete, buildable UX component specs and design laws - spacing, dark mode, motion
timing, forms, tables, toasts, modals, destructive actions. Load when a UI "looks cheap".

### fe-redesign-mobile

Restructure a desktop-shaped UI so it works on a phone: tables into cards, column triage,
progressive disclosure, container-query breakpoints.

### repair-engine

Click-to-report loop for a running app: Alt+click an element, file a GitHub issue tagged
with the exact source `file:line`. Then drain the queue and fix each card.

### telegram-notify

Send yourself a Telegram message from any session - "tell me when it's done". Reads
`TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` from env or `~/.config/telegram-notify/.env`.
