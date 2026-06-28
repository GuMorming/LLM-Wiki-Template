#!/usr/bin/env python3
"""Fail if tracked raw/ files were modified or deleted during ingest."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def repo_root(start: Path) -> Path:
    for path in [start, *start.parents]:
        if (path / "AGENTS.md").exists() and (path / "raw").exists():
            return path
    raise SystemExit("Could not find wiki root containing AGENTS.md and raw/.")


def git_toplevel(root: Path) -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve()


def porcelain(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return result.stdout.splitlines()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-untracked",
        action="store_true",
        help="Also flag untracked raw/ files. Default only flags tracked modifications/deletions.",
    )
    args = parser.parse_args()

    root = repo_root(Path.cwd().resolve())
    top = git_toplevel(root)
    if top is None:
        print("not in a git repository; tracked raw-file check skipped")
        return 0
    if top != root:
        print(
            f"wiki root is nested under git top-level {top}; tracked raw-file check skipped to avoid checking the parent repository"
        )
        return 0

    bad: list[str] = []
    for line in porcelain(root):
        if len(line) < 4:
            continue
        status = line[:2]
        path = line[3:]
        if not path.startswith("raw/"):
            continue
        if status == "??":
            if args.include_untracked:
                bad.append(line)
            continue
        if "M" in status or "D" in status or "R" in status:
            bad.append(line)

    if bad:
        print("Tracked raw/ changes detected. Ingest should not modify raw files:", file=sys.stderr)
        for item in bad:
            print(f"- {item}", file=sys.stderr)
        return 1

    print("no tracked raw/ modifications or deletions detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
