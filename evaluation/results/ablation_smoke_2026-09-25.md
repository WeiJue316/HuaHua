# A1 / A2 消融 Smoke（2026-09-25）

**口径作废（2026-09-26，ADR-0015）**：检索指标按无序集合计算，且当时 A4 尚未接入；
只保留为工程记录，不得在论文中引用。新口径结果见路线图 `EV-10`。

## 固定条件

- 数据集：`pilot_questions.v2.jsonl`
- 快照：`evaluation/snapshots/pilot_v2_three_source.jsonl`
- 快照哈希：`87a9d5546e3ff66dea3446333664994c75407aaac5ce4a08a45be926f43cc6e33`
- 系统：B3、A1（去证据链）、A2（去 Planner）
- Top-K：5
- 评测运行 ID：`98b3f8f0-6ec7-400b-85fb-fb8564056fc8`
- 本地数据库：`data/ablation_smoke_final.db`（不进入 Git）

## 单题结果

| 系统 | Recall | Claim 数 | Evidence Coverage | Unsupported Claim Rate | Task Completion |
|---|---:|---:|---:|---:|---:|
| B3 | 0.0870 | 11 | 1.0 | 0.0 | 0.0 |
| A1 | 0.0870 | 14 | 0.0 | 1.0 | 0.0 |
| A2 | 0.0870 | 11 | 1.0 | 0.0 | 0.0 |

A1 的 Claim 数高于 B3 是预期差异：A1 不要求摘要中存在可定位证据，因此会为没有
Evidence Span 的通过过滤论文也生成 unsupported Claim。单题结果不能外推。

## A4 状态

A4（无引用约束）仍标记为未实现。原因是当前 B3 的 Claim/报告由确定性模板生成；
直接复用该路径无法产生“自由生成引用和结论”的真实消融，只会得到一个无证据的
A1 变体。A4 的前置条件是先实现可配置的 LLM synthesis/claim generation，再在关闭
引用校验的条件下运行。