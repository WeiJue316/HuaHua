# 评测设计

| 字段 | 内容 |
|---|---|
| 文档版本 | v0.1 |
| 状态 | 实验设计基线 |
| 日期 | 2026-09-23 |
| 关联文档 | `docs/PRD.md`, `docs/architecture.md`, `docs/data-model.md` |

## 1. 评测目标

评测必须回答三个研究问题：

- **RQ1（主）**：证据链机制能否降低无支撑结论率并提高引用准确率？
- **RQ2（次）**：多源 MCP 联邦与路由能否提高检索覆盖率和鲁棒性？
- **RQ3（支撑）**：状态机 + Plan-and-Execute 能否提高任务成功率并控制成本？

评测不能只展示“能跑通”，必须给出与 baseline 的可重复对比、消融结果和错误分析。

## 2. 假设与成功阈值

以下阈值是实验前设定的工程目标，不是已经得到的结论。

| 编号 | 假设 | 目标阈值 |
|---|---|---|
| H1a | 完整系统的引用准确率高于无引用约束 baseline | 引用准确率 ≥ 0.90 |
| H1b | 证据链降低无支撑结论率 | 相对 baseline 降低 ≥ 50% |
| H1c | 全文证据 locator 可重新定位 | locator 有效率 ≥ 0.90 |
| H2a | 多源联邦提高检索覆盖率 | Recall@20 相对 B1 提升 ≥ 15% |
| H2b | 路由降低无效源站调用 | 源站调用数减少 ≥ 20%，Recall 不显著下降 |
| H3a | Plan-and-Execute 提高任务完成率 | Task Completion Rate 相对纯 ReAct 提升 ≥ 10 个百分点 |
| H3b | 语义步骤受控后成本可接受 | token 成本不超过纯 ReAct 的 1.5 倍 |

若实验未达到阈值，必须如实报告，并分析原因，不修改数据或指标定义来“凑结果”。

## 3. 数据集

### 3.1 LitSearch

用途：评估科学文献检索能力。

- 论文：`arXiv:2407.18940`。
- 任务：给定研究问题，检索相关论文。
- 重点指标：Recall@K、Precision@K、nDCG@K。
- 作用：提供相对标准化的检索评测，减少完全依赖自建数据的问题。

### 3.2 AutoResearchBench

用途：评估研究任务的整体完成能力。

- 仓库：`https://github.com/CherYou/AutoResearchBench`。
- 重点指标：Task Success Rate、任务步骤完成度、检索质量和输出质量。
- 使用前必须检查数据许可、任务定义和评测协议，并记录实际采用的版本或 commit。

### 3.3 自建 CS/AI 证据链问题集

用途：评估 `Claim → Evidence Span → Paper → Source Record*` 和 `full_text → File → Document`，这是现有检索 benchmark 无法充分覆盖的部分。

规模：

- Pilot v1：10 个问题、24 个 gold paper 链接，用于调试指标和人工标注流程。
- Pilot v2：10 个问题、106 个 question-specific gold paper 链接，由模型初审 + Codex
  逐条审计 + 摘要逐字引文核验生成；用于工程迭代、回归测试、baseline 对比和消融实验。
- v2 不是独立人工金标；论文使用其支撑最终质量结论前，必须补充独立人工抽检并报告一致率。
- 正式集：30 个问题，最终版本冻结后不再修改。
- 每个问题包含 1–3 个可验证的子问题。
- 核心配置固定为 8 个：B0、B1、B2、B3、A1、A2、A3、A4。每个配置在每个问题上运行 3 次，共 `30 × 8 × 3 = 720` 次 Run。B1 的 arXiv 变体和 A5 为可选扩展，不计入核心 720 次。

领域分布：

| 子领域 | 比例 |
|---|---:|
| LLM / RAG / Agent | 30% |
| 计算机视觉 / 多模态 | 20% |
| NLP / 信息检索 | 20% |
| 机器学习系统 / 效率 | 15% |
| 数据集、评测与可复现性 | 15% |

问题类型：

- 方法综述：某类方法的代表性工作和差异。
- 比较问题：两个方法在指标、数据或限制上的差异。
- 趋势问题：近三年研究方向变化。
- 数据集问题：常用数据集、规模和评价指标。
- 可复现性问题：代码、数据、实验设置是否公开。
- 反例问题：某结论是否存在冲突证据。

每个问题记录：

```json
{
  "question_id": "csai_001",
  "question": "...",
  "subquestions": ["..."],
  "domain": "llm_rag",
  "year_range": [2022, 2026],
  "gold_papers": ["doi:...", "arxiv:..."],
  "gold_evidence": [
    {
      "paper_key": "arxiv:2407.18940",
      "evidence_level": "abstract",
      "quote": "...",
      "locator": {"section": "Abstract"},
      "supports_subquestion": 1
    }
  ],
  "acceptable_answers": ["..."],
  "notes": "标注分歧和边界"
}
```

标注要求：

- 每篇 gold paper 必须有稳定标识符或可验证标题。
- 每条 gold evidence 必须能被原文重新定位。
- 标注者不得只凭模型输出确认证据。
- 正式集冻结后，任何修改必须记录版本和原因。
- 尽量由两人独立标注；无法双标时，由作者初标并由导师或同学抽查。
- v2 的完整审计结果和局限见 `evaluation/review/audit-summary.md`。

### 3.4 召回窗口 K 的选择（2026-09-24 实测修正）

用 pilot 的 csai_007 实测了检索召回，结论是 **K 必须与指标的 K 一致，否则 recall 恒为 0**。

金标论文在源站的排序位置：

| 查询形式 | 金标排名 |
|---|---:|
| 停用词过滤后的内容词 | 17 |
| 完整问句 | 13 |
| 仅概念词 | 12 |
| 前两个内容词（如 "methods used"） | 25 名之内不存在 |

早期烟测使用 `--max-results 5`，金标排在第 12–18 位，**在任何查询变体下都无法被召回**，
recall 结构性为 0。提高到 20（与本文件 Recall@20 的记法一致）后恢复到 0.5。

同时确认两个检索策略问题：

- **去掉停用词会损害排序。** "methods used" 这类查询在 OpenAlex 上退化为宽泛匹配，
  返回定量 PCR、蒙特卡洛等完全无关的论文。停用词过滤后的变体不应作为首选。
- **多变体合并按顺序截断，第一个变体占满名额。** 若首个变体排序差，后续变体的结果
  全部被丢弃。合并策略需要按相关性而非变体顺序取舍。

### 3.5 金标规模对指标的影响

csai_007 的金标只有 2 篇，而系统在 K=20 下保留 31 篇候选。此时：

- `Precision@K = 1/31 = 0.03`，**该数字不可解释**——未命中的 30 篇可能同样相关，
  只是不在金标中。
- `Recall` 对单篇缺失极其敏感：漏掉 2 篇中的 1 篇，recall 直接减半。

因此正式 30 题集的金标规模需要显著扩大。建议每题 5–10 篇经验证的相关论文，
并在标注时明确记录检索策略与种子来源；否则 precision 与 recall 都缺乏解释力。
在金标扩充之前，pilot 上的指标只用于**相对比较**（各配置之间的差异），不用于报告绝对水平。

## 4. Baseline

| 编号 | Baseline | 目的 |
|---|---|---|
| B0 | BM25/关键词检索 + 单次 LLM 总结 | 最弱但常见的文献调研流程 |
| B1 | 单源 MCP（arXiv 或 OpenAlex）+ 相同 Agent Core | 验证多源联邦的增益 |
| B2 | 纯 ReAct | 验证状态机 + Plan-and-Execute 的增益 |
| B3 | 完整系统 | 证据链 + 联邦路由 + Plan-and-Execute |

### 4.1 B0：BM25 + 单次 LLM

- 使用冻结的本地 metadata/abstract 语料构建 BM25 索引；语料版本和来源快照写入配置。
- 取 Top-K 后一次性交给 LLM 生成摘要。
- 允许模型生成引用，但不提供证据定位和引用校验。
- 用于衡量“仅检索 + 总结”的基础水平。

### 4.2 B1：单源 MCP

- 保留完整系统的规划、存储和报告流程。
- 只允许使用一个源站，默认 OpenAlex；arXiv 版本为可选补充，不计入核心 720 次。
- 用于衡量多源联邦和去重带来的覆盖增益。

### 4.3 B2：纯 ReAct

- 让 LLM 通过工具调用循环自主决定下一步。
- 工具集合与完整系统相同。
- 不提供显式 Plan 状态机，不强制证据链校验。
- 用于衡量结构化运行时和受控语义步骤的价值。

### 4.4 B3：完整系统

- 状态机 + Plan-and-Execute。
- 五源 MCP + Federation Router。
- 完整证据链和引用校验。
- 输出 Markdown、JSON/CSV 和 BibTeX。

## 5. 消融实验

| 编号 | 消融项 | 移除内容 | 预期观察 |
|---|---|---|---|
| A1 | 去证据链 | Claim 直接生成，不建 Evidence Span | 引用准确率下降，无支撑率上升 |
| A2 | 去规划器 | 固定检索流水线，不做问题分解和补充查询 | 复杂问题成功率下降 |
| A3 | 去路由器 | 无条件查询全部源站 | 调用数和延迟上升，可能引入噪声 |
| A4 | 无引用约束 | 允许自由生成引用和结论 | 幻觉引用和无支撑 Claim 上升 |
| A5 | 去 provenance 合并 | 仅保留首选源记录 | 冲突不可审计，重复率上升 |
| A6 | 去语义相关性过滤 | 移除 judge_relevance 步骤 | Precision@K 下降、Citation Accuracy 下降、Unsupported Claim Rate 上升 |

A1–A4 与 A6 是核心消融；A5 作为多源联邦的补充实验。若时间不足，A5 可延后，
但 A1–A4 与 A6 必须完成。A6 的判定阈值（严格 / 宽松）作为配置项，两种取值都需报告。

A6 的依据见 `docs/adr/0012-semantic-relevance-filtering.md`：人工复核 pilot 数据集时发现，
纯关键词匹配会稳定地把邻域论文收进候选，且该失败无法用词重合消除。

## 6. 指标定义

### 6.1 检索指标

#### Recall@K

```text
Recall@K = |Relevant ∩ TopK| / |Relevant|
```

用于衡量系统是否找到已知相关论文。

#### Precision@K

```text
Precision@K = |Relevant ∩ TopK| / K
```

用于衡量候选集的噪声水平。

#### nDCG@K

使用二元相关性计算，排名越靠前的高相关论文贡献越大。用于比较不同检索排序策略。

#### Source Coverage

```text
SourceCoverage = 至少贡献一个有效结果的源站数 / 被允许调用的源站数
```

用于观察源站贡献是否集中，以及联邦是否真的扩展了覆盖范围。

### 6.2 证据指标

#### Evidence Coverage

```text
EvidenceCoverage = 至少有一个有效 Evidence Span 的 Claim 数 / 全部 Claim 数
```

“有效”指 Paper 存在、Evidence 原文可定位、支持状态一致。

#### Citation Accuracy

```text
CitationAccuracy = 正确引用数 / 全部引用数
```

正确引用必须同时满足：

1. 引用指向真实存在的 Paper。
2. Paper 与 Claim 主题相关。
3. Evidence Span 确实支持 Claim。
4. locator 能重新定位原文。

引用准确性需要人工或规则 + 人工抽样裁定。

#### Unsupported Claim Rate

```text
UnsupportedClaimRate = unsupported Claim 数 / 全部 Claim 数
```

`partially_supported` 单独统计，不并入 supported。

#### Locator Validity

```text
LocatorValidity = 能重新定位的 Evidence Span 数 / full_text Evidence Span 总数
```

#### Provenance Completeness

```text
ProvenanceCompleteness = 带 source、retrieved_at、source_record_id、api_endpoint、mapping_version 且保留 raw 记录的 Paper 数 / Paper 总数
```

### 6.3 任务指标

#### Task Completion Rate

```text
TaskCompletionRate = 满足 baseline-neutral 任务完成清单的 Run 数 / 总 Run 数
```

清单：

- 生成最终报告或答案。
- 覆盖主要子问题。
- 没有未处理异常。
- 在预算内完成。

该指标不要求证据链、引用校验或多源调用，用于 RQ3 的公平 baseline 比较。

#### Evidence Compliance Rate

```text
EvidenceComplianceRate = 通过证据和引用校验的 Claim 数 / 全部 Claim 数
```

用于 RQ1 评估证据链机制。

#### Task Success Rate

```text
TaskSuccessRate = 满足完整系统验收清单的 Run 数 / 总 Run 数
```

完整系统验收清单：

- 至少调用两个源站，完整系统为五源。
- 生成有效候选集。
- 至少获得一篇全文或明确记录不可获取原因。
- 生成带 locator 的证据表。
- 生成报告且引用校验通过。
- 没有策略违规和未处理异常。

Task Success Rate 只用于完整系统验收，不用于 H3a 的 baseline 比较。

#### Step Completion Rate

```text
StepCompletionRate = SUCCEEDED 或 SKIPPED 的 Step 数 / 总 Step 数
```

#### Recovery Rate

```text
RecoveryRate = 从失败或暂停状态恢复并完成的 Run 数 / 发生失败或暂停的 Run 数
```

### 6.4 效率指标

- 端到端延迟：P50、P95、最大值。
- 单源调用延迟：P50、P95。
- LLM 调用次数。
- 输入和输出 token。
- LLM 成本。
- 源站请求次数、重试次数、限流次数。
- PDF 下载成功率。
- PDF 解析成功率。

## 7. 人工评价

对报告进行分层抽样：

- 每个 baseline 至少抽取 10 个 Run。
- 每个 Run 抽取 5 条关键 Claim。
- 评价者看不到系统名称，避免品牌偏差。

评价维度：

| 维度 | 评分 |
|---|---|
| 相关性 | 1–5 |
| 证据支持 | 1–5 |
| 引用正确性 | 0/1 |
| 覆盖完整性 | 1–5 |
| 可读性 | 1–5 |
| 不确定性表达 | 1–5 |

至少计算评价者间一致性；第一轮人工复核覆盖 10% 的引用和证据，第二人再复核其中 20%。

## 8. 实验流程

```text
冻结问题集与 gold evidence
  → 冻结系统版本、模型版本和 prompt 版本
  → 为每个 baseline 和完整系统生成配置
  → 执行所有 Run
  → 自动计算指标
  → 人工抽样复核引用与证据
  → 导出聚合结果和失败样本
  → 统计检验
  → 生成论文图表
```

### 8.1 运行控制

- 核心 8 配置在每个正式问题上运行 3 次，温度设为 0；若模型仍随机，记录方差。
- B0/B1/B2 于 2026-12-01 至 2027-01-15 完成；B3/A1–A4 于 2027-01-16 至 2027-02-28 完成。B0/B1/B2 一旦开始正式运行，其配置和问题集不得再变。
- 评测人时按 12–22 小时/周规划，项目总人时按 32–47 小时/周规划。
- 所有源站请求记录时间、版本、限流和重试。
- 网络失败不得手工挑选成功样本；失败样本必须保留。
- 运行顺序随机化，避免 API 状态和时间偏差。
- 固定模型 provider、model ID、prompt version、parser version 和 source adapter version。

### 8.2 数据切分

- Pilot 集只用于调试，不计入最终论文主结果。
- 正式集冻结后用于最终对比。
- 不允许根据最终测试结果反复修改 prompt 后只在同一测试集上报告。

## 9. 统计方法

- 连续指标：配对 bootstrap 95% 置信区间。
- 二元指标：McNemar 检验或配对比例检验。
- 延迟和成本：Wilcoxon signed-rank 检验。
- 多个指标比较：Holm–Bonferroni 校正。
- 报告效应量，不只报告 p 值。
- 样本不足时使用描述性统计，并明确限制。

## 10. 错误分析

错误类别至少包括：

1. 查询构造错误。
2. 源站路由错误。
3. 元数据映射错误。
4. 跨源去重错误。
5. 候选筛选遗漏。
6. PDF 获取失败。
7. PDF 解析失败或乱码。
8. Evidence Span 定位失败。
9. 证据存在但不支持 Claim。
10. 引用编号或参考文献错误。
11. 模型过度总结或遗漏冲突证据。
12. 源站限流、超时或 API 变化。

每个类别报告数量、比例、典型案例和可能修复方向。

## 11. 可复现性要求

每次评测运行必须保存：

- 数据集版本和问题集哈希。
- 系统版本或 Git commit。
- Python、依赖和 parser 版本。
- 模型 provider、模型 ID、参数和 prompt version。
- MCP server 版本和源站 API 响应摘要。
- 运行配置、随机种子、开始和结束时间。
- 原始结果、聚合结果、失败样本和日志。
- 人工评价记录和评分者信息（匿名化）。

## 12. 有效性威胁

### 内部有效性

- LLM 随机性和 provider 更新可能影响结果。
- 人工标注可能带主观性。
- PDF 解析质量会影响 Evidence Span 定位。
- 源站 API 在实验期间可能变化。

### 外部有效性

- 数据集以英文计算机/AI 文献为主，不能直接外推到其他学科。
- 五个源站不能代表全部学术检索渠道。
- 单用户、单机环境不能代表多人协作场景。

### 构念有效性

- Recall 不能完全代表“科研质量”。
- Evidence Coverage 不能保证证据真正支持 Claim。
- Task Success 清单需要人工判断，不能只看程序退出码。

### 结论有效性

- 小样本可能不足以支持强统计结论。
- 多个指标比较需要校正。
- 不把相关性解释为因果关系；结论限定在实验条件下。

## 13. 预期论文图表

1. 系统架构图。
2. 证据链数据模型图。
3. MCP 联邦与路由流程图。
4. 五源能力矩阵。
5. Baseline 检索指标对比图。
6. 证据链指标对比图。
7. 消融实验柱状图或雷达图。
8. 延迟和成本对比图。
9. 错误类型分布图。
10. 一个完整 Run 的证据链案例图。

## 14. 评测完成标准

- 正式问题集冻结且有版本哈希。
- 核心 8 配置完成运行，共 720 次 Run。
- A1–A4 消融完成。
- 核心指标有置信区间或统计检验。
- 第一轮人工复核覆盖 10% 的引用和证据，第二人复核其中 20%。
- 错误分析覆盖所有主要失败类别。
- 原始结果和脚本可复现。
- 论文中的每张结果图都能追溯到配置文件、结果文件和运行时间。
