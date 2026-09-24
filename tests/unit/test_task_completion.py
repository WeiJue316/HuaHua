from __future__ import annotations

import json

import pytest

from research_agent.evaluator.dataset import EvaluationQuestion
from research_agent.evaluator.task_completion import TaskCompletionJudge
from research_agent.llm.gateway import ModelResponse


class JudgeGateway:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls = 0

    async def complete(
        self,
        *,
        prompt_hash: str,
        system: str,
        user: str,
        max_output_tokens: int = 900,
        temperature: float = 0.0,
        json_output: bool = False,
    ) -> ModelResponse:
        del system, user, max_output_tokens, temperature, json_output
        content = self.responses[self.calls]
        self.calls += 1
        return ModelResponse(
            provider="stub",
            model="stub-judge",
            content=content,
            prompt_hash=prompt_hash,
            response_hash=f"judge-{self.calls}",
            input_tokens=10,
            output_tokens=5,
            latency_ms=2,
            finish_reason="stop",
        )


def _question() -> EvaluationQuestion:
    return EvaluationQuestion(
        question_id="csai_test",
        question="How is the method evaluated?",
        subquestions=("Which metrics are used?", "Which datasets are used?"),
    )


@pytest.mark.asyncio
async def test_task_completion_requires_all_subquestions() -> None:
    gateway = JudgeGateway(
        [
            json.dumps(
                {
                    "subquestions": [
                        {"index": 1, "covered": True},
                        {"index": 2, "covered": False},
                    ]
                }
            )
        ]
    )
    judge = TaskCompletionJudge(gateway=gateway, model_call_budget=20)

    result = await judge.evaluate(
        question=_question(),
        report_text="The report covers metrics but not datasets.",
        model_calls_used=5,
    )

    assert result.report_created == 1
    assert result.subquestions_covered == 1
    assert result.coverage_rate == 0.5
    assert result.within_budget == 1
    assert result.task_completion == 0.0
    assert result.judge_failed == 0


@pytest.mark.asyncio
async def test_task_completion_is_one_when_all_checks_pass() -> None:
    gateway = JudgeGateway(
        [
            json.dumps(
                {
                    "subquestions": [
                        {"index": 1, "covered": True},
                        {"index": 2, "covered": True},
                    ]
                }
            )
        ]
    )
    judge = TaskCompletionJudge(gateway=gateway, model_call_budget=20)

    result = await judge.evaluate(
        question=_question(),
        report_text="The report covers both metrics and datasets.",
        model_calls_used=5,
    )

    assert result.coverage_rate == 1.0
    assert result.task_completion == 1.0


@pytest.mark.asyncio
async def test_task_completion_fails_closed_when_judge_is_invalid() -> None:
    gateway = JudgeGateway(["not json", "still not json"])
    judge = TaskCompletionJudge(gateway=gateway, model_call_budget=20)

    result = await judge.evaluate(
        question=_question(),
        report_text="A report exists.",
        model_calls_used=5,
    )

    assert gateway.calls == 2
    assert result.judge_failed == 1
    assert result.task_completion == 0.0


@pytest.mark.asyncio
async def test_task_completion_enforces_model_call_budget() -> None:
    gateway = JudgeGateway(
        [
            json.dumps(
                {
                    "subquestions": [
                        {"index": 1, "covered": True},
                        {"index": 2, "covered": True},
                    ]
                }
            )
        ]
    )
    judge = TaskCompletionJudge(gateway=gateway, model_call_budget=10)

    result = await judge.evaluate(
        question=_question(),
        report_text="A report exists.",
        model_calls_used=11,
    )

    assert result.within_budget == 0
    assert result.task_completion == 0.0