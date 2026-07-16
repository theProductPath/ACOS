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
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "acos-integrity-check.py"

# The script's filename has dashes, so it can't be imported normally.
_spec = importlib.util.spec_from_file_location("acos_integrity_check", SCRIPT_PATH)
aic = importlib.util.module_from_spec(_spec)
sys.modules["acos_integrity_check"] = aic
_spec.loader.exec_module(aic)


class TestNamingIsStructureNotStyle(unittest.TestCase):
    """ACOS governs structure, not style. The framework mandates no letter case."""

    def test_capitalized_folder_names_produce_no_finding(self):
        # The headline of the change: Steven capitalizes deliberately, and the
        # framework's own templates prescribe Clients/, Products/, Brand/. A rule
        # that flags the framework's own names is a rule everyone learns to ignore.
        for name in ["Clients", "Products", "Brand", "Admin", "Research",
                     "Design-System", "Heartland-Paving-Partners", "ACOS", "AIRS"]:
            with self.subTest(name=name):
                self.assertIsNone(aic.naming_violation(name))

    def test_no_case_is_flagged_in_any_direction(self):
        # Lowercase, PascalCase, camelCase, SCREAMING — all taste, none flagged.
        for name in ["clients", "MyFolder", "myFolder", "MYFOLDER", "tPPOS", "Sprout.ai"]:
            with self.subTest(name=name):
                self.assertIsNone(aic.naming_violation(name))

    def test_underscores_inside_a_name_are_harmless(self):
        # An underscore in the middle breaks nothing. (A *leading* underscore is
        # the agent-ignore signal — a different rule, tested in TestAgentIgnore.)
        self.assertIsNone(aic.naming_violation("SME_Brain_Dump_Build-Experiment"))
        self.assertIsNone(aic.naming_violation("my_folder"))

    def test_dots_digits_and_dashes_are_harmless(self):
        for name in ["Sprout.ai", "1H26-AI-Growth", "2026-review", "my--folder", "-leading"]:
            with self.subTest(name=name):
                self.assertIsNone(aic.naming_violation(name))

    def test_spaces_are_flagged_and_the_reason_says_what_breaks(self):
        reason = aic.naming_violation("File Cabinet")
        self.assertIsNotNone(reason)
        self.assertIn("space", reason)
        # The message has to be concrete about the damage, not just "violates rule".
        self.assertIn("shell", reason)
        self.assertIn("URL", reason)
        self.assertIn("markdown", reason)

    def test_other_breaking_characters_are_flagged(self):
        for name, expect in [
            ("Q1#2026", "#"),
            ("what?", "?"),
            ("100%-done", "%"),
            ("a|b", "|"),
            ("wild*card", "*"),
            ("back\\slash", "backslash"),
            ("colon:name", ":"),
        ]:
            with self.subTest(name=name):
                reason = aic.naming_violation(name)
                self.assertIsNotNone(reason, f"{name!r} should be flagged")
                self.assertIn(expect, reason)

    def test_empty_name_is_not_usable(self):
        self.assertIsNotNone(aic.naming_violation(""))
        self.assertIsNotNone(aic.naming_violation(None))


class TestOptionalInstanceNamingStyle(unittest.TestCase):
    """An instance MAY declare a naming policy. The framework ships none."""

    def test_the_framework_default_is_no_style_at_all(self):
        config = aic.InstanceConfig("/tmp/instance")
        self.assertEqual(config.naming_style, aic.NO_NAMING_STYLE)
        # With no declared style, nothing is ever a style violation.
        for name in ["Clients", "my_folder", "MYFOLDER", "sprout.ai"]:
            with self.subTest(name=name):
                self.assertIsNone(aic.style_violation(name, config.naming_style))

    def test_an_instance_can_opt_into_kebab_case(self):
        config = aic.InstanceConfig("/tmp/instance", config={"naming-style": "kebab-case"})
        self.assertIsNone(aic.style_violation("client-work", config.naming_style))
        violation = aic.style_violation("Clients", config.naming_style)
        self.assertIsNotNone(violation)
        self.assertIn("kebab-case", violation)

    def test_an_instance_can_opt_into_capitalized(self):
        config = aic.InstanceConfig("/tmp/instance", config={"naming-style": "capitalized"})
        self.assertIsNone(aic.style_violation("Clients", config.naming_style))
        self.assertIsNotNone(aic.style_violation("clients", config.naming_style))

    def test_an_unknown_style_is_inert_rather_than_crashing(self):
        self.assertIsNone(aic.style_violation("anything", "snake_case"))


