# 金标候选：csai_009

**问题**：What techniques accelerate transformer inference without retraining?

  → 哪些技术可以在不重新训练的情况下加速 Transformer 推理？

**子问题**：

1. Which inference-time optimizations are used?
  → 使用了哪些推理时优化？

2. What latency and quality trade-offs are reported?
  → 报告了哪些延迟与质量之间的权衡？


**现有 gold**：2 篇 **年份范围**：(2022, 2026) **引用图候选**：25 篇

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
| 1 | 2023 | Q-Diffusion: Quantizing Diffusion Models | Q-Diffusion：扩散模型的量化 | `10.1109/iccv51070.2023.01608` | 135 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：研究扩散模型 PTQ 加速，非 Transformer 结构与推理优化。 |
| 2 | 2023 | I-ViT: Integer-only Quantization for Efficient Vision Transformer Infe | I-ViT：面向高效视觉Transformer推理的纯整数量化 | `10.1109/iccv51070.2023.01565` | 126 | 引用了种子 | 3 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 摘要提出 Shiftmax/ShiftGELU 等免重训练纯整数量化推理技术（子问题1），并报告了 INT8 保持全精度相当精度以及 3.72~4.11 倍推理加速（子问题2）。 |
| 3 | 2025 | Edge Intelligence: A Review of Deep Neural Network Inference in Resour | 边缘智能：资源受限环境下深度神经网络推理综述 | `10.3390/electronics14122495` | 80 | 引用了种子 | 3 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 综述系统梳理模型压缩与编译优化等推理技术（子问题1），并深入分析延迟、能耗与精度之间的权衡（子问题2）。 |
| 4 | 2024 | Fluctuation-Based Adaptive Structured Pruning for Large Language Model | 面向大语言模型的基于波动的自适应结构化剪枝 | `10.1609/aaai.v38i10.28960` | 43 | 引用了种子 | 3 | 建议采纳(子问题1) | 采纳 | 1 | 摘要明确提出免重训练（retraining-free）的 FLAP 结构化剪枝框架提升推理速度，但未在摘要中给出具体的延迟-质量权衡数值。 |
| 5 | 2024 | Agile-Quant: Activation-Guided Quantization for Faster Inference of LL | Agile-Quant：面向边缘端大语言模型加速推理的激活引导量化 | `10.1609/aaai.v38i17.29860` | 34 | 引用了种子 | 3 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 摘要提出激活引导量化与 token 剪枝等推理优化（子问题1），并报告了高达 2.55 倍加速且保持任务性能的权衡（子问题2）。 |
| 6 | 2024 | Efficient LLMs Training and Inference: An Introduction | 高效大语言模型的训练与推理：导论 | `10.1109/access.2024.3501358` | 27 | 引用了种子 | 3 | 建议采纳(子问题1) | 采纳 | 1 | 摘要概括总结了 LLM 在推理阶段的优化策略，可直接回答子问题1，但未明确包含延迟与质量权衡的数据。 |
| 7 | 2024 | One-Shot Sensitivity-Aware Mixed Sparsity Pruning for Large Language M | 面向大语言模型的一次性敏感度感知混合稀疏剪枝 | `10.1109/icassp48485.2024.10445737` | 26 | 引用了种子 | 3 | 建议采纳(子问题1) | 采纳 | 1 | 摘要提出无需重训练（without retraining）的一次性混合稀疏剪枝加速 LLM 推理，未报告具体的延迟-质量权衡指标。 |
| 8 | 2024 | 8-bit Transformer Inference and Fine-tuning for Edge Accelerators | 面向边缘加速器的8位Transformer推理与微调 | `10.1145/3620666.3651368` | 26 | 引用了种子 | 3 | 建议采纳(子问题1) | 采纳 | 1 | 摘要提出 8-bit 量化作为降低 Transformer 推理计算与显存的推理期优化方法，但未包含具体的延迟-质量权衡数据。 |
| 9 | 2025 | AWQ: Activation-aware Weight Quantization for On-Device LLM Compressio | AWQ：面向端侧大语言模型压缩与加速的激活感知权重量化 | `10.1145/3714983.3714987` | 223 | 引用了种子 | 2 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 摘要提出免重训练的 AWQ 激活感知量化及 TinyChat 算子融合/解量化推理优化（子问题1），并给出 3-4x 加速与无损性能的权衡（子问题2）。 |
| 10 | 2025 | Empowering Edge Intelligence: A Comprehensive Survey on On-Device AI M | 赋能边缘智能：端侧AI模型综合综述 | `10.1145/3724420` | 189 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：泛泛讨论端侧 AI 模型部署，摘要未针对 Transformer 推理优化或无重训练方案展开细节。 |
| 11 | 2023 | LLMLingua: Compressing Prompts for Accelerated Inference of Large Lang | LLMLingua：压缩提示以实现大语言模型的加速推理 | `10.18653/v1/2023.emnlp-main.825` | 137 | 引用了种子 | 2 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 摘要提出无需重训练模型的 Prompt 压缩推理加速技术（子问题1），并报告了高达 20 倍压缩比且几乎无损性能的权衡（子问题2）。 |
| 12 | 2023 | Deep Learning Workload Scheduling in GPU Datacenters: A Survey | GPU数据中心中的深度学习工作负载调度：综述 | `10.1145/3638757` | 122 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：关注 GPU 数据中心的工作负载调度，非 Transformer 模型自身的推理期优化技术或延迟-质量权衡。 |
| 13 | 2023 | RepQ-ViT: Scale Reparameterization for Post-Training Quantization of V | RepQ-ViT：面向视觉Transformer训练后量化的尺度重参数化 | `10.1109/iccv51070.2023.01580` | 108 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 1 | 摘要提出无需重训练的 PTQ 重参数化量化技术（子问题1），但摘要未明确报告推理延迟数据。 |
| 14 | 2022 | Learned Token Pruning for Transformers | 面向Transformer的可学习词元剪枝 | `10.1145/3534678.3539260` | 107 | 引用了种子 | 2 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 摘要提出基于阈值的 Token Pruning 推理剪枝技术（子问题1），并报告了 2.1x FLOPs 降低、1.9x~2.0x 吞吐量提升与<1% 精度损失的权衡（子问题2）。 |
| 15 | 2024 | OWQ: Outlier-Aware Weight Quantization for Efficient Fine-Tuning and I | OWQ：面向大语言模型高效微调与推理的离群值感知权重量化 | `10.1609/aaai.v38i12.29237` | 70 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 1 | 摘要提出离群值感知权重量化（OWQ）降低 Transformer 推理存储开销（子问题1），但摘要未包含延迟与质量权衡数据。 |
| 16 | 2025 | A survey of model compression techniques: past, present, and future | 模型压缩技术综述：过去、现在与未来 | `10.3389/frobt.2025.1518965` | 69 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 1 | 综述涵盖量化、剪枝、低秩分解等推理期模型压缩技术，解答子问题1，但摘要未包含具体的延迟-质量权衡数据。 |
| 17 | 2024 | FIGNA: Integer Unit-Based Accelerator Design for FP-INT GEMM Preserving | FIGNA：面向FP-INT GEMM的整数单元加速器设计，保持数值精度 | `10.1109/hpca57654.2024.00064` | 40 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 1 | 摘要提出基于整数单元的硬件加速器 FIGNA 实现免重训练的高效 FP-INT 矩阵乘法推理（子问题1），仅报告面积与能效，未直接报告延迟-质量权衡。 |
| 18 | 2024 | Exploring Post-training Quantization in LLMs from Comprehensive Study  | 探索大语言模型中的训练后量化：从综合研究到低秩补偿 | `10.1609/aaai.v38i17.29908` | 22 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 1 | 摘要研究免重训练的 PTQ 及 Low-Rank Compensation（LoRC）推理优化方法（子问题1），未明确报告延迟数据。 |
| 19 | 2022 | Generative Adversarial Networks | 生成对抗网络 | `10.1017/9781108891530.013` | 2579 | 被种子引用 | 1 | 建议不采纳 | 不采纳 | - | 主题相邻/不符合：深度学习与 GAN 教材，未针对 Transformer 推理加速技术进行讨论。 |
| 20 | 2024 | AI and Memory Wall | 人工智能与内存墙 | `10.1109/mm.2024.3373763` | 321 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | - | 主题相邻：探讨内存墙瓶颈并提出架构重设计方向，未包含具体免重训练推理加速技术或延迟权衡数据。 |
| 21 | 2024 | Lightweight Deep Learning for Resource-Constrained Environments: A Sur | 资源受限环境下的轻量级深度学习：综述 | `10.1145/3657282` | 252 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | - | 主题相邻：轻量级深度学习通用综述，缺乏针对 Transformer 免重训练推理加速的专项深入阐述或数据。 |
| 22 | 2023 | A Comprehensive Survey on Model Quantization for Deep Neural Networks  | 面向图像分类的深度神经网络模型量化综合综述 | `10.1145/3623402` | 224 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | - | 主题相邻：专注于图像分类 CNN 模型的量化与量化训练，未涉及 Transformer 无重训练推理加速。 |
| 23 | 2024 | LLM-Based Edge Intelligence: A Comprehensive Survey on Architectures,  | 基于大语言模型的边缘智能：架构、应用、安全与可信性综合综述 | `10.1109/ojcoms.2024.3456549` | 184 | 引用了种子 | 1 | 建议采纳(子问题1) | 采纳 | 1 | 综述对资源受限边缘环境下的 LLM 推理优化技术进行了比较分析，可支持子问题1，未详细给出延迟与质量权衡。 |
| 24 | 2023 | Tiny Machine Learning: Progress and Futures [Feature] | 微型机器学习：进展与未来 [专题] | `10.1109/mcas.2023.3302182` | 179 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | - | 主题相邻：关注 MCU 上的 TinyML 系统-算法协同设计，未涵盖 Transformer 免重训练推理加速。 |
| 25 | 2025 | A Review on Edge Large Language Models: Design, Execution, and Applica | 边缘大语言模型综述：设计、执行与应用 | `10.1145/3719664` | 150 | 引用了种子 | 1 | 建议采纳(子问题1) | 采纳 | 1 | 综述涵盖端侧 LLM 运行时的推理优化技术（runtime inference optimizations），解答子问题1，未包含延迟-质量权衡细节。 |

## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | Gemini |
| 日期 | 2026-09-24 |
| 采纳的候选编号 | #2, #3, #4, #5, #6, #7, #8, #9, #11, #13, #14, #15, #16, #17, #18, #23, #25 |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |