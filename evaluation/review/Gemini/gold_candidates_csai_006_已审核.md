# 金标候选：csai_006

**问题**：How does dense retrieval compare with sparse retrieval for scientific search?
  → 在科学检索中，稠密检索与稀疏检索相比如何？

**子问题**：
1. What are the reported trade-offs?
  → 已报告的权衡是什么？
2. Which evaluation setups are used?
  → 使用了哪些评估设置？

**现有 gold**：2 篇 **年份范围**：(2022, 2026) **引用图候选**：25 篇

## 判定标准

一篇论文算作 gold，当且仅当**领域专家会把它作为回答某个子问题的证据引用**。
按子问题分别判定，因为证据是按子问题分配的。

逐条检查：
1. 论文是否真正回答某个子问题（不是主题相邻）
2. 年份是否在声明范围内
3. 摘要是否包含可以作为证据的完整句子
4. 判定它支撑哪个子问题（填编号）

## 候选清单

| # | 年份 | 标题 | 中文标题(机翻) | DOI | 被引 | 关系 | 命中 | 初审建议 | 判定 | 子问题 | 备注 |
|---:|---:|---|---|---|---:|---|---:|---|---|---|---|
| 1 | 2023 | Is ChatGPT Good at Search? Investigating Large Language Models as Re-R | ChatGPT擅长搜索吗？探究大语言模型作为重排序智能体 | `10.18653/v1/2023.emnlp-main.923` | 230 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 该文研究的是用LLM进行重排序（RankGPT），未涉及稠密检索与稀疏检索的对比或相关评测设置，属主题相邻（信息检索/排序）而非直接证据。 |
| 2 | 2025 | Retrieval augmented generation for large language models in healthcare | 医疗保健领域大语言模型的检索增强生成：一项系统综述 | `10.1371/journal.pdig.0000877` | 226 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 该文是医疗健康领域RAG的系统综述，未比较稠密与稀疏检索在科学搜索中的权衡或评估设置，属于主题相邻但不相关。 |
| 3 | 2023 | Query2doc: Query Expansion with Large Language Models | Query2doc：基于大语言模型的查询扩展 | `10.18653/v1/2023.emnlp-main.585` | 188 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：该文虽同时涉及稀疏与稠密检索，但未报告二者权衡比较，且评测为通用 ad-hoc IR 数据集而非科学搜索场景。 |
| 4 | 2024 | Fine-Tuning LLaMA for Multi-Stage Text Retrieval | 面向多阶段文本检索的LLaMA微调 | `10.1145/3626772.3657951` | 112 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：论文聚焦微调 LLaMA 作为稠密检索器和重排器，并未比较稠密与稀疏检索在科学搜索中的权衡或相应评测设置。 |
| 5 | 2025 | Evaluating Retrieval-Augmented Generation Variants for Clinical Decisi | 评估面向临床决策支持的检索增强生成变体：幻觉缓解与安全本地化部署 | `10.3390/electronics14214227` | 14 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：该文评估临床决策支持（CDS）中的RAG变体，场景为患者病历分析而非科学文献搜索，不构成直接证据。 |
| 6 | 2022 | Unsupervised Corpus Aware Language Model Pre-training for Dense Passag | 面向稠密段落检索的无监督语料感知语言模型预训练 | `10.18653/v1/2022.acl-long.203` | 144 | 被种子引用 | 2 | 建议不采纳 | 不采纳 | - | 论文仅讨论稠密检索器的训练方法与评估数据集，未涉及与稀疏检索的对比或科学搜索场景，属于主题相邻而非直接证据。 |
| 7 | 2023 | The Information Retrieval Experiment Platform | 信息检索实验平台 | `10.1145/3539618.3591888` | 54 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 该论文描述了通用 IR 实验平台（TIREx/TIRA）的基础设施，而并未报告任何针对科学检索中稠密与稀疏检索比较的评估设置，因此仅为主题相邻。 |
| 8 | 2023 | Large Language Models Know Your Contextual Search Intent: A Prompting  | 大语言模型了解你的上下文搜索意图：面向会话搜索的提示框架 | `10.18653/v1/2023.findings-emnlp.86` | 49 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 该论文研究基于LLM提示的对话式搜索意图理解与查询重写，未涉及稠密与稀疏检索在科学搜索中的比较，因此仅属主题相邻而非直接证据。 |
| 9 | 2024 | Soft prompt tuning for augmenting dense retrieval with large language  | 利用大语言模型增强稠密检索的软提示调优 | `10.1016/j.knosys.2024.112758` | 26 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：论文聚焦于用软提示调优增强稠密检索，并未比较稠密检索与稀疏检索，也未涉及科学搜索场景下的权衡或评估设置。 |
| 10 | 2024 | Generative Multi-Modal Knowledge Retrieval with Large Language Models | 基于大语言模型的生成式多模态知识检索 | `10.1609/aaai.v38i17.29837` | 24 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 该论文研究基于LLM的多模态生成式知识检索，未涉及稠密与稀疏检索在科学搜索中的比较，属于主题相邻（多模态检索）而非直接证据。 |
| 11 | 2025 | Retrieval-Augmented Generation to Generate Knowledge Assets and Creati | 检索增强生成用于生成知识资产与创建行动驱动因素 | `10.3390/app15116247` | 22 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：该文讨论RAG架构与检索增强技术，但未比较稠密与稀疏检索在科学搜索中的权衡或评估设置。 |
| 12 | 2024 | Customized Retrieval Augmented Generation and Benchmarking for EDA Tool | 面向EDA工具文档问答的定制化检索增强生成与基准测试 | `10.1145/3676536.3676730` | 21 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：该论文聚焦于EDA工具文档QA的定制RAG框架与基准，未比较稠密与稀疏检索的权衡或评估设置。 |
| 13 | 2025 | MoRSE: Bridging the Gap in Cybersecurity Expertise with Retrieval Augm | MoRSE：利用检索增强生成弥合网络安全专业知识差距 | `10.1145/3672608.3707898` | 14 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 该论文聚焦网络安全领域的RAG聊天机器人系统，虽涉及检索但未比较稠密与稀疏检索，也未针对科学搜索场景，属于主题相邻。 |
| 14 | 2025 | Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs)  | 面向企业知识管理与文档自动化的检索增强生成（RAG）与大语言模型（LLMs）：系统性文献综述 | `10.3390/app16010368` | 11 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：该文综述企业知识管理中的RAG/LLM，涉及检索框架与评估方法，但未比较面向科学搜索的稠密与稀疏检索及其权衡或评估设置。 |
| 15 | 2023 | SCITAB: A Challenging Benchmark for Compositional Reasoning and Claim  | SCITAB：一个用于科学表格组合推理与声明验证的挑战性基准 | `10.18653/v1/2023.emnlp-main.483` | 9 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 该论文研究科学表格上的声明验证基准，完全不涉及稠密与稀疏检索的比较，属于科学NLP但检索主题之外的完全无关工作。 |
| 16 | 2025 | An In-depth Analysis of the Linguistic Characteristics of Science Clai | 网络科学主张的语言特征及其对事实核查影响的深入分析 | `10.1145/3746170` | 2 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 该论文研究科学网络声明的语言学特征及其对事实核查的影响，虽涉及科学文本与BERT模型，但未比较稠密检索与稀疏检索，也未报告相关权衡或评测设置，属主题相邻而非直接相关。 |
| 17 | 2025 | The Next Phase of Scientific Fact-Checking: Advanced Evidence Retrieva | 科学事实核查的下一阶段：从复杂结构化学术论文中进行高级证据检索 | `10.1145/3731120.3744614` | 2 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：论文展望科学事实核查中的证据检索挑战，未包含明确的稠密与稀疏检索性能权衡数据或实证评估设置对比。 |
| 18 | 2025 | +VeriRel: Verification Feedback to Enhance Document Retrieval for Scie | +VeriRel：验证反馈以增强科学事实核查的文档检索 | `10.1145/3746252.3760822` | 1 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：该文聚焦科学事实核查中的文档检索与验证反馈，但未比较密集检索与稀疏检索，也未报告二者权衡或相关评估设置。 |
| 19 | 2023 | The student becomes the master: Outperforming GPT3 on Scientific Factual | 学生成为大师：在科学事实性错误纠正上超越 GPT3 | `10.18653/v1/2023.findings-emnlp.451` | 0 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 该论文研究科学事实性错误纠正（SciFix），虽同属科学主张验证领域且使用SciFact数据集，但未涉及稠密检索与稀疏检索的对比或相关评测设置，属于主题相邻而非直接证据。 |
| 20 | 2023 | FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long | FActScore：长文本生成中事实精确度的细粒度原子评估 | `10.18653/v1/2023.emnlp-main.741` | 345 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | - | 该论文提出的是长文本生成事实精确度的细粒度评估方法（FActScore），与稠密/稀疏检索的对比或其评估设置完全无关，属于完全无关。 |
| 21 | 2025 | Hallucination Mitigation for Retrieval-Augmented Large Language Models | 检索增强大语言模型的幻觉缓解：综述 | `10.3390/math13050856` | 130 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | - | 主题相邻：该综述讨论检索增强大语言模型的幻觉缓解，并未比较稠密检索与稀疏检索在科学搜索中的权衡或评测设置。 |
| 22 | 2026 | Retrieval-Augmented Generation for AI-Generated Content: A Survey | 面向AI生成内容的检索增强生成：综述 | `10.1007/s41019-025-00335-5` | 106 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | - | 主题相邻：该论文综述RAG在AIGC中的应用，未具体比较稠密与稀疏检索在科学搜索中的权衡或评估设置。 |
| 23 | 2023 | Generative Relevance Feedback with Large Language Models | 基于大语言模型的生成式相关性反馈 | `10.1145/3539618.3591992` | 47 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | - | 主题相邻：该论文研究生成式相关反馈与查询扩展在通用文档检索中的效果，未比较稠密与稀疏检索，也未针对科学搜索的权衡或评测设置。 |
| 24 | 2025 | Improving knowledge management in building engineering with hybrid ret | 利用混合检索增强生成框架改进建筑工程中的知识管理 | `10.1016/j.jobe.2025.112189` | 27 | 引用了种子 | 1 | 无法判断 | 不采纳 | - | 场景为建筑工程领域知识管理，不符合科学文献搜索（Scientific Search）要求，且无法作为直接证据。 |
| 25 | 2025 | MemoRAG: Boosting Long Context Processing with Global Memory-Enhanced  | MemoRAG：通过全局记忆增强的检索增强提升长上下文处理 | `10.1145/3696410.3714805` | 23 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | - | 该论文聚焦长上下文RAG与全局记忆增强，未比较稠密与稀疏检索在科学搜索中的权衡或评测设置，属于主题相邻。 |

## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | Gemini |
| 日期 | 2026-09-24 |
| 采纳的候选编号 | 无 |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |