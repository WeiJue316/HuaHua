# 金标候选：csai_001

**问题**：What are the main evaluation methods for retrieval-augmented generation systems?

　　→ 检索增强生成系统的主要评估方法有哪些？

**子问题**：

1. Which metrics are used?
　　→ 使用了哪些指标？

2. Which datasets and baselines are common?
　　→ 常用的数据集和基线有哪些？


**现有 gold**：3 篇　**年份范围**：(2022, 2026)　**引用图候选**：25 篇

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
|---:|---:|---|---|---|---:|---|---:|---|---:|---|---|
| 1 | 2025 | A self-correcting Agentic Graph RAG for clinical decision support in h | 面向肝病学临床决策支持的自校正智能体图RAG | `10.3389/fmed.2025.1716327` | 9 | 引用了种子 | 8 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 该论文明确报告了RAG评估所用的指标（faithfulness、context recall、answer relevancy）以及常见基线（GPT-4、standard RAG、Graph RAG）和自建临床问答数据集，可直接作为两个子问题的证据。 |
| 2 | 2025 | Improving large language model applications in biomedicine with retrie | 利用检索增强生成改进生物医学中的大语言模型应用：系统综述、元分析与临床开发指南 | `10.1093/jamia/ocaf008` | 173 | 引用了种子 | 6 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 该综述系统报告了RAG在生物医学中的评估方法、基线LLM及检索策略，可为指标与常用基线/数据集子问题提供证据。 |
| 3 | 2025 | The Great Nugget Recall: Automating Fact Extraction and RAG Evaluation | 伟大的要点召回：利用大语言模型实现事实抽取与RAG评估的自动化 | `10.1145/3726302.3730090` | 13 | 引用了种子 | 6 | 建议采纳(子问题1) | 采纳 | 1 | The abstract directly addresses RAG evaluation metrics by proposing an automatic nugget-based evaluation framework (atomic facts, nugget recall, automatic nugget creation/assignment), but it does not discuss common datasets and baselines beyond using the TREC 2024 RAG Track as a case study. |
| 4 | 2025 | Conversational Gold: Evaluating Personalized Conversational Search Sys | 对话式黄金标准：使用黄金要点评估个性化对话式搜索系统 | `10.1145/3726302.3730316` | 12 | 引用了种子 | 6 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 摘要提出基于nugget的RAG长答案评估框架及nugget抽取/匹配方法，并发布TREC iKAT 2024数据集，可为评估指标和数据集子问题提供证据。 |
| 5 | 2025 | A Systematic Evaluation of Large Language Models and Retrieval-Augment | 面向哈萨克语问答任务的大语言模型与检索增强生成系统性评估 | `10.3390/info16110943` | 10 | 引用了种子 | 6 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 该摘要描述了RAG系统的评估框架，包含检索指标和答案正确性等评价指标，并涉及Kazakh QA数据集、专有/开源模型及不同检索器作为基线的对比，可作为两个子问题的证据。 |
| 6 | 2025 | A retrieval augmented generation based optimization approach for medic | 面向大语言模型医学知识理解与推理的基于检索增强生成的优化方法 | `10.1016/j.array.2025.100504` | 8 | 引用了种子 | 6 | 建议采纳(子问题2) | 采纳 | 2 | 论文使用CCKS-TCMBench数据集并对比基线，可作为子问题2关于常用数据集和基线的证据；但未具体列出评估指标，故不直接支持子问题1。 |
| 7 | 2025 | Evaluating Open-Source LLMs in RAG Systems: A Benchmark on Diploma The | 评估RAG系统中的开源大语言模型：基于Ragas的学位论文摘要基准测试 | `10.1007/s44427-025-00006-3` | 7 | 引用了种子 | 6 | 建议采纳(子问题1) | 采纳 | 1 | 摘要明确使用Ragas框架并聚焦检索效果与答案质量指标，直接回答子问题1；但其数据集为自建文凭论文摘要，未讨论常见数据集与基线，故不直接支持子问题2。 |
| 8 | 2025 | Evaluation of a retrieval-augmented generation system using a Japanese | 基于日本机构核医学手册和大语言模型自动评分的检索增强生成系统评估 | `10.1007/s12194-025-00941-y` | 6 | 引用了种子 | 6 | 建议采纳(子问题1) | 采纳 | 1 | 该论文主要报告了RAG评估所用指标（RAGAS的factual correctness和context recall，以及ROUGE、Levenshtein、专家评分），可作为子问题1的证据，但未系统讨论常见数据集和基线，故不直接支持子问题2。 |
| 9 | 2024 | Applying generative AI with retrieval augmented generation to summariz | 应用结合检索增强生成的生成式人工智能从电子健康记录中总结和提取关键临床信息 | `10.1016/j.jbi.2024.104662` | 150 | 引用了种子 | 5 | 建议采纳(子问题1) | 采纳 | 1 | 该文使用准确率并将模型输出与金标准人工对比来评估RAG在临床摘要/信息抽取中的效果，可作为RAG系统评价指标的实例证据，但其数据集和基线为该临床场景定制，不足以说明常见数据集与基线。 |
| 10 | 2024 | CRUD-RAG: A Comprehensive Chinese Benchmark for Retrieval-Augmented Ge | CRUD-RAG：大语言模型检索增强生成的综合性中文基准 | `10.1145/3701228` | 96 | 引用了种子 | 5 | 建议采纳(子问题2) | 采纳 | 2 | 该摘要构建了面向RAG的大型中文基准，针对CRUD四类场景开发了不同数据集并评测检索器、上下文长度、知识库构建与LLM等组件，可作为常见数据集/基线这一子问题的证据；但摘要未明确提及具体评价指标，故不支持子问题1。 |
| 11 | 2024 | Evaluating Retrieval-Augmented Generation Models for Financial Report  | 评估用于财务报告问答的检索增强生成模型 | `10.3390/app14209318` | 42 | 引用了种子 | 5 | 建议采纳(子问题1) | 采纳 | 1 | 摘要明确使用context relevance、answer faithfulness、answer relevance等指标评估RAG，但未涉及常用数据集或基线。 |
| 12 | 2024 | Hybrid Retrieval-Augmented Generation Approach for LLMs Query Response | 面向大语言模型查询响应增强的混合检索增强生成方法 | `10.1109/icwr61162.2024.10533345` | 34 | 引用了种子 | 5 | 建议不采纳 | 不采纳 | | 主题相邻：该文提出一种混合RAG方法并泛泛提到用基准数据集和指标评估，但未列出具体指标、数据集或基线，不能作为回答RAG评估方法子问题的证据。 |
| 13 | 2025 | Development and Evaluation of a Retrieval-Augmented Generation Chatbot | 用于骨科与创伤外科患者教育的检索增强生成聊天机器人的开发与评价：混合方法研究 | `10.2196/75262` | 19 | 引用了种子 | 5 | 建议采纳(子问题1) | 采纳 | 1 | 该论文明确使用了RAGAS指标（答案相关性、上下文精确率、忠实度）及人工评分来评估RAG系统，可为“使用哪些指标”子问题提供证据，但未涉及常见数据集或基线比较，故不支撑子问题2。 |
| 14 | 2025 | SynthMedic: Utilizing large language models for synthetic discharge su | SynthMedic：利用大语言模型生成、校正与验证合成出院小结 | `10.1016/j.jbi.2025.104906` | 9 | 引用了种子 | 5 | 建议不采纳 | 不采纳 | | 主题相邻：该文关注合成出院摘要的生成与验证，虽提及Faithfulness指标，但未研究RAG系统的评估方法、常用指标或数据集/基线。 |
| 15 | 2025 | Optimization of Customer Feedback Summarization Using Large Language M | 利用大语言模型（LLM）与先进检索增强生成优化客户反馈摘要 | `10.1109/access.2025.3588337` | 7 | 引用了种子 | 5 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 摘要明确列出了用于评估RAG系统的多项指标（语义/事实准确性、相关性、覆盖度、一致性、流畅度）以及基线模型（BM25、BERT），可直接作为子问题1和2的证据。 |
| 16 | 2025 | Benchmarking Vector, Graph and Hybrid Retrieval Augmented Generation ( | 面向开放无线接入网（ORAN）的向量、图与混合检索增强生成（RAG）流水线基准评测 | `10.1109/pimrc62392.2025.11274810` | 7 | 引用了种子 | 5 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 该论文明确采用忠实度、答案相关性、上下文相关性、事实正确性等生成指标评估RAG，并以ORAN规范为数据集、以Vector RAG为基线对比GraphRAG与Hybrid GraphRAG，同时覆盖指标与数据集/基线两个子问题。 |
| 17 | 2025 | RAGTrace: Understanding and Refining Retrieval-Generation Dynamics in  | RAGTrace：理解与优化检索增强生成中的检索—生成动态 | `10.1145/3746059.3747741` | 6 | 引用了种子 | 5 | 建议不采纳 | 不采纳 | | 该论文聚焦于RAG交互式评估系统与检索-生成动态分析，未具体涉及评估指标或常用数据集与基线，属于主题相邻而非直接证据。 |
| 18 | 2025 | A comprehensive survey of loss functions and metrics in deep learning | 深度学习损失函数与评价指标的全面综述 | `10.1007/s10462-025-11198-7` | 285 | 引用了种子 | 4 | 建议采纳(子问题1) | 采纳 | 1 | 该综述明确讨论了用于评估检索增强生成系统的专门指标（如faithfulness和context relevance），可作为子问题1关于评价指标的证据，但未涉及常用数据集和基线。 |
| 19 | 2024 | AI–Human Hybrids for Marketing Research: Leveraging Large Language Mod | 面向市场研究的AI—人类混合模式：以大型语言模型（LLM）作为协作者 | `10.1177/00222429241276529` | 151 | 引用了种子 | 4 | 建议不采纳 | 不采纳 | | 主题相邻：该文仅在营销研究中应用检索增强生成，未评估RAG系统的指标、数据集或基线。 |
| 20 | 2025 | Hallucination‐Free? Assessing the Reliability of Leading AI Legal Rese | 无幻觉？评估主流AI法律研究工具的可靠性 | `10.1111/jels.12413` | 150 | 引用了种子 | 4 | 建议采纳(两个子问题) | 采纳 | 1, 2 | The paper empirically evaluates RAG-based legal AI tools using metrics such as hallucination rate, accuracy, and responsiveness, and introduces a preregistered dataset plus comparisons against GPT-4 as a baseline, providing evidence for both metrics and datasets/baselines. |
| 21 | 2024 | RDguru: A Conversational Intelligent Agent for Rare Diseases | RDguru：面向罕见病的对话式智能体 | `10.1109/jbhi.2024.3464555` | 26 | 引用了种子 | 4 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 摘要明确使用了ROUGE、GPT-4自动评分和RAGAs等RAG评估指标，并在238例罕见病数据上以PheLR、ChatGPT等作为基线/对比，因此可作为指标及数据集/基线两个子问题的证据。 |
| 22 | 2025 | Correctness is not Faithfulness in Retrieval Augmented Generation Attr | 检索增强生成归因中的正确性并不等同于忠实性 | `10.1145/3731120.3744592` | 17 | 引用了种子 | 4 | 建议采纳(子问题1) | 采纳 | 1 | 该文聚焦RAG引用评估指标（引用正确性与引用忠实性），可作为子问题1关于评价指标的证据，但未涉及常用数据集与基线。 |
| 23 | 2025 | Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs)  | 面向企业知识管理与文档自动化的检索增强生成（RAG）与大语言模型（LLM）：系统文献综述 | `10.3390/app16010368` | 11 | 引用了种子 | 4 | 建议采纳(子问题1) | 采纳 | 1 | 摘要明确讨论了RAG评估中的验证指标（如k-fold交叉验证和静态留出集），可作为子问题1的证据；但未具体说明常用数据集或基线，因此不充分支持子问题2。 |
| 24 | 2025 | Can LLMs be Trusted for Evaluating RAG Systems? A Survey of Methods an | 大语言模型能否可信地评估 RAG 系统？方法与数据集综述 | `10.1109/sds66131.2025.00010` | 11 | 引用了种子 | 4 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 该综述系统梳理了63篇文献中的RAG评估方法，明确涵盖数据集（对应子问题2）与评估指标/自动化评估方法（对应子问题1），可直接作为两个子问题的证据。 |
| 25 | 2025 | Faithfulness-Aware Multi-Objective Context Ranking for Retrieval-Augme | 面向检索增强生成的忠实性感知多目标上下文排序 | `10.1145/3797161.3797180` | 9 | 引用了种子 | 4 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 该摘要报告了RAG排序方法的评估，使用了Exact Match、faithfulness指标和幻觉率等指标，并在Natural Questions、TriviaQA、HotpotQA数据集上与RankRAG等基线比较，因此可作为子问题1和2的证据。 |

## 摘要（判定用）
*(省略摘要部分以保持文件整洁，与原文一致)*

## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | Gemini |
| 日期 | 2026-09-24 |
| 采纳的候选编号 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 16, 18, 20, 21, 22, 23, 24, 25 |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |