---
type: dashboard-company
subject: <Company name>
status: skeleton  # skeleton | drafting | active | stale
last-updated: YYYY-MM-DD
last-refreshed: YYYY-MM-DD HH:MM <timezone>
maintainer: <Name>
purpose: Singleton company dashboard — the morning-glance state record for what the company is doing right now. Companion to company-brief.md (who the company is); the dashboard answers what it's doing this week.
---

# <Company name> — Dashboard

> **Cascade:** Read the instance root README first if you haven't. This dashboard is a *state record* — it decays. The brief is stable; the dashboard is volatile. Treat anything older than the `last-refreshed` timestamp above as possibly stale, and reconcile against the underlying briefs and READMEs when accuracy matters.
>
> *(Note: this template assumes the dashboard lives at the instance root as `dashboard.md`. If you've copied it elsewhere, fix the paths in the Links section.)*
>
> **Use this dashboard when:** starting a working session and needing to know what's live, briefing an agent picking up a task with no context, or scanning for what's about to slip.

## At a glance

> **TODO:** One to three sentences. What week or phase the company is in, the single biggest live thing, and any condition that should colour the rest of the day's work (e.g., "two proposals out, one client renewal under review, AIRS launch slipped to next week"). Hand-edited by the principal at the top of the day, or rolled up by the dashboard-refresh skill from the most recent open commitments. Keep it short — this is the line a fresh agent reads first.

## Active clients

> **TODO:** Clients currently in flight. Sourced from each `Clients/<client>/brief.md` — pull clients whose brief status is `active` and whose engagement state is not `dormant` or `wrapping`. Sort by recency of last touch. Each client may have multiple concurrent workstreams; list them as a multi-line cell rather than collapsing to one phrase. Include each workstream's immediate next move so the table is actionable per workstream, not just per client.

| Client | Current workstreams | Last touch |
|---|---|---|
| <client name> | • <workstream A> — <next move><br>• <workstream B> — <next move> | YYYY-MM-DD |

## Pipeline

> **TODO:** Future workstreams within active clients — known, named, and reasonably probable next pieces of work that haven't started yet. This is the predictable side of future revenue: work queued behind current workstreams with people who already buy. Sourced from each active client's "Pipeline opportunities" or "Future work" sections in their brief. Distinguish from "Leads" below (new prospects who aren't clients yet).
>
> Order by expected start date or by estimated value, whichever the principal finds more useful at 6am. The instance overlay may declare the preference.

| Workstream | Client | Stage | Next move | Last touch |
|---|---|---|---|---|
| <workstream name> | <client name> | <exploring / proposed / negotiating / awaiting decision> | <next action> | YYYY-MM-DD |

## Leads

> **Optional — populate only if the instance has a prospect tracker.** New prospects: organizations not yet clients but in active conversation. Sourced from a dedicated prospect tracker if one exists; otherwise leave this section empty. Leads are less predictable than pipeline (workstreams within active clients) and the dashboard treats them separately so the principal can scan each pool independently.

| Lead | Source | Stage | Next move | Last contact |
|---|---|---|---|---|
| <prospect name> | <referral / inbound / outbound / event> | <discovery / proposal / negotiation / cold> | <next action> | YYYY-MM-DD |

## Projects in flight

> **TODO:** Internal initiatives the company is currently moving on — *not* client work, *not* shipped products. Sourced from each `Projects/<project>/README.md` whose status is `active`. Include a one-line "what's next" so a glance tells the principal whether anything is blocked.

| Project | Phase | What's next | Blocked? |
|---|---|---|---|
| <project name> | <discovery / build / rollout / wind-down> | <next action> | <Yes / No — reason if yes> |

## Products in flight

> **TODO:** Products the company is actively building, shipping, or supporting. Sourced from each `Products/<product>/README.md` whose status is `active` or `drafting`. Distinguish "actively building" from "shipped and supported" if the instance has both.

| Product | State | Current focus | Next milestone |
|---|---|---|---|
| <product name> | <building / shipped-supported / drafting> | <one phrase> | <next deliverable + date> |

## Open commitments

> **TODO:** Things the principal has promised — to clients, prospects, partners, or themselves. Rolled up from briefs' "Open commitments" or "Interaction log" sections, filtered to commitments the principal owns (inbound commitments — things others owe the principal — are surfaced separately or omitted; see the refresh skill for the filtering convention). Sort by due date ascending where dates exist; undated items follow. A commitment that's slipped past its date moves to the top and gets flagged.
>
> The `Due (if known)` column may be blank when the source doesn't attach a date — the dashboard does not fabricate dates. Instances that want stricter date enforcement can layer in a dedicated commitment-tracking skill that augments this section.

| Commitment | To whom | Due (if known) | Source |
|---|---|---|---|
| <one line> | <name> | YYYY-MM-DD or blank | <brief path or "verbal"> |

## This week

> **TODO:** Calendar and time-bound items for the next seven days — meetings, deadlines, travel, scheduled deliverables. In a markdown-only context, this is hand-maintained or pulled from a calendar export. In a rendered view (e.g., a Cowork artifact) the calendar is pulled live and this block is dynamic.

- <day> — <event or deliverable>
- <day> — <event or deliverable>

## Operations

> **TODO:** Optional. This slot is reserved for the operational and financial state of the company once those data sources are wired in: client hours, invoices outstanding, payments due, runway, capacity, retainer utilization. Leave empty until your instance has a source of truth for these. When you fill it in, declare the data source in your instance overlay so the dashboard-refresh skill knows where to pull from.

> *Examples of what this section might eventually carry:*
>
> - **Hours**: utilization this month, capacity remaining.
> - **Invoicing**: invoiced this month, outstanding receivables aged.
> - **Payments**: due this week, recently received.
> - **Runway / cashflow**: current position, burn or accrual trend.

## System health

> **TODO:** Signals about the instance itself, not the business. Rolled up from the `acos-integrity` skill if it's installed: stale READMEs, missing briefs, orphaned overlays, broken cross-references. Skip this section entirely if the instance is small enough that integrity issues are visible by inspection.

- <signal> — <one line>
- <signal> — <one line>

## Layout notes

> **Journal — not a section.** In-the-moment reactions to the dashboard's layout: what was useful, what was noise, what's missing, what should move. The `dashboard-tune` skill reads accumulated notes here on a slower cadence and proposes template or overlay changes. Captures are short and dated.

- YYYY-MM-DD — <one-line note from the principal or an agent>
- YYYY-MM-DD — <one-line note>

## Links

- Instance root: [README](README.md)
- Company brief: [company-brief.md](company-brief.md)
- Refresh skill: `<path-to-acos>/framework/skills/dashboard-refresh/SKILL.md`
- Tuning skill: `<path-to-acos>/framework/skills/dashboard-tune/SKILL.md`
- Brand asset library (if present): `../Brand/README.md`

## How this dashboard stays current

The `dashboard-refresh` skill re-rolls this file on a cadence — daily 6am local by default, overridable by the instance overlay. Hand-edits between refreshes are preserved within section boundaries; the skill never overwrites the "At a glance" narrative or the "Layout notes" journal without explicit instruction.

The markdown source you're reading is the canonical state of the company. Any rendered view of this dashboard (a Cowork HTML artifact, an exported PDF, a printed snapshot) is a presentation layer over this content and must apply the instance's brand tokens per the framework house rule.
