# 项目路线图与里程碑

| 字段 | 内容 |
|---|---|
| 文档版本 | v0.2 |
| 状态 | 执行基线 |
| 日期 | 2026-09-26 |
| 当前阶段 | M2 修复阶段；问题清单批次 1（评测口径，ADR-0015）进行中 |
| 可投入时间 | Phase 0–2 约 30 小时/周；Phase 3–4 为 32–47 小时/周（仅开发与评测） |

## 0. 如何使用本文件

本文件是后续实现、修复和优化的对齐基准，只管理项目开发与评测。论文写作、学校节点和论文素材
由 `docs/thesis-plan.md` 单独管理；本文件的排期不因论文计划调整，也不引用论文节点。

- 所有待办以 §4 问题清单为准。每一项有稳定编号（例如 `EV-01`），提交说明、周报和汇报引用该编号。
- 新发现的问题先登记到 §4（编号、位置、影响、验收标准），再动手修；不在清单里的改动需要说明理由。
- 一项完成后，把状态改为“已完成”，并写明验证方式（测试名、命令或结果记录路径）。
- 涉及评测口径、数据模型或 MCP 契约的项，必须先有 ADR 或文档更新（见 AGENTS.md §6）。
- 触及 AGENTS.md §7 红线的项（不可恢复的删除、已有数据迁移、修改冻结数据、超过阈值的付费调用等），在 §5 开放决策中登记，得到确认后再做。
- 每周复盘时更新 §2 进度快照。

编号前缀：

| 前缀 | 含义 |
|---|---|
| `EV` | 评测口径与实验有效性 |
| `EC` | 证据链正确性 |
| `SR` | 源站适配、缓存与安全 |
| `CL` | 命令行、路径与工程 |
| `SC` | v1 范围缺口 |
| `FE` | 用户前端（ADR-0016） |
| `OP` | 不阻塞里程碑的优化 |

## 1. 路线图结论

项目从 2026-09-23 开始，开发计划到 2027-03 代码冻结与复现包为止。关键路径是：

```text
规范与数据模型
  → 单源最小闭环
  → Agent Core + 证据链
  → 五源 MCP 联邦
  → 评测口径修正
  → 评测与消融
  → 代码冻结与复现包
```

截至 2026-09-26，功能实现超前于日历，但**最大风险已经从“功能缺失”转为“评测口径失真”和“证据链断口”**：
现有 Pilot 数字的 Precision/Recall 不是按 @K 计算，A3 与 B3 实际相同，A4 同时改变两个变量；
报告仍列出被过滤的论文，全文 locator 无法重新定位。这些问题不会报错，却会让实验结论站不住。
因此 10 月的主线是先修口径、再修证据链，而不是继续扩功能。

必须优先保证：

1. 2026-10-04 前完成评测口径修正（批次 1），并用新口径重跑 Pilot。
2. 2026-11-01 前完成证据链正确性修复（批次 2–4），Agent Core 与证据模型冻结。
3. 2026-11-15 前完成可演示原型（含 JSON/CSV/BibTeX 导出与下载 Policy）。
4. 2027-01-15 前完成多源、归档、报告和 Web 证据链。
5. 2027-02-28 前完成正式实验与消融。
6. 2027-03-01 代码功能冻结；2027-03-15 前完成复现包与离线演示包。
7. M7 之后交付用户前端第二版（M8，ADR-0016），只新增前端与任务类 API，不改变实验条件。

## 2. 当前进度快照（2026-09-26）

### 2.1 已完成

- 规范与文档基线：AGENTS.md、PRD、架构、MCP 契约、数据模型、评测、术语表、ADR 0001–0015。
- 五个源站 MCP server（arXiv、OpenAlex、Crossref、Semantic Scholar、DBLP）与 source registry。
- Federation：并行查询、并发预算、部分失败可见、查询变体合并；跨源 DOI 合并目前在存储层完成（见 §5 D1）。
- Planner（确定性打分）与 Executor（七步 Run：路由、检索、持久化、相关性判断、Claim 综合、引用校验、报告）。
- 证据链：Source Record、Paper、Evidence Span、Claim 持久化；arXiv PDF 内容寻址归档、Document 解析、full_text Evidence。
- 语义相关性过滤（ADR-0012）与源站响应缓存（ADR-0013）。
- LLM Claim 综合 `synthesis-v1`：评测中有模型网关时默认启用，CLI 用 `--synthesis` 开启；失败时退回模板首句。
- 评测基础设施：问题集哈希、EvaluationRun/Case 持久化、批量矩阵、三源冻结快照、Task Completion judge。
- Baseline 与消融接线：B0、B1、B2、B3、A1、A2、A3、A4、A6。
- Pilot v1（人工复核，10 题 / 24 篇）与 Pilot v2（AI 审计，10 题 / 106 篇）已冻结。

### 2.2 已验证

- 2026-09-26：`uv run ruff check .`、`uv run mypy src`、`uv run pytest`（242 passed）、`uv run research-agent --help`、`python scripts/check_docs.py` 全部通过。
- 2026-09-26：冻结快照上 1 题 B3/A4 烟测，`synthesis-v1` 实际生成非模板 Claim 与 Findings。

### 2.3 口径作废的结果

以下记录按 ADR-0015 口径作废，只保留为工程记录，不得作为实验结论引用：

- `evaluation/results/pilot_system_comparison_2026-09-25.md`
- `evaluation/results/ablation_smoke_2026-09-25.md`
- 2026-09-26 的 B3/A4 单题综合烟测（未入库记录）

### 2.4 未完成

- §4 批次 1–5 的全部项目。
- 正式 30 题集、Web UI。

## 3. 时间预算

按阶段分配；Phase 3–4 总人时为 32–47 小时/周，Phase 0–2 评测投入较低。

| 工作流 | 每周小时 | 说明 |
|---|---:|---|
| Agent Core 与证据链 | 8–10 | runtime、planner、executor、evidence、storage |
| MCP 与源站适配 | 6–8 | 每源独立 server、契约测试、限流与重试 |
| 评测与数据 | 12–22 | Phase 3–4；Phase 0–2 为 4–6 小时/周。问题集、baseline、指标、结果分析 |
| 文档与代码审查 | 2 | 更新规范、ADR、测试和重构 |
| 缓冲 | 2 | 处理源站变化、解析失败和课程冲突 |

论文写作时间不计入本表，见 `docs/thesis-plan.md`。

