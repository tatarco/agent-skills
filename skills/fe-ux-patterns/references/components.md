# Component specs

Each entry is the short list of decisions that separate a shipped component from a demo one.
Grep for the component you are building.

---

## Forms & input

### Input states — ship all six
1. **Default** — label *outside*, helper text below. A placeholder is not a label; it vanishes
   the moment they type, taking the question with it.
2. **Focus** — ring at ≥3:1 contrast against the background. The usual soft blue glow fails.
3. **Error** — three channels: colour shift **+ icon + message below**. A red border alone is
   invisible to ~12% of users with colour-vision deficiency.
4. **Success** — a green check *inside the field*, not a toast. The field confirms itself.
5. **Disabled** — greyscale background, not `opacity: .5`; keep it readable to screen readers.
6. **Loading** — spinner inside, input locked. This is the state that prevents the double-submit
   bug that ships every week.

One forgotten state equals one perceived bug.

### Validation timing
Validate **on blur**. On every keystroke you scream "invalid email" at the first letter —
technically correct, completely cruel. On submit only, they fill ten fields blind and everything
turns red at once. After a field has failed once, **switch that field to live** and clear the
error the instant it is fixed. A green check is feedback too — silence after effort feels like
the form is judging them.

### Microcopy
- Button labels are **promises**: "Create my free account", not "Submit". It is the last thing
  read before committing.
- Errors name the problem **and the fix**: "That email is taken — want to log in?" not "Invalid
  input". A good error is a detour sign, not a dead end.
- Write like a person. No human says "operation failed" or "invalid entry".
- Copy carries the brand louder than the palette does.

### Password field
Strength is **entropy, not checkboxes** — `P@ssw0rd` passes every rule and cracks in hours;
length beats symbols. Show the checklist **while typing**, each requirement ticking live, with a
growing bar (a red "weak" only punishes after the fact). Eye toggle to reveal. **Never block
paste** — password managers type stronger passwords than humans. Best pattern: a one-tap
**generate** — unique, saved, zero typing.

### OTP input
Six boxes are **one value split across six slots** — track one string, not six states.
Paste-to-fill: strip spaces, one digit per box. Auto-advance on type, jump back on backspace
into an empty box. `inputmode="numeric"` plus SMS autofill so the user taps nothing. Resend
behind a **30s timer** or people hammer it into a rate limit. Wrong code: shake, clear, refocus
box one. Right code: lock all six green.

### Card input
Group digits **4×4 as they type**. First digit names the brand (4 = Visa, 5 = Mastercard) — show
the logo the moment it is known. Keep the cursor correct when a space is auto-inserted. Validate
on blur, forgive while typing — red means *done and wrong*, not *unfinished*. Strip dashes and
noise rather than rejecting a value you could clean yourself. **Mask for humans, store raw digits.**

### Inline editing
The text must **whisper that it is editable** — a pencil on hover, a soft background tint —
or users file tickets asking you to change a title. On swap to input, **nothing moves**: same
font, size, padding; the border was there all along, transparent. Enter commits, Escape cancels.
**Blur is the argument** — Notion saves, spreadsheets discard. Pick one rule and never break it.
Save optimistically; on failure roll back, keep the draft, say why. More power means more
accidents — match editability to the cost of a typo.

### Wizard / multi-step form
Twelve fields in one wall triggers scroll fatigue; the brain handles ~3 at a time. **Group by
context** (personal / shipping / payment / review), not by count — arbitrary splits feel slow.
Show progress: one of bar, numbered dots, or step labels. **Validate inside the step** — a bad
email on step 1 must not surface on step 4. **Save state on every step change** so Back and
refresh both survive. Lose the form once and you lose the user.

### Disabled buttons are usually the wrong tool
A disabled button drops out of the tab order, says nothing to a screen reader, and fails contrast
grey-on-grey. Worse, `pointer-events` are dead, so the tooltip explaining *why* never fires — the
reason is unreachable by design. **Keep the button live**: on click, validate, light up the two
blocking fields and move focus to the first. Same protection, visible path forward.
**Disabled ≠ loading**: during a request the button keeps focus, shows a spinner and reports busy.

### Double-submit guard
Disable **on tap**, instantly — a slow network must not buy twice. Swap the label for a spinner
**inside the same button with the width locked** (layout shift reads as broken). Disabling the UI
is not enough: guard the handler in code, and give the server a real **idempotency key**. On
success morph the spinner into a check for a beat before moving on; on error snap back and say
why *on the button*. Re-enable only when the real request resolves — never on a timer.

---

## Menus, navigation & search

### Dropdown / select
Obvious trigger (caret, hover state, ≥44px target). **Flip up at the viewport bottom** — never
clip the last item. Keyboard: arrows move, Enter selects, Escape closes. Past **10 items add
search**; past 100, virtualise. Open in **under 150ms**.

### Context menu
It **measures before it opens**: no room below → flip up, no room right → mirror left, always
anchored to the cursor and inside the viewport. Twelve flat actions read as noise — group by
intent with dividers, destructive alone at the bottom in red. **Hover intent:** draw an invisible
triangle from cursor to submenu so it survives a drifting cursor (the Figma trick). Arrows walk,
letters jump (D → Duplicate), **Escape closes one level**, not the whole thing. Mobile has no
right-click: long-press opens the same actions as a bottom sheet.

### Command palette (⌘K)
Not a search box. **Fuzzy match with the matched letters highlighted** — "stg" finds Settings.
**Group results**: recent → actions → pages; a flat dump is slow. Full keyboard: arrows move,
Enter runs, Escape closes. On empty, show **recent commands**, not a void. Async commands spin
**inline** with the palette open — never freeze the screen. Sub-menus step back one level on
Escape. Power users only: never the primary nav for new users, who don't know it exists.

### Navigation patterns — pick by job
| Pattern | Where | When |
|---|---|---|
| Tab bar | Mobile only | 3–5 top-level destinations, always thumb-reachable |
| Sidebar | Desktop only | Hierarchical content or >5 sections; persistent, collapsible, never hidden |
| Hamburger | Mobile only | **Secondary** content (settings, account, support). ~40% fewer clicks on hidden menus |
| Command palette | Power users | Additive, never primary |
| Breadcrumbs | Any | Only past two levels of hierarchy; in a flat structure they confuse |

Default: mobile = tabs, desktop = sidebar. Everything else has a specific job.

### Tabs
The underline **slides, never teleports**; spring config matches the content fade. Eight tabs on
one screen do not wrap to a second line — scroll horizontally with **edge fades** so more is
visible, plus chevrons on desktop. Keyboard: arrows between tabs, Home/End to the ends, Tab moves
to the next focusable group. **Focus ring and active state never share a colour.** Content: fade
out, 80ms pause, fade in, matched height. Mobile: segmented control under 5 tabs, bottom sheet
over 5 — never a scaled-down desktop version.

### Search
Five parts, most apps ship two.
1. **Placeholder is onboarding** — "Search by name, SKU or brand", not "Search".
2. **Empty state is not empty** — recent searches on focus, one click to refill.
3. **Autocomplete ranks by clicks, not alphabet**, each result carrying a category badge. Three
   good results beat ten.
4. **Keyboard** — arrows navigate, Enter selects, Escape closes, focus ring stays visible.
5. **Zero results is not a dead end** — suggest alternatives, popular searches, category jumps.

### Scroll restoration
An SPA resets scroll to zero on every route change; the browser used to remember and your router
forgot how. **Save scroll position per history entry and restore it** — position is state.
**Offset the restore by a sticky header's height**, or you land close but wrong; give anchors
`scroll-margin-top` for the same reason. And note that infinite scroll pushes the footer away
forever — your links, contact and terms live down there and nobody ever reaches them.

---

## Data display

### Data table — six decisions
1. **Alignment.** Numbers right with tabular figures, text left. A column of centred amounts
   cannot be compared.
2. **Rows.** One hairline between rows, hover lights the current row. Zebra stripes fight the
   content and only earn their place on very wide rows.
3. **Density is a decision, not padding.** Compact 40 / default 48 / comfortable 56, one toggle.
4. **Pin the first column and the header.** Twelve columns, six visible: scroll right and the
   row loses its name.
5. **An empty cell is a question** — missing, zero, or loading? Use an em dash. Truncate long
   text with a tooltip; **numbers never truncate**.
6. **Actions on every row are noise** — 50 rows, 50 pencils. Reveal on hover/focus; touch gets a
   kebab. Sort arrows only on the active column.

For the phone version of a table, use the **`redesign-for-mobile`** skill.

### Bulk actions
The header checkbox has **three** states — checked, empty, **partial**. Drop the partial state
and users lose track of what they picked; clicking it selects everything, never clears.
"Select all" grabs the six rows on screen — **say the number out loud**: "Select all 247
matching", and update it live as filters change. **Shift-click selects a range**; every desktop
user expects it. Selection lives in **app state, not the visible rows**, or it dies on page
change. Deleting 247 rows needs no confirm dialog: echo the count in the button, run it, offer
**undo for 10 seconds**.

### Pagination
**Cursor, not offset.** "After this ID" stays stable; `skip 500` shifts every page when a row is
added and users see the same item twice. Choose by job: **numbered** for jumping, **load more**
for control, **infinite** for feeds. Don't render 500 links — truncate `first … current … last`,
always keeping first and last reachable. **Put the page in the URL** so it is shareable and
survives refresh, and restore scroll on back.

### Charts
- **Bar charts start at zero. No exceptions.** A truncated baseline turns 4% into "400%".
- Bars compare values; lines show change over time. **Pie breaks past five slices** — the eye
  cannot rank angles.
- **Colour is encoding, not decoration**: categorical for groups, sequential for scale, diverging
  around a midpoint. One accent for the point, the rest grey.
- Kill the non-data ink — heavy gridlines, 3D bars, drop shadows. **Label the line directly,
  drop the legend.**
- Aspect ratio changes the story: aim for slopes near **45°**, where the eye reads change best.

### Avatar
Image first, **initials on failure**, generic icon last resort — never a broken square. Generate
the background colour **from the name hash** so the same person is the same colour everywhere,
forever. Two initials by default; drop to one only at tiny sizes ("JD" reads as a person, "J"
reads as a bug). Groups: cap the row and spill into "+3". Online status goes **on the ring**, not
a second badge. Pick three sizes and stop — 24 in lists, 32 in headers, 40 in profiles.

### Notification badge
Cap the number so the shape stays stable (`99+`) and **pin it to the corner** so the icon never
moves under it. **A dot says something changed; a number says how much** — showing both is noise.
A count badge and a status dot are different objects with different colours (red = act now,
green = online). **It clears the moment the view opens** — a badge that lingers after you look
trains people to ignore every badge. It ticks up as the count climbs; a reset-to-zero flash reads
as a bug. **Badge only what needs a decision**, or the colour stops meaning anything.

---

## Feedback surfaces

### Notifications — severity picks the surface
| Surface | Volume | Dismissal | Example |
|---|---|---|---|
| Toast | corner, low | auto 4s | "New message" |
| Banner | full top, medium | until dismissed | "Server degraded" |
| Modal | blocks everything | requires a choice | "Card declined" |
| Badge | passive | on view | "3 unread comments" |

Mix surfaces by severity, never by habit. Wrong surface = zero attention. Three toasts breathe in
a stack; three modals are a trainwreck.

### Toast
**Position:** desktop bottom-right, mobile top. Never centred — it blocks what the user is doing.
**Timing:** info 4s, warning 7s, errors stay until acknowledged. A fixed timer is a bug.
**Stacking:** max three visible, new ones push old ones up with spring physics.
**Always dismissable:** close button, swipe on mobile, pause on hover. If they cannot escape it,
it is a modal. **Colour-code with an icon plus a left border** — a background tint alone excludes
the ~6% who cannot distinguish it. Destructive actions get an undo inside the toast.

### Error states
1. **Type the error first** — validation, network, server, permission. Each gets a different
   pattern. Do not show a 500 modal for a typo.
2. **Every error needs a way out** — retry, refresh, contact. A dead end is the worst thing you
   can ship.
3. **Severity decides the surface** — inline for recoverable, toast for transient, modal only
   when nothing else works.
4. **Human copy** — "Lost connection, reconnecting in 5s", not "An error occurred".
5. **Inline validation kills ~80% of errors before they happen.**

### Empty states
Your first impression, usually wasted. A blank screen tells the user nothing is wrong — one small
illustration changes that. Copy sounds like a product, not a log file. **Every empty state needs
a primary action** — the next step they would take if they knew what to do — not a refresh button.
**There are four kinds of empty** and each needs its own design: first run, no results, filtered
out, and error. First-run empty is your best onboarding moment: teach what the feature does
before they touch it.

### Copy to clipboard
Icon flips to a check **the instant the copy fires** — no spinner, no delay. Hold ~2s, then fade
back; left stuck forever, the next copy gives no signal at all. **Copy the raw value**, not the
formatted span with its line breaks and zero-width characters — paste that into a terminal and
watch it break. **Announce "Copied" through a live region**: screen readers hear nothing when an
icon quietly changes, and silent success is still a failure for someone. On an insecure origin
the clipboard API fails silently — fall back, because a silent button lies.

---

## Controls

### Toggle / switch
Rail width = knob diameter × 2; padding = knob radius. These ratios are what make the knob feel
anchored. **Don't snap — morph**: rail colour, knob slide, knob shadow and label cross-fade
together in 250ms ease-out. Space bar toggles, visible focus ring, ARIA announces the state
change; skip these and it is a fake button. Async: spinner **in the knob**, roll back if the
server says no — the user never waits for the network.

Toggles apply **instantly**. Anything with a bigger blast radius (identity fields, billing) gets
a save/cancel bar instead. Match the model to the consequence.

### Slider
A 4px track is a coin toss between 47 and 48 — **extend the hit area far past the line**; the
whole row should respond. **Fill everything left of the thumb** so the value reads before you
check it. **Snap to steps** — most values are discrete (volume, ratings, price) and continuous
sliders never land clean. Show the value above the thumb while dragging, then fade it. Two thumbs
for a range. Arrow keys nudge one step, Home/End jump to the edges.

### Star rating
**Hover fills before the click** — show where they are about to land, and snap back when the
cursor leaves. Preview and selection are **two layers**; mixing them makes the value flicker.
A 4.4 average is not five full stars — render the real fraction with a **clipped half star**, or
you are lying. Fill left to right, **30ms apart**; all at once feels dead. Pair discrete stars
with one continuous arc for the summary — the ring reads faster than any number.

### Date picker
Same date: six clicks or one. **Presets cover ~90%** — today, yesterday, last 7, last 30, last
quarter — with custom range for the rest. **Highlight the range**: hover paints a preview, click
start, click end, drag the edges to refine. **Two months side by side** (three on wide screens)
because ranges cross months. Keyboard: type the date directly, Enter validates, Escape kills,
PageUp jumps a month, Shift+PageUp a year. **Mobile is not a popover** — full-screen sheet,
vertically scrolling calendar, today at the top, big confirm at the bottom.

### Filter chips
Three visible states — idle, active, disabled. If active looks like idle the filter feels broken.
**Update the result count the instant a chip flips**, or users tap twice. **Clear-all with the
count** so they know what it wipes. Ten chips never fit a phone: scroll them sideways in one row
with an edge fade — wrapping into a wall buries the results. **Pin active chips on top** so users
can see why the list shrank.

### Tooltip
**300ms delay before showing** — instant tooltips fire on every passing cursor; that is noise.
An **arrow** connects it to its trigger. **Flip near viewport edges.** **Dismiss on everything** —
mouse leave, Escape, focus out, tap outside. **Max ~300px wide, one sentence.** A tooltip is a
hint, not documentation — and never the only place information lives.

### Resizable panels
The visible divider is 1px; **the grab target must be ~12px**, or the resize feels stuck.
**Clamp every drag between a min and a max** so a panel can never collapse into something you
cannot reopen — limits are the feature. Near the edge, **snap fully closed** instead of leaving a
sliver; halfway states read as bugs. While dragging, **drop an invisible overlay over the whole
page**, or an iframe or a text selection eats the mouse and the panel freezes mid-drag. Set the
resize cursor on `body`, not just the handle, so it does not flicker. **Persist the width across
reloads** — otherwise you throw away the layout the user set by hand.

### Settings page
Most of it is harmless; the bottom deletes everything. **Match the interaction model to the blast
radius**: toggles apply instantly, identity fields get a save bar and cancel. **Group by task**
(payments / billing / team), hide advanced behind one click — 40 settings in a list is a phone
book. **Power users search, they never scroll** — one input finds any setting three levels deep,
highlighting the match and showing its path. **Mark every changed setting** with a dot and a
reset (VS Code's coloured bar); people experiment when undo is one click away. Destructive
actions live in quarantine: red border, bottom of the page, type the name to arm the button.

---

## Gestures & direct manipulation

### Hover does not exist on touch
Touch has no hover, so the browser fakes one: the first tap becomes a hover and the revealed
actions **freeze there** until the user taps elsewhere. Guard with `@media (hover: hover)` — a
media query, not a device sniff, so a tablet with a mouse still gets the full treatment; pair
with `(pointer: coarse)` when targets need to grow. **Anything hidden behind hover is gone on
mobile** — move those actions into the card, a swipe, or a bottom sheet. Hover reveals extras,
**never the primary action.** Tap targets need 44px: pad the hit area, keep the icon small.

### Swipe actions
Two thresholds: a short pull **reveals buttons** (a pause, a choice); past the commit line the
action **fires on release**. The row resists like a rubber band; at the commit point the icon
pops, the resistance dies, and a haptic beat fires. **Direction is a language** — right for safe
(archive), left for destructive. Swap the sides and muscle memory deletes the wrong email.
Gestures are invisible, so **peek the first row on first launch** — buttons half-revealed, then
settling. A full swipe deletes in one motion, and that speed only works with a net: a 5s undo toast.

### Pull to refresh
Fires **past a threshold, never before** — release above the line and the list snaps back with no
reload. Drag should **resist**, as if the content had weight; a 1:1 drag feels cheap. At the
threshold the stretch indicator **hands off to the spinner** — the gesture becomes the loader.
One short haptic **at the threshold**, before the finger even lifts, so the hand knows it caught.
Overshoot and settle; a hard stop feels broken. **Don't lock the scroll while reloading** — frozen
content feels dead.

### Drag and drop — files
The drop zone must **answer on drag-over**: border, glow, copy shift — three signals before the
drop. **Honest progress**: percent and time remaining, not a spinner, so the user can decide to
wait or walk away. When an upload dies at 90%, **inline retry that keeps the file loaded** — never
restart. Show a thumbnail, type and size as proof the right file arrived. Ten files: **each gets
its own progress and its own retry**, and one failure never blocks the other nine.

### Drag and drop — boards and canvases
Three signals that you are holding something: cursor changes, card lifts, background fades.
**Drop zones speak first** — an insertion line for a list, a fill highlight for a zone; no preview
means a blind drop. **Snap for structured lists, free placement for a canvas** — pick the wrong
one and users fight the UI. On a bad drop, a toast: "Moved to Done — Undo", 5 seconds.

---

## Systems that span a screen

### Destructive actions
- **Hold to delete** — a 300ms progress ring *is* the confirmation. Release early and nothing
  fires. Nobody reads "Are you sure?".
- **Name the verb** — "Delete project", not "Yes". The verb is the warning.
- **Geography is friction** — never put a destructive button where the primary sits; muscle
  memory clicks primary spots blind.
- **Red is a budget** — spend it on destruction only. A red logout button cries wolf and makes
  delete look routine.
- **Danger zone** — bordered, labelled, last on the page (GitHub-style).
- **Type the name to arm it** for the truly irreversible. Earn the irreversible.
- **Cooldown** — schedule the deletion with an N-day cancel window. Time is the last defence.

### Undo instead of confirm
"Are you sure?" punishes everyone for one person's mistake; undo punishes nobody. The action
happens instantly and regret gets a second chance:
- The item leaves the **screen**, not the database — a deleted flag, 30 days in trash. **Deletion
  is a state, not an event.**
- One undo is a toast; **a stack is a time machine** — ⌘Z walks back step by step.
- Gmail's send delay is the same idea: the 10-second hold **is** the feature. It catches the typo,
  the wrong recipient, the reply-all.
- Reserve friction for what genuinely cannot be undone.

### Autosave
Nothing saves on every keystroke: a **debounce timer** starts on pause, resets on type — ~800ms
of silence, then one clean write. **The status pill is a state machine** — typing / saving /
saved / offline / error — and users trust it more than the feature, so it must never lie.
**Offline, every edit joins a local queue** with a badge counting what is waiting; on reconnect it
drains oldest-first. Two tabs on one document: **merge or warn, never overwrite in silence** —
last-write-wins makes somebody's hour disappear. On close with unsaved work, block the tab and
ask; one ugly dialog beats an afternoon retyped.

### Multiplayer / presence
The server sends ~10 cursor positions a second and the screen draws 60 — **interpolate**, or
cursors teleport. **Hash the colour from the user ID** so the same person is the same colour in
every session — identity you can track from the corner of your eye. **Stack avatars** before
anyone speaks: three faces then "+5", so you feel the room before reading a name. When someone
grabs an object it **glows in their colour and locks** — two people editing one shape is a
corrupted shape, and the lock prevents the conflict rather than resolving it. Click an avatar to
**follow their viewport** — their pans and zooms, live; a design review without a screen share.
