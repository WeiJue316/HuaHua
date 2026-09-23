from __future__ import annotations

from pathlib import Path

import pytest

from research_agent.executor.executor import Executor, StepSpec
from research_agent.storage.migrations import apply_migrations, connect_database
from research_agent.storage.repository import ResearchRepository


def _seed_plan(db_path: Path) -> tuple[str, str]:
    apply_migrations(db_path)
    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        project_id = repo.create_project("project")
        question_id = repo.create_research_question(project_id, "question")
        run_id = repo.create_run(project_id, question_id)
        plan_id = repo.record_plan(run_id=run_id, plan_json={"steps": ["one", "two"]})
        conn.commit()
    return run_id, plan_id


@pytest.mark.asyncio
async def test_executor_completes_plan(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    run_id, plan_id = _seed_plan(db_path)
    calls: list[str] = []

    async def first() -> dict[str, bool]:
        calls.append("first")
        return {"ok": True}

    async def second() -> dict[str, bool]:
        calls.append("second")
        return {"ok": True}

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        result = await Executor(repo).execute_plan(
            run_id=run_id,
            plan_id=plan_id,
            steps=[
                StepSpec(step_key="one", step_type="build_query", handler=first),
                StepSpec(
                    step_key="two",
                    step_type="search_sources",
                    depends_on=("one",),
                    handler=second,
                ),
            ],
        )

        assert calls == ["first", "second"]
        assert result.status == "COMPLETED"
        assert conn.execute(
            "SELECT status FROM run WHERE id = ?", (run_id,)
        ).fetchone()[0] == "COMPLETED"
        assert conn.execute(
            "SELECT COUNT(*) FROM plan_step WHERE status = 'SUCCEEDED'"
        ).fetchone()[0] == 2
        assert conn.execute(
            "SELECT COUNT(*) FROM step_attempt WHERE status = 'succeeded'"
        ).fetchone()[0] == 2


@pytest.mark.asyncio
async def test_executor_retries_then_succeeds(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    run_id, plan_id = _seed_plan(db_path)
    attempts = 0

    async def flaky() -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("transient")

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        result = await Executor(repo).execute_plan(
            run_id=run_id,
            plan_id=plan_id,
            steps=[
                StepSpec(step_key="one", step_type="search_sources", handler=flaky)
            ],
            max_attempts=2,
        )

        assert result.status == "COMPLETED"
        assert attempts == 2
        assert conn.execute(
            "SELECT COUNT(*) FROM step_attempt"
        ).fetchone()[0] == 2
        assert conn.execute(
            "SELECT status FROM plan_step WHERE step_key = 'one'"
        ).fetchone()[0] == "SUCCEEDED"


@pytest.mark.asyncio
async def test_executor_marks_run_failed_after_retry_budget(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    run_id, plan_id = _seed_plan(db_path)

    async def always_fails() -> None:
        raise RuntimeError("persistent")

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        result = await Executor(repo).execute_plan(
            run_id=run_id,
            plan_id=plan_id,
            steps=[
                StepSpec(
                    step_key="one",
                    step_type="search_sources",
                    handler=always_fails,
                )
            ],
            max_attempts=2,
        )

        assert result.status == "FAILED"
        assert result.failed_step == "one"
        assert conn.execute(
            "SELECT COUNT(*) FROM step_attempt"
        ).fetchone()[0] == 2
        assert conn.execute(
            "SELECT status FROM run WHERE id = ?", (run_id,)
        ).fetchone()[0] == "FAILED"
