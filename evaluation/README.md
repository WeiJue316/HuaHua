# 评测目录

本目录保存问题集、gold evidence、冻结语料与快照、审阅记录和结果摘要。

- `datasets/`：冻结后的问题集和标注版本；版本、哈希和变更原因记录在 `datasets/VERSIONS.md`。
- `corpora/`：B0 使用的冻结 BM25 语料及 manifest。
- `snapshots/`：跨系统对照实验使用的冻结源站快照及 manifest。
- `review/`：金标候选审阅记录（模型初审与人工/AI 复核）。
- `results/`：结果摘要（Markdown），提交到 Git；原始评测数据库和报告在 `data/`、`reports/`，不提交。
- 评测脚本位于项目根目录 `scripts/`。
- 任何正式集修改都必须记录版本、哈希和原因。
- 2026-09-25 及之前的对比与消融摘要按 ADR-0015 口径作废，只作工程记录。
