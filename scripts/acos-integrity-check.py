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

# --- Configuration & Taxonomy ---

REQUIRED_FRONTMATTER = ["type", "status", "last-updated", "maintainer", "purpose"]

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
    "client-manifest",
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


class ACOSIntegrityChecker:
    def __init__(self, root_path, config=None):
        # Don't resolve: stay in logical path space (Google Drive symlinks).
        self.root_path = Path(root_path).expanduser()
        self.config = config or InstanceConfig(self.root_path)
        self.report = []
        self.stats = {"pass": 0, "warning": 0, "fail": 0, "info": 0}
        self.in_scope_folders = []
        self.folders_walked = 0

    def log(self, check_id, title, status, message=""):
        if check_id in self.config.suppress_checks:
            return
        self.stats[status] += 1
        icon = {"pass": "✅", "warning": "⚠️", "fail": "❌", "info": "ℹ️"}[status]
        self.report.append((check_id, f"{icon} {check_id} {title} — {status}{': ' + message if message else ''}"))

    def run_checks(self):
        self.check_overlay()
        self.check_root()

        if not self.in_scope_folders:
            self.log("0.0", "Instance Walk", "fail", "No in-scope folders found to walk.")
            return

        for folder_name in self.in_scope_folders:
            if folder_name in self.config.exclude_folders:
                self.log("0.2", "Excluded folder", "info", f"Skipping '{folder_name}' per overlay exclude-folders")
                continue
            folder_path = self.root_path.parent / folder_name
            if folder_path.exists():
                self.check_folder_recursive(folder_path, is_container=True)
            else:
                self.log("1.2", "In-scope folder exists", "fail",
                         f"Folder '{folder_name}' declared in map but not found at {folder_path}")

        # A clean instance would otherwise report almost nothing, since the
        # per-folder checks only speak up when something is wrong. Say what was
        # actually inspected so "no findings" reads as "checked" and not "skipped".
        self.log("0.4", "Instance walk", "pass",
                 f"Walked {self.folders_walked} folders under {len(self.in_scope_folders)} in-scope roots")

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
                self.log("1.2", "In-scope folder README", "fail",
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

        # An asset library's children are material, not OS structure. Stop here:
        # do not walk in, do not expect READMEs, at any depth.
        if self.is_asset_library(path):
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
        brief_path = path / "brief.md"
        if brief_path.exists():
            self.validate_fm(brief_path, load_frontmatter(brief_path), "brief-client")
        else:
            self.log("2.2", "Client brief presence", "warning", f"No brief.md in {path.name}")

        # 2.3 Client Manifest
        manifest_path = path / "manifest.md"
        if manifest_path.exists():
            self.validate_fm(manifest_path, load_frontmatter(manifest_path), "client-manifest")
        else:
            self.log("2.3", "Client manifest presence", "warning", f"No manifest.md in {path.name}")

        # 2.4 Duplicate briefs
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

        # 3.1 Type check — taxonomy first, then the expectation for this position.
        doc_type = fm.get("type")
        if doc_type and doc_type not in self.config.known_types():
            self.log("3.1", "Type taxonomy", "warning",
                     f"{rel_path} uses unknown type '{doc_type}' (not in the framework taxonomy)")
        elif doc_type in PENDING_TYPES:
            self.log("3.1", "Type taxonomy", "info",
                     f"{rel_path} uses '{doc_type}', which is in use but undocumented in framework/README.md")
        elif doc_type != expected_type:
            self.log("3.1", "Type validation", "warning",
                     f"{rel_path} type is '{doc_type}', expected '{expected_type}'")

        # 3.2 Status check
        status = fm.get("status")
        if status and status not in self.config.known_statuses():
            self.log("3.2", "Status validation", "warning", f"{rel_path} uses unknown status '{status}'")

        # 3.3 Date check
        updated = fm.get("last-updated")
        if updated and not validate_date(str(updated)):
            self.log("3.3", "ISO date validation", "fail", f"{rel_path} has invalid date format: '{updated}'")

    def print_report(self, stream=None):
        # Resolve stdout at call time so callers can redirect it.
        stream = stream or sys.stdout

        def w(line=""):
            print(line, file=stream)

        w(f"# ACOS Integrity Report — {self.config.instance_name}")
        w()
        w(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
        w(f"**Instance root:** {self.root_path}")
        w(f"**Checks run:** {sum(self.stats.values())}")
        w(f"**Pass:** {self.stats['pass']}  **Warning:** {self.stats['warning']}  "
          f"**Fail:** {self.stats['fail']}  **Info:** {self.stats['info']}")
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
    checker = ACOSIntegrityChecker(root, config=config)
    checker.run_checks()
    checker.print_report()

    if args.strict and checker.stats["fail"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
