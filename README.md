---
type: folder-readme-item
folder: ACOS
parent: Products
status: drafting
last-updated: 2026-07-03
maintainer: Steven Jones
purpose: ACOS product overview — what it is, who it's for, and how the framework relates to its first reference instance (tPPOS).
---

# ACOS — Agentic Company Operating System

> **Cascade:** This README is the operational front door for ACOS as a product. For the substantive framework operating manual — cascade rules, README patterns, frontmatter taxonomy, house rules, skill conventions — read [`framework/README.md`](framework/README.md). Anyone outside the tPP reference instance (i.e., adopting ACOS for their own company) can start there directly; tPPOS is not required reading. If you arrived here through tPP's internal cascade (tPPOS root → Products → ACOS), you've already done that walk and don't need to circle back.

## What this is

ACOS is theProductPath's framework for running a company as a coherent context surface for AI agents. The premise is simple: when multiple AI tools work across multiple folders for the same company, they need a shared operating layer — conventions for where things live, how documents reference each other, what to skip, how skills attach to a company instance — or each tool reinvents context on every task.

tPPOS, the operating system theProductPath itself runs on, is the first and canonical reference instance of ACOS. ACOS extracts the generic, reusable parts of tPPOS — the cascade rules, the README pattern set, the template library, the skill structure — and packages them as something another company can adopt.

## Positioning

ACOS is **LLM-agnostic, tool-agnostic, and instance-pluggable.** It assumes:

- The company keeps its operating context in a synced folder tree (Google Drive, OneDrive, Dropbox, a repo — the storage layer doesn't matter).
- AI agents orient themselves by reading folder READMEs in cascade, top-down, before acting.
- Company-specific content (voice, clients, products, brand) lives in an *instance* that adopts ACOS conventions but is otherwise the company's own.

What ACOS provides:

- A small, opinionated set of folder README patterns (root, container, item, asset).
- A template library for the artifacts that show up in every company: company brief, client brief, client manifest.
- A skill library — reusable agent capabilities that work against any ACOS instance.
- An overlay convention so each instance can configure skills without forking them.
- House rules covering folder naming, markdown style, frontmatter, and the meta-rule for codifying ambiguity as it emerges.

What ACOS does *not* provide:

- Storage. Bring your own folder tree.
- Tooling. Any LLM or AI platform that can read markdown and walk a folder tree can use ACOS.
- Content. Briefs are templates, not filled-in identities. Each instance fills them in.

## Status

Drafting, v0.1. Currently being extracted from tPPOS into its own coherent surface. The skill library has grown past the first skill: `client-brief-processor`, `client-brand-capture`, `dashboard-refresh`, `dashboard-tune`, `acos-integrity`, and `readme-refresh` are live in `framework/skills/`, with more to follow as patterns harden inside tPPOS and prove general enough to promote.

This product follows the standard `Products/` rule: it's a self-contained codebase with its own internal structure, separate from the tPPOS layer that wraps the rest of theProductPath. Expect ACOS to eventually become its own repo once the surface stabilizes.

## How to navigate

- `framework/README.md` — the substantive operating manual. Cascade rules, README patterns, frontmatter taxonomy, house rules. **This is the canonical "ACOS docs" entry point.**
- `framework/agent-ignore.md` — the skip-rule convention.
- `framework/templates/` — copy these into a new instance to scaffold its folders and briefs.
- `framework/skills/` — agent capabilities that work against any ACOS instance. Each skill folder has its own `SKILL.md` and supporting references.
- `docs/extending-acos.md` — conventions for agents and contributors extending the framework. Read this before adding a new skill, template, or rule.
- `docs/adopting-acos.md` — guide for a new company adopting ACOS: scaffolding an instance, filling in the templates, wiring in skills, and pointing agents at the tree.
- `instances/README.md` — known instances of ACOS. tPPOS is currently the only one and is the reference implementation.

## Relationship to tPPOS

tPPOS is the tPP instance of ACOS. The relationship works in both directions:

- **ACOS → tPPOS:** improvements to the framework propagate to tPPOS by reference. tPPOS adopts ACOS templates, ACOS skills, ACOS conventions without re-implementing them.
- **tPPOS → ACOS:** patterns that emerge in tPPOS and prove generally useful get *promoted* to ACOS, with a thin overlay in tPPOS capturing whatever residual tPP-specificity remains.

The decision rule for where a new change lands is in [`docs/extending-acos.md`](docs/extending-acos.md). When in doubt: tPP-specific changes go in tPPOS, reusable changes go in ACOS.

## Links

- Parent: [Products](../README.md)
- Marketing site: https://acos.theproductpath.com — published from the `gh-pages` branch of this repo. It is not part of a framework clone; see `setup-acos-repo.sh` and `acos-site/` (on `gh-pages`) for how it's wired.
- Framework manual: [`framework/README.md`](framework/README.md)
- Reference instance (tPP): [`../../tPPOS/README.md`](../../tPPOS/README.md)
- Extension conventions: [`docs/extending-acos.md`](docs/extending-acos.md)
- tPPOS company brief (positioning context for why tPP built this): [`../../tPPOS/company-brief.md`](../../tPPOS/company-brief.md)

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

SPDX-License-Identifier: Apache-2.0

## Trademarks

The project names, logos, and associated brand assets are trademarks of their respective owners. Use of the code, documentation, templates, and examples is governed by the Apache-2.0 license; use of names and brand assets may require separate permission.
