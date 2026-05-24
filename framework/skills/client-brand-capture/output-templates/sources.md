---
type: skill-audit
skill: client-brand-capture
subject: <Client name>
last-updated: YYYY-MM-DD
purpose: Audit trail for the brand-capture run — URLs scraped, what was extracted from each, companion-plugin handoffs, and principal sign-off.
---

# <Client name> — Brand capture sources

Append-only log. Most recent run at the top.

## Run — YYYY-MM-DD

**Resolved principal:** <Principal name> (resolution rule: <single principal | primary stakeholder | maintainer fallback>)
**Primary marketing URL:** https://<client-domain>
**Skill version:** <SKILL.md last-updated date>

### URLs fetched

| URL | Fetched at | Used for |
|---|---|---|
| https://<client-domain> | YYYY-MM-DD HH:MM | Hero copy, palette, typography, logo |
| https://<client-domain>/about | YYYY-MM-DD HH:MM | Voice samples, team page logo confirmation |
| <additional URLs> | YYYY-MM-DD HH:MM | <purpose> |

### Companion plugins used

- **brand-voice:** <yes / no>. <If yes: which sub-skill, what samples were handed over, where output landed.>

### Extraction summary

- **Colors:** <N> distinct after clustering; <M> tagged with roles; <K> remaining as TODO.
- **Typography:** <font names> identified. <Weights captured>. <K> remaining as TODO.
- **Logos:** <N> candidates downloaded. Best candidate: `logos/<filename>`. Alternates retained.
- **Voice:** <N> sentences sampled across <M> pages. Tone descriptors: <list>. Confidence: <high / medium / low>.

### Outstanding TODOs at end of run

- > **TODO:** Verify with <principal name> — <specific item, e.g., "primary color #c75c2a vs. alternate #d96d3a">

### Principal sign-off

- **Reviewed by:** <Principal name>
- **Date:** YYYY-MM-DD
- **Status:** <pending | partial | complete>
- **Notes:** <any edits made on review>

---

## Run — <earlier date, if re-run>

<Same structure, oldest at the bottom.>
