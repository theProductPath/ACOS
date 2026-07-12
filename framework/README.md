---
type: folder-readme-root
folder: ACOS-framework
status: active
last-updated: 2026-07-12
maintainer: Steven Jones
purpose: The ACOS framework operating manual — system-wide rules, README cascade conventions, frontmatter taxonomy, house rules, and pointers for any company instance that adopts the framework.
---

# ACOS Framework — operating manual

> The portable, LLM-agnostic operating system for running a company as a coherent context surface for AI agents.
>
> If you are an AI tool, agent, or assistant of any kind reading this file: **start here.** This document tells you what an ACOS instance looks like, where context lives, and how to behave when working inside one.

## What this is

ACOS is the connective tissue between everything a company runs on. The folders that sit alongside an instance root — `Clients/`, `Projects/`, `Products/`, `Brand/`, `Research/`, or whatever a given company chooses — each contain a slice of the business. ACOS is the index, the operating manual, and the convention layer that makes those slices usable by any LLM or AI platform without re-explaining the company every time.

Point a tool at an ACOS-instrumented company tree, have it read the instance root first, and it should be able to orient itself, find the right context, and follow the company's working conventions.

## How AI tools should use an ACOS instance

Read the instance root first. Then read into the specific folder(s) relevant to the task. Default behavior:

