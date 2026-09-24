# 金标候选：csai_010

**问题**：What reproducibility practices are reported in machine learning benchmark papers?

  → 机器学习基准论文中报告了哪些可复现性实践？

**子问题**：

1. Which artifacts and metadata are shared?
  → 共享了哪些工件与元数据？

2. What barriers to reproducibility are reported?
  → 报告了哪些可复现性障碍？


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
| 1 | 2024 | Data leakage inflates prediction performance in connectome-based machi | 数据泄漏会虚高基于连接组的机器学习模型的预测性能 | `10.1038/s41467-024-46150-w` | 205 | 引用了种子 | 4 | 建议采纳(子问题2) | 采纳 | 2 | 摘要明确指出数据泄漏（如特征选择泄漏、重复受试者等）是破坏模型有效性与可复现性的普遍错误做法，直接解答了可复现性障碍（子问题2）。 |
| 2 | 2024 | Capturing end-to-end provenance for machine learning pipelines | 为机器学习流水线捕获端到端溯源信息 | `10.1016/j.is.2024.102495` | 22 | 引用了种子 | 4 | 建议不采纳 | 不采纳 | - | 主题相邻：关注机器学习流水线溯源工具（MLflow2PROV）的开发，未涉及基准论文中的可复现实践或障碍。 |
| 3 | 2023 | Metadata Representations for Queryable Repositories of Machine Learnin | 面向可查询机器学习模型仓库的元数据表示 | `10.1109/access.2023.3330647` | 8 | 引用了种子 | 4 | 建议不采纳 | 不采纳 | - | 主题相邻：提议统一的模型库元数据表示格式，非基准论文中实证报告的实践或障碍。 |
| 4 | 2024 | Avoiding common machine learning pitfalls | 避免常见的机器学习陷阱 | `10.1016/patter.2024.101046` | 125 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：为避免常见陷阱的教程指南，未对基准论文的共享工件或具体复现障碍提供实证证据。 |
| 5 | 2024 | Cracking the black box of deep sequence-based protein–protein interact | 破解基于深度序列的蛋白质-蛋白质相互作用预测黑箱 | `10.1093/bib/bbae076` | 93 | 引用了种子 | 3 | 建议采纳(子问题2) | 采纳 | 2 | 摘要揭示了随机划分导致数据泄漏、过度依赖序列相似性与节点度信息等导致性能高估的复现性与评估障碍（子问题2）。 |
| 6 | 2025 | Don’t push the button! Exploring data leakage risks in machine learnin | 别按那个按钮！探索机器学习与迁移学习中的数据泄漏风险 | `10.1007/s10462-025-11326-3` | 75 | 引用了种子 | 3 | 建议采纳(子问题2) | 采纳 | 2 | 摘要揭示了“一键式”机器学习导致的管道步骤遗漏、数据泄漏及过于乐观的性能评估障碍（子问题2）。 |
| 7 | 2025 | Reproducibility in machine‐learning‐based research: Overview, barriers | 基于机器学习的研究中的可复现性：概述、障碍与驱动因素 | `10.1002/aaai.70002` | 68 | 引用了种子 | 3 | 建议采纳(子问题2) | 采纳 | 2 | 摘要系统性提出了机器学习研究中的关键复现性障碍，包括缺乏透明度、数据/代码缺失、标准遵循差及训练条件敏感性（子问题2）。 |
| 8 | 2025 | Exploring the Intersection of Machine Learning and Big Data: A Survey | 探索机器学习与大数据的交叉：综述 | `10.3390/make7010013` | 51 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：大数据与机器学习结合的通用综述，未涉及基准论文的复现实践。 |
| 9 | 2024 | An Exploratory Study of Dataset and Model Management in Open Source Ma | 开源机器学习应用中数据集与模型管理的探索性研究 | `10.1145/3644815.3644963` | 6 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：关注开源应用中的数据集和模型文件存储与版本控制管理，非基准论文分析。 |
| 10 | 2023 | Integration of Open-Source Machine Learning Operations Tools into a Si | 将开源机器学习运维工具集成到单一框架中 | `10.1109/icccis60361.2023.10425558` | 4 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：基于 MLflow 的 MLOps 工具集成，非基准论文可复现性研究。 |
| 11 | 2024 | Collaboration Management for Federated Learning | 联邦学习中的协作管理 | `10.1109/icdew61823.2024.00043` | 4 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：联邦学习分布式协作与环境配置研究。 |
| 12 | 2024 | A Digital Twin System for Oil And Gas Industry: A Use Case on Mooring  | 面向油气行业的数字孪生系统：系泊缆完整性监测应用案例 | `10.1145/3652620.3688244` | 4 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：油气工业数字孪生应用，与可复现性无关。 |
| 13 | 2023 | Artificial Intelligence for Drug Discovery: Are We There Yet? | 人工智能用于药物发现：我们是否已抵达目标？ | `10.1146/annurev-pharmtox-040323-040828` | 227 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：AI 在药物研发中的应用综述，仅泛泛提及可重复性危机。 |
| 14 | 2024 | Simple Behavioral Analysis (SimBA) as a platform for explainable machi | 简单行为分析（SimBA）：行为神经科学中可解释机器学习的平台 | `10.1038/s41593-024-01649-9` | 210 | 引用了种子 | 2 | 无法判断 | 不采纳 | - | 缺少摘要，且为特定领域软件平台介绍，非基准论文可复现性分析。 |
| 15 | 2025 | Machine‐Learning‐Aided Advanced Electrochemical Biosensors | 机器学习辅助的先进电化学生物传感器 | `10.1002/adma.202417520` | 145 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：电化学生物传感器领域的 ML 应用综述。 |
| 16 | 2024 | Guiding questions to avoid data leakage in biological machine learning | 避免生物机器学习应用中数据泄漏的指导性问题 | `10.1038/s41592-024-02362-y` | 137 | 引用了种子 | 2 | 无法判断 | 不采纳 | - | 源站无摘要，属于避免数据泄漏的提示建议，非基准论文实证数据。 |
| 17 | 2025 | A multimodal whole-slide foundation model for pathology | 面向病理学的多模态全切片基础模型 | `10.1038/s41591-025-03982-3` | 137 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 领域特定基础模型（TITAN）的具体提出论文，不解答基准论文可复现实践。 |
| 18 | 2024 | A review of model evaluation metrics for machine learning in genetics  | 遗传学与基因组学中机器学习的模型评估指标综述 | `10.3389/fbinf.2024.1457619` | 123 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：基因组学 ML 评估指标（如分类/回归指标）综述。 |
| 19 | 2022 | Systematic review of the radiomics quality score applications: an EuSo | 影像组学质量评分应用的系统综述：EuSoMII影像组学审计组倡议 | `10.1007/s00330-022-09187-3` | 120 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：医学影像组学（Radiomics）质量评分系统综述，非机器学习通用基准论文研究。 |
| 20 | 2024 | REFORMS: Consensus-based Recommendations for Machine-learning-based Sc | REFORMS：基于机器学习的科学研究的共识性建议 | `10.1126/sciadv.adk3452` | 117 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：提出了可复现性与规范报告的 CheckList（REFORMS 框架），非对既有基准论文实践的实证调查。 |
| 21 | 2024 | Recent methodological advances in federated learning for healthcare | 面向医疗的联邦学习近期方法学进展 | `10.1016/j.patter.2024.101006` | 116 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：医疗联邦学习方法学综述。 |
| 22 | 2024 | Weak baselines and reporting biases lead to overoptimism in machine le | 弱基线与报告偏倚导致流体相关偏微分方程机器学习过度乐观 | `10.1038/s42256-024-00897-5` | 102 | 引用了种子 | 2 | 无法判断 | 不采纳 | - | 源站无完整摘要，属于特定物理 PDE 场景下的比较性分析。 |
| 23 | 2025 | Data splitting to avoid information leakage with DataSAIL | 使用 DataSAIL 进行数据划分以避免信息泄漏 | `10.1038/s41467-025-58606-8` | 89 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 具体的算法/工具（DataSAIL）开发，非对基准论文实践的分析。 |
| 24 | 2024 | Toward Improving Breast Cancer Classification Using an Adaptive Voting | 基于自适应投票集成学习算法改进乳腺癌分类 | `10.1109/access.2024.3356602` | 78 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 乳腺癌分类具体应用论文，无关。 |
| 25 | 2024 | Lung Sound Classification With Multi-Feature Integration Utilizing Lig | 利用轻量级 CNN 模型进行多特征融合的肺音分类 | `10.1109/access.2024.3361943` | 75 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 肺音分类具体应用论文，无关。 |

## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | Gemini |
| 日期 | 2026-09-24 |
| 采纳的候选编号 | #1, #5, #6, #7 |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |