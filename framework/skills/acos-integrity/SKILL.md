---
name: acos-integrity
description: Run integrity checks on an ACOS instance to confirm that folder structure, READMEs, briefs, manifests, frontmatter, folder naming, overlays, and internal links comply with the ACOS framework rules. Use when asked to check instance health, run an integrity audit, validate an ACOS tree, or when a scheduled trigger fires an integrity check.
---

# ACOS Integrity

Walk an ACOS instance tree and report violations of the framework conventions. The skill is a diagnostic — it reads the tree, checks each convention, and produces a structured report. It does not modify files.

**This spec and the script are one thing.** Every check below is implemented in [`scripts/acos-integrity-check.py`](../../../scripts/acos-integrity-check.py), and every check the script implements is documented below. There are no aspirational checks here: a spec that describes a tool that does not exist is the same "documentation that lies" failure ACOS was built to prevent, so the two are kept in lockstep by a test (`tests/test_acos_integrity_check.py`) that fails the build if they drift. If you add a check, document it here in the same change. If you delete one, delete it from both.

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

23 checks, organized by category. Each produces pass, warning, fail, or info.

### Category 0: Membership

Everything in this skill applies **only to folders that are part of the operating system**, and membership is opt-in. Read [Membership](../../README.md#membership--what-is-part-of-the-operating-system) in the framework manual before running any check; it is the model the rest of this skill assumes.

**Check 0.1 — The folder map is the roster**

The `## Folder map` table in the instance root README is the membership allowlist. A sibling folder is in the OS **if and only if** it has a row there. Parse the table; walk what it lists and nothing else.

- **Pass:** The table is present and parses; report which folders opted in.
- **Fail:** No `## Folder map` section, or it doesn't parse as a table. Without it, nothing is in scope.
- **Never a finding:** A folder on disk that is *not* in the table. It is not part of the OS. Do not report it, do not count it, do not suggest adding it. Say nothing.

**Check 0.3 — Instance overlay**

Report whether an `acos-integrity` overlay was found and whether it carried a parseable `acos-config` block.

- **Pass:** Overlay found and config loaded.
- **Warning:** Overlay file exists but carries no `acos-config` block, so the run silently fell back to framework defaults.
- **Info:** No overlay. This is a valid, fully-conformant state.

**Check 0.4 — The walk itself**

Report how many folders were inspected and how many OS documents were read. This check exists because **a conformant instance emits almost no findings**, which makes it look exactly like a run where the walk did nothing — the failure the folder-map format can cause (reformat the table and the checker walks nothing and reports a cheerful pass).

- **Pass:** The walk inspected at least one folder; the message says how many.
- **Fail:** The roster was empty, or the roster named folders and the walk inspected none of them. **A run that walked nothing is never a pass**, in any report and in any exit code, even without `--strict`.

### Category 1: README cascade completeness

These checks confirm the README cascade is populated **for the folders that are in the OS**.

**Check 1.1 — Instance root README exists**

The instance root (the folder containing `company-brief.md`) must have a `README.md`.

- **Pass:** `README.md` exists.
- **Fail:** `README.md` is missing.

**Check 1.2 — Folders on the roster have READMEs**

Every folder listed in the root README's folder map must exist and must contain a `README.md`. A folder on the roster opted into the OS, so it owes the OS a front door: without a README nothing declares what it is or what its children are.

- **Pass:** Every folder in the map exists and has a `README.md`.
- **Fail:** A folder in the map doesn't exist on disk, or exists with no `README.md`.

**Check 1.3 — A folder's declared type matches its position**

The `type` in a folder README's frontmatter is what tells an agent whether to descend into that folder, so a wrong one sends the whole cascade the wrong way. A roster folder is expected to be a container (or an asset library, if it says so); a child of a container is expected to be an item.

- **Pass:** The declared type matches what the folder's position implies.
- **Warning:** The type is legal but not the one this position implies (for example a container README typed `folder-readme-item`). Never a failure — the frontmatter is allowed to be the authority on what a folder is; this check just says the two disagree.

**Check 1.4 — A container's child without a README is not an OS item**

A folder inside a container with no `README.md` has **not opted into the OS**. This is *information, not an error* — a folder is in the system only if it says so, and plenty of folders correctly say nothing.

- **Pass:** The child has a `README.md`; it is an OS item and the cascade continues into it.
- **Warning (informational):** No `README.md`. Report it as what it is — *this folder is not visible to the OS and agents will not read into it* — and name the three ways to change that, all of them valid: give it a README (to include it), type its parent `folder-readme-asset` (to declare it material rather than structure), or underscore-prefix it (to hide it). Doing nothing is also valid.
- **Never a fail.** A missing README is an absence of opt-in, not a violation. Reporting it as a failure inverts the model and trains people to ignore the checker.

**Check 1.5 — Asset libraries end the walk**

A folder whose README says `type: folder-readme-asset` — or that the overlay names in `asset-folders` — is an **asset library**. Its children are *material*: files, images, scanned documents, sub-folders of assets. They are not OS items.

- **Info:** Validate the asset README, then **stop**, and say where the walk stopped. A reader who sees no findings for a folder full of logos should be able to tell that the checker deliberately ended the walk there rather than silently skipping it.
- **Do not walk into an asset library's children, at any depth.** They never need READMEs and never carry frontmatter. Produce **no findings** for anything inside one.
- An asset library on the roster with no README at all is still a 1.2 failure.

### Category 2: Brief and manifest presence

These checks confirm that the substantive companion documents exist where the framework expects them.

**Check 2.1 — Company brief exists**

The instance root must contain `company-brief.md`.

- **Pass:** `company-brief.md` exists.
- **Fail:** `company-brief.md` is missing.

**Check 2.2 — Client folders have briefs**

Every client folder inside a client container (`Clients/` by default; overlay key `client-containers`) should contain a `brief.md`.

- **Pass:** Client has `brief.md`.
- **Warning:** Client folder exists but has no `brief.md` (may be a newly scaffolded client).

**Check 2.3 — Client folders have manifests**

Every client folder inside a client container should contain a `manifest.md`.

- **Pass:** Client has `manifest.md`.
- **Warning:** Client folder exists but has no `manifest.md`.

**Check 2.4 — No duplicate briefs**

A client folder should have exactly one `brief.md`. Files like `brief 2.md` or `brief-draft.md` alongside the canonical brief are flagged — that is what a cloud-sync conflict looks like, and two briefs mean an agent will read the wrong one half the time.

- **Pass:** Exactly one `brief.md`.
- **Warning:** Additional brief-like files found alongside `brief.md` (list them).

**Check 2.5 — Frontmatter presence and required fields**

Every OS document (README, brief, manifest) must open with frontmatter carrying `type`, `status`, `last-updated`, `maintainer`, `purpose`.

- **Pass:** All five fields present and non-empty.
- **Warning:** Frontmatter exists but is missing one or more of the required five.
- **Fail:** No frontmatter at all, or it could not be parsed.
- **Exempt:** The direct children of a container named in the overlay's `repo-child-containers`. Their `README.md` is a codebase README owned by that repository, not an OS-managed document.

### Category 3: Frontmatter validation

**Check 3.1 — Type values are recognized**

Every `type:` value must be one of the recognized types. The taxonomy is defined in [`framework/README.md`](../../README.md#frontmatter) — that list is the source of truth, and this skill defers to it rather than restating it. Instances may add their own via the overlay's `custom-types`.

- **Pass:** All type values are recognized.
- **Warning:** The type is not in the taxonomy and the overlay didn't declare it.
- **Info:** The type is one the framework uses in its own artifacts but has not yet written into the manual's taxonomy. Accepted, and reported so the drift stays visible.

**Check 3.2 — Status values are valid**

`status` must be one of the values in the framework [status vocabulary](../../README.md#status-vocabulary) — that list is the source of truth and this skill defers to it. Instances may add their own via the overlay's `custom-statuses`.

- **Pass:** All status values are recognized.
- **Warning:** Unrecognized status value.

**Check 3.3 — Dates are ISO 8601**

`last-updated` values must be `YYYY-MM-DD`.

- **Pass:** Valid ISO 8601.
- **Fail:** Any other format. This one *is* a failure: the field exists to be machine-read, and a date a tool cannot parse is a field that does not work.

**Check 3.4 — Staleness**

A document with `status: active` whose `last-updated` is older than the staleness limit (90 days by default; overlay key `staleness-days`, `0` to turn it off).

- **Pass:** All active documents are within the limit.
- **Warning:** An active document has not been touched in longer than the limit. Either refresh it or give it an honest status — `stale`, `paused`, `dormant`, and `wrapped` all exist, and none of them is flagged here.
- **Never a fail.** Only a human knows whether an old document is wrong or simply finished.

### Category 4: Folder naming

**ACOS does not govern letter case.** See [Folder naming — structure, not style](../../README.md#folder-naming--structure-not-style), which is the source of truth. A capitalized folder name produces **no finding**. Neither does a lowercase one, a mixed-case one, or an underscore inside a name. Do not flag style. Do not suggest renames on aesthetic grounds.

**Check 4.1 — Folder names don't contain characters that break things**

The only naming finding the framework makes. A name containing a space, `#`, `?`, `%`, `\`, `:`, `|`, `*`, `<`, `>`, or `"` breaks real machinery — shell paths, markdown links, URLs — and that's worth saying out loud.

- **Pass:** No breaking characters.
- **Warning:** A breaking character is present. Say **concretely what it breaks** (a space needs `%20` in a URL, angle brackets in a markdown link, and quoting in a shell; a `#` truncates a URL at the fragment; a `*` is a glob wildcard). Never a failure — a legacy folder with a space in it works fine until something links to it, and renaming may break references that already point at it.
- The instance root folder is exempt (it's named for the instance), as is any name in the overlay's `naming-exempt`.

**Check 4.2 — The instance's own naming style, if it declared one**

The framework ships **no** default naming convention. An instance that wants one enforced sets `naming-style` in its overlay (`kebab-case` or `capitalized`).

- **Not run at all** when the overlay carries no `naming-style` key. This is the default, and a clean instance that never declares one is fully conformant — the report says so explicitly under "Not run".
- **Pass:** Names match the instance's declared style.
- **Warning:** A name doesn't match the style the instance declared for itself.

### Category 5: Agent-ignore compliance

**Check 5.1 — Underscore-prefixed folders are not linked into**

No OS document should link to something inside an `_`-prefixed **folder**. Agents are told to skip those folders at any depth, so a link into one is a pointer the reader has been instructed not to follow: either the link is wrong or the underscore is.

- **Pass:** No OS document links into an `_`-prefixed folder.
- **Warning:** A link resolves through an `_`-prefixed folder (file and line reported).
- **Folders, not files.** [`agent-ignore.md`](../../agent-ignore.md) scopes the rule to folders (`_*/`, `**/_*/`), and the framework depends on that: [`client-brand-capture`](../client-brand-capture/SKILL.md) deliberately writes `Brand/_principal-review.md` and the client brief template deliberately links to it. An underscore-prefixed *file* is not agent-ignored and is not flagged. Flagging the framework's own prescribed output is how a validator teaches people to ignore it.

### Category 6: Overlays

**Check 6.1 — Overlays have matching skills**

Every overlay in `<instance-root>/overlays/` should correspond to a skill in the framework's `skills/` directory. An overlay with no skill is dead configuration: nothing will ever read it, and the day someone edits it expecting an effect is the day the instance lies to its owner.

- **Pass:** Every overlay has a matching framework skill.
- **Warning:** Overlay exists with no matching framework skill (orphaned overlay).
- **Not run** when the framework directory can't be found from where the script is running (pass `--framework`).

**Check 6.2 — Overlay frontmatter is valid**

Every overlay should carry frontmatter with `type: skill-overlay`, `skill`, `instance`, and `last-updated`.

- **Pass:** Valid frontmatter.
- **Warning:** Missing one or more required fields, or a `type` other than `skill-overlay`.
- **Fail:** No readable frontmatter at all.

### Category 8: Cross-reference integrity

**Check 8.1 — Internal links resolve**

Every relative markdown link in an OS document must resolve to something that exists on disk. Anchors, `mailto:`, and absolute URLs are ignored; `%20` and other percent-escapes are decoded before resolving, so a link into a folder with a space in its name is judged on what it actually points at.

- **Pass:** All internal links resolve. The message says how many were checked.
- **Warning:** A link target doesn't exist (file and line reported), or a template placeholder like `<client-name>` survived into a live document.
- **Never a fail**, because a link usually breaks when the *target* moves, and the person running the checker is often not the person who should fix it.

This is the highest-value check in the set and the one the framework went longest without. A stale internal link is precisely the rot ACOS exists to prevent: the tree looks navigable, an agent follows a pointer, and the pointer goes nowhere. Two dead links sat in the reference instance's own root README for months because nothing looked.

The checker only follows links in documents the walk actually opened — so nothing outside the OS, and nothing behind an asset library, is ever reported.

## What this checker deliberately does not check

An honest list of things it would be easy to add and wrong to:

- **Markdown style** — curly quotes, `---` dividers, title-case headings. The framework [decided that it governs structure, not style](../../../docs/extending-acos.md#acos-governs-structure-not-style), and policing prose style is the same category error as policing letter case: apply the test — *if the convention were violated, what would actually break?* — and the honest answer is "nothing, it would just look inconsistent." A validator that spends its warnings on aesthetics trains everyone to ignore its warnings, including the ones that matter. The framework's markdown-style house rule remains as guidance for agents *writing* files; it is not the validator's business. (Earlier versions of this spec described checks 7.1-7.3 for exactly this. They were never implemented and have been deleted rather than built.)
- **Reciprocal cross-references** (a brief and a README pointing at each other) — good practice, not a rule. Nothing breaks when they don't.
- **Template shape conformance** (does this README have the same sections as its template?) — templates are starting points, not schemas. A folder that outgrew its template is healthy, not broken.
- **Template coverage** (does every pattern in use have a template?) — a property of the *framework*, not of an instance, so it belongs in the framework's own test suite, and that is where it now lives.
- **Content-level analysis** — contradictory briefs, an identifier in a manifest that never appears in the brief, circular reference chains. All require reading meaning rather than structure. If they become worth doing, they are a skill's job, not a script's.
- **The framework's own health** — a missing `agent-ignore.md`, a broken link inside ACOS itself. This script checks an *instance*. The framework checks itself with [`scripts/check-links.py`](../../../scripts/check-links.py) and its unit tests, in CI, on every push.

## Running the checks

### Walk order

1. Start at the instance root (the folder containing `company-brief.md`).
2. Read the instance root `README.md` and parse the `## Folder map` table. **That table is the roster** — it is the complete list of what is in the OS.
3. Walk each folder on the roster, reading its README. Anything on disk that isn't on the roster is not part of the OS: don't walk it, don't report it, don't mention it.
4. At each folder, let its README's `type` tell you what to do next:
   - `folder-readme-container` → descend into its children; each child with a README is an OS item, and each child without one is simply not in the OS (check 1.4, a warning, not a failure).
   - `folder-readme-asset` → **stop**. Its children are material, not structure. Do not descend, at any depth.
5. Skip all `_`-prefixed folders, at any depth (per the agent-ignore convention).
6. Collect every `README.md`, `brief.md`, `manifest.md`, `dashboard.md`, and overlay encountered. Checks 5.1 and 8.1 run over that collection at the end, so they see exactly what the walk saw.

### Check execution

- Run every check, collecting results. A check that finds nothing has still *run*, and the report says so.
- A check with nothing in this instance to run against (no client container, no declared naming style, no overlays) is reported under **Not run**, with the reason. It is not a pass and not a failure.
- A check that encounters an error (permission denied, unreadable file) produces a **warning** and continues.

### Report format

```
# ACOS Integrity Report — <instance name>

**Date:** YYYY-MM-DD
**Instance root:** <path>
**Checks attempted:** 22 of 23 (0.1, 0.3, 0.4, 1.1, ...)
**Findings:** 13 pass · 4 warning · 0 fail · 2 info
**Inspected:** 30 folders, 38 OS documents

**Not run:**
- 4.2 Instance naming style — this instance declared no naming-style (the framework ships no default)

✅ 0.1 Folder map — the membership roster — pass: 7 folders opted into the OS: ...
⚠️ 1.3 Declared type matches position — warning: Clients/README.md type is 'folder-readme-root', expected 'folder-readme-container'
⚠️ 8.1 Internal links resolve — warning: README.md:101 -> ../Products/gone/README.md (does not exist)
❌ 1.2 Roster folder has a README — fail: 'Vault' is listed in the folder map but has no README.md

## Items needing attention
1. [❌] ...
2. [⚠️] ...
```

**Checks attempted is not the same number as findings**, and reporting the latter as the former is a bug this skill has already shipped once. A clean instance emits four or five findings and runs all 23 checks; a broken walk emits four or five findings and runs *nothing*. The counter has to be able to tell those apart, so it counts checks attempted, names them, names the ones that didn't run and why, and says how many folders and documents were actually inspected. A run that walked zero folders prints a banner saying it is not a pass, and exits non-zero regardless of `--strict`.

### Severity guide

- **✅ Pass** — Convention met. No action needed.
- **⚠️ Warning** — Convention may not be met, or a gray area. Review and decide.
- **❌ Fail** — Convention violated. Fix recommended.
- **ℹ️ Info** — Not a finding. Something worth knowing (the walk stopped here; this type isn't in the manual yet).

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
staleness-days: 90
```
````

| Key | Meaning | Default with no overlay |
|---|---|---|
| `instance-name` | Display name; also exempt from the folder-name check (the instance root is named for the instance, not for its contents). | The instance root folder's name. |
| `client-containers` | Folders whose direct children are client engagements. Checks 2.2-2.4 apply to each child. | `Clients` |
| `asset-folders` | Folders that *are* asset libraries: the walk stops at them and their children are never OS items (check 1.5). Usually unnecessary — a folder whose own README says `type: folder-readme-asset` is already treated as one. This key is for saying it once here instead. | none |
| `repo-child-containers` | Containers whose direct children are self-contained repositories. Their `README.md` is a codebase README owned by that repo, so checks 2.5 and 3.1 are exempt for them. | none |
| `exclude-folders` | Folders to skip during the walk, in addition to `_`-prefixed and hidden folders. Rarely needed: a folder that shouldn't be in the OS should simply not be on the roster. | none |
| `suppress-checks` | Check IDs to skip entirely (e.g. `4.1`). Suppressed checks are named in the report, so suppression is visible rather than silent. | none |
| `custom-types` | Instance-specific `type:` values treated as valid in addition to the framework taxonomy (check 3.1). | none |
| `custom-statuses` | Instance-specific `status:` values treated as valid (check 3.2). | none |
| `naming-exempt` | Folder names exempt from the naming checks (4.1, 4.2) — the place to record accepted legacy names. | none |
| `naming-style` | The instance's **own** naming policy, enforced as a warning (check 4.2): `kebab-case`, `capitalized`, or `none`. **The framework ships no default and has no opinion on case** — with no key, check 4.2 does not run. | `none` |
| `staleness-days` | How long an `active` document may go untouched before check 3.4 mentions it. `0` turns the check off. | `90` |

Report destination is prose, not config: the script writes to stdout, and the agent routes the report per the overlay's routing section.

The skill is self-sufficient without an overlay. With no overlay, the script falls back to convention-based discovery: instance root by walking up for `company-brief.md`, in-scope folders from the root README's folder map, `Clients` as the client container.

## Running the script

```
python3 <path-to-acos>/scripts/acos-integrity-check.py [--root PATH] [--overlay PATH] [--framework PATH] [--strict]
```

- `--root` — the instance root (the folder containing `company-brief.md`). Defaults to walking up from the working directory.
- `--overlay` — an explicit overlay path. Defaults to `<instance-root>/overlays/acos-integrity.md`.
- `--framework` — the ACOS `framework/` directory, used to pair overlays with skills (check 6.1). Defaults to the `framework/` next to the script.
- `--strict` — exit non-zero if any check fails. Useful in CI; off by default so scheduled runs report rather than break. A run that walked **nothing** exits non-zero either way: that is a broken checker, not a clean instance.

The script is stdlib-only and has no dependencies. Its tests live in `tests/test_acos_integrity_check.py` and run in CI on every push and PR — including a test that this document and the script implement the same set of checks.

## Links

- Framework README: [`../../README.md`](../../README.md)
- Agent-ignore convention: [`../../agent-ignore.md`](../../agent-ignore.md)
- Templates directory: [`../../templates/`](../../templates/)
- Instance root: the folder containing `company-brief.md` in the instance being checked. Resolved at runtime, never hardcoded.
