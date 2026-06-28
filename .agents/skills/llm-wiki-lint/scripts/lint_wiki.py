#!/usr/bin/env python3
"""Run mechanical lint checks for a repository-local LLM Research Wiki."""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path


REQUIRED_KEYS = {"title", "type", "tags", "related", "created", "updated"}
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


@dataclass
class Issue:
    severity: str
    code: str
    title: str
    path: str
    detail: str
    recommendation: str


def repo_root(start: Path) -> Path:
    for path in [start, *start.parents]:
        if (path / "AGENTS.md").exists() and (path / "wiki").exists():
            return path
    raise SystemExit("Could not find repository root containing AGENTS.md and wiki/.")


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def markdown_files(root: Path) -> list[Path]:
    files = [root / "index.md", root / "log.md"]
    files.extend(sorted((root / "wiki").rglob("*.md")))
    return [path for path in files if path.exists()]


def wiki_files(root: Path) -> list[Path]:
    return sorted((root / "wiki").rglob("*.md"))


def frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" in line and not line.startswith((" ", "\t", "-")):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


def normalized_title(value: str) -> str:
    value = value.strip().strip('"').strip("'").lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def parse_related(value: str) -> list[str]:
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        return []
    inner = value[1:-1].strip()
    if not inner:
        return []
    return [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]


def section_text(text: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^## ", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def expected_type_for(path: Path) -> str | None:
    if path.name == "index.md" and "wiki/projects" in str(path):
        return "project"
    if path.name == "index.md":
        return None
    folder = path.parent.name
    mapping = {
        "source-notes": "source-note",
        "concepts": "concept",
        "methods": "method",
        "systems": "system",
        "benchmarks": "benchmark",
        "datasets": "dataset",
        "experiments": "experiment",
        "claims": "claim",
        "syntheses": "synthesis",
        "authors": "author",
        "debates": "debate",
        "themes": "theme",
    }
    return mapping.get(folder)


def add_issue(issues: list[Issue], severity: str, code: str, title: str, path: str, detail: str, recommendation: str) -> None:
    issues.append(Issue(severity, code, title, path, detail, recommendation))


def check_frontmatter(root: Path, path: Path, text: str, issues: list[Issue]) -> dict[str, str] | None:
    fm = frontmatter(text)
    if fm is None:
        add_issue(
            issues,
            "P1",
            "missing-frontmatter",
            "Wiki page is missing YAML frontmatter",
            rel(root, path),
            "Every wiki page must begin with YAML frontmatter.",
            "Add required frontmatter keys from AGENTS.md.",
        )
        return None

    missing = REQUIRED_KEYS - set(fm)
    if missing:
        add_issue(
            issues,
            "P1",
            "missing-frontmatter-keys",
            "Wiki page is missing required frontmatter keys",
            rel(root, path),
            f"Missing keys: {', '.join(sorted(missing))}.",
            "Add the missing keys required by AGENTS.md.",
        )

    expected_type = expected_type_for(path)
    page_type = fm.get("type", "").strip().strip('"').strip("'")
    if expected_type and page_type and page_type != expected_type:
        add_issue(
            issues,
            "P2",
            "wrong-page-type",
            "Page type does not match folder convention",
            rel(root, path),
            f"Folder suggests '{expected_type}', found '{page_type}'.",
            "Either move the page or adjust the frontmatter type.",
        )

    return fm


def check_links(root: Path, path: Path, text: str, issues: list[Issue], inbound: Counter[str]) -> None:
    base = path.parent
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target_no_anchor = target.split("#", 1)[0]
        if not target_no_anchor:
            continue
        decoded = urllib.parse.unquote(target_no_anchor)
        resolved = (base / decoded).resolve()
        try:
            target_rel = rel(root, resolved)
        except RuntimeError:
            target_rel = str(resolved)
        try:
            resolved.relative_to(root)
        except ValueError:
            add_issue(
                issues,
                "P1",
                "link-escapes-repo",
                "Relative link escapes repository",
                rel(root, path),
                f"Link target: {target}.",
                "Use a repository-local relative link.",
            )
            continue
        if not resolved.exists():
            add_issue(
                issues,
                "P1",
                "broken-link",
                "Broken relative link",
                rel(root, path),
                f"Link target does not exist: {target}.",
                "Fix the path or create the linked page.",
            )
        elif target_rel.endswith(".md") and target_rel.startswith("wiki/"):
            inbound[target_rel] += 1


def check_related(root: Path, path: Path, fm: dict[str, str], all_stems: set[str], issues: list[Issue]) -> None:
    for stem in parse_related(fm.get("related", "")):
        if stem and stem not in all_stems:
            add_issue(
                issues,
                "P2",
                "related-missing-stem",
                "Frontmatter related stem has no matching wiki page",
                rel(root, path),
                f"related entry '{stem}' does not match any wiki filename stem.",
                "Update the related list or create/log the missing page.",
            )


def check_source_support(root: Path, path: Path, text: str, fm: dict[str, str], issues: list[Issue]) -> None:
    page_type = fm.get("type", "").strip().strip('"').strip("'")
    if page_type in {"concept", "method", "system", "benchmark", "dataset"}:
        support = section_text(text, "Source Support") or section_text(text, "Usage in Sources")
        if not support:
            add_issue(
                issues,
                "P2",
                "missing-source-support",
                "Reusable page lacks source support section",
                rel(root, path),
                f"Page type '{page_type}' should cite source notes or usage evidence.",
                "Add Source Support/Usage in Sources with source-note links.",
            )
        elif "../source-notes/" not in support and "source-notes/" not in support:
            add_issue(
                issues,
                "P2",
                "thin-source-support",
                "Source support section has no source-note link",
                rel(root, path),
                "The source support section does not link to any source note.",
                "Link at least one supporting source note or state why support is pending.",
            )

    if page_type == "source-note" and "**Raw file:**" not in text:
        add_issue(
            issues,
            "P1",
            "source-note-missing-raw",
            "Source note lacks raw file reference",
            rel(root, path),
            "Source notes must record the raw source path.",
            "Add a **Raw file:** link.",
        )


def check_claim_evidence(root: Path, path: Path, text: str, fm: dict[str, str], issues: list[Issue]) -> None:
    if fm.get("type", "").strip().strip('"').strip("'") != "claim":
        return
    evidence = section_text(text, "Evidence")
    if not evidence:
        add_issue(
            issues,
            "P1",
            "claim-missing-evidence",
            "Claim page lacks an Evidence section",
            rel(root, path),
            "Claims must stay evidence-backed.",
            "Add an Evidence section with source/experiment references.",
        )
        return
    markers = ["sec.", "section", "fig.", "figure", "table", "experiment", "source note", "source-notes", "raw", "evaluation"]
    if not any(marker in evidence.lower() for marker in markers):
        add_issue(
            issues,
            "P1",
            "claim-weak-evidence",
            "Claim evidence lacks exact references",
            rel(root, path),
            "Evidence does not mention section, figure, table, experiment, source note, or raw artifact.",
            "Point the claim to explicit evidence before using it in research writing.",
        )


def check_overgrown(root: Path, path: Path, text: str, issues: list[Issue]) -> None:
    lines = text.count("\n") + 1
    if lines > 300:
        add_issue(
            issues,
            "P3",
            "overgrown-page",
            "Page may be too large",
            rel(root, path),
            f"Page has {lines} lines.",
            "Consider splitting if it mixes multiple concepts, sources, or experiments.",
        )


def check_duplicates(root: Path, metadata: dict[Path, dict[str, str]], issues: list[Issue]) -> None:
    by_title: defaultdict[str, list[Path]] = defaultdict(list)
    by_stem: defaultdict[str, list[Path]] = defaultdict(list)
    for path, fm in metadata.items():
        title = fm.get("title", "")
        if title:
            by_title[normalized_title(title)].append(path)
        by_stem[path.stem].append(path)

    for title, paths in by_title.items():
        type_folder_pairs = {
            (
                metadata[path].get("type", "").strip().strip('"').strip("'"),
                path.parent.name,
            )
            for path in paths
        }
        same_type_or_folder = len({item[0] for item in type_folder_pairs}) < len(type_folder_pairs) or len({item[1] for item in type_folder_pairs}) < len(type_folder_pairs)
        if title and len(paths) > 1 and same_type_or_folder:
            add_issue(
                issues,
                "P2",
                "duplicate-title",
                "Multiple pages share the same normalized title",
                ", ".join(rel(root, p) for p in paths),
                f"Normalized title: {title}.",
                "Check whether these pages should be merged, renamed, or cross-linked with clearer boundaries.",
            )

    for stem, paths in by_stem.items():
        if stem != "index" and len(paths) > 1:
            add_issue(
                issues,
                "P3",
                "duplicate-stem",
                "Multiple wiki pages share the same filename stem",
                ", ".join(rel(root, p) for p in paths),
                f"Filename stem: {stem}.",
                "Check whether duplicate stems make frontmatter related links ambiguous.",
            )


def check_orphans(root: Path, inbound: Counter[str], issues: list[Issue]) -> None:
    for path in wiki_files(root):
        path_rel = rel(root, path)
        if path.name == ".gitkeep":
            continue
        if path_rel.startswith("wiki/projects/") and path.name == "index.md":
            continue
        if inbound[path_rel] == 0:
            add_issue(
                issues,
                "P2",
                "orphan-page",
                "Wiki page has no inbound Markdown links",
                path_rel,
                "No link from index.md, log.md, or another wiki page was found.",
                "Add an index/cluster backlink or mark it as intentionally standalone.",
            )


def sort_key(issue: Issue) -> tuple[int, str, str]:
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    return (order.get(issue.severity, 9), issue.code, issue.path)


def print_text(issues: list[Issue]) -> None:
    if not issues:
        print("No mechanical lint issues found.")
        return
    print(f"Mechanical lint found {len(issues)} issue(s):")
    for issue in sorted(issues, key=sort_key):
        print()
        print(f"- [{issue.severity}] {issue.title} ({issue.code})")
        print(f"  Path: {issue.path}")
        print(f"  Evidence: {issue.detail}")
        print(f"  Recommended fix: {issue.recommendation}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument("--fail-on-issues", action="store_true", help="Exit 1 when issues are found.")
    args = parser.parse_args()

    root = repo_root(Path.cwd().resolve())
    issues: list[Issue] = []
    inbound: Counter[str] = Counter()
    metadata: dict[Path, dict[str, str]] = {}
    all_stems = {path.stem for path in wiki_files(root)}

    for path in markdown_files(root):
        text = path.read_text(encoding="utf-8")
        if rel(root, path).startswith("wiki/"):
            fm = check_frontmatter(root, path, text, issues)
            if fm is not None:
                metadata[path] = fm
        check_links(root, path, text, issues, inbound)

    for path, fm in metadata.items():
        text = path.read_text(encoding="utf-8")
        check_related(root, path, fm, all_stems, issues)
        check_source_support(root, path, text, fm, issues)
        check_claim_evidence(root, path, text, fm, issues)
        check_overgrown(root, path, text, issues)

    check_duplicates(root, metadata, issues)
    check_orphans(root, inbound, issues)

    issues = sorted(issues, key=sort_key)
    if args.json:
        print(json.dumps([asdict(issue) for issue in issues], indent=2, ensure_ascii=False))
    else:
        print_text(issues)

    return 1 if issues and args.fail_on_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
