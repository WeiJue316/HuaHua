# 三源评测快照

`pilot_v2_three_source.jsonl` 是 B1/B2/B3 受控对比使用的冻结候选池。
它由 v2 问题的中性 Planner 查询变体生成，覆盖 OpenAlex、Crossref 和
Semantic Scholar。

## 当前版本

- 快照版本：`pilot-v2-three-source-v1`
- 数据集：`pilot_questions.v2.jsonl`
- 数据集哈希：`f0ce2276db698bf0e13754a8ec357fa8c37234ab687dd53d37f59a89d7dd18ac`
- 源站：OpenAlex、Crossref、Semantic Scholar
- Per-source 上限：50
- 文档数：1441（每源 500）
- 快照哈希：`87a9d5546e3ff66dea3446333664994c75407aaac5ce4a08a45be926f43cc6e33`
- 源站构建错误：0

完整 manifest 见 `pilot_v2_three_source.manifest.json`。

## 使用方式

```powershell
uv run research-agent evaluate `
  --systems B1,B2,B3 `
  --sources openalex,crossref,semantic_scholar `
  --source-snapshot evaluation/snapshots/pilot_v2_three_source.jsonl `
  --max-results 5
```

快照模式中，每个源仍只返回本源的候选。不同系统可以用不同 query，但所有
query 都在同一候选池内做 BM25 排序，因此不会再因实时源站波动改变候选宇宙。

## 解释边界

快照的目标是控制变量，不是模拟 OpenAlex/Crossref/Semantic Scholar 的真实
排序算法。论文如果要报告真实在线检索性能，必须另跑 live-source 实验，并与
快照实验结果分开报告。
