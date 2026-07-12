---
type: acos-doc
subject: adopting-acos
status: active
last-updated: 2026-07-12
maintainer: Steven Jones
purpose: Guide for a new company adopting ACOS — how to scaffold an instance, fill in the templates, wire in skills, and point agents at the tree. Written 2026-07-07 from the settled framework and the tPPOS reference instance.
---

# Adopting ACOS

This guide takes you from an ordinary folder tree to a working ACOS instance — a company that any AI agent can read, orient itself in, and act on without being re-taught every time. It's written for the person setting up a new instance, not for contributors extending the framework itself (that's [`extending-acos.md`](extending-acos.md)).

You don't need to read the whole framework manual first. Skim [`../framework/README.md`](../framework/README.md) for the vocabulary, then work through the steps below.

Two notes on what you will and won't find here. Every pattern this guide asks you to create has a template in [`../framework/templates/`](../framework/templates/) — that's the worked example, and it's the one you copy. The framework's first instance, tPPOS, is theProductPath's own company tree: it's private, it doesn't ship with ACOS, and this guide will never tell you to go read it. If a step is unclear, the gap is in the template or in this doc, and it's worth [raising](https://github.com/theProductPath/ACOS/issues) rather than working around.

## What ACOS asks of you

ACOS is deliberately thin. Before you start, know that it assumes three things and provides the rest:

- You keep your company's working context in a synced folder tree. Google Drive, OneDrive, Dropbox, or a git repo all work equally well — ACOS never touches the storage layer.
- Your AI tools can read markdown and walk a folder tree. Any model or platform that can do that can use an ACOS instance.
- You're willing to write down how your company works, once, so agents stop guessing.

Everything else — the README patterns, the templates, the skills, the house rules — comes from the framework. You bring storage, tooling, and content.

## The shape of an instance

An ACOS instance has an **instance root** and a set of **sibling folders** that hold the slices of your business. The root is the front door every agent reads first; the siblings are where the actual work lives.

At the root you'll end up with a `README.md` (the entry point), a `company-brief.md` (your stable identity), an optional `dashboard.md` (your current state), and an optional `overlays/` directory (per-skill configuration). Alongside the root sit the folders that matter to your company — `Clients/`, `Products/`, `Projects/`, `Brand/`, `Research/`, or whatever you actually run on. You don't need all of them, and you can add more later.

Hold that picture in mind: everything below is just filling that shape in, in an order that keeps you unblocked.

## Step 0 — Decide where ACOS itself lives

Before you copy a single template, decide where the framework sits relative to your tree, because every template you're about to copy carries a `<path-to-acos>` placeholder that you have to resolve. Three options, all fine:

- **Sibling clone.** Clone the ACOS repo next to your company tree and point at it with a relative path. Best if your agents run locally with filesystem access to both.
- **Vendored copy.** Copy `framework/` into your tree (many instances put it at `<instance-root>/acos/`). Best if your tree syncs to machines that won't have the repo — the tradeoff is that you have to re-copy it to take framework updates.
- **Remote reference.** Link to the ACOS repo on the web. Best if your agents can fetch URLs; worst if they can't, because then the framework rules are unreachable from inside the tree.

Whichever you pick, resolve `<path-to-acos>` the same way in every file, and write the choice down in your instance root README's Links section. An agent that cannot reach the framework manual from your tree has no rules to follow.

The same question applies to `scripts/acos-integrity-check.py`: it lives in the ACOS repo, not in your tree. If you vendored only `framework/`, you don't have the checker — take `scripts/` too, or run it from a clone.

## Step 1 — Choose the tree and create the instance root

Pick the folder that will be the top of your company's operating tree. This is usually the root of a synced drive or a dedicated company folder. Inside it, the instance root is the folder that holds your identity and rules — often the same top folder, or a named subfolder like `companyOS/` if you want the operating layer visibly separate from the business folders.

Create the root `README.md` by copying [`../framework/templates/folder-readme-root.md`](../framework/templates/folder-readme-root.md). Fill in what the instance is, list the sibling folders that are in scope, and point back at ACOS for the framework rules. This file is the single most important one you'll write: it's what an agent reads before doing anything, and it decides where the agent goes next.

Every README opens with a small YAML frontmatter block (`type`, `status`, `last-updated`, `maintainer`, `purpose`). Fill those in honestly as you go — they're what lets a future tool report which files have gone stale without reading the prose. `status` comes from the framework's [status vocabulary](../framework/README.md#status-vocabulary); each template's `status:` line carries the values legal for that document type in a trailing comment. Leave the comment or delete it — tools ignore it either way.

**The `## Folder map` table is machine-read, and it is the only thing that tells a tool which folders exist.** Keep the heading spelled exactly `## Folder map`, keep it a table, and keep each folder's name in backticks in the first column (`` | `Clients/` | … | ``). The integrity checker discovers your whole tree from this table and walks nothing that isn't in it; reformat it into bullets and every downstream tool goes blind. Include a row for the instance root itself.

## Step 2 — Fill in the company brief

Copy [`../framework/templates/brief-company.md`](../framework/templates/brief-company.md) to `<instance-root>/company-brief.md` and populate it. The brief is your company's canonical identity: positioning, what you offer, your voice, your defaults, and — importantly — your **principals**, the humans on whose behalf agents act and who they escalate to.

The brief is stable content. It answers "who is this company and what does it sound like," and it's read by any task that produces writing in your voice — proposals, outreach, marketing, positioning. Get this right early, because a lot of downstream agent behavior keys off it. If you have more than one principal, designate exactly one as the primary stakeholder so escalation is never ambiguous.

## Step 3 — Instrument your operating folders

Now walk your sibling folders and give each one a README, choosing the pattern that fits what the folder is. ACOS uses four shapes, each with a template in [`../framework/templates/`](../framework/templates/):

- Use the **container** pattern for folders that hold many similar children — `Clients/`, `Products/`, `Projects/`. The README is an index of children plus the conventions every child follows.
- Use the **item** pattern for a specific child inside a container — one client, one product. The README is curated context for that one thing.
- Use the **asset** pattern for a folder that is itself a source of truth — a brand kit, design tokens, a shared script library. The README is the substance, not an index.
- The **root** pattern you already used in step 1.

Your containers will not be the ones in the examples, and that's expected. The four README patterns are shapes, not a prescribed folder set: a clinic's containers are `Patients/` and `Suppliers/` and `Staff/`; a manufacturer's might be `Lines/` and `Vendors/`. `Clients/` is the only container name that carries extra machinery (briefs, manifests, and the client-facing skills), and only because that's the pattern that got built first. If your business's core entities aren't clients, you still get the README cascade and the integrity checker; you just won't use those skills.

You do not have to instrument everything at once. Start with the one or two folders where agents will do the most work and add the rest as you go — but be aware of the boundary the integrity checker draws: it walks every folder listed in your folder map and every direct child of those folders, and it reports a **missing README as a failure**. So an un-instrumented folder inside a declared container isn't free — it's a finding. Either give it a README or leave its parent out of the folder map until you're ready. Anything deeper than one level below a container is not walked at all, and is yours to organize however you like.

## Step 4 — Add briefs and manifests where the work is substantive

READMEs are operational front doors. When a folder needs to carry real substance — relationship history, contacts, engagement state — add a **brief** alongside the README. The clearest case is a client: copy [`../framework/templates/brief-client.md`](../framework/templates/brief-client.md) into each active client folder as `brief.md`, and it becomes the source of truth for that relationship.

If agents will route incoming material (transcripts, emails, notes) to the right client, also add a **manifest** from [`../framework/templates/manifest-client.md`](../framework/templates/manifest-client.md). The manifest lists the identifiers — company aliases, contact names, email domains, project keywords — that let a skill match a stray transcript to the correct client instead of guessing or inventing a new one.

The rule of thumb: README for "what's here and where to look," brief for "the substantive record," manifest for "how to route things to this folder."

## Step 5 — Wire in skills and overlays

ACOS ships a library of reusable agent capabilities in [`../framework/skills/`](../framework/skills/) — brief processing, brand capture, dashboard refresh and tune, integrity checks, README refresh. Each is a `SKILL.md` that works against any ACOS instance out of the box. Make them available to whatever agent tooling your company uses (how you install a skill depends on the tool).

When a skill needs to know something specific to your company — an account name, a folder path, a routing quirk — you don't fork the skill. You write a small **overlay** at `<instance-root>/overlays/<skill-name>.md` that adds that configuration. The framework skill stays generic; your specifics live in the overlay. If you ever find yourself wanting an overlay to *change* what a skill does rather than configure it, that's a signal the framework skill itself should improve — raise it rather than working around it.

There is no overlay template; an overlay is just a markdown file with frontmatter (`type: skill-overlay`, `skill`, `instance`, `last-updated`) and whatever configuration the skill's own SKILL.md says it reads. Each skill documents its own overlay keys — read the skill before writing its overlay.

The one overlay most instances end up wanting is [`acos-integrity.md`](../framework/skills/acos-integrity/SKILL.md#instance-overlay-configuration), which tells the integrity checker the handful of things it cannot infer: which container holds your clients, which folders are asset libraries, which containers hold self-contained code repos, and which legacy folder names you've decided to live with. Its config goes in a fenced ` ```acos-config ` block. The checker runs without it — it just has to guess — so write the overlay once the shape of your tree is settled.

## Step 6 — Stand up the dashboard

Once briefs and READMEs exist, add a `dashboard.md` at the instance root from [`../framework/templates/dashboard-company.md`](../framework/templates/dashboard-company.md). Where the company brief carries stable identity, the dashboard carries current state — what's active, what's about to slip, what needs a principal's attention this week. It's the morning-glance record, and it's one of the first artifacts a new instance actually benefits from.

The [`dashboard-refresh`](../framework/skills/dashboard-refresh/SKILL.md) skill keeps it current by re-rolling structured sections from your briefs and READMEs on a cadence, while preserving your hand-written narrative. Remember the ACOS principle here: the markdown is canonical, and any rendered view — an HTML export, a printed snapshot, a live artifact — is a presentation layer over that one source.

## Step 7 — Point your agents at the root

With the tree instrumented, the workflow is simple and the same for every agent: read the instance root README first, cascade down into the folder the task touches, follow the house rules, and surface ambiguity instead of guessing. An agent dropped deep in the tree still walks up to the root and back down, in order.

From here, the system compounds. Improve a rule once and every agent, on every model, inherits it. Prove a pattern in your instance and — if it's general enough — promote it into the framework so the next adopter gets it for free.

## Adoption checklist

Work through this and then run the integrity checker. A freshly-scaffolded instance that followed this guide should come back clean; if it doesn't, either the checklist below is short an item or the framework has a bug — [raise it](https://github.com/theProductPath/ACOS/issues) either way.

- ACOS itself reachable from the tree (sibling clone, vendored copy, or remote), and `<path-to-acos>` resolved consistently in every file.
- Instance root chosen, with a `README.md` from the root template listing in-scope siblings.
- `company-brief.md` populated, with at least one principal and a designated primary stakeholder.
- A `## Folder map` table in the root README, in the exact format above, with a row for every in-scope sibling and for the root itself.
- Container READMEs on every folder in the map, and an item README on every direct child of one — a child without a README is a checker failure, not a blank.
- `brief.md` and `manifest.md` on every client folder.
- ACOS skills made available to your agent tooling, with overlays for anything company-specific.
- An `overlays/acos-integrity.md` declaring your asset folders and client container, so the checker isn't guessing.
- `dashboard.md` in place and on a refresh cadence.
- `scripts/acos-integrity-check.py --strict` run against the tree, and clean.
- House rules honored: [folder naming](../framework/README.md#folder-naming--three-buckets) (Capitalized containers, proper-name items, kebab-case for everything else, and never a space or an underscore), straight quotes, sentence-case headings, ISO dates, and underscore-prefixed folders (`_archive/`, `_progress/`) left out of scope.

## Where to go next

- Read the full [framework manual](../framework/README.md) for the cascade rules, frontmatter taxonomy, and house rules in depth.
- When a pattern isn't obvious, go back to its template in [`../framework/templates/`](../framework/templates/) — each one carries `> **TODO:**` blocks describing what good content looks like in that section.
- Check your own instance against the conventions with the [`acos-integrity`](../framework/skills/acos-integrity/SKILL.md) skill, or with `scripts/acos-integrity-check.py` — a read-only validator, run from anywhere inside your instance tree (it walks up to find `company-brief.md`).
- Register your instance in [`../instances/README.md`](../instances/README.md) if you'd like it tracked alongside the reference implementation.
- When you start extending the framework rather than just adopting it, switch to [`extending-acos.md`](extending-acos.md).

## Related

- Framework manual: [`../framework/README.md`](../framework/README.md)
- Templates: [`../framework/templates/`](../framework/templates/)
- Skills: [`../framework/skills/`](../framework/skills/)
- Extension conventions (for contributors): [`extending-acos.md`](extending-acos.md)
- Known instances: [`../instances/README.md`](../instances/README.md)
