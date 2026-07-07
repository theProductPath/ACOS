#!/usr/bin/env python3
import os
import re
from datetime import datetime
from pathlib import Path

# --- Configuration & Taxonomy ---

REQUIRED_FRONTMATTER = ["type", "status", "last-updated", "maintainer", "purpose"]
KNOWN_TYPES = [
    "folder-readme-root", "folder-readme-container", "folder-readme-item",
    "folder-readme-asset", "brief-company", "brief-client", "client-manifest",
    "agent-ignore", "progress-checkpoint", "skill-overlay"
]
KNOWN_STATUSES = ["active", "drafting", "dormant", "archived", "deprecated"]

# --- Utility Functions ---

def load_frontmatter(file_path):
    """Extract and parse YAML frontmatter from a markdown file (regex fallback)."""
    try:
        content = Path(file_path).read_text()
        if content.startswith("---"):
            parts = content.split("---")
            if len(parts) >= 3:
                # Simple YAML parser for key-value pairs
                fm = {}
                for line in parts[1].strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        fm[k.strip()] = v.strip().strip('"').strip("'")
                return fm
    except Exception as e:
        return {"_error": str(e)}
    return None

def is_kebab_case(name):
    """Check if a string is kebab-case or an accepted non-kebab name pattern.

    ACOS allows: lowercase kebab-case (e.g., "my-folder"), PascalCase or camelCase
    (e.g., "MyFolder", "myFolder"), dotted names (e.g., "domain.tld"), hyphenated
    mixed-case (e.g., "My-Company-Name"), underscored names (e.g., "Some_Name"),
    and single-word names (e.g., common ACOS containers like Clients, Brand).
    Only flag names with actual spaces or clear naming violations.
    """
    # Allow established patterns
    if re.match(r'^[a-zA-Z0-9]', name) and ' ' not in name:
        return True
    return False

def validate_date(date_str):
    """Check if a string is a valid ISO 8601 date (YYYY-MM-DD)."""
    if not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# --- Check Implementation ---

