"""One identity for a paper across DOI, arXiv ID, arXiv DOI, and OpenAlex ID.

Gold labels and retrieved papers often name the same work differently:
``doi:10.48550/arxiv.2312.10997`` versus ``arxiv:2312.10997``, or a DOI URL
versus the bare DOI. Comparison always goes through the alias set, so either
spelling matches. A single paper still has one primary key for storage and
for counting distinct papers.
"""

from __future__ import annotations

import re

from research_agent.mcp_servers.common import PaperCandidate

_DOI_PREFIXES = (
    "https://doi.org/",
    "http://doi.org/",
    "https://dx.doi.org/",
    "http://dx.doi.org/",
    "https://www.doi.org/",
    "http://www.doi.org/",
    "doi:",
)
_ARXIV_DOI = re.compile(r"^10\.48550/arxiv\.(?P<arxiv_id>.+)$", re.IGNORECASE)
_ARXIV_VERSION = re.compile(r"v\d+$", re.IGNORECASE)
_ARXIV_URL = re.compile(
    r"^https?://arxiv\.org/(?:abs|pdf)/(?P<arxiv_id>.+?)(?:\.pdf)?/?$",
    re.IGNORECASE,
)
_OPENALEX_URL = re.compile(
    r"^https?://openalex\.org/(?P<openalex_id>W\d+)/?$",
    re.IGNORECASE,
)


def normalize_doi(value: str) -> str:
    """Lower-case a DOI and strip a resolver prefix."""

    normalized = value.strip().lower()
    for prefix in _DOI_PREFIXES:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :]
            break
    return normalized


def strip_arxiv_version(value: str) -> str:
    """Drop a trailing ``vN`` from an arXiv identifier."""

    return _ARXIV_VERSION.sub("", value.strip())


def arxiv_id_from_doi(doi: str) -> str | None:
    """Return the arXiv id inside a DataCite arXiv DOI, if this DOI is one."""

    match = _ARXIV_DOI.fullmatch(normalize_doi(doi))
    if match is None:
        return None
    arxiv_id = strip_arxiv_version(match.group("arxiv_id"))
    return arxiv_id or None


def label_aliases(label: str) -> frozenset[str]:
    """Expand one stored or gold label into every equivalent spelling."""

    text = label.strip()
    if not text:
        return frozenset()

    arxiv_url = _ARXIV_URL.fullmatch(text)
    if arxiv_url is not None:
        return frozenset({f"arxiv:{strip_arxiv_version(arxiv_url.group('arxiv_id')).lower()}"})

    openalex_url = _OPENALEX_URL.fullmatch(text)
    if openalex_url is not None:
        return frozenset({f"openalex:{openalex_url.group('openalex_id').upper()}"})

    lowered = text.lower()
    if lowered.startswith("arxiv:"):
        arxiv_id = strip_arxiv_version(lowered.removeprefix("arxiv:"))
        return frozenset({f"arxiv:{arxiv_id}"}) if arxiv_id else frozenset()

    if lowered.startswith("openalex:"):
        openalex_id = lowered.removeprefix("openalex:").strip().upper()
        return frozenset({f"openalex:{openalex_id}"}) if openalex_id else frozenset()

    doi_text = text
    if lowered.startswith("doi:"):
        doi_text = text.split(":", 1)[1]
    doi = normalize_doi(doi_text)
    arxiv_from_doi = arxiv_id_from_doi(doi)
    if arxiv_from_doi is not None:
        return frozenset({f"arxiv:{arxiv_from_doi}"})
    if doi:
        return frozenset({f"doi:{doi}"})
    return frozenset({lowered})


def identity_aliases(paper: PaperCandidate) -> frozenset[str]:
    """Every label that should match this candidate."""

    aliases: set[str] = set()
    if paper.doi:
        aliases.update(label_aliases(f"doi:{paper.doi}"))
    if paper.source == "arxiv" and paper.source_record_id.strip():
        aliases.update(label_aliases(f"arxiv:{paper.source_record_id}"))
    elif paper.source == "openalex" and paper.source_record_id.strip():
        aliases.update(label_aliases(f"openalex:{paper.source_record_id}"))
    if not aliases:
        aliases.add(f"{paper.source}:{paper.source_record_id.strip().lower()}")
    return frozenset(aliases)


def primary_identity(paper: PaperCandidate) -> str:
    """The one key used to store and count this paper.

    A journal DOI wins over the arXiv id of the same record. An arXiv DOI
    does not appear as a ``doi:`` alias; it is already the arXiv id, so two
    sources that only share that id still land on one key.
    """

    aliases = identity_aliases(paper)
    for prefix in ("doi:", "arxiv:", "openalex:"):
        matches = sorted(alias for alias in aliases if alias.startswith(prefix))
        if matches:
            return matches[0]
    return min(aliases)


def labels_match(left: str, right: str) -> bool:
    """Whether two labels name the same paper."""

    return bool(label_aliases(left) & label_aliases(right))


def matched_gold_keys(
    retrieved_keys: set[str],
    gold_keys: set[str],
    *,
    extra_aliases: set[str] | None = None,
) -> set[str]:
    """Gold labels that share an alias with a retrieved paper.

    ``extra_aliases`` carries identifiers that are not the paper's primary
    key, such as an OpenAlex ID on a paper counted under its DOI.
    """

    pool: set[str] = set(extra_aliases or ())
    for key in retrieved_keys:
        pool.update(label_aliases(key))
    return {gold for gold in gold_keys if label_aliases(gold) & pool}
