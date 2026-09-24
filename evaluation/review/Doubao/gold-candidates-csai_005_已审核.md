# 金标候选：csai_005

**问题**：What evaluation benchmarks are used for multimodal retrieval?

　　→ 多模态检索使用哪些评估基准？

**子问题**：

1. Which datasets are used?
　　→ 使用了哪些数据集？

2. Which retrieval metrics are reported?
　　→ 报告了哪些检索指标？


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
| 1 | 2024 | Multimodal Knowledge Graph-Guided Cross-Modal Graph Network for Image- | 多模态知识图谱引导的跨模态图网络用于图文检索 | `10.1109/bigcomp60711.2024.00024` | 6 | 引用了种子 | 4 | 建议采纳(子问题1) | 采纳 | 1 | 摘要明确说明在 MS-COCO 和 Flickr30K 基准数据集上实验，可作为多模态检索评估所用数据集的证据，但未具体报告检索指标。 |
| 2 | 2024 | Knowledge Graph Enhanced Multimodal Transformer for Image-Text Retriev | 知识图谱增强的多模态Transformer用于图文检索 | `10.1109/icde60146.2024.00013` | 13 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | | 主题相邻：论文虽涉及图像-文本检索评估，但仅笼统提及使用两个常用数据集和匹配指标，未给出具体数据集名称或检索指标，无法作为任一子问题的证据。 |
| 3 | 2025 | Bridging Modalities: Improving Universal Multimodal Retrieval by Multi | 桥接模态：利用多模态大语言模型改进通用多模态检索 | `10.1109/cvpr52734.2025.00866` | 13 | 引用了种子 | 3 | 建议采纳(子问题1) | 采纳 | 1 | 该论文构建了面向通用多模态检索的 UMR Benchmark（UMRB），可作为评估基准/数据集使用的证据，但摘要未提及具体检索指标。 |
| 4 | 2025 | Docopilot: Improving Multimodal Models for Document-Level Understandin | Docopilot：提升多模态模型的文档级理解能力 | `10.1109/cvpr52734.2025.00381` | 11 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | | 主题相邻：该文聚焦文档级多模态理解数据集（Doc-750K）与模型，仅提及RAG的局限，未使用或报告任何多模态检索基准数据集或检索评价指标。 |
| 5 | 2025 | Tevatron 2.0: Unified Document Retrieval Toolkit across Scale, Languag | Tevatron 2.0：跨规模、跨语言、跨模态的统一文档检索工具包 | `10.1145/3726302.3730135` | 5 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | | 主题相邻：该摘要描述了一个支持评估的多模态检索工具包，但未指明任何具体数据集或检索指标。 |
| 6 | 2025 | Beyond Semantic Matching: Structure-Aware Fusion for Multi-Modal Retri | 超越语义匹配：面向结构丰富核工业规程多模态检索的结构感知融合 | `10.1109/imcec66174.2025.11331939` | 0 | 引用了种子 | 3 | 建议采纳(子问题1) | 采纳 | 1 | 该论文构建并使用了面向核工业程序的多模态图像-文本数据集（13,000条）进行检索评估，因此可作为数据集证据，但未报告检索指标（如Recall、mAP、nDCG），只报告生成内容的正确性、完整性和合规性。 |
| 7 | 2026 | Gaze-based Personal Memory: Leveraging Eye Tracking to Improve Relevan | 基于注视的个人记忆：利用眼动追踪提高文本检索系统的相关性 ETRA013 | `10.1145/3806027` | 0 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | | 主题相邻：论文研究基于眼动信号提升文本检索，而非多模态检索评测基准，尽管使用了g-Rel-READER数据集并报告MAP。 |
| 8 | 2023 | Building Multimodal Knowledge Bases With Multimodal Computational Sequ | 使用多模态计算序列和生成对抗网络构建多模态知识库 | `10.1109/tmm.2023.3291503` | 22 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | | 该论文讨论构建多模态知识库与多模态特征表示方法，虽涉及多模态数据但与多模态检索评测基准无关，未提及检索数据集或检索指标，属于主题相邻。 |
| 9 | 2024 | Self-Supervised Multi-Modal Knowledge Graph Contrastive Hashing for Cr | 面向跨模态搜索的自监督多模态知识图谱对比哈希 | `10.1609/aaai.v38i12.29280` | 22 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | | 主题相邻：摘要仅泛泛提及跨模态基准数据集，未列出具体数据集名称或检索指标。 |
| 10 | 2024 | Semantic deep learning and adaptive clustering for handling multimodal | 用于处理多模态多媒体信息检索的语义深度学习和自适应聚类 | `10.1007/s11042-024-19312-7` | 13 | 引用了种子 | 2 | 无法判断 | 不采纳 | | 源站未提供摘要，需另行获取 |
| 11 | 2025 | Dynamic Visual Semantic Sub-Embeddings and Fast Re-Ranking for Image-T | 面向图像-文本检索的动态视觉语义子嵌入与快速重排序 | `10.1109/tmm.2025.3535373` | 12 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 1 | 摘要明确列出了用于图像-文本检索评测的三个基准数据集（MSCOCO、Flickr30K、CUB Captions），可作为子问题1（使用哪些数据集）的证据，但未提及任何具体检索指标（如Recall@K、mAP），故不支撑子问题2。 |
| 12 | 2025 | M3DocVQA: Multi-Modal Multi-Page Multi-Document Understanding | M3DocVQA：多模态多页面多文档理解 | `10.1109/iccvw69036.2025.00649` | 10 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 1 | 该文提出了用于多模态文档理解/检索评估的新基准数据集 M3DocVQA（并用到 MMLongBench-Doc、MP-DocVQA），可作为「使用哪些数据集」的证据，但摘要未提及任何检索指标（如 Recall@k、nDCG），故不支持子问题2。 |
| 13 | 2023 | Knowledge-integrated Multi-modal Movie Turning Point Identification | 知识融合的多模态电影转折点识别 | `10.1145/3638557` | 9 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | | 主题相邻：该文研究多模态电影转折点识别/场景角色识别，未涉及多模态检索任务，也未报告任何检索数据集或检索指标。 |
| 14 | 2023 | Multiple Pseudo-Siamese Network with Supervised Contrast Learning for  | 面向医学多模态检索的监督对比学习多重伪孪生网络 | `10.1145/3637441` | 8 | 引用了种子 | 2 | 建议采纳(两个子问题) | 采纳 | 1,2 | 摘要明确指出使用四个基准数据集（ADNI1、ADNI2、ADNI3、OASIS3）并报告mAP指标，直接回答了所用数据集与检索度量两个子问题。 |
| 15 | 2025 | SGG-MVAR: Cross-Modal Retrieval With Scene Graph Generation and Multiv | SGG-MVAR：结合场景图生成与多视图属性关系引导的跨模态检索 | `10.1109/tcss.2024.3524297` | 6 | 引用了种子 | 2 | 建议采纳(两个子问题) | 采纳 | 1,2 | 摘要明确提到使用RichDataset以及Flickr30k和MS-COCO等数据集，并报告了跨模态检索的recall指标，因此可同时回答数据集和检索指标两个子问题。 |
| 16 | 2025 | Multimodal multimedia information retrieval through the integration of | 集成模糊聚类、基于OWA的融合与孪生神经网络的多模态多媒体信息检索 | `10.1016/j.fss.2025.109419` | 6 | 引用了种子 | 2 | 无法判断 | 不采纳 | | 源站未提供摘要，需另行获取 |
| 17 | 2025 | Construction of a multimodal knowledge graph for LNG carrier port stat | 基于改进视觉提示微调的LNG运输船港口国监督检查多模态知识图谱构建 | `10.1016/j.oceaneng.2025.121963` | 4 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | | 该文聚焦LNG运输船港口国监督检验的多模态知识图谱构建（图像分类与实体识别），未涉及任何多模态检索基准数据集或检索指标，属于主题相邻。 |
| 18 | 2025 | VisualRAG: Knowledge-Guided Retrieval Augmentation for Image-Text Matc | VisualRAG：面向图像-文本匹配的知识引导检索增强 | `10.1109/tcsvt.2025.3597097` | 3 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 1 | 摘要明确使用MSCOCO和Flickr30K数据集进行图像-文本检索实验，可作为数据集证据，但未报告具体检索指标（如Recall@K、mAP），故不支持指标子问题。 |
| 19 | 2025 | MuralAgent: Enhancing Ancient Mural Outpainting with RAG-Based Texts a | MuralAgent：利用基于RAG的文本与多模态集成增强古代壁画外绘 | `10.1145/3743679` | 3 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | | 主题相邻：论文涉及RAG与多模态，但未使用多模态检索评测基准或报告检索指标，不能回答数据集或检索指标子问题。 |
| 20 | 2025 | R 2 LLMs: Retrieval and Ranking with LLMs | R 2 LLMs：基于大语言模型的检索与排序 | `10.1145/3726302.3731689` | 3 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | | 这是一篇关于LLM检索器与排序器的教程综述，仅泛泛提及多模态应用，摘要中未列出任何具体数据集或检索评价指标，属于主题相邻而非直接证据。 |
| 21 | 2025 | CoFi-VisRAG: Coarse-to-Fine Visual Retrieval-Augmented Generation for  | CoFi-VisRAG：面向多模态文档的由粗到细视觉检索增强生成 | `10.1007/978-981-95-4088-4_5` | 0 | 引用了种子 | 2 | 无法判断 | 不采纳 | | 源站未提供摘要，需另行获取 |
| 22 | 2025 | Improving Multimodal Speech-To-Slide Alignment for Academic Lectures w | 利用视觉大语言模型改进学术讲座中的多模态语音-幻灯片对齐 | `10.1109/asru65441.2025.11434615` | 0 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | | 主题相邻：论文关注讲座语音与幻灯片对齐，虽使用MaViLS等数据集和F1指标，但并非针对多模态检索的评估基准或检索指标。 |
| 23 | 2026 | Multigranularity Information Fusion for Multimodal Retrieval in Prefab | 面向装配式建筑多模态检索的多粒度信息融合 | `10.1109/tii.2026.3692747` | 0 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 1 | 摘要提到构建PCKB并用于多模态检索实验，可作为所用数据集的证据；但未报告具体检索评价指标。 |
| 24 | 2026 | MURE: Hierarchical Multi-Resolution Encoding via Vision-Language Model | MURE：基于视觉语言模型的层次化多分辨率编码用于视觉文档检索 | `10.1145/3805622.3810864` | 0 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | | 主题相邻：讨论视觉文档检索基准，但未提及具体数据集名称或检索指标。 |
| 25 | 2026 | CMDR: Contextual Multimodal Document Retrieval | CMDR：上下文感知的多模态文档检索 | `10.1007/978-3-032-37035-8_5` | 0 | 引用了种子 | 2 | 无法判断 | 不采纳 | | 源站未提供摘要，需另行获取 |

