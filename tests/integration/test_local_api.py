from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from research_agent.cli import app as cli_app
from research_agent.evidence.claims import ClaimDraft
from research_agent.interfaces.app import LOCAL_API_HOSTS, create_app
from research_agent.mcp_servers.common import Author, OpenAccessInfo, PaperCandidate
from research_agent.storage.migrations import apply_migrations, connect_database
from research_agent.storage.repository import ResearchRepository

SECRET = "super-secret-token"
LOCAL_SECRET_PATH = "C:/Users/secret/paper.pdf"


def _candidate() -> PaperCandidate:
    return PaperCandidate(
        source="arxiv",
        source_record_id="2407.18940",
        source_version="v1",
        title="Traceable Retrieval",
        abstract="We study evidence chains.",
        authors=[Author(name="Alice Example")],
        year=2024,
        venue="JMLR",
        doi="10.1000/example",
        landing_url="https://arxiv.org/abs/2407.18940",
        pdf_url="https://arxiv.org/pdf/2407.18940",
        open_access=OpenAccessInfo(is_oa=True, status="green", url=None),
        raw={"api_key": SECRET},
    )


def _seed(tmp_path: Path) -> dict[str, str]:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)
    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        project_id = repo.create_project("project")
        question_id = repo.create_research_question(project_id, "What is an evidence chain?")
        run_id = repo.create_run(
            project_id,
            question_id,
            config={"api_key": SECRET},
        )
        plan_id = repo.record_plan(run_id=run_id, plan_json={"steps": ["route_sources"]})
        repo.record_plan_step(
            plan_id=plan_id,
            step_key="route_sources",
            step_type="route_sources",
            status="SUCCEEDED",
        )
        repo.record_plan_step(
            plan_id=plan_id,
            step_key="search_sources",
            step_type="search_sources",
            depends_on=["route_sources"],
            status="SUCCEEDED",
        )
        call_id = repo.record_source_call(
            run_id=run_id,
            source="arxiv",
            tool_name="arxiv_search_papers",
            request_json={"query": "evidence chain"},
            status="success",
            started_at="2026-01-01T00:00:00Z",
        )
        source_record_id = repo.record_source_record(
            source_call_id=call_id,
            candidate=_candidate(),
            api_endpoint="https://export.arxiv.org/api/query",
            retrieved_at="2026-01-01T00:00:00Z",
        )
        paper_id, _ = repo.upsert_paper(_candidate())
        repo.link_paper_source_record(
            paper_id=paper_id,
            source_record_id=source_record_id,
            merge_reason="doi",
            is_primary_metadata=True,
        )
        repo.record_audit_event(
            run_id=run_id,
            action="semantic_relevance",
            target_type="paper",
            target_id=source_record_id,
            decision="denied",
            details={
                "reason": "out of scope",
                "domain_scope": "out_of_scope",
                "answer_role": "none",
            },
        )
        file_id = repo.record_file(
            paper_id=paper_id,
            kind="pdf",
            sha256="a" * 64,
            path=LOCAL_SECRET_PATH,
            size_bytes=12,
            content_type="application/pdf",
            source_url="https://arxiv.org/pdf/2407.18940",
            retrieved_at="2026-01-01T00:00:00Z",
        )
        document_id = repo.record_document(
            file_id=file_id,
            parser="pypdf",
            parser_version="1",
            text_path=LOCAL_SECRET_PATH,
            text_sha256="b" * 64,
            locator_scheme="page_paragraph",
            parse_status="success",
        )
        evidence_id = repo.record_evidence_span(
            paper_id=paper_id,
            source_record_id=source_record_id,
            quote="We study evidence chains.",
            locator={"section": "Abstract"},
            evidence_level="abstract",
            extraction_method="rule",
            confidence=0.8,
            verified=1,
        )
        full_text_id = repo.record_evidence_span(
            paper_id=paper_id,
            source_record_id=source_record_id,
            quote="Full text sentence.",
            locator={"page": 2, "char_start": 4, "char_end": 9},
            evidence_level="full_text",
            extraction_method="pdf_parser",
            confidence=0.7,
            verified=0,
            file_id=file_id,
            document_id=document_id,
        )
        report_id = repo.record_report(
            run_id=run_id,
            path="reports/run/report.md",
            content="# Report\n",
        )
        claim_id = repo.record_claim(
            report_id=report_id,
            claim=ClaimDraft(
                claim_text="The paper studies evidence chains.",
                claim_type="fact",
                support_status="supported",
                confidence=0.8,
                evidence_span_ids=[evidence_id],
            ),
        )
        conn.commit()
    return {
        "db_path": str(db_path),
        "run_id": run_id,
        "paper_id": paper_id,
        "source_record_id": source_record_id,
        "evidence_id": evidence_id,
        "full_text_id": full_text_id,
        "file_id": file_id,
        "document_id": document_id,
        "claim_id": claim_id,
    }


def _client(tmp_path: Path) -> tuple[TestClient, dict[str, str]]:
    ids = _seed(tmp_path)
    return TestClient(create_app(Path(ids["db_path"]))), ids


