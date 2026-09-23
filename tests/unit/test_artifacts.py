from __future__ import annotations

from pathlib import Path

from research_agent.storage.artifacts import archive_downloaded_file


def test_archive_downloaded_file_moves_to_hash_path(tmp_path: Path) -> None:
    source_path = tmp_path / "download.part"
    source_path.write_bytes(b"%PDF-1.4\nfixture\n")
    archive_dir = tmp_path / "papers"

    archived = archive_downloaded_file(
        source_path=source_path,
        archive_dir=archive_dir,
        sha256="abc123",
        suffix=".pdf",
    )

    assert archived == archive_dir / "abc123.pdf"
    assert archived.read_bytes() == b"%PDF-1.4\nfixture\n"
    assert not source_path.exists()


def test_archive_downloaded_file_reuses_existing_content(tmp_path: Path) -> None:
    source_path = tmp_path / "download.part"
    source_path.write_bytes(b"same")
    archive_dir = tmp_path / "papers"
    archive_dir.mkdir()
    existing = archive_dir / "samehash.pdf"
    existing.write_bytes(b"existing")

    archived = archive_downloaded_file(
        source_path=source_path,
        archive_dir=archive_dir,
        sha256="samehash",
        suffix=".pdf",
    )

    assert archived == existing
    assert archived.read_bytes() == b"existing"
    assert not source_path.exists()
