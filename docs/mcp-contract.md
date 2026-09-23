# MCP 契约与源站适配规范

| 字段 | 内容 |
|---|---|
| 文档版本 | v0.1 |
| 状态 | 设计基线 |
| 日期 | 2026-09-23 |
| 关联文档 | `docs/architecture.md`, `docs/data-model.md` |

## 1. 契约目标

本规范定义五个源站 MCP server 的公共边界，同时保留各源站原生能力差异。

核心原则：

1. 每个源站独立实现 MCP server。
2. 公共 envelope 只保证联邦层可处理，不强行抹平源站字段。
3. 源站原始记录必须保留在 `raw` 或 Source Record 中。
4. 去重、冲突合并和 provenance 合并属于 Federation，不属于单个 MCP server。
5. 不支持的 capability 必须明确返回，不得用空结果伪装成功。
6. 下载行为必须经过 Policy，且 MCP server 不直接写入最终归档。

## 2. 协议与版本

- 协议：Model Context Protocol，使用官方 Python SDK。
- 传输：v1 使用 stdio 或本地进程通信。
- 编码：JSON-RPC 2.0。
- 公共 envelope 版本：`schema_version = "1.0"`。
- 时间：UTC ISO 8601，例如 `2026-09-23T02:09:37Z`。
- 标识符：使用字符串，不把 DOI 或 arXiv ID 当整数。
- 分页：统一使用 cursor，不假设所有源站支持 offset。
- 错误：统一错误码 + 源站原始错误摘要。

## 3. Capability Manifest

每个 server 启动后必须提供 `<source>_describe`，返回能力声明：

```json
{
  "schema_version": "1.0",
  "source_id": "openalex",
  "display_name": "OpenAlex",
  "source_type": "metadata_index",
  "api_version": "2026-09",
  "capabilities": {
    "search_papers": true,
    "get_paper": true,
    "get_abstract": true,
    "get_citations": true,
    "get_references": true,
    "resolve_open_access": true,
    "download_pdf": false,
    "author_disambiguation": true
  },
  "supported_identifiers": ["doi", "openalex_id", "pmid", "arxiv_id"],
  "rate_limit": {
    "requests_per_second": 5,
    "burst": 10
  },
  "auth_required": false,
  "data_license": "CC0 for metadata; source-specific for full text",
  "notes": ["Full text is not hosted by OpenAlex."]
}
```

manifest 还必须记录 `protocol_version`、`sdk_version` 和 `upstream_api_version`，并声明 `max_limit`。示例中的 `api_version` 仅表示上游 API 版本。

### 3.1 源站类型

| `source_type` | 含义 | 示例 |
|---|---|---|
| `preprint_repository` | 托管预印本全文 | arXiv |
| `metadata_index` | 元数据和引文图谱 | OpenAlex、Semantic Scholar |
| `metadata_registry` | DOI 与注册元数据 | Crossref |
| `bibliography_database` | 领域书目数据库 | DBLP |

### 3.2 v1 能力矩阵

| 能力 | arXiv | OpenAlex | Crossref | Semantic Scholar | DBLP |
|---|---:|---:|---:|---:|---:|
| `search_papers` | 是 | 是 | 是 | 是 | 是 |
| `get_paper` | 是 | 是 | 是 | 是 | 是 |
| `get_abstract` | 是 | 是 | 部分 | 是 | 否 |
| `get_citations` | 否 | 是 | 部分 | 是 | 否 |
| `get_references` | 否 | 是 | 是 | 是 | 否 |
| `resolve_open_access` | 是 | 是 | 部分 | 是 | 否 |
| `download_pdf` | 是 | 否 | 否 | 部分 | 否 |
| `author_disambiguation` | 部分 | 是 | 部分 | 是 | 是 |

“部分”必须在响应中给出原因，例如 `not_supported`、`not_available` 或 `requires_external_resolution`。

`get_abstract` 是逻辑能力；若工具清单中没有独立工具，则由 `<source>_get_paper` 的 `include=["abstract"]` 提供。

## 4. 公共工具集合

工具名统一使用 `<source>_<verb>_<object>`。每个 server 只需实现自己声明为 `true` 的工具；调用未声明工具时返回 `capability_not_supported`。

### 4.1 必备工具

| 工具 | 作用 | 所有源站 |
|---|---|---:|
| `<source>_describe` | 返回 capability manifest | 是 |
| `<source>_search_papers` | 搜索论文 | 是 |
| `<source>_get_paper` | 按标识符获取单篇论文 | 是 |

### 4.2 可选工具

| 工具 | 作用 |
|---|---|
| `<source>_get_citations` | 获取引用该论文的记录 |
| `<source>_get_references` | 获取该论文引用的记录 |
| `<source>_resolve_open_access` | 解析开放获取地址 |
| `<source>_download_pdf` | 下载 PDF 到临时区域并返回 ArtifactRef |

### 4.3 v1 工具清单

```text
arxiv_describe
arxiv_search_papers
arxiv_get_paper
arxiv_resolve_open_access
arxiv_download_pdf

openalex_describe
openalex_search_papers
openalex_get_paper
openalex_get_citations
openalex_get_references
openalex_resolve_open_access

crossref_describe
crossref_search_papers
crossref_get_paper
crossref_get_references
crossref_resolve_open_access

semantic_scholar_describe
semantic_scholar_search_papers
semantic_scholar_get_paper
semantic_scholar_get_citations
semantic_scholar_get_references
semantic_scholar_resolve_open_access

dblp_describe
dblp_search_papers
dblp_get_paper
```

## 5. 查询请求模型

### 5.1 `search_papers` 请求

```json
{
  "schema_version": "1.0",
  "request_id": "req_01J...",
  "query": {
    "text": "multimodal retrieval augmented generation evaluation",
    "variants": [
      "multimodal RAG evaluation",
      "vision language retrieval augmented generation benchmark"
    ],
    "filters": {
      "year_from": 2022,
      "year_to": 2026,
      "languages": ["en"],
      "venues": [],
      "authors": [],
      "open_access_only": false
    },
    "sort": "relevance",
    "limit": 20,
    "cursor": null
  }
}
```

字段规则：

- `text` 必填，长度由 server 限制并在 manifest 中声明。
- `variants` 是联邦层构造的补充查询；若 server 执行 variants，必须合并为单一结果集和单一 cursor，否则由 Federation 分别调用。
- 不支持的 filter 必须返回 `unsupported_filter`，不能静默忽略。
- `sort` 支持 `relevance`、`date_desc`、`citations_desc`；不支持时明确报错。
- `limit` 必须受源站上限约束。

### 5.2 `get_paper` 请求

```json
{
  "schema_version": "1.0",
  "request_id": "req_01J...",
  "identifier": {
    "type": "doi",
    "value": "10.1145/xxxxx"
  },
  "include": ["metadata", "abstract", "open_access"]
}
```

支持的 identifier type 以 manifest 为准：

- `doi`
- `arxiv_id`
- `openalex_id`
- `semantic_scholar_id`
- `dblp_key`
- `title_author`（仅作为降级匹配，必须返回匹配分数）

### 5.3 `resolve_open_access` 请求

```json
{
  "schema_version": "1.0",
  "request_id": "req_01J...",
  "identifier": {
    "type": "doi",
    "value": "10.xxxx/xxxxx"
  }
}
```

### 5.4 `download_pdf` 请求

```json
{
  "schema_version": "1.0",
  "request_id": "req_01J...",
  "identifier": {
    "type": "arxiv_id",
    "value": "2407.18940"
  },
  "expected_url": "https://arxiv.org/pdf/2407.18940",
  "policy_context": {
    "allowed_domains": ["arxiv.org"],
    "max_bytes": 52428800,
    "timeout_seconds": 60
  }
}
```

规则：

- `expected_url` 必须与解析出的最终 URL 同域或属于显式允许域。
- 重定向后必须重新校验域名。
- 不跟随到非白名单域。
- 文件大小、MIME type 和超时必须校验。
- `allowed_domains` 只是调用方提示，server 必须使用自身配置的 allowlist 做最终校验。
- server 只写入临时目录，返回 ArtifactRef。
- 最终归档路径由 Agent Storage 决定。

## 6. 公共响应 Envelope

### 6.1 成功响应

