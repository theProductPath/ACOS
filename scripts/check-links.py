#!/usr/bin/env python3
"""Relative-link checker for the ACOS repo.

A read-only validator (see docs/extending-acos.md, "Code in ACOS"). It answers
one question: would a reader who clones this repo ever hit a dead link?

    python3 scripts/check-links.py

Exit code 0 = clean, 1 = at least one broken link.

Two classes of markdown file live in this repo, and they have different rules:

1. Docs that ship and are read *in place* — the READMEs, docs/, skills. Every
   relative link in these must resolve inside the repo. A link that escapes the
   repo root is broken by definition: the reader does not have whatever is out
   there. This is how ACOS shipped links to `../../../tPPOS/` for months.

2. Templates, under framework/templates/ and the skills' output-templates/.
   These are not read in place; they are *copied into an instance*, and their
   links are meant to resolve there, not here. Their links are therefore not
   existence-checked. Instead they are linted for the rule in extending-acos:
   a template must not hardcode a path to ACOS — it uses the `<path-to-acos>`
   placeholder, because ACOS lives somewhere different in every instance.

Only git-tracked files are checked, since only those exist in a clone. That is
why _progress/ (gitignored, maintainer-only) is out of scope here — but note
that nothing which ships may link *into* it.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

LINK_RE = re.compile(r"\[[^\]]*\]\(\s*(<[^>]*>|[^)\s]+)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")

TEMPLATE_DIRS = ("framework/templates/", "output-templates/")

# A template must not hardcode where ACOS lives in an instance.
HARDCODED_ACOS_RE = re.compile(r"(?<!<)\bProducts/ACOS\b|(?<!<)\bACOS/framework\b")


def tracked_markdown() -> list[Path]:
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "*.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    return [REPO_ROOT / p for p in out]


def is_template(rel: str) -> bool:
    return any(marker in rel for marker in TEMPLATE_DIRS)


def links_in(text: str):
    """Yield (lineno, target), skipping fenced code blocks."""
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for raw in LINK_RE.findall(line):
            yield lineno, raw.strip("<>") if raw.startswith("<") else raw


def is_external(target: str) -> bool:
    return (
        not target
        or target.startswith("#")
        or "://" in target
        or target.startswith("mailto:")
        or target.startswith("tel:")
    )


def main() -> int:
    broken: list[str] = []
    hardcoded: list[str] = []
    checked = skipped = 0

    for md in tracked_markdown():
        rel = md.relative_to(REPO_ROOT).as_posix()
        text = md.read_text(encoding="utf-8")
        template = is_template(rel)

        for lineno, target in links_in(text):
            if is_external(target):
                continue

            if template:
                skipped += 1
                if HARDCODED_ACOS_RE.search(target):
                    hardcoded.append(
                        f"  {rel}:{lineno}  ->  {target}"
                        "  (template hardcodes an ACOS path; use <path-to-acos>)"
                    )
                continue

            # A shipped doc must never carry an unresolved placeholder.
            if "<" in target and ">" in target:
                broken.append(
                    f"  {rel}:{lineno}  ->  {target}  (placeholder left in a shipped doc)"
                )
                continue

            path_part = target.split("#", 1)[0].split("?", 1)[0]
            if not path_part:
                continue

            checked += 1
            resolved = (md.parent / path_part).resolve()

            if REPO_ROOT not in resolved.parents and resolved != REPO_ROOT:
                broken.append(
                    f"  {rel}:{lineno}  ->  {target}  (resolves outside the repo)"
                )
            elif not resolved.exists():
                broken.append(f"  {rel}:{lineno}  ->  {target}  (does not exist)")

    print(
        f"checked {checked} relative links in shipped docs; "
        f"{skipped} template links linted (not existence-checked)"
    )

    if not broken and not hardcoded:
        print("OK — no broken relative links")
        return 0

    if broken:
        print(f"\nBROKEN LINKS: {len(broken)}")
        print("\n".join(broken))
    if hardcoded:
        print(f"\nTEMPLATES HARDCODING AN ACOS PATH: {len(hardcoded)}")
        print("\n".join(hardcoded))
    return 1


if __name__ == "__main__":
    sys.exit(main())
