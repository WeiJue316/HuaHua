"""Integration test: evaluation cases run through the real research pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from research_agent.evaluator.case_runner import (
    CaseRunnerSettings,
    ResearchCaseRunner,
)
from research_agent.evaluator.dataset import EvaluationQuestion
from research_agent.llm.gateway import ModelResponse

ARXIV_FIXTURE = Path(__file__).parents[1] / "fixtures" / "arxiv_search.xml"
OPENALEX_FIXTURE = Path(__file__).parents[1] / "fixtures" / "openalex_search.json"
# both fixtures describe 10.1000/example; arXiv also returns an unrelated paper
GOLD_KEY = "doi:10.1000/example"


def _handler(request: httpx.Request) -> httpx.Response:
    if request.url.host in {"export.arxiv.org", "arxiv.org"}:
        return httpx.Response(
            200,
            text=ARXIV_FIXTURE.read_text(encoding="utf-8"),
            headers={"content-type": "application/atom+xml"},
            request=request,
        )
    if request.url.host == "api.openalex.org":
        return httpx.Response(
            200,
            json=json.loads(OPENALEX_FIXTURE.read_text(encoding="utf-8")),
            headers={"content-type": "application/json"},
            request=request,
        )
    raise AssertionError(f"unexpected request: {request.url}")


class StubGateway:
    """Verdicts every paper in scope, optionally denying one by title."""

    def __init__(self, *, deny_title_fragment: str | None = None) -> None:
        self.deny_title_fragment = deny_title_fragment
        self.prompts: list[str] = []

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
        self.prompts.append(user)
        denied = bool(self.deny_title_fragment and self.deny_title_fragment in user)
        payload = {
            "abstract_available": True,
            "domain_scope": "out_of_scope" if denied else "in_scope",
            "answer_role": "none" if denied else "direct",
            "reason": "stub",
        }
        return ModelResponse(
            provider="stub",
            model="stub-model",
            content=json.dumps(payload),
            prompt_hash=prompt_hash,
            response_hash="stub",
            input_tokens=1,
            output_tokens=1,
            latency_ms=1,
            finish_reason="stop",
        )


def _question() -> EvaluationQuestion:
    return EvaluationQuestion(
        question_id="csai_test",
        question="evidence chain",
        subquestions=("How is evaluation done?",),
        domain="llm_rag",
        year_range=(2020, 2030),
        gold_papers=(GOLD_KEY,),
    )


def _settings(tmp_path: Path, name: str) -> CaseRunnerSettings:
    return CaseRunnerSettings(
        db_path=tmp_path / f"{name}.db",
        reports_root=tmp_path / f"reports-{name}",
        max_results_per_source=5,
        enable_task_completion_judge=False,
    )


async def _run(
    tmp_path: Path,
    name: str,
    system_id: str,
    gateway: object,
    *,
    b0_index: object | None = None,
):
    settings = _settings(tmp_path, name)
    async with httpx.AsyncClient(transport=httpx.MockTransport(_handler)) as http_client:
        runner = ResearchCaseRunner(
            questions=[_question()],
            settings=settings,
            http_client=http_client,
            gateway=gateway,  # type: ignore[arg-type]
            b0_index=b0_index,  # type: ignore[arg-type]
        )
        return await runner("csai_test", system_id, 1)


@pytest.mark.asyncio
async def test_full_system_case_reports_retrieval_and_evidence_metrics(
    tmp_path: Path,
) -> None:
    gateway = StubGateway()
    outcome = await _run(tmp_path, "b3", "B3", gateway)

    assert outcome.error_code is None
    assert outcome.research_run_id
    metrics = outcome.metrics or {}
    assert metrics["gold_count"] == 1.0
    assert metrics["matched_count"] == 1.0, "the gold paper must be found"
    assert metrics["recall"] == 1.0
    assert metrics["stored_paper_count"] >= metrics["retrieved_count"]
    assert "evidence_coverage" in metrics
    assert "unsupported_claim_rate" in metrics
    assert metrics["relevance_failures"] == 0.0
    assert metrics["source_attempts"] >= 1.0
    assert metrics["source_successes"] >= 1.0
    assert metrics["source_failures"] >= 0.0
    assert metrics["source_success_rate"] > 0.0
    assert metrics["llm_calls"] >= 1.0
    assert "input_tokens" in metrics
    assert "output_tokens" in metrics
    assert "model_latency_ms" in metrics


@pytest.mark.asyncio
async def test_a6_runs_without_the_filter(tmp_path: Path) -> None:
    outcome = await _run(tmp_path, "a6", "A6", None)

    assert outcome.error_code is None
    metrics = outcome.metrics or {}
    assert metrics["relevance_dropped"] == 0.0
    # without a filter the stored and kept sets are identical
    assert metrics["stored_paper_count"] == metrics["retrieved_count"]


@pytest.mark.asyncio
async def test_denied_candidates_leave_the_kept_set_and_the_claims(
    tmp_path: Path,
) -> None:
    allowed = await _run(tmp_path, "allow", "B3", StubGateway())
    denied = await _run(
        tmp_path, "deny", "B3", StubGateway(deny_title_fragment="Another Paper")
    )

    assert denied.error_code is None
    metrics = denied.metrics or {}
    assert metrics["relevance_dropped"] == 1.0
    assert metrics["retrieved_count"] < metrics["stored_paper_count"], (
        "a denied paper must leave the kept set while staying stored"
    )
    assert (metrics.get("claim_count") or 0) < (allowed.metrics or {}).get(
        "claim_count", 0.0
    )


@pytest.mark.asyncio
async def test_unimplemented_system_is_reported_not_silently_run(
    tmp_path: Path,
) -> None:
    outcome = await _run(tmp_path, "a1", "A1", None)

    assert outcome.error_code == "NotImplementedError"


@pytest.mark.asyncio
async def test_unknown_question_is_reported(tmp_path: Path) -> None:
    settings = _settings(tmp_path, "unknown")
    async with httpx.AsyncClient(transport=httpx.MockTransport(_handler)) as http_client:
        runner = ResearchCaseRunner(
            questions=[_question()],
            settings=settings,
            http_client=http_client,
            gateway=StubGateway(),  # type: ignore[arg-type]
        )
        outcome = await runner("does_not_exist", "B3", 1)

    assert outcome.error_code == "unknown_question"


@pytest.mark.asyncio
async def test_evaluation_runner_does_not_deadlock_against_the_research_db(
    tmp_path: Path,
) -> None:
    """A case writes to the same database the evaluation repository holds.

    The evaluation connection must not keep an open write transaction while a
    case runs, or every case fails with "database is locked".
    """

    from research_agent.evaluator.runner import EvaluationRunner
    from research_agent.storage.evaluation_repository import EvaluationRepository
    from research_agent.storage.migrations import apply_migrations, connect_database

    settings = _settings(tmp_path, "lock")
    apply_migrations(settings.db_path)
    question = _question()

    async with httpx.AsyncClient(transport=httpx.MockTransport(_handler)) as http_client:
        case_runner = ResearchCaseRunner(
            questions=[question],
            settings=settings,
            http_client=http_client,
            gateway=StubGateway(),  # type: ignore[arg-type]
        )
        with connect_database(settings.db_path) as conn:
            runner = EvaluationRunner(EvaluationRepository(conn))
            summary = await runner.run(
                questions=[question],
                systems=["B3"],
                repeats=1,
                run_case=case_runner,
                dataset_version="test",
                system_version="test",
                config={},
            )

    assert summary.failed_count == 0, "a locked database would fail the case"
    assert summary.completed_count == 1

    with connect_database(settings.db_path) as conn:
        row = conn.execute(
            "SELECT status, error_code, metrics_json FROM evaluation_case"
        ).fetchone()

    assert row is not None
    assert row["status"] == "completed"
    assert row["error_code"] is None
    assert "recall" in row["metrics_json"]


@pytest.mark.asyncio
async def test_second_run_against_the_same_db_still_counts_its_papers(
    tmp_path: Path,
) -> None:
    """Source records are deduplicated across runs, so retrieval metrics must
    come from the run result rather than a source_record join.

    Recording the same paper twice reuses the first run's source record; a
    per-run query through source_call.run_id then sees almost nothing for the
    second run while the pipeline reports a full candidate set.
    """

    settings = _settings(tmp_path, "shared")
    question = _question()

    async with httpx.AsyncClient(transport=httpx.MockTransport(_handler)) as http_client:
        first = ResearchCaseRunner(
            questions=[question],
            settings=settings,
            http_client=http_client,
            gateway=StubGateway(),  # type: ignore[arg-type]
        )
        second = ResearchCaseRunner(
            questions=[question],
            settings=settings,
            http_client=http_client,
            gateway=None,
        )
        first_outcome = await first("csai_test", "B3", 1)
        second_outcome = await second("csai_test", "A6", 1)

    first_metrics = first_outcome.metrics or {}
    second_metrics = second_outcome.metrics or {}

    assert first_outcome.error_code is None
    assert second_outcome.error_code is None
    assert first_metrics["stored_paper_count"] > 1
    assert second_metrics["stored_paper_count"] == first_metrics["stored_paper_count"], (
        "the second run retrieves the same papers and must count them all"
    )
    assert second_metrics["recall"] == first_metrics["recall"]


class SummaryGateway:
    """Return one plain-text summary for the B0 baseline."""

    def __init__(self) -> None:
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
        self.calls += 1
        return ModelResponse(
            provider="stub",
            model="stub-summary",
            content="Baseline report.",
            prompt_hash=prompt_hash,
            response_hash="stub",
            input_tokens=10,
            output_tokens=5,
            latency_ms=3,
            finish_reason="stop",
        )


@pytest.mark.asyncio
async def test_b0_uses_the_frozen_corpus_and_calls_the_model_once(
    tmp_path: Path,
) -> None:
    from research_agent.evaluator.bm25 import Bm25Document, Bm25Index

    gateway = SummaryGateway()
    index = Bm25Index(
        [
            Bm25Document(
                paper_key=GOLD_KEY,
                title="Evidence chain evaluation",
                abstract="How evaluation methods work for evidence chains.",
            )
        ]
    )

    outcome = await _run(tmp_path, "b0", "B0", gateway, b0_index=index)

    assert outcome.error_code is None
    metrics = outcome.metrics or {}
    assert gateway.calls == 1
    assert metrics["recall"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["llm_calls"] == 1.0
    assert metrics["report_written"] == 1.0
    reports = list((tmp_path / "reports-b0" / "b0").glob("*.md"))
    assert len(reports) == 1


class ScriptedReActGateway:
    """Return a fixed sequence of B2 actions."""

    def __init__(self, actions: list[dict[str, object]]) -> None:
        self.actions = list(actions)
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
        content = json.dumps(self.actions[self.calls], ensure_ascii=False)
        self.calls += 1
        return ModelResponse(
            provider="stub",
            model="stub-react",
            content=content,
            prompt_hash=prompt_hash,
            response_hash=f"react-{self.calls}",
            input_tokens=20,
            output_tokens=10,
            latency_ms=4,
            finish_reason="stop",
        )


@pytest.mark.asyncio
async def test_b2_runs_a_react_search_finish_loop(tmp_path: Path) -> None:
    gateway = ScriptedReActGateway(
        [
            {"action": "search", "source": "openalex", "query": "evidence chain"},
            {"action": "finish", "report": "ReAct baseline report."},
        ]
    )

    outcome = await _run(tmp_path, "b2", "B2", gateway)

    assert outcome.error_code is None
    metrics = outcome.metrics or {}
    assert gateway.calls == 2
    assert metrics["recall"] == 1.0
    assert metrics["search_calls"] == 1.0
    assert metrics["steps_used"] == 2.0
    assert metrics["llm_calls"] == 2.0
    assert metrics["report_written"] == 1.0
    reports = list((tmp_path / "reports-b2" / "b2").glob("*.md"))
    traces = list((tmp_path / "reports-b2" / "b2").glob("*.trace.json"))
    assert len(reports) == 1
    assert len(traces) == 1


@pytest.mark.asyncio
async def test_source_allowlist_can_disable_a_system_source(tmp_path: Path) -> None:
    settings = CaseRunnerSettings(
        db_path=tmp_path / "allowlist.db",
        reports_root=tmp_path / "reports-allowlist",
        max_results_per_source=5,
        allowed_sources=("arxiv",),
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(_handler)) as http_client:
        runner = ResearchCaseRunner(
            questions=[_question()],
            settings=settings,
            http_client=http_client,
            gateway=StubGateway(),  # type: ignore[arg-type]
        )
        outcome = await runner("csai_test", "B1", 1)

    assert outcome.error_code == "no_sources"


class CombinedEvaluationGateway:
    """Answer relevance calls and the task-completion judge."""

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
        del user, max_output_tokens, temperature, json_output
        if "covers the requested subquestions" in system:
            content = json.dumps(
                {"subquestions": [{"index": 1, "covered": True}]}
            )
        else:
            content = json.dumps(
                {
                    "abstract_available": True,
                    "domain_scope": "in_scope",
                    "answer_role": "direct",
                    "reason": "stub",
                }
            )
        return ModelResponse(
            provider="stub",
            model="stub-combined",
            content=content,
            prompt_hash=prompt_hash,
            response_hash="stub",
            input_tokens=1,
            output_tokens=1,
            latency_ms=1,
            finish_reason="stop",
        )


@pytest.mark.asyncio
async def test_task_completion_metrics_are_baseline_neutral(tmp_path: Path) -> None:
    settings = CaseRunnerSettings(
        db_path=tmp_path / "task-completion.db",
        reports_root=tmp_path / "reports-task-completion",
        max_results_per_source=5,
        enable_task_completion_judge=True,
        model_call_budget=20,
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(_handler)) as http_client:
        runner = ResearchCaseRunner(
            questions=[_question()],
            settings=settings,
            http_client=http_client,
            gateway=CombinedEvaluationGateway(),
        )
        outcome = await runner("csai_test", "B3", 1)

    assert outcome.error_code is None
    metrics = outcome.metrics or {}
    assert metrics["report_created"] == 1.0
    assert metrics["subquestions_covered"] == 1.0
    assert metrics["subquestion_coverage_rate"] == 1.0
    assert metrics["within_model_budget"] == 1.0
    assert metrics["task_completion"] == 1.0


@pytest.mark.asyncio
async def test_source_snapshot_replaces_live_source_clients(tmp_path: Path) -> None:
    from research_agent.evaluator.snapshot import SourceSnapshot
    from research_agent.mcp_servers.common import OpenAccessInfo, PaperCandidate

    paper = PaperCandidate(
        source="openalex",
        source_record_id="W-SNAPSHOT",
        title="Evidence chain evaluation",
        abstract="Evidence chain query methods.",
        doi=GOLD_KEY.removeprefix("doi:"),
        landing_url="https://example.org/snapshot",
        open_access=OpenAccessInfo(is_oa=True, status="gold"),
    )
    snapshot = SourceSnapshot({"openalex": [paper]})
    settings = CaseRunnerSettings(
        db_path=tmp_path / "snapshot.db",
        reports_root=tmp_path / "reports-snapshot",
        max_results_per_source=5,
        allowed_sources=("openalex",),
        enable_task_completion_judge=False,
    )

    def forbidden(request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"snapshot run made a live request: {request.url}")

    async with httpx.AsyncClient(transport=httpx.MockTransport(forbidden)) as http_client:
        runner = ResearchCaseRunner(
            questions=[_question()],
            settings=settings,
            http_client=http_client,
            gateway=StubGateway(),  # type: ignore[arg-type]
            source_snapshot=snapshot,
        )
        outcome = await runner("csai_test", "B3", 1)

    assert outcome.error_code is None
    assert (outcome.metrics or {})["recall"] == 1.0
