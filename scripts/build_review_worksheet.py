#!/usr/bin/env python3
"""Render a human-review worksheet for an evaluation question set.

Usage:
    uv run python scripts/build_review_worksheet.py
    uv run python scripts/build_review_worksheet.py \
        --dataset evaluation/datasets/pilot_questions.seed.jsonl

The worksheet lists every question with its gold papers and evidence quotes so a
reviewer can accept, edit or drop each item, and records the dataset hash that
must be carried into the frozen dataset's provenance record.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from research_agent.evaluator.dataset import (  # noqa: E402
    DatasetValidationError,
    dataset_hash,
    load_questions,
)

DEFAULT_DATASET = ROOT / "evaluation" / "datasets" / "pilot_questions.seed.jsonl"


def _cell(value: str) -> str:
    """Escape a value for use inside a Markdown table cell."""

    return " ".join(value.replace("|", "\\|").split())


def render_worksheet(dataset_path: Path) -> str:
    """Render the worksheet body for one dataset file."""

    questions = load_questions(dataset_path)
    relative = dataset_path.relative_to(ROOT) if dataset_path.is_relative_to(ROOT) else dataset_path
    lines = [
        "# 评测问题集人工复核工作表",
        "",
        f"- 数据集：`{relative.as_posix()}`",
        f"- 问题数：{len(questions)}",
        f"- 数据集哈希：`{dataset_hash(questions)}`",
        "",
        "复核规则：每道题逐项确认下面的判据，在「决定」处填写 `保留`、`修改` 或 `删除`，",
        "并在「原因」处写明修改内容或删除理由。复核完成后据此生成冻结版数据集，",
        "并把上面的哈希、复核人和日期写进版本记录。",
        "",
        "逐题判据：",
        "",
        "1. 问题属于计算机/AI 领域，表述清晰，存在明确答案。",
        "2. 两个子问题互不重叠，且都能被 gold evidence 覆盖。",
        "3. 年份范围与问题相符。",
        "4. 每篇 gold paper 都真正回答问题，无重复，DOI 可解析。",
        "5. 每条 quote 是摘要中的完整句子，能独立读懂，不是作者名单或残句。",
        "6. `supports_subquestion` 指向正确的子问题编号。",
        "",
        "---",
        "",
    ]

    for index, question in enumerate(questions, start=1):
        year_range = (
            f"{question.year_range[0]}–{question.year_range[1]}"
            if question.year_range
            else "未指定"
        )
        lines.extend(
            [
                f"## {index}. `{question.question_id}`",
                "",
                f"**领域**：`{question.domain or '未指定'}`　**年份范围**：{year_range}",
                "",
                f"**问题**：{question.question}",
                "",
                "**子问题**：",
                "",
            ]
        )
        for sub_index, subquestion in enumerate(question.subquestions, start=1):
            lines.append(f"{sub_index}. {subquestion}")
        if not question.subquestions:
            lines.append("（无）")
        lines.append("")

        if question.notes:
            lines.extend([f"> 生成备注：{question.notes}", ""])

        lines.extend(
            [
                "| # | gold paper | 年份 | 子问题 | quote |",
                "|---:|---|---:|---:|---|",
            ]
        )
        for evidence_index, evidence in enumerate(question.gold_evidence, start=1):
            paper_key = _cell(str(evidence.get("paper_key", "")))
            subquestion = _cell(str(evidence.get("supports_subquestion", "")))
            paper_year = evidence.get("paper_year")
            year_cell = str(paper_year) if paper_year is not None else "未记录"
            quote = _cell(str(evidence.get("quote", "")))
            lines.append(
                f"| {evidence_index} | `{paper_key}` | {year_cell} | {subquestion} "
                f"| {quote} |"
            )
        if not question.gold_evidence:
            lines.append("| — | （无 gold evidence） | — | — | — |")
        lines.extend(
            [
                "",
                "复核判据：",
                "",
                "- [ ] 判据 1：问题清晰且有明确答案",
                "- [ ] 判据 2：子问题互不重叠且都有证据覆盖",
                "- [ ] 判据 3：年份范围合适",
                "- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析",
                "- [ ] 判据 5：每条 quote 是完整可读的句子",
                "- [ ] 判据 6：supports_subquestion 指向正确",
                "",
                "决定：____（保留 / 修改 / 删除）　原因：________________________________",
                "",
                "---",
                "",
            ]
        )

    lines.extend(
        [
            "## 复核签署",
            "",
            "| 字段 | 内容 |",
            "|---|---|",
            "| 复核人 | |",
            "| 复核日期 | |",
            "| 来源数据集哈希 | |",
            "| 冻结版数据集路径 | `evaluation/datasets/pilot_questions.v1.jsonl` |",
            "| 冻结版哈希 | |",
            "| 修改原因汇总 | |",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    dataset_path = args.dataset if args.dataset.is_absolute() else ROOT / args.dataset
    if not dataset_path.is_file():
        print(f"dataset not found: {dataset_path}", file=sys.stderr)
        return 1

    try:
        worksheet = render_worksheet(dataset_path)
    except DatasetValidationError as exc:
        print(f"dataset is invalid: {exc}", file=sys.stderr)
        return 1

    output_path = args.output
    if output_path is None:
        output_path = ROOT / "evaluation" / "review" / f"{dataset_path.stem}.worksheet.md"
    elif not output_path.is_absolute():
        output_path = ROOT / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(worksheet, encoding="utf-8")
    print(f"worksheet: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
