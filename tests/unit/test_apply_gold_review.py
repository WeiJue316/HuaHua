"""Tests for the gold review worksheet parser.

The parser is the risky part: several index-mapping mistakes have already
happened elsewhere in this project, and a silent misread here would attach
evidence to the wrong subquestion.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_gold_review import (  # noqa: E402
    apply_worksheet,
    parse_audit_quote,
    parse_subquestions,
    parse_worksheet,
)
from expand_gold_candidates import Candidate, render_worksheet  # noqa: E402

from research_agent.evaluator.dataset import EvaluationQuestion  # noqa: E402
from research_agent.mcp_servers.common import OpenAccessInfo, PaperCandidate  # noqa: E402

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
    notes: str = "理由",
) -> str:
    return (
        f"| {index} | 2024 | A title | 一个标题 | `{doi}` | 5 | 引用了种子 "
        f"| 3 | 建议采纳(子问题1) | {verdict} | {subquestions} | {notes} |"
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


def test_parse_audit_quote_reads_the_verified_quote() -> None:
    notes = (
        "引文｜We evaluate on Natural Questions using EM.｜"
        "理由｜The sentence names a dataset and metric."
    )

    assert parse_audit_quote(notes) == "We evaluate on Natural Questions using EM."


class FakeOpenAlexClient:
    def __init__(self, paper: PaperCandidate) -> None:
        self.paper = paper

    async def get_work_by_doi(self, doi: str) -> PaperCandidate | None:
        return self.paper if doi == self.paper.doi else None


def _paper() -> PaperCandidate:
    return PaperCandidate(
        source="openalex",
        source_record_id="W1",
        title="Evaluation methods for retrieval augmented generation",
        abstract=(
            "Retrieval augmented generation systems are widely used. "
            "We evaluate Natural Questions with exact match and F1. "
            "The results show consistent improvements over baselines."
        ),
        doi="10.1/example",
        year=2024,
        landing_url="https://example.org/paper",
        open_access=OpenAccessInfo(is_oa=True, status="gold"),
    )


def _dataset(tmp_path: Path) -> Path:
    path = tmp_path / "pilot.jsonl"
    row = {
        "question_id": "csai_test",
        "question": "Which evaluation methods are used?",
        "subquestions": ["Which metrics are used?", "Which datasets are used?"],
        "domain": "llm_rag",
        "year_range": [2022, 2026],
        "gold_papers": [],
        "gold_evidence": [],
        "acceptable_answers": [],
        "notes": "",
    }
    path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


@pytest.mark.asyncio
async def test_apply_worksheet_preserves_quote_for_both_subquestions(
    tmp_path: Path,
) -> None:
    quote = "We evaluate Natural Questions with exact match and F1."
    worksheet = _worksheet(
        tmp_path,
        [
            _row(
                verdict="采纳",
                subquestions="1,2",
                notes=f"引文｜{quote}｜理由｜Names a dataset and metric.",
            )
        ],
    )
    dataset = _dataset(tmp_path)

    added, notes = await apply_worksheet(
        client=FakeOpenAlexClient(_paper()),
        dataset_path=dataset,
        worksheet_path=worksheet,
        dry_run=False,
    )

    assert added == 2
    assert notes == []
    saved = json.loads(dataset.read_text(encoding="utf-8"))
    assert saved["gold_papers"] == ["doi:10.1/example"]
    assert [item["supports_subquestion"] for item in saved["gold_evidence"]] == [1, 2]
    assert {item["quote"] for item in saved["gold_evidence"]} == {quote}


@pytest.mark.asyncio
async def test_apply_worksheet_skips_an_unverified_accepted_row(
    tmp_path: Path,
) -> None:
    worksheet = _worksheet(
        tmp_path,
        [_row(verdict="采纳", subquestions="1", notes="理由｜No quote.")],
    )
    dataset = _dataset(tmp_path)

    added, notes = await apply_worksheet(
        client=FakeOpenAlexClient(_paper()),
        dataset_path=dataset,
        worksheet_path=worksheet,
        dry_run=False,
    )

    assert added == 0
    assert any("没有可核验引文" in note for note in notes)
    saved = json.loads(dataset.read_text(encoding="utf-8"))
    assert saved["gold_papers"] == []



def test_fill_verdict_leaves_uncertain_rows_blank() -> None:
    question = EvaluationQuestion(
        question_id="csai_test",
        question="Which metrics are used?",
        subquestions=("Which metrics are used?",),
    )
    candidate = Candidate(
        paper=_paper(),
        relation="引用了种子",
        seed_key="doi:10.1/seed",
        topic_overlap=3,
    )

    rendered = render_worksheet(
        question=question,
        candidates=[candidate],
        years=(2022, 2026),
        prescreen={1: ("待人工判断", "")},
        fill_verdict=True,
    )

    row = next(line for line in rendered.splitlines() if line.startswith("| 1 |"))
    cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
    assert cells[8] == "待人工判断"
    assert cells[9] == ""
    assert cells[10] == ""
