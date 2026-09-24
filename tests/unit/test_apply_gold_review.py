"""Tests for the gold review worksheet parser.

The parser is the risky part: several index-mapping mistakes have already
happened elsewhere in this project, and a silent misread here would attach
evidence to the wrong subquestion.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_gold_review import parse_subquestions, parse_worksheet  # noqa: E402

HEADER = (
    "| # | 年份 | 标题 | 中文标题(机翻) | DOI | 被引 | 关系 | 命中 "
    "| 初审建议 | 判定 | 子问题 | 备注 |"
)
SEPARATOR = "|---:|---:|---|---|---|---:|---|---:|---|---:|---|---|"


def _worksheet(tmp_path: Path, rows: list[str]) -> Path:
    body = "\n".join(
        [
            "# 金标候选：csai_test",
            "",
            "**问题**：A question",
            "",
            HEADER,
            SEPARATOR,
            *rows,
            "",
            "## 记录",
        ]
    )
    path = tmp_path / "worksheet.md"
    path.write_text(body, encoding="utf-8")
    return path


def _row(
    *,
    index: int = 1,
    doi: str = "10.1/example",
    verdict: str = "",
    subquestions: str = "",
) -> str:
    return (
        f"| {index} | 2024 | A title | 一个标题 | `{doi}` | 5 | 引用了种子 "
        f"| 3 | 建议采纳(子问题1) | {verdict} | {subquestions} | 理由 |"
    )


def test_parse_subquestions_accepts_several_notations() -> None:
    assert parse_subquestions("1") == [1]
    assert parse_subquestions("1,2") == [1, 2]
    assert parse_subquestions("1、2") == [1, 2]
    assert parse_subquestions("") == []


def test_parse_worksheet_reads_the_question_id(tmp_path: Path) -> None:
    path = _worksheet(tmp_path, [_row()])

    question_id, rows = parse_worksheet(path)

    assert question_id == "csai_test"
    assert len(rows) == 1
    assert rows[0].doi == "10.1/example"
    assert rows[0].title == "A title"


def test_rejected_rows_are_not_treated_as_accepted(tmp_path: Path) -> None:
    """「不采纳」contains 「采纳」, so the check must test the negation first."""

    path = _worksheet(
        tmp_path,
        [
            _row(index=1, verdict="不采纳"),
            _row(index=2, doi="10.2/x", verdict="采纳", subquestions="1"),
        ],
    )

    _, rows = parse_worksheet(path)

    assert rows[0].accepted is False
    assert rows[1].accepted is True


def test_blank_verdict_is_neither_accepted_nor_rejected(tmp_path: Path) -> None:
    path = _worksheet(tmp_path, [_row(verdict="")])

    _, rows = parse_worksheet(path)

    assert rows[0].verdict == ""
    assert rows[0].accepted is False


def test_accepted_row_carries_its_subquestion(tmp_path: Path) -> None:
    path = _worksheet(
        tmp_path, [_row(verdict="采纳", subquestions="2")]
    )

    _, rows = parse_worksheet(path)

    assert rows[0].subquestions == [2]


def test_doi_backticks_are_stripped(tmp_path: Path) -> None:
    path = _worksheet(tmp_path, [_row(doi="10.48550/arxiv.2312.10997")])

    _, rows = parse_worksheet(path)

    assert rows[0].doi == "10.48550/arxiv.2312.10997"


def test_missing_header_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.md"
    path.write_text("# 金标候选：csai_test\n\nno table here\n", encoding="utf-8")

    with pytest.raises(ValueError, match="候选表"):
        parse_worksheet(path)