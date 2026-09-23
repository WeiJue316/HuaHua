# 金标候选：csai_008

**问题**：How do parameter-efficient fine-tuning methods reduce training memory?

**子问题**：

1. Which parameter subsets are updated?
2. What memory and quality trade-offs are reported?

**现有 gold**：3 篇　**年份范围**：(2022, 2026)　**引用图候选**：25 篇

## 判定标准

一篇论文算作 gold，当且仅当**领域专家会把它作为回答某个子问题的证据引用**。
按子问题分别判定，因为证据是按子问题分配的。

逐条检查：

1. 论文是否真正回答某个子问题（不是主题相邻）
2. 年份是否在声明范围内
3. 摘要是否包含可以作为证据的完整句子
4. 判定它支撑哪个子问题（填编号）

## 候选清单

| # | 年份 | 标题 | 中文标题(机翻) | DOI | 被引 | 关系 | 命中 | 判定 | 子问题 |
|---:|---:|---|---|---|---:|---|---:|---|---:|
| 1 | 2024 | Democratizing protein language models with parameter-efficient fine-tu | 以参数高效微调推动蛋白质语言模型的普及化 | `10.1073/pnas.2405840121` | 88 | 引用了种子 | 7 | | |
| 2 | 2023 | FacT: Factor-Tuning for Lightweight Adaptation on Vision Transformer | FacT：面向视觉Transformer轻量化适配的因子微调 | `10.1609/aaai.v37i1.25187` | 98 | 引用了种子 | 6 | | |
| 3 | 2024 | Fine-tuning protein language models boosts predictions across diverse  | 微调蛋白质语言模型可提升多种任务的预测性能 | `10.1038/s41467-024-51844-2` | 218 | 引用了种子 | 5 | | |
| 4 | 2025 | Parameter-efficient fine-tuning in large language models: a survey of  | 大语言模型中的参数高效微调：方法学综述 | `10.1007/s10462-025-11236-4` | 152 | 引用了种子 | 5 | | |
| 5 | 2023 | On the Effectiveness of Parameter-Efficient Fine-Tuning | 论参数高效微调的有效性 | `10.1609/aaai.v37i11.26505` | 139 | 引用了种子 | 5 | | |
| 6 | 2022 | SPoT: Better Frozen Model Adaptation through Soft Prompt Transfer | SPoT：通过软提示迁移实现更好的冻结模型适配 | `10.18653/v1/2022.acl-long.346` | 178 | 被种子引用 | 4 | | |
| 7 | 2022 | Cutting Down on Prompts and Parameters: Simple Few-Shot Learning with  | 减少提示与参数：基于语言模型的简单少样本学习 | `10.18653/v1/2022.findings-acl.222` | 129 | 引用了种子 | 4 | | |
| 8 | 2024 | Boosting Continual Learning of Vision-Language Models via Mixture-of-E | 通过专家混合适配器提升视觉-语言模型的持续学习 | `10.1109/cvpr52733.2024.02191` | 122 | 引用了种子 | 4 | | |
| 9 | 2024 | A survey on LoRA of large language models | 大语言模型 LoRA 综述 | `10.1007/s11704-024-40663-9` | 120 | 引用了种子 | 4 | | |
| 10 | 2023 | A Unified Continual Learning Framework with General Parameter-Efficien | 基于通用参数高效微调的统一持续学习框架 | `10.1109/iccv51070.2023.01055` | 93 | 引用了种子 | 4 | | |
| 11 | 2023 | Towards Adaptive Prefix Tuning for Parameter-Efficient Language Model  | 面向参数高效语言模型微调的自适应前缀调优 | `10.18653/v1/2023.acl-short.107` | 91 | 引用了种子 | 4 | | |
| 12 | 2023 | FedPETuning: When Federated Learning Meets the Parameter-Efficient Tun | FedPETuning：当联邦学习遇上预训练语言模型的参数高效调优方法 | `10.18653/v1/2023.findings-acl.632` | 89 | 引用了种子 | 4 | | |
| 13 | 2024 | When MOE Meets LLMs: Parameter Efficient Fine-tuning for Multi-task Me | 当MOE遇上大语言模型：面向多任务医疗应用的参数高效微调 | `10.1145/3626772.3657722` | 88 | 引用了种子 | 4 | | |
| 14 | 2024 | Enhancing efficiency of protein language models with minimal wet-lab d | 通过少样本学习利用极少量湿实验数据提升蛋白质语言模型的效率 | `10.1038/s41467-024-49798-6` | 84 | 引用了种子 | 4 | | |
| 15 | 2023 | All in One: Multi-Task Prompting for Graph Neural Networks | 多合一：图神经网络的多任务提示 | `10.1145/3580305.3599256` | 175 | 引用了种子 | 3 | | |
| 16 | 2022 | No more fine-tuning? an experimental evaluation of prompt tuning in co | 不再需要微调？代码智能中提示微调的实验评估 | `10.1145/3540250.3549113` | 150 | 引用了种子 | 3 | | |
| 17 | 2023 | ViTPose++: Vision Transformer for Generic Body Pose Estimation | ViTPose++：用于通用人体姿态估计的视觉Transformer | `10.1109/tpami.2023.3330016` | 147 | 引用了种子 | 3 | | |
| 18 | 2023 | Enhancing Chat Language Models by Scaling High-quality Instructional C | 通过扩展高质量指令对话增强聊天语言模型 | `10.18653/v1/2023.emnlp-main.183` | 123 | 引用了种子 | 3 | | |
| 19 | 2023 | Fill in the Blank: Context-aware Automated Text Input Generation for M | 填空：面向移动GUI测试的上下文感知自动文本输入生成 | `10.1109/icse48619.2023.00119` | 121 | 引用了种子 | 3 | | |
| 20 | 2023 | Baize: An Open-Source Chat Model with Parameter-Efficient Tuning on Se | Baize：基于自聊天数据参数高效微调的开源聊天模型 | `10.18653/v1/2023.emnlp-main.385` | 119 | 引用了种子 | 3 | | |
| 21 | 2024 | SDSTrack: Self-Distillation Symmetric Adapter Learning for Multi-Modal | SDSTrack：面向多模态视觉目标跟踪的自蒸馏对称适配器学习 | `10.1109/cvpr52733.2024.02507` | 114 | 引用了种子 | 3 | | |
| 22 | 2024 | From Large Language Models to Large Multimodal Models: A Literature Re | 从大语言模型到大多模态模型：文献综述 | `10.3390/app14125068` | 101 | 引用了种子 | 3 | | |
| 23 | 2024 | Stronger, Fewer, & Superior: Harnessing Vision Foundation Models for D | 更强、更少、更优：利用视觉基础模型实现领域泛化语义分割 | `10.1109/cvpr52733.2024.02704` | 100 | 引用了种子 | 3 | | |
| 24 | 2024 | Deep learning for rice leaf disease detection: A systematic literature | 面向水稻叶片病害检测的深度学习：新兴趋势、方法与技术的系统性文献综述 | `10.1016/j.inpa.2024.04.006` | 92 | 引用了种子 | 3 | | |
| 25 | 2025 | A foundation model for generalizable cancer diagnosis and survival pre | 一种基于组织病理学图像的可泛化癌症诊断与生存预测基础模型 | `10.1038/s41467-025-57587-y` | 83 | 引用了种子 | 3 | | |

## 摘要（判定用）

判据 3 要求确认摘要里存在可作为证据的完整句子，因此这里附上原文摘要。
机翻标题仅供快速定位，**判定必须依据英文原文**。

**1. Democratizing protein language models with parameter-efficient fine-tuning**

- DOI：`10.1073/pnas.2405840121`
- 关联种子：`doi:10.1038/s42256-023-00626-4`（引用了种子）

Proteomics has been revolutionized by large protein language models (PLMs), which learn unsupervised representations from large corpora of sequences. These models are typically fine-tuned in a supervised setting to adapt the model to specific downstream tasks. However, the computational and memory footprint of fine-tuning (FT) large PLMs presents a barrier for many research groups with limited computational resources. Natural language processing has seen a similar explosion in the size of models, where these challenges have been addressed by methods for parameter-efficient fine-tuning (PEFT). In this work, we introduce this paradigm to proteomics through leveraging the parameter-efficient method LoRA and training new models for two important tasks: predicting protein-protein interactions (PPIs) and predicting the symmetry of homooligomer quaternary structures. We show that these approaches are competitive with traditional FT while requiring reduced memory and substantially fewer parameters. We additionally show that for the PPI prediction task, training only the classification head also remains competitive with full FT, using five orders of magnitude fewer parameters, and that each of these methods outperform state-of-the-art PPI prediction methods with substantially reduced compute. We further perform a comprehensive evaluation of the hyperparameter space, demonstrate that PEFT of PLMs is robust to variations in these hyperparameters, and elucidate where best practices for PEFT in proteomics differ from those in natural language processing. All our model adaptation and evaluation code is available open-source at https://github.com/microsoft/peft_proteomics. Thus, we provide a blueprint to democratize the power of PLM adaptation to groups with limited computational resources.

**2. FacT: Factor-Tuning for Lightweight Adaptation on Vision Transformer**

- DOI：`10.1609/aaai.v37i1.25187`
- 关联种子：`doi:10.18653/v1/2022.acl-short.1`（引用了种子）

Recent work has explored the potential to adapt a pre-trained vision transformer (ViT) by updating only a few parameters so as to improve storage efficiency, called parameter-efficient transfer learning (PETL). Current PETL methods have shown that by tuning only 0.5% of the parameters, ViT can be adapted to downstream tasks with even better performance than full fine-tuning. In this paper, we aim to further promote the efficiency of PETL to meet the extreme storage constraint in real-world applications. To this end, we propose a tensorization-decomposition framework to store the weight increments, in which the weights of each ViT are tensorized into a single 3D tensor, and their increments are then decomposed into lightweight factors. In the fine-tuning process, only the factors need to be updated and stored, termed Factor-Tuning (FacT). On VTAB-1K benchmark, our method performs on par with NOAH, the state-of-the-art PETL method, while being 5x more parameter-efficient. We also present a tiny version that only uses 8K (0.01% of ViT's parameters) trainable parameters but outperforms full fine-tuning and many other PETL methods such as VPT and BitFit. In few-shot settings, FacT also beats all PETL baselines using the fewest parameters, demonstrating its strong capability in the low-data regime.

**3. Fine-tuning protein language models boosts predictions across diverse tasks**

- DOI：`10.1038/s41467-024-51844-2`
- 关联种子：`doi:10.1038/s42256-023-00626-4`（引用了种子）

Prediction methods inputting embeddings from protein language models have reached or even surpassed state-of-the-art performance on many protein prediction tasks. In natural language processing fine-tuning large language models has become the de facto standard. In contrast, most protein language model-based protein predictions do not back-propagate to the language model. Here, we compare the fine-tuning of three state-of-the-art models (ESM2, ProtT5, Ankh) on eight different tasks. Two results stand out. Firstly, task-specific supervised fine-tuning almost always improves downstream predictions. Secondly, parameter-efficient fine-tuning can reach similar improvements consuming substantially fewer resources at up to 4.5-fold acceleration of training over fine-tuning full models. Our results suggest to always try fine-tuning, in particular for problems with small datasets, such as for fitness landscape predictions of a single protein. For ease of adaptability, we provide easy-to-use notebooks to fine-tune all models used during this work for per-protein (pooling) and per-residue prediction tasks.

**4. Parameter-efficient fine-tuning in large language models: a survey of methodologies**

- DOI：`10.1007/s10462-025-11236-4`
- 关联种子：`doi:10.18653/v1/2022.acl-short.8`（引用了种子）

The large language models, as predicted by scaling law forecasts, have made groundbreaking progress in many fields, particularly in natural language generation tasks, where they have approached or even surpassed human levels. However, the unprecedented scale of their parameters brings significant computational and storage costs. These large language models require substantial computational resources and GPU memory to operate. When adapting large language models to specific downstream tasks, their massive parameter scale poses a significant challenge in fine-tuning on hardware platforms with limited computational power and GPU memory. To address this issue, parameter-efficient fine-tuning (PEFT) offers a practical solution by efficiently adjusting the parameters of large pre-trained models to suit various downstream tasks. Specifically, PEFT adjusts the parameters of pre-trained large language models to adapt to specific tasks or domains, minimizing the introduction of additional parameters and the computational resources required. This review mainly introduces the preliminary knowledge of PEFT, the core ideas and principles of various PEFT algorithms, the applications of PEFT, and potential future research directions. By reading this review, we believe that interested parties can quickly grasp the PEFT methodology, thereby accelerating its development and innovation.

**5. On the Effectiveness of Parameter-Efficient Fine-Tuning**

- DOI：`10.1609/aaai.v37i11.26505`
- 关联种子：`doi:10.18653/v1/2022.acl-short.1`（引用了种子）

Fine-tuning pre-trained models has been ubiquitously proven to be effective in a wide range of NLP tasks. However, fine-tuning the whole model is parameter inefficient as it always yields an entirely new model for each task. Currently, many research works propose to only fine-tune a small portion of the parameters while keeping most of the parameters shared across different tasks. These methods achieve surprisingly good performance and are shown to be more stable than their corresponding fully fine-tuned counterparts. However, such kind of methods is still not well understood. Some natural questions arise: How does the parameter sparsity lead to promising performance? Why is the model more stable than the fully fine-tuned models? How to choose the tunable parameters? In this paper, we first categorize the existing methods into random approaches, rule-based approaches, and projection-based approaches based on how they choose which parameters to tune. Then, we show that all of the methods are actually sparse fine-tuned models and conduct a novel theoretical analysis of them. We indicate that the sparsity is actually imposing a regularization on the original model by controlling the upper bound of the stability. Such stability leads to better generalization capability which has been empirically observed in a lot of recent research works. Despite the effectiveness of sparsity grounded by our theory, it still remains an open problem of how to choose the tunable parameters. Currently, the random and rule-based methods do not utilize task-specific data information while the projection-based approaches suffer from the projection discontinuity problem. To better choose the tunable parameters, we propose a novel Second-order Approximation Method (SAM) which approximates the original problem with an analytically solvable optimization function. The tunable parameters are determined by directly optimizing the approximation function. We conduct extensive experiments on several tasks. The experimental results show that our proposed SAM model outperforms many strong baseline models and it also verifies our theoretical analysis. The source code of this paper can be obtained from https://github.com/fuzihaofzh/AnalyzeParameterEff\/icientFinetune .

**6. SPoT: Better Frozen Model Adaptation through Soft Prompt Transfer**

- DOI：`10.18653/v1/2022.acl-long.346`
- 关联种子：`doi:10.1038/s42256-023-00626-4`（被种子引用）

There has been growing interest in parameter-efficient methods to apply pre-trained language models to downstream tasks. Building on the Prompt Tuning approach of Lester et al. (2021), which learns task-specific soft prompts to condition a frozen pre-trained model to perform different tasks, we propose a novel prompt-based transfer learning approach called SPoT: Soft Prompt Transfer. SPoT first learns a prompt on one or more source tasks and then uses it to initialize the prompt for a target task. We show that SPoT significantly boosts the performance of Prompt Tuning across many tasks. More remarkably, across all model sizes, SPoT matches or outperforms standard Model Tuning (which fine-tunes all model parameters) on the SuperGLUE benchmark, while using up to 27,000× fewer task-specific parameters. To understand where SPoT is most effective, we conduct a large-scale study on task transferability with 26 NLP tasks in 160 combinations, and demonstrate that many tasks can benefit each other via prompt transfer. Finally, we propose an efficient retrieval approach that interprets task prompts as task embeddings to identify similar tasks and predict the most transferable source tasks for a novel target task.

**7. Cutting Down on Prompts and Parameters: Simple Few-Shot Learning with Language Models**

- DOI：`10.18653/v1/2022.findings-acl.222`
- 关联种子：`doi:10.18653/v1/2022.acl-short.1`（引用了种子）

Prompting language models (LMs) with training examples and task descriptions has been seen as critical to recent successes in few-shot learning.In this work, we show that finetuning LMs in the few-shot setting can considerably reduce the need for prompt engineering.In fact, one can use null prompts, prompts that contain neither task-specific templates nor training examples, and achieve competitive accuracy to manually-tuned prompts across a wide range of tasks.While finetuning LMs does introduce new parameters for each downstream task, we show that this memory overhead can be substantially reduced-finetuning only the bias terms can achieve comparable or better accuracy than standard finetuning while only updating 0.1% of the parameters.All in all, we recommend finetuning LMs for few-shot learning as it is more accurate, has relatively stable performance across different prompts, and can be made nearly as efficient as using frozen LMs.

**8. Boosting Continual Learning of Vision-Language Models via Mixture-of-Experts Adapters**

- DOI：`10.1109/cvpr52733.2024.02191`
- 关联种子：`doi:10.18653/v1/2022.acl-short.1`（引用了种子）

Continual learning can empower vision-language models to continuously acquire new knowledge, without the need for access to the entire historical dataset. However, mitigating the performance degradation in large-scale models is non-trivial due to (i) parameter shifts throughout life-long learning and (ii) significant computational burdens associated with full-model tuning. In this work, we present a parameter-efficient continual learning framework to alleviate long-term forgetting in incremental learning with vision-language models. Our approach involves the dynamic expansion of a pre-trained CLIP model, through the integration of Mixture-of-Experts (MoE) adapters in response to new tasks. To preserve the zero-shot recognition capability of vision-language models, we further introduce a Distribution Discriminative Auto-Selector (DDAS) that automatically routes in-distribution and out-of-distribution inputs to the MoE Adapter and the original CLIP, respectively. Through extensive experiments across various settings, our proposed method consistently outperforms previous state-of-the-art approaches while concurrently reducing parameter training burdens by 60%. Our code locates at https://github.com/JiazuoYu/MoE-Adapters4CL

**9. A survey on LoRA of large language models**

- DOI：`10.1007/s11704-024-40663-9`
- 关联种子：`doi:10.1038/s42256-023-00626-4`（引用了种子）

Abstract Low-Rank Adaptation (LoRA), which updates the dense neural network layers with pluggable low-rank matrices, is one of the best performed parameter efficient fine-tuning paradigms. Furthermore, it has significant advantages in cross-task generalization and privacy-preserving. Hence, LoRA has gained much attention recently, and the number of related literature demonstrates exponential growth. It is necessary to conduct a comprehensive overview of the current progress on LoRA. This survey categorizes and reviews the progress from the perspectives of (1) downstream adaptation improving variants that improve LoRA’s performance on downstream tasks; (2) cross-task generalization methods that mix multiple LoRA plugins to achieve cross-task generalization; (3) efficiency-improving methods that boost the computation-efficiency of LoRA; (4) data privacy-preserving methods that use LoRA in federated learning; (5) application. Besides, this survey also discusses the future directions in this field.

**10. A Unified Continual Learning Framework with General Parameter-Efficient Tuning**

- DOI：`10.1109/iccv51070.2023.01055`
- 关联种子：`doi:10.18653/v1/2022.acl-short.1`（引用了种子）

The "pre-training → downstream adaptation" presents both new opportunities and challenges for Continual Learning (CL). Although the recent state-of-the-art in CL is achieved through Parameter-Efficient-Tuning (PET) adaptation paradigm, only prompt has been explored, limiting its application to Transformers only. In this paper, we position prompting as one instantiation of PET, and propose a unified CL framework with general PET, dubbed as Learning-Accumulation-Ensemble (LAE). PET, e.g., using Adapter, LoRA, or Prefix, can adapt a pre-trained model to downstream tasks with fewer parameters and resources. Given a PET method, our LAE framework incorporates it for CL with three novel designs. 1) Learning: the pre-trained model adapts to the new task by tuning an online PET module, along with our adaptation speed calibration to align different PET modules, 2) Accumulation: the task-specific knowledge learned by the online PET module is accumulated into an offline PET module through momentum update, 3) Ensemble: During inference, we respectively construct two experts with online/offline PET modules (which are favored by the novel/historical tasks) for prediction ensemble. We show that LAE is compatible with a battery of PET methods and gains strong CL capability. For example, LAE with Adaptor PET surpasses the prior state-of-the-art by 1.3% and 3.6% in last-incremental accuracy on CIFAR100 and ImageNet-R datasets, respectively. Code is available at https://github.com/gqk/LAE.

