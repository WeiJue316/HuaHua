"""Parse OpenAlex works responses into normalized paper candidates."""

from __future__ import annotations

import json
import re
from typing import Any

from research_agent.mcp_servers.common import Author, OpenAccessInfo, PaperCandidate

OPENALEX_ID_PATTERN = re.compile(r"W\d+$", re.IGNORECASE)


class OpenAlexParseError(ValueError):
    """Raised when an OpenAlex response cannot be parsed safely."""


def normalize_openalex_id(value: str) -> str:
    """Normalize an OpenAlex work ID from a URL or raw value."""

    candidate = value.strip().rstrip("/")
    candidate = candidate.rsplit("/", 1)[-1]
    if not OPENALEX_ID_PATTERN.fullmatch(candidate):
        raise OpenAlexParseError(f"invalid OpenAlex identifier: {value!r}")
    return candidate.upper()


def normalize_doi(value: str | None) -> str | None:
    """Normalize an OpenAlex DOI value."""

    if not value:
        return None
    normalized = value.strip().lower()
    normalized = normalized.removeprefix("https://doi.org/")
    normalized = normalized.removeprefix("http://doi.org/")
    normalized = normalized.removeprefix("doi:")
    return normalized or None


def reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str | None:
    """Rebuild plain text from OpenAlex's inverted abstract index."""

    if not inverted_index:
        return None
    positioned_words: list[tuple[int, str]] = []
    for word, positions in inverted_index.items():
        for position in positions:
            positioned_words.append((int(position), word))
    if not positioned_words:
        return None
    positioned_words.sort(key=lambda item: item[0])
    return " ".join(word for _, word in positioned_words)


def _author_list(work: dict[str, Any]) -> list[Author]:
    authors: list[Author] = []
    for authorship in work.get("authorships") or []:
        author = authorship.get("author") or {}
        name = author.get("display_name")
        if not name:
            continue
        authors.append(
            Author(
                name=str(name),
                source_author_id=author.get("id"),
            )
        )
    return authors


def _landing_url(work: dict[str, Any], openalex_id: str, doi: str | None) -> str:
    primary_location = work.get("primary_location") or {}
    landing_url = primary_location.get("landing_page_url")
    if landing_url:
        return str(landing_url)
    if doi:
        return f"https://doi.org/{doi}"
    return f"https://openalex.org/{openalex_id}"


def _pdf_url(work: dict[str, Any]) -> str | None:
    primary_location = work.get("primary_location") or {}
    open_access = work.get("open_access") or {}
    value = primary_location.get("pdf_url") or open_access.get("oa_url")
    return str(value) if value else None


def parse_work(work: dict[str, Any]) -> PaperCandidate:
    """Normalize one OpenAlex work object."""

    raw_id = work.get("id")
    if not isinstance(raw_id, str):
        raise OpenAlexParseError("OpenAlex work is missing id")
    openalex_id = normalize_openalex_id(raw_id)
    doi = normalize_doi(work.get("doi"))
    title = work.get("display_name")
    if not title:
        raise OpenAlexParseError(f"OpenAlex work {openalex_id} is missing display_name")

    primary_location = work.get("primary_location") or {}
    source = primary_location.get("source") or {}
    open_access = work.get("open_access") or {}
    authors = _author_list(work)
    abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
    topics = [
        str(topic.get("display_name"))
        for topic in work.get("topics") or []
        if topic.get("display_name")
    ]
    category_terms = [
        str(concept.get("display_name"))
        for concept in work.get("concepts") or []
        if concept.get("display_name")
    ]
    categories = topics or category_terms

    return PaperCandidate(
        source="openalex",
        source_record_id=openalex_id,
        title=str(title),
        abstract=abstract,
        authors=authors,
        year=work.get("publication_year"),
        published_at=work.get("publication_date"),
        venue=source.get("display_name"),
        categories=categories,
        doi=doi,
        landing_url=_landing_url(work, openalex_id, doi),
        pdf_url=_pdf_url(work),
        open_access=OpenAccessInfo(
            is_oa=bool(open_access.get("is_oa")),
            status=str(open_access.get("oa_status") or "unknown"),
            url=_pdf_url(work),
        ),
        raw={
            "openalex_id": openalex_id,
            "doi": work.get("doi"),
            "display_name": title,
            "publication_year": work.get("publication_year"),
            # OpenAlex 返回被引数但此前被丢弃；引用图扩展和论文报告都需要它
            "cited_by_count": work.get("cited_by_count"),
            "publication_date": work.get("publication_date"),
            "type": work.get("type"),
            "language": work.get("language"),
            "primary_location": primary_location,
            "open_access": open_access,
            "authorships": work.get("authorships") or [],
            "abstract_inverted_index": work.get("abstract_inverted_index"),
            "topics": work.get("topics") or [],
            "concepts": work.get("concepts") or [],
        },
    )


def parse_search_response(json_text: str) -> list[PaperCandidate]:
    """Parse an OpenAlex works list response."""

    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise OpenAlexParseError(f"invalid OpenAlex JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise OpenAlexParseError("OpenAlex response must be a JSON object")
    results = payload.get("results")
    if results is None:
        raise OpenAlexParseError("OpenAlex response is missing results")
    if not isinstance(results, list):
        raise OpenAlexParseError("OpenAlex results must be a list")
    return [parse_work(work) for work in results if isinstance(work, dict)]
