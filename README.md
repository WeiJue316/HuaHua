# 面向计算机/AI 文献调研的可追溯科研 Agent 框架

当前仓库处于 M2 修复阶段（路线图批次 1）。项目目标是实现一个独立的科研助理 Agent，完成调研、查询、下载、归档和汇报，并以 `Claim → Evidence Span → Paper → Source Record*` 的证据链作为论文主贡献；`full_text` 证据再关联 `File → Document`。

Pi 仅作为设计参考，不进入运行时依赖。系统采用独立 Agent Core、每源独立 MCP server、自研 Federation/Router、SQLite + FTS5 + 文件系统。

## 当前状态

后续修复与优化以 [路线图](docs/roadmap.md) §4 的问题清单为准；进度快照见路线图 §2。论文写作另见 [论文计划](docs/thesis-plan.md)（默认休眠），与开发计划互不驱动。

- M0 已完成：工作规范、PRD、架构、MCP 契约、数据模型、评测方案、路线图、术语表、ADR 0001–0015、Pi 调研记录、文档结构校验脚本、Python 3.12 + uv 脚手架、跨平台项目规则、GitHub Actions 配置、SQLite 初始 schema 和迁移 runner。
- M1 已完成：arXiv MCP server、arXiv Atom 解析、SourceRecord/Paper/EvidenceSpan 持久化、CLI 纵向流程和 Markdown 报告。
- M2 已完成：OpenAlex MCP server（含 citations/references）、并行 Federation、DOI 跨源合并、双源 provenance 保留、Evidence → Claim 构建与引用校验、限流/网络错误的有界重试与 `Retry-After` 支持，以及内容寻址 PDF 归档、Document 解析、full-text Evidence 和 File provenance。
- M3 进行中：五源 MCP server、source registry、Federation 并发预算、部分源错误可见性、确定性 Planner、Plan/AuditEvent 持久化，以及由 Executor 驱动的七步 Run 流程（路由、检索、持久化、相关性判断、Claim 综合、引用校验、报告）、StepAttempt 和重试预算。
- 评测基础设施：JSONL 问题集加载与哈希、EvaluationRun/Case/Result 持久化、批量 case matrix 调度、三源冻结快照；Pilot v1（人工复核）和 v2（AI 审计）已冻结；B0、B1、B2、B3、A1、A2、A3、A4、A6 已接入评测矩阵。
- 当前阶段：M2 修复阶段，正在执行路线图批次 1（评测口径修正，ADR-0015）。

### 未完成与已知限制

完整清单与验收标准见路线图 §4，这里只列影响使用和结论的要点：

- **现有 Pilot 数字口径作废**：检索指标按无序集合计算、未统一论文身份键；A3 与 B3 实际相同；A4 同时改变了提示词和后处理。修正见 ADR-0015 与 `EV-01`–`EV-10`。
- **证据链断口**：报告仍列出被相关性过滤的论文；全文 locator 页码写死为 1、偏移不可重新定位；补全摘要挂在错误的 Source Record 上；步骤重试会重复写入（`EC-01`–`EC-04`）。
- **安全**：OpenAlex API key 会随 URL 写入源站缓存文件（`SR-01`）。
- 评测在有模型网关时用 `synthesis-v1` 从已存储 Evidence Span 写 Claim 和 Findings；模型失败或 CLI 未加 `--synthesis` 时退回模板首句。
- 只输出 Markdown 报告；JSON/CSV 证据表、BibTeX 导出、下载 Policy 尚未实现（`SC-01`、`SC-02`）。
- 目前只有 CLI。用户前端按 ADR-0016 分两步：第一版证据链查看器对齐 M4（2027-01-15），第二版面向普通用户的完整前端在 M7 之后（M8，`FE-01`–`FE-10`）。
- 正式 30 题集尚未实现。
- 真实源站限制：arXiv 间歇 406/429、Semantic Scholar 429、DBLP 返回 bot challenge，三者当前无法稳定完成真实烟测；CI 全部使用 fixture 离线验证。
- Crossref 搜索结果普遍不含 abstract，目前对证据链没有贡献。
- Planner 的 `query_variants` 已进入检索，但 Federation 仍按变体顺序截断，靠后的变体只能补上前面没出现的论文（`OP-01`）。

### 验证状态

- 2026-09-26 已通过：Ruff、mypy（strict）、pytest（252 passed）、`research-agent --help`、`python scripts/check_docs.py`。
- 受限环境下 pytest 默认临时目录可能无写权限，可加 `--basetemp <可写目录>`（`CL-08`）。
- 一键本地检查：`uv run python scripts/check_all.py`，执行与 CI 相同的命令组。
## 快速开始

### 环境要求

- Python 3.12 或更新版本。
- [uv](https://docs.astral.sh/uv/)。
- Windows、Linux 或 macOS。

### 初始化

```powershell
uv sync --dev
uv run research-agent doctor
uv run research-agent --help
uv run research-agent research "evidence chain" --sources arxiv,openalex --max-results 5 --download-pdf
```

`research` 默认开启语义相关性过滤，需要环境变量 `DEEPSEEK_API_KEY`；没有密钥时加 `--no-relevance-filter`。加 `--synthesis` 可用模型从已存储证据写 Claim。

### 开发验证

```powershell
uv run ruff check .
uv run mypy src
uv run pytest
python scripts/check_docs.py
```

运行时数据默认写入当前工作目录下的 `data/` 和 `reports/`，请在项目根目录运行命令（改为按项目根目录解析见 `CL-01`）；这两个目录及其内容不提交到 Git。密钥只能来自环境变量或系统凭据管理器。
## 持续集成

GitHub Actions 配置位于 `.github/workflows/ci.yml`。工作流在 Windows、Linux 和 macOS 上执行：

- `uv sync --dev --python 3.12`
- `uv run ruff check .`
- `uv run mypy src`
- `uv run pytest`
- `uv run python scripts/check_docs.py`
- `uv run research-agent --help`

CI 已通过 Windows、Linux 和 macOS 三个平台的首轮验证。

## 独立 MCP server

arXiv MCP server 使用官方 MCP Python SDK，通过 stdio 启动：

```powershell
uv run arxiv-mcp
```

MCP 工具包括 `arxiv_describe`、`arxiv_search_papers`、`arxiv_get_paper`、`arxiv_resolve_open_access` 和 `arxiv_download_pdf`。下载只返回临时 ArtifactRef，不直接写最终归档。

## 文档入口

- [工作规范](AGENTS.md)
- [产品需求](docs/PRD.md)
- [系统架构](docs/architecture.md)
- [MCP 契约](docs/mcp-contract.md)
- [数据模型](docs/data-model.md)
- [评测设计](docs/evaluation.md)
- [路线图](docs/roadmap.md)
- [论文计划](docs/thesis-plan.md)
- [术语表](docs/glossary.md)
- [Pi 调研记录](docs/references/pi-investigation.md)
- [架构决策记录](docs/adr/README.md)

## 当前主线

10 月先修评测口径，再修证据链，不继续扩功能：

```text
批次 1 评测口径（ADR-0015，2026-10-04）
  → 批次 2 证据链正确性（2026-10-18）
  → 批次 3 源站与安全（2026-10-25）
  → 批次 4 命令行与工程（2026-11-01，Agent Core 与证据模型冻结）
  → 批次 5 导出、下载 Policy（2026-11-15，M3 可演示原型）
  → 前端第一版：证据链查看器（2027-01-15，M4）
  → 前端第二版：用户前端（M7 之后，M8）
```

正式评测规模已冻结为 30 题、核心 8 配置、每配置 3 次、共 720 次 Run；评测从 2026-12-01 开始，分两批完成。

在批次 1–4 完成前，不扩展 Web UI、额外源站或 Office 导出。

## 许可证

本项目默认采用 MIT License，详见 [LICENSE](LICENSE)。