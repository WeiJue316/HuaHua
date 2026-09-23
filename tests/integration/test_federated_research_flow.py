from __future__ import annotations

import io
import json
from pathlib import Path

import httpx
import pytest
from reportlab.pdfgen import canvas

from research_agent.mcp_servers.arxiv.client import ArxivClient
from research_agent.mcp_servers.openalex.client import OpenAlexClient
from research_agent.runtime.research_service import run_federated_research
from research_agent.storage.migrations import connect_database

ARXIV_FIXTURE = Path(__file__).parents[1] / "fixtures" / "arxiv_search.xml"
OPENALEX_FIXTURE = Path(__file__).parents[1] / "fixtures" / "openalex_search.json"

def _pdf_bytes(text: str) -> bytes:
    buffer = io.BytesIO()
    document = canvas.Canvas(buffer)
    document.drawString(72, 720, text)
    document.save()
    return buffer.getvalue()

@pytest.mark.asyncio
async def test_federated_research_merges_doi_and_keeps_provenance(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host in {"export.arxiv.org", "arxiv.org"}:
            if "/pdf/" in request.url.path:
                return httpx.Response(
                    200,
                    content=_pdf_bytes(f"Full text evidence for {request.url.path}"),
                    headers={"content-type": "application/pdf"},
                    request=request,
                )
            return httpx.Response(
                200,
                text=ARXIV_FIXTURE.read_text(encoding="utf-8"),
                headers={"content-type": "application/atom+xml"},
                request=request,
            )
        if request.url.host == "api.openalex.org":
            return httpx.Response(
                200,
                json=json.loads(OPENALEX_FIXTURE.read_text(encoding="utf-8")),
                headers={"content-type": "application/json"},
                request=request,
            )
        raise AssertionError(f"unexpected request: {request.url}")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        result = await run_federated_research(
            question="evidence chain",
            db_path=tmp_path / "research_agent.db",
            reports_root=tmp_path / "reports",
            clients={
                "arxiv": ArxivClient(http_client=http_client),
                "openalex": OpenAlexClient(http_client=http_client),
            },
            max_results_per_source=5,
            download_pdf=True,
            artifact_root=tmp_path / "archive",
        )

    assert result.source_counts == {"arxiv": 2, "openalex": 1}
    assert result.paper_count == 2
    assert result.evidence_count == 5
    assert result.claim_count == 5
    assert result.file_count == 2
    assert result.document_count == 2
    assert result.report_path.is_file()
    report = result.report_path.read_text(encoding="utf-8")
    assert "arxiv" in report
    assert "openalex" in report
    assert "## Claims" in report
    assert "page 1" in report

    with connect_database(tmp_path / "research_agent.db") as conn:
        assert conn.execute("SELECT COUNT(*) FROM source_record").fetchone()[0] == 3
        assert conn.execute("SELECT COUNT(*) FROM paper").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM paper_source_record").fetchone()[0] == 3
        assert conn.execute("SELECT COUNT(*) FROM evidence_span").fetchone()[0] == 5
        assert conn.execute("SELECT COUNT(*) FROM claim").fetchone()[0] == 5
        assert conn.execute("SELECT COUNT(*) FROM claim_evidence").fetchone()[0] == 5
        assert conn.execute("SELECT COUNT(*) FROM file").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM document").fetchone()[0] == 2
        full_text_count = conn.execute(
            "SELECT COUNT(*) FROM evidence_span WHERE evidence_level = 'full_text'"
        ).fetchone()[0]
        assert full_text_count == 2
