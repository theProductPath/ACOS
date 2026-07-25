#!/usr/bin/env python3
"""Rewrite relative links when a folder moves inside an instance tree.

An operator tool (see docs/extending-acos.md, "Code in ACOS — tools yes, runtime
no"). It is run by choice, edits plain markdown in place, and nothing in an
instance depends on it existing: delete it and every instance it ever touched
carries on unchanged. It passes the three-part test — an instance does not stop
working without it, it does not have to run for the conventions to hold, and its
only output is human-owned files plus a report.

It solves the one genuinely error-prone part of relocating a folder: relative
links break in *both* directions, and the fix is different for each.

  - Inbound: a file elsewhere links *into* the folder that moved. Its link now
    resolves to nothing and needs the new location.
  - Outbound: a file *inside* the moved folder links back *out* of it. The file
    dropped to a new depth, so every `../` chain that escapes the folder needs
    re-counting.
  - Internal: a link from one file in the moved folder to another file in the
    same folder is unaffected — both moved together — and must be left alone.

Getting the `../` arithmetic right by hand, across all three cases, is where a
manual pass slips. This script computes it lexically for every markdown link in
the tree and rewrites only the ones that actually change.

Usage (run while the folder is still at its OLD path; the physical move happens
last, optionally by this script):

    python3 scripts/relink-folder.py --root <instance-root> OLD NEW            # dry run
    python3 scripts/relink-folder.py --root <instance-root> OLD NEW --apply    # rewrite links
    python3 scripts/relink-folder.py --root <instance-root> OLD NEW --apply --move   # also mv

OLD and NEW are paths relative to the instance root, e.g.  Brand  Marketing/Brand.

Exit code 0 = clean (or a dry run), 1 = a problem the caller should see.

What it does NOT do, on purpose (keep it honest about its limits):

  - It rewrites markdown links only — `[text](path)` and `<path>` forms. It does
    not touch HTML `href`/`src`, JSON/JS string paths (e.g. a `"path": "..."`
    data file), CSS `url()`, or a folder name mentioned in prose or inline code.
    Those are not links with defined resolution semantics, and guessing wrong is
    worse than not touching them. Instead it *reports* every non-markdown file
    that mentions the moved folder's name as a path segment, as a review list.
  - It does not re-render generated artifacts (diagrams, dashboards) that embed
    the old path — regenerate those from their source.
  - It matches by lexical path math, not by opening link targets, so it works
    before the move and against trees that are not git repos (an instance on a
    synced drive is the normal case).
"""

import argparse
import importlib.util
import os
import sys
from pathlib import Path

# Reuse the integrity checker's link parser so the two can't drift — same
# approach check-links.py takes. Both live in scripts/, side by side.
_spec = importlib.util.spec_from_file_location(
    "acos_integrity_check", Path(__file__).resolve().parent / "acos-integrity-check.py"
)
_aic = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_aic)

iter_links = _aic.iter_links
is_external_link = _aic.is_external_link
is_agent_ignored = _aic.is_agent_ignored

# Files whose markdown links we rewrite.
MARKDOWN_EXT = {".md", ".markdown", ".mmd"}
# Text files we scan (but never auto-edit) for a stray mention of the moved
# folder, so the caller has a review list for HTML/JSON/JS/CSS/etc.
SCAN_EXT = {".html", ".htm", ".js", ".mjs", ".json", ".css", ".svg", ".txt", ".yaml", ".yml"}


def norm(*parts):
    """Lexically normalized absolute path — no filesystem access, no symlink
    resolution, so it is correct before the move and for a path that does not
    exist yet (the NEW location)."""
    return os.path.normpath(os.path.join(*parts))


def is_under(child, parent):
    """True if `child` is `parent` itself or sits beneath it."""
    if child == parent:
        return True
    return child.startswith(parent + os.sep)


def split_target(target):
    """Split a link target into (path, tail) where tail keeps any #anchor/?query."""
    for i, ch in enumerate(target):
        if ch in "#?":
            return target[:i], target[i:]
    return target, ""


def moved_path(abs_path, old_abs, new_abs):
    """Where `abs_path` ends up after the move (unchanged if not under OLD)."""
    if abs_path == old_abs:
        return new_abs
    if is_under(abs_path, old_abs):
        return norm(new_abs, os.path.relpath(abs_path, old_abs))
    return abs_path


