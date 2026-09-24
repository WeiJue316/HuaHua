#!/usr/bin/env python3
"""Build a frozen multi-source candidate snapshot for controlled evaluation."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections import Counter
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from research_agent.evaluator.dataset import dataset_hash, load_questions  # noqa: E402
from research_agent.evaluator.snapshot import SourceSnapshot  # noqa: E402
from research_agent.mcp_servers.cache import ResponseCache  # noqa: E402
from research_agent.mcp_servers.common import PaperCandidate  # noqa: E402
from research_agent.planner.planner import plan_research  # noqa: E402
from research_agent.router.federation import search_sources  # noqa: E402
from research_agent.router.registry import build_source_clients  # noqa: E402
from research_agent.storage.repository import canonical_key  # noqa: E402

DEFAULT_DATASET = ROOT / "evaluation" / "datasets" / "pilot_questions.v2.jsonl"
DEFAULT_OUTPUT = ROOT / "evaluation" / "snapshots" / "pilot_v2_three_source.jsonl"
DEFAULT_MANIFEST = (
    ROOT / "evaluation" / "snapshots" / "pilot_v2_three_source.manifest.json"
)
DEFAULT_CACHE = ROOT / "data" / "cache" / "source-snapshot"
DEFAULT_SOURCES = ("openalex", "crossref", "semantic_scholar")


def _write_snapshot(path: Path, papers: list[PaperCandidate]) -> None:
    ordered = sorted(papers, key=lambda paper: (paper.source, canonical_key(paper)))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            json.dumps(paper.model_dump(mode="json"), ensure_ascii=False)
            for paper in ordered
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


async def build_snapshot(args: argparse.Namespace) -> int:
    questions = load_questions(args.dataset)
    sources = tuple(args.sources)
    cache = ResponseCache(args.cache_dir, ttl_seconds=None)
    papers: dict[tuple[str, str], PaperCandidate] = {}
    source_counts: Counter[str] = Counter()
    errors: dict[str, str] = {}

    async with httpx.AsyncClient(timeout=60.0) as http_client:
        clients = build_source_clients(http_client, sources, cache=cache)
        for question in questions:
            plan = plan_research(
                question.question,
                available_sources=sources,
                max_results_per_source=args.per_source,
                max_sources=len(sources),
            )
            result = await search_sources(
                clients,
                query=question.question,
                query_variants=(*plan.query_variants, *question.subquestions),
                max_results_per_source=args.per_source,
                max_concurrency=plan.max_concurrency,
            )
            for paper in result.papers:
                key = (paper.source, canonical_key(paper))
                papers[key] = paper
                source_counts[paper.source] += 1
            for source, message in result.errors.items():
                errors[source] = message
            print(
                f"{question.question_id}: {result.source_counts} "
                f"errors={result.errors}"
            )

    ordered = [
        papers[key] for key in sorted(papers, key=lambda item: (item[0], item[1]))
    ]
    _write_snapshot(args.output, ordered)
    snapshot = SourceSnapshot.from_jsonl(args.output)
    manifest = {
        "snapshot_version": "pilot-v2-three-source-v1",
        "dataset_path": args.dataset.relative_to(ROOT).as_posix(),
        "dataset_hash": dataset_hash(questions),
        "sources": list(sources),
        "per_source_limit": args.per_source,
        "document_count": len(ordered),
        "documents_by_source": dict(sorted(source_counts.items())),
        "source_errors": errors,
        "cache_hash": cache.directory_hash(),
        "snapshot_hash": snapshot.snapshot_hash,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument(
        "--sources",
        nargs="+",
        default=list(DEFAULT_SOURCES),
        help="Source IDs to include.",
    )
    parser.add_argument("--per-source", type=int, default=50)
    args = parser.parse_args()
    return asyncio.run(build_snapshot(args))


if __name__ == "__main__":
    sys.exit(main())