# 证据链查看器设计（FE-04）

| 字段 | 内容 |
|---|---|
| 文档版本 | v1 |
| 状态 | 设计待审阅 |
| 日期 | 2026-10-14 |
| 关联文档 | `docs/local-api.md`, `docs/adr/0016-user-frontend-spa.md`, `docs/glossary.md`, `docs/roadmap.md` |

## 1. 目的

一个完整 Run 要能在浏览器里从结论一路追到源站，满足路线图 Phase 3 的验收。

页面有两类读者：

- 答辩和导师演示：不熟悉系统的人要一眼看懂“哪次运行、有哪些结论、证据从哪来”。
- 作者调试和核对实验：需要 ID、哈希、locator 原值等细节。

因此默认只显示人能读懂的内容，技术字段放进可展开的「详细信息」。

## 2. 约束

- 只读。页面只发 `GET`，数据全部来自 `docs/local-api.md` 的 `/v1` 接口。
- 页面不生成、不改写、不补全证据。数据缺失时如实显示缺失。
- 不显示密钥、`raw_json` 或本机绝对路径。接口已经保证这一点，前端不另外拼路径。
- 不新增运行时依赖。只用已有的 React。路由、请求、横条图和样式都自己写。
- 不加载外部字体或外部资源，离线可用。
- 默认连接 `http://127.0.0.1:8765`，即 `research-agent serve` 的默认端口；可用 `VITE_API_BASE` 改。

## 3. 布局

三栏。左栏选 Run，中栏看这个 Run 的内容，右栏看一条结论的证据链。

### 3.1 顶栏

- 标题「证据链查看器」。
- 当前 API 地址和连接状态（已连接 / 连不上）。

### 3.2 左栏：Run 列表

- 每项显示：问题原文、Run 状态、开始时间、论文数、证据数、结论数。
- 按 `started_at` 降序，与接口一致。
- 每次加载 20 条，底部「加载更多」。
- 当前选中项用深蓝左边线标出。

### 3.3 中栏：三个标签页

选中 Run 后默认进入「概览」。

**概览**

- 计划步骤：按执行顺序横向排列，每步显示中文名、英文 `step_key` 和状态；失败的步骤显示 `error_code` 和尝试次数。
- 来源分布：每个源站一行横条，显示调用次数、成功次数、失败次数、论文数。
- Run 失败时，在顶部写出 `error_code`。

**候选论文**

- 表格列：标题、年份、DOI 或 arXiv ID、开放获取状态、相关性判定。
- 被过滤（`denied`）的论文照常显示，整行淡化，并写出判定原因。
- 筛选：全部 / 保留 / 被过滤 / 未判定。
- 一次取完所有页（`limit=100` 循环到 `total`），再在页面里筛选；接口没有筛选参数。

**结论**

- 每条结论显示支持状态、结论正文、证据数、置信度。
- 没有证据的结论写「未关联证据，只能视为待验证」。
- 每次加载 20 条，「加载更多」。
- 点一条结论，右栏显示它的证据链，网址同步更新。

### 3.4 右栏：证据链

从上到下：

1. 结论 Claim：正文和支持状态。
2. 每条证据片段 Evidence Span 一组，可折叠：引文原文、位置、证据级别、抽取方法、置信度、是否已重新定位。
3. 论文 Paper：标题、年份、会议或期刊、DOI、arXiv ID。
4. 源站记录 Source Record：源站、源站侧 ID、抓取时间。
5. 仅当证据级别为 `full_text`：文件 File（类型、状态、大小、项目相对路径）和解析文本 Document（解析器、解析状态、文本路径）。

卡片之间用一行小字说明关系：「由证据支持」「出自」「来自源站」「全文文件」「解析为」。

每张卡片底部有「详细信息」，展开后显示：ID、`quote` 所在的 `locator` 原始对象、`canonical_key`、`sha256`、`api_endpoint`、解析器版本等。

### 3.5 网址

当前位置写进网址的 hash，刷新或分享后停在同一处：

| 网址 | 含义 |
|---|---|
| `#/runs` | 只有 Run 列表 |
| `#/runs/{run_id}/overview` | 某 Run 的概览 |
| `#/runs/{run_id}/papers` | 某 Run 的候选论文 |
| `#/runs/{run_id}/claims` | 某 Run 的结论列表 |
| `#/runs/{run_id}/claims/{claim_id}` | 结论列表并在右栏打开该结论的证据链 |

无法识别的网址回到 `#/runs`。

### 3.6 窄屏

| 宽度 | 布局 |
|---|---|
| 1200px 及以上 | 三栏同时可见 |
| 900–1199px | 右栏变成从右侧滑出的抽屉，选中结论时打开，有关闭按钮 |
| 900px 以下 | 左栏收成顶部的 Run 下拉选择；右栏仍是抽屉 |

