#!/usr/bin/env python3
"""Curate gold evidence for the pilot evaluation dataset.

Two modes:

    # 1. look for candidate papers that could answer a subquestion
    uv run python scripts/add_gold_evidence.py --question csai_001 \
        --search "RAG evaluation benchmark datasets baselines"

    # 2. attach a candidate to a subquestion
    uv run python scripts/add_gold_evidence.py --question csai_001 \
        --doi 10.18653/v1/2024.eacl-demo.16 --subquestion 2

The script applies the same rules as the seed builder: the paper must fall
inside the question's year range, and the recorded quote must be a usable
abstract sentence rather than an author list, a container title, or a
fragment. Use --quote to supply a verbatim sentence when the automatic choice
is wrong, and --remove to drop a paper that does not belong.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from research_agent.evaluator.pilot_seed import (  # noqa: E402
    match_terms,
    paper_key,
    paper_to_annotation,
    usable_evidence_sentence,
    within_year_range,
)
from research_agent.mcp_servers.common import PaperCandidate  # noqa: E402
from research_agent.router.registry import build_openalex_client  # noqa: E402

DEFAULT_DATASET = ROOT / "evaluation" / "datasets" / "pilot_questions.seed.jsonl"


def read_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    payload = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n"
    path.write_text(payload, encoding="utf-8")


def find_row(rows: list[dict[str, Any]], question_id: str) -> dict[str, Any]:
    for row in rows:
        if row.get("question_id") == question_id:
            return row
    raise SystemExit(f"unknown question_id: {question_id}")


def uncovered_subquestions(row: dict[str, Any]) -> list[int]:
    covered = {
        int(item["supports_subquestion"])
        for item in row.get("gold_evidence") or []
        if isinstance(item, dict) and "supports_subquestion" in item
    }
    return [
        index
        for index in range(1, len(row.get("subquestions") or []) + 1)
        if index not in covered
    ]


def year_range_of(row: dict[str, Any]) -> tuple[int, int] | None:
    value = row.get("year_range")
    if isinstance(value, list) and len(value) == 2:
        return (int(value[0]), int(value[1]))
    return None


def describe(paper: PaperCandidate, *, quote: str | None) -> str:
    year = paper.year if paper.year is not None else "?"
    lines = [f"  {paper_key(paper)}  ({year})  {paper.title}"]
    if quote:
        lines.append(f"      quote: {quote}")
    return "\n".join(lines)


async def search_mode(
    row: dict[str, Any],
    query: str,
    *,
    limit: int,
    show_all: bool,
) -> int:
    """Print candidate papers for a question so the reviewer can pick one."""

    async with httpx.AsyncClient(timeout=30.0) as http_client:
        client = build_openalex_client(http_client)
        result = await client.search(query, max_results=limit)

    subquestions = row.get("subquestions") or []
    terms = [match_terms(item) for item in subquestions]
    year_range = year_range_of(row)
    existing = set(row.get("gold_papers") or [])

    kept: list[tuple[PaperCandidate, str, int]] = []
    for paper in result.papers:
        if not show_all and not within_year_range(paper, year_range):
            continue
        key = paper_key(paper)
        if key in existing:
            continue
        best_index = 1
        best_score = -1
        for index, group in enumerate(terms):
            quote = usable_evidence_sentence(paper.abstract, prefer_terms=group)
            if quote is None:
                continue
            score = len(group & set(quote.lower().split()))
            if score > best_score:
                best_index, best_score = index + 1, score
        annotation = paper_to_annotation(paper, supports_subquestion=best_index)
        quote = annotation["quote"] if annotation else None
        kept.append((paper, quote or "", best_index))

    print(f"candidates for {row['question_id']} (year_range={year_range}):")
    if not kept:
        print("  none passed the year-range and quote filters; try --show-all")
        return 0
    for paper, quote, best_index in kept:
        print(describe(paper, quote=quote))
        print(f"      suggested subquestion: {best_index}")
    print()
    print("add one with:")
    print(
        "  uv run python scripts/add_gold_evidence.py "
        f"--question {row['question_id']} --doi <DOI> --subquestion <N>"
    )
    return 0


async def add_paper(
    row: dict[str, Any],
    doi: str,
    *,
    subquestion: int,
    quote_override: str | None,
    force: bool,
) -> None:
    """Attach one paper to a subquestion, validating the evidence it carries."""

    subquestions = row.get("subquestions") or []
    if not 1 <= subquestion <= len(subquestions):
        raise SystemExit(
            f"subquestion must be between 1 and {len(subquestions)}"
        )

    async with httpx.AsyncClient(timeout=30.0) as http_client:
        client = build_openalex_client(http_client)
        paper = await client.get_work_by_doi(doi)
    if paper is None:
        raise SystemExit(f"OpenAlex has no record for DOI {doi}")

    year_range = year_range_of(row)
    if not within_year_range(paper, year_range) and not force:
        raise SystemExit(
            f"{paper_key(paper)} is from {paper.year}, outside the declared "
            f"year range {year_range}. Fix the range or pass --force."
        )

    key = paper_key(paper)
    if key in set(row.get("gold_papers") or []):
        raise SystemExit(f"{key} is already part of {row['question_id']}")

    prefer_terms = match_terms(str(subquestions[subquestion - 1]))
    if quote_override:
        quote = quote_override.strip()
    else:
        quote = usable_evidence_sentence(paper.abstract, prefer_terms=prefer_terms)
        if quote is None:
            raise SystemExit(
                "this record has no usable abstract sentence for the "
                "subquestion. Read the paper and pass --quote \"<verbatim "
                "sentence>\"."
            )

    annotation: dict[str, Any] = {
        "paper_key": key,
        "evidence_level": "abstract",
        "quote": quote,
        "locator": {"section": "Abstract"},
        "supports_subquestion": subquestion,
        "paper_year": paper.year,
    }
    row.setdefault("gold_papers", []).append(key)
    row.setdefault("gold_evidence", []).append(annotation)

    print(f"added to {row['question_id']}:")
    print(describe(paper, quote=quote))
    print(f"      supports_subquestion: {subquestion}")


def remove_paper(row: dict[str, Any], key: str) -> None:
    gold_papers = row.get("gold_papers") or []
    if key not in gold_papers:
        raise SystemExit(f"{key} is not part of {row['question_id']}")
    row["gold_papers"] = [item for item in gold_papers if item != key]
    row["gold_evidence"] = [
        item
        for item in row.get("gold_evidence") or []
        if item.get("paper_key") != key
    ]
    print(f"removed {key} from {row['question_id']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--question", required=True, help="question_id, e.g. csai_001")
    parser.add_argument("--search", help="free-text query to look for candidates")
    parser.add_argument("--doi", help="DOI to attach")
    parser.add_argument("--subquestion", type=int, help="1-based subquestion index")
    parser.add_argument("--quote", help="verbatim sentence to record instead")
    parser.add_argument("--remove", help="paper key to drop, e.g. doi:10.1/xyz")
    parser.add_argument("--limit", type=int, default=10, help="search result limit")
    parser.add_argument("--show-all", action="store_true", help="ignore year range in search")
    parser.add_argument("--force", action="store_true", help="allow an out-of-range paper")
    parser.add_argument("--dry-run", action="store_true", help="do not write the dataset")
    args = parser.parse_args()

    dataset = args.dataset if args.dataset.is_absolute() else ROOT / args.dataset
    if not dataset.is_file():
        raise SystemExit(f"dataset not found: {dataset}")

    rows = read_rows(dataset)
    row = find_row(rows, args.question)

    if args.search:
        return asyncio.run(
            search_mode(row, args.search, limit=args.limit, show_all=args.show_all)
        )

    if args.remove:
        remove_paper(row, args.remove)
        added = False
    elif args.doi:
        if args.subquestion is None:
            raise SystemExit("--subquestion is required when attaching a DOI")
        asyncio.run(
            add_paper(
                row,
                args.doi,
                subquestion=args.subquestion,
                quote_override=args.quote,
                force=args.force,
            )
        )
        added = True
    else:
        raise SystemExit("nothing to do: pass --search, --doi or --remove")

    if not args.dry_run:
        write_rows(dataset, rows)
        print(f"\nwrote {dataset}")

    remaining = uncovered_subquestions(row)
    print()
    if remaining:
        print(
            f"{row['question_id']} still has no evidence for subquestion(s): "
            f"{', '.join(str(index) for index in remaining)}"
        )
    else:
        print(f"{row['question_id']} now covers every subquestion")

    if added and args.dry_run:
        print("(dry run: the dataset was not modified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
