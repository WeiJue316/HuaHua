"""Parse arXiv Atom API responses into normalized paper candidates."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from research_agent.mcp_servers.common import Author, OpenAccessInfo, PaperCandidate

ATOM_NS = "http://www.w3.org/2005/Atom"
ARXIV_NS = "http://arxiv.org/schemas/atom"
NS = {"atom": ATOM_NS, "arxiv": ARXIV_NS}
NEW_ID_PATTERN = re.compile(r"^\d{4}\.\d{4,5}$")
OLD_ID_PATTERN = re.compile(r"^[a-z-]+(?:\.[A-Z]{2})?/\d{7}$", re.IGNORECASE)
VERSION_PATTERN = re.compile(r"v(?P<version>\d+)$", re.IGNORECASE)


class ArxivParseError(ValueError):
    """Raised when an arXiv response cannot be parsed safely."""


def _text(element: ET.Element, path: str) -> str | None:
    child = element.find(path, NS)
    if child is None or child.text is None:
        return None
    value = " ".join(child.text.split())
    return value or None


def _normalize_whitespace(value: str | None) -> str:
    return " ".join(value.split()) if value else ""


def normalize_arxiv_id(value: str) -> str:
    """Normalize an arXiv identifier from a URL or raw value."""

    candidate = value.strip().rstrip("/")
    candidate = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "", candidate, flags=re.IGNORECASE)
    candidate = VERSION_PATTERN.sub("", candidate)
    if not (NEW_ID_PATTERN.fullmatch(candidate) or OLD_ID_PATTERN.fullmatch(candidate)):
        raise ArxivParseError(f"invalid arXiv identifier: {value!r}")
    return candidate


def _entry_id(entry: ET.Element) -> tuple[str, str | None]:
    raw_id = _text(entry, "atom:id")
    if raw_id is None:
        raise ArxivParseError("arXiv entry is missing atom:id")
    source_record_id = normalize_arxiv_id(raw_id)
    version_match = VERSION_PATTERN.search(raw_id.rstrip("/"))
    source_version = f"v{version_match.group('version')}" if version_match else None
    return source_record_id, source_version


def _entry_links(entry: ET.Element, source_record_id: str) -> tuple[str, str]:
    landing_url = f"https://arxiv.org/abs/{source_record_id}"
    pdf_url = f"https://arxiv.org/pdf/{source_record_id}"
    for link in entry.findall("atom:link", NS):
        href = link.attrib.get("href")
        if not href:
            continue
        if link.attrib.get("rel") == "alternate":
            landing_url = href
        if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
            pdf_url = href
    return landing_url, pdf_url


def parse_search_response(xml_text: str) -> list[PaperCandidate]:
    """Parse an arXiv Atom search response."""

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ArxivParseError(f"invalid arXiv XML: {exc}") from exc

    papers: list[PaperCandidate] = []
    for entry in root.findall("atom:entry", NS):
        source_record_id, source_version = _entry_id(entry)
        title = _normalize_whitespace(_text(entry, "atom:title"))
        abstract = _normalize_whitespace(_text(entry, "atom:summary")) or None
        authors = [
            Author(name=name)
            for author in entry.findall("atom:author", NS)
            if (name := _text(author, "atom:name"))
        ]
        published_at = _text(entry, "atom:published")
        updated_at = _text(entry, "atom:updated")
        year = int(published_at[:4]) if published_at and published_at[:4].isdigit() else None
        categories = [
            term
            for category in entry.findall("atom:category", NS)
            if (term := category.attrib.get("term"))
        ]
        primary_category = entry.find("arxiv:primary_category", NS)
        if primary_category is not None:
            primary_term = primary_category.attrib.get("term")
            if primary_term and primary_term not in categories:
                categories.insert(0, primary_term)
        landing_url, pdf_url = _entry_links(entry, source_record_id)
        license_text = _text(entry, "arxiv:license")
        raw = {
            "entry_xml": ET.tostring(entry, encoding="unicode"),
            "source_record_id": source_record_id,
            "source_version": source_version,
            "title": title,
            "abstract": abstract,
            "authors": [author.name for author in authors],
            "published_at": published_at,
            "updated_at": updated_at,
            "categories": categories,
            "doi": _text(entry, "arxiv:doi"),
            "journal_ref": _text(entry, "arxiv:journal_ref"),
        }
        papers.append(
            PaperCandidate(
                source="arxiv",
                source_record_id=source_record_id,
                source_version=source_version,
                title=title,
                abstract=abstract,
                authors=authors,
                year=year,
                published_at=published_at,
                updated_at=updated_at,
                venue=_text(entry, "arxiv:journal_ref"),
                categories=categories,
                doi=_text(entry, "arxiv:doi"),
                landing_url=landing_url,
                pdf_url=pdf_url,
                open_access=OpenAccessInfo(
                    is_oa=True,
                    status="green",
                    license=license_text,
                    url=pdf_url,
                ),
                raw=raw,
            )
        )
    return papers