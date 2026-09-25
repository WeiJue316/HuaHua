"""Evaluation system configurations.

The identifiers follow docs/evaluation.md. Only the configurations the current
pipeline can express are marked implemented; the rest are listed so an
evaluation run fails loudly instead of silently measuring the wrong system.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

ALL_SOURCES = ("arxiv", "openalex", "crossref", "semantic_scholar", "dblp")


def restrict_sources(
    requested: Sequence[str],
    allowed: Sequence[str] | None,
) -> tuple[str, ...]:
    """Intersect requested sources with an optional run-level allowlist."""

    if allowed is None:
        return tuple(requested)
    allowed_set = set(allowed)
    return tuple(source for source in requested if source in allowed_set)


@dataclass(frozen=True)
class SystemConfig:
    """One configuration under evaluation."""

    system_id: str
    description: str
    sources: tuple[str, ...] | None
    relevance_filter: bool
    citation_constraint: bool = True
    implemented: bool = True

    def __post_init__(self) -> None:
        if not self.system_id:
            raise ValueError("system_id must not be empty")


SYSTEMS: dict[str, SystemConfig] = {
    "B1": SystemConfig(
        system_id="B1",
        description="单源 MCP（OpenAlex）+ 相同 Agent Core",
        sources=("openalex",),
        relevance_filter=True,
    ),
    "B3": SystemConfig(
        system_id="B3",
        description="完整系统：证据链 + 联邦路由 + Plan-and-Execute",
        sources=None,
        relevance_filter=True,
    ),
    "A3": SystemConfig(
        system_id="A3",
        description="去路由器：无条件查询全部源站",
        sources=ALL_SOURCES,
        relevance_filter=True,
    ),
    "A6": SystemConfig(
        system_id="A6",
        description="去语义相关性过滤",
        sources=None,
        relevance_filter=False,
    ),
    "B0": SystemConfig(
        system_id="B0",
        description="BM25/关键词检索 + 单次 LLM 总结",
        sources=(),
        relevance_filter=False,
    ),
    "B2": SystemConfig(
        system_id="B2",
        description="纯 ReAct：受限 search/finish 循环，无 Plan 和证据链",
        sources=None,
        relevance_filter=False,
    ),
    "A1": SystemConfig(
        system_id="A1",
        description="去证据链：直接生成 unsupported Claim，不创建 Evidence Span",
        sources=None,
        relevance_filter=True,
    ),
    "A2": SystemConfig(
        system_id="A2",
        description="去规划器：固定单查询流水线",
        sources=None,
        relevance_filter=True,
    ),
    "A4": SystemConfig(
        system_id="A4",
        description="无引用约束：同一综合，不把悬空引用降为 unsupported",
        sources=None,
        relevance_filter=True,
        citation_constraint=False,
    ),
}


def get_system(system_id: str) -> SystemConfig:
    """Return the configuration for an identifier, rejecting unknown ones."""

    try:
        config = SYSTEMS[system_id]
    except KeyError as exc:
        raise KeyError(
            f"unknown system {system_id!r}; known: {', '.join(sorted(SYSTEMS))}"
        ) from exc
    if not config.implemented:
        raise NotImplementedError(
            f"system {system_id} is declared in docs/evaluation.md but the "
            "pipeline cannot express it yet"
        )
    return config