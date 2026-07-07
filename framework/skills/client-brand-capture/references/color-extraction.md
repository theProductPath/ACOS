---
type: skill-reference
skill: client-brand-capture
last-updated: 2026-05-12
purpose: Heuristics for extracting a usable brand palette from a marketing website's HTML and CSS.
---

# Color extraction — heuristics

Goal: turn raw color declarations on a website into a small, role-tagged palette a designer would recognize as that company's brand.

## Sources to parse

Parse colors from, in order of weight:

1. **CSS custom properties** (`--primary`, `--brand`, `--accent`, etc.) — declared on `:root` or top-level selectors. These are the highest-signal: if a site defines `--brand: #c75c2a`, that's the brand.
2. **Inline `style=` attributes** on `<header>`, hero sections, primary CTAs.
3. **External stylesheets** — parse and walk all `color`, `background-color`, `border-color`, `fill`, `stroke`, and `background` declarations.
4. **SVG `fill` and `stroke`** on logo and icon elements.
5. **Computed styles via headless render**, when static parsing under-counts (sites with heavy JS theming).

Normalize all values to lowercase hex (`#rrggbb`). Strip alpha unless meaningfully <1 and used recurrently.

## Clustering

Raw extraction often yields 80–200 distinct colors due to anti-aliasing, opacity variants, and one-off design exceptions. Cluster aggressively:

- **Merge near-duplicates** within ΔE 3 (perceptual distance) — these are anti-aliasing artifacts or near-identical shade variants.
- **Collapse opacity stacks** — `#000000` at 0.1, 0.2, 0.4 opacity all map to the same base color with overlay notes.
- **Drop one-offs** — colors appearing fewer than 3 times across the corpus are usually noise (stock photo color picks, third-party widget defaults).

After clustering, you should have 10–25 distinct colors.

## Role tagging

Assign each remaining color a role by where it appears:

| Role | Heuristic |
|---|---|
| **Primary** | High frequency on `<header>` background, CTA buttons, branded `<svg>` logo fills, or in any CSS variable named `--primary`, `--brand`, `--accent`. |
| **Secondary** | Recurring but not dominant — used on secondary CTAs, section accents, illustration highlights. |
| **Text — body** | The color of `<p>`, `<li>`, and default `<body>` text. Usually a dark gray (`#2a2a2a`–`#4a4a4a`) or near-black. |
| **Text — heading** | Heading element colors if different from body. Often near-black or the primary brand color. |
| **Surface — page** | Body / page background. |
| **Surface — card** | Recurring background for cards, panels, sections. |
| **Border / divider** | Thin-stroke colors on lines, table borders, input outlines. |
| **State — success / warning / error** | Greens/yellows/reds appearing on alerts, validation, status indicators. |
| **Neutral grays** | Remaining gray ramp not yet tagged. |

If a color does not clearly fit a role, tag it `unassigned` and surface in the TODO list.

## Output to `palette.md`

The palette file should present colors in this order, with hex codes and usage notes. Mark every value extracted by the skill with a confidence rating:

- **High** — appeared as a CSS variable, in `<header>` or hero CTA, or in the logo SVG.
- **Medium** — recurring across the corpus but not in a high-signal location.
- **Low** — extracted but ambiguous; flag with a TODO sentinel.

Always include a "How to use" line per color. Even at low confidence, suggesting an intent helps the principal decide whether the extraction is right.

## What to skip

- **Stock photo colors** — colors sampled from large image regions almost never belong to the brand.
- **Third-party widget defaults** — chat widgets, social embeds, video players bring their own palettes. If a color appears only inside iframes or known-third-party class names (e.g., `intercom-`, `hubspot-`, `zd-`), drop it.
- **Browser defaults** — `currentColor`, `transparent`, default link blue.

## Edge cases

- **Dark / light mode** — many modern sites ship both. Capture both palettes if both are present, and tag each token with its mode. The principal decides which mode is canonical.
- **Gradient brands** — when the brand uses a gradient (e.g., a fintech with a purple-to-blue header), capture the gradient stops as a single `gradient` entry plus the individual stop colors as primary candidates.
- **No CSS variables** — older or hand-coded sites may have none. Lean harder on header/CTA frequency.
- **Heavy JS theming** — if static parse is sparse, fall back to a headless render and parse computed styles on key elements.
