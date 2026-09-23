# 金标候选：csai_006

**问题**：How does dense retrieval compare with sparse retrieval for scientific search?

　　→ 在科学检索中，稠密检索与稀疏检索相比如何？

**子问题**：

1. What are the reported trade-offs?
　　→ 已报告的权衡是什么？

2. Which evaluation setups are used?
　　→ 使用了哪些评估设置？


**现有 gold**：2 篇　**年份范围**：(2022, 2026)　**引用图候选**：25 篇

## 判定标准

一篇论文算作 gold，当且仅当**领域专家会把它作为回答某个子问题的证据引用**。
按子问题分别判定，因为证据是按子问题分配的。

**「初审建议」是模型预判，只是给你省时间，不是结论。**
最终「判定」必须由你确认——金标是评测系统的尺子，
由被测系统自己判定会构成循环论证，项目评测设计也禁止这样做。

逐条检查：

1. 论文是否真正回答某个子问题（不是主题相邻）
2. 年份是否在声明范围内
3. 摘要是否包含可以作为证据的完整句子
4. 判定它支撑哪个子问题（填编号）

## 候选清单

| # | 年份 | 标题 | 中文标题(机翻) | DOI | 被引 | 关系 | 命中 | 初审建议 | 判定 | 子问题 | 备注 |
|---:|---:|---|---|---|---:|---|---:|---|---:|---|
| 1 | 2023 | Is ChatGPT Good at Search? Investigating Large Language Models as Re-R | ChatGPT擅长搜索吗？探究大语言模型作为重排序智能体 | `10.18653/v1/2023.emnlp-main.923` | 230 | 引用了种子 | 3 | 建议不采纳 | | | 该文研究的是用LLM进行重排序（RankGPT），未涉及稠密检索与稀疏检索的对比或相关评测设置，属主题相邻（信息检索/排序）而非直接证据。 |
| 2 | 2025 | Retrieval augmented generation for large language models in healthcare | 医疗保健领域大语言模型的检索增强生成：一项系统综述 | `10.1371/journal.pdig.0000877` | 226 | 引用了种子 | 3 | 建议不采纳 | | | 该文是医疗健康领域RAG的系统综述，未比较稠密与稀疏检索在科学搜索中的权衡或评估设置，属于主题相邻但不相关。 |
| 3 | 2023 | Query2doc: Query Expansion with Large Language Models | Query2doc：基于大语言模型的查询扩展 | `10.18653/v1/2023.emnlp-main.585` | 188 | 引用了种子 | 3 | 建议不采纳 | | | 主题相邻：该文虽同时涉及稀疏与稠密检索，但未报告二者权衡比较，且评测为通用 ad-hoc IR 数据集而非科学搜索场景。 |
| 4 | 2024 | Fine-Tuning LLaMA for Multi-Stage Text Retrieval | 面向多阶段文本检索的LLaMA微调 | `10.1145/3626772.3657951` | 112 | 引用了种子 | 3 | 建议不采纳 | | | 主题相邻：论文聚焦微调 LLaMA 作为稠密检索器和重排器，并未比较稠密与稀疏检索在科学搜索中的权衡或相应评测设置。 |
| 5 | 2025 | Evaluating Retrieval-Augmented Generation Variants for Clinical Decisi | 评估面向临床决策支持的检索增强生成变体：幻觉缓解与安全本地化部署 | `10.3390/electronics14214227` | 14 | 引用了种子 | 3 | 建议不采纳 | | | 主题相邻：该文评估临床决策支持中的RAG检索变体，而非科学检索场景下的稠密与稀疏检索对比。 |
| 6 | 2022 | Unsupervised Corpus Aware Language Model Pre-training for Dense Passag | 面向稠密段落检索的无监督语料感知语言模型预训练 | `10.18653/v1/2022.acl-long.203` | 144 | 被种子引用 | 2 | 建议不采纳 | | | 论文仅讨论稠密检索器的训练方法与评估数据集，未涉及与稀疏检索的对比或科学搜索场景，属于主题相邻而非直接证据。 |
| 7 | 2023 | The Information Retrieval Experiment Platform | 信息检索实验平台 | `10.1145/3539618.3591888` | 54 | 引用了种子 | 2 | 建议不采纳 | | | 该论文描述了通用 IR 实验平台（TIREx/TIRA）的基础设施，而并未报告任何针对科学检索中稠密与稀疏检索比较的评估设置，因此仅为主题相邻。 |
| 8 | 2023 | Large Language Models Know Your Contextual Search Intent: A Prompting  | 大语言模型了解你的上下文搜索意图：面向会话搜索的提示框架 | `10.18653/v1/2023.findings-emnlp.86` | 49 | 引用了种子 | 2 | 建议不采纳 | | | 该论文研究基于LLM提示的对话式搜索意图理解与查询重写，未涉及稠密与稀疏检索在科学搜索中的比较，因此仅属主题相邻而非直接证据。 |
| 9 | 2024 | Soft prompt tuning for augmenting dense retrieval with large language  | 利用大语言模型增强稠密检索的软提示调优 | `10.1016/j.knosys.2024.112758` | 26 | 引用了种子 | 2 | 建议不采纳 | | | 主题相邻：论文聚焦于用软提示调优增强稠密检索，并未比较稠密检索与稀疏检索，也未涉及科学搜索场景下的权衡或评估设置。 |
| 10 | 2024 | Generative Multi-Modal Knowledge Retrieval with Large Language Models | 基于大语言模型的生成式多模态知识检索 | `10.1609/aaai.v38i17.29837` | 24 | 引用了种子 | 2 | 建议不采纳 | | | 该论文研究基于LLM的多模态生成式知识检索，未涉及稠密与稀疏检索在科学搜索中的比较，属于主题相邻（多模态检索）而非直接证据。 |
| 11 | 2025 | Retrieval-Augmented Generation to Generate Knowledge Assets and Creati | 检索增强生成用于生成知识资产与创建行动驱动因素 | `10.3390/app15116247` | 22 | 引用了种子 | 2 | 建议不采纳 | | | 主题相邻：该文讨论RAG架构与检索增强技术，但未比较稠密与稀疏检索在科学搜索中的权衡或评估设置。 |
| 12 | 2024 | Customized Retrieval Augmented Generation and Benchmarking for EDA Too | 面向EDA工具文档问答的定制化检索增强生成与基准测试 | `10.1145/3676536.3676730` | 21 | 引用了种子 | 2 | 建议不采纳 | | | 主题相邻：该论文聚焦于EDA工具文档QA的定制RAG框架与基准，未比较稠密与稀疏检索的权衡或评估设置。 |
| 13 | 2025 | MoRSE: Bridging the Gap in Cybersecurity Expertise with Retrieval Augm | MoRSE：利用检索增强生成弥合网络安全专业知识差距 | `10.1145/3672608.3707898` | 14 | 引用了种子 | 2 | 建议不采纳 | | | 该论文聚焦网络安全领域的RAG聊天机器人系统，虽涉及检索但未比较稠密与稀疏检索，也未针对科学搜索场景，属于主题相邻。 |
| 14 | 2025 | Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs)  | 面向企业知识管理与文档自动化的检索增强生成（RAG）与大语言模型（LLMs）：系统性文献综述 | `10.3390/app16010368` | 11 | 引用了种子 | 2 | 建议不采纳 | | | 主题相邻：该文综述企业知识管理中的RAG/LLM，涉及检索框架与评估方法，但未比较面向科学搜索的稠密与稀疏检索及其权衡或评估设置。 |
| 15 | 2023 | SCITAB: A Challenging Benchmark for Compositional Reasoning and Claim  | SCITAB：一个用于科学表格组合推理与声明验证的挑战性基准 | `10.18653/v1/2023.emnlp-main.483` | 9 | 引用了种子 | 2 | 建议不采纳 | | | 该论文研究科学表格上的声明验证基准，完全不涉及稠密与稀疏检索的比较，属于科学NLP但检索主题之外的完全无关工作。 |
| 16 | 2025 | An In-depth Analysis of the Linguistic Characteristics of Science Clai | 网络科学主张的语言特征及其对事实核查影响的深入分析 | `10.1145/3746170` | 2 | 引用了种子 | 2 | 建议不采纳 | | | 该论文研究科学网络声明的语言学特征及其对事实核查的影响，虽涉及科学文本与BERT模型，但未比较稠密检索与稀疏检索，也未报告相关权衡或评测设置，属主题相邻而非直接相关。 |
| 17 | 2025 | The Next Phase of Scientific Fact-Checking: Advanced Evidence Retrieva | 科学事实核查的下一阶段：从复杂结构化学术论文中进行高级证据检索 | `10.1145/3731120.3744614` | 2 | 引用了种子 | 2 | 建议不采纳 | | | 主题相邻：论文关注科学事实核查中的证据检索，但未涉及稠密与稀疏检索的对比或相应评估设置。 |
| 18 | 2025 | +VeriRel: Verification Feedback to Enhance Document Retrieval for Scie | +VeriRel：验证反馈以增强科学事实核查的文档检索 | `10.1145/3746252.3760822` | 1 | 引用了种子 | 2 | 建议不采纳 | | | 主题相邻：该文聚焦科学事实核查中的文档检索与验证反馈，但未比较密集检索与稀疏检索，也未报告二者权衡或相关评估设置。 |
| 19 | 2023 | The student becomes the master: Outperforming GPT3 on Scientific Factu | 学生成为大师：在科学事实性错误纠正上超越 GPT3 | `10.18653/v1/2023.findings-emnlp.451` | 0 | 引用了种子 | 2 | 建议不采纳 | | | 该论文研究科学事实性错误纠正（SciFix），虽同属科学主张验证领域且使用SciFact数据集，但未涉及稠密检索与稀疏检索的对比或相关评测设置，属于主题相邻而非直接证据。 |
| 20 | 2023 | FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long | FActScore：长文本生成中事实精确度的细粒度原子评估 | `10.18653/v1/2023.emnlp-main.741` | 345 | 引用了种子 | 1 | 建议不采纳 | | | 该论文提出的是长文本生成事实精确度的细粒度评估方法（FActScore），与稠密/稀疏检索的对比或其评估设置完全无关，属于完全无关。 |
| 21 | 2025 | Hallucination Mitigation for Retrieval-Augmented Large Language Models | 检索增强大语言模型的幻觉缓解：综述 | `10.3390/math13050856` | 130 | 引用了种子 | 1 | 建议不采纳 | | | 主题相邻：该综述讨论检索增强大语言模型的幻觉缓解，并未比较稠密检索与稀疏检索在科学搜索中的权衡或评测设置。 |
| 22 | 2026 | Retrieval-Augmented Generation for AI-Generated Content: A Survey | 面向AI生成内容的检索增强生成：综述 | `10.1007/s41019-025-00335-5` | 106 | 引用了种子 | 1 | 建议不采纳 | | | 主题相邻：该论文综述RAG在AIGC中的应用，未具体比较稠密与稀疏检索在科学搜索中的权衡或评估设置。 |
| 23 | 2023 | Generative Relevance Feedback with Large Language Models | 基于大语言模型的生成式相关性反馈 | `10.1145/3539618.3591992` | 47 | 引用了种子 | 1 | 建议不采纳 | | | 主题相邻：该论文研究生成式相关反馈与查询扩展在通用文档检索中的效果，未比较稠密与稀疏检索，也未针对科学搜索的权衡或评测设置。 |
| 24 | 2025 | Improving knowledge management in building engineering with hybrid ret | 利用混合检索增强生成框架改进建筑工程中的知识管理 | `10.1016/j.jobe.2025.112189` | 27 | 引用了种子 | 1 | 无法判断 | | | 源站未提供摘要，需另行获取 |
| 25 | 2025 | MemoRAG: Boosting Long Context Processing with Global Memory-Enhanced  | MemoRAG：通过全局记忆增强的检索增强提升长上下文处理 | `10.1145/3696410.3714805` | 23 | 引用了种子 | 1 | 建议不采纳 | | | 该论文聚焦长上下文RAG与全局记忆增强，未比较稠密与稀疏检索在科学搜索中的权衡或评测设置，属于主题相邻。 |

## 摘要（判定用）

判据 3 要求确认摘要里存在可作为证据的完整句子，因此这里附上原文摘要。
机翻标题仅供快速定位，**判定必须依据英文原文**。

**1. Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents**

- DOI：`10.18653/v1/2023.emnlp-main.923`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

Large Language Models (LLMs) have demonstrated remarkable zero-shot generalization across various language-related tasks, including search engines.However, existing work utilizes the generative ability of LLMs for Information Retrieval (IR) rather than direct passage ranking.The discrepancy between the pretraining objectives of LLMs and the ranking objective poses another challenge.In this paper, we first investigate generative LLMs such as ChatGPT and GPT-4 for relevance ranking in IR.Surprisingly, our experiments reveal that properly instructed LLMs can deliver competitive, even superior results to state-of-the-art supervised methods on popular IR benchmarks.Furthermore, to address concerns about data contamination of LLMs, we collect a new test set called NovelEval, based on the latest knowledge and aiming to verify the model's ability to rank unknown knowledge.Finally, to improve efficiency in real-world applications, we delve into the potential for distilling the ranking capabilities of ChatGPT into small specialized models using a permutation distillation scheme.Our evaluation results turn out that a distilled 440M model outperforms a 3B supervised model on the BEIR benchmark.The code to reproduce our results is available at www.github.com/sunnweiwei/RankGPT.

**2. Retrieval augmented generation for large language models in healthcare: A systematic review**

- DOI：`10.1371/journal.pdig.0000877`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

Large Language Models (LLMs) have demonstrated promising capabilities to solve complex tasks in critical sectors such as healthcare. However, LLMs are limited by their training data which is often outdated, the tendency to generate inaccurate ("hallucinated") content and a lack of transparency in the content they generate. To address these limitations, retrieval augmented generation (RAG) grounds the responses of LLMs by exposing them to external knowledge sources. However, in the healthcare domain there is currently a lack of systematic understanding of which datasets, RAG methodologies and evaluation frameworks are available. This review aims to bridge this gap by assessing RAG-based approaches employed by LLMs in healthcare, focusing on the different steps of retrieval, augmentation and generation. Additionally, we identify the limitations, strengths and gaps in the existing literature. Our synthesis shows that 78.9% of studies used English datasets and 21.1% of the datasets are in Chinese. We find that a range of techniques are employed RAG-based LLMs in healthcare, including Naive RAG, Advanced RAG, and Modular RAG. Surprisingly, proprietary models such as GPT-3.5/4 are the most used for RAG applications in healthcare. We find that there is a lack of standardised evaluation frameworks for RAG-based applications. In addition, the majority of the studies do not assess or address ethical considerations related to RAG in healthcare. It is important to account for ethical challenges that are inherent when AI systems are implemented in the clinical setting. Lastly, we highlight the need for further research and development to ensure responsible and effective adoption of RAG in the medical domain.

**3. Query2doc: Query Expansion with Large Language Models**

