# Repair Engine — Install Guide

Reference implementation: `studio-flow` (Vite + React + Supabase). Copy these files
verbatim, adjust `@` import alias / repo name / Supabase client import path to match
the target app.

## 0. Dependencies

`@vitejs/plugin-react@6` (Oxc-based) **dropped the inline `babel: { plugins: [...] }`
option**. Do NOT wire it that way. Instead run a separate Babel plugin instance
alongside `react()` using `@rolldown/plugin-babel`:

```bash
npm install -D @rolldown/plugin-babel @babel/core @types/babel__core \
  @babel/preset-react @babel/preset-typescript
```

(The last two presets are only needed if the plugin's own test/lint pipeline parses
JSX/TSX directly with Babel; the app's runtime JSX transform still goes through Oxc
via `react()`.)

## 1. `src/repair-engine/babel-data-src.cjs`

Build-time Babel plugin: stamps every host JSX element (`<div>`, not `<Component/>`)
with `data-src="relpath:line"` so a clicked DOM node maps straight to source.

```js
// src/repair-engine/babel-data-src.cjs
// Build-time: stamp each host (lowercase) JSX element with data-src="relpath:line"
// so a clicked DOM node maps straight to its source location. Runs in prod build.
const path = require('path')

module.exports = function dataSrcPlugin({ types: t }) {
  return {
    name: 'repair-data-src',
    visitor: {
      JSXOpeningElement(nodePath, state) {
        const nameNode = nodePath.node.name
        // host elements only: <div>, not <Component />
        if (!t.isJSXIdentifier(nameNode)) return
        const tag = nameNode.name
        if (!/^[a-z]/.test(tag)) return
        const already = nodePath.node.attributes.some(
          (a) => t.isJSXAttribute(a) && t.isJSXIdentifier(a.name, { name: 'data-src' }),
        )
        if (already) return
        const filename = state.file.opts.filename
        if (!filename || filename.includes('node_modules')) return
        const rel = path.relative(state.file.opts.cwd || process.cwd(), filename)
        const line = nodePath.node.loc ? nodePath.node.loc.start.line : 0
        nodePath.node.attributes.push(
          t.jsxAttribute(t.jsxIdentifier('data-src'), t.stringLiteral(`${rel}:${line}`)),
        )
      },
    },
  }
}
```

## 2. `src/repair-engine/bundle.ts`

The machine-readable capture bundle: route, subtab, ancestor chain, nearby text,
geometry, and resolved `source`.

```ts
export interface RepairBundle {
  note: string
  route: string
  subtab: string | null
  source: string | null
  area: string | null
  ancestors: string[]
  nearbyText: string
  rect: { x: number; y: number; w: number; h: number }
  userAgent: string
  capturedAt: string
}

export function describe(el: Element): string {
  const tag = el.tagName.toLowerCase()
  const id = (el as HTMLElement).id ? `#${(el as HTMLElement).id}` : ''
  const cls = el.classList.length ? `.${el.classList[0]}` : ''
  return `${tag}${id}${cls}`
}

export function buildBundle(el: Element, note: string): RepairBundle {
  const ancestors: string[] = []
  let source: string | null = null
  let area: string | null = null
  let node: Element | null = el
  while (node && node !== document.body && ancestors.length < 8) {
    ancestors.push(describe(node))
    const ds = node.getAttribute('data-src')
    if (!source && ds) source = ds
    const da = node.getAttribute('data-area')
    if (!area && da) area = da
    node = node.parentElement
  }
  const r = el.getBoundingClientRect()
  const now = new Date()
  return {
    note,
    route: location.pathname + location.search + location.hash,
    subtab: (window as unknown as { __repairSubtab?: string }).__repairSubtab ?? null,
    source,
    area,
    ancestors,
    nearbyText: (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 200),
    rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) },
    userAgent: navigator.userAgent,
    capturedAt: now.toISOString(),
  }
}
```

## 3. `src/repair-engine/overlay.ts`

Two capture paths → one bottom-sheet composer:
- **Desktop:** `Alt+click` an element.
- **Touch/mobile:** tap the 🔧 FAB to *arm* repair mode, then tap the element
  (single tap — no long-press/double-tap, which collide with native mobile
  gestures). While armed, the target tap is intercepted so the app's own handler
  doesn't fire. Input is a bottom sheet (not a point-anchored box) so the on-screen
  keyboard never covers it; a `visualViewport` listener keeps it above the keyboard.

All our chrome carries a `.repair-ui` marker class so arm-mode ignores taps on
itself. Covered by `overlay.test.ts` (Alt+click send, arm→tap→sheet, app-handler
cancellation, cleanup).

```ts
import { buildBundle, type RepairBundle } from './bundle'

type Send = (b: RepairBundle) => Promise<{ url: string }>

// Desktop power path (Alt+click) + a touch-friendly path: tap the 🔧 FAB to arm
// "repair mode", then tap the element to report. Both funnel into one bottom-sheet
// composer, so the mobile keyboard never covers the input.
export function installOverlay(send: Send): () => void {
  const onClick = (e: MouseEvent) => {
    if (!e.altKey) return
    const target = e.target as Element | null
    if (!target || target.closest('.repair-ui')) return
    e.preventDefault()
    e.stopPropagation()
    openComposer(target, send)
  }
  document.addEventListener('click', onClick, true)
  const fab = mountFab(send)
  return () => {
    document.removeEventListener('click', onClick, true)
    fab.remove()
    disarm()
    document.querySelector('.repair-sheet')?.remove()
  }
}

// ── Arm mode (touch) ────────────────────────────────────────────────────────
let disarm = () => {}

function mountFab(send: Send): HTMLElement {
  const fab = document.createElement('button')
  fab.className = 'repair-ui repair-fab'
  fab.type = 'button'
  fab.textContent = '🔧'
  fab.setAttribute('aria-label', 'Report a change')
  Object.assign(fab.style, {
    position: 'fixed', right: '16px', bottom: 'calc(16px + env(safe-area-inset-bottom))',
    zIndex: '2147483646', width: '48px', height: '48px', borderRadius: '50%',
    border: 'none', background: '#4f46e5', color: '#fff', fontSize: '20px',
    boxShadow: '0 4px 14px rgba(0,0,0,.4)', cursor: 'pointer', lineHeight: '48px',
  })
  fab.addEventListener('click', (e) => { e.stopPropagation(); arm(send) })
  document.body.appendChild(fab)
  return fab
}

function arm(send: Send) {
  disarm() // idempotent: clear any prior arm

  const dim = document.createElement('div')
  dim.className = 'repair-ui repair-dim'
  Object.assign(dim.style, {
    position: 'fixed', inset: '0', zIndex: '2147483645',
    background: 'rgba(0,0,0,.28)', pointerEvents: 'none', // visual only — taps pass through
  })

  const banner = document.createElement('div')
  banner.className = 'repair-ui repair-banner'
  banner.innerHTML = 'Tap what to fix <span style="opacity:.7">· ✕</span>'
  Object.assign(banner.style, {
    position: 'fixed', top: 'calc(12px + env(safe-area-inset-top))', left: '50%',
    transform: 'translateX(-50%)', zIndex: '2147483646', padding: '8px 14px',
    borderRadius: '999px', background: '#4f46e5', color: '#fff', font: '600 13px system-ui',
    boxShadow: '0 4px 14px rgba(0,0,0,.4)', cursor: 'pointer',
  })
  banner.addEventListener('click', (e) => { e.stopPropagation(); disarm() })

  // Suppress native long-press callout/selection while aiming.
  document.body.style.setProperty('-webkit-touch-callout', 'none')
  document.body.style.userSelect = 'none'

  const onPick = (e: Event) => {
    const target = e.target as Element | null
    if (!target || target.closest('.repair-ui')) return // our own chrome → ignore
    e.preventDefault()
    e.stopImmediatePropagation() // cancel the app's own handler for this tap
    disarm()
    openComposer(target, send)
  }
  const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') disarm() }

  document.addEventListener('click', onPick, true)
  document.addEventListener('contextmenu', preventInArm, true)
  document.addEventListener('keydown', onKey, true)

  document.body.append(dim, banner)

  disarm = () => {
    document.removeEventListener('click', onPick, true)
    document.removeEventListener('contextmenu', preventInArm, true)
    document.removeEventListener('keydown', onKey, true)
    document.body.style.removeProperty('-webkit-touch-callout')
    document.body.style.removeProperty('user-select')
    dim.remove()
    banner.remove()
    disarm = () => {}
  }
}

function preventInArm(e: Event) { e.preventDefault() }

// ── Composer (bottom sheet) ─────────────────────────────────────────────────
function openComposer(target: Element, send: Send) {
  document.querySelector('.repair-sheet')?.remove()

  const sheet = document.createElement('div')
  sheet.className = 'repair-ui repair-sheet'
  Object.assign(sheet.style, {
    position: 'fixed', left: '0', right: '0', bottom: '0', zIndex: '2147483647',
    display: 'flex', flexDirection: 'column', gap: '8px',
    padding: '12px 12px calc(12px + env(safe-area-inset-bottom))',
    background: '#111', color: '#fff', font: '14px system-ui',
    borderTop: '1px solid #4f46e5', boxShadow: '0 -6px 24px rgba(0,0,0,.5)',
    transition: 'bottom .15s ease',
  })

  const chip = document.createElement('div')
  chip.textContent = describeEl(target)
  Object.assign(chip.style, {
    alignSelf: 'flex-start', maxWidth: '100%', overflow: 'hidden', textOverflow: 'ellipsis',
    whiteSpace: 'nowrap', padding: '3px 8px', borderRadius: '6px',
    background: '#4f46e5', color: '#fff', font: '600 12px system-ui',
  })

  const input = document.createElement('textarea')
  input.className = 'repair-note-input'
  input.rows = 2
  input.placeholder = 'What should change here?'
  Object.assign(input.style, {
    width: '100%', boxSizing: 'border-box', padding: '10px', borderRadius: '8px',
    border: '1px solid #333', background: '#000', color: '#fff', font: '15px system-ui',
    resize: 'none',
  })

  const row = document.createElement('div')
  Object.assign(row.style, { display: 'flex', gap: '8px', justifyContent: 'flex-end' })
  const cancel = mkBtn('Cancel', '#333', 'repair-cancel')
  const submit = mkBtn('Send', '#4f46e5', 'repair-send')
  row.append(cancel, submit)

  const cleanup = () => { sheet.remove(); vv?.removeEventListener('resize', reflow); vv?.removeEventListener('scroll', reflow) }
  cancel.addEventListener('click', cleanup)
  submit.addEventListener('click', async () => {
    const note = input.value.trim()
    if (!note) return cleanup()
    submit.disabled = true
    input.disabled = true
    try {
      const { url } = await send(buildBundle(target, note))
      toast(`Reported → ${url}`)
    } catch {
      toast('Report failed', true)
    } finally {
      cleanup()
    }
  })

  sheet.append(chip, input, row)
  document.body.appendChild(sheet)
  input.focus()

  // Keep the sheet above the on-screen keyboard (iOS moves the visual viewport).
  const vv = window.visualViewport
  const reflow = () => {
    if (!vv) return
    sheet.style.bottom = `${Math.max(0, window.innerHeight - vv.height - vv.offsetTop)}px`
  }
  vv?.addEventListener('resize', reflow)
  vv?.addEventListener('scroll', reflow)
}

function describeEl(el: Element): string {
  const tag = el.tagName.toLowerCase()
  const text = (el.textContent ?? '').trim().replace(/\s+/g, ' ').slice(0, 40)
  return text ? `${tag} · ${text}` : tag
}

function mkBtn(label: string, bg: string, cls: string): HTMLButtonElement {
  const b = document.createElement('button')
  b.type = 'button'
  b.className = `repair-ui ${cls}`
  b.textContent = label
  Object.assign(b.style, {
    padding: '9px 16px', borderRadius: '8px', border: 'none', background: bg,
    color: '#fff', font: '600 14px system-ui', cursor: 'pointer',
  })
  return b
}

function toast(msg: string, err = false) {
  const t = document.createElement('div')
  t.className = 'repair-ui'
  t.textContent = msg
  Object.assign(t.style, {
    position: 'fixed', bottom: 'calc(20px + env(safe-area-inset-bottom))', left: '50%',
    transform: 'translateX(-50%)', zIndex: '2147483647', padding: '10px 16px',
    borderRadius: '8px', background: err ? '#b91c1c' : '#15803d', color: '#fff',
    font: '14px system-ui',
  })
  document.body.appendChild(t)
  setTimeout(() => t.remove(), 3000)
}
```

## 4. `src/repair-engine/index.ts`

Public entry point. Ships in the prod bundle but stays inert unless the server
probe confirms the logged-in user is an allowlisted reporter.

```ts
// Public entry. Ships in the prod bundle; activates ONLY for an authorized reporter.
import { supabase } from '@/lib/supabase'
import { installOverlay } from './overlay'
import type { RepairBundle } from './bundle'

const FN = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/repair-capture`

async function authHeaders(): Promise<Record<string, string> | null> {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  if (!token) return null
  return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
}

export async function mountRepairEngine(): Promise<void> {
  const headers = await authHeaders()
  if (!headers) return // not logged in → inert
  // Probe: server decides if this user may report. Silent on any non-200.
  let ok = false
  try {
    const res = await fetch(FN, { method: 'POST', headers, body: JSON.stringify({ probe: true }) })
    ok = res.status === 200
  } catch {
    return
  }
  if (!ok) return
  installOverlay(async (b: RepairBundle) => {
    const h = await authHeaders()
    if (!h) throw new Error('no-session')
    const res = await fetch(FN, { method: 'POST', headers: h, body: JSON.stringify({ bundle: b }) })
    if (!res.ok) throw new Error(`capture-${res.status}`)
    return res.json()
  })
}
```

Adjust the `@/lib/supabase` import to wherever the target app's Supabase client
singleton lives.

## 5. `supabase/functions/repair-capture/authz.ts`

```ts
export function isReporter(email: string | undefined, allowlistCsv: string | undefined): boolean {
  if (!email || !allowlistCsv) return false
  const set = allowlistCsv.split(',').map((s) => s.trim().toLowerCase()).filter(Boolean)
  return set.includes(email.trim().toLowerCase())
}

export function issueFromBundle(b: Record<string, unknown>): { title: string; body: string } {
  const note = String(b.note ?? 'repair').replace(/\s+/g, ' ').trim()
  const title = note.length > 80 ? note.slice(0, 77) + '…' : note
  const src = b.source ? `\n**Source:** \`${b.source}\`` : ''
  const route = b.route ? `\n**Route:** \`${b.route}\`` : ''
  const body = `Captured via repair-engine.${src}${route}\n\n\`\`\`json\n${JSON.stringify(b, null, 2)}\n\`\`\``
  return { title, body }
}
```

## 6. `supabase/functions/repair-capture/index.ts`

```ts
// Edge function: repair-capture — receives an Alt+click capture from an authorized
// reporter and files it as a GitHub issue. Reporter allowlist + global flag are env
// secrets; the caller's Supabase identity is verified server-side.
//
// Secrets required:
//   SUPABASE_URL, SUPABASE_ANON_KEY  — auto-injected; used to verify the caller.
//   REPAIR_ENGINE_ENABLED            — "true" to enable; anything else disables.
//   REPAIR_REPORTERS                 — comma-separated authorized emails.
//   GITHUB_TOKEN                     — fine-grained token, Issues:write on the repo.
//   GITHUB_REPO                      — "owner/repo", e.g. "tatarco/studio-flow".
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { isReporter, issueFromBundle } from './authz.ts'

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
}
const json = (b: unknown, status = 200) =>
  new Response(JSON.stringify(b), { status, headers: { ...cors, 'Content-Type': 'application/json' } })

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors })
  if (req.method !== 'POST') return json({ error: 'method' }, 405)

  if (Deno.env.get('REPAIR_ENGINE_ENABLED') !== 'true') return json({ error: 'disabled' }, 403)

  const url = Deno.env.get('SUPABASE_URL')!
  const anon = Deno.env.get('SUPABASE_ANON_KEY')!
  const caller = createClient(url, anon, {
    global: { headers: { Authorization: req.headers.get('Authorization') ?? '' } },
  })
  const { data: who, error: whoErr } = await caller.auth.getUser()
  if (whoErr || !who?.user) return json({ error: 'auth' }, 401)
  if (!isReporter(who.user.email, Deno.env.get('REPAIR_REPORTERS'))) return json({ error: 'forbidden' }, 403)

  const payload = await req.json().catch(() => ({}))
  if (payload.probe === true) return json({ ok: true }, 200)

  const bundle = payload.bundle
  if (!bundle || typeof bundle.note !== 'string') return json({ error: 'bad_bundle' }, 400)

  const repo = Deno.env.get('GITHUB_REPO')!
  const token = Deno.env.get('GITHUB_TOKEN')!
  const { title, body } = issueFromBundle(bundle)
  const gh = await fetch(`https://api.github.com/repos/${repo}/issues`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/vnd.github+json',
      'Content-Type': 'application/json',
      'User-Agent': 'repair-engine',
    },
    body: JSON.stringify({ title, body, labels: ['repair', 'repair:inbox'] }),
  })
  if (!gh.ok) return json({ error: 'github', detail: await gh.text() }, 502)
  const issue = await gh.json()
  return json({ url: issue.html_url }, 201)
})
```

## 7. Wire it into `vite.config.ts`

**This is the corrected wiring.** `@vitejs/plugin-react@6` uses Oxc and no longer
accepts a `babel:` option on `react()`. Run the data-src plugin as a separate,
standalone plugin instance placed after `react()`:

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
// ...other plugin imports

export default defineConfig({
  plugins: [
    react(),
    // Runs the data-src Babel plugin on JSX/TSX only. react()/Oxc still
    // performs the JSX transform; this plugin only adds a data-src attribute.
    babel({
      plugins: ['./src/repair-engine/babel-data-src.cjs'],
      include: /\.[jt]sx$/,
    }),
    // ...other plugins (tailwind, PWA, etc.)
  ],
  // ...rest of config unchanged
})
```