## 4. 代码结构

全部在 `web/src/` 下。每个文件只做一件事。

| 文件 | 职责 |
|---|---|
| `api/types.ts` | 按 `docs/local-api.md` 写的响应类型 |
| `api/client.ts` | 只发 `GET`；检查 `api_version === "v1"`；把错误转成 `ApiError`（`unreachable`、`not_found`、`invalid_request`、`internal_error`、`version_mismatch`） |
| `api/cache.ts` | 按 ID 缓存单个资源，同一页面会话内同一 ID 只请求一次 |
| `routing.ts` | 解析和生成 hash 网址；`useRoute` 监听 `hashchange` |
| `labels.ts` | 状态值到中文的对照，见第 5 节 |
| `format.ts` | 把 UTC 时间显示为北京时间（`Intl.DateTimeFormat`，`timeZone: "Asia/Shanghai"`） |
| `components/StatusBadge.tsx` | 中文加英文原值的状态标签 |
| `components/Details.tsx` | 用 `<details>` 折叠的技术字段 |
| `components/RunList.tsx` | 左栏 |
| `components/RunOverview.tsx` | 概览标签页（步骤进度、来源横条） |
| `components/PaperTable.tsx` | 候选论文标签页 |
| `components/ClaimList.tsx` | 结论标签页 |
| `components/EvidenceChain.tsx` | 右栏，内含各类卡片 |
| `styles.css` | 颜色、字体、间距等设计变量与布局 |
| `App.tsx` | 顶栏、三栏骨架、根据网址组合组件 |

### 4.1 数据流

1. 打开页面：`GET /v1/runs?limit=20&offset=0`。
2. 选中 Run：`GET /v1/runs/{run_id}`；按当前标签页再取 `steps` 与 `sources`、`papers` 或 `claims`。
3. 选中结论：读出 `evidence_span_ids`，并行 `GET /v1/evidence-spans/{id}`。
4. 每条证据再并行取 `papers/{paper_id}` 和 `source-records/{source_record_id}`。
5. 只有 `evidence_level === "full_text"` 时，再取 `files/{file_id}` 和 `documents/{document_id}`。
6. 第 3 到 5 步走 `api/cache.ts`，切换回已看过的结论不重复请求。

## 5. 文字对照

界面用中文，状态值旁附英文原值，例如「已完成 COMPLETED」。论文标题和引文保持原文。

| 字段 | 原值 → 中文 |
|---|---|
| Run `status` | `CREATED` 已创建、`PLANNED` 已规划、`RUNNING` 运行中、`WAITING_CONFIRMATION` 待确认、`PAUSED` 已暂停、`COMPLETED` 已完成、`FAILED` 失败、`CANCELLED` 已取消 |
| 步骤 `status` | `PENDING` 等待、`READY` 就绪、`RUNNING` 运行中、`RETRYING` 重试中、`SUCCEEDED` 成功、`FAILED` 失败、`SKIPPED` 跳过 |
| 步骤 `step_key` | `route_sources` 路由、`search_sources` 检索、`persist_results` 入库、`judge_relevance` 相关性判断、`synthesize_claims` 结论综合、`validate_citations` 引用校验、`generate_report` 生成报告；未知值原样显示 |
| `support_status` | `supported` 有证据、`partially_supported` 部分支持、`unsupported` 无证据、`disputed` 有争议 |
| `evidence_level` | `metadata` 元数据、`abstract` 摘要、`full_text` 全文、`external` 外部材料 |
| `extraction_method` | `rule` 规则抽取、`pdf_parser` PDF 解析、`llm` 模型抽取、`human` 人工 |
| 相关性 `decision` | `allowed` 保留、`denied` 被过滤、`not_judged` 未判定 |
| 文件 `status` | `stored` 已保存、`quarantined` 已隔离、`missing` 缺失、`deleted` 已删除 |

## 6. 加载、空状态与错误

### 6.1 加载

固定高度的灰色占位块，数据到了再替换，不让页面跳动。右栏按 `evidence_span_ids` 的数量先画占位卡片。

### 6.2 空状态

| 情况 | 显示 |
|---|---|
| 没有任何 Run | 「还没有 Run。先运行 `research-agent research "<问题>"`，再刷新本页。」 |
| Run 没有结论 | 「这个 Run 没有生成结论。」 |
| 结论没有证据 | 「未关联证据，只能视为待验证。」 |
| Run 没有计划步骤或来源调用 | 「没有记录。」 |

### 6.3 错误

错误只出现在出错的那一块，其他部分照常可用。每个错误写出原因，并给「重试」按钮（版本不匹配除外）。

| `ApiError` | 显示 |
|---|---|
| `unreachable` | 顶栏变为「连不上本地 API（地址）」；面板提示「请先运行 `research-agent serve`」 |
| `not_found` | 「找不到这个 Run」或「找不到这条结论」，并给出回到 `#/runs` 的链接 |
| `version_mismatch` | 「API 版本不匹配，前端需要 v1。」不解析数据 |
| `internal_error` | 「服务器出错。」 |
| `invalid_request` | 「请求参数不合法。」 |

一条结论有多条证据时，某条证据或它的论文、源站记录没取到，只有那张卡片报错并可重试，其余卡片照常显示。

### 6.4 需要标出的数据情况

- 结论引用的论文被相关性过滤（`decision === "denied"`）：照常显示，论文卡片加警告「该论文已被相关性过滤」。按契约这不应出现，出现即数据问题。
- 文件 `status === "quarantined"`：标「已隔离，不能作为证据」。
- 文件 `path` 为空：显示「未保存到磁盘」。

### 6.5 可访问性

- 状态都用文字标出，不只靠颜色。
- Run、标签页、结论都是 `<button>` 或带键盘支持的元素；标签页使用 `role="tablist"`。
- 有清楚的焦点框。
- 错误区域使用 `role="alert"`。
- 抽屉打开时焦点移入，`Esc` 关闭并把焦点还给触发它的结论。

## 7. 视觉风格

浅色，像在读文献。深蓝只用来标“当前选中”和证据链路。

| 变量 | 值 | 用途 |
|---|---|---|
| `--surface` | `#ffffff` | 中栏、卡片 |
| `--surface-muted` | `#fafaf9` | 顶栏、左栏、右栏 |
| `--border` | `#e7e5e4` | 分隔线、卡片边框 |
| `--text` | `#1f2937` | 正文 |
| `--text-muted` | `#78716c` | 次要信息 |
| `--accent` | `#1e3a8a` | 选中、链接、卡片标题 |
| `--accent-soft` | `#eff6ff` | 选中背景 |
| `--ok` / `--ok-soft` | `#166534` / `#dcfce7` | 成功、有证据、保留 |
| `--bad` / `--bad-soft` | `#991b1b` / `#fee2e2` | 失败、无证据、被过滤 |
| `--warn` / `--warn-soft` | `#92400e` / `#fef3c7` | 运行中、部分支持、已隔离 |

- 正文字体：`"Segoe UI", "Microsoft YaHei", system-ui, sans-serif`，14px，行高 1.55。
- 引文字体：`Georgia, "Songti SC", SimSun, serif`，15px，左侧 3px 深蓝边线。
- 等宽字体：`Consolas, "Cascadia Mono", monospace`，用于 ID、DOI、哈希。
- 间距按 4px 递增；圆角 8px；不用阴影。唯一的动画是抽屉滑出（200ms），开启 `prefers-reduced-motion` 时直接显示。
- 文字和背景的对比度至少 4.5:1。

## 8. 测试

全部离线，不需要启动后端。

- `api/client.ts`：用模拟的 `fetch` 测版本不是 `v1` 时报 `version_mismatch`；404、500 转成对应类型；网络失败转成 `unreachable`；只用 `GET`。
- `routing.ts`：解析与生成来回一致；非法网址回到 `#/runs`。
- `labels.ts` 与 `format.ts`：已知值有中文；未知值原样显示；UTC 显示为北京时间。
- 组件（Testing Library，模拟接口）：
  1. 点一条结论后，右栏依次出现证据、论文、源站记录。
  2. 全文证据多出文件和解析文本卡片。
  3. 没有证据的结论显示「未关联证据」。
  4. 被过滤的论文在候选列表里显示原因，四种筛选都正确。
  5. 一条证据请求失败时，只有那张卡片报错，其余照常。
  6. 连不上 API 时，顶栏和面板都显示提示。
- 静态检查：`web/src` 中除 `api/client.ts` 外不直接调用 `fetch`；`client.ts` 只发 `GET`。
- 收尾：`uv run python scripts/check_web.py` 通过；用真实的 `research-agent serve` 打开一个已有 Run，截图核对整条证据链。

## 9. 不在本次范围

- 提问、取消任务、实时进度推送（`FE-05`–`FE-07`）。
- 报告渲染与 JSON/CSV/BibTeX 下载（`FE-08`）。
- 人工确认（`FE-09`）。
- 关系图视图、深色主题。
- 浏览器端到端测试（`FE-10`）。

## 10. 验收

- 一个完整 Run 能在页面里从结论追到证据片段、论文、源站记录；全文证据再到文件和解析文本。
- 被过滤论文能看到原因；没有证据的结论被明确标出。
- 页面只读，不展示存储里没有的证据。
- `uv run python scripts/check_web.py`、Python 侧全部检查通过。
