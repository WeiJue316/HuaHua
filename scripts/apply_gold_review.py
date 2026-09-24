#!/usr/bin/env python3
"""读取填好的候选复核表，把采纳的论文写进数据集。

用法：

    # 先看会做什么（不写文件）
    uv run python scripts/apply_gold_review.py \
        --worksheet evaluation/review/gold-candidates-csai_007.md --dry-run

    # 确认无误后落库
    uv run python scripts/apply_gold_review.py \
        --worksheet evaluation/review/gold-candidates-csai_007.md

    # 一次处理多份
    uv run python scripts/apply_gold_review.py --worksheet-dir evaluation/review

你只需要在表里填两栏：

    判定    填「采纳」或「不采纳」
    子问题  采纳时填编号，如 1、2、或 1,2；不采纳留空

脚本会替你做的事：

    · 按 DOI 去 OpenAlex 取题录与摘要
    · 校验年份是否在题目的 year_range 内
    · 校验复核表里的逐字引文确实出现在摘要中
    · 去重、追加到 gold_papers 与 gold_evidence

脚本**不会**替你做的事：

    · 判断论文是否该采纳（那是标注，不是脚本的职责）
    · 在摘要抽不出可用句子时编造引文——这种情况会列出来让你手工补
    · 接受没有可核验引文的「采纳」行——这类行会安全地跳过

注意：数据集里的 paper_key 是 `doi:...` 形式，且年份校验使用题目自带的
`year_range`，与复核表里显示的年份可能因数据源更新而不同，脚本以数据集为准。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from research_agent.evaluator.pilot_seed import (  # noqa: E402
    match_terms,
    paper_key,
    paper_to_annotation,
    within_year_range,
)
from research_agent.mcp_servers.cache import (  # noqa: E402
    DEFAULT_TTL_SECONDS,
    ResponseCache,
)
from research_agent.router.registry import build_openalex_client  # noqa: E402

DEFAULT_DATASET = ROOT / "evaluation" / "datasets" / "pilot_questions.v2.jsonl"

# 复核表的列顺序，与 expand_gold_candidates.py 生成的表头一致
COL_INDEX = 0
COL_YEAR = 1
COL_TITLE = 2
COL_DOI = 4
COL_VERDICT = 9
COL_SUBQUESTION = 10
COL_NOTES = 11

ACCEPT = "采纳"
REJECT = "不采纳"
AUDIT_QUOTE = re.compile(r"引文[｜|](.+?)[｜|]理由[｜|]", re.S)


def parse_audit_quote(notes: str) -> str:
    """从备注栏取出模型逐字摘出的审计引文。"""

    match = AUDIT_QUOTE.search(notes)
    return match.group(1).strip() if match else ""


@dataclass
class ReviewRow:
    """复核表里的一行。"""

    line_number: int
    title: str
    doi: str
    verdict: str
    subquestions: list[int] = field(default_factory=list)
    audit_quote: str = ""

    @property
    def accepted(self) -> bool:
        # 注意「不采纳」也含有「采纳」两个字，必须先判否定
        text = self.verdict.strip()
        if text.startswith(REJECT):
            return False
        return text.startswith(ACCEPT)


def parse_verdict(text: str) -> str:
    return text.strip()


def parse_subquestions(text: str) -> list[int]:
    """从「1」「2」「1,2」这类写法里取出编号。"""

    return sorted({int(n) for n in re.findall(r"\d+", text)})


def parse_worksheet(path: Path) -> tuple[str, list[ReviewRow]]:
    """解析工作表，返回 (question_id, 行列表)。"""

    lines = path.read_text(encoding="utf-8").splitlines()
    question_id = ""
    for line in lines:
        if line.startswith("# 金标候选："):
            question_id = line.split("：", 1)[1].strip()
            break
    if not question_id:
        raise ValueError(f"工作表缺少标题行：{path}")

    header_index = next(
        (i for i, line in enumerate(lines) if line.startswith("| # |")), None
    )
    if header_index is None:
        raise ValueError(f"工作表缺少候选表：{path}")

    rows: list[ReviewRow] = []
    for offset, line in enumerate(lines[header_index + 2 :], start=header_index + 3):
        if not line.startswith("| "):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) <= COL_SUBQUESTION:
            continue
        doi = cells[COL_DOI].strip("`").strip()
        if not doi:
            continue
        rows.append(
            ReviewRow(
                line_number=offset,
                title=cells[COL_TITLE],
                doi=doi,
                verdict=parse_verdict(cells[COL_VERDICT]),
                subquestions=parse_subquestions(cells[COL_SUBQUESTION]),
                audit_quote=parse_audit_quote(
                    cells[COL_NOTES] if len(cells) > COL_NOTES else ""
                ),
            )
        )
    return question_id, rows


def read_rows(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    payload = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n"
    path.write_text(payload, encoding="utf-8")


async def apply_worksheet(
    *,
    client: object,
    dataset_path: Path,
    worksheet_path: Path,
    dry_run: bool,
) -> tuple[int, list[str]]:
    """把一份复核表应用到数据集，返回 (新增条数, 提示信息)。"""

    question_id, review_rows = parse_worksheet(worksheet_path)
    dataset_rows = read_rows(dataset_path)
    target = next(
        (r for r in dataset_rows if r.get("question_id") == question_id), None
    )
    if target is None:
        raise ValueError(f"数据集里没有 {question_id}")

    gold_papers: list[str] = list(target.get("gold_papers") or [])  # type: ignore[arg-type]
    gold_evidence: list[dict[str, object]] = list(
        target.get("gold_evidence") or []  # type: ignore[arg-type]
    )
    known = set(gold_papers)
    subquestions: list[str] = list(target.get("subquestions") or [])  # type: ignore[arg-type]
    year_range = target.get("year_range")
    parsed_range = (
        (int(year_range[0]), int(year_range[1]))
        if isinstance(year_range, list) and len(year_range) == 2
        else None
    )

    added = 0
    notes: list[str] = []

    for row in review_rows:
        if not row.verdict:
            continue
        if not row.accepted:
            continue
        if not row.subquestions:
            notes.append(
                f"第 {row.line_number} 行标记为采纳但子问题栏为空：{row.doi}"
            )
            continue
        invalid = [n for n in row.subquestions if not 1 <= n <= len(subquestions)]
        if invalid:
            notes.append(
                f"第 {row.line_number} 行子问题编号越界 {invalid}"
                f"（该题只有 {len(subquestions)} 个）：{row.doi}"
            )
            continue

        paper = await client.get_work_by_doi(row.doi)  # type: ignore[attr-defined]
        if paper is None:
            notes.append(f"第 {row.line_number} 行 OpenAlex 查无此 DOI：{row.doi}")
            continue
        key = paper_key(paper)
        if not within_year_range(paper, parsed_range):
            notes.append(
                f"第 {row.line_number} 行年份 {paper.year} 超出 "
                f"{parsed_range}：{key}"
            )
            continue

        if not row.audit_quote:
            notes.append(
                f"第 {row.line_number} 行标记为采纳但没有可核验引文：{key}"
            )
            continue

        existing_subquestions = {
            int(item["supports_subquestion"])
            for item in gold_evidence
            if item.get("paper_key") == key
            and isinstance(item.get("supports_subquestion"), int)
        }
        annotations: list[dict[str, object]] = []
        for sub_index in row.subquestions:
            if sub_index in existing_subquestions:
                continue
            annotation = paper_to_annotation(
                paper,
                supports_subquestion=sub_index,
                prefer_terms=match_terms(subquestions[sub_index - 1]),
                evidence_quote=row.audit_quote,
            )
            if annotation is None:
                notes.append(
                    f"第 {row.line_number} 行引文无法通过摘要逐字核验"
                    f"（子问题 {sub_index}）：{key}"
                )
                annotations = []
                break
            annotations.append(annotation)

        if not annotations:
            continue

        if key not in known:
            gold_papers.append(key)
            known.add(key)
        gold_evidence.extend(annotations)
        added += len(annotations)

    if added and not dry_run:
        target["gold_papers"] = gold_papers
        target["gold_evidence"] = gold_evidence
        write_rows(dataset_path, dataset_rows)

    return added, notes


async def main_async(args: argparse.Namespace) -> int:
    worksheets: list[Path] = []
    if args.worksheet:
        worksheets.append(args.worksheet)
    if args.worksheet_dir:
        worksheets.extend(sorted(args.worksheet_dir.glob("gold-candidates-*.md")))
    if not worksheets:
        print("需要指定 --worksheet 或 --worksheet-dir", file=sys.stderr)
        return 1

    dataset = args.dataset if args.dataset.is_absolute() else ROOT / args.dataset
    if not dataset.is_file():
        print(f"数据集不存在：{dataset}", file=sys.stderr)
        return 1

    ttl = None if args.freeze_cache else DEFAULT_TTL_SECONDS
    cache = ResponseCache(args.cache_dir, ttl_seconds=ttl)
    total_added = 0
    all_notes: list[str] = []

    async with httpx.AsyncClient(timeout=60.0) as http_client:
        client = build_openalex_client(http_client, cache=cache)
        for worksheet in worksheets:
            added, notes = await apply_worksheet(
                client=client,
                dataset_path=dataset,
                worksheet_path=worksheet,
                dry_run=args.dry_run,
            )
            total_added += added
            all_notes.extend(f"{worksheet.stem}：{n}" for n in notes)
            print(f"{worksheet.stem}: 新增 {added} 条")

    print(f"\n合计新增 {total_added} 条" + ("（dry-run，未写入）" if args.dry_run else ""))
    if all_notes:
        print("\n需要你处理的条目：")
        for note in all_notes:
            print(f"  · {note}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--worksheet", type=Path, help="单份复核表")
    parser.add_argument("--worksheet-dir", type=Path, help="包含复核表的目录")
    parser.add_argument("--dry-run", action="store_true", help="只报告，不写数据集")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "data" / "cache" / "openalex")
    parser.add_argument("--freeze-cache", action="store_true", help="缓存不过期")
    args = parser.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())