Install the devDeps first (see Step 0 above):

```bash
npm install -D @rolldown/plugin-babel @babel/core @types/babel__core \
  @babel/preset-react @babel/preset-typescript
```

## 8. Mount it in the app root (`src/main.tsx` or equivalent)

Add near the top-level render call, before or after other mount-time setup:

```ts
import { mountRepairEngine } from '@/repair-engine'
// Activates only for an allowlisted reporter (server-probed); inert otherwise.
void mountRepairEngine()
```

## 9. Build spot-check: confirm `data-src` made it into the prod bundle

```bash
npm run build
grep -rl 'data-src' dist/assets | head -1 && echo has-data-src
```

Expected: prints a file path + `has-data-src`. If nothing prints, the Babel plugin
isn't running on JSX/TSX files — check the `include` regex and plugin order in
`vite.config.ts`.

You can also smoke-test the dev server before a full build:

```bash
npm run preview &   # or `npm run dev &`
sleep 2 && curl -s http://localhost:4173 | grep -q data-src && echo has-data-src
kill %1
```

## 10. Create the GitHub labels

```bash
for l in "repair:6f42c1" "repair:inbox:1d76db" "repair:doing:fbca04" "repair:needs-info:d93f0b"; do
  name="${l%:*}"; color="${l##*:}"
  gh label create "$name" --repo <owner>/<repo> --color "$color" --force
done
gh label list --repo <owner>/<repo> | grep repair
```

Expected: four `repair*` labels listed (`repair`, `repair:inbox`, `repair:doing`,
`repair:needs-info`).

## 11. Set the edge-function secrets and deploy

```bash
# Replace the email(s), repo, and token before running.
supabase secrets set \
  REPAIR_ENGINE_ENABLED=true \
  REPAIR_REPORTERS="reporter1@example.com,reporter2@example.com" \
  GITHUB_REPO="<owner>/<repo>" \
  GITHUB_TOKEN="<fine-grained PAT: Issues read/write on the repo>"
supabase functions deploy repair-capture
```

`SUPABASE_URL` and `SUPABASE_ANON_KEY` are auto-injected by Supabase for every
edge function — do NOT set them yourself.

## 12. End-to-end verify (manual, in the deployed/preview app)

**Authorized path:**
1. Log in as an allowlisted user (email in `REPAIR_REPORTERS`).
2. Alt+click any element → type a note → Enter.
3. Expect a green toast with an issue URL.
4. `gh issue list --repo <owner>/<repo> --label repair:inbox` shows the card; its
   body has the fenced JSON bundle with a `source` `file:line`.

**Unauthorized path:**
1. Log in as a NON-allowlisted user.
2. Alt+click → nothing happens (no popup, no network call succeeds).
3. Confirm no issue was created.

## Removal

Delete `src/repair-engine/` and `supabase/functions/repair-capture/`, revert the
`vite.config.ts` and `main.tsx` wire lines, and unset the function secrets
(`supabase secrets unset REPAIR_ENGINE_ENABLED REPAIR_REPORTERS GITHUB_REPO GITHUB_TOKEN`).
No database schema to unwind.