## 摘要（判定用）

判据 3 要求确认摘要里存在可作为证据的完整句子，因此这里附上原文摘要。
机翻标题仅供快速定位，**判定必须依据英文原文**。

**1. Multimodal Knowledge Graph-Guided Cross-Modal Graph Network for Image-Text Retrieval**

- DOI：`10.1109/bigcomp60711.2024.00024`
- 关联种子：`doi:10.1145/3580501`（引用了种子）

Image-text retrieval is a fundamental cross-modal task, which dedicates to align the representation space between image modality and text modality. Existing cross-interactive image-text retrieval methods generate image and sentence em-beddings independently, introduce interaction-based networks for cross-modal reasoning, and then retrieve them using matching metrics. However, existing approaches do not consider fully utilizing semantic relationships among multimodal knowledge to enhance cross-modal fine-grained implicit semantic reasoning capabilities. In this paper, we propose Multimodal Knowledge Graph-guided Cross-modal Graph Network (MKCGN) that exploits multimodal knowledge graphs to explore cross-modal relationships and enhance global representations. In MKCGN, images generate semantic and spatial graphs, which are used to represent visual graphs, and sentences generate textual graphs based on word semantic relations. The visual and textual graphs are used to implement inter-modal reasoning respectively. Then we obtain interest embeddings of image regions and text words based on entity embed dings in Multimodal Knowledge Graph (MKG), which approximates and aligns the representation space of regions and words to a certain extent, thus obtaining effective inter-modal interactions and learning fine-grained cross-modal communication through graph node contrast loss for inter-modal semantic reasoning. Finally, we mine the implicit semantics and potential relationships of images and texts through the MKG as a means of enhancing the global representations and use cross-modal contrast loss to narrow the space of coarse-grained cross-modal representations. Experiments on the MS-COCO and Flickr30K benchmark datasets show that our proposed MKCGN outperforms state-of-the-art image-text retrieval methods.

