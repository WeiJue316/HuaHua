"""Integration test: semantic relevance filtering removes candidates from claims."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

import httpx
import pytest

from research_agent.llm.gateway import ModelResponse
from research_agent.mcp_servers.common import PaperCandidate
from research_agent.planner.planner import plan_research
from research_agent.policy.relevance import (
    DOMAIN_IN_SCOPE,
    DOMAIN_OUT_OF_SCOPE,
    ROLE_DIRECT,
    ROLE_NONE,
    RelevanceJudge,
    RelevanceVerdict,
)
from research_agent.router.registry import build_source_clients
from research_agent.runtime.research_service import run_federated_research
from research_agent.storage.migrations import connect_database

ARXIV_FIXTURE = Path(__file__).parents[1] / "fixtures" / "arxiv_search.xml"
OPENALEX_FIXTURE = Path(__file__).parents[1] / "fixtures" / "openalex_search.json"
SOURCES = ("arxiv", "openalex")


class _UnusedGateway:
    """Satisfies the gateway protocol so the stub judge can be constructed."""

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
        raise AssertionError("the stub judge must not reach the gateway")


class StubJudge(RelevanceJudge):
    """A judge with a fixed decision rule instead of a model call."""

    def __init__(self, *, deny_all: bool) -> None:
        # The parent sets prompt_version, which the runtime records on every
        # model_call row, so the stub must go through it.
        super().__init__(gateway=_UnusedGateway())
        self.deny_all = deny_all
        self.judged: list[str] = []

    async def judge(
        self,
        *,
        question: str,
        subquestions: Sequence[str],
        paper: PaperCandidate,
    ) -> tuple[RelevanceVerdict, ModelResponse]:
        key = (
            f"doi:{paper.doi}"
            if paper.doi
            else f"{paper.source}:{paper.source_record_id}"
        )
        self.judged.append(key)
        verdict = RelevanceVerdict(
            paper_key=key,
            domain_scope=DOMAIN_OUT_OF_SCOPE if self.deny_all else DOMAIN_IN_SCOPE,
            answer_role=ROLE_NONE if self.deny_all else ROLE_DIRECT,
            abstract_available=True,
            reason="stub decision",
        )
        return verdict, ModelResponse(
            provider="stub",
            model="stub-model",
            content="{}",
            prompt_hash=f"stub-{key}",
            response_hash="stub",
            input_tokens=1,
            output_tokens=1,
            latency_ms=1,
            finish_reason="stop",
        )


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


async def _run(
    tmp_path: Path,
    name: str,
    judge: RelevanceJudge | None,
    *,
    evidence_chain: bool = True,
) -> object:
    db_path = tmp_path / f"{name}.db"
    async with httpx.AsyncClient(transport=httpx.MockTransport(_handler)) as http_client:
        clients = build_source_clients(http_client, SOURCES)
        plan = plan_research(
            "evidence chain",
            available_sources=SOURCES,
            max_results_per_source=5,
            max_sources=2,
        )
        return await run_federated_research(
            question="evidence chain",
            db_path=db_path,
            reports_root=tmp_path / f"reports-{name}",
            clients=clients,
            max_results_per_source=5,
            plan=plan,
            relevance_judge=judge,
            subquestions=("How is evaluation performed?",),
            evidence_chain=evidence_chain,
        )


@pytest.mark.asyncio
async def test_filtering_is_off_by_default(tmp_path: Path) -> None:
    result = await _run(tmp_path, "default", None)

    assert result.relevance_skipped is True  # type: ignore[attr-defined]
    assert result.claim_count > 0  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_denied_candidates_produce_no_claims(tmp_path: Path) -> None:
    baseline = await _run(tmp_path, "baseline", None)
    assert baseline.claim_count > 0  # type: ignore[attr-defined]

    judge = StubJudge(deny_all=True)
    result = await _run(tmp_path, "filtered", judge)

    assert result.relevance_skipped is False  # type: ignore[attr-defined]
    assert result.relevance_judged == len(judge.judged) > 0  # type: ignore[attr-defined]
    assert result.relevance_dropped == len(judge.judged)  # type: ignore[attr-defined]
    assert result.claim_count == 0, "denied candidates must not produce claims"  # type: ignore[attr-defined]
    assert baseline.claim_count > result.claim_count  # type: ignore[attr-defined]

    with connect_database(tmp_path / "filtered.db") as conn:
        decisions = [
            row[0]
            for row in conn.execute(
                "SELECT decision FROM audit_event WHERE action = 'semantic_relevance'"
            )
        ]
        calls = conn.execute(
            "SELECT COUNT(*) FROM model_call WHERE purpose = 'semantic_relevance'"
        ).fetchone()[0]

    assert decisions, "every judgement must be audited"
    assert set(decisions) == {"denied"}
    assert calls == len(judge.judged), "every model call must be recorded"


@pytest.mark.asyncio
async def test_allowed_candidates_keep_their_claims(tmp_path: Path) -> None:
    baseline = await _run(tmp_path, "baseline2", None)
    judge = StubJudge(deny_all=False)
    result = await _run(tmp_path, "allowed", judge)

    assert result.relevance_dropped == 0  # type: ignore[attr-defined]
    assert result.claim_count == baseline.claim_count  # type: ignore[attr-defined]

@pytest.mark.asyncio
async def test_a1_direct_claims_respect_relevance_filtering(tmp_path: Path) -> None:
    judge = StubJudge(deny_all=True)
    result = await _run(
        tmp_path,
        "a1-filtered",
        judge,
        evidence_chain=False,
    )

    assert result.claim_count == 0  # type: ignore[attr-defined]
    assert result.evidence_count == 0  # type: ignore[attr-defined]