如果某周低于当前阶段预算，优先保留：核心闭环、评测、实验记录；可以延后 Web UI 美化、额外源站和 Office 导出。

## 4. 问题清单与修复批次

来源：2026-09-26 全仓审阅，已逐项核对代码。审阅中两条误报已剔除：Semantic Scholar
引用接口的 `fields` 参数不带前缀可以正常使用；`pilot_questions.v2.jsonl` 存在。

### 4.1 批次总览

| 批次 | 主题 | 目标日期 | 为什么这个顺序 |
|---|---|---|---|
| 1 | 评测口径（ADR-0015） | 2026-10-04 | 不修的话，之后跑的每个 Pilot 结果都要作废 |
| 2 | 证据链正确性 | 2026-10-18 | 主贡献 RQ1 与 H1c 的地基；需在 11-01 冻结前完成 |
| 3 | 源站适配、缓存与安全 | 2026-10-25 | 密钥进入缓存属于红线类问题，其余为小修 |
| 4 | 命令行、路径与工程 | 2026-11-01 | 批量跑实验前需要可靠的退出码和可移植路径 |
| 5 | v1 范围缺口 | 2026-11-15 起 | 导出和下载 Policy 构成可演示原型（M3）；前端第一版对齐 M4 |
| 6 | 用户前端第二版（ADR-0016） | M7 之后，建议 2027-03-16 起 | 面向普通用户；放在实验与代码冻结之后，不影响正式实验 |

每批完成的统一验收：`uv run ruff check .`、`uv run mypy src scripts`、`uv run pytest`、
`uv run research-agent --help`、`python scripts/check_docs.py` 全部通过，本节状态已更新。

### 4.2 批次 1：评测口径（ADR-0015）

完成后用冻结快照、K=20 重跑 Pilot 10 题：先 B1/B3/A3/A4，再 B0/B2/A1/A2/A6；结果写入
`evaluation/results/`，注明 ADR-0015。

- **EV-01 统一论文身份键**（已完成，2026-09-26）
  - 问题：相关性过滤用 `doi:{原始DOI}`（`policy/relevance.py` 的 `paper_key`），检索用 `canonical_key`（`storage/repository.py`，DOI 小写去前缀）；arXiv 条目为 `arxiv:<id>`，金标常为 `doi:10.48550/arxiv.<id>`。
  - 影响：被过滤的论文可能仍算进 Recall；A1 漏过滤；arXiv 命中被记成未命中。
  - 验收：同一论文的 DOI、arXiv ID、arXiv DOI、OpenAlex ID 得到同一身份键；大小写不同的 DOI 在过滤键和检索键上相同，因此会离开保留集合。
  - 验证：`tests/unit/test_paper_identity.py`、`tests/unit/test_evaluation_metrics.py`、`tests/unit/test_repository.py::test_repository_merges_arxiv_record_with_arxiv_doi`。
- **EV-02 排序 Top-K 指标与 nDCG**（已完成，2026-09-26）
  - 问题：`evaluator/metrics.py` 的 `retrieval_metrics` 接收无序集合，Precision 除以保留论文数；无 nDCG；测试把错误定义固定为期望值。
  - 验收：P@K 分母为 K、R@K 与 nDCG@K 有手算样例测试；现有集合指标改名为 `precision_kept`、`recall_kept`。
  - 验证：`tests/unit/test_evaluation_metrics.py` 的手算样例。送入 @K 的顺序由 `EV-03` 规定。
- **EV-03 统一候选列表口径**（已完成，2026-09-26）
  - 问题：B0 取 Top-K，B2（`evaluator/react.py`）计入全部搜到的论文，B3 为 K×源站数再过滤。
  - 验收：三类系统都输出长度不超过 K 的有序列表，排序规则按 ADR-0015 §1。
  - 验证：`tests/unit/test_ranking.py`。B0 按 BM25 得分；B2 按首次出现顺序截到 K；B1/B3/A1–A4/A6 按源站轮转，过滤只删除不重排，再截到 K。
- **EV-04 B3 路由预算与 A3**（已完成，2026-09-26）
  - 问题：`evaluator/case_runner.py` 中 `max_sources=len(source_ids)`，B3 与 A3 都查全部五源。
  - 验收：B3 的 Plan 快照 `selected_sources` 不超过 3 个且 `fallback_sources` 非空；A3 固定 5 个；`evaluation.md` 与系统描述同步。
  - 验证：`tests/integration/test_evaluation_case_runner.py::test_b3_routes_three_sources_and_a3_uses_all_five`。平分时按源站注册顺序取前 3 个。A1/A4/A6 使用同一预算；A2 也使用该预算选择源站，但查询变体固定为原问题。
- **EV-05 A4 单因素化**（已完成，2026-09-26）
  - 问题：`evidence/synthesis.py` 在约束关闭时追加 `CONSTRAINT_OFF_NOTE`，且 prompt hash 含约束开关。
  - 验收：B3 与 A4 对同一证据的 user message 与 prompt hash 完全相同；A4 仍能在集成测试中产生 `dangling_support_count > 0`。
  - 验证：`tests/unit/test_claim_synthesis.py::test_b3_and_a4_share_one_synthesis_prompt` 与 `tests/integration/test_evaluation_case_runner.py::test_a4_keeps_dangling_support_that_b3_demotes`。
- **EV-06 源站实际请求数**（已完成，2026-09-26）
  - 问题：`source_attempts` 是源站个数，不是请求次数，无法支撑 H2b。
  - 验收：新增 `source_http_calls`，包含查询变体与重试；B2 与 B3 口径一致。
  - 验证：`tests/unit/test_http_retry.py` 确认一次 429 重试计为 2 次；评测里 B2 的 `source_http_calls` 不少于搜索次数，B3 的不少于被调用源站数。缓存命中不计。
- **EV-07 Task Completion 预算按配置估算**（已完成，2026-09-26）
  - 问题：固定 `model_call_budget=20`，K=20 时 B3 几乎必然超出，Task Completion 被系统性判为 0。
  - 验收：预算由 K、源站数、是否启用过滤与综合计算，写入评测配置快照；文档给出公式；
    judge 调用失败时记录 `judge_failed` 并把该 case 排除出 Task Completion 分母，而不是计为未完成。
  - 验证：`tests/unit/test_task_completion.py`。公式见 `docs/evaluation.md` §6.3。
    `EC-08` 把相关性过滤改成按批调用后，K=20、3 源、批大小 8、过滤加综合时预算为 9。
    按篇调用时同一条件的预算是 61。