```json
{
  "ok": true,
  "schema_version": "1.0",
  "request_id": "req_01J...",
  "source": "openalex",
  "source_api": "works",
  "retrieved_at": "2026-09-23T02:09:37Z",
  "items": [
    {
      "source_record_id": "W123456789",
      "identifiers": {
        "doi": "10.xxxx/xxxxx",
        "arxiv_id": null,
        "openalex_id": "W123456789",
        "semantic_scholar_id": null,
        "dblp_key": null
      },
      "title": "Paper title",
      "authors": [
        {
          "name": "Alice Example",
          "orcid": null,
          "source_author_id": "A123"
        }
      ],
      "year": 2025,
      "venue": "Example Conference",
      "abstract": "Abstract text if available.",
      "urls": {
        "landing": "https://example.org/paper",
        "pdf": "https://example.org/paper.pdf"
      },
      "open_access": {
        "is_oa": true,
        "status": "gold",
        "license": "CC-BY",
        "url": "https://example.org/paper.pdf"
      },
      "provenance": {
        "source": "openalex",
        "source_record_id": "W123456789",
        "retrieved_at": "2026-09-23T02:09:37Z",
        "api_endpoint": "https://api.openalex.org/works/W123456789"
      },
      "raw": {}
    }
  ],
  "page": {
    "cursor": "next_cursor",
    "total": 123,
    "has_more": true
  },
  "diagnostics": {
    "elapsed_ms": 432,
    "retry_count": 0,
    "warnings": []
  }
}
```

### 6.2 错误响应

```json
{
  "ok": false,
  "schema_version": "1.0",
  "request_id": "req_01J...",
  "source": "semantic_scholar",
  "retrieved_at": "2026-09-23T02:09:37Z",
  "error": {
    "code": "rate_limited",
    "message": "Rate limit exceeded",
    "retryable": true,
    "retry_after_ms": 1500,
    "source_error": {
      "status": 429,
      "body_excerpt": "Too many requests"
    }
  },
  "diagnostics": {
    "elapsed_ms": 812,
    "retry_count": 2,
    "warnings": []
  }
}
```

### 6.3 统一错误码

| 错误码 | 可重试 | 含义 |
|---|---:|---|
| `invalid_request` | 否 | 请求参数不符合契约 |
| `unsupported_filter` | 否 | 源站不支持指定过滤条件 |
| `capability_not_supported` | 否 | 未声明该能力 |
| `not_found` | 否 | 标识符或论文不存在 |
| `auth_required` | 否 | 缺少凭据 |
| `forbidden` | 否 | 策略或源站拒绝 |
| `rate_limited` | 是 | 触发限流 |
| `timeout` | 是 | 请求超时 |
| `upstream_unavailable` | 是 | 源站 5xx 或临时不可用 |
| `network_error` | 是 | 网络错误 |
| `parse_error` | 否 | 响应无法按源站 schema 解析 |
| `download_rejected` | 否 | 下载不满足 Policy |
| `internal_error` | 否 | server 内部错误；若为暂时性上游问题，应映射为 `upstream_unavailable` |

`source_error.body_excerpt` 必须截断并脱敏，不得包含 Cookie、Authorization 或密钥。

## 7. ArtifactRef 契约

`download_pdf` 成功时返回：

```json
{
  "ok": true,
  "schema_version": "1.0",
  "request_id": "req_01J...",
  "source": "arxiv",
  "artifact": {
    "artifact_id": "art_01J...",
    "artifact_uri": "artifact://arxiv/2407.18940",
    "filename": "2407.18940.pdf",
    "content_type": "application/pdf",
    "size_bytes": 1234567,
    "sha256": "hex...",
    "source_url": "https://arxiv.org/pdf/2407.18940",
    "final_url": "https://arxiv.org/pdf/2407.18940",
    "retrieved_at": "2026-09-23T02:09:37Z",
    "license": "arXiv license"
  }
}
```

`artifact_uri` 是受控句柄；本地 stdio 实现可以解析为配置的临时目录，不把绝对主机路径作为公共契约。

Agent Storage 必须：

1. 检查文件存在、大小和 MIME type。
2. 重新计算 SHA-256，确认与 ArtifactRef 一致。
3. 按内容寻址或项目规则生成最终路径。
4. 原子移动到最终归档目录。
5. 写入 File 实体和审计事件。
6. 清理或按策略保留临时文件。

## 8. Provenance 与 Source Record

每个源站记录必须保留：

- `source`
- `source_record_id`
- `retrieved_at`
- `api_endpoint`
- `query_hash` 或 `query_snapshot`
- `raw` 源站原始对象
- `mapping_version`

Federation 合并规则：

1. 有 DOI 时按 DOI 归一化。
2. 无 DOI 但有 arXiv ID 时按 arXiv ID。
3. 无稳定标识符时使用标题 + 年份 + 作者相似度，并保留 `match_score`。
4. 合并后的 Paper 保留全部 Source Record。
5. 冲突字段保留候选值和来源，不静默覆盖。
6. `raw` 不直接进入报告，只用于审计和重新归一化。

## 9. 源站适配要求

### 9.1 arXiv

- 搜索使用官方 API 或合规接口。
- 下载只允许开放获取 PDF。
- 保留 arXiv ID、版本号、分类、更新时间和 license。
- 解析 arXiv 版本时不得把 v1 和 v2 错误合并为同一版本。

### 9.2 OpenAlex

- 负责元数据、作者、机构、引用和开放获取位置。
- 不把 OpenAlex 的 `is_oa` 等同于本地已有 PDF。
- 保留 work ID、DOI、OA status 和 license。

### 9.3 Crossref

- 以 DOI 元数据为准，但不假设摘要完整。
- 记录 publisher、type、container-title、issued date。
- 引用关系缺失时必须返回部分结果，不伪造。

### 9.4 Semantic Scholar

- 负责论文图、引用、参考文献和推荐相关度。
- `openAccessPdf` 存在不代表可无条件下载，仍需 Policy 校验。
- 保留 paperId、corpusId、fieldsOfStudy 等源站字段。

### 9.5 DBLP

- 作为计算机领域书目和 venue/author 去重来源。
- 通常不提供摘要和全文，必须显式返回能力缺失。
- 保留 dblp key、venue、type 和作者顺序。

## 10. 超时、重试、限流与缓存

### 10.1 超时

- 单源搜索默认 15 秒。
- 单源元数据默认 10 秒。
- PDF 下载默认 60 秒，可配置。
- Federation 总超时不能小于单源超时，且必须可观测。

### 10.2 重试

- `rate_limited`、`timeout`、`upstream_unavailable`、`network_error` 可重试。
- 默认最多 3 次，指数退避 + jitter。
- `retry_after_ms` 存在时必须遵守。
- 不允许无限重试或高频轮询。

### 10.3 限流

- 每个 server 自己实现令牌桶或等价限流。
- 联邦层保留全局预算，防止五源同时放大请求。
- 请求记录包含 source、endpoint、耗时和是否被限流。

### 10.4 缓存

- 缓存键包含 source、endpoint、query、filter 和 schema 版本。
- 元数据缓存可使用 TTL；下载文件按哈希缓存。
- 缓存命中不得改变 provenance 和 retrieved_at 语义。
- 缓存内容可清理，不作为唯一证据来源。

## 11. 契约测试

每个 MCP server 必须通过以下测试：

1. `<source>_describe` 返回合法 manifest。
2. 所有声明的工具可被调用。
3. 未声明能力返回 `capability_not_supported`。
4. 成功响应通过公共 envelope schema 校验。
5. 错误响应包含稳定错误码和 retryable 标志。
6. 分页 cursor 可正常推进和终止。
7. 原始记录保留在 `raw`。
8. 限流、超时和重试行为可 mock。
9. 下载 ArtifactRef 的哈希、大小和 MIME type 可校验。
10. 不在日志中输出密钥、Cookie 或 Authorization header。

## 12. 版本演进

- 公共 envelope 采用语义化版本。
- 新增可选字段不提升 major version。
- 删除字段、改变字段含义或错误语义必须提升 major version。
- 每个 server 的 manifest 记录支持的 schema 版本。
- Federation 遇到不支持的版本时必须拒绝或降级，并记录诊断信息。
