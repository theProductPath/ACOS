#!/usr/bin/env python3
"""ACOS integrity checker.

Walks an ACOS instance tree and reports violations of the framework conventions
described in framework/README.md and framework/skills/acos-integrity/SKILL.md.

The script is framework-level: it carries no knowledge of any particular
instance. Everything instance-specific (which folder holds clients, which
folders are asset libraries, which containers hold self-contained repos) is
read from the instance's own overlay at:

    <instance-root>/overlays/acos-integrity.md

inside a fenced ```acos-config block. The script is self-sufficient without an
overlay: with no overlay present it falls back to convention-based discovery.

Usage:
    acos-integrity-check.py [--root PATH] [--overlay PATH] [--strict]

With no --root, the instance root is discovered by walking up from the current
directory looking for company-brief.md.

Stdlib only. No third-party dependencies (hard product constraint).
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

# --- Configuration & Taxonomy ---

REQUIRED_FRONTMATTER = ["type", "status", "last-updated", "maintainer", "purpose"]

# Every check this script implements, in report order. This list is the contract
# with framework/skills/acos-integrity/SKILL.md: the SKILL documents exactly
# these checks and no others. If you add a check, add it here and document it
# there in the same change (tests/test_acos_integrity_check.py enforces the
# pairing). If you remove one, remove it from both.
#
# The registry also makes the report honest: a clean instance emits almost no
# findings, so the report says how many checks were *attempted*, which is the
# only way "everything passed" can be told apart from "the walk did nothing".
CHECK_REGISTRY = [
    ("0.1", "Folder map — the membership roster"),
    ("0.3", "Instance overlay"),
    ("0.4", "Instance walk"),
    ("1.1", "Instance root README"),
    ("1.2", "Roster folder has a README"),
    ("1.3", "Declared type matches position"),
    ("1.4", "OS membership"),
    ("1.5", "Asset library ends the walk"),
    ("2.1", "Company brief exists"),
    ("2.2", "Client brief presence"),
    ("2.3", "Client manifest presence"),
    ("2.4", "Duplicate brief detection"),
    ("2.5", "Frontmatter — presence and required fields"),
    ("3.1", "Type taxonomy"),
    ("3.2", "Status vocabulary"),
    ("3.3", "ISO 8601 dates"),
    ("3.4", "Staleness"),
    ("4.1", "Folder naming — breaking characters"),
    ("4.2", "Instance naming style"),
    ("5.1", "No references into agent-ignored folders"),
    ("6.1", "Overlay has a matching framework skill"),
    ("6.2", "Overlay frontmatter"),
    ("8.1", "Internal links resolve"),
]

CHECK_IDS = {cid for cid, _ in CHECK_REGISTRY}

# 3.4 — an `active` document nobody has touched in this long is worth a look.
# Overlay key `staleness-days`; 0 turns the check off.
DEFAULT_STALENESS_DAYS = 90

# 3.4 only applies to documents that claim to be current. A `wrapped` client or
# an `archived` doc is *supposed* to sit still.
STALENESS_STATUSES = {"active"}

# The canonical `type` taxonomy, as documented in framework/README.md
# ("Frontmatter" section). The manual is the source of truth; if you add a type
# here, document it there in the same change.
FRAMEWORK_TYPES = {
    "folder-readme-root",
    "folder-readme-container",
    "folder-readme-item",
    "folder-readme-asset",
    "brief-company",
    "brief-client",
    "brief-stakeholder",
    "manifest-client",
    "dashboard-company",
    "agent-ignore",
    "progress-checkpoint",
}

# Types that exist in real framework artifacts (templates, skills, docs) but are
# not yet documented in the framework/README.md taxonomy. Accepted so they don't
# produce false failures, but reported as info so the drift stays visible.
# The fix is to document them in framework/README.md and move them above.
PENDING_TYPES = {
    "skill-overlay",        # <instance>/overlays/*.md; in SKILL.md, not in the manual
    "acos-doc",             # docs/*.md
    "framework-doc",        # framework/companion-plugins.md
    "skill-reference",      # framework/skills/*/references/*.md
    "brief-section-template",
    "brand-asset",          # client-brand-capture output templates
    "principal-review",
    "skill-audit",
}

# The status vocabulary, as documented in framework/README.md ("Status
# vocabulary"). The manual is the source of truth; the per-type subsets live in
# the templates. Instances may add more via the overlay's custom-statuses key.
KNOWN_STATUSES = {
    "skeleton",
    "drafting",
    "active",
    "paused",
    "dormant",
    "prospect",
    "exploratory",
    "wrapped",
    "alumni",
    "stale",
    "archived",
    "deprecated",
}

# --- Folder naming (framework/README.md, "Folder naming — structure, not style") ---
#
# ACOS governs structure, not style. It does NOT dictate letter case: a folder
# named `Clients`, `clients`, or `clientS` is equally valid as far as the
# framework is concerned, and none of them produce a finding. Underscores inside
# a name are harmless too (a *leading* underscore is the agent-ignore signal,
# which is a different rule handled by is_agent_ignored()).
#
# What the framework does flag is a character that genuinely breaks something —
# paths, markdown links, or URLs. Those are warnings, never failures, and the
# message says concretely what breaks.
BREAKING_CHARS = [
    (" ", "a space", "breaks unquoted shell paths, needs %20 in URLs, and breaks markdown "
                     "links unless the whole target is angle-bracketed"),
    ("\t", "a tab", "breaks shell paths and is invisible in every tool that has to render it"),
    ("#", "a '#'", "truncates a URL at the fragment marker, so links into this folder silently "
                   "resolve to the wrong place"),
    ("?", "a '?'", "starts the query string in a URL, so links into this folder are cut short"),
    ("%", "a '%'", "starts a percent-escape in a URL, so the path is decoded into something else"),
    ("\\", "a backslash", "is a path separator on Windows and an escape character in most shells"),
    (":", "a ':'", "is a path separator in some tools and breaks Windows paths outright"),
    ("|", "a '|'", "is a pipe in every shell and a cell separator in markdown tables"),
    ("*", "a '*'", "is a glob wildcard, so any script that touches this path can match the wrong "
                   "folder"),
    ('"', "a double quote", "breaks shell quoting"),
    ("<", "a '<'", "is a shell redirect and an HTML tag opener"),
    (">", "a '>'", "is a shell redirect and an HTML tag closer"),
]

# --- Optional instance naming policy (overlay: naming-style) ---
#
# The framework ships NO default naming style. An instance that wants one
# enforced declares it in its acos-integrity overlay; without that key, the
# style check does not run at all.
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CAPITALIZED_RE = re.compile(r"^[A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*$")

NAMING_STYLES = {
    "kebab-case": (KEBAB_RE, "kebab-case (lowercase words joined by single dashes)"),
    "capitalized": (CAPITALIZED_RE, "Capitalized (initial capital, dashes between words)"),
}

NO_NAMING_STYLE = "none"

FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)

CONFIG_BLOCK_RE = re.compile(r"```acos-config[ \t]*\r?\n(.*?)```", re.DOTALL)

# --- Markdown links (checks 5.1 and 8.1) ---
#
# Shared with scripts/check-links.py, which imports these three helpers rather
# than keeping a second copy: the two validators ask the same question ("does
# this relative link resolve?") of two different trees, and one of them drifting
# from the other is the exact failure both exist to catch.

# Two shapes of link target. The angle-bracket form `[x](<a b.md>)` wraps the
# WHOLE target, so it is only recognized when the `>` is followed by the closing
# paren — otherwise `[x](<client-name>/brief.md)` would be read as a link to
# `client-name` and the unresolved placeholder would vanish instead of being
# reported. That placeholder is the one an adopter is most likely to leave behind.
LINK_RE = re.compile(r"\[[^\]]*\]\(\s*(<[^>]*>\s*\)|[^)\s]+)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def iter_links(text):
    """Yield (lineno, target) for every markdown link, skipping fenced code blocks."""
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for raw in LINK_RE.findall(line):
            if raw.endswith(")"):  # the angle-bracket form: <target>
                raw = raw[:-1].strip().strip("<>")
            yield lineno, raw


def is_external_link(target):
    """True for anything that doesn't name a file on this disk."""
    return (
        not target
        or target.startswith("#")
        or "://" in target
        or target.startswith("mailto:")
        or target.startswith("tel:")
    )


def link_target_path(target):
    """The filesystem path a link points at, or None if it points at nothing local.

    Strips the `#anchor` and `?query` tails and percent-decodes the rest, so a
    link written `Research/AI%20Gateways/README.md` resolves to the folder that
    is actually on disk.
    """
    if is_external_link(target):
        return None
    path_part = target.split("#", 1)[0].split("?", 1)[0].strip()
    if not path_part:
        return None
    return unquote(path_part)


# --- Utility Functions ---


def _strip_inline_comment(value):
    """Strip a YAML-style trailing comment from an unquoted scalar."""
    if value[:1] in ('"', "'"):
        return value
    return re.split(r"\s+#", value, maxsplit=1)[0].strip()


def load_frontmatter(file_path_or_text, _is_text=False):
    """Extract and parse YAML frontmatter from a markdown file.

    Returns a dict of the frontmatter keys, None if the file has no frontmatter
    block, or {"_error": ...} if the file could not be read.
    """
    try:
        if _is_text:
            content = file_path_or_text
        else:
            content = Path(file_path_or_text).read_text(encoding="utf-8")
    except Exception as exc:  # unreadable file, bad encoding, permissions
        return {"_error": str(exc)}

    match = FRONTMATTER_RE.match(content)
    if not match:
        return None

    fm = {}
    for line in match.group(1).split("\n"):
        line = line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = _strip_inline_comment(value.strip())
        fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm


def parse_frontmatter_text(text):
    """Convenience wrapper used by tests: parse frontmatter from a string."""
    return load_frontmatter(text, _is_text=True)


def is_kebab_case(name):
    """True only for lowercase kebab-case names.

    Retained because an instance may opt into `naming-style: kebab-case` in its
    overlay. The framework itself mandates no case convention.
    """
    if not isinstance(name, str) or not name:
        return False
    return bool(KEBAB_RE.match(name))


