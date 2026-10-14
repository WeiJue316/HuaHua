"""Enriched abstracts keep the provenance of the source that supplied them."""

from __future__ import annotations

from pathlib import Path

import pytest

from research_agent.mcp_servers.common import OpenAccessInfo, PaperCandidate
from research_agent.planner.planner import ResearchPlan
from research_agent.runtime.enrichment import AbstractEnrichment
from research_agent.runtime.research_service import run_federated_research
from research_agent.storage.migrations import connect_database

DOI = "10.1000/example"
OPENALEX_ID = "W999"
RECOVERED = "Recovered from OpenAlex."


def _paper(
    *,
    source: str,
    source_record_id: str,
    abstract: str | None,
) -> PaperCandidate:
    return PaperCandidate(
        source=source,
        source_record_id=source_record_id,
        title="Sparse metadata paper",
        abstract=abstract,
        doi=DOI,
        landing_url=f"https://example.org/{source_record_id}",
        open_access=OpenAccessInfo(is_oa=False, status="unknown"),
    )


class _SearchResult:
    def __init__(self, papers: list[PaperCandidate]) -> None:
        self.papers = papers


class _CrossrefClient:
    async def search(self, query: str, *, max_results: int = 20) -> _SearchResult:
        del query, max_results
        return _SearchResult(
            [_paper(source="crossref", source_record_id=DOI, abstract=None)]
        )


class _Resolver:
    async def resolve_abstract(self, candidate: PaperCandidate) -> AbstractEnrichment:
        assert candidate.source == "crossref"
        return AbstractEnrichment(
            abstract=RECOVERED,
            source=_paper(
                source="openalex",
                source_record_id=OPENALEX_ID,
                abstract=RECOVERED,
            ),
        )


@pytest.mark.asyncio
async def test_enriched_abstract_is_attributed_to_openalex(tmp_path: Path) -> None:
    plan = ResearchPlan(
        question="evidence chain",
        query_variants=("evidence chain",),
        selected_sources=("crossref",),
        fallback_sources=(),
        max_results_per_source=5,
        max_concurrency=1,
        reason="test",
    )
    await run_federated_research(
        question="evidence chain",
        db_path=tmp_path / "enrichment.db",
        reports_root=tmp_path / "reports",
        clients={"crossref": _CrossrefClient()},
        max_results_per_source=5,
        plan=plan,
        abstract_resolver=_Resolver(),
    )

    with connect_database(tmp_path / "enrichment.db") as conn:
        evidence = conn.execute(
            """
            SELECT evidence_span.quote, source_record.source, source_record.source_record_id
            FROM evidence_span
            JOIN source_record ON source_record.id = evidence_span.source_record_id
            WHERE evidence_span.evidence_level = 'abstract'
            """
        ).fetchall()
        linked_papers = conn.execute(
            """
            SELECT COUNT(DISTINCT paper_source_record.paper_id)
            FROM paper_source_record
            JOIN source_record ON source_record.id = paper_source_record.source_record_id
            WHERE source_record.source = 'openalex'
              AND source_record.source_record_id = ?
            """,
            (OPENALEX_ID,),
        ).fetchone()

    assert [tuple(row) for row in evidence] == [(RECOVERED, "openalex", OPENALEX_ID)]
    assert linked_papers is not None
    assert linked_papers[0] == 1