**2. Knowledge Graph Enhanced Multimodal Transformer for Image-Text Retrieval**

- DOI：`10.1109/icde60146.2024.00013`
- 关联种子：`doi:10.1145/3580501`（引用了种子）

Image-text retrieval is a fundamental cross-modal task that aims to align the representation spaces between the image and text modalities. Existing cross-modal image-text retrieval methods independently generate embeddings for images and text, introduce interaction-based networks for cross-modal inference, and then achieve retrieval by using matching metrics. However, they overlook the semantic relationship between the coarse-grained and fine-grained representations within each modality, failing to capture the consistency of representations across different modalities, which affects the semantic learning of cross-modal representations, and makes it difficult to align modalities in semantic space. Consequently, these previous works inevitably suffer from low retrieval accuracy or high computational costs. In this paper, instead of directly fusing two cross-modal het-erogeneous spaces, we propose an multimodal knowledge enhanced multimodal transformer network framework to combine coarse-grained and fine-grained representation learning into a unified framework, capturing alignment information between targets, constructing a global semantic graph, and ultimately align multimodal representations in the semantic space. In our approach, images generate semantic and spatial graphs to represent visual information, while sentences generate text graphs based on semantic relationships between words, and they are used for intra-modal graph network inference. Subsequently, the generated global and local embeddings are fused into an enhanced multimodal transformer framework, effectively imple-menting cross-modal interaction processes by leveraging prior implicit semantic information from the multimodal knowledge graph. Furthermore, compared to simply matching words with image regions, our method proposes a bidirectional fine-grained matching method to filter the salient regions and words of images and texts, remove the interfering noise information, and realize bidirectional fine-grained pairing, which captures fine-grained bi-directional representational information, thus enable the model to generate more discriminative representations Finally, equipped with a coarse-to-fine inference method based on hybrid global and local cross-modal similarities, we demonstrate that the proposed method is able to significantly outperform existing state-of-the-art algorithms by evaluating our method using two widely-used datasets.

**3. Bridging Modalities: Improving Universal Multimodal Retrieval by Multimodal Large Language Models**

- DOI：`10.1109/cvpr52734.2025.00866`
- 关联种子：`doi:10.18653/v1/2024.emnlp-main.373`（引用了种子）

Universal Multimodal Retrieval (UMR) aims to enable search across various modalities using a unified model, where queries and candidates can consist of pure text, images, or a combination of both. Previous work has attempted to adopt multimodal large language models (MLLMs) to realize UMR using only text data. However, our preliminary experiments demonstrate that more diverse multimodal training data can further unlock the potential of MLLMs. Despite its effectiveness, the existing multimodal training data is highly imbalanced in terms of modality, which motivates us to develop a training data synthesis pipeline and construct a large-scale, high-quality fused-modal training dataset. Based on the synthetic training data, we develop the General Multimodal Embedder (GME), an MLLM-based dense retriever designed for UMR. Furthermore, we construct a comprehensive UMR Benchmark (UMRB) to evaluate the effectiveness of our approach. Experimental results show that our method achieves state-of-the-art performance among existing UMR methods. Last, we provide in-depth analyses of model scaling and training strategies, and perform ablation studies on both the model and synthetic data.

**4. Docopilot: Improving Multimodal Models for Document-Level Understanding**

- DOI：`10.1109/cvpr52734.2025.00381`
- 关联种子：`doi:10.18653/v1/2024.emnlp-main.373`（引用了种子）

Despite significant progress in multimodal large language models (MLLMs), their performance on complex, multi-page document comprehension remains inadequate, largely due to the lack of high-quality, document-level datasets. While current retrieval-augmented generation (RAG) methods offer partial solutions, they suffer from issues, such as fragmented retrieval contexts, multi-stage error accumulation, and extra time costs of retrieval. In this work, we present a high-quality document-level dataset, Doc-750K, designed to support in-depth understanding of multimodal documents. This dataset includes diverse document structures, extensive cross-page dependencies, and real question-answer pairs derived from the original documents. Building on the dataset, we develop a native multimodal model—Docopilot, which can accurately handle document-level dependencies without relying on RAG. Experiments demonstrate that Docopilot achieves superior coherence, accuracy, and efficiency in document understanding tasks and multi-turn interactions, setting a new baseline for document-level multimodal understanding. Data, code, and models are released at https://github.com/OpenGVLab/Docopilot.

**5. Tevatron 2.0: Unified Document Retrieval Toolkit across Scale, Language, and Modality**

- DOI：`10.1145/3726302.3730135`
- 关联种子：`doi:10.18653/v1/2024.emnlp-main.373`（引用了种子）

Recent advancements in large language models (LLMs) have driven interest in billion-scale retrieval models with strong generalization across retrieval tasks and languages. Additionally, progress in large vision-language models has created new opportunities for multimodal retrieval. In response, we have updated the Tevatron toolkit, introducing a unified pipeline that enables researchers to explore retriever models at different scales, across multiple languages, and with various modalities. This demo paper highlights the toolkit's key features, bridging academia and industry by supporting efficient training, inference, and evaluation of neural retrievers. We showcase a unified dense retriever achieving strong multilingual and multimodal effectiveness, and conduct a cross-modality zero-shot study to demonstrate its research potential. Alongside, we release OmniEmbed, to the best of our knowledge, the first embedding model that unifies text, image document, video, and audio retrieval, serving as a baseline for future research.

**6. Beyond Semantic Matching: Structure-Aware Fusion for Multi-Modal Retrieval in Structure-Rich Nuclear Industry Procedures**

- DOI：`10.1109/imcec66174.2025.11331939`
- 关联种子：`doi:10.18653/v1/2024.emnlp-main.373`（引用了种子）

Nuclear industry procedures, such as equipment maintenance and emergency response protocols, typically describe requirements and operational standards. These procedures are presented to users in document form and are characterized by complex chapter structures, flexible content organization, the presence of multimodal information (e.g., extensive image-text descriptions and numerous flowcharts), and a high density of specialized terminology. Traditional retrieval augmented generation (RAG) methods rely solely on semantic retrieval, often overlooking structural interference in documents that leads to inaccurate retrieval matching, such as cross-page separation of images and text, misalignment on the same page, confusion among multiple images, and irrelevant graphics or text. To address these limitations, this paper proposes Multi-modal Structure-aware Retrieval Augmented Generation method(MultiStruct-RAG), a retrieval-augmented generation architecture that incorporates two key technical features: multimodal semantics and structural awareness. This approach enhances the relevance of retrieved image-text associations by mitigating interference from positional relationships in nuclear power maintenance procedures. Furthermore, we built a text-image multimodal dataset for nuclear industry procedures and validated our method on this dataset. In this experiment, 13,000 nuclear industry procedures were used. Our proposed method is compared with existing text-based RAG and general multimodal RAG across three dimensions: the correctness, completeness, and compliance of the generated content. Experimental results demonstrate that, compared to traditional text-only RAG methods and conventional image-text hybrid RAG, our method achieves superior retrieval performance, providing results that contain richer image-related information and improved semantic accuracy. It better satisfies the nuclear industry's requirement for “high reliability and zero major errors” in question-answering applications.

**7. Gaze-based Personal Memory: Leveraging Eye Tracking to Improve Relevance in Text Retrieval Systems ETRA013**

- DOI：`10.1145/3806027`
- 关联种子：`doi:10.18653/v1/2024.emnlp-main.373`（引用了种子）

