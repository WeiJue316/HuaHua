"""Deterministic claim construction and citation validation."""

from __future__ import annotations

import re
from dataclasses import dataclass

from research_agent.mcp_servers.common import PaperCandidate

EvidenceRow = tuple[str, str, str, str, str, str]


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
    for title, quote, _source_record_id, _source, evidence_id, _locator in evidence:
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


def build_direct_claims(papers: list[PaperCandidate]) -> list[ClaimDraft]:
    """Build claims directly from papers without Evidence Span linkage."""

    claims: list[ClaimDraft] = []
    for paper in papers:
        title = " ".join(paper.title.split())
        if not title:
            continue
        claims.append(
            ClaimDraft(
                claim_text=f"{title} reports findings relevant to the research question.",
                claim_type="fact",
                support_status="unsupported",
                confidence=0.4,
                evidence_span_ids=[],
            )
        )
    return claims


def persistable_evidence_ids(
    claim: ClaimDraft,
    available_evidence_ids: set[str],
) -> list[str]:
    """Return evidence IDs that exist and can be written to claim_evidence."""

    return [
        evidence_id
        for evidence_id in claim.evidence_span_ids
        if evidence_id in available_evidence_ids
    ]


def detach_unknown_span_ids(
    claims: list[ClaimDraft],
    available_evidence_ids: set[str],
) -> list[ClaimDraft]:
    """Drop span IDs that are not in the store, and keep the model's status.

    Unknown IDs cannot be written to ``claim_evidence``. Keeping
    ``support_status`` is what makes the no-constraint ablation measurable:
    a claim can still say it is supported after its citation has been detached.
    """

    return [
        ClaimDraft(
            claim_text=claim.claim_text,
            claim_type=claim.claim_type,
            support_status=claim.support_status,
            confidence=claim.confidence,
            evidence_span_ids=persistable_evidence_ids(claim, available_evidence_ids),
        )
        for claim in claims
    ]


def constrain_claim_citations(
    claims: list[ClaimDraft],
    available_evidence_ids: set[str],
) -> list[ClaimDraft]:
    """Drop unknown span IDs and demote supported claims that have none left.

    The citation constraint is a code-side filter. It never invents locators or
    quotes; it only refuses to treat a dangling reference as support.
    """

    constrained: list[ClaimDraft] = []
    for claim in claims:
        kept = persistable_evidence_ids(claim, available_evidence_ids)
        status = claim.support_status
        if status in {"supported", "partially_supported"} and not kept:
            status = "unsupported"
        constrained.append(
            ClaimDraft(
                claim_text=claim.claim_text,
                claim_type=claim.claim_type,
                support_status=status,
                confidence=claim.confidence if kept else min(claim.confidence, 0.4),
                evidence_span_ids=kept,
            )
        )
    return constrained


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
