from __future__ import annotations

from pathlib import Path

import pytest

from research_agent.evaluator.dataset import (
    DatasetValidationError,
    dataset_hash,
    dataset_version_from_path,
    load_questions,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "evaluation_questions.jsonl"


def test_load_questions_and_hash_are_stable() -> None:
    questions = load_questions(FIXTURE)

    assert len(questions) == 2
    assert questions[0].question_id == "csai_001"
    assert questions[0].subquestions == (
        "Which metrics are used?",
        "Which datasets are common?",
    )
    assert questions[0].year_range == (2022, 2026)
    assert dataset_hash(questions) == dataset_hash(load_questions(FIXTURE))


def test_load_questions_rejects_duplicate_ids(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.jsonl"
    content = FIXTURE.read_text(encoding="utf-8").splitlines()
    duplicate.write_text("\n".join([content[0], content[0]]) + "\n", encoding="utf-8")

    with pytest.raises(DatasetValidationError, match="duplicate"):
        load_questions(duplicate)


def test_dataset_version_is_derived_from_the_frozen_filename() -> None:
    assert (
        dataset_version_from_path(Path("evaluation/datasets/pilot_questions.v2.jsonl"))
        == "pilot-v2"
    )
    assert dataset_version_from_path(Path("custom.jsonl")) == "custom"
