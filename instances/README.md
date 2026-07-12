---
type: folder-readme-container
folder: instances
parent: ACOS
status: active
last-updated: 2026-07-12
maintainer: Steven Jones
purpose: Index of known ACOS instances. Each instance is a company's adoption of the framework; this folder is the registry, not the home for instance content.
---

# instances — known ACOS instances

> **Cascade:** Read [ACOS product README](../README.md) and the [framework README](../framework/README.md) first. This folder is a registry of known instances, not a home for instance content — each instance lives wherever its company tree lives.

## What this is

This folder records which companies have adopted ACOS and points at where each instance lives. It exists for two reasons: so contributors extending the framework know what real-world adoption looks like, and so the framework's evolution can be traced against actual usage.

## Known instances

| Instance | Company | Location | Status | Notes |
|---|---|---|---|---|
| **tPPOS** | theProductPath | Private company tree — not distributed | Active | Reference implementation — the first and most fully populated instance. Patterns in tPPOS often migrate to ACOS via the promotion path. |

An instance is a company's own folder tree, so its location is usually private and this registry records it, rather than linking to it. Nothing in the framework requires reading an instance: every pattern is specified in [`../framework/README.md`](../framework/README.md) and scaffolded in [`../framework/templates/`](../framework/templates/).

> **TODO:** Add rows as additional companies adopt ACOS. The minimum entry: instance name, company, location (a path or URL only if it's actually reachable by a reader of this repo — otherwise say so plainly), status, one-line note.

## Why "instances" and not "deployments" or "adopters"

"Instance" matches the framework-vs-instance vocabulary used throughout ACOS. Other terms (deployment, adopter, tenant) carry connotations from SaaS or multi-tenant architectures that don't fit — ACOS isn't hosted, isn't multi-tenant, and doesn't have a runtime. Each instance is a separate folder tree that happens to follow the same conventions.

## Links

- ACOS product README: [`../README.md`](../README.md)
- Framework manual: [`../framework/README.md`](../framework/README.md)
- Extension conventions: [`../docs/extending-acos.md`](../docs/extending-acos.md)
