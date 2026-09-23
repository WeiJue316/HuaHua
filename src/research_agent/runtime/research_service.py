"""Research flow: source search to traceable Markdown report."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from research_agent.evidence.claims import (
    ClaimDraft,
    build_claims_from_evidence,
    validate_claim_evidence,
)
from research_agent.mcp_servers.arxiv.client import ArxivClient
from research_agent.mcp_servers.common import PaperCandidate
from research_agent.router.federation import SearchClient, search_sources
from research_agent.storage.migrations import apply_migrations, connect_database
from research_agent.storage.repository import ResearchRepository, utc_now


@dataclass(frozen=True)
class ResearchRunResult:
    """Outcome of one research run."""

    run_id: str
    report_path: Path
    paper_count: int
    evidence_count: int
    claim_count: int
    source_counts: dict[str, int]


def _md_cell(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.replace("|", "\\|").split())


def render_report(
    *,
    question: str,
    run_id: str,
    source_records: list[tuple[PaperCandidate, str]],
    evidence: list[tuple[str, str, str, str, str]],
    claims: list[ClaimDraft],
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
        "| # | Title | Source | Source ID | DOI | Source Record |",
        "|---:|---|---|---|---|---|",
    ]
    for index, (paper, source_record_id) in enumerate(source_records, start=1):
        lines.append(
            f"| {index} | {_md_cell(paper.title)} | {_md_cell(paper.source)} "
            f"| {_md_cell(paper.source_record_id)} | {_md_cell(paper.doi)} "
            f"| `{source_record_id}` |"
        )

    evidence_index = {
        evidence_id: index
        for index, (*_prefix, evidence_id) in enumerate(evidence, start=1)
    }
    lines.extend(
        [
            "",
            "## Evidence",
            "",
            "| # | Paper | Source | Quote | Locator | source_record_id |",
            "|---:|---|---|---|---|---|",
        ]
    )
    for index, (title, quote, source_record_id, source, _evidence_id) in enumerate(
        evidence, start=1
    ):
        lines.append(
            f"| E{index} | {_md_cell(title)} | {_md_cell(source)} "
            f"| {_md_cell(quote)} | Abstract | `{source_record_id}` |"
        )

    lines.extend(
        [
            "",
            "## Claims",
            "",
            "| # | Claim | Support | Evidence |",
            "|---:|---|---|---|",
        ]
    )
    for index, claim in enumerate(claims, start=1):
        references = ", ".join(
            f"E{evidence_index[evidence_id]}"
            for evidence_id in claim.evidence_span_ids
            if evidence_id in evidence_index
        )
        lines.append(
            f"| C{index} | {_md_cell(claim.claim_text)} "
            f"| {_md_cell(claim.support_status)} | {references} |"
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
    """Run the arXiv vertical slice through the federation service."""

    clients: Mapping[str, SearchClient] = {"arxiv": client}
    return await run_federated_research(
        question=question,
        db_path=db_path,
        reports_root=reports_root,
        clients=clients,
        max_results_per_source=max_results,
    )


async def run_federated_research(
    *,
    question: str,
    db_path: Path,
    reports_root: Path,
    clients: Mapping[str, SearchClient],
    max_results_per_source: int = 10,
) -> ResearchRunResult:
    """Query multiple sources, preserve provenance, and render one report."""

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
            config={
                "max_results_per_source": max_results_per_source,
                "sources": sorted(clients),
            },
        )
        connection.commit()

    federated = await search_sources(
        clients,
        query=question,
        max_results_per_source=max_results_per_source,
    )

    source_records: list[tuple[PaperCandidate, str]] = []
    evidence_rows: list[tuple[str, str, str, str, str]] = []
    paper_ids: set[str] = set()
    with connect_database(db_path) as connection:
        repository = ResearchRepository(connection)
        for source in clients:
            source_failed = source in federated.errors
            source_call_id = repository.record_source_call(
                run_id=run_id,
                source=source,
                tool_name=f"{source}_search_papers",
                request_json={
                    "query": question,
                    "max_results": max_results_per_source,
                },
                status="failed" if source_failed else "success",
                started_at=started_at,
                finished_at=utc_now(),
                error_code="upstream_unavailable" if source_failed else None,
                error_details=(
                    {"message": federated.errors[source]} if source_failed else None
                ),
            )
            if source_failed:
                continue

            for candidate in (
                paper for paper in federated.papers if paper.source == source
            ):
                paper_id, _ = repository.upsert_paper(candidate)
                paper_ids.add(paper_id)
                stored_source_record_id = repository.record_source_record(
                    source_call_id=source_call_id,
                    candidate=candidate,
                    api_endpoint=_source_endpoint(source),
                    query_snapshot={
                        "query": question,
                        "max_results": max_results_per_source,
                    },
                )
                repository.link_paper_source_record(
                    paper_id=paper_id,
                    source_record_id=stored_source_record_id,
                    merge_reason="doi" if candidate.doi else "source_id",
                    is_primary_metadata=source == "arxiv",
                )
                source_records.append((candidate, stored_source_record_id))
                if candidate.abstract:
                    evidence_id = repository.record_evidence_span(
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
                        (
                            candidate.title,
                            candidate.abstract,
                            stored_source_record_id,
                            candidate.source,
                            evidence_id,
                        )
                    )

        claims = build_claims_from_evidence(evidence_rows)
        available_evidence_ids = {row[4] for row in evidence_rows}
        for claim in claims:
            validate_claim_evidence(claim, available_evidence_ids)

        report_text = render_report(
            question=question,
            run_id=run_id,
            source_records=source_records,
            evidence=evidence_rows,
            claims=claims,
        )
        report_path = reports_root / run_id / "report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_text, encoding="utf-8")
        report_id = repository.record_report(
            run_id=run_id,
            path=report_path.as_posix(),
            content=report_text,
        )
        for claim in claims:
            repository.record_claim(report_id=report_id, claim=claim)
        connection.commit()

    return ResearchRunResult(
        run_id=run_id,
        report_path=report_path,
        paper_count=len(paper_ids),
        evidence_count=len(evidence_rows),
        claim_count=len(claims),
        source_counts=federated.source_counts,
    )


def _source_endpoint(source: str) -> str:
    if source == "arxiv":
        return "https://export.arxiv.org/api/query"
    if source == "openalex":
        return "https://api.openalex.org/works"
    return source