def naming_violation(name):
    """Describe the character in `name` that genuinely breaks something, or None.

    ACOS governs structure, not style. Case is taste: `Clients`, `clients`, and
    `CLIENTS` are all fine and none of them is a finding. Underscores inside a
    name are harmless. The only thing reported here is a character that breaks
    real machinery — shell paths, markdown links, URLs — and the reason says what.
    """
    if not isinstance(name, str) or not name:
        return "is not a usable folder name"

    for char, label, breaks in BREAKING_CHARS:
        if char in name:
            return f"contains {label}, which {breaks}"
    return None


def style_violation(name, style):
    """Check `name` against an instance-declared naming policy, or None.

    The framework ships no default: `style` is whatever the instance put in its
    overlay's `naming-style` key. Absent (or "none"), this never fires.
    """
    if not style or style == NO_NAMING_STYLE:
        return None
    rule = NAMING_STYLES.get(style)
    if not rule:
        return None
    pattern, description = rule
    if isinstance(name, str) and pattern.match(name):
        return None
    return f"does not match this instance's declared naming-style: {description}"


def validate_date(date_str):
    """Check if a string is a valid ISO 8601 date (YYYY-MM-DD)."""
    if not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_agent_ignored(name):
    """Agent-ignore rule: underscore-prefixed folders are out of scope.

    Hidden dot-folders (.git, .obsidian) are tool metadata, not content, and are
    skipped for the same reason.
    """
    return name.startswith("_") or name.startswith(".")


# --- Instance configuration (read from the instance, never hardcoded) ---


def parse_config_block(text):
    """Parse the fenced ```acos-config block out of an overlay's markdown.

    Supports `key: value`, `key: [a, b]`, and dash-list blocks:

        key:
          - a
          - b

    Returns {} if the text carries no config block.
    """
    match = CONFIG_BLOCK_RE.search(text or "")
    if not match:
        return {}

    config = {}
    current_list_key = None
    for raw in match.group(1).split("\n"):
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        stripped = line.strip()
        if stripped.startswith("- ") and current_list_key:
            config[current_list_key].append(_strip_inline_comment(stripped[2:].strip()).strip("\"'"))
            continue

        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = _strip_inline_comment(value.strip())
        if not value:
            current_list_key = key
            config[key] = []
        elif value.startswith("[") and value.endswith("]"):
            items = [v.strip().strip("\"'") for v in value[1:-1].split(",")]
            config[key] = [v for v in items if v]
            current_list_key = None
        else:
            config[key] = value.strip("\"'")
            current_list_key = None
    return config


class InstanceConfig:
    """Instance-specific knowledge. Defaults are convention-based, not baked in."""

    def __init__(self, root_path, overlay_path=None, config=None):
        config = config or {}
        self.root_path = Path(root_path)

        # The instance root folder is named for the instance, not for its
        # contents; it is exempt from the folder-name check.
        self.instance_name = config.get("instance-name", self.root_path.name)

        # An instance MAY declare a naming policy. The framework ships none: with
        # no `naming-style` key, the style check does not run. See
        # framework/README.md, "Folder naming — structure, not style".
        self.naming_style = config.get("naming-style", NO_NAMING_STYLE)

        # Convention default: an in-scope folder literally named "clients" holds
        # one folder per client. Overridable for instances that name it otherwise.
        self.client_containers = config.get("client-containers", ["Clients"])

        # Folders that ARE asset libraries (framework/README.md "Asset" README
        # pattern). Their children are material, not OS items: never walked,
        # never expected to carry READMEs. A folder whose own README declares
        # `type: folder-readme-asset` gets the same treatment without needing an
        # overlay entry — this key is for instances that would rather say it once
        # here than trust the frontmatter.
        self.asset_folders = config.get("asset-folders", [])

        # Containers whose direct children are self-contained repos carrying
        # their own codebase README: exempt from frontmatter (2.5) and type (3.1).
        self.repo_child_containers = config.get("repo-child-containers", [])

        # 3.4 — how long an `active` document may sit untouched before the
        # checker mentions it. `0` turns the check off entirely.
        try:
            self.staleness_days = int(config.get("staleness-days", DEFAULT_STALENESS_DAYS))
        except (TypeError, ValueError):
            self.staleness_days = DEFAULT_STALENESS_DAYS

        self.exclude_folders = config.get("exclude-folders", [])
        self.suppress_checks = config.get("suppress-checks", [])
        self.naming_exempt = config.get("naming-exempt", [])
        self.custom_types = set(config.get("custom-types", []))
        self.custom_statuses = set(config.get("custom-statuses", []))

        self.overlay_path = overlay_path
        self.overlay_loaded = bool(config)

    @classmethod
    def load(cls, root_path, overlay_path=None):
        root_path = Path(root_path)
        overlay_path = Path(overlay_path) if overlay_path else root_path / "overlays" / "acos-integrity.md"
        config = {}
        if overlay_path.exists():
            try:
                config = parse_config_block(overlay_path.read_text(encoding="utf-8"))
            except Exception:
                config = {}
        return cls(root_path, overlay_path=overlay_path, config=config)

    def known_types(self):
        return FRAMEWORK_TYPES | PENDING_TYPES | self.custom_types

    def known_statuses(self):
        return KNOWN_STATUSES | self.custom_statuses

    def is_naming_exempt(self, name):
        return name == self.instance_name or name in self.naming_exempt


