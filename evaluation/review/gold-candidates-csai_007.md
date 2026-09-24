# 金标候选：csai_007

**问题**：What methods are used for query expansion in neural information retrieval?

　　→ 在神经信息检索中，查询扩展使用了哪些方法？

**子问题**：

1. What are the main query expansion families?
　　→ 查询扩展的主要家族有哪些？

2. What evidence supports their effectiveness?
　　→ 有哪些证据支持其有效性？


**现有 gold**：2 篇　**年份范围**：(2022, 2026)　**引用图候选**：25 篇

## 判定标准

一篇论文算作 gold，当且仅当**领域专家会把它作为回答某个子问题的证据引用**。
按子问题分别判定，因为证据是按子问题分配的。

**「初审建议」是模型预判；「判定」栏是当前审计结论，不因填写「判定」就自动等于人工审核。**
每条「采纳」都附带一句从摘要逐字摘出的引文，程序已核对引文确实
出现在摘要中——**核对引文比通读摘要快得多，这是本表的验证单元**。

标注来源需在 `evaluation/datasets/VERSIONS.md` 中如实记录：
模型初审 + Codex 逐条审计 + 摘要逐字核验；不等同于独立人工金标。

逐条检查：

1. 论文是否真正回答某个子问题（不是主题相邻）
2. 年份是否在声明范围内
3. 摘要是否包含可以作为证据的完整句子
4. 判定它支撑哪个子问题（填编号）

## 候选清单