- **EV-08 综合 prompt hash 与实际提示一致**（已完成，2026-09-26）
  - 问题：`build_prompt_hash` 哈希完整摘要，user message 却把摘要截断到 1200 字符。
  - 验收：prompt hash 由实际发送的 system + user 文本计算。
  - 验证：`tests/unit/test_claim_synthesis.py::test_prompt_hash_matches_the_truncated_text_sent_to_the_model`。只在第 1200 个字符之后不同的两段摘要，哈希相同。
- **EV-09 评测命令可靠退出**（已完成，2026-09-26）
  - 问题：`evaluate` 有 case 失败仍以 0 退出；总是构造 DeepSeek 网关，无密钥时连 A6 也跑不了；`evaluator/runner.py` 在 `error_code` 分支未即时提交。
  - 验收：失败 case 时退出码非零；只在所选系统需要模型时构造网关；每个终态 case 立即提交。
  - 验证：`tests/unit/test_evaluation_runner.py` 用另一个数据库连接看到失败 case 已提交；`tests/unit/test_cli.py` 确认只有 A6 不需要模型。
- **EV-10 重跑 Pilot 并记录**（已完成，2026-10-12）
  - 验收：新结果记录包含数据集哈希、快照哈希、K、系统版本、ADR 编号；旧记录顶部标注“口径作废”。
  - 验证：`evaluation/results/pilot_v2_adr0015_2026-10-12.md`。90 个 case 完成。快照只有 3 个源，A3 与 B3 的源站集合相同；`source_http_calls` 在快照模式下为 0。

### 4.3 批次 2：证据链正确性

- **EC-01 报告只列保留的论文与证据**（已完成，2026-10-14）
  - 问题：`runtime/research_service.py` 的 `generate_report_step` 把全部 `source_records` 与 `evidence_rows` 交给 `render_report`，被相关性过滤的论文仍出现在 Papers、Evidence 表中；`evidence_count` 也包含它们。
  - 验收：被过滤项只出现在单独的“已排除候选”节并附过滤理由；集成测试覆盖。
  - 验证：`tests/unit/test_research_report.py`；`tests/integration/test_relevance_filtering.py` 的 `test_denied_papers_leave_the_report_tables`。数据库仍保留被排除论文的 Evidence Span，报告和 `evidence_count` 只计保留项。
- **EC-02 全文 locator 可重新定位**（已完成，2026-10-14）
  - 问题：全文证据 `page` 写死为 1，`char_start/char_end` 在 `strip()` 之后计算；`storage/pdf_parser.py` 合并页面时跳过空页，页码与内容错位。
  - 验收：新增“重新定位”测试：`document_text[char_start:char_end] == quote`，页码与 PDF 实际页一致；这是 H1c 的实现前提。
  - 验证：`tests/unit/test_pdf_parser.py` 的 `test_first_paragraph_locator_relocates_quote_on_its_pdf_page`；`tests/integration/test_federated_research_flow.py` 的 `test_full_text_evidence_relocates_onto_the_parsed_page`。空白首页之后的引文页码为 2，字符切片等于原文。
- **EC-03 补全摘要的 provenance**（已完成，2026-10-14）
  - 问题：缺摘要时从 OpenAlex 补回（`runtime/enrichment.py`），证据却挂在原候选（如 Crossref）的 Source Record 上。
  - 验收：补全摘要对应一条 OpenAlex Source Record 并与 Paper 关联，Evidence Span 的 `source_record_id` 指向它。
  - 验证：`tests/integration/test_abstract_enrichment.py`。Crossref 候选没有摘要时，补回的摘要挂在 OpenAlex Source Record `W999` 上，并与同一篇 Paper 关联。
- **EC-04 步骤重试幂等**（已完成，2026-10-14）
  - 问题：`executor/executor.py` 在一次尝试失败后先提交再重跑处理函数；`persist_results` 会重复写入 Evidence，`file` 行撞 `UNIQUE(paper_id, sha256)`；`judge_relevance` 与 `generate_report` 同样重复写入。
  - 方案：失败时回滚本次尝试的数据库写入，并重置该步骤的运行上下文；不引入新的唯一约束（避免 schema 变更）。
  - 验收：注入“首次失败、第二次成功”的步骤，确认无重复行、无约束错误。
  - 验证：`tests/integration/test_federated_research_flow.py` 的 `test_retry_after_a_failed_persist_does_not_duplicate_rows`。PDF 解析第一次失败、第二次成功时，`file` 仍是 2 行，`persist_results` 有 2 次尝试。
- **EC-05 引用校验与综合使用同一证据集合**（已完成，2026-10-14）
  - 问题：`validate_citations_step` 用全部证据校验，综合只用未被过滤的证据。
  - 验收：两处共用同一可用证据集合。
  - 验证：`tests/integration/test_relevance_filtering.py` 的 `test_citation_check_uses_the_same_evidence_as_synthesis`。被过滤论文的 Evidence Span 不进入引用校验。
- **EC-06 Executor 依赖错误时标记失败**（已完成，2026-10-14）
  - 问题：依赖未满足时抛 `ValueError`，Run 停在 `RUNNING`。
  - 验收：Run 状态为 `FAILED` 并记录错误码。
  - 验证：`tests/unit/test_executor.py` 的 `test_executor_fails_the_run_when_a_dependency_is_missing`。缺少的依赖不会执行该步骤，Run 与该步骤的错误码都是 `unresolved_dependencies`。
- **EC-07 论文元数据补空合并**（已完成，2026-10-14）
  - 问题：`upsert_paper` 命中已有论文时直接返回，后来源站的摘要、年份、venue 不会补进 Paper，FTS 也不更新。
  - 验收：只补空、不覆盖已有值；FTS 通过更新触发器保持一致。
  - 验证：`tests/unit/test_repository.py` 的 `test_repository_fills_blank_metadata_without_overwriting`。空摘要被补上后能被 `paper_fts` 检索到，后到的不同摘要、年份和 venue 不会覆盖。
