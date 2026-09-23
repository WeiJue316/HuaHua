"""Research flow: source search to traceable Markdown report."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

from research_agent.evidence.claims import (
    ClaimDraft,
    build_claims_from_evidence,
    validate_claim_evidence,
)
from research_agent.executor.executor import Executor, StepSpec
from research_agent.mcp_servers.arxiv.client import ArxivClient
from research_agent.mcp_servers.common import PaperCandidate
from research_agent.planner.planner import ResearchPlan
from research_agent.policy.relevance import RelevanceJudge, RelevanceVerdict
from research_agent.router.federation import (
    FederatedSearchResult,
    SearchClient,
    search_sources,
)
from research_agent.runtime.enrichment import AbstractResolver
from research_agent.storage.artifacts import archive_downloaded_file
from research_agent.storage.migrations import apply_migrations, connect_database
from research_agent.storage.pdf_parser import parse_pdf
from research_agent.storage.repository import (
    ResearchRepository,
    canonical_key,
    sha256_text,
    utc_now,
)


class ResearchExecutionError(RuntimeError):
    """Raised when an Executor step fails."""


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
    variant_errors: dict[str, str]
    relevance_judged: int = 0
    relevance_dropped: int = 0
    relevance_failures: int = 0
    relevance_skipped: bool = False
    retrieved_paper_keys: tuple[str, ...] = ()
    dropped_paper_keys: tuple[str, ...] = ()


@dataclass
class _RunContext:
    """Mutable state passed between Executor steps."""

    question: str
    clients: Mapping[str, SearchClient]
    plan: ResearchPlan
    max_results_per_source: int
    download_pdf: bool
    archive_root: Path
    project_id: str
    run_id: str
    selected_sources: list[str] = field(default_factory=list)
    federated: FederatedSearchResult | None = None
    source_records: list[tuple[PaperCandidate, str]] = field(default_factory=list)
    evidence_rows: list[tuple[str, str, str, str, str, str]] = field(
        default_factory=list
    )
    file_rows: list[tuple[str, str, str, str]] = field(default_factory=list)
    paper_ids: set[str] = field(default_factory=set)
    document_count: int = 0
    claims: list[ClaimDraft] = field(default_factory=list)
    dropped_source_record_ids: set[str] = field(default_factory=set)
    retrieved_keys: set[str] = field(default_factory=set)
    dropped_keys: set[str] = field(default_factory=set)
    verdicts: list[RelevanceVerdict] = field(default_factory=list)
    relevance_failures: int = 0
    relevance_skipped: bool = False
    retrieved_paper_keys: tuple[str, ...] = ()
    dropped_paper_keys: tuple[str, ...] = ()
    report_path: Path | None = None
    report_id: str | None = None


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
        for index, (*_prefix, evidence_id, _locator) in enumerate(evidence, start=1)
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
    """Run the arXiv vertical slice through the federated runtime."""

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
    abstract_resolver: AbstractResolver | None = None,
    relevance_judge: RelevanceJudge | None = None,
    subquestions: Sequence[str] = (),
) -> ResearchRunResult:
    """Run a source search and report pipeline through the Executor."""

    db_path = Path(db_path)
    reports_root = Path(reports_root)
    archive_root = Path(artifact_root) if artifact_root else db_path.parent
    apply_migrations(db_path)
    if plan is None:
        from research_agent.planner.planner import plan_research

        plan = plan_research(
            question,
            available_sources=tuple(clients),
            max_results_per_source=max_results_per_source,
            max_concurrency=min(5, len(clients)),
            max_sources=len(clients),
        )

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
                "plan": plan.to_dict(),
            },
        )
        plan_id = repository.record_plan(
            run_id=run_id,
            plan_json=plan.to_dict(),
            strategy="template",
            status="active",
        )
        connection.commit()

        context = _RunContext(
            question=question,
            clients=clients,
            plan=plan,
            max_results_per_source=max_results_per_source,
            download_pdf=download_pdf,
            archive_root=archive_root,
            project_id=project_id,
            run_id=run_id,
        )

        async def route_sources_step() -> dict[str, object]:
            selected = [source for source in plan.selected_sources if source in clients]
            if not selected:
                raise ValueError("Planner selected no available source")
            context.selected_sources = selected
            repository.record_audit_event(
                run_id=run_id,
                action="route_sources",
                target_type="plan",
                target_id=plan_id,
                decision="allowed",
                details={
                    "selected_sources": selected,
                    "fallback_sources": list(plan.fallback_sources),
                    "reason": plan.reason,
                },
            )
            return {"selected_sources": selected}

        async def search_sources_step() -> dict[str, object]:
            selected_clients = {
                source: clients[source] for source in context.selected_sources
            }
            context.federated = await search_sources(
                selected_clients,
                query=question,
                query_variants=plan.query_variants,
                max_results_per_source=max_results_per_source,
                max_concurrency=plan.max_concurrency,
            )
            return {
                "source_counts": context.federated.source_counts,
                "source_errors": context.federated.errors,
            }

        async def persist_results_step() -> dict[str, object]:
            if context.federated is None:
                raise RuntimeError("search_sources must run before persist_results")
            selected_clients = {
                source: clients[source] for source in context.selected_sources
            }
            for source in context.selected_sources:
                source_failed = source in context.federated.errors
                source_call_id = repository.record_source_call(
                    run_id=run_id,
                    source=source,
                    tool_name=f"{source}_search_papers",
                    request_json={
                        "query": question,
                        "max_results": max_results_per_source,
                    },
                    status="failed" if source_failed else "success",
                    started_at=utc_now(),
                    finished_at=utc_now(),
                    error_code="upstream_unavailable" if source_failed else None,
                    error_details=(
                        {"message": context.federated.errors[source]}
                        if source_failed
                        else None
                    ),
                )
                if source_failed:
                    continue
                client = selected_clients[source]
                for candidate in (
                    paper
                    for paper in context.federated.papers
                    if paper.source == source
                ):
                    paper_id, _ = repository.upsert_paper(candidate)
                    context.paper_ids.add(paper_id)
                    context.retrieved_keys.add(canonical_key(candidate))
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
                    context.source_records.append(
                        (candidate, stored_source_record_id)
                    )
                    abstract = candidate.abstract
                    if not abstract and abstract_resolver is not None:
                        abstract = await abstract_resolver.resolve_abstract(candidate)
                    if abstract:
                        evidence_id = repository.record_evidence_span(
                            paper_id=paper_id,
                            source_record_id=stored_source_record_id,
                            quote=abstract,
                            locator={"section": "Abstract"},
                            evidence_level="abstract",
                            extraction_method="rule",
                            confidence=0.8,
                            verified=1,
                        )
                        context.evidence_rows.append(
                            (
                                candidate.title,
                                abstract,
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
                        context.file_rows.append(
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
                        context.document_count += 1
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
                            context.evidence_rows.append(
                                (
                                    candidate.title,
                                    full_text_quote,
                                    stored_source_record_id,
                                    candidate.source,
                                    full_text_evidence_id,
                                    "page 1",
                                )
                            )
            return {
                "papers": len(context.paper_ids),
                "source_records": len(context.source_records),
                "evidence": len(context.evidence_rows),
                "files": len(context.file_rows),
                "documents": context.document_count,
            }

        async def judge_relevance_step() -> dict[str, object]:
            """Apply semantic relevance filtering before claims are built."""

            if relevance_judge is None:
                context.relevance_skipped = True
                return {"judged": 0, "dropped": 0, "skipped": True}

            failures = 0
            for candidate, stored_source_record_id in context.source_records:
                verdict, response = await relevance_judge.judge(
                    question=question,
                    subquestions=subquestions,
                    paper=candidate,
                )
                context.verdicts.append(verdict)
                if response is not None:
                    repository.record_model_call(
                        run_id=run_id,
                        provider=response.provider,
                        model=response.model,
                        purpose="semantic_relevance",
                        prompt_hash=response.prompt_hash,
                        prompt_version=relevance_judge.prompt_version,
                        response_hash=response.response_hash,
                        input_tokens=response.input_tokens,
                        output_tokens=response.output_tokens,
                        latency_ms=response.latency_ms,
                        status="success",
                    )
                else:
                    failures += 1
                    repository.record_model_call(
                        run_id=run_id,
                        provider="deepseek",
                        model="unknown",
                        purpose="semantic_relevance",
                        prompt_hash="",
                        prompt_version=relevance_judge.prompt_version,
                        status="failed",
                        error_code=verdict.reason[:120],
                    )
                repository.record_audit_event(
                    run_id=run_id,
                    action="semantic_relevance",
                    target_type="paper",
                    target_id=stored_source_record_id,
                    decision="allowed" if verdict.keep else "denied",
                    details={
                        "paper_key": verdict.paper_key,
                        "domain_scope": verdict.domain_scope,
                        "answer_role": verdict.answer_role,
                        "abstract_available": verdict.abstract_available,
                        "reason": verdict.reason,
                        "failed": verdict.failed,
                    },
                )
                if not verdict.keep:
                    context.dropped_source_record_ids.add(stored_source_record_id)
                    context.dropped_keys.add(verdict.paper_key)

            context.relevance_failures = failures
            return {
                "judged": len(context.verdicts),
                "dropped": len(context.dropped_source_record_ids),
                "failures": failures,
            }

        async def synthesize_claims_step() -> dict[str, object]:
            usable = [
                row
                for row in context.evidence_rows
                if row[2] not in context.dropped_source_record_ids
            ]
            context.claims = build_claims_from_evidence(usable)
            return {"claim_count": len(context.claims)}

        async def validate_citations_step() -> dict[str, object]:
            available_evidence_ids = {row[4] for row in context.evidence_rows}
            for claim in context.claims:
                validate_claim_evidence(claim, available_evidence_ids)
            return {"validated_claims": len(context.claims)}

        async def generate_report_step() -> dict[str, object]:
            report_text = render_report(
                question=question,
                run_id=run_id,
                source_records=context.source_records,
                evidence=context.evidence_rows,
                claims=context.claims,
                files=context.file_rows,
            )
            report_path = reports_root / run_id / "report.md"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report_text, encoding="utf-8")
            report_id = repository.record_report(
                run_id=run_id,
                path=report_path.as_posix(),
                content=report_text,
            )
            for claim in context.claims:
                repository.record_claim(report_id=report_id, claim=claim)
            context.report_path = report_path
            context.report_id = report_id
            return {"report_path": report_path.as_posix()}

        steps = [
            StepSpec(
                step_key="route_sources",
                step_type="route_sources",
                handler=route_sources_step,
            ),
            StepSpec(
                step_key="search_sources",
                step_type="search_sources",
                depends_on=("route_sources",),
                handler=search_sources_step,
            ),
            StepSpec(
                step_key="persist_results",
                step_type="persist_results",
                depends_on=("search_sources",),
                handler=persist_results_step,
            ),
            StepSpec(
                step_key="judge_relevance",
                step_type="judge_relevance",
                depends_on=("persist_results",),
                handler=judge_relevance_step,
            ),
            StepSpec(
                step_key="synthesize_claims",
                step_type="synthesize_claims",
                depends_on=("judge_relevance",),
                handler=synthesize_claims_step,
            ),
            StepSpec(
                step_key="validate_citations",
                step_type="validate_citations",
                depends_on=("synthesize_claims",),
                handler=validate_citations_step,
            ),
            StepSpec(
                step_key="generate_report",
                step_type="generate_report",
                depends_on=("validate_citations",),
                handler=generate_report_step,
            ),
        ]
        execution = await Executor(repository).execute_plan(
            run_id=run_id,
            plan_id=plan_id,
            steps=steps,
            max_attempts=3,
        )
        if execution.status != "COMPLETED" or context.report_path is None:
            raise ResearchExecutionError(
                f"research run failed at step: {execution.failed_step}"
            )
        if context.federated is None:
            raise ResearchExecutionError("research run completed without search results")

        return ResearchRunResult(
            run_id=run_id,
            report_path=context.report_path,
            paper_count=len(context.paper_ids),
            evidence_count=len(context.evidence_rows),
            claim_count=len(context.claims),
            file_count=len(context.file_rows),
            document_count=context.document_count,
            source_counts=context.federated.source_counts,
            source_errors=context.federated.errors,
            variant_errors=context.federated.variant_errors,
            relevance_judged=len(context.verdicts),
            relevance_dropped=len(context.dropped_source_record_ids),
            relevance_failures=context.relevance_failures,
            relevance_skipped=context.relevance_skipped,
            retrieved_paper_keys=tuple(sorted(context.retrieved_keys)),
            dropped_paper_keys=tuple(sorted(context.dropped_keys)),
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