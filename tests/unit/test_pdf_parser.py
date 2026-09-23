from __future__ import annotations

from pathlib import Path

from reportlab.pdfgen import canvas

from research_agent.storage.pdf_parser import parse_pdf


def _write_pdf(path: Path, text: str) -> None:
    document = canvas.Canvas(str(path))
    document.drawString(72, 720, text)
    document.save()


def test_parse_pdf_extracts_text_and_page_count(tmp_path: Path) -> None:
    pdf_path = tmp_path / "paper.pdf"
    _write_pdf(pdf_path, "Evidence chain fixture.")

    result = parse_pdf(pdf_path)

    assert result.page_count == 1
    assert "Evidence chain fixture" in result.text
    assert result.parser == "pypdf"
    assert result.parser_version
