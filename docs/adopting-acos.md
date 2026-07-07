---
type: acos-doc
subject: adopting-acos
status: drafting
last-updated: 2026-07-07
maintainer: Steven Jones
purpose: Guide for a new company adopting ACOS — how to scaffold an instance, fill in the templates, wire in skills, and point agents at the tree. Written 2026-07-07 from the settled framework and the tPPOS reference instance.
---

# Adopting ACOS

This guide takes you from an ordinary folder tree to a working ACOS instance — a company that any AI agent can read, orient itself in, and act on without being re-taught every time. It's written for the person setting up a new instance, not for contributors extending the framework itself (that's [`extending-acos.md`](extending-acos.md)).

You don't need to read the whole framework manual first. Skim [`../framework/README.md`](../framework/README.md) for the vocabulary, then work through the steps below. When you want to see any pattern fully populated, [tPPOS](../../../tPPOS/) — theProductPath's own instance — is the reference implementation.

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

## Step 1 — Choose the tree and create the instance root

Pick the folder that will be the top of your company's operating tree. This is usually the root of a synced drive or a dedicated company folder. Inside it, the instance root is the folder that holds your identity and rules — often the same top folder, or a named subfolder like `companyOS/` if you want the operating layer visibly separate from the business folders.

Create the root `README.md` by copying [`../framework/templates/folder-readme-root.md`](../framework/templates/folder-readme-root.md). Fill in what the instance is, list the sibling folders that are in scope, and point back at ACOS for the framework rules. This file is the single most important one you'll write: it's what an agent reads before doing anything, and it decides where the agent goes next.

Every README opens with a small YAML frontmatter block (`type`, `status`, `last-updated`, `maintainer`, `purpose`). Fill those in honestly as you go — they're what lets a future tool report which files have gone stale without reading the prose.

## Step 2 — Fill in the company brief

Copy [`../framework/templates/brief-company.md`](../framework/templates/brief-company.md) to `<instance-root>/company-brief.md` and populate it. The brief is your company's canonical identity: positioning, what you offer, your voice, your defaults, and — importantly — your **principals**, the humans on whose behalf agents act and who they escalate to.

The brief is stable content. It answers "who is this company and what does it sound like," and it's read by any task that produces writing in your voice — proposals, outreach, marketing, positioning. Get this right early, because a lot of downstream agent behavior keys off it. If you have more than one principal, designate exactly one as the primary stakeholder so escalation is never ambiguous.

## Step 3 — Instrument your operating folders

Now walk your sibling folders and give each one a README, choosing the pattern that fits what the folder is. ACOS uses four shapes, each with a template in [`../framework/templates/`](../framework/templates/):

- Use the **container** pattern for folders that hold many similar children — `Clients/`, `Products/`, `Projects/`. The README is an index of children plus the conventions every child follows.
- Use the **item** pattern for a specific child inside a container — one client, one product. The README is curated context for that one thing.
- Use the **asset** pattern for a folder that is itself a source of truth — a brand kit, design tokens, a shared script library. The README is the substance, not an index.
- The **root** pattern you already used in step 1.

You do not have to instrument everything at once. Start with the one or two folders where agents will do the most work — for most companies that's `Clients/` or `Products/` — and add the rest as you go. An unlabeled folder just means an agent has less context there, not that anything breaks.

## Step 4 — Add briefs and manifests where the work is substantive

READMEs are operational front doors. When a folder needs to carry real substance — relationship history, contacts, engagement state — add a **brief** alongside the README. The clearest case is a client: copy [`../framework/templates/brief-client.md`](../framework/templates/brief-client.md) into each active client folder as `brief.md`, and it becomes the source of truth for that relationship.

If agents will route incoming material (transcripts, emails, notes) to the right client, also add a **manifest** from [`../framework/templates/manifest-client.md`](../framework/templates/manifest-client.md). The manifest lists the identifiers — company aliases, contact names, email domains, project keywords — that let a skill match a stray transcript to the correct client instead of guessing or inventing a new one.

The rule of thumb: README for "what's here and where to look," brief for "the substantive record," manifest for "how to route things to this folder."

## Step 5 — Wire in skills and overlays

ACOS ships a library of reusable agent capabilities in [`../framework/skills/`](../framework/skills/) — brief processing, brand capture, dashboard refresh and tune, integrity checks, README refresh. Each is a `SKILL.md` that works against any ACOS instance out of the box. Make them available to whatever agent tooling your company uses (how you install a skill depends on the tool).

When a skill needs to know something specific to your company — an account name, a folder path, a routing quirk — you don't fork the skill. You write a small **overlay** at `<instance-root>/overlays/<skill-name>.md` that adds that configuration. The framework skill stays generic; your specifics live in the overlay. If you ever find yourself wanting an overlay to *change* what a skill does rather than configure it, that's a signal the framework skill itself should improve — raise it rather than working around it.

## Step 6 — Stand up the dashboard

Once briefs and READMEs exist, add a `dashboard.md` at the instance root from [`../framework/templates/dashboard-company.md`](../framework/templates/dashboard-company.md). Where the company brief carries stable identity, the dashboard carries current state — what's active, what's about to slip, what needs a principal's attention this week. It's the morning-glance record, and it's one of the first artifacts a new instance actually benefits from.

The [`dashboard-refresh`](../framework/skills/dashboard-refresh/SKILL.md) skill keeps it current by re-rolling structured sections from your briefs and READMEs on a cadence, while preserving your hand-written narrative. Remember the ACOS principle here: the markdown is canonical, and any rendered view — an HTML export, a printed snapshot, a live artifact — is a presentation layer over that one source.

## Step 7 — Point your agents at the root

With the tree instrumented, the workflow is simple and the same for every agent: read the instance root README first, cascade down into the folder the task touches, follow the house rules, and surface ambiguity instead of guessing. An agent dropped deep in the tree still walks up to the root and back down, in order.

From here, the system compounds. Improve a rule once and every agent, on every model, inherits it. Prove a pattern in your instance and — if it's general enough — promote it into the framework so the next adopter gets it for free.

## Adoption checklist

- Instance root chosen, with a `README.md` from the root template listing in-scope siblings.
- `company-brief.md` populated, with at least one principal and a designated primary stakeholder.
- Container READMEs on the folders where agents will work most.
- Item READMEs and `brief.md` files on active clients or products.
- Manifests on any folder that needs incoming material routed to it.
- ACOS skills made available to your agent tooling, with overlays for anything company-specific.
- `dashboard.md` in place and on a refresh cadence.
- House rules honored: kebab-case folder names, straight quotes, sentence-case headings, ISO dates, and underscore-prefixed folders (`_archive/`, `_progress/`) left out of scope.

## Where to go next

- Read the full [framework manual](../framework/README.md) for the cascade rules, frontmatter taxonomy, and house rules in depth.
- Study [tPPOS](../../../tPPOS/) as a fully populated instance when a pattern isn't obvious from the template.
- When you start extending the framework rather than just adopting it, switch to [`extending-acos.md`](extending-acos.md).

## Related

- Framework manual: [`../framework/README.md`](../framework/README.md)
- Templates: [`../framework/templates/`](../framework/templates/)
- Skills: [`../framework/skills/`](../framework/skills/)
- Extension conventions (for contributors): [`extending-acos.md`](extending-acos.md)
- Reference instance: [`../../../tPPOS/`](../../../tPPOS/)