| # | 年份 | 标题 | 中文标题(机翻) | DOI | 被引 | 关系 | 命中 | 初审建议 | 判定 | 子问题 | 备注 |
|---:|---:|---|---|---|---:|---|---:|---|---:|---|---|
| 1 | 2024 | "In-Context Learning" or: How I learned to stop worrying and love "App | “上下文学习”，或：我如何学会不再担忧并爱上“应用信息检索” | `10.1145/3626772.3657842` | 12 | 引用了种子 | 5 | 建议不采纳 | 不采纳 |  | 主题相邻：论文讨论ICL中few-shot示例选择与神经排序器，但未涉及查询扩展方法或其有效性证据。 |
| 2 | 2022 | Query Expansion Using Contextual Clue Sampling with Language Models | 使用基于语言模型的上下文线索采样进行查询扩展 | `10.48550/arxiv.2210.07093` | 3 | 被种子引用 | 5 | 建议采纳(两个子问题) | 采纳 | 1 | 引文｜One recent line of research uses language models to generate query-related contexts for expansion.｜理由｜审计修正：该句支持查询扩展方法家族，不提供有效性对比证据。 |
| 3 | 2024 | Semantic grounding of LLMs using knowledge graphs for query reformulat | 基于知识图谱的大语言模型语义接地用于医学信息检索中的查询重构 | `10.1109/bigdata62323.2024.10826117` | 1 | 引用了种子 | 5 | 建议不采纳 | 不采纳 |  | 主题相邻：论文聚焦医学检索中基于知识图谱的查询重构/精炼，未直接讨论 query expansion 的方法家族或其有效性证据。 |
| 4 | 2026 | A critical evaluation of generative query expansion on biomedical lite | 对生物医学文献检索中生成式查询扩展的批判性评估 | `10.1093/jamia/ocag037` | 0 | 引用了种子 | 5 | 建议采纳(子问题2) | 采纳 | 2 | 引文｜On BioASQ-Y/N, GPT-4o-based query expansion shifts Recall@10 to 0.417-0.512 and nDCG@10 to 0.358-0.479, relative to a baseline of 0.491 and 0.456.｜理由｜该文系统评估了八种生成式查询扩展方法在多个数据集上的检索效果，提供了支持查询扩展有效性的定量证据。 |
| 5 | 2025 | Large Language Models for Information Retrieval: A Survey | 大语言模型在信息检索中的应用：综述 | `10.1145/3748304` | 98 | 引用了种子 | 4 | 建议采纳(子问题1) | 采纳 | 1 | 引文｜In this survey, we delve into the confluence of LLMs and IR systems, including crucial aspects such as query rewriters, retrievers, rerankers, readers, and search agents.｜理由｜该综述明确将查询重写器（query rewriters）列为LLM与IR结合的关键环节，可作为梳理查询扩展/重写方法家族的证据，但摘要未提供任何效果验证的实验证据，故不支持子问题2。 |
| 6 | 2024 | Can Query Expansion Improve Generalization of Strong Cross-Encoder Ran | 查询扩展能否提升强交叉编码器排序器的泛化能力？ | `10.1145/3626772.3657979` | 13 | 引用了种子 | 4 | 建议采纳(子问题2) | 采纳 | 2 | 引文｜Experiments on BEIR and TREC Deep Learning 2019/2020 show that the nDCG@10 scores of both MonoT5 and RankT5 following these steps are improved, which points out a direction for applying query expansion to strong cross-encoder rankers.｜理由｜该文通过BEIR和TREC DL实验证明查询扩展步骤能提升强交叉编码器排序器的nDCG@10，为查询扩展有效性提供了直接证据，但未梳理查询扩展方法家族，故仅支持子问题2。 |
| 7 | 2023 | A Test Collection of Synthetic Documents for Training Rankers: ChatGPT | 用于训练排序器的合成文档测试集：ChatGPT 与人类专家之比较 | `10.1145/3583780.3615111` | 12 | 引用了种子 | 4 | 建议不采纳 | 不采纳 |  | 主题相邻：该文研究用LLM生成合成文档来训练cross-encoder重排器，属于神经检索的训练数据增强，并未涉及查询扩展方法或其有效性证据。 |
| 8 | 2024 | Drop your Decoder: Pre-training with Bag-of-Word Prediction for Dense  | 丢弃解码器：基于词袋预测的稠密段落检索预训练 | `10.1145/3626772.3657792` | 5 | 引用了种子 | 4 | 建议不采纳 | 不采纳 |  | 该论文研究稠密检索的预训练方法（用词袋预测替代解码器），与查询扩展方法及其有效性证据无关，属于主题相邻。 |
| 9 | 2023 | Can Query Expansion Improve Generalization of Strong Cross-Encoder Ran | 查询扩展能否提升强交叉编码器排序器的泛化能力？ | `10.48550/arxiv.2311.09175` | 0 | 引用了种子 | 4 | 建议采纳(子问题2) | 不采纳 |  | 审计排除｜与已采纳的 10.1145/3626772.3657979 标题和引文完全相同，属同一论文的重复版本。 |
| 10 | 2026 | Bmqexpander: ontology-guided query expansion for biomedical document r | BMQExpander：利用大语言模型的本体引导生物医学文档检索查询扩展 | `10.1007/s10618-026-01220-z` | 0 | 引用了种子 | 4 | 建议采纳(两个子问题) | 采纳 | 1,2 | 引文｜We show that BMQExpander has superior retrieval performance on three popular biomedical Information Retrieval (IR) benchmarks: NFCorpus, TREC-COVID, and SciFact—with improvements of up to 22.1% in NDCG@10 over sparse baselines and up to 6.5% over the strongest baseline.｜理由｜The paper proposes an ontology-guided, LLM-based query expansion pipeline (a query expansion family) and reports quantified retrieval gains (NDCG@10 improvements over sparse, dense and QE baselines), giving evidence for effectiveness. |
| 11 | 2022 | Text Embeddings by Weakly-Supervised Contrastive Pre-training | 基于弱监督对比预训练的文本嵌入 | `10.48550/arxiv.2212.03533` | 123 | 被种子引用 | 3 | 建议不采纳 | 不采纳 |  | 主题相邻：该文提出E5文本嵌入模型，属于神经检索的表示学习，但全文未涉及任何查询扩展方法或其有效性证据。 |
| 12 | 2024 | Fine-Tuning LLaMA for Multi-Stage Text Retrieval | 微调LLaMA用于多阶段文本检索 | `10.1145/3626772.3657951` | 112 | 引用了种子 | 3 | 建议不采纳 | 不采纳 |  | 主题相邻：摘要仅在背景中提及 query expansion，研究重点是微调 LLaMA 作为检索器与重排序器，未涉及查询扩展家族分类或有效性证据。 |
| 13 | 2024 | CRUD-RAG: A Comprehensive Chinese Benchmark for Retrieval-Augmented Ge | CRUD-RAG：面向大语言模型检索增强生成的综合中文基准 | `10.1145/3701228` | 96 | 引用了种子 | 3 | 建议不采纳 | 不采纳 |  | 该论文是RAG系统评测基准，仅涉及检索器组件整体评估，未讨论任何查询扩展方法或其有效性证据，属于主题相邻。 |
| 14 | 2024 | When Search Engine Services Meet Large Language Models: Visions and Ch | 当搜索引擎服务遇上大语言模型：愿景与挑战 | `10.1109/tsc.2024.3451185` | 65 | 引用了种子 | 3 | 建议不采纳 | 不采纳 |  | 该文是对搜索引擎与大语言模型融合（Search4LLM/LLM4Search）的愿景与挑战综述，仅笼统提及“improve query outcomes through optimization”，未涉及查询扩展方法家族或其实证效果，属主题相邻。 |
| 15 | 2025 | A Survey of Conversational Search | 对话式搜索综述 | `10.1145/3759453` | 42 | 引用了种子 | 3 | 建议不采纳 | 不采纳 |  | 主题相邻：该文是对话式搜索综述，仅在列举系统模块时提及 query reformulation，未涉及神经信息检索中查询扩展的方法家族或有效性证据。 |
| 16 | 2025 | A Comprehensive Survey of Retrieval-Augmented Large Language Models fo | 面向农业决策的检索增强大语言模型综合综述：未解决的问题与研究机遇 | `10.2478/jaiscr-2025-0007` | 28 | 引用了种子 | 3 | 建议不采纳 | 不采纳 |  | 主题相邻：该文讨论农业决策支持系统中LLM与RAG的应用，未涉及神经信息检索中的查询扩展方法或其有效性证据。 |
| 17 | 2024 | SimIIR 3: A Framework for the Simulation of Interactive and Conversati | SimIIR 3：用于交互式和会话式信息检索模拟的框架 | `10.1145/3673791.3698427` | 13 | 引用了种子 | 3 | 建议不采纳 | 不采纳 |  | 该摘要描述的是交互式与会话式信息检索的模拟框架（SimIIR 3）及其组件，属于IR主题相邻工作，但未涉及任何查询扩展方法或其有效性证据，无法回答任一子问题。 |
| 18 | 2024 | Exploration Robot Chat: Uncovering Decades of Exploration Knowledge an | Exploration Robot Chat：利用会话式大语言模型发掘数十年的探索知识与数据 | `10.2118/218439-ms` | 8 | 引用了种子 | 3 | 建议不采纳 | 不采纳 |  | 主题相邻：论文讨论面向油气勘探的检索增强生成（RAG）系统与对话式LLM，未涉及神经信息检索中的查询扩展方法或其有效性证据。 |
| 19 | 2023 | Report on the 1st Workshop on Generative Information Retrieval (Gen-IR | SIGIR 2023 第一届生成式信息检索研讨会（Gen-IR 2023）报告 | `10.1145/3642979.3642995` | 0 | 引用了种子 | 3 | 建议不采纳 | 不采纳 |  | 该摘要仅介绍生成式信息检索研讨会的目标、形式与成果，未涉及查询扩展方法或有效性证据，属于主题相邻但无关。 |
| 20 | 2026 | When More Reformulations Hurt: Avoiding Drift using Ranker Feedback | 当更多改写反而有害：利用排序器反馈避免漂移 | `10.1145/3805712.3809721` | 0 | 引用了种子 | 3 | 建议不采纳 | 不采纳 |  | 主题相邻：该文讨论查询改写/扩展结果的自适应选择与推理预算权衡，但摘要既未梳理查询扩展方法的主要类别，也未提供有效性证据。 |
| 21 | 2024 | A Survey on Hallucination in Large Language Models: Principles, Taxono | 大语言模型幻觉综述：原理、分类、挑战与开放问题 | `10.1145/3703155` | 2084 | 引用了种子 | 2 | 建议不采纳 | 不采纳 |  | 该综述主题是 LLM 幻觉的检测与缓解，虽涉及信息检索但完全未讨论查询扩展方法或其有效性，属于「主题相邻」而非相关证据。 |
| 22 | 2023 | Is ChatGPT Good at Search? Investigating Large Language Models as Re-R | ChatGPT擅长搜索吗？探究大语言模型作为重排序智能体 | `10.18653/v1/2023.emnlp-main.923` | 230 | 引用了种子 | 2 | 建议不采纳 | 不采纳 |  | 主题相邻：论文研究LLM作为重排序代理，而非查询扩展方法。 |
| 23 | 2025 | Hallucination Mitigation for Retrieval-Augmented Large Language Models | 检索增强大语言模型的幻觉缓解：综述 | `10.3390/math13050856` | 130 | 引用了种子 | 2 | 建议不采纳 | 不采纳 |  | 主题相邻：论文讨论RAG/LLM幻觉缓解，未涉及神经信息检索中的查询扩展方法或其有效性证据。 |
| 24 | 2026 | Retrieval-Augmented Generation for AI-Generated Content: A Survey | 面向AI生成内容的检索增强生成：综述 | `10.1007/s41019-025-00335-5` | 106 | 引用了种子 | 2 | 建议不采纳 | 不采纳 |  | 该论文是检索增强生成（RAG）综述，聚焦检索器如何增强生成器及RAG应用，未涉及神经信息检索中的查询扩展方法或其实证证据，属于主题相邻。 |
| 25 | 2022 | Generate rather than Retrieve: Large Language Models are Strong Contex | 生成而非检索：大语言模型是强大的上下文生成器 | `10.48550/arxiv.2209.10063` | 86 | 被种子引用 | 2 | 建议不采纳 | 不采纳 |  | 该论文研究用大语言模型生成上下文文档替代检索，属于知识密集型任务与检索生成结合，主题相邻但并未涉及神经信息检索中的查询扩展方法或其有效性证据。 |

## 摘要（判定用）

判据 3 要求确认摘要里存在可作为证据的完整句子，因此这里附上原文摘要。
机翻标题仅供快速定位，**判定必须依据英文原文**。

**1. "In-Context Learning" or: How I learned to stop worrying and love "Applied Information Retrieval"**

- DOI：`10.1145/3626772.3657842`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（引用了种子）

With the increasing ability of large language models (LLMs), in-context learning (ICL) has evolved as a new paradigm for natural language processing (NLP), where instead of fine- tuning the parameters of an LLM specific to a downstream task with labeled examples,a small number of such examples is appended to a prompt instruction for controlling the decoder's generation process. ICL, thus, is conceptually similar to a non-parametric approach, such as k-NN,where the prediction for each instance essentially depends on the local topology, i.e., on a localised set of similar instances and their labels (called few-shot examples). This suggests that a test instance in ICL is analogous to a query in IR, and similar examples in ICL retrieved from a training set relate to a set of documents retrieved from a collection in IR. While standard unsupervised ranking models can be used to retrieve these few-shot examples from a training set, the effectiveness of the examples can potentially be improved by re-defining the notion of relevance specific to its utility for the downstream task, i.e., considering an example to be relevant if including it in the prompt instruction leads to a correct prediction. With this task-specific notion of relevance, it is possible to train a supervised ranking model (e.g., a bi-encoder or cross-encoder), which potentially learns to optimally select the few-shot examples. We believe that the recent advances in neural rankers can potentially find a use case for this task of optimally choosing examples for more effective downstream ICL predictions.

**2. Query Expansion Using Contextual Clue Sampling with Language Models**

- DOI：`10.48550/arxiv.2210.07093`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（被种子引用）

Query expansion is an effective approach for mitigating vocabulary mismatch between queries and documents in information retrieval. One recent line of research uses language models to generate query-related contexts for expansion. Along this line, we argue that expansion terms from these contexts should balance two key aspects: diversity and relevance. The obvious way to increase diversity is to sample multiple contexts from the language model. However, this comes at the cost of relevance, because there is a well-known tendency of models to hallucinate incorrect or irrelevant contexts. To balance these two considerations, we propose a combination of an effective filtering strategy and fusion of the retrieved documents based on the generation probability of each context. Our lexical matching based approach achieves a similar top-5/top-20 retrieval accuracy and higher top-100 accuracy compared with the well-established dense retrieval model DPR, while reducing the index size by more than 96%. For end-to-end QA, the reader model also benefits from our method and achieves the highest Exact-Match score against several competitive baselines.

**3. Semantic grounding of LLMs using knowledge graphs for query reformulation in medical information retrieval**

- DOI：`10.1109/bigdata62323.2024.10826117`
- 关联种子：`doi:10.48550/arxiv.2305.03653`（引用了种子）

The widespread adoption of electronic health records has generated a vast amount of patient-related data, mostly presented in the form of unstructured text, which could be used for document retrieval. However, querying these texts in full could present challenges due to their unstructured and lengthy nature, as they may contain noise or irrelevant terms that can interfere with the retrieval process. Recently, large language models (LLMs) have revolutionized natural language processing tasks. However, despite their promising capabilities, their use in the medical domain has raised concerns due to their lack of understanding, hallucinations, and reliance on outdated knowledge. To address these concerns, we evaluate a Retrieval Augmented Generation (RAG) approach that integrates medical knowledge graphs with LLMs to support query refinement in medical document retrieval tasks. Our initial findings from experiments using two benchmark TREC datasets demonstrate that knowledge graphs can effectively ground LLMs in the medical domain.

**4. A critical evaluation of generative query expansion on biomedical literature retrieval**

- DOI：`10.1093/jamia/ocag037`
- 关联种子：`doi:10.48550/arxiv.2305.03653`（引用了种子）

OBJECTIVE: To evaluate the effectiveness of generative query expansion for biomedical literature retrieval. MATERIALS AND METHODS: We thoroughly examined eight generative query expansion methods using three large language models across five datasets for biomedical literature retrieval. We further performed a quantitative analysis, including performance comparisons, rank transition analysis, and article-type effect analysis. We also conducted a qualitative examination of representative cases, from which we derived an error taxonomy. RESULTS: On BioASQ-Y/N, GPT-4o-based query expansion shifts Recall@10 to 0.417-0.512 and nDCG@10 to 0.358-0.479, relative to a baseline of 0.491 and 0.456. For PubMedQA, Precision@1 ranges from 0.764 to 0.876 and nDCG@10 from 0.847 to 0.931, compared with baseline values of 0.893 and 0.935. For 2019-Trec-PM, query expansion yields Recall@100 of 0.217-0.256 and nDCG@100 of 0.272-0.312, versus a baseline of 0.227 and 0.274. Similarly, for 2018-TREC-PM, Recall@100 spans 0.169-0.227 and nDCG@100 spans 0.195-0.250, relative to baseline scores of 0.164 and 0.191. For 2017-TREC-PM, Recall@100 and nDCG@100 fall within 0.111-0.139 and 0.154-0.191 under query expansion, compared with baseline metrics of 0.102 and 0.147. Both general-purpose and domain-specific Llama-based models demonstrate similar performance to GPT-4o. DISCUSSION AND CONCLUSION: The impact of query expansion varies significantly by the expansion methods and type of evidence, but is relatively agnostic to backbone model choice. Notably, query expansion primarily affects article ranking but has a limited impact on the screening stage. Our findings underscore the unique challenges of biomedical literature retrieval and highlight the need to develop domain-specific information retrieval techniques.

**5. Large Language Models for Information Retrieval: A Survey**

- DOI：`10.1145/3748304`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（引用了种子）

As a primary means of information acquisition, information retrieval (IR) systems, such as search engines, have integrated themselves into our daily lives. These systems also serve as components of dialogue, question-answering, and recommender systems. The trajectory of IR has evolved dynamically from its origins in term-based methods to its integration with advanced neural models. While the neural models excel at capturing complex contextual signals and semantic nuances, they still face challenges such as data scarcity, interpretability, and the generation of contextually plausible yet potentially inaccurate responses. This evolution requires a combination of traditional methods (such as term-based sparse retrieval methods with rapid response) and modern neural architectures (such as language models with powerful language understanding capacity). Meanwhile, the emergence of large language models (LLMs) has revolutionized natural language processing due to their remarkable language understanding, generation, and reasoning abilities. Consequently, recent research has sought to leverage LLMs to improve IR systems. Given the rapid evolution of this research trajectory, it is necessary to consolidate existing methodologies and provide nuanced insights through a comprehensive overview. In this survey, we delve into the confluence of LLMs and IR systems, including crucial aspects such as query rewriters, retrievers, rerankers, readers, and search agents.

**6. Can Query Expansion Improve Generalization of Strong Cross-Encoder Rankers?**

- DOI：`10.1145/3626772.3657979`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（引用了种子）

Query expansion has been widely used to improve the search results of first-stage retrievers, yet its influence on second-stage, cross-encoder rankers remains under-explored. A recent study shows that current expansion techniques benefit weaker models but harm stronger rankers. In this paper, we re-examine this conclusion and raise the following question: Can query expansion improve generalization of strong cross-encoder rankers? To answer this question, we first apply popular query expansion methods to different cross-encoder rankers and verify the deteriorated zero-shot effectiveness. We identify two vital steps in the experiment: high-quality keyword generation and minimally-disruptive query modification. We show that it is possible to improve the generalization of a strong neural ranker, by generating keywords through a reasoning chain and aggregating the ranking results of each expanded query via self-consistency, reciprocal rank weighting, and fusion. Experiments on BEIR and TREC Deep Learning 2019/2020 show that the nDCG@10 scores of both MonoT5 and RankT5 following these steps are improved, which points out a direction for applying query expansion to strong cross-encoder rankers.

**7. A Test Collection of Synthetic Documents for Training Rankers: ChatGPT vs. Human Experts**

- DOI：`10.1145/3583780.3615111`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（引用了种子）

In this resource paper, we investigate the usefulness of generative Large Language Models (LLMs) in generating training data for cross-encoder re-rankers in a novel direction: generating synthetic documents instead of synthetic queries. We introduce a new dataset, ChatGPT-RetrievalQA, and compare the effectiveness of strong models fine-tuned on both LLM-generated and human-generated data. We build ChatGPT-RetrievalQA based on an existing dataset, human ChatGPT Comparison Corpus (HC3), consisting of public question collections with human responses and answers from ChatGPT. We fine-tune a range of cross-encoder re-rankers on either human-generated or ChatGPT-generated data. Our evaluation on MS MARCO DEV, TREC DL'19, and TREC DL'20 demonstrates that cross-encoder re-ranking models trained on LLM-generated responses are significantly more effective for out-of-domain re-ranking than those trained on human responses. For in-domain re-ranking, the human-trained re-rankers outperform the LLM-trained re-rankers. Our novel findings suggest that generative LLMs have high potential in generating training data for neural retrieval models and can be used to augment training data, especially in domains with smaller amounts of labeled data. We believe that our dataset, ChatGPT-RetrievalQA, presents various opportunities for analyzing and improving rankers with human and synthetic data. We release our data, code, and model checkpoints for future work.

**8. Drop your Decoder: Pre-training with Bag-of-Word Prediction for Dense Passage Retrieval.**

- DOI：`10.1145/3626772.3657792`
- 关联种子：`doi:10.48550/arxiv.2305.03653`（引用了种子）

Masked auto-encoder pre-training has emerged as a prevalent technique for initializing and enhancing dense retrieval systems. It generally utilizes additional Transformer decoder blocks to provide sustainable supervision signals and compress contextual information into dense representations. However, the underlying reasons for the effectiveness of such a pre-training technique remain unclear. The usage of additional Transformer-based decoders also incurs significant computational costs. In this study, we aim to shed light on this issue by revealing that masked auto-encoder (MAE) pre-training with enhanced decoding significantly improves the term coverage of input tokens in dense representations, compared to vanilla BERT checkpoints. Building upon this observation, we propose a modification to the traditional MAE by replacing the decoder of a masked auto-encoder with a completely simplified Bag-of-Word prediction task. This modification enables the efficient compression of lexical signals into dense representations through unsupervised pre-training. Remarkably, our proposed method achieves state-of-the-art retrieval performance on several large-scale retrieval benchmarks without requiring any additional parameters, which provides a 67% training speed-up compared to standard masked auto-encoder pre-training with enhanced decoding.

**9. Can Query Expansion Improve Generalization of Strong Cross-Encoder Rankers?**

- DOI：`10.48550/arxiv.2311.09175`
- 关联种子：`doi:10.48550/arxiv.2305.03653`（引用了种子）

Query expansion has been widely used to improve the search results of first-stage retrievers, yet its influence on second-stage, cross-encoder rankers remains under-explored. A recent work of Weller et al. [44] shows that current expansion techniques benefit weaker models such as DPR and BM25 but harm stronger rankers such as MonoT5. In this paper, we re-examine this conclusion and raise the following question: Can query expansion improve generalization of strong cross-encoder rankers? To answer this question, we first apply popular query expansion methods to state-of-the-art cross-encoder rankers and verify the deteriorated zero-shot performance. We identify two vital steps for cross-encoders in the experiment: high-quality keyword generation and minimal-disruptive query modification. We show that it is possible to improve the generalization of a strong neural ranker, by prompt engineering and aggregating the ranking results of each expanded query via fusion. Specifically, we first call an instruction-following language model to generate keywords through a reasoning chain. Leveraging self-consistency and reciprocal rank weighting, we further combine the ranking results of each expanded query dynamically. Experiments on BEIR and TREC Deep Learning 2019/2020 show that the nDCG@10 scores of both MonoT5 and RankT5 following these steps are improved, which points out a direction for applying query expansion to strong cross-encoder rankers.

**10. Bmqexpander: ontology-guided query expansion for biomedical document retrieval using large language models**

- DOI：`10.1007/s10618-026-01220-z`
- 关联种子：`doi:10.48550/arxiv.2305.03653`（引用了种子）

Abstract Effective Question Answering (QA) on large biomedical document collections requires effective document retrieval techniques. The latter remains a challenging task due to the domain-specific vocabulary and semantic ambiguity in user queries. We propose BMQExpander , a novel ontology-aware query expansion pipeline that combines medical knowledge—definitions and relationships—from the UMLS Metathesaurus with the generative capabilities of large language models (LLMs) to enhance retrieval effectiveness. We implemented several state-of-the-art baselines, including sparse and dense retrievers, query expansion methods, and biomedical-specific solutions. We show that BMQExpander has superior retrieval performance on three popular biomedical Information Retrieval (IR) benchmarks: NFCorpus, TREC-COVID, and SciFact—with improvements of up to 22.1% in NDCG@10 over sparse baselines and up to 6.5% over the strongest baseline. Further, BMQExpander generalizes robustly under query perturbation settings, in contrast to supervised baselines, achieving up to 12.5% improvement over the strongest baseline. As a side contribution, we publish our paraphrased benchmarks. Finally, our qualitative analysis shows that BMQExpander has the potential to reduce hallucinations compared to other LLM-based query expansion baselines.

**11. Text Embeddings by Weakly-Supervised Contrastive Pre-training**

- DOI：`10.48550/arxiv.2212.03533`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（被种子引用）

This paper presents E5, a family of state-of-the-art text embeddings that transfer well to a wide range of tasks. The model is trained in a contrastive manner with weak supervision signals from our curated large-scale text pair dataset (called CCPairs). E5 can be readily used as a general-purpose embedding model for any tasks requiring a single-vector representation of texts such as retrieval, clustering, and classification, achieving strong performance in both zero-shot and fine-tuned settings. We conduct extensive evaluations on 56 datasets from the BEIR and MTEB benchmarks. For zero-shot settings, E5 is the first model that outperforms the strong BM25 baseline on the BEIR retrieval benchmark without using any labeled data. When fine-tuned, E5 obtains the best results on the MTEB benchmark, beating existing embedding models with 40x more parameters.

**12. Fine-Tuning LLaMA for Multi-Stage Text Retrieval**

- DOI：`10.1145/3626772.3657951`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（引用了种子）

While large language models (LLMs) have shown impressive NLP capabilities, existing IR applications mainly focus on prompting LLMs to generate query expansions or generating permutations for listwise reranking. In this study, we leverage LLMs directly to serve as components in the widely used multi-stage text ranking pipeline. Specifically, we fine-tune the open-source LLaMA-2 model as a dense retriever (repLLaMA) and a pointwise reranker (rankLLaMA). This is performed for both passage and document retrieval tasks using the MS MARCO training data. Our study shows that finetuned LLM retrieval models outperform smaller models. They are more effective and exhibit greater generalizability, requiring only a straightforward training strategy. Moreover, our pipeline allows for the fine-tuning of LLMs at each stage of a multi-stage retrieval pipeline. This demonstrates the strong potential for optimizing LLMs to enhance a variety of retrieval tasks. Furthermore, as LLMs are naturally pre-trained with longer contexts, they can directly represent longer documents. This eliminates the need for heuristic segmenting and pooling strategies to rank long documents. On the MS MARCO and BEIR datasets, our repLLaMA-rankLLaMA pipeline demonstrates a high level of effectiveness.

**13. CRUD-RAG: A Comprehensive Chinese Benchmark for Retrieval-Augmented Generation of Large Language Models**

- DOI：`10.1145/3701228`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（引用了种子）

Retrieval-augmented generation (RAG) is a technique that enhances the capabilities of large language models (LLMs) by incorporating external knowledge sources. This method addresses common LLM limitations, including outdated information and the tendency to produce inaccurate “hallucinated” content. However, evaluating RAG systems is a challenge. Most benchmarks focus primarily on question-answering applications, neglecting other potential scenarios where RAG could be beneficial. Accordingly, in the experiments, these benchmarks often assess only the LLM components of the RAG pipeline or the retriever in knowledge-intensive scenarios, overlooking the impact of external knowledge base construction and the retrieval component on the entire RAG pipeline in non-knowledge-intensive scenarios. To address these issues, this article constructs a large-scale and more comprehensive benchmark and evaluates all the components of RAG systems in various RAG application scenarios. Specifically, we refer to the CRUD actions that describe interactions between users and knowledge bases and also categorize the range of RAG applications into four distinct types—create, read, update, and delete (CRUD). “Create” refers to scenarios requiring the generation of original, varied content. “Read” involves responding to intricate questions in knowledge-intensive situations. “Update” focuses on revising and rectifying inaccuracies or inconsistencies in pre-existing texts. “Delete” pertains to the task of summarizing extensive texts into more concise forms. For each of these CRUD categories, we have developed different datasets to evaluate the performance of RAG systems. We also analyze the effects of various components of the RAG system, such as the retriever, context length, knowledge base construction, and LLM. Finally, we provide useful insights for optimizing the RAG technology for different scenarios. The source code is available at GitHub: https://github.com/IAAR-Shanghai/CRUD_RAG .

**14. When Search Engine Services Meet Large Language Models: Visions and Challenges**

- DOI：`10.1109/tsc.2024.3451185`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（引用了种子）

Combining Large Language Models (LLMs) with search engine services marks a significant shift in the field of services computing, opening up new possibilities to enhance how we search for and retrieve information, understand content, and interact with internet services. This paper conducts an in-depth examination of how integrating LLMs with search engines can mutually benefit both technologies. We focus on two main areas: using search engines to improve LLMs (Search4LLM) and enhancing search engine functions using LLMs (LLM4Search). For Search4LLM, we investigate how search engines can provide diverse high-quality datasets for pre-training of LLMs, how they can use the most relevant documents to help LLMs learn to answer queries more accurately, how training LLMs with Learning-To-Rank (LTR) tasks can enhance their ability to respond with greater precision, and how incorporating recent search results can make LLM-generated content more accurate and current. In terms of LLM4Search, we examine how LLMs can be used to summarize content for better indexing by search engines, improve query outcomes through optimization, enhance the ranking of search results by analyzing document relevance, and help in annotating data for learning-to-rank tasks in various learning contexts. However, this promising integration comes with its challenges, which include addressing potential biases and ethical issues in training models, managing the computational and other costs of incorporating LLMs into search services, and continuously updating LLM training with the ever-changing web content. We discuss these challenges and chart out required research directions to address them. We also discuss broader implications for service computing, such as scalability, privacy concerns, and the need to adapt search engine architectures for these advanced models.

**15. A Survey of Conversational Search**

- DOI：`10.1145/3759453`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（引用了种子）

As a cornerstone of modern information access, search engines have become indispensable in everyday life. With the rapid advancements in AI and natural language processing (NLP) technologies, particularly large language models (LLMs), search engines have evolved to support more intuitive and intelligent interactions between users and systems. Conversational search, an emerging paradigm for next-generation search engines, leverages natural language dialogue to facilitate complex and precise information retrieval, thus attracting significant attention. Unlike traditional keyword-based search engines, conversational search systems enhance user experience by supporting intricate queries, maintaining context over multi-turn interactions, and providing robust information integration and processing capabilities. Key components such as query reformulation, search clarification, conversational retrieval, and response generation work in unison to enable these sophisticated interactions. In this survey, we explore the recent advancements and potential future directions in conversational search, examining the critical modules that constitute a conversational search system. We highlight the integration of LLMs in enhancing these systems and discuss the challenges and opportunities that lie ahead in this dynamic field. Additionally, we provide insights into real-world applications and robust evaluations of current conversational search systems, aiming to guide future research and development in conversational search.

**16. A Comprehensive Survey of Retrieval-Augmented Large Language Models for Decision Making in Agriculture: Unsolved Problems and Research Opportunities**

- DOI：`10.2478/jaiscr-2025-0007`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（引用了种子）

Abstract The breakthrough in developing large language models (LLMs) over the past few years has led to their widespread implementation in various areas of industry, business, and agriculture. The aim of this article is to critically analyse and generalise the known results and research directions on approaches to the development and utilisation of LLMs, with a particular focus on their functional characteristics when integrated into decision support systems (DSSs) for agricultural monitoring. The subject of the research is approaches to the development and integration of LLMs into DSSs for agrotechnical monitoring. The main scientific and applied results of the article are as follows: the world experience of using LLMs to improve agricultural processes has been analysed; a critical analysis of the functional characteristics of LLMs has been carried out, and the areas of application of their architectures have been identified; the necessity of focusing on retrieval-augmented generation (RAG) as an approach to solving one of the main limitations of LLMs, which is the limited knowledge base of training data, has been established; the characteristics and prospects of using LLMs for DSSs in agriculture have been analysed to highlight trustworthiness, explainability and bias reduction as priority areas of research; the potential socio-economic effect from the implementation of LLMs and RAG in the agricultural sector is substantiated.

**17. SimIIR 3: A Framework for the Simulation of Interactive and Conversational Information Retrieval**

- DOI：`10.1145/3673791.3698427`
- 关联种子：`doi:10.48550/arxiv.2305.03653`（引用了种子）

boxes denote the new components added in order to support conversational search simulations, simulated users with cognitive states, Markovian users, search systems powered by pyTerrier, and users powered by Large Language Models.

**18. Exploration Robot Chat: Uncovering Decades of Exploration Knowledge and Data with Conversational Large Language Models**

- DOI：`10.2118/218439-ms`
- 关联种子：`doi:10.48550/arxiv.2305.03653`（引用了种子）

Abstract Hydrocarbon exploration and carbon capture and storage (CCS) evaluation are inherently multi-disciplinary tasks that require the integration of knowledge from multiple datatypes set in a historical and geological context. The diverse nature of subsurface data is often represented by a combination of direct and indirect measurements, interpretations and observations documented in multi-dimensional datasets as images, and written reports. The fidelity of these images and reports can have an enormous variety, and different qualities leading to a challenging situation where explorationists need to determine the value of a source of information while combining these sources across large spatiotemporal contexts. Modern search engines today can not only search through document text but also images. These capabilities have improved our ability to find well-known concepts based on short phrases, or keywords, combined with significant meta-data. While these types of search engines have certainly benefited practitioners, the challenge of combining information from multiple data-sources, data modalities and languages remains an open problem. With the advent of conversational large language model (LLM) systems such as ChatGPT (Achiam et al. 2023) that provide coherent textual information and are informed by their training data, have become a reality. While ChatGPT certainly has taken many industries and their disciplines by storm, the tool is not without its shortcomings. For industry applications, in many cases the information necessary to provide answers will be highly proprietary, not shared with third parties and not part of the training data of the popular LLMs. Furthermore, due to their probabilistic nature LLMs suffer from so-called hallucinations, where the model provides a confident answer based on the user provided input but is non-factual and often non-sensical. To answer a given user-query with factuality it is important to provide relevant information as context to the LLMs. Lewis et al. (2020) proposes combining two systems: An information retrieval system that provide relevant information to answer a given question or to solve a specific task, and a second system being an LLM that is supplemented with the retrieved information as context to answer the user's question. This pattern of so-called retrieval-augmented generation (RAG) has become highly popular in the last year due to the strong conversational capabilities of systems like ChatGPT, accessible developer APIs for interfacing with LLMs, open-source software to orchestrate RAG-systems, as well as the rapid development of open-source LLMs (Touvron et al. 2023). Moreover, since the RAG pattern does not require fine-tuning or re-training a language model, it remains one of the most accessible ways to tailor LLMs to proprietary knowledge bases.

**19. Report on the 1st Workshop on Generative Information Retrieval (Gen-IR 2023) at SIGIR 2023**

- DOI：`10.1145/3642979.3642995`
- 关联种子：`doi:10.48550/arxiv.2305.03653`（引用了种子）

The first edition of the workshop on Generative Information Retrieval (Gen-IR 2023) took place in July 2023 in a hybrid fashion, co-located with the ACM SIGIR Conference 2023 in Taipei (SIGIR 2023). The aim was to bring information retrieval researchers together around the topic of generative AI that gathered attention in 2022 and 2023 with large language models and diffusion models. Given the novelty of the topic, the workshop was focused around multi-sided discussions, namely panels and poster sessions of the accepted proceedings papers. Two main research outcomes are the proceedings of the workshop1 and the potential research directions discussed in this report. Date : 27 July 2023. Website : https://coda.io/@sigir/gen-ir.

**20. When More Reformulations Hurt: Avoiding Drift using Ranker Feedback**

- DOI：`10.1145/3805712.3809721`
- 关联种子：`doi:10.48550/arxiv.2305.03653`（引用了种子）

Modern retrieval pipelines increasingly rely on query reformulation and neural reranking to improve effectiveness, but this comes at a significant computational cost and introduces a fundamental tradeoff between recall and query drift. Generating many reformulated queries can substantially increase recall, yet naïvely merging or exhaustively reranking their results is prohibitively expensive. In this work, we argue that the core challenge is not reformulation generation itself, but the adaptive selection of reformulations and their retrieved documents under a strict inference budget.

**21. A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions**

- DOI：`10.1145/3703155`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（引用了种子）

The emergence of large language models (LLMs) has marked a significant breakthrough in natural language processing (NLP), fueling a paradigm shift in information acquisition. Nevertheless, LLMs are prone to hallucination, generating plausible yet nonfactual content. This phenomenon raises significant concerns over the reliability of LLMs in real-world information retrieval (IR) systems and has attracted intensive research to detect and mitigate such hallucinations. Given the open-ended general-purpose attributes inherent to LLMs, LLM hallucinations present distinct challenges that diverge from prior task-specific models. This divergence highlights the urgency for a nuanced understanding and comprehensive overview of recent advances in LLM hallucinations. In this survey, we begin with an innovative taxonomy of hallucination in the era of LLM and then delve into the factors contributing to hallucinations. Subsequently, we present a thorough overview of hallucination detection methods and benchmarks. Our discussion then transfers to representative methodologies for mitigating LLM hallucinations. Additionally, we delve into the current limitations faced by retrieval-augmented LLMs in combating hallucinations, offering insights for developing more robust IR systems. Finally, we highlight the promising research directions on LLM hallucinations, including hallucination in large vision-language models and understanding of knowledge boundaries in LLM hallucinations.

**22. Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents**

- DOI：`10.18653/v1/2023.emnlp-main.923`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（引用了种子）

Large Language Models (LLMs) have demonstrated remarkable zero-shot generalization across various language-related tasks, including search engines.However, existing work utilizes the generative ability of LLMs for Information Retrieval (IR) rather than direct passage ranking.The discrepancy between the pretraining objectives of LLMs and the ranking objective poses another challenge.In this paper, we first investigate generative LLMs such as ChatGPT and GPT-4 for relevance ranking in IR.Surprisingly, our experiments reveal that properly instructed LLMs can deliver competitive, even superior results to state-of-the-art supervised methods on popular IR benchmarks.Furthermore, to address concerns about data contamination of LLMs, we collect a new test set called NovelEval, based on the latest knowledge and aiming to verify the model's ability to rank unknown knowledge.Finally, to improve efficiency in real-world applications, we delve into the potential for distilling the ranking capabilities of ChatGPT into small specialized models using a permutation distillation scheme.Our evaluation results turn out that a distilled 440M model outperforms a 3B supervised model on the BEIR benchmark.The code to reproduce our results is available at www.github.com/sunnweiwei/RankGPT.

**23. Hallucination Mitigation for Retrieval-Augmented Large Language Models: A Review**

- DOI：`10.3390/math13050856`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（引用了种子）

Retrieval-augmented generation (RAG) leverages the strengths of information retrieval and generative models to enhance the handling of real-time and domain-specific knowledge. Despite its advantages, limitations within RAG components may cause hallucinations, or more precisely termed confabulations in generated outputs, driving extensive research to address these limitations and mitigate hallucinations. This review focuses on hallucination in retrieval-augmented large language models (LLMs). We first examine the causes of hallucinations from different sub-tasks in the retrieval and generation phases. Then, we provide a comprehensive overview of corresponding hallucination mitigation techniques, offering a targeted and complete framework for addressing hallucinations in retrieval-augmented LLMs. We also investigate methods to reduce the impact of hallucination through detection and correction. Finally, we discuss promising future research directions for mitigating hallucinations in retrieval-augmented LLMs.

**24. Retrieval-Augmented Generation for AI-Generated Content: A Survey**

- DOI：`10.1007/s41019-025-00335-5`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（引用了种子）

Advancements in model algorithms, the growth of foundational models, and access to high-quality datasets have propelled the evolution of Artificial Intelligence Generated Content (AIGC). Despite its notable successes, AIGC still faces hurdles such as updating knowledge, handling long-tail data, mitigating data leakage, and managing high training and inference costs. Retrieval-augmented generation (RAG) has recently emerged as a paradigm to address such challenges. In particular, RAG introduces the information retrieval process, which enhances the generation process by retrieving relevant objects from available data stores, leading to higher accuracy and better robustness. In this paper, we comprehensively review existing efforts that integrate RAG techniques into AIGC scenarios. We first classify RAG foundations according to how the retriever augments the generator, distilling the fundamental abstractions of the augmentation methodologies for various retrievers and generators. This unified perspective encompasses all RAG scenarios, illuminating advancements and pivotal technologies that help with potential future progress. We also summarize additional enhancement methods for RAG, facilitating effective engineering and implementation of RAG systems. Then from another view, we survey practical applications of RAG across different modalities and tasks, offering valuable references for researchers and practitioners. Furthermore, we introduce the benchmarks for RAG, discuss the limitations of current RAG systems, and suggest potential directions for future research.

**25. Generate rather than Retrieve: Large Language Models are Strong Context Generators**

- DOI：`10.48550/arxiv.2209.10063`
- 关联种子：`doi:10.18653/v1/2023.emnlp-main.585`（被种子引用）

Knowledge-intensive tasks, such as open-domain question answering (QA), require access to a large amount of world or domain knowledge. A common approach for knowledge-intensive tasks is to employ a retrieve-then-read pipeline that first retrieves a handful of relevant contextual documents from an external corpus such as Wikipedia and then predicts an answer conditioned on the retrieved documents. In this paper, we present a novel perspective for solving knowledge-intensive tasks by replacing document retrievers with large language model generators. We call our method generate-then-read (GenRead), which first prompts a large language model to generate contextutal documents based on a given question, and then reads the generated documents to produce the final answer. Furthermore, we propose a novel clustering-based prompting method that selects distinct prompts, resulting in the generated documents that cover different perspectives, leading to better recall over acceptable answers. We conduct extensive experiments on three different knowledge-intensive tasks, including open-domain QA, fact checking, and dialogue system. Notably, GenRead achieves 71.6 and 54.4 exact match scores on TriviaQA and WebQ, significantly outperforming the state-of-the-art retrieve-then-read pipeline DPR-FiD by +4.0 and +3.9, without retrieving any documents from any external knowledge source. Lastly, we demonstrate the model performance can be further improved by combining retrieval and generation. Our code and generated documents can be found at https://github.com/wyu97/GenRead.


## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | Codex（AI 审计，非独立人工复核） |
| 日期 | 2026-09-24 |
| 采纳的候选编号 | 2, 4, 5, 6, 10 |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |
| 审计方法 | 模型初审 + Codex 逐条复核 + 摘要逐字引文核验 + 标题去重 |
