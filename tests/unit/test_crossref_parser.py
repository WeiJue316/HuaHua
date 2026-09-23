from __future__ import annotations

from pathlib import Path

from research_agent.mcp_servers.crossref.parser import (
    normalize_crossref_doi,
    parse_search_response,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "crossref_search.json"


def test_parse_crossref_search_response() -> None:
    result = parse_search_response(FIXTURE.read_text(encoding="utf-8"))

    assert result.next_cursor == "next-page"
    assert len(result.papers) == 1
    paper = result.papers[0]
    assert paper.source == "crossref"
    assert paper.source_record_id == "10.1145/1234567.1234568"
    assert paper.doi == "10.1145/1234567.1234568"
    assert paper.title == "Traceable Retrieval for Scientific Agents"
    assert paper.abstract == (
        "We study evidence chains for scientific literature agents."
    )
    assert paper.year == 2024
    assert paper.venue == "Proceedings of the Example Conference"
    assert paper.pdf_url == "https://example.org/paper.pdf"
    assert [author.name for author in paper.authors] == [
        "Alice Example",
        "Bob Example",
    ]
    assert paper.raw["publisher"] == "Example Publisher"
    assert paper.raw["type"] == "proceedings-article"


def test_normalize_crossref_doi() -> None:
    assert normalize_crossref_doi("https://doi.org/10.1145/ABC") == "10.1145/abc"
    assert normalize_crossref_doi("10.1145/ABC") == "10.1145/abc"
