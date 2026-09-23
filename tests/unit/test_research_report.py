"""Regression tests for the evidence-first Markdown report."""

from __future__ import annotations

from research_agent.evidence.claims import ClaimDraft
from research_agent.mcp_servers.common import OpenAccessInfo, PaperCandidate
from research_agent.runtime.research_service import render_report

EvidenceRow = tuple[str, str, str, str, str, str]


def _paper(*, source: str, source_record_id: str, title: str) -> PaperCandidate:
    return PaperCandidate(
        source=source,
        source_record_id=source_record_id,
        title=title,
        landing_url=f"https://example.org/{source_record_id}",
        open_access=OpenAccessInfo(is_oa=False, status="unknown"),
    )


def _evidence(
    *,
    title: str,
    quote: str,
    source_record_id: str,
    source: str,
    evidence_id: str,
    locator: str,
) -> EvidenceRow:
    return (title, quote, source_record_id, source, evidence_id, locator)


def _claim(claim_text: str, evidence_span_ids: list[str]) -> ClaimDraft:
    return ClaimDraft(
        claim_text=claim_text,
        claim_type="fact",
        support_status="supported",
        confidence=0.8,
        evidence_span_ids=evidence_span_ids,
    )


def test_claims_reference_the_evidence_rows_that_support_them() -> None:
    paper = _paper(source="openalex", source_record_id="W1", title="Paper One")
    evidence = [
        _evidence(
            title=paper.title,
            quote="We study evidence chains.",
            source_record_id="record-1",
            source="openalex",
            evidence_id="evidence-1",
            locator="Abstract",
        )
    ]

    report = render_report(
        question="evidence chain",
        run_id="run-1",
        source_records=[(paper, "record-1")],
        evidence=evidence,
        claims=[_claim("Paper One reports that We study evidence chains.", ["evidence-1"])],
        files=[],
    )

    assert "| C1 | Paper One reports that We study evidence chains. | supported | E1 |" in report


def test_claims_keep_distinct_references_when_locators_repeat() -> None:
    first = _paper(source="openalex", source_record_id="W1", title="Paper One")
    second = _paper(source="crossref", source_record_id="10.1/x", title="Paper Two")
    evidence = [
        _evidence(
            title=first.title,
            quote="First quote.",
            source_record_id="record-1",
            source="openalex",
            evidence_id="evidence-1",
            locator="Abstract",
        ),
        _evidence(
            title=second.title,
            quote="Second quote.",
            source_record_id="record-2",
            source="crossref",
            evidence_id="evidence-2",
            locator="Abstract",
        ),
    ]

    report = render_report(
        question="evidence chain",
        run_id="run-2",
        source_records=[(first, "record-1"), (second, "record-2")],
        evidence=evidence,
        claims=[_claim("Two papers report evidence.", ["evidence-1", "evidence-2"])],
        files=[],
    )

    assert "| C1 | Two papers report evidence. | supported | E1, E2 |" in report