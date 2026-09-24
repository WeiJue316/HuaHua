from __future__ import annotations

import json
from pathlib import Path

import pytest

from research_agent.evaluator.dataset import EvaluationQuestion
from research_agent.evaluator.react import PureReActBaseline, ReActExecutionError
from research_agent.llm.gateway import ModelResponse
from research_agent.mcp_servers.common import OpenAccessInfo, PaperCandidate


class ScriptedGateway:
    def __init__(self, contents: list[str]) -> None:
        self.contents = list(contents)
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
        content = self.contents[self.calls]
        self.calls += 1
        return ModelResponse(
            provider="stub",
            model="stub-react",
            content=content,
            prompt_hash=prompt_hash,
            response_hash=f"response-{self.calls}",
            input_tokens=10,
            output_tokens=5,
            latency_ms=2,
            finish_reason="stop",
        )


class FakeSearchClient:
    def __init__(self, papers: list[PaperCandidate]) -> None:
        self.papers = papers
        self.queries: list[str] = []

    async def search(self, query: str, *, max_results: int = 20) -> object:
        del max_results
        self.queries.append(query)
        return type("Result", (), {"papers": list(self.papers)})()


def _paper(key: str = "doi:gold") -> PaperCandidate:
    return PaperCandidate(
        source="openalex",
        source_record_id="W1",
        title="Evidence chain evaluation",
        abstract="We evaluate evidence chains.",
        doi=key.removeprefix("doi:"),
        landing_url="https://example.org/paper",
        open_access=OpenAccessInfo(is_oa=True, status="gold"),
    )


def _question() -> EvaluationQuestion:
    return EvaluationQuestion(
        question_id="csai_test",
        question="How is evidence-chain evaluation done?",
        subquestions=("Which methods are used?",),
        gold_papers=("doi:gold",),
    )


@pytest.mark.asyncio
async def test_react_runs_search_then_finish_and_writes_trace(tmp_path: Path) -> None:
    gateway = ScriptedGateway(
        [
            json.dumps(
                {"action": "search", "source": "openalex", "query": "evidence chain"}
            ),
            json.dumps({"action": "finish", "report": "Final ReAct report."}),
        ]
    )
    client = FakeSearchClient([_paper()])
    baseline = PureReActBaseline(
        clients={"openalex": client},
        gateway=gateway,
        reports_root=tmp_path / "reports",
        max_steps=4,
        max_results_per_search=5,
    )

    outcome = await baseline.run(_question(), run_number=1)

    assert outcome.retrieved_keys == frozenset({"doi:gold"})
    assert outcome.steps_used == 2
    assert outcome.search_calls == 1
    assert outcome.model_calls == 2
    assert outcome.source_attempts == 1
    assert outcome.source_successes == 1
    assert outcome.source_failures == 0
    assert client.queries == ["evidence chain"]
    assert "Final ReAct report." in outcome.report_path.read_text(encoding="utf-8")
    trace = json.loads(outcome.trace_path.read_text(encoding="utf-8"))
    assert [item["action"] for item in trace["trace"]] == ["search", "finish"]


@pytest.mark.asyncio
async def test_react_rejects_malformed_actions_after_retry(tmp_path: Path) -> None:
    gateway = ScriptedGateway(["not json", "still not json"])
    baseline = PureReActBaseline(
        clients={"openalex": FakeSearchClient([])},
        gateway=gateway,
        reports_root=tmp_path / "reports",
        max_steps=2,
    )

    with pytest.raises(ReActExecutionError, match="valid JSON"):
        await baseline.run(_question(), run_number=1)


@pytest.mark.asyncio
async def test_react_fails_when_max_steps_end_without_finish(tmp_path: Path) -> None:
    gateway = ScriptedGateway(
        [
            json.dumps(
                {"action": "search", "source": "openalex", "query": "evidence chain"}
            )
        ]
    )
    baseline = PureReActBaseline(
        clients={"openalex": FakeSearchClient([_paper()])},
        gateway=gateway,
        reports_root=tmp_path / "reports",
        max_steps=1,
    )

    with pytest.raises(ReActExecutionError, match="max_steps"):
        await baseline.run(_question(), run_number=1)

@pytest.mark.asyncio
async def test_react_counts_rejected_retry_calls_in_usage(tmp_path: Path) -> None:
    gateway = ScriptedGateway(
        [
            "not json",
            json.dumps(
                {"action": "search", "source": "openalex", "query": "evidence chain"}
            ),
            json.dumps({"action": "finish", "report": "Final report."}),
        ]
    )
    baseline = PureReActBaseline(
        clients={"openalex": FakeSearchClient([_paper()])},
        gateway=gateway,
        reports_root=tmp_path / "reports",
        max_steps=3,
    )

    outcome = await baseline.run(_question(), run_number=1)

    assert outcome.model_calls == 3
    assert outcome.input_tokens == 30
    trace = json.loads(outcome.trace_path.read_text(encoding="utf-8"))["trace"]
    assert [item["action"] for item in trace[0:2]] == [
        "rejected_action",
        "search",
    ]


class FailingSearchClient:
    async def search(self, query: str, *, max_results: int = 20) -> object:
        del query, max_results
        raise RuntimeError("source unavailable")


@pytest.mark.asyncio
async def test_react_records_failed_source_attempts(tmp_path: Path) -> None:
    gateway = ScriptedGateway(
        [
            json.dumps(
                {"action": "search", "source": "openalex", "query": "evidence chain"}
            ),
            json.dumps({"action": "finish", "report": "Insufficient evidence."}),
        ]
    )
    baseline = PureReActBaseline(
        clients={"openalex": FailingSearchClient()},
        gateway=gateway,
        reports_root=tmp_path / "reports",
        max_steps=2,
    )

    outcome = await baseline.run(_question(), run_number=1)

    assert outcome.source_attempts == 1
    assert outcome.source_successes == 0
    assert outcome.source_failures == 1
