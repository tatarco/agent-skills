# The lenses

Run each as its own agent. The point is not thoroughness per agent — it is
**independence**. Ten reviewers who cannot see each other's notes will
converge on the real defects and diverge on taste, and that difference is the
signal you are actually buying.

Drop any lens that does not exist on the machine. Do not substitute.

| Skill | What it reliably catches | Model |
|---|---|---|
| the project's own FE skill (e.g. `fe-gal`) | house rules, and the things the owner has already complained about twice | sonnet |
| `fe-design-taste` | AI-slop tells, dial calibration, breakpoint sprawl | sonnet |
| `fe-high-end-visual` | craft ceiling, materiality, spatial rhythm, signature moments | sonnet |
| `impeccable` (`critique <target>`) | heuristic scoring, banned patterns, z-index and token discipline | sonnet |
| `fe-web-guidelines` | a11y: focus traps, scroll lock, inert, landmarks, contrast | sonnet |
| `fe-animations` + `web-perf` | easing, durations, layout-animating properties, image weight, LCP | sonnet |
| `frontend-design:frontend-design` | aesthetic point of view — is it committed, is it memorable | sonnet |
| `fe-design-interface` | information architecture and per-audience user journeys | sonnet |
| `minimalist-ui` + `fe-brutalist-ui` | what to cut, and where the design is too polite for the subject | sonnet |
| `fe-redesign-existing` + `qa` | hard QA: link crawl, EN/HE parity, schema, sitemap, dead CSS | sonnet |

## Prompt shape for each agent

Every agent gets: the skill to invoke first, the repo path, the hard
constraints (no framework / no build step / whatever is true), the local
server URL, the screenshot directory, the owner's complaint in their own
words, and — critically — **a "do not re-report" list** of everything already
known or already being fixed. Without that list, agents nine and ten spend
their whole budget rediscovering what agent one found.

Ask each for at most 12–15 findings, each with severity, `file:line`, and the
specific fix. Ask them to cite what they measured. Tell the later ones you
want *new* material, not consensus.

## Which lenses disagree, and who to believe

Aesthetic lenses will contradict each other — that is correct and you resolve
it by taste and by what the owner asked for. The a11y and QA lenses make
falsifiable claims; go and falsify them. In practice roughly a quarter of all
findings are wrong, and the wrong ones are stated with exactly the same
confidence as the right ones.