- DOI：`10.18653/v1/2023.emnlp-main.585`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

This paper introduces a simple yet effective query expansion approach, denoted as query2doc, to improve both sparse and dense retrieval systems.The proposed method first generates pseudo-documents by few-shot prompting large language models (LLMs), and then expands the query with generated pseudodocuments.LLMs are trained on web-scale text corpora and are adept at knowledge memorization.The pseudo-documents from LLMs often contain highly relevant information that can aid in query disambiguation and guide the retrievers.Experimental results demonstrate that query2doc boosts the performance of BM25 by 3% to 15% on ad-hoc IR datasets, such as MS-MARCO and TREC DL, without any model fine-tuning.Furthermore, our method also benefits state-of-the-art dense retrievers in terms of both in-domain and out-ofdomain results.

**4. Fine-Tuning LLaMA for Multi-Stage Text Retrieval**

- DOI：`10.1145/3626772.3657951`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

While large language models (LLMs) have shown impressive NLP capabilities, existing IR applications mainly focus on prompting LLMs to generate query expansions or generating permutations for listwise reranking. In this study, we leverage LLMs directly to serve as components in the widely used multi-stage text ranking pipeline. Specifically, we fine-tune the open-source LLaMA-2 model as a dense retriever (repLLaMA) and a pointwise reranker (rankLLaMA). This is performed for both passage and document retrieval tasks using the MS MARCO training data. Our study shows that finetuned LLM retrieval models outperform smaller models. They are more effective and exhibit greater generalizability, requiring only a straightforward training strategy. Moreover, our pipeline allows for the fine-tuning of LLMs at each stage of a multi-stage retrieval pipeline. This demonstrates the strong potential for optimizing LLMs to enhance a variety of retrieval tasks. Furthermore, as LLMs are naturally pre-trained with longer contexts, they can directly represent longer documents. This eliminates the need for heuristic segmenting and pooling strategies to rank long documents. On the MS MARCO and BEIR datasets, our repLLaMA-rankLLaMA pipeline demonstrates a high level of effectiveness.

**5. Evaluating Retrieval-Augmented Generation Variants for Clinical Decision Support: Hallucination Mitigation and Secure On-Premises Deployment**

- DOI：`10.3390/electronics14214227`
- 关联种子：`doi:10.18653/v1/2022.findings-emnlp.347`（引用了种子）

For clinical decision support to work, medical knowledge needs to be easy to find quickly and accurately. Retrieval-Augmented Generation (RAG) systems use big language models and document retrieval to help with diagnostic reasoning, but they could cause hallucinations and have strict privacy rules in healthcare. We tested twelve different types of RAG, such as dense, sparse, hybrid, graph-based, multimodal, self-reflective, adaptive, and security-focused pipelines, on 250 de-identified patient vignettes. We used Precision@5, Mean Reciprocal Rank, nDCG@10, hallucination rate, and latency to see how well the system worked. The best retrieval accuracy (P@5 ≥ 0.68, nDCG@10 ≥ 0.67) was achieved by a Haystack pipeline (DPR + BM25 + cross-encoder) and hybrid fusion (RRF). Self-reflective RAG, on the other hand, lowered hallucinations to 5.8%. Sparse retrieval gave the fastest response (120 ms), but it was not as accurate. We also suggest a single framework for reducing hallucinations that includes retrieval confidence thresholds, chain-of-thought verification, and outside fact-checking. Our findings emphasize pragmatic protocols for the secure implementation of RAG on premises, incorporating encryption, provenance tagging, and audit trails. Future directions encompass the incorporation of clinician feedback and the expansion of multimodal inputs to genomics and proteomics for precision medicine.

**6. Unsupervised Corpus Aware Language Model Pre-training for Dense Passage Retrieval**

- DOI：`10.18653/v1/2022.acl-long.203`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（被种子引用）

Recent research demonstrates the effectiveness of using fine-tuned language models (LM) for dense retrieval.However, dense retrievers are hard to train, typically requiring heavily engineered fine-tuning pipelines to realize their full potential.In this paper, we identify and address two underlying problems of dense retrievers: i) fragility to training data noise and ii) requiring large batches to robustly learn the embedding space.We use the recently proposed Condenser pre-training architecture, which learns to condense information into the dense vector through LM pre-training.On top of it, we propose coCondenser, which adds an unsupervised corpus-level contrastive loss to warm up the passage embedding space.Experiments on MS-MARCO, Natural Question, and Trivia QA datasets show that coCondenser removes the need for heavy data engineering such as augmentation, synthesis, or filtering, and the need for large batch training.It shows comparable performance to RocketQA, a state-of-the-art, heavily engineered system, using simple small batch fine-tuning. 1

**7. The Information Retrieval Experiment Platform**

- DOI：`10.1145/3539618.3591888`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

We integrate irdatasets, ir_measures, and PyTerrier with TIRA in the Information Retrieval Experiment Platform (TIREx) to promote more standardized, reproducible, scalable, and even blinded retrieval experiments. Standardization is achieved when a retrieval approach implements PyTerrier's interfaces and the input and output of an experiment are compatible with ir_datasets and ir_measures. However, none of this is a must for reproducibility and scalability, as TIRA can run any dockerized software locally or remotely in a cloud-native execution environment. Version control and caching ensure efficient (re)execution. TIRA allows for blind evaluation when an experiment runs on a remote server or cloud not under the control of the experimenter. The test data and ground truth are then hidden from public access, and the retrieval software has to process them in a sandbox that prevents data leaks.

**8. Large Language Models Know Your Contextual Search Intent: A Prompting Framework for Conversational Search**

- DOI：`10.18653/v1/2023.findings-emnlp.86`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

Precisely understanding users' contextual search intent has been an important challenge for conversational search.As conversational search sessions are much more diverse and long-tailed, existing methods trained on limited data still show unsatisfactory effectiveness and robustness to handle real conversational search scenarios.Recently, large language models (LLMs) have demonstrated amazing capabilities for text generation and conversation understanding.In this work, we present a simple yet effective prompting framework, called LLM4CS, to leverage LLMs as a textbased search intent interpreter to help conversational search.Under this framework, we explore three prompting methods to generate multiple query rewrites and hypothetical responses, and propose to aggregate them into an integrated representation that can robustly represent the user's real contextual search intent.Extensive automatic evaluations and human evaluations on three widely used conversational search benchmarks, including CAsT-19, CAsT-20, and CAsT-21, demonstrate the remarkable performance of our simple LLM4CS framework compared with existing methods and even using human rewrites.Our findings provide important evidence to better understand and leverage LLMs for conversational search.The code is released at https://github.com/ kyriemao/LLM4CS.

**9. Soft prompt tuning for augmenting dense retrieval with large language models**

- DOI：`10.1016/j.knosys.2024.112758`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

Dense retrieval (DR) converts queries and documents into dense embeddings and measures the similarity between queries and documents in vector space. One of the major challenges in DR is the lack of domain-specific training data. While DR models can learn from large-scale public datasets like MS MARCO through transfer learning, evidence shows that not all DR models and domains can benefit from transfer learning. Recently, researchers have resorted to large language models (LLMs) to improve the zero-shot and few-shot DR models. However, the hard prompts or human-written prompts utilized in these works are suboptimal and the generated weak queries are often sensitive to the prompts. To tackle this, we propose soft prompt tuning for augmenting DR (SPTAR): for each task, we leverage soft prompt tuning to optimize a task-specific soft prompt on limited ground truth data and then prompt the LLMs to tag unlabeled documents with weak queries, yielding weak document–query pairs to train task-specific dense retrievers. We design a filter to select high-quality example document–query pairs in the prompt to further improve the quality of weak tagged queries. To the best of our knowledge, there is no prior work utilizing soft prompt tuning to augment DR models. Moreover, unlike much of the existing work, ours is based on popular open-source LLMs to ensure reproducible and deterministic results. Our experimental results demonstrate that SPTAR outperforms both unsupervised baselines and the recently proposed LLMs-based augmentation method for DR. • First to use LLMs with soft prompt tuning for augmenting dense retrieval tasks. • Novel soft prompt filter improves weak data quality. • Experiments show our method outperforms strong baselines. • Uses open-source LLMs for reproducible, robust results.

**10. Generative Multi-Modal Knowledge Retrieval with Large Language Models**

- DOI：`10.1609/aaai.v38i17.29837`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

Knowledge retrieval with multi-modal queries plays a crucial role in supporting knowledge-intensive multi-modal applications. However, existing methods face challenges in terms of their effectiveness and training efficiency, especially when it comes to training and integrating multiple retrievers to handle multi-modal queries. In this paper, we propose an innovative end-to-end generative framework for multi-modal knowledge retrieval. Our framework takes advantage of the fact that large language models (LLMs) can effectively serve as virtual knowledge bases, even when trained with limited data. We retrieve knowledge via a two-step process: 1) generating knowledge clues related to the queries, and 2) obtaining the relevant document by searching databases using the knowledge clue. In particular, we first introduce an object-aware prefix-tuning technique to guide multi-grained visual learning. Then, we align multi-grained visual features into the textual feature space of the LLM, employing the LLM to capture cross-modal interactions. Subsequently, we construct instruction data with a unified format for model training. Finally, we propose the knowledge-guided generation strategy to impose prior constraints in the decoding steps, thereby promoting the generation of distinctive knowledge clues. Through experiments conducted on three benchmarks, we demonstrate significant improvements ranging from 3.0% to 14.6% across all evaluation metrics when compared to strong baselines.

**11. Retrieval-Augmented Generation to Generate Knowledge Assets and Creation of Action Drivers**

- DOI：`10.3390/app15116247`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

This article explores the application of Retrieval-Augmented Generation (RAG) to enhance the creation of knowledge assets and develop actionable insights from complex datasets. It begins by contextualising the limitations of large language models (LLMs), notably their knowledge cut-offs and hallucination tendencies, and it will present RAG as a promising solution that integrates external knowledge retrieval to improve factual accuracy and relevance. This study reviews current RAG architectures, including naïve and advanced models, emphasising techniques such as optimised indexing, query refinement, metadata utilisation, and the incorporation of autonomous AI agents in agentic RAG systems. Methodologies for effective data preprocessing, semantic-aware chunking, and retrieval strategies—such as multihop retrieval and reranking—are also discussed to address challenges such as irrelevant retrieval and semantic fragmentation. This work further examines embedding models, notably the use of state-of-the-art vector representations, to facilitate precise similarity searches within knowledge bases. A case study demonstrates the deployment of an RAG pipeline for analysing multisheet datasets, highlighting challenges in data structuring, prompt engineering, and ensuring output consistency.

**12. Customized Retrieval Augmented Generation and Benchmarking for EDA Tool Documentation QA**

- DOI：`10.1145/3676536.3676730`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

Retrieval augmented generation (RAG) enhances the accuracy and reliability of generative AI models by sourcing factual information from external databases, which is extensively employed in document-grounded question-answering (QA) tasks. Off-the-shelf RAG flows are well pretrained on general-purpose documents, yet they encounter significant challenges when being applied to knowledge-intensive vertical domains, such as electronic design automation (EDA). This paper addresses such issue by proposing a customized RAG framework along with three domain-specific techniques for EDA tool documentation QA, including a contrastive learning scheme for text embedding model fine-tuning, a reranker distilled from proprietary LLM, and a generative LLM fine-tuned with high-quality domain corpus. Furthermore, we have developed and released a documentation QA evaluation benchmark, ORD-QA, for OpenROAD, an advanced RTL-to-GDSII design platform. Experimental results demonstrate that our proposed RAG flow and techniques have achieved superior performance on ORD-QA as well as on a commercial tool, compared with state-of-the-arts. The ORD-QA benchmark and the training dataset for our customized RAG flow are open-source at https://github.com/lesliepy99/RAG-EDA.

**13. MoRSE: Bridging the Gap in Cybersecurity Expertise with Retrieval Augmented Generation**

- DOI：`10.1145/3672608.3707898`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

In this paper, we introduce MoRSE (Mixture of RAGs Security Experts), the first specialised AI chatbot for cybersecurity. MoRSE aims to provide comprehensive and complete knowledge about cybersecurity. MoRSE uses two RAG (Retrieval Augmented Generation) systems designed to retrieve and organize information from multidimensional cybersecurity contexts. MoRSE differs from traditional RAGs by using parallel retrievers that work together to retrieve semantically related information in different formats and structures. Unlike traditional Large Language Models (LLMs) that rely on Parametric Knowledge Bases, MoRSE retrieves relevant documents from Non-Parametric Knowledge Bases in response to user queries. Subsequently, MoRSE uses this information to generate accurate answers. In addition, MoRSE benefits from real-time updates to its knowledge bases, enabling continuous knowledge enrichment without retraining. We have evaluated the effectiveness of MoRSE against other state-of-the-art LLMs, evaluating the system on 600 cybersecurity specific questions. The experimental evaluation has shown that the improvement in terms of relevance and correctness of the answer is more than 10% compared to known solutions such as GPT-4 and Mixtral 7x8.

**14. Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs) for Enterprise Knowledge Management and Document Automation: A Systematic Literature Review**

- DOI：`10.3390/app16010368`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

The integration of Retrieval-Augmented Generation (RAG) with Large Language Models (LLMs) is rapidly transforming enterprise knowledge management, yet a comprehensive understanding of their deployment in real-world workflows remains limited. This study presents a systematic literature review (SLR) analyzing 63 high-quality primary studies selected after rigorous screening to evaluate how these technologies address practical enterprise challenges. We formulated nine research questions targeting platforms, datasets, algorithms, and validation metrics to map the current landscape. Our findings reveal that enterprise adoption is largely in the experimental phase: 63.6% of implementations utilize GPT based models, and 80.5% rely on standard retrieval frameworks such as FAISS or Elasticsearch. Critically, this review identifies a significant ‘lab-to-market’ gap; while retrieval and classification sub-tasks frequently employ academic validation methods like k-fold cross-validation (93.6%), generative evaluation predominantly relies on static hold-out sets due to computational constraints. Furthermore, fewer than 15% of studies address real-time integration challenges required for production scale deployment. By systematically mapping these disparities, this study offers a data-driven perspective and a strategic roadmap for bridging the gap between academic prototypes and robust enterprise applications.

**15. SCITAB: A Challenging Benchmark for Compositional Reasoning and Claim Verification on Scientific Tables**

- DOI：`10.18653/v1/2023.emnlp-main.483`
- 关联种子：`doi:10.18653/v1/2022.findings-emnlp.347`（引用了种子）

Current scientific fact-checking benchmarks exhibit several shortcomings, such as biases arising from crowd-sourced claims and an overreliance on text-based evidence.We present SCITAB, a challenging evaluation dataset consisting of 1.2K expert-verified scientific claims that 1) originate from authentic scientific publications and 2) require compositional reasoning for verification.The claims are paired with evidence-containing scientific tables annotated with labels.Through extensive evaluations, we demonstrate that SCITAB poses a significant challenge to state-of-the-art models, including table-based pretraining models and large language models.All models except GPT-4 achieved performance barely above random guessing.Popular prompting techniques, such as Chain-of-Thought, do not achieve much performance gains on SCITAB.Our analysis uncovers several unique challenges posed by SCITAB, including table grounding, claim ambiguity, and compositional reasoning.

