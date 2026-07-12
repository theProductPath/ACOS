---
type: folder-readme-item
folder: ACOS
parent: Products
status: active
last-updated: 2026-07-12
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

**Active, v0.1.** The framework is published and in production use in its reference instance. The rules in `framework/README.md` are binding, not provisional — but the surface is young, and it will keep growing as patterns prove general enough to promote out of an instance.

Six skills are live in `framework/skills/`: `client-brief-processor`, `client-brand-capture`, `dashboard-refresh`, `dashboard-tune`, `acos-integrity`, and `readme-refresh`.

ACOS is developed in its own git repository, separate from any instance. A read-only copy is published into theProductPath's Drive tree so that Drive-scoped agents can read the framework; that copy is a mirror, and the repo is canonical.

## How to navigate

- `framework/README.md` — the substantive operating manual. Cascade rules, README patterns, frontmatter taxonomy, house rules. **This is the canonical "ACOS docs" entry point.**
- `framework/agent-ignore.md` — the skip-rule convention.
- `framework/templates/` — copy these into a new instance to scaffold its folders and briefs.
- `framework/skills/` — agent capabilities that work against any ACOS instance. Each skill folder has its own `SKILL.md` and supporting references.
- `docs/extending-acos.md` — conventions for agents and contributors extending the framework. Read this before adding a new skill, template, or rule.
- `docs/adopting-acos.md` — guide for a new company adopting ACOS: scaffolding an instance, filling in the templates, wiring in skills, and pointing agents at the tree.
- `instances/README.md` — known instances of ACOS. tPPOS is currently the only one and is the reference implementation.
- `scripts/` — developer tooling you run by choice, never a dependency. `acos-integrity-check.py` checks an instance against the conventions; `check-links.py` checks this repo's own links. ACOS ships no *runtime* tooling — nothing an instance needs in order to operate — see [`docs/extending-acos.md`](docs/extending-acos.md#code-in-acos--tools-yes-runtime-no) for where that line is drawn, and why a scaffolder like `acos init` falls on the permitted side of it.

## Relationship to tPPOS

tPPOS is theProductPath's own instance of ACOS. It's a private company tree — it is not distributed with the framework, and nothing in this repo requires you to read it. The relationship works in both directions:

- **ACOS → tPPOS:** improvements to the framework propagate to tPPOS by reference. tPPOS adopts ACOS templates, ACOS skills, ACOS conventions without re-implementing them.
- **tPPOS → ACOS:** patterns that emerge in tPPOS and prove generally useful get *promoted* to ACOS, with a thin overlay in tPPOS capturing whatever residual tPP-specificity remains.

The decision rule for where a new change lands is in [`docs/extending-acos.md`](docs/extending-acos.md). When in doubt: tPP-specific changes go in tPPOS, reusable changes go in ACOS.

## Links

- Framework manual: [`framework/README.md`](framework/README.md)
- Adoption guide: [`docs/adopting-acos.md`](docs/adopting-acos.md)
- Extension conventions: [`docs/extending-acos.md`](docs/extending-acos.md)
- Known instances: [`instances/README.md`](instances/README.md)
- Source: https://github.com/theProductPath/ACOS
- Marketing site: https://acos.theproductpath.com — built from the `gh-pages` branch of this repo, which is a separate content root. It is not part of a framework clone, and nothing on `main` depends on it.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

SPDX-License-Identifier: Apache-2.0

## Trademarks

The project names, logos, and associated brand assets are trademarks of their respective owners. Use of the code, documentation, templates, and examples is governed by the Apache-2.0 license; use of names and brand assets may require separate permission.
