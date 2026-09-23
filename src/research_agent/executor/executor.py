"""Minimal PlanStep executor with bounded retries."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from typing import Any

from research_agent.storage.repository import ResearchRepository, utc_now

StepHandler = Callable[[], Awaitable[Any]]


@dataclass(frozen=True)
class StepSpec:
    """One executable plan step."""

    step_key: str
    step_type: str
    handler: StepHandler
    depends_on: tuple[str, ...] = ()
    input_json: Any | None = None


@dataclass(frozen=True)
class ExecutionResult:
    """Outcome of executing a plan."""

    status: str
    completed_steps: tuple[str, ...]
    failed_step: str | None = None


class Executor:
    """Execute plan steps and persist every attempt."""

    def __init__(self, repository: ResearchRepository) -> None:
        self.repository = repository

    async def execute_plan(
        self,
        *,
        run_id: str,
        plan_id: str,
        steps: Sequence[StepSpec],
        max_attempts: int = 3,
    ) -> ExecutionResult:
        """Execute steps in order, retrying transient failures."""

        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self.repository.update_run_status(run_id=run_id, status="RUNNING")
        self.repository.connection.commit()

        completed: list[str] = []
        completed_keys: set[str] = set()
        for step in steps:
            missing_dependencies = [
                dependency
                for dependency in step.depends_on
                if dependency not in completed_keys
            ]
            if missing_dependencies:
                raise ValueError(
                    f"step {step.step_key} has unresolved dependencies: "
                    f"{missing_dependencies}"
                )

            step_id = self.repository.record_plan_step(
                plan_id=plan_id,
                step_key=step.step_key,
                step_type=step.step_type,
                depends_on=list(step.depends_on),
                status="READY",
                input_json=step.input_json,
            )
            self.repository.update_plan_step_status(
                step_id=step_id,
                status="RUNNING",
                attempt_count=0,
                started_at=utc_now(),
            )
            self.repository.connection.commit()

            last_error: Exception | None = None
            for attempt_no in range(1, max_attempts + 1):
                attempt_started_at = utc_now()
                try:
                    output = await step.handler()
                except Exception as exc:
                    last_error = exc
                    error_code = type(exc).__name__
                    self.repository.record_step_attempt(
                        step_id=step_id,
                        attempt_no=attempt_no,
                        status="failed",
                        input_json=step.input_json,
                        error_code=error_code,
                        started_at=attempt_started_at,
                        finished_at=utc_now(),
                    )
                    if attempt_no < max_attempts:
                        self.repository.update_plan_step_status(
                            step_id=step_id,
                            status="RETRYING",
                            attempt_count=attempt_no,
                            error_code=error_code,
                        )
                        self.repository.connection.commit()
                        continue
                    self.repository.update_plan_step_status(
                        step_id=step_id,
                        status="FAILED",
                        attempt_count=attempt_no,
                        error_code=error_code,
                        finished_at=utc_now(),
                    )
                    self.repository.update_run_status(
                        run_id=run_id,
                        status="FAILED",
                        error_code=error_code,
                        finished_at=utc_now(),
                    )
                    self.repository.connection.commit()
                    return ExecutionResult(
                        status="FAILED",
                        completed_steps=tuple(completed),
                        failed_step=step.step_key,
                    )
                else:
                    self.repository.record_step_attempt(
                        step_id=step_id,
                        attempt_no=attempt_no,
                        status="succeeded",
                        input_json=step.input_json,
                        output_json=output,
                        started_at=attempt_started_at,
                        finished_at=utc_now(),
                    )
                    self.repository.update_plan_step_status(
                        step_id=step_id,
                        status="SUCCEEDED",
                        attempt_count=attempt_no,
                        output_json=output,
                        finished_at=utc_now(),
                    )
                    self.repository.connection.commit()
                    completed.append(step.step_key)
                    completed_keys.add(step.step_key)
                    break

            if last_error is not None and step.step_key not in completed_keys:
                raise RuntimeError(
                    f"step {step.step_key} failed without terminal state"
                )

        self.repository.update_run_status(
            run_id=run_id,
            status="COMPLETED",
            finished_at=utc_now(),
        )
        self.repository.connection.commit()
        return ExecutionResult(
            status="COMPLETED",
            completed_steps=tuple(completed),
        )
