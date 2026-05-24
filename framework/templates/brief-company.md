---
type: brief-company
subject: <Company name>
status: skeleton  # skeleton | drafting | active | stale
last-updated: YYYY-MM-DD
maintainer: <Name>
purpose: Canonical company brief — the source of truth any AI tool reads when work needs to represent the company.
---

# <Company name> — Company Brief

> **Cascade:** If you are an AI tool, read the instance root README first. This brief carries the substance about *who the company is*; the README carries the rules about *how the instance operates*.
>
> *(Note: links below assume this brief lives at the instance root as `company-brief.md`. If you've copied this template elsewhere, fix the paths.)*
>
> **Use this brief when:** drafting outreach, writing proposals, producing marketing copy, generating positioning content, briefing a new agent on the company, or any task where the output should sound and feel like the company itself.

## Elevator pitch

> **TODO:** One or two sentences. What the company is, what it does, and who it's for. Tight enough to land in the first line of a proposal or a cold-outreach reply.

## Mission and origin

> **TODO:** Why the company exists. Where it came from. What problem the founder(s) are trying to solve in the world.

## What we sell

> **TODO:** The actual offerings — engagements, products, retainers, workshops. What a buyer can actually buy. Link to specific offerings under `Products/` (or equivalent) where relevant.

## Who we serve

> **TODO:** Ideal customer profile. Who hires us, what stage their company is in, what problems they show up with. Distinguish active patterns from aspirational ones.

## How engagements run

> **TODO:** Default engagement shape — discovery, scoping, delivery cadence, deliverables, billing model. The "what working with us looks like" section.

## Voice and positioning

> **TODO:** How the company sounds. Tone (warm / sharp / plainspoken / etc.). What differentiates us from generic competitors. Words and framings we use; words we avoid.

## People

> **TODO:** Founder(s), partners, collaborators, named personas that show up in the work. Roles and how to refer to each.

### Principals

The human(s) on whose behalf agents act within this instance. Agents needing human sign-off route to the principal listed here. When more than one principal is listed, the one marked **primary stakeholder** is the final escalation point. See the ACOS framework README for the full convention.

| Name | Role | Primary stakeholder | Decision scope |
|---|---|---|---|
| <Name> | <Role> | <Yes / No> | <e.g., "All decisions" / "Brand and design only" / "Engagement sign-off, deliverables, contracts"> |

> **TODO:** List one or more principals. In single-principal instances, that person is automatically the primary stakeholder. In multi-principal instances, mark exactly one as primary stakeholder and scope each principal's authority so skills can route correctly (e.g., brand decisions to a design lead, contract sign-off to the founder).

## Engineering defaults

Conventions that apply to **all software the company builds — for clients, for products, for internal projects** — unless a more specific layer overrides them. Overrides cascade most-specific-wins: **company default → client override → product/project override**. Client overrides live in that client's `brief.md` under an "Engineering defaults" section; product/project overrides live in that product/project's own README.

> **TODO:** List the defaults that apply across all software built under this instance. The bullets below are illustrative shapes — replace them with the company's actual choices, or delete bullets the company doesn't make a stance on.
>
> - **Default source repo home: `<git-host-org-url>`.** Where new apps, products, and internal projects live by default. Clients with their own preferred org declare that override in their brief.
> - **Default deployment environment: `<environment + account>`.** Where new apps and products deploy first. Clients or products with a different permanent host declare that override in the appropriate layer.
> - **Default packaging: `<packaging convention>`.** How apps are packaged for deployment. Often the seam that makes moves between environments tractable.
>
> When a new engineering default emerges that should apply across all the company's work, add it here. When a client or product diverges from a default for principled reasons, capture the override in the appropriate brief or README and link back so the cascade stays legible.

## What we don't do

> **TODO:** Explicit non-scope. Engagement types declined, problems routed elsewhere, lines we don't cross. Useful so any agent drafting outreach doesn't promise things the company doesn't deliver.

## Links

- Instance root: [README](README.md)
- Brand and visual identity: `../Brand/README.md` *(if present)*
- Products: `../Products/README.md` *(if present)*
- Active clients: `../Clients/README.md` *(if present)*
