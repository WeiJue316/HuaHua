# 评测问题集人工复核工作表

- 数据集：`evaluation/datasets/pilot_questions.seed.jsonl`
- 问题数：10
- 数据集哈希：`d45c6b473c56127c821fcfea984a65a4229a308adbaa77a8b061b930285e9ae6`

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
| 2 | `doi:10.1609/aaai.v38i16.29728` | 2024 | 1 | Retrieval-Augmented Generation (RAG) is a promising approach for mitigating the hallucination of large language models (LLMs). |
| 3 | `doi:10.18653/v1/2024.findings-acl.372` | 2024 | 1 | While large language models (LLMs) have achieved state-of-the-art performance on a wide range of medical question answering (QA) tasks, they still face challenges with hallucinations and outdated knowledge. |

复核判据：

- [x] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [x] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [x] 判据 5：每条 quote 是完整可读的句子
- [x] 判据 6：supports_subquestion 指向正确

决定：修改　原因：缺失子问题 2（常用数据集与 Baseline）的证据支持；现有的 3 条 Quote 均为 RAG/LLM 的背景与动机介绍，未能明确回答具体的评估指标（Metrics）。需要替换为针对 RAG 评估框架（如 RAGAS、ARES 等）的论文并补齐子问题 2 证据。

---

## 2. `csai_002`

**领域**：`llm_rag`　**年份范围**：2022–2026

**问题**：How do agentic tool-use methods differ in planning and memory design?

**子问题**：

1. How is planning represented?
2. How is long-term state retained?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing. Relevance threshold relaxed: no strong match was found. Subquestion(s) 2 have no supporting evidence.

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.1145/3586183.3606763` | 2023 | 1 | We demonstrate through ablation that the components of our agent architecture—observation, planning, and reflection—each contribute critically to the believability of agent behavior. |

复核判据：

- [x] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [x] 判据 3：年份范围合适
- [x] 判据 4：gold papers 相关、无重复、DOI 可解析
- [x] 判据 5：每条 quote 是完整可读的句子
- [x] 判据 6：supports_subquestion 指向正确

决定：修改　原因：缺失子问题 2（长期状态与记忆保留机制）的证据支持；且现有论文引文偏向概括，需补充说明具体的 Planning 表征形式以及 Long-term memory retention 机制的相关论文。

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
| 1 | `doi:10.1038/s41586-023-06291-2` | 2023 | 1 | Attempts to assess the clinical knowledge of models typically rely on automated evaluations based on limited benchmarks. |
| 2 | `doi:10.18653/v1/2023.acl-long.147` | 2023 | 1 | Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers). |
| 3 | `doi:10.1038/s41586-025-09422-z` | 2025 | 1 | General reasoning represents a long-standing and formidable challenge in artificial intelligence (AI). |

复核判据：

- [x] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [x] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [ ] 判据 5：每条 quote 是完整可读的句子
- [x] 判据 6：supports_subquestion 指向正确

决定：修改　原因：1. 缺失子问题 2 证据；2. Paper 2 的 quote 为会议论文集标题，违反判据 5（非摘要完整句子）；3. Paper 1 和 Paper 3 的引用仅为泛化的推理或医学基准背景描述，未能明确指出 CoT Prompting 的具体局限性与失效模式。需重新选取针对 CoT 局限性分析（如 Faithful Reasoning, Inverse Scaling）的论文。

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
| 3 | `doi:10.1109/cvpr52688.2022.01631` | 2022 | 1 | With the rise of powerful pre-trained vision-language models like CLIP, it becomes essential to investigate ways to adapt these models to downstream datasets. |

复核判据：

- [x] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [x] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [x] 判据 5：每条 quote 是完整可读的句子
- [x] 判据 6：supports_subquestion 指向正确

决定：修改　原因：缺失子问题 2（对齐效果的评估方法）证据；现有 Quotes 均为 VLP 预训练背景或下游微调（Prompt Tuning）的引言，缺乏明确指出具体的对齐目标（如对比学习、图文匹配 ITM、掩码语言建模 MLM）的针对性句子。

---

## 5. `csai_005`

**领域**：`vision_multimodal`　**年份范围**：2022–2026

**问题**：What evaluation benchmarks are used for multimodal retrieval?

**子问题**：

1. Which datasets are used?
2. Which retrieval metrics are reported?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing. Relevance threshold relaxed: no strong match was found. Subquestion(s) 2 have no supporting evidence.

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.1038/s41591-022-01981-2` | 2022 | 1 | The increasing availability of biomedical data from large biobanks, electronic health records, medical imaging, wearable and ambient biosensors, and the lower cost of genome and microbiome sequencing have set the stage for the development of multimodal artificial intelligence solutions that capture the complexity of human health and disease. |
| 2 | `doi:10.1109/tpami.2023.3275156` | 2023 | 1 | Transformer is a promising neural network learner, and has achieved great success in various machine learning tasks. |

复核判据：

- [x] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [x] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [x] 判据 5：每条 quote 是完整可读的句子
- [x] 判据 6：supports_subquestion 指向正确

决定：修改　原因：论文相关度严重不足。Paper 1 属于生物医疗 AI 综述，Paper 2 为通用 Transformer 介绍，均未提及任何具体的多模态检索数据集（如 Flickr30K, MS-COCO, CIRR 等）或检索指标（Recall@K, mAP）；且缺失子问题 2 证据。需彻底重新选取 gold papers。

---

## 6. `csai_006`

**领域**：`nlp_ir`　**年份范围**：2022–2026

**问题**：How does dense retrieval compare with sparse retrieval for scientific search?

**子问题**：

1. What are the reported trade-offs?
2. Which evaluation setups are used?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing. Subquestion(s) 2 have no supporting evidence.

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.18653/v1/2023.acl-long.99` | 2023 | 1 | While dense retrieval has been shown to be effective and efficient across tasks and languages, it remains difficult to create effective fully zero-shot dense retrieval systems when no relevance labels are available. |
| 2 | `doi:10.48550/arxiv.2308.07107` | 2023 | 1 | As a primary means of information acquisition, information retrieval (IR) systems, such as search engines, have integrated themselves into our daily lives. |

复核判据：

- [x] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [x] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [x] 判据 5：每条 quote 是完整可读的句子
- [x] 判据 6：supports_subquestion 指向正确

决定：修改　原因：缺失子问题 2（评估设置，如 SciFact, NFCorpus 等数据集框架）证据；已有的 Quote 仅讨论了 Zero-shot Dense Retrieval 的痛点或通用 IR 概述，未直接对比 Dense 与 Sparse 在科技文献搜索中的具体权衡（如 Out-of-Domain 泛化、延迟、词表覆盖率等）。

---

## 7. `csai_007`

**领域**：`nlp_ir`　**年份范围**：2022–2026

**问题**：What methods are used for query expansion in neural information retrieval?

**子问题**：

1. What are the main query expansion families?
2. What evidence supports their effectiveness?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing. Relevance threshold relaxed: no strong match was found. Subquestion(s) 2 have no supporting evidence.

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.48550/arxiv.2312.10997` | 2023 | 1 | Large Language Models (LLMs) showcase impressive capabilities but encounter challenges like hallucination, outdated knowledge, and non-transparent, untraceable reasoning processes. |

复核判据：

- [x] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [x] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [x] 判据 5：每条 quote 是完整可读的句子
- [x] 判据 6：supports_subquestion 指向正确

决定：修改　原因：论文存在严重错配。Paper 1 为 RAG 综述（与 `csai_001` 重复），Quote 讨论的是 LLM 幻觉与知识过期，与神经信息检索中的 Query Expansion（如 Doc2Query, PRF, LLM-based query rewriting）完全无关；且缺失子问题 2 证据。

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
| 1 | `doi:10.1038/s42256-023-00626-4` | 2023 | 1 | With the prevalence of pre-trained language models (PLMs) and the pre-training–fine-tuning paradigm, it has been continuously shown that larger models tend to yield better performance. |
| 2 | `doi:10.48550/arxiv.2203.02155` | 2022 | 1 | In human evaluations on our prompt distribution, outputs from the 1.3B parameter InstructGPT model are preferred to outputs from the 175B GPT-3, despite having 100x fewer parameters. |
| 3 | `doi:10.18653/v1/2022.acl-short.8` | 2022 | 2 | Prompt tuning, which only tunes continuous prompts with a frozen language model, substantially reduces per-task storage and memory usage at training. |

复核判据：

- [x] 判据 1：问题清晰且有明确答案
- [x] 判据 2：子问题互不重叠且都有证据覆盖
- [x] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [x] 判据 5：每条 quote 是完整可读的句子
- [x] 判据 6：supports_subquestion 指向正确

决定：修改　原因：Paper 2 (InstructGPT) 探讨的是基于 RLHF 的指令对齐与模型规模偏好，并不属于 PEFT 显存优化范畴；Paper 1 仅为预训练范式背景。建议移除 Paper 2，并补充专门阐述参数子集更新（如 LoRA 冻结主干只更新低秩矩阵、Adapter 插入模块）的论文作为子问题 1 的直接证据。

---

## 9. `csai_009`

**领域**：`ml_systems`　**年份范围**：2022–2026

**问题**：What techniques accelerate transformer inference without retraining?

**子问题**：

1. Which inference-time optimizations are used?
2. What latency and quality trade-offs are reported?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing. Subquestion(s) 1 have no supporting evidence.

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.48550/arxiv.2206.01191` | 2022 | 2 | Our fastest model, EfficientFormer-L1, achieves $79.2\%$ top-1 accuracy on ImageNet-1K with only $1.6$ ms inference latency on iPhone 12 (compiled with CoreML), which runs as fast as MobileNetV2$\times 1.4$ ($1.6$ ms, $74.7\%$ top-1), and our largest model, EfficientFormer-L7, obtains $83.3\%$ accuracy with only $7.0$ ms latency. |
| 2 | `doi:10.1109/jproc.2022.3226481` | 2022 | 2 | Data transmission to the cloud results in high latency, round-trip delay, security and privacy concerns, and the inability of real-time decisions. |

复核判据：

- [x] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [x] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [x] 判据 5：每条 quote 是完整可读的句子
- [x] 判据 6：supports_subquestion 指向正确

决定：修改　原因：1. 缺失子问题 1（具体推理优化技术）证据；2. Paper 1 (EfficientFormer) 为重新设计的网络架构，需要从头训练，不符合“无需重训练（without retraining）”的前提限制。需要替换为 FlashAttention, vLLM (KV Caching), PTQ (后训练量化) 等免重训练技术的论文并补充子问题 1 证据。

---

## 10. `csai_010`

**领域**：`datasets_repro`　**年份范围**：2022–2026

**问题**：What reproducibility practices are reported in machine learning benchmark papers?

**子问题**：

1. Which artifacts and metadata are shared?
2. What barriers to reproducibility are reported?

> 生成备注：Seed annotation generated from OpenAlex metadata; requires human verification before freezing. Subquestion(s) 2 have no supporting evidence.

| # | gold paper | 年份 | 子问题 | quote |
|---:|---|---:|---:|---|
| 1 | `doi:10.1109/access.2023.3262138` | 2023 | 1 | The final goal of all industrial machine learning (ML) projects is to develop ML products and rapidly bring them into production. |
| 2 | `doi:10.1145/3582302.3582306` | 2023 | 1 | The explorative and iterative nature of developing and operating ML applications leads to a variety of artifacts, such as datasets, features, models, hyperparameters, metrics, software, configurations, and logs. |

复核判据：

- [x] 判据 1：问题清晰且有明确答案
- [ ] 判据 2：子问题互不重叠且都有证据覆盖
- [x] 判据 3：年份范围合适
- [ ] 判据 4：gold papers 相关、无重复、DOI 可解析
- [x] 判据 5：每条 quote 是完整可读的句子
- [x] 判据 6：supports_subquestion 指向正确

决定：修改　原因：缺失子问题 2（可复现性障碍）证据；Paper 1 属于工业界 ML 产品落地的背景介绍，与 Benchmark 论文中的学术可复现性实践关联较弱。建议将 Paper 1 替换为专门探讨基准测试可复现性困难/屏障的文献，并补齐子问题 2 证据。

---

## 复核签署

| 字段 | 内容 |
|---|---|
| 复核人 | Senior Evaluation Reviewer |
| 复核日期 | 2026-09-23 |
| 来源数据集哈希 | `d45c6b473c56127c821fcfea984a65a4229a308adbaa77a8b061b930285e9ae6` |
| 冻结版数据集路径 | `evaluation/datasets/pilot_questions.v1.jsonl` |
| 冻结版哈希 | 待修正并生成 JSONL 后计算产生 |
| 修改原因汇总 | 1. **补充缺失证据**：几乎所有题目（除 csai_008 外）均存在子问题 2 缺少 gold evidence 的情况，需补采集；<br>2. **替换无关/偏离论文**：csai_005 (生物医疗/通用Transformer)、csai_007 (错误采入RAG论文)、csai_008 (采入InstructGPT/RLHF)、csai_009 (采入需重新训练的架构设计) 需要更精准匹配论文；<br>3. **修正格式与引文质量**：csai_003 包含会议论文集标题残句，多道题目的引文仅为 generic background，需提炼能直接回答问题的精准句子。 |