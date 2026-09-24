"""Load and hash evaluation question datasets."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


class DatasetValidationError(ValueError):
    """Raised when an evaluation dataset is invalid."""


@dataclass(frozen=True)
class EvaluationQuestion:
    """One evaluation question and its annotations."""

    question_id: str
    question: str
    subquestions: tuple[str, ...] = ()
    domain: str = ""
    year_range: tuple[int, int] | None = None
    gold_papers: tuple[str, ...] = ()
    gold_evidence: tuple[dict[str, Any], ...] = ()
    acceptable_answers: tuple[str, ...] = ()
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _parse_question(raw: dict[str, Any]) -> EvaluationQuestion:
    question_id = raw.get("question_id")
    question = raw.get("question")
    if not isinstance(question_id, str) or not question_id:
        raise DatasetValidationError("each question requires a non-empty question_id")
    if not isinstance(question, str) or not question:
        raise DatasetValidationError(f"{question_id} requires a non-empty question")
    year_range = raw.get("year_range")
    parsed_year_range = None
    if (
        isinstance(year_range, list)
        and len(year_range) == 2
        and all(isinstance(value, int) for value in year_range)
    ):
        parsed_year_range = (int(year_range[0]), int(year_range[1]))
    return EvaluationQuestion(
        question_id=question_id,
        question=question,
        subquestions=tuple(str(value) for value in raw.get("subquestions") or []),
        domain=str(raw.get("domain") or ""),
        year_range=parsed_year_range,
        gold_papers=tuple(str(value) for value in raw.get("gold_papers") or []),
        gold_evidence=tuple(
            value for value in raw.get("gold_evidence") or [] if isinstance(value, dict)
        ),
        acceptable_answers=tuple(
            str(value) for value in raw.get("acceptable_answers") or []
        ),
        notes=str(raw["notes"]) if raw.get("notes") is not None else None,
    )


def load_questions(path: Path) -> list[EvaluationQuestion]:
    """Load JSONL evaluation questions and reject duplicate IDs."""

    questions: list[EvaluationQuestion] = []
    seen_ids: set[str] = set()
    for line_number, line in enumerate(
        Path(path).read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DatasetValidationError(
                f"invalid JSON on line {line_number}: {exc}"
            ) from exc
        if not isinstance(raw, dict):
            raise DatasetValidationError(f"line {line_number} must be an object")
        question = _parse_question(raw)
        if question.question_id in seen_ids:
            raise DatasetValidationError(
                f"duplicate question_id: {question.question_id}"
            )
        seen_ids.add(question.question_id)
        questions.append(question)
    if not questions:
        raise DatasetValidationError("dataset contains no questions")
    return questions


def dataset_version_from_path(path: Path) -> str:
    """Return the stable label recorded in evaluation runs for a dataset file."""

    stem = Path(path).stem
    prefix = "pilot_questions."
    if stem.startswith(prefix):
        return "pilot-" + stem.removeprefix(prefix)
    return stem


def dataset_hash(questions: list[EvaluationQuestion]) -> str:
    """Return a stable hash for a frozen question set."""

    payload = json.dumps(
        [question.to_dict() for question in questions],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
