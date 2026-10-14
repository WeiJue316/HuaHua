from __future__ import annotations

import csv
import json
from pathlib import Path

from research_agent.evidence.claims import ClaimDraft
from research_agent.evidence.exports import (
    EVIDENCE_TABLE_COLUMNS,
    BibliographyEntry,
    EvidenceExportRow,
    render_bibtex,
    render_evidence_csv,
    render_evidence_json,
)
from research_agent.mcp_servers.common import Author, OpenAccessInfo, PaperCandidate
from research_agent.storage.migrations import apply_migrations, connect_database
from research_agent.storage.repository import ResearchRepository, sha256_text


def _row(**overrides: object) -> EvidenceExportRow:
    values: dict[str, object] = {
        "claim_id": "c1",
        "claim_text": "A claim, with comma",
        "support_status": "supported",
        "paper_id": "p1",
        "paper_title": 'Title "quoted"',
        "doi": "",
        "arxiv_id": "2407.18940",
        "file_sha256": "",
        "evidence_id": "e1",
        "quote": 'He said "hi"',
        "locator": '{"section": "Abstract"}',
        "evidence_level": "abstract",
        "extraction_method": "rule",
        "confidence": 0.9,
        "source": "arxiv",
        "retrieved_at": "2026-01-01T00:00:00Z",
    }
    values.update(overrides)
    return EvidenceExportRow(**values)  # type: ignore[arg-type]


def test_evidence_table_keeps_required_columns_and_does_not_invent_a_doi() -> None:
    row = _row()

    csv_text = render_evidence_csv([row])
    payload = json.loads(render_evidence_json([row]))

    assert csv_text.splitlines()[0] == ",".join(EVIDENCE_TABLE_COLUMNS)
    assert "10." not in csv_text
    assert payload[0]["doi"] == ""
    assert payload[0]["arxiv_id"] == "2407.18940"
    assert payload[0]["confidence"] == 0.9
    assert set(payload[0]) == set(EVIDENCE_TABLE_COLUMNS)
    parsed = list(csv.DictReader(csv_text.splitlines()))
    assert parsed[0]["quote"] == 'He said "hi"'
    assert parsed[0]["doi"] == ""


def test_bibtex_uses_placeholders_and_omits_a_missing_doi() -> None:
    text = render_bibtex(
        [
            BibliographyEntry(
                paper_id="paper-1",
                title="A & B",
                authors=(),
                year="",
                venue="",
                doi="",
                arxiv_id="",
            )
        ]
    )

    assert "@article{paper_paper_1," in text
    assert "title = {A \\& B}" in text
    assert "author = {unknown}" in text
    assert "year = {unknown}" in text
    assert "doi" not in text


def test_bibtex_keeps_a_real_doi_and_joins_authors() -> None:
    text = render_bibtex(
        [
            BibliographyEntry(
                paper_id="paper-1",
                title="Traceable Retrieval",
                authors=("Alice Example", "Bob Example"),
                year="2024",
                venue="JMLR",
                doi="10.1000/example",
                arxiv_id="2407.18940",
            )
        ]
    )

    assert "@article{doi_10_1000_example," in text
    assert "author = {Alice Example and Bob Example}" in text
    assert "doi = {10.1000/example}" in text
    assert "eprint = {2407.18940}" in text
    assert "journal = {JMLR}" in text


def _candidate() -> PaperCandidate:
    return PaperCandidate(
        source="arxiv",
        source_record_id="2407.18940",
        source_version="v2",
        title="Traceable Retrieval for Scientific Agents",
        abstract="We study evidence chains.",
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
    )


def test_repository_exports_the_evidence_table_and_bibtex(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr("research_agent.paths.project_root", lambda: tmp_path)
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)
    export_dir = tmp_path / "reports" / "run"

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
        paper_id, _ = repo.upsert_paper(_candidate())
        repo.link_paper_source_record(
            paper_id=paper_id,
            source_record_id=source_record_id,
            merge_reason="doi",
            is_primary_metadata=True,
        )
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
            path="reports/run/report.md",
            content="# Report\n",
        )
        repo.record_claim(
            report_id=report_id,
            claim=ClaimDraft(
                claim_text="The paper reports an evidence chain.",
                claim_type="fact",
                support_status="supported",
                confidence=0.8,
                evidence_span_ids=[evidence_id],
            ),
        )
        repo.record_claim(
            report_id=report_id,
            claim=ClaimDraft(
                claim_text="This conclusion is unverified.",
                claim_type="fact",
                support_status="unsupported",
                confidence=0.2,
                evidence_span_ids=[],
            ),
        )

        rows = repo.evidence_export_rows(report_id)
        bibliography = repo.bibliography_entries(report_id)
        csv_text = render_evidence_csv(rows)
        bibtex = render_bibtex(bibliography)
        export_dir.mkdir(parents=True)
        csv_path = export_dir / "evidence.csv"
        csv_path.write_text(csv_text, encoding="utf-8", newline="\n")
        repo.record_export(
            report_id=report_id,
            format="csv",
            path=csv_path.as_posix(),
            content=csv_text,
        )
        stored = conn.execute(
            "SELECT format, path, sha256 FROM export"
        ).fetchone()

    assert {row.support_status for row in rows} == {"supported", "unsupported"}
    supported = next(row for row in rows if row.support_status == "supported")
    unsupported = next(row for row in rows if row.support_status == "unsupported")
    assert supported.doi == "10.1000/example"
    assert supported.arxiv_id == "2407.18940"
    assert supported.quote == "We study evidence chains."
    assert supported.source == "arxiv"
    assert unsupported.evidence_id == ""
    assert unsupported.doi == ""
    assert "The paper reports an evidence chain." in csv_text
    assert "This conclusion is unverified." in csv_text
    assert "doi = {10.1000/example}" in bibtex
    assert bibliography[0].authors == ("Alice Example",)
    assert stored is not None
    assert stored["format"] == "csv"
    assert stored["path"] == "reports/run/evidence.csv"
    assert stored["sha256"] == sha256_text(csv_text)
