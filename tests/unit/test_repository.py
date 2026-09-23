from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from research_agent.evidence.claims import ClaimDraft
from research_agent.mcp_servers.common import Author, OpenAccessInfo, PaperCandidate
from research_agent.storage.migrations import apply_migrations, connect_database
from research_agent.storage.repository import ResearchRepository


def _candidate() -> PaperCandidate:
    return PaperCandidate(
        source="arxiv",
        source_record_id="2407.18940",
        source_version="v2",
        title="Traceable Retrieval for Scientific Agents",
        abstract="We study evidence chains for scientific literature agents.",
        authors=[Author(name="Alice Example")],
        year=2024,
        published_at="2024-07-26T00:00:00Z",
        updated_at="2024-08-01T00:00:00Z",
        categories=["cs.AI"],
        doi="10.1000/example",
        landing_url="https://arxiv.org/abs/2407.18940v2",
        pdf_url="https://arxiv.org/pdf/2407.18940v2",
        open_access=OpenAccessInfo(
            is_oa=True,
            status="green",
            url="https://arxiv.org/pdf/2407.18940v2",
        ),
        raw={"source_record_id": "2407.18940", "title": "Traceable Retrieval"},
    )


def test_repository_persists_paper_provenance_and_evidence(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        project_id = repo.create_project("project")
        question_id = repo.create_research_question(project_id, "question")
        run_id = repo.create_run(project_id, question_id)
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
        )
        paper_id, created = repo.upsert_paper(_candidate())
        repo.link_paper_source_record(
            paper_id=paper_id,
            source_record_id=source_record_id,
            merge_reason="arxiv_id",
            is_primary_metadata=True,
        )
        evidence_id = repo.record_evidence_span(
            paper_id=paper_id,
            source_record_id=source_record_id,
            quote=_candidate().abstract or "",
            locator={"section": "Abstract"},
            evidence_level="abstract",
            extraction_method="rule",
            confidence=0.9,
            verified=1,
        )
        report_id = repo.record_report(
            run_id=run_id,
            path="reports/project/run/report.md",
            content="# Report\n",
        )

        assert created is True
        assert conn.execute("SELECT COUNT(*) FROM source_record").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM paper").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM paper_source_record").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM evidence_span").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM report").fetchone()[0] == 1
        assert evidence_id
        assert report_id

        evidence = conn.execute(
            "SELECT paper_id, source_record_id, evidence_level FROM evidence_span WHERE id = ?",
            (evidence_id,),
        ).fetchone()
        assert evidence is not None
        assert evidence["paper_id"] == paper_id
        assert evidence["source_record_id"] == source_record_id
        assert evidence["evidence_level"] == "abstract"


def test_repository_deduplicates_paper_by_canonical_key(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        first_id, first_created = repo.upsert_paper(_candidate())
        second_id, second_created = repo.upsert_paper(_candidate())

        assert first_created is True
        assert second_created is False
        assert first_id == second_id
        assert conn.execute("SELECT COUNT(*) FROM paper").fetchone()[0] == 1


def test_repository_rejects_full_text_evidence_without_file(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        project_id = repo.create_project("project")
        question_id = repo.create_research_question(project_id, "question")
        run_id = repo.create_run(project_id, question_id)
        call_id = repo.record_source_call(
            run_id=run_id,
            source="arxiv",
            tool_name="arxiv_search_papers",
            request_json={},
            status="success",
            started_at="2026-01-01T00:00:00Z",
        )
        source_record_id = repo.record_source_record(
            source_call_id=call_id,
            candidate=_candidate(),
            api_endpoint="https://export.arxiv.org/api/query",
        )
        paper_id, _ = repo.upsert_paper(_candidate())

        with pytest.raises(sqlite3.IntegrityError):
            repo.record_evidence_span(
                paper_id=paper_id,
                source_record_id=source_record_id,
                quote="full text quote",
                locator={"page": 1},
                evidence_level="full_text",
                extraction_method="pdf_parser",
                confidence=0.9,
                verified=1,
            )

def test_repository_reuses_project_by_name(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        first_id = repo.get_or_create_project("project")
        second_id = repo.get_or_create_project("project")

        assert first_id == second_id
        assert conn.execute("SELECT COUNT(*) FROM project").fetchone()[0] == 1


def test_repository_enriches_existing_paper_with_doi(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        without_doi = _candidate().model_copy(update={"doi": None})
        first_id, first_created = repo.upsert_paper(without_doi)
        second_id, second_created = repo.upsert_paper(_candidate())

        assert first_created is True
        assert second_created is False
        assert first_id == second_id
        assert conn.execute("SELECT COUNT(*) FROM paper").fetchone()[0] == 1
        assert conn.execute(
            "SELECT COUNT(*) FROM paper_identifier WHERE type = 'doi'"
        ).fetchone()[0] == 1

def test_repository_records_claim_with_evidence(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        project_id = repo.create_project("project")
        question_id = repo.create_research_question(project_id, "question")
        run_id = repo.create_run(project_id, question_id)
        call_id = repo.record_source_call(
            run_id=run_id,
            source="arxiv",
            tool_name="arxiv_search_papers",
            request_json={},
            status="success",
            started_at="2026-01-01T00:00:00Z",
        )
        source_record_id = repo.record_source_record(
            source_call_id=call_id,
            candidate=_candidate(),
            api_endpoint="https://export.arxiv.org/api/query",
        )
        paper_id, _ = repo.upsert_paper(_candidate())
        evidence_id = repo.record_evidence_span(
            paper_id=paper_id,
            source_record_id=source_record_id,
            quote="We study evidence chains.",
            locator={"section": "Abstract"},
            evidence_level="abstract",
            extraction_method="rule",
            confidence=0.9,
            verified=1,
        )
        report_id = repo.record_report(
            run_id=run_id,
            path="reports/project/run/report.md",
            content="# Report\n",
        )

        claim_id = repo.record_claim(
            report_id=report_id,
            claim=ClaimDraft(
                claim_text="Paper reports that We study evidence chains.",
                claim_type="fact",
                support_status="supported",
                confidence=0.8,
                evidence_span_ids=[evidence_id],
            ),
        )

        assert claim_id
        assert conn.execute("SELECT COUNT(*) FROM claim").fetchone()[0] == 1
        claim_evidence = conn.execute(
            "SELECT evidence_span_id, relation_type FROM claim_evidence"
        ).fetchone()
        assert claim_evidence is not None
        assert claim_evidence["evidence_span_id"] == evidence_id
        assert claim_evidence["relation_type"] == "supports"

def test_repository_deduplicates_five_sources_by_doi(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)

    candidates = [
        _candidate(),
        _candidate().model_copy(
            update={"source": "openalex", "source_record_id": "W123456789"}
        ),
        _candidate().model_copy(
            update={"source": "crossref", "source_record_id": "10.1000/example"}
        ),
        _candidate().model_copy(
            update={"source": "semantic_scholar", "source_record_id": "S123"}
        ),
        _candidate().model_copy(
            update={"source": "dblp", "source_record_id": "conf/example/paper"}
        ),
    ]

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        project_id = repo.create_project("project")
        question_id = repo.create_research_question(project_id, "question")
        run_id = repo.create_run(project_id, question_id)
        paper_ids: set[str] = set()

        for candidate in candidates:
            call_id = repo.record_source_call(
                run_id=run_id,
                source=candidate.source,
                tool_name=f"{candidate.source}_search_papers",
                request_json={},
                status="success",
                started_at="2026-01-01T00:00:00Z",
            )
            source_record_id = repo.record_source_record(
                source_call_id=call_id,
                candidate=candidate,
                api_endpoint=f"https://example.org/{candidate.source}",
            )
            paper_id, created = repo.upsert_paper(candidate)
            if created:
                paper_ids.add(paper_id)
            repo.link_paper_source_record(
                paper_id=paper_id,
                source_record_id=source_record_id,
                merge_reason="doi",
                is_primary_metadata=candidate.source == "arxiv",
            )

        assert len(paper_ids) == 1
        assert conn.execute("SELECT COUNT(*) FROM paper").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM source_record").fetchone()[0] == 5
        assert (
            conn.execute("SELECT COUNT(*) FROM paper_source_record").fetchone()[0]
            == 5
        )