**11. Towards Adaptive Prefix Tuning for Parameter-Efficient Language Model Fine-tuning**

- DOI：`10.18653/v1/2023.acl-short.107`
- 关联种子：`doi:10.18653/v1/2022.acl-short.8`（引用了种子）

Fine-tuning large pre-trained language models on various downstream tasks with whole parameters is prohibitively expensive.Hence, Parameter-efficient fine-tuning has attracted attention that only optimizes a few task-specific parameters with the frozen pre-trained model.In this work, we focus on prefix tuning, which only optimizes continuous prefix vectors (i.e.pseudo tokens) inserted into Transformer layers.Based on the observation that the learned syntax and semantics representation varies a lot at different layers, we argue that the adaptive prefix will be further tailored to each layer than the fixed one, enabling the fine-tuning more effective and efficient.Thus, we propose Adaptive Prefix Tuning (APT) to adjust the prefix in terms of both fine-grained token level and coarse-grained layer level with a gate mechanism.Experiments on the SuperGLUE and NER datasets show the effectiveness of APT.In addition, taking the gate as a probing, we validate the efficiency and effectiveness of the variable prefix.

**12. FedPETuning: When Federated Learning Meets the Parameter-Efficient Tuning Methods of Pre-trained Language Models**

- DOI：`10.18653/v1/2023.findings-acl.632`
- 关联种子：`doi:10.18653/v1/2022.acl-short.1`（引用了种子）

With increasing concerns about data privacy, there is an increasing necessity of fine-tuning pre-trained language models (PLMs) for adapting to downstream tasks located in end-user devices or local clients without transmitting data to the central server.This urgent necessity therefore calls the research of investigating federated learning (FL) for PLMs.However, large PLMs bring the curse of prohibitive communication overhead and local model adaptation costs for the FL system.To this end, we investigate the parameter-efficient tuning (PETuning) of PLMs and develop a corresponding federated benchmark for four representative PETuning methods, dubbed FedPETuning.Specifically, FedPETuning provides the first holistic empirical study of representative PLMs tuning methods in FL, covering privacy attacks, performance comparisons, and resource-constrained analysis.Intensive experimental results have indicated that FedPETuning can efficiently defend against privacy attacks and maintains acceptable performance with reducing heavy resource consumption.The open-source code and data are available at https://github. com/SMILELab-FL/FedPETuning.

**13. When MOE Meets LLMs: Parameter Efficient Fine-tuning for Multi-task Medical Applications**

- DOI：`10.1145/3626772.3657722`
- 关联种子：`doi:10.18653/v1/2022.acl-short.8`（引用了种子）

The recent surge in Large Language Models (LLMs) has garnered significant attention across numerous fields. Fine-tuning is often required to fit general LLMs for a specific domain, like the web-based healthcare system. However, two problems arise during fine-tuning LLMs for medical applications. One is the task variety problem, which involves distinct tasks in real-world medical scenarios. The variety often leads to sub-optimal fine-tuning for data imbalance and seesaw problems. Besides, the large amount of parameters in LLMs leads to huge time and computation consumption by fine-tuning. To address these two problems, we propose a novel parameter efficient fine-tuning framework for multi-task medical applications, dubbed as MOELoRA. The designed framework aims to absorb both the benefits of mixture-of-expert (MOE) for multi-task learning and low-rank adaptation (LoRA) for parameter efficient fine-tuning. For unifying MOE and LoRA, we devise multiple experts as the trainable parameters, where each expert consists of a pair of low-rank matrices to retain the small size of trainable parameters. Then, a task-motivated gate function for all MOELoRA layers is proposed, which can control the contributions of each expert and produce distinct parameters for various tasks. We conduct experiments on a multi-task medical dataset, indicating MOELoRA outperforms the existing parameter efficient fine-tuning methods. The code is available online.

**14. Enhancing efficiency of protein language models with minimal wet-lab data through few-shot learning**

- DOI：`10.1038/s41467-024-49798-6`
- 关联种子：`doi:10.1038/s42256-023-00626-4`（引用了种子）

