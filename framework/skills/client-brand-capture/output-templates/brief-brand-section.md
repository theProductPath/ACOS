---
type: brief-section-template
skill: client-brand-capture
inserts-into: brief-client.md
last-updated: 2026-05-12
purpose: The "Brand & identity" section appended to a client's brief.md after a brand-capture run.
---

# Brief section template — "Brand & identity"

The skill appends this section to `Clients/<client>/brief.md`. Insert it after the "How to communicate with them" section and before "Interaction log" — it belongs with the qualitative judgment layer about working with the client, not with the running log.

If the section already exists from a prior run, update it in place rather than appending a duplicate.

---

## Brand & identity

Captured from <client-domain> on YYYY-MM-DD. Full kit lives in [`Brand/`](Brand/); the summary below is the headline that an agent needs before they descend.

**Visual identity.** Primary color is `<hex>` (<one-word descriptor, e.g., "burnt orange">). Body typography is <font name>. Overall feel: <one sentence — e.g., "Clean editorial, generous whitespace, photography-led.">.

**Verbal identity.** <Tone descriptor sentence — e.g., "Direct, technically credible, audience is product and engineering leaders at insurers.">. Avoids <one or two pattern absences — e.g., "superlatives and hedge words.">.

**Use this brand for:** all client-facing artifacts produced for <Client name> — proposals, SOWs, decks, emails, and any document agents draft in their name. The substantive brand context (when each color or font applies, voice rules in detail) lives in [`Brand/`](Brand/).

> **TODO:** Verify with <Principal name>. Last updated YYYY-MM-DD by `client-brand-capture` skill.

---

# Placement rules

- **First-time insertion** (new client, or existing client without prior brand capture): place after "How to communicate with them," before "Interaction log."
- **Update on re-run:** locate the existing "Brand & identity" header, replace the section body, leave surrounding sections intact.
- **Cascade preservation:** do not add or modify the brief's top-level "Cascade" callout. Brand cascade is already implicit in the brief — agents are reading the brief, they see the Brand section, they descend if needed.
