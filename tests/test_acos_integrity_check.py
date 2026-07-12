#!/usr/bin/env python3
"""Tests for scripts/acos-integrity-check.py.

Stdlib only (unittest). Run from the repo root:

    python3 -m unittest discover -s tests -v
"""

import contextlib
import importlib.util
import io
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "acos-integrity-check.py"

# The script's filename has dashes, so it can't be imported normally.
_spec = importlib.util.spec_from_file_location("acos_integrity_check", SCRIPT_PATH)
aic = importlib.util.module_from_spec(_spec)
sys.modules["acos_integrity_check"] = aic
_spec.loader.exec_module(aic)


class TestKebabCase(unittest.TestCase):
    """The house rule: folder names are lowercase words joined by single dashes."""

    def test_valid_kebab_case(self):
        for name in [
            "my-folder",
            "acme-industries",
            "q3-strategy-review",
            "brand",
            "clients",
            "a",
            "2026-review",
            "tpp-website-v2",
            "a-b-c-d",
        ]:
            with self.subTest(name=name):
                self.assertTrue(aic.is_kebab_case(name), f"{name!r} should be valid kebab-case")

    def test_rejects_pascal_case(self):
        # The original bug: PascalCase silently passed.
        self.assertFalse(aic.is_kebab_case("MyFolder"))
        self.assertFalse(aic.is_kebab_case("Clients"))
        self.assertFalse(aic.is_kebab_case("Heartland-Paving-Partners"))

    def test_rejects_camel_case(self):
        self.assertFalse(aic.is_kebab_case("myFolder"))

    def test_rejects_screaming_case(self):
        self.assertFalse(aic.is_kebab_case("MYFOLDER"))
        self.assertFalse(aic.is_kebab_case("AIRS"))

    def test_rejects_snake_case(self):
        self.assertFalse(aic.is_kebab_case("my_folder"))
        self.assertFalse(aic.is_kebab_case("SME_Brain_Dump"))

    def test_rejects_spaces(self):
        self.assertFalse(aic.is_kebab_case("My Folder"))
        self.assertFalse(aic.is_kebab_case("AI Gateways"))
        self.assertFalse(aic.is_kebab_case("File Cabinet"))

    def test_rejects_dots_and_edge_cases(self):
        self.assertFalse(aic.is_kebab_case("sprout.ai"))
        self.assertFalse(aic.is_kebab_case("my--folder"))
        self.assertFalse(aic.is_kebab_case("-leading"))
        self.assertFalse(aic.is_kebab_case("trailing-"))
        self.assertFalse(aic.is_kebab_case(""))
        self.assertFalse(aic.is_kebab_case(None))

    def test_violation_reasons(self):
        self.assertIsNone(aic.kebab_violation("my-folder"))
        self.assertEqual(aic.kebab_violation("My Folder"), "contains spaces")
        self.assertEqual(aic.kebab_violation("MyFolder"), "contains uppercase characters")
        self.assertEqual(aic.kebab_violation("my_folder"), "contains underscores")
        self.assertEqual(aic.kebab_violation("sprout.ai"), "contains dots")
        self.assertEqual(aic.kebab_violation("my--folder"), "is not kebab-case")


class TestFrontmatterParsing(unittest.TestCase):
    def test_parses_required_fields(self):
        fm = aic.parse_frontmatter_text(
            "---\n"
            "type: folder-readme-item\n"
            "status: active\n"
            "last-updated: 2026-07-12\n"
            "maintainer: Steven Jones\n"
            "purpose: A thing.\n"
            "---\n\n# Heading\n"
        )
        self.assertEqual(fm["type"], "folder-readme-item")
        self.assertEqual(fm["status"], "active")
        self.assertEqual(fm["last-updated"], "2026-07-12")
        self.assertEqual(fm["purpose"], "A thing.")

    def test_no_frontmatter_returns_none(self):
        self.assertIsNone(aic.parse_frontmatter_text("# Just a heading\n\nSome prose.\n"))

    def test_body_horizontal_rules_do_not_confuse_the_parser(self):
        fm = aic.parse_frontmatter_text(
            "---\ntype: brief-client\nstatus: active\n---\n\n# Brief\n\n---\n\nsection\n"
        )
        self.assertEqual(set(fm), {"type", "status"})

    def test_values_with_colons_survive(self):
        fm = aic.parse_frontmatter_text(
            "---\npurpose: Do the thing: carefully, and well.\n---\n"
        )
        self.assertEqual(fm["purpose"], "Do the thing: carefully, and well.")

    def test_inline_comments_are_stripped(self):
        fm = aic.parse_frontmatter_text("---\nstatus: active  # active | paused | wrapped\n---\n")
        self.assertEqual(fm["status"], "active")

    def test_quotes_are_stripped(self):
        fm = aic.parse_frontmatter_text('---\nmaintainer: "Steven Jones"\n---\n')
        self.assertEqual(fm["maintainer"], "Steven Jones")

    def test_unreadable_file_reports_error(self):
        fm = aic.load_frontmatter(Path(tempfile.gettempdir()) / "definitely-not-a-real-file-xyz.md")
        self.assertIn("_error", fm)

    def test_iso_date_validation(self):
        self.assertTrue(aic.validate_date("2026-07-12"))
        self.assertFalse(aic.validate_date("07/12/2026"))
        self.assertFalse(aic.validate_date("July 12, 2026"))
        self.assertFalse(aic.validate_date("2026-13-01"))
        self.assertFalse(aic.validate_date(None))


