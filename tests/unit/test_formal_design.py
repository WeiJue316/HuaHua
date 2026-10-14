import pytest

from research_agent.evaluator.formal_design import (
    FORMAL_V1_DOMAIN_QUOTAS,
    FORMAL_V1_QUESTION_TYPES,
    FormalDesignError,
    validate_formal_records,
)


def _records() -> list[dict[str, object]]:
    domains: list[str] = []
    for domain, count in FORMAL_V1_DOMAIN_QUOTAS.items():
        domains.extend([domain] * count)
    types = [question_type for question_type in FORMAL_V1_QUESTION_TYPES for _ in range(5)]
    records: list[dict[str, object]] = []
    for index, (domain, question_type) in enumerate(zip(domains, types, strict=True), start=1):
        records.append(
            {
                "question_id": f"formal_{index:03d}",
                "question": f"Question {index}",
                "subquestions": ["What is known?", "What is still open?"],
                "domain": domain,
                "question_type": question_type,
                "year_range": [2022, 2026],
                "gold_papers": [],
                "gold_evidence": [],
            }
        )
    return records


def test_formal_v1_design_accepts_thirty_unannotated_questions() -> None:
    validate_formal_records(_records(), require_gold=False)


def test_formal_v1_design_rejects_a_shifted_domain_quota() -> None:
    records = _records()
    records[0]["domain"] = "datasets_repro"

    with pytest.raises(FormalDesignError, match="llm_rag"):
        validate_formal_records(records)


def test_formal_v1_design_rejects_gold_that_misses_a_subquestion() -> None:
    records = _records()
    records[0]["gold_papers"] = [f"doi:10.1000/paper{i}" for i in range(5)]
    records[0]["gold_evidence"] = [
        {"paper_key": "doi:10.1000/paper0", "supports_subquestion": 1}
    ]

    with pytest.raises(FormalDesignError, match="formal_001"):
        validate_formal_records(records, require_gold=True)
