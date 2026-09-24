# B0 冻结语料

`pilot_v2_b0.jsonl` 是 B0（BM25 + 单次 LLM）使用的自包含论文语料。
它从冻结的 OpenAlex 响应缓存中抽取 `PaperCandidate`，只保留可稳定复用的
`paper_key`、标题、摘要、年份和 DOI，因此不依赖本机缓存路径。

## 当前版本

- 语料版本：`pilot-v2-b0`
- 绑定数据集：`evaluation/datasets/pilot_questions.v2.jsonl`
- 数据集哈希：`f0ce2276db698bf0e13754a8ec357fa8c37234ab687dd53d37f59a89d7dd18ac`
- 文档数：777
- 语料哈希：`0384a7c1b4abe73c1c1f31da6eed61fc3b522e8d96b41fe4d3179820dc0b5662`
- 来源缓存哈希：`1419709409a7871ddbb241d445e1b1159cf073a48bf6612ff196406ef53612d4`
- v2 中所有 gold paper key 均存在于语料中。

## 重建命令

```powershell
uv run python scripts/build_b0_corpus.py
```

该命令只读 `data/cache/openalex`，生成 JSONL 和 manifest，不调用网络。
缓存被修改后语料哈希会变化；正式实验必须固定使用 manifest 记录的组合。

## 解释边界

这是一个面向 Pilot 的本地 metadata/abstract 语料，不是完整学术检索语料。
B0 指标只用于同一问题集、同一语料版本下的相对比较，不能外推为互联网检索
的绝对水平。