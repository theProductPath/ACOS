---
name: client-brief-processor
description: Extract structured client intelligence from raw input (pasted transcript text, email threads, meeting notes, Slack exports) and update the client brief in an ACOS instance. Use when a user provides a transcript or asks to process client communications, when pulling email threads for a client, or when updating a client brief with new information. Reads an optional instance overlay for company-specific configuration (account names, folder paths, routing rules); the framework skill is self-sufficient without one.
---

# Client Brief Processor

Extract structured intelligence from client communications and update the canonical client brief in an ACOS instance.

## When this skill triggers

- A user pastes a transcript and says "process this" or "update the brief"
- A user asks to pull recent emails for a client and process them
- A user mentions new client information that should be captured
- A user asks to update or refresh a client brief

## Instance overlay discovery

Before doing anything else, look for an instance overlay. The convention:

1. Find the instance root — the folder containing `company-brief.md`. Walk up from the working directory if needed.
2. Look for `<instance-root>/overlays/client-brief-processor.md`.
3. If present, load it. The overlay supplies instance-specific configuration: which email account to use, which folder pattern client data follows, routing quirks (subsidiary aliases, business unit mappings), and any instance-specific output preferences.
4. If absent, proceed with framework defaults. The skill is self-sufficient without an overlay; the overlay only adds configuration that isn't generally derivable.

## Client identification

When the user does not explicitly name the client, the skill must identify which client the input belongs to. Use this resolution order:

### Primary: explicit identification

The user tells you which client (e.g., "Process this for Acme" or "Update the Acme brief"). Use this without further lookup.

### Secondary: manifest lookup

If the user does not specify a client, or says something like "process this transcript" without naming the client:

1. Read all `manifest.md` files in the client folders.
2. Scan the input text for matches against:
   - **Company identifiers** — company names, abbreviations, email domains.
   - **Contact identifiers** — people's names and email addresses.
   - **Business unit identifiers** — subsidiary or brand names that route to a parent client.
   - **Project identifiers** — project, product, or initiative names.
3. Score matches: exact company name match > email domain match > contact name match > project keyword match.
4. If one client scores significantly higher than others, use it.
5. If multiple clients score similarly high, treat as a [multi-client signal](#multi-client-signal) (see below) and ask the user.
6. If no client matches, ask the user to confirm.

### Tertiary: brief content matching

If no manifest exists (or manifests are incomplete):

1. Read the `brief.md` in each client folder.
2. Match input text against contact names, company references, and project keywords in the briefs.
3. Use the best match.
4. If ambiguous, ask the user to confirm.

### Fallback: ask the user

If identification fails at all levels, ask: "I couldn't determine which client this belongs to. Which client should I update?"

### Multi-client signal

If two or more clients score similarly high — for example, an email thread that CC'd contacts from two clients, or a meeting comparing two prospects — do **not** silently pick one. Surface the ambiguity:

"This input has signal for both <Client A> and <Client B>. Should I:
(1) update one of the two briefs,
(2) split the content and update both, or
(3) only update one and ignore the rest?"

A brief updated for the wrong client is worse than no update at all. When in doubt, ask.

## Input sources

### Pasted transcript (default)

The user pastes raw transcript text directly into the conversation. This is the simplest path and requires no tool configuration.

1. Receive the pasted text as the input.
2. Identify the client (see [Client identification](#client-identification) above).
3. Proceed to [extraction](#extraction-process).

### Plaud / Audio drop-folder transcripts

When users use Plaud or other ad-hoc transcription devices, they export raw `.txt` or `.md` files to a client's drop-folder.

1. Each client folder should have `Transcripts/New/` and `Transcripts/Archive/` directories.
2. The user drops raw transcripts into `Transcripts/New/`.
3. The skill (often run on a scheduled sweep or requested manually) reads any files in `Transcripts/New/`.
4. Process each transcript according to the [extraction rules](#extraction-process) and update the client and stakeholder briefs.
5. Move the processed file to `Transcripts/Archive/`.

### Email threads (when configured)

Pull email threads for a specific client from a configured email system. Requires the instance overlay to specify email account, search command syntax, and any post-processing rules (e.g., applying a "processed" label after read).

1. The user specifies the client name.
2. Search for relevant email threads using the client's identifiers (company name, domain, contact names) — search command from the overlay.
3. Select relevant threads (recent, substantive — skip newsletters, automated receipts).
4. Read full message bodies and proceed to [extraction](#extraction-process).
5. Apply any post-processing the overlay specifies (e.g., labeling threads as processed).

If no overlay is present and the user asks for email-based input, ask which email system is available and what credentials are configured.

## Extraction process

Regardless of input source, extract these categories from the raw text:

### What to extract

1. **New contacts or role changes** — names, titles, emails, relationship signals (champion, blocker, etc.)
2. **Interaction log entries** — date, topic, who was there, decisions, next steps. Keep each entry short and dated.
3. **Commitments made or closed** — things the user/the team owes them, things they owe us, status updates.
4. **Opportunities surfaced** — potential new work, expansions, referrals. Move to "Active opportunities" if real, "Future work" if speculative.
5. **What they care about** — priorities, decision-making style, what moves them, what stalls them. This is qualitative judgment, not transcription.
6. **Communication preferences** — tone, channel, formality, anyone who needs cc'd by default.
7. **Stakeholder-scoped signal** — when an extracted item is clearly about *one person* rather than the client organization (their personal priorities, their decision style, what they said in a 1:1, side comments and asides), tag it for routing to that person's stakeholder brief instead of the client brief. See [Output: updating stakeholder briefs](#output-updating-stakeholder-briefs) below.

### Extraction rules

- **Short and useful over complete and verbose** — an interaction log entry should be 2-4 sentences, not a paragraph.
- **Signal over noise** — skip small talk, scheduling logistics, pleasantries. Capture what would matter to someone reading this before the next meeting.
- **Mark unknowns** — if something is ambiguous, note it with `?` rather than guessing.
- **No deduplication needed** — flag if something appears to duplicate an existing entry, but don't suppress it.
- **Attribute clearly** — who said what matters. If a contact made a commitment, name them. If the user made a commitment, note that it's on the user's side.

## Output: updating the client brief

The output target is the existing client brief. The path follows the ACOS convention: `Clients/<client-folder>/brief.md`.

### Steps

1. **Read the manifest** — load the client's `manifest.md` for context on identifiers and any routing notes.
2. **Read the existing brief** — load the current `brief.md` for the client.
3. **Read the client folder** — check for README, proposals, contracts, or other source documents in the client folder.
4. **Map extractions to brief sections** — the canonical mapping lives in [`references/brief-sections.md`](references/brief-sections.md). Read that file for the section-by-section guide; do not duplicate the mapping here.
5. **Write the updated brief** — merge new information into the existing brief:
   - Add new rows to tables (contacts, engagements, interaction log)
   - Fill TODO placeholders when information becomes available
   - Update `last-updated` in frontmatter to today's date
   - Update `updated-reason` in frontmatter with a brief note (e.g., "Processed transcript from 2026-05-11 call")
   - Preserve all existing content — only add or clarify, never delete historical entries
6. **Update the manifest** — if new contacts, aliases, or project keywords were discovered, add them to the client's `manifest.md`.
7. **Confirm what changed** — report back with a summary: "Updated [Client] brief. Added: [X new contacts, Y interaction log entries, Z opportunities]. Filled: [section names]."

### If no brief exists yet

If the client folder exists but has no `brief.md`:

1. Create one from the [brief-client template](../../templates/brief-client.md).
2. Populate it with whatever information is available from the current input.
3. Note in the confirmation: "Created brief for [Client]. Populated: [sections filled]. Remaining TODOs: [sections still empty]."

### If no manifest exists yet

If the client folder exists but has no `manifest.md`:

1. Create one from the [manifest-client template](../../templates/manifest-client.md).
2. Populate company identifiers, contacts, and project keywords from the current input and brief.
3. Note in the confirmation: "Created manifest for [Client]."

## Output: updating stakeholder briefs

When a client has designated primary stakeholders, they have per-person briefs in `Clients/<client>/Stakeholders/<kebab-name>.md`. Some of the extracted signal belongs there, not in the client brief.

### Routing rule

The routing decision is **who is the content about?**

- **About the client organization** → client brief. Engagement scope, opportunities, commitments tied to the company, what the company cares about (institutionally), communication norms at the org level.
- **About one specific person** → that person's stakeholder brief. Their personal priorities, their decision-making style, what they personally said in a 1:1, their communication quirks, their open threads with us, side comments and asides.

When in doubt, ask. A signal placed in the wrong file is worse than a signal flagged for routing review.

### Steps

For each transcript, after updating the client brief:

1. **Identify which stakeholders are present** — speakers in the transcript whose name maps to a Key contacts row in the client brief with a non-empty Brief column. Those are the active stakeholders for this transcript.
2. **Route stakeholder-scoped signal** — for each active stakeholder, append to their stakeholder brief:
   - An entry in their Interaction log (`### YYYY-MM-DD — Topic`), capturing what *they* said and did, not the company-level outcomes.
   - Any new What-they-care-about content, How-to-communicate-with-them updates, or open threads scoped to them.
3. **Preserve the client-brief interaction log** — the org-level entry in the client brief should still capture the meeting at a high level (who was there, what was decided org-wide). The stakeholder brief captures the person-level texture that would otherwise bloat the client brief.
4. **Update frontmatter** — bump `last-updated` on each touched stakeholder brief.
5. **Confirm what changed** — extend the summary: "Also updated stakeholder briefs: [Name 1, Name 2]."

### Creating a new stakeholder brief

If the user designates a new primary stakeholder (explicitly, or by promoting an existing Key contacts row), scaffold a stakeholder brief:

1. Create `Clients/<client>/Stakeholders/<kebab-name>.md` from the [stakeholder-brief template](../../templates/stakeholder-brief.md).
2. Fill in frontmatter (name, client, role, email, status).
3. Populate Who-they-are and Role-and-relationship from what's available in the client brief and any provided context.
4. Update the Brief column for that contact in the client brief's Key contacts table to link the new file.
5. Note in the confirmation: "Created stakeholder brief for [Name]."

### When a stakeholder leaves the client org

Set the stakeholder brief's frontmatter `status` to `alumni`, mirror the change on the client brief's Key contacts row (Relationship → `alumni`, Role → append `(former)`), and stop routing new transcript content to their stakeholder brief by default. Existing history stays — the brief becomes a frozen record. If the alumni stakeholder later resurfaces in a new role (at a new company or back at the same one), the user will tell you how to handle it.

## Manifest maintenance

The manifest is a living document. After every transcript processing:

- Add new contact names and emails that appeared in the transcript.
- Add new project keywords or abbreviations that emerged.
- Add any aliases or alternate names observed.
- Update `last-updated` in frontmatter.

When a new client folder is created, always create both a `manifest.md` (from the manifest template) and a `brief.md` (from the brief template).

## Reference files

- [`references/brief-sections.md`](references/brief-sections.md) — section-by-section guide for the client brief: what each section contains, what good content looks like, and the canonical mapping from extraction category to brief section (including stakeholder-scoped routing).
- [`../../templates/manifest-client.md`](../../templates/manifest-client.md) — template for creating a new client manifest.
- [`../../templates/brief-client.md`](../../templates/brief-client.md) — template for creating a new client brief.
- [`../../templates/stakeholder-brief.md`](../../templates/stakeholder-brief.md) — template for creating a new per-stakeholder brief.

## Future input sources

The following input sources are not yet implemented at the framework level. Instances may implement them via overlay, or contributors may extend the framework to support them.

- **Notion transcripts** — pulling meeting transcripts from a Notion database. Configuration would specify database ID, schema mapping, and which property holds the transcript body.
- **Slack exports** — accepting exported Slack channel or DM history and processing as if a transcript.

For now, when a user asks for any of these, suggest pasting the transcript text directly as the simplest path.

## Future output targets

The following output targets are not yet implemented. Do not implement until explicitly requested:

- **CRM updates** — writing contacts or status to a Notion contacts database, Salesforce, HubSpot, or similar.
- **Calendar events** — creating follow-up or meeting events from commitments surfaced in the transcript.
- **Activity log** — leaving a breadcrumb of processed inputs in a per-client `_history/` log.
