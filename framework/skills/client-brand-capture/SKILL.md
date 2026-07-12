---
name: client-brand-capture
description: Capture a client's visual and verbal brand identity from their primary marketing site (or supplied URLs) and write the results into the client's Brand/ subfolder under an ACOS instance. Use when scaffolding a new client folder, when a client folder lacks a Brand/ subfolder, when refreshing existing brand data, or when the user says "capture brand for <client>", "build the Brand folder for <client>", or similar. The skill drafts brand artifacts with TODO sentinels; final values are confirmed by the instance's principal before commit.
---

# Client Brand Capture

Capture a client's existing brand — colors, typography, logos, voice — from their public web presence and write structured artifacts into the client's `Brand/` subfolder. The skill produces a draft brand kit that the instance's principal reviews and signs off on; nothing extracted is treated as authoritative until human verification.

## When this skill triggers

- During the new-client checklist in `Clients/README.md` (step that creates the `Brand/` subfolder).
- When the user says "capture brand for <client>", "build the Brand folder for <client>", "scaffold brand for <client>", or similar.
- When the user asks to refresh or update an existing client's `Brand/` folder.
- When an agent is about to produce a client-facing artifact and the client's `Brand/` is missing or empty.

## Inputs

Required:

- **Client folder path** — the path to `Clients/<client>/` under the ACOS instance.
- **Primary marketing URL** — the client's canonical homepage. The skill asks the user for this if not supplied. For most B2B clients, this is the marketing root (e.g., `acme.com`), not a product or app subdomain.

Optional:

- **Additional URLs** — about page, services page, leadership/team page. The skill suggests these by following nav links on the homepage and asks the user to confirm or supply.
- **Logo file uploads** — if the user already has higher-fidelity logo assets, they can be dropped into `Brand/logos/` and the skill will skip web extraction for logos.

## Instance overlay discovery

Before doing anything else, look for an instance overlay:

1. Find the instance root — the folder containing `company-brief.md`. Walk up from the working directory if needed.
2. Look for `<instance-root>/overlays/client-brand-capture.md`.
3. If present, load it. The overlay may specify: preferred logo size variants, brand-data conventions specific to the instance, an alternative location for brand assets, or skill-specific routing rules.
4. If absent, proceed with framework defaults.

## Principal routing

This skill produces draft brand data that requires human verification. All TODO sentinels and verification prompts route to **the instance's principal** — never to a hardcoded name.

To resolve the principal:

1. Read `<instance-root>/company-brief.md`.
2. Locate the **Principals** subsection under the `People` section.
3. If a single principal is listed, route to that name.
4. If multiple principals are listed, route to the one marked **primary stakeholder**.
5. If no `Principals` subsection exists in the company brief, fall back to the `maintainer` value in the company brief frontmatter and surface a one-line note that the instance should formalize its principals.

TODO sentinels in generated artifacts use the phrasing: `> **TODO:** Verify with <principal name>.` — substituting the resolved name. The framework convention is *principal*; *primary stakeholder* is reserved for designating the final escalation point in multi-principal instances. Both terms are documented in the [ACOS framework README](../../README.md).

## Tool requirements and extraction tiers

This skill produces dramatically different output quality depending on what extraction tooling is available. Detect at run start and announce the tier to the user.

### Tier 1 — Live browser (preferred)

A connected live browser (Chrome MCP via `mcp__Claude_in_Chrome__*`, or computer-use against an open browser window) is the **preferred** path. With a live page session, the skill can:

- Read computed styles on any element — gives exact hex codes for colors, font families with full fallback chain, and actual rendered sizes.
- Run JavaScript across the page to collect frequency-weighted color/font usage.
- Fetch asset URLs (logo SVGs, favicons) via `fetch()` in the page context and save them to `Brand/logos/` directly.
- Walk the site naturally — hover states, modals, dark sections — for a complete extraction.

A Tier 1 run typically produces a near-complete brand kit with only judgment-call TODOs left (e.g., "Is this green approved for client-facing copy or just internal?").

### Tier 2 — Computer-use against a live browser

If Chrome MCP isn't connected but a desktop browser session is reachable via `mcp__computer-use__*`, the skill can drive the browser directly: open dev-tools, read computed styles by screenshot+OCR, save assets via right-click → save. Less precise than Tier 1 and slower, but still yields actual computed values rather than static-HTML guesses.

### Tier 3 — Static HTML fetch (fallback)

If no live browser is available, the skill falls back to static HTML retrieval via WebFetch. This path:

- Cannot read computed CSS — colors and fonts are inferred from filenames, meta tags, and HTML structure.
- Cannot reliably download asset files — logo URLs are identified and recorded for the principal to fetch manually.
- Cannot see hover states, modal content, or JavaScript-rendered sections.

Tier 3 output should be **explicitly marked** as preliminary in the run summary and in `_sources.md`. The principal should know the gaps are tooling-bounded, not site-bounded — a re-run at Tier 1 will fill most of them.

### Tier detection

At run start, check available tools in this order:

1. Is `mcp__Claude_in_Chrome__*` available? Call `list_connected_browsers` — if a browser is connected, select it and use Tier 1.
2. Else, is `mcp__computer-use__*` available with a browser application granted? Use Tier 2.
3. Else, use Tier 3 and note the limitation in the run summary.

If a higher tier becomes available later (e.g., user starts the Chrome extension mid-conversation), the skill can be re-run to upgrade the extraction.

## Capture workflow

### 1. Confirm inputs and detect tier

- Confirm the client folder path and primary marketing URL with the user before any network activity.
- Detect the available extraction tier (see [Tool requirements](#tool-requirements-and-extraction-tiers) above) and announce it: "Running at Tier 1 (live browser)" / "Tier 3 (static HTML, expect TODO-heavy output)."
- If the client folder lacks a `brief.md` or `manifest.md`, warn but proceed — the brief edit at the end becomes a TODO entry.

### 2. Fetch source pages

- Navigate to the homepage and (if confirmed) up to three secondary pages (about, services/products, team).
- At Tier 1: drive the browser to each page in turn; capture computed styles, fetch assets, and screenshot key sections for the audit trail.
- At Tier 3: fetch HTML statically; record what couldn't be extracted.
- Record every URL fetched, with timestamp and tier, in the eventual `Brand/_sources.md`.

### 3. Extract visual identity

Refer to [`references/color-extraction.md`](references/color-extraction.md) for the heuristics. In brief:

- Parse all `color`, `background-color`, `fill`, `stroke`, and CSS variable declarations.
- Cluster by frequency and role (text, surface, accent, link, button).
- Propose a palette: 1–2 primary brand colors, 2–4 secondary, neutrals (text, surface, border).
- Extract `font-family` declarations actually used (not just declared in `@font-face`). Note weights and approximate sizes for headings vs. body.
- Identify logo candidates by source — favicon, header `<img>` with `alt` or filename containing "logo", `<svg>` with role="img" in the header. Download all candidates to a temp area; the skill picks the best (highest resolution, transparent background where available) and proposes the rest as alternates.

### 4. Extract verbal identity

Refer to [`references/voice-analysis.md`](references/voice-analysis.md). In brief:

- Pull 8–15 representative sentences from the homepage and confirmed secondary pages — hero copy, value propositions, section subheads, CTAs.
- Summarize tone (formal/casual, technical/plain, warm/precise, direct/aspirational).
- Note recurring vocabulary, characteristic phrasings, and what the copy avoids.
- **Companion plugin check:** if the `brand-voice` plugin is detected in the running environment, hand the extracted samples to `brand-voice:guideline-generation` and use its output as the body of `Brand/voice.md`. If not detected, write the skill's own lightweight summary and mark deeper analysis as a TODO. See [Companion plugins](#companion-plugins) below.

### 5. Write drafts to the Brand folder

Create `Clients/<client>/Brand/` with this structure:

```
Brand/
├── README.md                ← folder-readme-asset, navigational only (no cascade text)
├── _principal-review.md     ← single consolidated checklist of every TODO from this run
├── _sources.md              ← URLs scraped, timestamp, tier, run audit
├── colors/
│   └── palette.md           ← extracted palette with usage notes
├── typography/
│   └── type-system.md       ← fonts, weights, fallbacks
├── voice.md                 ← tone summary, copy samples, what to avoid
└── logos/                   ← downloaded logo candidates (Tier 1/2) or empty placeholder (Tier 3)
```

Use the templates in [`output-templates/`](output-templates/) as the source for each file's structure. Every uncertain extraction is marked with a `TODO: Verify with <principal>` sentinel **and** appears as a checklist item in `_principal-review.md`.

### 5a. The `_principal-review.md` consolidated checklist

This file is the **single, explicit follow-up surface** the principal works through after a run. It exists so no TODO gets lost across multiple files. Behavior:

- Frontmatter: `type: principal-review`, subject, run date, resolved principal name.
- A single checklist grouping every TODO from the run by file (colors / typography / voice / logos / sign-off), each item linking back to the file and section it belongs to.
- Cross-referenced **prominently** from `Brand/README.md` ("X items pending — see `_principal-review.md`") and from the `brief.md` "Brand & identity" section ("Draft from <date>; X items pending principal review.").
- On re-run: the skill updates the file in place — already-checked items stay checked, new items append, items resolved by the new run get auto-checked.
- When all items are checked, the skill (or the principal manually) moves the file to `Brand/_archive/<date>-principal-review.md` and updates the `brief.md` brand section to drop the "pending" note.
- Until completed, any agent producing artifacts for this client should treat anything still unchecked in `_principal-review.md` as unsafe to assume. This rule belongs in the `_principal-review.md` body itself.

### 6. Update the client brief

Append (or update, if already present) a **Brand & identity** section in `Clients/<client>/brief.md`:

- 2–3 sentences summarizing visual identity (primary color, primary font, overall feel).
- 1–2 sentences on verbal identity (tone descriptor, what to avoid).
- A pointer down into `Brand/` for the full kit.

Use the template at [`output-templates/brief-brand-section.md`](output-templates/brief-brand-section.md). The skill writes this as a clearly-marked draft when `brief.md` already exists and contains other content; the principal accepts or edits it before commit.

### 7. Hand back to the user for review

Surface the results clearly:

- List every file written under `Brand/`.
- List every TODO sentinel and the proposed value for each.
- Show the proposed `brief.md` edit as a diff.
- Ask the principal to confirm, edit, or reject before the work is considered final.

## Outputs

- `Clients/<client>/Brand/` populated per the structure above
- `Clients/<client>/brief.md` updated with a "Brand & identity" section
- A summary message listing files, TODOs, and the brief edit for the principal's review

## Re-running on an existing Brand folder

The skill is idempotent but not destructive:

- If `Brand/` already exists, do not overwrite files without explicit user confirmation.
- Compare new extractions to existing values and surface diffs. Default behavior: write new findings to `Brand/_proposed/` and let the principal merge.
- Always append (not replace) the run entry in `Brand/_sources.md`.

## Companion plugins

This skill works standalone. The following plugins enhance specific steps when present in the environment; the skill detects them and uses them opportunistically.

- **`brand-voice` (knowledge-work-plugins marketplace)** — deeper voice-and-tone analysis and enforcement. When detected, the skill hands voice samples to `brand-voice:guideline-generation` for `Brand/voice.md` and notes the handoff in `_sources.md`. When not detected, the skill writes its own lightweight summary and leaves a TODO for deeper analysis.

See [`../../companion-plugins.md`](../../companion-plugins.md) for the general framework convention. The skill must always work without companions; companions are opportunistic enhancement, not dependencies.

## House rules this skill respects

- `Brand/` is an **asset library** (`type: folder-readme-asset`): its children (`colors/`, `typography/`, `logos/`) hold material, not OS items, so they carry no READMEs and nothing walks into them looking for structure.
- TODO sentinels for any value the skill could not verify, routed to the resolved principal.
- ISO dates (`YYYY-MM-DD`) in `_sources.md` and frontmatter.
- Frontmatter on every generated `.md` file (folder-readme-asset for `Brand/README.md`, content-file types for the others).
- Sentence-case headings, straight quotes, dashes per ACOS markdown house style.

## Links

- Framework house rules: [`../../README.md`](../../README.md)
- Companion plugins convention: [`../../companion-plugins.md`](../../companion-plugins.md)
- Output templates: [`output-templates/`](output-templates/)
- References: [`references/`](references/)
