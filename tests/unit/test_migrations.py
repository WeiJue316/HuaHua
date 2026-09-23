from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from research_agent.storage.migrations import (
    MigrationError,
    apply_migrations,
    connect_database,
    get_schema_version,
)


def _seed_source_call(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        INSERT INTO project (id, name, domain, status, created_at, updated_at, settings_json)
        VALUES ('p1', 'project', 'cs_ai', 'active', '2026-01-01T00:00:00Z',
                '2026-01-01T00:00:00Z', '{}')
        """
    )
    conn.execute(
        """
        INSERT INTO research_question
            (id, project_id, question_text, scope_json, version, created_at)
        VALUES ('q1', 'p1', 'question', '{}', 1, '2026-01-01T00:00:00Z')
        """
    )
    conn.execute(
        """
        INSERT INTO run
            (id, project_id, question_id, status, "trigger", config_hash, config_json,
             system_version)
        VALUES ('r1', 'p1', 'q1', 'CREATED', 'cli', 'cfg', '{}', 'test')
        """
    )
    conn.execute(
        """
        INSERT INTO source_call
            (id, run_id, source, tool_name, request_hash, request_json, status, retry_count,
             started_at)
        VALUES ('sc1', 'r1', 'arxiv', 'arxiv_search_papers', 'req', '{}', 'success', 0,
                '2026-01-01T00:00:00Z')
        """
    )
    conn.execute(
        """
        INSERT INTO source_record
            (id, source_call_id, source, source_record_id, api_endpoint, raw_json,
             mapping_version, retrieved_at, content_hash)
        VALUES ('sr1', 'sc1', 'arxiv', '2407.18940', 'https://export.arxiv.org/api/query',
                '{}', '1.0', '2026-01-01T00:00:00Z', 'hash')
        """
    )


def test_apply_migrations_creates_schema(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"

    version = apply_migrations(db_path)

    assert version == 1
    with connect_database(db_path) as conn:
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        assert {
            "schema_migrations",
            "project",
            "paper",
            "source_record",
            "evidence_span",
            "file",
            "document",
            "paper_fts",
            "evidence_fts",
            "note_fts",
        }.issubset(tables)
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert get_schema_version(conn) == version


def test_apply_migrations_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"

    assert apply_migrations(db_path) == 1
    assert apply_migrations(db_path) == 1

    with connect_database(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
        assert count == 1


def test_source_record_and_audit_event_are_immutable(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)

    with connect_database(db_path) as conn:
        _seed_source_call(conn)
        conn.execute(
            """
            INSERT INTO audit_event (id, actor, action, target_type, created_at)
            VALUES ('a1', 'system', 'seed', 'source_record', '2026-01-01T00:00:00Z')
            """
        )

        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE source_record SET raw_json = '{}' WHERE id = 'sr1'")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("DELETE FROM source_record WHERE id = 'sr1'")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE audit_event SET action = 'changed' WHERE id = 'a1'")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("DELETE FROM audit_event WHERE id = 'a1'")


def test_fts_index_tracks_paper_changes(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    apply_migrations(db_path)

    with connect_database(db_path) as conn:
        conn.execute(
            """
            INSERT INTO paper
                (id, canonical_key, title, title_normalized, created_at, updated_at)
            VALUES ('paper1', 'doi:10.1/example', 'Traceable retrieval', 'traceable retrieval',
                    '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')
            """
        )
        assert conn.execute(
            "SELECT COUNT(*) FROM paper_fts WHERE paper_fts MATCH 'traceable'"
        ).fetchone()[0] == 1

        conn.execute(
            """
            UPDATE paper
            SET title = 'Evidence chains', title_normalized = 'evidence chains',
                updated_at = '2026-01-02T00:00:00Z'
            WHERE id = 'paper1'
            """
        )
        assert conn.execute(
            "SELECT COUNT(*) FROM paper_fts WHERE paper_fts MATCH 'evidence'"
        ).fetchone()[0] == 1
        assert conn.execute(
            "SELECT COUNT(*) FROM paper_fts WHERE paper_fts MATCH 'traceable'"
        ).fetchone()[0] == 0


def test_migration_hash_mismatch_is_rejected(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    migration = migrations_dir / "0001_test.sql"
    migration.write_text("CREATE TABLE sample (id TEXT PRIMARY KEY);\n", encoding="utf-8")

    assert apply_migrations(db_path, migrations_dir=migrations_dir) == 1

    migration.write_text(
        "CREATE TABLE sample (id TEXT PRIMARY KEY, value TEXT);\n", encoding="utf-8"
    )
    with pytest.raises(MigrationError, match="hash"):
        apply_migrations(db_path, migrations_dir=migrations_dir)


def test_unversioned_nonempty_database_is_rejected(tmp_path: Path) -> None:
    db_path = tmp_path / "research_agent.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE existing_data (id INTEGER PRIMARY KEY)")

    with pytest.raises(MigrationError, match="unversioned"):
        apply_migrations(db_path)