def test_read_api_serves_the_evidence_chain(tmp_path: Path) -> None:
    client, ids = _client(tmp_path)

    listed = client.get("/v1/runs")
    assert listed.status_code == 200
    assert listed.headers["content-type"].startswith("application/json")
    body = listed.json()
    assert body["api_version"] == "v1"
    assert body["total"] == 1
    assert body["items"][0]["question_text"] == "What is an evidence chain?"
    assert body["items"][0]["paper_count"] == 1
    assert body["items"][0]["evidence_count"] == 2
    assert body["items"][0]["claim_count"] == 1
    assert "project_id" not in body["items"][0]

    detail = client.get(f"/v1/runs/{ids['run_id']}").json()
    assert detail["project_id"]
    assert detail["question_id"]

    steps = client.get(f"/v1/runs/{ids['run_id']}/steps").json()
    assert [step["step_key"] for step in steps["items"]] == [
        "route_sources",
        "search_sources",
    ]
    assert steps["items"][1]["depends_on"] == ["route_sources"]

    sources = client.get(f"/v1/runs/{ids['run_id']}/sources").json()
    assert sources["items"] == [
        {
            "source": "arxiv",
            "call_count": 1,
            "success_count": 1,
            "failed_count": 0,
            "paper_count": 1,
        }
    ]

    papers = client.get(f"/v1/runs/{ids['run_id']}/papers").json()
    paper = papers["items"][0]
    assert paper["id"] == ids["paper_id"]
    assert paper["doi"] == "10.1000/example"
    assert paper["arxiv_id"] == "2407.18940"
    assert paper["relevance"]["decision"] == "denied"
    assert paper["relevance"]["reason"] == "out of scope"
    assert paper["source_record_ids"] == [ids["source_record_id"]]
    assert client.get(f"/v1/papers/{ids['paper_id']}").json()["title"] == paper["title"]

    claims = client.get(f"/v1/runs/{ids['run_id']}/claims").json()
    assert claims["items"][0]["claim_text"] == "The paper studies evidence chains."
    assert claims["items"][0]["evidence_span_ids"] == [ids["evidence_id"]]
    assert client.get(f"/v1/claims/{ids['claim_id']}").json()["support_status"] == "supported"

    span = client.get(f"/v1/evidence-spans/{ids['evidence_id']}").json()
    assert span["locator"] == {"section": "Abstract"}
    assert span["verified"] is True
    assert span["file_id"] is None
    full_text = client.get(f"/v1/evidence-spans/{ids['full_text_id']}").json()
    assert full_text["file_id"] == ids["file_id"]
    assert full_text["document_id"] == ids["document_id"]

    record = client.get(f"/v1/source-records/{ids['source_record_id']}").json()
    assert record["source"] == "arxiv"
    assert record["source_record_id"] == "2407.18940"
    assert "raw_json" not in record

    stored_file = client.get(f"/v1/files/{ids['file_id']}").json()
    assert stored_file["path"] == ""
    document = client.get(f"/v1/documents/{ids['document_id']}").json()
    assert document["text_path"] == ""

    rendered = listed.text + client.get(f"/v1/runs/{ids['run_id']}").text
    rendered += client.get(f"/v1/files/{ids['file_id']}").text
    rendered += client.get(f"/v1/source-records/{ids['source_record_id']}").text
    assert SECRET not in rendered
    assert "config_json" not in rendered
    assert "raw_json" not in rendered
    assert LOCAL_SECRET_PATH not in rendered


def test_read_api_reports_missing_records_and_bad_pages(tmp_path: Path) -> None:
    client, _ids = _client(tmp_path)

    missing = client.get("/v1/runs/missing-run")
    assert missing.status_code == 404
    assert missing.json()["error"] == {"code": "not_found", "message": "run not found"}

    invalid = client.get("/v1/runs", params={"limit": 0})
    assert invalid.status_code == 400
    assert invalid.json()["error"]["code"] == "invalid_request"

    page = client.get("/v1/runs", params={"limit": 1, "offset": 5})
    assert page.status_code == 200
    assert page.json()["items"] == []
    assert page.json()["total"] == 1


def test_read_api_allows_only_local_frontend_origins(tmp_path: Path) -> None:
    client, _ids = _client(tmp_path)

    allowed = client.get("/v1/runs", headers={"Origin": "http://127.0.0.1:5173"})
    assert allowed.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"

    blocked = client.get("/v1/runs", headers={"Origin": "https://evil.example"})
    assert blocked.headers.get("access-control-allow-origin") != "https://evil.example"


def test_serve_refuses_a_public_host() -> None:
    from typer.testing import CliRunner

    assert "127.0.0.1" in LOCAL_API_HOSTS
    result = CliRunner().invoke(cli_app, ["serve", "--host", "0.0.0.0"])

    assert result.exit_code != 0
    assert "local" in (result.stdout + (result.stderr or "")).lower()


def test_full_text_document_id_matches_the_stored_document(tmp_path: Path) -> None:
    client, ids = _client(tmp_path)

    full_text = client.get(f"/v1/evidence-spans/{ids['full_text_id']}").json()

    assert full_text["document_id"] == ids["document_id"]
    assert full_text["evidence_level"] == "full_text"
    assert isinstance(full_text["verified"], bool)
    assert pytest.approx(full_text["confidence"]) == 0.7
