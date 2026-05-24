---
type: acos-doc
subject: adopting-acos
status: skeleton
last-updated: 2026-05-11
maintainer: Steven Jones
purpose: Guide for a new company adopting ACOS — how to scaffold an instance, fill in the templates, and start using the framework skills. Skeleton only as of 2026-05-11.
---

# Adopting ACOS — skeleton

> **TODO:** This doc is a placeholder. Will be written once the framework has settled and at least one second instance has gone through the process. For now, the canonical example of an ACOS instance is [tPPOS](../../../tPPOS/) — study that to see what an adoption looks like in practice.

## What this will cover (when written)

- **Set up the instance root.** Where to put it, what files it needs, how to initialize from [`folder-readme-root.md`](../framework/templates/folder-readme-root.md).
- **Fill in the company brief.** Walking through [`brief-company.md`](../framework/templates/brief-company.md) for a new adopter.
- **Lay out sibling folders.** Which siblings to create, when, and how to write their container READMEs.
- **Install skills.** How to make ACOS skills available to the agent tooling the company uses.
- **Write overlays.** When and how to write `<instance-root>/overlays/<skill-name>.md` to configure a skill for the company.
- **Maintain the instance.** Cadence for keeping briefs and manifests current, what to put in `_progress/`, when to promote a pattern to ACOS.

## For now

Read the [ACOS framework README](../framework/README.md) end-to-end, then look at [tPPOS](../../../tPPOS/) as a fully-populated example. The patterns will be obvious enough to copy.

## Related

- Framework manual: [`../framework/README.md`](../framework/README.md)
- Extension conventions (for contributors, not adopters): [`extending-acos.md`](extending-acos.md)
- Reference instance: [`../../../tPPOS/`](../../../tPPOS/)
