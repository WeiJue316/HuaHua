# B2 Pure ReAct Pilot Smoke（2026-09-24）

## 固定条件

- 数据集：`pilot_questions.v2.jsonl`
- 数据集哈希：`f0ce2276db698bf0e13754a8ec357fa8c37234ab687dd53d37f59a89d7dd18ac`
- 系统：B2 纯 ReAct
- 最大步数：8
- 每次搜索 Top-K：5
- 重复次数：1
- 评测运行 ID：`c1341444-5a38-42f5-ad91-78a30233651c`
- 本地数据库：`data/b2_smoke_full.db`（不进入 Git）
- 报告与 trace：`reports/b2-smoke-full/b2`（不进入 Git）

## 结果

- Case：10/10 completed，0 failed
- 平均 Recall@5：0.0578
- 平均 Precision@5：0.0430
- 平均模型调用：8.0
- 平均搜索动作：6.8
- 平均输入/输出 token：4840.5 / 3550.3
- 平均延迟：20064.6 ms
- 平均报告长度：8095.2 字符

源站动作与失败：

| 源站 | 搜索动作 | 失败 |
|---|---:|---:|
| arXiv | 10 | 10（406） |
| Semantic Scholar | 30 | 5（429/网络） |
| OpenAlex | 13 | 0 |
| Crossref | 9 | 0 |
| DBLP | 6 | 6（bot challenge） |

## 解释边界

B0 使用包含 gold 的冻结本地语料，B2 使用实时五源检索。因此 B0 与 B2 的
Recall/Precision **不可直接横向比较**。B2 的检索指标同时受到源站可用性影响：
arXiv 与 DBLP 在当前环境全部失败，Semantic Scholar 部分失败。

B2 当前可用于：

- 验证纯 ReAct 循环、轨迹和预算控制；
- 比较模型调用数、token、延迟和任务完成；
- 为 A1/A2/A4 和 B3 提供运行基线。

在论文中报告检索增益前，必须先统一候选宇宙或显式报告源站可用性差异。