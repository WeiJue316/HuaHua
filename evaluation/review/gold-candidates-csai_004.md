# 金标候选：csai_004

**问题**：How do vision-language models align image and text representations?

　　→ 视觉语言模型如何对齐图像表示与文本表示？

**子问题**：

1. Which alignment objectives are used?
　　→ 使用了哪些对齐目标？

2. How is alignment evaluated?
　　→ 对齐效果如何评估？


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
|---:|---:|---|---|---|---:|---|---:|---|---:|---|
| 1 | 2022 | Vision-Language Pre-Training with Triple Contrastive Learning | 基于三重对比学习的视觉-语言预训练 | `10.1109/cvpr52688.2022.01522` | 289 | 引用了种子 | 7 | 建议采纳(子问题1) | | | 该论文提出了跨模态对比、模态内对比以及局部-全局互信息最大化的对齐目标，直接回答了使用了哪些对齐目标，但未重点讨论对齐如何被评估。 |
| 2 | 2024 | Florence-2: Advancing a Unified Representation for a Variety of Vision | Florence-2：推进多种视觉任务的统一表示 | `10.1109/cvpr52733.2024.00461` | 262 | 引用了种子 | 6 | 建议不采纳 | | | 主题相邻：Florence-2是统一的视觉-语言基础模型，但摘要未涉及图像-文本表示对齐目标或对齐评估方法。 |
| 3 | 2024 | GLaMM: Pixel Grounding Large Multimodal Model | GLaMM：像素级定位的大型多模态模型 | `10.1109/cvpr52733.2024.01236` | 174 | 引用了种子 | 6 | 建议不采纳 | | | 主题相邻：论文关注视觉定位与分割生成，未涉及视觉-语言模型的对齐目标或对齐评估方法。 |
| 4 | 2023 | Open Vocabulary Semantic Segmentation with Patch Aligned Contrastive L | 基于块对齐对比学习的开放词汇语义分割 | `10.1109/cvpr52729.2023.01860` | 71 | 引用了种子 | 6 | 建议采纳(两个子问题) | | | 提出PACL修改CLIP对比损失以对齐图像patch token与文本CLS token，并通过零样本分割和分类基准评估对齐效果。 |
| 5 | 2023 | Video-LLaMA: An Instruction-tuned Audio-Visual Language Model for Vide | Video-LLaMA：用于视频理解的指令微调音视频语言模型 | `10.18653/v1/2023.emnlp-demo.49` | 555 | 引用了种子 | 5 | 建议采纳(子问题1) | | | 摘要明确提出通过大规模视频/图像-字幕对训练来对齐视觉编码器输出与LLM嵌入空间，这是图像-文本对齐目标的一个具体实例。 |
| 6 | 2024 | VadCLIP: Adapting Vision-Language Models for Weakly Supervised Video A | VadCLIP：面向弱监督视频异常检测的视觉-语言模型适配 | `10.1609/aaai.v38i6.28423` | 205 | 引用了种子 | 5 | 建议不采纳 | | | 主题相邻：该论文将CLIP的图像-文本对齐应用于视频异常检测，但未涉及对齐目标或评估对齐质量。 |
| 7 | 2023 | Deep Learning Approaches on Image Captioning: A Review | 图像描述中的深度学习方法：综述 | `10.1145/3617592` | 182 | 引用了种子 | 5 | 建议不采纳 | | | 该论文是图像描述综述，虽提及图像-文本模态间信息错位和描述评估指标，但并非聚焦于视觉-语言模型的图像-文本对齐目标或对齐评估方法，仅属主题相邻。 |
| 8 | 2024 | EarthGPT: A Universal Multimodal Large Language Model for Multisensor  | EarthGPT：面向遥感领域多传感器图像理解的通用多模态大语言模型 | `10.1109/tgrs.2024.3409624` | 173 | 引用了种子 | 5 | 建议不采纳 | | | 主题相邻：该文是遥感多模态大模型，虽涉及跨模态理解，但未讨论视觉-语言表征对齐目标或对齐评测方法。 |
| 9 | 2023 | Parameter-Efficient Transfer Learning for Remote Sensing Image–Text Re | 面向遥感图像-文本检索的参数高效迁移学习 | `10.1109/tgrs.2023.3308969` | 87 | 引用了种子 | 5 | 建议采纳(两个子问题) | | | 该论文提出混合多模态对比（HMMC）学习目标作为图像-文本对齐目标（子问题1），并在遥感图像-文本检索任务上通过检索性能基准评估对齐效果（子问题2）。 |
| 10 | 2024 | FuseCap: Leveraging Large Language Models for Enriched Fused Image Cap | FuseCap：利用大语言模型生成丰富的融合图像描述 | `10.1109/wacv57701.2024.00559` | 63 | 引用了种子 | 5 | 建议不采纳 | | | 主题相邻：论文聚焦于用LLM和视觉专家生成更丰富的图像描述数据来训练图像描述模型，并未讨论视觉语言模型中的图文对齐目标或对齐评估方法。 |
| 11 | 2024 | Structure-CLIP: Towards Scene Graph Knowledge to Enhance Multi-Modal S | Structure-CLIP：面向场景图知识以增强多模态结构化表示 | `10.1609/aaai.v38i3.28017` | 39 | 引用了种子 | 5 | 建议采纳(两个子问题) | | | 该文提出以场景图知识引导语义负例构建和 Knowledge-Enhance Encoder 的对齐目标（对应子问题1），并在 VG-Attribution、VG-Relation、MSCOCO 等图文匹配任务上评估结构化对齐表示（对应子问题2）。 |
| 12 | 2023 | Sigmoid Loss for Language Image Pre-Training | 用于语言-图像预训练的Sigmoid损失 | `10.1109/iccv51070.2023.01100` | 941 | 引用了种子 | 4 | 建议采纳(两个子问题) | | | 摘要提出成对 sigmoid 损失作为图文对齐目标，并用 ImageNet zero-shot 准确率评估预训练模型，因此可为两个子问题提供证据。 |
| 13 | 2024 | Vision-Language Models for Vision Tasks: A Survey | 面向视觉任务的视觉-语言模型：综述 | `10.1109/tpami.2024.3369699` | 897 | 引用了种子 | 4 | 建议采纳(两个子问题) | | | 摘要明确涵盖VLM预训练目标（可对应对齐目标）以及评估数据集与基准测试（可对应对齐评估），因此可作为两个子问题的证据。 |
| 14 | 2023 | Large-scale Multi-modal Pre-trained Models: A Comprehensive Survey | 大规模多模态预训练模型：全面综述 | `10.1007/s11633-022-1410-8` | 222 | 引用了种子 | 4 | 建议采纳(两个子问题) | | | 该综述明确涵盖多模态预训练的目标（对齐目标）和用于验证模型的下游任务（对齐评估），因此可作为两个子问题的证据。 |
| 15 | 2024 | VILA: On Pre-training for Visual Language Models | VILA：论视觉语言模型的预训练 | `10.1109/cvpr52733.2024.02520` | 222 | 引用了种子 | 4 | 建议不采纳 | | | 主题相邻：该文研究 VLM 预训练设计（冻结 LLM、交错数据、指令微调混合），但未具体讨论图文表示对齐目标或对齐评估方法。 |
| 16 | 2024 | CogAgent: A Visual Language Model for GUI Agents | CogAgent：面向GUI代理的视觉语言模型 | `10.1109/cvpr52733.2024.01354` | 173 | 引用了种子 | 4 | 建议不采纳 | | | 主题相邻：该论文提出面向GUI的视觉语言模型并报告VQA/导航基准，但未涉及图文表示对齐目标或对齐评估方法。 |
| 17 | 2024 | Improved Baselines with Visual Instruction Tuning | 使用视觉指令微调的改进基线 | `10.1109/cvpr52733.2024.02484` | 1477 | 引用了种子 | 3 | 建议不采纳 | | | 该文聚焦LLaVA视觉指令微调的设计选择与多模态基准性能，未讨论图像-文本表示对齐目标或其评估方法，属于主题相邻。 |
| 18 | 2023 | Tune-A-Video: One-Shot Tuning of Image Diffusion Models for Text-to-Vi | Tune-A-Video：面向文本到视频生成的图像扩散模型一次性调优 | `10.1109/iccv51070.2023.00701` | 545 | 引用了种子 | 3 | 建议不采纳 | | | 主题相邻：该文研究基于图像扩散模型的文本到视频生成与一次性微调，未涉及视觉-语言模型的图文表征对齐目标或对齐评估。 |
| 19 | 2023 | Evaluating Object Hallucination in Large Vision-Language Models | 评估大型视觉语言模型中的对象幻觉 | `10.18653/v1/2023.emnlp-main.20` | 498 | 引用了种子 | 3 | 建议不采纳 | | | 该论文研究LVLM的对象幻觉评估，未涉及图文表示对齐目标或对齐评价方法，仅与视觉语言模型评估主题相邻。 |
| 20 | 2024 | LISA: Reasoning Segmentation via Large Language Model | LISA：基于大语言模型的推理分割 | `10.1109/cvpr52733.2024.00915` | 375 | 引用了种子 | 3 | 建议不采纳 | | | 该论文聚焦于基于多模态LLM的推理分割任务（embedding-as-mask范式），虽属视觉-语言模型相邻主题，但未涉及图像-文本表示的对齐目标或对齐评估方法。 |
| 21 | 2024 | AnomalyGPT: Detecting Industrial Anomalies Using Large Vision-Language | AnomalyGPT：利用大型视觉-语言模型检测工业异常 | `10.1609/aaai.v38i3.27963` | 274 | 引用了种子 | 3 | 建议不采纳 | | | 主题相邻：该论文将大型视觉语言模型用于工业异常检测，未研究图像-文本表征对齐目标或对齐评估方法。 |
| 22 | 2023 | Make-It-3D: High-Fidelity 3D Creation from A Single Image with Diffusi | Make-It-3D：利用扩散先验从单张图像进行高保真3D创建 | `10.1109/iccv51070.2023.02086` | 190 | 引用了种子 | 3 | 建议不采纳 | | | 主题相邻：该文利用2D扩散先验进行单图3D生成，未涉及视觉-语言模型图文表示的对齐目标或对齐评估。 |
| 23 | 2024 | NavGPT: Explicit Reasoning in Vision-and-Language Navigation with Larg | NavGPT：利用大语言模型在视觉-语言导航中实现显式推理 | `10.1609/aaai.v38i7.28597` | 182 | 引用了种子 | 3 | 建议不采纳 | | | 该论文将视觉观测转为文本描述供LLM进行导航推理，未涉及图文表征对齐目标或对齐效果评估，属于主题相邻（视觉-语言导航/多模态LLM）而非本子问题证据。 |
| 24 | 2024 | mPLUG-OwI2: Revolutionizing Multi-modal Large Language Model with Moda | mPLUG-OwI2：通过模态协作革新多模态大语言模型 | `10.1109/cvpr52733.2024.01239` | 176 | 引用了种子 | 3 | 建议不采纳 | | | 该文聚焦于多模态大模型的模块化架构与模态协作，未涉及图文对齐目标（如对比学习、ITC/ITM损失）或对齐评测方法，属于主题相邻而非直接证据。 |
| 25 | 2024 | Driving with LLMs: Fusing Object-Level Vector Modality for Explainable | Driving with LLMs：融合对象级矢量模态以实现可解释自动驾驶 | `10.1109/icra57147.2024.10611018` | 175 | 引用了种子 | 3 | 建议不采纳 | | | 主题相邻：该文虽涉及多模态LLM对齐与评估，但对齐的是数值向量模态与LLM文本表示，并非视觉-语言模型中的图像-文本对齐。 |

## 摘要（判定用）

判据 3 要求确认摘要里存在可作为证据的完整句子，因此这里附上原文摘要。
机翻标题仅供快速定位，**判定必须依据英文原文**。

**1. Vision-Language Pre-Training with Triple Contrastive Learning**

- DOI：`10.1109/cvpr52688.2022.01522`
- 关联种子：`doi:10.1007/s11633-022-1369-5`（引用了种子）

Vision-language representation learning largely benefits from image-text alignment through contrastive losses (e.g., InfoNCE loss). The success of this alignment strategy is attributed to its capability in maximizing the mutual information (MI) between an image and its matched text. However, simply performing cross-modal alignment (CMA) ignores data potential within each modality, which may result in degraded representations. For instance, although CMA-based models are able to map image-text pairs close together in the embedding space, they fail to ensure that similar inputs from the same modality stay close by. This problem can get even worse when the pre-training data is noisy. In this paper, we propose triple contrastive learning (TCL) for vision-language pre-training by leveraging both cross-modal and intra-modal self-supervision. Besides CMA, TCL introduces an intra-modal contrastive objective to provide complementary benefits in representation learning. To take advantage of localized and structural information from image and text input, TCL further maximizes the average MI between local regions of image/text and their global summary. To the best of our knowledge, ours is the first work that takes into account local structure information for multi-modality representation learning. Experimental evaluations show that our approach is competitive and achieves the new state of the art on various common downstream vision-language tasks such as image-text retrieval and visual question answering.

**2. Florence-2: Advancing a Unified Representation for a Variety of Vision Tasks**

- DOI：`10.1109/cvpr52733.2024.00461`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

We introduce Florence-2, a novel vision foundation model with a unified, prompt-based representation for various computer vision and vision-language tasks. While existing large vision models excel in transfer learning, they struggle to perform diverse tasks with simple instructions, a capability that implies handling the complexity of various spatial hierarchy and semantic granularity. Florence-2 was designed to take text-prompt as task instructions and generate desirable results in text forms, whether it be captioning, object detection, grounding or segmentation. This multi-task learning setup demands large-scale, high-quality annotated data. To this end, we co-developed FLD-5B that consists of 5.4 billion comprehensive visual annotations on 126 million images, using an iterative strategy of automated image annotation and model refinement. We adopted a sequence-to-sequence structure to train Florence-2 to perform versatile and comprehensive vision tasks. Extensive evaluations on numerous tasks demonstrated Florence-2 to be a strong vision foundation model contender with un-precedented zero-shot and fine-tuning capabilities.

**3. GLaMM: Pixel Grounding Large Multimodal Model**

- DOI：`10.1109/cvpr52733.2024.01236`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

Large Multimodal Models (LMMs) extend Large Lan-guage Models to the vision domain. Initial LMMs used holistic images and text prompts to generate ungrounded textual responses. Recently, region-level LMMs have been used to generate visually grounded responses. However, they are limited to only referring to a single object category at a time, require users to specify the regions, or can-not offer dense pixel-wise object grounding. In this work, we present Grounding LMM (GLaMM), the first model that can generate natural language responses seamlessly in-tertwined with corresponding object segmentation masks. GLaMM not only grounds objects appearing in the con-versations but is flexible enough to accept both textual and optional visual prompts (region of interest) as input. This empowers users to interact with the model at various levels of granularity, both in textual and visual domains. Due to the lack of standard benchmarks for the novel setting of visually Grounded Conversation Generation (GCG), we in-troduce a comprehensive evaluation protocol with our curated grounded conversations. Our proposed GCG task requires densely grounded concepts in natural scenes at a large-scale. To this end, we propose a densely annotated Grounding-anything Dataset (GranD) using our proposed automated annotation pipeline that encompasses 7.5M unique concepts grounded in a total of 810M regions available with segmentation masks. Besides GCG, GLaMM also performs effectively on several downstream tasks, e.g., referring expression segmentation, image and region-level captioning and vision-language conversations.

**4. Open Vocabulary Semantic Segmentation with Patch Aligned Contrastive Learning**

- DOI：`10.1109/cvpr52729.2023.01860`
- 关联种子：`doi:10.1007/s11633-022-1369-5`（引用了种子）

We introduce Patch Aligned Contrastive Learning (PACL), a modified compatibility function for CLIP's contrastive loss, intending to train an alignment between the patch tokens of the vision encoder and the CLS token of the text encoder. With such an alignment, a model can identify regions of an image corresponding to a given text input, and therefore transfer seamlessly to the task of open vocabulary semantic segmentation without requiring any segmentation annotations during training. Using pre-trained CLIP encoders with PACL, we are able to set the state-of-the-art on the task of open vocabulary zero-shot segmentation on 4 different segmentation benchmarks: Pascal VOC, Pascal Context, COCO Stuff and ADE20K. Furthermore, we show that PACL is also applicable to image-level predictions and when used with a CLIP backbone, provides a general improvement in zero-shot classification accuracy compared to CLIP, across a suite of 12 image classification datasets.

