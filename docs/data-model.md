# 数据模型与存储设计

| 字段 | 内容 |
|---|---|
| 文档版本 | v0.1 |
| 状态 | 设计基线 |
| 日期 | 2026-09-23 |
| 关联文档 | `docs/architecture.md`, `docs/mcp-contract.md`, `docs/evaluation.md` |

## 1. 设计结论

v1 使用：

- 单个 SQLite 数据库保存实体、关系、状态、审计和 FTS5 索引。
- 文件系统保存不可变 PDF、解析文本、Markdown 笔记和报告。
- 数据库只保存文件路径和哈希，不保存 PDF 二进制。
- Source Record 不可变；Paper 是跨源归一化后的规范实体。
- Claim 必须通过 Evidence Span 关联 Paper 和 Source Record；full_text 证据还必须关联 File 和 Document。
- Zotero、BibTeX、CSV、JSON 都是导出视图，不是主数据源。

## 2. 核心实体关系

```text
Project
  └── ResearchQuestion
        └── Run
              ├── Plan
              │     └── PlanStep
              │           └── StepAttempt
              ├── Query
              │     └── SourceCall
              │           ├── SourceCallAttempt
              │           └── SourceRecord
              ├── Report
              │     └── Claim
              │           └── ClaimEvidence
              │                 └── EvidenceSpan
              │                       ├── Paper
              │                       ├── SourceRecord
              │                       └── Document → File
              ├── Note
              ├── AuditEvent
              └── ModelCall

Paper
  ├── PaperIdentifier
  ├── PaperAuthor → Author
  ├── PaperSourceRecord → SourceRecord
  └── File
        └── Document

EvaluationRun
  ├── EvaluationCase
  └── EvaluationResult
```

## 3. 实体定义

### 3.1 Project

表示一个研究项目或论文课题。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `name` | TEXT | NOT NULL | 项目名 |
| `description` | TEXT | NULL | 项目描述 |
| `domain` | TEXT | NOT NULL | v1 固定为 `cs_ai` |
| `status` | TEXT | NOT NULL | `active`, `archived` |
| `created_at` | TEXT | NOT NULL | UTC ISO 8601 |
| `updated_at` | TEXT | NOT NULL | UTC ISO 8601 |
| `settings_json` | TEXT | NOT NULL | 非密钥项目配置 |

### 3.2 ResearchQuestion

研究问题及其版本。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `project_id` | TEXT | FK | Project |
| `question_text` | TEXT | NOT NULL | 原始问题 |
| `normalized_question` | TEXT | NULL | 归一化问题 |
| `scope_json` | TEXT | NOT NULL | 年份、语言、venue、目标数量等 |
| `version` | INTEGER | NOT NULL | 从 1 开始 |
| `parent_id` | TEXT | NULL | 上一版本 |
| `created_at` | TEXT | NOT NULL | UTC ISO 8601 |

### 3.3 Run

一次完整 Agent 执行。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `project_id` | TEXT | FK | Project |
| `question_id` | TEXT | FK | ResearchQuestion |
| `status` | TEXT | NOT NULL | Run 状态 |
| `trigger` | TEXT | NOT NULL | `cli`, `web`, `evaluation` |
| `config_hash` | TEXT | NOT NULL | 可复现配置哈希 |
| `config_json` | TEXT | NOT NULL | 完整可复现配置快照 |
| `system_version` | TEXT | NOT NULL | 代码版本或 Git commit |
| `environment_json` | TEXT | NULL | Python、依赖、模型和 parser 版本 |
| `started_at` | TEXT | NULL | UTC |
| `finished_at` | TEXT | NULL | UTC |
| `error_code` | TEXT | NULL | 失败原因 |
| `summary_json` | TEXT | NULL | 运行摘要 |

Run 状态：

```text
CREATED
PLANNED
RUNNING
WAITING_CONFIRMATION
PAUSED
COMPLETED
FAILED
CANCELLED
```

### 3.4 Plan

