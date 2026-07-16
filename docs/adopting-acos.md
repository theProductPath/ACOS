---
type: acos-doc
subject: adopting-acos
status: active
last-updated: 2026-07-16
maintainer: Steven Jones
purpose: Guide for a new company adopting ACOS — the small day-one core you stand up by hand, and the growth path agents carry from there. Written from the settled framework and the tPPOS reference instance.
---

# Adopting ACOS

This guide takes you from an ordinary folder tree to a working ACOS instance — a company that any AI agent can read, orient itself in, and act on without being re-taught every time. It's written for the person setting up a new instance, not for contributors extending the framework itself (that's [`extending-acos.md`](extending-acos.md)).

ACOS is a company context system, not a documentation project. You are not going to sit down and write your whole company out. You stand up a **small day-one core** — a front door, an identity, one folder that matters — and from there your agents grow the instance as real work demands it. In the tPPOS reference instance, roughly 95% of the supporting records were created by agents in the course of the work, not by a human up front. So don't read this as a wall of setup; read it as one short sitting, then a growth path.

You don't need to read the whole framework manual first. Skim [`../framework/README.md`](../framework/README.md) for the vocabulary, then work through the day-one core below.

Two notes on what you will and won't find here. Every pattern this guide asks you to create has a template in [`../framework/templates/`](../framework/templates/) — that's the worked example, and it's the one you copy. The framework's first instance, tPPOS, is theProductPath's own company tree: it's private, it doesn't ship with ACOS, and this guide will never tell you to go read it. If a step is unclear, the gap is in the template or in this doc, and it's worth [raising](https://github.com/theProductPath/ACOS/issues) rather than working around.

## What ACOS asks of you

ACOS is deliberately thin. It assumes three things and provides the rest — the README patterns, the templates, the skills, and the house rules all come from the framework.

- **A synced folder tree.** Google Drive, OneDrive, Dropbox, or a git repo all work equally well — ACOS never touches the storage layer.
- **Tools that read markdown.** Any model or platform that can read markdown and walk a folder tree can use an ACOS instance.
- **A seed of judgment.** You supply the identity, the scope, and the decision-makers. Agents document the rest as the work happens — you're not signing up to write it all down yourself.

## The shape of an instance

An ACOS instance has an **instance root** and a set of **sibling folders** that hold the slices of your business. The root is the front door every agent reads first; the siblings are where the actual work lives.

At the root you'll end up with a `README.md` (the entry point), a `company-brief.md` (your stable identity), an optional `dashboard.md` (your current state), and an optional `overlays/` directory (per-skill configuration). Alongside the root sit the folders that matter to your company — `Clients/`, `Products/`, `Projects/`, `Brand/`, `Research/`, or whatever you actually run on. You don't need all of them, and you can add more later.

Hold that picture in mind: the day-one core seeds that shape, and everything after it is filling the shape in as you go — mostly with agents doing the filling.

## Day one: the small core

Four steps, one sitting. The goal isn't finished documentation — it's agents working inside your company by the end of the day.

### Step 1 — Choose your tree and create the instance root

Pick the folder that will be the top of your company's operating tree. This is usually the root of a synced drive or a dedicated company folder. Inside it, the instance root is the folder that holds your identity and rules — often the same top folder, or a named subfolder like `companyOS/` if you want the operating layer visibly separate from the business folders.

Before you copy anything, decide **where the framework itself lives relative to your tree**, because every template you copy carries a `<path-to-acos>` placeholder you have to resolve. Three options, all fine: a **sibling clone** of the ACOS repo next to your tree (best if agents run locally with filesystem access to both); a **vendored copy** of `framework/` inside your tree (best if your tree syncs to machines that won't have the repo — the tradeoff is re-copying to take updates); or a **remote reference** to the repo on the web (best if your agents can fetch URLs, unreachable if they can't). Resolve `<path-to-acos>` the same way in every file and write the choice down in your root README's Links section — an agent that can't reach the framework manual has no rules to follow. The same applies to `scripts/acos-integrity-check.py`: it lives in the repo, so if you vendored only `framework/`, take `scripts/` too or run the checker from a clone.

Now create the root `README.md` by copying [`../framework/templates/folder-readme-root.md`](../framework/templates/folder-readme-root.md). Fill in what the instance is, list the sibling folders in scope, and point back at ACOS for the framework rules. This is the single most important file you'll write: it's what an agent reads before doing anything, and it decides where the agent goes next. Every README opens with a small YAML frontmatter block (`type`, `status`, `last-updated`, `maintainer`, `purpose`) — fill it in honestly so a future tool can report which files have gone stale without reading the prose. The legal `status` values come from the framework's [status vocabulary](../framework/README.md#status-vocabulary), and each template carries the ones valid for its type in a trailing comment.

**The `## Folder map` table is the membership allowlist, and it is load-bearing.** A folder is part of your operating system **if and only if** it has a row in that table — see [Membership](../framework/README.md#membership--what-is-part-of-the-operating-system) in the manual. Keep the heading spelled exactly `## Folder map`, keep it a table, and keep each folder's name in backticks in the first column. The integrity checker discovers your whole tree from this table and walks nothing that isn't in it. Two consequences make adoption much cheaper than it looks:

- **You are not adopting ACOS for your whole company.** You're adopting it for the folders you list. Everything else in the tree — the scanned receipts, the photo dumps, the folder someone made last Tuesday — is simply not in the OS. Not excluded, not ignored, not a finding. List one folder and the OS governs one folder.
- **Never write a list of folders to ignore.** An exclusion list rots the moment someone adds or deletes a folder, and then it lies to every agent that reads it. The allowlist can't rot: the only way in is a human writing a row.

On day one the folder map can be short — the root itself plus the one area you're about to instrument in Step 3. You add rows as you bring more of the tree into the OS.

### Step 2 — Fill in your company brief

Copy [`../framework/templates/brief-company.md`](../framework/templates/brief-company.md) to `<instance-root>/company-brief.md` and populate it. The brief is your company's canonical identity: positioning, what you offer, your voice, your defaults, and — importantly — your **principals**, the humans on whose behalf agents act and who they escalate to. If you have more than one principal, designate exactly one as the **primary stakeholder** so escalation is never ambiguous.

This is the one record worth real care on day one. It's stable content — it answers "who is this company and what does it sound like" — and it's read by any task that produces writing in your voice: proposals, outreach, marketing, positioning. A lot of downstream agent behavior keys off it.

### Step 3 — Instrument your first high-value area

Don't instrument everything. Pick the **one** folder where agents will do the most work — for most companies that's `Clients/` or `Products/` — and give it a README from the pattern that fits.

That first folder is almost always a **container**: a folder that holds many similar children (clients, products, projects). Copy [`../framework/templates/folder-readme-container.md`](../framework/templates/folder-readme-container.md) into it and declare `type: folder-readme-container` — that's how you tell agents its children are OS items and the cascade continues into them. Your container won't be named like the examples, and that's expected: the patterns are shapes, not a prescribed folder set. A clinic's containers are `Patients/` and `Suppliers/`; a manufacturer's might be `Lines/` and `Vendors/`. `Clients/` is the only name that carries extra machinery — briefs, manifests, and the client-facing skills — and only because it got built first; if your core entities aren't clients, you still get the cascade and the integrity checker, you just won't use those skills.

ACOS has four README shapes in all — **root** (you just used it), **container**, **item** (one specific child), and **asset** (a folder that *is* a source of truth, like a brand kit or a cabinet of scanned filings, whose children are material rather than OS items). You'll reach for item and asset as the instance grows; the full set is in [the manual](../framework/README.md#four-readme-patterns). For now, one container is enough. A folder you leave out costs you nothing — a folder inside a container with no README isn't a failure, it just hasn't opted into the OS, and the checker says so as information, not an error.

### Step 4 — Point an agent at the root and run the first check

Now prove the core works. Point an agent at your instance root and ask it to check the instance's health. The framework's [`acos-integrity`](../framework/skills/acos-integrity/SKILL.md) skill walks your tree and confirms your READMEs, frontmatter, and naming follow the rules — and to do that, the agent first has to orient itself through the cascade, exactly the way every future agent will. A clean report means your front door, brief, and container README are doing their jobs. Have the agent save the report under `_progress/` (an underscore-prefixed, [agent-ignored](../framework/README.md#agent-ignore--skip-underscore-prefixed-folders) folder) — and that's your instance's first agent-generated artifact, minutes after setup.

**That's the whole upfront ask.** Everything below happens as you operate — and mostly, agents do it.

## As you work: the instance grows

You keep working the way you always have. But now, when the work reveals a durable need, your agents fortify the instance with the right kind of record — inside the rules, with you supplying judgment and approvals — and every task that follows starts from a stronger foundation.

- **A new client engagement lands.** An agent scaffolds the client's item README and its **brief** — copy [`../framework/templates/brief-client.md`](../framework/templates/brief-client.md) into the folder as `brief.md`, and it becomes the source of truth for that relationship. When one contact becomes a decision-maker or recurring 1:1 partner, a **stakeholder brief** from [`../framework/templates/brief-stakeholder.md`](../framework/templates/brief-stakeholder.md) keeps their person-level history out of the organizational record. You review; the relationship record compounds from there.
- **Incoming material needs routing.** A **manifest** from [`../framework/templates/manifest-client.md`](../framework/templates/manifest-client.md) lists the identifiers — company aliases, contact names, email domains, project keywords — that let a skill match a stray transcript or email to the right client instead of guessing or inventing a new one. It's saved in the client folder as `manifest.md`.
- **Another area of the business matters.** Instrument it the way you did the first — a **container** if its children are things the OS manages, an **asset** library if they're material it merely stores. Getting that call right is the highest-leverage decision each time, because it sets what the OS expects one level down: mistype an asset library (a folder per year of receipts) as a container and you'll get a finding for every folder without a README, which is the checker faithfully reporting what you told it. Ask: *are this folder's children things the operating system manages, or material it merely stores?*
- **A company-specific quirk shows up.** It becomes an **overlay** at `<instance-root>/overlays/<skill-name>.md` — not a fork. The framework skill stays generic; your account names, paths, and routing quirks live in the overlay (frontmatter `type: skill-overlay`, `skill`, `instance`, `last-updated`, plus whatever the skill's own SKILL.md says it reads). The one most instances end up wanting is [`acos-integrity.md`](../framework/skills/acos-integrity/SKILL.md#instance-overlay-configuration), which tells the checker the few things it can't infer — which container holds your clients, which hold self-contained code repos, and any legacy folder names you've decided to live with. It's also where an instance may declare a naming policy (`naming-style: kebab-case` or `capitalized`) if it wants one; the framework ships no default and doesn't care about case, so most instances leave it out. If you ever want an overlay to *change* what a skill does rather than configure it, that's a signal the framework skill should improve — raise it.
- **A recurring choice gets settled.** A **decision record** preserves why, the alternatives considered, and when to revisit — so future agents don't blindly reopen a settled question.
- **A deliverable repeats itself.** It becomes a **template** — the next proposal, invoice, or client area starts from a proven shape instead of a blank page.
- **You want a morning glance.** Add a `dashboard.md` at the instance root from [`../framework/templates/dashboard-company.md`](../framework/templates/dashboard-company.md). Where the company brief carries stable identity, the dashboard carries current state — what's active, what's about to slip, what needs a principal this week. The [`dashboard-refresh`](../framework/skills/dashboard-refresh/SKILL.md) skill re-rolls its structured sections on a cadence while preserving your hand-written narrative. The markdown stays canonical; any rendered view — an HTML export, a printed snapshot, a live artifact — is a presentation layer over that one source.

ACOS never asks you to predict every record your company will need. It gives agents the vocabulary and the rules to add the right kind of record when the work reveals the need — and each one leaves the company better documented than the task found it.

## Adoption checklist

Two lists: what you do on day one, and what accrues over time — most of it agent-built. When you've done the day-one set, run the integrity checker; a freshly-scaffolded core should come back clean, and if it doesn't, either an item below is missing or the framework has a bug — [raise it](https://github.com/theProductPath/ACOS/issues) either way.

**Day one — you:**

- ACOS itself reachable from the tree (sibling clone, vendored copy, or remote), with `<path-to-acos>` resolved consistently in every file.
- Instance root chosen, with a `README.md` from the root template and a `## Folder map` table listing the root and your first in-scope area — and no list of folders to *exclude*, ever.
- `company-brief.md` populated, with at least one principal and a designated primary stakeholder.
- A container README on your first high-value folder, typed honestly.
- First integrity check run, with the report saved by the agent under `_progress/`.

**Earned over time — mostly agent-built:**

- Item READMEs, briefs, and manifests on active clients or products; stakeholder briefs where a person's history warrants one.
- Overlays for anything company-specific; an `overlays/acos-integrity.md` declaring your client container and asset folders.
- Decision records where recurring choices got settled; templates for repeated deliverables.
- `dashboard.md` in place and on a refresh cadence.
- House rules honored throughout: straight quotes, sentence-case headings, ISO dates, underscore-prefixed folders (`_archive/`, `_progress/`) left out of scope, and no [breaking characters](../framework/README.md#folder-naming--structure-not-style) in folder names. Note what is *not* on this list: **letter case**. ACOS has no opinion on it — capitalize your folders or don't.

## Where to go next

- Read the full [framework manual](../framework/README.md) for the cascade rules, frontmatter taxonomy, and house rules in depth.
- When a pattern isn't obvious, go back to its template in [`../framework/templates/`](../framework/templates/) — each one carries `> **TODO:**` blocks describing what good content looks like in that section.
- Check your instance against the conventions with the [`acos-integrity`](../framework/skills/acos-integrity/SKILL.md) skill, or with `scripts/acos-integrity-check.py` — a read-only validator you can run from anywhere inside the tree (it walks up to find `company-brief.md`).
- Register your instance in [`../instances/README.md`](../instances/README.md) if you'd like it tracked alongside the reference implementation.
- When you start extending the framework rather than just adopting it, switch to [`extending-acos.md`](extending-acos.md).

## Related

- Framework manual: [`../framework/README.md`](../framework/README.md)
- Templates: [`../framework/templates/`](../framework/templates/)
- Skills: [`../framework/skills/`](../framework/skills/)
- Extension conventions (for contributors): [`extending-acos.md`](extending-acos.md)
- Known instances: [`../instances/README.md`](../instances/README.md)
