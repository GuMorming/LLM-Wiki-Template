#!/usr/bin/env python3
"""Audit wiki markdown frontmatter and relative links."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
from pathlib import Path


REQUIRED_KEYS = {"title", "type", "tags", "related", "created", "updated"}
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def repo_root(start: Path) -> Path:
    for path in [start, *start.parents]:
        if (path / "AGENTS.md").exists() and (path / "wiki").exists():
            return path
    raise SystemExit("Could not find repository root containing AGENTS.md and wiki/.")


def frontmatter_keys(text: str) -> set[str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    keys: set[str] = set()
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" in line and not line.startswith((" ", "\t", "-")):
            keys.add(line.split(":", 1)[0].strip())
    return keys


def markdown_files(root: Path) -> list[Path]:
    files = [root / "index.md", root / "log.md"]
    files.extend(sorted((root / "wiki").rglob("*.md")))
    return [path for path in files if path.exists()]


def check_frontmatter(root: Path, path: Path, errors: list[str]) -> None:
    if not path.relative_to(root).parts[0] == "wiki":
        return
    text = path.read_text(encoding="utf-8")
    keys = frontmatter_keys(text)
    rel = path.relative_to(root)
    if keys is None:
        errors.append(f"{rel}: missing YAML frontmatter")
        return
    missing = REQUIRED_KEYS - keys
    if missing:
        errors.append(f"{rel}: missing frontmatter keys: {', '.join(sorted(missing))}")


def check_links(root: Path, path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    base = path.parent
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.split("#", 1)[0]
        if not target:
            continue
        target = urllib.parse.unquote(target)
        resolved = (base / target).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            errors.append(f"{path.relative_to(root)}: link escapes repo: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{path.relative_to(root)}: broken link: {target}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-frontmatter", action="store_true", help="Skip wiki frontmatter checks.")
    parser.add_argument("--no-links", action="store_true", help="Skip relative link checks.")
    args = parser.parse_args()

    root = repo_root(Path.cwd().resolve())
    errors: list[str] = []
    files = markdown_files(root)

    for path in files:
        if not args.no_frontmatter:
            check_frontmatter(root, path, errors)
        if not args.no_links:
            check_links(root, path, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"audited {len(files)} markdown files; {len(errors)} issue(s)", file=sys.stderr)
        return 1

    print(f"audited {len(files)} markdown files; no frontmatter/link issues")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