- **EC-08 A6 严格与宽松阈值、批量判断**（已完成，2026-10-14）
  - 问题：ADR-0012 要求严格/宽松两种阈值且两种都报告；当前 `keep` 只剔除 `out_of_scope`，逐篇调用模型。
  - 验收：阈值为系统配置项；支持批量判断并记录调用数；`evaluation.md` 写明两种取值的定义。
  - 验证：`tests/unit/test_relevance_judge.py` 的 `test_strict_threshold_keeps_only_direct_answers` 与 `test_judge_batch_makes_one_call_per_chunk`；`tests/integration/test_relevance_filtering.py` 的 `test_strict_threshold_drops_supporting_papers`。宽松为默认。每批最多 8 篇。

### 4.4 批次 3：源站适配、缓存与安全

- **SR-01 密钥不进入缓存**（已完成，2026-10-14；旧文件未删）
  - 问题：OpenAlex `api_key` 放在查询参数里，缓存键和缓存文件保存完整 URL（`mcp_servers/common.py`、`mcp_servers/cache.py`）。
  - 验收：缓存键和落盘 URL 去掉密钥类参数；测试确认缓存文件中不含密钥。已有缓存文件的清理需删除文件，见 §5 D5。
  - 验证：`tests/unit/test_response_cache.py` 的 `test_cache_drops_api_keys_from_the_stored_url`。`api_key`、`apikey`、`api-key`、`access_token`、`token`、`secret` 不进入缓存键和落盘 URL。已有缓存文件未删除，仍待 D5 确认。
- **SR-02 OpenAlex 详情请求带上 `mailto` 与 `api_key`**（已完成，2026-10-14）
  - 问题：`get_paper`、`resolve_open_access` 与 `get_references` 首次请求未经 `_params`。
  - 验证：`tests/unit/test_openalex_client.py` 的 `test_openalex_detail_requests_include_mailto_and_api_key`。这三处详情请求都带上联系邮箱和 API key。
- **SR-03 统一网络异常包装**（已完成，2026-10-14）
  - 问题：Crossref、Semantic Scholar、DBLP 客户端未把 `httpx.HTTPError` 转为各自的客户端错误；作为独立 MCP server 运行时，超时不会以 `ok: false` 返回。
  - 验证：三个 server 测试 `test_*_server_reports_timeout_as_failed_envelope`。超时返回 `ok: false`，错误码为 `upstream_unavailable`。
- **SR-04 arXiv `.pdf` URL 解析**（已完成，2026-10-14）
  - 问题：`https://arxiv.org/pdf/<id>v2.pdf` 在 `arxiv/parser.py` 中解析失败。
  - 验证：`tests/unit/test_arxiv_parser.py` 的 `test_normalize_arxiv_id_handles_urls_and_versions`。`https://arxiv.org/pdf/2312.10997v2.pdf` 归一为 `2312.10997`。
- **SR-05 `Retry-After` 支持 HTTP 日期格式**（已完成，2026-10-14）
  - 验证：`tests/unit/test_http_retry.py` 的 `test_parse_retry_after_reads_an_http_date` 与 `test_get_with_retry_waits_for_an_http_date`。秒数和 HTTP 日期都能换算成等待时间；过去的日期等待 0 秒；无法识别时仍走原有退避。
- **SR-06 PDF 下载防护**（已完成，2026-10-14）
  - 问题：`arxiv/client.py` 一次性读入全部内容，无大小上限，不检查 `%PDF` 文件头。
  - 验收：设大小上限、校验文件头；不符合的文件标记为 `quarantined`。
  - 验证：`tests/unit/test_arxiv_client.py` 的 `test_non_pdf_download_is_quarantined` 与 `test_oversized_pdf_download_is_quarantined`；`tests/integration/test_federated_research_flow.py` 的 `test_non_pdf_download_is_recorded_as_quarantined`。上限为 32 MiB。超限内容不落盘，也不解析成证据。
- **SR-07 共享 DOI 归一化**（已完成，2026-10-14）
  - 问题：四个解析器与存储层各有一份 DOI 归一化，未处理 `dx.doi.org`、`www.doi.org`。
  - 验证：Crossref、OpenAlex、Semantic Scholar、DBLP 的解析测试。四处都调用 `identity.normalize_doi`，`dx.doi.org` 与 `www.doi.org` 都会去掉。存储层在 EV-01 已使用同一函数。
- **SR-08 MCP server 入口读取环境配置**（已完成，2026-10-14）
  - 问题：OpenAlex、Crossref、Semantic Scholar 的 `main()` 未读取 API key 与联系邮箱。
  - 验证：三个 `test_*_main_reads_*`。OpenAlex 读取 `RESEARCH_AGENT_CONTACT` 与 `OPENALEX_API_KEY`；Crossref 读取联系邮箱；Semantic Scholar 读取 `SEMANTIC_SCHOLAR_API_KEY`。与进程内 registry 使用同一组变量。
- **SR-09 OpenAlex 解析 `ids.arxiv`**（已完成，2026-10-14）
  - 问题：envelope 固定 `arxiv_id: null`，没有 DOI 时无法与 arXiv 合并。
  - 验证：`tests/unit/test_openalex_parser.py` 的 `test_parse_work_reads_arxiv_id_without_a_doi`；`tests/unit/test_repository.py` 的 `test_repository_merges_openalex_record_by_arxiv_id_without_doi`。`ids.arxiv` 归一成无版本号的 arXiv ID，envelope 写出它，存储层据此与 arXiv 记录合并。
- **SR-10 缓存目录哈希排除过期条目**（已完成，2026-10-14）
  - 验证：`tests/unit/test_response_cache.py` 的 `test_directory_hash_ignores_expired_entries`。超过 TTL 的条目不进入 `directory_hash`；未过期条目和 `ttl_seconds=None` 的缓存仍计入。
- **SR-11 Federation 不重复发送主查询**（已完成，2026-10-14）
  - 问题：`search_sources` 把原始 `query` 放在 Planner 变体之前，空白差异时会先查询未归一化的问题。
  - 验收：只使用 `plan.query_variants`，顺序与 Planner 一致。
  - 验证：`tests/unit/test_federation.py` 的 `test_search_sources_uses_planner_variants_without_the_raw_query`。没有变体时才退回原始问题。

### 4.5 批次 4：命令行、路径与工程

- **CL-01 默认路径按项目根目录解析**（已完成，2026-10-14）
  - 问题：`cli.py` 的 `data/`、`reports/` 默认值与 arXiv server 下载目录按当前工作目录解析，违反 AGENTS.md §9。
  - 验证：`tests/unit/test_paths.py`。相对路径解析到含 `pyproject.toml` 的项目根；绝对路径保持不变。`research`、`evaluate`、`warm-cache` 和 arXiv server 的下载目录都走这一规则。