Accurately modeling the protein fitness landscapes holds great importance for protein engineering. Pre-trained protein language models have achieved state-of-the-art performance in predicting protein fitness without wet-lab experimental data, but their accuracy and interpretability remain limited. On the other hand, traditional supervised deep learning models require abundant labeled training examples for performance improvements, posing a practical barrier. In this work, we introduce FSFP, a training strategy that can effectively optimize protein language models under extreme data scarcity for fitness prediction. By combining meta-transfer learning, learning to rank, and parameter-efficient fine-tuning, FSFP can significantly boost the performance of various protein language models using merely tens of labeled single-site mutants from the target protein. In silico benchmarks across 87 deep mutational scanning datasets demonstrate FSFP's superiority over both unsupervised and supervised baselines. Furthermore, we successfully apply FSFP to engineer the Phi29 DNA polymerase through wet-lab experiments, achieving a 25% increase in the positive rate. These results underscore the potential of our approach in aiding AI-guided protein engineering.

**15. All in One: Multi-Task Prompting for Graph Neural Networks**

- DOI：`10.1145/3580305.3599256`
- 关联种子：`doi:10.18653/v1/2022.acl-short.8`（引用了种子）

Recently, "pre-training and fine-tuning'' has been adopted as a standard workflow for many graph tasks since it can take general graph knowledge to relieve the lack of graph annotations from each application. However, graph tasks with node level, edge level, and graph level are far diversified, making the pre-training pretext often incompatible with these multiple tasks. This gap may even cause a "negative transfer'' to the specific application, leading to poor results. Inspired by the prompt learning in natural language processing (NLP), which has presented significant effectiveness in leveraging prior knowledge for various NLP tasks, we study the prompting topic for graphs with the motivation of filling the gap between pre-trained models and various graph tasks. In this paper, we propose a novel multi-task prompting method for graph models. Specifically, we first unify the format of graph prompts and language prompts with the prompt token, token structure, and inserting pattern. In this way, the prompting idea from NLP can be seamlessly introduced to the graph area. Then, to further narrow the gap between various graph tasks and state-of-the-art pre-training strategies, we further study the task space of various graph applications and reformulate downstream problems to the graph-level task. Afterward, we introduce meta-learning to efficiently learn a better initialization for the multi-task prompt of graphs so that our prompting framework can be more reliable and general for different tasks. We conduct extensive experiments, results from which demonstrate the superiority of our method.

**16. No more fine-tuning? an experimental evaluation of prompt tuning in code intelligence**

- DOI：`10.1145/3540250.3549113`
- 关联种子：`doi:10.18653/v1/2022.acl-short.8`（引用了种子）

Pre-trained models have been shown effective in many code intelligence tasks. These models are pre-trained on large-scale unlabeled corpus and then fine-tuned in downstream tasks. However, as the inputs to pre-training and downstream tasks are in different forms, it is hard to fully explore the knowledge of pre-trained models. Besides, the performance of fine-tuning strongly relies on the amount of downstream data, while in practice, the scenarios with scarce data are common. Recent studies in the natural language processing (NLP) field show that prompt tuning, a new paradigm for tuning, alleviates the above issues and achieves promising results in various NLP tasks. In prompt tuning, the prompts inserted during tuning provide task-specific knowledge, which is especially beneficial for tasks with relatively scarce data. In this paper, we empirically evaluate the usage and effect of prompt tuning in code intelligence tasks. We conduct prompt tuning on popular pre-trained models CodeBERT and CodeT5 and experiment with three code intelligence tasks including defect prediction, code summarization, and code translation. Our experimental results show that prompt tuning consistently outperforms fine-tuning in all three tasks. In addition, prompt tuning shows great potential in low-resource scenarios, e.g., improving the BLEU scores of fine-tuning by more than 26% on average for code summarization. Our results suggest that instead of fine-tuning, we could adapt prompt tuning for code intelligence tasks to achieve better performance, especially when lacking task-specific data.

**17. ViTPose++: Vision Transformer for Generic Body Pose Estimation**

- DOI：`10.1109/tpami.2023.3330016`
- 关联种子：`doi:10.18653/v1/2022.acl-short.8`（引用了种子）

In this paper, we show the surprisingly good properties of plain vision transformers for body pose estimation from various aspects, namely simplicity in model structure, scalability in model size, flexibility in training paradigm, and transferability of knowledge between models, through a simple baseline model dubbed ViTPose. ViTPose employs the plain and non-hierarchical vision transformer as an encoder to encode features and a lightweight decoder to decode body keypoints in either a top-down or a bottom-up manner. It can be scaled to 1B parameters by taking the advantage of the scalable model capacity and high parallelism, setting a new Pareto front for throughput and performance. Besides, ViTPose is very flexible regarding the attention type, input resolution, and pre-training and fine-tuning strategy. Based on the flexibility, a novel ViTPose++ model is proposed to deal with heterogeneous body keypoint categories via knowledge factorization, i.e., adopting task-agnostic and task-specific feed-forward networks in the transformer. We also demonstrate that the knowledge of large ViTPose models can be easily transferred to small ones via a simple knowledge token. Our largest single model ViTPose-G sets a new record on the MS COCO test set without model ensemble. Furthermore, our ViTPose++ model achieves state-of-the-art performance simultaneously on a series of body pose estimation tasks, including MS COCO, AI Challenger, OCHuman, MPII for human keypoint detection, COCO-Wholebody for whole-body keypoint detection, as well as AP-10K and APT-36K for animal keypoint detection, without sacrificing inference speed.

