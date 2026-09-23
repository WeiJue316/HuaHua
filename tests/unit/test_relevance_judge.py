"""Offline tests for the semantic relevance judge."""

from __future__ import annotations

import json

import pytest

from research_agent.llm.gateway import ModelGatewayError, ModelResponse
from research_agent.mcp_servers.common import OpenAccessInfo, PaperCandidate
from research_agent.policy.relevance import (
    DOMAIN_OUT_OF_SCOPE,
    ROLE_DIRECT,
    RelevanceJudge,
    parse_verdict,
)


def _paper(
    *,
    doi: str = "10.1/example",
    abstract: str | None = "We study retrieval.",
) -> PaperCandidate:
    return PaperCandidate(
        source="openalex",
        source_record_id="W1",
        title="A paper",
        abstract=abstract,
        doi=doi,
        year=2024,
        landing_url="https://example.org/paper",
        open_access=OpenAccessInfo(is_oa=False, status="unknown"),
    )


class StubGateway:
    """Returns a canned reply, or raises, without touching the network."""

    def __init__(
        self,
        *,
        content: str = "{}",
        raises: bool = False,
        truncated: bool = False,
    ) -> None:
        self.content = content
        self.raises = raises
        self.truncated = truncated
        self.calls: list[dict[str, object]] = []

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
        self.calls.append({"prompt_hash": prompt_hash, "user": user, "json_output": json_output})
        if self.raises:
            raise ModelGatewayError("upstream 503", status_code=503)
        return ModelResponse(
            provider="stub",
            model="stub-model",
            content=self.content,
            prompt_hash=prompt_hash,
            response_hash="deadbeef",
            input_tokens=10,
            output_tokens=5,
            latency_ms=1,
            finish_reason="length" if self.truncated else "stop",
        )


def test_parse_in_scope_direct_verdict() -> None:
    verdict = parse_verdict(
        "doi:10.1/x",
        json.dumps(
            {
                "abstract_available": True,
                "domain_scope": "in_scope",
                "answer_role": "direct",
                "reason": "abstract reports the metrics asked for",
            }
        ),
    )

    assert verdict.domain_scope == "in_scope"
    assert verdict.answer_role == ROLE_DIRECT
    assert verdict.keep is True
    assert verdict.failed is False


def test_out_of_scope_is_the_only_thing_that_removes_a_candidate() -> None:
    in_scope_none = parse_verdict(
        "k", '{"abstract_available": true, "domain_scope": "in_scope", "answer_role": "none"}'
    )
    out_of_scope = parse_verdict(
        "k", '{"abstract_available": true, "domain_scope": "out_of_scope", "answer_role": "none"}'
    )

    assert in_scope_none.keep is True, "supporting material must survive"
    assert out_of_scope.keep is False


def test_missing_abstract_fails_open() -> None:
    verdict = parse_verdict(
        "k", '{"abstract_available": false, "domain_scope": "unknown", "answer_role": "unknown"}'
    )

    assert verdict.domain_scope != DOMAIN_OUT_OF_SCOPE
    assert verdict.keep is True


def test_unparseable_reply_fails_open() -> None:
    verdict = parse_verdict("k", "I am unable to answer.")

    assert verdict.failed is True
    assert verdict.keep is True


def test_json_is_extracted_from_surrounding_prose() -> None:
    reply = (
        "Here is my judgement:\n"
        '{"abstract_available": true, "domain_scope": "in_scope", '
        '"answer_role": "supporting", "reason": "adjacent evidence"}\n'
        "Let me know if you need more."
    )

    verdict = parse_verdict("k", reply)

    assert verdict.failed is False
    assert verdict.answer_role == "supporting"


def test_unknown_enum_values_are_normalised() -> None:
    verdict = parse_verdict(
        "k", '{"abstract_available": true, "domain_scope": "maybe", "answer_role": "sort-of"}'
    )

    assert verdict.domain_scope == "unknown"
    assert verdict.answer_role == "unknown"
    assert verdict.keep is True


@pytest.mark.asyncio
async def test_judge_sends_the_subquestion_and_abstract() -> None:
    gateway = StubGateway(
        content='{"abstract_available": true, "domain_scope": "in_scope", "answer_role": "direct"}'
    )
    judge = RelevanceJudge(gateway)

    verdict, response = await judge.judge(
        question="How are RAG systems evaluated?",
        subquestions=["Which metrics are used?"],
        paper=_paper(abstract="We report F1 and EM."),
    )

    assert verdict.keep is True
    assert response is not None
    sent = gateway.calls[0]
    assert "Which metrics are used?" in str(sent["user"])
    assert "We report F1 and EM." in str(sent["user"])
    assert sent["json_output"] is True


@pytest.mark.asyncio
async def test_gateway_error_yields_a_failed_but_kept_verdict() -> None:
    judge = RelevanceJudge(StubGateway(raises=True))

    verdict, response = await judge.judge(
        question="q", subquestions=["s"], paper=_paper()
    )

    assert verdict.failed is True
    assert verdict.keep is True, "an infrastructure failure must not drop a candidate"
    assert response is None


@pytest.mark.asyncio
async def test_truncated_reply_yields_a_failed_but_kept_verdict() -> None:
    gateway = StubGateway(content="", truncated=True)
    judge = RelevanceJudge(gateway)

    verdict, response = await judge.judge(
        question="q", subquestions=["s"], paper=_paper()
    )

    assert verdict.failed is True
    assert verdict.keep is True
    assert response is not None
    assert "output budget" in verdict.reason


@pytest.mark.asyncio
async def test_prompt_hash_changes_with_the_subquestion() -> None:
    gateway = StubGateway(
        content='{"abstract_available": true, "domain_scope": "in_scope", "answer_role": "none"}'
    )
    judge = RelevanceJudge(gateway)
    paper = _paper()

    await judge.judge(question="q", subquestions=["first subquestion"], paper=paper)
    await judge.judge(question="q", subquestions=["second subquestion"], paper=paper)

    first, second = (call["prompt_hash"] for call in gateway.calls)
    assert first != second, "the subquestions must be part of the prompt identity"


@pytest.mark.asyncio
async def test_every_subquestion_is_sent_to_the_model() -> None:
    gateway = StubGateway(
        content='{"abstract_available": true, "domain_scope": "in_scope", "answer_role": "none"}'
    )
    judge = RelevanceJudge(gateway)

    await judge.judge(
        question="How do agents plan and remember?",
        subquestions=["How is planning represented?", "How is state retained?"],
        paper=_paper(),
    )

    sent = str(gateway.calls[0]["user"])
    assert "How is planning represented?" in sent
    assert "How is state retained?" in sent
    assert "How do agents plan and remember?" in sent