- **CL-02 数据库保存项目相对路径**（已完成，2026-10-14）
  - 问题：`file.path`、`document.text_path`、`report.path` 保存传入的路径（常为绝对路径），与 `data-model.md` 的“项目相对路径”不符。
  - 验证：`tests/unit/test_repository.py` 的 `test_new_artifact_paths_are_stored_relative_to_the_project`；`tests/unit/test_paths.py` 的 `test_stored_project_path_keeps_outside_and_empty_paths`。项目内的新写入保存为相对 POSIX 路径；项目外路径保持绝对路径；空路径保持空。不迁移已有数据库（D6）。
- **CL-03 `doctor` 做真实检查**（已完成，2026-10-14）
  - 验收：检查 Python 版本、`data/` 与 `reports/` 可写、迁移可执行、可选环境变量是否存在（不打印值）。
  - 验证：`tests/unit/test_doctor.py`。Python 低于 3.12、目录不可写或迁移失败时退出码为 1。迁移在临时数据库上执行，不改已有数据库。`DEEPSEEK_API_KEY`、`OPENALEX_API_KEY`、`RESEARCH_AGENT_CONTACT`、`SEMANTIC_SCHOLAR_API_KEY` 只报告 set 或 unset。
- **CL-04 无密钥时 `research` 的默认行为**（已完成，2026-10-14）
  - 问题：默认开启相关性过滤，无 `DEEPSEEK_API_KEY` 时直接失败。
  - 验证：`tests/unit/test_cli.py` 的 `test_research_without_an_api_key_skips_relevance_and_says_so`。没有密钥时跳过默认过滤，输出 `relevance: skipped (DEEPSEEK_API_KEY is not set)`，并且不构造模型客户端。显式 `--relevance-filter` 或 `--synthesis` 在检索开始前失败。有密钥时过滤保持开启。空白密钥与缺失相同。不打印密钥的值。
- **CL-05 CI 步骤命名与格式检查**（已完成，2026-10-14）
  - 问题：CI 中名为 “Check formatting” 的步骤实际运行 `ruff check`。修改 CI 属于红线，改动前确认。
  - 验证：`tests/unit/test_ci_steps.py`。该步骤改名为 Lint，命令仍是 `uv run ruff check .`。`scripts/check_all.py` 使用同一名称。未加入 `ruff format --check`：当前有 86 个文件不符合 formatter，加入后 CI 会失败。
- **CL-06 `scripts/` 纳入 mypy**（已完成，2026-10-14）
  - 验证：`tests/unit/test_ci_steps.py` 的 `test_typecheck_covers_source_and_scripts`。`uv run mypy src scripts` 在 strict 下检查 `src/` 和 `scripts/`。CI 的 Type check 步骤与 `scripts/check_all.py` 使用同一命令。
- **CL-07 文档校验覆盖目录树**（已完成，2026-10-14）
  - 验收：`scripts/check_docs.py` 检查 AGENTS.md §4 列出的模块文件是否存在。
  - 验证：`tests/unit/test_check_docs.py`。目录树里的具体文件必须存在；`NNNN` 占位名和注释为「尚未创建」的条目不要求存在。
- **CL-08 Windows 临时目录**（已记录，2026-10-14）
  - 现象：受限环境下 pytest 默认临时目录无权限，需 `--basetemp` 指向可写目录。不改代码。
  - 说明：写入 `AGENTS.md` §6 与 `README.md`「开发验证」。Windows 上把 `TEMP`、`TMP` 和 `--basetemp` 指到 `%LOCALAPPDATA%\Temp`。

### 4.6 批次 5：v1 范围缺口

- **SC-01 JSON/CSV 证据表与 BibTeX 导出**（已完成，2026-10-14）
  - 问题：AGENTS.md §3、PRD 要求的导出只有 Markdown 报告；schema 已有 `export` 表但无写入逻辑。
  - 验证：`tests/unit/test_exports.py`；`tests/integration/test_federated_research_flow.py`。一次 Run 写入 `evidence.json`、`evidence.csv`、`references.bib`，并在 `export` 表记录路径与 SHA-256。缺失 DOI 不编造。Zotero 仍未实现。
- **SC-02 下载 Policy**（已完成，2026-10-14）
  - 问题：`policy/` 只有相关性判断；下载没有域名白名单、开放获取检查和审计记录。
  - 验证：`tests/unit/test_download_policy.py`；`tests/integration/test_federated_research_flow.py` 的 `test_federated_research_merges_doi_and_keeps_provenance`。允许的主机是 `arxiv.org`、`www.arxiv.org`、`export.arxiv.org`。非开放获取或重定向到名单外主机会拒绝，审计只记录主机和原因，不记录 URL。下载预算仍未实现。
- **SC-03 正式 30 题集**（设计已冻结，2026-10-14；标注未开始，计划 2026-12）
  - 验证：`tests/unit/test_formal_design.py`；说明见 `evaluation/datasets/formal_v1_design.md`。30 题、每题 2 个子问题、年份 2022–2026。领域为 9/6/6/5/4，六种题型各 5 题。未创建问题文件，未改 Pilot。标注时每题至少 5 篇 gold paper，且两个子问题都要有证据。
- **SC-04 最小 Web UI**（2026-12-01 至 2027-01-10，对齐 M4）
  - 按 ADR-0016 实现为用户前端的第一版（证据链查看器），拆分为 `FE-01`–`FE-04`，见 §4.7。
- **SC-05 Run 暂停、恢复与检查点**（Phase 3）
- **SC-06 Memory 与 FTS5 的 v1 边界**（待决定，见 §5 D3、D4）

### 4.7 用户前端（ADR-0016）

前端是同一个工程的两次迭代：第一版是只读的证据链查看器（对齐 `SC-04` 与 M4），第二版在此基础上
让普通用户在浏览器里完成“提问 → 看进度 → 浏览报告与证据链 → 导出”（M8）。技术栈为
React + Vite + TypeScript（`web/`），后端为 FastAPI 本地 API（`src/research_agent/interfaces/`）。

每项完成的前端验收：类型检查、lint、单元测试、生产构建全部通过，三平台构建通过。

第一版：证据链查看器（2026-12-01 至 2027-01-10）

