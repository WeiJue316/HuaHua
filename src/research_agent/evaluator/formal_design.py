"""Frozen design of the formal 30-question set.

The design is fixed here. The annotated file is not created until every
question has gold evidence. Pilot files stay unchanged.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

FORMAL_V1_SIZE = 30
FORMAL_V1_SUBQUESTION_COUNT = 2
FORMAL_V1_YEAR_RANGE = (2022, 2026)
FORMAL_V1_MIN_GOLD_PAPERS = 5
FORMAL_V1_DOMAIN_QUOTAS = {
    "llm_rag": 9,
    "vision_multimodal": 6,
    "nlp_ir": 6,
    "ml_systems": 5,
    "datasets_repro": 4,
}
FORMAL_V1_QUESTION_TYPES = (
    "method_survey",
    "comparison",
    "trend",
    "dataset",
    "reproducibility",
    "counterexample",
)


class FormalDesignError(ValueError):
    """Raised when a record set does not match the formal v1 design."""


def validate_formal_records(
    records: Sequence[Mapping[str, Any]],
    *,
    require_gold: bool = False,
) -> None:
    """Check quotas, identifiers, and, when requested, gold coverage."""

    if len(records) != FORMAL_V1_SIZE:
        raise FormalDesignError(
            f"expected {FORMAL_V1_SIZE} questions, found {len(records)}"
        )
    domains: Counter[str] = Counter()
    question_types: Counter[str] = Counter()
    for index, record in enumerate(records, start=1):
        question_id = f"formal_{index:03d}"
        if record.get("question_id") != question_id:
            raise FormalDesignError(
                f"{question_id} is missing or out of order"
            )
        question = record.get("question")
        if not isinstance(question, str) or not question.strip():
            raise FormalDesignError(f"{question_id} requires a question")
        _require_subquestions(question_id, record.get("subquestions"))
        domain = record.get("domain")
        if domain not in FORMAL_V1_DOMAIN_QUOTAS:
            raise FormalDesignError(f"{question_id} has an unknown domain")
        domains[str(domain)] += 1
        question_type = record.get("question_type")
        if question_type not in FORMAL_V1_QUESTION_TYPES:
            raise FormalDesignError(f"{question_id} has an unknown question_type")
        question_types[str(question_type)] += 1
        if record.get("year_range") != list(FORMAL_V1_YEAR_RANGE):
            raise FormalDesignError(f"{question_id} year_range must be [2022, 2026]")
        if require_gold:
            _require_gold(question_id, record)
    for domain, quota in FORMAL_V1_DOMAIN_QUOTAS.items():
        if domains[domain] != quota:
            raise FormalDesignError(f"{domain} quota is {quota}, found {domains[domain]}")
    for question_type in FORMAL_V1_QUESTION_TYPES:
        if question_types[question_type] != 5:
            raise FormalDesignError(
                f"{question_type} quota is 5, found {question_types[question_type]}"
            )


def _require_subquestions(question_id: str, subquestions: object) -> None:
    if (
        not isinstance(subquestions, list)
        or len(subquestions) != FORMAL_V1_SUBQUESTION_COUNT
        or any(not isinstance(item, str) or not item.strip() for item in subquestions)
    ):
        raise FormalDesignError(f"{question_id} requires exactly two subquestions")


def _require_gold(question_id: str, record: Mapping[str, Any]) -> None:
    papers = record.get("gold_papers")
    if (
        not isinstance(papers, list)
        or len(papers) < FORMAL_V1_MIN_GOLD_PAPERS
        or any(not isinstance(item, str) or not item.strip() for item in papers)
    ):
        raise FormalDesignError(
            f"{question_id} requires at least {FORMAL_V1_MIN_GOLD_PAPERS} gold papers"
        )
    evidence = record.get("gold_evidence")
    if not isinstance(evidence, list):
        raise FormalDesignError(f"{question_id} requires gold evidence")
    supported = {
        item.get("supports_subquestion")
        for item in evidence
        if isinstance(item, dict)
    }
    if not {1, 2} <= supported:
        raise FormalDesignError(f"{question_id} has a subquestion without gold evidence")