一次 Run 使用的计划。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `run_id` | TEXT | FK | Run |
| `version` | INTEGER | NOT NULL | 重规划时递增 |
| `strategy` | TEXT | NOT NULL | `template`, `llm`, `hybrid` |
| `status` | TEXT | NOT NULL | `draft`, `validated`, `active`, `superseded` |
| `plan_json` | TEXT | NOT NULL | 完整计划快照 |
| `created_at` | TEXT | NOT NULL | UTC |

### 3.5 PlanStep

计划中的可执行步骤。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `plan_id` | TEXT | FK | Plan |
| `step_key` | TEXT | NOT NULL | 计划内唯一 |
| `step_type` | TEXT | NOT NULL | 见下表 |
| `status` | TEXT | NOT NULL | 步骤状态 |
| `depends_on_json` | TEXT | NOT NULL | 依赖 step_key 数组 |
| `input_json` | TEXT | NULL | 输入摘要 |
| `output_json` | TEXT | NULL | 输出摘要 |
| `attempt_count` | INTEGER | NOT NULL | 默认 0 |
| `started_at` | TEXT | NULL | UTC |
| `finished_at` | TEXT | NULL | UTC |
| `error_code` | TEXT | NULL | 失败原因 |
| `checkpoint_json` | TEXT | NULL | 最近一次可恢复检查点 |

Step 类型：

- `build_query`
- `route_sources`
- `search_sources`
- `normalize_results`
- `deduplicate`
- `screen_candidates`
- `acquire_files`
- `parse_documents`
- `extract_evidence`
- `synthesize_claims`
- `validate_citations`
- `generate_report`
- `evaluate_run`

Step 状态：

```text
PENDING
READY
RUNNING
RETRYING
SUCCEEDED
FAILED
SKIPPED
```

### 3.6 Query

系统构造的一次查询。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `run_id` | TEXT | FK | Run |
| `plan_step_id` | TEXT | FK | PlanStep |
| `query_text` | TEXT | NOT NULL | 主查询 |
| `variants_json` | TEXT | NULL | 查询变体 |
| `filters_json` | TEXT | NOT NULL | 规范化过滤条件 |
| `query_hash` | TEXT | NOT NULL | 用于缓存与复现 |
| `created_at` | TEXT | NOT NULL | UTC |

### 3.7 SourceCall

对某个 MCP server 的一次调用。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `run_id` | TEXT | FK | Run |
| `query_id` | TEXT | NULL | FK Query |
| `source` | TEXT | NOT NULL | 源站 ID |
| `tool_name` | TEXT | NOT NULL | MCP 工具名 |
| `request_hash` | TEXT | NOT NULL | 请求哈希 |
| `request_json` | TEXT | NOT NULL | 脱敏请求快照 |
| `status` | TEXT | NOT NULL | `success`, `partial`, `failed` |
| `retry_count` | INTEGER | NOT NULL | 重试次数 |
| `http_status` | INTEGER | NULL | 若适用 |
| `elapsed_ms` | INTEGER | NULL | 耗时 |
| `response_hash` | TEXT | NULL | 响应摘要哈希 |
| `error_code` | TEXT | NULL | 统一错误码 |
| `error_details_json` | TEXT | NULL | 脱敏错误详情 |
| `started_at` | TEXT | NOT NULL | UTC |
| `finished_at` | TEXT | NULL | UTC |

### 3.8 SourceRecord

源站返回的原始记录。不可变。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `source_call_id` | TEXT | FK | SourceCall |
| `source` | TEXT | NOT NULL | 源站 ID |
| `source_record_id` | TEXT | NOT NULL | 源站内 ID |
| `api_endpoint` | TEXT | NOT NULL | 源站 API 端点 |
| `source_version` | TEXT | NULL | 源站记录版本，例如 arXiv v2 |
| `raw_json` | TEXT | NOT NULL | 原始对象 |
| `mapping_version` | TEXT | NOT NULL | 归一化映射版本 |
| `retrieved_at` | TEXT | NOT NULL | UTC |
| `query_hash` | TEXT | NULL | 查询复现 |
| `query_snapshot_json` | TEXT | NULL | 脱敏查询快照 |
| `response_hash` | TEXT | NULL | 原始响应哈希 |
| `content_hash` | TEXT | NOT NULL | raw_json 哈希 |

