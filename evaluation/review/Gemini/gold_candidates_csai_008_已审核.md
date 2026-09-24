# 金标候选：csai_008

**问题**：How do parameter-efficient fine-tuning methods reduce training memory?

  → 参数高效微调方法如何减少训练内存？

**子问题**：

1. Which parameter subsets are updated?
  → 哪些参数子集会被更新？

2. What memory and quality trade-offs are reported?
  → 报告了哪些内存与质量之间的权衡？


**现有 gold**：3 篇 **年份范围**：(2022, 2026) **引用图候选**：25 篇

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
| 1 | 2024 | Democratizing protein language models with parameter-efficient fine-tu | 通过参数高效微调普及蛋白质语言模型 | `10.1073/pnas.2405840121` | 88 | 引用了种子 | 7 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 摘要明确指出更新参数子集为 LoRA 和仅分类头（子问题1），同时报告了与全量微调相比内存降低、参数极大减少且性能相当（子问题2）。 |
| 2 | 2023 | FacT: Factor-Tuning for Lightweight Adaptation on Vision Transformer | FacT：用于视觉Transformer轻量级适配的因子微调 | `10.1609/aaai.v37i1.25187` | 98 | 引用了种子 | 6 | 建议采纳(子问题1) | 采纳 | 1 | 摘要指出了更新的参数子集（将权重增量张量分解后的轻量因子 factors），但仅讨论了参数量与性能权衡，未直接报告训练显存/内存权衡。 |
| 3 | 2024 | Fine-tuning protein language models boosts predictions across diverse  | 微调蛋白质语言模型提升跨多种任务的预测性能 | `10.1038/s41467-024-51844-2` | 218 | 引用了种子 | 5 | 建议不采纳 | 不采纳 | - | 主题相邻：摘要提及 PEFT 节省资源和训练加速，但未阐明更新哪些参数子集，也未具体报告显存/内存权衡指标。 |
| 4 | 2025 | Parameter-efficient fine-tuning in large language models: a survey of  | 大语言模型中的参数高效微调：方法综述 | `10.1007/s10462-025-11236-4` | 152 | 引用了种子 | 5 | 建议采纳(子问题1) | 采纳 | 1 | 综述摘要提及介绍多种 PEFT 算法的核心原理与参数调整方式，可作为解释“更新哪些参数子集”的概括性证据，未具体报告内存-质量权衡。 |
| 5 | 2023 | On the Effectiveness of Parameter-Efficient Fine-Tuning | 论参数高效微调的有效性 | `10.1609/aaai.v37i11.26505` | 139 | 引用了种子 | 5 | 建议采纳(子问题1) | 采纳 | 1 | 论文探讨如何选择可调参数子集（随机、规则、投影及 SAM 算法），直接回答子问题 1，但摘要未包含训练显存/内存与质量权衡的数据。 |
| 6 | 2022 | SPoT: Better Frozen Model Adaptation through Soft Prompt Transfer | SPoT：通过软提示迁移实现更好的冻结模型适配 | `10.18653/v1/2022.acl-long.346` | 178 | 被种子引用 | 4 | 建议采纳(子问题1) | 采纳 | 1 | 摘要明确指出保持模型冻结，仅学习和更新任务特定的软提示（soft prompt）参数，但仅报告参数量与性能对比，未涉及内存权衡。 |
| 7 | 2022 | Cutting Down on Prompts and Parameters: Simple Few-Shot Learning with  | 减少提示与参数：使用语言模型的简单小样本学习 | `10.18653/v1/2022.findings-acl.222` | 129 | 引用了种子 | 4 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 摘要明确提出仅微调 bias 项（更新子集，子问题1），并报告仅更新 0.1% 参数量下可减少内存开销且取得相当或更好效果（子问题2）。 |
| 8 | 2024 | Boosting Continual Learning of Vision-Language Models via Mixture-of-E | 通过专家混合适配器提升视觉-语言模型的持续学习 | `10.1109/cvpr52733.2024.02191` | 122 | 引用了种子 | 4 | 建议采纳(子问题1) | 采纳 | 1 | 摘要明确通过扩展 MoE 适配器进行微调，仅更新新增适配器参数而非全模型，可作为参数子集更新的证据。 |
| 9 | 2024 | A survey on LoRA of large language models | 大语言模型LoRA综述 | `10.1007/s11704-024-40663-9` | 120 | 引用了种子 | 4 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 综述摘要明确说明 LoRA 更新低秩矩阵参数子集（子问题1），并涵盖计算效率提升与下游任务性能权衡的讨论（子问题2）。 |
| 10 | 2023 | A Unified Continual Learning Framework with General Parameter-Efficien | 基于通用参数高效微调的统一持续学习框架 | `10.1109/iccv51070.2023.01055` | 93 | 引用了种子 | 4 | 建议不采纳 | 不采纳 | - | 主题相邻：聚焦持续学习框架 LAE，虽然提及 Adapter/LoRA/Prefix，但未深入分析更新子集细节或内存-质量权衡。 |
| 11 | 2023 | Towards Adaptive Prefix Tuning for Parameter-Efficient Language Model  | 面向自适应前缀调优的参数高效语言模型微调 | `10.18653/v1/2023.acl-short.107` | 91 | 引用了种子 | 4 | 建议采纳(子问题1) | 采纳 | 1 | 摘要明确指出 prefix tuning 仅优化插入 Transformer 层的连续前缀向量（伪 token），详细回答了更新的具体参数子集。 |
| 12 | 2023 | FedPETuning: When Federated Learning Meets the Parameter-Efficient Tun | FedPETuning：当联邦学习遇上预训练语言模型的参数高效调优方法 | `10.18653/v1/2023.findings-acl.632` | 89 | 引用了种子 | 4 | 建议采纳(子问题2) | 采纳 | 2 | 摘要在联邦学习背景下开展资源受限分析，报告了大幅降低重度资源消耗并保持可接受性能的权衡证据（子问题2）。 |
| 13 | 2024 | When MOE Meets LLMs: Parameter Efficient Fine-tuning for Multi-task Me | 当混合专家模型遇上大语言模型：面向多任务医疗应用的参数高效微调 | `10.1145/3626772.3657722` | 88 | 引用了种子 | 4 | 建议采纳(子问题1) | 采纳 | 1 | 摘要指出了可训练参数子集由低秩矩阵专家与门控机制构成，解答了哪些参数子集被更新的问题。 |
| 14 | 2024 | Enhancing efficiency of protein language models with minimal wet-lab d | 通过少样本学习以最少湿实验数据提升蛋白质语言模型的效率 | `10.1038/s41467-024-49798-6` | 84 | 引用了种子 | 4 | 建议不采纳 | 不采纳 | - | 主题相邻：该文侧重湿实验与少样本策略，仅笼统提及 PEFT，未涉及更新参数子集细节及训练内存权衡。 |
| 15 | 2023 | All in One: Multi-Task Prompting for Graph Neural Networks | 多合一：面向图神经网络的多任务提示 | `10.1145/3580305.3599256` | 175 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：讨论图神经网络的 prompt 学习与元学习初始化，未说明更新参数子集及训练内存权衡。 |
| 16 | 2022 | No more fine-tuning? an experimental evaluation of prompt tuning in co | 不再需要微调？代码智能中提示调优的实验评估 | `10.1145/3540250.3549113` | 150 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：评估代码任务中的 prompt tuning，未提供具体的参数子集更新说明或训练显存/内存权衡数据。 |
| 17 | 2023 | ViTPose++: Vision Transformer for Generic Body Pose Estimation | ViTPose++：用于通用人体姿态估计的视觉Transformer | `10.1109/tpami.2023.3330016` | 147 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：聚焦姿态估计的 ViT 结构，仅笼统提及微调策略，未涉及 PEFT 参数子集或内存权衡。 |
| 18 | 2023 | Enhancing Chat Language Models by Scaling High-quality Instructional C | 通过扩展高质量指令对话增强聊天语言模型 | `10.18653/v1/2023.emnlp-main.183` | 123 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：侧重于 UltraChat 对话数据集构造与指令微调效果，未讨论 PEFT 方法或训练内存权衡。 |
| 19 | 2023 | Fill in the Blank: Context-aware Automated Text Input Generation for M | 填空：面向移动GUI测试的上下文感知自动文本输入生成 | `10.1109/icse48619.2023.00119` | 121 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：利用 LLM 辅助移动 GUI 测试，未深入分析 PEFT 更新参数子集或训练显存权衡。 |
| 20 | 2023 | Baize: An Open-Source Chat Model with Parameter-Efficient Tuning on Se | Baize：基于自聊天数据进行参数高效调优的开源聊天模型 | `10.18653/v1/2023.emnlp-main.385` | 119 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：仅提及对 LLaMA 应用 PEFT，未阐述更新的具体参数子集，亦未报告内存与质量权衡。 |
| 21 | 2024 | SDSTrack: Self-Distillation Symmetric Adapter Learning for Multi-Modal | SDSTrack：用于多模态视觉目标跟踪的自蒸馏对称适配器学习 | `10.1109/cvpr52733.2024.02507` | 114 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：多模态跟踪的 adapter 应用，未具体阐述更新参数子集的机制或训练内存-性能权衡。 |
| 22 | 2024 | From Large Language Models to Large Multimodal Models: A Literature Re | 从大语言模型到大型多模态模型：文献综述 | `10.3390/app14125068` | 101 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：宏观综述，未针对 PEFT 的参数更新子集或训练显存/内存权衡给出具体证据。 |
| 23 | 2024 | Stronger, Fewer, & Superior: Harnessing Vision Foundation Models for D | 更强、更少、更优：利用视觉基础模型实现域泛化语义分割 | `10.1109/cvpr52733.2024.02704` | 100 | 引用了种子 | 3 | 建议采纳(子问题1) | 采纳 | 1 | 摘要明确说明了更新的参数子集（冻结主干中新增的 trainable tokens，仅占 1% 参数），支持子问题 1。 |
| 24 | 2024 | Deep learning for rice leaf disease detection: A systematic literature | 面向水稻叶片病害检测的深度学习：新兴趋势、方法与技术的系统文献综述 | `10.1016/j.inpa.2024.04.006` | 92 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 领域不符/主题相邻：水稻病害检测深度学习综述，未涉及 PEFT 参数子集或内存权衡。 |
| 25 | 2025 | A foundation model for generalizable cancer diagnosis and survival pre | 用于从组织病理学图像中进行可泛化癌症诊断和生存预测的基础模型 | `10.1038/s41467-025-57587-y` | 83 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：病理图像自监督基础模型，仅笼统提及适配，不包含 PEFT 参数子集或内存权衡证据。 |

## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | Gemini |
| 日期 | 2026-09-24 |
| 采纳的候选编号 | #1, #2, #4, #5, #6, #7, #8, #9, #11, #12, #13, #23 |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |