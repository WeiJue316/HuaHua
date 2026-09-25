"""B2 baseline: a bounded pure ReAct search/finish loop."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from research_agent.evaluator.dataset import EvaluationQuestion
from research_agent.llm.gateway import ModelGateway, ModelGatewayError, ModelResponse
from research_agent.mcp_servers.common import PaperCandidate
from research_agent.router.federation import SearchClient
from research_agent.storage.repository import canonical_key, sha256_text

_JSON_OBJECT = re.compile(r"\{.*\}", re.S)

REACT_SYSTEM_PROMPT = """You are a research assistant using a ReAct-style tool loop.

You may choose exactly one action per turn:
1. search: search one literature source.
   JSON: {"action":"search","source":"<source>","query":"<query>","max_results":10}
2. finish: submit the final report and stop.
   JSON: {"action":"finish","report":"<report text>"}

Rules:
- Do not invent a plan object or request tools outside the available list.
- Use search observations to decide whether another source or query is useful.
- Stop with finish when you can answer the research question or must report
  that the available evidence is insufficient.
- Return JSON only. Do not wrap it in Markdown fences.
"""


class ReActExecutionError(RuntimeError):
    """Raised when a pure ReAct case cannot produce a valid final action."""


@dataclass(frozen=True)
class ReActOutcome:
    """Artifacts and cost metadata from one B2 case."""

    retrieved_keys: frozenset[str]
    ranked_keys: tuple[str, ...]
    report: str
    report_path: Path
    trace_path: Path
    model_calls: int
    input_tokens: int
    output_tokens: int
    latency_ms: int
    steps_used: int
    search_calls: int
    source_attempts: int
    source_successes: int
    source_failures: int


@dataclass(frozen=True)
class _Action:
    kind: str
    source: str = ""
    query: str = ""
    max_results: int | None = None
    report: str = ""


@dataclass(frozen=True)
class _ActionCall:
    action: _Action
    responses: tuple[ModelResponse, ...]
    rejected: tuple[str, ...] = ()


class PureReActBaseline:
    """Execute a fixed-budget ReAct loop without Planner or Executor state."""

    def __init__(
        self,
        *,
        clients: Mapping[str, SearchClient],
        gateway: ModelGateway,
        reports_root: Path,
        max_steps: int = 8,
        max_results_per_search: int = 10,
        max_action_retries: int = 1,
    ) -> None:
        if not clients:
            raise ValueError("ReAct baseline requires at least one source client")
        if max_steps < 1:
            raise ValueError("max_steps must be at least 1")
        if max_results_per_search < 1:
            raise ValueError("max_results_per_search must be at least 1")
        if max_action_retries < 0:
            raise ValueError("max_action_retries must not be negative")
        self.clients = dict(clients)
        self.gateway = gateway
        self.reports_root = reports_root
        self.max_steps = max_steps
        self.max_results_per_search = max_results_per_search
        self.max_action_retries = max_action_retries

    async def run(
        self,
        question: EvaluationQuestion,
        *,
        run_number: int,
    ) -> ReActOutcome:
        artifact_id = uuid4().hex[:8]
        output_dir = self.reports_root / "b2"
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / (
            f"{question.question_id}-run{run_number}-{artifact_id}.md"
        )
        trace_path = output_dir / (
            f"{question.question_id}-run{run_number}-{artifact_id}.trace.json"
        )

        retrieved: dict[str, PaperCandidate] = {}
        observations: list[str] = []
        trace: list[dict[str, Any]] = []
        model_calls = 0
        input_tokens = 0
        output_tokens = 0
        latency_ms = 0
        search_calls = 0
        source_successes = 0
        source_failures = 0

        try:
            for step in range(1, self.max_steps + 1):
                try:
                    call = await self._next_action(
                        question=question,
                        observations=observations,
                        retrieved=retrieved,
                        step=step,
                    )
                except ReActExecutionError as exc:
                    trace.append(
                        {
                            "step": step,
                            "action": "invalid",
                            "observation": str(exc),
                        }
                    )
                    raise
                for response in call.responses:
                    model_calls += 1
                    input_tokens += response.input_tokens or 0
                    output_tokens += response.output_tokens or 0
                    latency_ms += response.latency_ms or 0
                for rejected in call.rejected:
                    trace.append(
                        {
                            "step": step,
                            "action": "rejected_action",
                            "observation": rejected,
                        }
                    )
                action = call.action

                if action.kind == "search":
                    search_calls += 1
                    observation, new_count, source_ok = await self._run_search(
                        action=action,
                        retrieved=retrieved,
                    )
                    if source_ok:
                        source_successes += 1
                    else:
                        source_failures += 1
                    observations.append(observation)
                    trace.append(
                        {
                            "step": step,
                            "action": "search",
                            "source": action.source,
                            "query": action.query,
                            "new_paper_count": new_count,
                            "observation": observation,
                        }
                    )
                    continue

                report = self._render_report(question, retrieved, action.report)
                report_path.write_text(report, encoding="utf-8", newline="\n")
                trace.append(
                    {
                        "step": step,
                        "action": "finish",
                        "report_chars": len(action.report),
                    }
                )
                self._write_trace(trace_path, question, trace, success=True)
                return ReActOutcome(
                    retrieved_keys=frozenset(retrieved),
                    ranked_keys=tuple(retrieved),
                    report=report,
                    report_path=report_path,
                    trace_path=trace_path,
                    model_calls=model_calls,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_ms=latency_ms,
                    steps_used=step,
                    search_calls=search_calls,
                    source_attempts=search_calls,
                    source_successes=source_successes,
                    source_failures=source_failures,
                )

            message = f"max_steps={self.max_steps} reached without finish"
            trace.append(
                {"step": self.max_steps, "action": "exhausted", "observation": message}
            )
            raise ReActExecutionError(message)
        except Exception:
            self._write_trace(trace_path, question, trace, success=False)
            raise

    async def _next_action(
        self,
        *,
        question: EvaluationQuestion,
        observations: list[str],
        retrieved: Mapping[str, PaperCandidate],
        step: int,
    ) -> _ActionCall:
        last_error = "model reply did not contain valid JSON"
        responses: list[ModelResponse] = []
        rejected: list[str] = []
        for attempt in range(self.max_action_retries + 1):
            user = self._build_user_message(
                question=question,
                observations=observations,
                retrieved=retrieved,
                step=step,
                previous_error=last_error if attempt else None,
            )
            try:
                response = await self.gateway.complete(
                    prompt_hash=sha256_text(REACT_SYSTEM_PROMPT + "\x00" + user),
                    system=REACT_SYSTEM_PROMPT,
                    user=user,
                    max_output_tokens=2500 if attempt == 0 else 5000,
                    json_output=True,
                )
            except ModelGatewayError as exc:
                last_error = f"model call failed: {exc}"
                continue
            responses.append(response)
            if response.truncated:
                last_error = "model output was truncated before a valid action"
                rejected.append(last_error)
                continue
            try:
                action = self._parse_action(response.content)
            except ReActExecutionError as exc:
                last_error = str(exc)
                rejected.append(last_error)
                continue
            return _ActionCall(
                action=action,
                responses=tuple(responses),
                rejected=tuple(rejected),
            )
        raise ReActExecutionError(last_error)

    def _parse_action(self, content: str) -> _Action:
        match = _JSON_OBJECT.search(content or "")
        if match is None:
            raise ReActExecutionError("model reply did not contain valid JSON")
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            raise ReActExecutionError("model reply did not contain valid JSON") from None
        if not isinstance(payload, dict):
            raise ReActExecutionError("model action must be a JSON object")
        action = payload.get("action")
        if action == "search":
            source = payload.get("source")
            query = payload.get("query")
            requested = payload.get("max_results", self.max_results_per_search)
            if not isinstance(source, str) or source not in self.clients:
                raise ReActExecutionError(f"unknown search source: {source!r}")
            if not isinstance(query, str) or not query.strip():
                raise ReActExecutionError("search action requires a non-empty query")
            if not isinstance(requested, int) or requested < 1:
                raise ReActExecutionError("max_results must be a positive integer")
            return _Action(
                kind="search",
                source=source,
                query=query.strip(),
                max_results=min(requested, self.max_results_per_search),
            )
        if action == "finish":
            report = payload.get("report")
            if not isinstance(report, str) or not report.strip():
                raise ReActExecutionError("finish action requires a non-empty report")
            return _Action(kind="finish", report=report.strip())
        raise ReActExecutionError(f"unsupported action: {action!r}")

    async def _run_search(
        self,
        *,
        action: _Action,
        retrieved: dict[str, PaperCandidate],
    ) -> tuple[str, int, bool]:
        try:
            result = await self.clients[action.source].search(
                action.query,
                max_results=action.max_results or self.max_results_per_search,
            )
        except Exception as exc:
            return (
                f"search failed for source={action.source}: {type(exc).__name__}: {exc}",
                0,
                False,
            )

        papers = getattr(result, "papers", [])
        new_count = 0
        new_titles: list[str] = []
        for paper in papers:
            if not isinstance(paper, PaperCandidate):
                continue
            key = canonical_key(paper)
            if key in retrieved:
                continue
            retrieved[key] = paper
            new_count += 1
            if len(new_titles) < 5:
                new_titles.append(f"{paper.title} ({paper.year or '?'})")
        observation = (
            f"source={action.source} query={action.query!r} returned "
            f"{new_count} new papers; total={len(retrieved)}."
        )
        if new_titles:
            observation += " Titles: " + "; ".join(new_titles)
        return observation, new_count, True

    def _build_user_message(
        self,
        *,
        question: EvaluationQuestion,
        observations: list[str],
        retrieved: Mapping[str, PaperCandidate],
        step: int,
        previous_error: str | None,
    ) -> str:
        subquestions = "\n".join(
            f"{index}. {text}"
            for index, text in enumerate(question.subquestions, start=1)
        )
        recent = observations[-8:]
        observation_block = "\n".join(recent) or "(no searches yet)"
        if len(observation_block) > 8000:
            observation_block = observation_block[-8000:]
        retry = (
            f"\nPrevious action was rejected: {previous_error}\n"
            if previous_error
            else ""
        )
        return (
            f"Research question: {question.question}\n"
            f"Subquestions:\n{subquestions or '(none)'}\n\n"
            f"Available sources: {', '.join(sorted(self.clients))}\n"
            f"Retrieved paper count: {len(retrieved)}\n"
            f"Step: {step}/{self.max_steps}\n"
            f"Previous observations:\n{observation_block}\n"
            f"{retry}\n"
            "Choose exactly one JSON action."
        )

    @staticmethod
    def _render_report(
        question: EvaluationQuestion,
        retrieved: Mapping[str, PaperCandidate],
        summary: str,
    ) -> str:
        papers = "\n".join(
            f"{index}. {paper.title} ({paper.doi or key})"
            for index, (key, paper) in enumerate(sorted(retrieved.items()), start=1)
        )
        return (
            "# B2 Pure ReAct Report\n\n"
            f"**Question**: {question.question}\n\n"
            f"## Retrieved Papers\n\n{papers or '(none)'}\n\n"
            f"## Report\n\n{summary.strip()}\n"
        )

    @staticmethod
    def _write_trace(
        path: Path,
        question: EvaluationQuestion,
        trace: list[dict[str, Any]],
        *,
        success: bool,
    ) -> None:
        path.write_text(
            json.dumps(
                {
                    "question_id": question.question_id,
                    "success": success,
                    "trace": trace,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )