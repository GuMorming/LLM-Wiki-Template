#!/usr/bin/env python3
"""Resolve a requested ingest source path inside the repository raw/ tree."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def repo_root(start: Path) -> Path:
    for path in [start, *start.parents]:
        if (path / "AGENTS.md").exists() and (path / "raw").exists():
            return path
    raise SystemExit("Could not find repository root containing AGENTS.md and raw/.")


def source_kind(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    parts = rel.parts
    if len(parts) >= 3 and parts[0] == "raw" and parts[1] == "own works":
        return "own-work"
    if path.is_dir():
        names = {p.name.lower() for p in path.iterdir()}
        if "readme.md" in names or ".git" in names:
            return "codebase"
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "external-paper"
    if suffix in {".bib", ".tex", ".md", ".txt"}:
        return "note"
    return "unknown"


def candidates(raw_arg: str, root: Path) -> list[Path]:
    raw_arg = raw_arg.strip()
    base = Path(raw_arg).expanduser()
    values: list[Path] = []

    if base.is_absolute():
        values.append(base)
    else:
        values.append(root / base)

    replacements = {
        "raw/artical/": "raw/articles/",
        "raw/artical": "raw/articles",
        "raw/article/": "raw/articles/",
        "raw/article": "raw/articles",
    }
    for old, new in replacements.items():
        if old in raw_arg:
            fixed = raw_arg.replace(old, new, 1)
            values.append(root / fixed)

    expanded: list[Path] = []
    for value in values:
        expanded.append(value)
        if value.suffix:
            continue
        for suffix in [".pdf", ".md", ".txt", ".tex"]:
            expanded.append(value.with_suffix(suffix))

    seen: set[Path] = set()
    unique: list[Path] = []
    for value in expanded:
        resolved = value.resolve()
        if resolved not in seen:
            unique.append(resolved)
            seen.add(resolved)
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="User-provided source path, usually under raw/.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    root = repo_root(Path.cwd().resolve())
    tried = candidates(args.source, root)
    found = next((path for path in tried if path.exists()), None)

    if found is None:
        payload = {
            "ok": False,
            "source": args.source,
            "tried": [str(path.relative_to(root)) if path.is_relative_to(root) else str(path) for path in tried],
        }
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"Source not found: {args.source}")
            print("Tried:")
            for item in payload["tried"]:
                print(f"- {item}")
        return 1

    try:
        rel = found.relative_to(root)
    except ValueError:
        rel = found

    under_raw = isinstance(rel, Path) and len(rel.parts) > 0 and rel.parts[0] == "raw"
    payload = {
        "ok": True,
        "path": str(rel),
        "absolute_path": str(found),
        "under_raw": under_raw,
        "kind": source_kind(found, root) if under_raw else "outside-raw",
        "is_dir": found.is_dir(),
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"path: {payload['path']}")
        print(f"kind: {payload['kind']}")
        print(f"under_raw: {str(payload['under_raw']).lower()}")
        print(f"is_dir: {str(payload['is_dir']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