- **FE-01 本地 API 契约**（已完成，2026-10-14）
  - 内容：资源与字段（Run、Plan 步骤、来源、候选论文、Claim、Evidence Span、Source Record、File、Document）、分页、错误格式、版本号；字段使用 `snake_case`，术语与 `docs/glossary.md` 一致。
  - 验证：`docs/local-api.md`；`tests/unit/test_local_api_contract.py`。第一版只读，路径前缀 `/v1`。服务本身属于 `FE-02`。实现前仍可改这份契约。
- **FE-02 本地只读 API**（已完成，2026-10-14）
  - 内容：FastAPI 应用放在 `interfaces/`，复用 repository 所在的 SQLite；默认只监听 `127.0.0.1`，CORS 只允许本地前端来源。
  - 验证：`tests/integration/test_local_api.py`。响应含 `api_version`，不含密钥、`raw_json` 或本机绝对路径。`serve --host 0.0.0.0` 会拒绝启动。
- **FE-03 前端工程脚手架**（已完成，2026-10-14）
  - 内容：`web/` 目录、Node.js 版本声明、依赖锁定文件、lint、类型检查、单元测试、构建；`.gitignore` 忽略 `node_modules/` 与构建产物；本地检查脚本与 CI 增加前端步骤。
  - 验证：`tests/unit/test_check_web.py`；`tests/unit/test_ci_steps.py` 的 `test_ci_checks_the_web_app`。Node.js 24。一条命令是 `uv run python scripts/check_web.py`，它会 `npm ci` 再执行 lint、类型检查、测试和构建。没有 Node.js 时退出 0。证据链页面仍属 `FE-04`。
- **FE-04 证据链查看页面**（设计待审阅，见 `docs/evidence-viewer.md`）
  - 内容：Run 列表与状态、Plan 步骤进度、来源分布、候选论文（含被过滤项与理由）、从 Claim 逐级追溯到 Evidence Span、Paper、Source Record，full_text 再到 File 与 Document。
  - 验收：一个完整 Run 可在 UI 中查看从源站到证据的链路（Phase 3 验收）；页面只展示存储中的证据，不生成或改写证据。

第二版：用户前端（M7 之后，建议 2027-03-16 起）

- **FE-05 任务类 API**（待开始）
  - 内容：提交研究问题（源站、K、是否启用相关性过滤与综合）、取消任务；后台单用户、单并发执行队列。
  - 验收：通过 API 提交的 Run 与 CLI 同参数运行得到相同的 Plan 与配置快照。
- **FE-06 实时进度**（待开始）
  - 内容：步骤状态推送（SSE，或轮询兜底）。
  - 验收：页面进度与 `plan_step` 状态一致，断线后能恢复显示。
- **FE-07 提问与进度页面**（待开始）
  - 内容：研究问题表单、参数说明、运行中进度、失败原因展示（源站失败、缺少模型密钥、预算超限）。
  - 验收：不看文档的用户能完成一次提问并看懂失败原因。
- **FE-08 报告浏览与导出**（待开始，依赖 `SC-01`）
  - 内容：Markdown 报告渲染、Claim 点击跳转证据、JSON/CSV/BibTeX 下载。
- **FE-09 人工确认界面**（待开始，依赖 `SC-02`）
  - 内容：需要人工确认的操作（`docs/PRD.md` §7）在前端只发起“待确认”请求，由后端 Policy 执行并写审计日志。
- **FE-10 端到端测试与使用说明**（待开始）
  - 内容：浏览器端到端测试覆盖“提问 → 进度 → 报告 → 导出”；README 增加前端启动说明。
  - 验收：三平台端到端测试通过；离线演示包（M7）可在前端中打开。

### 4.8 优化（不阻塞里程碑）

- **OP-01** 查询变体按排名交错合并，替代“第一个变体占满名额”（`router/federation.py`）。
- **OP-02** 相关性判断并发执行，并按 `(prompt_version, 问题哈希, 身份键)` 复用判定结果。
- **OP-03** 用具名类型替代 6 元组证据行，减少 `row[2]`、`row[4]` 这类下标错误。
- **OP-04** 数据库连接只在持久化时持有，不跨越网络、PDF 与模型调用的 `await`。
- **OP-05** 主元数据来源按字段完整度选择，而不是固定为 arXiv。
- **OP-06** 写入作者关系并填充 `paper_fts.authors_text`。
- **OP-07** `source_call` 记录真实耗时。
- **OP-08** 抽取 JSON 时用 `json.JSONDecoder.raw_decode` 替代贪婪正则（综合、相关性、ReAct、judge 共四处）。

## 5. 开放决策

以下事项需要用户确认后才能实施。

| 编号 | 事项 | 选项 | 建议 |
|---|---|---|---|
| D1 | 跨源合并归属 | 契约写在 Federation，实现在存储层；改实现或改契约 | 保持存储层合并，修改契约与架构文档，Federation 只用 EV-01 身份键统计 |
| D2 | 相关性过滤粒度 | 按 Paper 或按 Source Record | 按 Paper，与指标和金标一致 |
| D3 | Memory 在 v1 的边界 | 独立模块，或说明 v1 由存储层承担 | 由存储层承担，文档写明 |
| D4 | FTS5 用途 | 实现本地检索命令，或文档收窄为“索引已建、未使用” | M3 前收窄文档，Phase 3 再实现 |
| D5 | 清理已有缓存中的密钥 | 删除受影响的缓存文件（红线） | 新写入已不再保存密钥（SR-01，2026-10-14）；删除旧文件仍需确认 |
| D6 | 已有数据库路径转换 | 迁移旧数据（红线），或只改新写入 | 新写入已改为相对路径（CL-02，2026-10-14）；迁移旧数据仍需确认 |
| D7 | 安装 Node.js 工具链 | 新增全局依赖（红线） | 已确认使用本机 Node.js 24（FE-03，2026-10-14）；不另装全局运行时 |
| D8 | CI 增加前端检查 | 修改 CI（红线） | 已确认在现有 CI job 增加前端检查（FE-03，2026-10-14） |
| D9 | 前端第二版起止日期 | 建议 2027-03-16 至 2027-04-30 | M7 完成时按实际进度确认 |

已确认：

- 2026-09-26：A3 保留，B3 设路由预算（每题最多 3 源），写入 ADR-0015。
- 2026-09-26：问题清单从批次 1 开始实施。
- 2026-09-26：前端分两阶段交付，技术栈为 React + Vite + TypeScript，写入 ADR-0016。
- 2026-09-26：AGENTS.md §7 红线改为 11 条加“只需说明”一档；付费调用阈值为单次任务 50 次模型调用；本地 `git commit` 只需说明。
- 2026-09-26：确认执行 `EV-10`，用冻结三源快照、K=20、Pilot v2 共 10 题重跑 B1/B3/A3/A4/B0/B2/A1/A2/A6，允许超过 50 次模型调用。
- 2026-10-14：确认 `CL-05`。只把 `.github/workflows/ci.yml` 中实际执行 `ruff check` 的步骤改名为 Lint，并同步 `scripts/check_all.py`。不新增工作流，不加入 `ruff format`，不改 D8 的前端检查。
- 2026-10-14：确认 `CL-06`。已有 Type check 步骤的命令从 `uv run mypy src` 改为 `uv run mypy src scripts`。不新增工作流，不改其他步骤。
- 2026-10-14：用户要求提交并推送 `main`。范围是 `8f98e1d` 之后的 EC-05 到 FE-04 设计与计划，以及尚未推送的 `8f98e1d`。
- 2026-10-14：确认 `FE-03` 的 D7、D8。使用已安装的 Node.js 24，不另装全局运行时。在现有 CI job 中用 `actions/setup-node` 与 `scripts/check_web.py` 做前端检查。没有 Node.js 时该脚本退出 0。

## 6. 阶段与里程碑

### Phase 0：规范、脚手架与单源原型

**时间**：2026-09-23 至 2026-10-15　**状态**：交付物已完成

- `AGENTS.md`、PRD、架构、MCP 契约、数据模型、评测、路线图与 ADR 基线。
- Python 3.12 脚手架、SQLite schema 与迁移策略、arXiv MCP server、CLI 原型、最小 Markdown 报告、CI。

### Phase 1：Agent Core、证据链与端到端最小闭环

**时间**：2026-10-16 至 2026-11-01　**状态**：功能已提前完成；本阶段改为执行批次 1–4

目标：让“一个问题 → 多源检索 → 去重 → 候选 → 证据表 → 报告”的每一环都经得起评测。

交付物：

- 批次 1：评测口径修正与 Pilot 重跑。
- 批次 2：证据链正确性。
- 批次 3：源站与安全修复。
- 批次 4：命令行与路径可移植性。

验收：

- 新口径下 Pilot 10 题完成 B1/B3/A3/A4 对比，并有结果记录。
- 全文 Evidence Span 通过重新定位测试。
- 报告中不出现被过滤的论文。
- 2026-11-01 Agent Core 与证据模型冻结。

### Phase 2：导出、下载 Policy 与初版评测

**时间**：2026-11-02 至 2026-11-29

交付物：

- SC-01 导出与 SC-02 下载 Policy（11-15 前），构成可演示原型（M3）。
- 10 题 Pilot 全系统结果（新口径）与初版实验记录。
- 正式集 v1 设计冻结为 30 题（SC-03）。

验收：

- 五源可独立启动、独立测试；至少四个源站能完成真实查询或有冻结快照替代并说明原因。
- 一次完整 Run 可导出 Markdown 报告、JSON/CSV 证据表和 BibTeX。
- 下载前经过 Policy 检查并写入审计记录。

### Phase 3：多源完善、归档、报告与 Web 证据链

**时间**：2026-11-30 至 2027-01-15

交付物：

- 五源联邦稳定版；源站健康状态、限流、重试、部分失败处理。
- PDF 解析与 locator 稳定性改进。
- 前端第一版（`SC-04`，`FE-01`–`FE-04`）：本地只读 API 与证据链查看器，展示任务状态、来源分布、候选论文、证据链。
- Run 暂停与恢复（SC-05）。
- 正式问题集 v1（30 题）标注与冻结。
- B0/B1/B2 正式批次（2026-12-01 至 2027-01-15）。

验收：

- 一个完整 Run 可在 UI 中查看从源站到证据的链路。
- 至少 90% 的 full-text Evidence Span 能重新定位。
- 引用校验能阻止明显不存在或错配的引用。
- 2027-01-15 功能和数据源冻结，下一阶段只做完善和实验，不再大改架构。

### Phase 4：正式实验与消融

**时间**：2027-01-16 至 2027-02-28

交付物：

- 正式问题集和系统版本冻结。
- B3 + A1–A4 正式批次；B0–B3 正式对比，核心 8 配置共 720 次 Run；A6 严格与宽松两种阈值。
- 人工引用和证据抽样复核；错误分析。
- `docs/evaluation.md` §13 列出的实验图表。

验收：

- 所有核心指标有结果和置信区间。
- 主要实验可在同一配置下重新运行。
- 不再新增会改变主实验条件的功能。

### Phase 5：代码冻结、复现包与演示包

**时间**：2027-03-01 至 2027-03-15

交付物：

- 代码功能冻结，只修 bug 和文档。
- 实验复现包：配置、数据集哈希、快照、脚本和结果记录，能在同一配置下重跑主要实验。
- 离线演示包：冻结快照 + 本地数据库 + 演示脚本，不依赖网络与模型 API 也能展示完整证据链。
- 代码、实验数据和说明归档。

验收：

- 在一台干净环境上按说明完成安装、离线演示和一次复现运行。
- 结果记录中的每个数字都能追溯到配置文件、结果文件和运行 ID。

### Phase 6：用户前端第二版（v1 之后）

**时间**：M7 之后，建议 2027-03-16 至 2027-04-30（§5 D9）

目标：普通用户不用命令行，在浏览器里完成一次完整调研。

交付物：`FE-05`–`FE-10`（任务类 API、实时进度、提问与进度页面、报告浏览与导出、人工确认界面、端到端测试与使用说明）。

边界：

- 只新增 `web/` 与 `interfaces/` 中的任务类接口；Agent Core、证据链、评测逻辑保持冻结，需要改动时先写 ADR。
- 不改变任何已完成实验的配置与结果。

验收：

- 用户在浏览器中完成“提问 → 看进度 → 浏览报告与证据链 → 导出”。
- 没有 Node.js 的环境仍可完整使用 CLI。
- 三平台端到端测试通过。

## 7. 关键里程碑

| 里程碑 | 日期 | 完成定义 | 状态 |
|---|---|---|---|
| M0 规范冻结 | 2026-10-01 | 文档基线可执行，目录和术语固定 | 已完成 |
| M1 单源闭环 | 2026-10-15 | arXiv 查询 → 保存 → 报告 | 已完成 |
| M2 证据链闭环 | 2026-11-01 | 双源 → 去重 → 下载 → Evidence → Claim；批次 1–4 完成 | 功能完成，修复进行中 |
| M3 可演示原型 | 2026-11-15 | 导出、下载 Policy、新口径 Pilot 全系统结果 | 未开始 |
| M4 五源稳定与 Web 证据链 | 2027-01-15 | 五源、归档、报告、Web 证据链可用 | 未开始 |
| M5 实验完成 | 2027-02-28 | 正式对比和消融完成 | 未开始 |
| M6 代码冻结 | 2027-03-01 | 只修 bug 和文档 | 未开始 |
| M7 复现与演示包 | 2027-03-15 | 复现包与离线演示包可用 | 未开始 |
| M8 用户前端可用 | 建议 2027-04-30 | 浏览器中完成提问、进度、报告与证据链、导出 | 未开始 |

## 8. 每周工作节奏

建议每周固定：

- 1 次规划会：确认本周要关闭的问题编号、风险和冻结项。
- 3 次开发块：Agent Core、MCP、存储与证据。
- 1 次评测块：运行问题集并记录失败样本。
- 1 次复盘：更新 §2 快照、§4 状态、ADR 和下一周计划。

每周必须留下：可运行增量、测试结果、实验或失败记录、风险和阻塞项。

## 9. 工作流优先级

### P0：不能延后

- 评测口径修正（批次 1）与证据链正确性（批次 2）。
- 独立 Agent Core；证据链和引用校验。
- 至少 arXiv + OpenAlex 双源闭环；数据模型和可复现存储。
- 正式问题集和 baseline；实验记录与结果图表。

### P1：支撑主贡献

- Crossref、Semantic Scholar、DBLP 的稳定性修复（批次 3）。
- 联邦路由、限流、重试和 provenance 合并。
- JSON/CSV/BibTeX 导出与下载 Policy（批次 5）。
- Web 证据链；消融实验 A1–A4 与 A6；错误分析。
- 语义相关性过滤已落地（ADR-0012，2026-09-24），严格/宽松阈值和批量判断见 `EC-08`。
  过滤准确率仍要以 Pilot v1 的人工复核结果为参照报告。v1 冻结记录见
  `evaluation/datasets/VERSIONS.md`：复核中被替换的论文（芯片设计、语音数据集、生物医学检索、
  RLHF 等）是该能力的动机证据；落地后整体重跑这 10 题并报告准确率，而不是再次逐条手改。

### P2：可延后

- A5 provenance 消融。
- Word、PDF、PPT 导出。
- 额外全文源，如 OpenReview、ACL Anthology、CVF。
- 用户前端第二版（`FE-05`–`FE-10`），在 M7 之后进行；§4.8 优化项。
- 多项目、多用户和远程部署。

### 不做

- 多 Agent 自治。
- 向量数据库。
- 付费墙绕过。
- 大规模模型微调。
- 与主贡献无关的插件市场。

## 10. 风险登记表

| 风险 | 触发信号 | 影响 | 缓解措施 |
|---|---|---|---|
| 评测口径失真 | 指标定义与文档不符、消融无差异 | 实验结论不成立 | ADR-0015；批次 1 在正式实验前完成；旧结果标注作废 |
| 密钥泄漏 | 缓存或日志中出现密钥 | 违反合规红线 | SR-01；测试扫描缓存文件 |
| 范围膨胀 | 同时做 UI、Office、多 Agent、向量库 | 主线延期 | P0/P1/P2 分层，冻结 v1 |
| MCP 工作量过高 | 五源契约不一致、调试时间超预期 | M3 或 M4 延期 | 冻结快照替代不稳定源站，批次 3 只修确定问题 |
| 评测规模过大 | 720 次 Run、人工标注和重跑超预期 | 实验延期 | 30 题、13 周铺开、分批、缓存和批量自动化 |
| 源站 API 变化 | 响应字段或限流变化 | 查询失败 | 契约测试、fixture、manifest、适配器隔离 |
| PDF 解析质量差 | 乱码、页序错误、locator 失效 | 证据链受损 | 多 parser 降级、保留原文本、人工校验 |
| 下载受限 | 403、重定向、验证码 | 无法获取全文 | 只做 OA，记录失败原因，增加开放全文源 |
| 评测数据不足 | 自建问题标注慢 | 无法完成消融 | Pilot 10 题先行，正式集冻结 |
| 金标证据质量差 | 引文是背景句、论文与子问题不对口 | 指标失去意义 | 六项判据人工复核、前置校验、语义过滤 |
| LLM 成本高 | token 或费用超预算 | 实验无法完成 | 确定性步骤优先、批量判断、缓存、预算上限 |
| 前端工具链成本 | Node.js 三平台差异、CI 变慢、依赖升级频繁 | M4 延期 | 固定 Node 版本与锁文件；CLI 不依赖前端；第一版只做只读视图 |
| 前端侵入核心 | 为界面需求修改 runtime、证据或评测代码 | 实验条件被改变 | 前端只经 HTTP API；第二版只新增 `web/` 与任务类接口，改核心先写 ADR |
| 单点环境故障 | 本机损坏、数据库丢失 | 数据不可恢复 | 定期备份、导出报告和实验记录 |
| 演示失败 | 演示时网络或 API 不可用 | 原型无法展示 | M7 离线演示包、冻结快照 |

## 11. 范围冻结点

- 2026-10-04：ADR-0015 口径修正完成，Pilot 以新口径重跑。
- 2026-11-01：Agent Core 和证据模型冻结。
- 2026-12-05：系统架构冻结，只做修复和完善。
- 2027-01-15：功能和数据源冻结。
- 2027-02-15：实验条件冻结。
- 2027-03-01：代码功能冻结，只修 bug 和文档。冻结范围是 Agent Core、证据链、源站适配与评测；
  `web/` 与 `interfaces/` 的任务类接口按 ADR-0016 不受此限，用于 Phase 6。

任何冻结后的重大变更必须写 ADR，并说明对后续里程碑的影响。

## 12. 路线图维护规则

- 每周更新一次 §2 进度快照与 §4 状态。
- 里程碑变更必须写明原因、影响和补偿措施。
- 新增功能必须先判断是否影响证据链主贡献，并在 §4 登记编号。
- 如果进度落后，优先削减 P2，不允许削减测试、评测和实验记录。
- 论文计划提出的新实验或修复需求，同样先在 §4 登记编号，再按本文件排期。
