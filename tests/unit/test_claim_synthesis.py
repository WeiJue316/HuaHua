from __future__ import annotations

import json

import pytest

from research_agent.evidence.claims import (
    ClaimDraft,
    constrain_claim_citations,
    detach_unknown_span_ids,
    persistable_evidence_ids,
)
from research_agent.evidence.synthesis import (
    PROMPT_VERSION,
    ClaimSynthesizer,
    labeled_evidence,
    parse_synthesis_payload,
)
from research_agent.llm.gateway import ModelGatewayError, ModelResponse

EVIDENCE = [
    (
        "Traceable Retrieval",
        "We bind claims to evidence spans.",
        "sr-1",
        "arxiv",
        "span-1",
        "Abstract",
    ),
    (
        "Another Paper",
        "Keyword overlap is not relevance.",
        "sr-2",
        "openalex",
        "span-2",
        "Abstract",
    ),
]


def test_labeled_evidence_assigns_stable_e_labels() -> None:
    catalog = labeled_evidence(EVIDENCE)

    assert list(catalog) == ["E1", "E2"]
    assert catalog["E1"].evidence_id == "span-1"
    assert catalog["E2"].evidence_id == "span-2"


def test_parse_synthesis_maps_labels_to_span_ids() -> None:
    payload = json.dumps(
        {
            "findings": "Evidence chains make claims auditable.",
            "claims": [
                {
                    "claim_text": "Claims can be bound to spans.",
                    "support_status": "supported",
                    "evidence_labels": ["E1"],
                }
            ],
        }
    )

    result = parse_synthesis_payload(payload, labeled_evidence(EVIDENCE))

    assert result.findings == "Evidence chains make claims auditable."
    assert len(result.claims) == 1
    assert result.claims[0].evidence_span_ids == ["span-1"]
    assert result.claims[0].support_status == "supported"
    assert "reports that" not in result.claims[0].claim_text


def test_parse_synthesis_keeps_unknown_labels_out_of_span_ids() -> None:
    payload = json.dumps(
        {
            "findings": "A hallucinated citation.",
            "claims": [
                {
                    "claim_text": "An invented paper proves the opposite.",
                    "support_status": "supported",
                    "evidence_labels": ["E99"],
                }
            ],
        }
    )

    result = parse_synthesis_payload(payload, labeled_evidence(EVIDENCE))

    assert result.claims[0].evidence_span_ids == []
    assert result.claims[0].support_status == "supported"


def test_constrain_demotes_supported_claims_without_real_spans() -> None:
    claim = ClaimDraft(
        claim_text="Invented result.",
        claim_type="fact",
        support_status="supported",
        confidence=0.5,
        evidence_span_ids=[],
    )

    constrained = constrain_claim_citations([claim], {"span-1"})

    assert constrained[0].support_status == "unsupported"
    assert constrained[0].evidence_span_ids == []


def test_constrain_drops_unknown_span_ids() -> None:
    claim = ClaimDraft(
        claim_text="Mixed citations.",
        claim_type="fact",
        support_status="supported",
        confidence=0.5,
        evidence_span_ids=["span-1", "missing"],
    )

    constrained = constrain_claim_citations([claim], {"span-1"})

    assert constrained[0].support_status == "supported"
    assert constrained[0].evidence_span_ids == ["span-1"]


def test_detach_keeps_supported_status_after_dropping_unknown_spans() -> None:
    claim = ClaimDraft(
        claim_text="Invented result.",
        claim_type="fact",
        support_status="supported",
        confidence=0.5,
        evidence_span_ids=["span-1", "missing"],
    )

    detached = detach_unknown_span_ids([claim], {"span-1"})

    assert detached[0].support_status == "supported"
    assert detached[0].evidence_span_ids == ["span-1"]


def test_persistable_ids_never_include_unknown_spans() -> None:
    claim = ClaimDraft(
        claim_text="Hallucinated citation.",
        claim_type="fact",
        support_status="supported",
        confidence=0.5,
        evidence_span_ids=["span-1", "missing"],
    )

    assert persistable_evidence_ids(claim, {"span-1"}) == ["span-1"]


class _Gateway:
    def __init__(self, content: str, *, raises: bool = False) -> None:
        self.content = content
        self.raises = raises
        self.calls: list[str] = []

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
        self.calls.append(user)
        if self.raises:
            raise ModelGatewayError("upstream 503")
        finish_reason = getattr(self, "finish_reason", "stop")
        return ModelResponse(
            provider="stub",
            model="stub-model",
            content=self.content,
            prompt_hash=prompt_hash,
            response_hash="deadbeef",
            input_tokens=10,
            output_tokens=20,
            latency_ms=3,
            finish_reason=finish_reason,
        )


@pytest.mark.asyncio
async def test_synthesizer_records_prompt_version_and_answers_subquestions() -> None:
    gateway = _Gateway(
        json.dumps(
            {
                "findings": "Subquestion 1 is answered by span E1.",
                "claims": [
                    {
                        "claim_text": "Binding claims to spans is feasible.",
                        "support_status": "supported",
                        "evidence_labels": ["E1"],
                    }
                ],
            }
        )
    )
    synthesizer = ClaimSynthesizer(gateway)

    result = await synthesizer.synthesize(
        question="How do evidence chains work?",
        subquestions=("How are claims bound?",),
        evidence=EVIDENCE,
        citation_constraint=True,
    )

    assert synthesizer.prompt_version == PROMPT_VERSION
    assert result.used_fallback is False
    assert result.claims[0].evidence_span_ids == ["span-1"]
    assert "E1" in gateway.calls[0]
    assert "How are claims bound?" in gateway.calls[0]
    assert "Citation checking is disabled" not in gateway.calls[0]


@pytest.mark.asyncio
async def test_synthesizer_tells_the_model_when_citation_constraint_is_off() -> None:
    gateway = _Gateway(
        json.dumps({"findings": "Free generation.", "claims": []})
    )
    synthesizer = ClaimSynthesizer(gateway)

    await synthesizer.synthesize(
        question="How do evidence chains work?",
        subquestions=(),
        evidence=EVIDENCE,
        citation_constraint=False,
    )

    assert "Citation checking is disabled" in gateway.calls[0]


@pytest.mark.asyncio
async def test_synthesizer_keeps_a_complete_json_object_when_the_call_is_truncated() -> None:
    gateway = _Gateway(
        json.dumps(
            {
                "findings": "A complete object arrived before the budget ended.",
                "claims": [
                    {
                        "claim_text": "Stored spans can still be cited.",
                        "support_status": "supported",
                        "evidence_labels": ["E1"],
                    }
                ],
            }
        )
    )
    gateway.finish_reason = "length"
    synthesizer = ClaimSynthesizer(gateway)

    result = await synthesizer.synthesize(
        question="How do evidence chains work?",
        subquestions=(),
        evidence=EVIDENCE,
        citation_constraint=True,
    )

    assert result.used_fallback is False
    assert result.claims[0].evidence_span_ids == ["span-1"]
    assert result.response is not None
    assert result.response.truncated is True


@pytest.mark.asyncio
async def test_synthesizer_falls_back_to_template_claims_on_model_failure() -> None:
    synthesizer = ClaimSynthesizer(_Gateway("{}", raises=True))

    result = await synthesizer.synthesize(
        question="How do evidence chains work?",
        subquestions=(),
        evidence=EVIDENCE,
        citation_constraint=True,
    )

    assert result.used_fallback is True
    assert result.response is None
    assert result.claims[0].claim_text.startswith("Traceable Retrieval reports that")
