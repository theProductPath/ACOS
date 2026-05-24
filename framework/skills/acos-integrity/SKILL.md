---
name: acos-integrity
description: Run integrity checks on an ACOS instance to confirm that folder structure, READMEs, briefs, manifests, frontmatter, naming conventions, and cross-references comply with the ACOS framework rules. Use when asked to check instance health, run an integrity audit, validate an ACOS tree, or when a scheduled trigger fires an integrity check.
---

# ACOS Integrity

Walk an ACOS instance tree and report violations of the framework conventions. The skill is a diagnostic — it reads the tree, checks each convention, and produces a structured report. It does not modify files.

## When this skill triggers

- A user says "run integrity check", "check ACOS health", "validate the instance", or similar.
- A scheduled trigger (cron, recurring task) fires an integrity audit.
- After a significant change to the instance (new client folder, template promotion, skill addition) when the user wants confirmation that nothing broke.
- Before promoting a pattern from instance to framework, to confirm the instance is clean.

## Instance overlay discovery

Before doing anything else, look for an instance overlay:

1. Find the instance root — the folder containing `company-brief.md`. Walk up from the working directory if needed.
2. Look for `<instance-root>/overlays/acos-integrity.md`.
3. If present, load it. The overlay may specify: instance-specific folders to include or exclude, custom check thresholds, routing for the report, or suppression rules for known legacy violations that should not surface.
4. If absent, proceed with framework defaults. The skill is self-sufficient without an overlay.

## What the skill checks

The skill runs a series of discrete checks, each producing pass/warning/fail results. Checks are organized by category.

### Category 1: README cascade completeness

These checks confirm the README cascade pattern is fully populated.

**Check 1.1 — Instance root README exists**

The instance root (the folder containing `company-brief.md`) must have a `README.md`.

- **Pass:** `README.md` exists and is non-empty.
- **Fail:** `README.md` is missing or empty.

**Check 1.2 — In-scope folders have READMEs**

Every folder listed in the instance root README's folder map must contain a `README.md`.

- **Pass:** All in-scope folders have a `README.md`.
- **Fail:** Any in-scope folder is missing its `README.md`.

**Check 1.3 — Container folders have container-type READMEs**

Folders that hold sibling sub-folders (like `Clients/`, `Products/`, `Projects/`) should have a `README.md` with `type: folder-readme-container` in frontmatter.

- **Pass:** Container README has `type: folder-readme-container`.
- **Warning:** Container README has a different type (may need correction).
- **Fail:** Container folder has no README.

**Check 1.4 — Item folders have item-type READMEs**

Each sub-folder inside a container (e.g., `Clients/Heartland-Paving-Partners/`) should have a `README.md` with `type: folder-readme-item`.

- **Pass:** Item README has `type: folder-readme-item`.
- **Warning:** Item README has a different type.
- **Fail:** Item folder has no README.

**Check 1.5 — Asset folders have asset-type READMEs**

Folders declared as asset libraries (like `Brand/`) should have a `README.md` with `type: folder-readme-asset`.

- **Pass:** Asset README has `type: folder-readme-asset`.
- **Warning:** Asset README has a different type.
- **Fail:** Asset folder has no README.

### Category 2: Brief and manifest presence

These checks confirm that the substantive companion documents exist where the framework expects them.

**Check 2.1 — Company brief exists**

The instance root must contain `company-brief.md`.

- **Pass:** `company-brief.md` exists and is non-empty.
- **Fail:** `company-brief.md` is missing or empty.

**Check 2.2 — Client folders have briefs**

Every client folder inside `Clients/` should contain a `brief.md`.

- **Pass:** Client has `brief.md`.
- **Warning:** Client folder exists but has no `brief.md` (may be a newly scaffolded client).
- **Fail:** `brief.md` exists but is empty or contains only frontmatter with no substantive content.

**Check 2.3 — Client folders have manifests**

Every client folder inside `Clients/` should contain a `manifest.md`.

- **Pass:** Client has `manifest.md`.
- **Warning:** Client folder exists but has no `manifest.md`.
- **Fail:** `manifest.md` exists but is empty.

**Check 2.4 — No duplicate briefs**

A client folder should have exactly one `brief.md`. Files like `brief 2.md` or `brief-draft.md` alongside the canonical brief are flagged.

- **Pass:** Exactly one `brief.md`.
- **Warning:** Additional brief-like files found alongside `brief.md` (list them).
- **Fail:** No canonical `brief.md` but brief-like files exist.

**Check 2.5 — Brief frontmatter has required fields**

Every `brief.md` and `company-brief.md` must include: `type`, `status`, `last-updated`, `maintainer`, `purpose`.

- **Pass:** All five fields present and non-empty.
- **Warning:** Some fields present but missing one or more of the required five.
- **Fail:** No frontmatter at all, or frontmatter is malformed.

### Category 3: Frontmatter validation

These checks confirm that frontmatter across all READMEs, briefs, and manifests follows the ACOS taxonomy.

**Check 3.1 — Type values are recognized**

Every `type:` value in frontmatter across the instance must be one of the recognized types: `folder-readme-root`, `folder-readme-container`, `folder-readme-item`, `folder-readme-asset`, `brief-company`, `brief-client`, `client-manifest`, `agent-ignore`, `progress-checkpoint`, `skill-overlay`, or a type declared in the instance's own glossary.

- **Pass:** All type values are recognized.
- **Warning:** Type value is not in the known taxonomy but could be a valid instance-specific addition (list it).
- **Fail:** Type value is clearly a typo or mistake (e.g., `folder-readme-contianer`).

**Check 3.2 — Status values are valid**

`status` in frontmatter should be one of: `active`, `drafting`, `archived`, `deprecated`.

- **Pass:** All status values are recognized.
- **Warning:** Unusual but plausible status value (list it).
- **Fail:** Clearly invalid status value.

**Check 3.3 — Dates are ISO 8601**

`last-updated` values in frontmatter must follow `YYYY-MM-DD` format.

- **Pass:** All dates are valid ISO 8601.
- **Fail:** Any date uses a non-standard format.

**Check 3.4 — Staleness detection**

Flag READMEs or briefs with `status: active` whose `last-updated` date is older than 90 days.

- **Pass:** All active documents updated within 90 days.
- **Warning:** Active document last updated more than 90 days ago (may need refresh).
- **Note:** This is informational, not a hard fail.

### Category 4: Folder naming

**Check 4.1 — No spaces in new folder names**

Folder names should use kebab-case (words separated by dashes, no spaces). Legacy folders with spaces are expected but flagged as known exceptions.

- **Pass:** All folder names use kebab-case or single words.
- **Warning:** Folder name contains spaces (note whether it appears to be legacy or recent).
- **Fail:** Recently created folder (within 30 days) with spaces in its name.

### Category 5: Agent-ignore compliance

**Check 5.1 — Underscore-prefixed folders are not referenced**

No in-scope file (README, brief, manifest, overlay) should contain a link to or explicit reference of a file inside an `_`-prefixed folder, unless the reference is in the `agent-ignore.md` file itself.

- **Pass:** No in-scope files reference `_`-prefixed content.
- **Warning:** In-scope file references `_archive/` or `_progress/` content (may be intentional but should be reviewed).

**Check 5.2 — Agent-ignore file exists at framework level**

The ACOS framework directory should contain an `agent-ignore.md`.

- **Pass:** `agent-ignore.md` exists in the framework.
- **Fail:** `agent-ignore.md` is missing from the framework.

### Category 6: Lateral cascade references

**Check 6.1 — Brand README exists when Brand folder is declared**

If the instance root's folder map declares a `Brand/` folder, that folder should have a `README.md` with `type: folder-readme-asset`.

- **Pass:** `Brand/README.md` exists with correct type.
- **Warning:** `Brand/` folder exists but has no README or wrong type.
- **Fail:** `Brand/` folder declared in folder map but folder doesn't exist.

**Check 6.2 — Overlays have matching skills**

Every overlay in `<instance-root>/overlays/` should correspond to a skill in the framework's `skills/` directory.

- **Pass:** Every overlay has a matching framework skill.
- **Warning:** Overlay exists with no matching framework skill (orphaned overlay).

**Check 6.3 — Overlay frontmatter is valid**

Every overlay file should have frontmatter with at least `type: skill-overlay`, `skill`, `instance`, and `last-updated`.