With the rapid growth of digital textual content, users face increasing challenges in rediscovering information which they have encountered in the past. Traditional search engines lack the ability to prioritize content truly viewed by users over merely visible content. We propose a method that captures both text passages and corresponding gaze data while reading, storing them in a searchable knowledge base. We then explore boosting strategies to improve text retrieval by prioritizing passages that users actually viewed, improving the personalization and relevance of search results. To this end, we repurposed the recent g-Rel-READER dataset to evaluate various gaze-based boosting techniques and address the research gap caused by the lack of combined text, gaze, and relevance data. The evaluation demonstrates the potential of gaze data to serve as a boosting criterion for search, with mean average precision (MAP) increased by over 33% over a purely text-based retrieval.

**8. Building Multimodal Knowledge Bases With Multimodal Computational Sequences and Generative Adversarial Networks**

- DOI：`10.1109/tmm.2023.3291503`
- 关联种子：`doi:10.1145/3580501`（引用了种子）

Conventional knowledge graphs (KGs) are composed solely of entities, attributes, and relationships, which poses challenges for enhancing multimodal knowledge representation and reasoning. To address the issue, this article proposes a multimodal deep learning-based approach to build a multimodal knowledge base (MMKB) for better multimodal feature (MMF) utilization. First, we construct a multimodal computation sequence (MCS) model for structured multimodal data storage. Then, we propose multimodal node, relationship, and dictionary models to enhance multimodal knowledge representation. Various feature extractors are used to extract MMFs from text, audio, image, and video data. Finally, we leverage generative adversarial networks (GANs) to facilitate MMF representation and update the MMKB dynamically. We examine the performance of the proposed method by using three multimodal datasets. BOW-, LBP-, Volume-, and VGGish-based feature extractors outperform the other methods by reducing at least 1.13%, 22.14%, 39.87, and 5.65% of the time cost, respectively. The average time costs of creating multimodal indexes improve by approximately 55.07% and 68.60% exact matching rates compared with the baseline method, respectively. The deep learning-based autoencoder method reduces the search time cost by 98.90% after using the trained model, outperforming the state-of-the-art methods. In terms of multimodal data representation, the GAN-CNN models achieve an average correct rate of 82.70%. Our open-source work highlights the importance of flexible MMF utilization in multimodal KGs, leading to more powerful and diverse applications that can leverage different types of data.

**9. Self-Supervised Multi-Modal Knowledge Graph Contrastive Hashing for Cross-Modal Search**

- DOI：`10.1609/aaai.v38i12.29280`
- 关联种子：`doi:10.1145/3580501`（引用了种子）

Deep cross-modal hashing technology provides an effective and efficient cross-modal unified representation learning solution for cross-modal search. However, the existing methods neglect the implicit fine-grained multimodal knowledge relations between these modalities such as when the image contains information that is not directly described in the text. To tackle this problem, we propose a novel self-supervised multi-grained multi-modal knowledge graph contrastive hashing method for cross-modal search (CMGCH). Firstly, in order to capture implicit fine-grained cross-modal semantic associations, a multi-modal knowledge graph is constructed, which represents the implicit multimodal knowledge relations between the image and text as inter-modal and intra-modal semantic associations. Secondly, a cross-modal graph contrastive attention network is proposed to reason on the multi-modal knowledge graph to sufficiently learn the implicit fine-grained inter-modal and intra-modal knowledge relations. Thirdly, a cross-modal multi-granularity contrastive embedding learning mechanism is proposed, which fuses the global coarse-grained and local fine-grained embeddings by multihead attention mechanism for inter-modal and intra-modal contrastive learning, so as to enhance the cross-modal unified representations with stronger discriminativeness and semantic consistency preserving power. With the joint training of intra-modal and inter-modal contrast, the invariant and modal-specific information of different modalities can be maintained in the final unified cross-modal unified hash space. Extensive experiments on several cross-modal benchmark datasets demonstrate that the proposed CMGCH outperforms the state-of the-art methods.

**10. Semantic deep learning and adaptive clustering for handling multimodal multimedia information retrieval**

- DOI：`10.1007/s11042-024-19312-7`
- 关联种子：`doi:10.1145/3580501`（引用了种子）

（源站未提供摘要——需另行获取，或直接放弃该候选）

**11. Dynamic Visual Semantic Sub-Embeddings and Fast Re-Ranking for Image-Text Retrieval**

- DOI：`10.1109/tmm.2025.3535373`
- 关联种子：`doi:10.1145/3580501`（引用了种子）

The core of image-text retrieval is to accurately measure the similarity between different modalities in a unified representation space. However, compared to textual descriptions of a certain perspective, the visual modality has more semantic variations. Therefore, images are usually associated with multiple textual captions in databases. Although popular symmetric embedding methods have explored numerous modal interaction approaches, they often learn toward outputting the average representation of multiple semantic variations within image embeddings. Consequently, information entropy in embeddings is increased, resulting in redundancy and decreased accuracy. In this work, we propose a Dynamic Visual Semantic Sub-Embeddings framework (DVSE) to reduce the information entropy. Specifically, we obtain a set of heterogeneous visual sub-embeddings through dynamic orthogonal constraint loss. To encourage the generated candidate image embeddings to capture various semantic variations, we construct a mixed distribution and employ a variance-aware weighting loss to assign different weights to the optimization process. In addition, we develop a Fast Re-ranking strategy (FR) to efficiently evaluate the retrieval results and enhance the performance. We compare the performance with existing set-based method using five image feature encoders and three text feature encoders on three benchmark datasets: MSCOCO, Flickr30K and CUB Captions. We also show the role of different components by ablation studies and perform a sensitivity analysis of the hyperparameters. The qualitative analysis of visualized bidirectional retrieval and attention maps further demonstrates the ability of our method to encode semantic variations.

