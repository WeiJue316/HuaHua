# 金标候选：csai_006

**问题**：How does dense retrieval compare with sparse retrieval for scientific search?

**子问题**：

1. What are the reported trade-offs?
2. Which evaluation setups are used?

**现有 gold**：2 篇　**年份范围**：(2022, 2026)　**引用图候选**：25 篇

## 判定标准

一篇论文算作 gold，当且仅当**领域专家会把它作为回答某个子问题的证据引用**。
按子问题分别判定，因为证据是按子问题分配的。

逐条检查：

1. 论文是否真正回答某个子问题（不是主题相邻）
2. 年份是否在声明范围内
3. 摘要是否包含可以作为证据的完整句子
4. 判定它支撑哪个子问题（填编号）

## 候选清单

| # | 年份 | 标题 | DOI | 被引 | 与种子的关系 | 主题命中 | 判定 | 子问题 |
|---:|---:|---|---|---:|---|---:|---|---:|
| 1 | 2023 | Is ChatGPT Good at Search? Investigating Large Language Models as Re-R | `10.18653/v1/2023.emnlp-main.923` | 230 | 引用了种子 | 3 | | |
| 2 | 2025 | Retrieval augmented generation for large language models in healthcare | `10.1371/journal.pdig.0000877` | 226 | 引用了种子 | 3 | | |
| 3 | 2023 | Query2doc: Query Expansion with Large Language Models | `10.18653/v1/2023.emnlp-main.585` | 188 | 引用了种子 | 3 | | |
| 4 | 2024 | Fine-Tuning LLaMA for Multi-Stage Text Retrieval | `10.1145/3626772.3657951` | 112 | 引用了种子 | 3 | | |
| 5 | 2025 | Evaluating Retrieval-Augmented Generation Variants for Clinical Decisi | `10.3390/electronics14214227` | 14 | 引用了种子 | 3 | | |
| 6 | 2022 | Unsupervised Corpus Aware Language Model Pre-training for Dense Passag | `10.18653/v1/2022.acl-long.203` | 144 | 被种子引用 | 2 | | |
| 7 | 2023 | The Information Retrieval Experiment Platform | `10.1145/3539618.3591888` | 54 | 引用了种子 | 2 | | |
| 8 | 2023 | Large Language Models Know Your Contextual Search Intent: A Prompting  | `10.18653/v1/2023.findings-emnlp.86` | 49 | 引用了种子 | 2 | | |
| 9 | 2024 | Soft prompt tuning for augmenting dense retrieval with large language  | `10.1016/j.knosys.2024.112758` | 26 | 引用了种子 | 2 | | |
| 10 | 2024 | Generative Multi-Modal Knowledge Retrieval with Large Language Models | `10.1609/aaai.v38i17.29837` | 24 | 引用了种子 | 2 | | |
| 11 | 2025 | Retrieval-Augmented Generation to Generate Knowledge Assets and Creati | `10.3390/app15116247` | 22 | 引用了种子 | 2 | | |
| 12 | 2024 | Customized Retrieval Augmented Generation and Benchmarking for EDA Too | `10.1145/3676536.3676730` | 21 | 引用了种子 | 2 | | |
| 13 | 2025 | MoRSE: Bridging the Gap in Cybersecurity Expertise with Retrieval Augm | `10.1145/3672608.3707898` | 14 | 引用了种子 | 2 | | |
| 14 | 2025 | Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs)  | `10.3390/app16010368` | 11 | 引用了种子 | 2 | | |
| 15 | 2023 | SCITAB: A Challenging Benchmark for Compositional Reasoning and Claim  | `10.18653/v1/2023.emnlp-main.483` | 9 | 引用了种子 | 2 | | |
| 16 | 2025 | An In-depth Analysis of the Linguistic Characteristics of Science Clai | `10.1145/3746170` | 2 | 引用了种子 | 2 | | |
| 17 | 2025 | The Next Phase of Scientific Fact-Checking: Advanced Evidence Retrieva | `10.1145/3731120.3744614` | 2 | 引用了种子 | 2 | | |
| 18 | 2025 | +VeriRel: Verification Feedback to Enhance Document Retrieval for Scie | `10.1145/3746252.3760822` | 1 | 引用了种子 | 2 | | |
| 19 | 2023 | The student becomes the master: Outperforming GPT3 on Scientific Factu | `10.18653/v1/2023.findings-emnlp.451` | 0 | 引用了种子 | 2 | | |
| 20 | 2023 | FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long | `10.18653/v1/2023.emnlp-main.741` | 345 | 引用了种子 | 1 | | |
| 21 | 2025 | Hallucination Mitigation for Retrieval-Augmented Large Language Models | `10.3390/math13050856` | 130 | 引用了种子 | 1 | | |
| 22 | 2026 | Retrieval-Augmented Generation for AI-Generated Content: A Survey | `10.1007/s41019-025-00335-5` | 106 | 引用了种子 | 1 | | |
| 23 | 2023 | Generative Relevance Feedback with Large Language Models | `10.1145/3539618.3591992` | 47 | 引用了种子 | 1 | | |
| 24 | 2025 | Improving knowledge management in building engineering with hybrid ret | `10.1016/j.jobe.2025.112189` | 27 | 引用了种子 | 1 | | |
| 25 | 2025 | MemoRAG: Boosting Long Context Processing with Global Memory-Enhanced  | `10.1145/3696410.3714805` | 23 | 引用了种子 | 1 | | |

## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | |
| 日期 | |
| 采纳的候选编号 | |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |
