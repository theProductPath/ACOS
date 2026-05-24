---
type: folder-readme-asset
folder: <FolderName>
status: active  # active | drafting | stale
last-updated: YYYY-MM-DD
maintainer: <Name or persona>
purpose: <One-line purpose — describe what asset library this folder is>
---

# <FolderName> — <one-line description>

> **Cascade:** If you are an AI tool, read the instance root README first. This folder is an **asset library** — the README *is* the source of truth, not an index of children. Read it whenever a task needs the substance this folder owns (typically: brand assets, design tokens, shared scripts, reference content that applies across the whole instance).

## What this is

> **TODO:** One paragraph. What does this asset library cover, and what should an agent reach for it for? An asset folder differs from a Container folder in that the README contains *the answer*, not pointers to sub-folders with answers.

## When to read this

> **TODO:** List the trigger task types. For a brand library: "Any task producing a client-facing or polished artifact: proposals, decks, Word docs, PDFs, web, marketing copy, social." This section should make it easy for a lateral-cascade rule in ACOS or the instance to point at this folder.

## The substance

The rest of this README *is* the substance. Sections should be specific to what this asset library carries. Examples of section types you might use:

- **Colors / palette** — hex codes, tokens, when each is used.
- **Typography** — typefaces, weights, fallback chain.
- **Logo usage** — file paths, clearspace, do-not's.
- **Voice rules** — specific to this asset's domain, separate from the company brief's general voice.
- **Reference snippets** — code, copy patterns, templates.

> **TODO:** Replace this list with the actual structure of this asset library.

## Known gaps

> **TODO:** If part of the asset library is incomplete or in flux, flag it here so agents know to ask before improvising. Examples:
>
> - "Dark mode tokens are drafting; ask before using them in a production deliverable."
> - "Logo PDF master is out of date; the SVG is the source of truth."

## Links

- Parent: instance root README
- Framework: [ACOS](../<path-to-acos>/framework/README.md)
- Related: TODO