**12. M3DocVQA: Multi-Modal Multi-Page Multi-Document Understanding**

- DOI：`10.1109/iccvw69036.2025.00649`
- 关联种子：`doi:10.18653/v1/2024.emnlp-main.373`（引用了种子）

Document Visual Question Answering (DocVQA) offers a promising approach to extracting insights from large document corpora. However, existing benchmarks focus on evaluating multi-modal understanding within a single document. This gap hinders the development of methods integrating scattered information across pages and documents. To address this, we introduce M3Doc VQA, the first benchmark designed for multi-modal, multi-page, and multi-document understanding. M3DocVQA comprises over 3,000 PDF documents with more than 40,000 pages, offering a challenging environment where evidence is distributed across diverse sources and modalities. Along-side the dataset, we introduce M3DocRAG, a baseline method based on multi-modal retrieval-augmented generation. M3DocRAG flexibly handles both single and multiple document settings while preserving critical visual information, establishing a useful starting point for future work in open-domain multi-modal document understanding. Our experiments across three benchmarks (M3DocVQA, MMLongBench-Doc, and MP-DocVQA) show that existing methods struggle with open-domain question answering over extensive, multi-modal documents. Although M3DocRAG has shown promising performance, there is large room for future improvement. We provide comprehensive ablation studies of different indexing, multi-modal language models, and multi-modal retrieval models, along with qualitative examples to guide future research.

**13. Knowledge-integrated Multi-modal Movie Turning Point Identification**

- DOI：`10.1145/3638557`
- 关联种子：`doi:10.1145/3580501`（引用了种子）

The rapid development of artificial intelligence provides rich technologies and tools for the automated understanding of literary works. As a comprehensive carrier of storylines, movies are natural multimodal data sources that provide sufficient data foundations, and how to fully leverage the benefits of data remains a sustainable research hotspot. In addition, the efficient representation of multi-source data also poses new challenges for information fusion technology. Therefore, we propose a knowledge-enhanced turning points identification (KTPi) method for multimodal scene recognition. First, the BiLSTM method is used to encode scene text and integrate contextual information into scene representations to complete text sequence modeling. Then, the graph structure is used to model all scenes, which strengthens long-range semantic dependencies between scenes and enhances scene representations using graph convolution network. After, the self-supervised method is used to obtain the optimal number of neighboring nodes in sparse graph. Next, actor and verb knowledge involved in the scene text are added to the multimodal data to enhance the diversity of scene feature expressions. Finally, the teacher-student network strategy is used to train the KTPi model. Experimental results show that KTPi outperforms baseline methods in scene role recognition tasks, and ablation experiments show that incorporating knowledge into multimodal model can improve its performance.

**14. Multiple Pseudo-Siamese Network with Supervised Contrast Learning for Medical Multi-modal Retrieval**

- DOI：`10.1145/3637441`
- 关联种子：`doi:10.1145/3580501`（引用了种子）

Medical multi-modal retrieval aims to provide doctors with similar medical images from different modalities, which can greatly promote the efficiency and accuracy of clinical diagnosis. However, most existing medical retrieval methods hardly support the retrieval of multi-modal medical images, i.e., the number of modalities is greater than 2, and just convert retrieval to classification or clustering. It futilely breaks the gap between the visual information and the semantic information in different medical image modalities. To solve the problem, a S upervised C ontrast L earning method based on a M ultiple P seudo- S iamese network (SCL-MPS) is proposed for multi-modal medical image retrieval. In order to make the samples with semantic similarity close neighbors on Riemann manifold, the multiple constraints based on semantic consistency and modal invariance are designed in different forward stages of SCL-MPS. We theoretically demonstrate the feasibility of the designed constraints. Finally, experiments on four benchmark datasets (ADNI1, ADNI2, ADNI3, and OASIS3) show that SCL-MPS achieves state-of-the-art performance compared to 15 retrieval methods. Especially, SCL-MPS achieves a 100% mAP score in medical cross-modal retrieval on ADNI1.

**15. SGG-MVAR: Cross-Modal Retrieval With Scene Graph Generation and Multiview Attribute Relationship Guidance**

- DOI：`10.1109/tcss.2024.3524297`
- 关联种子：`doi:10.1145/3580501`（引用了种子）

Cross-modal retrieval is crucial for achieving accurate and efficient information retrieval by establishing semantic correlations between heterogeneous images and text. However, traditional image-text training sets suffer from information asymmetry, which includes short lengths and limited sentence structures. This phenomenon often results in insufficient representations of essential visual information. We introduce RichDataset, which offers extensive semantic information. It includes diverse real-life image-text pairs and AI-generated content across domains such as news, entertainment, education, and posters. Compared with classic benchmarks such as Flickr30k and MS-COCO, RichDataset exhibits a novel and balanced distribution. Existing cross-modal retrieval models face challenges in extracting distinct features from the emerging data, leading to low retrieval accuracy. We propose SGG-MVAR, a comprehensive retrieval model guided by multiview scene information and semantic relationships. Leveraging a scene knowledge database, our model parses scene graphs and identifies differences in attributes and relationships. We conduct extensive experiments to evaluate our proposed dataset and model. All experimental results consistently demonstrate a significant improvement in recall for cross-modal retrieval.

