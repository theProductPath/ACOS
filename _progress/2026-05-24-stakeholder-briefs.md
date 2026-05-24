---
type: progress-checkpoint
subject: stakeholder-briefs
status: complete
last-updated: 2026-05-24
maintainer: Steven Jones
purpose: Checkpoint for the stakeholder-brief pattern — a new per-person asset category that sits alongside the client brief, plus the routing rules that split transcript content between the two. Captures what was added and why so future contributors understand the dual-target shape of the client-brief-processor skill.
---

# Stakeholder-brief pattern — checkpoint

## What was added to ACOS

This change introduces the **stakeholder brief** as a new per-person asset category nested inside each client folder. Where the client brief is canonical for the organization and the relationship overall, the stakeholder brief is canonical for one person — their priorities, communication patterns, and rolling 1:1 interaction history. Together they let an instance track conversations with specific stakeholders without bloating the client brief.

Files added:

- `framework/templates/stakeholder-brief.md` — per-person template with frontmatter (`type: brief-stakeholder`, status that includes `alumni`, parent client pointer) and seven body sections: Who they are, Role & relationship, What they care about, How to communicate with them, Personal context, Open threads / things to raise, Interaction log. The cascade note codifies the routing rule (org → client brief, person → stakeholder brief).

Files edited:

- `framework/templates/brief-client.md` — Key contacts table gained a **Brief** column linking to `Stakeholders/<kebab-name>.md` when a contact is designated a primary stakeholder. New guidance prose explains the threshold ("decision-maker, recurring 1:1 partner, or someone whose personal context materially shapes how we operate the engagement"). The `Stakeholders/` subfolder is referenced as the conventional location.
- `framework/skills/client-brief-processor/SKILL.md` — extended with dual-target routing. Extraction category #7 ("Stakeholder-scoped signal") was added. A new "Output: updating stakeholder briefs" section codifies the routing rule, the steps for updating an existing stakeholder brief, the steps for creating a new one, and the alumni transition. The Reference files list now includes the stakeholder-brief template.
- `framework/skills/client-brief-processor/references/brief-sections.md` — the extraction-to-section mapping table was reshaped to include a Target column, with separate rows for org-level vs person-level versions of Interaction log, Commitments, What-they-care-about, and Communication preferences. New "Routing tie-breakers" subsection handles ambiguous cases. New "Stakeholder briefs" section at the end explains the pattern and the "only primary stakeholders get a brief" rule.

Earlier in the same session, an unrelated but adjacent change had already added `alumni` to the relationship enum in `brief-client.md` and to the canonical list in `brief-sections.md`. The stakeholder-brief template mirrors that — `alumni` is a valid frontmatter `status` value, and the SKILL's alumni-transition section handles the state change uniformly across both files.

## Decisions captured

- **Per-stakeholder briefs are a subset, not a superset, of Key contacts.** Only primary stakeholders get a per-person brief. Everyone else stays in the Key contacts table without a per-person file. The threshold is explicit designation by the instance maintainer — not automatic on first 1:1, not automatic for any C-level contact.
- **Folder convention is `Stakeholders/` inside each client folder.** Chosen over `Contacts/` (which implied every contact gets a brief) and `People/` (which lost the stakeholder framing the pattern was named for).
- **Routing rule is "who is the content about?"** Content about the client organization (engagement scope, opportunities, org-level commitments) lands in the client brief. Content about one specific person (their priorities, their decision style, what they said in a 1:1) lands in their stakeholder brief. The client-brief interaction log still records the meeting at an org level; the stakeholder brief captures the person-level texture.
- **Duplication is minimized but allowed.** When a signal is genuinely both (e.g., an executive's personal priority that *is* effectively the company's priority), the substantive note goes in the client brief and the stakeholder brief gets a short pointer ("See client brief: What they care about"). Don't fan the same paragraph into both.
- **Alumni state propagates uniformly.** When a primary stakeholder leaves the client org, the stakeholder brief frontmatter flips to `status: alumni`, the Key contacts row mirrors with Relationship → `alumni` and Role → `(former)` suffix, and the SKILL stops routing new transcript content to that brief by default. Existing history stays — the brief becomes a frozen record.
- **The pattern is framework-level, not instance-specific.** Although tPPOS drove the need, the addition was made directly in ACOS rather than as a tPP customization. Any future ACOS instance gets the pattern out of the box. The tPP-specific reasoning lives in [`tPPOS/decisions/0008-stakeholder-briefs.md`](../../../tPPOS/decisions/0008-stakeholder-briefs.md).

## What was deliberately *not* done

- **No automatic stakeholder-brief creation on first 1:1.** The threshold is explicit designation. Automatically scaffolding briefs on first contact would proliferate files for people who don't warrant them and would invent designations the instance owner hasn't made.
- **No stakeholder-brief-processor skill.** Stakeholder briefs are updated by the existing `client-brief-processor` skill, which now handles both targets. A second skill would split logic that belongs together — the same transcript usually updates both files in one pass.
- **No CRM integration.** Stakeholder briefs deliberately live in markdown alongside the client brief, not in an external system. A future instance might want to sync to Notion or Salesforce, but that's an overlay concern, not a framework concern.
- **No `Stakeholders/README.md` template at the framework level.** The two instance-level retrofits (HPP, Lock 8) include a `Stakeholders/README.md` modeled on `folder-readme-container.md`, but no dedicated framework template was created. The `Stakeholders/` folder is simple enough that the generic container README pattern suffices; if multiple instances diverge on this README's shape, a dedicated template can be added later.
- **No retroactive sweep across all clients.** The framework change is universal, but instance retrofits are surgical. Only HPP and Lock 8 had primary stakeholders designated and briefs scaffolded in this pass. Other tPP clients (Sprout.ai, Objective Partners, madefor-solutions) keep their Key contacts table as-is until the instance owner promotes someone.

## Future pointers

- **Validate the routing rule against real transcripts.** The SKILL's dual-target routing is specified but unproven at volume. The first few transcripts processed under this rule will surface edge cases — content that doesn't cleanly map to either target, or content the routing decision sends to the wrong place. Adjust `brief-sections.md` as those patterns emerge.
- **Watch file count per client.** A client with many concurrent 1:1s could accumulate enough stakeholder briefs that the `Stakeholders/` folder becomes hard to scan. The README index helps. If a real instance hits 10+ active stakeholder briefs at one client, revisit whether the flat-file shape is still right.
- **Consider a stakeholder-brief integrity check.** Analogous to the existing `acos-integrity` skill: verify that every Key contacts row with a Brief link points at an existing file, that every `Stakeholders/*.md` file has a corresponding Key contacts row, and that frontmatter `status` values align between the two.
- **Promotion candidates within the pattern.** Two adjacent ideas surfaced during the design but were deferred: a "primary stakeholder map" view across all clients (one-glance answer to "who are my decision-makers right now"), and a "stakeholder-1:1 prep" skill that synthesizes the relevant stakeholder brief into pre-meeting context. Both belong at the framework level if they prove useful at any one instance.
