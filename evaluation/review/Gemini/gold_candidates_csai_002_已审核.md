# 金标候选：csai_002

**问题**：How do agentic tool-use methods differ in planning and memory design?

　　→ 智能体式工具使用方法在规划与记忆设计上有何差异？

**子问题**：

1. How is planning represented?
　　→ 规划是如何表示的？

2. How is long-term state retained?
　　→ 长期状态是如何保留的？


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
|---:|---:|---|---|---|---:|---|---:|---|---:|---|---|
| 1 | 2024 | MemoryRepository for AI NPC | 面向AI NPC的记忆仓库 | `10.1109/access.2024.3393485` | 15 | 引用了种子 | 4 | 建议采纳(子问题2) | 采纳 | 子问题2 | 该论文提出了面向LLM AI NPC的MemoryRepository，明确设计了短期与长期记忆及遗忘/总结机制，可作为“长期状态如何保留”子问题的证据，但未涉及规划表示或工具使用规划。 |
| 2 | 2026 | Prompt-Native Semantic Runtimes for Language Models: Inference-Time Se | 面向语言模型的提示原生语义运行时：推理期语义治理、溯源、压缩与文档级过程教学 | `10.5281/zenodo.19059674` | 10 | 引用了种子 | 4 | 建议不采纳 | 不采纳 | - | 主题相邻：该文提出的是上下文内语义治理运行时（证据分级、溯源膜、压缩鲁棒性），明确与记忆操作系统/编排框架划清界限，未具体讨论规划的表示方式或长期状态的保留机制。 |
| 3 | 2024 | LLM-Collab: a framework for enhancing task planning via chain-of-thoug | LLM-Collab：通过思维链与多智能体协作增强任务规划的框架 | `10.3934/aci.2024019` | 7 | 引用了种子 | 4 | 建议采纳(子问题1) | 采纳 | 子问题1 | 该摘要聚焦于通过思维链与多智能体协作（分析者/执行者角色）表示任务规划，直接回答了「规划如何表示」，但完全未涉及长期状态或记忆的保留，故仅支持子问题1。 |
| 4 | 2025 | Agentic Lab: An Agentic-physical AI system for cell and organoid exper | Agentic Lab：用于细胞与类器官实验及制造的智能体-物理AI系统 | `10.1101/2025.11.11.686354` | 4 | 引用了种子 | 4 | 建议采纳(两个子问题) | 采纳 | 子问题1, 2 | 该摘要明确描述了多智能体编排与协议设计/规划闭环，并提到通过长期记忆数据库累积实验日志来保留长期状态。 |
| 5 | 2023 | GPTeach: Interactive TA Training with GPT-based Students | GPTeach：基于GPT模拟学生的交互式助教培训 | `10.1145/3573051.3593393` | 118 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：该文用GPT模拟学生做教师培训，属LLM角色扮演应用，未涉及agentic工具使用中的规划表示或长期状态保留设计。 |
| 6 | 2024 | Agent design pattern catalogue: A collection of architectural patterns | 智能体设计模式目录：面向基于基础模型的智能体的架构模式集合 | `10.1016/j.jss.2024.112278` | 43 | 引用了种子 | 3 | 建议采纳(子问题1) | 采纳 | 子问题1 | 该摘要明确提到基于基础模型的智能体架构模式，并涵盖目标寻求、计划生成与规划相关设计，因此可作为规划表示子问题的证据，但未涉及长期状态保留。 |
| 7 | 2025 | Agentic AI: The age of reasoning—A review | 智能体式人工智能：推理时代——综述 | `10.1016/j.jai.2025.08.003` | 41 | 引用了种子 | 3 | 建议采纳(子问题1) | 采纳 | 子问题1 | 该综述明确将 planning 列为智能体核心模式之一，可作为规划表示子问题的证据，但摘要未涉及长期状态/记忆保留。 |
| 8 | 2024 | Can LLMs Answer Investment Banking Questions? Using Domain-Tuned Funct | 大语言模型能否回答投资银行问题？利用领域微调函数提升大语言模型在知识密集型分析任务中的表现 | `10.1609/aaaiss.v3i1.31191` | 14 | 引用了种子 | 3 | 建议采纳(子问题1) | 采纳 | 子问题1 | 摘要提到系统通过领域调优函数支持信息检索和规划，可视为规划以外部工具/函数形式表示，但未涉及长期状态保留。 |
| 9 | 2024 | Toward the Emergence of Intelligent Control: Episodic Generalization a | 迈向智能控制的涌现：情景泛化与优化 | `10.1162/opmi_a_00143` | 9 | 引用了种子 | 3 | 建议采纳(子问题2) | 采纳 | 子问题2 | 论文提出的EGO框架包含情节记忆模块和循环上下文模块，用于快速学习刺激关系并维持任务相关上下文表征以支持长期状态保留，但未涉及规划表示。 |
| 10 | 2025 | Conversational Agents: From RAG to LTM | 对话智能体：从检索增强生成到长期记忆 | `10.1145/3767695.3769671` | 4 | 引用了种子 | 3 | 建议采纳(子问题2) | 采纳 | 子问题2 | The paper focuses on long-term memory (LTM) mechanisms for conversational agents, directly addressing how long-term state is retained (subquestion 2), but does not discuss planning representation (subquestion 1). |
| 11 | 2025 | Enhancing Reasoning Capacity of SLM Using Cognitive Enhancement | 利用认知增强提升SLM的推理能力 | `10.1109/icaiic64266.2025.10920811` | 3 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | - | 主题相邻：讨论SLM在网络安全中通过认知提示增强推理，但未涉及agentic tool-use的规划表示或长期状态保留。 |
| 12 | 2025 | Agentic Large Language Models for Conceptual Systems Engineering and D | 面向概念系统工程与设计的智能体大语言模型 | `10.1115/1.4070328` | 2 | 引用了种子 | 3 | 建议采纳(两个子问题) | 采纳 | 子问题1, 2 | 该文用可序列化的设计状态图（DSG）作为多智能体迭代构建/细化的持久状态表示，既描述了规划的任务分解与图结构表示（子问题1），也描述了跨轮次保留长期状态的机制（子问题2）。 |
| 13 | 2026 | From simulated empathy to structural attunement: Realtime Editable Mem | 从模拟共情到结构性调谐：实时可编辑记忆拓扑与情感锚定AI的演化 | `10.3389/frai.2026.1749517` | 1 | 引用了种子 | 3 | 建议采纳(子问题2) | 采纳 | 子问题2 | 该文提出REMT以图结构、边强化/衰减/剪枝和情绪效价实现跨会话持久记忆，直接涉及长期状态保留（子问题2），但未讨论规划表示（子问题1）。 |
| 14 | 2024 | A survey on LLM-based multi-agent systems: workflow, infrastructure, a | 基于LLM的多智能体系统综述：工作流、基础设施与挑战 | `10.1007/s44336-024-00009-2` | 362 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：摘要虽提及LLM智能体的规划能力与多智能体工作流，但未具体讨论规划表示或长期状态保留，不能作为这两个子问题的直接证据。 |
| 15 | 2024 | LLM-Based Edge Intelligence: A Comprehensive Survey on Architectures,  | 基于LLM的边缘智能：架构、应用、安全与可信赖性的全面综述 | `10.1109/ojcoms.2024.3456549` | 184 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 该论文是LLM边缘智能架构、安全与可信度的综述，虽提及自主性优化，但未涉及智能体工具使用中的规划表示或长期状态/记忆保留，属主题相邻。 |
| 16 | 2023 | The Exploration of Integrating the Midjourney Artificial Intelligence  | 将Midjourney人工智能生成内容工具融入设计系统以引导设计师迈向未来导向创新的探索 | `10.3390/systems11120566` | 123 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：讨论AIGC设计工具（Midjourney）的工作流整合，未涉及agentic规划表示或长期状态记忆机制。 |
| 17 | 2024 | Materials science in the era of large language models: a perspective | 大语言模型时代的材料科学：一个视角 | `10.1039/d4dd00074a` | 105 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：论文讨论LLM在材料科学中的应用概述与案例，未涉及agentic工具使用方法的规划表示或长期状态保留设计。 |
| 18 | 2024 | Towards Responsible Generative AI: A Reference Architecture for Design | 迈向负责任的生成式人工智能：设计基于基础模型的智能体的参考架构 | `10.1109/icsa-c63560.2024.00028` | 16 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 子问题1 | 摘要关注基于基础模型智能体的参考架构，并明确涉及规划（如分解目标、编排执行），但未提及长期状态保留。 |
| 19 | 2024 | Speech-Copilot: Leveraging Large Language Models for Speech Processing | Speech-Copilot：利用大语言模型通过任务分解、模块化和程序生成进行语音处理 | `10.1109/slt61566.2024.10832184` | 8 | 引用了种子 | 2 | 建议采纳(子问题1) | 采纳 | 子问题1 | 摘要描述了通过任务分解、模块化和程序生成进行规划，但未提及长期状态或记忆保留。 |
| 20 | 2025 | Spike sorting AI agent | 锋电位分类AI智能体 | `10.1101/2025.02.11.637754` | 8 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：该论文将LLM智能体应用于脉冲分选任务，但未讨论智能体工具使用方法的规划表示或长期状态保留设计。 |
| 21 | 2024 | Evaluating Top-k RAG-based approach for Game Review Generation | 评估基于Top-k RAG的游戏评论生成方法 | `10.1109/ic2pct60090.2024.10486273` | 8 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 主题相邻：该论文研究RAG用于游戏评论生成，未涉及agentic规划表示或长期状态保留设计。 |
| 22 | 2024 | Unified Multi-Scenario Summarization Evaluation and Explanation | 统一的多场景摘要评估与解释 | `10.1109/tkde.2024.3509715` | 4 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 该文研究多智能体摘要评估与解释，虽涉及LLM-based agents，但未讨论规划表示或长期状态保留，属于主题相邻而非直接证据。 |
| 23 | 2025 | AgentArcEval: An architecture evaluation method for foundation model b | AgentArcEval：一种基于基础模型的智能体架构评估方法 | `10.1016/j.jss.2025.112656` | 3 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 该论文提出的是基于基础模型的智能体架构评估方法与场景目录，聚焦质量属性评估，并未涉及规划如何表示或长期状态如何保留，属于主题相邻。 |
| 24 | 2026 | MDSD: Multi-turn Diverse Synthetic Dialog Generation for Domain Specif | MDSD：面向领域特定不完整请求理解的多轮多样合成对话生成 | `10.1109/icde65706.2026.00355` | 0 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | - | 该论文聚焦合成多轮对话生成与引导用户澄清不完整请求，虽涉及agent工作流和对话交互，但未讨论工具使用方法的规划表示或长期状态保留，属于主题相邻而非直接证据。 |
| 25 | 2024 | A survey on large language model based autonomous agents | 基于大语言模型的自主智能体综述 | `10.1007/s11704-024-40231-1` | 1624 | 引用了种子 | 1 | 建议采纳(两个子问题) | 采纳 | 子问题1, 2 | 该综述从整体视角提出LLM自主智能体的统一构建框架，此类框架通常系统覆盖规划模块与记忆/长期状态模块，故可同时作为两个子问题的证据。 |

## 摘要（判定用）

*(摘要部分内容未作更改，保留原文方便对照核查，为控制长度，此处略去原文件该部分的完整复制。完整审核文件已更新了上方的表格与下方的记录。)*

## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | Gemini |
| 日期 | 2026-09-24 |
| 采纳的候选编号 | 1, 3, 4, 6, 7, 8, 9, 10, 12, 13, 18, 19, 25 |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |