# ACOS marketing site — revamp status (read me first)

**Branch:** `gh-pages` (this site). Framework lives on `main`.
**Last worked:** 2026-07-10. Live at `acos.theproductpath.com`.
**Spec:** all of this follows `Brand/document-templates/product-page-style-spec.md` — ACOS is now the **flagship reference implementation**. Read that spec before making changes.
**Positioning:** all copy follows `Projects/tPP-website/notes/acos-public-positioning-handoff-2026-07-09.md` (Drive) — ACOS is a **company context system**, not a README system; small day-one core, agents grow the instance through work. Read that note before changing any copy.

---

## What we did (done + pushed)

**Brand / logo**
- New ACOS logo: white rounded-square tile + orange **layered surfaces with a centered "you-are-here" map pin** (the cascade motif). Assets in `Brand/logos/acos/` — `favicon.svg`, PNG set (32–1024), `logo-lockup.svg` + `logo-lockup-on-light.svg`. Wordmark "ACOS" is all-orange (matches the AIRS flagship acronym convention).
- Favicon on all site pages is `favicon.svg` (white-square); `favicon.png` is the 256px white-square version.

**Header + footer (all pages: index, adopt, blueprint, cascade)**
- Standard header: white-square ACOS lockup + `THEPRODUCTPATH` wordmark, page nav kept (Home/Adopt/Blueprint/Cascade), compact CTAs (`Schedule a call` primary + `Download from GitHub` ghost). Header dimensions normalized so it doesn't shift between pages.
- Common dark family footer (`#12161d`): `ACOS · theProductPath` + copyright, product links AIRS · **ACOS** · Talent Cycle · Burner Apps · AgentComms (ACOS current/unlinked).

**index.html — fully built out (flagship)**
- **Two-column hero:** headline + CTAs left; a large **inline animated SVG "build"** right (self-contained CSS+JS, id prefix `acoshb-`). It loops a 4-phase story: your folders → ACOS drops a README `MD` in each → two LLM agents read markdown up their own paths (bi-directional, methodical, synced lighting) → agents spin up "ready to work" with the bright payoff line.
- **De-boxed sections for variety** (see spec's "Section variety"): bright editorial accent-rule list ("What ACOS is"), bright accent-bar panels ("What's included"), numbered process flow ("How it works"), divided ✕-list ("The problem"), inline stat band ("Proof"), top-accent-rule columns ("Who it's for").
- Heading width caps widened (no premature 3-line wraps). Version (`v0.1`) and license (`Apache-2.0`) language removed throughout — not part of the story.

**adopt.html — full positioning rework (2026-07-10)**
- Restructured per the positioning handoff: seven flat steps → **two phases**.
- **Phase A "Day one: the small core"** — bright band (`#f0ede8`, matches index bright sections), 4 numbered steps written from the user's perspective with explicit copy-template-then-fill mechanics (`folder-readme-root.md`, `brief-company.md`, `folder-readme-container.md` — names verified against `framework/templates/` on `main`). Step 4 is a concrete first exercise: run the `acos-integrity` skill → validates the core, saves the first agent-generated artifact to `_progress/`. Closes with a solid-orange payoff banner ("That's the whole upfront ask.").
- **Phase B "As you work: the instance grows"** — dark section; six growth events (client engagement, routing, overlay, decision record, template, dashboard) each led by a repeated orange **agent glyph** (bot badge) + `agent`/`you review`/`you decide` chips showing division of labor. `~95%` tPPOS proof point as a stat band; key-reassurance callout closes.
- "What ACOS asks of you" → three top-accent-rule columns (third is "A seed of judgment" — NOT "write it all down"). Checklist split: "Day one — you" (✓) vs "Earned over time — mostly agent-built" (bot glyphs). Hero lede + chips reframed (no "seven steps"/"20 min read"). TOC trimmed to 6 entries. "Where to go next": Blueprint + Cascade as the two cards; GitHub/Home demoted to ghost buttons.

**blueprint.html — rails + your-instance rework (2026-07-10)**
- **Two directional rails** flanking the layer stack: orange chevrons down-left ("Rules cascade down"), green (`--up:#3fb27f`) chevrons up-right ("Proven patterns promote up", fading before the views layer — views never feed back). Inter-layer flow pills are now **paired directional bands** (↓ orange / ↑ green); legend at the bottom is two matching tinted boxes.
- **De-tPPOS'd**: middle layer is "Your company instance / Your instance" — the user's company, second-person copy throughout. tPPOS appears nowhere on the page (it stays as the ~95% proof point on adopt only). Products node no longer says ACOS lives in it.
- **Dashed "ghost" cards** (`n-ghost`): 8th operating-folder slot ("Your folders…") and 4th views slot ("Your views…") — the shapes shown are common, not prescriptive.
- **Views layer corrected**: Blueprint + Cascade removed (they're marketing-site explainers now, not user presentation-layer views). Real views listed instead: **Company Atlas, Orbit Model, Product Garden** (descriptions from `tPPOS/views/*/README.md`).
- **Detail panel**: inner sticky wrapper (fixed the broken `position:sticky` — old aside had `min-height:100%`), and it now **adopts the selected node's accent color** (left stripe, kicker, gradient wash) via `detail.className` swap in `selectItem`.
- Layer headers restructured to grid so descriptions span full box width (no premature wrap under the badge column).

**Static asset for the Products page**
- `Brand/logos/acos/acos-context-cascade.svg` + `.png` — a tall/portrait snapshot of the animation's final "ready" state, for the theProductPath **Products** page. (PNG rendered with fallback fonts in the sandbox; SVG is font-correct. For a pixel-perfect PNG, screenshot the live hero's final frame.)

---

## What's LEFT to do

1. **cascade.html** — still Pass-1. Positioning-note direction: follow **one concrete task** (e.g. processing a transcript or preparing a client deliverable) through each cascade stop, showing the artifact AND its job at each stop, ending at the **write-back moment**. Carry over the blueprint's directional/agent vocabulary where it helps.
2. **Back-port the adopt reframe to `docs/adopting-acos.md` on `main`** — the markdown is canonical and still carries the old "seven steps" framing; the page and doc have now diverged.
3. **index.html positioning pass** — the note wants "records that make agents useful" and "it gets better as you use it" sections (Orient → Understand → Improve) without overwhelming the visitor. Not started.
4. **Products-page image** — decide final crop/placement; optionally regenerate the PNG in true brand fonts via a live-frame screenshot.
5. **AIRS** (the other flagship) — retro-review against the updated spec + this ACOS reference.

## Handy pointers
- The animated hero is inline in `index.html` (search `acoshb-` for the SVG/CSS/JS block; the phase timeline + "ready" tagline are in the `<script>`).
- adopt.html new CSS blocks: `.phase-a` (bright band), `.payoff`, `.grow-list`/`.agent-badge`/`.who` (Phase B), `.proof-line`, `.check-cols`, `.next-minor`.
- Cross-page header/footer must stay identical; if you touch one page's nav/footer, mirror it on all four.
