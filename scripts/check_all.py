#!/usr/bin/env python3
"""Run the same verification steps as CI, locally, in one command.

Usage:
    uv run python scripts/check_all.py

Every step below mirrors a step in .github/workflows/ci.yml, so a green local
run means the CI job is expected to be green as well.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS: list[tuple[str, list[str]]] = [
    ("Check formatting", ["ruff", "check", "."]),
    ("Type check", ["mypy", "src"]),
    ("Run tests", ["pytest"]),
    ("Check documentation", ["python", "scripts/check_docs.py"]),
    ("Check CLI", ["research-agent", "--help"]),
]


def run_step(label: str, args: list[str], uv: str) -> int:
    print(f"\n=== {label} ===", flush=True)
    print(f"$ uv {' '.join(args)}", flush=True)
    try:
        completed = subprocess.run(
            [uv, "run", *args],
            cwd=ROOT,
            check=False,
        )
    except OSError as exc:
        print(f"could not start uv: {exc}", file=sys.stderr)
        return 1
    return completed.returncode


def report_git_status() -> None:
    """Report a dirty work tree as a warning; it never fails the run."""

    git = shutil.which("git")
    if git is None:
        return
    print("\n=== Work tree status (informational) ===", flush=True)
    completed = subprocess.run(
        [git, "status", "--short"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        print("git status unavailable")
        return
    if completed.stdout.strip():
        print("work tree is not clean:")
        print(completed.stdout.rstrip())
        print("local runtime data must stay out of Git; review before pushing.")
    else:
        print("work tree is clean")


def main() -> int:
    uv = shutil.which("uv")
    if uv is None:
        print("uv is required: https://docs.astral.sh/uv/", file=sys.stderr)
        return 1

    failures: list[str] = []
    for label, args in STEPS:
        code = run_step(label, args, uv)
        if code != 0:
            failures.append(f"{label} (exit {code})")

    report_git_status()

    print()
    if failures:
        print("CHECK_ALL_FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"CHECK_ALL_OK ({len(STEPS)} steps)")
    return 0


if __name__ == "__main__":
    sys.exit(main())