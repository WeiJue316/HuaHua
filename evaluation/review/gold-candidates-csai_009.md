# 金标候选：csai_009

**问题**：What techniques accelerate transformer inference without retraining?

**子问题**：

1. Which inference-time optimizations are used?
2. What latency and quality trade-offs are reported?

**现有 gold**：2 篇　**年份范围**：(2022, 2026)　**引用图候选**：25 篇

## 判定标准

一篇论文算作 gold，当且仅当**领域专家会把它作为回答某个子问题的证据引用**。
按子问题分别判定，因为证据是按子问题分配的。

逐条检查：

1. 论文是否真正回答某个子问题（不是主题相邻）
2. 年份是否在声明范围内
3. 摘要是否包含可以作为证据的完整句子
4. 判定它支撑哪个子问题（填编号）

## 候选清单

| # | 年份 | 标题 | DOI | 被引 | 与种子的关系 | 主题命中 | 判定 | 子问题 |
|---:|---:|---|---|---:|---|---:|---|---:|
| 1 | 2023 | Q-Diffusion: Quantizing Diffusion Models | `10.1109/iccv51070.2023.01608` | 135 | 引用了种子 | 3 | | |
| 2 | 2023 | I-ViT: Integer-only Quantization for Efficient Vision Transformer Infe | `10.1109/iccv51070.2023.01565` | 126 | 引用了种子 | 3 | | |
| 3 | 2025 | Edge Intelligence: A Review of Deep Neural Network Inference in Resour | `10.3390/electronics14122495` | 80 | 引用了种子 | 3 | | |
| 4 | 2024 | Fluctuation-Based Adaptive Structured Pruning for Large Language Model | `10.1609/aaai.v38i10.28960` | 43 | 引用了种子 | 3 | | |
| 5 | 2024 | Agile-Quant: Activation-Guided Quantization for Faster Inference of LL | `10.1609/aaai.v38i17.29860` | 34 | 引用了种子 | 3 | | |
| 6 | 2024 | Efficient LLMs Training and Inference: An Introduction | `10.1109/access.2024.3501358` | 27 | 引用了种子 | 3 | | |
| 7 | 2024 | One-Shot Sensitivity-Aware Mixed Sparsity Pruning for Large Language M | `10.1109/icassp48485.2024.10445737` | 26 | 引用了种子 | 3 | | |
| 8 | 2024 | 8-bit Transformer Inference and Fine-tuning for Edge Accelerators | `10.1145/3620666.3651368` | 26 | 引用了种子 | 3 | | |
| 9 | 2025 | AWQ: Activation-aware Weight Quantization for On-Device LLM Compressio | `10.1145/3714983.3714987` | 223 | 引用了种子 | 2 | | |
| 10 | 2025 | Empowering Edge Intelligence: A Comprehensive Survey on On-Device AI M | `10.1145/3724420` | 189 | 引用了种子 | 2 | | |
| 11 | 2023 | LLMLingua: Compressing Prompts for Accelerated Inference of Large Lang | `10.18653/v1/2023.emnlp-main.825` | 137 | 引用了种子 | 2 | | |
| 12 | 2023 | Deep Learning Workload Scheduling in GPU Datacenters: A Survey | `10.1145/3638757` | 122 | 引用了种子 | 2 | | |
| 13 | 2023 | RepQ-ViT: Scale Reparameterization for Post-Training Quantization of V | `10.1109/iccv51070.2023.01580` | 108 | 引用了种子 | 2 | | |
| 14 | 2022 | Learned Token Pruning for Transformers | `10.1145/3534678.3539260` | 107 | 引用了种子 | 2 | | |
| 15 | 2024 | OWQ: Outlier-Aware Weight Quantization for Efficient Fine-Tuning and I | `10.1609/aaai.v38i12.29237` | 70 | 引用了种子 | 2 | | |
| 16 | 2025 | A survey of model compression techniques: past, present, and future | `10.3389/frobt.2025.1518965` | 69 | 引用了种子 | 2 | | |
| 17 | 2024 | FIGNA: Integer Unit-Based Accelerator Design for FP-INT GEMM Preservin | `10.1109/hpca57654.2024.00064` | 40 | 引用了种子 | 2 | | |
| 18 | 2024 | Exploring Post-training Quantization in LLMs from Comprehensive Study  | `10.1609/aaai.v38i17.29908` | 22 | 引用了种子 | 2 | | |
| 19 | 2022 | Generative Adversarial Networks | `10.1017/9781108891530.013` | 2579 | 被种子引用 | 1 | | |
| 20 | 2024 | AI and Memory Wall | `10.1109/mm.2024.3373763` | 321 | 引用了种子 | 1 | | |
| 21 | 2024 | Lightweight Deep Learning for Resource-Constrained Environments: A Sur | `10.1145/3657282` | 252 | 引用了种子 | 1 | | |
| 22 | 2023 | A Comprehensive Survey on Model Quantization for Deep Neural Networks  | `10.1145/3623402` | 224 | 引用了种子 | 1 | | |
| 23 | 2024 | LLM-Based Edge Intelligence: A Comprehensive Survey on Architectures,  | `10.1109/ojcoms.2024.3456549` | 184 | 引用了种子 | 1 | | |
| 24 | 2023 | Tiny Machine Learning: Progress and Futures [Feature] | `10.1109/mcas.2023.3302182` | 179 | 引用了种子 | 1 | | |
| 25 | 2025 | A Review on Edge Large Language Models: Design, Execution, and Applica | `10.1145/3719664` | 150 | 引用了种子 | 1 | | |

## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | |
| 日期 | |
| 采纳的候选编号 | |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |
