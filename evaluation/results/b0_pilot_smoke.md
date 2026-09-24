# B0 Pilot Smoke（2026-09-24）

## 固定条件

- 数据集：`pilot_questions.v2.jsonl`
- 数据集哈希：`f0ce2276db698bf0e13754a8ec357fa8c37234ab687dd53d37f59a89d7dd18ac`
- B0 语料：`evaluation/corpora/pilot_v2_b0.jsonl`
- 语料哈希：`0384a7c1b4abe73c1c1f31da6eed61fc3b522e8d96b41fe4d3179820dc0b5662`
- 系统：B0（BM25 + 单次 LLM 总结）
- Top-K：5
- 重复次数：1
- 评测运行 ID：`c3ff8a7f-f8a4-4c67-bc71-77e0a1b22aee`
- 本地数据库：`data/b0_smoke_final.db`（不进入 Git）
- 报告目录：`reports/b0-smoke-final`（不进入 Git）

## 结果

- Case：10/10 completed，0 failed
- 平均 Recall@5：0.2886
- 平均 Precision@5：0.5000
- 平均输入 token：1340.9
- 平均输出 token：1552.2
- 平均延迟：7736.7 ms
- 平均报告长度：5044.2 字符

## 过程中发现并修正的问题

第一次 smoke 使用 2000 output token，10 题中 3 题因模型推理耗尽输出预算而截断。
将 B0 单次总结预算提高到 6000 token 后，重新运行完整 10 题，全部完成。

该记录只验证评测管线和 B0 可运行性。Top-K=5 不是正式 K，也不是最终论文结果；
正式对比必须固定 K、正式 30 题集、模型版本、提示词版本和语料哈希后再报告。