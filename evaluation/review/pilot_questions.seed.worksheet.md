# 评测问题集人工复核工作表

- 数据集：`evaluation/datasets/pilot_questions.seed.jsonl`
- 问题数：10
- 数据集哈希：`e7ed21c8567713f7341fafccf64242d030b05b4c4ef1b212ebd1f57a3a9be46b`

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

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.48550/arxiv.2312.10997` | 2023 | 1 | Large Language Models (LLMs) showcase impressive capabilities but encounter challenges like hallucination, outdated knowledge, and non-transparent, untraceable reasoning processes. |

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

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.1145/3586183.3606763` | 2023 | 1 | We demonstrate through ablation that the components of our agent architecture—observation, planning, and reflection—each contribute critically to the believability of agent behavior. |
| 2 | `doi:10.1109/mlcad65511.2025.11189204` | 2025 | 2 | ORFS-agent adaptively explores parameter configurations, demonstrating clear improvements over standard Bayesian optimization approaches in terms of resource efficiency and final design metrics. |
| 3 | `doi:10.1007/s10462-022-10246-w` | 2022 | 2 | This collaboration between AI models and humans should not be limited only to the learning process; if we go further, we can see other terms that arise such as Usable and Useful AI. |

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

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.1038/s41586-023-06291-2` | 2023 | 1 | Here, to address these limitations, we present MultiMedQA, a benchmark combining six existing medical question answering datasets spanning professional medicine, research and consumer queries and a new dataset of medical questions searched online, HealthSearchQA. |
| 2 | `doi:10.1038/s41586-025-09422-z` | 2025 | 1 | General reasoning represents a long-standing and formidable challenge in artificial intelligence (AI). |

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

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.48550/arxiv.2201.12086` | 2022 | 1 | Vision-Language Pre-training (VLP) has advanced the performance for many vision-language tasks. |
| 2 | `doi:10.48550/arxiv.2301.12597` | 2023 | 1 | The cost of vision-and-language pre-training has become increasingly prohibitive due to end-to-end training of large-scale models. |

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

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing.

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.1609/aaai.v38i16.29728` | 2024 | 2 | Retrieval-Augmented Generation (RAG) is a promising approach for mitigating the hallucination of large language models (LLMs). |
| 2 | `doi:10.48550/arxiv.2312.10997` | 2023 | 2 | Retrieval-Augmented Generation (RAG) has emerged as a promising solution by incorporating knowledge from external databases. |
| 3 | `doi:10.1109/slt54892.2023.10023141` | 2023 | 1 | FLEURS is an n-way parallel speech dataset in 102 languages built on top of the machine translation FLoRes-101 benchmark, with approximately 12 hours of speech supervision per language. |

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

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing.

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.18653/v1/2023.acl-long.99` | 2023 | 1 | While dense retrieval has been shown to be effective and efficient across tasks and languages, it remains difficult to create effective fully zero-shot dense retrieval systems when no relevance labels are available. |
| 2 | `doi:10.1109/tpami.2022.3218591` | 2022 | 2 | Our survey considers a wide variety of recent methods, whereby we identify milestone work, reveal connections among various methods and present the commonly used benchmarks, evaluation results, common challenges, and propose promising future directions. |
| 3 | `doi:10.1093/bioinformatics/btad651` | 2023 | 2 | In addition, MedCPT also generates better biomedical article and sentence representations for semantic evaluations. |

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

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing. Subquestion(s) 2 have no supporting evidence.

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.18653/v1/2023.emnlp-main.585` | 2023 | 1 | This paper introduces a simple yet effective query expansion approach, denoted as query2doc, to improve both sparse and dense retrieval systems. |
| 2 | `doi:10.1093/gpbjnl/qzaf072` | 2025 | 1 | The Genome Sequence Archive family (GSA family) provides a comprehensive suite of database resources for archiving, retrieving, and sharing multi-omics data for the global academic and industrial communities. |

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

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.1038/s42256-023-00626-4` | 2023 | 1 | However, as PLMs scale up, fine-tuning and storing all the parameters is prohibitively costly and eventually becomes practically infeasible. |
| 2 | `doi:10.48550/arxiv.2203.02155` | 2022 | 1 | In human evaluations on our prompt distribution, outputs from the 1.3B parameter InstructGPT model are preferred to outputs from the 175B GPT-3, despite having 100x fewer parameters. |
| 3 | `doi:10.18653/v1/2022.acl-short.8` | 2022 | 2 | Prompt tuning, which only tunes continuous prompts with a frozen language model, substantially reduces per-task storage and memory usage at training. |

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

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing. Subquestion(s) 2 have no supporting evidence.

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.1201/9781003162810-13` | 2022 | 1 | Achieving efficient, real-time NNs with optimal accuracy requires rethinking the design, training, and deployment of NN models. |
| 2 | `doi:10.48550/arxiv.2206.01191` | 2022 | 1 | Our fastest model, EfficientFormer-L1, achieves $79.2\%$ top-1 accuracy on ImageNet-1K with only $1.6$ ms inference latency on iPhone 12 (compiled with CoreML), which runs as fast as MobileNetV2$\times 1.4$ ($1.6$ ms, $74.7\%$ top-1), and our largest model, EfficientFormer-L7, obtains $83.3\%$ accuracy with only $7.0$ ms latency. |

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

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.1016/j.patter.2023.100804` | 2023 | 2 | We systematically investigate reproducibility issues in ML-based science. |
| 2 | `doi:10.1109/access.2023.3262138` | 2023 | 1 | The final goal of all industrial machine learning (ML) projects is to develop ML products and rapidly bring them into production. |
| 3 | `doi:10.1145/3582302.3582306` | 2023 | 1 | The explorative and iterative nature of developing and operating ML applications leads to a variety of artifacts, such as datasets, features, models, hyperparameters, metrics, software, configurations, and logs. |

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
