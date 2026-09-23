"""Parse DBLP publication search responses."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from research_agent.mcp_servers.common import Author, OpenAccessInfo, PaperCandidate


class DblpParseError(ValueError):
    """Raised when a DBLP response cannot be parsed safely."""


@dataclass(frozen=True)
class DblpSearchPage:
    """Normalized DBLP search page."""

    total: int
    papers: list[PaperCandidate]


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def normalize_dblp_doi(value: str | None) -> str | None:
    """Normalize a DBLP DOI value."""

    if not value:
        return None
    normalized = value.strip().lower()
    normalized = normalized.removeprefix("https://doi.org/")
    normalized = normalized.removeprefix("http://doi.org/")
    normalized = normalized.removeprefix("doi:")
    return normalized or None


def _authors(info: dict[str, Any]) -> list[Author]:
    authors_container = info.get("authors") or {}
    author_items = authors_container.get("author") if isinstance(authors_container, dict) else None
    authors: list[Author] = []
    for item in _as_list(author_items):
        name: str | None
        if isinstance(item, str):
            name = item
            source_author_id = None
        elif isinstance(item, dict):
            raw_name = item.get("text")
            name = str(raw_name) if raw_name else None
            source_author_id = item.get("@pid")
        else:
            continue
        if name:
            authors.append(
                Author(name=str(name), source_author_id=source_author_id)
            )
    return authors


def parse_paper(info: dict[str, Any]) -> PaperCandidate:
    """Normalize one DBLP publication info object."""

    key = info.get("key")
    if not isinstance(key, str) or not key:
        raise DblpParseError("DBLP record is missing key")
    title = info.get("title")
    if not title:
        raise DblpParseError(f"DBLP record {key} is missing title")
    doi = normalize_dblp_doi(info.get("doi"))
    landing_url = info.get("url") or f"https://dblp.org/rec/{key}"
    raw_year = info.get("year")
    year = (
        int(raw_year)
        if isinstance(raw_year, (str, int)) and str(raw_year).isdigit()
        else None
    )
    return PaperCandidate(
        source="dblp",
        source_record_id=key,
        title=str(title),
        abstract=None,
        authors=_authors(info),
        year=year,
        venue=info.get("venue"),
        doi=doi,
        landing_url=str(landing_url),
        pdf_url=None,
        open_access=OpenAccessInfo(is_oa=False, status="unknown"),
        raw={
            "key": key,
            "type": info.get("type"),
            "ee": info.get("ee"),
            "url": info.get("url"),
            "doi": info.get("doi"),
            "venue": info.get("venue"),
            "year": info.get("year"),
        },
    )


def parse_search_response(json_text: str) -> DblpSearchPage:
    """Parse a DBLP publication-search response."""

    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise DblpParseError(f"invalid DBLP JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise DblpParseError("DBLP response must be a JSON object")
    result = payload.get("result")
    if not isinstance(result, dict):
        raise DblpParseError("DBLP response is missing result")
    hits = result.get("hits")
    if not isinstance(hits, dict):
        raise DblpParseError("DBLP response is missing hits")
    raw_hits = _as_list(hits.get("hit"))
    papers: list[PaperCandidate] = []
    for hit in raw_hits:
        if not isinstance(hit, dict):
            continue
        info = hit.get("info")
        if isinstance(info, dict):
            papers.append(parse_paper(info))
    return DblpSearchPage(
        total=int(hits.get("@total") or len(papers)),
        papers=papers,
    )
