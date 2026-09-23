from __future__ import annotations

from pathlib import Path

import pytest

from research_agent.evaluator.dataset import load_questions
from research_agent.evaluator.runner import (
    EvaluationCaseOutcome,
    EvaluationRunner,
)
from research_agent.storage.evaluation_repository import EvaluationRepository
from research_agent.storage.migrations import apply_migrations, connect_database

FIXTURE = Path(__file__).parents[1] / "fixtures" / "evaluation_questions.jsonl"


@pytest.mark.asyncio
async def test_evaluation_runner_executes_full_case_matrix(tmp_path: Path) -> None:
    db_path = tmp_path / "evaluation.db"
    apply_migrations(db_path)
    calls: list[tuple[str, str, int]] = []

    async def run_case(question_id: str, system_id: str, run_number: int) -> EvaluationCaseOutcome:
        calls.append((question_id, system_id, run_number))
        return EvaluationCaseOutcome(
            research_run_id=None,
            metrics={"Task Completion Rate": 1.0, "Evidence Compliance Rate": 0.8},
        )

    with connect_database(db_path) as conn:
        repository = EvaluationRepository(conn)
        runner = EvaluationRunner(repository)
        summary = await runner.run(
            questions=load_questions(FIXTURE),
            systems=("B3", "B1"),
            repeats=2,
            run_case=run_case,
            dataset_version="pilot-v1",
            system_version="test-version",
            config={"temperature": 0},
        )

        assert summary.status == "completed"
        assert summary.case_count == 8
        assert len(calls) == 8
        assert conn.execute("SELECT COUNT(*) FROM evaluation_case").fetchone()[0] == 8
        assert conn.execute("SELECT COUNT(*) FROM evaluation_result").fetchone()[0] == 16
        assert conn.execute(
            "SELECT status FROM evaluation_run WHERE id = ?", (summary.evaluation_run_id,)
        ).fetchone()[0] == "completed"
