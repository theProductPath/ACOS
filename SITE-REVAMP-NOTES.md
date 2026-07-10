# ACOS marketing site — revamp status (read me first)

**Branch:** `gh-pages` (this site). Framework lives on `main`.
**Last worked:** 2026-07-09. Live at `acos.theproductpath.com`.
**Spec:** all of this follows `Brand/document-templates/product-page-style-spec.md` — ACOS is now the **flagship reference implementation**. Read that spec before making changes.

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

**adopt.html — first-pass improvement only**
- Numbered step badges (circled numbers in a left gutter), a folder-tree diagram in "The shape of an instance," cleaned meta chips (no version/Apache). Still fundamentally a text guide.

**Static asset for the Products page**
- `Brand/logos/acos/acos-context-cascade.svg` + `.png` — a tall/portrait snapshot of the animation's final "ready" state, for the theProductPath **Products** page. (PNG rendered with fallback fonts in the sandbox; SVG is font-correct. For a pixel-perfect PNG, screenshot the live hero's final frame.)

---

## What's LEFT to do

1. **blueprint.html & cascade.html** — only have Pass-1 header/footer. They're interactive explainers and still need the flagship body treatment / de-boxing pass. **(Deliberately deferred — not done yet.)**
2. **adopt.html** — reduce text density further if desired (e.g. lighter treatment for the "What ACOS asks of you" list and the checklist). Numbered-step structure is the current win.
3. **Products-page image** — decide final crop/placement; optionally regenerate the PNG in true brand fonts (Inter / JetBrains Mono) via a live-frame screenshot.
4. **AIRS** (the other flagship) — retro-review against the updated spec + this ACOS reference.

## Handy pointers
- The animated hero is inline in `index.html` (search `acoshb-` for the SVG/CSS/JS block; the phase timeline + "ready" tagline are in the `<script>`).
- Edits this session were made as `.py` transform scripts (in the agent's scratch outputs) then committed here — not required to keep, just how they were applied.
- Cross-page header/footer must stay identical; if you touch one page's nav/footer, mirror it on all four.
