"""Parse Semantic Scholar responses into normalized paper candidates."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from research_agent.mcp_servers.common import Author, OpenAccessInfo, PaperCandidate


class SemanticScholarParseError(ValueError):
    """Raised when a Semantic Scholar response cannot be parsed safely."""


@dataclass(frozen=True)
class SemanticScholarSearchPage:
    """Normalized Semantic Scholar search page."""

    total: int
    next_offset: int | None
    papers: list[PaperCandidate]


def normalize_semantic_scholar_doi(value: str | None) -> str | None:
    """Normalize a Semantic Scholar DOI value."""

    if not value:
        return None
    normalized = value.strip().lower()
    normalized = normalized.removeprefix("https://doi.org/")
    normalized = normalized.removeprefix("http://doi.org/")
    normalized = normalized.removeprefix("doi:")
    return normalized or None


def _authors(paper: dict[str, Any]) -> list[Author]:
    authors: list[Author] = []
    for item in paper.get("authors") or []:
        name = item.get("name")
        if not name:
            continue
        authors.append(
            Author(
                name=str(name),
                source_author_id=item.get("authorId"),
            )
        )
    return authors


def parse_paper(paper: dict[str, Any]) -> PaperCandidate:
    """Normalize one Semantic Scholar paper object."""

    paper_id = paper.get("paperId")
    if not isinstance(paper_id, str) or not paper_id:
        raise SemanticScholarParseError("Semantic Scholar paper is missing paperId")
    title = paper.get("title")
    if not title:
        raise SemanticScholarParseError(
            f"Semantic Scholar paper {paper_id} is missing title"
        )
    external_ids = paper.get("externalIds") or {}
    doi = normalize_semantic_scholar_doi(external_ids.get("DOI"))
    arxiv_id = external_ids.get("ArXiv")
    open_access_pdf = paper.get("openAccessPdf") or {}
    pdf_url = open_access_pdf.get("url")
    url = paper.get("url") or f"https://www.semanticscholar.org/paper/{paper_id}"
    fields = [str(value) for value in paper.get("fieldsOfStudy") or []]
    return PaperCandidate(
        source="semantic_scholar",
        source_record_id=paper_id,
        title=str(title),
        abstract=paper.get("abstract"),
        authors=_authors(paper),
        year=paper.get("year"),
        published_at=paper.get("publicationDate"),
        venue=paper.get("venue"),
        categories=fields,
        doi=doi,
        landing_url=str(url),
        pdf_url=str(pdf_url) if pdf_url else None,
        open_access=OpenAccessInfo(
            is_oa=pdf_url is not None,
            status=str(open_access_pdf.get("status") or "unknown").lower(),
            url=str(pdf_url) if pdf_url else None,
        ),
        raw={
            "paper_id": paper_id,
            "corpus_id": paper.get("corpusId"),
            "external_ids": external_ids,
            "arxiv_id": arxiv_id,
            "fields_of_study": fields,
            "citation_count": paper.get("citationCount"),
            "reference_count": paper.get("referenceCount"),
            "open_access_pdf": open_access_pdf,
        },
    )


def parse_search_response(json_text: str) -> SemanticScholarSearchPage:
    """Parse a Semantic Scholar paper-search response."""

    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise SemanticScholarParseError(
            f"invalid Semantic Scholar JSON: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise SemanticScholarParseError("Semantic Scholar response must be an object")
    data = payload.get("data")
    if not isinstance(data, list):
        raise SemanticScholarParseError("Semantic Scholar response is missing data")
    return SemanticScholarSearchPage(
        total=int(payload.get("total") or 0),
        next_offset=payload.get("next"),
        papers=[parse_paper(item) for item in data if isinstance(item, dict)],
    )
