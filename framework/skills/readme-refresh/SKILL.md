---
name: readme-refresh
description: Refresh stale source-contract READMEs across an ACOS instance after the freshness check flags them. Reads a flagged README plus the folder it describes, drafts a proposed update into a staging area, and applies it only after review — canonical contracts are never rewritten unattended. Use when the user says "refresh the READMEs", "update the stale readmes", "run the readme refresh", "propose readme updates", or when a scheduled trigger fires the refresh. This is the write-capable counterpart to the read-only acos-integrity / freshness check.
---

# README Refresh

Bring stale source-contract READMEs back in line with the folders they describe. Where the freshness check (read-only) only *flags* likely-stale contracts, this skill *proposes and applies* fixes — under a strict propose-then-apply boundary so canonical Markdown is never rewritten without review.

A README in an ACOS instance is a **source contract**, not a disposable rendered view. It declares what a folder is, how it is organized, and how agents should treat it. When the folder drifts ahead of its README, downstream skills and agents orient off stale instructions. This skill closes that gap deliberately and reviewably.

## The boundary (read this first)

This skill separates three actions with escalating stakes:

1. **Detect** — read-only. Classify each source contract as fresh / watch / stale / missing. Safe on any cadence.
2. **Propose** — writes only to a staging area. Drafts a revised README next to a diff and a rationale. Touches no canonical file.
3. **Apply** — copies a proposal onto the real file. Gated by trust level.

The hard rule: **a scheduled or unattended run may Detect and Propose, but must never Apply to a `canonical`-trust source.** Applying to a canonical contract requires a human to review the proposal and approve it in an interactive session. Only `view`-trust (disposable) sources may be auto-applied, and only when the instance overlay opts in.

If you are ever unsure of a source's trust level, treat it as `canonical`.

## When this skill triggers

- A user says "refresh the READMEs", "propose readme updates", "the readmes are stale", "reconcile the readmes with the folders", or similar.
- A scheduled trigger fires the refresh (propose-only — see the boundary above).
- After a batch of structural work (folders added, files moved, a product promoted) when the user wants the affected READMEs reconciled before they drift.
- The freshness check has flagged one or more contracts and the user wants to act on the flags rather than just see them.

## Instance overlay discovery

Before doing anything else, look for an instance overlay:

1. Find the instance root — the folder containing `company-brief.md`. Walk up from the working directory if needed.
2. Look for `<instance-root>/overlays/readme-refresh.md`.
3. If present, load it. The overlay declares: the source registry (which files, at which trust level), the staging location, the scan/propose helpers the instance provides, the cadence, review routing, whether any `view`-trust sources may be auto-applied, and instance-specific preservation rules.
4. If absent, proceed with framework defaults below. The skill is self-sufficient without an overlay, but with no overlay every source defaults to `canonical` and nothing is ever auto-applied.

## Pass 1 — detect

Produce (or refresh) the freshness classification.

1. If the overlay names a scan helper (e.g. a script that regenerates the freshness snapshot), run it. Otherwise, for each source in the registry read its `last-updated` frontmatter, its filesystem modified date, and scan its body for open-loop language (TODO / placeholder / "not yet" / "future <thing>").
2. Classify each source: `missing` (file absent), `stale` (declared update past the stale threshold), `watch` (past the watch threshold, or carries open-loop language, or has no declared date), else `fresh`.
3. Carry each source's `trust` level and `refreshEligible` flag forward. Sources marked as owned by another skill (a dashboard, a brief processor) are shown for context but are **not** candidates here — that skill owns them.

The output of this pass is the set of refresh-eligible sources whose status is worse than `fresh`.

## Pass 2 — propose

For each eligible flagged source, draft a proposal. Never edit the source file in this pass.

1. **Read the contract and its territory.** Read the flagged README in full. Then read what it claims to describe: the immediate child folders and files, the item READMEs or briefs one level down, and any manifest the README references. The question you are answering is: *where does the declared state disagree with the actual folder?*
2. **Gather recent activity.** If git is available, look at what changed under the folder since the README's declared `last-updated`. Otherwise use file modified dates. This tells you what drifted.
3. **Draft a small, honest update.** Correct what is now wrong: files or subfolders that exist but aren't listed, listed things that are gone, counts and indexes that moved, status language that no longer matches. Keep the edit minimal and surgical — this is reconciliation, not a rewrite.
4. **Preserve intentional open loops.** A TODO or "future" note that describes real deferred work is a feature, not staleness. Do not delete open loops to make a file look fresh. Only remove open-loop language when the loop has actually been closed by work in the folder. When in doubt, keep it and note it in the rationale.
5. **Handle `last-updated` honestly.** Propose bumping `last-updated` only if the body content meaningfully changed. A no-op reconciliation (folder still matches the README) should *not* bump the date — bumping it would hide the fact that nothing was verified against reality. If nothing needs to change, record the source as "verified, no change" rather than producing an empty proposal.
6. **Write the proposal to staging.** For each source, the overlay's staging area gets: the proposed full README, a diff against the current file, and a short rationale (what drifted, what you changed, what you deliberately left alone). Add the source to the review queue / refresh-state the review surface reads.

## Pass 3 — apply (gated)

Applying is deliberate and never bundled into a scheduled run.

- **`canonical` trust:** never auto-apply. Surface the proposal for human review. Apply only when a person, in an interactive session, has read the diff and approved this specific proposal. On approval, copy the proposed content onto the real file and set `last-updated` to today.
- **`view` trust:** may be auto-applied *only if* the overlay's `auto-apply` setting enables it for view-trust sources. Otherwise treat like canonical.
- After applying, clear that source from the review queue and re-run Detect so the freshness snapshot reflects the now-current file.

Never apply a proposal you have not just regenerated against the current file — if the source changed since the proposal was drafted, re-propose first to avoid clobbering newer edits.

## Output

- Updated freshness classification (snapshot + machine-readable scan).
- Zero-to-many proposals in the staging area, each with proposed content, a diff, and a rationale.
- An updated review-state artifact the refresh view renders.
- On an interactive apply: the reconciled canonical file(s), with `last-updated` bumped, and the queue cleared for those sources.

## Notes

- This skill is the write-capable sibling of `acos-integrity`. Integrity answers "does the tree comply with the framework?"; readme-refresh answers "does each contract still match its folder, and if not, what is the smallest honest fix?"
- The propose-then-apply split exists because READMEs are contracts. The cost of a wrong automated edit to a contract is higher than the cost of a human spending thirty seconds on a diff. The skill optimizes for reviewable correctness, not unattended throughput.
- Sources owned by another skill (dashboards refreshed by `dashboard-refresh`, briefs maintained by `client-brief-processor`) are out of scope here even when flagged. Route those flags to their owning skill.
