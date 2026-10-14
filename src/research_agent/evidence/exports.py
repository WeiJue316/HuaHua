"""JSON, CSV, and BibTeX views of a stored report.

Missing BibTeX fields use a stable placeholder. A missing DOI is omitted.
"""

from __future__ import annotations

import csv
import io
import json
import re
from collections.abc import Sequence
from dataclasses import dataclass

EVIDENCE_TABLE_COLUMNS = (
    "claim_id",
    "claim_text",
    "support_status",
    "paper_id",
    "paper_title",
    "doi",
    "arxiv_id",
    "file_sha256",
    "evidence_id",
    "quote",
    "locator",
    "evidence_level",
    "extraction_method",
    "confidence",
    "source",
    "retrieved_at",
)

_BIBTEX_ESCAPES = str.maketrans(
    {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
    }
)


@dataclass(frozen=True)
class EvidenceExportRow:
    """One claim-to-evidence row in the export table."""

    claim_id: str
    claim_text: str
    support_status: str
    paper_id: str
    paper_title: str
    doi: str
    arxiv_id: str
    file_sha256: str
    evidence_id: str
    quote: str
    locator: str
    evidence_level: str
    extraction_method: str
    confidence: float | None
    source: str
    retrieved_at: str

    def as_dict(self) -> dict[str, object]:
        return {
            "claim_id": self.claim_id,
            "claim_text": self.claim_text,
            "support_status": self.support_status,
            "paper_id": self.paper_id,
            "paper_title": self.paper_title,
            "doi": self.doi,
            "arxiv_id": self.arxiv_id,
            "file_sha256": self.file_sha256,
            "evidence_id": self.evidence_id,
            "quote": self.quote,
            "locator": self.locator,
            "evidence_level": self.evidence_level,
            "extraction_method": self.extraction_method,
            "confidence": self.confidence,
            "source": self.source,
            "retrieved_at": self.retrieved_at,
        }


@dataclass(frozen=True)
class BibliographyEntry:
    """One paper cited by a report."""

    paper_id: str
    title: str
    authors: tuple[str, ...]
    year: str
    venue: str
    doi: str
    arxiv_id: str


def render_evidence_json(rows: Sequence[EvidenceExportRow]) -> str:
    """Serialize the evidence table as JSON."""

    payload = [row.as_dict() for row in rows]
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def render_evidence_csv(rows: Sequence[EvidenceExportRow]) -> str:
    """Serialize the evidence table as CSV."""

    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=EVIDENCE_TABLE_COLUMNS,
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        values = row.as_dict()
        confidence = values["confidence"]
        values["confidence"] = "" if confidence is None else format(confidence, ".10g")
        writer.writerow(values)
    return buffer.getvalue()


def render_bibtex(entries: Sequence[BibliographyEntry]) -> str:
    """Serialize cited papers as BibTeX."""

    blocks = [_bibtex_entry(entry) for entry in entries]
    if not blocks:
        return ""
    return "\n\n".join(blocks) + "\n"


def _bibtex_entry(entry: BibliographyEntry) -> str:
    fields = [
        ("title", entry.title or "unknown"),
        ("author", " and ".join(entry.authors) if entry.authors else "unknown"),
        ("year", entry.year or "unknown"),
    ]
    if entry.venue:
        fields.append(("journal", entry.venue))
    if entry.doi:
        fields.append(("doi", entry.doi))
    if entry.arxiv_id:
        fields.append(("eprint", entry.arxiv_id))
    body = ",\n".join(
        f"  {name} = {{{_escape_bibtex(value)}}}" for name, value in fields
    )
    return f"@article{{{_bibtex_key(entry)},\n{body},\n}}"


def _bibtex_key(entry: BibliographyEntry) -> str:
    if entry.doi:
        return "doi_" + _slug(entry.doi)
    if entry.arxiv_id:
        return "arxiv_" + _slug(entry.arxiv_id)
    return "paper_" + _slug(entry.paper_id)


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return cleaned or "unknown"


def _escape_bibtex(value: str) -> str:
    return value.translate(_BIBTEX_ESCAPES)