**16. Multimodal multimedia information retrieval through the integration of fuzzy clustering, OWA-based fusion, and Siamese neural networks**

- DOI：`10.1016/j.fss.2025.109419`
- 关联种子：`doi:10.1145/3580501`（引用了种子）

（源站未提供摘要——需另行获取，或直接放弃该候选）

**17. Construction of a multimodal knowledge graph for LNG carrier port state control inspections based on improved visual prompt tuning**

- DOI：`10.1016/j.oceaneng.2025.121963`
- 关联种子：`doi:10.1145/3580501`（引用了种子）

Because of transitions in global energy, “intelligent” port state control (PSC) inspections for liquefied natural gas (LNG) carrier transportation safety are urgently needed. Traditional PSC inspections rely on practical experience, suffer from low efficiency and strong subjectivity, and struggle to handle multisource heterogeneous data. This study comprehensively applies data processing techniques of multiple modalities to construct a multimodal knowledge graph and is committed to improving the accuracy and efficiency of PSC inspections for LNG carriers. First, a multimodal database containing text, images, audio, and video is established. Data standardization and annotation are achieved through two-dimensional image classification and text preprocessing. To address equipment image recognition, an efficient visual prompt tuning (EVPT) model for channel attention is proposed, which integrates the channelwise convolutional attention module and visual prompt tuning (VPT). This model significantly improves equipment classification accuracy at low computational costs, achieving accuracies of 88.69 % and 85.47 % on the LNG-E and LNG-A image datasets, respectively. The RoBERTa-BiLSTM-CRF model is used for text entity recognition to extract key entities such as inspection points, with an F1 score of 87.53 %. Through manual cross-modal data alignment, multisource information is subsequently integrated to construct a multimodal knowledge graph containing 7401 valid triples. Case studies demonstrate that the graph helps inspectors locate defect evidence, understand operational specifications, and provide multidimensional knowledge support. This research innovates multimodal data fusion and knowledge management in the maritime field, promoting intelligent LNG carrier safety supervision.

**18. VisualRAG: Knowledge-Guided Retrieval Augmentation for Image-Text Matching**

- DOI：`10.1109/tcsvt.2025.3597097`
- 关联种子：`doi:10.1145/3580501`（引用了种子）

Image-text matching as a fundamental cross-modal understanding task presents unique challenges in weakly-aligned scenarios. Such data typically feature highly abstract textual captions with sparse entity references, creating a significant semantic gap with visual content. Current mainstream methods, primarily designed for strongly aligned data pairs, employ dynamic modeling or multi-dimensional similarity computation to achieve feature space mapping. However, they struggle with information asymmetry and modal heterogeneity in weakly aligned cases. To address this, we propose a Visual Perception Knowledge Enhancement (VPKE) framework. Unlike existing methods based on strong alignment assumptions, this framework mines latent image semantics through vision-language models and generates auxiliary captions, overcoming the information bottleneck of traditional text modalities. Its core innovation lies in an adaptive knowledge distillation mechanism that combines retrieval-augmented generation (RAG) with key entity extraction. This mechanism effectively filters noise when introducing external knowledge while optimizing cross-modal feature integration. The framework employs multi-level similarity evaluation to dynamically adjust fusion weights among original text, key entities, and auxiliary captions, enabling adaptive integration of diverse semantic features and significantly improving model flexibility. Additionally, multi-scale feature extraction further enhances cross-modal representation capabilities. Experimental results show that the proposed method performs excellently in image-text retrieval tasks on the MSCOCO and Flickr30K datasets, validating its effectiveness.

**19. MuralAgent: Enhancing Ancient Mural Outpainting with RAG-Based Texts and Multimodal Integration**

- DOI：`10.1145/3743679`
- 关联种子：`doi:10.1145/3580501`（引用了种子）

In the context of the digital age, utilizing cutting-edge technology for the digitization and creative expansion of ancient murals is crucial, aimed at preserving and passing on cultural heritage. Existing image outpainting techniques suffer from a lack of semantic guidance. This article introduces MuralAgent, a multimodal model based on Retrieval-Augmented Generation (RAG) technology. It precisely extracts key information from mural images and integrates it with a constructed ancient texts knowledge base to ensure the cultural and semantic consistency of the expanded images. Moreover, fine-tuning the Stable Diffusion model ensures the fidelity of the generated image styles. Specifically, this study involves constructing an ancient texts knowledge base for accurate matching, designing specific prompts for GPT-4V(ision) to extract key information, and innovatively expanding artworks through Stable Diffusion, providing a novel way for the public to reinterpret ancient murals.

**20. R 2 LLMs: Retrieval and Ranking with LLMs**

