---
name: dashboard-refresh
description: Refresh the instance dashboard at <instance-root>/dashboard.md by rolling up current state from briefs, READMEs, and manifests across the instance. Use when the user says "refresh the dashboard", "update the dashboard", "roll up the dashboard", "state of the company", or when a scheduled trigger fires the refresh. Default cadence is daily at 6am local; the instance overlay can override.
---

# Dashboard Refresh

Re-roll the singleton company dashboard (`<instance-root>/dashboard.md`) from the current state of the instance. The skill reads briefs and READMEs across the tree, extracts the inputs that each dashboard section expects, and writes a fresh version of the dashboard in place. Hand-edited blocks are preserved; rolled-up blocks are replaced.

The markdown dashboard is the canonical state of the company. Any rendered view (a Cowork artifact, an HTML export, a printed snapshot) reads this file as its source of truth.

## When this skill triggers

- A user says "refresh the dashboard", "update the dashboard", "roll up the dashboard", "what's the state of the company", or asks for a morning-glance summary of where things stand.
- A scheduled trigger (the instance's task scheduler, a cron-equivalent) fires the refresh.
- After a significant state change — a new client signed, a project closed, a product launched — when the user wants the dashboard to reflect the new reality before the next scheduled refresh.
- The first time the dashboard is set up in a new instance, run the skill once to populate `dashboard.md` from the template.

## Instance overlay discovery

Before doing anything else, look for an instance overlay:

1. Find the instance root — the folder containing `company-brief.md`. Walk up from the working directory if needed.
2. Look for `<instance-root>/overlays/dashboard-refresh.md`.
3. If present, load it. The overlay may specify: which folders count as in-scope for which section, what `status` values qualify as "active", what counts as "stale", a different cadence than the framework default, the voice rules for the at-a-glance narrative, and routing for the operations section.
4. If absent, proceed with framework defaults. The skill is self-sufficient without an overlay.

## What the skill does

The refresh runs in three passes: read, roll up, write.

### Pass 1 — read

1. Read the instance root `README.md` to get the folder map.
2. Read `company-brief.md` for principal identity and voice context.
3. Walk each in-scope container folder declared by the folder map (typically `Clients/`, `Projects/`, `Products/`), reading their READMEs and the `brief.md` and `README.md` inside each item folder. Skip `_`-prefixed folders per agent-ignore.
4. If the overlay declares additional data sources (e.g., a connector for hours or invoicing), load them.
5. Read the existing `dashboard.md` to preserve hand-edited sections.

### Pass 2 — roll up

For each section of the dashboard, derive the new content from the inputs:

| Section | Source | Rule |
|---|---|---|
| At a glance | Existing dashboard + most recent open commitments | Preserve unless the user explicitly asks to regenerate. This block is principal-voiced and lossy to overwrite. |
| Active clients | `Clients/<client>/brief.md` | Include where `status: active` and engagement is not `dormant` or `wrapping`. Sort by recency of last touch. List concurrent workstreams as a multi-line cell (one workstream per line, each with its next move). Source the workstream list from the brief's "Active opportunities" section. Source last-touch from the most recent dated entry in the brief's "Interaction log". |
| Pipeline | Each active client's brief — "Pipeline opportunities" or "Future work / open ideas" section | Future workstreams within active clients. One row per workstream, grouped or sortable by client. Order by the overlay's preference (expected start date or estimated value); default is by client, then by stage. Drop workstreams marked cold for more than 60 days unless the overlay overrides the threshold. |
| Leads | Overlay-declared prospect tracker only | Optional. Populate only if the overlay names a prospect tracker source (file, folder, connector). When no source is declared, leave the section empty with a one-line note that no tracker is wired in. The dashboard does not infer leads from informal sources. |
| Projects in flight | `Projects/<project>/README.md` | Include where status is `active`. |
| Products in flight | `Products/<product>/README.md` | Include where status is `active` or `drafting`. Companion folders (marketing sites, sibling repos for the same product) may be collapsed under their parent or excluded entirely per the overlay's `companion-folders` map. |
| Open commitments | Each client brief's "Open commitments" or "Interaction log" sections | Filter to commitments the **principal owns** — items the principal has promised to do. When a brief format mixes inbound (others owe the principal) and outbound (principal owes others) in the same list, parse the owner tag (e.g., `* [ ] **<owner>**: <action>`) and include only outbound by default. The overlay may opt into a split view that shows inbound separately. Sort by due date ascending where dates exist; undated items follow in source order. Slipped (past-due) commitments float to the top, flagged. Never fabricate a due date when the source doesn't attach one. |
| This week | Hand-edited by default; overlay may declare a calendar source | Markdown-only refresh leaves this section alone unless the overlay wires it in. |
| Operations | Overlay-declared sources only | If no overlay declares a data source for this slot, leave the placeholder copy in place. Don't fabricate. |
| System health | `acos-integrity` skill output if it ran recently | If the skill hasn't been run in the last 7 days, leave a note saying so rather than reporting stale findings. |
| Layout notes | The existing dashboard, preserved verbatim | Never overwrite. This is a journal owned by the principal. |

### Pass 3 — write

1. Update the `last-refreshed` frontmatter field to the current timestamp in the principal's local timezone.
2. Update `last-updated` only if the content of the body has changed.
3. Write the file back to `<instance-root>/dashboard.md`.
4. If the overlay declares a render destination (e.g., a Cowork artifact to refresh, a PDF to regenerate, an HTML to export), trigger the matching downstream action. Render destinations are companion outputs only — the markdown is canonical.

## Preservation rules

The skill is deliberately conservative about what it overwrites. The default contract:

- **Never overwrite:** the `## At a glance` narrative, the `## Layout notes` journal, and any section whose body has been hand-marked with the comment `<!-- pinned -->` immediately under the heading.
- **Always re-roll:** the structured table sections (active clients, pipeline, projects in flight, products in flight, open commitments).
- **Conditional:** the `## This week` and `## Operations` sections are only re-rolled when the overlay declares a source. Otherwise they're left intact.

If the skill would overwrite a section that has been hand-edited *more recently* than the last refresh timestamp, it pauses and asks the principal whether to keep the hand-edit or accept the re-rolled version. Re-rolls are not destructive by default.

## Default cadence

The framework default is **daily, 6am local time** for the principal declared as primary stakeholder in `company-brief.md`. The cadence is a property of the *instance*, not the skill, and is configured at the scheduler layer (the instance's task scheduler, cron, or equivalent). The framework just declares the default.

The instance overlay can override the cadence — for example, twice-daily, weekly Monday morning, or business-hours-only. When an instance is in early build-out and the dashboard is mostly hand-maintained, weekly is often more honest than daily.

## Companion plugins

This skill works without any companion plugin, producing a markdown file as its sole output. Some optional companions can extend it:

- **A task scheduler** (the host environment's recurring-job mechanism). Without one, the skill runs only when invoked manually.
- **A Cowork artifact, dashboard renderer, or PDF exporter.** When the overlay declares one of these as a render destination, the skill triggers it after writing the markdown. Without one, the markdown is the only output.
- **The `acos-integrity` skill.** When recent integrity output is available, the System health section reflects it. Without it, the System health section degrades to a placeholder note.

A skill that breaks when a companion isn't installed is a framework bug. This skill is designed to degrade gracefully: missing companions reduce coverage but never block the refresh.

## Output

The skill produces:

1. **A refreshed `dashboard.md`** — the primary output, written to `<instance-root>/dashboard.md`.
2. **A diff summary** — a short message in the conversation describing what changed since the last refresh (counts: clients added/dropped, commitments slipped, new pipeline entries). Useful for the principal to skim without re-reading the whole dashboard.
3. **Optional companion outputs** — any render destinations the overlay declared (a Cowork artifact, an exported PDF, etc.).

When invoked by a scheduled trigger, the diff summary may be delivered to a destination declared in the overlay (a message, a channel, an email) rather than inline.

## Instance overlay configuration

An overlay at `<instance-root>/overlays/dashboard-refresh.md` may specify:

- **Cadence override** — a non-default schedule (e.g., `cadence: weekly-monday-07:00-local`).
- **Section sources** — for any section whose default source the instance overrides (e.g., pipeline ordering preference: by start date vs. by value).
- **Leads source** — when the instance has a prospect tracker for new-prospect Leads (separate from within-client Pipeline), declare its location and shape here. When unset, the Leads section stays empty.
- **Pipeline ordering** — `start-date` (default) or `estimated-value`. Controls how the Pipeline section is sorted at the top.
- **Operations data source** — when the instance has wired in hours, invoicing, payments, or runway, declare where to read from.
- **This-week data source** — when the instance has wired in a calendar source, declare where to read from.
- **Active-status criteria** — instance-specific definitions of what counts as "active" for clients, projects, or products.
- **Companion folders** — a map declaring sibling folders that should be **collapsed under** a parent (e.g., `agentcomms-site` collapses under `agentcomms`) or **excluded entirely** from "Products in flight". The framework default treats every folder as first-class; the overlay narrows that.
- **Open commitments direction** — `outbound-only` (default — principal-owed items only) or `split` (separate sub-blocks for outbound and inbound) or `all` (combined). When the brief format mixes both, the overlay's choice controls what gets surfaced.
- **Stale thresholds** — overrides for the 60-day pipeline cold window or any other staleness threshold.
- **Render destinations** — companion outputs the skill should trigger after writing the markdown (e.g., a named Cowork artifact, an exported PDF path).
- **Pinned sections** — sections that should never be touched by the refresh, beyond the framework defaults.
- **Voice rules for the at-a-glance narrative** — pointers to the instance's voice section in `company-brief.md` or a more specific voice doc, used only when the user explicitly asks to regenerate the narrative.

## Brand pre-flight

The markdown output of this skill is content, not a polished artifact, and does not itself require brand pre-flight. However, *every rendered view* this skill triggers downstream — Cowork artifacts, HTML exports, PDFs, printed snapshots — does require brand pre-flight per the framework house rule on instance branding for dashboards. The skill is responsible for ensuring that any render destination it triggers has access to the instance's Brand asset README; it surfaces a warning if the instance declares a render destination but has no Brand asset library.

## Links

- Framework README: [`../../README.md`](../../README.md)
- Dashboard template: [`../../templates/dashboard-company.md`](../../templates/dashboard-company.md)
- Companion skill (slower cadence): [`../dashboard-tune/SKILL.md`](../dashboard-tune/SKILL.md)
- Companion skill (system health input): [`../acos-integrity/SKILL.md`](../acos-integrity/SKILL.md)
- Agent-ignore convention: [`../../agent-ignore.md`](../../agent-ignore.md)
- Extending ACOS: [`../../../docs/extending-acos.md`](../../../docs/extending-acos.md)
