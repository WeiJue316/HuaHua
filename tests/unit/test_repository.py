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


def test_new_artifact_paths_are_stored_relative_to_the_project(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("research_agent.paths.project_root", lambda: tmp_path)
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)
    report = tmp_path / "reports" / "run" / "report.md"
    pdf = tmp_path / "data" / "papers" / "a.pdf"
    text = tmp_path / "data" / "parsed" / "a.txt"

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        project_id = repo.create_project("project")
        question_id = repo.create_research_question(project_id, "question")
        run_id = repo.create_run(project_id, question_id)
        paper_id, _ = repo.upsert_paper(_candidate())
        repo.record_report(run_id=run_id, path=report.as_posix(), content="# Report\n")
        file_id = repo.record_file(
            paper_id=paper_id,
            kind="pdf",
            sha256="a" * 64,
            path=pdf.as_posix(),
            size_bytes=1,
            content_type="application/pdf",
            source_url="https://arxiv.org/pdf/2407.18940",
            retrieved_at="2026-01-01T00:00:00Z",
        )
        repo.record_file(
            paper_id=paper_id,
            kind="pdf",
            sha256="b" * 64,
            path="",
            size_bytes=0,
            content_type="application/pdf",
            source_url="https://arxiv.org/pdf/too-big",
            retrieved_at="2026-01-01T00:00:00Z",
            status="quarantined",
        )
        repo.record_document(
            file_id=file_id,
            parser="pypdf",
            parser_version="1",
            text_path=text.as_posix(),
            text_sha256="c" * 64,
            locator_scheme="page_paragraph",
            parse_status="success",
        )
        report_path = conn.execute("SELECT path FROM report").fetchone()[0]
        file_paths = [
            row[0] for row in conn.execute("SELECT path FROM file ORDER BY path")
        ]
        text_path = conn.execute("SELECT text_path FROM document").fetchone()[0]

    assert report_path == "reports/run/report.md"
    assert file_paths == ["", "data/papers/a.pdf"]
    assert text_path == "data/parsed/a.txt"


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


def test_repository_fills_blank_metadata_without_overwriting(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)
    sparse = _candidate().model_copy(
        update={"abstract": None, "year": None, "venue": None}
    )
    filled = _candidate().model_copy(
        update={
            "source": "openalex",
            "source_record_id": "W999",
            "abstract": "Backfilled abstract about evidence chains.",
            "year": 2024,
            "venue": "Backfilled Venue",
            "landing_url": "https://openalex.org/W999",
        }
    )
    conflicting = filled.model_copy(
        update={
            "source": "crossref",
            "source_record_id": "10.1000/example",
            "abstract": "A later abstract that must stay out.",
            "year": 1999,
            "venue": "Other Venue",
            "landing_url": "https://doi.org/10.1000/example",
        }
    )

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        paper_id, created = repo.upsert_paper(sparse)
        same_id, filled_created = repo.upsert_paper(filled)
        row = conn.execute(
            "SELECT abstract, year, venue FROM paper WHERE id = ?",
            (paper_id,),
        ).fetchone()
        indexed = conn.execute(
            "SELECT COUNT(*) FROM paper_fts WHERE paper_fts MATCH 'backfilled'"
        ).fetchone()[0]
        repo.upsert_paper(conflicting)
        kept = conn.execute(
            "SELECT abstract, year, venue FROM paper WHERE id = ?",
            (paper_id,),
        ).fetchone()

    assert created is True
    assert filled_created is False
    assert same_id == paper_id
    assert row["abstract"] == "Backfilled abstract about evidence chains."
    assert row["year"] == 2024
    assert row["venue"] == "Backfilled Venue"
    assert indexed == 1
    assert kept["abstract"] == "Backfilled abstract about evidence chains."
    assert kept["year"] == 2024
    assert kept["venue"] == "Backfilled Venue"


