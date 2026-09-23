# 面向计算机/AI 文献调研的可追溯科研 Agent 框架

当前仓库处于设计基线阶段。项目目标是实现一个独立的科研助理 Agent，完成调研、查询、下载、归档和汇报，并以 `Claim → Evidence Span → Paper → Source Record*` 的证据链作为论文主贡献；`full_text` 证据再关联 `File → Document`。

Pi 仅作为设计参考，不进入运行时依赖。系统采用独立 Agent Core、每源独立 MCP server、自研 Federation/Router、SQLite + FTS5 + 文件系统。

## 当前状态

- 已完成：工作规范、PRD、架构、MCP 契约、数据模型、评测方案、路线图、术语表、ADR、Pi 调研记录、文档结构校验脚本、Python 3.12 + uv 最小脚手架、跨平台项目规则、GitHub Actions 配置、SQLite 初始 schema 和迁移 runner。
- M1 已实现：arXiv MCP server、arXiv Atom 解析、SourceRecord/Paper/EvidenceSpan 持久化、CLI 纵向流程和 Markdown 报告。
- M3 已实现第三站：Crossref、Semantic Scholar 和 DBLP MCP server（元数据、citations/references、领域书目）。
- M2 已实现：OpenAlex MCP server（含 citations/references）、并行 Federation、DOI 跨源合并、双源 provenance 保留、双源 CLI、Evidence → Claim 构建与引用校验、限流/网络错误的有界重试与 `Retry-After` 支持，以及内容寻址 PDF 归档、Document 解析、full-text Evidence 和 File provenance。
- 未完成：真实 arXiv smoke test 当前被 429 限流阻断；Agent Core、Claim 综合、评测和实验尚未开始。
- 已通过：Ruff、mypy、pytest（72 passed）、`research-agent research --help` 和 `python scripts/check_docs.py`。
- 文档校验：`python scripts/check_docs.py`。
- 当前阶段：M1，arXiv 单源纵向闭环。
- 论文定稿：2027-03-19 17:00。
- 答辩：2027-04-10。

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

### 开发验证

```powershell
uv run ruff check .
uv run mypy src
uv run pytest
python scripts/check_docs.py
```

运行时数据默认写入项目根目录下的 `data/` 和 `reports/`；这两个目录及其内容不提交到 Git。密钥只能来自环境变量或系统凭据管理器。
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
- [术语表](docs/glossary.md)
- [Pi 调研记录](docs/references/pi-investigation.md)
- [架构决策记录](docs/adr/README.md)

## 第一项实现目标

先完成 arXiv 单源纵向闭环；M1 通过后再扩展到 arXiv + OpenAlex 双源闭环。

```text
一个问题
  → arXiv 查询
  → 保存 Source Record
  → Paper + provenance
  → 最小 Markdown 报告
```

正式评测规模已冻结为 30 题、核心 8 配置、每配置 3 次、共 720 次 Run；评测从 2026-12-01 开始，分两批完成。

在最小闭环通过测试和端到端验证前，不扩展 Web UI、额外源站或 Office 导出。

## 许可证

本项目默认采用 MIT License，详见 [LICENSE](LICENSE)。