**5. Video-LLaMA: An Instruction-tuned Audio-Visual Language Model for Video Understanding**

- DOI：`10.18653/v1/2023.emnlp-demo.49`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

We present Video-LLaMA 1 a multi-modal framework that empowers Large Language Models (LLMs) with the capability of understanding both visual and auditory content in the video.Video-LLaMA bootstraps cross-modal training from the frozen pre-trained visual & audio encoders and the frozen LLMs.Unlike previous works that complement LLMs to process the visual or audio signals only (Zhu et al., 2023;Liu et al., 2023; Huang et al., 2023a), Video-LLaMA enables video comprehension by tackling two challenges: (1) capturing the temporal changes in visual scenes, (2) integrating audio-visual signals.To counter the first challenge, we propose a Video Q-former to assemble a pre-trained image encoder into our video encoder and introduce a video-to-text generation task to learn video-language correspondence.For the second challenge, we leverage ImageBind (Girdhar et al., 2023), a universal embedding model aligning multiple modalities, as the pre-trained audio encoder and introduce an Audio Q-former on top of ImageBind to learn reasonable auditory query embeddings for the LLM module.To align the output of both visual & audio encoders with LLM's embedding space, we first train Video-LLaMA on massive video/image-caption pairs and then tune our model with visual-instruction datasets of moderate amount but higher quality.We found Video-LLaMA shows the ability to perceive and comprehend video content and generate meaningful responses grounded in the visual and auditory information presented in the videos.

**6. VadCLIP: Adapting Vision-Language Models for Weakly Supervised Video Anomaly Detection**

- DOI：`10.1609/aaai.v38i6.28423`
- 关联种子：`doi:10.1007/s11633-022-1369-5`（引用了种子）

The recent contrastive language-image pre-training (CLIP) model has shown great success in a wide range of image-level tasks, revealing remarkable ability for learning powerful visual representations with rich semantics. An open and worthwhile problem is efficiently adapting such a strong model to the video domain and designing a robust video anomaly detector. In this work, we propose VadCLIP, a new paradigm for weakly supervised video anomaly detection (WSVAD) by leveraging the frozen CLIP model directly without any pre-training and fine-tuning process. Unlike current works that directly feed extracted features into the weakly supervised classifier for frame-level binary classification, VadCLIP makes full use of fine-grained associations between vision and language on the strength of CLIP and involves dual branch. One branch simply utilizes visual features for coarse-grained binary classification, while the other fully leverages the fine-grained language-image alignment. With the benefit of dual branch, VadCLIP achieves both coarse-grained and fine-grained video anomaly detection by transferring pre-trained knowledge from CLIP to WSVAD task. We conduct extensive experiments on two commonly-used benchmarks, demonstrating that VadCLIP achieves the best performance on both coarse-grained and fine-grained WSVAD, surpassing the state-of-the-art methods by a large margin. Specifically, VadCLIP achieves 84.51% AP and 88.02% AUC on XD-Violence and UCF-Crime, respectively. Code and features are released at https://github.com/nwpu-zxr/VadCLIP.

**7. Deep Learning Approaches on Image Captioning: A Review**

- DOI：`10.1145/3617592`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

Image captioning is a research area of immense importance, aiming to generate natural language descriptions for visual content in the form of still images. The advent of deep learning and more recently vision-language pre-training techniques has revolutionized the field, leading to more sophisticated methods and improved performance. In this survey article, we provide a structured review of deep learning methods in image captioning by presenting a comprehensive taxonomy and discussing each method category in detail. Additionally, we examine the datasets commonly employed in image captioning research, as well as the evaluation metrics used to assess the performance of different captioning models. We address the challenges faced in this field by emphasizing issues such as object hallucination, missing context, illumination conditions, contextual understanding, and referring expressions. We rank different deep learning methods’ performance according to widely used evaluation metrics, giving insight into the current state-of-the-art. Furthermore, we identify several potential future directions for research in this area, which include tackling the information misalignment problem between image and text modalities, mitigating dataset bias, incorporating vision-language pre-training methods to enhance caption generation, and developing improved evaluation tools to accurately measure the quality of image captions.

**8. EarthGPT: A Universal Multimodal Large Language Model for Multisensor Image Comprehension in Remote Sensing Domain**

- DOI：`10.1109/tgrs.2024.3409624`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

Multi-modal large language models (MLLMs) have demonstrated remarkable success in vision and visual-language tasks within the natural image domain. Owing to the significant domain gap between natural and remote sensing (RS) images, the development of MLLMs in the RS domain is still in the infant stage. To fill the gap, a pioneer MLLM named EarthGPT integrating various multi-sensor RS interpretation tasks uniformly is proposed in this paper for universal RS image comprehension. Firstly, a visual-enhanced perception mechanism is constructed to refine and incorporate coarse-scale semantic perception information and fine-scale detailed perception information. Secondly, a cross-modal mutual comprehension approach is proposed, aiming at enhancing the interplay between visual perception and language comprehension and deepening the comprehension of both visual and language content. Finally, a unified instruction tuning method for multi-sensor multi-task in the RS domain is proposed to unify a wide range of tasks including scene classification, image captioning, region-level captioning, visual question answering (VQA), visual grounding, object detection, etc. More importantly, a dataset named MMRS-1M featuring large-scale multi-sensor multi-modal RS instruction-following is constructed, comprising over 1M image-text pairs based on 34 existing diverse RS datasets and including multi-sensor images such as optical, synthetic aperture radar (SAR), and infrared. The MMRS-1M dataset addresses the drawback of MLLMs on RS expert knowledge and stimulates the development of MLLMs in the RS domain. Extensive experiments are conducted, demonstrating the EarthGPT’s superior performance in various RS visual interpretation tasks compared with the other specialist models and MLLMs, proving the effectiveness of the proposed EarthGPT and offering a versatile paradigm for open-set reasoning tasks. Our code and dataset are available at https://github.com/wivizhang/EarthGPT.