- **Pass:** All overlays have valid frontmatter.
- **Warning:** Overlay missing one or more required frontmatter fields.
- **Fail:** Overlay has no frontmatter.

### Category 7: Markdown style

These are style linting checks — lower priority but useful for consistency.

**Check 7.1 — No horizontal-rule dividers between sections**

Markdown files should not use `---` between sections (only in frontmatter delimiters).

- **Pass:** No section-divider horizontal rules found.
- **Warning:** Horizontal rules found between sections in one or more files (list them).

**Check 7.2 — Straight quotes only**

Markdown files should use straight quotes (`'` and `"`), not curly quotes.

- **Pass:** No curly quotes found.
- **Warning:** Curly quotes found in one or more files (list them).

**Check 7.3 — Sentence-case headings**

Section headings should use sentence case, not title case.

- **Pass:** All headings appear to use sentence case.
- **Warning:** Headings found that appear to use title case (list them — this is a judgment call, not an automated fail).

### Category 8: Cross-reference integrity

**Check 8.1 — Internal links resolve**

Markdown links that point to other files within the instance tree (relative links) should resolve to existing files.

- **Pass:** All internal links resolve.
- **Warning:** Internal link targets a file that doesn't exist (list the broken links).

**Check 8.2 — Brief-to-README cross-references**

When a `brief.md` and `README.md` coexist in a client folder, the brief should reference the README and vice versa.

- **Pass:** Both reference each other.
- **Warning:** One references the other but not reciprocally.
- **Note:** Not required, just good practice.

### Category 9: Template coverage

**Check 9.1 — Every folder pattern has a template**

For each README pattern in use (root, container, item, asset) and each brief pattern (company, client), the framework's `templates/` directory should have a corresponding template file.

- **Pass:** All in-use patterns have templates.
- **Warning:** A pattern is in use but has no template (may indicate a gap in the framework).

**Check 9.2 — Folders using templates correctly**

When a folder's README declares a `type`, check that its structure matches the corresponding template.

- **Pass:** All typed folders match their template structure.
- **Warning:** Folder deviates from its declared template (list deviations).

## Running the checks

### Walk order

1. Start at the instance root (the folder containing `company-brief.md`).
2. Read the instance root `README.md` to get the folder map.
3. Walk each in-scope folder in the folder map, reading its README and descending into its children.
4. Skip all `_`-prefixed folders (per agent-ignore convention).
5. Collect all `brief.md`, `manifest.md`, and `README.md` files encountered.

### Check execution

- Run all checks in each category, collecting results.
- A check that cannot be evaluated (e.g., no folder map to walk) produces an **info** result, not a fail.
- A check that encounters an error (e.g., permission denied reading a file) produces a **warning** and continues.

### Report format

Produce a structured report with this shape:

```
# ACOS Integrity Report — <instance name>

**Date:** YYYY-MM-DD
**Instance root:** <path>
**Checks run:** <number>
**Pass:** <number>  **Warning:** <number>  **Fail:** <number>  **Info:** <number>

---

## Category 1: README cascade completeness
✅ 1.1 Instance root README — pass
✅ 1.2 In-scope folders have READMEs — pass
⚠️ 1.3 Container type — warning: Clients/README.md has type "folder-readme-root" (expected "folder-readme-container")
❌ 1.4 Item READMEs — fail: <client-folder>/README.md is missing

## Category 2: Brief and manifest presence
...

## Summary of items needing attention
1. [⚠️] Clients/README.md type mismatch
2. [❌] <client-folder> missing README.md
3. ...
```

### Severity guide

- **✅ Pass** — Convention met. No action needed.
- **⚠️ Warning** — Convention may not be met, or a gray area. Review and decide.
- **❌ Fail** — Convention violated. Fix recommended.
- **ℹ️ Info** — Check could not be evaluated. Informational only.

## Output

The skill produces:

1. **A report** — the structured integrity report described above.
2. **A summary** — a one-paragraph human-readable summary of overall health, suitable for a chat message or notification.
3. **An action list** — a prioritized list of fixes, if any, grouped by urgency (failures first, then warnings).

If an overlay specifies a report destination (e.g., write to a file, send to a channel), follow that routing. Otherwise, deliver the report inline in the conversation and offer to save it to `<instance-root>/_progress/YYYY-MM-DD-integrity-check.md`.

