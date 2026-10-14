"""Read-only queries for the local evidence-chain API."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from research_agent.paths import project_root


def public_path(value: str | None) -> str:
    """Return a project-relative path, never a machine path."""

    if not value:
        return ""
    candidate = Path(value)
    if not candidate.is_absolute():
        return candidate.as_posix()
    try:
        return candidate.resolve().relative_to(project_root().resolve()).as_posix()
    except ValueError:
        return ""


def list_runs(
    connection: sqlite3.Connection,
    *,
    limit: int,
    offset: int,
) -> tuple[list[dict[str, Any]], int]:
    total = int(connection.execute("SELECT COUNT(*) FROM run").fetchone()[0])
    rows = connection.execute(
        f"""
        SELECT
            run.id,
            research_question.question_text,
            run.status,
            run."trigger" AS trigger_name,
            run.started_at,
            run.finished_at,
            run.error_code,
            {_count_sql()}
        FROM run
        JOIN research_question ON research_question.id = run.question_id
        ORDER BY run.started_at IS NULL, run.started_at DESC, run.id
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    ).fetchall()
    return [_run_item(row) for row in rows], total


def get_run(connection: sqlite3.Connection, run_id: str) -> dict[str, Any] | None:
    row = connection.execute(
        f"""
        SELECT
            run.id,
            research_question.question_text,
            run.status,
            run."trigger" AS trigger_name,
            run.started_at,
            run.finished_at,
            run.error_code,
            run.project_id,
            run.question_id,
            {_count_sql()}
        FROM run
        JOIN research_question ON research_question.id = run.question_id
        WHERE run.id = ?
        """,
        (run_id,),
    ).fetchone()
    if row is None:
        return None
    item = _run_item(row)
    item["project_id"] = str(row["project_id"])
    item["question_id"] = str(row["question_id"])
    return item


def list_steps(connection: sqlite3.Connection, run_id: str) -> list[dict[str, Any]] | None:
    if get_run(connection, run_id) is None:
        return None
    plan = connection.execute(
        """
        SELECT id FROM plan
        WHERE run_id = ?
        ORDER BY version DESC
        LIMIT 1
        """,
        (run_id,),
    ).fetchone()
    if plan is None:
        return []
    rows = connection.execute(
        """
        SELECT id, step_key, step_type, status, depends_on_json, attempt_count,
               started_at, finished_at, error_code
        FROM plan_step
        WHERE plan_id = ?
        ORDER BY rowid
        """,
        (str(plan["id"]),),
    ).fetchall()
    steps: list[dict[str, Any]] = []
    for row in rows:
        depends = json.loads(str(row["depends_on_json"]))
        steps.append(
            {
                "id": str(row["id"]),
                "step_key": str(row["step_key"]),
                "step_type": str(row["step_type"]),
                "status": str(row["status"]),
                "depends_on": [str(item) for item in depends] if isinstance(depends, list) else [],
                "attempt_count": int(row["attempt_count"]),
                "started_at": row["started_at"],
                "finished_at": row["finished_at"],
                "error_code": row["error_code"],
            }
        )
    return steps


def list_sources(connection: sqlite3.Connection, run_id: str) -> list[dict[str, Any]] | None:
    if get_run(connection, run_id) is None:
        return None
    rows = connection.execute(
        """
        SELECT
            source_call.source AS source,
            COUNT(*) AS call_count,
            COALESCE(SUM(CASE WHEN source_call.status = 'success' THEN 1 ELSE 0 END), 0)
                AS success_count,
            COALESCE(SUM(CASE WHEN source_call.status = 'failed' THEN 1 ELSE 0 END), 0)
                AS failed_count,
            (
                SELECT COUNT(DISTINCT paper_source_record.paper_id)
                FROM source_record
                JOIN paper_source_record
                    ON paper_source_record.source_record_id = source_record.id
                WHERE source_record.source_call_id IN (
                    SELECT id FROM source_call AS calls_for_source
                    WHERE calls_for_source.run_id = source_call.run_id
                      AND calls_for_source.source = source_call.source
                )
            ) AS paper_count
        FROM source_call
        WHERE source_call.run_id = ?
        GROUP BY source_call.source
        ORDER BY source_call.source
        """,
        (run_id,),
    ).fetchall()
    return [
        {
            "source": str(row["source"]),
            "call_count": int(row["call_count"]),
            "success_count": int(row["success_count"]),
            "failed_count": int(row["failed_count"]),
            "paper_count": int(row["paper_count"]),
        }
        for row in rows
    ]


def list_papers(
    connection: sqlite3.Connection,
    run_id: str,
    *,
    limit: int,
    offset: int,
) -> tuple[list[dict[str, Any]], int] | None:
    if get_run(connection, run_id) is None:
        return None
    total = int(
        connection.execute(
            f"SELECT COUNT(*) {_paper_from_sql()}",
            (run_id,),
        ).fetchone()[0]
    )
    rows = connection.execute(
        f"""
        SELECT paper.*
        {_paper_from_sql()}
        ORDER BY paper.created_at, paper.id
        LIMIT ? OFFSET ?
        """,
        (run_id, limit, offset),
    ).fetchall()
    return [_paper_item(connection, row, run_id) for row in rows], total


def get_paper(connection: sqlite3.Connection, paper_id: str) -> dict[str, Any] | None:
    row = connection.execute("SELECT * FROM paper WHERE id = ?", (paper_id,)).fetchone()
    if row is None:
        return None
    return _paper_item(connection, row, None)


def list_claims(
    connection: sqlite3.Connection,
    run_id: str,
    *,
    limit: int,
    offset: int,
) -> tuple[list[dict[str, Any]], int] | None:
    if get_run(connection, run_id) is None:
        return None
    report_id = _latest_report_id(connection, run_id)
    if report_id is None:
        return [], 0
    total = int(
        connection.execute(
            "SELECT COUNT(*) FROM claim WHERE report_id = ?",
            (report_id,),
        ).fetchone()[0]
    )
    rows = connection.execute(
        """
        SELECT * FROM claim
        WHERE report_id = ?
        ORDER BY created_at, id
        LIMIT ? OFFSET ?
        """,
        (report_id, limit, offset),
    ).fetchall()
    return [_claim_item(connection, row) for row in rows], total


def get_claim(connection: sqlite3.Connection, claim_id: str) -> dict[str, Any] | None:
    row = connection.execute("SELECT * FROM claim WHERE id = ?", (claim_id,)).fetchone()
    if row is None:
        return None
    return _claim_item(connection, row)


def get_evidence_span(
    connection: sqlite3.Connection,
    evidence_span_id: str,
) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM evidence_span WHERE id = ?",
        (evidence_span_id,),
    ).fetchone()
    if row is None:
        return None
    locator = json.loads(str(row["locator_json"]))
    return {
        "id": str(row["id"]),
        "paper_id": str(row["paper_id"]),
        "source_record_id": str(row["source_record_id"]),
        "quote": str(row["quote"]),
        "locator": locator if isinstance(locator, dict) else {},
        "evidence_level": str(row["evidence_level"]),
        "extraction_method": str(row["extraction_method"]),
        "confidence": float(row["confidence"]),
        "verified": bool(row["verified"]),
        "file_id": row["file_id"],
        "document_id": row["document_id"],
    }


def get_source_record(
    connection: sqlite3.Connection,
    source_record_id: str,
) -> dict[str, Any] | None:
    row = connection.execute(
        """
        SELECT id, source, source_record_id, retrieved_at, api_endpoint
        FROM source_record
        WHERE id = ?
        """,
        (source_record_id,),
    ).fetchone()
    if row is None:
        return None
    return {
        "id": str(row["id"]),
        "source": str(row["source"]),
        "source_record_id": str(row["source_record_id"]),
        "retrieved_at": str(row["retrieved_at"]),
        "api_endpoint": str(row["api_endpoint"]),
    }


def get_file(connection: sqlite3.Connection, file_id: str) -> dict[str, Any] | None:
    row = connection.execute("SELECT * FROM file WHERE id = ?", (file_id,)).fetchone()
    if row is None:
        return None
    return {
        "id": str(row["id"]),
        "paper_id": str(row["paper_id"]),
        "kind": str(row["kind"]),
        "sha256": str(row["sha256"]),
        "path": public_path(str(row["path"])),
        "size_bytes": int(row["size_bytes"]),
        "content_type": str(row["content_type"]),
        "source_url": str(row["source_url"]),
        "retrieved_at": str(row["retrieved_at"]),
        "status": str(row["status"]),
    }


def get_document(connection: sqlite3.Connection, document_id: str) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM document WHERE id = ?",
        (document_id,),
    ).fetchone()
    if row is None:
        return None
    return {
        "id": str(row["id"]),
        "file_id": str(row["file_id"]),
        "parser": str(row["parser"]),
        "parser_version": str(row["parser_version"]),
        "text_path": public_path(str(row["text_path"])),
        "locator_scheme": str(row["locator_scheme"]),
        "parse_status": str(row["parse_status"]),
    }


def _count_sql() -> str:
    return """
        (
            SELECT COUNT(DISTINCT paper_source_record.paper_id)
            FROM source_call
            JOIN source_record ON source_record.source_call_id = source_call.id
            JOIN paper_source_record
                ON paper_source_record.source_record_id = source_record.id
            WHERE source_call.run_id = run.id
        ) AS paper_count,
        (
            SELECT COUNT(*)
            FROM source_call
            JOIN source_record ON source_record.source_call_id = source_call.id
            JOIN evidence_span ON evidence_span.source_record_id = source_record.id
            WHERE source_call.run_id = run.id
        ) AS evidence_count,
        (
            SELECT COUNT(*)
            FROM report
            JOIN claim ON claim.report_id = report.id
            WHERE report.run_id = run.id
        ) AS claim_count
    """