# --- Check Implementation ---


FRAMEWORK_DIR = Path(__file__).resolve().parent.parent / "framework"


class ACOSIntegrityChecker:
    def __init__(self, root_path, config=None, framework_path=None):
        # Don't resolve: stay in logical path space (Google Drive symlinks).
        self.root_path = Path(root_path).expanduser()
        self.config = config or InstanceConfig(self.root_path)
        self.framework_path = Path(framework_path) if framework_path else FRAMEWORK_DIR
        self.report = []
        self.stats = {"pass": 0, "warning": 0, "fail": 0, "info": 0}
        self.in_scope_folders = []
        self.folders_walked = 0
        # Every OS document the walk actually opened. Checks 5.1 and 8.1 run
        # over this set at the end, so they see exactly what the walk saw —
        # nothing outside the OS, nothing behind an asset library.
        self.os_files = []
        # Checks *attempted*, which is not the same thing as findings emitted.
        # A conformant instance emits almost no findings; without this, its
        # report is indistinguishable from one where the walk did nothing.
        self.attempted = set()
        self.not_run = {}

    def log(self, check_id, title, status, message=""):
        if check_id in self.config.suppress_checks:
            return
        self.attempt(check_id)
        self.stats[status] += 1
        icon = {"pass": "✅", "warning": "⚠️", "fail": "❌", "info": "ℹ️"}[status]
        self.report.append((check_id, f"{icon} {check_id} {title} — {status}{': ' + message if message else ''}"))

    def attempt(self, check_id):
        """Record that a check ran, whether or not it had anything to say.

        Call this from any check that can legitimately produce no finding. A
        silent check that was never marked attempted is reported as *not run*,
        which is the honest answer and the one that catches a broken walk.
        """
        if check_id in self.config.suppress_checks or check_id not in CHECK_IDS:
            return False
        self.attempted.add(check_id)
        self.not_run.pop(check_id, None)
        return True

    def not_applicable(self, check_id, reason):
        """Record why a check had nothing to run against in this instance."""
        if check_id in self.attempted or check_id in self.config.suppress_checks:
            return
        self.not_run[check_id] = reason

    def run_checks(self):
        self.check_overlay()
        self.check_root()

        if not self.in_scope_folders:
            self.log("0.4", "Instance walk", "fail",
                     "Nothing was walked: the root README's '## Folder map' yielded no folders, so "
                     "no check below inspected anything. This is not a pass — it is a checker that "
                     "found nothing to check. Confirm the folder map is a table whose first column "
                     "holds the folder name in backticks")
            self.finalize()
            return

        for folder_name in self.in_scope_folders:
            if folder_name in self.config.exclude_folders:
                self.log("0.4", "Instance walk", "info",
                         f"Skipping '{folder_name}' per the overlay's exclude-folders")
                continue
            folder_path = self.root_path.parent / folder_name
            if folder_path.exists():
                self.check_folder_recursive(folder_path, is_container=True)
            else:
                self.log("1.2", "Roster folder has a README", "fail",
                         f"Folder '{folder_name}' declared in the folder map but not found at {folder_path}")

        self.check_overlays()
        self.check_links()

        # A clean instance would otherwise report almost nothing, since the
        # per-folder checks only speak up when something is wrong. Say what was
        # actually inspected so "no findings" reads as "checked" and not "skipped".
        if self.folders_walked:
            self.log("0.4", "Instance walk", "pass",
                     f"Walked {self.folders_walked} folders under {len(self.in_scope_folders)} in-scope "
                     f"roots and read {len(self.os_files)} OS documents")
        else:
            self.log("0.4", "Instance walk", "fail",
                     f"The folder map named {len(self.in_scope_folders)} folders and the walk inspected "
                     "0 of them. Every check below therefore ran against nothing. This is not a pass")
        self.finalize()

    def finalize(self):
        """Record why each unattempted check had nothing to run against."""
        reasons = {
            "1.5": "no asset library on the roster",
            "2.2": "no client container in this instance (overlay key: client-containers)",
            "2.3": "no client container in this instance (overlay key: client-containers)",
            "2.4": "no client container in this instance (overlay key: client-containers)",
            "3.4": ("the overlay set staleness-days: 0" if self.config.staleness_days <= 0
                    else "no dated OS document was read"),
            "4.2": "this instance declared no naming-style (the framework ships no default)",
            "6.1": "this instance has no overlays/ directory",
            "6.2": "this instance has no overlays/ directory",
        }
        blind = self.folders_walked == 0
        for cid, _ in CHECK_REGISTRY:
            if cid in self.attempted or cid in self.config.suppress_checks:
                continue
            if blind:
                # Don't dress a broken walk up as an instance with nothing to check.
                self.not_run.setdefault(cid, "the walk inspected nothing — see 0.4")
                continue
            self.not_run.setdefault(cid, reasons.get(cid, "nothing in this instance to run it against"))

    def check_overlay(self):
        overlay = self.config.overlay_path
        if overlay and Path(overlay).exists():
            if self.config.overlay_loaded:
                self.log("0.3", "Instance overlay", "pass",
                         f"Loaded config from {Path(overlay).name}")
            else:
                self.log("0.3", "Instance overlay", "warning",
                         f"{Path(overlay).name} exists but carries no ```acos-config block; "
                         "running on framework defaults")
        else:
            self.log("0.3", "Instance overlay", "info", "No acos-integrity overlay; using framework defaults")

    def check_root(self):
        # 2.1 Company Brief
        cb_path = self.root_path / "company-brief.md"
        if cb_path.exists():
            self.log("2.1", "Company brief exists", "pass")
            self.validate_fm(cb_path, load_frontmatter(cb_path), "brief-company")
        else:
            self.log("2.1", "Company brief exists", "fail", "company-brief.md missing")

        # The instance root's other singletons are OS documents too: their links
        # are checked (8.1) even though they are files, not folders.
        dashboard = self.root_path / "dashboard.md"
        if dashboard.exists():
            self.os_files.append(dashboard)

        # 1.1 Root README
        readme_path = self.root_path / "README.md"
        if not readme_path.exists():
            self.log("1.1", "Instance root README", "fail", "README.md missing at root")
            return

        self.log("1.1", "Instance root README", "pass")
        self.validate_fm(readme_path, load_frontmatter(readme_path), "folder-readme-root")

        # The `## Folder map` table IS the membership allowlist. A sibling folder
        # is part of the OS if and only if it has a row here. Anything else on
        # disk is not in the OS — silently, with no finding. This table is
        # load-bearing and machine-parsed; see framework/README.md, "Membership".
        content = readme_path.read_text(encoding="utf-8")
        if "## Folder map" in content:
            section = content.split("## Folder map")[1].split("\n##")[0]
            folders = re.findall(r"^\|\s*`([^/`]+)/?`", section, re.MULTILINE)
            self.in_scope_folders = [f for f in folders if not is_agent_ignored(f)]
            self.log("0.1", "Folder map — the membership roster", "pass",
                     f"{len(self.in_scope_folders)} folders opted into the OS: "
                     f"{', '.join(self.in_scope_folders)}")
        else:
            self.log("0.1", "Folder map — the membership roster", "fail",
                     "Could not find the '## Folder map' section in the root README. It is the "
                     "allowlist that defines what is in the OS; without it nothing is in scope")

    @staticmethod
    def declared_type(path):
        """The `type` a folder's own README claims, or None."""
        readme = Path(path) / "README.md"
        if not readme.exists():
            return None
        fm = load_frontmatter(readme) or {}
        return fm.get("type")

    def is_asset_library(self, path):
        """True if this folder is an asset library — a source-of-truth material store.

        Two ways a folder says so, and either is enough:
          1. Its own README declares `type: folder-readme-asset`. The README is
             allowed to speak for itself; that is what frontmatter is for.
          2. The instance overlay names it in `asset-folders`.

        An asset library's children are *material* — files, images, documents,
        sub-folders of assets. They are never OS items, they never need READMEs,
        and the checker does not walk into them looking for OS structure.
        """
        if path.name in self.config.asset_folders:
            return True
        return self.declared_type(path) == "folder-readme-asset"

    def expected_type_for(self, path, is_container):
        if self.is_asset_library(path):
            return "folder-readme-asset"
        return "folder-readme-container" if is_container else "folder-readme-item"

    def check_naming(self, path):
        """4.1 — the only folder-name findings ACOS makes.

        Structure, not style: no case rule. A breaking character is a warning
        (it really does break links, paths, and URLs); an instance-declared
        naming-style, if any, is also a warning. Neither is ever a failure.
        """
        if self.config.is_naming_exempt(path.name):
            return

        # 4.1 runs against every folder walked; it just usually has nothing to
        # say, which is the point of tracking attempts separately from findings.
        self.attempt("4.1")
        if self.config.naming_style != NO_NAMING_STYLE:
            self.attempt("4.2")

        reason = naming_violation(path.name)
        if reason:
            self.log("4.1", "Folder naming", "warning", f"'{self.rel(path)}' {reason}")

        style = style_violation(path.name, self.config.naming_style)
        if style:
            self.log("4.2", "Instance naming style", "warning", f"'{self.rel(path)}' {style}")

    def check_folder_recursive(self, path, is_container=False):
        """Walk one folder of the OS.

        `is_container=True` means this folder is on the roster — it is listed in
        the instance root README's `## Folder map`, which is the membership
        allowlist. `is_container=False` means it is a *candidate* child of a
        container, which is in the OS only if it has a README.
        """
        # Agent-ignore (framework/agent-ignore.md): underscore-prefixed folders
        # are out of scope at any depth, and so are hidden tool folders.
        if is_agent_ignored(path.name):
            return
        if path.name in self.config.exclude_folders:
            return

        self.folders_walked += 1
        self.check_naming(path)

        readme_path = path / "README.md"

        if not readme_path.exists():
            if is_container:
                # A folder on the roster opted into the OS but has no front door.
                # That is a real failure: the map promised an OS folder and there
                # is nothing there to declare what it is or what its children are.
                self.log("1.2", "Roster folder has a README", "fail",
                         f"'{self.rel(path)}' is listed in the root README's folder map "
                         "but has no README.md, so nothing declares what it is")
            else:
                # A child of a container with no README is simply NOT AN OS ITEM.
                # That is information, not an error: a folder is part of the OS
                # only if it opts in. Say so, and say how to change it.
                self.log("1.4", "OS membership", "warning",
                         f"'{self.rel(path)}' has no README.md, so it is not visible to the OS "
                         "and agents will not read into it. That may be exactly right. To bring "
                         "it in, give it a README; to declare it material rather than structure, "
                         "type its parent 'folder-readme-asset'; to hide it, prefix it with '_'")
            return

        if is_container:
            # 1.2 passes silently on a roster folder that has its front door.
            self.attempt("1.2")
        else:
            # 1.4 ran and found the child opted in. Nothing to say, but it ran.
            self.attempt("1.4")

        # The instance root is on its own roster; check_root already validated it.
        if path == self.root_path:
            return

        # Repo children: a self-contained repository's README.md is a codebase
        # README owned by that repo, not an OS-managed doc. Which containers
        # hold repos is instance knowledge, declared in the overlay.
        if path.parent.name in self.config.repo_child_containers and not is_container:
            self.log("2.5", "Repo README (frontmatter exempt)", "pass",
                     f"{self.rel(path)}/README.md is a codebase repo README")
            return

        self.validate_fm(readme_path, load_frontmatter(readme_path),
                         self.expected_type_for(path, is_container))

        # 1.5 — an asset library's children are material, not OS structure. Stop
        # here: do not walk in, do not expect READMEs, at any depth. Reported as
        # info so a reader can see where the walk deliberately ended, rather than
        # wondering why a folder full of logos produced no findings.
        if self.is_asset_library(path):
            self.log("1.5", "Asset library ends the walk", "info",
                     f"'{self.rel(path)}' is an asset library; its children are material, "
                     "not OS items, and were not walked")
            return

        # Client-specific checks (2.2-2.4) on direct children of a client container.
        if path.parent.name in self.config.client_containers and not is_container:
            self.check_client_folder(path)

        if is_container:
            for item in sorted(path.iterdir()):
                if item.is_dir() and not is_agent_ignored(item.name):
                    self.check_folder_recursive(item, is_container=False)

    def check_client_folder(self, path):
        # 2.2 Client Brief
        self.attempt("2.2")
        brief_path = path / "brief.md"
        if brief_path.exists():
            self.validate_fm(brief_path, load_frontmatter(brief_path), "brief-client")
        else:
            self.log("2.2", "Client brief presence", "warning", f"No brief.md in {path.name}")

        # 2.3 Client Manifest
        self.attempt("2.3")
        manifest_path = path / "manifest.md"
        if manifest_path.exists():
            self.validate_fm(manifest_path, load_frontmatter(manifest_path), "manifest-client")
        else:
            self.log("2.3", "Client manifest presence", "warning", f"No manifest.md in {path.name}")

        # 2.4 Duplicate briefs
        self.attempt("2.4")
        other_briefs = sorted(path.glob("brief*.md"))
        if len(other_briefs) > 1:
            canonical = path / "brief.md"
            others = [f.name for f in other_briefs if f != canonical]
            self.log("2.4", "Duplicate brief detection", "warning",
                     f"Found extra briefs in {path.name}: {', '.join(others)}")

    def rel(self, path):
        try:
            return str(Path(path).relative_to(self.root_path.parent))
        except ValueError:
            return str(path)

    def validate_fm(self, path, fm, expected_type):
        rel_path = self.rel(path)
        # Every document the OS owns. Its links are checked at the end (5.1, 8.1).
        if Path(path).suffix == ".md":
            self.os_files.append(Path(path))

        self.attempt("2.5")
        if not fm:
            self.log("2.5", "Frontmatter presence", "fail", f"No frontmatter in {rel_path}")
            return
        if "_error" in fm:
            self.log("2.5", "Frontmatter parsing", "fail", f"Error parsing frontmatter in {rel_path}: {fm['_error']}")
            return

        # 2.5 Required fields
        missing = [f for f in REQUIRED_FRONTMATTER if not fm.get(f)]
        if missing:
            self.log("2.5", "Required FM fields", "warning", f"{rel_path} missing: {', '.join(missing)}")

        # 3.1 Type taxonomy — is this a `type` the framework (or the overlay) knows?
        self.attempt("3.1")
        self.attempt("1.3")
        doc_type = fm.get("type")
        if doc_type and doc_type not in self.config.known_types():
            self.log("3.1", "Type taxonomy", "warning",
                     f"{rel_path} uses unknown type '{doc_type}' (not in the framework taxonomy)")
        elif doc_type in PENDING_TYPES:
            self.log("3.1", "Type taxonomy", "info",
                     f"{rel_path} uses '{doc_type}', which is in use but undocumented in framework/README.md")
        elif doc_type != expected_type:
            # 1.3 — the type is legal, but it isn't the one this position implies.
            # This is the check that catches a container README typed as an item:
            # the type is what tells an agent whether to descend, so a wrong one
            # sends the cascade the wrong way.
            self.log("1.3", "Declared type matches position", "warning",
                     f"{rel_path} type is '{doc_type}', expected '{expected_type}' for a folder in "
                     "this position")

        # 3.2 Status check
        self.attempt("3.2")
        status = fm.get("status")
        if status and status not in self.config.known_statuses():
            self.log("3.2", "Status validation", "warning", f"{rel_path} uses unknown status '{status}'")

        # 3.3 Date check
        self.attempt("3.3")
        updated = fm.get("last-updated")
        if updated and not validate_date(str(updated)):
            self.log("3.3", "ISO date validation", "fail", f"{rel_path} has invalid date format: '{updated}'")
            return

        # 3.4 Staleness — a document that claims to be `active` and hasn't been
        # touched in months is either fine or lying, and only a human knows which.
        # Informational by design: never a failure, and off entirely at 0 days.
        limit = self.config.staleness_days
        if limit > 0 and status in STALENESS_STATUSES and updated and validate_date(str(updated)):
            self.attempt("3.4")
            age = (datetime.now() - datetime.strptime(str(updated), "%Y-%m-%d")).days
            if age > limit:
                self.log("3.4", "Staleness", "warning",
                         f"{rel_path} is 'active' but was last updated {updated} ({age} days ago, "
                         f"limit {limit}). Either refresh it or set an honest status")

    def check_overlays(self):
        """6.1 and 6.2 — the instance's overlays are its configuration surface.

        An overlay with no matching framework skill is dead configuration: nothing
        will ever read it, and the day someone edits it expecting an effect is the
        day the instance lies to its owner.
        """
        overlays_dir = self.root_path / "overlays"
        if not overlays_dir.is_dir():
            return

        skills_dir = self.framework_path / "skills"
        overlays = sorted(p for p in overlays_dir.glob("*.md") if not is_agent_ignored(p.name))
        if not overlays:
            return

        for overlay in overlays:
            rel_path = self.rel(overlay)
            self.os_files.append(overlay)

            # 6.1 — pairing. Skipped (not failed) if we can't see the framework:
            # the script may have been copied somewhere without it.
            if skills_dir.is_dir():
                self.attempt("6.1")
                skill_name = overlay.stem
                if not (skills_dir / skill_name / "SKILL.md").exists():
                    self.log("6.1", "Overlay has a matching framework skill", "warning",
                             f"{rel_path} configures a skill named '{skill_name}', but there is no "
                             f"{skill_name}/SKILL.md in the framework. Nothing will read this overlay")
            else:
                self.not_applicable("6.1", f"framework skills not found at {skills_dir}")

            # 6.2 — an overlay's own frontmatter.
            self.attempt("6.2")
            fm = load_frontmatter(overlay)
            if not fm or "_error" in fm:
                self.log("6.2", "Overlay frontmatter", "fail", f"No readable frontmatter in {rel_path}")
                continue
            missing = [f for f in ("type", "skill", "instance", "last-updated") if not fm.get(f)]
            if missing:
                self.log("6.2", "Overlay frontmatter", "warning",
                         f"{rel_path} missing: {', '.join(missing)}")
            elif fm.get("type") != "skill-overlay":
                self.log("6.2", "Overlay frontmatter", "warning",
                         f"{rel_path} type is '{fm.get('type')}', expected 'skill-overlay'")

    @staticmethod
    def _points_into_ignored_folder(path_part):
        """True if a link target passes through an `_`-prefixed *folder*.

        The final component is only treated as a folder when the link says so
        (a trailing slash), because `agent-ignore.md` scopes the rule to folders:
        `_*/`, `**/_*/`. An underscore-prefixed file is not ignored, and the
        framework prescribes one (`Brand/_principal-review.md`).
        """
        components = list(Path(path_part).parts)
        if not path_part.endswith("/"):
            components = components[:-1]
        return any(part.startswith("_") for part in components)

    def check_links(self):
        """5.1 and 8.1 — every relative link in an OS document resolves.

        8.1 is the check the framework most needed and least had. A stale internal
        link is precisely the rot ACOS exists to prevent: the tree looks navigable,
        an agent follows a pointer, and the pointer goes nowhere. Two dead links
        survived in the reference instance's own root README for months because
        nothing looked.

        Warning, never failure: a link can break because the *target* moved, and
        the person running the checker may not be the person who should fix it.
        """
        if not self.os_files:
            return

        self.attempt("8.1")
        self.attempt("5.1")
        checked = 0

        for md in self.os_files:
            rel_file = self.rel(md)
            try:
                text = md.read_text(encoding="utf-8")
            except Exception as exc:
                self.log("8.1", "Internal links resolve", "warning",
                         f"Could not read {rel_file}: {exc}")
                continue

            for lineno, target in iter_links(text):
                path_part = link_target_path(target)
                if path_part is None:
                    continue

                # A placeholder that survived scaffolding is a dead link with a
                # friendlier face. Say what it is.
                if "<" in path_part and ">" in path_part:
                    self.log("8.1", "Internal links resolve", "warning",
                             f"{rel_file}:{lineno} -> {target} (unresolved template placeholder)")
                    continue

                checked += 1
                resolved = (md.parent / path_part)

                # 5.1 — nothing in the OS should point into an agent-ignored
                # folder. The reader is told to skip it; the link tells them not to.
                #
                # FOLDERS only. agent-ignore.md is explicit that the rule is
                # `_*/` — a *folder* prefix — and the framework relies on that:
                # client-brand-capture deliberately writes `Brand/_principal-review.md`
                # and the client brief template deliberately links to it. Flagging
                # underscore-prefixed *files* would flag the framework's own
                # prescribed output, which is how a validator teaches people to
                # ignore it.
                if self._points_into_ignored_folder(path_part):
                    self.log("5.1", "No references into agent-ignored folders", "warning",
                             f"{rel_file}:{lineno} -> {target} points inside an '_'-prefixed folder, "
                             "which agents are told to skip at any depth. Either the link or the "
                             "underscore is wrong")

                if not resolved.exists():
                    self.log("8.1", "Internal links resolve", "warning",
                             f"{rel_file}:{lineno} -> {target} (does not exist)")

        if checked:
            self.log("8.1", "Internal links resolve", "pass",
                     f"Resolved {checked} relative links across {len(self.os_files)} OS documents")

    def print_report(self, stream=None):
        # Resolve stdout at call time so callers can redirect it.
        stream = stream or sys.stdout

        def w(line=""):
            print(line, file=stream)

        titles = dict(CHECK_REGISTRY)
        suppressed = [cid for cid, _ in CHECK_REGISTRY if cid in self.config.suppress_checks]
        attempted = [cid for cid, _ in CHECK_REGISTRY if cid in self.attempted]
        skipped = [cid for cid, _ in CHECK_REGISTRY
                   if cid not in self.attempted and cid not in self.config.suppress_checks]

        w(f"# ACOS Integrity Report — {self.config.instance_name}")
        w()
        w(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
        w(f"**Instance root:** {self.root_path}")
        w(f"**Checks attempted:** {len(attempted)} of {len(CHECK_REGISTRY)} "
          f"({', '.join(attempted) if attempted else 'none'})")
        w(f"**Findings:** {self.stats['pass']} pass · {self.stats['warning']} warning · "
          f"{self.stats['fail']} fail · {self.stats['info']} info")
        w(f"**Inspected:** {self.folders_walked} folders, {len(self.os_files)} OS documents")
        w()

        # The failure mode this guards: reformat the folder map and the walk
        # silently visits nothing, every check finds nothing to complain about,
        # and the report reads like a clean bill of health. It must not.
        if self.folders_walked == 0:
            w("> **NOTHING WAS WALKED — THIS IS NOT A PASS.**")
            w("> The walk inspected 0 folders, so no check below had anything to run against. "
              "A report with no findings and no walk means the checker was blind, not that the "
              "instance is clean. Fix the `## Folder map` table in the instance root README "
              "(exact heading, real markdown table, folder name in backticks in the first column) "
              "and run again.")
            w()

        if skipped:
            w("**Not run:**")
            for cid in skipped:
                w(f"- {cid} {titles[cid]} — {self.not_run.get(cid, 'nothing to run it against')}")
            w()
        if suppressed:
            w(f"**Suppressed by the overlay:** {', '.join(suppressed)}")
            w()

        for _, line in sorted(self.report, key=lambda r: r[0]):
            w(line)

        attention = [line for cid, line in sorted(self.report, key=lambda r: r[0])
                     if line.startswith("❌") or line.startswith("⚠️")]
        if attention:
            w()
            w("## Items needing attention")
            for i, line in enumerate(attention, 1):
                w(f"{i}. {line}")


def find_instance_root(start_dir):
    """Walk up from start_dir looking for company-brief.md (the instance root marker)."""
    curr = Path(start_dir)
    while True:
        if (curr / "company-brief.md").exists():
            return curr
        if curr == curr.parent:
            return None
        curr = curr.parent


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run ACOS integrity checks against an instance tree.")
    parser.add_argument("--root", help="Instance root (folder containing company-brief.md). "
                                       "Default: discovered by walking up from the current directory.")
    parser.add_argument("--overlay", help="Path to the acos-integrity overlay. "
                                          "Default: <instance-root>/overlays/acos-integrity.md")
    parser.add_argument("--framework", help="Path to the ACOS framework/ directory, used to pair "
                                            "overlays with skills (check 6.1). "
                                            "Default: the framework/ next to this script.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any check fails.")
    args = parser.parse_args(argv)

    if args.root:
        root = Path(args.root).expanduser()
        if not (root / "company-brief.md").exists():
            print(f"Error: {root} is not an ACOS instance root (no company-brief.md).", file=sys.stderr)
            return 1
    else:
        # PWD first: preserves the logical path on macOS/Google Drive.
        root = find_instance_root(Path(os.environ.get("PWD", os.getcwd())))
        if not root:
            print("Error: Could not find ACOS instance root (company-brief.md) by walking up "
                  "from the current directory. Pass --root explicitly.", file=sys.stderr)
            return 1

    config = InstanceConfig.load(root, overlay_path=args.overlay)
    checker = ACOSIntegrityChecker(root, config=config, framework_path=args.framework)
    checker.run_checks()
    checker.print_report()

    # A walk that inspected nothing is a broken checker, not a clean instance, and
    # it exits non-zero whether or not --strict was asked for. Reporting rather
    # than breaking is a courtesy the findings get; it is not one a blind run gets.
    if checker.folders_walked == 0:
        return 1
    if args.strict and checker.stats["fail"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
