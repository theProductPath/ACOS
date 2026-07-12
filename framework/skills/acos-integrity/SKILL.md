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

### Category 0: Membership

Everything in this skill applies **only to folders that are part of the operating system**, and membership is opt-in. Read [Membership](../../README.md#membership--what-is-part-of-the-operating-system) in the framework manual before running any check; it is the model the rest of this skill assumes.

**Check 0.1 — The folder map is the roster**

The `## Folder map` table in the instance root README is the membership allowlist. A sibling folder is in the OS **if and only if** it has a row there. Parse the table; walk what it lists and nothing else.

- **Pass:** The table is present and parses; report which folders opted in.
- **Fail:** No `## Folder map` section, or it doesn't parse as a table. Without it, nothing is in scope.
- **Never a finding:** A folder on disk that is *not* in the table. It is not part of the OS. Do not report it, do not count it, do not suggest adding it. Say nothing.

### Category 1: README cascade completeness

These checks confirm the README cascade is populated **for the folders that are in the OS**.

**Check 1.1 — Instance root README exists**

The instance root (the folder containing `company-brief.md`) must have a `README.md`.

- **Pass:** `README.md` exists and is non-empty.
- **Fail:** `README.md` is missing or empty.

**Check 1.2 — Folders on the roster have READMEs**

Every folder listed in the root README's folder map must exist and must contain a `README.md`. A folder on the roster opted into the OS, so it owes the OS a front door: without a README nothing declares what it is or what its children are.

- **Pass:** Every folder in the map exists and has a `README.md`.
- **Fail:** A folder in the map doesn't exist on disk, or exists with no `README.md`.

**Check 1.3 — Container folders have container-type READMEs**

A folder whose README says `type: folder-readme-container` is declaring that **its children are OS items**. That declaration is what makes check 1.4 apply to them.

- **Pass:** Container README has `type: folder-readme-container`.
- **Warning:** Container README has a different type than its position suggests.

**Check 1.4 — A container's child without a README is not an OS item**

A folder inside a container with no `README.md` has **not opted into the OS**. This is *information, not an error* — a folder is in the system only if it says so, and plenty of folders correctly say nothing.

- **Pass:** The child has a `README.md`; it is an OS item and the cascade continues into it.
- **Warning (informational):** No `README.md`. Report it as what it is — *this folder is not visible to the OS and agents will not read into it* — and name the three ways to change that, all of them valid: give it a README (to include it), type its parent `folder-readme-asset` (to declare it material rather than structure), or underscore-prefix it (to hide it). Doing nothing is also valid.
- **Never a fail.** A missing README is an absence of opt-in, not a violation. Reporting it as a failure inverts the model and trains people to ignore the checker.

**Check 1.5 — Asset libraries end the walk**

A folder whose README says `type: folder-readme-asset` — or that the overlay names in `asset-folders` — is an **asset library**. Its children are *material*: files, images, scanned documents, sub-folders of assets. They are not OS items.

- **Pass:** Asset README has `type: folder-readme-asset`. Validate that README, then **stop**.
- **Do not walk into an asset library's children, at any depth.** They never need READMEs and never carry frontmatter. Produce **no findings** for anything inside one.
- **Fail:** The folder is on the roster and has no README at all (that's 1.2).

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

Every `type:` value in frontmatter across the instance must be one of the recognized types. The taxonomy is defined in [`framework/README.md`](../../README.md#frontmatter) — that list is the source of truth, and this skill defers to it rather than restating it. Instances may add their own via the overlay's `custom-types`.

- **Pass:** All type values are recognized.
- **Warning:** Type value is not in the known taxonomy but could be a valid instance-specific addition (list it).
- **Fail:** Type value is clearly a typo or mistake (e.g., `folder-readme-contianer`).

**Check 3.2 — Status values are valid**

`status` in frontmatter must be one of the values in the framework [status vocabulary](../../README.md#status-vocabulary) — that list is the source of truth and this skill defers to it rather than restating it. Instances may add their own via the overlay's `custom-statuses`.

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

**ACOS does not govern letter case.** See [Folder naming — structure, not style](../../README.md#folder-naming--structure-not-style), which is the source of truth. A capitalized folder name produces **no finding**. Neither does a lowercase one, a mixed-case one, or an underscore inside a name. Do not flag style. Do not suggest renames on aesthetic grounds.

**Check 4.1 — Folder names don't contain characters that break things**

The only naming finding the framework makes. A name containing a space, `#`, `?`, `%`, `\`, `:`, `|`, `*`, `<`, `>`, or `"` breaks real machinery — shell paths, markdown links, URLs — and that's worth saying out loud.

- **Pass:** No breaking characters.
- **Warning:** A breaking character is present. Say **concretely what it breaks** (a space needs `%20` in a URL, angle brackets in a markdown link, and quoting in a shell; a `#` truncates a URL at the fragment; a `*` is a glob wildcard). Never a failure — a legacy folder with a space in it works fine until something links to it, and renaming may break references that already point at it.
- The instance root folder is exempt (it's named for the instance), as is any name in the overlay's `naming-exempt`.

**Check 4.2 — The instance's own naming style, if it declared one**

The framework ships **no** default naming convention. An instance that wants one enforced sets `naming-style` in its overlay (`kebab-case` or `capitalized`).

- **Not run at all** when the overlay carries no `naming-style` key. This is the default, and a clean instance that never declares one is fully conformant.
- **Pass:** Names match the instance's declared style.
- **Warning:** A name doesn't match the style the instance declared for itself.

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
2. Read the instance root `README.md` and parse the `## Folder map` table. **That table is the roster** — it is the complete list of what is in the OS.
3. Walk each folder on the roster, reading its README. Anything on disk that isn't on the roster is not part of the OS: don't walk it, don't report it, don't mention it.
4. At each folder, let its README's `type` tell you what to do next:
   - `folder-readme-container` → descend into its children; each child with a README is an OS item, and each child without one is simply not in the OS (check 1.4, a warning, not a failure).
   - `folder-readme-asset` → **stop**. Its children are material, not structure. Do not descend, at any depth.
5. Skip all `_`-prefixed folders, at any depth (per the agent-ignore convention).
6. Collect all `brief.md`, `manifest.md`, and `README.md` files encountered.

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

An overlay at `<instance-root>/overlays/acos-integrity.md` carries everything instance-specific. The framework skill and the script it ships with hold **no** knowledge of any particular instance's folder names — which folder holds clients, which folders are asset libraries, which containers hold self-contained repos all come from here.

The overlay is prose for the agent, plus one fenced `acos-config` block that the script (`scripts/acos-integrity-check.py`) parses. Agents running the skill by hand should read the same block.

````
```acos-config
instance-name: <Instance>
client-containers: [Clients]
asset-folders: [Brand]
repo-child-containers: [Products]
exclude-folders: []
suppress-checks: []
custom-types: []
custom-statuses: []
naming-exempt: []
naming-style: none
```
````

| Key | Meaning | Default with no overlay |
|---|---|---|
| `instance-name` | Display name; also exempt from the folder-name check (the instance root is named for the instance, not for its contents). | The instance root folder's name. |
| `client-containers` | Folders whose direct children are client engagements. Checks 2.2-2.4 apply to each child. | `Clients` |
| `asset-folders` | Folders that *are* asset libraries: the walk stops at them and their children are never OS items (check 1.5). Usually unnecessary — a folder whose own README says `type: folder-readme-asset` is already treated as one. This key is for saying it once here instead. | none |
| `repo-child-containers` | Containers whose direct children are self-contained repositories. Their `README.md` is a codebase README owned by that repo, so checks 2.5 and 3.1 are exempt for them. | none |
| `exclude-folders` | Folders to skip during the walk, in addition to `_`-prefixed and hidden folders. Rarely needed: a folder that shouldn't be in the OS should simply not be on the roster. | none |
| `suppress-checks` | Check IDs to skip entirely (e.g. `4.1`). | none |
| `custom-types` | Instance-specific `type:` values treated as valid in addition to the framework taxonomy (check 3.1). | none |
| `custom-statuses` | Instance-specific `status:` values treated as valid (check 3.2). | none |
| `naming-exempt` | Folder names exempt from the naming checks (4.1, 4.2) — the place to record accepted legacy names. | none |
| `naming-style` | The instance's **own** naming policy, enforced as a warning (check 4.2): `kebab-case`, `capitalized`, or `none`. **The framework ships no default and has no opinion on case** — with no key, check 4.2 does not run. | `none` |

Report destination is prose, not config: the script writes to stdout, and the agent routes the report per the overlay's routing section.

The skill is self-sufficient without an overlay. With no overlay, the script falls back to convention-based discovery: instance root by walking up for `company-brief.md`, in-scope folders from the root README's folder map, `Clients` as the client container.

## Running the script

```
python3 <path-to-acos>/scripts/acos-integrity-check.py [--root PATH] [--overlay PATH] [--strict]
```

- `--root` — the instance root (the folder containing `company-brief.md`). Defaults to walking up from the working directory.
- `--overlay` — an explicit overlay path. Defaults to `<instance-root>/overlays/acos-integrity.md`.
- `--strict` — exit non-zero if any check fails. Useful in CI; off by default so scheduled runs report rather than break.

The script is stdlib-only and has no dependencies. Its tests live in `tests/test_acos_integrity_check.py` and run in CI on every push and PR.

## Links

- Framework README: [`../../README.md`](../../README.md)
- Agent-ignore convention: [`../../agent-ignore.md`](../../agent-ignore.md)
- Templates directory: [`../../templates/`](../../templates/)
- Instance root: the folder containing `company-brief.md` in the instance being checked. Resolved at runtime, never hardcoded.

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