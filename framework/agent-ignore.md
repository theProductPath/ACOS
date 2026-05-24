---
type: agent-ignore
status: active
last-updated: 2026-05-11
maintainer: Steven Jones
purpose: Canonical reference for folders and paths AI tools should skip anywhere inside an ACOS instance. The convention is "underscore prefix means skip"; this file states the rule, names the patterns, and explains its limits.
---

# Agent-ignore — folders AI should not read

> **Cascade:** Read [the ACOS framework README](README.md) first. This file is a lateral-cascade reference: it applies regardless of where the work is happening in the tree, and should be honored before any folder traversal begins.

## The rule

Any folder whose name begins with an underscore is **out of scope for AI work** by default. AI tools should not:

- Read files inside underscore-prefixed folders for context.
- List underscore-prefixed children when summarizing what a parent folder contains.
- Write new content into them.

The signal is the prefix itself. There are no exceptions in the framework today; if an instance ever needs one, it should be documented in the instance's own README rather than weakening this rule.

## What this currently covers

- `_archive/` (at any depth) — retired material, intentionally kept out of context windows. Instances often also exclude these subfolders from local sync to save space; if a tool fails to open a file under an `_archive/` path, the cause may be that the folder is cloud-only on the working machine.
- `_progress/` — meta-checkpoints about how an ACOS instance is being built or evolving. For the maintainer's reference, not for AI to crawl.
- Any future underscore-prefixed folder — same default treatment without needing this file to be updated. The rule is the prefix itself, not an enumerated list.

## Why this exists

Underscore-prefixed folders typically hold one of three things: archived material that's no longer current, working notes meant for humans and not for AI ingestion, or system-management metadata that would dilute task-relevant context if pulled into a context window. Letting AI crawl them creates noise in the best case and surfaces stale or private content in the worst.

## What this convention does not enforce

This is a *convention* for AI agents that read an ACOS instance's operating docs and follow them. It is reliable for that class of tool — agentic IDE assistants, conversational AI tools that orient themselves by reading the root README before acting, and similar. It is **not** reliable for indexing or RAG pipelines that ingest folder contents without consulting this file, or for any tool that walks directories programmatically without an instruction layer in front of it.

If a specific tool ever traverses an ACOS instance without honoring this convention, the right response is to layer in a tool-specific ignore mechanism (`.gitignore`, `.cursorignore`, vendor-specific exclude files, etc.) rather than to weaken or relocate the convention here.

This file is also not a privacy boundary. For genuinely sensitive material — credentials, private notes, anything that absolutely must not surface — store it outside the ACOS instance tree.

## Override

The only override is an explicit in-conversation instruction from a human to look into a specific underscore-prefixed folder for a specific reason. Without that, the default is to skip.

## Patterns

For tools that can parse `.gitignore`-style patterns, the canonical rule is:

```gitignore
_*/
**/_*/
```

Those two lines cover any underscore-prefixed folder at the root and at any depth in the tree.
