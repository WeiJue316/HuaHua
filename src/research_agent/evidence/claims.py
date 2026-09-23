"""Deterministic claim construction and citation validation."""

from __future__ import annotations

import re
from dataclasses import dataclass

EvidenceRow = tuple[str, str, str, str, str]


class CitationValidationError(ValueError):
    """Raised when a claim cannot resolve its evidence support."""


@dataclass(frozen=True)
class ClaimDraft:
    """A claim before it is persisted with evidence links."""

    claim_text: str
    claim_type: str
    support_status: str
    confidence: float
    evidence_span_ids: list[str]


def first_sentence(value: str) -> str:
    """Return the first sentence-like unit from a text fragment."""

    normalized = " ".join(value.split())
    if not normalized:
        return ""
    return re.split(r"(?<=[.!?])\s+", normalized, maxsplit=1)[0]


def build_claims_from_evidence(evidence: list[EvidenceRow]) -> list[ClaimDraft]:
    """Create one traceable claim per recorded evidence span."""

    claims: list[ClaimDraft] = []
    for title, quote, _source_record_id, _source, evidence_id in evidence:
        sentence = first_sentence(quote)
        if not sentence:
            continue
        claims.append(
            ClaimDraft(
                claim_text=f"{title} reports that {sentence}",
                claim_type="fact",
                support_status="supported",
                confidence=0.8,
                evidence_span_ids=[evidence_id],
            )
        )
    return claims


def validate_claim_evidence(
    claim: ClaimDraft,
    available_evidence_ids: set[str],
) -> None:
    """Validate that every supported claim points to existing evidence."""

    if claim.support_status == "supported" and not claim.evidence_span_ids:
        raise CitationValidationError(
            f"supported claim has no evidence: {claim.claim_text}"
        )
    missing = [
        evidence_id
        for evidence_id in claim.evidence_span_ids
        if evidence_id not in available_evidence_ids
    ]
    if missing:
        raise CitationValidationError(
            f"claim references missing evidence: {', '.join(missing)}"
        )
