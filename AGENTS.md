# AGENTS.md

本文件是本项目的最高层工作约定。后续实现、文档、测试和实验均以本文件为准；若规范与实践冲突，先修改本文件，再调整实现。

## 1. 项目定位

- 项目名称：面向计算机/AI 文献调研的可追溯科研 Agent 框架设计与实现。
- 项目性质：LYY 的本科毕业设计，同时也是可运行的独立 Agent 系统，不是单一 MCP server、插件 demo 或 Pi 二次封装。
- 核心贡献：证据链机制（Claim → Evidence Span → Paper → Source Record*；full_text 证据再关联 File → Document）。
- 支撑贡献：多源 MCP 联邦与路由、Plan-and-Execute Agent Runtime、科研任务评测。
- 参考对象：Pi 框架及其 Skills/MCP 思路可以借鉴；Pi 不是运行时依赖，不直接 fork 后改名为自研框架。
- 实验范围：产品定位面向理工科，但第一版实验收窄到计算机/AI 文献调研。

## 2. 设计原则

1. 问题本质优先：先判断是否真正解决问题，不照搬框架惯例。
2. 确定性优先：检索、去重、下载、归档、状态流转由代码执行；LLM 只介入规划、相关性判断、证据抽取和综合生成。
3. 证据优先：支持性结论必须能追溯到 Paper、Source Record 和 locator；full_text 证据还必须能追溯到 File/Document；无法追溯的内容只能标为推测或待验证。
4. 本地优先：PDF、元数据、笔记和报告默认保存在本地；调用云端模型时明确数据边界。
5. 可评测优先：新增能力必须说明对应指标、baseline 或消融方式，不能只展示 demo。
6. 最小闭环优先：纵向切片优于横向堆模块；先跑通“一个问题 → 多源检索 → 去重 → 候选 → 证据表 → 报告”。
7. 合规优先：只下载开放获取全文或复用用户已有授权的机构会话，不绕过付费墙、验证码和访问控制。

## 3. 范围边界

### v1 必须包含

- 独立 Agent Runtime：状态机 + Plan-and-Execute。
- 自研核心模块：runtime、planner、executor、memory、router、policy、evaluator。
- 源站 MCP：arXiv、OpenAlex、Crossref、Semantic Scholar、DBLP，各自独立 server。
- MCP federation/router：统一 envelope、并行调用、超时、重试、限流、去重、provenance 合并。
- 存储：SQLite + FTS5 + 不可变文件系统。
- 证据链：Claim、Evidence Span、Paper、File 的完整关联。
- 输出：Markdown 证据报告、JSON/CSV 证据表、BibTeX。
- 最小 Web UI：任务状态、来源列表、证据链可视化。按 ADR-0016 作为用户前端的第一版实现；面向普通用户的完整前端（提问、进度、报告、导出）属于 v1 之后。

### v1 明确不做

- 不做多 Agent 协作、自主反思循环或通用 AGI 式规划。
- 不引入向量数据库；FTS5 满足第一版全文检索需求。
- 不接入 CNKI、Google Scholar、IEEE Xplore、ACM DL 的付费全文抓取。
- 不绕过登录、验证码、付费墙或网站访问控制。
- 不把 Zotero/BibTeX 作为主数据库；它们只是导出视图。
- 不把 Word/PDF/PPT 汇报作为第一优先级。

## 4. 目录规范

