from __future__ import annotations

from pathlib import Path

from research_agent.mcp_servers.semantic_scholar.parser import (
    parse_paper,
    parse_search_response,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "semantic_scholar_search.json"


def test_parse_semantic_scholar_search_response() -> None:
    result = parse_search_response(FIXTURE.read_text(encoding="utf-8"))

    assert result.total == 1
    assert result.next_offset == 1
    assert len(result.papers) == 1
    paper = result.papers[0]
    assert paper.source == "semantic_scholar"
    assert paper.source_record_id == "abc123paper"
    assert paper.doi == "10.1000/example"
    assert paper.title == "Traceable Retrieval for Scientific Agents"
    assert paper.abstract == (
        "We study evidence chains for scientific literature agents."
    )
    assert paper.year == 2024
    assert paper.venue == "Example Conference"
    assert paper.pdf_url == "https://example.org/paper.pdf"
    assert [author.name for author in paper.authors] == [
        "Alice Example",
        "Bob Example",
    ]
    assert paper.raw["arxiv_id"] == "2407.18940"
    assert paper.raw["fields_of_study"] == ["Computer Science"]


def test_parse_semantic_scholar_paper_handles_empty_open_access() -> None:
    paper = parse_paper(
        {
            "paperId": "paper-1",
            "title": "A paper",
            "externalIds": {},
            "authors": [],
        }
    )

    assert paper.open_access.is_oa is False
    assert paper.pdf_url is None
