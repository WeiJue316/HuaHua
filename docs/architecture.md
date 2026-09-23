# 系统架构设计

| 字段 | 内容 |
|---|---|
| 文档版本 | v0.1 |
| 状态 | 设计基线 |
| 日期 | 2026-09-23 |
| 关联文档 | `docs/PRD.md`, `docs/mcp-contract.md`, `docs/data-model.md` |

## 1. 架构结论

系统采用“**独立 Agent Core + 每源独立 MCP Server + Federation Router + Evidence Store**”的四层结构。

- Agent Core 是论文的主要自研对象，负责运行时、规划、执行、策略、记忆、路由、评测。
- MCP Server 是源站适配层，每个源站独立实现，不共享业务状态。
- Federation Router 负责多源并行查询、能力路由、归一化、去重和 provenance 合并。
- Evidence Store 负责保存 Claim、Evidence Span、Paper、File 的完整关系。
- Pi 只作为交互和插件设计参考，不进入依赖图。

核心约束是：**LLM 不是状态机，检索结果不是事实，报告不是最终产物，证据链才是。**

## 2. 架构目标与质量属性

| 质量属性 | 目标 |
|---|---|
| 可追溯性 | 任意 Claim 可定位到 Evidence Span、Paper、File 和源站记录 |
| 可复现性 | Run 的配置、Plan、源站响应摘要、模型版本和输出均可重放或审计 |
| 可恢复性 | 单步失败、源站超时、进程重启后可以恢复 Run |
| 可扩展性 | 新增源站只需新增 MCP server 和 capability 声明，不修改 Agent Core |
| 可测试性 | 核心策略、去重、证据定位和引用校验可在无网络环境测试 |
| 合规性 | 下载行为受 Policy 约束，不绕过访问控制 |
| 成本可控 | LLM 调用只用于语义步骤，记录 token 和费用，支持预算限制 |

## 3. 系统上下文

```text
┌─────────────────────────────────────────────────────────────────────┐
│                              User                                   │
│                    CLI / minimal Web UI                             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                        Research Agent Core                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ Planner  │→ │ Runtime  │→ │ Executor │→ │ Evaluator│            │
│  └──────────┘  └────┬─────┘  └────┬─────┘  └──────────┘            │
│                     │             │                                  │
│               ┌─────▼─────┐ ┌─────▼─────┐ ┌──────────┐             │
│               │  Memory   │ │  Policy   │ │ Evidence │             │
│               └───────────┘ └───────────┘ └────┬─────┘             │
└──────────────────────────────┬──────────────────┼───────────────────┘
                               │                  │
┌──────────────────────────────▼──────────────┐   │
│          Federation Router / Registry       │   │
│  capability routing · parallel call · retry  │   │
│  normalization · dedup · provenance merge   │   │
└───────┬──────────┬──────────┬──────────┬─────┘   │
        │          │          │          │         │
┌───────▼───┐ ┌────▼─────┐ ┌──▼───────┐ ┌▼───────┐ │
│ arXiv MCP │ │OpenAlex  │ │Crossref  │ │S2 MCP  │ │
│ Server    │ │MCP       │ │MCP       │ │        │ │
└───────┬───┘ └────┬─────┘ └──┬───────┘ └┬───────┘ │
        │          │          │          │         │
┌───────▼───┐ ┌────▼─────┐ ┌──▼───────┐ ┌▼───────┐ │
│ DBLP MCP  │ │ External │ │ External │ │ External│ │
│ Server    │ │ API      │ │ API      │ │ API     │ │
└───────────┘ └──────────┘ └──────────┘ └─────────┘ │
                                                    │
┌───────────────────────────────────────────────────▼──────────────┐
│                         Storage Layer                            │
│ SQLite + FTS5 │ immutable PDFs │ parsed text │ notes │ reports    │
└──────────────────────────────────────────────────────────────────┘
```

## 4. 分层与模块职责

### 4.1 Interface Layer

职责：

- CLI：项目创建、问题输入、运行、暂停、恢复、查看状态和导出。
- Web UI：任务状态、Plan 进度、来源分布、候选论文和证据链可视化。
- 人工确认：删除、移动、公开发送、高风险下载和 schema 迁移。

不负责：

- 业务规划。
- 源站协议。
- 证据抽取。
- 直接修改存储。

