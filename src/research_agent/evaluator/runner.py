"""Execute evaluation case matrices."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from typing import Any

from research_agent.evaluator.dataset import EvaluationQuestion, dataset_hash
from research_agent.storage.evaluation_repository import EvaluationRepository
from research_agent.storage.repository import utc_now

RunCase = Callable[[str, str, int], Awaitable["EvaluationCaseOutcome"]]


@dataclass(frozen=True)
class EvaluationCaseOutcome:
    """Result returned by one concrete evaluation case run."""

    research_run_id: str | None = None
    metrics: dict[str, float] | None = None
    error_code: str | None = None


@dataclass(frozen=True)
class EvaluationSummary:
    """Aggregate summary of a batch evaluation."""

    evaluation_run_id: str
    status: str
    case_count: int
    failed_count: int
    completed_count: int


class EvaluationRunner:
    """Run systems/questions/repeats and persist every case."""

    def __init__(self, repository: EvaluationRepository) -> None:
        self.repository = repository

    async def run(
        self,
        *,
        questions: Sequence[EvaluationQuestion],
        systems: Sequence[str],
        repeats: int,
        run_case: RunCase,
        dataset_version: str,
        system_version: str,
        config: Any,
    ) -> EvaluationSummary:
        if repeats < 1:
            raise ValueError("repeats must be at least 1")
        evaluation_run_id = self.repository.create_run(
            dataset_version=dataset_version,
            dataset_hash=dataset_hash(list(questions)),
            system_version=system_version,
            config=config,
        )
        self.repository.update_run(
            evaluation_run_id=evaluation_run_id,
            status="running",
        )
        # Release the write lock before running any case: a case runner writes
        # its research run to the same database, and holding an open write
        # transaction here makes every case fail with "database is locked".
        self.repository.connection.commit()
        case_count = 0
        failed_count = 0
        completed_count = 0
        try:
            for system_id in systems:
                for question in questions:
                    for run_number in range(1, repeats + 1):
                        case_id = self.repository.create_case(
                            evaluation_run_id=evaluation_run_id,
                            question_id=question.question_id,
                            system_id=system_id,
                            run_number=run_number,
                        )
                        case_count += 1
                        self.repository.update_case(
                            case_id=case_id,
                            status="running",
                        )
                        self.repository.connection.commit()
                        try:
                            outcome = await run_case(
                                question.question_id,
                                system_id,
                                run_number,
                            )
                        except Exception as exc:
                            failed_count += 1
                            self.repository.update_case(
                                case_id=case_id,
                                status="failed",
                                error_code=f"{type(exc).__name__}: {exc}"[:200],
                            )
                            self.repository.connection.commit()
                            continue
                        if outcome.error_code:
                            failed_count += 1
                            self.repository.update_case(
                                case_id=case_id,
                                status="failed",
                                research_run_id=outcome.research_run_id,
                                error_code=outcome.error_code,
                            )
                            continue
                        for metric_name, metric_value in (outcome.metrics or {}).items():
                            self.repository.record_result(
                                case_id=case_id,
                                metric_name=metric_name,
                                metric_value=metric_value,
                            )
                        completed_count += 1
                        self.repository.update_case(
                            case_id=case_id,
                            status="completed",
                            research_run_id=outcome.research_run_id,
                            metrics=outcome.metrics,
                        )
                        self.repository.connection.commit()
            status = "completed" if failed_count == 0 else "failed"
            self.repository.update_run(
                evaluation_run_id=evaluation_run_id,
                status=status,
                summary={
                    "case_count": case_count,
                    "completed_count": completed_count,
                    "failed_count": failed_count,
                    "finished_at": utc_now(),
                },
                finished_at=utc_now(),
            )
            self.repository.connection.commit()
            return EvaluationSummary(
                evaluation_run_id=evaluation_run_id,
                status=status,
                case_count=case_count,
                failed_count=failed_count,
                completed_count=completed_count,
            )
        except Exception:
            self.repository.update_run(
                evaluation_run_id=evaluation_run_id,
                status="failed",
            )
            self.repository.connection.commit()
            raise
