# 金标候选：csai_009

**问题**：What techniques accelerate transformer inference without retraining?

　　→ 哪些技术能在不重新训练的情况下加速 Transformer 推理？

**子问题**：

1. Which inference-time optimizations are used?
　　→ 使用了哪些推理时优化方法？

2. What latency and quality trade-offs are reported?
　　→ 报告了哪些延迟与质量的权衡？


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
| 1 | 2023 | Q-Diffusion: Quantizing Diffusion Models | Q-Diffusion：量化扩散模型 | `10.1109/iccv51070.2023.01608` | 135 | 引用了种子 | 3 | 建议不采纳 | 不采纳 |  | 该论文研究扩散模型的训练后量化加速，未涉及 transformer 推理，属于主题相邻但不直接回答任何子问题。 |
| 2 | 2023 | I-ViT: Integer-only Quantization for Efficient Vision Transformer Infe | I-ViT：面向高效视觉Transformer推理的纯整数量化 | `10.1109/iccv51070.2023.01565` | 126 | 引用了种子 | 3 | 建议采纳(两个子问题) | 采纳 | 2 | 引文｜Furthermore, we utilize TVM for practical hardware deployment on the GPU’s integer arithmetic units, achieving 3.72 ~ 4.11 inference speedup compared to the FP model.｜理由｜审计修正：该引文直接支持速度收益与硬件实现，不单独证明推理时优化类别。 |
| 3 | 2025 | Edge Intelligence: A Review of Deep Neural Network Inference in Resour | 边缘智能：资源受限环境下深度神经网络推理综述 | `10.3390/electronics14122495` | 80 | 引用了种子 | 3 | 建议不采纳 | 不采纳 |  | 该综述讨论的是边缘设备上通用DNN推理加速（模型压缩、编译器优化、软硬件协同设计），未涉及Transformer架构，也未区分是否需要重训练，属于主题相邻而非直接证据。 |
| 4 | 2024 | Fluctuation-Based Adaptive Structured Pruning for Large Language Model | 基于波动的自适应结构化剪枝用于大语言模型 | `10.1609/aaai.v38i10.28960` | 43 | 引用了种子 | 3 | 建议采纳(子问题1) | 采纳 | 1 | 引文｜In this paper, we propose a novel retraining-free structured pruning framework for LLMs, named FLAP (FLuctuation-based Adaptive Structured Pruning).｜理由｜It proposes retraining-free structured pruning to accelerate LLM inference, supporting subquestion 1. |
| 5 | 2024 | Agile-Quant: Activation-Guided Quantization for Faster Inference of LL | Agile-Quant：面向边缘端大语言模型更快推理的激活引导量化 | `10.1609/aaai.v38i17.29860` | 34 | 引用了种子 | 3 | 建议采纳(两个子问题) | 采纳 | 1,2 | 引文｜Considering the hardware profiling and activation analysis, we first introduce a basic activation quantization strategy to balance the trade-off of task performance and real inference speed.｜理由｜该摘要明确涉及推理时激活量化等优化，并讨论了任务性能与真实推理速度之间的权衡。 |
| 6 | 2024 | Efficient LLMs Training and Inference: An Introduction | 高效大语言模型训练与推理：导论 | `10.1109/access.2024.3501358` | 27 | 引用了种子 | 3 | 建议不采纳 | 不采纳 |  | 主题相邻：摘要仅泛泛提及训练与推理阶段的优化策略，未列出任何具体的推理时优化技术，也未报告延迟与质量权衡。 |
| 7 | 2024 | One-Shot Sensitivity-Aware Mixed Sparsity Pruning for Large Language M | 面向大语言模型的一次性敏感度感知混合稀疏剪枝 | `10.1109/icassp48485.2024.10445737` | 26 | 引用了种子 | 3 | 建议采纳(子问题1) | 采纳 | 1 | 引文｜In this work, we propose a method based on Hessian sensitivity-aware mixed sparsity pruning to prune LLMs to at least 50% sparsity without the need of any retraining.｜理由｜该文提出免重训练的稀疏剪枝来降低大模型推理延迟，属于加速推理的压缩技术，但摘要未给出具体的延迟与质量权衡数据，故只支持子问题1。 |
| 8 | 2024 | 8-bit Transformer Inference and Fine-tuning for Edge Accelerators | 面向边缘加速器的 8 位 Transformer 推理与微调 | `10.1145/3620666.3651368` | 26 | 引用了种子 | 3 | 建议采纳(子问题1) | 采纳 | 1 | 引文｜Quantization to lower precision data types is a promising way to reduce computation and memory resources.｜理由｜该文以8位量化（int8/FP8）作为减少Transformer推理计算与内存开销的推理时优化手段，可回答子问题1（推理时优化技术）；摘要未报告延迟与质量的具体权衡数据，故不支持子问题2。 |
| 9 | 2025 | AWQ: Activation-aware Weight Quantization for On-Device LLM Compressio | AWQ：面向端侧大语言模型压缩与加速的激活感知权重量化 | `10.1145/3714983.3714987` | 223 | 引用了种子 | 2 | 建议采纳(两个子问题) | 采纳 | 1,2 | 引文｜TinyChat, an optimized inference framework, translates AWQ's theoretical memory savings into practical speedups through techniques such as on-the-fly dequantization, SIMD-aware weight packing, and kernel fusion.｜理由｜AWQ 是一种免训练的后训练权重量化方法，其 TinyChat 框架明确列出了推理时优化技术（on-the-fly dequantization、SIMD-aware weight packing、kernel fusion），并报告了 4x 模型压缩与 3-4x 加速且“preserving performance”的延迟-质量权衡，因此同时回答两个子问题。 |
| 10 | 2025 | Empowering Edge Intelligence: A Comprehensive Survey on On-Device AI M | 赋能边缘智能：端侧 AI 模型综合综述 | `10.1145/3724420` | 189 | 引用了种子 | 2 | 建议不采纳 | 不采纳 |  | 主题相邻：该综述讨论端侧AI的模型压缩与硬件加速等优化，但未具体涉及transformer推理加速技术或延迟与质量权衡。 |
| 11 | 2023 | LLMLingua: Compressing Prompts for Accelerated Inference of Large Lang | LLMLingua：压缩提示以实现大语言模型的加速推理 | `10.18653/v1/2023.emnlp-main.825` | 137 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 1 | 引文｜To accelerate model inference and reduce cost, this paper presents LLMLingua, a coarse-to-fine prompt compression method that involves a budget controller to maintain semantic integrity under high compression ratios, a token-level iterative compression algorithm to better model the interdependence between compressed contents, and an instruction tuning based method for distribution alignment between language models.｜理由｜该文提出无需重训练的推理期提示压缩方法（LLMLingua）以加速模型推理，属于推理时优化技术，可作为子问题1的证据；摘要未报告延迟指标，故不支撑子问题2。 |
| 12 | 2023 | Deep Learning Workload Scheduling in GPU Datacenters: A Survey | GPU数据中心中的深度学习工作负载调度：综述 | `10.1145/3638757` | 122 | 引用了种子 | 2 | 建议不采纳 | 不采纳 |  | 该综述聚焦GPU数据中心的调度与资源利用，而非transformer推理加速技术或延迟-质量权衡，属于主题相邻（调度/资源管理层面）而非直接证据。 |
| 13 | 2023 | RepQ-ViT: Scale Reparameterization for Post-Training Quantization of V | RepQ-ViT：面向视觉Transformer训练后量化的尺度重参数化 | `10.1109/iccv51070.2023.01580` | 108 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 1 | 引文｜RepQ-ViT decouples the quantization and inference processes, where the former employs complex quantizers and the latter employs scale-reparameterized simplified quantizers.｜理由｜该文提出免重训练的PTQ框架，通过量化尺度重参数化在推理阶段使用简化的分层/log2量化器，属于推理时优化技术，可回答子问题1，但摘要未报告延迟数据，故不支撑子问题2。 |
| 14 | 2022 | Learned Token Pruning for Transformers | 面向Transformer的可学习词元剪枝 | `10.1145/3534678.3539260` | 107 | 引用了种子 | 2 | 建议采纳(子问题2) | 采纳 | 2 | 引文｜In particular, LTP achieves up to 2.1× FLOPs reduction with less than 1% accuracy drop, which results in up to 1.9× and 2.0× throughput improvement on Intel Haswell CPUs and NVIDIA V100 GPUs.｜理由｜该文报告了token剪枝带来的FLOPs/吞吐量提升与精度损失之间的量化权衡，可直接作为子问题2（延迟与质量权衡）的证据，但其阈值需在训练中学习，故不属于免重训练技术。 |
| 15 | 2024 | OWQ: Outlier-Aware Weight Quantization for Efficient Fine-Tuning and I | OWQ：面向大语言模型高效微调与推理的离群值感知权重量化 | `10.1609/aaai.v38i12.29237` | 70 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 1 | 引文｜OWQ prioritizes a small subset of structured weights sensitive to quantization, storing them in high-precision, while applying highly tuned quantization to the remaining dense weights.｜理由｜该文提出免重训练的权重低精度量化方法，属于可直接用于加速Transformer推理的推理期优化技术，可作为子问题1的证据。 |
| 16 | 2025 | A survey of model compression techniques: past, present, and future | 模型压缩技术综述：过去、现在与未来 | `10.3389/frobt.2025.1518965` | 69 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 1 | 引文｜To meet the urgent demand for efficient deployment, we delve into several compression methods-such as quantization, pruning, low-rank decomposition, and knowledge distillation-emphasizing their fundamental principles, recent advancements, and innovative strategies.｜理由｜该综述系统梳理了量化、剪枝等可在推理阶段加速部署的压缩技术，能为「使用了哪些推理时优化」这一子问题提供证据，但摘要未报告具体的延迟与质量权衡数据。 |
| 17 | 2024 | FIGNA: Integer Unit-Based Accelerator Design for FP-INT GEMM Preservin | FIGNA：用于保持数值精度的FP-INT GEMM的基于整数单元的加速器设计 | `10.1109/hpca57654.2024.00064` | 40 | 引用了种子 | 2 | 建议不采纳 | 不采纳 |  | 主题相邻：该文提出的是基于整数单元的硬件加速器设计（FP-INT GEMM 专用单元），属于硬件/体系结构层面的加速方案，而非可部署的推理时优化技术，也未报告推理延迟与质量的权衡数据。 |
| 18 | 2024 | Exploring Post-training Quantization in LLMs from Comprehensive Study  | 探索大型语言模型中的训练后量化：从全面研究到低秩补偿 | `10.1609/aaai.v38i17.29908` | 22 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 1 | 引文｜Post-training quantization (PTQ) has emerged as a promising technique for mitigating memory consumption and computational costs in large language models (LLMs).｜理由｜该文研究的是无需重训练的后训练量化（PTQ）等推理阶段优化方法，直接回答了子问题1所用的推理期优化技术；但摘要只报告了模型大小与精度的权衡，未涉及延迟数据，故不覆盖子问题2。 |
| 19 | 2022 | Generative Adversarial Networks | 生成对抗网络 | `10.1017/9781108891530.013` | 2579 | 被种子引用 | 1 | 建议不采纳 | 不采纳 |  | 这是一本深度学习教材的介绍，仅泛泛提及涵盖 Transformer 等架构，完全未涉及推理时优化技术或延迟与质量权衡，属于主题相邻而非可引用的证据。 |
| 20 | 2024 | AI and Memory Wall | AI与内存墙 | `10.1109/mm.2024.3373763` | 321 | 引用了种子 | 1 | 建议不采纳 | 不采纳 |  | 该摘要仅论证内存带宽是解码器 Transformer 服务的主要瓶颈并呼吁重新设计架构/训练/部署，未提出任何具体的推理时优化技术，也未报告延迟与质量的权衡数据，属于主题相邻（motivates but does not provide evidence）。 |
| 21 | 2024 | Lightweight Deep Learning for Resource-Constrained Environments: A Sur | 面向资源受限环境的轻量级深度学习：综述 | `10.1145/3657282` | 252 | 引用了种子 | 1 | 建议不采纳 | 不采纳 |  | 主题相邻：该综述泛论轻量模型设计与压缩/硬件加速，但未涉及 transformer 推理加速的具体技术，也未报告延迟与质量权衡，无法直接支撑任一子问题。 |
| 22 | 2023 | A Comprehensive Survey on Model Quantization for Deep Neural Networks  | 图像分类中深度神经网络的模型量化全面综述 | `10.1145/3623402` | 224 | 引用了种子 | 1 | 建议不采纳 | 不采纳 |  | 主题相邻：该综述聚焦DNN量化与图像分类，未涉及transformer架构或推理时优化/延迟权衡。 |
| 23 | 2024 | LLM-Based Edge Intelligence: A Comprehensive Survey on Architectures,  | 基于大语言模型的边缘智能：架构、应用、安全与可信性全面综述 | `10.1109/ojcoms.2024.3456549` | 184 | 引用了种子 | 1 | 建议不采纳 | 不采纳 |  | 主题相邻：摘要讨论LLM边缘智能架构、优化与安全，但未具体涉及推理时加速技术或延迟/质量权衡。 |
| 24 | 2023 | Tiny Machine Learning: Progress and Futures [Feature] | 微型机器学习：进展与未来 [专题] | `10.1109/mcas.2023.3302182` | 179 | 引用了种子 | 1 | 建议不采纳 | 不采纳 |  | 主题相邻：该文是TinyML/MCU端高效深度学习的综述，讨论模型压缩与系统协同设计，并未涉及transformer推理加速技术或相关延迟与质量权衡。 |
| 25 | 2025 | A Review on Edge Large Language Models: Design, Execution, and Applica | 边缘大语言模型综述：设计、执行与应用 | `10.1145/3719664` | 150 | 引用了种子 | 1 | 建议采纳(子问题1) | 采纳 | 1 | 引文｜This survey provides a comprehensive overview of recent advancements in edge LLMs, covering the entire lifecycle—from resource-efficient model design and pre-deployment strategies to runtime inference optimizations.｜理由｜摘要明确说明综述涵盖运行时推理优化，可作为子问题1关于推理时优化技术的证据，但未报告延迟与质量权衡。 |

## 摘要（判定用）

判据 3 要求确认摘要里存在可作为证据的完整句子，因此这里附上原文摘要。
机翻标题仅供快速定位，**判定必须依据英文原文**。

**1. Q-Diffusion: Quantizing Diffusion Models**

- DOI：`10.1109/iccv51070.2023.01608`
- 关联种子：`doi:10.1201/9781003162810-13`（引用了种子）

Diffusion models have achieved great success in image synthesis through iterative noise estimation using deep neural networks. However, the slow inference, high memory consumption, and computation intensity of the noise estimation model hinder the efficient adoption of diffusion models. Although post-training quantization (PTQ) is considered a go-to compression method for other tasks, it does not work out-of-the-box on diffusion models. We propose a novel PTQ method specifically tailored towards the unique multi-timestep pipeline and model architecture of the diffusion models, which compresses the noise estimation network to accelerate the generation process. We identify the key difficulty of diffusion model quantization as the changing output distributions of noise estimation networks over multiple time steps and the bimodal activation distribution of the shortcut layers within the noise estimation network. We tackle these challenges with timestep-aware calibration and split shortcut quantization in this work. Experimental results show that our proposed method is able to quantize full-precision unconditional diffusion models into 4-bit while maintaining comparable performance (small FID change of at most 2.34 compared to >100 for traditional PTQ) in a training-free manner. Our approach can also be applied to text-guided image generation, where we can run stable diffusion in 4-bit weights with high generation quality for the first time.

**2. I-ViT: Integer-only Quantization for Efficient Vision Transformer Inference**

- DOI：`10.1109/iccv51070.2023.01565`
- 关联种子：`doi:10.1201/9781003162810-13`（引用了种子）

Vision Transformers (ViTs) have achieved state-of-the-art performance on various computer vision applications. However, these models have considerable storage and computational overheads, making their deployment and efficient inference on edge devices challenging. Quantization is a promising approach to reducing model complexity, and the dyadic arithmetic pipeline can allow the quantized models to perform efficient integer-only inference. Unfortunately, dyadic arithmetic is based on the homogeneity condition in convolutional neural networks, which is not applicable to the non-linear components in ViTs, making integer-only inference of ViTs an open issue. In this paper, we propose I-ViT, an integer-only quantization scheme for ViTs, to enable ViTs to perform the entire computational graph of inference with integer arithmetic and bit-shifting, and without any floating-point arithmetic. In I-ViT, linear operations (e.g., MatMul and Dense) follow the integer-only pipeline with dyadic arithmetic, and non-linear operations (e.g., Softmax, GELU, and LayerNorm) are approximated by the proposed light-weight integer-only arithmetic methods. More specifically, I-ViT applies the proposed Shiftmax and ShiftGELU, which are designed to use integer bit-shifting to approximate the corresponding floating-point operations. We evaluate I-ViT on various benchmark models and the results show that integer-only INT8 quantization achieves comparable (or even slightly higher) accuracy to the full-precision (FP) baseline. Furthermore, we utilize TVM for practical hardware deployment on the GPU’s integer arithmetic units, achieving 3.72 ~ 4.11 inference speedup compared to the FP model. Code of both Pytorch and TVM is released at https://github.com/zkkli/I-ViT.