**16. An In-depth Analysis of the Linguistic Characteristics of Science Claims on the Web and their Impact on Fact-checking**

- DOI：`10.1145/3746170`
- 关联种子：`doi:10.18653/v1/2022.findings-emnlp.347`（引用了种子）

Web claims, seen as assertions shared on the web and eligible for fact-checking, are at the heart of online discourse. They have been studied extensively on a variety of downstream tasks such as fact-checking, claim retrieval, bias detection, argument mining, or viewpoint discovery. On the other hand, claims originating from scientific publications have also been the subject of several downstream NLP tasks. However, research carried out so far has yet to focus on scientific web claims, which are scientific claims made on the web (e.g., on social media and news articles). The process of detecting and fact-checking a claim from the web can be very different depending on whether the claim is scientific or not, thus making it crucial for the developed datasets, methods, and models to make a distinction between the two. With this work, we aim at understanding what makes this distinction necessary, by understanding the linguistic differences between scientific and non-scientific claims on the web, and the impact those differences have on existing downstream tasks. To do so, we manually annotate 1,524 web claims from established benchmarks for fact-checking-related tasks, and we run statistical tests to analyze and compare the linguistic features of each group. We find that scientific claims on the web use more analytical speech, but also use more sentiment-related speech, more expressions of physical motion, and have distinct parts of speech (PoS) and punctuation styles. We also conduct experiments showing that BERT-based language models perform worse on scientific web claims by up to 17 F1 points for several downstream tasks. To understand why, we develop a novel methodology to map predictive tokens of language models to explainable linguistic features and find that language models fail to detect a specific subset of predictive features of scientific web claims. We conclude by stating that language models aimed at studying scientific web claims ought to be trained on scientific web discourse, as opposed to being trained only on generic web discourse or only on scientific text from scientific publications.

**17. The Next Phase of Scientific Fact-Checking: Advanced Evidence Retrieval from Complex Structured Academic Papers**

- DOI：`10.1145/3731120.3744614`
- 关联种子：`doi:10.18653/v1/2022.findings-emnlp.347`（引用了种子）

Scientific fact-checking aims to determine the veracity of scientific claims by retrieving and analysing evidence from research literature. The problem is inherently more complex than general fact-checking since it must accommodate the evolving nature of scientific knowledge, the structural complexity of academic literature and the challenges posed by long-form, multimodal scientific expression. However, existing approaches focus on simplified versions of the problem based on small-scale datasets consisting of abstracts rather than full papers, thereby avoiding the distinct challenges associated with processing complete documents. This paper examines the limitations of current scientific fact-checking systems and reveals the many potential features and resources that could be exploited to advance their performance. It identifies key research challenges within evidence retrieval, including (1) evidence-driven retrieval that addresses semantic limitations and topic imbalance (2) time-aware evidence retrieval with citation tracking to mitigate outdated information, (3) structured document parsing to leverage long-range context, (4) handling complex scientific expressions, including tables, figures, and domain-specific terminology and (5) assessing the credibility of scientific literature. Preliminary experiments were conducted to substantiate these challenges and identify potential solutions. This perspective paper aims to advance scientific fact-checking with a specialised IR system tailored for real-world applications.

**18. +VeriRel: Verification Feedback to Enhance Document Retrieval for Scientific Fact Checking**

- DOI：`10.1145/3746252.3760822`
- 关联种子：`doi:10.18653/v1/2022.findings-emnlp.347`（引用了种子）

Identification of appropriate supporting evidence is critical to the success of scientific fact checking. However, existing approaches rely on off-the-shelf Information Retrieval algorithms that rank documents based on relevance rather than the evidence they provide to support or refute the claim being checked. This paper proposes +VeriRel which includes verification success in the document ranking. Experimental results on three scientific fact checking datasets (SciFact, SciFact-Open and Check-Covid) demonstrate consistently leading performance by +VeriRel for document evidence retrieval and a positive impact on downstream verification. This study highlights the potential of integrating verification feedback to document relevance assessment for effective scientific fact checking systems. It shows promising future work to evaluate fine-grained relevance when examining complex documents for advanced scientific fact checking.

**19. The student becomes the master: Outperforming GPT3 on Scientific Factual Error Correction**

- DOI：`10.18653/v1/2023.findings-emnlp.451`
- 关联种子：`doi:10.18653/v1/2022.findings-emnlp.347`（引用了种子）

