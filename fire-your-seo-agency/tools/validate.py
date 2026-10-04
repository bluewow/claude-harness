#!/usr/bin/env python3
"""Repository checks for the fire-your-seo-agency Claude Code plugin.

Standard library only. Guards the parts of a documentation-only plugin repo that
rot silently: the SKILL.md frontmatter contract, manifest and version
consistency, relative links and anchors, Korean/English reference parity,
asset budgets, license metadata and accidentally committed secrets.

Usage:
    python3 tools/validate.py [--root DIR] [--json] [--strict]
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

SKILL_PATH = "SKILL.md"
PLUGIN_PATH = ".claude-plugin/plugin.json"
MARKETPLACE_PATH = ".claude-plugin/marketplace.json"
CHANGELOG_PATH = "CHANGELOG.md"
LICENSE_PATH = "LICENSE"
REFERENCES_DIR = "references"
MIRROR_DIR = "references/en"
SOCIAL_PREVIEW_PATH = "assets/social-preview.png"

MAX_SKILL_NAME = 64
MAX_DESCRIPTION = 1024
MAX_ASSET_BYTES = 1_200_000
MAX_FILE_BYTES = 2_000_000
SOCIAL_PREVIEW_DIMENSIONS = (1280, 640)

SKIP_DIRS = frozenset({".git", "node_modules", "__pycache__", ".venv", ".idea", ".vscode"})
TEXT_SUFFIXES = frozenset({".md", ".json", ".txt", ".yml", ".yaml", ".py", ".sh", ".toml", ".cfg", ".ini"})
REQUIRED_PLUGIN_KEYS = ("name", "description", "version", "license")
REQUIRED_PLUGIN_ENTRY_KEYS = ("name", "description", "source", "version")
KNOWN_FRONTMATTER_KEYS = frozenset({
    "name",
    "description",
    "allowed-tools",
    "license",
    "version",
    "author",
    "metadata",
    "model",
    "disable-model-invocation",
})
REPO_TOP_LEVEL = frozenset({"references", "assets", ".claude-plugin", "tools", "tests"})
README_LINK_RE = re.compile(r"\]\(\.?/?README(?:\.ko)?\.md\)")

SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.\-]+)?$")
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]*)>?(?:\s+[\"']([^\"']*)[\"'])?\s*\)")
MENTION_RE = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|json|png|jpe?g|webp|ya?ml|txt|sh|py))`")
CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[[ xX]\]")
NUMBERED_HEADING_RE = re.compile(r"^(#{2,3})\s+(\d+(?:-\d+)?)\.\s")
COPYRIGHT_RE = re.compile(r"Copyright \(c\) \d{4} \S")
CHANGELOG_VERSION_RE = re.compile(r"^##\s+\[?(\d+\.\d+\.\d+)\]?", re.MULTILINE)

SECRET_PATTERNS = (
    ("aws_access_key_id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github_token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}")),
    ("github_pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{50,}")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{32,}")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}")),
    ("private_key_block", re.compile("-----BEGIN " + r"[A-Z ]*PRIVATE KEY-----")),
    ("inline_client_secret", re.compile(r"(?i)\b(?:client[_-]?secret|api[_-]?secret|secret[_-]?key)\s*[:=]\s*[\"']?[A-Za-z0-9_/+=-]{16,}")),
)


@dataclass
class Finding:
    check: str
    ok: bool
    detail: str = ""
    warn: bool = False

    @property
    def level(self) -> str:
        if self.ok:
            return "pass"
        return "warn" if self.warn else "fail"


@dataclass
class Report:
    findings: list = field(default_factory=list)

    def add(self, check: str, ok: bool, detail: str = "", warn: bool = False) -> None:
        self.findings.append(Finding(check, bool(ok), detail, bool(warn)))

    @property
    def ok(self) -> bool:
        return not self.failures()

    def failures(self) -> list:
        return [f for f in self.findings if not f.ok and not f.warn]

    def warnings(self) -> list:
        return [f for f in self.findings if not f.ok and f.warn]

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "checked": len(self.findings),
            "failed": len(self.failures()),
            "warnings": len(self.warnings()),
            "findings": [
                {"check": f.check, "level": f.level, "detail": f.detail} for f in self.findings
            ],
        }


class Repo:
    """A read-only view of the files that would actually be committed."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.files = self._collect()

    def _collect(self) -> list:
        found = []
        for path in sorted(self.root.rglob("*")):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.is_file():
                found.append(path)
        return found

    def rel(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def has(self, rel: str) -> bool:
        return (self.root / rel).is_file()

    def read(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")

    def text_files(self) -> list:
        return [p for p in self.files if p.suffix.lower() in TEXT_SUFFIXES]


def slugify(text: str) -> str:
    """Approximate the anchor GitHub generates for a markdown heading."""
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.replace("`", "").replace("*", "").replace("~", "")
    text = text.strip().lower()
    kept = [ch if (ch.isalnum() or ch in " -_") else "" for ch in text]
    return re.sub(r"\s+", "-", "".join(kept).strip())


def parse_frontmatter(block: str) -> dict:
    """Parse the small flat frontmatter contract used by SKILL.md."""
    values: dict = {}
    for lineno, raw in enumerate(block.splitlines(), start=1):
        line = raw.rstrip()
        if not line.strip():
            continue
        if line[0].isspace():
            raise ValueError("line %d is indented; nested frontmatter is not supported" % lineno)
        key, sep, value = line.partition(":")
        if not sep or not key.strip():
            raise ValueError("line %d is not a key: value pair" % lineno)
        key = key.strip()
        if key in values:
            raise ValueError("duplicate frontmatter key %r" % key)
        values[key] = value.strip()
    return values


def strict_yaml(block: str):
    """Return the YAML mapping when PyYAML is importable, else None."""
    try:
        import yaml
    except ImportError:
        return None
    try:
        return yaml.safe_load(block)
    except Exception as exc:  # pragma: no cover - depends on optional dependency
        raise ValueError("frontmatter is not valid YAML: %s" % exc) from exc


def read_png_dimensions(path: Path) -> tuple:
    with open(path, "rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    if header[12:16] != b"IHDR":
        raise ValueError("PNG is missing a leading IHDR chunk")
    return struct.unpack(">II", header[16:24])


def load_json_object(repo: Repo, rel: str, report: Report, check: str):
    if not repo.has(rel):
        report.add(check, False, "%s is missing" % rel)
        return None
    try:
        data = json.loads(repo.read(rel))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        report.add(check, False, "%s is not valid JSON: %s" % (rel, exc))
        return None
    if not isinstance(data, dict):
        report.add(check, False, "%s must contain a JSON object" % rel)
        return None
    return data


def non_empty_str(value) -> bool:
    return isinstance(value, str) and bool(value.strip())
def read_text(path: Path):
    """Read UTF-8 text, or return None when the file is missing or binary."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def check_skill(repo: Repo, report: Report):
    if not repo.has(SKILL_PATH):
        report.add("skill.frontmatter", False, "%s is missing" % SKILL_PATH)
        return None
    text = read_text(repo.root / SKILL_PATH)
    if text is None:
        report.add("skill.frontmatter", False, "%s is not valid UTF-8" % SKILL_PATH)
        return None
    match = FRONTMATTER_RE.match(text)
    if not match:
        report.add("skill.frontmatter", False, "%s must start with a --- delimited frontmatter block" % SKILL_PATH)
        return None
    block = match.group(1)
    try:
        values = parse_frontmatter(block)
        parsed = strict_yaml(block)
    except ValueError as exc:
        report.add("skill.frontmatter", False, "%s frontmatter: %s" % (SKILL_PATH, exc))
        return None
    if parsed is not None and not isinstance(parsed, dict):
        report.add("skill.frontmatter", False, "%s frontmatter must parse as a YAML mapping" % SKILL_PATH)
        return None
    name = values.get("name", "")
    description = values.get("description", "")
    problems = []
    if not name:
        problems.append("name is missing or empty")
    elif not SKILL_NAME_RE.match(name):
        problems.append("name %r must be lowercase kebab-case" % name)
    elif len(name) > MAX_SKILL_NAME:
        problems.append("name is %d chars (max %d)" % (len(name), MAX_SKILL_NAME))
    if not description:
        problems.append("description is missing or empty")
    elif len(description) > MAX_DESCRIPTION:
        problems.append("description is %d chars (max %d)" % (len(description), MAX_DESCRIPTION))
    if "\n" in description:
        problems.append("description must stay on a single line")
    if not text[match.end():].strip():
        problems.append("%s has no body after the frontmatter" % SKILL_PATH)
    if problems:
        report.add("skill.frontmatter", False, "; ".join(problems))
        return None
    report.add("skill.frontmatter", True, "name=%s (%d chars), description=%d chars" % (name, len(name), len(description)))
    for key in sorted(set(values) - KNOWN_FRONTMATTER_KEYS):
        report.add("skill.frontmatter.keys", False, "unexpected frontmatter key %r" % key, warn=True)
    return name


def check_plugin_manifest(repo: Repo, report: Report, skill_name):
    data = load_json_object(repo, PLUGIN_PATH, report, "manifest.plugin")
    if data is None:
        return None
    problems = []
    for key in REQUIRED_PLUGIN_KEYS:
        if not non_empty_str(data.get(key)):
            problems.append("%s must be a non-empty string" % key)
    version = data.get("version") if isinstance(data.get("version"), str) else ""
    if version and not SEMVER_RE.match(version):
        problems.append("version %r is not semver" % version)
    if skill_name and data.get("name") != skill_name:
        problems.append("name %r does not match the SKILL.md name %r" % (data.get("name"), skill_name))
    author = data.get("author")
    if not isinstance(author, dict) or not non_empty_str(author.get("name")):
        problems.append("author.name must be a non-empty string")
    homepage = data.get("homepage")
    if homepage is not None and not (non_empty_str(homepage) and homepage.startswith("https://")):
        problems.append("homepage must be an https URL")
    keywords = data.get("keywords")
    if not isinstance(keywords, list) or not keywords:
        problems.append("keywords must be a non-empty list")
    elif any(not non_empty_str(k) for k in keywords):
        problems.append("keywords must all be non-empty strings")
    if problems:
        report.add("manifest.plugin", False, "; ".join(problems))
        return None
    report.add("manifest.plugin", True, "name=%s version=%s keys=%d" % (data["name"], version, len(data)))
    return data


def check_marketplace_manifest(repo: Repo, report: Report, plugin, skill_name):
    data = load_json_object(repo, MARKETPLACE_PATH, report, "manifest.marketplace")
    if data is None:
        return None
    problems = []
    for key in ("name", "description"):
        if not non_empty_str(data.get(key)):
            problems.append("%s must be a non-empty string" % key)
    owner = data.get("owner")
    if not isinstance(owner, dict) or not non_empty_str(owner.get("name")):
        problems.append("owner.name must be a non-empty string")
    if skill_name and data.get("name") != skill_name:
        problems.append("marketplace name %r does not match the SKILL.md name %r" % (data.get("name"), skill_name))
    entries = data.get("plugins")
    if not isinstance(entries, list) or not entries:
        problems.append("plugins must be a non-empty list")
        entries = []
    root = repo.root.resolve()
    for index, entry in enumerate(entries):
        label = "plugins[%d]" % index
        if not isinstance(entry, dict):
            problems.append("%s must be an object" % label)
            continue
        for key in REQUIRED_PLUGIN_ENTRY_KEYS:
            if not non_empty_str(entry.get(key)):
                problems.append("%s.%s must be a non-empty string" % (label, key))
        version = entry.get("version") if isinstance(entry.get("version"), str) else ""
        if version and not SEMVER_RE.match(version):
            problems.append("%s.version %r is not semver" % (label, version))
        if plugin and version and plugin.get("version") and version != plugin["version"]:
            problems.append("%s.version %s != plugin.json version %s" % (label, version, plugin["version"]))
        if skill_name and entry.get("name") != skill_name:
            problems.append("%s.name %r does not match the SKILL.md name %r" % (label, entry.get("name"), skill_name))
        source = entry.get("source")
        if non_empty_str(source):
            candidate = Path(source)
            if candidate.is_absolute():
                problems.append("%s.source must be repository-relative, not absolute" % label)
            else:
                resolved = (repo.root / candidate).resolve()
                if resolved != root and root not in resolved.parents:
                    problems.append("%s.source %r escapes the repository" % (label, source))
                elif not resolved.exists():
                    problems.append("%s.source %r does not exist" % (label, source))
    if problems:
        report.add("manifest.marketplace", False, "; ".join(problems))
        return None
    report.add("manifest.marketplace", True, "%d plugin entry, version %s" % (len(entries), entries[0].get("version", "?")))
    return data


def reference_stats(path: Path):
    text = read_text(path)
    if text is None:
        return None
    stats = {
        "h1": 0,
        "h2": 0,
        "h3": 0,
        "fences": 0,
        "table_rows": 0,
        "checkboxes": 0,
        "bytes": len(text.encode("utf-8")),
        "numbers": [],
    }
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```") or line.startswith("~~~"):
            in_fence = not in_fence
            stats["fences"] += 1
            continue
        if in_fence:
            continue
        heading = HEADING_RE.match(line)
        if heading:
            depth = len(heading.group(1))
            if depth in (1, 2, 3):
                stats["h%d" % depth] += 1
            numbered = NUMBERED_HEADING_RE.match(line)
            if numbered:
                stats["numbers"].append(numbered.group(2))
        if line.startswith("|"):
            stats["table_rows"] += 1
        if CHECKBOX_RE.match(line):
            stats["checkboxes"] += 1
    stats["fences"] //= 2
    return stats


def check_references(repo: Repo, report: Report) -> None:
    source_dir = repo.root / REFERENCES_DIR
    mirror_dir = repo.root / MIRROR_DIR
    if not source_dir.is_dir():
        report.add("docs.references", False, "%s/ is missing" % REFERENCES_DIR)
        return
    names = sorted(p.name for p in source_dir.glob("*.md"))
    if not names:
        report.add("docs.references", False, "%s/ contains no markdown documents" % REFERENCES_DIR)
        return
    if not mirror_dir.is_dir():
        report.add("docs.references", False, "%s/ is missing" % MIRROR_DIR)
        return
    mirrored = sorted(p.name for p in mirror_dir.glob("*.md"))
    problems = []
    for name in sorted(set(names) - set(mirrored)):
        problems.append("%s/%s has no English mirror" % (REFERENCES_DIR, name))
    for name in sorted(set(mirrored) - set(names)):
        problems.append("%s/%s has no canonical Korean source" % (MIRROR_DIR, name))
    for name in sorted(set(names) & set(mirrored)):
        left = reference_stats(source_dir / name)
        right = reference_stats(mirror_dir / name)
        if left is None or right is None:
            problems.append("%s: mirror is not readable as UTF-8" % name)
            continue
        for metric in ("h1", "h2", "h3", "fences", "table_rows", "checkboxes"):
            if left[metric] != right[metric]:
                problems.append("%s: %s %d (ko) vs %d (en)" % (name, metric, left[metric], right[metric]))
                break
        if left["numbers"] != right["numbers"]:
            problems.append(
                "%s: section numbering drifted (%s vs %s)"
                % (name, ",".join(left["numbers"]), ",".join(right["numbers"])),
            )
    if problems:
        report.add("docs.references", False, "; ".join(problems))
        return
    total = sum((reference_stats(source_dir / n) or {"bytes": 0})["bytes"] for n in names)
    report.add("docs.references", True, "%d documents mirrored, %d canonical bytes" % (len(names), total))


def markdown_files(repo: Repo) -> list:
    return [p for p in repo.text_files() if p.suffix.lower() == ".md"]


def anchor_slugs(path: Path) -> set:
    body = read_text(path)
    if body is None:
        return set()
    slugs = set()
    in_fence = False
    for line in body.splitlines():
        if line.startswith("```") or line.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = HEADING_RE.match(line)
        if heading:
            slugs.add(slugify(heading.group(2)))
    return slugs


def check_links(repo: Repo, report: Report) -> None:
    files = markdown_files(repo)
    if not files:
        report.add("docs.links", False, "no markdown files found", warn=True)
        return
    root = repo.root.resolve()
    broken, dangling, missing_paths = [], [], []
    total = 0
    resolved = 0
    for path in files:
        rel = repo.rel(path)
        body = read_text(path)
        if body is None:
            broken.append("%s: not valid UTF-8" % rel)
            continue
        lines = body.splitlines()
        for lineno, line in enumerate(lines, start=1):
            for target, _title in LINK_RE.findall(line):
                total += 1
                target = target.strip()
                if not target:
                    broken.append("%s:%d has an empty link target" % (rel, lineno))
                    continue
                if re.match(r"^(?:[A-Za-z][A-Za-z0-9+.\-]*:|//)", target):
                    continue
                fragment = ""
                if "#" in target:
                    target, fragment = target.split("#", 1)
                target = unquote(target)
                if target.startswith("/"):
                    broken.append("%s:%d %s is an absolute path" % (rel, lineno, target))
                    continue
                if not target:
                    destination = path
                else:
                    destination = (path.parent / target).resolve()
                    if destination != root and root not in destination.parents:
                        broken.append("%s:%d %s escapes the repository" % (rel, lineno, target))
                        continue
                    if not destination.exists():
                        broken.append("%s:%d %s does not exist" % (rel, lineno, target))
                        continue
                resolved += 1
                if fragment and destination.is_file() and destination.suffix.lower() == ".md":
                    if fragment not in anchor_slugs(destination):
                        dangling.append("%s:%d %s#%s" % (rel, lineno, target or rel, fragment))
            for mention in MENTION_RE.findall(line):
                if (path.parent / mention).exists() or (repo.root / mention).exists():
                    continue
                if mention.split("/")[0] in REPO_TOP_LEVEL:
                    missing_paths.append("%s:%d %s" % (rel, lineno, mention))
    detail = "%d links in %d files (%d resolved), %d broken, %d dangling anchors, %d dangling path mentions" % (
        total,
        len(files),
        resolved,
        len(broken),
        len(dangling),
        len(missing_paths),
    )
    problems = broken + dangling + missing_paths
    if problems:
        report.add("docs.links", False, "%s | %s" % ("; ".join(problems[:12]), detail))
    else:
        report.add("docs.links", True, detail)
    if total == 0:
        report.add("docs.links.coverage", False, "no markdown links were found at all", warn=True)


def check_readmes(repo: Repo, report: Report) -> None:
    names = ["README.md", "README.ko.md"]
    problems = []
    texts = {}
    for name in names:
        if not repo.has(name):
            problems.append("%s is missing" % name)
            continue
        body = read_text(repo.root / name)
        if body is None:
            problems.append("%s is not valid UTF-8" % name)
            continue
        texts[name] = body
        if SOCIAL_PREVIEW_PATH not in texts[name]:
            problems.append("%s does not embed %s" % (name, SOCIAL_PREVIEW_PATH))
    if len(texts) == 2:
        if not README_LINK_RE.search(texts["README.md"]):
            problems.append("README.md has no link to README.ko.md")
        if not README_LINK_RE.search(texts["README.ko.md"]):
            problems.append("README.ko.md has no link to README.md")
    source_dir = repo.root / REFERENCES_DIR
    if source_dir.is_dir():
        for path in sorted(source_dir.glob("*.md")):
            for name, text in texts.items():
                if path.name not in text:
                    problems.append("%s does not list %s/%s" % (name, REFERENCES_DIR, path.name))
    if problems:
        report.add("docs.readme", False, "; ".join(problems))
        return
    report.add("docs.readme", True, "both READMEs embed the preview and list every reference")


def check_assets(repo: Repo, report: Report) -> None:
    problems = []
    summary = "assets within budget"
    preview = repo.root / SOCIAL_PREVIEW_PATH
    if not preview.is_file():
        problems.append("%s is missing" % SOCIAL_PREVIEW_PATH)
    else:
        try:
            width, height = read_png_dimensions(preview)
        except (OSError, ValueError) as exc:
            problems.append("%s: %s" % (SOCIAL_PREVIEW_PATH, exc))
        else:
            expected = SOCIAL_PREVIEW_DIMENSIONS
            if (width, height) != expected:
                problems.append(
                    "%s is %dx%d, expected %dx%d"
                    % (SOCIAL_PREVIEW_PATH, width, height, expected[0], expected[1]),
                )
            size = preview.stat().st_size
            if size > MAX_ASSET_BYTES:
                problems.append(
                    "%s is %d bytes, over the %d byte budget; run tools/optimize_assets.py"
                    % (SOCIAL_PREVIEW_PATH, size, MAX_ASSET_BYTES),
                )
            summary = "%s %dx%d, %d bytes" % (SOCIAL_PREVIEW_PATH, width, height, size)
    for path in repo.files:
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            problems.append("%s is %.2f MiB" % (repo.rel(path), size / 1048576.0))
    total = sum(path.stat().st_size for path in repo.files)
    summary = "%s, %.2f MiB across %d files" % (summary, total / 1048576.0, len(repo.files))
    if problems:
        report.add("assets.budget", False, "; ".join(problems))
    else:
        report.add("assets.budget", True, summary)


def check_license(repo: Repo, report: Report, plugin) -> None:
    if not repo.has(LICENSE_PATH):
        report.add("legal.license", False, "%s is missing" % LICENSE_PATH)
        return
    text = read_text(repo.root / LICENSE_PATH)
    if text is None:
        report.add("legal.license", False, "%s is not valid UTF-8" % LICENSE_PATH)
        return
    problems = []
    if "MIT License" not in text:
        problems.append("%s is not the MIT license text" % LICENSE_PATH)
    if not COPYRIGHT_RE.search(text):
        problems.append("%s has no Copyright line" % LICENSE_PATH)
    if plugin and plugin.get("license") != "MIT":
        problems.append("plugin.json license %r does not match LICENSE" % plugin.get("license"))
    if problems:
        report.add("legal.license", False, "; ".join(problems))
    else:
        report.add("legal.license", True, "MIT")


def check_changelog(repo: Repo, report: Report, version) -> None:
    if not repo.has(CHANGELOG_PATH):
        report.add("release.changelog", False, "%s is missing" % CHANGELOG_PATH)
        return
    body = read_text(repo.root / CHANGELOG_PATH)
    if body is None:
        report.add("release.changelog", False, "%s is not valid UTF-8" % CHANGELOG_PATH)
        return
    versions = CHANGELOG_VERSION_RE.findall(body)
    if not versions:
        report.add("release.changelog", False, "%s has no version heading" % CHANGELOG_PATH)
        return
    if version and versions[0] != version:
        report.add(
            "release.changelog",
            False,
            "%s top entry %s does not match manifest version %s" % (CHANGELOG_PATH, versions[0], version),
        )
        return
    report.add("release.changelog", True, "top entry %s, %d releases recorded" % (versions[0], len(versions)))


def check_secrets(repo: Repo, report: Report) -> None:
    hits = []
    scanned = 0
    for path in repo.text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        scanned += 1
        for lineno, line in enumerate(text.splitlines(), start=1):
            for name, pattern in SECRET_PATTERNS:
                match = pattern.search(line)
                if match:
                    hits.append("%s:%d (%s, %d chars redacted)" % (repo.rel(path), lineno, name, len(match.group(0))))
    if hits:
        report.add("security.secrets", False, "; ".join(hits[:12]))
    else:
        report.add("security.secrets", True, "%d text files scanned, 0 matches" % scanned)


def validate(root: Path) -> Report:
    repo = Repo(root)
    report = Report()
    skill_name = check_skill(repo, report)
    plugin = check_plugin_manifest(repo, report, skill_name)
    check_marketplace_manifest(repo, report, plugin, skill_name)
    check_references(repo, report)
    check_links(repo, report)
    check_readmes(repo, report)
    check_assets(repo, report)
    check_license(repo, report, plugin)
    check_changelog(repo, report, plugin.get("version") if plugin else None)
    check_secrets(repo, report)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate a fire-your-seo-agency style plugin repository.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--json", dest="as_json", action="store_true", help="print the report as JSON")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        print("error: %s is not a directory" % root, file=sys.stderr)
        return 2
    report = validate(root)
    failing = report.failures() + (report.warnings() if args.strict else [])
    if args.as_json:
        payload = report.to_dict()
        payload["root"] = str(root)
        payload["strict"] = bool(args.strict)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for finding in report.findings:
            print("%-5s %-24s %s" % (finding.level.upper(), finding.check, finding.detail))
        print(
            "%d checks, %d failed, %d warnings%s"
            % (len(report.findings), len(report.failures()), len(report.warnings()), " (strict)" if args.strict else ""),
        )
    return 1 if failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