**3. Edge Intelligence: A Review of Deep Neural Network Inference in Resource-Limited Environments**

- DOI：`10.3390/electronics14122495`
- 关联种子：`doi:10.48550/arxiv.2211.10438`（引用了种子）

Deploying deep neural networks (DNNs) in resource-limited environments—such as smartwatches, IoT nodes, and intelligent sensors—poses significant challenges due to constraints in memory, computing power, and energy budgets. This paper presents a comprehensive review of recent advances in accelerating DNN inference on edge platforms, with a focus on model compression, compiler optimizations, and hardware–software co-design. We analyze the trade-offs between latency, energy, and accuracy across various techniques, highlighting practical deployment strategies on real-world devices. In particular, we categorize existing frameworks based on their architectural targets and adaptation mechanisms and discuss open challenges such as runtime adaptability and hardware-aware scheduling. This review aims to guide the development of efficient and scalable edge intelligence solutions.

**4. Fluctuation-Based Adaptive Structured Pruning for Large Language Models**

- DOI：`10.1609/aaai.v38i10.28960`
- 关联种子：`doi:10.48550/arxiv.2211.10438`（引用了种子）

Network Pruning is a promising way to address the huge computing resource demands of the deployment and inference of Large Language Models (LLMs). Retraining-free is important for LLMs' pruning methods. However, almost all of the existing retraining-free pruning approaches for LLMs focus on unstructured pruning, which requires specific hardware support for acceleration. In this paper, we propose a novel retraining-free structured pruning framework for LLMs, named FLAP (FLuctuation-based Adaptive Structured Pruning). It is hardware-friendly by effectively reducing storage and enhancing inference speed. For effective structured pruning of LLMs, we highlight three critical elements that demand the utmost attention: formulating structured importance metrics, adaptively searching the global compressed model, and implementing compensation mechanisms to mitigate performance loss. First, FLAP determines whether the output feature map is easily recoverable when a column of weight is removed, based on the fluctuation pruning metric. Then it standardizes the importance scores to adaptively determine the global compressed model structure. At last, FLAP adds additional bias terms to recover the output feature maps using the baseline values. We thoroughly evaluate our approach on a variety of language benchmarks. Without any retraining, our method significantly outperforms the state-of-the-art methods, including LLM-Pruner and the extension of Wanda in structured pruning. The code is released at https://github.com/CASIA-IVA-Lab/FLAP.

**5. Agile-Quant: Activation-Guided Quantization for Faster Inference of LLMs on the Edge**

- DOI：`10.1609/aaai.v38i17.29860`
- 关联种子：`doi:10.48550/arxiv.2211.10438`（引用了种子）

Large Language Models (LLMs) stand out for their impressive performance in intricate language modeling tasks. However, their demanding computational and memory needs pose obstacles for broad use on edge devices. Quantization is then introduced to boost LLMs' on-device efficiency. Recent works show that 8-bit or lower weight quantization is feasible with minimal impact on end-to-end task performance, while the activation is still not quantized. On the other hand, mainstream commodity edge devices still struggle to execute these sub-8-bit quantized networks effectively. In this paper, we propose Agile-Quant, an Activation-Guided quantization framework for faster Inference of popular Large Language Models (LLMs) on the Edge. Considering the hardware profiling and activation analysis, we first introduce a basic activation quantization strategy to balance the trade-off of task performance and real inference speed. Then we leverage the activation-aware token pruning technique to reduce the outliers and the adverse impact on attentivity. Ultimately, we utilize the SIMD-based 4-bit multiplier and our efficient TRIP matrix multiplication to implement the accelerator for LLMs on the edge. We apply our framework on different scales of LLMs including LLaMA, OPT, and BLOOM with 4-bit or 8-bit for the activation and 4-bit for the weight quantization. Experiments show that Agile-Quant achieves simultaneous quantization of model weights and activations while maintaining task performance comparable to existing weight-only quantization methods. Moreover, in the 8- and 4-bit scenario, Agile-Quant achieves an on-device speedup of up to 2.55x compared to its FP16 counterparts across multiple edge devices, marking a pioneering advancement in this domain.

**6. Efficient LLMs Training and Inference: An Introduction**

- DOI：`10.1109/access.2024.3501358`
- 关联种子：`doi:10.48550/arxiv.2211.10438`（引用了种子）

ChatGPT was released in late November 2022, making a significant impact globally. Following this release, numerous domestic and international open-source projects for large model training emerged, including Alpaca, BOOLM, LLaMA, ChatGLM, DeepSpeedChat, and ColossalChat. Both academia and industry have a growing need to train large models for optimizing downstream tasks. Research has demonstrated that instruction tuning using high-quality training data can enable models with over 10 billion parameters to exhibit emergent abilities, particularly in complex reasoning tasks. Training a model with tens of billions of parameters is often necessary to improve business metrics using large model technology. However, most research teams lack the extensive computing resources required for such large-scale models, often possessing only a few V100 (32G) GPUs and occasionally a few A100s. Consequently, training or inferring a large model of this magnitude is impractical under limited computational resources. Therefore, adopting optimization strategies during the training and inference stages is essential to address these challenges. This survey summarizes a series of optimization techniques for large models during the training and inference phases, enabling the training of large models even with constrained computational resources.

**7. One-Shot Sensitivity-Aware Mixed Sparsity Pruning for Large Language Models**

- DOI：`10.1109/icassp48485.2024.10445737`
- 关联种子：`doi:10.48550/arxiv.2211.10438`（引用了种子）

Various Large Language Models (LLMs) from the Generative Pretrained Transformer (GPT) family have achieved outstanding performances in a wide range of text generation tasks. However, the enormous model sizes have hindered their practical use in real-world applications due to high inference latency. Therefore, improving the efficiencies of LLMs through quantization, pruning, and other means has been a key issue in LLM studies. In this work, we propose a method based on Hessian sensitivity-aware mixed sparsity pruning to prune LLMs to at least 50% sparsity without the need of any retraining. It allocates sparsity adaptively based on sensitivity, allowing us to reduce pruning-induced error while maintaining the overall sparsity level. The advantages of the proposed method exhibit even more when the sparsity is extremely high. Furthermore, our method is compatible with quantization, enabling further compression of LLMs.

**8. 8-bit Transformer Inference and Fine-tuning for Edge Accelerators**

- DOI：`10.1145/3620666.3651368`
- 关联种子：`doi:10.48550/arxiv.2211.10438`（引用了种子）

Transformer models achieve state-of-the-art accuracy on natural language processing (NLP) and vision tasks, but demand significant computation and memory resources, which makes it difficult to perform inference and training (fine-tuning) on edge accelerators. Quantization to lower precision data types is a promising way to reduce computation and memory resources. Prior work has employed 8-bit integer (int8) quantization for Transformer inference, but int8 lacks the precision and range required for training. 8-bit floating-point (FP8) quantization has been used for Transformer training, but prior work only quantizes the inputs to matrix multiplications and leaves the rest of the operations in high precision.

**9. AWQ: Activation-aware Weight Quantization for On-Device LLM Compression and Acceleration**

- DOI：`10.1145/3714983.3714987`
- 关联种子：`doi:10.48550/arxiv.2211.10438`（引用了种子）

Large language models (LLMs) have transformed numerous AI applications. On-device LLM is becoming increasingly important: running LLMs locally on edge devices can reduce cloud computing costs and protect users' privacy. However, the astronomical model size and the limited hardware resources pose significant deployment challenges. To solve these issues, we propose Activation-aware Weight Quantization (AWQ) and TinyChat, an algorithm-system full-stack solution for efficient on-device LLM deployment. AWQ is a novel quantization method that identifies and protects salient weights based on activation distribution, significantly reducing model size while preserving performance. TinyChat, an optimized inference framework, translates AWQ's theoretical memory savings into practical speedups through techniques such as on-the-fly dequantization, SIMD-aware weight packing, and kernel fusion. Together, they enable 4x model size reduction and 3-4x acceleration across various edge platforms, from high-end desktop GPUs to resource-constrained IoT devices. This solution democratizes on-device LLM deployment, offering privacy-preserving, low-latency AI capabilities across a wide range of applications.

**10. Empowering Edge Intelligence: A Comprehensive Survey on On-Device AI Models**

- DOI：`10.1145/3724420`
- 关联种子：`doi:10.1201/9781003162810-13`（引用了种子）

The rapid advancement of artificial intelligence (AI) technologies has led to an increasing deployment of AI models on edge and terminal devices, driven by the proliferation of the Internet of Things (IoT) and the need for real-time data processing. This survey comprehensively explores the current state, technical challenges, and future trends of on-device AI models. We define on-device AI models as those designed to perform local data processing and inference, emphasizing their characteristics such as real-time performance, resource constraints, and enhanced data privacy. The survey is structured around key themes, including the fundamental concepts of AI models, application scenarios across various domains, and technical challenges faced in edge environments. We also discuss optimization and implementation strategies, such as data preprocessing, model compression, and hardware acceleration, which are essential for effective deployment. Furthermore, we examine the impact of emerging technologies, including edge computing and foundation models, on the evolution of on-device AI models. By providing a structured overview of the challenges, solutions, and future directions, this survey aims to facilitate further research and application of on-device AI, ultimately contributing to the advancement of intelligent systems in everyday life.

**11. LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models**

- DOI：`10.18653/v1/2023.emnlp-main.825`
- 关联种子：`doi:10.48550/arxiv.2211.10438`（引用了种子）

Large language models (LLMs) have been applied in various applications due to their astonishing capabilities.With advancements in technologies such as chain-of-thought (CoT) prompting and in-context learning (ICL), the prompts fed to LLMs are becoming increasingly lengthy, even exceeding tens of thousands of tokens.To accelerate model inference and reduce cost, this paper presents LLMLingua, a coarse-to-fine prompt compression method that involves a budget controller to maintain semantic integrity under high compression ratios, a token-level iterative compression algorithm to better model the interdependence between compressed contents, and an instruction tuning based method for distribution alignment between language models.We conduct experiments and analysis over four datasets from different scenarios, i.e., GSM8K, BBH, ShareGPT, and Arxiv-March23; showing that the proposed approach yields state-of-the-art performance and allows for up to 20x compression with little performance loss. 1

**12. Deep Learning Workload Scheduling in GPU Datacenters: A Survey**

- DOI：`10.1145/3638757`
- 关联种子：`doi:10.1201/9781003162810-13`（引用了种子）

