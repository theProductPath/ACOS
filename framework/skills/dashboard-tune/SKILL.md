---
name: dashboard-tune
description: Review the accumulated Layout notes on the instance dashboard and propose refinements to the dashboard template or instance overlay. Use when the user says "tune the dashboard", "review the dashboard layout", "what should change on the dashboard", or when a slower scheduled trigger fires the tuning pass. Default cadence is monthly; the instance overlay can override.
---

# Dashboard Tune

This skill is the slow companion to `dashboard-refresh`. Where `dashboard-refresh` re-rolls the current state every morning, `dashboard-tune` runs less frequently and asks a different question: is the dashboard still showing the right things?

The dashboard is the most volatile artifact in an ACOS instance, and even well-designed sections decay. Some go stale because they don't reflect new realities; others go stale because the principal stops looking at them. This skill notices both and proposes changes — never makes them automatically.

> **Status:** stub. The convention, interface, and decision rules are defined here. The runtime implementation is deferred until at least one instance has accumulated enough Layout notes to validate the approach. Don't run this skill against an instance before it has at least a month of dashboard history.

## When this skill triggers

- A user says "tune the dashboard", "review the dashboard layout", "what's not earning its slot on the dashboard", or asks for a layout retrospective.
- A scheduled trigger fires the tuning pass — default cadence monthly, overlay-overridable.
- After a meaningful change in the business (a new offering, a closed client, a new operating mode) that suggests the dashboard's section list may need to follow.

## Instance overlay discovery

Same convention as every other ACOS skill:

1. Find the instance root — the folder containing `company-brief.md`.
2. Look for `<instance-root>/overlays/dashboard-tune.md`.
3. If present, load it. The overlay may specify: a different cadence, sections the instance considers pinned (never propose changes to), promotion routing (when a tPP-specific section pattern proves general enough to push into the framework template), and any human approval requirements before changes land.
4. If absent, proceed with framework defaults.

## Inputs

The skill reads:

1. The current `<instance-root>/dashboard.md`, including its frontmatter and Layout notes section.
2. The previous N versions of the dashboard if the instance keeps a history (e.g., in `_progress/` or a git log). The framework default is to compare against the dashboard from 30 days ago.
3. The instance overlay for `dashboard-refresh`, to see which sections are pinned, which sections are sourced from external data, and which the overlay has already customized.
4. The framework `dashboard-company` template, to see which sections are baseline vs. instance-added.

## What the skill does

The tuning pass runs three diagnostics, each producing a proposal — not a change. The principal reviews and approves.

### Diagnostic 1 — earned slot review

For each section in the current dashboard, judge whether the section has *earned its slot* over the review window. The earned-slot rule:

> A block earns its slot by being looked at *and acted on*. Blocks that aren't acted on for N consecutive refreshes get flagged for removal.

Signals that a section is earning its slot include: items added or removed across refreshes, Layout notes referencing the section, and any explicit principal commentary in the at-a-glance narrative. Signals that a section is *not* earning its slot include: identical content across many refreshes, no Layout notes mentioning it, and no indication anywhere else in the instance that the section's contents drove a decision.

Output: a list of sections grouped by status (earning, marginal, candidate for removal), with the evidence for each.

### Diagnostic 2 — layout notes synthesis

Read the Layout notes journal. Group entries by theme. Themes that recur (the same kind of complaint or suggestion appearing more than once) become candidate proposals. Themes that appear once and don't recur are surfaced separately as "one-off observations" that the principal can consider but the skill doesn't push on.

Output: a synthesized list of proposed layout changes, each linked back to the originating Layout notes that motivated it.

### Diagnostic 3 — promotion check

For each section that the instance has customized via overlay (added, replaced, or reshaped from the framework template), assess whether the customization is mature and general enough to *promote* to the framework template itself. The promotion criteria, per `docs/extending-acos.md`:

- The section has been stable in the overlay for at least 60 days.
- The principal can articulate the section's purpose in a sentence that doesn't reference any company-specific concept.
- The shape of the section is plausibly useful to a hypothetical other company.

Output: a list of overlay sections that meet (or come close to meeting) the promotion bar, with the suggested framework template language for each.

## Output

The skill produces a structured proposal report with this shape:

```
# Dashboard tune — <instance name>

Review window: <start date> to <end date>
Refreshes in window: <count>

## Sections earning their slot
- <Section name> — <one-line evidence>

## Sections at the margin
- <Section name> — <one-line evidence>; recommendation: <keep / reshape / remove>

## Candidate removals
- <Section name> — <one-line evidence>; recommendation: <remove / replace with X>

## Proposals from Layout notes
- <Theme> — supported by <count> notes; recommendation: <change>

## Promotion candidates
- <Section> — overlay customization is mature; suggested framework template language: <draft>

## Approval needed
- <Proposed change> — apply now? [yes / no / discuss]
```

The skill never modifies the dashboard, the template, or the overlay directly. Every change requires explicit principal approval. The overlay may declare that some categories of change (e.g., promoting overlay sections to the framework) require a higher level of approval than others.

## Default cadence

Monthly by default. The first day of the calendar month, after the morning refresh has run. The overlay may shift to a different cadence — quarterly is reasonable for instances where the dashboard is stable, biweekly for instances in heavy build-out.

## Companion plugins

This skill is markdown-only and has no required companions. Optional companions:

- **Version history.** When the host environment provides previous versions of `dashboard.md` (a git log, a `_progress/` snapshot trail, a periodic backup), the skill can compare across time and produce richer earned-slot evidence. Without history, the skill operates on the current state and Layout notes only.
- **The `acos-integrity` skill.** When integrity output is available, promotion candidates can be checked for framework-cleanliness (no instance-specific names, dates, paths) before being proposed.

## Instance overlay configuration

An overlay at `<instance-root>/overlays/dashboard-tune.md` may specify:

- **Cadence override** — a non-default schedule.
- **Pinned sections** — sections the skill should never propose changes to (typically: brand-required blocks, principal-voiced narrative).
- **Approval routing** — who approves what category of proposal (e.g., overlay changes are auto-applied with a notification; framework promotions require explicit principal approval).
- **Review window** — override the default 30-day comparison window.
- **Promotion criteria** — instance-specific additions to the framework's promotion criteria (e.g., "do not propose promotion of any section that references AIRS").

## Links

- Framework README: [`../../README.md`](../../README.md)
- Dashboard template: [`../../templates/dashboard-company.md`](../../templates/dashboard-company.md)
- Companion skill (daily cadence): [`../dashboard-refresh/SKILL.md`](../dashboard-refresh/SKILL.md)
- Extending ACOS (promotion path): [`../../../docs/extending-acos.md`](../../../docs/extending-acos.md)

## Future enhancements

Listed as placeholders, not implementation requirements.

### Placeholder A — automated layout experiments

When an instance accumulates enough history, the skill could propose temporary A/B-style experiments: try a new section shape for one month, compare engagement (Layout notes activity, refresh hand-edits) against the baseline, and recommend keeping or reverting.

### Placeholder B — cross-instance learning

If ACOS one day hosts multiple instances and a privacy-respecting telemetry channel exists, the skill could surface "patterns adopted by N+ instances" as candidates for framework promotion. Out of scope until ACOS has more than its reference instance.

### Placeholder C — Layout notes templating

Encourage Layout notes that are easier to synthesize by offering a lightweight template (e.g., `YYYY-MM-DD section:<name> verdict:<keep|reshape|remove> reason:<text>`). Skill could parse structured notes more reliably than free-form prose.
