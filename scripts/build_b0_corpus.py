#!/usr/bin/env python3
"""Build a self-contained B0 BM25 corpus from frozen OpenAlex cache entries."""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from research_agent.evaluator.bm25 import Bm25Document, Bm25Index  # noqa: E402
from research_agent.evaluator.dataset import dataset_hash, load_questions  # noqa: E402
from research_agent.mcp_servers.cache import ResponseCache  # noqa: E402
from research_agent.mcp_servers.common import PaperCandidate  # noqa: E402
from research_agent.mcp_servers.openalex.parser import (  # noqa: E402
    OpenAlexParseError,
    parse_search_response,
    parse_work,
)
from research_agent.storage.repository import canonical_key  # noqa: E402

DEFAULT_CACHE_DIR = ROOT / "data" / "cache" / "openalex"
DEFAULT_DATASET = ROOT / "evaluation" / "datasets" / "pilot_questions.v2.jsonl"
DEFAULT_OUTPUT = ROOT / "evaluation" / "corpora" / "pilot_v2_b0.jsonl"
DEFAULT_MANIFEST = ROOT / "evaluation" / "corpora" / "pilot_v2_b0.manifest.json"


def extract_papers(payload: dict[str, Any]) -> list[PaperCandidate]:
    """Extract normalized works from either a search or single-work response."""

    if isinstance(payload.get("results"), list):
        try:
            return parse_search_response(json.dumps(payload, ensure_ascii=False))
        except OpenAlexParseError:
            return []
    if isinstance(payload.get("id"), str) and isinstance(
        payload.get("display_name"), str
    ):
        try:
            return [parse_work(payload)]
        except OpenAlexParseError:
            return []
    return []


def _decode_cache_payload(path: Path) -> dict[str, Any] | None:
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
        content = base64.b64decode(stored["content_b64"])
        payload = json.loads(content)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _deduplicate(papers: list[PaperCandidate]) -> dict[str, Bm25Document]:
    documents: dict[str, Bm25Document] = {}
    for paper in papers:
        key = canonical_key(paper)
        candidate = Bm25Document(
            paper_key=key,
            title=paper.title,
            abstract=paper.abstract or "",
            year=paper.year,
            doi=paper.doi,
        )
        previous = documents.get(key)
        if previous is None or len(candidate.abstract) > len(previous.abstract):
            documents[key] = candidate
    return documents


def build_corpus(
    *,
    cache_dir: Path,
    dataset_path: Path,
    output_path: Path,
    manifest_path: Path,
) -> int:
    questions = load_questions(dataset_path)
    papers: list[PaperCandidate] = []
    cache_entries = sorted(cache_dir.glob("*.json"))
    for path in cache_entries:
        payload = _decode_cache_payload(path)
        if payload is not None:
            papers.extend(extract_papers(payload))

    documents = _deduplicate(papers)
    ordered = [documents[key] for key in sorted(documents)]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n".join(
            json.dumps(
                {
                    "paper_key": document.paper_key,
                    "title": document.title,
                    "abstract": document.abstract,
                    "year": document.year,
                    "doi": document.doi,
                },
                ensure_ascii=False,
            )
            for document in ordered
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    corpus = Bm25Index(ordered)
    gold_keys = {key for question in questions for key in question.gold_papers}
    missing = sorted(gold_keys - set(documents))
    manifest = {
        "corpus_version": "pilot-v2-b0",
        "dataset_path": dataset_path.relative_to(ROOT).as_posix(),
        "dataset_hash": dataset_hash(questions),
        "cache_entry_count": len(cache_entries),
        "parsed_paper_count": len(papers),
        "document_count": len(ordered),
        "missing_gold_keys": missing,
        "cache_hash": ResponseCache(cache_dir, ttl_seconds=None).directory_hash(),
        "corpus_hash": corpus.corpus_hash,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 1 if missing else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    return build_corpus(
        cache_dir=args.cache_dir,
        dataset_path=args.dataset,
        output_path=args.output,
        manifest_path=args.manifest,
    )


if __name__ == "__main__":
    sys.exit(main())