**9. Parameter-Efficient Transfer Learning for Remote Sensing Image–Text Retrieval**

- DOI：`10.1109/tgrs.2023.3308969`
- 关联种子：`doi:10.1007/s11633-022-1369-5`（引用了种子）

Vision-and-language pre-training (VLP) models have experienced a surge in popularity recently. By fine-tuning them on specific datasets, significant performance improvements have been observed in various tasks. However, full fine-tuning of VLP models not only consumes a significant amount of computational resources but also has a significant environmental impact. Moreover, as remote sensing (RS) data is constantly being updated, full fine-tuning may not be practical for real-world applications. To address this issue, in this work, we investigate the parameter-efficient transfer learning (PETL) method to effectively and efficiently transfer visual-language knowledge from the natural domain to the RS domain on the image-text retrieval task. To this end, we make the following contributions. 1) We construct a novel and sophisticated PETL framework for the RS image-text retrieval (RSITR) task, which includes the pretrained CLIP model, a multimodal remote sensing adapter, and a hybrid multi-modal contrastive (HMMC) learning objective; 2) To deal with the problem of high intra-modal similarity in RS data, we design a simple yet effective HMMC loss; 3) We provide comprehensive empirical studies for PETL-based RS image-text retrieval. Our results demonstrate that the proposed method is promising and of great potential for practical applications. 4) We benchmark extensive state-of-the-art PETL methods on the RSITR task. Our proposed model only contains 0.16M training parameters, which can achieve a parameter reduction of 98.9% compared to full fine-tuning, resulting in substantial savings in training costs. Our retrieval performance exceeds traditional methods by 7-13% and achieves comparable or better performance than full fine-tuning. This work can provide new ideas and useful insights for RS vision-language tasks.

**10. FuseCap: Leveraging Large Language Models for Enriched Fused Image Captions**

- DOI：`10.1109/wacv57701.2024.00559`
- 关联种子：`doi:10.1007/s11633-022-1369-5`（引用了种子）

The advent of vision-language pre-training techniques enhanced substantial progress in the development of models for image captioning. However, these models frequently produce generic captions and may omit semantically important image details. This limitation can be traced back to the image-text datasets; while their captions typically offer a general description of image content, they frequently omit salient details. Considering the magnitude of these datasets, manual reannotation is impractical, emphasizing the need for an automated approach. To address this challenge, we leverage existing captions and explore augmenting them with visual details using "frozen" vision experts including an object detector, an attribute recognizer, and an Optical Character Recognizer (OCR). Our proposed method, FuseCap, fuses the outputs of such vision experts with the original captions using a large language model (LLM), yielding comprehensive image descriptions. We automatically curate a training set of 12M image-enriched caption pairs. These pairs undergo extensive evaluation through both quantitative and qualitative analyses. Subsequently, this data is utilized to train a captioning generation BLIP-based model. This model outperforms current state-of-the-art approaches, producing more precise and detailed descriptions, demonstrating the effectiveness of the proposed data-centric approach. We release this large-scale dataset of enriched image-caption pairs for the community.

**11. Structure-CLIP: Towards Scene Graph Knowledge to Enhance Multi-Modal Structured Representations**

- DOI：`10.1609/aaai.v38i3.28017`
- 关联种子：`doi:10.48550/arxiv.2204.03162`（引用了种子）

Large-scale vision-language pre-training has achieved significant performance in multi-modal understanding and generation tasks. However, existing methods often perform poorly on image-text matching tasks that require structured representations, i.e., representations of objects, attributes, and relations. The models cannot make a distinction between "An astronaut rides a horse" and "A horse rides an astronaut". This is because they fail to fully leverage structured knowledge when learning multi-modal representations. In this paper, we present an end-to-end framework Structure-CLIP, which integrates Scene Graph Knowledge (SGK) to enhance multi-modal structured representations. Firstly, we use scene graphs to guide the construction of semantic negative examples, which results in an increased emphasis on learning structured representations. Moreover, a Knowledge-Enhance Encoder (KEE) is proposed to leverage SGK as input to further enhance structured representations. To verify the effectiveness of the proposed framework, we pre-train our model with the aforementioned approaches and conduct experiments on downstream tasks. Experimental results demonstrate that Structure-CLIP achieves state-of-the-art (SOTA) performance on VG-Attribution and VG-Relation datasets, with 12.5% and 4.1% ahead of the multi-modal SOTA model respectively. Meanwhile, the results on MSCOCO indicate that Structure-CLIP significantly enhances the structured representations while maintaining the ability of general representations. Our code is available at https://github.com/zjukg/Structure-CLIP.

**12. Sigmoid Loss for Language Image Pre-Training**

- DOI：`10.1109/iccv51070.2023.01100`
- 关联种子：`doi:10.1007/s11633-022-1369-5`（引用了种子）