```text
.
├── .editorconfig                 # 跨编辑器格式约定
├── .gitattributes                # 跨平台换行和二进制文件规则
├── .gitignore
├── AGENTS.md
├── LICENSE                       # 默认 MIT；发布前可调整
├── README.md                     # 项目入口
├── pyproject.toml                # 项目元数据与依赖
├── uv.lock                       # 可复现依赖锁定
├── docs/
│   ├── PRD.md                    # 产品目标、用户、需求、验收标准
│   ├── architecture.md           # 系统架构、模块边界、运行流程
│   ├── mcp-contract.md           # MCP 公共契约与源站适配规范
│   ├── data-model.md             # 核心实体、关系、状态和存储约定
│   ├── evaluation.md             # 数据集、baseline、指标和消融实验
│   ├── roadmap.md                # 开发与评测的里程碑、问题清单和风险控制
│   ├── thesis-plan.md            # 论文计划（学校节点、写作节奏）；默认休眠，与开发计划互不驱动
│   ├── glossary.md               # 统一术语，避免同义词漂移
│   ├── references/               # 外部框架和资料来源
│   │   └── pi-investigation.md
│   └── adr/                      # 架构决策记录
│       ├── README.md
│       └── NNNN-kebab-case.md
├── .github/workflows/ci.yml      # 三平台 CI；修改属于红线
├── src/research_agent/           # Python 包
│   ├── cli.py                   # research / evaluate / warm-cache / doctor 命令
│   ├── identity.py              # 论文身份键：DOI、arXiv ID、arXiv DOI、OpenAlex ID
│   ├── runtime/
│   │   ├── research_service.py  # 七步 Run 编排与 Markdown 报告
│   │   └── enrichment.py        # 缺摘要时按 DOI 从 OpenAlex 补全
│   ├── planner/
│   │   └── planner.py           # 确定性源选择、查询变体和预算计划
│   ├── executor/
│   │   └── executor.py          # PlanStep 状态机、StepAttempt 和重试
│   ├── memory/                  # 空包；v1 边界见 docs/roadmap.md §5 D3
│   ├── router/
│   │   ├── federation.py        # 多源并行搜索、并发预算与部分失败处理
│   │   └── registry.py          # 五源 client registry
│   ├── llm/
│   │   ├── gateway.py           # ModelGateway 协议
│   │   └── deepseek.py          # DeepSeek provider
│   ├── policy/
│   │   └── relevance.py         # 语义相关性判断（ADR-0012）
│   ├── evaluator/
│   │   ├── dataset.py           # JSONL 问题集加载与哈希
│   │   ├── pilot_seed.py        # Pilot 种子问题与 OpenAlex 标注草稿
│   │   ├── runner.py            # EvaluationRun/Case 矩阵调度
│   │   ├── case_runner.py       # 把各系统接到评测回调
│   │   ├── systems.py           # B0–B3、A1–A4、A6 配置
│   │   ├── metrics.py           # 检索、证据、成本指标
│   │   ├── task_completion.py   # baseline-neutral 任务完成 judge
│   │   ├── bm25.py              # 本地 BM25 索引
│   │   ├── b0.py                # B0：BM25 + 单次 LLM
│   │   ├── react.py             # B2：纯 ReAct（ADR-0014）
│   │   └── snapshot.py          # 冻结源站快照
│   ├── evidence/
│   │   ├── claims.py            # Evidence → Claim 与引用校验
│   │   └── synthesis.py         # LLM Claim 综合（synthesis-v1）
│   ├── storage/                 # 迁移、repository、不可变文件归档
│   │   ├── migrations/          # NNNN_*.sql
│   │   ├── migrations.py
│   │   ├── artifacts.py
│   │   ├── evaluation_repository.py
│   │   ├── pdf_parser.py
│   │   └── repository.py
│   ├── mcp_servers/
│   │   ├── common.py            # 公共 envelope、数据模型、重试与限流
│   │   ├── cache.py             # 源站响应缓存（ADR-0013）
│   │   ├── arxiv/               # arXiv 适配与 MCP server
│   │   │   ├── client.py
│   │   │   ├── parser.py
│   │   │   └── server.py
│   │   ├── openalex/            # OpenAlex 适配与 MCP server
│   │   │   ├── client.py
│   │   │   ├── parser.py
│   │   │   └── server.py
│   │   ├── crossref/            # Crossref 适配与 MCP server
│   │   │   ├── client.py
│   │   │   ├── parser.py
│   │   │   └── server.py
│   │   ├── semantic_scholar/    # Semantic Scholar 适配与 MCP server
│   │   │   ├── client.py
│   │   │   ├── parser.py
│   │   │   └── server.py
│   │   └── dblp/                # DBLP 适配与 MCP server
│   │       ├── client.py
│   │       ├── parser.py
│   │       └── server.py
│   └── interfaces/              # 空包；计划放 FastAPI 本地 API（ADR-0016，路线图 FE-02）
├── web/                          # 用户前端（React + Vite + TypeScript，ADR-0016）；尚未创建，见路线图 FE-03
├── tests/
│   ├── fixtures/                # 可公开的脱敏测试响应
│   ├── unit/
│   ├── integration/
│   └── e2e/                     # 尚未创建
├── evaluation/
│   ├── datasets/                # 冻结问题集与 VERSIONS.md
│   ├── corpora/                 # B0 冻结语料
│   ├── snapshots/               # 冻结源站快照
│   ├── review/                  # 金标审阅记录
│   └── results/                 # 结果摘要（Markdown）；原始数据库在 data/
├── configs/                      # 非密钥配置
├── scripts/                      # 开发与运维脚本（check_all、check_docs、金标与快照构建）
├── data/                         # 本地运行数据，禁止提交
├── reports/                      # 生成的报告，默认禁止提交
└── local/                        # 个人与学位材料，禁止提交
```

### 命名约定

- Python 包、模块、函数、变量：`snake_case`。
- Python 类：`PascalCase`。
- 测试文件：`test_<module>.py`。
- 文档：产品文档使用大写缩写文件名；其他文档使用 `kebab-case.md`。
- ADR：`NNNN-kebab-case.md`，编号不跳号、不重复。
- 数据库表、字段：`snake_case`。
- MCP tool：`<source>_<verb>_<object>`，例如 `arxiv_search_papers`；公共 envelope 字段使用 `snake_case`。
- 时间统一存储为 UTC ISO 8601；用户界面和报告可显示 Asia/Shanghai。

## 5. 数据与文件纪律

- `data/`、`reports/`、下载的 PDF、API 缓存和数据库文件不得进入 Git。
- `local/` 存放个人与学位材料（开题报告、论文草稿、导师反馈、评审记录等），
  不得进入 Git。这些材料包含姓名、学号等个人信息，且属于未定稿的学位材料，
  公开发布会带来隐私与学术规范风险。`local/` 只保留 `.gitkeep`，其余内容被忽略。
- 原始 PDF 只追加、不原地覆盖；更新版本时新建文件并保留哈希。
- 每个 Paper 必须通过 `PaperSourceRecord` 关联 `source`、`source_id`、`retrieved_at` 和 provenance。
- 每个 File 必须记录 SHA-256、路径、MIME type、大小和来源 URL。
- 每条 Evidence 必须记录原文片段、locator、抽取方法、置信度、关联 Paper 和 `source_record_id`；full_text 证据还必须关联 File 和 Document。
- 密钥、token、密码只能来自环境变量或系统凭据管理器，不写入代码、数据库、日志或文档。
- 日志默认脱敏；不记录完整 API key、Cookie、Authorization header 或用户私密查询内容。

## 6. 工程流程

1. 规范先行：新增目录、模块或外部接口前，先更新本文件或对应文档。
2. 设计先行：涉及架构、数据模型、MCP 契约、评测方法的改动，先写 ADR 或更新文档。
3. 纵向切片：每次实现尽量交付一个可运行、可测试、可演示的端到端能力。
4. 测试先行：核心逻辑采用 TDD；至少覆盖去重、证据定位、引用约束、权限策略和失败重试。
5. 改动即验证：完成实现后运行格式检查、静态检查、单元测试和相关集成测试。
6. 实验记录：每个里程碑结束后更新 `evaluation/results/` 的实验记录和图表素材。论文写作由 `docs/thesis-plan.md` 单独管理，开发排期不因论文计划调整；论文需要的新实验或修复先在路线图登记编号。
7. 路线图对齐：修复和优化以 `docs/roadmap.md` §4 问题清单为准，提交说明和汇报引用问题编号（如 `EV-01`）；新发现的问题先登记再修，完成后更新状态和验证方式。

### 验证命令

首次环境初始化：

```powershell
uv sync --dev
```

每次实现完成后至少运行：

```powershell
uv run ruff check .
uv run mypy src
uv run pytest
uv run research-agent --help
python scripts/check_docs.py
```

## 7. 红线：必须先获得用户确认

本节约束在本仓库工作的开发者与编码 Agent。运行时 Agent 对最终用户的确认规则见 `docs/PRD.md` §7，两者不混用。

以下操作即使处于 auto-accept 模式，也必须先停下来询问：

1. 不可恢复的删除：删除受版本控制的文件或目录、`data/` 中的数据库与归档、`local/` 中的任何内容，或删除 Git 历史。
2. 丢弃未提交的改动：`git reset --hard`、`git checkout -- <path>`、`git restore`、`git clean`、`git stash drop`。
3. 改写或推送远端：`git push`（含强制推送）、`git rebase`、修改已推送的提交、创建远程仓库。
4. 密钥：修改 `.env`、密钥或 token；读取或输出任何密钥的值（只允许检查是否存在）。
5. CI/CD：修改 `.github/workflows/` 或新增自动化流程。
6. 数据：对已有本地数据库执行迁移或批量改写；修改已冻结的数据集、快照、语料或金标（只能新建版本）。
7. 环境：安装全局依赖、修改系统配置或系统环境变量。
8. 外发数据：把 `local/` 内容或用户私有文件发送给云端模型或第三方服务。
9. 费用：单次任务预计模型调用超过 50 次（如 Pilot 全量重跑、正式评测批次）。
10. 公开发布：部署、发布包、公开发表文章。
11. 规则本身：修改本节，或推翻已接受的 ADR。

不需要确认，但必须在汇报中说明：

- 删除本次会话自己创建、未纳入版本控制的临时文件，以及 `.pytest_cache/`、`.ruff_cache/`、`.mypy_cache/` 等可再生缓存。
- 新增迁移文件并在临时数据库上测试（仍按 ADR-0010 与 §6 先写文档）。
- 新增或升级项目依赖（写入 `pyproject.toml` 与 `uv.lock`）。
- 本地 `git commit`。
- 阈值以内的付费模型调用，汇报调用次数与 token。

确认结果记入 `docs/roadmap.md` §5“已确认”，注明日期与范围；一次确认只覆盖所述范围。

## 8. 汇报格式

- 默认中文；代码、命令、变量名使用英文。
- 结论先行，再给理由；指出风险和取舍，不迎合。
- 汇报必须区分：已完成、已验证、未验证、待用户确认。
- 不声称“完成”或“通过”，除非已经运行对应验证命令并检查输出。

## 9. 可移植性与发布

- 支持 Windows、Linux 和 macOS；实现不得依赖 Windows 专有路径、盘符或 shell 行为。
- 运行时基线为 Python 3.12；依赖使用 `uv` 管理，提交 `pyproject.toml` 和 `uv.lock`，不提交 `.venv/`。
- 受版本控制的文件不得包含本机绝对路径、个人目录、密钥或本地数据库。
- 配置路径相对于项目根目录解析；密钥只能来自环境变量或系统凭据管理器。
- 代码、配置和文档统一使用 UTF-8；跨平台换行规则由 `.gitattributes` 维护。
- 远程仓库、推送、CI/CD 与公开发布的确认规则以 §7 为准。