### 4.2 Agent Core

#### Runtime

- 维护 Run 状态机。
- 驱动 Plan 步骤的执行顺序。
- 处理暂停、恢复、取消、失败和重试。
- 记录事件、耗时、错误和检查点。
- 不直接调用源站 API，不直接访问 PDF。

#### Planner

- 将 Research Question 分解为 Plan。
- 生成查询意图、查询变体、筛选标准和步骤依赖。
- 只生成结构化 Plan，不执行外部操作。
- 支持规则模板与 LLM 规划两种策略。

#### Executor

- 执行 Plan Step。
- 调用 Router、Storage、Evidence 或 Tool。
- 将执行结果写回 Runtime 状态。
- 对可重试错误应用退避策略。
- 不自行改变 Plan；需要重规划时向 Runtime 发出请求。

#### Memory

- 管理 Project、Research Question、Run、Plan 和会话状态。
- 保存长期实体关系与短期执行上下文。
- 提供上下文检索，不负责全文解析。
- v1 不使用向量数据库，语义检索通过结构化过滤 + FTS5 + LLM 重排实现。

#### Router

- 维护源站能力注册表。
- 根据研究问题、语言、年份、资源类型、源站健康状态和策略选择源站。
- 决定查询并发度、预算和降级顺序。
- 将统一请求转换为源站 MCP 调用。

#### Policy

- 定义允许、拒绝和需要人工确认的操作。
- 管理下载域白名单、限流、预算、数据边界和审计要求。
- 在执行前检查，在执行后记录审计事件。
- 不把安全逻辑散落在 UI 或 MCP server 中。

#### Evaluator

- 运行问题集和 baseline。
- 计算检索、证据、引用、任务、延迟和成本指标。
- 保存配置、原始输出、聚合结果和失败样本。
- 为论文生成可复现实验记录。

#### Evidence Engine

- 解析 PDF 或摘要。
- 抽取候选 Evidence Span。
- 建立 Claim、Evidence、Paper、File 的关系。
- 校验引用真实性和 locator 有效性。
- 计算证据覆盖率和无支撑结论率。

### 4.3 Federation Layer

职责：

- 读取每个 MCP server 的 capability manifest。
- 将统一查询分发到多个源站。
- 并行执行、超时、重试、限流和部分失败处理。
- 将源站原生结果转换为公共 envelope。
- 执行 DOI/arXiv ID/标题/作者去重。
- 合并 provenance 和冲突字段。

不负责：

- 生成研究结论。
- 修改源站数据。
- 执行 PDF 归档。
- 保存业务实体最终状态。

### 4.4 MCP Layer

每个源站一个独立 MCP server：

- `arxiv-mcp`
- `openalex-mcp`
- `crossref-mcp`
- `semantic-scholar-mcp`
- `dblp-mcp`

共享代码只允许放在 `mcp-common`：

- MCP 协议初始化。
- 日志与错误类型。
- 限流与重试基础类。
- 公共 envelope 的校验工具。
- 测试 fixture 和 mock transport。

禁止：

- 共享源站业务状态。
- 让一个 server 直接调用另一个 server。
- 用简单 HTTP wrapper 冒充独立适配。
- 在公共层吞掉源站特有字段和错误语义。

### 4.5 Storage Layer

- SQLite：实体、关系、状态、Run、审计和 FTS5 索引。
- 文件系统：不可变 PDF、解析文本、Markdown 笔记、报告。
- 缓存：源站响应和解析中间结果，必须可清理且不参与最终证据。
- 导出：BibTeX、JSON、CSV、Zotero 兼容文件。

## 5. 运行时状态机

### 5.1 Run 状态

```text
CREATED
  → PLANNED
  → RUNNING
  → WAITING_CONFIRMATION
  → PAUSED
  → COMPLETED
  → FAILED
  → CANCELLED
```

规则：

- `CREATED → PLANNED`：Plan 已生成并校验。
- `PLANNED → RUNNING`：至少一个 Step 进入 READY。
- `RUNNING → WAITING_CONFIRMATION`：遇到 Policy 要求的人工操作。
- `WAITING_CONFIRMATION → RUNNING`：用户确认后继续。
- `RUNNING → PAUSED`：用户暂停或系统达到预算阈值。
- `PAUSED → RUNNING`：从最后一个检查点恢复。
- 任意非终态 → `FAILED`：不可恢复错误。
- 任意非终态 → `CANCELLED`：用户主动取消。

### 5.2 Step 状态

```text
PENDING → READY → RUNNING → SUCCEEDED
                         ↘ RETRYING → RUNNING
                         ↘ FAILED
                         ↘ SKIPPED
```

每个 Step 必须保存：

- `step_id`、`step_type`、`status`。
- 输入摘要和输出摘要。
- 依赖步骤和重试次数。
- 开始时间、结束时间、耗时。
- 错误类型、错误信息和恢复建议。
- 关联 Run、Plan 和审计事件。

## 6. Plan-and-Execute 流程

```text
Research Question
  → Planner 生成 Plan
  → Plan Validator 检查依赖和可执行性
  → Runtime 选择 READY Step
  → Executor 调用 Router / Storage / Evidence
  → Step Result 写回状态
  → 如果失败：重试、降级或请求重规划
  → 如果证据不足：触发补充查询
  → 所有必要 Step 完成后生成报告
  → Evaluator 记录指标
```

### 6.1 为什么不是纯 ReAct

纯 ReAct 的主要问题是：

- 执行轨迹不稳定，难以恢复。
- 检索、下载和引用校验混在一个循环中，无法单独评测。
- 失败后缺少明确检查点。
- token 成本和工具调用次数不可控。

因此 v1 使用状态机控制生命周期，Plan-and-Execute 控制步骤依赖，LLM 只在 Step 内部完成语义任务。

## 7. 多源路由策略

### 7.1 源站能力模型

每个源站声明：

```text
source_id
display_name
capabilities:
  search
  metadata
  abstract
  citations
  references
  open_access_url
  download_pdf
  author_disambiguation
rate_limit
auth_required
supported_identifiers
data_license
```

### 7.2 路由决策输入

- 研究问题类型：探索、综述、方法比较、数据集查找、作者/机构查询。
- 查询语言和领域。
- 年份和 venue 限制。
- 是否需要引用图谱。
- 是否需要全文下载。
- 源站健康状态、限流状态和历史成功率。
- 用户的数据源白名单和预算。

### 7.3 路由输出

- 选中的源站列表。
- 每个源站的查询变体。
- 并发度、超时和重试策略。
- 降级顺序。
- 结果融合权重。

### 7.4 融合原则

1. 标识符优先：DOI、arXiv ID 优先于标题匹配。
2. 标题相似度辅助：仅在缺少标识符时使用，并保留匹配分数。
3. 元数据不直接覆盖：冲突字段保留多个值及来源。
4. Provenance 不丢失：合并后的 Paper 必须能反查每个 Source Record。
5. 全文来源独立：Paper 可以没有可下载 File，但必须保留获取状态。

## 8. 证据链架构

```text
Report
  └── Claim
        └── Evidence Span
              └── Paper
                    ├── Source Record*        # metadata/abstract/full_text provenance
                    └── File → Document       # full_text evidence only
```

### 8.1 Claim

- 报告中的可验证陈述。
- 必须包含支持状态：`supported`、`partially_supported`、`unsupported`、`disputed`。
- 可以关联多个 Evidence Span，也可以标记为待验证。

### 8.2 Evidence Span

- 原文片段及其位置。
- 记录抽取方法：规则、PDF parser、LLM 或人工。
- 记录置信度和版本。
- locator 必须尽可能稳定；PDF 重解析后需验证或重新定位。
- metadata/abstract 证据必须记录 `source_record_id`；full_text 证据必须记录 Source Record、File 和 Document。

### 8.3 Paper 与 File

- Paper 是规范化的文献实体。
- Source Record 是源站原始记录。
- File 是实际获得的 PDF 或解析文本；只有 full_text 证据强制要求 File。
- 没有 File 的 Paper 仍可用于元数据分析和摘要级证据，但必须明确证据级别。

### 8.4 引用校验

报告生成后执行：

1. Claim 是否至少有一个 Evidence Span。
2. Evidence Span 是否指向存在的 Paper。
3. full_text Evidence Span 是否指向存在的 File 和 Document。
4. locator 是否能在解析文本中重新定位。
5. 引用编号和参考文献是否一致。
6. 无支撑 Claim 是否被显式标记。

