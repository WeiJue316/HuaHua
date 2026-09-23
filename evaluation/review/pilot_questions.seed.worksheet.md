# 评测问题集人工复核工作表

- 数据集：`evaluation/datasets/pilot_questions.seed.jsonl`
- 问题数：10
- 数据集哈希：`ce5516b789fbfc347ec6c97c972bdcc9eea99e3d562d9ab4d9cf862240eff0e3`

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
| 1 | `doi:10.18653/v1/2024.eacl-demo.16` | 2024 | 1 | With RAGAs, we introduce a suite of metrics that can evaluate these different dimensions without relying on ground truth human annotations. |
| 2 | `doi:10.18653/v1/2024.naacl-long.20` | 2024 | 2 | Across eight different knowledge-intensive tasks in KILT, SuperGLUE, and AIS, ARES accurately evaluates RAG systems while using only a few hundred human annotations during evaluation. |
| 3 | `doi:10.48550/arxiv.2312.10997` | 2023 | 1 | Furthermore, this paper introduces up-to-date evaluation framework and benchmark. |

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
| 2 | `doi:10.48550/arxiv.2402.02716` | 2024 | 1 | We provide a taxonomy of existing works on LLM-Agent planning, which can be categorized into Task Decomposition, Plan Selection, External Module, Reflection and Memory. |
| 3 | `doi:10.48550/arxiv.2310.08560` | 2023 | 2 | To enable using context beyond limited context windows, we propose virtual context management, a technique drawing inspiration from hierarchical memory systems in traditional operating systems that provide the appearance of large memory resources through data movement between fast and slow memory. |

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
| 1 | `doi:10.48550/arxiv.2305.04388` | 2023 | 2 | However, we find that CoT explanations can systematically misrepresent the true reason for a model's prediction. |
| 2 | `doi:10.48550/arxiv.2410.05229` | 2024 | 1 | To overcome the limitations of existing evaluations, we introduce GSM-Symbolic, an improved benchmark created from symbolic templates that allow for the generation of a diverse set of questions. |

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
| 1 | `doi:10.48550/arxiv.2204.03162` | 2022 | 2 | We present a novel task and dataset for evaluating the ability of vision and language models to conduct visio-linguistic compositional reasoning, which we call Winoground. |
| 2 | `doi:10.1007/s11633-022-1369-5` | 2023 | 1 | To give readers a better overall grasp of VLP, we first review its recent advances in five aspects: feature extraction, model architecture, pre-training objectives, pre-training datasets, and downstream tasks. |
| 3 | `doi:10.48550/arxiv.2301.12597` | 2023 | 1 | The first stage bootstraps vision-language representation learning from a frozen image encoder. The second stage bootstraps vision-to-language generative learning from a frozen language model. |

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
| 1 | `doi:10.1145/3580501` | 2022 | 1 | Extensive experiments are conducted on two widely used datasets, namely, Flickr30k and MSCOCO, to demonstrate the superiority of the proposed MKVSE approach in achieving state-of-the-art performances. |
| 2 | `doi:10.18653/v1/2024.emnlp-main.373` | 2024 | 2 | Additionally, in a mixed-modality task of slide retrieval, DSE significantly outperforms OCR text retrieval methods by over 15 points in nDCG@10. |

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
| 2 | `doi:10.18653/v1/2022.findings-emnlp.347` | 2022 | 2 | In this work, we present SCIFACT-OPEN, a new test collection designed to evaluate the performance of scientific claim verification systems on a corpus of 500K research abstracts. |

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
| 2 | `doi:10.48550/arxiv.2305.03653` | 2023 | 2 | Experimental results on MS-MARCO and BEIR demonstrate that query expansions generated by LLMs can be more powerful than traditional query expansion methods. |

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
| 1 | `doi:10.18653/v1/2022.acl-short.8` | 2022 | 2 | Prompt tuning, which only tunes continuous prompts with a frozen language model, substantially reduces per-task storage and memory usage at training. |
| 2 | `doi:10.1038/s42256-023-00626-4` | 2023 | 1 | This necessitates a new branch of research focusing on the parameter-efficient adaptation of PLMs, which optimizes a small portion of the model parameters while keeping the rest fixed, drastically cutting down computation and storage costs. |
| 3 | `doi:10.18653/v1/2022.acl-short.1` | 2022 | 1 | We introduce BitFit, a sparse-finetuning method where only the bias-terms of the model (or a subset of them) are being modified. |

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
| 1 | `doi:10.48550/arxiv.2211.10438` | 2022 | 2 | We demonstrate up to 1.56x speedup and 2x memory reduction for LLMs with negligible loss in accuracy. |
| 2 | `doi:10.1201/9781003162810-13` | 2022 | 1 | This chapter provides approaches to the problem of quantizing the numerical values in deep Neural Network computations, covering the advantages/disadvantages of current methods. |

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
| 2 | `doi:10.1145/3582302.3582306` | 2023 | 1 | The explorative and iterative nature of developing and operating ML applications leads to a variety of artifacts, such as datasets, features, models, hyperparameters, metrics, software, configurations, and logs. |

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
