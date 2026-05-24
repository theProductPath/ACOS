---
type: progress-checkpoint
subject: dashboard-pattern-phase-1
status: complete
last-updated: 2026-05-19
maintainer: Steven Jones
purpose: Checkpoint for phase 1 of the company dashboard pattern — framework template, refresh skill, tune skill stub, README updates, extending-acos additions. Captures what was added and why so phase 2+ can build on it.
---

# Dashboard pattern — phase 1 checkpoint

## What was added to ACOS

Phase 1 introduced the **dashboard** as a new singleton artifact category at the instance root, parallel to the company brief but with different semantics (state, not identity; volatile, not stable).

Files added:

- `framework/templates/dashboard-company.md` — singleton template with sections for at-a-glance, active clients, pipeline, projects in flight, products in flight, open commitments, this week, operations (reserved), system health, and a Layout notes journal footer.
- `framework/skills/dashboard-refresh/SKILL.md` — daily-cadence refresh skill. Reads briefs and READMEs, rolls up structured sections, preserves hand-edited blocks. Default cadence is daily 6am local, overlay-overridable.
- `framework/skills/dashboard-tune/SKILL.md` — monthly-cadence tuning skill (stub). Reviews Layout notes and proposes template or overlay refinements. Runtime implementation deferred until at least one instance has accumulated history.

Files edited:

- `framework/README.md` — added `dashboard-company` to the frontmatter type taxonomy, added an Instance structure mention of the optional `dashboard.md`, added a new top-level Dashboards section parallel to Briefs, and added a new house rule "Instance branding on dashboards" between brand pre-flight and folder naming.
- `docs/extending-acos.md` — added an "Adding a new artifact category" section after "Adding a new README pattern", capturing the bar for proposing future categories beyond briefs, manifests, and dashboards.

## Decisions captured

- **Markdown is canonical, renders are views.** The `dashboard.md` file is the source of truth. Cowork artifacts, HTML exports, PDFs, etc. read from it; they don't replace it.
- **Refreshes are conservative.** Hand-edited blocks (at-a-glance, Layout notes, pinned sections) are preserved across refreshes. Structured tables are re-rolled. The skill pauses and asks if it would overwrite a hand-edit newer than the last refresh.
- **Cadence is daily 6am local.** Framework default chosen to match a "morning glance" use case. Overlay-overridable; weekly is sensible for instances in early build-out.
- **Operations section is reserved, not active.** Financial, hours, invoicing, and capacity data have a placeholder slot but no framework content. Instances wire these in as they wire in the underlying data sources.
- **Dashboards get brand pre-flighted in their rendered views.** New house rule in the framework README. The markdown stays neutral; every render applies instance brand tokens.

## What was deliberately *not* done

- No skill runtime implementation. The skill specs declare the contract; agents executing the skills implement the walk and roll-up at runtime against the instance.
- No tPP-specific content. Per the framework/instance split, all phase 1 deliverables are placeholder-shaped. tPP-specific seeding happens in phase 3.
- No Cowork artifact built. That's phase 4, after the markdown layer is in place and proves out.
- No scheduled task created. That's phase 5.
- No promotion-from-tPPOS happened. This pattern was designed fresh in ACOS first, since the dashboard concept didn't pre-exist in tPPOS.

## Phase 2+ pointers

- **Phase 2:** validate the refresh skill against tPPOS by hand — run it conceptually, see whether the framework template's sections fit what tPP actually wants to see at 6am.
- **Phase 3:** seed `tPPOS/dashboard.md` from the template and create `tPPOS/overlays/dashboard-refresh.md`. This is where the operations placeholder gets wired in if any of tPP's financial/hours data is already accessible.
- **Phase 4:** build the Cowork artifact as a brand-pre-flighted render of the markdown.
- **Phase 5:** schedule the refresh.

The pattern was deliberately built framework-first rather than promoted from tPPOS. If tPP's instance reveals shape changes the framework should adopt, the standard promotion path applies (see `docs/extending-acos.md`).

## Phase 2 decisions applied (2026-05-19)

Phase 2 was a dry-run of the refresh skill against tPPOS. The walk surfaced five strain points; the principal's decisions on each were applied back into the framework template and the refresh skill before phase 3 begins.

- **Pipeline redefined.** Pipeline now means *future workstreams within active clients* — predictable, income-generating work queued behind current workstreams. Not new prospects. Framework template and skill roll-up table updated to reflect this. Table shape: `Workstream | Client | Stage | Next move | Last touch`.
- **Leads added as a separate optional section.** Reserved slot for new-prospect tracking, populated only when the instance overlay declares a prospect tracker source. Placed between Pipeline and Projects in flight in the layout. The principal flagged a Prospect Tracker is coming in the days ahead and will use "Leads" terminology.
- **Active clients shape.** The single-phrase "Engagement" column was replaced with a multi-line "Current workstreams" cell — one workstream per line, each with its immediate next move. This matches the reality that real engagements run multiple concurrent workstreams.
- **Open commitments — direction filter.** Refresh skill now filters to principal-owned (outbound) commitments by default when the source mixes inbound and outbound in a single list. Overlay can opt into `split` or `all` modes. Documented as a parseable tag convention (`* [ ] **<owner>**: <action>`).
- **Open commitments — undated allowed.** The `Due` column became `Due (if known)` with explicit copy that the dashboard does not fabricate dates. The principal flagged that more rigorous commitment tracking is a future skill layer, not the dashboard's job.
- **Companion folders.** Marketing-site companion folders (e.g., `*-site/`) should not surface as first-class products. New overlay key `companion-folders` lets an instance declare a collapse or exclude map. Framework default remains "every folder is first-class"; the overlay narrows that.

These edits were applied to:

- `framework/templates/dashboard-company.md` — Active clients, Pipeline (reshaped), Leads (new), Open commitments.
- `framework/skills/dashboard-refresh/SKILL.md` — Pass 2 roll-up table (all affected rows) and Instance overlay configuration list (new keys: `Leads source`, `Pipeline ordering`, `Companion folders`, `Open commitments direction`).

No tPP content was added in phase 2. Phase 3 (seeding `tPPOS/dashboard.md` and `tPPOS/overlays/dashboard-refresh.md`) begins from this revised framework state.
