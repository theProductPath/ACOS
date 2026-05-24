---
type: brand-asset
asset: type-system
subject: <Client name>
last-updated: YYYY-MM-DD
maintainer: <Principal name>
purpose: Captured typography for <Client name> — fonts in use, weights, fallback chains. Source of truth for any agent producing client-facing artifacts.
---

# <Client name> — Typography

Source: <client-domain>, captured YYYY-MM-DD.

## Fonts in use

| Role | Font family | Confidence | Notes |
|---|---|---|---|
| Headings | <font name> | <High/Med/Low> | <e.g., "Loaded via Google Fonts; weights 600 and 700 used."> |
| Body | <font name> | <conf> | <e.g., "Same as headings, weight 400."> |
| Display / hero | <font name, if distinct> | <conf> | <notes> |
| Monospace / code (if present) | <font name> | <conf> | <notes> |

## Weight and size scale

Captured from rendered styles on the homepage and confirmed secondary pages.

| Level | Size (px) | Weight | Use |
|---|---|---|---|
| H1 / hero | ~__px | ___ | Hero headline. |
| H2 | ~__px | ___ | Section headers. |
| H3 | ~__px | ___ | Sub-section headers. |
| Body | ~__px | ___ | Default paragraph text. |
| Small / caption | ~__px | ___ | Captions, footnotes. |

Sizes are approximate — captured from the rendered styles, which vary by viewport. The principal should confirm canonical sizes before these are used as authoritative.

## Fallback chain

When applying this typography in environments without the live web fonts loaded (Word, PowerPoint, PDF generation):

| Primary | Fallback 1 | Fallback 2 | Generic |
|---|---|---|---|
| <font name> | <web-safe alternative> | <system font> | sans-serif / serif |

## Web font loading

If the fonts are served via a font service (Google Fonts, Adobe Fonts, self-hosted), note here:

- **Source:** <Google Fonts / Adobe Fonts / self-hosted / system>
- **License notes:** <if known; if open-source, note license; if licensed, mark as TODO for the principal>
- **Embed URL:** <if Google Fonts or similar, the embed link>

## TODO sentinels

> **TODO:** Verify with <Principal name> — <list each low-confidence or approximated extraction>

## How this was extracted

See [`../_sources.md`](../_sources.md) for the audit trail.
