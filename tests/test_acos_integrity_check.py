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


class TestContainerBucket(unittest.TestCase):
    """Bucket 1: the top-level organizing folders are Capitalized."""

    def test_accepts_capitalized_containers(self):
        for name in ["Clients", "Products", "Projects", "Brand", "Research", "Admin",
                     "Suppliers", "Design-System", "Q3-Reviews", "C"]:
            with self.subTest(name=name):
                self.assertTrue(aic.is_container_name(name))
                self.assertIsNone(aic.naming_violation(name, aic.CONTAINER))

    def test_rejects_lowercase_containers(self):
        # The framework prescribes Clients/, not clients/.
        for name in ["clients", "brand", "design-system"]:
            with self.subTest(name=name):
                self.assertFalse(aic.is_container_name(name))
                self.assertEqual(aic.naming_violation(name, aic.CONTAINER),
                                 "is a container folder but is not Capitalized")

    def test_rejects_spaces_and_underscores_in_containers(self):
        self.assertEqual(aic.naming_violation("File Cabinet", aic.CONTAINER), "contains spaces")
        self.assertEqual(aic.naming_violation("File_Cabinet", aic.CONTAINER), "contains underscores")

    def test_rejects_malformed_containers(self):
        for name in ["-Clients", "Clients-", "Clients--Old", "Sprout.ai", ""]:
            with self.subTest(name=name):
                self.assertIsNotNone(aic.naming_violation(name, aic.CONTAINER))


class TestItemBucket(unittest.TestCase):
    """Bucket 2: an item folder carries the real-world proper name of its thing."""

    def test_accepts_proper_names(self):
        # Every one of these is a name ACOS itself, or a real instance, prescribes.
        for name in [
            "ACOS", "AIRS", "ATP", "LAIR", "RAG",
            "Heartland-Paving-Partners", "Lock-8-Partners", "Objective-Partners",
            "Sprout.ai", "madefor-solutions", "1H26-AI-Growth", "tPP-website",
            "Anthropic-Academy", "Accounting", "colors",
        ]:
            with self.subTest(name=name):
                self.assertTrue(aic.is_item_name(name))
                self.assertIsNone(aic.naming_violation(name, aic.ITEM))

    def test_rejects_spaces_and_underscores_in_items(self):
        # These are the violations the narrowed rule still cares about.
        self.assertEqual(aic.naming_violation("AI Gateways", aic.ITEM), "contains spaces")
        self.assertEqual(aic.naming_violation("File Cabinet", aic.ITEM), "contains spaces")
        self.assertEqual(aic.naming_violation("SME_Brain_Dump_Build-Experiment", aic.ITEM),
                         "contains underscores")

    def test_rejects_malformed_items(self):
        for name in ["-leading", "trailing-", "my--folder", "", "a/b"]:
            with self.subTest(name=name):
                self.assertIsNotNone(aic.naming_violation(name, aic.ITEM))

    def test_an_item_is_not_forced_to_be_kebab(self):
        # The whole point of the narrowing: kebab-checking a proper noun is wrong.
        self.assertFalse(aic.is_kebab_case("Heartland-Paving-Partners"))
        self.assertIsNone(aic.naming_violation("Heartland-Paving-Partners", aic.ITEM))


class TestKebabCase(unittest.TestCase):
    """Bucket 3 (the default): everything else is lowercase words joined by dashes."""

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

    def test_the_default_bucket_still_rejects_container_and_item_styling(self):
        # A skill, template, or overlay named "Clients" or "Sprout.ai" is wrong.
        self.assertEqual(aic.naming_violation("Clients", aic.DEFAULT), "contains uppercase characters")
        self.assertEqual(aic.naming_violation("Sprout.ai", aic.DEFAULT), "contains uppercase characters")
        self.assertEqual(aic.naming_violation("sprout.ai", aic.DEFAULT), "contains dots")
        self.assertIsNone(aic.naming_violation("client-brief-processor", aic.DEFAULT))

    def test_naming_violation_defaults_to_the_kebab_bucket(self):
        self.assertEqual(aic.naming_violation("MyFolder"), "contains uppercase characters")


class TestStatusVocabulary(unittest.TestCase):
    """The statuses the templates prescribe must be the statuses the checker accepts."""

    def test_every_status_the_templates_prescribe_is_accepted(self):
        # The bug this guards: templates shipped `status: skeleton` while the
        # checker only knew active/drafting/dormant/archived/deprecated, so a
        # freshly-scaffolded instance failed the framework's own validator.
        config = aic.InstanceConfig("/tmp/instance")
        prescribed = set()
        for template in (REPO_ROOT / "framework" / "templates").glob("*.md"):
            fm_match = re.match(r"\A---\n(.*?)\n---", template.read_text(encoding="utf-8"), re.DOTALL)
            if not fm_match:
                continue
            for line in fm_match.group(1).split("\n"):
                if line.startswith("status:"):
                    value, _, comment = line[len("status:"):].partition("#")
                    prescribed.add(value.strip())
                    prescribed.update(v.strip() for v in comment.split("|") if v.strip())
        self.assertGreaterEqual(len(prescribed), 8)
        self.assertIn("skeleton", prescribed)
        missing = prescribed - config.known_statuses()
        self.assertEqual(missing, set(),
                         f"statuses prescribed by framework/templates/ but rejected by the checker: {missing}")

    def test_unknown_status_is_still_rejected(self):
        config = aic.InstanceConfig("/tmp/instance")
        self.assertNotIn("on hold", config.known_statuses())
        self.assertNotIn("in-progress", config.known_statuses())


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
            "| `Clients/` | Client work. |\n"
            "| `Brand/` | Assets. |\n"
            "| `Repos/` | Codebases. |\n"
            "\n## Next section\n\nnot part of the map\n",
        )
        write(tree / "Clients" / "README.md", readme("folder-readme-container", "Clients"))
        # A well-formed client, named for the real-world thing it stands for.
        write(tree / "Clients" / "Acme-Industries" / "README.md", readme("folder-readme-item", "Acme"))
        write(tree / "Clients" / "Acme-Industries" / "brief.md", readme("brief-client", "Acme"))
        write(tree / "Clients" / "Acme-Industries" / "manifest.md", readme("client-manifest", "Acme"))
        # A badly named client with a missing brief and a bogus status.
        write(tree / "Clients" / "Bad Client" / "README.md", readme("folder-readme-item", "Bad", status="on hold"))
        write(tree / "Clients" / "Bad Client" / "manifest.md", readme("client-manifest", "Bad"))
        # Agent-ignored: must never be walked.
        write(tree / "Clients" / "_archive" / "README.md", readme("nonsense-type", "Archived"))
        write(tree / "Clients" / "_archive" / "MyBadName" / "README.md", "no frontmatter\n")
        # Asset library.
        write(tree / "Brand" / "README.md", readme("folder-readme-asset", "Brand"))
        write(tree / "Brand" / "colors" / "README.md", readme("folder-readme-item", "Colors"))
        # Repo container: children carry codebase READMEs with no frontmatter.
        write(tree / "Repos" / "README.md", readme("folder-readme-container", "Repos"))
        write(tree / "Repos" / "widget" / "README.md", "# widget\n\nA codebase README.\n")

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
        self.assertEqual(checker.in_scope_folders, ["acme-os", "Clients", "Brand", "Repos"])

    def test_agent_ignore_rule_skips_underscore_folders(self):
        _, lines = self.run_checker()
        joined = "\n".join(lines)
        self.assertNotIn("_archive", joined)
        self.assertNotIn("MyBadName", joined)
        self.assertNotIn("nonsense-type", joined)

    def test_only_the_real_naming_violation_is_reported(self):
        # Capitalized containers and a proper-name item are correct, not findings.
        _, lines = self.run_checker()
        hits = [line for line in lines if "4.1" in line]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("Bad Client", hits[0])
        self.assertIn("contains spaces", hits[0])

    def test_lowercase_container_is_reported(self):
        (self.tree / "Clients").rename(self.tree / "vendors")
        readme_path = self.root / "README.md"
        readme_path.write_text(
            readme_path.read_text(encoding="utf-8").replace("| `Clients/` |", "| `vendors/` |"),
            encoding="utf-8",
        )
        _, lines = self.run_checker()
        self.assertTrue([line for line in lines if "4.1" in line and "vendors" in line
                         and "not Capitalized" in line])

    def test_instance_root_folder_is_naming_exempt(self):
        _, lines = self.run_checker({"instance-name": "AcmeOS"})
        self.assertFalse([line for line in lines if "AcmeOS" in line and "4.1" in line])

    def test_naming_exempt_suppresses_a_known_legacy_name(self):
        _, lines = self.run_checker({"naming-exempt": ["Bad Client"]})
        self.assertFalse([line for line in lines if "4.1" in line])

    def test_missing_client_brief_is_flagged(self):
        _, lines = self.run_checker()
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
        _, lines = self.run_checker({"asset-folders": ["Brand"]})
        hits = [line for line in lines if "3.1" in line and "colors" in line]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("expected 'folder-readme-asset'", hits[0])

    def test_a_self_declared_asset_library_needs_no_overlay(self):
        # The bug this guards: an instance built exactly as adopting-acos.md
        # describes has no acos-integrity overlay (the guide never mentions one),
        # and its Brand/README.md — correctly typed folder-readme-asset per the
        # asset template — was flagged as "expected folder-readme-container".
        _, lines = self.run_checker()
        self.assertFalse([line for line in lines if "3.1" in line and "Brand/README.md" in line])

    def test_the_walk_is_reported_even_when_nothing_is_wrong(self):
        checker, lines = self.run_checker()
        self.assertTrue([line for line in lines if line.startswith("✅ 0.4")])
        self.assertGreater(checker.folders_walked, 0)

    def test_repo_child_readme_is_frontmatter_exempt_when_configured(self):
        _, lines = self.run_checker({"repo-child-containers": ["Repos"]})
        self.assertTrue([line for line in lines if line.startswith("✅ 2.5") and "widget" in line])
        self.assertFalse([line for line in lines if line.startswith("❌ 2.5") and "widget" in line])

    def test_repo_child_readme_fails_frontmatter_without_the_exemption(self):
        _, lines = self.run_checker()
        self.assertTrue([line for line in lines if line.startswith("❌ 2.5") and "widget" in line])

    def test_missing_readme_is_a_failure(self):
        (self.tree / "Clients" / "Orphan-Client").mkdir()
        _, lines = self.run_checker()
        self.assertTrue([line for line in lines if "1.4" in line and "Orphan-Client" in line])

    def test_suppress_checks_from_overlay(self):
        _, lines = self.run_checker({"suppress-checks": ["4.1", "3.2"]})
        self.assertFalse([line for line in lines if "4.1" in line or "3.2" in line])

    def test_exclude_folders_from_overlay(self):
        _, lines = self.run_checker({"exclude-folders": ["Clients"]})
        self.assertFalse([line for line in lines if "Bad Client" in line])

    def test_missing_in_scope_folder_fails(self):
        shutil.rmtree(self.tree / "Brand")
        _, lines = self.run_checker()
        self.assertTrue([line for line in lines if line.startswith("❌ 1.2") and "Brand" in line])

    def test_overlay_is_read_from_disk(self):
        write(
            self.root / "overlays" / "acos-integrity.md",
            "# overlay\n\n```acos-config\nasset-folders: [Brand]\nsuppress-checks: [4.1]\n```\n",
        )
        config = aic.InstanceConfig.load(self.root)
        self.assertTrue(config.overlay_loaded)
        self.assertEqual(config.asset_folders, ["Brand"])
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
        found = aic.find_instance_root(self.tree / "Clients" / "Acme-Industries")
        self.assertIsNone(found)  # company-brief.md is not above Clients/
        self.assertEqual(aic.find_instance_root(self.root), self.root)

    def test_main_exit_codes(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(aic.main(["--root", str(self.root)]), 0)
            # widget/README.md has no frontmatter and no exemption configured.
            self.assertEqual(aic.main(["--root", str(self.root), "--strict"]), 1)
            self.assertEqual(aic.main(["--root", str(self.tree / "Clients")]), 1)  # not an instance root


if __name__ == "__main__":
    unittest.main()