We propose a simple pairwise sigmoid loss for imagetext pre-training. Unlike standard contrastive learning with softmax normalization, the sigmoid loss operates solely on image-text pairs and does not require a global view of the pairwise similarities for normalization. The sigmoid loss simultaneously allows further scaling up the batch size, while also performing better at smaller batch sizes. With only four TPUv4 chips, we can train a Base CLIP model at 4k batch size and a Large LiT model at 20k batch size, the latter achieves 84.5% ImageNet zero-shot accuracy in two days. This disentanglement of the batch size from the loss further allows us to study the impact of examples vs pairs and negative to positive ratio. Finally, we push the batch size to the extreme, up to one million, and find that the benefits of growing batch size quickly diminish, with a more reasonable batch size of 32k being sufficient. We hope our research motivates further explorations in improving the quality and efficiency of language-image pre-training.

**13. Vision-Language Models for Vision Tasks: A Survey**

- DOI：`10.1109/tpami.2024.3369699`
- 关联种子：`doi:10.1007/s11633-022-1369-5`（引用了种子）

Most visual recognition studies rely heavily on crowd-labelled data in deep neural networks (DNNs) training, and they usually train a DNN for each single visual recognition task, leading to a laborious and time-consuming visual recognition paradigm. To address the two challenges, Vision-Language Models (VLMs) have been intensively investigated recently, which learns rich vision-language correlation from web-scale image-text pairs that are almost infinitely available on the Internet and enables zero-shot predictions on various visual recognition tasks with a single VLM. This paper provides a systematic review of visual language models for various visual recognition tasks, including: (1) the background that introduces the development of visual recognition paradigms; (2) the foundations of VLM that summarize the widely-adopted network architectures, pre-training objectives, and downstream tasks; (3) the widely-adopted datasets in VLM pre-training and evaluations; (4) the review and categorization of existing VLM pre-training methods, VLM transfer learning methods, and VLM knowledge distillation methods; (5) the benchmarking, analysis and discussion of the reviewed methods; (6) several research challenges and potential research directions that could be pursued in the future VLM studies for visual recognition.

**14. Large-scale Multi-modal Pre-trained Models: A Comprehensive Survey**

- DOI：`10.1007/s11633-022-1410-8`
- 关联种子：`doi:10.1007/s11633-022-1369-5`（引用了种子）

Abstract With the urgent demand for generalized deep models, many pre-trained big models are proposed, such as bidirectional encoder representations (BERT), vision transformer (ViT), generative pre-trained transformers (GPT), etc. Inspired by the success of these models in single domains (like computer vision and natural language processing), the multi-modal pre-trained big models have also drawn more and more attention in recent years. In this work, we give a comprehensive survey of these models and hope this paper could provide new insights and helps fresh researchers to track the most cutting-edge works. Specifically, we firstly introduce the background of multi-modal pre-training by reviewing the conventional deep learning, pre-training works in natural language process, computer vision, and speech. Then, we introduce the task definition, key challenges, and advantages of multi-modal pre-training models (MM-PTMs), and discuss the MM-PTMs with a focus on data, objectives, network architectures, and knowledge enhanced pre-training. After that, we introduce the downstream tasks used for the validation of large-scale MM-PTMs, including generative, classification, and regression tasks. We also give visualization and analysis of the model parameters and results on representative downstream tasks. Finally, we point out possible research directions for this topic that may benefit future works. In addition, we maintain a continuously updated paper list for large-scale pre-trained multi-modal big models: https://github.com/wangxiao5791509/MultiModal_BigModels_Survey .

**15. VILA: On Pre-training for Visual Language Models**

- DOI：`10.1109/cvpr52733.2024.02520`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

Visual language models (VLMs) rapidly progressed with the recent success of large language models. There have been growing efforts on visual instruction tuning to extend the LLM with visual inputs, but lacks an in-depth study of the visual language pre-training process, where the model learns to perform joint modeling on both modalities. In this work, we examine the design options for VLM pre-training by augmenting LLM towards VLM through step-by-step controllable comparisons. We introduce three main findings: (1) freezing LLMs during pre-training can achieve decent zero-shot performance, but lack in-context learning capability, which requires unfreezing the LLM; (2) interleaved pre-training data is beneficial whereas image-text pairs alone are not optimal; (3) re-blending text-only instruction data to image-text data during instruction fine-tuning not only remedies the degradation of text-only tasks, but also boosts VLM task accuracy. With an enhanced pre-training recipe we build VILA, a Visual Language model family that consistently outperforms the state-of-the-art models, e.g., LLaVA-1.5, across main benchmarks without bells and whistles. Multi-modal pre-training also helps unveil appealing properties of VILA, including multi-image reasoning, enhanced in-context learning, and better world knowledge. VILA is also deployable on Jetson Orin for on-device VLM.

**16. CogAgent: A Visual Language Model for GUI Agents**

- DOI：`10.1109/cvpr52733.2024.01354`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

People are spending an enormous amount of time on dig-ital devices through graphical user interfaces (GUIs), e.g., computer or smartphone screens. Large language models (LLMs) such as ChatGPT can assist people in tasks like writing emails, but struggle to understand and interact with GUIs, thus limiting their potential to increase automation levels. In this paper, we introduce CogAgent, an 18-billion-parameter visual language model (VLM) specializing in GUI understanding and navigation. By utilizing both low-resolution and high-resolution image encoders, CogA-gent supports input at a resolution of1120 × 1120, enabling it to recognize tiny page elements and text. As a general-ist visual language model, CogAgent achieves the state of the art on five text-rich and four general VQA benchmarks, including VQAv2, OK- VQA, Text- Vqa, St- Vqa, ChartQA, infoVQA, DocVQA, MM-Vet, and POPE. CogAgent, using only screenshots as input, outperforms LLM-based methods that consume extracted HTML text on both PC and Android GUI navigation tasks-Mind2Web and AITW, ad-vancing the state of the art. The model and codes are available at https://github.com/THUDM/CogVLM.

**17. Improved Baselines with Visual Instruction Tuning**

- DOI：`10.1109/cvpr52733.2024.02484`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

Large multimodal models (LMM) have recently shown encouraging progress with visual instruction tuning. In this paper, we present the first systematic study to investigate the design choices of LMMs in a controlled setting under the LLaVA framework. We show that the fully-connected vision-language connector in LLaVA is surprisingly power-ful and data-efficient. With simple modifications to LLa VA, namely, using CLIP- ViT-L-336px with an MLP projection and adding academic-task-oriented VQA data with response formatting prompts, we establish stronger baselines that achieve state-of-the-art across 11 benchmarks. Our final 13B checkpoint uses merely 1.2M publicly available data, and finishes full training in ~ 1 day on a single 8-AI00 node. Furthermore, we present some early exploration of open problems in LMMs, including scaling to higher resolution inputs, compositional capabilities, and model hallucination, etc. We hope this makes state-of-the-art LMM research more accessible. Code and model will be publicly available.

**18. Tune-A-Video: One-Shot Tuning of Image Diffusion Models for Text-to-Video Generation**

- DOI：`10.1109/iccv51070.2023.00701`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

To replicate the success of text-to-image (T2I) generation, recent works employ large-scale video datasets to train a text-to-video (T2V) generator. Despite their promising results, such paradigm is computationally expensive. In this work, we propose a new T2V generation setting—One-Shot Video Tuning, where only one text-video pair is presented. Our model is built on state-of-the-art T2I diffusion models pre-trained on massive image data. We make two key observations: 1) T2I models can generate still images that represent verb terms; 2) extending T2I models to generate multiple images concurrently exhibits surprisingly good content consistency. To further learn continuous motion, we introduce Tune-A-Video, which involves a tailored spatio-temporal attention mechanism and an efficient one-shot tuning strategy. At inference, we employ DDIM inversion to provide structure guidance for sampling. Extensive qualitative and numerical experiments demonstrate the remarkable ability of our method across various applications.

**19. Evaluating Object Hallucination in Large Vision-Language Models**

- DOI：`10.18653/v1/2023.emnlp-main.20`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

Inspired by the superior language abilities of large language models (LLM), large visionlanguage models (LVLM) have been recently proposed by integrating powerful LLMs for improving the performance on complex multimodal tasks.Despite the promising progress on LVLMs, we find that they suffer from object hallucinations, i.e., they tend to generate objects inconsistent with the target images in the descriptions.To investigate it, this work presents the first systematic study on object hallucination of LVLMs.We conduct the evaluation experiments on several representative LVLMs, and show that they mostly suffer from severe object hallucination issues.We further discuss that the visual instructions may influence the hallucination, and find that: objects that frequently appear in the visual instructions or co-occur with the image objects are obviously prone to be hallucinated by LVLMs.Besides, we further design a polling-based query method called POPE for better evaluation of object hallucination.Experiment results show that our POPE can evaluate object hallucination in a more stable and flexible way.

**20. LISA: Reasoning Segmentation via Large Language Model**

- DOI：`10.1109/cvpr52733.2024.00915`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

Although perception systems have made remarkable ad-vancements in recent years, they still rely on explicit human instruction or pre-defined categories to identify the target objects before executing visual recognition tasks. Such systems cannot actively reason and comprehend implicit user intention. In this work, we propose a new segmentation task - reasoning segmentation. The task is designed to output a segmentation mask given a complex and implicit query text. Furthermore, we establish a benchmark comprising over one thousand image-instruction-mask data samples, incorporating intricate reasoning and world knowledge for evaluation purposes. Finally, we present LISA: large Language Instructed Segmentation Assistant, which inherits the language generation capabilities of multimodal Large Language Models (LLMs) while also possessing the ability to produce segmentation masks. We expand the original vocabulary with atoken and propose the embedding-as-mask paradigm to unlock the segmentation capability. Remarkably, LISA can handle cases involving complex rea-soning and world knowledge. Also, it demonstrates robust zero-shot capability when trained exclusively on reasoning-free datasets. In addition, fine-tuning the model with merely 239 reasoning segmentation data samples results in further performance enhancement. Both quantitative and qualitative experiments show our method effectively unlocks new reasoning segmentation capabilities for multimodal LLMs. Code, models, and data are available at github.com/dvlab-research/LISA.

**21. AnomalyGPT: Detecting Industrial Anomalies Using Large Vision-Language Models**

- DOI：`10.1609/aaai.v38i3.27963`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

Large Vision-Language Models (LVLMs) such as MiniGPT-4 and LLaVA have demonstrated the capability of understanding images and achieved remarkable performance in various visual tasks. Despite their strong abilities in recognizing common objects due to extensive training datasets, they lack specific domain knowledge and have a weaker understanding of localized details within objects, which hinders their effectiveness in the Industrial Anomaly Detection (IAD) task. On the other hand, most existing IAD methods only provide anomaly scores and necessitate the manual setting of thresholds to distinguish between normal and abnormal samples, which restricts their practical implementation. In this paper, we explore the utilization of LVLM to address the IAD problem and propose AnomalyGPT, a novel IAD approach based on LVLM. We generate training data by simulating anomalous images and producing corresponding textual descriptions for each image. We also employ an image decoder to provide fine-grained semantic and design a prompt learner to fine-tune the LVLM using prompt embeddings. Our AnomalyGPT eliminates the need for manual threshold adjustments, thus directly assesses the presence and locations of anomalies. Additionally, AnomalyGPT supports multi-turn dialogues and exhibits impressive few-shot in-context learning capabilities. With only one normal shot, AnomalyGPT achieves the state-of-the-art performance with an accuracy of 86.1%, an image-level AUC of 94.1%, and a pixel-level AUC of 95.3% on the MVTec-AD dataset.

