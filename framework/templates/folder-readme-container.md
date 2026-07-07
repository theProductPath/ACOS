---
type: folder-readme-container
folder: <FolderName>
status: skeleton  # skeleton | drafting | active | stale
last-updated: YYYY-MM-DD
maintainer: <Name or persona>
purpose: <One-line purpose — keep tight>
---

# <FolderName> — <one-line purpose>

> **Cascade:** If you are an AI tool, read the instance root README first, then this. This README adds folder-specific scope on top of the system-wide rules in [ACOS](../<path-to-acos>/framework/README.md).

## What this folder is

> **TODO:** One paragraph. What kind of work lives here, why it exists as its own folder, and what makes something belong here vs. elsewhere in the instance.

## What counts as a child here

> **TODO:** Define the rule for what becomes a sub-folder of this folder. Examples:
>
> - "One sub-folder per active client engagement."
> - "One sub-folder per product, plus its companion `*-site` repo."
>
> If there are categories or types of children, list them.

## Child folder conventions

How each sub-folder inside this folder should be structured.

> **TODO:** Specify the expected internal structure for a child folder. For example:
>
> - Required files (e.g., `README.md` from the [Item template](../<path-to-acos>/framework/templates/folder-readme-item.md), `brief.md`).
> - Standard sub-folders (e.g., `deliverables/`, `notes/`, `inputs/`).
> - File naming conventions inside.
>
> If a `templates/` folder exists at this level, point at it as the source of truth for child scaffolding.

## Children — active index

| Sub-folder | Status | Purpose | Last touched |
|---|---|---|---|
| `<child-folder>/` | active | TODO | YYYY-MM-DD |

> **TODO:** Keep this table current. List active children only. Anything dormant moves to `_archive/` (out of scope per [agent-ignore](../<path-to-acos>/framework/agent-ignore.md)).

## Local house rules

Conventions that apply *only inside this folder*, on top of the system-wide rules in ACOS and any instance-level rules in the instance root README.

> **TODO:** Leave this section empty if there are no folder-specific rules. Examples of what would go here:
>
> - "Client deliverables are saved as PDF, never `.docx`."
> - "All inbound briefs land in `inbound/` before being processed."
>
> Local rules **add to** but cannot loosen the global rules.

## Links

- Parent: instance root README
- Framework: [ACOS](../<path-to-acos>/framework/README.md)
- Reusable scaffolding: `templates/` (if present in this folder)
- Agent-ignore rule: [`agent-ignore.md`](../<path-to-acos>/framework/agent-ignore.md)