唯一约束：

```text
UNIQUE(source, source_record_id, content_hash)
```

### 3.9 Paper

跨源归一化后的论文实体。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `canonical_key` | TEXT | UNIQUE | 归一化主键 |
| `title` | TEXT | NOT NULL | 规范标题 |
| `title_normalized` | TEXT | NOT NULL | 用于匹配 |
| `abstract` | TEXT | NULL | 合并后的摘要 |
| `year` | INTEGER | NULL | 发表年份 |
| `publication_date` | TEXT | NULL | ISO 日期 |
| `venue` | TEXT | NULL | 规范 venue |
| `type` | TEXT | NULL | article、conference paper 等 |
| `language` | TEXT | NULL | ISO 639-1 |
| `open_access_status` | TEXT | NULL | gold、green、hybrid、closed、unknown |
| `citation_count` | INTEGER | NULL | 来源相关，不保证跨源一致 |
| `merge_confidence` | REAL | NULL | 0–1 |
| `created_at` | TEXT | NOT NULL | UTC |
| `updated_at` | TEXT | NOT NULL | UTC |

`canonical_key` 生成顺序：

1. `doi:<normalized_doi>`
2. `arxiv:<normalized_arxiv_id_without_version>`
3. `openalex:<id>`
4. `semantic_scholar:<id>`
5. `dblp:<key>`
6. `title_author_year:<hash>`

### 3.10 PaperIdentifier

论文标识符。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `paper_id` | TEXT | FK | Paper |
| `type` | TEXT | NOT NULL | doi、arxiv_id 等 |
| `value` | TEXT | NOT NULL | 原始值 |
| `normalized_value` | TEXT | NOT NULL | 归一化值 |
| `source_record_id` | TEXT | NULL | FK SourceRecord |
| `is_primary` | INTEGER | NOT NULL | 0/1 |

唯一约束：

```text
UNIQUE(type, normalized_value)
```

### 3.11 Author 与 PaperAuthor

Author 保存规范作者实体；PaperAuthor 保存作者与论文的关系。

| Author 字段 | 类型 | 约束 |
|---|---|---|
| `id` | TEXT | PK |
| `name` | TEXT | NOT NULL |
| `name_normalized` | TEXT | NOT NULL |
| `orcid` | TEXT | NULL |
| `source_author_id` | TEXT | NULL |
| `created_at` | TEXT | NOT NULL |

| PaperAuthor 字段 | 类型 | 约束 |
|---|---|---|
| `paper_id` | TEXT | FK |
| `author_id` | TEXT | FK |
| `position` | INTEGER | NOT NULL |
| `is_corresponding` | INTEGER | NULL |

主键：`(paper_id, author_id, position)`。

### 3.12 PaperSourceRecord

Paper 与源站记录的关联，保留合并依据。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `paper_id` | TEXT | FK | Paper |
| `source_record_id` | TEXT | FK | SourceRecord |
| `match_score` | REAL | NULL | 0–1 |
| `merge_reason` | TEXT | NOT NULL | doi、arxiv、title_author 等 |
| `is_primary_metadata` | INTEGER | NOT NULL | 0/1 |

主键：`(paper_id, source_record_id)`。

### 3.13 File

实际获得的 PDF 或其他文献文件。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `paper_id` | TEXT | FK | Paper |
| `kind` | TEXT | NOT NULL | `pdf`, `html`, `text` |
| `sha256` | TEXT | NOT NULL | 文件哈希 |
| `path` | TEXT | NOT NULL | 项目相对路径 |
| `size_bytes` | INTEGER | NOT NULL | 文件大小 |
| `content_type` | TEXT | NOT NULL | MIME type |
| `source_url` | TEXT | NOT NULL | 原始下载地址 |
| `final_url` | TEXT | NULL | 重定向后地址 |
| `retrieved_at` | TEXT | NOT NULL | UTC |
| `license` | TEXT | NULL | 许可信息 |
| `status` | TEXT | NOT NULL | `stored`, `quarantined`, `missing`, `deleted` |
| `created_at` | TEXT | NOT NULL | UTC |

唯一约束：

```text
UNIQUE(paper_id, sha256)
```

文件状态：

- `stored`：已归档且哈希校验通过。
- `quarantined`：下载或解析校验失败，不能用于证据。
- `missing`：数据库有记录但文件不存在。
- `deleted`：经用户确认后删除，只保留审计记录。

### 3.14 Document

PDF 或 HTML 解析后的文本表示。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `file_id` | TEXT | FK | File |
| `parser` | TEXT | NOT NULL | 例如 PyMuPDF、pdfplumber |
| `parser_version` | TEXT | NOT NULL | 解析器版本 |
| `text_path` | TEXT | NOT NULL | 解析文本路径 |
| `text_sha256` | TEXT | NOT NULL | 解析文本哈希 |
| `locator_scheme` | TEXT | NOT NULL | `page_char`, `page_paragraph` 等 |
| `parse_status` | TEXT | NOT NULL | `success`, `partial`, `failed` |
| `created_at` | TEXT | NOT NULL | UTC |

同一个 File 允许多个 Document，但每个 Run 必须固定使用一个 parser 和版本，保证可复现。

### 3.15 EvidenceSpan

证据片段，是证据链的核心。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `paper_id` | TEXT | FK | Paper |
| `source_record_id` | TEXT | FK | SourceRecord；系统生成的证据必需 |
| `document_id` | TEXT | NULL | FK Document；摘要证据可为空 |
| `file_id` | TEXT | NULL | FK File；摘要证据可为空 |
| `quote` | TEXT | NOT NULL | 原文片段 |
| `quote_hash` | TEXT | NOT NULL | 原文哈希 |
| `locator_json` | TEXT | NOT NULL | 位置结构 |
| `evidence_level` | TEXT | NOT NULL | `metadata`, `abstract`, `full_text`, `external` |
| `extraction_method` | TEXT | NOT NULL | `rule`, `pdf_parser`, `llm`, `human` |
| `extractor_version` | TEXT | NULL | 抽取器版本 |
| `confidence` | REAL | NOT NULL | 0–1 |
| `verified` | INTEGER | NOT NULL | 是否重新定位成功 |
| `created_at` | TEXT | NOT NULL | UTC |

locator 示例：

```json
{
  "page": 7,
  "paragraph_index": 3,
  "char_start": 1204,
  "char_end": 1398,
  "section": "4.2 Evaluation",
  "quote_hash": "hex..."
}
```

证据级别：

- `metadata`：只来自元数据，不能支持方法或结论性 Claim。
- `abstract`：来自摘要，可支持高层描述，但不能支持细节数字。
- `full_text`：来自全文，可支持方法、结果和限制。
- `external`：来自网页或其他材料，必须单独标记来源。

### 3.16 Claim

报告中的可验证陈述。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `report_id` | TEXT | FK | Report |
| `claim_text` | TEXT | NOT NULL | 陈述 |
| `claim_type` | TEXT | NOT NULL | fact、comparison、trend、limitation 等 |
| `support_status` | TEXT | NOT NULL | 支持状态 |
| `confidence` | REAL | NOT NULL | 0–1 |
| `created_at` | TEXT | NOT NULL | UTC |

支持状态：

```text
supported
partially_supported
unsupported
disputed
```

约束：

- `supported` 必须至少关联一个 `full_text` 或 `abstract` Evidence Span。
- `unsupported` 必须显式出现在报告中。
- 不允许把 `unsupported` Claim 渲染成普通事实。

