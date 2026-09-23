# 开题报告正文草稿

> 依据《成都锦城学院毕业论文（设计）开题报告》六栏结构撰写，参考往届范文的篇幅与写法。
> 参考文献的标题、作者、年份与卷期页码已逐条核验（Crossref / DataCite，2026-09-23）。
> 标记 `【待补】` 的位置需要补充经核验的来源。

## 一、选题意义

人工智能与大数据技术的普及深刻改变了科研工作方式，也带来了新的效率瓶颈。全球学术产出
持续快速增长，计算机与人工智能方向尤为突出。研究者在文献调研上投入的时间被大量消耗在
"检索—筛选—阅读—归纳"的重复环节，真正用于思考与创新的时间被压缩。

现有学术检索工具解决了"找得到"的问题，却没有解决"信得过、查得回"的问题。以 Google
Scholar、CNKI、Semantic Scholar 为代表的平台返回的是论文列表，仍需人工逐篇阅读判断；
而直接让大语言模型生成文献综述虽能快速成文，却存在两个致命缺陷：一是幻觉，模型可能生成
并不存在的引用；二是不可追溯，读者无法核实某条结论究竟出自哪篇文献的哪一段原文。

本研究拟构建面向计算机/AI 领域的可追溯科研 Agent 框架，以**证据链**为核心机制：
每一条支持性结论都必须能够沿"结论—原文片段—论文—来源记录"逐级回溯，若证据取自全文，
还需进一步关联到本地文件与解析后的文档对象。在此基础上，系统通过独立的源站 MCP 服务
联邦调用多个学术源，由确定性规划器与执行器驱动完整流程，保证检索、去重、下载、归档与
状态流转的可复现性。

研究意义体现在两个层面。理论上，提出一套证据链的形式化建模方法，并给出"结构指标可
自动判定、语义指标需人工或模型判定"的评测设计，为生成式系统在学术场景下的可信性评估提供
参考。实践上，形成一套本地优先、可离线运行、可移植的科研辅助工具，降低文献调研成本；
其证据链机制对本项目之外的场景——任何需要"生成内容可核查"的应用——同样具有借鉴价值。

## 二、国内外研究现状概述

### （一）国内研究现状

国内在大语言模型基础能力上的进展为本研究提供了可行的技术底座。通义千问团队发布的
Qwen2 系列覆盖多种参数规模并在多项基准上达到开源模型领先水平[1]；智谱团队提出的
ChatGLM 系列覆盖至 GLM-4 All Tools[2]；DeepSeek 团队先后发布 DeepSeek-V3[3]，其
推理增强版本 DeepSeek-R1 通过强化学习提升推理能力并发表于《自然》[4]。这些工作
标志着国内在大模型基础能力与推理增强方向已进入国际前沿。

在科研知识服务层面，国内目前仍以检索平台为主。CNKI、万方数据、百度学术等平台提供
文献检索、引文网络与全文下载，但其输出形态仍是文献列表与统计信息，缺少面向"研究问题"
的证据级组织。国内学术界在检索增强生成与科研智能体方向的跟进研究正在增多，但在
"面向科研任务的智能体框架"与"生成结论的证据可追溯性"两个方向上的系统性研究仍相对薄弱。
【待补：请补充 2–3 篇国内学者在 RAG 或科研智能体方向的代表性论文，建议在知网以
"检索增强生成""科研智能体""大模型文献综述"为关键词检索近三年高被引文献，
核对期刊、年份与页码后补入，并在本段相应位置加引用标注。】

### （二）国外研究现状

**检索增强生成范式的建立与演进。** 检索增强生成将参数化语言模型与非参数化外部知识库
结合，以缓解幻觉与知识过时问题。Gao 等人系统梳理了该方向从朴素 RAG、高级 RAG 到
模块化 RAG 的演进脉络，并指出评测方法与基准是该领域的关键缺口[5]。

**RAG 评测方法。** 针对 RAG 系统缺少评估手段的问题，Es 等人提出 RAGAs，用一套无需
人工标注真值的指标评估检索质量、忠实度与生成质量[6]；Saad-Falcon 等人提出 ARES，
用轻量语言模型判别器在降低人工标注量的前提下评估 RAG 系统的上下文相关性、答案忠实度
与答案相关性[7]。

**检索模型与科学检索评测。** 稠密检索与稀疏检索的取舍是科学文献检索的核心问题。
Gao 等人指出在缺少相关性标注时构建完全零样本的稠密检索系统仍很困难[8]；Wadden 等人
发布 SciFact-Open，用 50 万篇研究摘要评估科学论断验证系统在开放域下的泛化能力[9]。
在图像文本检索方向，Wei 等人构建 M-BEIR 基准以统一多模态检索评测[10]。

**智能体的规划与记忆设计。** Huang 等人系统梳理了 LLM 智能体的规划方法，将其归纳为
任务分解、计划选择、外部模块、反思与记忆五类[11]；Packer 等人提出 MemGPT，借鉴操作系统
的层级内存思想，通过快慢内存间的数据搬运在有限上下文窗口内提供扩展上下文[12]；
Park 等人构建的生成式智能体通过观察、规划与反思组件实现可信行为模拟[13]。

**推理能力局限的实证研究。** Turpin 等人发现思维链解释可能系统性地歪曲模型预测的真实
原因[14]；Mirzadeh 等人通过 GSM-Symbolic 揭示模型在仅改变数值或增加无关子句时性能
显著下降，质疑既有基准的可靠性[15]。这类研究说明：模型输出的"看起来合理"不等于
"可被证据支撑"。

**多模态与高效部署。** Chen 等人系统综述了视觉语言预训练中的特征提取、模型架构、
预训练目标与下游任务[16]；Li 等人提出 BLIP-2，用轻量查询变换器分两阶段桥接模态差距[17]。
在效率方向，Xiao 等人提出 SmoothQuant，在免训练的前提下实现 8 位量化并报告了加速与
精度损失[18]；Ben Zaken 等人提出 BitFit，仅微调偏置项以降低训练开销[19]。

**工具协议。** 模型上下文协议（MCP）被提出用于标准化大语言模型与外部工具、数据源的
交互方式，正在成为工具调用的事实标准[20]。这为本研究"每源独立 MCP 服务 + 联邦路由"
的架构选择提供了直接参照。

**小结。** 现有工作分别在检索模型、生成范式、评测方法、智能体架构、效率优化等方向取得
进展，但呈现明显的"分段解决"特征：检索工作关注召回质量，评测工作关注指标设计，
智能体工作关注任务完成度，三者之间缺少一条贯穿的**证据可追溯链路**。同时，学术场景
特别要求的"任一结论可回溯到原文出处"这一约束，在通用智能体框架中并未被作为一等目标
对待。本研究正是针对这一缺口，把证据链作为核心贡献而非附属功能。

## 三、主要研究内容

本研究立足计算机与人工智能领域的文献调研场景，聚焦"生成结论如何被证据支撑"这一
核心问题，构建"多源检索—证据抽取—引用校验—报告生成"的研究框架，实现一个可独立运行
的可追溯科研 Agent 系统。

**核心问题**：在缺少人工标注真值的条件下，如何让自动生成的文献调研结论具备可核查的
证据支撑？该问题可分解为三个子问题：其一，多源异构的学术元数据如何在没有中心权威源的
情况下统一、去重并保留溯源信息；其二，如何把论文摘要或全文中的具体片段与其支撑的
结论建立稳定关联，并在生成阶段强制校验；其三，如何设计一套既有客观结构指标、又能
反映语义质量的评测方案，使系统改进可被量化。

**理论依据**。本研究的方法论建立在两条已有结论之上。一是检索增强生成的有效性——
外部知识的引入可以降低大语言模型的幻觉风险[5]；二是思维链等推理过程的内在不可靠性——
模型给出的解释未必反映真实决策依据[14]，因此仅凭模型自述不足以构成证据，必须回到原文。
这两点共同指向"把证据从生成过程中独立出来、单独建模与校验"的设计选择。

**研究目标**：

（1）**建立证据链模型并落地为数据模型。** 定义"结论—证据片段—论文—来源记录"的
关联关系，全文证据进一步关联文件与解析文档；每个来源记录记录源标识、检索时间与
来源元数据，每个文件记录 SHA-256、路径、MIME 类型与来源 URL，使任一结论可回溯、
可验证、可复现。

（2）**实现五源联邦检索与确定性执行流程。** 为 arXiv、OpenAlex、Crossref、
Semantic Scholar、DBLP 分别实现独立的 MCP 服务，由联邦路由层统一封装超时、重试、
限流、并发预算与部分失败可见性；由确定性规划器选择源与查询变体、执行器以状态机
驱动完整流程，保证同一问题在相同配置下可复现。

（3）**设计并执行可复现的评测方案。** 建立问题集、金标证据与配置矩阵，区分
"结构指标"（可由程序自动判定，如引用覆盖率、证据链完整性）与"语义指标"（需人工或
模型判定），并通过基线对比与消融实验验证证据链机制与多源联邦的实际增益。

**潜在贡献**。其一，把证据链从"生成后处理"提升为系统的一等设计目标，给出可落地的
数据模型与引用校验机制；其二，提出按"确定性优先"原则划分人机职责的智能体架构——
检索、去重、下载、归档与状态流转由代码执行，模型只介入规划、相关性判断与综合生成，
使系统行为可复现、可审计；其三，通过实际构建过程中发现的失败案例（例如纯关键词
匹配会把芯片设计、语音数据集等邻域论文误收为金标证据），为"论文相关"与"证据回答了
问题"之间的差异提供实证，并据此引入语义相关性判定作为消融条件。

## 四、拟采用的研究思路（方法、技术路线、可行性论证等）

**1. 研究方法**

采用"规范先行—纵向切片—评测驱动"的工程研究方法，配合定量评测验证。

建模阶段使用文献分析法，梳理检索增强生成、智能体架构与学术评测三个方向的既有工作，
提炼证据链所需的最小实体集合与关系。实现阶段采用纵向切片策略：每完成一个能力即打通
"一个问题 → 多源检索 → 去重 → 证据抽取 → 报告生成"的完整链路并交付可运行版本，
避免横向堆叠模块导致集成风险后置。验证阶段采用问题集驱动的方法，建立冻结版本的
问题集与金标证据（当前已冻结 10 题 / 24 篇的 pilot 版本），在固定配置下批量运行并
聚合指标，配合失败样本分析定位系统短板。

**2. 技术路线**

系统自下而上分为四层。**存储层**采用 SQLite + FTS5 与内容寻址文件系统，实现元数据
检索、全文检索与不可变归档；原始文件只追加不覆盖，更新版本时新建文件并保留哈希。
**源站层**为每个学术源实现独立 MCP 服务，向上暴露统一的 `<source>_<verb>_<object>`
工具契约，向下适配各源差异化的查询语法、分页机制与限流策略，并支持按 DOI 跨源补全
缺失的摘要字段。**联邦层**负责多源并行调用与结果合并，实现按主机粒度的限流、
有界重试与 `Retry-After` 支持、查询变体去重、部分失败与整体失败的区别上报——某源
部分查询变体失败时保留已获得结果并显式记录，避免静默降级为"零结果"。**智能体层**
由确定性规划器与执行器构成：规划器根据问题特征选择源集合、生成由精到宽的查询变体并
分配预算；执行器以状态机驱动路由、检索、持久化、结论合成、引用校验与报告生成等步骤，
每步记录尝试次数与审计事件。

工程上以 Python 3.12 与 `uv` 管理依赖，通过 GitHub Actions 在 Windows、Linux、
macOS 三个平台执行格式检查、静态类型检查、单元与集成测试及文档结构校验，保证可移植性。

**3. 可行性论证**

**理论可行**：检索增强生成降低幻觉的有效性已获广泛验证[5]，证据链所需的数据模型
（实体—关系—来源记录）在学术元数据领域有成熟的建模先例。

**技术可行**：五个目标数据源均提供公开 API，且已在本项目前期完成适配并跑通真实调用；
MCP 协议的开放性与既有框架的插件化实践验证了模块化扩展路径。当前系统已实现五源
MCP 服务、联邦路由、规划执行流程、证据链持久化与 PDF 归档解析，并通过 123 项自动化
测试。

**数据可行**：评测问题集可通过公开学术源构建，并已有冻结的 pilot 版本与配套的人工
复核流程（六项判据 + 工作表）。正式集将在语义相关性判定落地后扩展至 30 题。

**风险可控**：项目的主要风险是源站限流与接口变动。已采取的缓解措施包括每主机限流、
有界重试、失败可见性、契约测试与离线 fixture 测试；评测全部使用离线数据，避免网络
不稳定影响结果复现。

## 五、研究工作安排及进度

（学校各环节截止时间均为当日 17:00）

2026-11-02 至 2026-11-06：完成论文选题与定题。
2026-11-09 至 2026-11-11：配合学术委员会审题。
2026-11-12 至 2026-11-15：接受导师下达的任务书。
2026-11-16 至 2026-11-29：完成开题报告及开题材料，准备开题答辩。
2026-12-05：参加开题答辩。

2026-12 至 2027-01 上旬：完善证据链机制与语义相关性判定，扩展正式评测集至 30 题，
建立基线与消融配置；同步撰写论文的架构、MCP 契约与数据模型章节。
2027-01-11 至 2027-01-15：参加中期检查，提交阶段成果与实验记录。

2027-01 中旬 至 2027-02：执行正式对比实验与消融实验，完成全部数据采集与统计；
撰写实验与讨论章节。
2027-02-28：完成全部实验。
2027-03-01 至 2027-03-19：论文整合、格式规范与定稿。
2027-03-19 17:00：论文定稿提交。
2027-03-22 17:00：完成格式检测与查重。
2027-03-23 至 2027-04-04：配合指导教师评审与专家评审，按意见修改。
2027-04-10：参加论文答辩。
2027-04-12 至 2027-04-29：完成答辩后整改与终版提交。
2027-05-06 至 2027-05-13：配合论文信息核查。
2027-05-14 至 2027-05-28：完成存档材料打印与提交。

## 六、参考文献目录

> 标题、作者、年份与卷期页码已通过 Crossref（出版商 DOI）或 DataCite（arXiv DOI）
> 逐条核验，核验日期 2026-09-23。

[1] Yang A, Yang B, Hui B, et al. Qwen2 Technical Report[EB/OL]. arXiv:2407.10671, 2024.
[2] GLM Team, Zeng A, Xu B, et al. ChatGLM: A Family of Large Language Models from GLM-130B to GLM-4 All Tools[EB/OL]. arXiv:2406.12793, 2024.
[3] DeepSeek-AI, Liu A, Feng B, et al. DeepSeek-V3 Technical Report[EB/OL]. arXiv:2412.19437, 2024.
[4] Guo D, Yang D, Zhang H, et al. DeepSeek-R1 incentivizes reasoning in LLMs through reinforcement learning[J]. Nature, 2025, 645(8081): 633-638. DOI:10.1038/s41586-025-09422-z.
[5] Gao Y, Xiong Y, Gao X, et al. Retrieval-Augmented Generation for Large Language Models: A Survey[EB/OL]. arXiv:2312.10997, 2023.
[6] Es S, James J, Espinosa Anke L, et al. RAGAs: Automated Evaluation of Retrieval Augmented Generation[C]//Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations. 2024: 150-158. DOI:10.18653/v1/2024.eacl-demo.16.
[7] Saad-Falcon J, Khattab O, Potts C, et al. ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems[C]//Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies. 2024: 338-354. DOI:10.18653/v1/2024.naacl-long.20.
[8] Gao L, Ma X, Lin J, et al. Precise Zero-Shot Dense Retrieval without Relevance Labels[C]//Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics. 2023: 1762-1777. DOI:10.18653/v1/2023.acl-long.99.
[9] Wadden D, Lo K, Kuehl B, et al. SciFact-Open: Towards open-domain scientific claim verification[C]//Findings of the Association for Computational Linguistics: EMNLP 2022. 2022: 4719-4734. DOI:10.18653/v1/2022.findings-emnlp.347.
[10] Wei C, Chen Y, Chen H, et al. UniIR: Training and Benchmarking Universal Multimodal Information Retrievers[C]//Proceedings of the European Conference on Computer Vision (ECCV 2024), Lecture Notes in Computer Science. 2025: 387-404. DOI:10.1007/978-3-031-73021-4_23.
[11] Huang X, Liu W, Chen X, et al. Understanding the planning of LLM agents: A survey[EB/OL]. arXiv:2402.02716, 2024.
[12] Packer C, Wooders S, Lin K, et al. MemGPT: Towards LLMs as Operating Systems[EB/OL]. arXiv:2310.08560, 2023.
[13] Park J S, O'Brien J, Cai C J, et al. Generative Agents: Interactive Simulacra of Human Behavior[C]//Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology. 2023: 1-22. DOI:10.1145/3586183.3606763.
[14] Turpin M, Michael J, Perez E, et al. Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting[C]//Advances in Neural Information Processing Systems 36. 2023. arXiv:2305.04388.
[15] Mirzadeh I, Alizadeh K, Shahrokhi H, et al. GSM-Symbolic: Understanding the Limitations of Mathematical Reasoning in Large Language Models[EB/OL]. arXiv:2410.05229, 2024.
[16] Chen F L, Zhang D Z, Han M L, et al. VLP: A Survey on Vision-Language Pre-training[J]. Machine Intelligence Research, 2023, 20(1): 38-56. DOI:10.1007/s11633-022-1369-5.
[17] Li J, Li D, Savarese S, et al. BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models[C]//Proceedings of the 40th International Conference on Machine Learning. 2023. arXiv:2301.12597.
[18] Xiao G, Lin J, Seznec M, et al. SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models[C]//Proceedings of the 40th International Conference on Machine Learning. 2023. arXiv:2211.10438.
[19] Ben Zaken E, Goldberg Y, Ravfogel S. BitFit: Simple Parameter-efficient Fine-tuning for Transformer-based Masked Language-models[C]//Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers). 2022: 1-9. DOI:10.18653/v1/2022.acl-short.1.
[20] Anthropic. Model Context Protocol Specification[EB/OL]. https://modelcontextprotocol.io, 2024.

---

## 待办与待确认

1. **国内研究现状**需补充 2–3 篇中文文献，正文段末已用 `【待补】` 标出位置与检索建议。
2. **封面信息**待提供：学号、年级、专业名称、指导教师、最终题目。
3. **题目建议**：面向计算机/AI 文献调研的可追溯科研 Agent 框架设计与实现。
4. 若学校要求 GB/T 7714 严格格式，需按规范调整标点与文献类型标识。
5. 开题报告会议纪要、任务书、指导记录表、中期检查表属于学校流程表格，
   待有实际记录后填写。
