from __future__ import annotations

from research_agent.evaluator.systems import restrict_sources


def test_restrict_sources_preserves_requested_order() -> None:
    assert restrict_sources(
        ("openalex", "crossref", "semantic_scholar"),
        ("semantic_scholar", "openalex"),
    ) == ("openalex", "semantic_scholar")


def test_restrict_sources_without_allowlist_keeps_requested_sources() -> None:
    assert restrict_sources(("openalex", "crossref"), None) == (
        "openalex",
        "crossref",
    )


def test_restrict_sources_can_remove_every_source() -> None:
    assert restrict_sources(("openalex",), ("arxiv",)) == ()