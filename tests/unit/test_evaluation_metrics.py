"""Tests for the deterministic evaluation metrics."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from research_agent.evaluator.metrics import (
    evidence_metrics,
    load_claim_rows,
    load_contributing_sources,
    load_model_usage,
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
    assert metrics.recall_kept == pytest.approx(2 / 3)
    assert metrics.precision_kept == pytest.approx(2 / 3)


def test_retrieval_metrics_treat_arxiv_doi_and_arxiv_id_as_one_paper() -> None:
    metrics = retrieval_metrics(
        retrieved_keys={"arxiv:2312.10997"},
        gold_keys={"doi:10.48550/arxiv.2312.10997", "doi:10.1000/missing"},
    )

    assert metrics.matched_count == 1
    assert metrics.recall_kept == pytest.approx(0.5)


def test_retrieval_metrics_handles_empty_gold() -> None:
    metrics = retrieval_metrics(retrieved_keys={"doi:a"}, gold_keys=set())

    assert metrics.recall_kept == 0.0
    assert metrics.precision_kept == 0.0


def test_retrieval_metrics_handles_empty_retrieval() -> None:
    metrics = retrieval_metrics(retrieved_keys=set(), gold_keys={"doi:a"})

    assert metrics.recall_kept == 0.0
    assert metrics.precision_kept == 0.0


def test_ranked_metrics_use_k_as_the_precision_denominator() -> None:
    """Hand check: one hit in a two-item list, K=4.

    Precision@4 = 1/4, not 1/2. Recall@4 = 1/2.
    Gains are [1, 0, 0, 0], so DCG = 1/log2(2) = 1.
    Ideal gains for two gold papers are [1, 1, 0, 0],
    IDCG = 1 + 1/log2(3). nDCG = 1 / (1 + 1/log2(3)).
    """

    metrics = retrieval_metrics(
        retrieved_keys={"doi:hit", "doi:miss"},
        gold_keys={"doi:hit", "doi:other"},
        ranked_keys=("doi:hit", "doi:miss"),
        k=4,
    )

    ideal = 1 + 1 / math.log2(3)
    assert metrics.precision_at_k == pytest.approx(1 / 4)
    assert metrics.recall_at_k == pytest.approx(1 / 2)
    assert metrics.ndcg_at_k == pytest.approx(1 / ideal)
    assert metrics.precision_kept == pytest.approx(1 / 2)


def test_ranked_metrics_prefer_an_earlier_hit() -> None:
    """The same hit at rank 2 instead of rank 1 lowers nDCG and leaves P@K."""

    early = retrieval_metrics(
        retrieved_keys={"doi:hit", "doi:miss"},
        gold_keys={"doi:hit"},
        ranked_keys=("doi:hit", "doi:miss"),
        k=2,
    )
    late = retrieval_metrics(
        retrieved_keys={"doi:hit", "doi:miss"},
        gold_keys={"doi:hit"},
        ranked_keys=("doi:miss", "doi:hit"),
        k=2,
    )

    assert early.precision_at_k == late.precision_at_k == pytest.approx(1 / 2)
    assert early.ndcg_at_k == pytest.approx(1.0)
    assert late.ndcg_at_k == pytest.approx((1 / math.log2(3)) / 1)


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


def test_evidence_metrics_count_supported_claims_with_no_span() -> None:
    metrics = evidence_metrics(
        [
            ("supported", 1),
            ("supported", 0),
            ("partially_supported", 0),
        ]
    )

    assert metrics.dangling_support_count == 2
    assert metrics.unsupported_claim_rate == 0.0


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
        repo.record_model_call(
            run_id=run_id,
            provider="deepseek",
            model="deepseek-flash",
            purpose="semantic_relevance",
            prompt_hash="prompt-1",
            prompt_version="relevance-v1",
            input_tokens=120,
            output_tokens=30,
            latency_ms=25,
            status="success",
        )
        repo.record_model_call(
            run_id=run_id,
            provider="deepseek",
            model="deepseek-flash",
            purpose="semantic_relevance",
            prompt_hash="prompt-2",
            prompt_version="relevance-v1",
            latency_ms=5,
            status="failed",
            error_code="timeout",
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
        usage = load_model_usage(conn, run_id)

    assert retrieved == {"doi:10.1000/example"}
    assert claims == [("supported", 1)]
    assert sources == {"openalex"}
    assert usage.calls == 2
    assert usage.input_tokens == 120
    assert usage.output_tokens == 30
    assert usage.latency_ms == 30
    assert usage.to_dict() == {
        "llm_calls": 2.0,
        "input_tokens": 120.0,
        "output_tokens": 30.0,
        "model_latency_ms": 30.0,
    }
