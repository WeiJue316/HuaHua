"""PDF text extraction with a stable parser boundary."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path

from pypdf import PdfReader


class PdfParseError(ValueError):
    """Raised when a PDF cannot be parsed safely."""


@dataclass(frozen=True)
class PdfParseResult:
    """Extracted text and parser metadata."""

    text: str
    page_count: int
    parser: str
    parser_version: str


def parse_pdf(path: Path) -> PdfParseResult:
    """Extract text from every page of a PDF."""

    try:
        reader = PdfReader(str(path))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
    except Exception as exc:
        raise PdfParseError(f"PDF parse failed: {exc}") from exc
    return PdfParseResult(
        text="\n\n".join(page for page in pages if page),
        page_count=len(reader.pages),
        parser="pypdf",
        parser_version=version("pypdf"),
    )
