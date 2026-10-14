"""PDF text extraction with a stable parser boundary."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path

from pypdf import PdfReader

PAGE_SEPARATOR = "\n\n"


class PdfParseError(ValueError):
    """Raised when a PDF cannot be parsed safely."""


@dataclass(frozen=True)
class PdfParseResult:
    """Extracted text and parser metadata.

    ``pages`` keeps one string per PDF page, including blank pages, in PDF
    order. ``text`` is those pages joined with ``PAGE_SEPARATOR``.
    """

    text: str
    page_count: int
    parser: str
    parser_version: str
    pages: tuple[str, ...]


@dataclass(frozen=True)
class TextSpan:
    """A quote that is an exact slice of the parsed document text."""

    quote: str
    page: int
    paragraph_index: int
    char_start: int
    char_end: int


def parse_pdf(path: Path) -> PdfParseResult:
    """Extract text from every page of a PDF."""

    try:
        reader = PdfReader(str(path))
        pages = tuple((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:
        raise PdfParseError(f"PDF parse failed: {exc}") from exc
    return PdfParseResult(
        text=PAGE_SEPARATOR.join(pages),
        page_count=len(pages),
        parser="pypdf",
        parser_version=version("pypdf"),
        pages=pages,
    )


def first_paragraph_locator(result: PdfParseResult) -> TextSpan | None:
    """Locate the first non-blank paragraph without changing its characters.

    Offsets refer to ``result.text``. Blank pages stay in the page sequence,
    so ``page`` is the 1-based PDF page rather than the index among pages
    that happened to contain text.
    """

    document_offset = 0
    for page_number, page_text in enumerate(result.pages, start=1):
        paragraph_index = 0
        search_from = 0
        while search_from <= len(page_text):
            break_at = page_text.find(PAGE_SEPARATOR, search_from)
            end = len(page_text) if break_at == -1 else break_at
            quote = page_text[search_from:end]
            if quote.strip():
                char_start = document_offset + search_from
                return TextSpan(
                    quote=quote,
                    page=page_number,
                    paragraph_index=paragraph_index,
                    char_start=char_start,
                    char_end=char_start + len(quote),
                )
            if break_at == -1:
                break
            paragraph_index += 1
            search_from = break_at + len(PAGE_SEPARATOR)
        document_offset += len(page_text)
        if page_number != result.page_count:
            document_offset += len(PAGE_SEPARATOR)
    return None