## Re-running

The skill is idempotent. Running it again produces a fresh report. Previous reports saved to `_progress/` are not modified.

## Instance overlay configuration

An overlay at `<instance-root>/overlays/acos-integrity.md` may specify:

- **Exclude folders** — specific folders to skip during the walk (in addition to `_`-prefixed folders). Useful for legacy areas not yet migrated to ACOS conventions.
- **Suppress checks** — specific check IDs to skip (e.g., `7.1` if the instance has a known style exception for horizontal rules).
- **Staleness threshold** — override the default 90-day staleness window for check 3.4.
- **Report destination** — a file path or channel to write the report to.
- **Custom type additions** — instance-specific `type:` values that should be treated as valid in addition to the framework taxonomy.

## Links

- Framework README: [`../../README.md`](../../README.md)
- Agent-ignore convention: [`../../agent-ignore.md`](../../agent-ignore.md)
- Templates directory: [`../../templates/`](../../templates/)
- Instance root (tPPOS example): [`../../../../tPPOS/README.md`](../../../../tPPOS/README.md)

---

## Future checks (placeholders)

These checks are not yet implemented. They are listed here as placeholders for ACOS enhancements that will make them feasible. Do not implement until the corresponding framework feature exists or is explicitly requested.

### Placeholder A — Schema validation for manifests

When the client manifest template gains a formal schema (e.g., JSON Schema for the identifier tables), the integrity check should validate each `manifest.md` against it. Currently manifests are freeform markdown, so structural validation is limited to "has the expected sections."

### Placeholder B — Overlay-schema validation

When overlays gain a formal schema (e.g., required fields per skill type), validate each overlay against its corresponding skill's expected overlay schema. Currently overlays are freeform markdown.

### Placeholder C — Template freshness

Compare the last-updated date on each template in `framework/templates/` against the templates actually in use in the instance. If a template has been updated more recently than the files derived from it, flag that the instance's files may be out of date.

### Placeholder D — Circular reference detection

Walk all cross-references (markdown links between files) and detect cycles — e.g., file A links to B, B links to C, C links back to A. This requires a graph walk and is deferred until the cross-reference check (8.1) is stable.

### Placeholder E — Duplicate brief detection (content-level)

Beyond the structural check for duplicate brief files (2.4), detect when two briefs have overlapping or contradictory content — e.g., two client briefs that both claim the same contact person. This requires content analysis, not just filename comparison.

### Placeholder F — Orphaned client folders

Detect client folders inside `Clients/` that have no corresponding entry in the `Clients/README.md` container index, and vice versa — entries in the container README that point to non-existent folders.

### Placeholder G — Brand pre-flight readiness

When a Brand folder exists, verify that it contains the minimum artifacts required for brand pre-flight (color palette, typography definitions, logo directory, voice guidelines). The exact minimum set will be defined as the client-brand-capture skill matures.

### Placeholder H — Skill-overlay parameter coverage

For each overlay that exists, verify that it provides values for all the parameters the corresponding framework skill expects from overlays. This requires parsing the skill's SKILL.md for expected overlay keys, which is a future enhancement.

### Placeholder I — Dependency graph between briefs and manifests

Verify that every contact, project keyword, or identifier in a client manifest is also referenced in the corresponding client brief (or vice versa). Detect identifiers that exist in one but not the other.

### Placeholder J — File encoding and whitespace hygiene

Check for common markdown hygiene issues: trailing whitespace, mixed line endings (CRLF vs LF), non-UTF-8 encoding, BOM markers. Low priority but contributes to long-term consistency.

### Placeholder K — Companion plugin availability

When the `companion-plugins.md` file at the framework level declares expected plugins (e.g., `brand-voice`), verify that any plugin-specific code paths in skills can be reached — i.e., the skill's plugin detection logic is documented and the companion-plugins file is consistent with what skills reference.

### Placeholder L — Scheduled trigger health

When ACOS instances configure scheduled integrity checks (e.g., via cron or a task runner), verify that the trigger configuration is valid, the schedule is reasonable, and the last run completed successfully. This depends on a scheduling convention that doesn't exist yet.