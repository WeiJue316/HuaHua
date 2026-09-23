from __future__ import annotations

from pathlib import Path

from research_agent.mcp_servers.openalex.parser import (
    normalize_openalex_id,
    parse_search_response,
    reconstruct_abstract,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "openalex_search.json"


def test_parse_openalex_search_response() -> None:
    papers = parse_search_response(FIXTURE.read_text(encoding="utf-8"))

    assert len(papers) == 1
    paper = papers[0]
    assert paper.source == "openalex"
    assert paper.source_record_id == "W123456789"
    assert paper.doi == "10.1000/example"
    assert paper.title == "Traceable Retrieval for Scientific Agents"
    assert paper.year == 2024
    assert paper.venue == "arXiv"
    assert paper.abstract == "We study evidence chains for scientific agents."
    assert paper.landing_url == "https://example.org/paper"
    assert paper.pdf_url == "https://example.org/paper.pdf"
    assert paper.open_access.is_oa is True
    assert paper.open_access.status == "green"
    assert [author.name for author in paper.authors] == ["Alice Example", "Bob Example"]
    assert paper.raw["openalex_id"] == "W123456789"


def test_reconstruct_abstract_orders_words() -> None:
    assert (
        reconstruct_abstract({"world": [1], "Hello": [0], "again": [2]})
        == "Hello world again"
    )


def test_normalize_openalex_id_accepts_urls() -> None:
    assert normalize_openalex_id("https://openalex.org/W123456789") == "W123456789"
    assert normalize_openalex_id("W123456789") == "W123456789"


def test_parse_work_preserves_the_citation_count() -> None:
    """OpenAlex returns cited_by_count; it used to be dropped.

    Citation counts feed the citation-graph candidate ranking and appear in
    the thesis, so they must survive parsing.
    """

    from research_agent.mcp_servers.openalex.parser import parse_work

    paper = parse_work(
        {
            "id": "https://openalex.org/W123",
            "doi": "https://doi.org/10.1/example",
            "display_name": "A paper",
            "publication_year": 2024,
            "cited_by_count": 42,
            "primary_location": {},
        }
    )

    assert paper.raw["cited_by_count"] == 42