**22. Make-It-3D: High-Fidelity 3D Creation from A Single Image with Diffusion Prior**

- DOI：`10.1109/iccv51070.2023.02086`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

In this work, we investigate the problem of creating high-fidelity 3D content from only a single image. This is inherently challenging: it essentially involves estimating the underlying 3D geometry while simultaneously hallucinating unseen textures. To address this challenge, we leverage prior knowledge from a well-trained 2D diffusion model to act as 3D-aware supervision for 3D creation. Our approach, Make-It-3D, employs a two-stage optimization pipeline: the first stage optimizes a neural radiance field by incorporating constraints from the reference image at the frontal view and diffusion prior at novel views; the second stage transforms the coarse model into textured point clouds and further elevates the realism with diffusion prior while leveraging the high-quality textures from the reference image. Extensive experiments demonstrate that our method outperforms prior works by a large margin, resulting in faithful reconstructions and impressive visual quality. Our method presents the first attempt to achieve high-quality 3D creation from a single image for general objects and enables various applications such as text-to-3D creation and texture editing.

**23. NavGPT: Explicit Reasoning in Vision-and-Language Navigation with Large Language Models**

- DOI：`10.1609/aaai.v38i7.28597`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

Trained with an unprecedented scale of data, large language models (LLMs) like ChatGPT and GPT-4 exhibit the emergence of significant reasoning abilities from model scaling. Such a trend underscored the potential of training LLMs with unlimited language data, advancing the development of a universal embodied agent. In this work, we introduce the NavGPT, a purely LLM-based instruction-following navigation agent, to reveal the reasoning capability of GPT models in complex embodied scenes by performing zero-shot sequential action prediction for vision-and-language navigation (VLN). At each step, NavGPT takes the textual descriptions of visual observations, navigation history, and future explorable directions as inputs to reason the agent's current status, and makes the decision to approach the target. Through comprehensive experiments, we demonstrate NavGPT can explicitly perform high-level planning for navigation, including decomposing instruction into sub-goals, integrating commonsense knowledge relevant to navigation task resolution, identifying landmarks from observed scenes, tracking navigation progress, and adapting to exceptions with plan adjustment. Furthermore, we show that LLMs is capable of generating high-quality navigational instructions from observations and actions along a path, as well as drawing accurate top-down metric trajectory given the agent's navigation history. Despite the performance of using NavGPT to zero-shot R2R tasks still falling short of trained models, we suggest adapting multi-modality inputs for LLMs to use as visual navigation agents and applying the explicit reasoning of LLMs to benefit learning-based models. Code is available at: https://github.com/GengzeZhou/NavGPT.

**24. mPLUG-OwI2: Revolutionizing Multi-modal Large Language Model with Modality Collaboration**

- DOI：`10.1109/cvpr52733.2024.01239`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

Multi-modal Large Language Models (MLLMs) have demonstrated impressive instruction abilities across various open-ended tasks. However, previous methods primarily fo-cus on enhancing multi-modal capabilities. In this work, we introduce a versatile multi-modal large language model, mPLUG-Owl2, which effectively leverages modality collab-oration to improve performance in both text and multi-modal tasks. mPLUG-Owl2 utilizes a modularized network design, with the language decoder acting as a universal interface for managing different modalities. Specifically, mPLUG-Owl2 incorporates shared functional modules to facilitate modal-ity collaboration and introduces a modality-adaptive module that preserves modality-specific features. Extensive experi-ments reveal that mPLUG-Owl2 is capable of generalizing both text tasks and multi-modal tasks and achieving state-of-the-art performances with a single generic model. Notably, mPLUG-Owl2 is the first MLLM model that demonstrates the modality collaboration phenomenon in both pure-text and multi-modal scenarios, setting a pioneering path in the development of future multi-modal foundation models.

**25. Driving with LLMs: Fusing Object-Level Vector Modality for Explainable Autonomous Driving**

- DOI：`10.1109/icra57147.2024.10611018`
- 关联种子：`doi:10.48550/arxiv.2301.12597`（引用了种子）

Large Language Models (LLMs) have shown promise in the autonomous driving sector, particularly in generalization and interpretability. We introduce a unique objectlevel multimodal LLM architecture that merges vectorized numeric modalities with a pre-trained LLM to improve context understanding in driving situations. We also present a new dataset of 160k QA pairs derived from 10k driving scenarios, paired with high quality control commands collected with RL agent and question answer pairs generated by teacher LLM (GPT-3.5). A distinct pretraining strategy is devised to align numeric vector modalities with static LLM representations using vector captioning language data. We also introduce an evaluation metric for Driving QA and demonstrate our LLM-driver’s proficiency in interpreting driving scenarios, answering questions, and decision-making. Our findings highlight the potential of LLM-based driving action generation in comparison to traditional behavioral cloning. We make our benchmark, datasets, and model available1for further exploration.


## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | |
| 日期 | |
| 采纳的候选编号 | |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |
