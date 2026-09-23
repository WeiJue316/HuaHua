"""Parse Crossref works responses into normalized paper candidates."""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from typing import Any

from research_agent.mcp_servers.common import Author, OpenAccessInfo, PaperCandidate

TAG_PATTERN = re.compile(r"<[^>]+>")


class CrossrefParseError(ValueError):
    """Raised when a Crossref response cannot be parsed safely."""


@dataclass(frozen=True)
class CrossrefSearchPage:
    """Normalized Crossref search page."""

    papers: list[PaperCandidate]
    next_cursor: str | None


def normalize_crossref_doi(value: str) -> str:
    """Normalize a Crossref DOI value."""

    normalized = value.strip().lower()
    normalized = normalized.removeprefix("https://doi.org/")
    normalized = normalized.removeprefix("http://doi.org/")
    normalized = normalized.removeprefix("doi:")
    if not normalized:
        raise CrossrefParseError("Crossref DOI must not be empty")
    return normalized


def strip_markup(value: str | None) -> str | None:
    """Strip JATS/HTML tags and normalize whitespace."""

    if not value:
        return None
    text = html.unescape(TAG_PATTERN.sub(" ", value))
    normalized = " ".join(text.split())
    return normalized or None


def _first_title(work: dict[str, Any]) -> str:
    title = work.get("title")
    if isinstance(title, list) and title:
        return str(title[0])
    if isinstance(title, str) and title:
        return title
    doi = work.get("DOI")
    return f"Untitled work {doi}" if doi else "Untitled Crossref work"


def _authors(work: dict[str, Any]) -> list[Author]:
    authors: list[Author] = []
    for item in work.get("author") or []:
        name = " ".join(
            value for value in (item.get("given"), item.get("family")) if value
        )
        if not name:
            name = item.get("name")
        if not name:
            continue
        authors.append(
            Author(
                name=str(name),
                orcid=item.get("ORCID"),
                source_author_id=None,
            )
        )
    return authors


def _date_year(work: dict[str, Any]) -> int | None:
    for key in ("published", "published-online", "issued", "created"):
        date = work.get(key)
        if not isinstance(date, dict):
            continue
        parts = date.get("date-parts")
        if (
            isinstance(parts, list)
            and parts
            and isinstance(parts[0], list)
            and parts[0]
            and isinstance(parts[0][0], int)
        ):
            return int(parts[0][0])
    return None


def _published_at(work: dict[str, Any]) -> str | None:
    for key in ("published", "published-online", "issued", "created"):
        date = work.get(key)
        if not isinstance(date, dict):
            continue
        parts = date.get("date-parts")
        if (
            isinstance(parts, list)
            and parts
            and isinstance(parts[0], list)
            and len(parts[0]) >= 3
        ):
            year, month, day = parts[0][:3]
            return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
    return None


def _pdf_url(work: dict[str, Any]) -> str | None:
    for link in work.get("link") or []:
        if link.get("content-type") == "application/pdf" and link.get("URL"):
            return str(link["URL"])
    return None


def parse_work(work: dict[str, Any]) -> PaperCandidate:
    """Normalize one Crossref work."""

    raw_doi = work.get("DOI")
    if not isinstance(raw_doi, str):
        raise CrossrefParseError("Crossref work is missing DOI")
    doi = normalize_crossref_doi(raw_doi)
    title = _first_title(work)
    container_titles = work.get("container-title") or []
    venue = str(container_titles[0]) if container_titles else None
    pdf_url = _pdf_url(work)
    license_items = work.get("license") or []
    license_url = None
    if license_items and isinstance(license_items[0], dict):
        license_url = license_items[0].get("URL")
    landing_url = work.get("URL") or f"https://doi.org/{doi}"
    subjects = [str(value) for value in work.get("subject") or []]
    return PaperCandidate(
        source="crossref",
        source_record_id=doi,
        title=title,
        abstract=strip_markup(work.get("abstract")),
        authors=_authors(work),
        year=_date_year(work),
        published_at=_published_at(work),
        venue=venue,
        categories=subjects,
        doi=doi,
        landing_url=str(landing_url),
        pdf_url=pdf_url,
        open_access=OpenAccessInfo(
            is_oa=pdf_url is not None,
            status="unknown",
            license=str(license_url) if license_url else None,
            url=pdf_url,
        ),
        raw={
            "doi": raw_doi,
            "publisher": work.get("publisher"),
            "type": work.get("type"),
            "container-title": container_titles,
            "published": work.get("published"),
            "published-online": work.get("published-online"),
            "issued": work.get("issued"),
            "link": work.get("link") or [],
            "license": license_items,
            "subject": subjects,
        },
    )


def parse_search_response(json_text: str) -> CrossrefSearchPage:
    """Parse a Crossref work-list response."""

    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise CrossrefParseError(f"invalid Crossref JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise CrossrefParseError("Crossref response must be a JSON object")
    message = payload.get("message")
    if not isinstance(message, dict):
        raise CrossrefParseError("Crossref response is missing message")
    items = message.get("items")
    if not isinstance(items, list):
        raise CrossrefParseError("Crossref message.items must be a list")
    return CrossrefSearchPage(
        papers=[parse_work(item) for item in items if isinstance(item, dict)],
        next_cursor=message.get("next-cursor"),
    )
