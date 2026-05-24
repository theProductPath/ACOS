---
type: folder-readme-root
folder: <InstanceName>
status: skeleton  # skeleton | drafting | active | stale
last-updated: YYYY-MM-DD
maintainer: <Name>
purpose: <InstanceName> entry-point README — instance-specific folder map, local conventions, and pointers to the ACOS framework for system-wide rules.
---

# <InstanceName> — <Company name>'s ACOS instance

> The <Company name> instance of [ACOS](../<path-to-acos>/framework/README.md) — the framework-level operating manual for all system-wide rules and cascade conventions.
>
> If you are an AI tool, agent, or assistant of any kind reading this file: **start here.** This document tells you what this instance contains, where context lives, and how to behave when working inside it. For system-wide rules (cascade behavior, frontmatter taxonomy, house rules), read the ACOS framework README; this file adds instance-specific scope on top.

## What this is

> **TODO:** One paragraph. What this instance covers — which company, which folders are in scope, what makes this instance distinct from a generic ACOS adoption. Reference the company brief for who the company is.

## Where this lives

> **TODO:** Describe the storage layer (Google Drive, OneDrive, a repo, etc.), sync expectations, and any quirks about which sub-folders are or are not available offline. Note: `_archive/` and other underscore-prefixed folders are excluded from AI scope per [agent-ignore](../<path-to-acos>/framework/agent-ignore.md), so sync quirks for those folders rarely matter.

## Folder map

Every folder below sits as a **sibling** of this instance root. Read the description first; only descend into a folder when the task warrants it.

| Folder | What's in it | When an AI should read into it |
|---|---|---|
| `<this-folder>/` | **You are here.** The instance root and instance-specific conventions. | Always, first. |
| `Clients/` | TODO — one sub-folder per client engagement. | Any task referencing a specific client. |
| `Projects/` | TODO — internal initiatives. | Internal strategy, ops, or build projects. |
| `Products/` | TODO — things this company has built or is building. | Anything touching a product. |
| `Brand/` | TODO — single source of truth for logos, colors, typography. | Any design, marketing, document, or visual asset task. |
| `Research/` | TODO — experiments, notes, exploratory work. | When the task is exploratory or references prior research. |

> **TODO:** Add or remove rows to match this instance's actual folder tree. Some instances will not have all of these; some will have additional sibling folders.

## Instance-specific conventions

Conventions that apply *only inside this instance*, on top of the framework rules in [ACOS](../<path-to-acos>/framework/README.md).

> **TODO:** Leave this section empty if there are no instance-specific rules. Examples of what would go here:
>
> - Voice and tone specific to this company.
> - Document conventions (file naming, version suffixes).
> - Local glossary and acronyms.
> - Working defaults (preferred file formats, default output locations).
>
> Instance rules **add to** but cannot loosen the framework rules.

## Skill overlays

If this instance customizes any ACOS skills, the overlays live in `overlays/` at this folder. See the ACOS [Skills and overlays](../<path-to-acos>/framework/README.md#skills-and-overlays) section for the discovery convention.

> **TODO:** List active overlays here as they're created. Example:
>
> - [`overlays/client-brief-processor.md`](overlays/client-brief-processor.md) — instance config for the client-brief-processor skill (Gmail account, client folder paths, routing quirks).

## About <Company name>

The canonical company brief lives in [`company-brief.md`](company-brief.md) — start there for any task that needs to represent the company (proposals, marketing, positioning, voice).

## Links

- ACOS framework: [`../<path-to-acos>/framework/README.md`](../<path-to-acos>/framework/README.md)
- ACOS agent-ignore: [`../<path-to-acos>/framework/agent-ignore.md`](../<path-to-acos>/framework/agent-ignore.md)
- Company brief: [`company-brief.md`](company-brief.md)
- Out of scope: anything under `_archive/` or other underscore-prefixed folders (per agent-ignore).

## Versioning and maintenance

- **Version:** TODO
- **Last updated:** YYYY-MM-DD
- **Maintainer:** <Name>
- **Status:** TODO
