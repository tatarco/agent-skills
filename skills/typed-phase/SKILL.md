---
name: typed-phase
description: Turn a vague project scope into typed phases - what goes in, what comes out, what "done" looks like, who signs off and by when, what triggers payment, and what is explicitly excluded. Use when scoping freelance or contract work, breaking a project into milestones, writing a statement of work, defining acceptance criteria, or when a project has no written definition of done. Flags every field the client has not given you enough information to fill, instead of inventing it.
---

# typed-phase

A phase in a project is a function.

| In code | In the deal |
|---|---|
| the signature | what goes in, and what has to be done with it. The scope. |
| the return value | what "done" looks like. |
| the test | the acceptance criterion. Written **before** the work, approved by the client. |
| the PR | the payment milestone. It does not land until it is green. |
| a change request | a new ticket. Not a free fix to a function that is already open. |

A phase without that signature is a function without types. The client passes in
whatever they want and you are obliged to return something. That is not a bad
client, it is a bad signature - and it is what people are describing when they
complain about scope creep.

This skill types the phases. It does not price them.

## What this skill does

Input: a requirements doc, a spec, a thread of client messages, or a rough
verbal scope. Any language.

Output: the work sliced into phases, each one typed with the six fields below,
plus an explicit list of everything you could not type yet and the question that
would resolve it.

## The six fields, in this order

Order matters. Payment sits above the acceptance criterion, so that by the time
anyone reads what "done" means they already know what it releases.

```
Phase <n> - <name>

in:            what you receive, in what format, with what limits
out:           what exists at the end that did not exist before
payment:       what this phase releases, and when
done when:     the acceptance criterion, in observable terms
signed off by: a named person, a deadline, and what happens if the deadline passes
not included:  the neighbouring work this phase does NOT cover
```

### in
Format, source and **limits**. "A CSV" is untyped. "A CSV in the agreed format,
up to 50k rows" is typed. The limit is the part that stops the phase from
growing after it starts.

### out
What exists at the end that did not exist before. Nouns, not activities.
"Integration work" is an activity. "Customers in the system plus an error
report" is an artifact.

### payment
What this phase releases. Split it so neither side carries the whole risk -
a deposit up front, the balance on sign-off, is the ordinary shape.

### done when
An observable event, not an adjective. Not "the import works well". Rather:
"your sample file imports, malformed rows are reported and do not kill the run."
Written before the work starts. If you cannot write a sentence that both of you
would read the same way, the phase is not ready to start.

The test is written first. This is the same discipline as writing the test
before the implementation, and it is load-bearing for the same reason: it is
the only version of "done" that was not written by the person who wants the
answer to be yes.

### signed off by
**A named person, a deadline, and a default.** This is the field people leave
out, and it is the one that costs the most.

A phase that is finished but unapproved is a phase you have paid for with your
own time. Name the individual who can approve it - not "the client", not "the
team". Give them a window. Then say what happens when the window passes:

> Dana, within 5 business days. If Dana is unavailable it is approved
> automatically and payment is released.

That last clause is deemed acceptance. It is normal in commercial contracts and
it is the single most useful sentence in this template, because the most common
way a phase stalls is not rejection, it is silence.

### not included
The neighbouring work a reasonable person might assume is in. This field exists
to be read out loud in the kickoff call. It is not a legal shield, it is a
shared expectation - and the things you list here are usually the best
candidates for the next phase.

## Slicing into phases

Everyone already knows how to break work into tickets. On your own invoice it
stops being hygiene and starts being how you get paid.

Cut the work so that each phase:

1. **Delivers something the client can use on its own.** A phase whose value only
   arrives when a later phase lands is not a phase, it is an instalment plan for
   your own risk.
2. **Has the smallest acceptance surface you can manage.** Fewer things to check
   means faster sign-off, and sign-off is what releases payment. A phase that
   takes three weeks to review is worse than two phases that take three days each.
3. **Closes before the next one opens.** Two open phases means neither has a clean
   boundary, and a boundary you cannot point at is the one the client will move.
4. **Keeps you visible.** Shipping something every few weeks buys more trust than
   any status report, and it means you never disappear for a year and reappear
   asking to be paid.

Build the real MVP first - the smallest slice that is genuinely useful, not the
first slice that happens to be easy.

A phase boundary is not a line on a Gantt chart. It is where the risk changes
hands. Before the phase, the unknowns are yours; after sign-off, they are the
client's. Slice where you actually want that handover to happen.

## Never invent a field

If the input does not tell you what the acceptance criterion is, who approves,
or what the input format looks like, **do not guess and do not soften it**. Emit
the phase with the field marked and add the question to an "unresolved" list:

```
Phase 3 - reporting
in:            ??? - which reports, from which data, at what refresh rate?
out:           ...
done when:     ??? - "useful reports" is not observable. What would you check?
signed off by: ??? - who is the named approver, and by when?
```

An unresolved list is a strong deliverable, not a weak one. "I cannot define
done for phase 3 until you tell me who signs it off" is a sentence that protects
both sides. Sending a fully-typed phase built on assumptions is how you end up
delivering something nobody asked for and cannot refuse to pay for either.

## Worked example

```
Phase 2 - customer import

in:            a CSV in the agreed format, up to 50,000 rows
out:           the customers in the system, plus an error report
payment:       30% deposit, balance on delivery
done when:     your sample file imports; malformed rows are reported
               and do not kill the run
signed off by: Dana, within 5 business days. If Dana is unavailable it is
               approved automatically and payment is released.
not included:  data cleaning, deduplication, other formats
```

Hebrew, same phase:

```
שלב 2 - ייבוא לקוחות

נכנס:      קובץ CSV בפורמט שסוכם, עד 50 אלף שורות
יוצא:      הלקוחות במערכת + דוח שגיאות
תשלום:     30% מקדמה, השאר במסירה
גמור כש:   ייבוא של קובץ הדוגמה שלכם עובר, שורות פגומות
           מדווחות ולא מפילות את הריצה
מי מאשר:   דנה, עד 5 ימי עסקים. אם דנה לא זמינה זה מאושר
           אוטומטית ומועבר תשלום.
לא כלול:   ניקוי דאטא, מיזוג כפילויות, פורמטים אחרים
```

## Change requests

Once a phase is open, a change request is a new ticket. Not a free amendment,
not "while you're in there". The sentence that makes this survivable is agreed
before anything is built:

> Changes to an agreed phase are quoted separately. They do not move the
> current phase's acceptance criterion or its date.

Without it you have no ground to stand on, because there is no written record of
what the phase was before the change. With it, saying yes to a change costs the
client something and costs you nothing - which means you can say yes far more
often.

## Out of scope for this skill

Pricing. This skill will not put a number on a phase, pick a rate, or tell you
what your work is worth. Typing the phase and pricing it are different jobs, and
doing them in the same breath is how a scope discussion turns into a discount
discussion.

## License

MIT. Take it, change it, ship it.
