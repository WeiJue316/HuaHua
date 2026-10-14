"""Research flow: source search to traceable Markdown report."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

from research_agent.evaluator.ranking import interleave_by_source
from research_agent.evidence.claims import (
    ClaimDraft,
    build_claims_from_evidence,
    build_direct_claims,
    constrain_claim_citations,
    detach_unknown_span_ids,
    validate_claim_evidence,
)
from research_agent.evidence.synthesis import ClaimSynthesizer
from research_agent.executor.executor import Executor, StepSpec
from research_agent.identity import identity_aliases
from research_agent.mcp_servers.arxiv.client import ArxivClient
from research_agent.mcp_servers.cache import ResponseCache
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
from research_agent.storage.pdf_parser import first_paragraph_locator, parse_pdf
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
    paper_aliases: tuple[tuple[str, tuple[str, ...]], ...] = ()
    source_http_calls: int = 0


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
    retrieved_order: list[str] = field(default_factory=list)
    dropped_keys: set[str] = field(default_factory=set)
    identity_aliases: dict[str, frozenset[str]] = field(default_factory=dict)
    verdicts: list[RelevanceVerdict] = field(default_factory=list)
    relevance_failures: int = 0
    relevance_skipped: bool = False
    retrieved_paper_keys: tuple[str, ...] = ()
    dropped_paper_keys: tuple[str, ...] = ()
    findings: str = ""
    report_path: Path | None = None
    report_id: str | None = None


@dataclass(frozen=True)
class _ContextSnapshot:
    """Copies of the fields one step may change, taken before that step runs."""

    selected_sources: list[str]
    federated: FederatedSearchResult | None
    source_records: list[tuple[PaperCandidate, str]]
    evidence_rows: list[tuple[str, str, str, str, str, str]]
    file_rows: list[tuple[str, str, str, str]]
    paper_ids: set[str]
    document_count: int
    claims: list[ClaimDraft]
    dropped_source_record_ids: set[str]
    retrieved_keys: set[str]
    retrieved_order: list[str]
    dropped_keys: set[str]
    identity_aliases: dict[str, frozenset[str]]
    verdicts: list[RelevanceVerdict]
    relevance_failures: int
    relevance_skipped: bool
    retrieved_paper_keys: tuple[str, ...]
    dropped_paper_keys: tuple[str, ...]
    findings: str
    report_path: Path | None
    report_id: str | None


def _capture_context(context: _RunContext) -> _ContextSnapshot:
    return _ContextSnapshot(
        selected_sources=list(context.selected_sources),
        federated=context.federated,
        source_records=list(context.source_records),
        evidence_rows=list(context.evidence_rows),
        file_rows=list(context.file_rows),
        paper_ids=set(context.paper_ids),
        document_count=context.document_count,
        claims=list(context.claims),
        dropped_source_record_ids=set(context.dropped_source_record_ids),
        retrieved_keys=set(context.retrieved_keys),
        retrieved_order=list(context.retrieved_order),
        dropped_keys=set(context.dropped_keys),
        identity_aliases=dict(context.identity_aliases),
        verdicts=list(context.verdicts),
        relevance_failures=context.relevance_failures,
        relevance_skipped=context.relevance_skipped,
        retrieved_paper_keys=context.retrieved_paper_keys,
        dropped_paper_keys=context.dropped_paper_keys,
        findings=context.findings,
        report_path=context.report_path,
        report_id=context.report_id,
    )


def _restore_context(context: _RunContext, snapshot: _ContextSnapshot) -> None:
    context.selected_sources = snapshot.selected_sources
    context.federated = snapshot.federated
    context.source_records = snapshot.source_records
    context.evidence_rows = snapshot.evidence_rows
    context.file_rows = snapshot.file_rows
    context.paper_ids = snapshot.paper_ids
    context.document_count = snapshot.document_count
    context.claims = snapshot.claims
    context.dropped_source_record_ids = snapshot.dropped_source_record_ids
    context.retrieved_keys = snapshot.retrieved_keys
    context.retrieved_order = snapshot.retrieved_order
    context.dropped_keys = snapshot.dropped_keys
    context.identity_aliases = snapshot.identity_aliases
    context.verdicts = snapshot.verdicts
    context.relevance_failures = snapshot.relevance_failures
    context.relevance_skipped = snapshot.relevance_skipped
    context.retrieved_paper_keys = snapshot.retrieved_paper_keys
    context.dropped_paper_keys = snapshot.dropped_paper_keys
    context.findings = snapshot.findings
    context.report_path = snapshot.report_path
    context.report_id = snapshot.report_id


def _rewind_on_failure(
    context: _RunContext,
    handler: Callable[[], Awaitable[Any]],
) -> Callable[[], Awaitable[Any]]:
    """Restore step state when the handler fails, so a retry starts clean."""

    async def wrapped() -> Any:
        snapshot = _capture_context(context)
        try:
            return await handler()
        except Exception:
            _restore_context(context, snapshot)
            raise

    return wrapped


def _md_cell(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.replace("|", "\\|").split())


def _report_inputs(
    context: _RunContext,
) -> tuple[
    list[tuple[PaperCandidate, str]],
    list[tuple[PaperCandidate, str, str]],
    list[tuple[str, str, str, str, str, str]],
    list[tuple[str, str, str, str]],
]:
    """Split persisted rows into the report body and the excluded section."""

    dropped_ids = context.dropped_source_record_ids
    reason_by_record = {
        source_record_id: verdict.reason
        for (_paper, source_record_id), verdict in zip(
            context.source_records,
            context.verdicts,
            strict=False,
        )
    }
    kept_records = [
        (paper, source_record_id)
        for paper, source_record_id in context.source_records
        if source_record_id not in dropped_ids
    ]
    excluded = [
        (paper, source_record_id, reason_by_record.get(source_record_id, ""))
        for paper, source_record_id in context.source_records
        if source_record_id in dropped_ids
    ]
    kept_evidence = [
        row for row in context.evidence_rows if row[2] not in dropped_ids
    ]
    dropped_files = {
        (paper.title, paper.source)
        for paper, source_record_id in context.source_records
        if source_record_id in dropped_ids
    }
    kept_file_keys = {(paper.title, paper.source) for paper, _sid in kept_records}
    hidden_files = dropped_files - kept_file_keys
    kept_files = [
        row for row in context.file_rows if (row[0], row[1]) not in hidden_files
    ]
    return kept_records, excluded, kept_evidence, kept_files


def render_report(
    *,
    question: str,
    run_id: str,
    source_records: list[tuple[PaperCandidate, str]],
    evidence: list[tuple[str, str, str, str, str, str]],
    claims: list[ClaimDraft],
    files: list[tuple[str, str, str, str]],
    findings: str = "",
    excluded: Sequence[tuple[PaperCandidate, str, str]] = (),
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

    if findings.strip():
        lines.extend(["", "## Findings", "", findings.strip()])

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

    if excluded:
        lines.extend(
            [
                "",
                "## 已排除候选",
                "",
                "这些候选被相关性过滤移除，不进入论文、证据或结论。",
                "",
                "| # | Title | Source | Source ID | Source Record | Reason |",
                "|---:|---|---|---|---|---|",
            ]
        )
        for index, (paper, source_record_id, reason) in enumerate(excluded, start=1):
            lines.append(
                f"| {index} | {_md_cell(paper.title)} | {_md_cell(paper.source)} "
                f"| {_md_cell(paper.source_record_id)} | `{source_record_id}` "
                f"| {_md_cell(reason)} |"
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
    response_cache: ResponseCache | None = None,
    evidence_chain: bool = True,
    claim_synthesizer: ClaimSynthesizer | None = None,
    citation_constraint: bool = True,
) -> ResearchRunResult:
    """Run a source search and report pipeline through the Executor."""

    db_path = Path(db_path)
    reports_root = Path(reports_root)
    archive_root = Path(artifact_root) if artifact_root else db_path.parent
    apply_migrations(db_path)
    if plan is None:
        from research_agent.planner.planner import ROUTING_BUDGET, plan_research

        plan = plan_research(
            question,
            available_sources=tuple(clients),
            max_results_per_source=max_results_per_source,
            max_concurrency=min(5, len(clients)),
            max_sources=ROUTING_BUDGET,
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
                "evidence_chain": evidence_chain,
                "synthesis": (
                    claim_synthesizer.prompt_version
                    if claim_synthesizer is not None
                    else "template"
                ),
                "citation_constraint": citation_constraint,
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
            # snapshot before the search so the step reports this run's cache
            # activity, not the cache's lifetime totals
            hits_before = response_cache.stats.hits if response_cache else 0
            misses_before = response_cache.stats.misses if response_cache else 0
            context.federated = await search_sources(
                selected_clients,
                query=question,
                query_variants=plan.query_variants,
                max_results_per_source=max_results_per_source,
                max_concurrency=plan.max_concurrency,
            )
            payload: dict[str, object] = {
                "source_counts": context.federated.source_counts,
                "source_errors": context.federated.errors,
            }
            if response_cache is not None:
                payload["cache_hits"] = response_cache.stats.hits - hits_before
                payload["cache_misses"] = (
                    response_cache.stats.misses - misses_before
                )
            return payload

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
                    paper_key = canonical_key(candidate)
                    context.retrieved_keys.add(paper_key)
                    context.identity_aliases[paper_key] = identity_aliases(candidate)
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
                    evidence_source_record_id = stored_source_record_id
                    evidence_source = candidate.source
                    if not abstract and abstract_resolver is not None:
                        enrichment = await abstract_resolver.resolve_abstract(candidate)
                        if enrichment is not None and enrichment.abstract:
                            abstract = enrichment.abstract
                            evidence_source = enrichment.source.source
                            evidence_source_record_id = _record_abstract_source(
                                repository,
                                run_id=run_id,
                                paper_id=paper_id,
                                source=enrichment.source,
                                doi=candidate.doi,
                            )
                    if evidence_chain and abstract:
                        evidence_id = repository.record_evidence_span(
                            paper_id=paper_id,
                            source_record_id=evidence_source_record_id,
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
                                evidence_source_record_id,
                                evidence_source,
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
                        span = first_paragraph_locator(parse_result)
                        if evidence_chain and span is not None:
                            full_text_evidence_id = repository.record_evidence_span(
                                paper_id=paper_id,
                                source_record_id=stored_source_record_id,
                                document_id=document_id,
                                file_id=file_id,
                                quote=span.quote,
                                locator={
                                    "page": span.page,
                                    "paragraph_index": span.paragraph_index,
                                    "char_start": span.char_start,
                                    "char_end": span.char_end,
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
                                    span.quote,
                                    stored_source_record_id,
                                    candidate.source,
                                    full_text_evidence_id,
                                    f"page {span.page}",
                                )
                            )
            groups: list[list[str]] = []
            for source in context.selected_sources:
                group: list[str] = []
                seen_in_source: set[str] = set()
                for paper in context.federated.papers:
                    if paper.source != source:
                        continue
                    key = canonical_key(paper)
                    if key in seen_in_source:
                        continue
                    seen_in_source.add(key)
                    group.append(key)
                groups.append(group)
            context.retrieved_order = interleave_by_source(groups)
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
            available_evidence_ids = {row[4] for row in usable}
            mode = "template"
            if not evidence_chain:
                papers_by_key = {
                    canonical_key(paper): paper
                    for paper, _source_record_id in context.source_records
                    if canonical_key(paper) not in context.dropped_keys
                }
                context.claims = build_direct_claims(list(papers_by_key.values()))
                context.findings = ""
                mode = "direct"
            elif claim_synthesizer is None:
                context.claims = build_claims_from_evidence(usable)
                context.findings = ""
            else:
                synthesized = await claim_synthesizer.synthesize(
                    question=question,
                    subquestions=subquestions,
                    evidence=usable,
                )
                mode = "fallback" if synthesized.used_fallback else "llm"
                context.findings = synthesized.findings
                if synthesized.response is not None:
                    repository.record_model_call(
                        run_id=run_id,
                        provider=synthesized.response.provider,
                        model=synthesized.response.model,
                        purpose="claim_synthesis",
                        prompt_hash=synthesized.response.prompt_hash,
                        prompt_version=claim_synthesizer.prompt_version,
                        response_hash=synthesized.response.response_hash,
                        input_tokens=synthesized.response.input_tokens,
                        output_tokens=synthesized.response.output_tokens,
                        latency_ms=synthesized.response.latency_ms,
                        status="success",
                    )
                else:
                    repository.record_model_call(
                        run_id=run_id,
                        provider="unknown",
                        model="unknown",
                        purpose="claim_synthesis",
                        prompt_hash="",
                        prompt_version=claim_synthesizer.prompt_version,
                        status="failed",
                        error_code="model_gateway_error",
                    )
                if citation_constraint:
                    context.claims = constrain_claim_citations(
                        synthesized.claims,
                        available_evidence_ids,
                    )
                else:
                    context.claims = detach_unknown_span_ids(
                        synthesized.claims,
                        available_evidence_ids,
                    )
            repository.record_audit_event(
                run_id=run_id,
                action="synthesize_claims",
                target_type="run",
                target_id=run_id,
                decision="allowed",
                details={
                    "mode": mode,
                    "citation_constraint": citation_constraint,
                    "claim_count": len(context.claims),
                },
            )
            return {
                "claim_count": len(context.claims),
                "mode": mode,
                "citation_constraint": citation_constraint,
            }

        async def validate_citations_step() -> dict[str, object]:
            if not citation_constraint:
                return {"validated_claims": 0, "citation_constraint": False}
            available_evidence_ids = {row[4] for row in context.evidence_rows}
            for claim in context.claims:
                validate_claim_evidence(claim, available_evidence_ids)
            return {
                "validated_claims": len(context.claims),
                "citation_constraint": True,
            }

        async def generate_report_step() -> dict[str, object]:
            kept_records, excluded, kept_evidence, kept_files = (
                _report_inputs(context)
            )
            report_text = render_report(
                question=question,
                run_id=run_id,
                source_records=kept_records,
                evidence=kept_evidence,
                claims=context.claims,
                files=kept_files,
                findings=context.findings,
                excluded=excluded,
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
                handler=_rewind_on_failure(context, route_sources_step),
            ),
            StepSpec(
                step_key="search_sources",
                step_type="search_sources",
                depends_on=("route_sources",),
                handler=_rewind_on_failure(context, search_sources_step),
            ),
            StepSpec(
                step_key="persist_results",
                step_type="persist_results",
                depends_on=("search_sources",),
                handler=_rewind_on_failure(context, persist_results_step),
            ),
            StepSpec(
                step_key="judge_relevance",
                step_type="judge_relevance",
                depends_on=("persist_results",),
                handler=_rewind_on_failure(context, judge_relevance_step),
            ),
            StepSpec(
                step_key="synthesize_claims",
                step_type="synthesize_claims",
                depends_on=("judge_relevance",),
                handler=_rewind_on_failure(context, synthesize_claims_step),
            ),
            StepSpec(
                step_key="validate_citations",
                step_type="validate_citations",
                depends_on=("synthesize_claims",),
                handler=_rewind_on_failure(context, validate_citations_step),
            ),
            StepSpec(
                step_key="generate_report",
                step_type="generate_report",
                depends_on=("validate_citations",),
                handler=_rewind_on_failure(context, generate_report_step),
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
            evidence_count=len(_report_inputs(context)[2]),
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
            retrieved_paper_keys=tuple(context.retrieved_order),
            dropped_paper_keys=tuple(sorted(context.dropped_keys)),
            paper_aliases=tuple(
                (key, tuple(sorted(aliases)))
                for key, aliases in sorted(context.identity_aliases.items())
            ),
            source_http_calls=context.federated.http_calls,
        )


def _record_abstract_source(
    repository: ResearchRepository,
    *,
    run_id: str,
    paper_id: str,
    source: PaperCandidate,
    doi: str | None,
) -> str:
    """Store the source that supplied a backfilled abstract and link it to the paper."""

    repository.upsert_paper(source)
    source_call_id = repository.record_source_call(
        run_id=run_id,
        source=source.source,
        tool_name=f"{source.source}_get_paper",
        request_json={"doi": doi, "purpose": "abstract_enrichment"},
        status="success",
        started_at=utc_now(),
        finished_at=utc_now(),
    )
    source_record_id = repository.record_source_record(
        source_call_id=source_call_id,
        candidate=source,
        api_endpoint=_source_endpoint(source.source),
        query_snapshot={"doi": doi, "purpose": "abstract_enrichment"},
    )
    repository.link_paper_source_record(
        paper_id=paper_id,
        source_record_id=source_record_id,
        merge_reason="abstract_enrichment",
    )
    return source_record_id


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