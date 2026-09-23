"""Tests for the deterministic evaluation metrics."""

from __future__ import annotations

from pathlib import Path

import pytest

from research_agent.evaluator.metrics import (
    evidence_metrics,
    load_claim_rows,
    load_contributing_sources,
    load_retrieved_keys,
    retrieval_metrics,
    source_coverage,
)
from research_agent.evidence.claims import ClaimDraft
from research_agent.mcp_servers.common import OpenAccessInfo, PaperCandidate
from research_agent.storage.migrations import apply_migrations, connect_database
from research_agent.storage.repository import ResearchRepository


def test_retrieval_metrics_counts_matches() -> None:
    metrics = retrieval_metrics(
        retrieved_keys={"doi:a", "doi:b", "doi:c"},
        gold_keys={"doi:a", "doi:b", "doi:d"},
    )

    assert metrics.matched_count == 2
    assert metrics.recall == pytest.approx(2 / 3)
    assert metrics.precision == pytest.approx(2 / 3)


def test_retrieval_metrics_handles_empty_gold() -> None:
    metrics = retrieval_metrics(retrieved_keys={"doi:a"}, gold_keys=set())

    assert metrics.recall == 0.0
    assert metrics.precision == 0.0


def test_retrieval_metrics_handles_empty_retrieval() -> None:
    metrics = retrieval_metrics(retrieved_keys=set(), gold_keys={"doi:a"})

    assert metrics.recall == 0.0
    assert metrics.precision == 0.0


def test_evidence_metrics_separate_partial_from_supported() -> None:
    metrics = evidence_metrics(
        [
            ("supported", 1),
            ("supported", 2),
            ("partially_supported", 1),
            ("unsupported", 0),
            ("disputed", 1),
        ]
    )

    assert metrics.claim_count == 5
    assert metrics.supported_count == 2
    assert metrics.partially_supported_count == 1
    assert metrics.unsupported_count == 1
    assert metrics.claims_with_evidence == 4
    assert metrics.evidence_coverage == pytest.approx(4 / 5)
    assert metrics.unsupported_claim_rate == pytest.approx(1 / 5)


def test_evidence_metrics_handle_no_claims() -> None:
    metrics = evidence_metrics([])

    assert metrics.claim_count == 0
    assert metrics.evidence_coverage == 0.0
    assert metrics.unsupported_claim_rate == 0.0


def test_source_coverage_counts_only_allowed_sources() -> None:
    assert source_coverage(
        contributing_sources={"arxiv", "openalex", "other"},
        allowed_sources={"arxiv", "openalex", "crossref"},
    ) == pytest.approx(2 / 3)
    assert source_coverage(contributing_sources=set(), allowed_sources=set()) == 0.0


def _candidate() -> PaperCandidate:
    return PaperCandidate(
        source="openalex",
        source_record_id="W1",
        title="Traceable Retrieval",
        abstract="We study evidence chains.",
        year=2024,
        doi="10.1000/example",
        landing_url="https://example.org/paper",
        open_access=OpenAccessInfo(is_oa=False, status="unknown"),
    )


def test_metric_queries_read_back_what_the_repository_wrote(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        project_id = repo.create_project("project")
        question_id = repo.create_research_question(project_id, "question")
        run_id = repo.create_run(project_id, question_id)
        call_id = repo.record_source_call(
            run_id=run_id,
            source="openalex",
            tool_name="openalex_search_papers",
            request_json={"query": "evidence chain"},
            status="success",
            started_at="2026-01-01T00:00:00Z",
        )
        source_record_id = repo.record_source_record(
            source_call_id=call_id,
            candidate=_candidate(),
            api_endpoint="https://api.openalex.org/works",
        )
        paper_id, _ = repo.upsert_paper(_candidate())
        repo.link_paper_source_record(
            paper_id=paper_id,
            source_record_id=source_record_id,
            merge_reason="doi",
            is_primary_metadata=True,
        )
        evidence_id = repo.record_evidence_span(
            paper_id=paper_id,
            source_record_id=source_record_id,
            quote="We study evidence chains.",
            locator={"section": "Abstract"},
            evidence_level="abstract",
            extraction_method="rule",
            confidence=0.8,
            verified=1,
        )
        report_id = repo.record_report(
            run_id=run_id, path="reports/r/report.md", content="# Report\n"
        )
        repo.record_claim(
            report_id=report_id,
            claim=ClaimDraft(
                claim_text="Traceable Retrieval reports that we study evidence chains.",
                claim_type="fact",
                support_status="supported",
                confidence=0.8,
                evidence_span_ids=[evidence_id],
            ),
        )

        retrieved = load_retrieved_keys(conn, run_id)
        claims = load_claim_rows(conn, run_id)
        sources = load_contributing_sources(conn, run_id)

    assert retrieved == {"doi:10.1000/example"}
    assert claims == [("supported", 1)]
    assert sources == {"openalex"}