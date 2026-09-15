# Perception & psychology

Why an interface *feels* a certain way before anyone reads a word — and where the line is
between using this and abusing it.

## Laws worth designing around

### Fitts's law
Time to hit a target depends on **distance and size**. So: make important targets bigger, and put
them where the user already is. On mobile, the primary action at the top with the thumb at the
bottom is a tax on every tap; moving it into thumb reach is one of the largest cheap wins
available. The best target is the one already under the cursor — which is why **inline editing,
in-place actions and context menus beat any toolbar**: they reduce distance to zero.

### Serial position effect
Memory is U-shaped: the **first** item benefits from primacy, the **last** from recency, and
items two through eight vanish.
- **Nav bar** — logo first, conversion CTA last; the weakest links go in the middle.
- **Landing page** — strongest value prop first, strongest proof (testimonial, logo wall) last.
  The middle is the skipping zone; don't bury the gold there.
- **Onboarding** — slide one hooks, the last slide pays off, filler in between.

### Zeigarnik effect
Unfinished tasks stay in active memory up to twice as long as completed ones. This is why
onboarding checklists ship with one or two items unchecked — 100% complete and you forget, 80%
and it nags. **The honest version:** use it on outcomes the user actually wants to finish. A
progress bar on a chore is not motivation, it is friction.

### Peak–end rule
The brain does not average an experience; it remembers **the peak moment and the end**. Two
identical 60-second flows, one ending in a confetti beat, rate ~40% higher in memory. So design
**one intentional peak** — the aha when the filters click, a delivery date that beats
expectation. One delight beats five neutral interactions. It cuts both ways: a perfect onboarding
that ends in a payment error is remembered only as the error.

### Shape
Sharp corners read as threat (thorns, claws), rounded edges as safe and touchable — the judgment
happens in milliseconds, before cognition. This is why every button, card and toggle rounded over
the last decade. Use radius deliberately (see `foundations.md`), not as a blanket.

### Colour meaning
Red = danger / urgency / act now. Blue = safe / trustworthy / take your time. Green = go /
confirm / success. The same button changes what the user decides purely by hue. Colour is
communication, not decoration — and it must never be the **only** channel carrying a meaning.

## Persuasion that is defensible

Pricing cards, used honestly:
- **Anchoring** — show the higher price first, struck through; the brain does the discount maths.
- **Social proof** — a "Most popular" badge removes doubt about which to choose.
- **Loss framing** — people feel losses more than gains, so frame a discount as what they lose by
  not taking it.

These stay defensible only while the anchor is a real former price, the badge is true, and the
offer is genuine. Fabricate any of the three and it is the next section.

## Dark patterns — recognise them, refuse to ship them

Every one of these works. That is precisely the problem. **Do not build them, and name them when
you see them in a brief.**

- **Confirmshaming** — making the "no" option embarrassing so guilt drives the yes.
- **Hidden costs** — a low headline price with fees piled on at checkout.
- **Roach motel** — one click to sign up, a maze to leave.
- **Variable rewards** — an unpredictable feed, mechanically identical to a slot machine.
- **Streaks and loss aversion** — a 147-day counter kept out of fear of losing it, not desire.
- **Social reciprocity loops** — a like creates an obligation to return one; the cycle never ends.
- **Removing every exit point** — infinite scroll (no end, so no decision), autoplay (no gap in
  which to leave), pull-to-refresh dopamine. Every pixel spent deleting the user's next reason to
  stop.

The same mechanisms have honest uses — a progress bar that helps someone finish something they
came to do, a streak on a habit they chose. **The test is whose goal it serves.** If the pattern
only works because the user cannot see it operating, it is a dark pattern.
