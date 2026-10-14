"""Baseline-neutral Task Completion Rate judgement."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from typing import Any

from research_agent.evaluator.dataset import EvaluationQuestion
from research_agent.llm.gateway import ModelGateway, ModelGatewayError
from research_agent.policy.relevance import RELEVANCE_BATCH_SIZE
from research_agent.storage.repository import sha256_text

_JSON_OBJECT = re.compile(r"\{.*\}", re.S)
PROMPT_VERSION = "task-completion-v1"
# B2's loop allows this many steps, and one extra model call when an action is rejected.
REACT_STEP_LIMIT = 8
REACT_ACTION_RETRIES = 1


def estimated_model_call_budget(
    *,
    k: int,
    source_count: int,
    relevance_filter: bool,
    synthesis: bool,
    react: bool = False,
) -> int:
    """Upper bound on system model calls for one case.

    A relevance judgement is one model call per batch of papers, and each
    source keeps at most K papers. Synthesis is one call. The ReAct baseline
    may call the model once per step plus one retry after a rejected action.
    A system that uses none of these still makes one summary call.
    """

    if k < 1:
        raise ValueError("k must be at least 1")
    if source_count < 0:
        raise ValueError("source_count must not be negative")
    calls = 0
    if relevance_filter:
        papers = k * max(source_count, 1)
        calls += math.ceil(papers / RELEVANCE_BATCH_SIZE)
    if synthesis:
        calls += 1
    if react:
        calls += REACT_STEP_LIMIT * (REACT_ACTION_RETRIES + 1)
    return calls or 1

SYSTEM_PROMPT = """You evaluate whether a research report covers the requested subquestions.

Judge coverage only from the supplied report. A subquestion is covered only
when the report contains a substantive answer, not merely the same words or a
promise to investigate it later. Do not require citations or an evidence chain;
this metric is baseline-neutral.

Return JSON only:
{"subquestions":[{"index":1,"covered":true,"reason":"<short reason>"}, ...]}
Every supplied subquestion must appear exactly once."""


@dataclass(frozen=True)
class TaskCompletionResult:
    """Checklist components for one evaluation case."""

    report_created: int
    subquestions_total: int
    subquestions_covered: int
    coverage_rate: float
    within_budget: int
    judge_failed: int
    task_completion: float | None

    def to_dict(self) -> dict[str, float]:
        payload = {
            "report_created": float(self.report_created),
            "subquestions_total": float(self.subquestions_total),
            "subquestions_covered": float(self.subquestions_covered),
            "subquestion_coverage_rate": float(self.coverage_rate),
            "within_model_budget": float(self.within_budget),
            "task_completion_judge_failed": float(self.judge_failed),
            "task_completion_included": 0.0 if self.task_completion is None else 1.0,
        }
        if self.task_completion is not None:
            payload["task_completion"] = float(self.task_completion)
        return payload


class TaskCompletionJudge:
    """Compute the baseline-neutral Task Completion checklist for one case."""

    def __init__(
        self,
        *,
        gateway: ModelGateway,
        model_call_budget: int | None = None,
        max_attempts: int = 2,
    ) -> None:
        if model_call_budget is not None and model_call_budget < 1:
            raise ValueError("model_call_budget must be at least 1")
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self.gateway = gateway
        self.model_call_budget = model_call_budget
        self.max_attempts = max_attempts

    async def evaluate(
        self,
        *,
        question: EvaluationQuestion,
        report_text: str,
        model_calls_used: int,
        model_call_budget: int | None = None,
    ) -> TaskCompletionResult:
        budget = (
            self.model_call_budget
            if model_call_budget is None
            else model_call_budget
        )
        if budget is None or budget < 1:
            raise ValueError("model_call_budget must be at least 1")
        report_created = 1 if report_text.strip() else 0
        within_budget = 1 if 0 <= model_calls_used <= budget else 0
        total = len(question.subquestions)
        if total == 0:
            coverage_rate = 1.0 if report_created else 0.0
            return self._result(
                report_created=report_created,
                total=0,
                covered=0,
                coverage_rate=coverage_rate,
                within_budget=within_budget,
                judge_failed=0,
            )

        covered, failed = await self._judge_coverage(
            question=question,
            report_text=report_text,
        )
        coverage_rate = covered / total if not failed else 0.0
        return self._result(
            report_created=report_created,
            total=total,
            covered=covered,
            coverage_rate=coverage_rate,
            within_budget=within_budget,
            judge_failed=failed,
        )

    async def _judge_coverage(
        self,
        *,
        question: EvaluationQuestion,
        report_text: str,
    ) -> tuple[int, int]:
        subquestion_block = "\n".join(
            f"{index}. {text}"
            for index, text in enumerate(question.subquestions, start=1)
        )
        report = report_text.strip()
        if len(report) > 12000:
            report = report[:12000].rstrip() + "..."
        user = (
            f"Research question:\n{question.question}\n\n"
            f"Subquestions:\n{subquestion_block}\n\n"
            f"Report:\n{report}"
        )
        for _ in range(self.max_attempts):
            try:
                response = await self.gateway.complete(
                    prompt_hash=sha256_text(PROMPT_VERSION + "\x00" + user),
                    system=SYSTEM_PROMPT,
                    user=user,
                    max_output_tokens=1200,
                    json_output=True,
                )
            except ModelGatewayError:
                continue
            if response.truncated:
                continue
            match = _JSON_OBJECT.search(response.content or "")
            if match is None:
                continue
            try:
                payload: Any = json.loads(match.group(0))
            except json.JSONDecodeError:
                continue
            covered = self._parse_subquestion_coverage(
                payload=payload,
                expected=len(question.subquestions),
            )
            if covered is None:
                continue
            return covered, 0
        return 0, 1

    @staticmethod
    def _parse_subquestion_coverage(
        *,
        payload: Any,
        expected: int,
    ) -> int | None:
        if not isinstance(payload, dict):
            return None
        rows = payload.get("subquestions")
        if not isinstance(rows, list):
            return None
        seen: dict[int, bool] = {}
        for row in rows:
            if not isinstance(row, dict):
                return None
            index = row.get("index")
            covered = row.get("covered")
            if not isinstance(index, int) or not isinstance(covered, bool):
                return None
            if index < 1 or index > expected or index in seen:
                return None
            seen[index] = covered
        if set(seen) != set(range(1, expected + 1)):
            return None
        return sum(1 for covered in seen.values() if covered)

    @staticmethod
    def _result(
        *,
        report_created: int,
        total: int,
        covered: int,
        coverage_rate: float,
        within_budget: int,
        judge_failed: int,
    ) -> TaskCompletionResult:
        if judge_failed:
            completed: float | None = None
        else:
            complete = (
                report_created == 1
                and within_budget == 1
                and coverage_rate >= 1.0
            )
            completed = 1.0 if complete else 0.0
        return TaskCompletionResult(
            report_created=report_created,
            subquestions_total=total,
            subquestions_covered=covered,
            coverage_rate=coverage_rate,
            within_budget=within_budget,
            judge_failed=judge_failed,
            task_completion=completed,
        )