**18. Enhancing Chat Language Models by Scaling High-quality Instructional Conversations**

- DOI：`10.18653/v1/2023.emnlp-main.183`
- 关联种子：`doi:10.1038/s42256-023-00626-4`（引用了种子）

Fine-tuning on instruction data has been widely validated as an effective practice for implementing chat language models like ChatGPT.Scaling the diversity and quality of such data, although straightforward, stands a great chance of leading to improved performance.This paper aims to push the upper bound of opensource models further.We first provide a systematically designed, diverse, informative, large-scale dataset of instructional conversations, UltraChat, which does not involve human queries.Our objective is to capture the breadth of interactions between a human user and an AI assistant and employs a comprehensive framework to generate multi-turn conversation iteratively.UltraChat contains 1.5 million high-quality multi-turn dialogues and covers a wide range of topics and instructions.Our statistical analysis of UltraChat reveals its superiority in various key metrics, including scale, average length, diversity, coherence, etc., solidifying its position as a leading opensource dataset.Building upon UltraChat, we fine-tune a LLaMA model to create a powerful conversational model, UltraLM.Our evaluations indicate that UltraLM consistently outperforms other open-source models, including WizardLM and Vicuna, the previously recognized state-of-the-art open-source models.

**19. Fill in the Blank: Context-aware Automated Text Input Generation for Mobile GUI Testing**

- DOI：`10.1109/icse48619.2023.00119`
- 关联种子：`doi:10.18653/v1/2022.acl-short.8`（引用了种子）

Automated GUI testing is widely used to help ensure the quality of mobile apps. However, many GUIs require appropriate text inputs to proceed to the next page, which remains a prominent obstacle for testing coverage. Considering the diversity and semantic requirement of valid inputs (e.g., flight departure, movie name), it is challenging to automate the text input generation. Inspired by the fact that the pre-trained Large Language Model (LLM) has made outstanding progress in text generation, we propose an approach named QTypist based on LLM for intelligently generating semantic input text according to the GUI context. To boost the performance of LLM in the mobile testing scenario, we develop a prompt-based data construction and tuning method which automatically extracts the prompts and answers for model tuning. We evaluate QTypist on 106 apps from Google Play, and the result shows that the passing rate of QTypist is 87%, which is 93% higher than the best baseline. We also integrate QTypist with the automated GUI testing tools and it can cover 42% more app activities, 52% more pages, and subsequently help reveal 122% more bugs compared with the raw tool.

**20. Baize: An Open-Source Chat Model with Parameter-Efficient Tuning on Self-Chat Data**

- DOI：`10.18653/v1/2023.emnlp-main.385`
- 关联种子：`doi:10.18653/v1/2022.acl-short.1`（引用了种子）

Chat models, such as ChatGPT, have shown impressive capabilities and have been rapidly adopted across numerous domains.However, these models are only accessible through a restricted API, creating barriers for new research and progress in the field.We propose a pipeline that can automatically generate a highquality multi-turn chat corpus by leveraging ChatGPT to engage in a conversation with itself.Subsequently, we employ parameter-efficient tuning to enhance LLaMA, an open-source large language model.The resulting model, named Baize, demonstrates good performance in multi-turn dialogues with guardrails that minimize potential risks.Additionally, we propose a new technique called Self-Distill with Feedback, to further improve the performance of the Baize models with feedback from ChatGPT.The Baize models and data are released for research purposes only. 1

**21. SDSTrack: Self-Distillation Symmetric Adapter Learning for Multi-Modal Visual Object Tracking**

- DOI：`10.1109/cvpr52733.2024.02507`
- 关联种子：`doi:10.18653/v1/2022.acl-short.1`（引用了种子）

Multimodal Visual Object Tracking (VOT) has recently gained significant attention due to its robustness. Early research focused on fully fine-tuning RGB-based trackers, which was inefficient and lacked generalized representation due to the scarcity of multimodal data. Therefore, recent studies have utilized prompt tuning to transfer pre-trained RGB-based trackers to multimodal data. However, the modality gap limits pre-trained knowledge recall, and the dominance of the RGB modality persists, preventing the full utilization of information from other modalities. To address these issues, we propose a novel symmetric multimodal tracking framework called SDSTrack. We introduce lightweight adaptation for efficient fine-tuning, which directly transfers the feature extraction ability from RGB to other domains with a small number of trainable parameters and integrates multimodal features in a balanced, symmetric manner. Furthermore, we design a complementary masked patch distillation strategy to enhance the robustness of trackers in complex environments, such as extreme weather, poor imaging, and sensor failure. Extensive experiments demonstrate that SDSTrack outperforms state-of-the-art methods in various multimodal tracking scenarios, including RGB+Depth, RGB+Thermal, and RGB+Event tracking, and exhibits impressive results in extreme conditions. Our source code is available at: https://github.com/hoqolo/SDSTrack.

**22. From Large Language Models to Large Multimodal Models: A Literature Review**

- DOI：`10.3390/app14125068`
- 关联种子：`doi:10.18653/v1/2022.acl-short.8`（引用了种子）

With the deepening of research on Large Language Models (LLMs), significant progress has been made in recent years on the development of Large Multimodal Models (LMMs), which are gradually moving toward Artificial General Intelligence. This paper aims to summarize the recent progress from LLMs to LMMs in a comprehensive and unified way. First, we start with LLMs and outline various conceptual frameworks and key techniques. Then, we focus on the architectural components, training strategies, fine-tuning guidance, and prompt engineering of LMMs, and present a taxonomy of the latest vision–language LMMs. Finally, we provide a summary of both LLMs and LMMs from a unified perspective, make an analysis of the development status of large-scale models in the view of globalization, and offer potential research directions for large-scale models.

**23. Stronger, Fewer, & Superior: Harnessing Vision Foundation Models for Domain Generalized Semantic Segmentation**

- DOI：`10.1109/cvpr52733.2024.02704`
- 关联种子：`doi:10.18653/v1/2022.acl-short.8`（引用了种子）

In this paper, we first assess and harness various Vision Foundation Models (VFMs) in the context of Domain Generalized Semantic Segmentation (DGSS). Driven by the motivation that Leveraging Stronger pre-trained models and Fewer trainable parameters for Superior generalizability, we introduce a robust fine-tuning approach, namely “Rein”, to parameter-efficiently harness VFMs for DGSS. Built upon a set of trainable tokens, each linked to distinct instances, Rein precisely refines and forwards the feature maps from each layer to the next layer within the backbone. This process produces diverse refinements for different categories within a single image. With fewer trainable parameters, Rein efficiently fine-tunes VFMs for DGSS tasks, surprisingly surpassing full parameter fine-tuning. Extensive experiments across various settings demonstrate that Rein significantly outperforms state-of-the-art methods. Remarkably, with just an extra 1% of trainable parameters within the frozen backbone, Rein achieves a mIoU of 78.4% on the Cityscapes, without accessing any real urban-scene datasets. Code is available at https://github.com/w1oves/Rein.git.

**24. Deep learning for rice leaf disease detection: A systematic literature review on emerging trends, methodologies and techniques**

- DOI：`10.1016/j.inpa.2024.04.006`
- 关联种子：`doi:10.18653/v1/2022.acl-short.1`（引用了种子）

Rice is an essential food crop that is cultivated in many countries. Rice leaf diseases can cause significant damage to crop cultivation, leading to reduced yields and economic losses. Traditional disease detection approaches are often time-consuming, labor-intensive, and require expertise. Automatic leaf disease detection approaches help farmers detect diseases without or with less human interference. Most of the earlier studies on rice leaf disease detection depended on image processing and machine learning techniques. Image processing techniques are used to extract features from diseased leaf images, such as the color, texture, vein patterns, and shape of lesions. Machine learning techniques are used to detect diseases based on the extracted features. In contrast, deep learning techniques learn complex patterns from large datasets without explicit feature extraction techniques and are well-suited for disease detection tasks. This systematic review explores various deep learning approaches used in the literature for rice leaf disease detection, such as Transfer Learning, Ensemble Learning, and Hybrid approaches. This review also discusses the effectiveness of these approaches in addressing various challenges. This review discusses the details of various models and hyperparameter settings used, model fine-tuning techniques followed, and performance evaluation metrics utilized in various studies. This review also discusses the limitations of existing studies and presents future directions for further developing more robust and efficient rice leaf disease detection techniques.

**25. A foundation model for generalizable cancer diagnosis and survival prediction from histopathological images**

- DOI：`10.1038/s41467-025-57587-y`
- 关联种子：`doi:10.1038/s42256-023-00626-4`（引用了种子）

Computational pathology, utilizing whole slide images (WSIs) for pathological diagnosis, has advanced the development of intelligent healthcare. However, the scarcity of annotated data and histological differences hinder the general application of existing methods. Extensive histopathological data and the robustness of self-supervised models in small-scale data demonstrate promising prospects for developing foundation pathology models. Here we show BEPH (BEiT-based model Pre-training on Histopathological image), a foundation model that leverages self-supervised learning to learn meaningful representations from 11 million unlabeled histopathological images. These representations are then efficiently adapted to various tasks, including patch-level cancer diagnosis, WSI-level cancer classification, and survival prediction for multiple cancer subtypes. By leveraging the masked image modeling (MIM) pre-training approach, BEPH offers an efficient solution to enhance model performance, reduce the reliance on expert annotations, and facilitate the broader application of artificial intelligence in clinical settings. The pre-trained model is available at https://github.com/Zhcyoung/BEPH .


## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | |
| 日期 | |
| 采纳的候选编号 | |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |
