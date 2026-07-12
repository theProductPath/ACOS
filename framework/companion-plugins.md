---
type: framework-doc
folder: ACOS-framework
status: active
last-updated: 2026-07-12
maintainer: Steven Jones
purpose: Defines the companion-plugin convention — how ACOS skills declare optional partner plugins that enhance their output without becoming dependencies.
---

# Companion plugins

A **companion plugin** is a third-party plugin (typically from the Anthropic plugin marketplace or a similar source) that *enhances* an ACOS skill when present but is *not required* for the skill to function. The convention exists so ACOS skills can take advantage of high-quality specialty plugins without forcing every instance adopter to install the same set.

## The rule

A skill that declares a companion plugin must:

1. **Work standalone.** Without the companion installed, the skill produces a complete (if lower-fidelity) output. Failure to install the companion is never a runtime error.
2. **Detect the companion at runtime.** Check whether the companion's tools are available before attempting to use them.
3. **Degrade gracefully.** When the companion is absent, the skill writes its own scaffolded output and clearly marks where a deeper pass by the companion would improve quality.
4. **Log the handoff.** When the companion is used, record the handoff in the skill's audit trail (e.g., `_sources.md` for `client-brand-capture`) so the principal can see which output came from where.

A skill that breaks when a companion isn't installed is a framework bug.

## Why this convention exists

ACOS is meant to run anywhere — on a small one-person consultancy, on a mid-sized agency, in a Fortune-500 product org. Each environment will have a different set of installed plugins, and a useful framework cannot assume a particular plugin shelf. Companion declaration lets a skill say "I would do better with X, but I still do my job without it."

It also separates concerns. ACOS skills are framework-level capabilities. A specialty plugin like `brand-voice` exists for one well-defined purpose and is maintained independently. Wiring them together via opportunistic detection keeps the skill independently useful while letting the marketplace plugin do what it does best.

## SKILL.md section convention

Skills declare their companions in a section titled `## Companion plugins` near the bottom of `SKILL.md`. The structure:

```markdown
## Companion plugins

This skill works standalone. The following plugins enhance specific steps when present in the environment; the skill detects them and uses them opportunistically.

- **`<plugin-id>` (<marketplace name>)** — <one-line description of what it enhances>. When detected, the skill <specific handoff behavior>. When not detected, the skill <fallback behavior> and leaves a TODO for deeper analysis.

See [`<framework-relative-path>/companion-plugins.md`](...) for the general framework convention. The skill must always work without companions; companions are opportunistic enhancement, not dependencies.
```

The skill's runtime detection logic checks for the companion's tools by name pattern (e.g., `mcp__brand-voice__*`) and routes accordingly. When the handoff occurs, the audit trail records what was sent, where the output landed, and the plugin version when knowable.

## Detection patterns

Common ways a skill detects whether a companion is available:

- **Tool availability** — the companion's tools appear in the running agent's tool list. Most reliable signal.
- **Skill availability** — the companion's skills appear in the skill catalog. Useful when a companion skill is the right entry point.
- **Configuration in an instance overlay** — the instance explicitly declares the companion is installed and how to invoke it. Useful when detection is ambiguous or when an instance wants to opt out of using an installed companion.

When detection is ambiguous, prefer the safe default: assume the companion is unavailable and produce standalone output. Surfacing the decision in the run summary ("I detected `brand-voice` but didn't invoke it because…") helps the principal understand what happened.

## Documenting a new companion

When a new companion plugin is added to a skill:

1. Add a `## Companion plugins` section to `SKILL.md` if one doesn't exist.
2. Describe what the companion enhances, the detection rule, the handoff behavior, and the fallback behavior.
3. Update the skill's `_sources.md` template (or equivalent audit file) to capture the handoff when it occurs.
4. Test the skill **both** with and without the companion installed before treating the integration as complete. The standalone path is the load-bearing one.

## Examples in the wild

| Skill | Companion plugin | What the companion enhances |
|---|---|---|
| `client-brand-capture` | `brand-voice` (knowledge-work-plugins) | Voice and tone analysis from copy samples; generates enforceable voice guidelines. |

> **TODO:** Add new entries as skills declare companions.

## Where this convention lives

This document is part of the ACOS framework operating manual. Instances do not need to redeclare the rule — they inherit it by adopting ACOS. If an instance wants to *disable* a companion handoff for a specific skill, the instance overlay for that skill can specify "companion: off".
