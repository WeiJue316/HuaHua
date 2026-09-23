from __future__ import annotations

import pytest

from research_agent.evidence.claims import (
    CitationValidationError,
    ClaimDraft,
    build_claims_from_evidence,
    validate_claim_evidence,
)


def test_build_claims_from_evidence_creates_traceable_claims() -> None:
    evidence = [
        (
            "Traceable Retrieval for Scientific Agents",
            "We study evidence chains. The method is reproducible.",
            "source-record-1",
            "arxiv",
            "evidence-1",
            "Abstract",
        )
    ]

    claims = build_claims_from_evidence(evidence)

    assert len(claims) == 1
    claim = claims[0]
    assert claim.claim_text == (
        "Traceable Retrieval for Scientific Agents reports that "
        "We study evidence chains."
    )
    assert claim.support_status == "supported"
    assert claim.evidence_span_ids == ["evidence-1"]


def test_validate_claim_evidence_accepts_existing_support() -> None:
    claim = ClaimDraft(
        claim_text="Paper reports a result.",
        claim_type="fact",
        support_status="supported",
        confidence=0.8,
        evidence_span_ids=["evidence-1"],
    )

    validate_claim_evidence(claim, {"evidence-1"})


def test_validate_claim_evidence_rejects_missing_support() -> None:
    claim = ClaimDraft(
        claim_text="Unsupported claim.",
        claim_type="fact",
        support_status="supported",
        confidence=0.8,
        evidence_span_ids=[],
    )

    with pytest.raises(CitationValidationError, match="supported claim"):
        validate_claim_evidence(claim, set())


def test_validate_claim_evidence_rejects_unknown_evidence() -> None:
    claim = ClaimDraft(
        claim_text="Paper reports a result.",
        claim_type="fact",
        support_status="supported",
        confidence=0.8,
        evidence_span_ids=["missing-evidence"],
    )

    with pytest.raises(CitationValidationError, match="missing-evidence"):
        validate_claim_evidence(claim, {"evidence-1"})
