---
type: folder-readme-item
folder: <FolderName>
parent: <ParentFolderName>
status: active  # active | paused | wrapped | exploratory | stale
last-updated: YYYY-MM-DD
maintainer: <Name or persona>
purpose: <One-line purpose>
---

# <FolderName> — <one-line description>

> **Cascade:** If you are an AI tool, read the instance root README and the [<ParentFolderName>](../README.md) README first. This README is the **operational front door** for the folder — what's here, what state it's in, where to look. If a `brief.md` is present in this folder, that file is the canonical substantive record (history, contacts, opportunities, content) — read it for substance; this file is for navigation.

## What this is

> **TODO:** One paragraph. What does this folder represent — a client engagement, a product, an internal project, a research thread? Quick framing only; substantive context lives in `brief.md` if present.

## Status

> **TODO:** One line. Current state, as of the `last-updated` date in frontmatter. Examples:
>
> - "Active engagement; Q2 2026 retainer in progress."
> - "Shipped v1; in maintenance."
> - "Paused pending decision on scope expansion."
>
> If `brief.md` is present, full engagement / release / interaction history lives there.

## Key files

A guided tour of the files in this folder. Not a directory listing — a curated pointer list.

> **TODO:** Examples (list `brief.md` first if present, since it's the source of truth):
>
> - `brief.md` — canonical record for this <client / product / project>. Read first for substance.
> - `manifest.md` — lookup index for matching transcripts and communications to this folder (clients).
> - `Brand/` — captured brand kit (visual + verbal identity); produced by the `client-brand-capture` skill. The headline summary lives in `brief.md` under "Brand & identity"; the full kit lives here.
> - `engagement-2026-q2.md` — current scope-of-work doc.
> - `outputs/<latest-deliverable>.pdf` — most recent deliverable.
>
> If a file is the source of truth for something, say so explicitly.

## People

> **TODO:**
>
> - **If `brief.md` is present:** point at it and stop. Example: "Canonical contact list lives in [`brief.md`](brief.md)."
> - **If no `brief.md`:** list key people inline. Example:
>   - <Name> — <role> (<email>)

## Open threads

> **TODO:**
>
> - **If `brief.md` is present:** the running list of open commitments and pipeline lives in `brief.md`. Surface only the most urgent one or two items here, with a pointer.
> - **If no `brief.md`:** list open items inline. Quick bullets are fine.

## Links

- Parent: [<ParentFolderName>](../README.md)
- Instance root: the instance's `README.md` at the top of the tree
- Brief (if present): [`brief.md`](brief.md)
- Related: TODO (other folders or briefs that connect to this one)
