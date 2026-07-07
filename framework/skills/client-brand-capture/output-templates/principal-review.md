---
type: principal-review
skill: client-brand-capture
subject: <Client name>
run-date: YYYY-MM-DD
tier: <1 | 2 | 3>
principal: <Resolved principal name>
status: pending  # pending | partial | complete
purpose: Single consolidated checklist of every TODO from the brand-capture run. The principal works through this list to sign off the kit; nothing in Brand/ should be treated as authoritative until the relevant items are checked.
---

# <Client name> — Principal review

**For:** <Principal name> (resolved via `tPPOS/company-brief.md` Principals → <single principal | primary stakeholder | maintainer fallback>)
**Run date:** YYYY-MM-DD
**Extraction tier:** <1 — live browser | 2 — computer-use | 3 — static HTML (preliminary)>

> **Until the items below are checked, no agent should treat the brand kit as authoritative.** Unchecked items mean the skill could not verify the value — using it in a client-facing artifact risks getting brand details wrong. When you complete an item, edit the source file directly, then check the box here.

## How to use this file

1. Open the file linked next to each item and confirm or correct the value.
2. Check the box here once the file is right.
3. When every box is checked, move this file to `Brand/_archive/<run-date>-principal-review.md` (or ask the skill to do it on its next run) and remove the "pending" note from `brief.md`.
4. New brand-capture runs append new items; checked items from prior runs stay checked.

## Colors — [`colors/palette.md`](colors/palette.md)

- [ ] Confirm primary brand color hex code (currently `<value>`)
- [ ] Confirm secondary / accent colors
- [ ] Confirm neutral scale (body text, surfaces, borders)
- [ ] Confirm state colors (success / warning / error), if used in any artifacts you'll produce
- [ ] Confirm dark-mode palette if a separate one exists

## Typography — [`typography/type-system.md`](typography/type-system.md)

- [ ] Confirm body font family (currently `<value>`) and that the fallback chain is appropriate for Word/PowerPoint/PDF
- [ ] Confirm heading font family (currently `<value>`)
- [ ] Confirm weight scale (which weights to use for H1/H2/H3/body)
- [ ] Confirm font license / source if you'll be embedding for non-web artifacts

## Logos — [`logos/`](logos/)

- [ ] Confirm logo files captured are the canonical assets (vs. needing higher-fidelity sources)
- [ ] Pull any missing variants (color-on-light, white-on-color, mark-only) into `logos/`
- [ ] Confirm logo usage rules — when each variant applies

## Voice — [`voice.md`](voice.md)

- [ ] Confirm tone descriptors match how the client actually sounds in your direct experience
- [ ] Confirm any internal-only language (employee terms, internal metaphors) flagged in voice.md is correctly scoped (internal vs. client-facing)
- [ ] Confirm signature phrases are accurate
- [ ] If `brand-voice` plugin becomes available, re-run for deeper analysis

## Sign-off

- [ ] All items above resolved
- [ ] `_sources.md` updated with sign-off entry
- [ ] `brief.md` "Brand & identity" section updated — "pending" note removed
- [ ] This file moved to `Brand/_archive/`

---

## Notes from the principal

> Use this space to record any edits or notes made during review. Future agents will read this if a question arises about brand interpretation.

> **TODO:** *(Principal fills in as they work through the list.)*
