# 正式问题集 v1 设计冻结

状态：设计冻结（2026-10-14）。标注文件尚未创建。

本文件只冻结题量、领域、题型和标注门槛。它不是评测集。
`formal_questions.v1.jsonl` 要等每题都有金标后再新建，并且不得改写
`pilot_questions.v1.jsonl` 或 `pilot_questions.v2.jsonl`。

检查规则在 `research_agent.evaluator.formal_design.validate_formal_records`。

## 规模

- 30 题，编号 `formal_001` 到 `formal_030`，顺序固定。
- 每题恰好 2 个子问题。
- 每题 `year_range` 为 `[2022, 2026]`。
- 标注完成前可以没有 `gold_papers`。标注完成时每题至少 5 篇 gold paper，
  且两个子问题都至少有一条 `gold_evidence`。

## 领域配额

评测文档里的 15% 乘以 30 不是整数。两个 15% 领域合计 9 题，分成 5 和 4。
多出的 1 题给机器学习系统，因为 Pilot 里该领域已经比数据集题更多。

| 领域代码 | 含义 | 题数 |
|---|---|---:|
| `llm_rag` | LLM / RAG / Agent | 9 |
| `vision_multimodal` | 计算机视觉 / 多模态 | 6 |
| `nlp_ir` | NLP / 信息检索 | 6 |
| `ml_systems` | 机器学习系统 / 效率 | 5 |
| `datasets_repro` | 数据集、评测与可复现性 | 4 |

## 题型配额

每种题型 5 题。字段名是 `question_type`。Pilot 加载器不读这个字段，因此不改变已冻结 Pilot 的内容哈希。

| 代码 | 含义 |
|---|---|
| `method_survey` | 方法综述 |
| `comparison` | 比较 |
| `trend` | 趋势 |
| `dataset` | 数据集 |
| `reproducibility` | 可复现性 |
| `counterexample` | 反例或冲突证据 |

## 还不在这次冻结里

- 不写 30 道题的正文，也不预填空金标。
- 不把 Pilot 复制后改名当作正式集。
- 论文结果在该文件冻结并登记哈希之前，仍只能引用 Pilot 版本。
