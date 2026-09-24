# 评测数据集版本记录

正式评测集一经冻结不得原地修改。任何变更都要新增版本号，并在这里登记日期、
内容哈希和变更原因。冻结版的内容哈希是实验可复现性的锚点：论文中报告评测结果时
必须写明所用版本与哈希。

| 版本 | 文件 | 冻结日期 | 问题数 | gold paper 数 | 内容哈希 | 复核人 | 状态 |
|---|---|---:|---:|---:|---|---|---|
| v1 | `pilot_questions.v1.jsonl` | 2026-09-23 | 10 | 24 | `ce5516b789fbfc347ec6c97c972bdcc9eea99e3d562d9ab4d9cf862240eff0e3` | LYY | 冻结 |
| v2 | `pilot_questions.v2.jsonl` | 2026-09-24 | 10 | 106 | `f0ce2276db698bf0e13754a8ec357fa8c37234ab687dd53d37f59a89d7dd18ac` | Codex（AI 审计） | 冻结（AI 审计） |

`pilot_questions.seed.jsonl` 不是评测集，它是 `research_agent.evaluator.pilot_seed`
的可再生草稿，供后续重新生成使用。评测与论文引用一律以带版本号的冻结文件为准。

## v1 冻结说明

- 来源：由 `pilot_questions.seed.jsonl` 复制而来，冻结未改动任何内容，两者哈希相同。
- 领域分布：`llm_rag` 3 题、`vision_multimodal` 2 题、`nlp_ir` 2 题、
  `ml_systems` 2 题、`datasets_repro` 1 题。
- 年份范围：全部为 2022–2026。
- 覆盖情况：10 题的 20 个子问题全部有 gold evidence 支撑。

### 复核过程

复核按六项判据逐条进行：问题是否属于计算机/AI 且答案明确、子问题是否互不重叠
且都有证据、年份范围是否相符、gold paper 是否真正回答问题、quote 是否为可独立
阅读的完整句子、`supports_subquestion` 是否指向正确。

复核期间发现并修正的生成器缺陷（均已落地为回归测试）：

- 摘要字段混入作者名单或会议名称时被当作证据引用
- 连字符不拆词，`retrieval-augmented` 无法匹配 `retrieval augmented`
- 单复数不匹配，`datasets` 无法匹配 `dataset`
- 声明的 `year_range` 未被强制执行，混入 1999–2021 年的论文
- 论文年份未记录，年份判据无法从数据本身验证

复核期间被替换的论文包括芯片设计、语音数据集、生物医学检索、RLHF 指令微调等
与题目不对口的条目。这些替换记录是本项目引入语义相关性过滤的直接动机，详见
`docs/roadmap.md` 的 P1 条目。

### 已知取舍

- **v1 是人工复核版本，不是自动生成版本。** 自动生成路径的产出仍达不到可直接冻结
  的质量，语义过滤（P1）落地后应以 v1 为参照标准衡量其准确率。
- 子问题数量固定为每题 2 个，若后续需要更细的分解应在新版本中调整。


## v2 冻结说明

- 来源：以冻结的 `pilot_questions.v1.jsonl` 为底稿复制，不改写 v1。
- 候选扩展：10 题各取 OpenAlex 引用图候选 25 条，共 250 条。
- 审计结果：采纳 82 条候选，不采纳 157 条，源站无摘要而暂不纳入 11 条。
- 数据集规模：10 题、106 个 question-specific gold paper 链接、119 条
  `gold_evidence`。采纳候选按子问题展开后新增 95 条 evidence annotation；
  同一篇论文支撑两个子问题时会生成两条 annotation，但 `gold_papers` 只记一次。
- 审计方法：模型初审 + Codex 逐条复核 + 摘要逐字引文核验 + 标题去重。
- 审计记录：`evaluation/review/audit-summary.md` 与
  `evaluation/review/gold-candidates-csai_*.md`。
- 引文核验：`uv run python scripts/apply_gold_review.py --worksheet-dir evaluation/review --dry-run --freeze-cache`
  在冻结前无未处理条目。

### v2 证据边界

v2 是 **AI 审计版本**，不是两名独立人类标注者完成的金标版本。它可用于工程迭代、
回归测试、baseline 对比和消融实验；若论文要用 v2 支撑最终质量结论，应至少补充
独立人工抽检，并报告抽样比例、一致率和争议项处理方式。不得在论文中将 v2 表述为
“人工金标”。

“暂不纳入”只表示当前源站未提供可核验摘要，不表示论文主题不相关。

## 变更规则

1. 不得原地修改任何已冻结文件。
2. 新版本写新文件，`v2`、`v3` 依次递增，并在上表新增一行。
3. 每行必须记录：版本、文件名、冻结日期、问题数、gold paper 数、内容哈希、
   复核人、状态。
4. 内容哈希由 `research_agent.evaluator.dataset.dataset_hash` 计算，
   可用 `uv run python -c "from pathlib import Path; from research_agent.evaluator.dataset import load_questions, dataset_hash; print(dataset_hash(load_questions(Path('evaluation/datasets/pilot_questions.v2.jsonl'))))"` 复算。
5. 评测运行必须记录所用数据集版本与哈希，否则结果不可追溯。
