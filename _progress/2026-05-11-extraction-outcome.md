---
type: progress-checkpoint
status: active
last-updated: 2026-05-12
maintainer: Steven Jones
purpose: After-action report for the 2026-05-11 ACOS extraction. Documents what actually shipped from the restructure that pulled the generic framework out of tPPOS and landed it at Products/ACOS/. Pairs with the pre-extraction audit and plan at tPPOS/_progress/2026-05-11-acos-extraction-review.md.
---

# 2026-05-11 ACOS extraction — outcome report

The framework/instance split shipped. ACOS now exists as a separate product at `Products/ACOS/`; tPPOS shrank to its instance-specific role and points at ACOS for system-wide rules. This report is the after-action companion to the pre-extraction audit at [`tPPOS/_progress/2026-05-11-acos-extraction-review.md`](../../../tPPOS/_progress/2026-05-11-acos-extraction-review.md).

## What ACOS now is

A standalone product folder at `Products/ACOS/` with four top-level sections:

- **`framework/`** — the framework operating manual. Includes the README that any LLM should read first when it lands inside an ACOS instance, the agent-ignore convention, the four README templates, the brief and manifest templates, and the (currently one) shared skill.
- **`docs/`** — supporting documentation for people *outside* the framework boundary: `extending-acos.md` for contributors, `adopting-acos.md` for prospective adopters.
- **`_progress/`** — ACOS's own progress log, separate from `tPPOS/_progress/`. The instance and the framework now keep distinct lineage trails.
- **`README.md`** — the product front door (Item-shaped, codebase-style). Positions ACOS for an outside reader, points internal readers at `framework/README.md` for the substantive content.

Positioning is clean: ACOS is LLM-agnostic, tool-agnostic, instance-pluggable. tPPOS is the first reference instance.

## What shipped against the plan

The pre-extraction review listed eleven files moving to ACOS and a handful of new docs. All eleven moved; all new docs were created.

### Framework files in place

- `framework/README.md` — the framework operating manual, extracted from the old combined tPPOS README
- `framework/agent-ignore.md` — the underscore-prefix skip rule
- `framework/templates/folder-readme-root.md` — the new "root" README pattern
- `framework/templates/folder-readme-container.md` — container pattern
- `framework/templates/folder-readme-item.md` — item pattern
- `framework/templates/folder-readme-asset.md` — asset pattern (newly extracted as a template; previously was prose-only in `Brand/README.md`)
- `framework/templates/brief-company.md` — company brief template
- `framework/templates/brief-client.md` — client brief template
- `framework/templates/manifest-client.md` — client manifest template
- `framework/skills/client-brief-processor/SKILL.md` — the first ACOS skill, rewritten generic
- `framework/skills/client-brief-processor/references/brief-sections.md` — the brief-section mapping, scrubbed of tPP-specific examples

### Outside-the-framework documentation

- `README.md` — the ACOS product README (codebase-style item README)
- `docs/extending-acos.md` — conventions for agents and contributors who want to extend the framework
- `docs/adopting-acos.md` — short guide for a company adopting ACOS as their own instance

### Bonus that wasn't explicitly planned

- `docs/adopting-acos.md` was new — the pre-extraction review only named `extending-acos.md`. Adoption guidance ended up being its own short doc, separate from the contributor guidance, which is the right split.

### Instance side — what stayed (and shrank) in tPPOS

- `tPPOS/README.md` rewritten as a short instance README that points at the ACOS framework for system-wide rules. Now ~50 lines instead of the ~250-line combined doc it used to be.
- `tPPOS/company-brief.md` unchanged in role; this is instance content.
- `tPPOS/overlays/client-brief-processor.md` — the instance-specific configuration for the framework skill (Gmail account, folder paths, HPP subsidiary routing). Moved out of the old skill folder into the new overlays convention.
- `tPPOS/templates/client-brief-processor/` — deleted (the skill itself moved to ACOS).

## New conventions introduced by the split

The extraction surfaced and codified four conventions that didn't exist as named rules before:

### Framework vs. instance decision rule

A change belongs in ACOS when another adopter would also want it; otherwise it stays in the instance. When an instance-only pattern proves reusable, it's promoted to ACOS with an instance-thin overlay left behind for whatever residual specificity remains. Documented in `framework/README.md` and `docs/extending-acos.md`.

### Overlay convention

Each ACOS skill that needs instance-specific configuration looks for an overlay at `<instance-root>/overlays/<skill-name>.md`. The instance root is discovered by walking up the tree until a folder containing `company-brief.md` is found. This generalizes what was previously implicit in the `client-brief-processor`.

### Asset pattern as a first-class README shape

Previously the asset pattern was exemplified only by `Brand/README.md` ("the asset pattern is what `Brand/` does"). Extraction promoted it to a fourth README template alongside root/container/item, so any folder that holds assets (binary or text) has a documented shape to copy.

### `_progress/` joins `_archive/` under agent-ignore

Already in informal use, formally codified when ACOS got its own `_progress/` separate from tPPOS's. The underscore-prefix convention scales: any future underscore-prefixed folder inherits the same treatment without rule-text changes.

## Open items deferred

From the pre-extraction review's "Open questions deferred":

- **tPPOS's `templates/` folder post-move purpose.** Status: still unresolved. The folder is mostly empty post-extraction; deferred until a clear instance-only template surfaces.
- **Whether ACOS becomes its own GitHub repo.** Per the Products convention, this is the expected end state. Status: still pending; ACOS lives inside the `theProductPath/` tree for now, will be promoted to a separate repo when version 1 is ready for outside adoption.
- **`brief-product.md` template.** Flagged again, still deferred. Will be revisited when Products' Item READMEs are filled in (currently most product folders lack item READMEs entirely — see [`tPPOS/_progress/2026-05-11-roadmap.md`](../../../tPPOS/_progress/2026-05-11-roadmap.md)).

## Skill audit follow-up

The pre-extraction review's audit of `client-brief-processor` flagged eight issues to fix during the port plus three lower-priority observations deferred. The port should have addressed the eight high-priority items; an audit pass against the new `framework/skills/client-brief-processor/SKILL.md` confirming each fix landed is a useful next step — not done as part of this report.

## What this means for what's next

The framework can now grow without touching the tPP instance, and the tPP instance can evolve without polluting the framework. Two paths opened up by the split:

- **Framework-level work** — new skills (the next one will be the first since extraction), refined cascade rules, new template patterns. Tracked in [`_progress/2026-05-11-roadmap.md`](2026-05-11-roadmap.md).
- **Instance-level work** — populating remaining client/product/project Item READMEs, voice and tone codification, file-naming conventions. Tracked in [`tPPOS/_progress/2026-05-11-roadmap.md`](../../../tPPOS/_progress/2026-05-11-roadmap.md).

Until ACOS is adopted by a second company, every framework decision is informed by exactly one instance (tPPOS). That's a deliberate constraint — better to have one strong reference than to design for hypothetical second adopters that don't exist yet — but it should be acknowledged: framework decisions should be evaluated against the tPP instance and then sanity-checked against the question "would another company also want this?" rather than designed from a generic specification.

## Lineage

- Pre-extraction state: [`tPPOS/_progress/2026-05-04-foundation-checkpoint.md`](../../../tPPOS/_progress/2026-05-04-foundation-checkpoint.md)
- Pre-extraction audit and plan: [`tPPOS/_progress/2026-05-11-acos-extraction-review.md`](../../../tPPOS/_progress/2026-05-11-acos-extraction-review.md)
- ACOS roadmap (framework-side what's next): [`_progress/2026-05-11-roadmap.md`](2026-05-11-roadmap.md)
- tPPOS roadmap (instance-side what's next): [`tPPOS/_progress/2026-05-11-roadmap.md`](../../../tPPOS/_progress/2026-05-11-roadmap.md)
- Next progress report: [`_progress/2026-05-12-client-brand-capture.md`](2026-05-12-client-brand-capture.md) — first new ACOS skill plus two new conventions on top of the extraction baseline