def manual_types():
    """The `type` taxonomy as documented in framework/README.md.

    The manual is the source of truth for the taxonomy — not the script. This
    parses the bullet list under the "Frontmatter" section so the two can't
    drift apart silently again.
    """
    text = (REPO_ROOT / "framework" / "README.md").read_text(encoding="utf-8")
    section = text.split("The `type` taxonomy currently in use:", 1)[1].split("\n##", 1)[0]
    return set(re.findall(r"^- `([a-z0-9-]+)`", section, re.MULTILINE))


class TestTaxonomy(unittest.TestCase):
    def test_the_manual_documents_at_least_the_core_types(self):
        # Guard against the parse silently returning nothing.
        types = manual_types()
        self.assertGreaterEqual(len(types), 10)
        self.assertIn("folder-readme-root", types)
        self.assertIn("dashboard-company", types)

    def test_every_type_in_the_manual_is_accepted_by_the_checker(self):
        # This is the bug that shipped: the manual documented types the script
        # had never heard of (dashboard-company among them).
        config = aic.InstanceConfig("/tmp/instance")
        missing = manual_types() - config.known_types()
        self.assertEqual(missing, set(), f"types documented in framework/README.md but unknown to the script: {missing}")

    def test_the_script_invents_no_framework_types(self):
        # Anything in FRAMEWORK_TYPES must be documented in the manual.
        undocumented = aic.FRAMEWORK_TYPES - manual_types()
        self.assertEqual(undocumented, set(),
                         f"types in FRAMEWORK_TYPES with no entry in framework/README.md: {undocumented}")

    def test_pending_types_are_disjoint_from_framework_types(self):
        self.assertEqual(aic.PENDING_TYPES & aic.FRAMEWORK_TYPES, set())

    def test_pending_types_are_accepted_not_rejected(self):
        config = aic.InstanceConfig("/tmp/instance")
        for t in ["skill-overlay", "brief-stakeholder", "acos-doc", "framework-doc"]:
            with self.subTest(type=t):
                self.assertIn(t, config.known_types())

    def test_custom_types_from_overlay_extend_the_taxonomy(self):
        config = aic.InstanceConfig("/tmp/instance", config={"custom-types": ["instance-decision"]})
        self.assertIn("instance-decision", config.known_types())
        self.assertNotIn("some-other-type", config.known_types())


class TestConfigBlockParsing(unittest.TestCase):
    def test_parses_inline_lists_and_scalars(self):
        config = aic.parse_config_block(
            "prose before\n\n"
            "```acos-config\n"
            "instance-name: tPPOS\n"
            "client-containers: [Clients]\n"
            "asset-folders: [Brand, Design]\n"
            "exclude-folders: []\n"
            "```\n\nprose after\n"
        )
        self.assertEqual(config["instance-name"], "tPPOS")
        self.assertEqual(config["client-containers"], ["Clients"])
        self.assertEqual(config["asset-folders"], ["Brand", "Design"])
        self.assertEqual(config["exclude-folders"], [])

    def test_parses_dash_lists(self):
        config = aic.parse_config_block(
            "```acos-config\nnaming-exempt:\n  - AI Gateways\n  - File Cabinet\n```\n"
        )
        self.assertEqual(config["naming-exempt"], ["AI Gateways", "File Cabinet"])

    def test_no_block_returns_empty(self):
        self.assertEqual(aic.parse_config_block("# Overlay\n\nJust prose.\n"), {})

    def test_defaults_are_framework_neutral(self):
        config = aic.InstanceConfig("/tmp/acme-os")
        self.assertEqual(config.instance_name, "acme-os")
        self.assertEqual(config.asset_folders, [])
        self.assertEqual(config.repo_child_containers, [])
        self.assertEqual(config.suppress_checks, [])


class TestAgentIgnore(unittest.TestCase):
    def test_underscore_prefixed_names_are_ignored(self):
        self.assertTrue(aic.is_agent_ignored("_archive"))
        self.assertTrue(aic.is_agent_ignored("_progress"))
        self.assertTrue(aic.is_agent_ignored("_Notes"))

    def test_hidden_folders_are_ignored(self):
        self.assertTrue(aic.is_agent_ignored(".git"))
        self.assertTrue(aic.is_agent_ignored(".obsidian"))

    def test_normal_folders_are_not_ignored(self):
        self.assertFalse(aic.is_agent_ignored("clients"))
        self.assertFalse(aic.is_agent_ignored("Brand"))


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def readme(type_, name, status="active"):
    return (
        f"---\ntype: {type_}\nstatus: {status}\nlast-updated: 2026-07-12\n"
        f"maintainer: Test\npurpose: {name}\n---\n\n# {name}\n"
    )


class TestWalkOnFixtureInstance(unittest.TestCase):
    """End-to-end walk over a synthetic instance (no tPPOS knowledge required)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        tree = self.tmp / "acme"
        self.root = tree / "acme-os"

        write(self.root / "company-brief.md", readme("brief-company", "Acme"))
        write(
            self.root / "README.md",
            readme("folder-readme-root", "Acme OS")
            + "\n## Folder map\n\n| Folder | What |\n|---|---|\n"
            "| `acme-os/` | You are here. |\n"
            "| `clients/` | Client work. |\n"
            "| `brand/` | Assets. |\n"
            "| `repos/` | Codebases. |\n"
            "\n## Next section\n\nnot part of the map\n",
        )
        write(tree / "clients" / "README.md", readme("folder-readme-container", "Clients"))
        # A well-formed client.
        write(tree / "clients" / "good-client" / "README.md", readme("folder-readme-item", "Good"))
        write(tree / "clients" / "good-client" / "brief.md", readme("brief-client", "Good"))
        write(tree / "clients" / "good-client" / "manifest.md", readme("client-manifest", "Good"))
        # A badly named client with a missing brief and a bogus status.
        write(tree / "clients" / "Bad Client" / "README.md", readme("folder-readme-item", "Bad", status="on hold"))
        write(tree / "clients" / "Bad Client" / "manifest.md", readme("client-manifest", "Bad"))
        # Agent-ignored: must never be walked.
        write(tree / "clients" / "_archive" / "README.md", readme("nonsense-type", "Archived"))
        write(tree / "clients" / "_archive" / "MyBadName" / "README.md", "no frontmatter\n")
        # Asset library.
        write(tree / "brand" / "README.md", readme("folder-readme-asset", "Brand"))
        write(tree / "brand" / "colors" / "README.md", readme("folder-readme-item", "Colors"))
        # Repo container: children carry codebase READMEs with no frontmatter.
        write(tree / "repos" / "README.md", readme("folder-readme-container", "Repos"))
        write(tree / "repos" / "widget" / "README.md", "# widget\n\nA codebase README.\n")

        self.tree = tree

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_checker(self, overlay_config=None):
        config = aic.InstanceConfig(self.root, config=overlay_config)
        checker = aic.ACOSIntegrityChecker(self.root, config=config)
        checker.run_checks()
        return checker, [line for _, line in checker.report]

    def test_folder_map_extraction(self):
        checker, _ = self.run_checker()
        self.assertEqual(checker.in_scope_folders, ["acme-os", "clients", "brand", "repos"])

    def test_agent_ignore_rule_skips_underscore_folders(self):
        _, lines = self.run_checker()
        joined = "\n".join(lines)
        self.assertNotIn("_archive", joined)
        self.assertNotIn("MyBadName", joined)
        self.assertNotIn("nonsense-type", joined)

    def test_kebab_case_violation_is_reported(self):
        _, lines = self.run_checker()
        hits = [line for line in lines if "4.1" in line]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("Bad Client", hits[0])
        self.assertIn("contains spaces", hits[0])

    def test_instance_root_folder_is_naming_exempt(self):
        _, lines = self.run_checker({"instance-name": "AcmeOS"})
        self.assertFalse([line for line in lines if "AcmeOS" in line and "4.1" in line])

    def test_naming_exempt_suppresses_a_known_legacy_name(self):
        _, lines = self.run_checker({"client-containers": ["clients"], "naming-exempt": ["Bad Client"]})
        self.assertFalse([line for line in lines if "4.1" in line])

    def test_missing_client_brief_is_flagged(self):
        _, lines = self.run_checker({"client-containers": ["clients"]})
        self.assertTrue([line for line in lines if "2.2" in line and "Bad Client" in line])

    def test_client_checks_do_not_run_without_a_client_container(self):
        # No client-containers configured (and none named "Clients"): 2.2/2.3 silent.
        _, lines = self.run_checker({"client-containers": []})
        self.assertFalse([line for line in lines if line.startswith("⚠️ 2.2") or line.startswith("⚠️ 2.3")])

    def test_unknown_status_is_flagged(self):
        _, lines = self.run_checker()
        self.assertTrue([line for line in lines if "3.2" in line and "on hold" in line])

    def test_custom_status_from_overlay_silences_it(self):
        _, lines = self.run_checker({"custom-statuses": ["on hold"]})
        self.assertFalse([line for line in lines if "3.2" in line])

    def test_asset_folder_children_expect_asset_type(self):
        _, lines = self.run_checker({"asset-folders": ["brand"]})
        hits = [line for line in lines if "3.1" in line and "colors" in line]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("expected 'folder-readme-asset'", hits[0])

    def test_repo_child_readme_is_frontmatter_exempt_when_configured(self):
        _, lines = self.run_checker({"repo-child-containers": ["repos"]})
        self.assertTrue([line for line in lines if line.startswith("✅ 2.5") and "widget" in line])
        self.assertFalse([line for line in lines if line.startswith("❌ 2.5") and "widget" in line])

    def test_repo_child_readme_fails_frontmatter_without_the_exemption(self):
        _, lines = self.run_checker()
        self.assertTrue([line for line in lines if line.startswith("❌ 2.5") and "widget" in line])

    def test_missing_readme_is_a_failure(self):
        (self.tree / "clients" / "orphan-client").mkdir()
        _, lines = self.run_checker()
        self.assertTrue([line for line in lines if "1.4" in line and "orphan-client" in line])

    def test_suppress_checks_from_overlay(self):
        _, lines = self.run_checker({"suppress-checks": ["4.1", "3.2"]})
        self.assertFalse([line for line in lines if "4.1" in line or "3.2" in line])

    def test_exclude_folders_from_overlay(self):
        _, lines = self.run_checker({"exclude-folders": ["clients"]})
        self.assertFalse([line for line in lines if "Bad Client" in line])

    def test_missing_in_scope_folder_fails(self):
        shutil.rmtree(self.tree / "brand")
        _, lines = self.run_checker()
        self.assertTrue([line for line in lines if line.startswith("❌ 1.2") and "brand" in line])

    def test_overlay_is_read_from_disk(self):
        write(
            self.root / "overlays" / "acos-integrity.md",
            "# overlay\n\n```acos-config\nasset-folders: [brand]\nsuppress-checks: [4.1]\n```\n",
        )
        config = aic.InstanceConfig.load(self.root)
        self.assertTrue(config.overlay_loaded)
        self.assertEqual(config.asset_folders, ["brand"])
        checker = aic.ACOSIntegrityChecker(self.root, config=config)
        checker.run_checks()
        lines = [line for _, line in checker.report]
        self.assertTrue([line for line in lines if line.startswith("✅ 0.3")])
        self.assertFalse([line for line in lines if "4.1" in line])

    def test_no_overlay_still_runs(self):
        config = aic.InstanceConfig.load(self.root)
        self.assertFalse(config.overlay_loaded)
        checker = aic.ACOSIntegrityChecker(self.root, config=config)
        checker.run_checks()
        self.assertTrue(checker.report)

    def test_find_instance_root(self):
        found = aic.find_instance_root(self.tree / "clients" / "good-client")
        self.assertIsNone(found)  # company-brief.md is not above clients/
        self.assertEqual(aic.find_instance_root(self.root), self.root)

    def test_main_exit_codes(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(aic.main(["--root", str(self.root)]), 0)
            # widget/README.md has no frontmatter and no exemption configured.
            self.assertEqual(aic.main(["--root", str(self.root), "--strict"]), 1)
            self.assertEqual(aic.main(["--root", str(self.tree / "clients")]), 1)  # not an instance root


if __name__ == "__main__":
    unittest.main()
