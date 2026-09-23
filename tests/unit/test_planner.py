from __future__ import annotations

from research_agent.planner.planner import plan_research

ALL_SOURCES = ("arxiv", "openalex", "crossref", "semantic_scholar", "dblp")


def test_plan_research_prefers_citation_graph_sources() -> None:
    plan = plan_research(
        "survey the citation graph for retrieval augmented generation",
        available_sources=ALL_SOURCES,
        max_sources=3,
    )

    assert {"openalex", "semantic_scholar"}.issubset(set(plan.selected_sources))
    assert "citations" in plan.reason
    assert plan.max_results_per_source > 0
    assert plan.max_concurrency > 0


def test_plan_research_prefers_arxiv_for_full_text_requests() -> None:
    plan = plan_research(
        "find open access PDFs and full text for RAG papers",
        available_sources=ALL_SOURCES,
        max_sources=2,
    )

    assert plan.selected_sources[0] == "arxiv"
    assert "full_text" in plan.reason


def test_plan_research_keeps_fallback_order() -> None:
    plan = plan_research(
        "survey citation graph",
        available_sources=ALL_SOURCES,
        max_sources=2,
    )

    assert len(plan.selected_sources) == 2
    assert len(plan.fallback_sources) == 3
    assert set(plan.selected_sources).isdisjoint(plan.fallback_sources)

def test_plan_research_builds_content_term_query_variants() -> None:
    plan = plan_research(
        "evidence chain in scientific literature",
        available_sources=ALL_SOURCES,
    )

    assert plan.query_variants[0] == "evidence chain scientific literature"
    assert "evidence chain in scientific literature" in plan.query_variants
    assert "evidence chain" in plan.query_variants
    assert len(plan.query_variants) == len(set(plan.query_variants))
