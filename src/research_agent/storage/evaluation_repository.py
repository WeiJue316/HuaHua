"""Persistence operations for evaluation runs."""

from __future__ import annotations

import sqlite3
from typing import Any
from uuid import uuid4

from research_agent.storage.repository import json_text, utc_now


class EvaluationRepository:
    """Repository for EvaluationRun, EvaluationCase and EvaluationResult."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def create_run(
        self,
        *,
        dataset_version: str,
        dataset_hash: str,
        system_version: str,
        config: Any,
    ) -> str:
        evaluation_run_id = str(uuid4())
        self.connection.execute(
            """
            INSERT INTO evaluation_run
                (id, dataset_version, dataset_hash, system_version, config_json, status)
            VALUES (?, ?, ?, ?, ?, 'created')
            """,
            (
                evaluation_run_id,
                dataset_version,
                dataset_hash,
                system_version,
                json_text(config),
            ),
        )
        return evaluation_run_id

    def update_run(
        self,
        *,
        evaluation_run_id: str,
        status: str,
        summary: Any | None = None,
        finished_at: str | None = None,
    ) -> None:
        started_at = utc_now() if status == "running" else None
        if summary is None:
            self.connection.execute(
                """
                UPDATE evaluation_run
                SET status = COALESCE(?, status),
                    started_at = COALESCE(?, started_at),
                    finished_at = COALESCE(?, finished_at)
                WHERE id = ?
                """,
                (status, started_at, finished_at, evaluation_run_id),
            )
        else:
            self.connection.execute(
                """
                UPDATE evaluation_run
                SET status = ?,
                    started_at = COALESCE(?, started_at),
                    finished_at = COALESCE(?, finished_at),
                    summary_json = ?
                WHERE id = ?
                """,
                (status, started_at, finished_at, json_text(summary), evaluation_run_id),
            )

    def create_case(
        self,
        *,
        evaluation_run_id: str,
        question_id: str,
        system_id: str,
        run_number: int,
    ) -> str:
        case_id = str(uuid4())
        self.connection.execute(
            """
            INSERT INTO evaluation_case
                (id, evaluation_run_id, question_id, system_id, run_number, status,
                 created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
            """,
            (
                case_id,
                evaluation_run_id,
                question_id,
                system_id,
                run_number,
                utc_now(),
            ),
        )
        return case_id

    def update_case(
        self,
        *,
        case_id: str,
        status: str,
        research_run_id: str | None = None,
        metrics: Any | None = None,
        error_code: str | None = None,
    ) -> None:
        self.connection.execute(
            """
            UPDATE evaluation_case
            SET status = ?,
                research_run_id = COALESCE(?, research_run_id),
                metrics_json = COALESCE(?, metrics_json),
                error_code = ?
            WHERE id = ?
            """,
            (
                status,
                research_run_id,
                json_text(metrics) if metrics is not None else None,
                error_code,
                case_id,
            ),
        )

    def record_result(
        self,
        *,
        case_id: str,
        metric_name: str,
        metric_value: float,
        metric_unit: str | None = None,
        details: Any | None = None,
    ) -> str:
        result_id = str(uuid4())
        self.connection.execute(
            """
            INSERT INTO evaluation_result
                (id, evaluation_case_id, metric_name, metric_value, metric_unit,
                 details_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result_id,
                case_id,
                metric_name,
                metric_value,
                metric_unit,
                json_text(details) if details is not None else None,
                utc_now(),
            ),
        )
        return result_id
