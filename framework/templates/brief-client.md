---
type: brief-client
subject: <Client name>
status: active  # active | paused | wrapped | prospect | dormant
last-updated: YYYY-MM-DD
maintainer: <Name>
purpose: Canonical record for this client — who they are, the relationship history, contacts, engagements, opportunities, and open commitments.
---

# <Client name> — Client Brief

> **Cascade:** If you are an AI tool, read the instance root README, the [Clients](../README.md) container README, and this folder's [README](README.md) first. This brief is the substantive record about the client and our relationship with them — the folder README is the operational front door.
>
> **Use this brief when:** preparing for a meeting, drafting outreach to this client, writing a proposal, recalling history, deciding whether to revisit an opportunity, or briefing a new agent on the relationship.
>
> *(Note: links below assume this brief lives at `Clients/<client>/brief.md`. If you've copied this template elsewhere, fix the paths.)*

## Who they are

> **TODO:** A paragraph or two. What does this client do, what's their business, where do they sit in their market, what's relevant context. Don't reproduce their About page — capture what *we* know about them that matters for working with them.

## Key contacts

| Name | Role | Email | Relationship | Last contact | Brief |
|---|---|---|---|---|---|
| <Name> | <Role> | <email> | <champion / warm / neutral / cool / blocker / alumni> | YYYY-MM-DD | [`Stakeholders/<slug>.md`](Stakeholders/<slug>.md) or `—` |

> **TODO:** One row per contact who has materially shown up in our work with this client. Mark champions and blockers honestly — that's the part that doesn't survive in email threads. Update "Last contact" as conversations happen. When someone leaves the client org, change their Relationship to "alumni" and append "(former)" to their Role — keep the row rather than deleting, because the relationship can still pay off when they resurface elsewhere.
>
> **Brief column:** when a contact is designated a **primary stakeholder**, scaffold a per-person brief at [`Stakeholders/<kebab-name>.md`](Stakeholders/) and link it here. Stakeholder briefs hold the rolling 1:1 history and person-level notes that would otherwise bloat this file. See the [`stakeholder-brief` template](../../<path-to-acos>/framework/templates/stakeholder-brief.md). Contacts who don't warrant a brief use `—` in this column. Only promote someone to a stakeholder brief when they're a decision-maker, a recurring 1:1 partner, or someone whose personal context materially shapes how we operate the engagement.

## Engagement history

Paid work delivered to date.

| Engagement | Dates | Scope | Outcome | Value |
|---|---|---|---|---|
| <Engagement name> | YYYY-MM – YYYY-MM | TODO | TODO | TODO |

> **TODO:** One row per paid engagement. Capture enough that a future person (or agent) can answer "what have we already done for them?" without digging through email or invoices.

## Active opportunities

What we're actively exploring with them now.

> **TODO:** Each item: what the opportunity is, who raised it, current status, next step, and who owns the next step. Move items to "Engagement history" when they convert; drop them with a one-line note if they die.

## Future work / open ideas

A holding pen for things we've discussed or thought about but aren't actively pursuing.

> **TODO:** Keep light. If an idea matures into something real, promote it to "Active opportunities."

## What they care about

Their priorities, decision-making style, what moves them, what stalls them.

> **TODO:** This is the qualitative judgment layer — the stuff you'd tell a colleague before they walked into a meeting. Examples:
>
> - What problems do they reliably get excited about?
> - How do they make buying decisions — fast/slow, top-down/consensus, budget-driven/value-driven?
> - What's the internal political landscape (champions, skeptics, decision-makers)?
> - What have past engagements taught us about how they prefer to work?

## How to communicate with them

Tone, channel preferences, things to avoid.

> **TODO:** What sounds right when writing to this client. Email vs. Slack vs. text. Formal vs. casual. Specific phrasings that have landed (or backfired). Anyone who needs to be cc'd by default.

## Brand & identity

The headline of the client's visual and verbal brand, so any agent producing artifacts for them has enough to act on without descending into `Brand/` for every task. Full kit lives in [`Brand/`](Brand/).

> **TODO:** Populated automatically by the [`client-brand-capture`](../../<path-to-acos>/framework/skills/client-brand-capture/) skill on first run. If the section is missing, run the skill to scaffold it; if values are stale, re-run.

**Visual identity.** *(Primary brand color and one-word descriptor. Body typography. Overall feel in one sentence.)*

**Verbal identity.** *(Tone descriptor sentence. Audience. One or two pattern absences — what the copy avoids.)*

**Use this brand for:** *(All artifacts produced for this client — proposals, scope docs, slides, emails. The substantive tokens and copy samples live in [`Brand/`](Brand/); pending items live in [`Brand/_principal-review.md`](Brand/_principal-review.md) when present.)*

## Engineering defaults

Conventions that apply to **all software built for this client**, unless a specific project explicitly opts out. These extend the company-wide defaults at the instance root (`company-brief.md` → "Engineering defaults"); list only the deltas from the company default — everything else is inherited.

> **TODO:** Populate only when this client has actual overrides on the company defaults — e.g., their own source-repo org, their own preferred deployment environment, a packaging or auth requirement that differs from the company default. If the client inherits everything, leave a one-line note saying so rather than restating the company defaults here.
>
> Example shape for an override bullet (replace with the real ones, or delete):
>
> - **Source repo home: `<client-git-org-url>`.** Overrides the company default; new projects for this client live here.
> - **Permanent deployment target: `<client-environment>`.** Overrides the company default. If the target environment isn't ready yet, note that the project may stay on the company-default deploy host as an interim home until it is.

## Interaction log

Reverse-chronological. Most recent at the top.

### YYYY-MM-DD — <Topic / type of interaction>

> **TODO:** What happened, who was there, what was decided, what's next. Keep entries short and dated. Don't try to capture everything — capture what would matter to a future-you reading this before the next meeting.

## Open commitments / notes for next conversation

Things we owe them, things they owe us, things to raise next time we talk.

> **TODO:** A small running list. Clear items as they're closed. If a commitment turns into an active opportunity, move it up.

## Links

- Folder operating doc: [`README`](README.md)
- Clients index: [`../README.md`](../README.md)
- Instance root: the instance's `README.md` at the top of the tree
- Company brief (how the company sounds): the instance's `company-brief.md`
- Related: TODO (proposals, deliverables, contracts in this folder)
