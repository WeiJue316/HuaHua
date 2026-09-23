"""Build a seed Pilot question set from OpenAlex metadata."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import httpx

from research_agent.mcp_servers.common import PaperCandidate
from research_agent.mcp_servers.openalex.client import OpenAlexClient

PILOT_SEEDS: tuple[dict[str, Any], ...] = (
    {
        "question_id": "csai_001",
        "question": (
            "What are the main evaluation methods for "
            "retrieval-augmented generation systems?"
        ),
        "subquestions": [
            "Which metrics are used?",
            "Which datasets and baselines are common?",
        ],
        "domain": "llm_rag",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_002",
        "question": "How do agentic tool-use methods differ in planning and memory design?",
        "subquestions": [
            "How is planning represented?",
            "How is long-term state retained?",
        ],
        "domain": "llm_rag",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_003",
        "question": (
            "What are reported limitations of chain-of-thought prompting "
            "on reasoning benchmarks?"
        ),
        "subquestions": [
            "Which benchmarks expose limitations?",
            "Which failure modes are reported?",
        ],
        "domain": "llm_rag",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_004",
        "question": "How do vision-language models align image and text representations?",
        "subquestions": [
            "Which alignment objectives are used?",
            "How is alignment evaluated?",
        ],
        "domain": "vision_multimodal",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_005",
        "question": "What evaluation benchmarks are used for multimodal retrieval?",
        "subquestions": [
            "Which datasets are used?",
            "Which retrieval metrics are reported?",
        ],
        "domain": "vision_multimodal",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_006",
        "question": "How does dense retrieval compare with sparse retrieval for scientific search?",
        "subquestions": [
            "What are the reported trade-offs?",
            "Which evaluation setups are used?",
        ],
        "domain": "nlp_ir",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_007",
        "question": "What methods are used for query expansion in neural information retrieval?",
        "subquestions": [
            "What are the main query expansion families?",
            "What evidence supports their effectiveness?",
        ],
        "domain": "nlp_ir",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_008",
        "question": "How do parameter-efficient fine-tuning methods reduce training memory?",
        "subquestions": [
            "Which parameter subsets are updated?",
            "What memory and quality trade-offs are reported?",
        ],
        "domain": "ml_systems",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_009",
        "question": "What techniques accelerate transformer inference without retraining?",
        "subquestions": [
            "Which inference-time optimizations are used?",
            "What latency and quality trade-offs are reported?",
        ],
        "domain": "ml_systems",
        "year_range": [2022, 2026],
    },
    {
        "question_id": "csai_010",
        "question": (
            "What reproducibility practices are reported in machine "
            "learning benchmark papers?"
        ),
        "subquestions": [
            "Which artifacts and metadata are shared?",
            "What barriers to reproducibility are reported?",
        ],
        "domain": "datasets_repro",
        "year_range": [2022, 2026],
    },
)


def _first_sentence(value: str | None) -> str | None:
    if not value:
        return None
    normalized = " ".join(value.split())
    sentence = re.split(r"(?<=[.!?])\s+", normalized, maxsplit=1)[0].strip()
    return sentence or None


def paper_to_annotation(paper: PaperCandidate) -> dict[str, Any]:
    """Convert a paper candidate into one gold-evidence annotation."""

    paper_key = (
        f"doi:{paper.doi}"
        if paper.doi
        else f"openalex:{paper.source_record_id}"
    )
    quote = _first_sentence(paper.abstract)
    return {
        "paper_key": paper_key,
        "evidence_level": "abstract",
        "quote": quote,
        "locator": {"section": "Abstract"},
        "supports_subquestion": 1,
    }


async def build_seed_questions(
    client: OpenAlexClient,
    *,
    seeds: Sequence[dict[str, Any]] = PILOT_SEEDS,
    results_per_question: int = 3,
) -> list[dict[str, Any]]:
    """Query OpenAlex and build seed annotations for each question."""

    records: list[dict[str, Any]] = []
    for seed in seeds:
        result = await client.search(
            str(seed["question"]),
            max_results=results_per_question,
        )
        papers = result.papers
        gold_papers = [
            (
                f"doi:{paper.doi}"
                if paper.doi
                else f"openalex:{paper.source_record_id}"
            )
            for paper in papers
        ]
        gold_evidence = [
            paper_to_annotation(paper)
            for paper in papers
            if _first_sentence(paper.abstract) is not None
        ]
        records.append(
            {
                **seed,
                "gold_papers": gold_papers,
                "gold_evidence": gold_evidence,
                "acceptable_answers": [],
                "notes": (
                    "Seed annotation generated from OpenAlex metadata; "
                    "requires human verification before freezing."
                ),
            }
        )
    return records


async def _amain(output_path: Path) -> None:
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        client = OpenAlexClient(http_client=http_client)
        records = await build_seed_questions(client)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    """Generate the Pilot seed JSONL file."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("evaluation/datasets/pilot_questions.seed.jsonl"),
    )
    args = parser.parse_args()
    asyncio.run(_amain(args.output))


if __name__ == "__main__":
    main()
