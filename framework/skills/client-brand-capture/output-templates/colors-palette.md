---
type: brand-asset
asset: color-palette
subject: <Client name>
last-updated: YYYY-MM-DD
maintainer: <Principal name>
purpose: Captured color palette for <Client name>, with role tagging and usage notes. Source of truth for any agent producing client-facing artifacts.
---

# <Client name> — Color palette

Source: <client-domain>, captured YYYY-MM-DD.

Every token below carries a confidence rating: **High** (CSS variable, header / hero / CTA, logo SVG), **Medium** (recurring across the site), **Low** (extracted but ambiguous — verify before use).

## Primary

| Name | Hex | Confidence | How to use |
|---|---|---|---|
| <Primary 1> | `#______` | High | <e.g., "Brand color — buttons, logo, headline accents."> |
| <Primary 2, if applicable> | `#______` | <High/Med/Low> | <usage> |

## Secondary

| Name | Hex | Confidence | How to use |
|---|---|---|---|
| <Secondary 1> | `#______` | <conf> | <usage> |
| <Secondary 2> | `#______` | <conf> | <usage> |

## Neutrals

| Name | Hex | Confidence | How to use |
|---|---|---|---|
| Text — body | `#______` | <conf> | Default body text color. |
| Text — heading | `#______` | <conf> | Heading text if distinct from body. |
| Surface — page | `#______` | <conf> | Page background. |
| Surface — card | `#______` | <conf> | Card / panel background. |
| Border / divider | `#______` | <conf> | Thin-stroke borders, dividers, input outlines. |

## State (if present)

| Name | Hex | Confidence | How to use |
|---|---|---|---|
| Success | `#______` | <conf> | Confirmations, success messages. |
| Warning | `#______` | <conf> | Cautionary states. |
| Error | `#______` | <conf> | Validation errors, destructive actions. |

## Dark mode (if captured)

> Captured / Not present.

If captured, repeat the structure above with dark-mode equivalents.

## Gradients (if used)

| Name | Stops | Use |
|---|---|---|
| <Gradient name> | `#______ → #______` | <e.g., "Hero section background"> |

## TODO sentinels

> **TODO:** Verify with <Principal name> — <list each low-confidence extraction>

## Usage notes

> **TODO:** Once verified, capture any client-specific application rules — e.g., "Primary color is only used on CTAs and the logo, never on body backgrounds" or "Dark surfaces are reserved for navigation, not content."

## How this palette was extracted

See [`../_sources.md`](../_sources.md) for the audit trail.
