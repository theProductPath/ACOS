---
type: acos-doc
subject: reorganizing-an-instance
status: active
last-updated: 2026-07-25
maintainer: Steven Jones
purpose: How to reshape an existing instance — group folders under a container and relocate a folder — without breaking the reference graph. Read this before demoting a top-level folder, introducing a grouping layer, or moving anything load-bearing.
---

# Reorganizing an instance — functional grouping and safe relocation

Adoption scaffolds an instance; extension adds to the framework. This doc covers the third thing that happens to a real instance over time: its shape changes. A folder that started at the top level turns out to belong under a grouping folder. A function that was one folder grows into several and wants a home. Doing that safely is mostly one skill — moving a folder without leaving dangling references behind — and this doc is that skill written down, plus the design judgment about when to reach for it.

Nothing here is a new convention every instance must learn. It is a procedure, and an [operator tool](extending-acos.md#code-in-acos--tools-yes-runtime-no) that automates the error-prone part.

## Functional grouping: a container over scattered siblings

The [membership rule](../framework/README.md#house-rules) makes the instance root's folder map the roster: a folder is part of the operating system exactly when it has a row there. That keeps membership explicit, but it says nothing about *shape* — whether ten functions sit as ten top-level rows, or as three containers with the rest nested underneath. Shape is the adopter's call.

The pattern worth naming is **functional grouping**: when several folders serve one function, give the function a top-level container and nest the folders under it, instead of leaving them as loose siblings at the root. A single `Brand/` folder at the top level is fine until the day marketing also needs campaigns, content, and social; at that point a `Marketing/` container with `Brand/` as its first area keeps the function together and gives the newcomers an obvious home.

Two README patterns carry the distinction, and picking the right one is the whole design decision:

- A **container** (`folder-readme-container`) holds child folders that are themselves operating-system items. Its README indexes and routes into them; agents cascade through it. The new grouping folder is a container.
- An **asset library** (`folder-readme-asset`) holds *material* — logos, source documents, data — whose children are not OS items. The walk stops at its README. A folder full of brand assets is an asset library, and it stays one after it moves; only its parent changed.

So a grouping move typically produces a container wrapping one or more existing asset libraries or items. The container is new; the thing you moved keeps its own type.

When *not* to group: a single folder with no siblings on the horizon does not need a container above it — that is nesting for its own sake, and it costs a level of depth in every reference. Group when a second area is real or clearly coming, not on speculation.

## Relocating a folder without breaking the tree

Moving a folder is a rename; keeping the instance coherent afterward is the work. Relative links break in **both directions**, and the fix differs for each — this is the part a careful manual pass still gets wrong.

- **Inbound** — a file elsewhere links *into* the folder that moved. Its link now points at nothing and must be repointed at the new location. A link like `../<folder>/README.md` gains the new grouping segment: `../<container>/<folder>/README.md`.
- **Outbound** — a file *inside* the moved folder links back *out* of it. The file dropped one level deeper, so every `../` chain that escapes the folder needs one more `../`. A reference to `../<sibling>/` written when the folder was at the top becomes `../../<sibling>/` once it sits under a container.
- **Internal** — a link between two files that both live inside the moved folder is unaffected. They moved together; leave those exactly as they are. Rewriting them is a common overcorrection.

The reference graph is **wider than markdown links.** A relocation that fixes only Markdown hyperlinks will still leave breakage in:

- HTML `href` and `src` attributes (page mockups, embedded views).
- Data files that store paths as strings — a `"path": "<folder>/README.md"` entry in JSON or JS that a tool reads. These are often written relative to the instance root, not to the file, so they need care, not a blind rewrite.
- Prose and inline code that name the folder's path (`the source of truth is <folder>/README.md`).
- Generated artifacts — diagrams, dashboards, rendered images — that embed the old path. These are not edited by hand; regenerate them from source.
- Any machine-readable config that names the folder (for example an overlay that lists asset folders — check whether it matches by name or by full path before assuming it still resolves).

Order of operations:

1. Decide the new shape and write the container's README first, so the destination is real.
2. Run the relink helper as a **dry run** to see every link that will change and every non-link mention that needs a human eye.
3. Move the folder (`mv`), and apply the link rewrites.
4. Handle the review list by hand: HTML, data files, prose, config.
5. Regenerate any diagrams or dashboards that embedded the old path.
6. Re-run [`acos-integrity-check.py`](../scripts/acos-integrity-check.py); its link-resolution check is the proof that nothing dangles.
7. Record the reasoning where the instance keeps its decisions — a demotion is exactly the kind of non-obvious structural choice worth an audit trail.

## The relink helper

[`scripts/relink-folder.py`](../scripts/relink-folder.py) automates step 2–3. It is an operator tool, not runtime: run by choice, edits plain markdown in place, and nothing depends on it after it exits (it passes the [three-part test](extending-acos.md#code-in-acos--tools-yes-runtime-no)). It shares its link parser with the integrity checker so the two cannot drift.

Given the old and new paths (relative to the instance root), it computes the correct rewrite for every markdown link in the tree — inbound, outbound, and internal — using lexical path math, so it works before the move and against a tree that is not a git repo (the normal case for an instance on a synced drive):

```
python3 scripts/relink-folder.py --root <instance-root> <old> <new>            # dry run
python3 scripts/relink-folder.py --root <instance-root> <old> <new> --apply    # rewrite links
python3 scripts/relink-folder.py --root <instance-root> <old> <new> --apply --move   # also mv the folder
```

It is deliberately honest about its edge. It rewrites **markdown links only**, because those have defined resolution semantics. It does **not** touch HTML attributes, JSON/JS string paths, CSS `url()`, prose, or generated artifacts — instead it *reports* every non-markdown file that mentions the moved folder as a path segment, as a review list (which will include false positives, such as a same-named subfolder elsewhere in the tree). That review list is the manual half of the job, surfaced rather than silently skipped — a tool that claimed to catch everything would be the dangerous kind.

## Framework or instance?

Reshaping is almost always an **instance** change: the [framework-vs-instance rule](extending-acos.md#the-framework-vs-instance-rule) leaves tree shape to the adopter, so grouping and relocation happen in the instance and touch no framework file. The one exception is when a shipped template *assumes* the old shape — a template that names a folder path in the layout it scaffolds. If you change the shape you want every future instance to inherit, that assumption moves with it, following the ordinary [promotion path](extending-acos.md#the-promotion-path): edit the template in the framework, leave the instance's own copies to the relink pass above. Confirm it is the right default for *every* adopter before you promote it — a grouping that fits one company can be needless depth for another.

## Checklist

- [ ] New shape decided; container README written (right type: container over asset/item).
- [ ] Grouping actually earns the container — a second area is real or imminent, not speculative.
- [ ] Relink helper dry-run reviewed: markdown rewrites look right, review list understood.
- [ ] Folder moved; markdown links applied.
- [ ] Review list handled: HTML, data/config files, prose, generated artifacts.
- [ ] Diagrams and dashboards regenerated.
- [ ] `acos-integrity-check.py` re-run: link resolution clean.
- [ ] Decision recorded in the instance's decision log.
- [ ] If a shipped template assumed the old shape, promoted per the framework-vs-instance rule.

## Links

- Framework-vs-instance rule and the code-in-ACOS test: [`extending-acos.md`](extending-acos.md)
- Setting up a fresh instance: [`adopting-acos.md`](adopting-acos.md)
- Membership rule and README patterns: [`framework/README.md`](../framework/README.md)
- Relink helper: [`scripts/relink-folder.py`](../scripts/relink-folder.py)
- Integrity checker: [`scripts/acos-integrity-check.py`](../scripts/acos-integrity-check.py)
