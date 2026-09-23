"""Shared MCP-facing data models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Author(BaseModel):
    """Normalized author information."""

    name: str
    orcid: str | None = None
    source_author_id: str | None = None


class OpenAccessInfo(BaseModel):
    """Open-access resolution result."""

    is_oa: bool
    status: str
    license: str | None = None
    url: str | None = None


class PaperCandidate(BaseModel):
    """Source-neutral paper candidate returned by an MCP server."""

    source: str
    source_record_id: str
    source_version: str | None = None
    title: str
    abstract: str | None = None
    authors: list[Author] = Field(default_factory=list)
    year: int | None = None
    published_at: str | None = None
    updated_at: str | None = None
    venue: str | None = None
    categories: list[str] = Field(default_factory=list)
    doi: str | None = None
    landing_url: str
    pdf_url: str | None = None
    open_access: OpenAccessInfo
    raw: dict[str, Any] = Field(default_factory=dict)