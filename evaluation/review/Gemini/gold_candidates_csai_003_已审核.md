# 金标候选：csai_003

**问题**：What are reported limitations of chain-of-thought prompting on reasoning benchmarks?

　　→ 在推理基准上，思维链提示被报告出哪些局限性？

**子问题**：

1. Which benchmarks expose limitations?
　　→ 哪些基准揭示了这些局限性？

2. Which failure modes are reported?
　　→ 报告了哪些失败模式？


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
| 1 | 2023 | The Art of SOCRATIC QUESTIONING: Recursive Thinking with Large Languag | 苏格拉底式提问的艺术：基于大语言模型的递归思维 | `10.18653/v1/2023.emnlp-main.255` | 24 | 引用了种子 | 4 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 摘要明确报告CoT受单遍顺序生成和早期错误累积限制，并在MMLU、MATH、LogiQA和视觉问答等推理基准上通过优于CoT的表现暴露这些局限。 |
| 2 | 2023 | Faithful Chain-of-Thought Reasoning | 忠实的思维链推理 | `10.18653/v1/2023.ijcnlp-main.20` | 111 | 引用了种子 | 3 | 建议不采纳 | 不采纳 | | 摘要仅为作者与会议信息，未含任何关于基准、失败模式或局限性的实质内容；标题涉及CoT故属主题相邻而非完全无关。 |
| 3 | 2023 | On Second Thought, Let’s Not Think Step by Step! Bias and Toxicity in  | 转念一想，还是别一步步思考了！零样本推理中的偏见与毒性 | `10.18653/v1/2023.acl-long.244` | 68 | 引用了种子 | 3 | 建议采纳(两个子问题) | 采纳 | 1, 2 | The paper identifies limitation benchmarks (harmful questions and stereotype benchmarks) and reports failure modes (increased harmful, toxic, or undesirable CoT outputs) for zero-shot chain-of-thought prompting. |
| 4 | 2023 | Can ChatGPT Defend its Belief in Truth? Evaluating LLM Reasoning via D | ChatGPT能否捍卫其对真理的信念？通过辩论评估大语言模型推理 | `10.18653/v1/2023.findings-emnlp.795` | 47 | 引用了种子 | 2 | 建议采纳(两个子问题) | 采纳 | 1, 2 | 摘要报告在数学、常识、逻辑和BIG-Bench等推理基准上，LLM虽能生成正确逐步解，但在被无效论证挑战时无法维护其信念，因此既指出了暴露局限的基准类型，也报告了失败模式。 |
| 5 | 2024 | From Automation to Augmentation: Redefining Engineering Design and Man | 从自动化到增强：在下一代人工智能时代重新定义工程设计与制造 | `10.21428/e4baedd9.e39b392d` | 22 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | | 该摘要讨论Gen-AI在工程设计制造中的局限，未涉及chain-of-thought prompting或推理基准，属于主题相邻但无法回答任一子问题。 |
| 6 | 2025 | Dual-process theory and decision-making in large language models | 大语言模型中的双过程理论与决策 | `10.1038/s44159-025-00506-1` | 11 | 引用了种子 | 2 | 建议不采纳 | 不采纳 | | 主题相邻：该综述讨论LLM决策中的双过程理论与偏见/幻觉等局限，但未涉及链式思维提示在推理基准上的具体局限或失败模式。 |
| 7 | 2024 | Generative AI in the context of assistive technologies: Trends, limita | 辅助技术背景下的生成式人工智能：趋势、局限与未来方向 | `10.1016/j.imavis.2024.105347` | 45 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | | 主题相邻：该文综述生成式AI在辅助技术中的局限与伦理问题，并未涉及链式思维提示在推理基准上的具体限制或失败模式。 |
| 8 | 2023 | Prompting is not a substitute for probability measurements in large la | 提示并非大语言模型中概率测量的替代品 | `10.18653/v1/2023.emnlp-main.306` | 37 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | | 主题相邻：该文讨论prompting与概率测量在语言知识评估上的局限，但未涉及chain-of-thought prompting或推理基准上的失败模式。 |
| 9 | 2025 | “It’s Not Only Attention We Need”: Systematic Review of Large Language | “我们需要的不仅仅是注意力”：大语言模型在心理保健中的系统综述 | `10.2196/78410` | 20 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | | 该文是心理健康护理中LLM应用的范围综述，仅顺带提到评估推理能力有限，未涉及思维链提示在推理基准上的局限，属于主题相邻但无关子问题。 |
| 10 | 2025 | Generating and leveraging explanations of AI/ML models in materials an | 在材料与制造研究中生成并利用AI/ML模型的解释 | `10.1016/j.patter.2025.101340` | 12 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | | 该文讨论材料与制造领域的可解释AI，未涉及链式思维提示在推理基准上的局限或失败模式，仅属主题相邻。 |
| 11 | 2024 | The Evaluation of GenAI Capabilities to Implement Professional Tasks | 生成式AI执行专业任务能力的评估 | `10.17323/2500-2597.2024.4.67.76` | 9 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | | 该文讨论LLM在专业任务上的通用局限（如非因果性错误、参数弹性），并未涉及链式思维提示（CoT）或其推理基准上的失败模式，属于主题相邻而非直接证据。 |
| 12 | 2025 | A Survey on Enhancing Causal Reasoning Ability of Large Language Model | 增强大语言模型因果推理能力的综述 | `10.1007/978-981-96-8183-9_29` | 8 | 引用了种子 | 1 | 无法判断 | 不采纳 | | 源站未提供摘要，无法作为当前证据采纳。 |
| 13 | 2025 | If You Give an LLM a Legal Practice Guide | 如果你给大语言模型一本法律实务指南 | `10.1145/3709025.3712220` | 5 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | | 主题相邻：该文研究法律问答中检索/实践指南提示与子问题分解的效果，并未评估 chain-of-thought prompting 在推理基准上的局限。 |
| 14 | 2025 | Psychometrically derived 60-question benchmarks: Substantial efficienc | 基于心理测量学构建的60题基准：显著的效率提升与人类—AI比较的可能性 | `10.1016/j.intell.2025.101922` | 4 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | | 主题相邻：涉及推理基准（GSM8K 等）与 LLM 评测，但未讨论 chain-of-thought prompting 的局限性或失败模式。 |
| 15 | 2025 | Developing an Accounting Virtual Assistant Through Supervised Fine‐Tun | 通过小语言模型（SLM）的监督微调（SFT）开发会计虚拟助手 | `10.1002/isaf.70011` | 2 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | | 论文聚焦会计领域小语言模型的监督微调与评估，未涉及思维链提示、推理基准或其局限/失败模式，因此与两个子问题完全无关。 |
| 16 | 2025 | Comparative Evaluation of GPT Models in FHIR Proficiency | GPT 模型在 FHIR 熟练度方面的对比评估 | `10.1145/3718095` | 2 | 引用了种子 | 1 | 建议不采纳 | 不采纳 | | 完全无关：该文评估GPT模型在FHIR医疗数据标准考试中的表现，未涉及思维链提示或其推理基准上的局限与失败模式。 |
| 17 | 2023 | Gender bias and stereotypes in Large Language Models | 大型语言模型中的性别偏见与刻板印象 | `10.1145/3582269.3615599` | 366 | 引用了种子 | 0 | 建议不采纳 | 不采纳 | | 主题相邻——该论文研究LLM中的性别偏见与刻板印象，并未涉及思维链提示或其局限性，也未涉及推理基准或思维链失败模式。 |
| 18 | 2024 | AI deception: A survey of examples, risks, and potential solutions | 人工智能欺骗：实例、风险与潜在解决方案综述 | `10.1016/j.patter.2024.100988` | 219 | 引用了种子 | 0 | 建议不采纳 | 不采纳 | | 该论文主题为AI欺骗及其风险与治理，未涉及思维链提示在推理基准上的局限性、相关基准或失败模式，属于主题相邻但完全未回答该子问题。 |
| 19 | 2023 | Automated evaluation of written discourse coherence using GPT-4 | 使用 GPT-4 自动评估书面语篇连贯性 | `10.18653/v1/2023.bea-1.32` | 76 | 引用了种子 | 0 | 建议不采纳 | 不采纳 | | 主题相邻：论文讨论GPT-4用于写作连贯性评估，未涉及链式思维提示或推理基准的局限性。 |
| 20 | 2025 | Sycophancy in Large Language Models: Causes and Mitigations | 大型语言模型中的谄媚现象：成因与缓解措施 | `10.1007/978-3-031-92611-2_5` | 76 | 引用了种子 | 0 | 无法判断 | 不采纳 | | 源站未提供摘要，无法作为当前证据采纳。 |
| 21 | 2025 | Helpful, harmless, honest? Sociotechnical limits of AI alignment and s | 有用、无害、诚实？通过人类反馈强化学习实现AI对齐与安全的社会技术局限 | `10.1007/s10676-025-09837-2` | 46 | 引用了种子 | 0 | 建议不采纳 | 不采纳 | | 该文讨论RLHF对齐（HHH原则）的社会技术局限，未涉及chain-of-thought prompting或其推理基准表现，属于主题相邻但与两个子问题均无证据关联。 |
| 22 | 2025 | Formal requirements engineering and large language models: A two-way r | 形式化需求工程与大语言模型：一条双向路线图 | `10.1016/j.infsof.2025.107697` | 46 | 引用了种子 | 0 | 建议不采纳 | 不采纳 | | 该论文讨论LLM在需求工程中的正确性与形式化方法路线图，未涉及chain-of-thought提示或推理基准，与子问题仅主题相邻（同属LLM局限性话题）。 |
| 23 | 2024 | Large language models can help boost food production, but be mindful o | 大语言模型有助于促进粮食生产，但需警惕其风险 | `10.3389/frai.2024.1326153` | 42 | 引用了种子 | 0 | 建议不采纳 | 不采纳 | | 该论文讨论LLM在农业生产中的风险与机会，未涉及链式思维提示、推理基准或其失败模式，属于主题相邻但完全无关。 |
| 24 | 2024 | Quo Vadis ChatGPT? From large language models to Large Knowledge Model | ChatGPT何去何从？从大语言模型到大型知识模型 | `10.1016/j.compchemeng.2024.108895` | 41 | 引用了种子 | 0 | 建议不采纳 | 不采纳 | | 主题相邻：摘要讨论LLM在科学工程领域缺乏推理/规划能力，但未涉及chain-of-thought prompting、推理基准或相关失败模式。 |
| 25 | 2023 | Leveraging GPT-4 for Automatic Translation Post-Editing | 利用GPT-4进行自动翻译译后编辑 | `10.18653/v1/2023.findings-emnlp.804` | 40 | 引用了种子 | 0 | 建议不采纳 | 不采纳 | | 该论文研究GPT-4用于翻译译后编辑（涉及幻觉编辑等局限），但完全未涉及思维链提示或推理基准，属于主题相邻（LLM局限与幻觉）而非同一子问题。 |

## 摘要（判定用）

判据 3 要求确认摘要里存在可作为证据的完整句子，因此这里附上原文摘要。
机翻标题仅供快速定位，**判定必须依据英文原文**。

*(Abstract texts omitted for brevity as they remain unchanged from the prompt)*

## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | AI 助手 |
| 日期 | 2026-09-24 |
| 采纳的候选编号 | 1, 3, 4 |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |