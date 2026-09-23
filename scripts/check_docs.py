#!/usr/bin/env python3
"""Run lightweight structural checks over the Markdown documentation."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "data", "reports", "__pycache__"}
REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "docs/PRD.md",
    "docs/architecture.md",
    "docs/mcp-contract.md",
    "docs/data-model.md",
    "docs/evaluation.md",
    "docs/roadmap.md",
    "docs/glossary.md",
    "docs/adr/README.md",
    "docs/references/pi-investigation.md",
]
BANNED_TERMS = {
    "source_describe": "旧工具名；公共工具名应使用 <source>_describe",
    "temporary_path": "旧 ArtifactRef 字段；应使用 artifact_uri",
}
# Review records and frozen data quote historical material verbatim, so the
# terminology rule only applies to the project's own documentation.
TERM_CHECK_SKIP_PARTS = {"evaluation"}
LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def iter_markdown_files():
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        yield path


def read_text(path):
    return path.read_text(encoding="utf-8")


def check_required(errors):
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"missing required file: {rel}")


def check_code_fences(path, text, errors):
    opened = None
    for line_no, line in enumerate(text.splitlines(), 1):
        match = FENCE_RE.match(line)
        if not match:
            continue
        marker = match.group(1)
        if opened is None:
            opened = (marker[0], len(marker), line_no)
        elif marker[0] == opened[0] and len(marker) >= opened[1]:
            opened = None
    if opened is not None:
        errors.append(
            f"{path.relative_to(ROOT)}:{opened[2]}: "
            f"unclosed code fence opened with {opened[0] * opened[1]}"
        )


def check_links(path, text, errors):
    in_fence = False
    for line_no, line in enumerate(text.splitlines(), 1):
        fence = FENCE_RE.match(line)
        if fence:
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for _image, label, target in LINK_RE.findall(line):
            clean = target.strip().strip("<>")
            if not clean or clean.startswith("#"):
                continue
            if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", clean):
                continue
            clean = clean.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            candidate = (path.parent / clean).resolve()
            if not candidate.exists():
                errors.append(
                    f"{path.relative_to(ROOT)}:{line_no}: broken local link [{label}]({target})"
                )


def split_table_row(line):
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    cells = []
    current = []
    escaped = False
    in_code = False
    for char in stripped[1:-1]:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            current.append(char)
            escaped = True
        elif char == "`":
            in_code = not in_code
            current.append(char)
        elif char == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    cells.append("".join(current).strip())
    return cells


def check_tables(path, text, errors):
    in_fence = False
    table_start = None
    expected_columns = None
    for line_no, line in enumerate(text.splitlines(), 1):
        fence = FENCE_RE.match(line)
        if fence:
            in_fence = not in_fence
            table_start = None
            expected_columns = None
            continue
        if in_fence:
            continue
        row = split_table_row(line)
        if row is None:
            table_start = None
            expected_columns = None
            continue
        if expected_columns is None:
            table_start = line_no
            expected_columns = len(row)
        elif len(row) != expected_columns:
            errors.append(
                f"{path.relative_to(ROOT)}:{line_no}: table started at line {table_start} "
                f"has {len(row)} columns, expected {expected_columns}"
            )


def check_terms(path, text, errors):
    if TERM_CHECK_SKIP_PARTS & set(path.relative_to(ROOT).parts):
        return
    for line_no, line in enumerate(text.splitlines(), 1):
        for term, reason in BANNED_TERMS.items():
            if term in line:
                errors.append(
                    f"{path.relative_to(ROOT)}:{line_no}: outdated term '{term}': {reason}"
                )


def check_adr_numbers(errors):
    adr_dir = ROOT / "docs" / "adr"
    numbers = []
    for path in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
        numbers.append(int(path.name[:4]))
    if numbers != list(range(1, len(numbers) + 1)):
        errors.append(f"ADR numbering is not continuous: {numbers}")


def main():
    errors = []
    check_required(errors)
    files = list(iter_markdown_files())
    for path in files:
        text = read_text(path)
        check_code_fences(path, text, errors)
        check_links(path, text, errors)
        check_tables(path, text, errors)
        check_terms(path, text, errors)
    check_adr_numbers(errors)

    if errors:
        print("DOC_CHECKS_FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"ALL_DOC_CHECKS_OK ({len(files)} Markdown files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())