"""Deterministic BM25 retrieval over a frozen local paper corpus."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


def _singularize(token: str) -> str:
    """Fold only unambiguous English plurals for lexical matching."""

    if len(token) <= 4:
        return token
    if token.endswith("ies"):
        return token[:-3] + "y"
    if token.endswith(("ss", "us", "is", "as")):
        return token
    if token.endswith("s"):
        return token[:-1]
    return token


def tokenize(value: str) -> list[str]:
    """Return lowercase terms, splitting hyphens and underscores."""

    flattened = value.lower().replace("-", " ").replace("_", " ")
    return [
        _singularize(token)
        for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9]*", flattened)
    ]


@dataclass(frozen=True)
class Bm25Document:
    """One searchable paper in the frozen B0 corpus."""

    paper_key: str
    title: str
    abstract: str = ""
    year: int | None = None
    doi: str | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Bm25Document:
        paper_key = raw.get("paper_key")
        title = raw.get("title")
        abstract = raw.get("abstract") or ""
        year = raw.get("year")
        doi = raw.get("doi")
        if not isinstance(paper_key, str) or not paper_key:
            raise ValueError("corpus row requires a non-empty paper_key")
        if not isinstance(title, str) or not title:
            raise ValueError(f"{paper_key} requires a non-empty title")
        if not isinstance(abstract, str):
            raise ValueError(f"{paper_key} abstract must be a string")
        if year is not None and not isinstance(year, int):
            raise ValueError(f"{paper_key} year must be an integer or null")
        if doi is not None and not isinstance(doi, str):
            raise ValueError(f"{paper_key} doi must be a string or null")
        return cls(
            paper_key=paper_key,
            title=title,
            abstract=abstract,
            year=year,
            doi=doi,
        )

    def searchable_text(self) -> str:
        return f"{self.title} {self.abstract}".strip()


@dataclass(frozen=True)
class Bm25Hit:
    """One scored document returned by BM25 search."""

    document: Bm25Document
    score: float


class Bm25Index:
    """In-memory BM25 index with stable ordering and a reproducible hash."""

    def __init__(
        self,
        documents: Sequence[Bm25Document],
        *,
        k1: float = 1.2,
        b: float = 0.75,
    ) -> None:
        if k1 <= 0:
            raise ValueError("k1 must be positive")
        if not 0 <= b <= 1:
            raise ValueError("b must be between 0 and 1")
        if not documents:
            raise ValueError("BM25 corpus must not be empty")
        ordered = tuple(sorted(documents, key=lambda document: document.paper_key))
        keys = [document.paper_key for document in ordered]
        if len(keys) != len(set(keys)):
            raise ValueError("BM25 corpus contains duplicate paper_key values")

        self.documents = ordered
        self.k1 = k1
        self.b = b
        self._tokens = [tokenize(document.searchable_text()) for document in ordered]
        self._lengths = [len(tokens) for tokens in self._tokens]
        self._average_length = sum(self._lengths) / len(self._lengths)
        postings: dict[str, dict[int, int]] = defaultdict(dict)
        for index, tokens in enumerate(self._tokens):
            term_counts: dict[str, int] = defaultdict(int)
            for token in tokens:
                term_counts[token] += 1
            for term, count in term_counts.items():
                postings[term][index] = count
        self._postings = dict(postings)
        self._document_frequency = {
            term: len(indexes) for term, indexes in self._postings.items()
        }
        count = len(ordered)
        self._idf = {
            term: math.log(
                1.0
                + (count - document_frequency + 0.5)
                / (document_frequency + 0.5)
            )
            for term, document_frequency in self._document_frequency.items()
        }
        self.corpus_hash = self._compute_hash()

    @classmethod
    def from_jsonl(cls, path: Path) -> Bm25Index:
        documents: list[Bm25Document] = []
        seen: set[str] = set()
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"invalid corpus JSON on line {line_number}: {exc}"
                ) from exc
            if not isinstance(raw, dict):
                raise ValueError(f"corpus line {line_number} must be an object")
            document = Bm25Document.from_dict(raw)
            if document.paper_key in seen:
                raise ValueError(
                    f"duplicate paper_key on line {line_number}: "
                    f"{document.paper_key}"
                )
            seen.add(document.paper_key)
            documents.append(document)
        return cls(documents)

    def search(self, query: str, *, top_k: int = 10) -> list[Bm25Hit]:
        """Return the highest-scoring documents for a lexical query."""

        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        query_terms = set(tokenize(query))
        if not query_terms:
            return []
        scores: dict[int, float] = defaultdict(float)
        for term in query_terms:
            postings = self._postings.get(term)
            if not postings:
                continue
            idf = self._idf[term]
            for document_index, term_frequency in postings.items():
                document_length = self._lengths[document_index]
                denominator = term_frequency + self.k1 * (
                    1.0
                    - self.b
                    + self.b * document_length / self._average_length
                )
                scores[document_index] += idf * (
                    term_frequency * (self.k1 + 1.0) / denominator
                )
        ranked = sorted(
            scores.items(),
            key=lambda item: (-item[1], self.documents[item[0]].paper_key),
        )
        return [
            Bm25Hit(document=self.documents[index], score=score)
            for index, score in ranked[:top_k]
        ]

    def _compute_hash(self) -> str:
        payload = json.dumps(
            [asdict(document) for document in self.documents],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()