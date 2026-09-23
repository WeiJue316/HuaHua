"""Research flow: source search to traceable Markdown report."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from research_agent.evidence.claims import (
    ClaimDraft,
    build_claims_from_evidence,
    validate_claim_evidence,
)
from research_agent.mcp_servers.arxiv.client import ArxivClient
from research_agent.mcp_servers.common import PaperCandidate
from research_agent.planner.planner import ResearchPlan
from research_agent.router.federation import SearchClient, search_sources
from research_agent.storage.artifacts import archive_downloaded_file
from research_agent.storage.migrations import apply_migrations, connect_database
from research_agent.storage.pdf_parser import parse_pdf
from research_agent.storage.repository import ResearchRepository, sha256_text, utc_now


@dataclass(frozen=True)
class ResearchRunResult:
    """Outcome of one research run."""

    run_id: str
    report_path: Path
    paper_count: int
    evidence_count: int
    claim_count: int
    file_count: int
    document_count: int
    source_counts: dict[str, int]
    source_errors: dict[str, str]


def _md_cell(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.replace("|", "\\|").split())


def render_report(
    *,
    question: str,
    run_id: str,
    source_records: list[tuple[PaperCandidate, str]],
    evidence: list[tuple[str, str, str, str, str, str]],
    claims: list[ClaimDraft],
    files: list[tuple[str, str, str, str]],
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
    for index, (
        title,
        quote,
        source_record_id,
        source,
        _evidence_id,
        locator,
    ) in enumerate(evidence, start=1):
        lines.append(
            f"| E{index} | {_md_cell(title)} | {_md_cell(source)} "
            f"| {_md_cell(quote)} | {_md_cell(locator)} | `{source_record_id}` |"
        )

    lines.extend(
        [
            "",
            "## Files",
            "",
            "| # | Paper | Source | SHA-256 | Archived Path |",
            "|---:|---|---|---|---|",
        ]
    )
    for index, (title, source, sha256, path) in enumerate(files, start=1):
        lines.append(
            f"| F{index} | {_md_cell(title)} | {_md_cell(source)} "
            f"| `{sha256}` | `{_md_cell(path)}` |"
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
    download_pdf: bool = False,
    artifact_root: Path | None = None,
    plan: ResearchPlan | None = None,
) -> ResearchRunResult:
    """Query multiple sources, preserve provenance, and render one report."""

    db_path = Path(db_path)
    reports_root = Path(reports_root)
    archive_root = Path(artifact_root) if artifact_root else db_path.parent
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
                "download_pdf": download_pdf,
                "plan": plan.to_dict() if plan else None,
            },
        )
        if plan is not None:
            plan_id = repository.record_plan(
                run_id=run_id,
                plan_json=plan.to_dict(),
                strategy="template",
                status="active",
            )
            repository.record_plan_step(
                plan_id=plan_id,
                step_key="route_sources",
                step_type="route_sources",
                depends_on=[],
                input_json={"question": question},
            )
            repository.record_audit_event(
                run_id=run_id,
                action="route_sources",
                target_type="plan",
                target_id=plan_id,
                decision="allowed",
                details={
                    "selected_sources": list(plan.selected_sources),
                    "fallback_sources": list(plan.fallback_sources),
                    "reason": plan.reason,
                },
            )
        connection.commit()

    federated = await search_sources(
        clients,
        query=question,
        max_results_per_source=max_results_per_source,
    )

    source_records: list[tuple[PaperCandidate, str]] = []
    evidence_rows: list[tuple[str, str, str, str, str, str]] = []
    file_rows: list[tuple[str, str, str, str]] = []
    paper_ids: set[str] = set()
    document_count = 0
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
            client = clients[source]

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
                            "Abstract",
                        )
                    )

                if (
                    download_pdf
                    and candidate.pdf_url
                    and isinstance(client, ArxivClient)
                ):
                    temp_dir = archive_root / "cache" / "downloads"
                    artifact = await client.download_pdf(
                        candidate.pdf_url,
                        temp_dir,
                        artifact_id=candidate.source_record_id,
                    )
                    final_path = archive_downloaded_file(
                        source_path=temp_dir / artifact.filename,
                        archive_dir=archive_root / project_id / "papers",
                        sha256=artifact.sha256,
                        suffix=".pdf",
                    )
                    file_id = repository.record_file(
                        paper_id=paper_id,
                        kind="pdf",
                        sha256=artifact.sha256,
                        path=final_path.as_posix(),
                        size_bytes=artifact.size_bytes,
                        content_type=artifact.content_type,
                        source_url=artifact.source_url,
                        final_url=artifact.final_url,
                        retrieved_at=artifact.retrieved_at,
                        license=artifact.license,
                    )
                    file_rows.append(
                        (
                            candidate.title,
                            candidate.source,
                            artifact.sha256,
                            final_path.as_posix(),
                        )
                    )
                    parse_result = parse_pdf(final_path)
                    document_id = str(uuid4())
                    parsed_dir = archive_root / project_id / "parsed"
                    parsed_dir.mkdir(parents=True, exist_ok=True)
                    text_path = parsed_dir / f"{document_id}.txt"
                    text_path.write_text(parse_result.text, encoding="utf-8")
                    document_id = repository.record_document(
                        document_id=document_id,
                        file_id=file_id,
                        parser=parse_result.parser,
                        parser_version=parse_result.parser_version,
                        text_path=text_path.as_posix(),
                        text_sha256=sha256_text(parse_result.text),
                        locator_scheme="page_paragraph",
                        parse_status="success",
                    )
                    document_count += 1
                    full_text_quote = parse_result.text.split("\n\n", 1)[0].strip()
                    if full_text_quote:
                        full_text_evidence_id = repository.record_evidence_span(
                            paper_id=paper_id,
                            source_record_id=stored_source_record_id,
                            document_id=document_id,
                            file_id=file_id,
                            quote=full_text_quote,
                            locator={
                                "page": 1,
                                "paragraph_index": 0,
                                "char_start": 0,
                                "char_end": len(full_text_quote),
                            },
                            evidence_level="full_text",
                            extraction_method="pdf_parser",
                            extractor_version=parse_result.parser_version,
                            confidence=0.8,
                            verified=1,
                        )
                        evidence_rows.append(
                            (
                                candidate.title,
                                full_text_quote,
                                stored_source_record_id,
                                candidate.source,
                                full_text_evidence_id,
                                "page 1",
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
            files=file_rows,
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
        file_count=len(file_rows),
        document_count=document_count,
        source_counts=federated.source_counts,
        source_errors=federated.errors,
    )


def _source_endpoint(source: str) -> str:
    if source == "arxiv":
        return "https://export.arxiv.org/api/query"
    if source == "openalex":
        return "https://api.openalex.org/works"
    if source == "crossref":
        return "https://api.crossref.org/works"
    if source == "semantic_scholar":
        return "https://api.semanticscholar.org/graph/v1"
    if source == "dblp":
        return "https://dblp.org/search/publ/api"
    return source