Due to the prohibitively high cost of creating error correction datasets, most Factual Claim Correction methods rely on a powerful verification model to guide the correction process.This leads to a significant drop in performance in domains like scientific claims, where good verification models do not always exist.In this work, we introduce SciFix, a scientific claim correction system that does not require a verifier but can outperform existing methods by a considerable margin -achieving correction accuracy of 84% on the SciFact dataset, 77% on SciFact-Open and 72% on the CovidFact dataset, compared to next best accuracies of 7%, 5%, and 15% on the same datasets respectively.Our method leverages the power of prompting with LLMs during training to create a richly annotated dataset that can be used for fully supervised training and regularization.We additionally use a claim-aware decoding procedure to improve the quality of corrected claims.Our method outperforms the very LLM that was used to generate the annotated datasetwith Few-Shot Prompting on GPT3.5 achieving 58%, 61%, and 64% on the respective datasets, a consistently lower correction accuracy, despite using nearly 800 times as many parameters as our model.

**20. FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation**

- DOI：`10.18653/v1/2023.emnlp-main.741`
- 关联种子：`doi:10.18653/v1/2022.findings-emnlp.347`（引用了种子）

Sewon Min, Kalpesh Krishna, Xinxi Lyu, Mike Lewis, Wen-tau Yih, Pang Koh, Mohit Iyyer, Luke Zettlemoyer, Hannaneh Hajishirzi. Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing. 2023.

**21. Hallucination Mitigation for Retrieval-Augmented Large Language Models: A Review**

- DOI：`10.3390/math13050856`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

Retrieval-augmented generation (RAG) leverages the strengths of information retrieval and generative models to enhance the handling of real-time and domain-specific knowledge. Despite its advantages, limitations within RAG components may cause hallucinations, or more precisely termed confabulations in generated outputs, driving extensive research to address these limitations and mitigate hallucinations. This review focuses on hallucination in retrieval-augmented large language models (LLMs). We first examine the causes of hallucinations from different sub-tasks in the retrieval and generation phases. Then, we provide a comprehensive overview of corresponding hallucination mitigation techniques, offering a targeted and complete framework for addressing hallucinations in retrieval-augmented LLMs. We also investigate methods to reduce the impact of hallucination through detection and correction. Finally, we discuss promising future research directions for mitigating hallucinations in retrieval-augmented LLMs.

**22. Retrieval-Augmented Generation for AI-Generated Content: A Survey**

- DOI：`10.1007/s41019-025-00335-5`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

Advancements in model algorithms, the growth of foundational models, and access to high-quality datasets have propelled the evolution of Artificial Intelligence Generated Content (AIGC). Despite its notable successes, AIGC still faces hurdles such as updating knowledge, handling long-tail data, mitigating data leakage, and managing high training and inference costs. Retrieval-augmented generation (RAG) has recently emerged as a paradigm to address such challenges. In particular, RAG introduces the information retrieval process, which enhances the generation process by retrieving relevant objects from available data stores, leading to higher accuracy and better robustness. In this paper, we comprehensively review existing efforts that integrate RAG techniques into AIGC scenarios. We first classify RAG foundations according to how the retriever augments the generator, distilling the fundamental abstractions of the augmentation methodologies for various retrievers and generators. This unified perspective encompasses all RAG scenarios, illuminating advancements and pivotal technologies that help with potential future progress. We also summarize additional enhancement methods for RAG, facilitating effective engineering and implementation of RAG systems. Then from another view, we survey practical applications of RAG across different modalities and tasks, offering valuable references for researchers and practitioners. Furthermore, we introduce the benchmarks for RAG, discuss the limitations of current RAG systems, and suggest potential directions for future research.

**23. Generative Relevance Feedback with Large Language Models**

- DOI：`10.1145/3539618.3591992`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

Current query expansion models use pseudo-relevance feedback to improve first-pass retrieval effectiveness; however, this fails when the initial results are not relevant. Instead of building a language model from retrieved results, we propose Generative Relevance Feedback (GRF) that builds probabilistic feedback models from long-form text generated from Large Language Models. We study the effective methods for generating text by varying the zero-shot generation subtasks: queries, entities, facts, news articles, documents, and essays. We evaluate GRF on document retrieval benchmarks covering a diverse set of queries and document collections, and the results show that GRF methods significantly outperform previous PRF methods. Specifically, we improve MAP between 5-19% and NDCG@10 17-24% compared to RM3 expansion, and achieve state-of-the-art recall across all datasets.

**24. Improving knowledge management in building engineering with hybrid retrieval-augmented generation framework**

- DOI：`10.1016/j.jobe.2025.112189`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

（源站未提供摘要——需另行获取，或直接放弃该候选）

**25. MemoRAG: Boosting Long Context Processing with Global Memory-Enhanced Retrieval Augmentation**

- DOI：`10.1145/3696410.3714805`
- 关联种子：`doi:10.18653/v1/2023.acl-long.99`（引用了种子）

Processing long contexts presents a significant challenge for large language models (LLMs). While recent advancements allow LLMs to handle much longer contexts than before (e.g., 32K or 128K tokens), it is computationally expensive and can still be insufficient for many applications. Retrieval-Augmented Generation (RAG) is considered a promising strategy to address this problem. However, conventional RAG methods face inherent limitations because of two underlying requirements: 1) explicitly stated queries, and 2) well-structured knowledge. These conditions, however, do not hold in general long-context processing tasks.


## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | |
| 日期 | |
| 采纳的候选编号 | |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |
