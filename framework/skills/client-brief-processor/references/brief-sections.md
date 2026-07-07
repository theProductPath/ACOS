# Brief sections reference

Detailed guide for each section of the client brief template, plus the canonical mapping from extraction category to brief section. Load this when you need guidance on what good content looks like in a specific section, or when you need to know which extracted item goes where.

## Extraction category → brief section mapping

This is the canonical mapping used by the [`client-brief-processor`](../SKILL.md) skill. The skill points at this file rather than duplicating the table; if section names change in the [brief-client template](../../../templates/brief-client.md) or the [stakeholder-brief template](../../../templates/stakeholder-brief.md), update this mapping and the templates in the same pass.

Two targets exist: the **client brief** (organization-scoped) and a **stakeholder brief** per designated primary stakeholder (person-scoped). The "Target" column says which one each category lands in.

| Extraction category | Target | Section |
|---|---|---|
| New contacts / role changes | Client brief | Key contacts |
| Interaction log entries (org-level — who was there, what was decided organization-wide) | Client brief | Interaction log (newest first) |
| Interaction log entries (person-level — what *this stakeholder* said, did, signaled in 1:1) | Stakeholder brief | Interaction log (newest first) |
| Commitments made (org-level — engagement deliverables, scope items) | Client brief | Open commitments / notes for next conversation |
| Commitments made (person-level — something we owe *this person*, or they owe us) | Stakeholder brief | Open threads / things to raise with them |
| Commitments closed | Move from Open commitments / Open threads, note in the corresponding Interaction log |
| Opportunities surfaced (real) | Client brief | Active opportunities |
| Opportunities surfaced (speculative) | Client brief | Future work / open ideas |
| What the client (institutionally) cares about | Client brief | What they care about |
| What *this person* personally cares about | Stakeholder brief | What they care about |
| Communication preferences (org-level norms — who to cc, channels the team uses) | Client brief | How to communicate with them |
| Communication preferences (person-level — their quirks, channels they read, tone that lands) | Stakeholder brief | How to communicate with them |
| Personal context (family, hobbies, background — surfaced organically) | Stakeholder brief | Personal context |

### Routing tie-breakers

When the same signal could plausibly land on either target:

- **Default to the client brief** for anything the user might want to find again without remembering whose meeting it came from.
- **Default to the stakeholder brief** for anything that's only legible in the context of one person's voice or working style.
- **Duplicate sparingly.** If a signal is genuinely both (e.g., an executive's personal priority that *is* effectively the company's priority), put the substantive note in the client brief and add a short pointer in the stakeholder brief like "See client brief: What they care about."

## Who they are

A paragraph or two capturing what *we* know about the client that matters for working with them. Not their About page — the operational context.

**Good:** "<Client> is a mid-market <industry> firm that <core activity>. They have <key stat> and are <current trajectory>. Decision-making is <fast/slow/consensus/top-down>."

**Bad:** "<Client> is a <industry> firm founded in <year> specializing in <generic positioning>." (That's their website copy.)

## Key contacts

One row per contact who has materially shown up in our work. Not everyone in the org — just the people who matter to the relationship.

Columns:

- **Name** — as they introduce themselves
- **Role** — their actual title, or how they function if title is misleading
- **Email** — primary work email
- **Relationship** — one of: champion, warm, neutral, cool, blocker, alumni. Be honest.
- **Last contact** — YYYY-MM-DD of most recent interaction. Update as conversations happen.

**When adding from transcript:** Don't add someone who was just mentioned in passing. Add people who actively participated or were identified as decision-makers/stakeholders.

**Alumni handling:** When a transcript or other signal reveals that a contact has left the client organization, set their Relationship to `alumni` and append "(former)" to their Role rather than deleting the row. The relationship may still have value — they can become a referral, a future buyer at a new company, or context that explains a past engagement. If their warmth toward us was previously tracked (e.g. "Champion"), preserve it as a secondary note like `Alumni / former Champion`. Update "Last contact" only if you've actually re-engaged with them since their departure.

## Engagement history

One row per paid engagement. Enough detail that a future team member can answer "what have we already done for them?"

Columns:

- **Engagement** — name of the engagement
- **Dates** — start and end (month granularity is fine)
- **Scope** — 1-2 sentence description
- **Outcome** — what happened, what was delivered
- **Value** — dollar amount or "TBD" if not disclosed

## Active opportunities

What we're actively exploring. Each item should have:

- What the opportunity is
- Who raised it
- Current status
- Next step
- Who owns the next step

Move items to Engagement history when they convert. Drop them with a one-line note if they die.

## Future work / open ideas

A holding pen. Keep light. If an idea matures, promote it to Active opportunities.

**Good:** "<Contact> mentioned they're thinking about <opportunity> — unclear if real or aspirational."

**Bad:** A detailed 5-paragraph proposal for something that hasn't been scoped.

## What they care about

Qualitative judgment layer. The stuff you'd tell a colleague before they walked into a meeting.

- What problems do they reliably get excited about?
- How do they make buying decisions — fast/slow, top-down/consensus, budget-driven/value-driven?
- What's the internal political landscape (champions, skeptics, decision-makers)?
- What have past engagements taught us about how they prefer to work?

## How to communicate with them

Tone, channel preferences, things to avoid.

- Email vs. Slack vs. text
- Formal vs. casual
- Specific phrasings that have landed (or backfired)
- Anyone who needs to be cc'd by default

## Interaction log

Reverse-chronological. Most recent at the top. Each entry:

```
### YYYY-MM-DD — Topic / type

What happened, who was there, what was decided, what's next. 2-4 sentences.
```

Don't try to capture everything. Capture what would matter to a future-you reading this before the next meeting.

## Open commitments / notes for next conversation

A small running list. Clear items as they're closed. If a commitment turns into an active opportunity, move it up.

Format:

- **We owe them:** [description] → [status]
- **They owe us:** [description] → [status]
- **Raise next time:** [topic to bring up]

## Stakeholder briefs

When a contact is designated a **primary stakeholder**, they get a per-person brief at `Clients/<client>/Stakeholders/<kebab-name>.md` based on the [stakeholder-brief template](../../../templates/stakeholder-brief.md). Stakeholder briefs hold the person-scoped material that would otherwise bloat the client brief: rolling 1:1 history, personal priorities, communication quirks, open threads with that individual.

The routing table above governs which content lands where. Two notes:

1. **Only primary stakeholders get a brief.** Not every Key contact warrants one. The user (or an agent on their instruction) flags someone as a primary stakeholder; everyone else stays in the Key contacts table without a per-person file.
2. **The client-brief interaction log still records meetings at the org level.** When a transcript is processed for a meeting that included a primary stakeholder, the high-level entry (date, who, what was decided org-wide) goes in the client brief. The person-level texture (what they said, how they reacted, side comments) goes in their stakeholder brief.
