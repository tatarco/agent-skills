# Motion — timing, feedback, and the loading system

Motion is not decoration. It is how the interface answers you.

## The timing table (memorise this)

| Kind | Duration | Easing |
|---|---|---|
| **Feedback** — press, hover, toggle | **< 100ms** | ease-out |
| **Exits** — modal close, panel dismiss | **150–200ms** | ease-in (snappier; the user already decided) |
| **Entrances** — page transitions, modals, panels | **200–300ms** | ease-out |
| **Attention** — error shake, notification | **500–800ms** | with bounce |
| **List stagger** | **50ms per item** | not 30, not 100 |
| **Dropdown / tooltip open** | **< 150ms** | ease-out |

Faster than the range feels broken; slower feels heavy. Nothing interactive goes past ~300ms.

## The three things that make a button feel designed

1. **Easing.** Linear is robotic; ease-out feels alive. This is the single biggest difference
   between a cheap-feeling app and an expensive one.
2. **Feedback.** Silence equals anxiety. On tap, something must change *on the tap* — not when
   the network answers.
3. **Anticipation.** A squash before the bounce. Disney worked this out in 1937.

Applied to a button: **hover** — scale ~1.05, deepen the shadow, a subtle edge glow.
**Press** — scale down slightly, shift the shadow inward, so it reads as a physical press.
**Release** — a ripple from the click point, spring ease-out, never linear.

Every animation needs a `prefers-reduced-motion` alternative, and "none at all" is rarely it.

## Loading is a system — stop using skeletons for everything

| Situation | Use |
|---|---|
| Under **300ms** | **Nothing.** A flash of loading state reads as a bug. |
| Short, unknown duration, < 3s | Spinner. Never for a full page. |
| You know the *shape* (cards, lists, articles) and it's > 300ms | **Skeleton** matching the final layout |
| You know the *percentage*, > 3s (uploads, installs) | Progress bar with percent **and** time left |
| Mutation that succeeds ~99% of the time (like, save, rename) | **Optimistic UI** |

A skeleton whose layout does not match the loaded content causes a jump that reads as breakage.

## Perceived performance

- Anything under **400ms** reads as instant. Past that, a spinner reads as broken even when it
  is working correctly.
- **Progress-bar psychology:** start fast, slow at the end. Identical duration, remembered as
  faster.
- You are not buying speed, you are buying the feeling of it — but see the exception below.

## Optimistic UI

Update the screen first, send the request second, reconcile when the server answers. On failure,
**roll back visibly** — the like un-likes, the count returns. Optimistic is not ignoring errors;
it is betting on the happy path and being honest when the bet loses.

**Never optimistic:** payments, transfers, anything irreversible. Those earn a real spinner and
the truth. Money is not optimistic.

## What actually happens behind a click (why the split matters)

1. Client validates — no network yet; instant feedback is a frontend job.
2. Request leaves with payload, headers, auth token.
3. **Server validates everything again** — client input is never trusted.
4. Business logic: stock, price, charge.
5. Database write, one transaction, all rows commit or none.
6. Response returns; the UI repaints with **server truth, not a guess**.

Steps 1 and 6 are the two places the interface can lie. Optimistic UI moves the repaint before
step 6 — legitimate for a rename, dishonest for a payment.

## Motion that carries information

- A tab underline **slides**, it never teleports. Content cross-fades: fade out, 80ms pause, fade
  in, matched height so nothing shifts.
- A toggle **morphs** — rail colour, knob slide, knob shadow and label cross-fade all in 250ms
  ease-out. A snap reads as a fake button.
- Stars fill **left to right, 30ms apart**. All at once feels dead.
- Toast stacking uses spring physics — damping ~20, stiffness ~180.
- Rubber-band overshoot on a pull; a hard stop feels broken.