def test_repository_merges_openalex_record_by_arxiv_id_without_doi(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)
    arxiv = _candidate().model_copy(
        update={
            "doi": None,
            "source_record_id": "2312.10997",
            "landing_url": "https://arxiv.org/abs/2312.10997",
        }
    )
    openalex = _candidate().model_copy(
        update={
            "source": "openalex",
            "source_record_id": "W1",
            "doi": None,
            "landing_url": "https://openalex.org/W1",
            "raw": {"arxiv_id": "2312.10997"},
        }
    )

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        first_id, _ = repo.upsert_paper(arxiv)
        second_id, created = repo.upsert_paper(openalex)

        assert created is False
        assert second_id == first_id
        assert conn.execute("SELECT COUNT(*) FROM paper").fetchone()[0] == 1


def test_repository_merges_arxiv_record_with_arxiv_doi(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)
    arxiv = _candidate()
    arxiv = arxiv.model_copy(
        update={"doi": None, "source_record_id": "2407.18940"}
    )
    openalex = _candidate().model_copy(
        update={
            "source": "openalex",
            "source_record_id": "W999",
            "doi": "10.48550/arXiv.2407.18940",
            "landing_url": "https://openalex.org/W999",
        }
    )

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        first_id, _ = repo.upsert_paper(arxiv)
        second_id, created = repo.upsert_paper(openalex)

        assert created is False
        assert second_id == first_id
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

def test_repository_records_plan_and_audit_event(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        project_id = repo.create_project("project")
        question_id = repo.create_research_question(project_id, "question")
        run_id = repo.create_run(project_id, question_id)
        plan_id = repo.record_plan(
            run_id=run_id,
            plan_json={"selected_sources": ["openalex", "semantic_scholar"]},
        )
        step_id = repo.record_plan_step(
            plan_id=plan_id,
            step_key="route_sources",
            step_type="route_sources",
            depends_on=[],
        )
        audit_id = repo.record_audit_event(
            run_id=run_id,
            action="route_sources",
            target_type="plan",
            target_id=plan_id,
            details={"reason": "citations"},
        )

        assert plan_id
        assert step_id
        assert audit_id
        assert conn.execute("SELECT COUNT(*) FROM plan").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM plan_step").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM audit_event").fetchone()[0] == 1


def test_repository_records_model_call(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        project_id = repo.create_project("project")
        question_id = repo.create_research_question(project_id, "question")
        run_id = repo.create_run(project_id, question_id)

        call_id = repo.record_model_call(
            run_id=run_id,
            provider="deepseek",
            model="deepseek-flash",
            purpose="semantic_relevance",
            prompt_hash="abc123",
            prompt_version="relevance-v1",
            response_hash="def456",
            input_tokens=506,
            output_tokens=245,
            latency_ms=1200,
        )

        row = conn.execute(
            "SELECT run_id, provider, model, purpose, prompt_version,"
            " input_tokens, output_tokens, latency_ms, status"
            " FROM model_call WHERE id = ?",
            (call_id,),
        ).fetchone()

    assert row is not None
    assert row["run_id"] == run_id
    assert row["provider"] == "deepseek"
    assert row["model"] == "deepseek-flash"
    assert row["purpose"] == "semantic_relevance"
    assert row["prompt_version"] == "relevance-v1"
    assert row["input_tokens"] == 506
    assert row["output_tokens"] == 245
    assert row["latency_ms"] == 1200
    assert row["status"] == "success"


def test_repository_records_a_denied_relevance_verdict(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)

    with connect_database(db_path) as conn:
        repo = ResearchRepository(conn)
        project_id = repo.create_project("project")
        question_id = repo.create_research_question(project_id, "question")
        run_id = repo.create_run(project_id, question_id)

        repo.record_audit_event(
            run_id=run_id,
            action="semantic_relevance",
            target_type="paper",
            target_id="doi:10.1/wrong-field",
            decision="denied",
            details={
                "domain_scope": "out_of_scope",
                "answer_role": "none",
                "reason": "management research, not agent planning",
            },
        )

        row = conn.execute(
            "SELECT actor, action, decision, details_json FROM audit_event"
            " WHERE run_id = ? AND action = 'semantic_relevance'",
            (run_id,),
        ).fetchone()

    assert row is not None
    assert row["actor"] == "system"
    assert row["decision"] == "denied"
    assert "out_of_scope" in row["details_json"]