class ACOSIntegrityChecker:
    def __init__(self, root_path):
        self.root_path = Path(root_path).expanduser() # Don't resolve, stay in logical path space
        self.report = []
        self.stats = {"pass": 0, "warning": 0, "fail": 0, "info": 0}
        self.in_scope_folders = []

    def log(self, check_id, title, status, message=""):
        self.stats[status] += 1
        icon = {"pass": "✅", "warning": "⚠️", "fail": "❌", "info": "ℹ️"}[status]
        self.report.append(f"{icon} {check_id} {title} — {status}{': ' + message if message else ''}")

    def run_checks(self):
        # 1. Root Checks
        self.check_root()
        
        if not self.in_scope_folders:
            self.log("0.0", "Instance Walk", "fail", "No in-scope folders found to walk.")
            return

        # 2. Folder Walk
        for folder_name in self.in_scope_folders:
            folder_path = self.root_path.parent / folder_name
            if folder_path.exists():
                self.check_folder_recursive(folder_path, is_container=True)
            else:
                self.log("1.2", "In-scope folder exists", "fail", f"Folder '{folder_name}' declared in map but not found at {folder_path}")

    def check_root(self):
        # 2.1 Company Brief
        cb_path = self.root_path / "company-brief.md"
        if cb_path.exists():
            self.log("2.1", "Company brief exists", "pass")
            fm = load_frontmatter(cb_path)
            self.validate_fm(cb_path, fm, "brief-company")
        else:
            self.log("2.1", "Company brief exists", "fail", "company-brief.md missing")

        # 1.1 Root README
        readme_path = self.root_path / "README.md"
        if readme_path.exists():
            self.log("1.1", "Instance root README", "pass")
            fm = load_frontmatter(readme_path)
            self.validate_fm(readme_path, fm, "folder-readme-root")
            
            # Extract folder map
            content = readme_path.read_text()
            # Simple extraction: look for table rows in the Folder map section
            if "## Folder map" in content:
                section = content.split("## Folder map")[1].split("##")[0]
                folders = re.findall(r'^\|\s*`([^/`]+)/?`', section, re.MULTILINE)
                self.in_scope_folders = [f for f in folders if not f.startswith("_")]
                self.log("0.1", "Folder map extraction", "pass", f"Found {len(self.in_scope_folders)} in-scope folders: {', '.join(self.in_scope_folders)}")
            else:
                self.log("0.1", "Folder map extraction", "fail", "Could not find '## Folder map' section in root README")
        else:
            self.log("1.1", "Instance root README", "fail", "README.md missing at root")

    def check_folder_recursive(self, path, is_container=False):
        # Skip agent-ignore folders
        if path.name.startswith("_"):
            return

        # 4.1 Naming - Allow tPPOS as instance name exception
        if not is_kebab_case(path.name) and path.name != "tPPOS":
            self.log("4.1", "Kebab-case naming", "warning", f"Folder '{path.name}' contains spaces or non-kebab characters.")
        
        readme_path = path / "README.md"
        if readme_path.exists():
            # If it's the root path itself, we already checked it
            if path == self.root_path:
                return

            # Products item folders are self-contained GitHub repos. Their README.md is a
            # codebase README written for the repo's developers/agents, not an OS-managed
            # doc, so it deliberately carries no tPPOS/ACOS frontmatter. Exempt these from
            # frontmatter (2.5) and type (3.1) validation. The OS layer for Products operates
            # at the container level only. See tPPOS/overlays/acos-integrity.md and
            # Products/README.md ("Child folder conventions").
            if path.parent.name == "Products" and not is_container:
                self.log("2.5", "Products repo README (frontmatter exempt)", "pass",
                         f"{path.name}/README.md is a codebase repo README")
                return

            expected_type = "folder-readme-container" if is_container else "folder-readme-item"
            # Special cases: Brand subfolders are assets, not items
            if path.name == "Brand": expected_type = "folder-readme-asset"
            if path.parent.name == "Brand": expected_type = "folder-readme-asset"
            
            fm = load_frontmatter(readme_path)
            self.validate_fm(readme_path, fm, expected_type)
        else:
            # Only fail README presence for Item/Container folders, not every subfolder
            if is_container or "Clients" in str(path) or "Products" in str(path):
                self.log("1.4", "README presence", "fail", f"Missing README.md in {path}")

        # Client specific checks
        if "Clients" in str(path) and not is_container:
            self.check_client_folder(path)

        # Recurse into children if this was a container
        if is_container:
            for item in path.iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    self.check_folder_recursive(item, is_container=False)

    def check_client_folder(self, path):
        # 2.2 Client Brief
        brief_path = path / "brief.md"
        if brief_path.exists():
            fm = load_frontmatter(brief_path)
            self.validate_fm(brief_path, fm, "brief-client")
        else:
            self.log("2.2", "Client brief presence", "warning", f"No brief.md in {path.name}")

        # 2.3 Client Manifest
        manifest_path = path / "manifest.md"
        if manifest_path.exists():
            fm = load_frontmatter(manifest_path)
            self.validate_fm(manifest_path, fm, "client-manifest")
        else:
            self.log("2.3", "Client manifest presence", "warning", f"No manifest.md in {path.name}")

        # 2.4 Duplicate briefs
        other_briefs = list(path.glob("brief*.md"))
        if len(other_briefs) > 1:
            canonical = path / "brief.md"
            others = [f.name for f in other_briefs if f != canonical]
            self.log("2.4", "Duplicate brief detection", "warning", f"Found extra briefs in {path.name}: {', '.join(others)}")

    def validate_fm(self, path, fm, expected_type):
        rel_path = path.relative_to(self.root_path.parent)
        if not fm:
            self.log("2.5", "Frontmatter presence", "fail", f"No frontmatter in {rel_path}")
            return
        if "_error" in fm:
            self.log("2.5", "Frontmatter parsing", "fail", f"Error parsing frontmatter in {rel_path}: {fm['_error']}")
            return

        # 2.5 Required fields
        missing = [f for f in REQUIRED_FRONTMATTER if f not in fm]
        if missing:
            self.log("2.5", "Required FM fields", "warning", f"{rel_path} missing: {', '.join(missing)}")

        # 3.1 Type check
        doc_type = fm.get("type")
        if doc_type != expected_type:
            self.log("3.1", "Type validation", "warning", f"{rel_path} type is '{doc_type}', expected '{expected_type}'")
        elif doc_type not in KNOWN_TYPES:
            self.log("3.1", "Type taxonomy", "info", f"{rel_path} uses custom type '{doc_type}'")

        # 3.2 Status check
        status = fm.get("status")
        if status and status not in KNOWN_STATUSES:
            self.log("3.2", "Status validation", "warning", f"{rel_path} uses unknown status '{status}'")

        # 3.3 Date check
        updated = fm.get("last-updated")
        if updated and not validate_date(str(updated)):
            self.log("3.3", "ISO date validation", "fail", f"{rel_path} has invalid date format: '{updated}'")

    def print_report(self):
        print(f"# ACOS Integrity Report — {self.root_path.parent.name}")
        print(f"\n**Date:** {datetime.now().strftime('%Y-%m-%d')}")
        print(f"**Instance root:** {self.root_path}")
        print(f"**Pass:** {self.stats['pass']}  **Warning:** {self.stats['warning']}  **Fail:** {self.stats['fail']}  **Info:** {self.stats['info']}")
        print("\n---")
        for line in self.report:
            print(line)

if __name__ == "__main__":
    import sys
    # Find root by walking up for company-brief.md
    # Try PWD env var first to preserve logical path on macOS/Google Drive
    start_dir = Path(os.environ.get('PWD', os.getcwd()))
    root = None
    curr = start_dir
    while curr != curr.parent:
        if (curr / "company-brief.md").exists():
            root = curr
            break
        curr = curr.parent
    
    if not root:
        print("Error: Could not find ACOS instance root (company-brief.md) by walking up from current directory.")
        sys.exit(1)

    checker = ACOSIntegrityChecker(root)
    checker.run_checks()
    checker.print_report()
