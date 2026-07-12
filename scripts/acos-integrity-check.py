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

# --- The three naming buckets (framework/README.md, "Folder naming") ---
#
# Bucket 3 / default — kebab-case: lowercase alphanumeric words joined by single
# dashes. Good: "acme-industries", "q3-strategy-review", "brand".
# Bad: "Acme Industries", "MyFolder", "my_folder", "MYFOLDER", "my--folder".
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Bucket 1 — container folders: the top-level organizing folders (the siblings of
# the instance root, listed in the root README's folder map). Capitalized, no
# spaces, no underscores, dashes between words.
# Good: "Clients", "Products", "Brand", "Design-System". Bad: "clients",
# "File Cabinet", "my_stuff".
CONTAINER_RE = re.compile(r"^[A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*$")

# Bucket 2 — item folders: a specific child of a container, named for the
# real-world thing it stands for. Any case (it's a proper noun, not a style
# choice), dots allowed (real company names have them), no spaces, no
# underscores, no leading/trailing/doubled dashes.
# Good: "Heartland-Paving-Partners", "ACOS", "Sprout.ai", "madefor-solutions",
# "1H26-AI-Growth". Bad: "AI Gateways", "SME_Brain_Dump", "-leading".
ITEM_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.]*(?:-[A-Za-z0-9][A-Za-z0-9.]*)*$")

CONTAINER, ITEM, DEFAULT = "container", "item", "default"

BUCKET_EXPECTATION = {
    CONTAINER: "container folders are Capitalized",
    ITEM: "item folders take the real-world proper name, dashes for spaces",
    DEFAULT: "expected kebab-case",
}

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
    """True only for lowercase kebab-case names — the default naming bucket."""
    if not isinstance(name, str) or not name:
        return False
    return bool(KEBAB_RE.match(name))


def is_container_name(name):
    """True for Capitalized container-folder names (Clients, Products, Design-System)."""
    if not isinstance(name, str) or not name:
        return False
    return bool(CONTAINER_RE.match(name))


def is_item_name(name):
    """True for proper-name item folders (ACOS, Heartland-Paving-Partners, Sprout.ai)."""
    if not isinstance(name, str) or not name:
        return False
    return bool(ITEM_RE.match(name))


def _universal_violation(name):
    """The two things forbidden in every bucket."""
    if " " in name or "\t" in name:
        return "contains spaces"
    if "_" in name:
        return "contains underscores"
    return None


def naming_violation(name, bucket=DEFAULT):
    """Describe why `name` breaks its naming bucket's rule, or None if it doesn't.

    Buckets (framework/README.md, "Folder naming — three buckets"):
      container — the top-level organizing folders. Capitalized.
      item      — a specific child of a container. Real-world proper name.
      default   — everything else. kebab-case.
    """
    if not isinstance(name, str) or not name:
        return "is not a usable folder name"

    universal = _universal_violation(name)
    if universal:
        return universal

    if bucket == CONTAINER:
        if is_container_name(name):
            return None
        if name[0].islower():
            return "is a container folder but is not Capitalized"
        return "is not a valid container name"

    if bucket == ITEM:
        if is_item_name(name):
            return None
        return "is not a usable item name (leading/trailing/doubled dash, or an illegal character)"

    if is_kebab_case(name):
        return None
    if any(c.isupper() for c in name):
        return "contains uppercase characters"
    if "." in name:
        return "contains dots"
    return "is not kebab-case"


def kebab_violation(name):
    """Back-compat shim: the default bucket's rule."""
    return naming_violation(name, DEFAULT)


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
        # contents; it is exempt from the kebab-case folder rule.
        self.instance_name = config.get("instance-name", self.root_path.name)

        # Convention default: an in-scope folder literally named "clients" holds
        # one folder per client. Overridable for instances that name it otherwise.
        self.client_containers = config.get("client-containers", ["Clients"])

        # Folders that ARE asset libraries (framework/README.md "Asset" README
        # pattern). Their README and their children's READMEs are asset-typed.
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

        content = readme_path.read_text(encoding="utf-8")
        if "## Folder map" in content:
            section = content.split("## Folder map")[1].split("\n##")[0]
            folders = re.findall(r"^\|\s*`([^/`]+)/?`", section, re.MULTILINE)
            self.in_scope_folders = [f for f in folders if not is_agent_ignored(f)]
            self.log("0.1", "Folder map extraction", "pass",
                     f"Found {len(self.in_scope_folders)} in-scope folders: {', '.join(self.in_scope_folders)}")
        else:
            self.log("0.1", "Folder map extraction", "fail", "Could not find '## Folder map' section in root README")

    def expected_type_for(self, path, is_container):
        if path.name in self.config.asset_folders or path.parent.name in self.config.asset_folders:
            return "folder-readme-asset"
        return "folder-readme-container" if is_container else "folder-readme-item"

    def check_folder_recursive(self, path, is_container=False):
        # Agent-ignore (framework/agent-ignore.md): underscore-prefixed folders
        # are out of scope, and so are hidden tool folders.
        if is_agent_ignored(path.name):
            return
        if path.name in self.config.exclude_folders:
            return

        # 4.1 Folder naming — the three-bucket house rule. A folder walked as a
        # container is in the container bucket; its direct children are items.
        # Anything deeper is the owner's working space and ACOS doesn't police it.
        if not self.config.is_naming_exempt(path.name):
            bucket = CONTAINER if is_container else ITEM
            reason = naming_violation(path.name, bucket)
            if reason:
                self.log("4.1", "Folder naming", "warning",
                         f"'{self.rel(path)}' {reason} ({BUCKET_EXPECTATION[bucket]})")

        readme_path = path / "README.md"
        if readme_path.exists():
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
        else:
            # 1.2 / 1.4 — containers and their item children must have a README.
            self.log("1.4", "README presence", "fail", f"Missing README.md in {self.rel(path)}")

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
