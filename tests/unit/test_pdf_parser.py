from __future__ import annotations

from pathlib import Path

from reportlab.pdfgen import canvas

from research_agent.storage.pdf_parser import first_paragraph_locator, parse_pdf


def _write_pdf(path: Path, text: str) -> None:
    document = canvas.Canvas(str(path))
    document.drawString(72, 720, text)
    document.save()


def _write_pdf_pages(path: Path, lines: list[str]) -> None:
    document = canvas.Canvas(str(path))
    for index, line in enumerate(lines):
        if line:
            document.drawString(72, 720, line)
        if index != len(lines) - 1:
            document.showPage()
    document.save()


def test_parse_pdf_extracts_text_and_page_count(tmp_path: Path) -> None:
    pdf_path = tmp_path / "paper.pdf"
    _write_pdf(pdf_path, "Evidence chain fixture.")

    result = parse_pdf(pdf_path)

    assert result.page_count == 1
    assert "Evidence chain fixture" in result.text
    assert result.parser == "pypdf"
    assert result.parser_version


def test_first_paragraph_locator_relocates_quote_on_its_pdf_page(tmp_path: Path) -> None:
    pdf_path = tmp_path / "blank-first.pdf"
    _write_pdf_pages(pdf_path, ["", "Second page evidence."])

    result = parse_pdf(pdf_path)
    span = first_paragraph_locator(result)

    assert span is not None
    assert result.text[span.char_start : span.char_end] == span.quote
    assert span.page == 2
    assert span.paragraph_index == 0
    assert "Second page evidence." in span.quote
