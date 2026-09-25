# 统一术语表

| 字段 | 内容 |
|---|---|
| 文档版本 | v0.2 |
| 状态 | 设计基线 |
| 日期 | 2026-09-26 |

## 1. 使用规则

- 文档、代码、数据库、MCP 工具和论文使用本表术语。
- 英文术语首次出现时保留英文，后续可只使用中文。
- 不允许用近义词替代规范实体名，除非明确说明映射。
- 术语发生含义变化时，先更新本文件，再修改其他文档和实现。

## 2. 核心术语

### Agent / 科研助理 Agent

在本地环境中围绕研究问题执行调研、查询、下载、归档和汇报的独立系统。

不要混用：助手、Bot、爬虫。

### Agent Core / Agent 核心

自研的运行时与决策组件集合，包括 runtime、planner、executor、memory、router、policy、evaluator 和 evidence engine。

不要混用：Pi 框架、LangChain。

### Pi

一个可参考的开源 TypeScript/Node Agent 框架。Pi 的 Skills、插件和 MCP 设计可以作为参考，但不是本项目的运行时依赖。MCP 通过扩展包接入，不是 Pi Core 的内置能力。

不要混用：本项目的基础框架、自研核心。

### MCP / Model Context Protocol

用于 Agent 与外部工具或数据源通信的协议。

### MCP Server / MCP 服务

某个源站或工具的独立协议适配实现。本项目要求每个源站一个独立 MCP server。

不要混用：源站、API、插件。

### Federation / 联邦层

对多个 MCP server 进行统一调度、归一化、去重和 provenance 合并的组件。

不要混用：Router。

### Router / 路由器

根据问题、源站能力、预算和健康状态选择源站及查询策略的组件。

不要混用：Federation、负载均衡器。

### Routing Budget / 路由预算

Router 每题最多选择的源站数。完整系统 B3 为 3；A3 消融不设预算，查询全部五个源站（ADR-0015）。

不要混用：并发度、请求次数。

### Source / 源站

外部学术数据来源，例如 arXiv、OpenAlex、Crossref、Semantic Scholar、DBLP。

不要混用：Provider、数据库、MCP server。

### Source Record / 源站记录

某个源站返回的原始记录，包含原始字段、抓取时间和 API 信息，不可变。

不要混用：Paper。

### Paper / 论文

跨源归一化后的规范文献实体。一个 Paper 可以关联多个 Source Record。

不要混用：Work、文献条目、源站记录。

### Paper Identity Key / 论文身份键

判断两条记录是否为同一篇论文的规范键。DOI、arXiv ID、arXiv DOI（`10.48550/arxiv.<id>`）和 OpenAlex ID 映射到同一身份键；运行时、相关性过滤、评测指标和金标比对必须使用同一个身份键函数（ADR-0015）。

不要混用：`source_record_id`、`canonical_key` 的某一种写法。

### File / 文件

实际获得的 PDF、HTML 或文本文件，必须记录 SHA-256、来源和许可。

不要混用：Paper、Document。

### Document / 文档解析结果

对 File 进行解析后得到的文本表示，包含 parser、版本和 locator 方案。

不要混用：File、原始 PDF。

### Evidence Span / 证据片段

从 Paper 的摘要、全文或外部材料中抽取的原文片段及其位置，是 Claim 的支持单元；必须关联提供证据的 Source Record。

不要混用：Quote、引用、参考文献。

### Locator / 定位信息

用于重新定位 Evidence Span 的结构化位置，例如页码、段落、章节和字符区间。

不要混用：URL、引用编号。

### Claim / 结论陈述

报告中的可验证陈述，必须标记支持状态，并尽可能关联 Evidence Span。

不要混用：句子、总结、事实。

### Provenance / 来源追踪

记录数据来自哪个源站、哪条源站记录、何时获取、经过什么映射和合并。它是证据链的一部分。

不要混用：引用、参考文献、来源列表。

### Run / 运行

一次完整 Agent 执行，包含 Plan、Step、Query、Source Call、Report 和审计事件。

不要混用：任务、查询。

### Plan / 计划

针对一个 Research Question 生成的结构化步骤集合。

不要混用：Prompt、任务列表。

### Plan-and-Execute

先规划完整步骤，再由 Runtime 和 Executor 逐步执行的架构模式。LLM 可以生成 Plan，但执行状态由代码控制。

不要混用：ReAct、多 Agent。

### Step / 步骤

Plan 中可独立执行、记录状态和重试的最小单元。

不要混用：Tool call。

### Runtime / 运行时

维护 Run 状态机、调度 Step、处理暂停恢复和错误的组件。

不要混用：Executor。

### Executor / 执行器

执行单个 Step，并调用 Router、Storage、Evidence 或工具的组件。

