---
name: repair-engine
description: >
  Operate and install the "repair engine" — a click-to-report loop (Alt+click on
  desktop, tap the 🔧 FAB then tap the target on mobile) that files UI
  change-requests from a running app to GitHub issues tagged with the exact source
  file:line. Use when the user says "repairs" / "drain the repair queue" (pull the
  repair:inbox queue and fix each card), or when installing the engine into an app —
  Vite+React+Supabase, or a static site on Cloudflare Pages (see "Static-site variant").
---

# Repair Engine

Two jobs: **install** the engine into a repo, and **run** the repair trigger.

## Trigger: the user says "repairs" / "drain the repair queue"

Drain the `repair:inbox` queue for the current repo. For each issue:

1. `gh issue list --label repair:inbox --json number,title,body` — the queue.
2. `gh issue edit <n> --add-label repair:doing --remove-label repair:inbox`.
3. Parse the fenced JSON bundle in the issue body. `source` (`file:line`) is a
   *starting point*, not gospel: it's the DOM element the reporter Alt+clicked,
   which is very often a **shared UI primitive** (`badge.tsx`, `card.tsx`,
   `button.tsx`) — NOT where the fix lives. Use `route` + `nearbyText` +
   `ancestors` to find the real feature file (e.g. the route/component that
   renders that badge). Still don't blind-search the repo; grep for `nearbyText`
   or the route's component.
4. Implement the fix.
5. `gh issue comment <n>` with a short per-card report (what changed, files).
6. **Ambiguous?** Two paths:
   - If the user is present and told you to "ask away / fix away": use
     `AskUserQuestion` with a **concrete proposal per card** (recommended option
     first, a mock/preview where it helps). Then implement their answer. Batch up
     to 4 cards per question call. Read the target files first so your options are
     grounded in what the UI actually does — don't ask the user to explain their
     own app.
   - Otherwise: `gh issue edit <n> --add-label repair:needs-info --remove-label repair:doing`,
     comment the clarifying question (still with a concrete proposal so the next
     drain can just execute), and SKIP. Never guess.
7. **Verify before you claim done.** For each fixed card run, in order:
   `tsc --noEmit` (or `npx tsc --noEmit`) → `eslint` on the changed files → then a
   real **browser clickthrough** for anything with runtime/data behavior (drive
   it via a `model="haiku"` Agent using the `claude-in-chrome` tools against the
   `npm run dev` server, not by calling the mcp tools from the main loop). Pure
   string/JSX-restructure fixes are covered by tsc+lint alone.
8. **Closing (standing authorization — don't ask):** close every card you've
   implemented AND verified — `gh issue close <n> -c "<what changed>" --reason completed`
   then `gh issue edit <n> --remove-label repair:doing`. "Verified" = `tsc` + `eslint`
   clean **plus** a browser clickthrough for anything with runtime/data behaviour
   (or a deterministic REST/DB check when the UI can't be driven, e.g. dnd-kit).
   Do NOT leave verified work open waiting for a "go" and do NOT ask whether to
   close it — just close it and report. Leave a card OPEN only when: (a) its runtime
   genuinely couldn't be verified — add a "ready — verify in-app" comment and say
   why; or (b) it's `needs-info`/blocked. The owner closes nothing by hand; that's
   your job once it's verified.

While you fix locally, Vite HMR reloads your screen preserving route/state; deployed
fixes reach the reporter on their next page load.

### Field notes (learned in the field)
- **`source` → primitive trap:** `badge.tsx:24` / `card.tsx:28` recur across
  unrelated cards — always the clicked chrome, never the fix site. `nearbyText`
  is your best locator.
- **Batch label transitions** (`for n in 103 104 109; do gh issue edit $n ...`).
- **DRY the fix:** if a card makes you duplicate existing logic (e.g. an
  impersonate/pay flow already in another component), extract a shared helper
  instead of copy-pasting — leaves the codebase better than a per-card patch.
- **New i18n strings go in BOTH languages** (this app: `hr` + `en` in
  `src/lib/i18n.ts`); a run parity-check (flatten both trees, diff keys) catches
  a forgotten side.
- **Pre-existing red build ≠ your fault.** If `npm run build` fails, check the
  errors are in files you didn't touch before blaming your change. A stray
  `chore(types): regenerate database.types` commit can silently overwrite a
  **hand-maintained** types file — wiping custom `export type`s (enums, JSON
  column shapes) that many files import — and break the build on `main`. Fix:
  restore the hand version (`git show <regen>^:src/lib/database.types.ts > …`)
  and typecheck; the machine regen was the mistake.

## Install (see reference/install.md for the full copy-paste)

Grafts three contained pieces into a Vite+React+Supabase repo:
1. `src/repair-engine/` — Babel `data-src` plugin, bundle builder, gated overlay
   (desktop Alt+click **and** mobile 🔧-FAB arm→tap → shared bottom-sheet composer), mount.
2. `supabase/functions/repair-capture/` — auth + allowlist + GitHub issue creation.
3. Two wires: a `@rolldown/plugin-babel` instance in `vite.config.ts` and a
   `mountRepairEngine()` call in the app root (`main.tsx`). (install.md covers the
   `plugin-react@6`/Oxc caveat.)

Gating is an env allowlist (`REPAIR_REPORTERS`) + `REPAIR_ENGINE_ENABLED` on the
function. Reporter gating is server-enforced.

**Removal:** delete `src/repair-engine/` + `supabase/functions/repair-capture/`,
revert the two wire lines, unset the function secrets. No schema to unwind.

## Static-site variant (Cloudflare Pages, no React, no Supabase)

Reference implementation: `tatarco/ilovik-website` (plain-node HTML generator → Pages).
Same UX, three differences:

1. **No `data-src`.** No component tree to Babel-instrument, so cards carry no
   `file:line`. Instead the bundle carries `lang`, `pageKey` (from `<body data-page>`),
   `nearbyText` and `sectionText` — and on a content-driven site that is *better* than
   file:line: the copy is all in one content module, so grep the text and you are at the
   source. Overlay is one plain-JS IIFE in the theme's assets dir.
2. **Capture endpoint is a Pages Function** (`functions/repair-capture.js`, root of the
   repo — `wrangler pages deploy <dist>` picks up `./functions` from cwd and logs
   "Uploading Functions bundle"). Env vars live on the Pages project, not Supabase.
3. **Gate is optional.** With no auth in the app there is no identity to check. For a
   preview URL, ship it ungated and rely on `REPAIR_ENGINE_ENABLED` alone; before a
   public launch, add an allowlist or a shared secret — the endpoint holds a GitHub
   token with Issues:write.

**The off switch that needs no rebuild:** the overlay probes `POST /repair-capture` with
`{probe:true}` on load and mounts *nothing* unless it answers OK. So flipping
`REPAIR_ENGINE_ENABLED` to `false` in the Pages dashboard removes the wrench sitewide,
instantly. Ship the script tag unconditionally; let the server decide.