def _run_item(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "question_text": str(row["question_text"]),
        "status": str(row["status"]),
        "trigger": str(row["trigger_name"]),
        "started_at": row["started_at"],
        "finished_at": row["finished_at"],
        "error_code": row["error_code"],
        "paper_count": int(row["paper_count"]),
        "evidence_count": int(row["evidence_count"]),
        "claim_count": int(row["claim_count"]),
    }


def _paper_from_sql() -> str:
    return """
        FROM paper
        WHERE paper.id IN (
            SELECT paper_source_record.paper_id
            FROM source_call
            JOIN source_record ON source_record.source_call_id = source_call.id
            JOIN paper_source_record
                ON paper_source_record.source_record_id = source_record.id
            WHERE source_call.run_id = ?
        )
    """


def _paper_item(
    connection: sqlite3.Connection,
    row: sqlite3.Row,
    run_id: str | None,
) -> dict[str, Any]:
    paper_id = str(row["id"])
    source_record_ids = _source_record_ids(connection, paper_id, run_id)
    return {
        "id": paper_id,
        "title": str(row["title"]),
        "year": row["year"],
        "venue": _blank_none(row["venue"]),
        "doi": _identifier(connection, paper_id, "doi"),
        "arxiv_id": _identifier(connection, paper_id, "arxiv_id"),
        "canonical_key": str(row["canonical_key"]),
        "open_access_status": _blank_none(row["open_access_status"]),
        "source_record_ids": source_record_ids,
        "relevance": _relevance(connection, source_record_ids, run_id),
    }


def _source_record_ids(
    connection: sqlite3.Connection,
    paper_id: str,
    run_id: str | None,
) -> list[str]:
    if run_id is None:
        rows = connection.execute(
            """
            SELECT source_record.id
            FROM paper_source_record
            JOIN source_record ON source_record.id = paper_source_record.source_record_id
            WHERE paper_source_record.paper_id = ?
            ORDER BY source_record.retrieved_at, source_record.id
            """,
            (paper_id,),
        ).fetchall()
    else:
        rows = connection.execute(
            """
            SELECT source_record.id
            FROM source_call
            JOIN source_record ON source_record.source_call_id = source_call.id
            JOIN paper_source_record
                ON paper_source_record.source_record_id = source_record.id
            WHERE source_call.run_id = ? AND paper_source_record.paper_id = ?
            ORDER BY source_record.retrieved_at, source_record.id
            """,
            (run_id, paper_id),
        ).fetchall()
    return [str(row["id"]) for row in rows]


def _identifier(connection: sqlite3.Connection, paper_id: str, identifier_type: str) -> str | None:
    row = connection.execute(
        """
        SELECT normalized_value FROM paper_identifier
        WHERE paper_id = ? AND type = ?
        ORDER BY is_primary DESC, normalized_value
        LIMIT 1
        """,
        (paper_id, identifier_type),
    ).fetchone()
    if row is None:
        return None
    return _blank_none(row["normalized_value"])


def _relevance(
    connection: sqlite3.Connection,
    source_record_ids: list[str],
    run_id: str | None,
) -> dict[str, Any]:
    empty = {
        "decision": "not_judged",
        "reason": None,
        "domain_scope": None,
        "answer_role": None,
    }
    if not source_record_ids:
        return empty
    placeholders = ", ".join("?" for _ in source_record_ids)
    params: list[Any] = list(source_record_ids)
    run_clause = ""
    if run_id is not None:
        run_clause = "AND run_id = ?"
        params.append(run_id)
    row = connection.execute(
        f"""
        SELECT decision, details_json
        FROM audit_event
        WHERE action = 'semantic_relevance'
          AND target_type = 'paper'
          AND target_id IN ({placeholders})
          {run_clause}
        ORDER BY created_at DESC, id DESC
        LIMIT 1
        """,
        params,
    ).fetchone()
    if row is None:
        return empty
    details = json.loads(str(row["details_json"] or "{}"))
    if not isinstance(details, dict):
        details = {}
    return {
        "decision": str(row["decision"]),
        "reason": _blank_none(details.get("reason")),
        "domain_scope": _blank_none(details.get("domain_scope")),
        "answer_role": _blank_none(details.get("answer_role")),
    }


def _latest_report_id(connection: sqlite3.Connection, run_id: str) -> str | None:
    row = connection.execute(
        """
        SELECT id FROM report
        WHERE run_id = ?
        ORDER BY version DESC
        LIMIT 1
        """,
        (run_id,),
    ).fetchone()
    if row is None:
        return None
    return str(row["id"])


def _claim_item(connection: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
    links = connection.execute(
        """
        SELECT evidence_span_id FROM claim_evidence
        WHERE claim_id = ?
        ORDER BY rank, evidence_span_id
        """,
        (str(row["id"]),),
    ).fetchall()
    return {
        "id": str(row["id"]),
        "report_id": str(row["report_id"]),
        "claim_text": str(row["claim_text"]),
        "claim_type": str(row["claim_type"]),
        "support_status": str(row["support_status"]),
        "confidence": float(row["confidence"]),
        "evidence_span_ids": [str(link["evidence_span_id"]) for link in links],
    }


def _blank_none(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