- DOI：`10.1145/3726302.3731689`
- 关联种子：`doi:10.18653/v1/2024.emnlp-main.373`（引用了种子）

Generative Large Language Models (LLMs) like GPT, Gemini, and Llama are transforming Information Retrieval, enabling new and more effective approaches to document retrieval and ranking. The switch from the previous generation pre-trained language models backbones (e.g., BERT, T5) to the new generative LLMs backbones has required the field to adapt training processes; it also has provided unprecedented capabilities and opportunities, stimulating research into zero-shot approaches, reasoning approaches, reinforcement learning based training, and multilingual and multimodal applications. This tutorial will provide a structured overview of LLM-based retrievers and rankers, covering fundamental architectures, training paradigms, real-world deployment considerations, and open challenges and research directions.

**21. CoFi-VisRAG: Coarse-to-Fine Visual Retrieval-Augmented Generation for Multimodal Documents**

- DOI：`10.1007/978-981-95-4088-4_5`
- 关联种子：`doi:10.18653/v1/2024.emnlp-main.373`（引用了种子）

（源站未提供摘要——需另行获取，或直接放弃该候选）

**22. Improving Multimodal Speech-To-Slide Alignment for Academic Lectures with Vision LLMs**

- DOI：`10.1109/asru65441.2025.11434615`
- 关联种子：`doi:10.18653/v1/2024.emnlp-main.373`（引用了种子）

We enhance the MaViLS multimodal algorithm to improve speech-to-slide alignment for lecture podcasts. Our approach integrates vision large language models for optical character recognition and automatic generation of lecture transcripts from slide content, coupled with a multilingual multimodal embedding model for text and image alignment. By combining slide-extracted text with automatically generated lecture transcripts and captioned slide images, we generate enhanced audio features that better capture speech-slide mapping. Our method improves the average F1 score for audio feature alignment on the English MaViLS dataset from 0.51 to 0.71 and on a newly created German podcast lectures dataset from 0.65 to 0.84.

**23. Multigranularity Information Fusion for Multimodal Retrieval in Prefabricated Construction**

- DOI：`10.1109/tii.2026.3692747`
- 关联种子：`doi:10.18653/v1/2024.emnlp-main.373`（引用了种子）

Prefabricated construction documents are characterized by domain-specific terminology, multilingual content, and rich multimodal elements including texts, tables, and images. General-purpose embedding models exhibit degraded performance in this vertical domain, and existing retrieval approaches often lack explicit cross-granularity alignment between page- and element-level objectives, failing to exploit their complementary strengths. To address these limitations in industrial informatics, this article proposes a multigranularity fusion (MGF) framework for representation learning. A multimodal and multilingual prefabricated construction knowledge base (PCKB) is first constructed from real-world prefabricated construction documents, featuring query-answer pairs explicitly linked to both page- and element-level sources. The MGF framework jointly optimizes three contrastive objectives: a page-level loss to preserve contextual coherence, an element-level loss to enhance fine-grained semantic fidelity, and an answer-guided auxiliary loss to align representations with downstream relevance. Through extensive experiments with multiple embedding models, consistent improvements in retrieval performance are observed after domain-specific training. Notably, the explicit fusion and alignment of page- and element-level objectives yield improvements, while the answer-guided loss enhances element-based retrieval and generally boosts overall performance. Finally, a retrieval module is implemented in a practical system that supports interactive switching between page- and element-level results for both PCKB and user-uploaded documents.

**24. MURE: Hierarchical Multi-Resolution Encoding via Vision-Language Models for Visual Document Retrieval**

- DOI：`10.1145/3805622.3810864`
- 关联种子：`doi:10.18653/v1/2024.emnlp-main.373`（引用了种子）

Visual Document Retrieval (VDR) requires representations that capture both fine-grained visual details and global document structure to ensure retrieval efficacy while maintaining computational efficiency. Existing VDR models struggle to balance effectiveness and efficiency when processing high-resolution documents: they often either lose fine-grained information or generate an excessive number of visual tokens, resulting in significant indexing overhead and high retrieval latency. In this work, we rethink the visual encoding mechanism and propose a new X-VisEmb paradigm that progresses from multi-resolution sampling and encoding, through cross-granularity feature fusion, to adaptive representation distillation. A preliminary study validates its feasibility and effectiveness in capturing complementary visual cues at varying scales. Building on the insights, we develop MURE , a novel framework that employs VLMs as a hierarchical multi-resolution encoder, integrates resolution-level Matryoshka representation learning (RMRL) for effective feature fusion, and applies a semantic-aware hierarchical clustering mechanism for visual token compression. Experiments on two widely used VDR benchmarks show that our MURE framework consistently beats strong baselines. Furthermore, it significantly outperforms ColPali with only 50% of its visual token budget.

**25. CMDR: Contextual Multimodal Document Retrieval**

- DOI：`10.1007/978-3-032-37035-8_5`
- 关联种子：`doi:10.18653/v1/2024.emnlp-main.373`（引用了种子）

（源站未提供摘要——需另行获取，或直接放弃该候选）


## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | |
| 日期 | 2026-09-24 |
| 采纳的候选编号 | 1, 3, 6, 11, 12, 14, 15, 18, 23 |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |
