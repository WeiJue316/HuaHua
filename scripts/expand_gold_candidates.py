#!/usr/bin/env python3
"""从引用图扩展金标候选，供人工复核。

用法：

    # 为某一道题扩展候选（种子取该题已有的 gold 论文）
    uv run python scripts/expand_gold_candidates.py --question csai_007

    # 为全部题目扩展
    uv run python scripts/expand_gold_candidates.py --all

    # 不依赖已有数据集，直接给种子 DOI 和问题
    uv run python scripts/expand_gold_candidates.py \
        --seed 10.18653/v1/2023.emnlp-main.585 \
        --question-text "What methods are used for query expansion..." \
        --years 2022 2026

为什么要用引用图：

    实测发现 pilot 每题只标了 2 篇 gold，而系统在 K=20 下会保留 30 篇以上候选。
    这时 precision 是 1/31，不可解释——没命中的论文里可能有很多同样相关，只是
    没有被标进 gold。金标是"抽样"而不是"全集"，指标就没有意义。

    引用图扩展的好处是：**候选来自独立的信号**（谁引用谁），而不是系统自己的
    检索结果。如果直接用系统返回的论文当金标，就变成"用系统自己的输出定义
    正确答案"的循环论证。

两个方向：

    · 反向引用（谁引用了种子）——通常是后续工作，方法更新
    · 正向引用（种子引用了谁）——通常是基础工作，方法更早

    脚本两个方向都取，合并去重后按"主题重合度 + 被引数"排序输出。
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from research_agent.evaluator.dataset import EvaluationQuestion, load_questions  # noqa: E402
from research_agent.evaluator.pilot_seed import match_terms  # noqa: E402
from research_agent.llm.deepseek import DeepSeekGateway  # noqa: E402
from research_agent.mcp_servers.cache import (  # noqa: E402
    DEFAULT_TTL_SECONDS,
    ResponseCache,
)
from research_agent.mcp_servers.common import PaperCandidate  # noqa: E402
from research_agent.mcp_servers.openalex.client import OpenAlexClient  # noqa: E402
from research_agent.router.registry import build_openalex_client  # noqa: E402

DEFAULT_DATASET = ROOT / "evaluation" / "datasets" / "pilot_questions.v1.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "evaluation" / "review"


def paper_key(paper: PaperCandidate) -> str:
    """论文的稳定标识，与数据集里的 paper_key 格式一致。"""

    if paper.doi:
        return f"doi:{paper.doi.lower()}"
    return f"openalex:{paper.source_record_id}"


@dataclass(frozen=True)
class Candidate:
    """一个待人工判定的候选论文。"""

    paper: PaperCandidate
    relation: str  # 与种子的关系：谁引用了谁
    seed_key: str  # 通过哪个种子找到的
    topic_overlap: int  # 与问题词的命中共数，用于排序

    @property
    def key(self) -> str:
        return paper_key(self.paper)


def _relevance_terms(question: EvaluationQuestion) -> set[str]:
    """问题的主题词，用于给候选排序。

    这里刻意用 match_terms（保留通用词）而不是 pilot_seed 的 _content_terms：
    排序只是给人工复核排个先后，宁可多留一些噪声，也不要因为过度过滤把
    好候选排到后面。
    """

    parts = [question.question, *question.subquestions]
    terms: set[str] = set()
    for part in parts:
        terms |= match_terms(part)
    return terms


def _topic_overlap(paper: PaperCandidate, terms: set[str]) -> int:
    """候选与问题主题的词重合数。"""

    text = f"{paper.title} {paper.abstract or ''}".lower()
    words = set(text.replace("-", " ").replace("_", " ").split())
    return len(terms & words)


def _in_year_range(paper: PaperCandidate, years: tuple[int, int] | None) -> bool:
    """年份过滤。年份未知的保留，交给人工判断。"""

    if years is None or paper.year is None:
        return True
    return years[0] <= paper.year <= years[1]


async def collect_for_question(
    client: OpenAlexClient,
    *,
    question: EvaluationQuestion,
    years: tuple[int, int] | None,
    per_direction: int,
) -> tuple[list[Candidate], list[str]]:
    """对一道题：沿引用图两个方向扩展，合并去重后排序。"""

    terms = _relevance_terms(question)
    known = {key.lower() for key in question.gold_papers}
    found: dict[str, Candidate] = {}
    failures: list[str] = []

    for seed in question.gold_papers:
        doi = seed.removeprefix("doi:")
        # get_citations / get_references 只接受 OpenAlex ID（W 开头），
        # 不接受 DOI，所以先把 DOI 解析成 OpenAlex 记录。
        try:
            seed_work = await client.get_work_by_doi(doi)
        except Exception as exc:  # 网络或解析失败：记录，不静默跳过
            failures.append(f"{seed}：解析失败（{type(exc).__name__}: {exc}）")
            continue
        if seed_work is None:
            failures.append(f"{seed}：OpenAlex 中没有这条记录")
            continue
        openalex_id = seed_work.source_record_id

        citing = referenced = None
        # 反向引用：谁引用了种子
        try:
            citing = await client.get_citations(openalex_id, max_results=per_direction)
        except Exception as exc:
            failures.append(f"{seed}：取反向引用失败（{type(exc).__name__}: {exc}）")
        # 正向引用：种子引用了谁
        try:
            referenced = await client.get_references(openalex_id, max_results=per_direction)
        except Exception as exc:
            failures.append(f"{seed}：取正向引用失败（{type(exc).__name__}: {exc}）")

        for result, relation in ((citing, "引用了种子"), (referenced, "被种子引用")):
            if result is None:
                continue
            for paper in result.papers:
                if not _in_year_range(paper, years):
                    continue
                key = paper_key(paper)
                # 已有的 gold 不必再作为候选提出
                if key.lower() in known:
                    continue
                candidate = Candidate(
                    paper=paper,
                    relation=relation,
                    seed_key=seed,
                    topic_overlap=_topic_overlap(paper, terms),
                )
                # 同一篇论文可能通过多个种子、多个方向找到，保留重合度最高的记录
                previous = found.get(key)
                if previous is None or candidate.topic_overlap > previous.topic_overlap:
                    found[key] = candidate
        # 标记已作为种子的论文，避免把 gold 自己列成候选
        known.add(seed.lower())

    # 排序：先按主题重合度，再按被引数。被引数用 0 兜底。
    ordered = sorted(
        found.values(),
        key=lambda item: (
            -item.topic_overlap,
            -(item.paper.raw.get("cited_by_count") or 0),
        ),
    )
    return ordered, failures


def render_worksheet(
    *,
    question: EvaluationQuestion,
    candidates: list[Candidate],
    years: tuple[int, int] | None,
    translations: dict[int, str] | None = None,
    header_translations: dict[int, str] | None = None,
) -> str:
    """把候选渲染成人工复核表。

    translations 是"候选序号 -> 中文标题"的映射，只用于复核时快速定位。
    中文标题是机器翻译，不能作为归档内容，也不能替代英文原文判断。
    """

    translations = translations or {}
    header_translations = header_translations or {}
    lines = [
        f"# 金标候选：{question.question_id}",
        "",
        f"**问题**：{question.question}",
        "",
    ]
    # 问题与子问题的中文注释：复核时先要读懂"在问什么"，再判断论文是否回答。
    # translate_texts 的键从 1 开始（1=问题，2..n+1=子问题），这里必须用同一基准；
    # 先前按 0 开始取值，结果整体错位一位，问题的译文挂到了子问题 1 上。
    if header_translations.get(1):
        lines.extend([f"　　→ {header_translations[1]}", ""])
    lines.extend(["**子问题**：", ""])
    for index, sub in enumerate(question.subquestions, start=1):
        lines.append(f"{index}. {sub}")
        if header_translations.get(index + 1):
            lines.append(f"　　→ {header_translations[index + 1]}")
        lines.append("")
    lines.extend(
        [
            "",
            f"**现有 gold**：{len(question.gold_papers)} 篇　"
            f"**年份范围**：{years or '不限'}　"
            f"**引用图候选**：{len(candidates)} 篇",
            "",
            "## 判定标准",
            "",
            "一篇论文算作 gold，当且仅当**领域专家会把它作为回答某个子问题的证据引用**。",
            "按子问题分别判定，因为证据是按子问题分配的。",
            "",
            "逐条检查：",
            "",
            "1. 论文是否真正回答某个子问题（不是主题相邻）",
            "2. 年份是否在声明范围内",
            "3. 摘要是否包含可以作为证据的完整句子",
            "4. 判定它支撑哪个子问题（填编号）",
            "",
            "## 候选清单",
            "",
            "| # | 年份 | 标题 | 中文标题(机翻) | DOI | 被引 | 关系 | 命中 | 判定 | 子问题 |",
            "|---:|---:|---|---|---|---:|---|---:|---|---:|",
        ]
    )
    for index, item in enumerate(candidates, start=1):
        paper = item.paper
        title = " ".join((paper.title or "").replace("|", "\\|").split())
        cited = paper.raw.get("cited_by_count") or 0
        zh = translations.get(index, "")
        lines.append(
            f"| {index} | {paper.year or '?'} | {title[:70]} | {zh} "
            f"| `{paper.doi or ''}` | {cited} | {item.relation} "
            f"| {item.topic_overlap} | | |"
        )
    lines.extend(
        [
            "",
            "## 摘要（判定用）",
            "",
            "判据 3 要求确认摘要里存在可作为证据的完整句子，因此这里附上原文摘要。",
            "机翻标题仅供快速定位，**判定必须依据英文原文**。",
            "",
        ]
    )
    for index, item in enumerate(candidates, start=1):
        abstract = " ".join((item.paper.abstract or "").split())
        lines.append(f"**{index}. {item.paper.title}**")
        lines.append("")
        lines.append(f"- DOI：`{item.paper.doi or ''}`")
        lines.append(f"- 关联种子：`{item.seed_key}`（{item.relation}）")
        lines.append("")
        lines.append(abstract or "（源站未提供摘要——需另行获取，或直接放弃该候选）")
        lines.append("")
    lines.extend(
        [
            "",
            "## 记录",
            "",
            "| 字段 | 内容 |",
            "|---|---|",
            "| 复核人 | |",
            "| 日期 | |",
            "| 采纳的候选编号 | |",
            "| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |",
            "",
        ]
    )
    return "\n".join(lines)


async def run(args: argparse.Namespace) -> int:
    if args.seed:
        # 直接给种子模式：不读数据集
        question = EvaluationQuestion(
            question_id=args.question_id or "adhoc",
            question=args.question_text or "",
            subquestions=tuple(args.subquestion or ()),
            year_range=tuple(args.years) if args.years else None,
            gold_papers=tuple(f"doi:{item}" for item in args.seed),
        )
        questions = [question]
    else:
        dataset = args.dataset if args.dataset.is_absolute() else ROOT / args.dataset
        if not dataset.is_file():
            print(f"数据集不存在：{dataset}", file=sys.stderr)
            return 1
        loaded = load_questions(dataset)
        questions = (
            loaded if args.all else [q for q in loaded if q.question_id == args.question]
        )
        if not questions:
            print(f"数据集里没有这道题：{args.question}", file=sys.stderr)
            return 1

    # --freeze-cache 时缓存永不过期（复现实验用），否则按默认 TTL 过期
    ttl = None if args.freeze_cache else DEFAULT_TTL_SECONDS
    cache = ResponseCache(args.cache_dir, ttl_seconds=ttl)
    written: list[Path] = []
    async with httpx.AsyncClient(timeout=60.0) as http_client:
        client = build_openalex_client(http_client, cache=cache)
        gateway = DeepSeekGateway(http_client=http_client) if args.translate else None
        for question in questions:
            years = (
                tuple(args.years)
                if args.years
                else (tuple(question.year_range) if question.year_range else None)
            )
            candidates, failures = await collect_for_question(
                client,
                question=question,
                years=years,  # type: ignore[arg-type]
                per_direction=args.per_direction,
            )
            if args.limit:
                candidates = candidates[: args.limit]
            translations: dict[int, str] = {}
            header_translations: dict[int, str] = {}
            if args.translate:
                translations, translate_failures = await translate_texts(
                    gateway,
                    [item.paper.title for item in candidates],
                    kind="学术论文标题",
                )
                for message in translate_failures:
                    print(f"    标题翻译失败：{message}", file=sys.stderr)
                # 键从 1 开始：1 = 研究问题，2..n+1 = 子问题
                header_translations, header_failures = await translate_texts(
                    gateway,
                    [question.question, *question.subquestions],
                    kind="研究问题或其子问题",
                )
                for message in header_failures:
                    print(f"    问题翻译失败：{message}", file=sys.stderr)
            content = render_worksheet(
                question=question,
                candidates=candidates,
                years=years,  # type: ignore[arg-type]
                translations=translations,
                header_translations=header_translations,
            )
            out = args.output_dir / f"gold-candidates-{question.question_id}.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(content, encoding="utf-8")
            written.append(out)
            print(f"{question.question_id}: {len(candidates)} 篇候选 -> {out}")
            # 失败必须可见，否则"0 篇候选"会被误读成"没有相关论文"
            for message in failures:
                print(f"    失败：{message}", file=sys.stderr)

    print(
        f"\n缓存：条目 {cache.entry_count()}，"
        f"命中 {cache.stats.hits}，未命中 {cache.stats.misses}"
    )
    print(f"缓存哈希：{cache.directory_hash()}")
    return 0


async def translate_texts(
    gateway: object,
    texts: list[str],
    *,
    kind: str = "学术论文标题",
    batch_size: int = 5,
) -> tuple[dict[int, str], list[str]]:
    """把英文文本翻成中文注释，**仅供复核时快速定位**。

    注意：
      · 机翻会丢失术语细节，判定必须依据英文原文
      · 结果不写入数据集，数据集只保留英文标题
    kind 用于提示语，取值如"学术论文标题"或"研究问题"。
    返回 (映射, 失败信息列表)。映射是 "序号(从1开始) -> 中文"。

    **绝不写入数据集**：机翻会丢术语细节，判定必须依据英文原文。

    失败必须上报：这里先前是静默 continue，一次限流会让整列中文留空，
    看起来像"模型没翻"而不是"调用失败了"。
    """

    import json as _json
    import re as _re

    from research_agent.llm.gateway import ModelGatewayError

    # 模型常把 JSON 包在说明文字或 ``` 代码块里，裸 loads 会直接失败。
    # 和 policy/relevance 的解析保持同一策略：先取出 JSON 对象再解析。
    json_block = _re.compile(r"\{.*\}", _re.S)

    result: dict[int, str] = {}
    failures: list[str] = []
    system = (
        f"你是学术文献的翻译助手。把英文{kind}译成简洁准确的中文，"
        "保留专业术语的通行译法。只输出 JSON。"
    )
    for start in range(0, len(texts), batch_size):
        chunk = texts[start : start + batch_size]
        numbered = "\n".join(
            f"{start + offset + 1}. {title}"
            for offset, title in enumerate(chunk)
        )
        user = (
            f"按顺序翻译下面 {len(chunk)} 条：\n{numbered}\n\n"
            f'返回格式：{{"translations":["第一句中文","第二句中文", ...]}}'
            "\n数组中必须正好有 "
            f"{len(chunk)} 个字符串，顺序与输入一一对应。"
        )
        payload = None
        last_error = ""
        # 解析失败重试一次：模型偶尔返回空内容或截断的 JSON，重试通常能成功。
        # 批次已经很小，再失败就如实上报，不要静默留空。
        for attempt in range(2):
            try:
                # 输出预算必须给足：模型先把预算花在内部推理上，给小了会返回
                # 空内容（finish_reason=length），表现为"不是 JSON"。
                response = await gateway.complete(  # type: ignore[attr-defined]
                    prompt_hash=f"translation-v1-{attempt}",
                    system=system,
                    user=user,
                    max_output_tokens=3000,
                    json_output=True,
                )
            except ModelGatewayError as exc:
                last_error = str(exc)
                continue
            match = json_block.search(response.content or "")
            if match is None:
                last_error = f"返回里没有 JSON（开头：{response.content[:60]!r}）"
                continue
            try:
                payload = _json.loads(match.group(0))
                break
            except _json.JSONDecodeError as exc:
                last_error = f"JSON 解析失败（{exc}）"
                continue
        if payload is None:
            failures.append(
                f"第 {start + 1}–{start + len(chunk)} 条：{last_error}"
            )
            continue
        # 批次之间稍作停顿，避免连续调用被限流
        await asyncio.sleep(0.4)
        # 关键：**按返回顺序对应**，不信任模型给出的编号。
        # 先前依赖模型回传的 index，但模型每批都从 1 重新编号，
        # 各批互相覆盖，结果是中文标题和论文完全错位——
        # 静默错位比缺翻译危险得多，复核时会照着错误标题判断另一篇论文。
        items = payload.get("translations") or []
        if len(items) != len(chunk):
            failures.append(
                f"第 {start + 1}–{start + len(chunk)} 条："
                f"返回 {len(items)} 条，期望 {len(chunk)} 条"
            )
            continue
        for offset, item in enumerate(items):
            zh = item.get("zh") if isinstance(item, dict) else item
            if isinstance(zh, str) and zh.strip():
                result[start + offset + 1] = zh.strip()
    return result, failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET, help="冻结的问题集 JSONL")
    parser.add_argument("--question", help="question_id，例如 csai_007")
    parser.add_argument("--all", action="store_true", help="处理数据集里的全部问题")
    parser.add_argument("--seed", action="append", help="直接指定种子 DOI，可重复")
    parser.add_argument("--question-text", help="配合 --seed 使用的问题文本")
    parser.add_argument("--subquestion", action="append", help="配合 --seed 使用的子问题，可重复")
    parser.add_argument("--question-id", help="配合 --seed 输出的文件名标识")
    parser.add_argument("--years", type=int, nargs=2, metavar=("起", "止"), help="年份范围")
    parser.add_argument("--per-direction", type=int, default=25, help="每个方向取多少篇（默认 25）")
    parser.add_argument("--limit", type=int, default=40, help="每题最多输出多少候选（默认 40）")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "data" / "cache" / "openalex")
    parser.add_argument("--freeze-cache", action="store_true", help="缓存不过期（复现实验时使用）")
    parser.add_argument(
        "--translate",
        action="store_true",
        help="用模型为标题加中文注释（仅供复核，不写入数据集，需 DEEPSEEK_API_KEY）",
    )
    args = parser.parse_args()

    if not args.all and not args.question and not args.seed:
        parser.error("需要指定 --question、--all 或 --seed")
    return asyncio.run(run(args))


if __name__ == "__main__":
    sys.exit(main())