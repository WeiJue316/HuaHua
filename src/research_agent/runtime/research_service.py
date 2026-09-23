"""M1 research flow: arXiv search to traceable Markdown report."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from research_agent.mcp_servers.arxiv.client import ArxivClient, ArxivClientError
from research_agent.mcp_servers.common import PaperCandidate
from research_agent.storage.migrations import apply_migrations, connect_database
from research_agent.storage.repository import ResearchRepository, utc_now


@dataclass(frozen=True)
class ResearchRunResult:
    """Outcome of one M1 research run."""

    run_id: str
    report_path: Path
    paper_count: int
    evidence_count: int


def _md_cell(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.replace("|", "\\|").split())


def render_report(
    *,
    question: str,
    run_id: str,
    source_records: list[tuple[PaperCandidate, str]],
    evidence: list[tuple[str, str, str]],
) -> str:
    """Render a minimal evidence-first Markdown report."""

    lines = [
        "# Research Report",
        "",
        f"**Question:** {question}",
        "",
        f"**Run ID:** `{run_id}`",
        "",
        "## Papers",
        "",
        "| # | Title | arXiv ID | DOI | Source Record |",
        "|---:|---|---|---|---|",
    ]
    for index, (paper, source_record_id) in enumerate(source_records, start=1):
        lines.append(
            f"| {index} | {_md_cell(paper.title)} | {_md_cell(paper.source_record_id)} "
            f"| {_md_cell(paper.doi)} | `{source_record_id}` |"
        )

    lines.extend(
        [
            "",
            "## Evidence",
            "",
            "| # | Paper | Quote | Locator | source_record_id |",
            "|---:|---|---|---|---|",
        ]
    )
    for index, (title, quote, source_record_id) in enumerate(evidence, start=1):
        lines.append(
            f"| {index} | {_md_cell(title)} | {_md_cell(quote)} | Abstract "
            f"| `{source_record_id}` |"
        )

    lines.extend(
        [
            "",
            "## Provenance",
            "",
            "All evidence rows are linked to an immutable Source Record. "
            "The report does not claim support beyond the recorded abstract evidence.",
            "",
        ]
    )
    return "\n".join(lines)


async def run_arxiv_research(
    *,
    question: str,
    db_path: Path,
    reports_root: Path,
    client: ArxivClient,
    max_results: int = 10,
) -> ResearchRunResult:
    """Run the M1 arXiv vertical slice and persist a traceable report."""

    db_path = Path(db_path)
    reports_root = Path(reports_root)
    apply_migrations(db_path)

    started_at = utc_now()
    with connect_database(db_path) as connection:
        repository = ResearchRepository(connection)
        project_id = repository.get_or_create_project("Default research project")
        question_id = repository.create_research_question(project_id, question)
        run_id = repository.create_run(
            project_id,
            question_id,
            config={"max_results": max_results, "source": "arxiv"},
        )
        connection.commit()

    try:
        search_result = await client.search(question, max_results=max_results)
    except ArxivClientError as exc:
        with connect_database(db_path) as connection:
            repository = ResearchRepository(connection)
            repository.record_source_call(
                run_id=run_id,
                source="arxiv",
                tool_name="arxiv_search_papers",
                request_json={"query": question, "max_results": max_results},
                status="failed",
                started_at=started_at,
                finished_at=utc_now(),
                error_code="upstream_unavailable",
                error_details={"message": str(exc)},
            )
            connection.commit()
        raise

    source_records: list[tuple[PaperCandidate, str]] = []
    evidence_rows: list[tuple[str, str, str]] = []
    with connect_database(db_path) as connection:
        repository = ResearchRepository(connection)
        source_call_id = repository.record_source_call(
            run_id=run_id,
            source="arxiv",
            tool_name="arxiv_search_papers",
            request_json={"query": question, "max_results": max_results},
            status="success",
            started_at=started_at,
            finished_at=utc_now(),
            response_hash=search_result.response_hash,
        )

        for candidate in search_result.papers:
            stored_source_record_id = repository.record_source_record(
                source_call_id=source_call_id,
                candidate=candidate,
                api_endpoint="https://export.arxiv.org/api/query",
                response_hash=search_result.response_hash,
                query_snapshot={"query": question, "max_results": max_results},
            )
            paper_id, _ = repository.upsert_paper(candidate)
            repository.link_paper_source_record(
                paper_id=paper_id,
                source_record_id=stored_source_record_id,
                merge_reason="doi" if candidate.doi else "arxiv_id",
                is_primary_metadata=True,
            )
            source_records.append((candidate, stored_source_record_id))
            if candidate.abstract:
                repository.record_evidence_span(
                    paper_id=paper_id,
                    source_record_id=stored_source_record_id,
                    quote=candidate.abstract,
                    locator={"section": "Abstract"},
                    evidence_level="abstract",
                    extraction_method="rule",
                    confidence=0.8,
                    verified=1,
                )
                evidence_rows.append(
                    (candidate.title, candidate.abstract, stored_source_record_id)
                )

        report_text = render_report(
            question=question,
            run_id=run_id,
            source_records=source_records,
            evidence=evidence_rows,
        )
        report_path = reports_root / run_id / "report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_text, encoding="utf-8")
        repository.record_report(
            run_id=run_id,
            path=report_path.as_posix(),
            content=report_text,
        )
        connection.commit()

    return ResearchRunResult(
        run_id=run_id,
        report_path=report_path,
        paper_count=len(source_records),
        evidence_count=len(evidence_rows),
    )