def walk_files(root):
    """Yield every non-ignored file under root, skipping agent-ignored folders
    (`_archive/`, hidden tool dirs) at any depth."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not is_agent_ignored(d)]
        for name in filenames:
            yield os.path.join(dirpath, name)


def compute_rewrites(root_abs, old_abs, new_abs):
    """Return (rewrites, scan_hits).

    rewrites: list of (file_abs, lineno, old_target, new_target) for markdown
              links that change.
    scan_hits: list of (file_abs, lineno, line_text) for non-markdown files that
               mention the moved folder as a path segment (review list).
    """
    rewrites = []
    scan_hits = []
    old_name = os.path.basename(old_abs)
    # A path segment equal to the moved folder's name: /Name/ or "Name/ or (Name/
    seg_markers = ("/" + old_name + "/", '"' + old_name + "/",
                   "'" + old_name + "/", "(" + old_name + "/", "`" + old_name + "/")

    for file_abs in walk_files(root_abs):
        ext = os.path.splitext(file_abs)[1].lower()
        try:
            text = Path(file_abs).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable — nothing to relink

        if ext in MARKDOWN_EXT:
            file_new = moved_path(file_abs, old_abs, new_abs)
            for lineno, target in iter_links(text):
                if is_external_link(target):
                    continue
                path_part, tail = split_target(target)
                if not path_part:
                    continue
                # Resolve from the file's ORIGINAL directory (pre-move tree).
                tgt_abs = norm(os.path.dirname(file_abs), _aic.link_target_path(path_part) or path_part)
                tgt_new = moved_path(tgt_abs, old_abs, new_abs)
                # Nothing moved that this link touches → leave it exactly as is.
                if file_new == file_abs and tgt_new == tgt_abs:
                    continue
                new_rel = os.path.relpath(tgt_new, os.path.dirname(file_new))
                new_rel = Path(new_rel).as_posix()
                if " " in new_rel or "%20" in path_part:
                    new_rel = new_rel.replace(" ", "%20")
                new_target = new_rel + tail
                if new_target != target:
                    rewrites.append((file_abs, lineno, target, new_target))

        elif ext in SCAN_EXT:
            for lineno, line in enumerate(text.splitlines(), start=1):
                if any(m in line for m in seg_markers):
                    scan_hits.append((file_abs, lineno, line.strip()))

    return rewrites, scan_hits


def apply_rewrites(rewrites):
    """Apply the rewrites in place, one truncating write per file (no unlink)."""
    by_file = {}
    for file_abs, lineno, old_t, new_t in rewrites:
        by_file.setdefault(file_abs, []).append((old_t, new_t))
    for file_abs, pairs in by_file.items():
        text = Path(file_abs).read_text(encoding="utf-8")
        # Longest-first so a shorter target isn't a prefix-collision of a longer one.
        for old_t, new_t in sorted(set(pairs), key=lambda p: -len(p[0])):
            text = text.replace(old_t, new_t)
        Path(file_abs).write_text(text, encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("old", help="Folder's current path, relative to the instance root (e.g. Brand)")
    ap.add_argument("new", help="Folder's new path, relative to the instance root (e.g. Marketing/Brand)")
    ap.add_argument("--root", default=".", help="Instance root (default: current directory)")
    ap.add_argument("--apply", action="store_true", help="Write the rewrites (default is a dry run)")
    ap.add_argument("--move", action="store_true",
                    help="After rewriting, mv the folder from OLD to NEW (only with --apply)")
    args = ap.parse_args(argv)

    root_abs = norm(os.path.abspath(args.root))
    old_abs = norm(root_abs, args.old)
    new_abs = norm(root_abs, args.new)

    if not os.path.isdir(old_abs):
        print(f"Error: OLD path does not exist as a folder: {args.old} (under {root_abs})",
              file=sys.stderr)
        return 1
    if os.path.exists(new_abs):
        print(f"Error: NEW path already exists: {args.new}. Move into a name that does not yet exist.",
              file=sys.stderr)
        return 1
    if is_under(old_abs, new_abs) or is_under(new_abs, old_abs):
        print("Error: OLD and NEW may not nest inside each other.", file=sys.stderr)
        return 1

    rewrites, scan_hits = compute_rewrites(root_abs, old_abs, new_abs)

    print(f"Relocating  {args.old}  ->  {args.new}")
    print(f"Instance root: {root_abs}\n")

    if rewrites:
        print(f"Markdown links to rewrite: {len(rewrites)}")
        for file_abs, lineno, old_t, new_t in rewrites:
            rel = os.path.relpath(file_abs, root_abs)
            print(f"  {rel}:{lineno}\n      - {old_t}\n      + {new_t}")
    else:
        print("Markdown links to rewrite: none")

    if scan_hits:
        print(f"\nReview by hand — non-markdown mentions of '{os.path.basename(old_abs)}/' "
              f"({len(scan_hits)}; includes false positives such as same-named subfolders):")
        for file_abs, lineno, line in scan_hits:
            rel = os.path.relpath(file_abs, root_abs)
            print(f"  {rel}:{lineno}  {line[:120]}")

    if not args.apply:
        print("\nDry run — nothing written. Re-run with --apply to rewrite the links above.")
        return 0

    apply_rewrites(rewrites)
    print(f"\nApplied {len(rewrites)} rewrite(s) across "
          f"{len({r[0] for r in rewrites})} file(s).")

    if args.move:
        os.makedirs(os.path.dirname(new_abs), exist_ok=True)
        os.rename(old_abs, new_abs)
        print(f"Moved {args.old} -> {args.new}")
    else:
        print(f"Next: move the folder itself —  mv '{args.old}' '{args.new}'  (or re-run with --move).")

    print("Then regenerate any diagrams/dashboards that embed the old path, and re-run "
          "acos-integrity-check.py to confirm links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
