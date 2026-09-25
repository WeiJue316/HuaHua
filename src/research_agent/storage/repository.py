"""SQLite repositories for the M1 research flow."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from research_agent.evidence.claims import ClaimDraft
from research_agent.identity import (
    arxiv_id_from_doi,
    normalize_doi,
    primary_identity,
    strip_arxiv_version,
)
from research_agent.mcp_servers.common import PaperCandidate


def utc_now() -> str:
    """Return a UTC ISO 8601 timestamp."""

    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def json_text(value: Any) -> str:
    """Serialize a value deterministically for storage."""

    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    """Return the SHA-256 hex digest of UTF-8 text."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_key(candidate: PaperCandidate) -> str:
    """Build the canonical paper key from stable identifiers."""

    return primary_identity(candidate)


class ResearchRepository:
    """Persistence boundary for the initial vertical slice."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def get_or_create_project(self, name: str, description: str | None = None) -> str:
        row = self.connection.execute(
            "SELECT id FROM project WHERE name = ? ORDER BY created_at LIMIT 1",
            (name,),
        ).fetchone()
        if row is not None:
            return str(row[0])
        return self.create_project(name, description)

    def create_project(self, name: str, description: str | None = None) -> str:
        project_id = str(uuid4())
        now = utc_now()
        self.connection.execute(
            """
            INSERT INTO project
                (id, name, description, domain, status, created_at, updated_at, settings_json)
            VALUES (?, ?, ?, 'cs_ai', 'active', ?, ?, '{}')
            """,
            (project_id, name, description, now, now),
        )
        return project_id

    def create_research_question(
        self,
        project_id: str,
        question_text: str,
        scope: dict[str, Any] | None = None,
    ) -> str:
        question_id = str(uuid4())
        version_row = self.connection.execute(
            "SELECT COALESCE(MAX(version), 0) + 1 FROM research_question WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        version = int(version_row[0]) if version_row is not None else 1
        self.connection.execute(
            """
            INSERT INTO research_question
                (id, project_id, question_text, normalized_question, scope_json, version,
                 created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                question_id,
                project_id,
                question_text,
                " ".join(question_text.lower().split()),
                json_text(scope or {}),
                version,
                utc_now(),
            ),
        )
        return question_id

    def create_run(
        self,
        project_id: str,
        question_id: str,
        *,
        trigger: str = "cli",
        config: dict[str, Any] | None = None,
        system_version: str = "development",
    ) -> str:
        run_id = str(uuid4())
        config_json = json_text(config or {})
        self.connection.execute(
            """
            INSERT INTO run
                (id, project_id, question_id, status, "trigger", config_hash, config_json,
                 system_version, started_at)
            VALUES (?, ?, ?, 'CREATED', ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                project_id,
                question_id,
                trigger,
                sha256_text(config_json),
                config_json,
                system_version,
                utc_now(),
            ),
        )
        return run_id

    def record_source_call(
        self,
        *,
        run_id: str,
        source: str,
        tool_name: str,
        request_json: Any,
        status: str,
        started_at: str,
        request_hash: str | None = None,
        query_id: str | None = None,
        finished_at: str | None = None,
        http_status: int | None = None,
        elapsed_ms: int | None = None,
        response_hash: str | None = None,
        error_code: str | None = None,
        error_details: Any | None = None,
    ) -> str:
        source_call_id = str(uuid4())
        request_text = json_text(request_json)
        self.connection.execute(
            """
            INSERT INTO source_call
                (id, run_id, query_id, source, tool_name, request_hash, request_json, status,
                 retry_count, http_status, elapsed_ms, response_hash, error_code,
                 error_details_json, started_at, finished_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_call_id,
                run_id,
                query_id,
                source,
                tool_name,
                request_hash or sha256_text(request_text),
                request_text,
                status,
                http_status,
                elapsed_ms,
                response_hash,
                error_code,
                json_text(error_details) if error_details is not None else None,
                started_at,
                finished_at,
            ),
        )
        return source_call_id

    def record_source_record(
        self,
        *,
        source_call_id: str,
        candidate: PaperCandidate,
        api_endpoint: str,
        mapping_version: str = "1.0",
        retrieved_at: str | None = None,
        query_hash: str | None = None,
        query_snapshot: Any | None = None,
        response_hash: str | None = None,
    ) -> str:
        source_record_id = str(uuid4())
        raw_json = json_text(candidate.raw)
        content_hash = sha256_text(raw_json)
        try:
            self.connection.execute(
                """
                INSERT INTO source_record
                    (id, source_call_id, source, source_record_id, api_endpoint, source_version,
                     raw_json, mapping_version, retrieved_at, query_hash, query_snapshot_json,
                     response_hash, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_record_id,
                    source_call_id,
                    candidate.source,
                    candidate.source_record_id,
                    api_endpoint,
                    candidate.source_version,
                    raw_json,
                    mapping_version,
                    retrieved_at or utc_now(),
                    query_hash,
                    json_text(query_snapshot) if query_snapshot is not None else None,
                    response_hash,
                    content_hash,
                ),
            )
        except sqlite3.IntegrityError:
            existing = self.connection.execute(
                """
                SELECT id FROM source_record
                WHERE source = ? AND source_record_id = ? AND content_hash = ?
                """,
                (candidate.source, candidate.source_record_id, content_hash),
            ).fetchone()
            if existing is None:
                raise
            return str(existing[0])
        return source_record_id

    def upsert_paper(self, candidate: PaperCandidate) -> tuple[str, bool]:
        existing_id = self._find_existing_paper(candidate)
        if existing_id is not None:
            self._record_identifiers(existing_id, candidate)
            return existing_id, False

        paper_id = str(uuid4())
        now = utc_now()
        self.connection.execute(
            """
            INSERT INTO paper
                (id, canonical_key, title, title_normalized, abstract, year, publication_date,
                 venue, type, language, open_access_status, citation_count, merge_confidence,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, NULL, 1.0, ?, ?)
            """,
            (
                paper_id,
                canonical_key(candidate),
                candidate.title,
                " ".join(candidate.title.lower().split()),
                candidate.abstract,
                candidate.year,
                candidate.published_at,
                candidate.venue,
                "preprint" if candidate.source == "arxiv" else None,
                candidate.open_access.status,
                now,
                now,
            ),
        )
        self._record_identifiers(paper_id, candidate)
        return paper_id, True

    def _find_existing_paper(self, candidate: PaperCandidate) -> str | None:
        lookups: list[tuple[str, str]] = []
        if candidate.doi:
            lookups.append(("doi", normalize_doi(candidate.doi)))
            arxiv_id = arxiv_id_from_doi(candidate.doi)
            if arxiv_id is not None:
                lookups.append(("arxiv_id", arxiv_id))
        if candidate.source == "arxiv":
            lookups.append(("arxiv_id", strip_arxiv_version(candidate.source_record_id).lower()))
        lookups.append((f"{candidate.source}_id", candidate.source_record_id))
        for identifier_type, normalized_value in lookups:
            row = self.connection.execute(
                """
                SELECT paper_id FROM paper_identifier
                WHERE type = ? AND normalized_value = ?
                """,
                (identifier_type, normalized_value),
            ).fetchone()
            if row is not None:
                return str(row[0])
        row = self.connection.execute(
            "SELECT id FROM paper WHERE canonical_key = ?",
            (canonical_key(candidate),),
        ).fetchone()
        return str(row[0]) if row is not None else None

    def _record_identifiers(self, paper_id: str, candidate: PaperCandidate) -> None:
        identifiers: list[tuple[str, str, str, int]] = []
        if candidate.doi:
            identifiers.append(("doi", candidate.doi, normalize_doi(candidate.doi), 1))
            arxiv_id = arxiv_id_from_doi(candidate.doi)
            if arxiv_id is not None:
                identifiers.append(("arxiv_id", arxiv_id, arxiv_id, 0))
        source_normalized = candidate.source_record_id
        if candidate.source == "arxiv":
            source_normalized = strip_arxiv_version(candidate.source_record_id).lower()
        identifiers.append(
            (
                f"{candidate.source}_id",
                candidate.source_record_id,
                source_normalized,
                0 if candidate.doi else 1,
            )
        )
        for identifier_type, value, normalized_value, is_primary in identifiers:
            self.connection.execute(
                """
                INSERT OR IGNORE INTO paper_identifier
                    (id, paper_id, type, value, normalized_value, source_record_id, is_primary)
                VALUES (?, ?, ?, ?, ?, NULL, ?)
                """,
                (
                    str(uuid4()),
                    paper_id,
                    identifier_type,
                    value,
                    normalized_value,
                    is_primary,
                ),
            )

    def link_paper_source_record(
        self,
        *,
        paper_id: str,
        source_record_id: str,
        merge_reason: str,
        match_score: float | None = None,
        is_primary_metadata: bool = False,
    ) -> None:
        self.connection.execute(
            """
            INSERT OR IGNORE INTO paper_source_record
                (paper_id, source_record_id, match_score, merge_reason, is_primary_metadata)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                paper_id,
                source_record_id,
                match_score,
                merge_reason,
                1 if is_primary_metadata else 0,
            ),
        )

    def record_file(
        self,
        *,
        paper_id: str,
        kind: str,
        sha256: str,
        path: str,
        size_bytes: int,
        content_type: str,
        source_url: str,
        retrieved_at: str,
        final_url: str | None = None,
        license: str | None = None,
        status: str = "stored",
    ) -> str:
        file_id = str(uuid4())
        self.connection.execute(
            """
            INSERT INTO file
                (id, paper_id, kind, sha256, path, size_bytes, content_type, source_url,
                 final_url, retrieved_at, license, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                file_id,
                paper_id,
                kind,
                sha256,
                path,
                size_bytes,
                content_type,
                source_url,
                final_url,
                retrieved_at,
                license,
                status,
                utc_now(),
            ),
        )
        return file_id

    def record_document(
        self,
        *,
        file_id: str,
        parser: str,
        document_id: str | None = None,
        parser_version: str,
        text_path: str,
        text_sha256: str,
        locator_scheme: str,
        parse_status: str,
    ) -> str:
        document_id = document_id or str(uuid4())
        self.connection.execute(
            """
            INSERT INTO document
                (id, file_id, parser, parser_version, text_path, text_sha256, locator_scheme,
                 parse_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                file_id,
                parser,
                parser_version,
                text_path,
                text_sha256,
                locator_scheme,
                parse_status,
                utc_now(),
            ),
        )
        return document_id

    def record_evidence_span(
        self,
        *,
        paper_id: str,
        source_record_id: str,
        quote: str,
        locator: Any,
        evidence_level: str,
        extraction_method: str,
        confidence: float,
        verified: int,
        document_id: str | None = None,
        file_id: str | None = None,
        extractor_version: str | None = None,
    ) -> str:
        evidence_id = str(uuid4())
        self.connection.execute(
            """
            INSERT INTO evidence_span
                (id, paper_id, source_record_id, document_id, file_id, quote, quote_hash,
                 locator_json, evidence_level, extraction_method, extractor_version,
                 confidence, verified, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evidence_id,
                paper_id,
                source_record_id,
                document_id,
                file_id,
                quote,
                sha256_text(quote),
                json_text(locator),
                evidence_level,
                extraction_method,
                extractor_version,
                confidence,
                verified,
                utc_now(),
            ),
        )
        return evidence_id

    def record_plan(
        self,
        *,
        run_id: str,
        plan_json: Any,
        strategy: str = "template",
        status: str = "active",
    ) -> str:
        plan_id = str(uuid4())
        version_row = self.connection.execute(
            "SELECT COALESCE(MAX(version), 0) + 1 FROM plan WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        version = int(version_row[0]) if version_row is not None else 1
        self.connection.execute(
            """
            INSERT INTO plan
                (id, run_id, version, strategy, status, plan_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                plan_id,
                run_id,
                version,
                strategy,
                status,
                json_text(plan_json),
                utc_now(),
            ),
        )
        return plan_id

    def record_plan_step(
        self,
        *,
        plan_id: str,
        step_key: str,
        step_type: str,
        depends_on: list[str] | None = None,
        status: str = "PENDING",
        input_json: Any | None = None,
    ) -> str:
        step_id = str(uuid4())
        self.connection.execute(
            """
            INSERT INTO plan_step
                (id, plan_id, step_key, step_type, status, depends_on_json, input_json,
                 output_json, attempt_count, started_at, finished_at, error_code,
                 checkpoint_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 0, NULL, NULL, NULL, NULL)
            """,
            (
                step_id,
                plan_id,
                step_key,
                step_type,
                status,
                json_text(depends_on or []),
                json_text(input_json) if input_json is not None else None,
            ),
        )
        return step_id

    def update_run_status(
        self,
        *,
        run_id: str,
        status: str,
        error_code: str | None = None,
        finished_at: str | None = None,
    ) -> None:
        if finished_at is None:
            self.connection.execute(
                "UPDATE run SET status = ?, error_code = ? WHERE id = ?",
                (status, error_code, run_id),
            )
        else:
            self.connection.execute(
                """
                UPDATE run
                SET status = ?, error_code = ?, finished_at = ?
                WHERE id = ?
                """,
                (status, error_code, finished_at, run_id),
            )

    def update_plan_step_status(
        self,
        *,
        step_id: str,
        status: str,
        attempt_count: int | None = None,
        input_json: Any | None = None,
        output_json: Any | None = None,
        checkpoint_json: Any | None = None,
        error_code: str | None = None,
        started_at: str | None = None,
        finished_at: str | None = None,
    ) -> None:
        self.connection.execute(
            """
            UPDATE plan_step
            SET status = ?,
                attempt_count = COALESCE(?, attempt_count),
                input_json = COALESCE(?, input_json),
                output_json = COALESCE(?, output_json),
                checkpoint_json = COALESCE(?, checkpoint_json),
                error_code = ?,
                started_at = COALESCE(?, started_at),
                finished_at = COALESCE(?, finished_at)
            WHERE id = ?
            """,
            (
                status,
                attempt_count,
                json_text(input_json) if input_json is not None else None,
                json_text(output_json) if output_json is not None else None,
                json_text(checkpoint_json) if checkpoint_json is not None else None,
                error_code,
                started_at,
                finished_at,
                step_id,
            ),
        )

    def record_step_attempt(
        self,
        *,
        step_id: str,
        attempt_no: int,
        status: str,
        input_json: Any | None = None,
        output_json: Any | None = None,
        checkpoint_json: Any | None = None,
        error_code: str | None = None,
        started_at: str,
        finished_at: str | None = None,
    ) -> str:
        attempt_id = str(uuid4())
        self.connection.execute(
            """
            INSERT INTO step_attempt
                (id, step_id, attempt_no, status, input_json, output_json,
                 checkpoint_json, error_code, started_at, finished_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attempt_id,
                step_id,
                attempt_no,
                status,
                json_text(input_json) if input_json is not None else None,
                json_text(output_json) if output_json is not None else None,
                json_text(checkpoint_json) if checkpoint_json is not None else None,
                error_code,
                started_at,
                finished_at,
            ),
        )
        return attempt_id

    def record_audit_event(
        self,
        *,
        run_id: str | None,
        action: str,
        target_type: str,
        target_id: str | None = None,
        actor: str = "system",
        decision: str | None = None,
        details: Any | None = None,
    ) -> str:
        audit_id = str(uuid4())
        self.connection.execute(
            """
            INSERT INTO audit_event
                (id, run_id, actor, action, target_type, target_id, decision,
                 details_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                audit_id,
                run_id,
                actor,
                action,
                target_type,
                target_id,
                decision,
                json_text(details) if details is not None else None,
                utc_now(),
            ),
        )
        return audit_id

    def record_model_call(
        self,
        *,
        run_id: str | None,
        provider: str,
        model: str,
        purpose: str,
        prompt_hash: str,
        prompt_version: str | None = None,
        response_hash: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        cost: float | None = None,
        latency_ms: int | None = None,
        status: str = "success",
        error_code: str | None = None,
    ) -> str:
        """Record one language-model call for cost and reproducibility auditing."""

        call_id = str(uuid4())
        self.connection.execute(
            """
            INSERT INTO model_call
                (id, run_id, provider, model, purpose, prompt_hash,
                 prompt_version, response_hash, input_tokens, output_tokens,
                 cost, latency_ms, status, error_code, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                call_id,
                run_id,
                provider,
                model,
                purpose,
                prompt_hash,
                prompt_version,
                response_hash,
                input_tokens,
                output_tokens,
                cost,
                latency_ms,
                status,
                error_code,
                utc_now(),
            ),
        )
        return call_id

    def record_claim(self, *, report_id: str, claim: ClaimDraft) -> str:
        claim_id = str(uuid4())
        self.connection.execute(
            """
            INSERT INTO claim
                (id, report_id, claim_text, claim_type, support_status, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                claim_id,
                report_id,
                claim.claim_text,
                claim.claim_type,
                claim.support_status,
                claim.confidence,
                utc_now(),
            ),
        )
        for rank, evidence_span_id in enumerate(claim.evidence_span_ids):
            self.connection.execute(
                """
                INSERT INTO claim_evidence
                    (claim_id, evidence_span_id, relation_type, rank)
                VALUES (?, ?, 'supports', ?)
                """,
                (claim_id, evidence_span_id, rank),
            )
        return claim_id

    def record_report(
        self,
        *,
        run_id: str,
        path: str,
        content: str,
        format: str = "markdown",
        status: str = "validated",
    ) -> str:
        report_id = str(uuid4())
        version_row = self.connection.execute(
            "SELECT COALESCE(MAX(version), 0) + 1 FROM report WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        version = int(version_row[0]) if version_row is not None else 1
        self.connection.execute(
            """
            INSERT INTO report
                (id, run_id, version, format, path, sha256, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                run_id,
                version,
                format,
                path,
                sha256_text(content),
                status,
                utc_now(),
            ),
        )
        return report_id