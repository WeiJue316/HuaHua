"""Ordered candidate lists for evaluation.

ADR-0015 requires every system to emit one list of at most K papers.
Multi-source systems rotate through sources: every source's first hit, then
every source's second hit, and so on. A later copy of a paper already placed
is skipped and does not pull the next hit of that source forward.
"""

from __future__ import annotations

from collections.abc import Sequence


def interleave_by_source(groups: Sequence[Sequence[str]]) -> list[str]:
    """Rotate across source lists, keeping each source's own order."""

    seen: set[str] = set()
    merged: list[str] = []
    depth = max((len(group) for group in groups), default=0)
    for index in range(depth):
        for group in groups:
            if index >= len(group):
                continue
            key = group[index]
            if key in seen:
                continue
            seen.add(key)
            merged.append(key)
    return merged


def candidate_list(
    ranked_keys: Sequence[str],
    *,
    dropped: set[str] | None = None,
    k: int,
) -> list[str]:
    """Drop filtered papers without reordering, then keep at most K."""

    if k < 0:
        raise ValueError("k must not be negative")
    denied = dropped or set()
    surviving = [key for key in ranked_keys if key not in denied]
    return surviving[:k]
