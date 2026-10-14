# 本地只读 API 契约

| 字段 | 内容 |
|---|---|
| 文档版本 | v1 |
| 状态 | 第一版契约；只读服务已实现（FE-02） |
| 日期 | 2026-10-14 |
| 关联文档 | `docs/adr/0016-user-frontend-spa.md`, `docs/data-model.md`, `docs/glossary.md` |

本文件约束证据链查看器要调用的 HTTP API。它不是 MCP server，也不是 CLI。
第一版只读：不提交研究问题、不取消任务、不下载导出文件、不发起人工确认。
那些接口属于 `FE-05` 及之后。

实现放在 `src/research_agent/interfaces/`，复用已有 repository。默认只监听
`127.0.0.1`。CORS 只允许本地前端来源。本文件不启动服务。

## 1. 版本

- 路径前缀为 `/v1`。
- 每个 JSON 响应都包含 `api_version`，第一版的值是 `"v1"`。
- 破坏字段含义或删除字段时递增版本，不在 `/v1` 里悄悄改语义。

## 2. 通用约定

- 请求和响应都是 JSON，`Content-Type` 为 `application/json; charset=utf-8`。
- 字段名使用 `snake_case`，与 `docs/glossary.md` 和 `docs/data-model.md` 一致。
- 时间是 UTC ISO 8601 字符串。未知时间用 `null`，不用空字符串。
- 标识符沿用数据库中的 UUID 或源站标识，不另造一套 ID。
- `file.path` 和 `document.text_path` 只返回项目相对 POSIX 路径。
- 响应不包含 API key、Cookie、Authorization、`config_json`、`environment_json`、
  `raw_json`、检查点或本机绝对路径。
- 前端不得根据响应自行生成或改写 Evidence Span。

## 3. 分页

列表接口接受查询参数：

| 参数 | 默认 | 约束 |
|---|---:|---|
| `limit` | 20 | 整数，1 到 100 |
| `offset` | 0 | 整数，大于等于 0 |

```json
{
  "api_version": "v1",
  "items": [],
  "limit": 20,
  "offset": 0,
  "total": 0
}
```

`items` 按资源规定的顺序排列。`total` 是过滤前的总条数，不是本页条数。

## 4. 错误

失败响应仍包含 `api_version`。`error.message` 是给界面看的短句，不包含堆栈、密钥或绝对路径。

```json
{
  "api_version": "v1",
  "error": {
    "code": "not_found",
    "message": "run not found"
  }
}
```

| HTTP | `error.code` | 何时使用 |
|---:|---|---|
| 400 | `invalid_request` | 分页参数或路径参数不合法 |
| 404 | `not_found` | Run、Claim、Evidence Span、Paper、Source Record、File 或 Document 不存在 |
| 500 | `internal_error` | 未预期的服务器错误；`message` 固定为 `internal error` |

## 5. 资源

### 5.1 Run

`GET /v1/runs`

按 `started_at` 降序，没有开始时间的排在后面。列表项：

| 字段 | 说明 |
|---|---|
| `id` | Run |
| `question_text` | Research Question 的原文 |
| `status` | `CREATED`、`PLANNED`、`RUNNING`、`WAITING_CONFIRMATION`、`PAUSED`、`COMPLETED`、`FAILED`、`CANCELLED` |
| `trigger` | `cli`、`web`、`evaluation` |
| `started_at` | UTC 或 `null` |
| `finished_at` | UTC 或 `null` |
| `error_code` | 失败原因或 `null` |
| `paper_count` | 该 Run 关联的 Paper 数 |
| `evidence_count` | Evidence Span 数 |
| `claim_count` | Claim 数 |

`GET /v1/runs/{run_id}` 在列表项之外增加 `project_id` 和 `question_id`。

### 5.2 Plan 步骤

`GET /v1/runs/{run_id}/steps`

使用该 Run 当前 Plan 的步骤，按执行顺序排列。不分页。

| 字段 | 说明 |
|---|---|
| `id` | Plan Step |
| `step_key` | 稳定步骤键 |
| `step_type` | 步骤类型 |
| `status` | `PENDING`、`READY`、`RUNNING`、`RETRYING`、`SUCCEEDED`、`FAILED`、`SKIPPED` |
| `depends_on` | 依赖的 `step_key` 数组 |
| `attempt_count` | 已尝试次数 |
| `started_at` | UTC 或 `null` |
| `finished_at` | UTC 或 `null` |
| `error_code` | 失败原因或 `null` |

### 5.3 来源

`GET /v1/runs/{run_id}/sources`

每个 Source 一项，按 `source` 字母序。不分页。

| 字段 | 说明 |
|---|---|
| `source` | 源站标识，如 `arxiv` |
| `call_count` | Source Call 数 |
| `success_count` | `status` 为 `success` 的调用数 |
| `failed_count` | `status` 为 `failed` 的调用数 |
| `paper_count` | 该源站记录合并进的 Paper 数 |

### 5.4 候选论文

`GET /v1/runs/{run_id}/papers`

包含被相关性过滤留下的记录。分页。排序为入库顺序。

| 字段 | 说明 |
|---|---|
| `id` | Paper |
| `title` | 标题 |
| `year` | 整数或 `null` |
| `venue` | 会议或期刊，没有则为 `null` |
| `doi` | 没有则为 `null`，不编造 |
| `arxiv_id` | 没有则为 `null` |
| `canonical_key` | 论文身份键 |
| `open_access_status` | `gold`、`green`、`hybrid`、`closed`、`unknown` 或 `null` |
| `source_record_ids` | 关联的 Source Record `id` 数组 |
| `relevance` | 见下表 |

`relevance`：

| 字段 | 说明 |
|---|---|
| `decision` | `allowed`、`denied` 或 `not_judged` |
| `reason` | 判断理由；未判断时为 `null` |
| `domain_scope` | 领域范围；未判断时为 `null` |
| `answer_role` | 回答角色；未判断时为 `null` |

`GET /v1/papers/{paper_id}` 返回同一对象。它不限于某一个 Run。

### 5.5 Claim

`GET /v1/runs/{run_id}/claims`

该 Run 最新报告中的 Claim，按 `created_at` 升序。分页。

| 字段 | 说明 |
|---|---|
| `id` | Claim |
| `report_id` | Report |
| `claim_text` | 陈述 |
| `claim_type` | 如 `fact` |
| `support_status` | `supported`、`partially_supported`、`unsupported`、`disputed` |
| `confidence` | 0 到 1 |
| `evidence_span_ids` | 按展示顺序排列的 Evidence Span `id` |

`GET /v1/claims/{claim_id}` 返回同一对象。

### 5.6 Evidence Span

`GET /v1/evidence-spans/{evidence_span_id}`

| 字段 | 说明 |
|---|---|
| `id` | Evidence Span |
| `paper_id` | Paper |
| `source_record_id` | 提供这段证据的 Source Record |
| `quote` | 原文片段 |
| `locator` | 对象，不是字符串；可含 `page`、`paragraph_index`、`char_start`、`char_end`、`section` |
| `evidence_level` | `metadata`、`abstract`、`full_text`、`external` |
| `extraction_method` | `rule`、`pdf_parser`、`llm`、`human` |
| `confidence` | 0 到 1 |
| `verified` | 布尔值；数据库中的 0/1 在这里变成 `false`/`true` |
| `file_id` | `full_text` 时必有，否则 `null` |
| `document_id` | `full_text` 时必有，否则 `null` |

### 5.7 Source Record

`GET /v1/source-records/{source_record_id}`

| 字段 | 说明 |
|---|---|
| `id` | Source Record |
| `source` | 源站 |
| `source_record_id` | 源站侧标识 |
| `retrieved_at` | UTC |
| `api_endpoint` | 源站端点 |

不返回 `raw_json`。

### 5.8 File

`GET /v1/files/{file_id}`

| 字段 | 说明 |
|---|---|
| `id` | File |
| `paper_id` | Paper |
| `kind` | `pdf`、`html`、`text` |
| `sha256` | 文件哈希 |
| `path` | 项目相对路径；隔离且未落盘时为空字符串 |
| `size_bytes` | 字节数 |
| `content_type` | MIME type |
| `source_url` | 下载来源 URL |
| `retrieved_at` | UTC |
| `status` | `stored`、`quarantined`、`missing`、`deleted` |

### 5.9 Document

`GET /v1/documents/{document_id}`

| 字段 | 说明 |
|---|---|
| `id` | Document |
| `file_id` | File |
| `parser` | 解析器 |
| `parser_version` | 解析器版本 |
| `text_path` | 项目相对路径 |
| `locator_scheme` | 如 `page_paragraph` |
| `parse_status` | `success`、`partial`、`failed` |

## 6. 证据链怎么读

查看器从 Claim 开始，只使用上面的字段，不补写证据：

1. `GET /v1/runs/{run_id}/claims` 取得 `evidence_span_ids`。
2. `GET /v1/evidence-spans/{evidence_span_id}` 取得 `quote`、`locator`、`paper_id` 和 `source_record_id`。
3. `GET /v1/papers/{paper_id}` 与 `GET /v1/source-records/{source_record_id}` 完成到 Paper 和 Source Record 的追溯。
4. 仅当 `evidence_level` 为 `full_text` 时，再读 `file_id` 与 `document_id`。

候选列表里的 `relevance.decision = denied` 表示论文被过滤，仍然可以查看，但不应当被画成被 Claim 引用的证据。