不要混用：Runtime。

### Memory / 记忆

保存项目、研究问题、Run、Plan、上下文和长期实体的组件。

不要混用：向量数据库、聊天记录。

### Policy / 策略

决定某操作允许、拒绝或需要人工确认的组件。

不要混用：权限系统、Prompt 规则。

### User Frontend / 用户前端

面向普通用户的浏览器界面（`web/`，React + Vite + TypeScript），只通过本地 HTTP API 访问数据（ADR-0016）。第一版是 v1 要求的最小 Web UI（证据链查看器），第二版增加提问、实时进度、报告浏览、导出和人工确认。

不要混用：CLI、本地 API、MCP server。

### Evaluator / 评测器

运行问题集和 baseline，计算指标并保存实验结果的组件。

不要混用：单元测试。

### Open Access / 开放获取

文献可以合法免费访问的状态。开放获取不等于无需遵守许可、限流或网站条款。

不要混用：免费下载、无版权。

### Baseline / 基线

用于对比完整系统效果的参考方法，例如 BM25 + 单次 LLM、单源 MCP、纯 ReAct。

不要混用：对照组（可作通俗解释，但论文使用 baseline）。

### Ablation / 消融实验

移除系统某个组件或约束后重新评测，以估计该组件贡献的实验。

不要混用：对比实验、压力测试。

### Citation Accuracy / 引用准确率

引用指向真实论文、内容相关且证据支持 Claim 的比例。

不要混用：参考文献数量。

### Evidence Coverage / 证据覆盖率

至少有一个有效 Evidence Span 的 Claim 比例。

不要混用：全文覆盖率。

### Unsupported Claim Rate / 无支撑结论率

`unsupported` Claim 占全部 Claim 的比例。

不要混用：错误率。

### Dangling Support / 悬空支持

`support_status` 为 `supported` 或 `partially_supported`、却没有关联任何 Evidence Span 的 Claim。完整系统在写入前把它降为 `unsupported`；A4 消融保留它，用 `dangling_support_count` 统计。

不要混用：无支撑结论（`unsupported`）。

### Ranked Candidate List / 有序候选列表

系统输出、用于计算 Precision@K、Recall@K 和 nDCG@K 的论文列表：按身份键去重、按规定规则排序、截断为 K（ADR-0015）。

不要混用：相关性过滤后的无序集合（只用于 `precision_kept`、`recall_kept`）。

### Task Success Rate / 任务成功率

满足完整系统验收清单的 Run 比例，用于完整系统验收，不用于 baseline-neutral 的 RQ3 比较。

不要混用：程序退出码为 0 的比例。

### Task Completion Rate / 任务完成率

满足 baseline-neutral 任务完成清单的 Run 比例，例如生成报告、覆盖子问题、无未处理异常和在预算内完成。

不要混用：证据链合规率。

### Evidence Compliance Rate / 证据合规率

通过证据和引用校验的 Claim 比例，用于评估证据链机制。

不要混用：任务完成率。

## 3. 源站类型术语

### Preprint Repository / 预印本库

托管预印本全文的站点，例如 arXiv。

### Metadata Index / 元数据索引

聚合元数据和引文关系但不直接托管全文的服务，例如 OpenAlex、Semantic Scholar。

### Metadata Registry / 元数据注册机构

负责标识符和注册元数据的机构，例如 Crossref。

### Bibliography Database / 书目数据库

面向特定领域整理出版信息的数据库，例如 DBLP。通常不提供全文。

## 4. 状态术语

### Run 状态

`CREATED`、`PLANNED`、`RUNNING`、`WAITING_CONFIRMATION`、`PAUSED`、`COMPLETED`、`FAILED`、`CANCELLED`。

### Step 状态

`PENDING`、`READY`、`RUNNING`、`RETRYING`、`SUCCEEDED`、`FAILED`、`SKIPPED`。

### Claim 支持状态

`supported`、`partially_supported`、`unsupported`、`disputed`。

### Evidence 级别

`metadata`、`abstract`、`full_text`、`external`。

## 5. 禁止的模糊表达

以下表达禁止在没有补充定义时使用：

- “系统自动完成所有事情”：必须说明自动边界和人工确认点。
- “支持论文下载”：必须说明源站、开放获取状态和授权范围。
- “引用准确”：必须说明是论文存在、主题相关还是证据支持。
- “多源提高效果”：必须说明哪个指标、哪个 baseline、多少提升。
- “Agent 自主规划”：必须说明 Plan 是模板、LLM 还是混合生成。
- “自研框架”：必须说明自研模块，不把 fork 或配置 Pi 称为自研。
- “本地优先”：必须说明哪些数据本地、哪些调用云端。
