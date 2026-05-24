---
type: progress-checkpoint
status: active
last-updated: 2026-05-18
maintainer: Steven Jones
purpose: Progress report for the 2026-05-18 promotion of the engineering-defaults pattern from tPPOS into the ACOS framework — placeholder sections added to brief-company and brief-client templates so new instances inherit the cascade.
---

# 2026-05-18 — Engineering-defaults pattern promoted to framework

A small but load-bearing convention extension. The "where do engineering defaults live, and how do they cascade?" question — flagged earlier as a tPPOS-productization item — got answered in practice during HPP Costing Tool spec preparation, and the answer is now in the framework templates so any new ACOS instance inherits the shape.

## What got added

### ACOS framework additions

- **`framework/templates/brief-company.md`** — new `## Engineering defaults` section placed between `## People` (with its `### Principals` subsection) and `## What we don't do`. Contains the cascade rule (`company → client → product/project`, most specific wins), a TODO block, and illustrative bullets for source repo, deployment environment, and packaging — all in angle-bracket placeholders so nothing instance-specific leaks.
- **`framework/templates/brief-client.md`** — new `## Engineering defaults` section placed between `## Brand & identity` and `## Interaction log`. Carries the "list only deltas from the company default" rule and example override shapes. Explicit note that a client inheriting everything should leave a one-line acknowledgment rather than restating the company defaults.

### Why this is a framework change and not just an instance change

Both criteria from `docs/extending-acos.md` apply: (a) the pattern would be useful to another company adopting ACOS (any consulting / agency / engineering practice that builds software for multiple clients faces the same "company defaults vs. client overrides" tension), and (b) the pattern has more than one use in the proving instance — tPPOS has now exercised it for both a company-wide section (`tPPOS/company-brief.md`) and a client-specific override section (`Clients/Heartland-Paving-Partners/brief.md`).

### Cascade design choice, recorded

The cascade hierarchy chosen — `company default → client override → product/project override`, most specific wins — is one valid shape, not the only possible one. For productized ACOS, the open questions in `tPPOS/` productization notes still apply: whether the cascade should be opinionated or configurable, whether engineering defaults belong in a brief section vs. a separate file vs. structured frontmatter, how a project opts out cleanly, and how to keep the override chain legible without forcing a reader to climb three files. The template currently encodes the brief-section choice; the other questions are deferred.

## Instance traceability

The proving-instance examples (tPP-side) of this pattern:

- **`tPPOS/company-brief.md`** — Engineering defaults section with three tPP-wide defaults (source repo home, default deployment environment, default packaging). Real, populated values.
- **`Clients/Heartland-Paving-Partners/brief.md`** — Engineering defaults section with two HPP-specific overrides (source repo at `PPCCadmin`, permanent deploy target Azure with the current-block / interim-fallback note). Explicitly says it lists only deltas from the tPP default.

These remain instance content (real org names, real environments) and stay in tPPOS, not in the framework — per the rule in `docs/extending-acos.md` that concrete examples belong in instance overlays.

## What didn't change

- No house-rule addition in `framework/README.md`. Engineering defaults are *substance* (what to choose), not *operating rules* (how to operate the system), so they belong in briefs, not in house rules. The brief template change is sufficient.
- No new `type:` value. Engineering defaults are sections inside existing `brief-company` and `brief-client` documents, not a new document type.
- No skill or skill overlay was added.

## Open follow-ups

- `docs/adopting-acos.md` is still TODO. When it's written, the engineering-defaults cascade is a natural item to call out under "what to fill in first when onboarding a new instance," because it's one of the few things a new instance can't reasonably leave blank for long without inheriting tacitly.
- The other open productization questions about this pattern (cascade as opinionated vs. configurable; brief-section vs. separate-file vs. frontmatter; opt-out mechanics; cross-layer legibility) remain in the tPPOS productization-discussion memory as items to revisit when productization kicks off in earnest.