class TestKebabHelper(unittest.TestCase):
    """is_kebab_case survives only to back the optional `naming-style: kebab-case`."""

    def test_valid_kebab_case(self):
        for name in ["my-folder", "acme-industries", "brand", "a", "2026-review"]:
            with self.subTest(name=name):
                self.assertTrue(aic.is_kebab_case(name))

    def test_rejects_everything_that_is_not_kebab(self):
        for name in ["MyFolder", "myFolder", "MYFOLDER", "my_folder", "My Folder",
                     "sprout.ai", "my--folder", "-leading", "trailing-", "", None]:
            with self.subTest(name=name):
                self.assertFalse(aic.is_kebab_case(name))


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


SKILL_PATH = REPO_ROOT / "framework" / "skills" / "acos-integrity" / "SKILL.md"


class TestSkillAndScriptSpecifyTheSameChecks(unittest.TestCase):
    """The SKILL must document exactly the checks the script implements.

    The bug this guards is the one that shipped: the SKILL specified ~27 checks
    across nine categories and the script implemented ~16 of them. A spec that
    describes a tool that doesn't exist is the same "documentation that lies"
    failure ACOS was built to prevent — so the two are pinned to each other here,
    and adding a check to one without the other fails the build.
    """

    def skill_checks(self):
        text = SKILL_PATH.read_text(encoding="utf-8")
        return set(re.findall(r"^\*\*Check (\d+\.\d+)", text, re.MULTILINE))

    def test_the_skill_documents_every_check_the_script_implements(self):
        undocumented = aic.CHECK_IDS - self.skill_checks()
        self.assertEqual(undocumented, set(),
                         f"checks in the script with no entry in SKILL.md: {sorted(undocumented)}")

    def test_the_skill_specifies_no_check_the_script_does_not_implement(self):
        aspirational = self.skill_checks() - aic.CHECK_IDS
        self.assertEqual(aspirational, set(),
                         f"checks specified in SKILL.md but not implemented: {sorted(aspirational)}")

    def test_the_deleted_style_checks_stay_deleted(self):
        # Category 7 was markdown style (curly quotes, dividers, title case).
        # ACOS governs structure, not style; policing prose is the same category
        # error as policing letter case. Deleted from the spec, never built.
        text = SKILL_PATH.read_text(encoding="utf-8")
        self.assertNotIn("### Category 7", text)
        self.assertFalse([cid for cid in aic.CHECK_IDS if cid.startswith("7.")])

    def test_every_registry_entry_has_a_title(self):
        for cid, title in aic.CHECK_REGISTRY:
            with self.subTest(check=cid):
                self.assertTrue(title.strip())


class TestTemplateCoverage(unittest.TestCase):
    """Was SKILL check 9.1. It is a property of the framework, not of an instance,
    so it belongs here — in the framework's own test suite — rather than in a
    validator that walks somebody else's tree."""

    TEMPLATE_FOR = {
        "folder-readme-root": "folder-readme-root.md",
        "folder-readme-container": "folder-readme-container.md",
        "folder-readme-item": "folder-readme-item.md",
        "folder-readme-asset": "folder-readme-asset.md",
        "brief-company": "brief-company.md",
        "brief-client": "brief-client.md",
        "brief-stakeholder": "brief-stakeholder.md",
        "manifest-client": "manifest-client.md",
        "dashboard-company": "dashboard-company.md",
    }

    def test_every_pattern_an_instance_can_use_has_a_template(self):
        templates = REPO_ROOT / "framework" / "templates"
        for doc_type, filename in self.TEMPLATE_FOR.items():
            with self.subTest(type=doc_type):
                self.assertTrue((templates / filename).exists(),
                                f"type '{doc_type}' has no template at framework/templates/{filename}")

    def test_the_map_covers_every_scaffoldable_framework_type(self):
        # agent-ignore and progress-checkpoint are framework-internal, not
        # scaffolded into an instance from a template.
        unmapped = aic.FRAMEWORK_TYPES - set(self.TEMPLATE_FOR) - {"agent-ignore", "progress-checkpoint"}
        self.assertEqual(unmapped, set(), f"framework types with no template mapping: {unmapped}")


class TestLinkParsing(unittest.TestCase):
    """Shared by the integrity checker (8.1) and scripts/check-links.py."""

    def test_finds_links_with_line_numbers(self):
        found = list(aic.iter_links("intro\n[a](one.md) and [b](two.md)\n"))
        self.assertEqual(found, [(2, "one.md"), (2, "two.md")])

    def test_skips_fenced_code_blocks(self):
        text = "[real](a.md)\n```\n[fake](b.md)\n```\n[also-real](c.md)\n"
        targets = [t for _, t in aic.iter_links(text)]
        self.assertEqual(targets, ["a.md", "c.md"])

    def test_angle_bracketed_targets_are_unwrapped(self):
        self.assertEqual([t for _, t in aic.iter_links("[x](<a b.md>)\n")], ["a b.md"])

    def test_a_placeholder_target_keeps_its_brackets(self):
        # `<client-name>` is a placeholder, not the angle-bracket link form. If
        # the parser unwraps it, the unresolved placeholder disappears from the
        # report instead of being flagged — and that is the single most likely
        # thing an adopter leaves behind after copying a template.
        self.assertEqual([t for _, t in aic.iter_links("[b](<client-name>/brief.md)\n")],
                         ["<client-name>/brief.md"])

    def test_external_targets_are_recognized(self):
        for target in ["https://example.com", "mailto:a@b.com", "#anchor", ""]:
            with self.subTest(target=target):
                self.assertTrue(aic.is_external_link(target))
                self.assertIsNone(aic.link_target_path(target))

    def test_percent_escapes_are_decoded(self):
        # 'Research/AI Gateways' is a real folder with a real space in it. A link
        # to it is written %20, and the checker has to resolve what's on disk.
        self.assertEqual(aic.link_target_path("Research/AI%20Gateways/README.md"),
                         "Research/AI Gateways/README.md")

    def test_anchors_and_queries_are_stripped(self):
        self.assertEqual(aic.link_target_path("../README.md#house-rules"), "../README.md")

    def test_underscore_files_are_not_underscore_folders(self):
        # agent-ignore is a FOLDER rule (`_*/`). The framework itself prescribes
        # Brand/_principal-review.md and links to it from the client brief.
        self.assertFalse(aic.ACOSIntegrityChecker._points_into_ignored_folder("Brand/_principal-review.md"))
        self.assertTrue(aic.ACOSIntegrityChecker._points_into_ignored_folder("Brand/_archive/old.md"))
        self.assertTrue(aic.ACOSIntegrityChecker._points_into_ignored_folder("../_progress/notes.md"))
        self.assertTrue(aic.ACOSIntegrityChecker._points_into_ignored_folder("_archive/"))


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
        write(tree / "Clients" / "Acme-Industries" / "manifest.md", readme("manifest-client", "Acme"))
        # A badly named client with a missing brief and a bogus status.
        write(tree / "Clients" / "Bad Client" / "README.md", readme("folder-readme-item", "Bad", status="on hold"))
        write(tree / "Clients" / "Bad Client" / "manifest.md", readme("manifest-client", "Bad"))
        # Agent-ignored: must never be walked.
        write(tree / "Clients" / "_archive" / "README.md", readme("nonsense-type", "Archived"))
        write(tree / "Clients" / "_archive" / "MyBadName" / "README.md", "no frontmatter\n")
        # Asset library. Its children are MATERIAL, not OS items: a folder of
        # palette files, a folder of logo images with no README at all, and a
        # nested folder deeper still. None of it is OS structure.
        write(tree / "Brand" / "README.md", readme("folder-readme-asset", "Brand"))
        write(tree / "Brand" / "colors" / "README.md", readme("folder-readme-item", "Colors"))
        write(tree / "Brand" / "logos" / "primary" / "logo.svg", "<svg/>")
        write(tree / "Brand" / "Type Faces" / "notes.txt", "material, not structure")
        # Repo container: children carry codebase READMEs with no frontmatter.
        write(tree / "Repos" / "README.md", readme("folder-readme-container", "Repos"))
        write(tree / "Repos" / "widget" / "README.md", "# widget\n\nA codebase README.\n")

        self.tree = tree

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # The fixture's Repos/widget/README.md is a codebase README with no
    # frontmatter, so it is a 2.5 failure unless the exemption is configured.
    # Tests that assert on failure *counts* start from this clean baseline.
    CLEAN = {"repo-child-containers": ["Repos"]}

    def run_checker(self, overlay_config=None):
        config = aic.InstanceConfig(self.root, config=overlay_config)
        checker = aic.ACOSIntegrityChecker(self.root, config=config)
        checker.run_checks()
        return checker, [line for _, line in checker.report]

    @staticmethod
    def render(checker):
        buf = io.StringIO()
        checker.print_report(stream=buf)
        return buf.getvalue()

    def test_the_clean_baseline_fixture_has_no_failures(self):
        checker, _ = self.run_checker(self.CLEAN)
        self.assertEqual(checker.stats["fail"], 0)

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
        # Capitalized containers and proper-name items are correct, not findings.
        # The one finding is the space in "Bad Client", which genuinely breaks links.
        _, lines = self.run_checker()
        hits = [line for line in lines if "4.1" in line]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("Bad Client", hits[0])
        self.assertIn("space", hits[0])
        # It is a warning, never a failure.
        self.assertTrue(hits[0].startswith("⚠️"))

    def test_a_capitalized_folder_name_produces_no_finding(self):
        # The headline of the case-mandate removal, asserted end-to-end: every
        # container in this fixture is Capitalized and none of them is reported.
        # Match the quoted rel path so "Clients/Bad Client" doesn't count as a
        # finding against "Clients".
        _, lines = self.run_checker()
        for name in ["Clients", "Brand", "Repos", "Clients/Acme-Industries"]:
            with self.subTest(name=name):
                self.assertFalse([line for line in lines if "4.1" in line and f"'{name}'" in line])

    def test_a_lowercase_container_is_also_no_finding(self):
        # ACOS has no opinion on case, in either direction.
        (self.tree / "Clients").rename(self.tree / "vendors")
        readme_path = self.root / "README.md"
        readme_path.write_text(
            readme_path.read_text(encoding="utf-8").replace("| `Clients/` |", "| `vendors/` |"),
            encoding="utf-8",
        )
        _, lines = self.run_checker()
        self.assertFalse([line for line in lines if "4.1" in line and "'vendors'" in line])

    def test_an_instance_declared_naming_style_is_enforced_as_4_2(self):
        # The framework ships no style; an instance may declare one.
        _, lines = self.run_checker({"naming-style": "kebab-case"})
        hits = [line for line in lines if "4.2" in line]
        self.assertTrue(hits)
        self.assertTrue(all(line.startswith("⚠️") for line in hits))
        self.assertTrue([line for line in hits if "Clients" in line])

    def test_no_naming_style_means_check_4_2_never_runs(self):
        _, lines = self.run_checker()
        self.assertFalse([line for line in lines if "4.2" in line])

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

    def test_an_asset_librarys_children_produce_no_findings_at_any_depth(self):
        # THE bug this whole model fixes: Brand/ correctly declared itself an
        # asset library and the checker still demanded READMEs in colors/,
        # logos/, typography/ — folders of palette files and logo images. An
        # asset library's children are material. The walk stops at the library.
        _, lines = self.run_checker()
        joined = "\n".join(lines)
        for child in ["colors", "logos", "primary", "Type Faces"]:
            with self.subTest(child=child):
                self.assertNotIn(child, joined)

    def test_asset_children_are_silent_whether_declared_by_frontmatter_or_overlay(self):
        # Two ways to say "this is an asset library"; both must end the walk.
        for cfg in (None, {"asset-folders": ["Brand"]}):
            with self.subTest(config=cfg):
                _, lines = self.run_checker(cfg)
                self.assertFalse([line for line in lines if "colors" in line])

    def test_a_throwaway_folder_under_an_asset_library_is_not_a_finding(self):
        # The model's sanity check: drop an empty, README-less folder into an
        # asset library and the OS says nothing at all about it.
        baseline, _ = self.run_checker(self.CLEAN)
        (self.tree / "Brand" / "scratch").mkdir()
        checker, lines = self.run_checker(self.CLEAN)
        self.assertFalse([line for line in lines if "scratch" in line])
        self.assertEqual(checker.stats["fail"], 0)
        # The throwaway folder adds no finding of any severity.
        self.assertEqual(checker.stats["warning"], baseline.stats["warning"])

    def test_a_self_declared_asset_library_needs_no_overlay(self):
        # An instance built exactly as adopting-acos.md describes has no
        # acos-integrity overlay (the guide never mentions one), and its
        # Brand/README.md — correctly typed folder-readme-asset per the asset
        # template — must not be flagged as "expected folder-readme-container".
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

    def test_a_container_child_without_a_readme_is_a_warning_not_a_failure(self):
        # Steven's principle: "Just because a folder exists at the sibling level
        # doesn't mean it's part of the operating system. If it doesn't have a
        # README and it just happens to be living in the same part of the
        # hierarchy, we should not assume that's an error."
        (self.tree / "Clients" / "Orphan-Client").mkdir()
        checker, lines = self.run_checker(self.CLEAN)
        hits = [line for line in lines if "1.4" in line and "Orphan-Client" in line]
        self.assertEqual(len(hits), 1, hits)
        self.assertTrue(hits[0].startswith("⚠️"), hits[0])
        self.assertFalse(hits[0].startswith("❌"))
        self.assertEqual(checker.stats["fail"], 0)

    def test_the_missing_readme_warning_is_phrased_as_information_with_a_way_out(self):
        (self.tree / "Clients" / "Orphan-Client").mkdir()
        _, lines = self.run_checker()
        message = [line for line in lines if "Orphan-Client" in line][0]
        self.assertIn("not visible to the OS", message)
        # It must name the ways to change it, all of them legitimate.
        self.assertIn("give it a README", message)
        self.assertIn("folder-readme-asset", message)
        self.assertIn("_", message)

    def test_a_readme_less_container_child_is_not_walked_for_client_checks(self):
        # It isn't an OS item, so it doesn't owe the OS a brief or a manifest.
        (self.tree / "Clients" / "Orphan-Client").mkdir()
        _, lines = self.run_checker()
        self.assertFalse([line for line in lines
                          if ("2.2" in line or "2.3" in line) and "Orphan-Client" in line])

    def test_a_folder_on_the_roster_with_no_readme_is_a_failure(self):
        # The roster IS the opt-in. A folder that opted in and then supplied no
        # front door is a real failure: nothing declares what it is.
        (self.tree / "Vault").mkdir()
        readme_path = self.root / "README.md"
        readme_path.write_text(
            readme_path.read_text(encoding="utf-8").replace(
                "| `Repos/` | Codebases. |", "| `Repos/` | Codebases. |\n| `Vault/` | No README. |"),
            encoding="utf-8",
        )
        checker, lines = self.run_checker(self.CLEAN)
        hits = [line for line in lines if line.startswith("❌ 1.2") and "Vault" in line]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("folder map", hits[0])
        self.assertEqual(checker.stats["fail"], 1)

    def test_a_folder_not_on_the_roster_is_silently_out_of_the_os(self):
        # The allowlist: membership is opt-in. A sibling folder nobody listed is
        # not in the OS — no finding, no mention, no suggestion to add it. This
        # is what replaces the rotting denylist: there is nothing to maintain.
        write(self.tree / "Events" / "some-file.txt", "not in the OS")
        (self.tree / "Roam-Export").mkdir()
        checker, lines = self.run_checker(self.CLEAN)
        joined = "\n".join(lines)
        self.assertNotIn("Events", joined)
        self.assertNotIn("Roam-Export", joined)
        self.assertEqual(checker.stats["fail"], 0)

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

    # --- The counter: checks attempted, not findings emitted ---

    def test_the_report_counts_checks_attempted_not_findings(self):
        # The bug: "Checks run: 5" on a clean instance, because the counter
        # counted findings. A conformant instance emits few findings and runs
        # every check; a broken walk emits few findings and runs none. The report
        # has to distinguish them.
        checker, _ = self.run_checker(self.CLEAN)
        report = self.render(checker)
        self.assertIn("**Checks attempted:**", report)
        self.assertNotIn("**Checks run:**", report)
        self.assertGreaterEqual(len(checker.attempted), 15)
        self.assertGreater(len(checker.attempted), sum(checker.stats.values()) - len(checker.attempted))
        self.assertIn(f"of {len(aic.CHECK_REGISTRY)}", report)

    def test_a_check_that_ran_silently_is_counted_as_attempted(self):
        # 4.1 finds nothing in a clean tree. It still ran, and must not be
        # reported as "not run" — that would be the same lie in the other direction.
        (self.tree / "Clients" / "Bad Client").rename(self.tree / "Clients" / "Good-Client")
        checker, _ = self.run_checker(self.CLEAN)
        self.assertIn("4.1", checker.attempted)
        self.assertNotIn("4.1", checker.not_run)

    def test_checks_with_nothing_to_run_against_are_named_with_a_reason(self):
        checker, _ = self.run_checker(self.CLEAN)
        report = self.render(checker)
        self.assertIn("**Not run:**", report)
        # This instance declares no naming-style, so 4.2 never runs — and the
        # report says why rather than leaving a silent gap.
        self.assertIn("4.2", checker.not_run)
        self.assertIn("naming-style", checker.not_run["4.2"])

    def test_suppressed_checks_are_named_in_the_report(self):
        checker, _ = self.run_checker({**self.CLEAN, "suppress-checks": ["4.1"]})
        report = self.render(checker)
        self.assertIn("Suppressed by the overlay", report)
        self.assertNotIn("4.1", checker.attempted)

    def test_a_walk_that_inspects_nothing_is_never_a_pass(self):
        # THE failure mode: reformat the folder map so it stops parsing, and the
        # old checker walked nothing, found nothing, and reported a cheerful pass.
        readme_path = self.root / "README.md"
        readme_path.write_text(
            readme("folder-readme-root", "Acme OS") + "\n## Folders\n\nNo map here.\n",
            encoding="utf-8",
        )
        checker, lines = self.run_checker(self.CLEAN)
        report = self.render(checker)
        self.assertEqual(checker.folders_walked, 0)
        self.assertGreater(checker.stats["fail"], 0)
        self.assertIn("NOTHING WAS WALKED — THIS IS NOT A PASS", report)
        self.assertTrue([line for line in lines if line.startswith("❌ 0.4")])

    def test_a_blind_run_exits_non_zero_even_without_strict(self):
        readme_path = self.root / "README.md"
        readme_path.write_text(readme("folder-readme-root", "Acme OS") + "\n# no map\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(aic.main(["--root", str(self.root)]), 1)

    # --- 1.3: declared type vs position ---

    def test_a_container_typed_as_an_item_is_a_1_3_warning(self):
        write(self.tree / "Clients" / "README.md", readme("folder-readme-item", "Clients"))
        _, lines = self.run_checker(self.CLEAN)
        hits = [line for line in lines if line.startswith("⚠️ 1.3") and "Clients/README.md" in line]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("expected 'folder-readme-container'", hits[0])

    def test_an_unknown_type_is_3_1_not_1_3(self):
        write(self.tree / "Clients" / "README.md", readme("folder-readme-contianer", "Clients"))
        _, lines = self.run_checker(self.CLEAN)
        self.assertTrue([line for line in lines if line.startswith("⚠️ 3.1") and "Clients/README.md" in line])
        self.assertFalse([line for line in lines if line.startswith("⚠️ 1.3") and "Clients/README.md" in line])

    # --- 3.4: staleness ---

    def test_a_stale_active_document_is_a_warning(self):
        old = (datetime.now() - timedelta(days=200)).strftime("%Y-%m-%d")
        write(self.tree / "Clients" / "Acme-Industries" / "brief.md",
              f"---\ntype: brief-client\nstatus: active\nlast-updated: {old}\n"
              "maintainer: Test\npurpose: Acme.\n---\n\n# Acme\n")
        checker, lines = self.run_checker(self.CLEAN)
        hits = [line for line in lines if "3.4" in line]
        self.assertEqual(len(hits), 1, hits)
        self.assertTrue(hits[0].startswith("⚠️"))
        self.assertIn("200 days ago", hits[0])
        self.assertEqual(checker.stats["fail"], 0)  # never a failure

    def test_an_honest_status_is_not_stale(self):
        # `wrapped`, `archived`, `paused` — a finished thing is supposed to sit still.
        old = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
        write(self.tree / "Clients" / "Acme-Industries" / "brief.md",
              f"---\ntype: brief-client\nstatus: wrapped\nlast-updated: {old}\n"
              "maintainer: Test\npurpose: Acme.\n---\n\n# Acme\n")
        _, lines = self.run_checker(self.CLEAN)
        self.assertFalse([line for line in lines if "3.4" in line])

    def test_staleness_days_zero_turns_the_check_off(self):
        old = (datetime.now() - timedelta(days=999)).strftime("%Y-%m-%d")
        write(self.tree / "Clients" / "Acme-Industries" / "brief.md",
              f"---\ntype: brief-client\nstatus: active\nlast-updated: {old}\n"
              "maintainer: Test\npurpose: Acme.\n---\n\n# Acme\n")
        checker, lines = self.run_checker({**self.CLEAN, "staleness-days": "0"})
        self.assertFalse([line for line in lines if "3.4" in line])
        self.assertIn("3.4", checker.not_run)

    def test_the_staleness_window_is_configurable(self):
        old = (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")
        write(self.tree / "Clients" / "Acme-Industries" / "brief.md",
              f"---\ntype: brief-client\nstatus: active\nlast-updated: {old}\n"
              "maintainer: Test\npurpose: Acme.\n---\n\n# Acme\n")
        _, lenient = self.run_checker({**self.CLEAN, "staleness-days": "365"})
        self.assertFalse([line for line in lenient if "3.4" in line])
        _, strict = self.run_checker({**self.CLEAN, "staleness-days": "30"})
        self.assertTrue([line for line in strict if "3.4" in line])

    # --- 6.1 / 6.2: overlays ---

    def overlay(self, name, body="", type_="skill-overlay", skill=None):
        write(self.root / "overlays" / f"{name}.md",
              f"---\ntype: {type_}\nskill: {skill or name}\ninstance: acme-os\n"
              f"last-updated: 2026-07-12\nmaintainer: Test\npurpose: Overlay.\n---\n\n# {name}\n{body}")

    def test_an_overlay_with_a_matching_framework_skill_is_silent(self):
        self.overlay("acos-integrity")
        checker, lines = self.run_checker(self.CLEAN)
        self.assertFalse([line for line in lines if line.startswith("⚠️ 6.")])
        self.assertIn("6.1", checker.attempted)
        self.assertIn("6.2", checker.attempted)

    def test_an_orphaned_overlay_is_flagged(self):
        # Dead configuration: nothing will ever read it, and the day someone edits
        # it expecting an effect is the day the instance lies to its owner.
        self.overlay("notion-sync")
        _, lines = self.run_checker(self.CLEAN)
        hits = [line for line in lines if line.startswith("⚠️ 6.1")]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("notion-sync", hits[0])

    def test_an_overlay_without_frontmatter_fails_6_2(self):
        write(self.root / "overlays" / "acos-integrity.md", "# overlay\n\nno frontmatter\n")
        checker, lines = self.run_checker(self.CLEAN)
        self.assertTrue([line for line in lines if line.startswith("❌ 6.2")])
        self.assertGreater(checker.stats["fail"], 0)

    def test_an_overlay_missing_required_fields_warns(self):
        write(self.root / "overlays" / "acos-integrity.md",
              "---\ntype: skill-overlay\nskill: acos-integrity\n---\n\n# overlay\n")
        _, lines = self.run_checker(self.CLEAN)
        hits = [line for line in lines if line.startswith("⚠️ 6.2")]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("instance", hits[0])

    def test_overlay_checks_do_not_run_without_an_overlays_directory(self):
        checker, _ = self.run_checker(self.CLEAN)
        self.assertIn("6.1", checker.not_run)
        self.assertIn("6.2", checker.not_run)

    # --- 8.1: internal links resolve (the one that matters most) ---

    def test_a_dead_internal_link_is_reported_with_file_and_line(self):
        # The rot ACOS exists to prevent: the tree looks navigable, an agent
        # follows a pointer, the pointer goes nowhere. Two of these survived in
        # the reference instance's own root README because nothing looked.
        write(self.tree / "Clients" / "README.md",
              readme("folder-readme-container", "Clients")
              + "\n- [Acme](Acme-Industries/README.md)\n- [Ghost](Ghost-Corp/README.md)\n")
        checker, lines = self.run_checker(self.CLEAN)
        hits = [line for line in lines if line.startswith("⚠️ 8.1")]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("Ghost-Corp/README.md", hits[0])
        self.assertRegex(hits[0], r"README\.md:\d+ ->")  # file and line
        self.assertIn("does not exist", hits[0])
        self.assertEqual(checker.stats["fail"], 0)  # a broken link is never a fail

    def test_links_that_resolve_produce_no_finding_and_a_pass_line(self):
        write(self.tree / "Clients" / "README.md",
              readme("folder-readme-container", "Clients") + "\n- [Acme](Acme-Industries/README.md)\n")
        _, lines = self.run_checker(self.CLEAN)
        self.assertFalse([line for line in lines if line.startswith("⚠️ 8.1")])
        self.assertTrue([line for line in lines if line.startswith("✅ 8.1")])

    def test_external_links_and_anchors_are_not_checked(self):
        write(self.tree / "Clients" / "README.md",
              readme("folder-readme-container", "Clients")
              + "\n[web](https://example.com/nope)\n[mail](mailto:a@b.com)\n[anchor](#somewhere)\n")
        _, lines = self.run_checker(self.CLEAN)
        self.assertFalse([line for line in lines if line.startswith("⚠️ 8.1")])

    def test_links_inside_code_fences_are_not_checked(self):
        write(self.tree / "Clients" / "README.md",
              readme("folder-readme-container", "Clients")
              + "\n```\n[example](Not-Real/README.md)\n```\n")
        _, lines = self.run_checker(self.CLEAN)
        self.assertFalse([line for line in lines if line.startswith("⚠️ 8.1")])

    def test_a_percent_escaped_link_to_a_real_folder_resolves(self):
        (self.tree / "Clients" / "Bad Client" / "docs").mkdir()
        write(self.tree / "Clients" / "Bad Client" / "docs" / "notes.md", "# notes\n")
        write(self.tree / "Clients" / "README.md",
              readme("folder-readme-container", "Clients")
              + "\n[notes](Bad%20Client/docs/notes.md)\n")
        _, lines = self.run_checker(self.CLEAN)
        self.assertFalse([line for line in lines if line.startswith("⚠️ 8.1")])

    def test_an_unresolved_template_placeholder_is_reported(self):
        write(self.tree / "Clients" / "Acme-Industries" / "README.md",
              readme("folder-readme-item", "Acme") + "\n[brief](<client-name>/brief.md)\n")
        _, lines = self.run_checker(self.CLEAN)
        hits = [line for line in lines if line.startswith("⚠️ 8.1")]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("placeholder", hits[0])

    def test_links_are_not_followed_into_an_asset_library(self):
        # The walk stops at Brand/, so nothing inside it is read — including its
        # children's links. An asset library's material is nobody's business.
        write(self.tree / "Brand" / "colors" / "README.md",
              readme("folder-readme-item", "Colors") + "\n[gone](../../Nowhere/README.md)\n")
        _, lines = self.run_checker(self.CLEAN)
        self.assertFalse([line for line in lines if "Nowhere" in line])

    def test_links_are_not_followed_into_agent_ignored_folders(self):
        write(self.tree / "Clients" / "_archive" / "old" / "README.md",
              readme("folder-readme-item", "Old") + "\n[gone](../../Nowhere/README.md)\n")
        _, lines = self.run_checker(self.CLEAN)
        self.assertFalse([line for line in lines if "Nowhere" in line])

    # --- 5.1: no references into agent-ignored folders ---

    def test_a_link_into_an_underscore_folder_is_flagged(self):
        write(self.tree / "Clients" / "Acme-Industries" / "README.md",
              readme("folder-readme-item", "Acme") + "\n[old](_archive/2025-notes.md)\n")
        _, lines = self.run_checker(self.CLEAN)
        hits = [line for line in lines if line.startswith("⚠️ 5.1")]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("_archive", hits[0])

    def test_an_underscore_prefixed_file_is_not_flagged(self):
        # agent-ignore is a FOLDER rule. client-brand-capture deliberately writes
        # Brand/_principal-review.md and brief-client.md deliberately links to it.
        # Flagging the framework's own prescribed output is how a validator
        # teaches everyone to ignore it.
        write(self.tree / "Clients" / "Acme-Industries" / "Brand" / "_principal-review.md", "# review\n")
        write(self.tree / "Clients" / "Acme-Industries" / "brief.md",
              readme("brief-client", "Acme") + "\n[pending](Brand/_principal-review.md)\n")
        _, lines = self.run_checker(self.CLEAN)
        self.assertFalse([line for line in lines if line.startswith("⚠️ 5.1")])
        self.assertFalse([line for line in lines if line.startswith("⚠️ 8.1")])


if __name__ == "__main__":
    unittest.main()
