"""Immutable file archiving helpers."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def archive_downloaded_file(
    *,
    source_path: Path,
    archive_dir: Path,
    sha256: str,
    suffix: str,
) -> Path:
    """Move a downloaded file into its content-addressed archive path."""

    if not sha256 or "/" in sha256 or "\\" in sha256:
        raise ValueError("sha256 must be a non-empty path-safe value")
    archive_dir.mkdir(parents=True, exist_ok=True)
    target_path = archive_dir / f"{sha256}{suffix}"
    if target_path.exists():
        source_path.unlink(missing_ok=True)
        return target_path
    try:
        os.replace(source_path, target_path)
    except OSError:
        shutil.move(str(source_path), str(target_path))
    return target_path