## 9. LLM 边界与模型网关

### 9.1 LLM 允许介入

- 将研究问题转化为查询意图。
- 对候选论文进行相关性判断。
- 从文本中抽取候选 Evidence Span。
- 对多篇证据进行综合并生成 Claim。
- 生成报告叙述。

### 9.2 LLM 禁止介入

- 决定文件是否删除。
- 绕过 Policy 或访问控制。
- 伪造 locator。
- 直接写入未经校验的引用。
- 修改数据库 schema。
- 代替确定性去重和状态流转。

### 9.3 模型网关要求

- 统一封装模型调用、超时、重试和费用记录。
- 记录 provider、model、prompt version、token、费用和响应哈希。
- 支持本地模型或不同云模型的替换。
- 对包含未发表内容的请求执行数据边界策略。

网关实现位于 `src/research_agent/llm/`，由 `ModelGateway` 协议与具体 provider 实现组成。
依赖规则：语义步骤（`policy`、`planner`、`evidence`）只依赖 `ModelGateway` 协议，
不得导入任何具体 provider；具体 provider 由 `runtime` 在组装时注入。这样新增或替换
模型只需新增一个实现，并满足本文件第 13 节"Policy → 具体模型 provider"的禁止条款。

## 10. 并发、重试与失败恢复

- 源站查询按源站独立并发，默认每源并发不超过其限流上限。
- Federation 使用 `asyncio.TaskGroup` 或等价机制处理并行任务。
- 单个源站失败不阻塞其他源站；结果标记为部分成功。
- 可重试错误：超时、429、5xx、临时网络错误。
- 不可重试错误：401/403、参数错误、内容不存在、策略拒绝。
- 重试采用指数退避 + jitter，并记录每次尝试。
- 每个 Step 完成后写检查点；重启时从最后一个有效检查点恢复。
- 下载使用临时文件，校验哈希后再原子移动到最终路径。

## 11. 安全与合规

- 源站 API key 使用环境变量或系统凭据管理器。
- 下载域名使用白名单；重定向后再次校验。
- 不执行未验证的外部 HTML/JS。
- PDF 解析器在受限目录运行，限制文件大小和解析时间。
- 报告和日志脱敏，不记录 Cookie、Authorization header 或完整密钥。
- 机构订阅内容只复用用户已有授权会话，不保存密码。
- 所有下载、移动和公开发送操作写入审计日志。

## 12. 部署与运行形态

### v1

- 单机运行。
- Python 3.12。
- FastAPI 提供本地 API。
- SQLite + FTS5。
- CLI 为主入口。
- MCP servers 以本地子进程或 stdio 方式启动。
- Web UI 与 API 同机运行。

### 后续

- 可替换为 PostgreSQL。
- 可增加远程 MCP transport。
- 可增加对象存储和任务队列。
- 可增加多项目、多用户和权限隔离。

这些扩展不进入 v1，避免偏离证据链主贡献。

## 13. 模块依赖规则

允许的依赖方向：

```text
interfaces → runtime → planner / executor / policy / evaluator
runtime → llm（仅用于注入具体 provider）
planner / policy / evidence → llm（仅协议）
executor → router / memory / storage / evidence
router → mcp_common + mcp clients
evidence → storage
storage → sqlite / filesystem
```

禁止的依赖：

- MCP server → Agent Core。
- MCP server → 另一个 MCP server。
- Evidence Engine → UI。
- Policy → 具体模型 provider。
- Planner → 源站 API 直连。
- Runtime → PDF 解析实现细节。

## 14. 架构决策记录

- `docs/adr/0001-independent-agent-pi-as-reference.md`
- `docs/adr/0002-state-machine-plan-and-execute.md`
- `docs/adr/0003-evidence-chain-as-primary-contribution.md`
- `docs/adr/0004-per-source-mcp-and-federation.md`
- `docs/adr/0005-local-first-sqlite-fts5-filesystem.md`
- `docs/adr/0006-evaluation-driven-development.md`
- `docs/adr/0007-mcp-protocol-vs-source-adapters.md`
- `docs/adr/0008-evidence-chain-cardinality-and-provenance.md`
- `docs/adr/0009-evaluation-scale-and-task-metric-separation.md`
