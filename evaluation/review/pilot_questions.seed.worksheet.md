# 评测问题集人工复核工作表

- 数据集：`evaluation/datasets/pilot_questions.seed.jsonl`
- 问题数：10
- 数据集哈希：`904108e0b340482d0c504f4e49b9b7289e23edbe0f6e58e50b42b62869bdfcca`

复核规则：每道题逐项确认下面的判据，在「决定」处填写 `保留`、`修改` 或 `删除`，
并在「原因」处写明修改内容或删除理由。复核完成后据此生成冻结版数据集，
并把上面的哈希、复核人和日期写进版本记录。

逐题判据：

1. 问题属于计算机/AI 领域，表述清晰，存在明确答案。
2. 两个子问题互不重叠，且都能被 gold evidence 覆盖。
3. 年份范围与问题相符。
4. 每篇 gold paper 都真正回答问题，无重复，DOI 可解析。
5. 每条 quote 是摘要中的完整句子，能独立读懂，不是作者名单或残句。
6. `supports_subquestion` 指向正确的子问题编号。

---

## 1. `csai_001`

**领域**：`llm_rag`　**年份范围**：2022–2026

**问题**：What are the main evaluation methods for retrieval-augmented generation systems?

**子问题**：

1. Which metrics are used?
2. Which datasets and baselines are common?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing. Subquestion(s) 2 have no supporting evidence.

| # | gold paper | 子问题 | quote |
|---:|---|---:|---|
| 1 | `doi:10.48550/arxiv.2312.10997` | 1 | Large Language Models (LLMs) showcase impressive capabilities but encounter challenges like hallucination, outdated knowledge, and non-transparent, untraceable reasoning processes. |
| 2 | `doi:10.1609/aaai.v38i16.29728` | 1 | Retrieval-Augmented Generation (RAG) is a promising approach for mitigating the hallucination of large language models (LLMs). |
| 3 | `doi:10.18653/v1/2024.findings-acl.372` | 1 | While large language models (LLMs) have achieved state-of-the-art performance on a wide range of medical question answering (QA) tasks, they still face challenges with hallucinations and outdated knowledge. |

复核判据：

- [ ] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [ ] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [ ] 判据 5：每条 quote 是完整可读的句子
- [ ] 判据 6：supports_subquestion 指向正确

决定：____（保留 / 修改 / 删除）　原因：________________________________

---

## 2. `csai_002`

**领域**：`llm_rag`　**年份范围**：2022–2026

**问题**：How do agentic tool-use methods differ in planning and memory design?

**子问题**：

1. How is planning represented?
2. How is long-term state retained?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing.

| # | gold paper | 子问题 | quote |
|---:|---|---:|---|
| 1 | `doi:10.7249/mr1626` | 2 | The checkered history of predicting the future — e.g., “Man will never fly” — has dissuaded policymakers from considering the long-term effects of decisions. |
| 2 | `doi:10.1613/jair.575` | 1 | Planning under uncertainty is a central problem in the study of automated sequential decision making, and has been addressed by researchers in many different fields, including AI planning, decision analysis, operations research, control theory and economics. |
| 3 | `doi:10.1080/00461520.2016.1207538` | 1 | Much has been written in the educational psychology literature about effective feedback and how to deliver it. |

复核判据：

- [ ] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [ ] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [ ] 判据 5：每条 quote 是完整可读的句子
- [ ] 判据 6：supports_subquestion 指向正确

决定：____（保留 / 修改 / 删除）　原因：________________________________

---

## 3. `csai_003`

**领域**：`llm_rag`　**年份范围**：2022–2026

**问题**：What are reported limitations of chain-of-thought prompting on reasoning benchmarks?

**子问题**：

1. Which benchmarks expose limitations?
2. Which failure modes are reported?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing. Subquestion(s) 2 have no supporting evidence.

| # | gold paper | 子问题 | quote |
|---:|---|---:|---|
| 1 | `doi:10.1038/s41586-023-06291-2` | 1 | Large language models (LLMs) have demonstrated impressive capabilities, but the bar for clinical applications is high. |
| 2 | `doi:10.1038/s41586-025-09422-z` | 1 | General reasoning represents a long-standing and formidable challenge in artificial intelligence (AI). |

复核判据：

- [ ] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [ ] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [ ] 判据 5：每条 quote 是完整可读的句子
- [ ] 判据 6：supports_subquestion 指向正确

决定：____（保留 / 修改 / 删除）　原因：________________________________

---

## 4. `csai_004`

**领域**：`vision_multimodal`　**年份范围**：2022–2026

**问题**：How do vision-language models align image and text representations?

**子问题**：

1. Which alignment objectives are used?
2. How is alignment evaluated?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing. Subquestion(s) 2 have no supporting evidence.

| # | gold paper | 子问题 | quote |
|---:|---|---:|---|
| 1 | `doi:10.48550/arxiv.2102.05918` | 1 | Pre-trained representations are becoming crucial for many NLP and perception tasks. |
| 2 | `doi:10.48550/arxiv.1910.10683` | 1 | Transfer learning, where a model is first pre-trained on a data-rich task before being fine-tuned on a downstream task, has emerged as a powerful technique in natural language processing (NLP). |
| 3 | `doi:10.48550/arxiv.2107.07651` | 1 | Large-scale vision and language representation learning has shown promising improvements on various vision-language tasks. |

复核判据：

- [ ] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [ ] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [ ] 判据 5：每条 quote 是完整可读的句子
- [ ] 判据 6：supports_subquestion 指向正确

决定：____（保留 / 修改 / 删除）　原因：________________________________

---

## 5. `csai_005`

**领域**：`vision_multimodal`　**年份范围**：2022–2026

**问题**：What evaluation benchmarks are used for multimodal retrieval?

**子问题**：

1. Which datasets are used?
2. Which retrieval metrics are reported?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing. Subquestion(s) 1 have no supporting evidence.

| # | gold paper | 子问题 | quote |
|---:|---|---:|---|
| 1 | `doi:10.1109/cvpr.2016.85` | 2 | Over the years, datasets and benchmarks have proven their fundamental importance in computer vision research, enabling targeted progress and objective comparisons in many fields. |
| 2 | `doi:10.18653/v1/2020.findings-emnlp.445` | 2 | In this paper, we introduce NLP resources for 11 major Indian languages from two major language families. |
| 3 | `doi:10.48550/arxiv.1412.6632` | 2 | In this paper, we present a multimodal Recurrent Neural Network (m-RNN) model for generating novel image captions. |

复核判据：

- [ ] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [ ] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [ ] 判据 5：每条 quote 是完整可读的句子
- [ ] 判据 6：supports_subquestion 指向正确

决定：____（保留 / 修改 / 删除）　原因：________________________________

---

## 6. `csai_006`

**领域**：`nlp_ir`　**年份范围**：2022–2026

**问题**：How does dense retrieval compare with sparse retrieval for scientific search?

**子问题**：

1. What are the reported trade-offs?
2. Which evaluation setups are used?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing. Subquestion(s) 2 have no supporting evidence.

| # | gold paper | 子问题 | quote |
|---:|---|---:|---|
| 1 | `doi:10.18653/v1/2023.acl-long.99` | 1 | While dense retrieval has been shown to be effective and efficient across tasks and languages, it remains difficult to create effective fully zero-shot dense retrieval systems when no relevance labels are available. |
| 2 | `doi:10.1109/tkde.2007.22` | 1 | Semantic search has been one of the motivations of the semantic Web since it was envisioned. |
| 3 | `doi:10.48550/arxiv.2112.09118` | 1 | Recently, information retrieval has seen the emergence of dense retrievers, using neural networks, as an alternative to classical sparse methods based on term-frequency. |

复核判据：

- [ ] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [ ] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [ ] 判据 5：每条 quote 是完整可读的句子
- [ ] 判据 6：supports_subquestion 指向正确

决定：____（保留 / 修改 / 删除）　原因：________________________________

---

## 7. `csai_007`

**领域**：`nlp_ir`　**年份范围**：2022–2026

**问题**：What methods are used for query expansion in neural information retrieval?

**子问题**：

1. What are the main query expansion families?
2. What evidence supports their effectiveness?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing.

| # | gold paper | 子问题 | quote |
|---:|---|---:|---|
| 1 | `doi:10.48550/arxiv.1511.05879` | 1 | Recently, image representation built upon Convolutional Neural Network (CNN) has been shown to provide effective descriptors for image search, outperforming pre-CNN features as short-vector representations. |
| 2 | `doi:10.48550/arxiv.1904.08375` | 1 | One technique to improve the retrieval effectiveness of a search engine is to expand documents with terms that are related or representative of the documents' content. |
| 3 | `doi:10.1145/3404835.3463238` | 2 | Pyserini is a Python toolkit for reproducible information retrieval research with sparse and dense representations. |

复核判据：

- [ ] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [ ] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [ ] 判据 5：每条 quote 是完整可读的句子
- [ ] 判据 6：supports_subquestion 指向正确

决定：____（保留 / 修改 / 删除）　原因：________________________________

---

## 8. `csai_008`

**领域**：`ml_systems`　**年份范围**：2022–2026

**问题**：How do parameter-efficient fine-tuning methods reduce training memory?

**子问题**：

1. Which parameter subsets are updated?
2. What memory and quality trade-offs are reported?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing.

| # | gold paper | 子问题 | quote |
|---:|---|---:|---|
| 1 | `doi:10.1038/s42256-023-00626-4` | 1 | With the prevalence of pre-trained language models (PLMs) and the pre-training–fine-tuning paradigm, it has been continuously shown that larger models tend to yield better performance. |
| 2 | `doi:10.48550/arxiv.2203.02155` | 1 | Making language models bigger does not inherently make them better at following a user's intent. |
| 3 | `doi:10.18653/v1/2022.acl-short.8` | 2 | Prompt tuning, which only tunes continuous prompts with a frozen language model, substantially reduces per-task storage and memory usage at training. |

复核判据：

- [ ] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [ ] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [ ] 判据 5：每条 quote 是完整可读的句子
- [ ] 判据 6：supports_subquestion 指向正确

决定：____（保留 / 修改 / 删除）　原因：________________________________

---

## 9. `csai_009`

**领域**：`ml_systems`　**年份范围**：2022–2026

**问题**：What techniques accelerate transformer inference without retraining?

**子问题**：

1. Which inference-time optimizations are used?
2. What latency and quality trade-offs are reported?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing. Subquestion(s) 1 have no supporting evidence.

| # | gold paper | 子问题 | quote |
|---:|---|---:|---|
| 1 | `doi:10.48550/arxiv.2206.01191` | 2 | Vision Transformers (ViT) have shown rapid progress in computer vision tasks, achieving promising results on various benchmarks. |
| 2 | `doi:10.1109/jproc.2022.3226481` | 2 | Successful integration of deep neural networks (DNNs) or deep learning (DL) has resulted in breakthroughs in many areas. |

复核判据：

- [ ] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [ ] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [ ] 判据 5：每条 quote 是完整可读的句子
- [ ] 判据 6：supports_subquestion 指向正确

决定：____（保留 / 修改 / 删除）　原因：________________________________

---

## 10. `csai_010`

**领域**：`datasets_repro`　**年份范围**：2022–2026

**问题**：What reproducibility practices are reported in machine learning benchmark papers?

**子问题**：

1. Which artifacts and metadata are shared?
2. What barriers to reproducibility are reported?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing.

| # | gold paper | 子问题 | quote |
|---:|---|---:|---|
| 1 | `doi:10.3390/app9204396` | 1 | Networks play important roles in modern life, and cyber security has become a vital research area. |
| 2 | `doi:10.48550/arxiv.2005.00687` | 1 | We present the Open Graph Benchmark (OGB), a diverse set of challenging and realistic benchmark datasets to facilitate scalable, robust, and reproducible graph machine learning (ML) research. |
| 3 | `doi:10.1371/journal.pbio.1002333` | 2 | There is a growing movement to encourage reproducibility and transparency practices in the scientific community, including public access to raw data and protocols, the conduct of replication studies, systematic integration of evidence in systematic reviews, and the documentation of funding and potential conflicts of interest. |

复核判据：

- [ ] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [ ] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [ ] 判据 5：每条 quote 是完整可读的句子
- [ ] 判据 6：supports_subquestion 指向正确

决定：____（保留 / 修改 / 删除）　原因：________________________________

---

## 复核签署

| 字段 | 内容 |
|---|---|
| 复核人 | |
| 复核日期 | |
| 来源数据集哈希 | |
| 冻结版数据集路径 | `evaluation/datasets/pilot_questions.v1.jsonl` |
| 冻结版哈希 | |
| 修改原因汇总 | |
