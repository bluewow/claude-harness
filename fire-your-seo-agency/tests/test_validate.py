"""Unit tests for the repository checks in tools/validate.py.

Each case builds a throwaway repository in a temp directory, so every check is
exercised against real files without touching the working tree.
"""

from __future__ import annotations

import contextlib
import io
import json
import json as json_module
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import optimize_assets, validate  # noqa: E402

SKILL_NAME = "demo-skill"
PREVIEW = "assets/social-preview.png"

SKILL_TEMPLATE = """---
name: {name}
description: {description}
---

# Demo skill

Body copy for the demo skill.
"""

REFERENCE = """# Demo reference

## 1. First section

- [ ] a checkbox

| a | b |
|---|---|
| 1 | 2 |

## 2. Second section

```bash
echo hello
```
"""

README_EN = """# Demo

[한국어](./README.ko.md)

![preview](./assets/social-preview.png)

## References

- seo.md
"""

README_KO = """# Demo

[English](./README.md)

![preview](./assets/social-preview.png)

## 구조

- seo.md
"""


def chunk(tag: bytes, payload: bytes) -> bytes:
    body = tag + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def png_bytes(width: int = 1280, height: int = 640) -> bytes:
    """A valid PNG signature plus IHDR, which is all the dimension check reads."""
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IEND", b"")
    )


def plugin_manifest(**overrides) -> dict:
    data = {
        "name": SKILL_NAME,
        "description": "A demo skill.",
        "version": "1.2.0",
        "author": {"name": "tester"},
        "homepage": "https://example.com/demo",
        "license": "MIT",
        "keywords": ["demo"],
    }
    data.update(overrides)
    return data


def marketplace_manifest(**overrides) -> dict:
    data = {
        "name": SKILL_NAME,
        "description": "A demo marketplace.",
        "owner": {"name": "tester"},
        "plugins": [
            {
                "name": SKILL_NAME,
                "source": "./",
                "description": "A demo plugin.",
                "version": "1.2.0",
            }
        ],
    }
    data.update(overrides)
    return data


class Fixture:
    """A minimal but complete repository that passes every check."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.write("SKILL.md", SKILL_TEMPLATE.format(name=SKILL_NAME, description="A demo skill for tests."))
        self.write_json(".claude-plugin/plugin.json", plugin_manifest())
        self.write_json(".claude-plugin/marketplace.json", marketplace_manifest())
        self.write("LICENSE", "MIT License\n\nCopyright (c) 2026 tester\n")
        self.write("CHANGELOG.md", "# Changelog\n\n## 1.2.0\n\n- thing\n")
        self.write("README.md", README_EN)
        self.write("README.ko.md", README_KO)
        self.write("references/seo.md", REFERENCE)
        self.write("references/en/seo.md", REFERENCE)
        self.write_bytes(PREVIEW, png_bytes())

    def path(self, rel: str) -> Path:
        return self.root / rel

    def write(self, rel: str, text: str) -> None:
        target = self.path(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def write_bytes(self, rel: str, payload: bytes) -> None:
        target = self.path(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)

    def write_json(self, rel: str, data) -> None:
        self.write(rel, json_module.dumps(data, ensure_ascii=False, indent=2))

    def read_json(self, rel: str):
        return json_module.loads(self.path(rel).read_text(encoding="utf-8"))

    def remove(self, rel: str) -> None:
        self.path(rel).unlink()


class ValidatorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.fixture = Fixture(self.root)

    def report(self) -> validate.Report:
        return validate.validate(self.root)

    def failures(self) -> list:
        return self.report().failures()

    def failed_checks(self) -> list:
        return sorted({finding.check for finding in self.failures()})

    def assertFails(self, check: str) -> None:
        found = self.failed_checks()
        self.assertIn(check, found, "expected %s among %s" % (check, found))

    def assertClean(self) -> None:
        self.assertEqual([f.check for f in self.failures()], [])

    def run_cli(self, *args) -> tuple:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = validate.main(["--root", str(self.root)] + list(args))
        return code, stream.getvalue()


class TestSkillFrontmatter(ValidatorTestCase):
    def test_complete_repository_passes(self) -> None:
        self.assertClean()

    def test_missing_skill_md(self) -> None:
        self.fixture.remove("SKILL.md")
        self.assertFails("skill.frontmatter")

    def test_missing_frontmatter_block(self) -> None:
        self.fixture.write("SKILL.md", "# Demo\n\nbody\n")
        self.assertFails("skill.frontmatter")

    def test_unterminated_frontmatter(self) -> None:
        self.fixture.write("SKILL.md", "---\nname: demo-skill\ndescription: x\n\n# Demo\n")
        self.assertFails("skill.frontmatter")

    def test_empty_frontmatter_values(self) -> None:
        self.fixture.write("SKILL.md", "---\nname:\ndescription:\n---\n\n# Demo\n")
        self.assertFails("skill.frontmatter")

    def test_name_must_be_kebab_case(self) -> None:
        self.fixture.write("SKILL.md", SKILL_TEMPLATE.format(name="Demo_Skill", description="x"))
        self.assertFails("skill.frontmatter")

    def test_name_must_fit_the_sixty_four_character_limit(self) -> None:
        self.fixture.write("SKILL.md", SKILL_TEMPLATE.format(name="a" * 65, description="x"))
        self.assertFails("skill.frontmatter")

    def test_description_must_fit_the_metadata_limit(self) -> None:
        self.fixture.write("SKILL.md", SKILL_TEMPLATE.format(name=SKILL_NAME, description="x" * 1025))
        self.assertFails("skill.frontmatter")

    def test_description_must_stay_on_one_line(self) -> None:
        self.fixture.write("SKILL.md", "---\nname: demo-skill\ndescription: first\n  continued\n---\n\n# Demo\n")
        self.assertFails("skill.frontmatter")

    def test_duplicate_keys_are_rejected(self) -> None:
        self.fixture.write("SKILL.md", "---\nname: demo-skill\nname: demo-skill\ndescription: x\n---\n\n# Demo\n")
        self.assertFails("skill.frontmatter")

    def test_body_must_not_be_empty(self) -> None:
        self.fixture.write("SKILL.md", "---\nname: demo-skill\ndescription: x\n---\n")
        self.assertFails("skill.frontmatter")

    def test_invalid_utf8_skill_md_is_reported_not_raised(self) -> None:
        (self.root / "SKILL.md").write_bytes(b"\xff\xfe\x00broken")
        self.assertFails("skill.frontmatter")

    def test_unknown_frontmatter_key_warns_without_failing(self) -> None:
        self.fixture.write("SKILL.md", "---\nname: demo-skill\ndescription: x\nsurprise: 1\n---\n\n# Demo\n")
        report = self.report()
        self.assertEqual(report.failures(), [])
        self.assertTrue(report.warnings())
        code, _ = self.run_cli()
        self.assertEqual(code, 0)
        strict_code, _ = self.run_cli("--strict")
        self.assertEqual(strict_code, 1)


class TestManifests(ValidatorTestCase):
    def test_plugin_json_must_be_valid_json(self) -> None:
        self.fixture.write(".claude-plugin/plugin.json", "{not json")
        self.assertFails("manifest.plugin")

    def test_plugin_json_must_be_an_object(self) -> None:
        self.fixture.write(".claude-plugin/plugin.json", "[]")
        self.assertFails("manifest.plugin")

    def test_plugin_json_must_exist(self) -> None:
        self.fixture.remove(".claude-plugin/plugin.json")
        self.assertFails("manifest.plugin")

    def test_plugin_requires_every_documented_key(self) -> None:
        for key in ("name", "description", "version", "license"):
            with self.subTest(key=key):
                data = plugin_manifest()
                del data[key]
                self.fixture.write_json(".claude-plugin/plugin.json", data)
                self.assertFails("manifest.plugin")
        self.fixture.write_json(".claude-plugin/plugin.json", plugin_manifest())
        self.assertClean()

    def test_plugin_version_must_be_semver(self) -> None:
        self.fixture.write_json(".claude-plugin/plugin.json", plugin_manifest(version="1.2"))
        self.assertFails("manifest.plugin")

    def test_plugin_name_must_match_the_skill_name(self) -> None:
        self.fixture.write_json(".claude-plugin/plugin.json", plugin_manifest(name="something-else"))
        self.assertFails("manifest.plugin")

    def test_plugin_author_name_is_required(self) -> None:
        self.fixture.write_json(".claude-plugin/plugin.json", plugin_manifest(author={"email": "a@b.c"}))
        self.assertFails("manifest.plugin")

    def test_plugin_homepage_must_be_https(self) -> None:
        self.fixture.write_json(".claude-plugin/plugin.json", plugin_manifest(homepage="http://example.com"))
        self.assertFails("manifest.plugin")

    def test_plugin_keywords_must_be_a_non_empty_list_of_strings(self) -> None:
        for value in ([], "demo", [""]):
            with self.subTest(value=value):
                self.fixture.write_json(".claude-plugin/plugin.json", plugin_manifest(keywords=value))
                self.assertFails("manifest.plugin")

    def test_marketplace_version_must_match_the_plugin(self) -> None:
        data = marketplace_manifest()
        data["plugins"][0]["version"] = "1.1.0"
        self.fixture.write_json(".claude-plugin/marketplace.json", data)
        self.assertFails("manifest.marketplace")

    def test_marketplace_requires_the_owner_name(self) -> None:
        data = marketplace_manifest()
        del data["owner"]
        self.fixture.write_json(".claude-plugin/marketplace.json", data)
        self.assertFails("manifest.marketplace")

    def test_marketplace_requires_at_least_one_entry(self) -> None:
        self.fixture.write_json(".claude-plugin/marketplace.json", marketplace_manifest(plugins=[]))
        self.assertFails("manifest.marketplace")

    def test_marketplace_entry_requires_every_key(self) -> None:
        for key in ("name", "source", "description", "version"):
            with self.subTest(key=key):
                data = marketplace_manifest()
                del data["plugins"][0][key]
                self.fixture.write_json(".claude-plugin/marketplace.json", data)
                self.assertFails("manifest.marketplace")
        self.fixture.write_json(".claude-plugin/marketplace.json", marketplace_manifest())
        self.assertClean()

    def test_marketplace_source_must_exist(self) -> None:
        data = marketplace_manifest()
        data["plugins"][0]["source"] = "./nowhere/"
        self.fixture.write_json(".claude-plugin/marketplace.json", data)
        self.assertFails("manifest.marketplace")

    def test_marketplace_source_must_not_escape_the_repository(self) -> None:
        data = marketplace_manifest()
        data["plugins"][0]["source"] = "../outside"
        self.fixture.write_json(".claude-plugin/marketplace.json", data)
        self.assertFails("manifest.marketplace")

    def test_marketplace_source_must_not_be_absolute(self) -> None:
        data = marketplace_manifest()
        data["plugins"][0]["source"] = "/etc"
        self.fixture.write_json(".claude-plugin/marketplace.json", data)
        self.assertFails("manifest.marketplace")

    def test_marketplace_name_must_match_the_skill_name(self) -> None:
        self.fixture.write_json(".claude-plugin/marketplace.json", marketplace_manifest(name="something-else"))
        self.assertFails("manifest.marketplace")


class TestLinks(ValidatorTestCase):
    def test_broken_relative_link(self) -> None:
        self.fixture.write("README.md", README_EN + "\n[missing](./nope.md)\n")
        self.assertFails("docs.links")

    def test_link_escaping_the_repository(self) -> None:
        self.fixture.write("README.md", README_EN + "\n[up](../outside.md)\n")
        self.assertFails("docs.links")

    def test_absolute_target_is_rejected(self) -> None:
        self.fixture.write("README.md", README_EN + "\n[abs](/etc/hosts)\n")
        self.assertFails("docs.links")

    def test_empty_target_is_rejected(self) -> None:
        self.fixture.write("README.md", README_EN + "\n[empty]()\n")
        self.assertFails("docs.links")

    def test_dangling_anchor(self) -> None:
        self.fixture.write("README.md", README_EN + "\n[jump](./references/seo.md#9-nope)\n")
        self.assertFails("docs.links")

    def test_valid_anchor_passes(self) -> None:
        self.fixture.write("README.md", README_EN + "\n[jump](./references/seo.md#1-first-section)\n")
        self.assertClean()

    def test_anchors_inside_code_fences_are_not_headings(self) -> None:
        self.fixture.write("references/seo.md", REFERENCE + "\n```\n# not a heading\n```\n")
        self.fixture.write("references/en/seo.md", REFERENCE + "\n```\n# not a heading\n```\n")
        self.fixture.write("README.md", README_EN + "\n[jump](./references/seo.md#not-a-heading)\n")
        self.assertFails("docs.links")

    def test_external_links_are_ignored(self) -> None:
        self.fixture.write("README.md", README_EN + "\n[site](https://example.com/nowhere)\n[mail](mailto:a@b.c)\n")
        self.assertClean()

    def test_dangling_reference_mention(self) -> None:
        self.fixture.write("README.md", README_EN + "\nsee `references/gone.md`\n")
        self.assertFails("docs.links")

    def test_project_relative_paths_are_not_repository_paths(self) -> None:
        self.fixture.write("README.md", README_EN + "\nsee `content/backlog.md` and `llms.txt`\n")
        self.assertClean()

    def test_invalid_utf8_markdown_is_reported_not_raised(self) -> None:
        (self.root / "notes.md").write_bytes(b"\xff\xfe\x00broken")
        self.assertFails("docs.links")


class TestReferenceParity(ValidatorTestCase):
    def test_missing_english_mirror(self) -> None:
        self.fixture.remove("references/en/seo.md")
        self.assertFails("docs.references")

    def test_extra_english_mirror(self) -> None:
        self.fixture.write("references/en/extra.md", REFERENCE)
        self.assertFails("docs.references")

    def test_structural_drift_is_detected(self) -> None:
        self.fixture.write("references/en/seo.md", REFERENCE.replace("## 2. Second section\n", ""))
        self.assertFails("docs.references")

    def test_section_numbering_drift_is_detected(self) -> None:
        self.fixture.write("references/en/seo.md", REFERENCE.replace("## 2. Second section", "## 3. Second section"))
        self.assertFails("docs.references")

    def test_table_drift_is_detected(self) -> None:
        self.fixture.write("references/en/seo.md", REFERENCE.replace("| 1 | 2 |", "| 1 | 2 |\n| 3 | 4 |"))
        self.assertFails("docs.references")

    def test_missing_references_directory(self) -> None:
        self.fixture.remove("references/seo.md")
        self.fixture.remove("references/en/seo.md")
        self.fixture.path("references/en").rmdir()
        self.fixture.path("references").rmdir()
        self.assertFails("docs.references")

    def test_empty_references_directory(self) -> None:
        self.fixture.remove("references/seo.md")
        self.fixture.remove("references/en/seo.md")
        self.assertFails("docs.references")

    def test_invalid_utf8_reference_is_reported_not_raised(self) -> None:
        (self.root / "references" / "seo.md").write_bytes(b"\xff\xfe")
        self.assertFails("docs.references")


class TestAssets(ValidatorTestCase):
    def test_wrong_preview_dimensions(self) -> None:
        self.fixture.write_bytes(PREVIEW, png_bytes(1200, 630))
        self.assertFails("assets.budget")

    def test_missing_preview(self) -> None:
        self.fixture.remove(PREVIEW)
        self.assertFails("assets.budget")

    def test_preview_must_be_a_png(self) -> None:
        self.fixture.write_bytes(PREVIEW, b"GIF89a-not-a-png")
        self.assertFails("assets.budget")

    def test_preview_over_the_byte_budget(self) -> None:
        self.fixture.write_bytes(PREVIEW, png_bytes() + b"\x00" * 1_300_000)
        self.assertFails("assets.budget")

    def test_oversized_file_is_reported(self) -> None:
        self.fixture.write_bytes("references/big.bin", b"\x00" * 2_100_000)
        self.assertFails("assets.budget")


class TestLegalAndRelease(ValidatorTestCase):
    def test_missing_license(self) -> None:
        self.fixture.remove("LICENSE")
        self.assertFails("legal.license")

    def test_non_mit_license(self) -> None:
        self.fixture.write("LICENSE", "Apache License\nVersion 2.0\n")
        self.assertFails("legal.license")

    def test_license_without_a_copyright_line(self) -> None:
        self.fixture.write("LICENSE", "MIT License\n\nPermission is hereby granted.\n")
        self.assertFails("legal.license")

    def test_manifest_license_must_match_the_license_file(self) -> None:
        self.fixture.write_json(".claude-plugin/plugin.json", plugin_manifest(license="Apache-2.0"))
        self.assertFails("legal.license")

    def test_missing_changelog(self) -> None:
        self.fixture.remove("CHANGELOG.md")
        self.assertFails("release.changelog")

    def test_changelog_without_version_headings(self) -> None:
        self.fixture.write("CHANGELOG.md", "# Changelog\n\nnothing yet\n")
        self.assertFails("release.changelog")

    def test_changelog_top_entry_must_match_the_manifest_version(self) -> None:
        self.fixture.write("CHANGELOG.md", "# Changelog\n\n## 1.1.0\n\n- old\n")
        self.assertFails("release.changelog")

    def test_unreleased_section_is_allowed_above_the_latest_version(self) -> None:
        self.fixture.write("CHANGELOG.md", "# Changelog\n\n## Unreleased\n\n- work\n\n## 1.2.0\n\n- thing\n")
        self.assertClean()


class TestSecrets(ValidatorTestCase):
    def test_aws_access_key_is_detected(self) -> None:
        self.fixture.write("notes.md", "key AKIA" + "Q" * 16 + "\n")
        self.assertFails("security.secrets")

    def test_github_token_is_detected(self) -> None:
        self.fixture.write("notes.md", "token ghp_" + "a" * 40 + "\n")
        self.assertFails("security.secrets")

    def test_private_key_block_is_detected(self) -> None:
        self.fixture.write("notes.md", "-----BEGIN " + "RSA PRIVATE KEY-----\n")
        self.assertFails("security.secrets")

    def test_inline_client_secret_is_detected(self) -> None:
        self.fixture.write("notes.md", "client_secret = " + "s" * 32 + "\n")
        self.assertFails("security.secrets")

    def test_clean_repository_reports_no_matches(self) -> None:
        check = [f for f in self.report().findings if f.check == "security.secrets"][0]
        self.assertTrue(check.ok)
        self.assertIn("0 matches", check.detail)


class TestCommandLine(ValidatorTestCase):
    def test_exit_code_is_zero_when_clean(self) -> None:
        code, output = self.run_cli()
        self.assertEqual(code, 0)
        self.assertIn("0 failed", output)

    def test_exit_code_is_one_when_failing(self) -> None:
        self.fixture.remove("CHANGELOG.md")
        code, output = self.run_cli()
        self.assertEqual(code, 1)
        self.assertIn("FAIL", output)

    def test_json_report_shape(self) -> None:
        code, output = self.run_cli("--json")
        self.assertEqual(code, 0)
        payload = json_module.loads(output)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["failed"], 0)
        self.assertEqual(payload["checked"], len(payload["findings"]))
        self.assertEqual(payload["root"], str(self.root.resolve()))
        for item in payload["findings"]:
            self.assertLessEqual({"check", "level", "detail"}, set(item))

    def test_json_report_redacts_secret_values(self) -> None:
        secret = "AKIA" + "Q" * 16
        self.fixture.write("notes.md", "key " + secret + "\n")
        _, output = self.run_cli("--json")
        self.assertNotIn(secret, output)
        self.assertIn("security.secrets", output)

    def test_missing_root_returns_two(self) -> None:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
            code = validate.main(["--root", str(self.root / "missing")])
        self.assertEqual(code, 2)

    def test_default_root_is_the_repository_ancestor(self) -> None:
        self.assertEqual(Path(validate.__file__).resolve().parents[1], ROOT)


class TestRobustness(ValidatorTestCase):
    def test_repeated_runs_are_identical(self) -> None:
        self.assertEqual(self.report().to_dict(), self.report().to_dict())

    def test_empty_directory_reports_failures_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = validate.validate(Path(tmp))
            self.assertTrue(report.failures())
            checks = {finding.check for finding in report.findings}
            self.assertIn("skill.frontmatter", checks)
            self.assertIn("manifest.plugin", checks)
            self.assertIn("docs.references", checks)
            self.assertIn("assets.budget", checks)
            self.assertIn("security.secrets", checks)
            self.assertTrue(report.warnings())

    def test_unreadable_directory_does_not_raise(self) -> None:
        target = self.root / "references" / "seo.md"
        target.write_bytes(b"\xff\xfe\x00binary")
        report = validate.validate(self.root)
        self.assertTrue(report.failures())


class RealRepositoryTestCase(unittest.TestCase):
    EXPECTED_CHECKS = (
        "skill.frontmatter",
        "manifest.plugin",
        "manifest.marketplace",
        "docs.references",
        "docs.links",
        "docs.readme",
        "assets.budget",
        "legal.license",
        "release.changelog",
        "security.secrets",
    )

    def test_every_check_runs(self) -> None:
        report = validate.validate(ROOT)
        self.assertEqual([finding.check for finding in report.findings], list(self.EXPECTED_CHECKS))

    def test_repository_is_clean(self) -> None:
        report = validate.validate(ROOT)
        self.assertEqual(
            report.failures(),
            [],
            "; ".join("%s: %s" % (finding.check, finding.detail) for finding in report.failures()),
        )

    def test_cli_passes_in_strict_mode(self) -> None:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = validate.main(["--root", str(ROOT), "--strict"])
        self.assertEqual(code, 0, stream.getvalue())


try:
    from PIL import Image as PillowImage  # noqa: F401

    HAS_PILLOW = True
except ImportError:  # pragma: no cover - Pillow is optional
    HAS_PILLOW = False


@unittest.skipUnless(HAS_PILLOW, "Pillow is not installed")
class TestOptimizeAssets(unittest.TestCase):
    SIZE = (160, 100)

    def setUp(self) -> None:
        from PIL import Image

        self.image_module = Image
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.target = self.root / "assets" / "social-preview.png"
        self.target.parent.mkdir(parents=True, exist_ok=True)
        self.original = self.write_uncompressed_png(self.target)

    def write_uncompressed_png(self, path: Path) -> bytes:
        image = self.image_module.new("RGB", self.SIZE)
        pixels = image.load()
        for x in range(self.SIZE[0]):
            for y in range(self.SIZE[1]):
                pixels[x, y] = ((x * 7) % 256, (y * 11) % 256, ((x + y) * 3) % 256)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", compress_level=0)
        payload = buffer.getvalue()
        path.write_bytes(payload)
        return payload

    def run_tool(self, *args) -> tuple:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = optimize_assets.main(["--root", str(self.root)] + list(args))
        return code, stream.getvalue()

    def test_check_mode_flags_an_uncompressed_asset(self) -> None:
        code, output = self.run_tool("--check", str(self.target))
        self.assertEqual(code, 1)
        self.assertIn("CHECK", output)

    def test_rewrite_is_lossless_and_smaller(self) -> None:
        code, _ = self.run_tool(str(self.target))
        self.assertEqual(code, 0)
        optimized = self.target.read_bytes()
        self.assertLess(len(optimized), len(self.original))
        before = optimize_assets.decode_pixels(self.image_module, self.original)
        after = optimize_assets.decode_pixels(self.image_module, optimized)
        self.assertEqual(before, after)

    def test_second_pass_reports_no_slack(self) -> None:
        self.run_tool(str(self.target))
        size = self.target.stat().st_size
        code, _ = self.run_tool("--check", str(self.target))
        self.assertEqual(code, 0)
        self.assertEqual(self.target.stat().st_size, size)

    def test_refuses_to_change_pixels(self) -> None:
        def fake_encode(image_module, payload, fmt):
            buffer = io.BytesIO()
            self.image_module.new("RGB", (2, 2), (1, 2, 3)).save(buffer, format="PNG")
            return buffer.getvalue()

        original_encode = optimize_assets.encode
        optimize_assets.encode = fake_encode
        self.addCleanup(setattr, optimize_assets, "encode", original_encode)
        error, before, after = optimize_assets.optimize(self.target, self.image_module, apply=True)
        self.assertIsNotNone(error)
        self.assertEqual(before, len(self.original))
        self.assertEqual(self.target.read_bytes(), self.original)

    def test_missing_file_is_skipped(self) -> None:
        code, output = self.run_tool("assets/missing.png")
        self.assertEqual(code, 0)
        self.assertIn("SKIP", output)

    def test_unsupported_format_is_skipped(self) -> None:
        (self.root / "notes.txt").write_text("plain", encoding="utf-8")
        code, output = self.run_tool("notes.txt")
        self.assertEqual(code, 0)
        self.assertIn("SKIP", output)