Deep learning (DL) has demonstrated its remarkable success in a wide variety of fields. The development of a DL model is a time-consuming and resource-intensive procedure. Hence, dedicated GPU accelerators have been collectively constructed into a GPU datacenter. An efficient scheduler design for a GPU datacenter is crucially important to reduce operational cost and improve resource utilization. However, traditional approaches designed for big data or high-performance computing workloads can not support DL workloads to fully utilize the GPU resources. Recently, many schedulers are proposed to tailor for DL workloads in GPU datacenters. This article surveys existing research efforts for both training and inference workloads. We primarily present how existing schedulers facilitate the respective workloads from the scheduling objectives and resource utilization manner . Finally, we discuss several promising future research directions including emerging DL workloads, advanced scheduling decision making, and underlying hardware resources. A more detailed summary of the surveyed paper and code links can be found at our project website: https://github.com/S-Lab-System-Group/Awesome-DL-Scheduling-Papers

**13. RepQ-ViT: Scale Reparameterization for Post-Training Quantization of Vision Transformers**

- DOI：`10.1109/iccv51070.2023.01580`
- 关联种子：`doi:10.1201/9781003162810-13`（引用了种子）

Post-training quantization (PTQ), which only requires a tiny dataset for calibration without end-to-end retraining, is a light and practical model compression technique. Recently, several PTQ schemes for vision transformers (ViTs) have been presented; unfortunately, they typically suffer from non-trivial accuracy degradation, especially in low-bit cases. In this paper, we propose RepQ-ViT, a novel PTQ framework for ViTs based on quantization scale reparameterization, to address the above issues. RepQ-ViT decouples the quantization and inference processes, where the former employs complex quantizers and the latter employs scale-reparameterized simplified quantizers. This ensures both accurate quantization and efficient inference, which distinguishes it from existing approaches that sacrifice quantization performance to meet the target hardware. More specifically, we focus on two components with extreme distributions: post-LayerNorm activations with severe inter-channel variation and post-Softmax activations with power-law features, and initially apply channel-wise quantization and log$\sqrt 2 $ quantization, respectively. Then, we reparameterize the scales to hardware-friendly layer-wise quantization and log2 quantization for inference, with only slight accuracy or computational costs. Extensive experiments are conducted on multiple vision tasks with different model variants, proving that RepQ-ViT, without hyperparameters and expensive reconstruction procedures, can outperform existing strong baselines and encouragingly improve the accuracy of 4-bit PTQ of ViTs to a usable level. Code is available at https://github.com/zkkli/RepQ-ViT.

**14. Learned Token Pruning for Transformers**

- DOI：`10.1145/3534678.3539260`
- 关联种子：`doi:10.1201/9781003162810-13`（引用了种子）

Efficient deployment of transformer models in practice is challenging due to their inference cost including memory footprint, latency, and power consumption, which scales quadratically with input sequence length. To address this, we present a novel token reduction method dubbed Learned Token Pruning (LTP) which adaptively removes unimportant tokens as an input sequence passes through transformer layers. In particular, LTP prunes tokens with an attention score below a threshold, whose value is learned for each layer during training. Our threshold-based method allows the length of the pruned sequence to vary adaptively based on the input sequence, and avoids algorithmically expensive operations such as top-k token selection. We extensively test the performance of LTP on GLUE and SQuAD tasks and show that our method outperforms the prior state-of-the-art token pruning methods by up to ∽2.5% higher accuracy with the same amount of FLOPs. In particular, LTP achieves up to 2.1× FLOPs reduction with less than 1% accuracy drop, which results in up to 1.9× and 2.0× throughput improvement on Intel Haswell CPUs and NVIDIA V100 GPUs. Furthermore, we demonstrate that LTP is more robust than prior methods to variations in input sequence lengths. Our code has been developed in PyTorch and open-sourced

**15. OWQ: Outlier-Aware Weight Quantization for Efficient Fine-Tuning and Inference of Large Language Models**

- DOI：`10.1609/aaai.v38i12.29237`
- 关联种子：`doi:10.48550/arxiv.2211.10438`（引用了种子）

Large language models (LLMs) with hundreds of billions of parameters require powerful server-grade GPUs for inference, limiting their practical deployment. To address this challenge, we introduce the outlier-aware weight quantization (OWQ) method, which aims to minimize LLM's footprint through low-precision representation. OWQ prioritizes a small subset of structured weights sensitive to quantization, storing them in high-precision, while applying highly tuned quantization to the remaining dense weights. This sensitivity-aware mixed-precision scheme reduces the quantization error notably, and extensive experiments demonstrate that 3.1-bit models using OWQ perform comparably to 4-bit models optimized by OPTQ. Furthermore, OWQ incorporates a parameter-efficient fine-tuning for task-specific adaptation, called weak column tuning (WCT), enabling accurate task-specific LLM adaptation with minimal memory overhead in the optimized format. OWQ represents a notable advancement in the flexibility, efficiency, and practicality of LLM optimization literature. The source code is available at https://github.com/xvyaward/owq.

**16. A survey of model compression techniques: past, present, and future**

- DOI：`10.3389/frobt.2025.1518965`
- 关联种子：`doi:10.48550/arxiv.2211.10438`（引用了种子）

The exceptional performance of general-purpose large models has driven various industries to focus on developing domain-specific models. However, large models are not only time-consuming and labor-intensive during the training phase but also have very high hardware requirements during the inference phase, such as large memory and high computational power. These requirements pose considerable challenges for the practical deployment of large models. As these challenges intensify, model compression has become a vital research focus to address these limitations. This paper presents a comprehensive review of the evolution of model compression techniques, from their inception to future directions. To meet the urgent demand for efficient deployment, we delve into several compression methods-such as quantization, pruning, low-rank decomposition, and knowledge distillation-emphasizing their fundamental principles, recent advancements, and innovative strategies. By offering insights into the latest developments and their implications for practical applications, this review serves as a valuable technical resource for researchers and practitioners, providing a range of strategies for model deployment and laying the groundwork for future advancements in model compression.

**17. FIGNA: Integer Unit-Based Accelerator Design for FP-INT GEMM Preserving Numerical Accuracy**

- DOI：`10.1109/hpca57654.2024.00064`
- 关联种子：`doi:10.48550/arxiv.2211.10438`（引用了种子）

The weight-only quantization has emerged as a promising technique for alleviating the computational burden of large language models (LLMs) by employing low-precision integer (INT) weights, while retaining full-precision floating point (FP) activations to ensure inference quality. Despite the memory footprint reduction achieved through decreased bit-precision of weight parameters, the actual computing performance is often not improved significantly due to FP-INT multiply-accumulation (MAC) operations being performed on the floating point unit (FPU) after de quantizing the INT weight values to FP values, owing to the lack of dedicated FP- INT arithmetic units. In this study, we investigate the impact of introducing a dedicated FP-INT unit on overall performance and find that such specialization does not yield substantial improvements. As an alternative approach, we propose FIGNA, an accelerator based on INT units designed specifically for FP- INT MAC operations. A key feature of FIGNA is its ability to achieve the same numerical accuracy as the FPU while relying solely on the integer-unit, a departure from prior methods that relied on integer-units with numerical approximations for FP arithmetic results, albeit claiming similar inference accuracy through dedicated network training. Through comprehensive experiments on FP- INT quantized networks for LLMs, including OPT and BLOOM, we demonstrate the superior performance of FIGNA compared to conventional FPUs in terms of performance per area ($TOPS/mm^{2}$) and energy efficiency (TOPS/W) across various input and weight precision combinations. For instance, in the FP16-INT4 case, FIGNA shows 6.34x higher$TOPS/ mm^{2}$and 2.19x higher TOPS/W compared to the baseline.

**18. Exploring Post-training Quantization in LLMs from Comprehensive Study to Low Rank Compensation**

- DOI：`10.1609/aaai.v38i17.29908`
- 关联种子：`doi:10.48550/arxiv.2211.10438`（引用了种子）

Post-training quantization (PTQ) has emerged as a promising technique for mitigating memory consumption and computational costs in large language models (LLMs). However, a systematic examination of various quantization schemes, model families, and quantization bit precision has been absent from the literature. In this paper, we conduct a comprehensive analysis of these factors by investigating the effects of PTQ on weight-only, activation-only, and weight-and-activation quantization using diverse methods such as round-to-nearest (RTN), GPTQ, ZeroQuant, and their variants. We apply these methods to two distinct model families with parameters ranging from 125M to 176B. Our contributions include: (1) a sensitivity analysis revealing that activation quantization is generally more susceptible to weight quantization, with smaller models often outperforming larger models in terms of activation quantization; (2) an evaluation and comparison of existing PTQ methods to optimize model size reduction while minimizing the impact on accuracy, revealing that none of the current methods can achieve the original model quality for quantization with either INT4-weight or INT4-weight-and-INT8-activation; (3) based on these insights, we propose an optimized method called Low-Rank Compensation (LoRC), which employs low-rank matrices to enhance model quality recovery with a minimal increase in model size.

**19. Generative Adversarial Networks**

- DOI：`10.1017/9781108891530.013`
- 关联种子：`doi:10.1201/9781003162810-13`（被种子引用）

The Science of Deep Learning emerged from courses taught by the author that have provided thousands of students with training and experience for their academic studies, and prepared them for careers in deep learning, machine learning, and artificial intelligence in top companies in industry and academia. The book begins by covering the foundations of deep learning, followed by key deep learning architectures. Subsequent parts on generative models and reinforcement learning may be used as part of a deep learning course or as part of a course on each topic. The book includes state-of-the-art topics such as Transformers, graph neural networks, variational autoencoders, and deep reinforcement learning, with a broad range of applications. The appendices provide equations for computing gradients in backpropagation and optimization, and best practices in scientific writing and reviewing. The text presents an up-to-date guide to the field built upon clear visualizations using a unified notation and equations, lowering the barrier to entry for the reader. The accompanying website provides complementary code and hundreds of exercises with solutions.

**20. AI and Memory Wall**

- DOI：`10.1109/mm.2024.3373763`
- 关联种子：`doi:10.1201/9781003162810-13`（引用了种子）

The availability of unprecedented unsupervised training data, along with neural scaling laws, has resulted in an unprecedented surge in model size and compute requirements for serving/training LLMs. However, the main performance bottleneck is increasingly shifting to memory bandwidth. Over the past 20 years, peak server hardware FLOPS has been scaling at 3.0×/2yrs, outpacing the growth of DRAM and interconnect bandwidth, which have only scaled at 1.6 and 1.4 times every 2 years, respectively. This disparity has made memory, rather than compute, the primary bottleneck in AI applications, particularly in serving. Here, we analyze encoder and decoder Transformer models and show how memory bandwidth can become the dominant bottleneck for decoder models. We argue for a redesign in model architecture, training, and deployment strategies to overcome this memory limitation.

**21. Lightweight Deep Learning for Resource-Constrained Environments: A Survey**

- DOI：`10.1145/3657282`
- 关联种子：`doi:10.1201/9781003162810-13`（引用了种子）

Over the past decade, the dominance of deep learning has prevailed across various domains of artificial intelligence, including natural language processing, computer vision, and biomedical signal processing. While there have been remarkable improvements in model accuracy, deploying these models on lightweight devices, such as mobile phones and microcontrollers, is constrained by limited resources. In this survey, we provide comprehensive design guidance tailored for these devices, detailing the meticulous design of lightweight models, compression methods, and hardware acceleration strategies. The principal goal of this work is to explore methods and concepts for getting around hardware constraints without compromising the model’s accuracy. Additionally, we explore two notable paths for lightweight deep learning in the future: deployment techniques for TinyML and Large Language Models. Although these paths undoubtedly have potential, they also present significant challenges, encouraging research into unexplored areas.

**22. A Comprehensive Survey on Model Quantization for Deep Neural Networks in Image Classification**

- DOI：`10.1145/3623402`
- 关联种子：`doi:10.1201/9781003162810-13`（引用了种子）

Recent advancements in machine learning achieved by Deep Neural Networks (DNNs) have been significant. While demonstrating high accuracy, DNNs are associated with a huge number of parameters and computations, which leads to high memory usage and energy consumption. As a result, deploying DNNs on devices with constrained hardware resources poses significant challenges. To overcome this, various compression techniques have been widely employed to optimize DNN accelerators. A promising approach is quantization, in which the full-precision values are stored in low bit-width precision. Quantization not only reduces memory requirements but also replaces high-cost operations with low-cost ones. DNN quantization offers flexibility and efficiency in hardware design, making it a widely adopted technique in various methods. Since quantization has been extensively utilized in previous works, there is a need for an integrated report that provides an understanding, analysis, and comparison of different quantization approaches. Consequently, we present a comprehensive survey of quantization concepts and methods, with a focus on image classification. We describe clustering-based quantization methods and explore the use of a scale factor parameter for approximating full-precision values. Moreover, we thoroughly review the training of a quantized DNN, including the use of a straight-through estimator and quantization regularization. We explain the replacement of floating-point operations with low-cost bitwise operations in a quantized DNN and the sensitivity of different layers in quantization. Furthermore, we highlight the evaluation metrics for quantization methods and important benchmarks in the image classification task. We also present the accuracy of the state-of-the-art methods on CIFAR-10 and ImageNet. This article attempts to make the readers familiar with the basic and advanced concepts of quantization, introduce important works in DNN quantization, and highlight challenges for future research in this field.

**23. LLM-Based Edge Intelligence: A Comprehensive Survey on Architectures, Applications, Security and Trustworthiness**

- DOI：`10.1109/ojcoms.2024.3456549`
- 关联种子：`doi:10.1201/9781003162810-13`（引用了种子）

The integration of Large Language Models (LLMs) and Edge Intelligence (EI) introduces a groundbreaking paradigm for intelligent edge devices. With their capacity for human-like language processing and generation, LLMs empower edge computing with a powerful set of tools, paving the way for a new era of decentralized intelligence. Yet, a notable research gap exists in obtaining a thorough comprehension of LLM-based EI architectures, which should incorporate crucial elements such as security, optimization, and responsible development. This survey aims to bridge this gap by providing a comprehensive resource for both researchers and practitioners. We explore LLM-based EI architectures in-depth, carefully analyzing state-of-the-art paradigms and design decisions. To facilitate efficient and scalable edge deployments, we perform a comparative analysis of recent optimization and autonomy techniques specifically designed for resource-constrained edge environments. Additionally, we shed light on the extensive potential of LLM-based EI by demonstrating its varied practical applications across a wide range of domains. Acknowledging the utmost importance of security, our survey thoroughly investigates potential vulnerabilities inherent in LLM-based EI deployments. We explore corresponding defense mechanisms to protect the integrity and confidentiality of data processed at the edge. In conclusion, highlighting the essential aspect of trustworthiness, we outline best practices and guiding principles for the responsible development and deployment of these systems. By conducting a comprehensive review of these key components, our survey aims to support the ethical development and strategic implementation of LLM-driven EI, paving the way for its transformative impact on diverse applications.

**24. Tiny Machine Learning: Progress and Futures [Feature]**

- DOI：`10.1109/mcas.2023.3302182`
- 关联种子：`doi:10.48550/arxiv.2211.10438`（引用了种子）

Tiny machine learning (TinyML) is a new frontier of machine learning. By squeezing deep learning models into billions of IoT devices and microcontrollers (MCUs), we expand the scope of applications and enable ubiquitous intelligence. However, TinyML is challenging due to the hardware constraints: the tiny memory resource is difficult hold deep learning models designed for cloud and mobile platforms. There is also limited compiler and inference engine support for bare-metal devices. Therefore, we need to co-design the algorithm and system stack to enable TinyML. In this review, we will first discuss the definition, challenges, and applications of TinyML. We then survey the recent progress in TinyML and deep learning on MCUs. Next, we will introduce MCUNet, showing how we can achieve ImageNet-scale AI applications on IoT devices with system-algorithm co-design. We will further extend the solution from inference to training and introduce tiny on-device training techniques. Finally, we present future directions in this area. Today’s “large” model might be tomorrow’s “tiny” model. The scope of TinyML should evolve and adapt over time.

**25. A Review on Edge Large Language Models: Design, Execution, and Applications**

- DOI：`10.1145/3719664`
- 关联种子：`doi:10.48550/arxiv.2211.10438`（引用了种子）

Large language models (LLMs) have revolutionized natural language processing with their exceptional understanding, synthesizing, and reasoning capabilities. However, deploying LLMs on resource-constrained edge devices presents significant challenges due to computational limitations, memory constraints, and edge hardware heterogeneity. This survey provides a comprehensive overview of recent advancements in edge LLMs, covering the entire lifecycle—from resource-efficient model design and pre-deployment strategies to runtime inference optimizations. It also explores on-device applications across various domains. By synthesizing state-of-the-art techniques and identifying future research directions, this survey bridges the gap between the immense potential of LLMs and the constraints of edge computing.


## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | Codex（AI 审计，非独立人工复核） |
| 日期 | 2026-09-24 |
| 采纳的候选编号 | 2, 4, 5, 7, 8, 9, 11, 13, 14, 15, 16, 18, 25 |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |
| 审计方法 | 模型初审 + Codex 逐条复核 + 摘要逐字引文核验 + 标题去重 |
