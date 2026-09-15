---
name: fe-redesign-mobile
description: Restructure a desktop-shaped UI so it actually works on a phone — tables into cards, column triage, one fixed slot per value, progressive disclosure, and container-query breakpoints. Use when a table, data grid, dashboard row, or dense list is being made responsive, when a page "looks broken on mobile", when horizontal scroll or shrunken text appears on small screens, or when the user asks for a mobile pass / mobile fix / responsive redesign.
---

# Redesign for mobile

**The rule: don't shrink it, restructure it.** Scaling a six-column table down produces a
horizontally-scrolling row where half the data is hidden and the type is unreadable. A phone
needs a different shape for the same data, not a smaller copy of the desktop one.

Apply the six moves in order. They are a sequence, not a menu.

## 1. Triage the columns

Not every column survives, and the survivors are **not the leftmost ones**. Rank each column by:

| Rank | Question | Example |
|---|---|---|
| **Use** | Is this what the user came to find out? | status, amount |
| **Identity** | Does this name the row? | client name |
| **Value** | Is this the number the decision hangs on? | total |
| **State** | Does this change and matter now? | overdue / paid |

**The ID leaves first.** Nobody reads a record ID on a phone. Three of six columns typically
survive; the rest move to disclosure (move 6), not to a horizontal scrollbar.

## 2. Stack the row, never scroll it

Horizontal scroll hides half the row and no one discovers it. Give each row **two lines**:

```
Acme Ltd.                    $1,240.00
Overdue · Due March 4
```

Line 1: identity left, value right. Line 2: state and secondary fields underneath.
The whole row reads as **one unit, thumb-sized** — one tap target, not six cells.

## 3. One fixed slot for the value

Cards kill comparison — that is their cost. On a table the numbers form a column the eye scans;
on cards they drift under names of different lengths and comparison dies.

Fix it: **the amount lives in exactly one slot — top right, every card, no exceptions** —
and uses `font-variant-numeric: tabular-nums` so digits align between cards. A list of cards
should still read as a column of numbers.

## 4. Label only the ambiguous

The header row is gone, so each card carries its own meaning — but do not label everything;
that is how a card becomes a form.

- `March 4` alone means nothing → **`Due March 4`**
- `$1,240.00` needs no label. Currency formatting is the label.
- A status pill needs no label. The word *is* the value.

## 5. Sorting becomes a control

The header row was also the sort UI. Deleting it deletes sorting unless you replace it —
a visible sort/filter control above the list (segmented control, or a sheet for >3 options).
Show the active sort in the control's label; never leave the user unable to reorder.

## 6. Hidden isn't deleted — disclose on tap

Everything cut in move 1 is still reachable. **Tap the row** and it comes back. Pick by volume:

- **1–2 extra fields** → expand in place; the card grows, the list keeps its scroll position.
- **A full record** (ID, notes, actions) → **bottom sheet**, dismissible by swipe.
- **Never a new page for a glance.** A navigation that loses list position and requires a
  back-tap is the wrong weight for "what's the invoice number".

## The breakpoint belongs to the table, not the screen

Do not branch on viewport width. The question is never "is this phone-sized", it is
**"does this table have room"** — six columns need roughly 700px, wherever they are. A desktop
side panel is 400px wide and needs cards exactly like a phone does.

```css
.table-wrap { container-type: inline-size; }

/* default = card list */
@container (min-width: 700px) {
  .table-wrap .cards { display: none; }
  .table-wrap table  { display: table; }
}
```

One container query, one component, correct in a phone, a split view, a side panel, and an
embedded widget. A media query is correct in exactly one of those.

## Checklist

- [ ] Columns ranked by use/identity/value/state; the ID is gone
- [ ] No horizontal scroll anywhere on the small layout
- [ ] Two-line stacked row; identity left, value right
- [ ] Value in one fixed slot, `tabular-nums`, same position on every card
- [ ] Ambiguous fields labelled, self-evident ones not
- [ ] Sort/filter control present and showing its active state
- [ ] Cut fields reachable by tap (expand ≤2 fields, sheet for a record)
- [ ] Breakpoint is a **container** query sized to the content, not a viewport media query
- [ ] Tap targets ≥44px; the row itself is the target

## Beyond tables

The same six moves apply to any dense desktop shape:

- **Dashboard stat grid** → one metric per line, value right-aligned in a fixed slot.
- **Multi-column form** → single column; the second column is almost always optional fields → disclosure.
- **Toolbar of 9 icons** → 2–3 primary actions + an overflow sheet, ranked by use.
- **Sidebar nav** → bottom bar for the top 4, sheet for the rest.

---
*Source: @designmotionhq (Instagram), "Your table doesn't fit a phone" — reel `Dc8RfGzNPCN`.*
