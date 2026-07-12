---
type: skill-reference
skill: client-brand-capture
last-updated: 2026-05-12
purpose: How this skill resolves "the principal" — the human whose sign-off is required on draft brand artifacts — for any ACOS instance.
---

# Principal routing

This skill produces draft artifacts that require human verification. To stay portable across ACOS instances, the skill never hardcodes a name; it resolves *the principal* at runtime from the instance's own metadata.

## Definitions

- **Principal** — a human on whose behalf agents act within an ACOS instance. The default approver when a skill needs human sign-off.
- **Primary stakeholder** — in instances with multiple principals, the one designated as the final escalation point. Used to disambiguate when consensus among principals isn't reachable or isn't expected for a given decision class.

Both terms are framework-level conventions. The full definition lives in the [ACOS framework README](../../../README.md#principals).

## Resolution order

To resolve which principal to route TODO sentinels and verification prompts to:

1. **Read `<instance-root>/company-brief.md`.** Walk up from the working directory until a folder containing `company-brief.md` is found. That's the instance root.
2. **Locate the `## People` section, then the `### Principals` subsection.**
3. **Apply this logic:**

| Case | Resolution |
|---|---|
| One principal listed | Route to that name. |
| Multiple principals, one marked **primary stakeholder** | Route to the primary stakeholder. |
| Multiple principals, none marked primary | Route to the first listed and surface a one-line warning that the instance should designate a primary stakeholder. |
| No `Principals` subsection exists | Fall back to the `maintainer` value in `company-brief.md`'s frontmatter. Surface a one-line note that the instance should formalize its principals per the ACOS framework convention. |
| No `company-brief.md` exists | Hard error. The instance is not ACOS-conformant; cannot proceed without confirmation from the user. |

## How the resolved name is used

Wherever the skill writes a verification prompt or TODO sentinel:

- **TODO sentinels**: `> **TODO:** Verify with <principal name>.`
- **Verification prompts to the user at run-end**: "I've drafted the Brand folder. <Principal name>, can you confirm or edit the proposed primary color, body font, and voice tone descriptors?"
- **`_sources.md` audit entry**: include the resolved principal name and the rule that selected them (single principal / primary stakeholder / fallback to maintainer).

Do not write the principal name into static content (headings, palette entries, file names). It belongs only in prompts and TODO sentinels — the parts the principal will actively respond to.

## Multi-stakeholder decisions

Some brand decisions might warrant routing to a domain-specific principal rather than the primary stakeholder — for example, an instance with a dedicated head of brand or marketing lead. The current convention is:

- **All** verification in this skill routes to the primary stakeholder by default.
- An instance overlay (`overlays/client-brand-capture.md`) may specify a domain-specific principal for brand-related sign-off ("route brand verification to <name> rather than primary stakeholder").
- If overlay routing is specified, surface the rule in `_sources.md` so the audit trail is clear.

## Instance examples

Single-principal instance (a solo operating company): one principal, listed once in `company-brief.md`, automatically the primary stakeholder. Nothing to route.

Multi-principal instance (an agency adopting ACOS): three principals — founder, head of accounts, head of design. The founder is marked as primary stakeholder, so the skill routes there by default. An overlay specifies head of design for brand verification, and that overrides the default for this skill only.