1. **Identify the task surface.** Which slice of the business does this touch — a client, a project, a product, the brand, research? Use the instance's folder map.
2. **Cascade through folder READMEs.** Read top-down: instance root → the in-scope folder's README → the specific item's README inside it. See [README cascade](#readme-cascade) below.
3. **Follow the instance's house rules** (which extend, but cannot loosen, the framework house rules in [House rules](#house-rules) below).
4. **Surface ambiguity early.** If the task spans multiple folders or the right folder isn't obvious, ask before guessing.

## Instance structure

An ACOS instance is a folder tree with an **instance root** containing:

- A `README.md` that introduces the instance, lists in-scope sibling folders, and points back at ACOS for framework-level rules.
- A `company-brief.md` populated from [`templates/brief-company.md`](templates/brief-company.md) — the canonical company identity content.
- An optional `dashboard.md` populated from [`templates/dashboard-company.md`](templates/dashboard-company.md) — the singleton state record kept current by the [`dashboard-refresh`](skills/dashboard-refresh/SKILL.md) skill (see [Dashboards](#dashboards--the-singleton-state-record)).
- An optional `overlays/` directory holding instance-specific overlays for ACOS skills (see [Skills and overlays](#skills-and-overlays)).
- Any instance-specific docs (voice, glossary, persona definitions) the company chooses to maintain.

Sibling folders of the instance root hold the slices of the business — clients, projects, products, brand, research, or whatever the company chooses. Each sibling folder follows the [README cascade](#readme-cascade) rules.

The first reference instance of ACOS is **tPPOS**, theProductPath's own instance. It is a private company tree and is not distributed with the framework, so this manual never sends you to it: every pattern below is fully specified here and scaffolded in [`templates/`](templates/). Where an example is genuinely load-bearing, it's inlined. Known instances are registered in [`../instances/README.md`](../instances/README.md).

A populated instance root, for orientation:

```
theProductPath/            <- the company tree
  tPPOS/                   <- the instance root
    README.md              <- folder-readme-root: the front door every agent reads first
    company-brief.md       <- brief-company: stable identity, principals, voice
    dashboard.md           <- dashboard-company: volatile current state
    overlays/              <- per-skill instance configuration
      client-brief-processor.md
  Clients/                 <- sibling folder, container README + one item folder per client
  Products/                <- sibling folder, container README
  Brand/                   <- sibling folder, asset README (source of truth, not an index)
```

## README cascade

Every in-scope folder in an ACOS instance should contain a `README.md` describing its purpose, conventions, and current state. AI tools orient themselves by **reading READMEs in cascade** — top-down from instance root to the folder where the work is actually happening.

### Read order

For any task, read READMEs in this order, stopping at the deepest one that exists:

1. The instance root README.
2. The README of the in-scope folder the work touches (e.g., `Clients/README.md`, `Products/README.md`).
3. The README of the specific item inside that folder, if applicable (e.g., `Clients/<client-name>/README.md`).

Each layer adds scope-specific context on top of the layer above. An agent dropped into a deep folder mid-task should still walk *up* to the root and back down, in order.

### Four README patterns

ACOS uses four README shapes, depending on what the folder *is*. Each has a template in [`templates/`](templates/).

| Pattern | Used for | Template |
|---|---|---|
| **Root** | The instance root — singleton per instance. The README is the entry point that tells AI tools what the instance is and where context lives. | [`templates/folder-readme-root.md`](templates/folder-readme-root.md) |
| **Container** | Folders that hold many sibling sub-folders (`Clients/`, `Products/`, `Projects/`, `Research/`). The README is an index of children plus conventions for how each child is structured. | [`templates/folder-readme-container.md`](templates/folder-readme-container.md) |
| **Item** | A specific child inside a container — a single client, product, project, or research thread. The README is curated context for that one thing. | [`templates/folder-readme-item.md`](templates/folder-readme-item.md) |
| **Asset** | A folder that *is* a source-of-truth library (brand assets, design tokens, shared scripts). The README is the substance itself, not an index of children. | [`templates/folder-readme-asset.md`](templates/folder-readme-asset.md) |

When creating a new README, copy the matching template into place and fill it in. Don't invent a new shape unless none of the four fit — and if that happens, propose a fifth pattern back here rather than going freelance.

### Override semantics

Folder READMEs **add to** but cannot **loosen** the framework rules in this file. Specifically:

- Global rules are binding: the [agent-ignore](#agent-ignore) convention, the `templates/` reuse pattern, and folder naming conventions are framework-level.
- Folder READMEs may add scope-specific rules on top (e.g., "Client deliverables save as PDF only") — those local rules apply within that folder's tree.
- If a folder README appears to contradict this framework README, treat the framework as authoritative and surface the contradiction.

### Frontmatter

Every README in an ACOS instance — including the instance root — opens with a small YAML frontmatter block: `type`, `status`, `last-updated`, `maintainer`, `purpose`, plus folder-specific fields where relevant (`folder`, `parent`). The point is to make the system machine-parseable later: a future tool can walk the tree and report which READMEs are stale or missing without reading prose. Fill these fields honestly; don't leave dates lying.

The `type` taxonomy currently in use:

- `folder-readme-root` — instance root README (singleton per instance).
- `folder-readme-container` — for folders that index child folders.
- `folder-readme-item` — for a specific child inside a container.
- `folder-readme-asset` — for sibling-level asset libraries that are sources of truth in their own right.
- `brief-company` — singleton company identity brief.
- `brief-client` — per-client CRM-flavored brief.
- `brief-stakeholder` — per-person brief for a primary stakeholder at a client. Lives at `Clients/<client>/Stakeholders/<kebab-name>.md`.
- `client-manifest` — per-client lookup index for matching transcripts and communications to the correct client. Lives in each client folder as `manifest.md`.
- `dashboard-company` — singleton company state record. Lives at the instance root as `dashboard.md`. Companion to `brief-company`: the brief is stable (who the company is), the dashboard is volatile (what it's doing right now).
- `agent-ignore` — singleton skip-rule reference (see [`agent-ignore.md`](agent-ignore.md)).
- `progress-checkpoint` — point-in-time snapshots of how an ACOS instance is being built. Stored under `_progress/`, which is itself out of scope per [agent-ignore](#agent-ignore).

Add a new `type` only when none of the above fits, and document it here when you do.

### Lateral cascade — always-on references

The [Read order](#read-order) above describes the **hierarchical cascade** — which README to read based on *where* the work is happening. Some references must be read regardless of folder location, triggered by *what kind of task* is being done. These are **lateral cascade** references.

| Reference | Triggered by | Why it's lateral |
|---|---|---|
| [`agent-ignore.md`](agent-ignore.md) | Any folder traversal, any task that walks the tree, any time before listing or reading folder contents. | The skip rule applies regardless of where in the tree the work is happening; it should be honored before any other reading begins. |
| Brand asset README (when an instance has one) | Any task producing a client-facing or polished artifact: proposals, decks, Word docs, PDFs, web, marketing copy, social. | Brand applies to output regardless of which client folder, product folder, or project the work lives in. |
| Instance `company-brief.md` | Any task producing writing in the company's voice: proposals, outreach, marketing copy, positioning, public statements, hire pitches. | Voice and positioning apply to everything the company says publicly, not just one folder's worth of work. |

Lateral references are powerful precisely because they're rare. Don't add a new one casually — the bar is "this thing applies to a class of tasks regardless of where they live." When in doubt, prefer adding a hierarchical reference (a folder README) over inventing a new lateral one.

### Briefs — the substantive companion to READMEs

Some folders also contain a `brief.md` — substantive content about the *thing the folder represents*. Briefs complement READMEs: the README is the operational front door (what's here, where to look), and the brief is the substantive record (history, contacts, content, positioning).

Three brief patterns exist today, all with templates in [`templates/`](templates/):

| Brief pattern | Used for | Template | Instance location |
|---|---|---|---|
| **Company brief** | Singleton — identity content about the company itself | [`templates/brief-company.md`](templates/brief-company.md) | `<instance-root>/company-brief.md` |
| **Client brief** | Per-client — relationship content (CRM-style contacts, engagement history, opportunities, interaction log) | [`templates/brief-client.md`](templates/brief-client.md) | `Clients/<client>/brief.md` (one per client) |
| **Stakeholder brief** | Per-person — the rolling 1:1 history and personal context for a *primary stakeholder*, kept out of the client brief so it doesn't bloat the organizational record | [`templates/stakeholder-brief.md`](templates/stakeholder-brief.md) | `Clients/<client>/Stakeholders/<kebab-name>.md` |

Only promote a contact to a stakeholder brief when they're a decision-maker, a recurring 1:1 partner, or someone whose personal context materially shapes the engagement. The client brief stays the source of truth for the *organization*; a stakeholder brief is scoped to one *person*.

Client folders also contain a **manifest** — a lookup index used by skills like [`client-brief-processor`](skills/client-brief-processor/SKILL.md) to route transcripts and communications to the correct client:

| Manifest pattern | Used for | Template | Instance location |
|---|---|---|---|
| **Client manifest** | Per-client — company identifiers, contact names, email domains, project keywords for transcript routing | [`templates/manifest-client.md`](templates/manifest-client.md) | `Clients/<client>/manifest.md` (one per client) |

When an Item README and a brief live in the same folder, the brief is the source of truth for substantive content. The README's "People" and "Open threads" sections shrink to pointers in that case — see [`templates/folder-readme-item.md`](templates/folder-readme-item.md) for how that's wired.

## Dashboards — the singleton state record

An ACOS instance optionally maintains a **dashboard** at `<instance-root>/dashboard.md` — a singleton companion to the company brief. Where the brief carries identity (who the company is, what it sells, how engagements run), the dashboard carries *current state* (what's active, what's about to slip, what the principal needs to look at this week). Briefs are stable. Dashboards decay.

| Pattern | Used for | Template | Instance location |
|---|---|---|---|
| **Company dashboard** | Singleton — the morning-glance state record for the instance | [`templates/dashboard-company.md`](templates/dashboard-company.md) | `<instance-root>/dashboard.md` |

The dashboard is kept current by the [`dashboard-refresh`](skills/dashboard-refresh/SKILL.md) skill, which re-rolls the file on a cadence (daily 6am local by default, overlay-overridable) by reading briefs and READMEs across the instance and rolling them up into structured sections. A slower companion skill, [`dashboard-tune`](skills/dashboard-tune/SKILL.md), runs on a monthly cadence and proposes layout refinements based on the Layout notes journal at the bottom of the dashboard.

Two non-obvious properties worth knowing:

- **Markdown is canonical, renders are views.** The `dashboard.md` file is the source of truth. Rendered views — a Cowork artifact, an HTML export, a PDF, a printed snapshot — are presentation layers over the same content, refreshed downstream of the markdown. An instance may have multiple render destinations; they all read from the one markdown source.
- **The refresh is conservative, not destructive.** Hand-edited blocks (the at-a-glance narrative, the Layout notes journal, any section explicitly pinned) are preserved across refreshes. Structured sections — active clients, pipeline, projects, products, open commitments — are re-rolled from their source files. See the skill spec for the full preservation contract.

The dashboard is one of the first artifacts a new instance benefits from once briefs and READMEs are in place. It's also where the framework house rule on [instance branding](#instance-branding-on-dashboards) applies: any rendered view of the dashboard must apply the instance brand tokens.

## Skills and overlays

ACOS skills are reusable agent capabilities — markdown documents (`SKILL.md`) that describe how an AI agent should perform a recurring task against an ACOS instance. Each skill lives in its own folder under [`skills/`](skills/) and is framework-level: it should work against any company that adopts ACOS conventions.

Instances customize skills via **overlays** — small files in `<instance-root>/overlays/<skill-name>.md` that provide instance-specific configuration (account names, API keys, folder paths, naming quirks, routing rules) without forking the skill itself.

### Overlay convention

The convention every ACOS skill follows:

- The framework skill is self-sufficient — it can operate without any overlay.
- Skills look for an overlay at `<instance-root>/overlays/<skill-name>.md` and load it if present.
- The instance root is the folder containing `company-brief.md`. An agent walks up from the working directory until it finds that file.
- Overlays may **add** configuration but should not **change** the skill's behavior in ways that contradict the framework skill.
- If an overlay needs to change framework behavior, that's a signal the framework skill itself needs to be improved.

See [`../docs/extending-acos.md`](../docs/extending-acos.md) for the full conventions for adding new skills.

## House rules

Conventions that apply across every ACOS instance. AI tools should follow these by default unless a folder's own README overrides them. These rules exist so that **multiple agents working in different folders behave consistently** — any tool reading this section should treat the rules below as binding.

### Agent-ignore — skip underscore-prefixed folders

Folders whose name begins with an underscore are **out of scope for AI work** by default. The signal is the prefix itself; the canonical rule, the reasoning, and the patterns live in [`agent-ignore.md`](agent-ignore.md), which is a lateral-cascade reference and should be honored before any folder traversal begins.

Currently this covers `_archive/` (retired material) and `_progress/` (instance build-out checkpoints, for the maintainer's reference). Any future underscore-prefixed folder inherits the same default treatment without needing this README to be updated.

The only override is an explicit in-conversation instruction from a human to look into a specific underscore-prefixed folder for a specific reason.

### `templates/` — reusable building blocks

Any folder named `templates/` (at any depth) holds **reusable artifacts** for the folder it sits in. Use it.

- When creating something new (a client folder, a project doc, a product scaffold), check the nearest `templates/` first.
- When a pattern emerges that's worth reusing, propose adding it to the appropriate `templates/` rather than reinventing it next time.

### Brand pre-flight (when an instance has a Brand asset)

Before producing any client-facing or polished artifact, the agent must read the instance's `Brand/README.md` (or equivalent asset README) and apply the relevant design tokens. This rule is **binding regardless of where the work is happening in the tree** — it's a lateral cascade rule.

Trigger artifact types (non-exhaustive):

- Proposals, statements of work, contracts, engagement letters
- PowerPoint decks, presentations, slide artifacts (PPTX)
- Word documents (DOCX) — reports, memos, briefs, leave-behinds
- PDF outputs, whether generated programmatically or exported
- Marketing copy, positioning content, social posts
- Web pages, dashboards, HTML artifacts
- Logo or visual asset embedding in any deliverable

If you're unsure whether a task qualifies, ask. Brand consistency across collateral is a more visible failure than almost any other operational drift, so the bias is toward over-applying, not under-applying. If the instance does not have a Brand asset library, this rule is inert.

### Instance branding on dashboards

The instance dashboard ([`<instance-root>/dashboard.md`](#dashboards--the-singleton-state-record)) is one of the first artifacts the company sees of itself. If the instance has a Brand asset library, the dashboard's *rendered views* — Cowork artifacts, HTML or PDF exports, printed snapshots, any other presentation layer over the markdown source — apply the instance brand tokens by default. The markdown source stays brand-neutral (content, not styling); every rendered view is brand-pre-flighted.

- *Why:* The dashboard is high-visibility internal collateral the principal looks at daily. It's exactly the artifact where brand consistency builds reflexive recognition over time, and exactly the artifact whose drift would be noticed first.
- *How to apply:* The markdown `dashboard.md` is exempt — it carries no styling. Any skill, agent, or human producing a rendered view of the dashboard reads the instance's Brand asset README first and applies tokens accordingly. If the instance declares a render destination but has no Brand asset library, surface the gap rather than improvising styling.

### Folder naming — no spaces, use dashes

New folders should use **`kebab-case`** — words separated by dashes, no spaces.

- Good: `acme-industries/`, `q3-strategy-review/`
- Avoid: `Acme Industries/`, `Q3 Strategy Review/`

Some legacy folders may predate this rule and still contain spaces. Don't rename them on sight — they're load-bearing in scripts, links, and references — but apply the rule to anything new.

### Markdown style

Generated and edited markdown files across an ACOS instance follow these rules so the system stays consistent across files and across agents. Apply silently; no need to ask permission per occurrence.

- **No horizontal-rule dividers (`---`) between sections.** Section headings (`##`, `###`) provide enough visual separation. The only place `---` should appear is as the YAML frontmatter delimiters at the very top of a file.
- **Straight quotes only.** Use `'` and `"`, never the curly variants. Straight quotes are grep-friendly, copy-paste-safe, and survive editor round-trips. If a tool inserts curly quotes, normalize them on the next edit.
- **Sentence case for section headings.** "What this folder is" — not "What This Folder Is." Acronyms and proper nouns keep their natural case.
- **Dashes for bullet lists** (`-`), not asterisks or plus signs.
- **ISO 8601 dates** (`2026-04-26`), not "April 26, 2026" or "4/26/2026."

### Principals — who agents escalate to

Every ACOS instance has at least one **principal** — a human on whose behalf agents act within the instance. The default approver when a skill needs human sign-off. Principals are declared in the instance's `company-brief.md` under `People` → `Principals` (see [`templates/brief-company.md`](templates/brief-company.md)).

- **Single-principal instances** list one principal, who is automatically the primary stakeholder.
- **Multi-principal instances** list multiple principals and **must designate exactly one as primary stakeholder** — the final escalation point when domain-specific routing doesn't apply or consensus isn't reachable. Each principal may have a scoped decision authority (e.g., brand decisions route to a design lead, engagement sign-off to the founder).

Skills that produce draft artifacts requiring verification resolve "the principal" at runtime by reading `company-brief.md`. They never hardcode names. The resolution order is single-principal → primary stakeholder → maintainer fallback. Skills may consult an instance overlay if domain-specific routing is configured (e.g., a `client-brand-capture.md` overlay specifying that brand sign-off routes to the design principal rather than the primary stakeholder).

This convention exists so the framework remains portable across instances of every size, from one-person operating companies to multi-principal partnerships and agencies. Hardcoded names in skill prose are a framework bug.

### Companion plugins — optional skill enhancements

Some skills work better when a complementary plugin is available in the running environment but **must not depend on one**. The companion-plugin convention lets a skill detect an optional partner at runtime and use it opportunistically. See [`companion-plugins.md`](companion-plugins.md) for the full rule, the SKILL.md section convention, and detection examples.

A skill that breaks when a companion isn't installed is a framework bug. Skills declare companions; they don't require them.

### Meta — capture ambiguity here

When an agent encounters a stylistic, structural, or behavioral choice that could plausibly be made multiple defensible ways — and no rule in this file yet covers it — surface the question, get a human decision, and **codify the answer here as a binding rule** rather than carrying it only in conversation memory or session-level notes. The point of ACOS is that the next agent shouldn't have to relitigate the same micro-decision.

Common surfaces where this comes up: markdown formatting, voice and tone in client-facing writing, file naming, when to ask vs. act, default deliverable formats, frontmatter conventions. If you notice a recurring micro-decision being made implicitly, write it down.

Instances may capture instance-specific ambiguity in their own README; framework-level ambiguity goes here.

## How to extend ACOS

When a new convention, pattern, or operating rule emerges from real work, capture it here rather than letting it live only in chat. See [`../docs/extending-acos.md`](../docs/extending-acos.md) for the full conventions, including:

- The decision rule for framework-vs-instance changes.
- The promotion path for moving a pattern from one instance into ACOS.
- How to add a new skill, a new template, or a new README pattern.
- Backwards-compatibility expectations as the framework evolves.

## Versioning and maintenance

- **Version:** 0.1 (initial extraction from tPPOS)
- **Last updated:** 2026-07-12
- **Maintainer:** Steven Jones (sjones@theproductpath.com)
- **Status:** Active. Published at v0.1 and in production use in the tPPOS reference instance — the rules in this file are binding, not provisional. The framework is still young: expect additive change as patterns get promoted out of instances, and read [`../docs/extending-acos.md`](../docs/extending-acos.md) before making any.
