"""Local read-only HTTP API for the evidence-chain viewer."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from research_agent.interfaces import queries
from research_agent.storage.migrations import connect_database

API_VERSION = "v1"
LOCAL_API_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
LOCAL_FRONTEND_ORIGINS = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
)


class ApiError(Exception):
    """A contract error with a stable code and a short message."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message


class Utf8JSONResponse(JSONResponse):
    """JSON responses that name the UTF-8 charset."""

    media_type = "application/json; charset=utf-8"


def create_app(db_path: Path) -> FastAPI:
    """Build the read-only API for one SQLite database."""

    app = FastAPI(title="research-agent", default_response_class=Utf8JSONResponse)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(LOCAL_FRONTEND_ORIGINS),
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["Accept", "Content-Type"],
    )
    app.add_exception_handler(ApiError, _api_error)
    app.add_exception_handler(RequestValidationError, _invalid_request)
    app.add_exception_handler(Exception, _internal_error)

    @app.get("/v1/runs")
    def read_runs(limit: int = 20, offset: int = 0) -> dict[str, Any]:
        _check_page(limit, offset)
        items, total = _call(
            db_path,
            lambda conn: queries.list_runs(conn, limit=limit, offset=offset),
        )
        return _page(items, limit, offset, total)

    @app.get("/v1/runs/{run_id}")
    def read_run(run_id: str) -> dict[str, Any]:
        row = _call(db_path, lambda conn: queries.get_run(conn, run_id))
        if row is None:
            raise ApiError(404, "not_found", "run not found")
        return _body(row)

    @app.get("/v1/runs/{run_id}/steps")
    def read_steps(run_id: str) -> dict[str, Any]:
        rows = _call(db_path, lambda conn: queries.list_steps(conn, run_id))
        if rows is None:
            raise ApiError(404, "not_found", "run not found")
        return _body({"items": rows})

    @app.get("/v1/runs/{run_id}/sources")
    def read_sources(run_id: str) -> dict[str, Any]:
        rows = _call(db_path, lambda conn: queries.list_sources(conn, run_id))
        if rows is None:
            raise ApiError(404, "not_found", "run not found")
        return _body({"items": rows})

    @app.get("/v1/runs/{run_id}/papers")
    def read_papers(run_id: str, limit: int = 20, offset: int = 0) -> dict[str, Any]:
        _check_page(limit, offset)
        found = _call(
            db_path,
            lambda conn: queries.list_papers(conn, run_id, limit=limit, offset=offset),
        )
        if found is None:
            raise ApiError(404, "not_found", "run not found")
        items, total = found
        return _page(items, limit, offset, total)

    @app.get("/v1/papers/{paper_id}")
    def read_paper(paper_id: str) -> dict[str, Any]:
        row = _call(db_path, lambda conn: queries.get_paper(conn, paper_id))
        if row is None:
            raise ApiError(404, "not_found", "paper not found")
        return _body(row)

    @app.get("/v1/runs/{run_id}/claims")
    def read_claims(run_id: str, limit: int = 20, offset: int = 0) -> dict[str, Any]:
        _check_page(limit, offset)
        found = _call(
            db_path,
            lambda conn: queries.list_claims(conn, run_id, limit=limit, offset=offset),
        )
        if found is None:
            raise ApiError(404, "not_found", "run not found")
        items, total = found
        return _page(items, limit, offset, total)

    @app.get("/v1/claims/{claim_id}")
    def read_claim(claim_id: str) -> dict[str, Any]:
        row = _call(db_path, lambda conn: queries.get_claim(conn, claim_id))
        if row is None:
            raise ApiError(404, "not_found", "claim not found")
        return _body(row)

    @app.get("/v1/evidence-spans/{evidence_span_id}")
    def read_evidence_span(evidence_span_id: str) -> dict[str, Any]:
        row = _call(db_path, lambda conn: queries.get_evidence_span(conn, evidence_span_id))
        if row is None:
            raise ApiError(404, "not_found", "evidence span not found")
        return _body(row)

    @app.get("/v1/source-records/{source_record_id}")
    def read_source_record(source_record_id: str) -> dict[str, Any]:
        row = _call(db_path, lambda conn: queries.get_source_record(conn, source_record_id))
        if row is None:
            raise ApiError(404, "not_found", "source record not found")
        return _body(row)

    @app.get("/v1/files/{file_id}")
    def read_file(file_id: str) -> dict[str, Any]:
        row = _call(db_path, lambda conn: queries.get_file(conn, file_id))
        if row is None:
            raise ApiError(404, "not_found", "file not found")
        return _body(row)

    @app.get("/v1/documents/{document_id}")
    def read_document(document_id: str) -> dict[str, Any]:
        row = _call(db_path, lambda conn: queries.get_document(conn, document_id))
        if row is None:
            raise ApiError(404, "not_found", "document not found")
        return _body(row)

    return app


def serve_local_api(db_path: Path, *, host: str = "127.0.0.1", port: int = 8765) -> None:
    """Listen on the local machine only."""

    if host not in LOCAL_API_HOSTS:
        raise ValueError("API host must stay on the local machine")
    import uvicorn

    uvicorn.run(create_app(db_path), host=host, port=port)


def _check_page(limit: int, offset: int) -> None:
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1 or limit > 100:
        raise ApiError(400, "invalid_request", "invalid request")
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ApiError(400, "invalid_request", "invalid request")


def _call[T](db_path: Path, reader: Callable[[Any], T]) -> T:
    with connect_database(db_path) as connection:
        return reader(connection)


def _body(payload: dict[str, Any]) -> dict[str, Any]:
    return {"api_version": API_VERSION, **payload}


def _page(items: list[dict[str, Any]], limit: int, offset: int, total: int) -> dict[str, Any]:
    return _body({"items": items, "limit": limit, "offset": offset, "total": total})


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    return Utf8JSONResponse(
        status_code=status_code,
        content={"api_version": API_VERSION, "error": {"code": code, "message": message}},
    )


def _api_error(_request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, ApiError):
        return _error(500, "internal_error", "internal error")
    return _error(exc.status_code, exc.code, exc.message)


def _invalid_request(_request: Request, _exc: Exception) -> JSONResponse:
    return _error(400, "invalid_request", "invalid request")


def _internal_error(_request: Request, _exc: Exception) -> JSONResponse:
    return _error(500, "internal_error", "internal error")
