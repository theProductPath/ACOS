---
type: acos-doc
subject: extending-acos
status: active
last-updated: 2026-07-12
maintainer: Steven Jones
purpose: Conventions for AI agents and contributors extending ACOS. Read this before adding a new skill, template, README pattern, or rule to the framework.
---

# Extending ACOS — conventions for contributors

This doc is for agents and humans adding to ACOS itself — new skills, new templates, new conventions. It's distinct from [`adopting-acos.md`](adopting-acos.md), which is for someone setting up a new company instance.

If you're an agent that just landed in this folder because a user asked you to extend or improve ACOS, read this file in full before you touch anything. The conventions are short on purpose.

## The framework-vs-instance rule

Every change either belongs in **ACOS** (the framework — this repo) or in an **instance** (a specific company's adoption of it, such as theProductPath's own tPPOS tree). Almost every mistake comes from putting a change in the wrong place. The rule:

- A change belongs in **ACOS** when it would be useful to *another* company adopting the framework. New skills, refined cascade rules, new template patterns, sharper rules for when to ask vs. act, frontmatter conventions, README patterns.
- A change belongs in the **instance** when it's specific to that company. New client manifest entries, account-specific overlays, tone rules tuned to one company's voice, project keywords that emerged from real work with one client.

When you're unsure, ask the user. Don't guess.

### The promotion path

A pattern often starts as instance-specific and only later proves general. That's expected, not a failure of forethought. When a pattern that lives in an instance starts being useful for the framework:

1. **Notice the signal.** Two or more uses in the same instance, or one use that the user explicitly flags as reusable, is enough to start.
2. **Extract.** Pull the generic version into the appropriate ACOS location — `framework/skills/`, `framework/templates/`, or a section of `framework/README.md`. Scrub instance-specifics (names, paths, accounts, examples). Replace with placeholders.
3. **Leave a thin overlay.** Whatever residual instance-specificity remains stays in the instance — typically as an overlay in `<instance>/overlays/<thing>.md`.
4. **Update references.** Any file in the instance that pointed at the instance-version path needs to point at the ACOS path now. Use `Grep` to find them.
5. **Archive the old.** Move the instance-version files into `<instance>/_archive/<thing>-pre-promotion-YYYY-MM-DD/`. Don't delete — the audit trail is worth keeping.

### When something genuinely belongs only in the instance

Some things are forever instance-only and shouldn't be promoted. Examples:

- A client manifest entry — that client exists for that company, not the framework.
- A Gmail account or API credential — instance-only by definition.
- A subsidiary alias or routing quirk — instance-only unless the framework grows a "common quirk patterns" feature, which it currently does not.

For these, the instance overlay is the right home and the framework should stay agnostic.

## Adding a new skill

Skills live at `framework/skills/<skill-name>/SKILL.md` with supporting references in `<skill-name>/references/`. The naming and structure conventions:

### Conventions for the skill itself

- **Naming.** Skill folder is `kebab-case` and names a *capability*, not a tool. Good: `client-brief-processor`, `proposal-drafter`, `meeting-summarizer`. Avoid: `gmail-thing`, `notion-helper` (those name *tools*, not capabilities — the same skill might use different tools in different instances).
- **Frontmatter.** `name`, `description`. The description is what an LLM triggers on, so it should name the inputs the user is plausibly going to mention, not the internal phases of the skill. Avoid leaking internal scaffolding (like "Phase 1", "Phase 2") into the description.
- **Self-sufficiency.** The framework skill must work without any overlay. The overlay only adds *configuration* (accounts, paths, search syntax, routing quirks), never *behavior*. If an instance would need the skill to behave differently — not just to be configured differently — that's a signal the framework skill itself needs to change.
- **Overlay discovery.** Every skill that supports overlays uses the same convention: look for `<instance-root>/overlays/<skill-name>.md`, where instance root is the folder containing `company-brief.md`. Document this near the top of the SKILL.md, not as a buried footnote.
- **No instance-specific examples.** Don't write "the Acme account" or "the Acme brief" in a framework skill. Use placeholders: `<client-name>`, `<email>`, `<domain>`. Concrete examples — real company names, real domains, real accounts — belong in the instance overlay, never in framework files.

### Conventions for skill references

References go in `<skill-name>/references/` and hold supporting material the skill points at: extraction guides, mapping tables, prompts, examples.

- **Single source of truth.** If the skill uses a mapping table or section list that also appears in a template (like the "extraction category → brief section" mapping), pick one location and have the other point at it. Don't duplicate.
- **Scrubbed of instance specifics** — same rule as the skill itself.
- **Loaded lazily.** Reference files are read by the skill when needed, not preloaded. Keep them as separable concerns.

### Testing a new skill

Before merging:

- Walk through the skill against a real instance (tPPOS today) and confirm it works end-to-end.
- Confirm the overlay convention by removing the overlay temporarily and verifying the skill still functions (perhaps degraded, but functional).
- Read the SKILL.md fresh, as if you'd never seen it. Anything that assumes context you only have from this conversation is a bug.

## Adding a new template

Templates live at `framework/templates/<template-name>.md`. The conventions:

- **One template, one type.** Each template corresponds to one `type:` value in the frontmatter taxonomy. If your template doesn't fit an existing type, you're either adding a new type (document it in `framework/README.md`) or you're conflating two patterns.
- **Placeholders in angle brackets.** `<Client name>`, `<email>`, `YYYY-MM-DD`. Don't fill in example values — they leak into instances when people forget to scrub.
- **TODO blocks for prose sections.** Wrap prose sections in `> **TODO:**` blocks so it's obvious to the next person what to fill in. The block can contain hints about what good content looks like.
- **Link relative to where the template will be used.** If the template ends up at an unknown path in the user's instance, use placeholder paths like `<path-to-acos>` and note that paths will need fixing on copy.

## Adding a new README pattern

The four patterns today are root, container, item, asset. Adding a fifth is a real commitment — it adds vocabulary that every future instance has to learn. Before proposing one:

- Confirm that none of the four existing patterns can be stretched to fit.
- Document the new pattern's *purpose* (when it's used), *shape* (what sections it has), and *frontmatter type* in `framework/README.md`.
- Add the template at `framework/templates/folder-readme-<pattern>.md`.
- Update the README cascade table in `framework/README.md` to reference it.

## Adding a new artifact category

ACOS distinguishes a few categories of substantive artifact, beyond READMEs:

- **Briefs** — substantive records about a *thing*. `brief-company` (singleton at the instance root, identity content) and `brief-client` (per-client, relationship content). Stable.
- **Manifests** — lookup indexes used by skills for routing. `client-manifest` (per-client). Stable.
- **Dashboards** — state records. `dashboard-company` (singleton at the instance root, current state). Volatile, refreshed on a cadence.

Adding a fifth category — alongside READMEs, briefs, manifests, and dashboards — is the same kind of commitment as adding a new README pattern: it adds vocabulary every instance has to learn, and every future skill has to know how to read. Before proposing one:

- Confirm that none of the existing categories can be stretched to fit. A new substantive record about a stable thing is probably a brief. A new lookup index is probably a manifest. A new volatile state record is probably a dashboard.
- Document the category's *purpose* (when it exists), *shape* (what sections it has), *cardinality* (singleton at the instance root, per-folder, per-item), *volatility* (stable or refreshed), and *frontmatter type* in `framework/README.md` — typically as its own section parallel to Briefs and Dashboards.
- Add the template at `framework/templates/<category>.md`.
- If the category is refreshed rather than stable, add a refresh skill at `framework/skills/<category>-refresh/SKILL.md` that defines a default cadence and an overlay-overridable contract.

## Adding or changing a house rule

House rules live in `framework/README.md` under [House rules](../framework/README.md#house-rules). Adding one is also a real commitment — every instance has to obey it. The bar is high:

- The rule must apply across instances, not be specific to one company's style preferences.
- Confirm the rule isn't already implied by an existing rule.
- Phrase it as a binding statement, not a suggestion.
- Include the *why* if it's non-obvious. Future agents will need to judge edge cases.

## Working in this folder safely

A few defensive habits that prevent future regret:

- **Read before you write.** When in doubt about what's currently in ACOS, `Read` or `Grep` first. The framework should be small enough to skim.
- **Use `_archive/` rather than deletion.** When superseding files, move them to `_archive/<thing>-pre-<change>-YYYY-MM-DD/` rather than deleting. Disk is cheap; reversibility is valuable.
- **Date your checkpoints.** When the framework gains a meaningful change, write a checkpoint in this repo's `_progress/` folder. It is underscore-prefixed and gitignored — maintainer-facing build notes, not adopter-facing docs — so nothing there may be linked from a file that ships in a clone.
- **Don't move what's load-bearing without updating references.** When you move a template or skill, `Grep` for the old path across the whole instance tree first. Update every reference in the same change.
- **Don't paraphrase good prose just to relocate it.** When extracting from an instance to the framework, preserve sentences that are already framework-neutral. Rewriting introduces drift.
- **Check your links before you commit.** Every relative link in a file that ships in a clone must resolve inside the repo. Run `python3 scripts/check-links.py`.

## Code in ACOS — validators yes, runtime no

ACOS is markdown conventions, not a platform. That principle is not negotiable, but it is narrower than "no code at all." The line:

- **No runtime tooling.** ACOS ships nothing that an instance *depends on to operate* — no servers, no daemons, no agent runners, no build systems, no libraries an instance imports, nothing that has to be installed, configured, or kept running for the conventions to hold. An ACOS instance is a folder tree of markdown. It must work when the only thing reading it is an LLM with a filesystem. If a proposed addition would make an instance stop working when you delete it, it is runtime tooling and it does not belong here. Build it as a *tool that consumes ACOS*, in its own product.
- **Validators are allowed.** ACOS may ship read-only scripts that check whether an instance (or this repo) conforms to the conventions, and report what they find. `scripts/acos-integrity-check.py` and `scripts/check-links.py` are the current examples. A framework that cannot verify its own conventions is just prose, and prose drifts — the rules in `framework/README.md` are only real to the extent something can tell you when you've broken them.

The test for which side a new script falls on, in order:

1. **Does an instance depend on it?** If deleting the script would break an instance — or break a skill, a template, or a house rule — it's runtime tooling. Rejected.
2. **Does it write anything?** A validator reads the tree, resolves the conventions against it, and prints a report. It does not edit files, move files, generate content, or call out to a network. If it mutates the instance, it's a tool, not a validator. Rejected. (Skills are how ACOS mutates an instance, and skills are markdown.)
3. **Is it optional?** A validator is a convenience for maintainers and adopters who want CI. An instance that never runs one is still a valid ACOS instance. If the answer is no, it's runtime tooling. Rejected.

A validator that passes all three is in scope. Keep it dependency-free (standard library only), keep it read-only, and keep it honest about what it can't check — a validator that reports a false pass is worse than no validator.

## What's *not* in ACOS (and shouldn't be)

A short list of things people sometimes propose adding that don't belong here:

- **Runtime tooling / runners.** See [Code in ACOS](#code-in-acos--validators-yes-runtime-no) above. If you find yourself proposing a JavaScript or Python *runner* — something that executes an instance rather than checking one — you're building a tool that consumes ACOS, which belongs in its own product.
- **A single specific LLM's quirks.** ACOS is LLM-agnostic. Notes like "Claude does X" or "GPT-4 does Y" don't belong in framework docs.
- **Marketing copy.** This repo is the operating manual, not the pitch. Adoption messaging lives in [`adopting-acos.md`](adopting-acos.md); the marketing site is published from a separate branch and is not part of a framework clone.
- **An instance's content.** This is the most common mistake. If a draft you're writing has a real company name in it, you've stepped over the line. Move that part to the instance.