### 3.17 ClaimEvidence

Claim 与 Evidence Span 的多对多关系。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `claim_id` | TEXT | FK | Claim |
| `evidence_span_id` | TEXT | FK | EvidenceSpan |
| `relation_type` | TEXT | NOT NULL | `supports`, `refutes`, `context` |
| `rank` | INTEGER | NOT NULL | 展示顺序 |

主键：`(claim_id, evidence_span_id, relation_type)`。

### 3.18 Report

一次 Run 生成的报告版本。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `run_id` | TEXT | FK | Run |
| `version` | INTEGER | NOT NULL | 从 1 开始 |
| `format` | TEXT | NOT NULL | `markdown`, `json`, `csv` |
| `path` | TEXT | NOT NULL | 项目相对路径 |
| `sha256` | TEXT | NOT NULL | 报告哈希 |
| `status` | TEXT | NOT NULL | `draft`, `validated`, `published` |
| `created_at` | TEXT | NOT NULL | UTC |

### 3.19 Export

报告导出视图。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `report_id` | TEXT | FK | Report |
| `format` | TEXT | NOT NULL | bibtex、zotero、csv、json |
| `path` | TEXT | NOT NULL | 导出路径 |
| `sha256` | TEXT | NOT NULL | 文件哈希 |
| `created_at` | TEXT | NOT NULL | UTC |

### 3.20 AuditEvent

所有关键行为的审计记录。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `run_id` | TEXT | NULL | FK Run |
| `actor` | TEXT | NOT NULL | `system`, `user`, `mcp_server` |
| `action` | TEXT | NOT NULL | 动作名 |
| `target_type` | TEXT | NOT NULL | 实体类型 |
| `target_id` | TEXT | NULL | 实体 ID |
| `decision` | TEXT | NULL | `allowed`, `denied`, `confirmed` |
| `details_json` | TEXT | NULL | 脱敏详情 |
| `created_at` | TEXT | NOT NULL | UTC |

### 3.21 ModelCall

LLM 调用记录。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `run_id` | TEXT | NULL | FK Run |
| `provider` | TEXT | NOT NULL | provider |
| `model` | TEXT | NOT NULL | 模型名 |
| `purpose` | TEXT | NOT NULL | planning、extraction 等 |
| `prompt_hash` | TEXT | NOT NULL | prompt 哈希 |
| `prompt_version` | TEXT | NULL | prompt 版本 |
| `response_hash` | TEXT | NULL | 模型响应哈希 |
| `input_tokens` | INTEGER | NULL | 输入 token |
| `output_tokens` | INTEGER | NULL | 输出 token |
| `cost` | REAL | NULL | 估算费用 |
| `latency_ms` | INTEGER | NULL | 延迟 |
| `status` | TEXT | NOT NULL | success、failed |
| `error_code` | TEXT | NULL | 失败原因 |
| `created_at` | TEXT | NOT NULL | UTC |

### 3.22 StepAttempt

PlanStep 的单次执行尝试。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `step_id` | TEXT | FK | PlanStep |
| `attempt_no` | INTEGER | NOT NULL | 从 1 开始 |
| `status` | TEXT | NOT NULL | `running`, `succeeded`, `failed`, `cancelled` |
| `input_json` | TEXT | NULL | 脱敏输入快照 |
| `output_json` | TEXT | NULL | 输出摘要 |
| `checkpoint_json` | TEXT | NULL | 可恢复检查点 |
| `error_code` | TEXT | NULL | 失败原因 |
| `started_at` | TEXT | NOT NULL | UTC |
| `finished_at` | TEXT | NULL | UTC |

唯一约束：

```text
UNIQUE(step_id, attempt_no)
```

### 3.23 SourceCallAttempt

SourceCall 的单次网络尝试。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `source_call_id` | TEXT | FK | SourceCall |
| `attempt_no` | INTEGER | NOT NULL | 从 1 开始 |
| `status` | TEXT | NOT NULL | `running`, `succeeded`, `failed`, `retrying` |
| `http_status` | INTEGER | NULL | 若适用 |
| `elapsed_ms` | INTEGER | NULL | 耗时 |
| `retry_after_ms` | INTEGER | NULL | 源站要求的等待时间 |
| `error_code` | TEXT | NULL | 统一错误码 |
| `error_details_json` | TEXT | NULL | 脱敏错误详情 |
| `started_at` | TEXT | NOT NULL | UTC |
| `finished_at` | TEXT | NULL | UTC |

唯一约束：

```text
UNIQUE(source_call_id, attempt_no)
```

### 3.24 Note

本地 Markdown 笔记的元数据和 FTS5 索引内容。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `project_id` | TEXT | FK | Project |
| `paper_id` | TEXT | NULL | FK Paper |
| `run_id` | TEXT | NULL | FK Run |
| `title` | TEXT | NOT NULL | 笔记标题 |
| `path` | TEXT | NOT NULL | 项目相对路径 |
| `sha256` | TEXT | NOT NULL | 文件哈希 |
| `body_text` | TEXT | NULL | 用于 FTS5 的正文副本 |
| `created_at` | TEXT | NOT NULL | UTC |
| `updated_at` | TEXT | NOT NULL | UTC |

### 3.25 EvaluationRun

一次批量评测运行。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `dataset_version` | TEXT | NOT NULL | 问题集版本 |
| `dataset_hash` | TEXT | NOT NULL | 问题集哈希 |
| `system_version` | TEXT | NOT NULL | 代码版本或 Git commit |
| `config_json` | TEXT | NOT NULL | 评测配置快照 |
| `status` | TEXT | NOT NULL | `created`, `running`, `completed`, `failed` |
| `started_at` | TEXT | NULL | UTC |
| `finished_at` | TEXT | NULL | UTC |
| `summary_json` | TEXT | NULL | 聚合摘要 |

### 3.26 EvaluationCase

一个评测配置在单个问题上的单次运行。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `evaluation_run_id` | TEXT | FK | EvaluationRun |
| `question_id` | TEXT | NOT NULL | 正式问题 ID |
| `system_id` | TEXT | NOT NULL | B0、B1、B2、B3、A1–A4 |
| `run_number` | INTEGER | NOT NULL | 从 1 开始 |
| `research_run_id` | TEXT | NULL | FK Run |
| `status` | TEXT | NOT NULL | `pending`, `running`, `completed`, `failed` |
| `metrics_json` | TEXT | NULL | 自动指标 |
| `error_code` | TEXT | NULL | 失败原因 |
| `created_at` | TEXT | NOT NULL | UTC |

唯一约束：

```text
UNIQUE(evaluation_run_id, question_id, system_id, run_number)
```

### 3.27 EvaluationResult

单个评测指标的明细结果。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | TEXT | PK | UUID |
| `evaluation_case_id` | TEXT | FK | EvaluationCase |
| `metric_name` | TEXT | NOT NULL | 指标名 |
| `metric_value` | REAL | NULL | 指标值 |
| `metric_unit` | TEXT | NULL | 单位 |
| `details_json` | TEXT | NULL | 明细和置信区间 |
| `created_at` | TEXT | NOT NULL | UTC |

唯一约束：

```text
UNIQUE(evaluation_case_id, metric_name)
```

## 4. 数据不变量

1. 每个 Claim 必须属于一个 Report。
2. `supported` Claim 必须至少有一个 Evidence Span。
3. 每条系统生成的 Evidence Span 必须关联 Paper 和 Source Record。
4. `metadata` 和 `abstract` Evidence Span 必须关联 Source Record，但不要求 File 和 Document。
5. `full_text` Evidence Span 必须同时关联 Source Record、File 和 Document。
6. Evidence Span 的 Paper 必须与 File 的 Paper 一致。
7. File 的 SHA-256 必须与磁盘文件一致。
8. Source Record 一旦写入不得原地修改；重新抓取产生新记录。
9. Paper 合并不得删除任何 Source Record。
10. 删除 File 只改变状态并写 AuditEvent，不物理删除数据库记录。
11. 报告中的引用必须能解析到 Paper 和 Evidence Span。
12. 缓存、摘要和模型输出不能替代原始证据。
13. 所有时间使用 UTC 存储。
14. 所有项目文件路径必须位于项目根目录内，禁止路径穿越。
15. Run 的配置快照、代码版本和运行环境必须保留。
16. ModelCall 必须保留响应哈希或失败原因，保证模型调用可审计。

## 5. SQLite 与 FTS5

### 5.1 数据库位置

```text
data/research_agent.db
```

单用户、单项目 v1 也使用单数据库 + `project_id` 隔离，便于后续扩展多个项目。

### 5.2 FTS5 索引

至少建立：

- `paper_fts(title, abstract, venue, authors_text)`
- `evidence_fts(quote, section, paper_title)`
- `note_fts(title, body_text)`

FTS5 用于本地候选检索、证据复查和笔记搜索，不用于替代源站检索。

### 5.3 索引一致性

- 实体更新后同步更新 FTS5。
- 重新解析 Document 时旧 Evidence Span 必须保留或标记失效，不能静默覆盖。
- 重建索引必须可重复执行，且不改变原始实体。

## 6. 文件系统布局

```text
data/
├── research_agent.db
├── cache/
│   ├── metadata/
│   └── downloads/
└── projects/
    └── <project_id>/
        ├── project.json
        ├── papers/
        │   └── <sha256>.pdf
        ├── parsed/
        │   └── <document_id>.jsonl
        ├── notes/
        │   └── <paper_id>.md
        └── quarantine/
            └── <artifact_id>/

reports/
└── <project_id>/
    └── <run_id>/
        ├── report.md
        ├── evidence.json
        ├── evidence.csv
        └── references.bib
```

### 6.1 文件命名

- PDF：内容哈希，例如 `a3f5...pdf`。
- 解析文本：`<document_id>.jsonl`。
- 笔记：`<paper_id>.md`。
- 报告：固定名称 + 版本目录或版本字段。
- 临时下载：`data/cache/downloads/<artifact_id>.part`。

### 6.2 原子写入

1. 下载到 `.part` 文件。
2. 计算 SHA-256。
3. 校验 MIME type、大小和 Policy。
4. `fsync` 后原子重命名。
5. 写入数据库 File 记录。
6. 若数据库写入失败，移动文件到 quarantine 并记录错误。

## 7. 数据保留与清理

- Source Record 和 AuditEvent 默认永久保留。
- 元数据缓存可设置 TTL。
- 下载缓存可在文件成功归档后清理。
- 用户可清理缓存，但清理不得删除已归档论文和证据。
- 删除原始文献、项目或数据库必须人工确认。
- 删除操作只做逻辑删除，除非用户明确要求物理删除。

## 8. 迁移策略

- schema 变更必须先写 ADR 和迁移方案，并获得用户确认。
- 每次迁移必须有版本号、前向脚本、回滚策略和备份路径。
- 迁移前备份 SQLite 数据库。
- 迁移脚本不得修改不可变 Source Record 和已归档文件。
- 迁移完成后运行完整性和引用链校验。

## 9. 数据导出

### BibTeX

- 从 Paper、Author、Venue 和 PaperIdentifier 生成。
- 缺失字段使用稳定占位，不伪造 DOI。
- 导出文件记录生成时间和来源 Run。

### JSON/CSV 证据表

至少包含：

```text
claim_id
claim_text
support_status
paper_id
paper_title
doi
arxiv_id
file_sha256
evidence_id
quote
locator
evidence_level
extraction_method
confidence
source
retrieved_at
```

### Zotero

- 作为外部视图导出，不参与主键和证据链。
- 导出前检查重复项和缺失元数据。
