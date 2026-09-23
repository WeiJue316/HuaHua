from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from research_agent.mcp_servers.arxiv.client import ArxivClient
from research_agent.runtime.research_service import run_arxiv_research
from research_agent.storage.migrations import connect_database

FIXTURE = Path(__file__).parents[1] / "fixtures" / "arxiv_search.xml"


@pytest.mark.asyncio
async def test_run_arxiv_research_persists_traceable_report(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text=FIXTURE.read_text(encoding="utf-8"),
            headers={"content-type": "application/atom+xml"},
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = ArxivClient(http_client=http_client)
        result = await run_arxiv_research(
            question="evidence chain evaluation",
            db_path=tmp_path / "research_agent.db",
            reports_root=tmp_path / "reports",
            client=client,
            max_results=5,
        )

    assert result.paper_count == 2
    assert result.evidence_count == 2
    assert result.report_path.is_file()
    report = result.report_path.read_text(encoding="utf-8")
    assert "evidence chain evaluation" in report
    assert "Traceable Retrieval for Scientific Agents" in report
    assert "2407.18940" in report
    assert "source_record_id" in report

    with connect_database(tmp_path / "research_agent.db") as conn:
        assert conn.execute("SELECT COUNT(*) FROM source_record").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM paper").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM evidence_span").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM paper_source_record").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM report").fetchone()[0] == 1
