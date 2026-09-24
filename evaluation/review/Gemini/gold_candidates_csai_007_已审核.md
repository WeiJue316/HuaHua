# 金标候选：csai_007

**问题**：What methods are used for query expansion in neural information retrieval?

　　→ 神经信息检索中用于查询扩展的方法有哪些？

**子问题**：

1. What are the main query expansion families?
　　→ 查询扩展的主要类别有哪些？

2. What evidence supports their effectiveness?
　　→ 有哪些证据支持其有效性？


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
|---:|---:|---|---|---|---:|---|---:|---|---:|---|---|
| 1 | 2024 | "In-Context Learning" or: How I learned to stop worrying and love "App | "上下文学习"，或：我如何学会不再担忧并爱上"应用信息检索" | `10.1145/3626772.3657842` | 12 | 引用了种子 | 5 | 建议不采纳 | 不采纳 | | 论文讨论ICL中少样本示例选择与IR检索的类比，未涉及查询扩展方法或其有效性，属于主题相邻。 |
| 2 | 2022 | Query Expansion Using Contextual Clue Sampling with Language Models | 使用语言模型与上下文线索采样的查询扩展 | `10.48550/arxiv.2210.07093` | 3 | 被种子引用 | 5 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 论文提出基于语言模型上下文采样的查询扩展方法，属于一个查询扩展家族，并给出检索与QA性能提升的实验证据支持其有效性。 |
| 3 | 2024 | Semantic grounding of LLMs using knowledge graphs for query reformulat | 面向医学信息检索查询重构的基于知识图谱的大语言模型语义接地 | `10.1109/bigdata62323.2024.10826117` | 1 | 引用了种子 | 5 | 建议不采纳 | 不采纳 | | 主题相邻：该文研究查询重构/精炼而非查询扩展，且未提供查询扩展有效性的证据。 |
| 4 | 2026 | A critical evaluation of generative query expansion on biomedical lite | 生成式查询扩展在生物医学文献检索中的批判性评估 | `10.1093/jamia/ocag037` | 0 | 引用了种子 | 5 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 该文系统评估了八种生成式查询扩展方法在生物医学检索中的效果，既涉及生成式查询扩展这一方法家族，也提供了其有效性的量化证据。 |
| 5 | 2025 | Large Language Models for Information Retrieval: A Survey | 大语言模型用于信息检索：综述 | `10.1145/3748304` | 98 | 引用了种子 | 4 | 建议采纳(子问题1) | 采纳 | 1 | 该综述涵盖LLM在IR中的查询重写器，与查询扩展家族直接相关，但摘要未提供关于其有效性的具体证据。 |
| 6 | 2024 | Can Query Expansion Improve Generalization of Strong Cross-Encoder Ran | 查询扩展能否提升强交叉编码器排序模型的泛化能力？ | `10.1145/3626772.3657979` | 13 | 引用了种子 | 4 | 建议采纳(子问题2) | 采纳 | 2 | 该论文通过BEIR和TREC DL实验证明，采用推理链关键词生成及自一致性、倒数排名加权与融合等查询扩展步骤能提升强交叉编码器排序器（MonoT5、RankT5）的nDCG@10，为查询扩展有效性提供证据，但未系统梳理查询扩展的主要方法家族。 |
| 7 | 2023 | A Test Collection of Synthetic Documents for Training Rankers: ChatGPT | 用于训练排序模型的合成文档测试集：ChatGPT 与人类专家的对比 | `10.1145/3583780.3615111` | 12 | 引用了种子 | 4 | 建议不采纳 | 不采纳 | | 主题相邻：该论文研究用合成文档训练神经重排序器，而非查询扩展方法或其有效性证据。 |
| 8 | 2024 | Drop your Decoder: Pre-training with Bag-of-Word Prediction for Dense  | 丢弃解码器：基于词袋预测的预训练用于稠密段落检索 | `10.1145/3626772.3657792` | 5 | 引用了种子 | 4 | 建议不采纳 | 不采纳 | | 该文研究密集段落检索的MAE预训练与Bag-of-Word预测，未涉及查询扩展方法或其有效性，属于主题相邻。 |
| 9 | 2023 | Can Query Expansion Improve Generalization of Strong Cross-Encoder Ran | 查询扩展能否提升强交叉编码器排序模型的泛化能力？ | `10.48550/arxiv.2311.09175` | 0 | 引用了种子 | 4 | 建议采纳(子问题2) | 采纳 | 2 | 论文通过实验证明对强交叉编码器排序器进行查询扩展并融合扩展查询排名可提升 nDCG@10，因此可作为查询扩展有效性的证据，但未系统梳理主要查询扩展家族。 |
| 10 | 2026 | Bmqexpander: ontology-guided query expansion for biomedical document r | BMQExpander：基于大语言模型的本体引导生物医学文档检索查询扩展 | `10.1007/s10618-026-01220-z` | 0 | 引用了种子 | 4 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 该文提出一种本体引导的LLM查询扩展方法并报告了NDCG@10提升（最高22.1%），既可作为查询扩展家族（本体+LLM生成式扩展）的证据，也提供了其有效性的实证结果。 |
| 11 | 2022 | Text Embeddings by Weakly-Supervised Contrastive Pre-training | 基于弱监督对比预训练的文本嵌入 | `10.48550/arxiv.2212.03533` | 123 | 被种子引用 | 3 | 建议不采纳 | 不采纳 | | 该文提出通用文本嵌入模型E5并评估检索效果，未涉及查询扩展方法或其有效性证据，属于神经检索主题相邻。 |
| 12 | 2024 | Fine-Tuning LLaMA for Multi-Stage Text Retrieval | 面向多阶段文本检索的LLaMA微调 | `10.1145/3626772.3657951` | 112 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | | 该文聚焦于微调 LLaMA 作为稠密检索器与重排序器，仅在背景处提及提示 LLM 生成查询扩展，未研究任何查询扩展家族或其有效性证据，属于主题相邻（神经检索）而非查询扩展证据。 |
| 13 | 2024 | CRUD-RAG: A Comprehensive Chinese Benchmark for Retrieval-Augmented Ge | CRUD-RAG：面向大语言模型检索增强生成的综合性中文基准 | `10.1145/3701228` | 96 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | | 该论文是RAG系统评测基准，涉及检索器与知识库构建，但未讨论查询扩展方法或其实证效果，属于主题相邻而非直接相关。 |
| 14 | 2024 | When Search Engine Services Meet Large Language Models: Visions and Ch | 当搜索引擎服务遇上大语言模型：愿景与挑战 | `10.1109/tsc.2024.3451185` | 65 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | | 主题相邻：讨论LLM与搜索引擎整合，仅泛泛提到通过优化改善查询结果，未具体涉及查询扩展方法族或其效果证据。 |
| 15 | 2025 | A Survey of Conversational Search | 对话式搜索综述 | `10.1145/3759453` | 42 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | | 主题相邻：该综述关注对话式搜索与查询重构，但未涉及神经信息检索中的查询扩展方法家族或其有效性证据。 |
| 16 | 2025 | A Comprehensive Survey of Retrieval-Augmented Large Language Models fo | 面向农业决策的检索增强大语言模型综合综述：未解决的问题与研究机遇 | `10.2478/jaiscr-2025-0007` | 28 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | | 该论文讨论农业决策支持中的检索增强生成（RAG），虽与检索相关，但未涉及神经信息检索中的查询扩展方法或其有效性证据，属于主题相邻。 |
| 17 | 2024 | SimIIR 3: A Framework for the Simulation of Interactive and Conversati | SimIIR 3：交互式与会话式信息检索模拟框架 | `10.1145/3673791.3698427` | 13 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | | 该摘要仅介绍交互与对话式信息检索仿真框架，未涉及任何查询扩展方法或其有效性证据，属于主题相邻但无法回答子问题。 |
| 18 | 2024 | Exploration Robot Chat: Uncovering Decades of Exploration Knowledge an | Exploration Robot Chat：利用会话式大语言模型挖掘数十年的探索知识与数据 | `10.2118/218439-ms` | 8 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | | 主题相邻：论文讨论检索增强生成（RAG）与LLM在勘探数据中的应用，但未涉及神经信息检索中的查询扩展方法或其有效性证据。 |
| 19 | 2023 | Report on the 1st Workshop on Generative Information Retrieval (Gen-IR | 第 1 届生成式信息检索研讨会（Gen-IR 2023）报告（SIGIR 2023） | `10.1145/3642979.3642995` | 0 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | | 主题相邻：该报告聚焦生成式信息检索与LLM/diffusion模型，但摘要未涉及查询扩展方法家族或其有效性证据。 |
| 20 | 2026 | When More Reformulations Hurt: Avoiding Drift using Ranker Feedback | 当更多查询改写反而有害：利用排序器反馈避免漂移 | `10.1145/3805712.3809721` | 0 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | | 主题相邻：讨论查询改写/重排序的推理预算与漂移权衡，但未梳理查询扩展方法族，也未提供其有效性的证据（摘要中亦无实验结果）。 |
| 21 | 2024 | A Survey on Hallucination in Large Language Models: Principles, Taxono | 大型语言模型幻觉研究综述：原理、分类、挑战与开放问题 | `10.1145/3703155` | 2084 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | | 主题相邻：该文综述LLM幻觉检测与缓解及检索增强LLM，但未涉及神经信息检索中的查询扩展方法或其有效性证据。 |
| 22 | 2023 | Is ChatGPT Good at Search? Investigating Large Language Models as Re-R | ChatGPT 擅长搜索吗？探究大型语言模型作为重排序智能体 | `10.18653/v1/2023.emnlp-main.923` | 230 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | | 该论文研究LLM作为相关性重排序代理（ranking/re-ranking），未涉及查询扩展方法或其有效性证据，属于主题相邻（LLM与IR）而非查询扩展。 |
| 23 | 2025 | Hallucination Mitigation for Retrieval-Augmented Large Language Models | 检索增强大型语言模型的幻觉缓解：综述 | `10.3390/math13050856` | 130 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | | 该综述聚焦RAG幻觉缓解，未涉及神经信息检索中的查询扩展方法家族或效果证据，属于主题相邻。 |
| 24 | 2026 | Retrieval-Augmented Generation for AI-Generated Content: A Survey | 面向人工智能生成内容的检索增强生成：综述 | `10.1007/s41019-025-00335-5` | 106 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | | 该综述聚焦检索增强生成（RAG）的整体框架与应用，摘要中未涉及查询扩展方法或其有效性证据，属于主题相邻而非直接相关。 |
| 25 | 2022 | Generate rather than Retrieve: Large Language Models are Strong Contex | 生成而非检索：大型语言模型是强大的上下文生成器 | `10.48550/arxiv.2209.10063` | 86 | 被种子引用 | 2 | 建议不采纳 | 不采纳 | | 主题相邻：该论文研究用LLM生成上下文替代文档检索，而非神经信息检索中的查询扩展方法或其有效性证据。 |

*(注：摘要部分为节省空间未在此处重复，完整文本可参考原文档。)*

## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | AI 助手 |
| 日期 | 2026-09-24 |
| 采纳的候选编号 | 2, 4, 5, 6, 9, 10 |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |