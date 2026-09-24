# Pilot 三系统对比（2026-09-25）

## 固定条件

- 数据集：`pilot_questions.v2.jsonl`
- 数据集哈希：`f0ce2276db698bf0e13754a8ec357fa8c37234ab687dd53d37f59a89d7dd18ac`
- 系统：B1（OpenAlex + Agent Core）、B2（纯 ReAct）、B3（完整系统）
- 源站白名单：`openalex`, `crossref`, `semantic_scholar`
- 排除：arXiv（406）、DBLP（bot challenge）
- 每次搜索 Top-K：5
- 重复次数：1
- 模型：`deepseek-flash`
- 语义过滤 prompt：`relevance-v1`
- 评测运行 ID：`c05ff1b4-b70e-4966-844f-530a93d0b029`
- 本地数据库：`data/eval_compare_full.db`（不进入 Git）
- 报告目录：`reports/eval-compare-full`（不进入 Git）
- 源站缓存哈希：`1c656d06349ae76d8516639f3b06da5fb48486188818104727ed0152ec1376d1`

## 总体结果

- Case：30/30 completed，0 failed
- B1/B3：证据覆盖率 1.0，无支撑 Claim Rate 0.0
- B2：不生成 Claim 和 Evidence，只有最终报告，因此不计算证据合规指标

| 系统 | 平均 Recall@5 | 平均 Precision@5 | Claim 数 | 模型调用 | 输入 token | 输出 token | 模型延迟 |
|---|---:|---:|---:|---:|---:|---:|---:|
| B1 | 0.0836 | 0.1700 | 2.6 | 5.0（相关过滤） | 3090.6 | 1871.0 | 11124.4 ms |
| B2 | 0.0543 | 0.0307 | 不适用 | 8.1（ReAct + 报告） | 5673.4 | 5191.6 | 28079.1 ms |
| B3 | 0.0836 | 0.0465 | 7.5 | 15.0（相关过滤） | 9660.2 | 5808.4 | 33448.3 ms |

## 当前可以支持的判断

- 三系统均能完成 10 题 Pilot 并生成报告。
- B3 比 B1 生成更多 Claim；两者在当前规模下的 Recall@5 相同。
- B2 的 ReAct 循环平均使用 7.5 步、8.1 次模型调用，成本显著高于 B1 的相关过滤调用。
- 统一源站白名单能避免 arXiv/DBLP 失败污染系统间对比。

## 当前不能支持的判断

- 不能报告“多源显著提高 Recall”：B1 和 B3 的 Recall@5 相同。
- 不能报告 B2 的检索劣势：B2 无证据链，且其 ReAct 查询分布与 B1/B3 的 Planner 查询不同。
- 不能报告最终 Token 成本差异：B1/B3 的成本口径主要是语义过滤，B2 包含 ReAct 决策和最终报告，口径不同。
- K=5、单次重复、AI 审计 Pilot 均不足以支撑论文最终结论。

## 下一步

1. 实现统一的任务完成率计算口径，覆盖 B1/B2/B3。
2. 把 B1/B3 的模型调用、token、延迟写回 evaluation metric。
3. 设计同一候选宇宙或源站健康快照，消除检索输入差异。
4. 在此基础上进入 A1、A2、A4 消融与正式 30 题集。

## 模型用量口径修正验证

2026-09-25 追加 1 题 smoke（评测运行 ID `d9d45a3b-2830-43ce-af7a-00adf9c11f64`）验证：
B1、B2、B3 现在都在 `evaluation_case.metrics_json` 中输出相同字段
`llm_calls`、`input_tokens`、`output_tokens`、`model_latency_ms`。

该验证只证明指标口径已一致，不改变上面的 Pilot 结论或正式实验规模。


## Task Completion Rate 口径验证

2026-09-25 追加 1 题 smoke（评测运行 ID `6dc05a67-c656-4b90-a635-0b42ad3372f9`），
统一使用 `task-completion-v1` 和 `--model-call-budget 20`：

| 系统 | Task Completion | 子问题覆盖 | 模型调用 |
|---|---:|---:|---:|
| B1 | 0.0 | 0/2 | 5 |
| B2 | 1.0 | 2/2 | 8 |
| B3 | 0.0 | 1/2 | 15 |

该 smoke 证明指标口径已经统一并可用，但单题结果不能外推。后续正式实验需要
对全部问题运行，并报告 judge 失败率和人工抽检一致性。
