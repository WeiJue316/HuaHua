from __future__ import annotations

import io
import json
from pathlib import Path

import httpx
import pytest
from reportlab.pdfgen import canvas

from research_agent.mcp_servers.arxiv.client import ArxivClient
from research_agent.mcp_servers.openalex.client import OpenAlexClient
from research_agent.planner.planner import plan_research
from research_agent.runtime.research_service import (
    ResearchExecutionError,
    run_federated_research,
)
from research_agent.storage.migrations import connect_database
from research_agent.storage.pdf_parser import PdfParseError, parse_pdf

ARXIV_FIXTURE = Path(__file__).parents[1] / "fixtures" / "arxiv_search.xml"
OPENALEX_FIXTURE = Path(__file__).parents[1] / "fixtures" / "openalex_search.json"

def _pdf_bytes(text: str) -> bytes:
    buffer = io.BytesIO()
    document = canvas.Canvas(buffer)
    document.drawString(72, 720, text)
    document.save()
    return buffer.getvalue()


def _pdf_pages(lines: list[str]) -> bytes:
    buffer = io.BytesIO()
    document = canvas.Canvas(buffer)
    for index, line in enumerate(lines):
        if line:
            document.drawString(72, 720, line)
        if index != len(lines) - 1:
            document.showPage()
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
        plan = plan_research(
            "evidence chain",
            available_sources=("arxiv", "openalex"),
            max_results_per_source=5,
            max_sources=2,
        )
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
            plan=plan,
        )

    assert result.source_counts == {"arxiv": 2, "openalex": 1}
    assert result.source_errors == {}
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
        assert conn.execute("SELECT COUNT(*) FROM plan").fetchone()[0] == 1
        # route, search, persist, judge_relevance, synthesize, validate, report
        assert conn.execute("SELECT COUNT(*) FROM plan_step").fetchone()[0] == 7
        step_types = {
            row[0]
            for row in conn.execute("SELECT step_type FROM plan_step")
        }
        assert step_types == {
            "route_sources",
            "search_sources",
            "persist_results",
            "judge_relevance",
            "synthesize_claims",
            "validate_citations",
            "generate_report",
        }
        assert conn.execute("SELECT COUNT(*) FROM step_attempt").fetchone()[0] == 7
        assert (
            conn.execute("SELECT status FROM run WHERE id = ?", (result.run_id,)).fetchone()[0]
            == "COMPLETED"
        )
        assert conn.execute(
            "SELECT COUNT(*) FROM audit_event WHERE action = 'route_sources'"
        ).fetchone()[0] == 1
        full_text_count = conn.execute(
            "SELECT COUNT(*) FROM evidence_span WHERE evidence_level = 'full_text'"
        ).fetchone()[0]
        assert full_text_count == 2


@pytest.mark.asyncio
async def test_full_text_evidence_relocates_onto_the_parsed_page(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host in {"export.arxiv.org", "arxiv.org"}:
            if "/pdf/" in request.url.path:
                return httpx.Response(
                    200,
                    content=_pdf_pages(["", "Second page evidence."]),
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
        plan = plan_research(
            "evidence chain",
            available_sources=("arxiv",),
            max_results_per_source=5,
            max_sources=1,
        )
        await run_federated_research(
            question="evidence chain",
            db_path=tmp_path / "research_agent.db",
            reports_root=tmp_path / "reports",
            clients={"arxiv": ArxivClient(http_client=http_client)},
            max_results_per_source=5,
            download_pdf=True,
            artifact_root=tmp_path / "archive",
            plan=plan,
        )

    with connect_database(tmp_path / "research_agent.db") as conn:
        rows = conn.execute(
            """
            SELECT evidence_span.quote, evidence_span.locator_json, document.text_path
            FROM evidence_span
            JOIN document ON document.id = evidence_span.document_id
            WHERE evidence_span.evidence_level = 'full_text'
            """
        ).fetchall()
    assert rows
    for quote, locator_json, text_path in rows:
        locator = json.loads(locator_json)
        document_text = Path(text_path).read_text(encoding="utf-8")
        assert document_text[locator["char_start"] : locator["char_end"]] == quote
        assert locator["page"] == 2
        assert "Second page evidence." in quote


@pytest.mark.asyncio
async def test_evidence_chain_ablation_persists_papers_without_evidence(
    tmp_path: Path,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host in {"export.arxiv.org", "arxiv.org"}:
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
        plan = plan_research(
            "evidence chain",
            available_sources=("arxiv", "openalex"),
            max_results_per_source=5,
            max_sources=2,
        )
        result = await run_federated_research(
            question="evidence chain",
            db_path=tmp_path / "a1.db",
            reports_root=tmp_path / "reports-a1",
            clients={
                "arxiv": ArxivClient(http_client=http_client),
                "openalex": OpenAlexClient(http_client=http_client),
            },
            max_results_per_source=5,
            plan=plan,
            evidence_chain=False,
        )

    assert result.paper_count > 0
    assert result.evidence_count == 0
    assert result.claim_count == result.paper_count
    with connect_database(tmp_path / "a1.db") as conn:
        assert conn.execute("SELECT COUNT(*) FROM evidence_span").fetchone()[0] == 0
        statuses = {
            row[0] for row in conn.execute("SELECT support_status FROM claim")
        }
    assert statuses == {"unsupported"}


@pytest.mark.asyncio
async def test_retry_after_a_failed_persist_does_not_duplicate_rows(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parses = 0

    def flaky_parse(path: Path):
        nonlocal parses
        parses += 1
        if parses == 1:
            raise PdfParseError("transient parse failure")
        return parse_pdf(path)

    monkeypatch.setattr("research_agent.runtime.research_service.parse_pdf", flaky_parse)
    pdf_body = _pdf_bytes("Full text evidence")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host in {"export.arxiv.org", "arxiv.org"}:
            if "/pdf/" in request.url.path:
                return httpx.Response(
                    200,
                    content=pdf_body,
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

    error: ResearchExecutionError | None = None
    result = None
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        plan = plan_research(
            "evidence chain",
            available_sources=("arxiv", "openalex"),
            max_results_per_source=5,
            max_sources=2,
        )
        try:
            result = await run_federated_research(
                question="evidence chain",
                db_path=tmp_path / "retry.db",
                reports_root=tmp_path / "reports-retry",
                clients={
                    "arxiv": ArxivClient(http_client=http_client),
                    "openalex": OpenAlexClient(http_client=http_client),
                },
                max_results_per_source=5,
                download_pdf=True,
                artifact_root=tmp_path / "archive",
                plan=plan,
            )
        except ResearchExecutionError as exc:
            error = exc

    assert error is None, error
    assert result is not None
    assert result.file_count == 2
    assert result.document_count == 2
    with connect_database(tmp_path / "retry.db") as conn:
        assert conn.execute("SELECT COUNT(*) FROM file").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM evidence_span").fetchone()[0] == (
            result.evidence_count
        )
        attempts = conn.execute(
            """
            SELECT COUNT(*)
            FROM step_attempt
            JOIN plan_step ON plan_step.id = step_attempt.step_id
            WHERE plan_step.step_key = 'persist_results'
            """
        ).fetchone()[0]
    assert attempts == 2

