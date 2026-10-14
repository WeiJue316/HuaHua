# 证据链查看器实现计划（FE-04）

> **给执行者：** 按任务顺序执行，每一步用 `- [ ]` 跟踪。每个任务先写失败的测试，再写实现。

**目标：** 在 `web/` 中实现只读的证据链查看器，一个完整 Run 能从结论追到证据片段、论文、源站记录，全文证据再到文件和解析文本。

**做法：** React 单页应用，三栏布局。所有数据通过 `api/client.ts` 以 `GET` 读取本地 `/v1` 接口。网址的 hash 保存当前位置。组件按“Run 列表 / Run 内容 / 证据链”拆分，各自负责加载、空状态和错误。

**技术栈：** React 19、TypeScript 5、Vite 7、Vitest 3、Testing Library（jsdom）。不新增依赖。

**设计：** `docs/evidence-viewer.md`。执行时同时打开设计文档。

## 全局约束

- 不修改 `web/package.json` 的依赖；不新增任何 npm 包。
- 页面只发 `GET`；除 `web/src/api/client.ts` 外不直接调用 `fetch`。
- 默认 API 地址 `http://127.0.0.1:8765`，可用 `VITE_API_BASE` 覆盖。
- 界面文字用中文，状态值旁附英文原值，例如「已完成 COMPLETED」；论文标题和引文保持原文。
- 时间按北京时间显示，格式 `YYYY-MM-DD HH:mm`。
- 不加载外部字体或外部资源。
- 断点：1200px 及以上三栏；900–1199px 右栏为抽屉；900px 以下左栏变为下拉选择。
- 颜色变量：`--surface #ffffff`、`--surface-muted #fafaf9`、`--border #e7e5e4`、`--text #1f2937`、`--text-muted #78716c`、`--accent #1e3a8a`、`--accent-soft #eff6ff`、`--ok #166534 / #dcfce7`、`--bad #991b1b / #fee2e2`、`--warn #92400e / #fef3c7`。
- 引文字体 `Georgia, "Songti SC", SimSun, serif`，15px，左侧 3px 深蓝边线。
- 不执行 `git commit`，除非用户要求。每个任务结束时在 `web/` 运行 `npm run check`。
- 新增目录或文件时，同步更新 `AGENTS.md` §4 目录树；`scripts/check_docs.py` 会检查其中列出的文件是否存在。

## 重点检查

设计没有逐条写出、但最容易让使用者碰到的情况：

1. 网址里的结论 ID 不存在（复制错链接、数据库换了）：右栏显示「找不到这条结论。」和回到列表的链接，不是空白。由任务 5 的测试覆盖。
2. 一次请求失败后点「重试」：必须重新请求，不能复用缓存里的失败结果。由任务 1 的缓存测试和任务 5 的重试测试覆盖。
3. 文件处于隔离状态且路径为空：显示「已隔离，不能作为证据。」和「未保存到磁盘」。由任务 5 的测试覆盖。
4. 后端以后新增状态值或步骤键：原样显示该值，不显示空白。由任务 2 的文字对照测试覆盖。
5. Run 超过一页：「加载更多」把新的一页追加在后面，不覆盖已显示的 Run。由任务 3 的测试覆盖。

长标题和长引文换行不出现横向滚动条：无法用单元测试覆盖，在任务 6 的真实页面截图中核对。

---

### 任务 1：测试基础与接口层

**文件：**
- 修改：`web/vite.config.ts`
- 修改：`web/src/vite-env.d.ts`
- 新建：`web/src/test/setup.ts`
- 新建：`web/src/test/fakeApi.ts`
- 新建：`web/src/test/fixtures.ts`
- 新建：`web/src/api/types.ts`
- 新建：`web/src/api/client.ts`
- 新建：`web/src/api/cache.ts`
- 新建：`web/src/api/evidence.ts`
- 测试：`web/src/api/client.test.ts`、`web/src/api/cache.test.ts`、`web/src/api/evidence.test.ts`
- 修改：`AGENTS.md`（目录树）

**接口：**
- 产出：`ApiError`（`kind: ApiErrorKind`）、`ApiErrorKind`、`API_BASE: string`、`getJson<T>(path, base?)`、`api.*`、`listAllPapers(runId): Promise<Paper[]>`。
- 产出：`createResourceCache(): ResourceCache`，`cache.get<T>(key, load): Promise<T>`。
- 产出：`loadEvidence(cache, evidenceSpanId): Promise<EvidenceBundle>`，`EvidenceBundle = { span, paper, record, file, document }`。
- 产出（测试用）：`installFakeApi(routes, fallback?)` 返回调用记录 `{ url, method }[]`；`failure(status, code, message)`；`NETWORK_DOWN`；`viewerRoutes()` 与样例常量。

- [ ] **步骤 1：更新目录树**

`AGENTS.md` §4 中 `web/` 的 `src/` 下改为：

```text
│   └── src/
│       ├── App.tsx              # 三栏骨架与网址路由
│       ├── api/                 # 只读 /v1 客户端、类型与缓存
│       ├── components/          # Run 列表、概览、候选论文、结论、证据链
│       └── test/                # 测试用的模拟接口与样例数据
```

- [ ] **步骤 2：配置测试环境**

`web/vite.config.ts` 的 `test` 改为：

```ts
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
  },
```

`web/src/vite-env.d.ts`：

```ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE?: string;
}
```

`web/src/test/setup.ts`：

```ts
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.location.hash = "";
});
```

`web/src/test/fakeApi.ts`：

```ts
import { vi } from "vitest";

export const NETWORK_DOWN = Symbol("network-down");

export class Reply {
  readonly status: number;
  readonly body: unknown;

  constructor(status: number, body: unknown) {
    this.status = status;
    this.body = body;
  }
}

export type FakeRoutes = Record<string, unknown>;

export interface FakeCall {
  url: string;
  method: string;
}

export function failure(status: number, code: string, message: string): Reply {
  return new Reply(status, { api_version: "v1", error: { code, message } });
}

export function installFakeApi(routes: FakeRoutes, fallback?: unknown): FakeCall[] {
  const calls: FakeCall[] = [];
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(String(input));
    const key = `${url.pathname}${url.search}`;
    calls.push({ url: key, method: init?.method ?? "GET" });
    const route = key in routes ? routes[key] : fallback;
    if (route === NETWORK_DOWN) {
      throw new TypeError("Failed to fetch");
    }
    if (route === undefined) {
      return toResponse(failure(404, "not_found", "not found"));
    }
    if (route instanceof Reply) {
      return toResponse(route);
    }
    return toResponse(
      new Reply(200, { api_version: "v1", ...(route as Record<string, unknown>) }),
    );
  });
  vi.stubGlobal("fetch", fetchMock);
  return calls;
}

function toResponse(reply: Reply): Response {
  return new Response(JSON.stringify(reply.body), {
    status: reply.status,
    headers: { "Content-Type": "application/json" },
  });
}
```

- [ ] **步骤 3：写响应类型**

`web/src/api/types.ts`：

```ts
export interface Versioned {
  api_version: string;
}

export interface Page<T> extends Versioned {
  items: T[];
  limit: number;
  offset: number;
  total: number;
}

export interface Items<T> extends Versioned {
  items: T[];
}

export interface RunSummary {
  id: string;
  question_text: string;
  status: string;
  trigger: string;
  started_at: string | null;
  finished_at: string | null;
  error_code: string | null;
  paper_count: number;
  evidence_count: number;
  claim_count: number;
}

export interface RunDetail extends RunSummary {
  project_id: string;
  question_id: string;
}

export interface PlanStep {
  id: string;
  step_key: string;
  step_type: string;
  status: string;
  depends_on: string[];
  attempt_count: number;
  started_at: string | null;
  finished_at: string | null;
  error_code: string | null;
}

export interface SourceSummary {
  source: string;
  call_count: number;
  success_count: number;
  failed_count: number;
  paper_count: number;
}

export type RelevanceDecision = "allowed" | "denied" | "not_judged";

export interface Relevance {
  decision: RelevanceDecision;
  reason: string | null;
  domain_scope: string | null;
  answer_role: string | null;
}

export interface Paper {
  id: string;
  title: string;
  year: number | null;
  venue: string | null;
  doi: string | null;
  arxiv_id: string | null;
  canonical_key: string;
  open_access_status: string | null;
  source_record_ids: string[];
  relevance: Relevance;
}

export interface Claim {
  id: string;
  report_id: string;
  claim_text: string;
  claim_type: string;
  support_status: string;
  confidence: number;
  evidence_span_ids: string[];
}

export interface EvidenceSpan {
  id: string;
  paper_id: string;
  source_record_id: string;
  quote: string;
  locator: Record<string, unknown>;
  evidence_level: string;
  extraction_method: string;
  confidence: number;
  verified: boolean;
  file_id: string | null;
  document_id: string | null;
}

export interface SourceRecord {
  id: string;
  source: string;
  source_record_id: string;
  retrieved_at: string;
  api_endpoint: string;
}

export interface FileRecord {
  id: string;
  paper_id: string;
  kind: string;
  sha256: string;
  path: string;
  size_bytes: number;
  content_type: string;
  source_url: string;
  retrieved_at: string;
  status: string;
}

export interface DocumentRecord {
  id: string;
  file_id: string;
  parser: string;
  parser_version: string;
  text_path: string;
  locator_scheme: string;
  parse_status: string;
}
```

- [ ] **步骤 4：写样例数据**

`web/src/test/fixtures.ts`：

```ts
import type {
  Claim,
  DocumentRecord,
  EvidenceSpan,
  FileRecord,
  Paper,
  PlanStep,
  RunDetail,
  SourceRecord,
  SourceSummary,
} from "../api/types";
import type { FakeRoutes } from "./fakeApi";

export const RUN: RunDetail = {
  id: "run-1",
  question_text: "What are the main evaluation methods for RAG systems?",
  status: "COMPLETED",
  trigger: "cli",
  started_at: "2026-10-12T13:40:00Z",
  finished_at: "2026-10-12T13:52:00Z",
  error_code: null,
  paper_count: 2,
  evidence_count: 2,
  claim_count: 3,
  project_id: "project-1",
  question_id: "question-1",
};

export const SECOND_RUN: RunDetail = {
  ...RUN,
  id: "run-2",
  question_text: "How do agentic tool-use methods plan?",
  status: "FAILED",
  error_code: "unresolved_dependencies",
};

export const STEPS: PlanStep[] = [
  {
    id: "step-1",
    step_key: "route_sources",
    step_type: "route_sources",
    status: "SUCCEEDED",
    depends_on: [],
    attempt_count: 1,
    started_at: "2026-10-12T13:40:00Z",
    finished_at: "2026-10-12T13:40:01Z",
    error_code: null,
  },
  {
    id: "step-2",
    step_key: "search_sources",
    step_type: "search_sources",
    status: "FAILED",
    depends_on: ["route_sources"],
    attempt_count: 3,
    started_at: "2026-10-12T13:40:01Z",
    finished_at: "2026-10-12T13:41:00Z",
    error_code: "upstream_unavailable",
  },
];

export const SOURCES: SourceSummary[] = [
  { source: "openalex", call_count: 4, success_count: 4, failed_count: 0, paper_count: 2 },
  { source: "arxiv", call_count: 2, success_count: 1, failed_count: 1, paper_count: 1 },
];

export const ALLOWED_PAPER: Paper = {
  id: "paper-1",
  title: "RAGAs: Automated Evaluation of Retrieval Augmented Generation",
  year: 2024,
  venue: "EACL",
  doi: "10.18653/v1/2024.eacl-demo.16",
  arxiv_id: null,
  canonical_key: "doi:10.18653/v1/2024.eacl-demo.16",
  open_access_status: "green",
  source_record_ids: ["record-1"],
  relevance: {
    decision: "allowed",
    reason: "directly answers the question",
    domain_scope: "in_scope",
    answer_role: "direct",
  },
};

export const DENIED_PAPER: Paper = {
  id: "paper-2",
  title: "Chip Floorplanning with Reinforcement Learning",
  year: 2023,
  venue: null,
  doi: null,
  arxiv_id: "2301.00001",
  canonical_key: "arxiv:2301.00001",
  open_access_status: null,
  source_record_ids: ["record-2"],
  relevance: {
    decision: "denied",
    reason: "out of scope",
    domain_scope: "out_of_scope",
    answer_role: "none",
  },
};

export const ABSTRACT_SPAN: EvidenceSpan = {
  id: "span-1",
  paper_id: "paper-1",
  source_record_id: "record-1",
  quote:
    "With RAGAs, we introduce a suite of metrics that can evaluate these different dimensions without relying on ground truth human annotations.",
  locator: { section: "Abstract" },
  evidence_level: "abstract",
  extraction_method: "rule",
  confidence: 0.8,
  verified: true,
  file_id: null,
  document_id: null,
};

export const FULL_TEXT_SPAN: EvidenceSpan = {
  id: "span-2",
  paper_id: "paper-1",
  source_record_id: "record-1",
  quote: "Faithfulness measures whether the answer is grounded in the retrieved context.",
  locator: { page: 3, paragraph_index: 2, char_start: 120, char_end: 198 },
  evidence_level: "full_text",
  extraction_method: "pdf_parser",
  confidence: 0.7,
  verified: true,
  file_id: "file-1",
  document_id: "document-1",
};

export const RECORD: SourceRecord = {
  id: "record-1",
  source: "openalex",
  source_record_id: "W4392",
  retrieved_at: "2026-10-12T13:38:00Z",
  api_endpoint: "https://api.openalex.org/works",
};

export const FILE: FileRecord = {
  id: "file-1",
  paper_id: "paper-1",
  kind: "pdf",
  sha256: "a".repeat(64),
  path: "data/archive/papers/a.pdf",
  size_bytes: 204800,
  content_type: "application/pdf",
  source_url: "https://arxiv.org/pdf/2309.15217",
  retrieved_at: "2026-10-12T13:39:00Z",
  status: "stored",
};

export const DOCUMENT: DocumentRecord = {
  id: "document-1",
  file_id: "file-1",
  parser: "pypdf",
  parser_version: "6.1.0",
  text_path: "data/archive/parsed/document-1.txt",
  locator_scheme: "page_paragraph",
  parse_status: "success",
};

export const CLAIMS: Claim[] = [
  {
    id: "claim-1",
    report_id: "report-1",
    claim_text: "RAGAs proposes reference-free metrics for RAG evaluation.",
    claim_type: "fact",
    support_status: "supported",
    confidence: 0.8,
    evidence_span_ids: ["span-1"],
  },
  {
    id: "claim-2",
    report_id: "report-1",
    claim_text: "Faithfulness checks grounding in the retrieved context.",
    claim_type: "fact",
    support_status: "supported",
    confidence: 0.7,
    evidence_span_ids: ["span-2"],
  },
  {
    id: "claim-3",
    report_id: "report-1",
    claim_text: "RAG evaluation is shifting to nugget-based methods.",
    claim_type: "trend",
    support_status: "unsupported",
    confidence: 0.3,
    evidence_span_ids: [],
  },
];

export function page<T>(items: T[], limit: number, offset = 0, total = items.length) {
  return { items, limit, offset, total };
}

export function viewerRoutes(): FakeRoutes {
  return {
    "/v1/runs?limit=1&offset=0": page([RUN], 1),
    "/v1/runs?limit=20&offset=0": page([RUN], 20),
    "/v1/runs/run-1": RUN,
    "/v1/runs/run-1/steps": { items: STEPS },
    "/v1/runs/run-1/sources": { items: SOURCES },
    "/v1/runs/run-1/papers?limit=100&offset=0": page([ALLOWED_PAPER, DENIED_PAPER], 100),
    "/v1/runs/run-1/claims?limit=20&offset=0": page(CLAIMS, 20),
    "/v1/claims/claim-1": CLAIMS[0],
    "/v1/claims/claim-2": CLAIMS[1],
    "/v1/claims/claim-3": CLAIMS[2],
    "/v1/evidence-spans/span-1": ABSTRACT_SPAN,
    "/v1/evidence-spans/span-2": FULL_TEXT_SPAN,
    "/v1/papers/paper-1": ALLOWED_PAPER,
    "/v1/source-records/record-1": RECORD,
    "/v1/files/file-1": FILE,
    "/v1/documents/document-1": DOCUMENT,
  };
}
```

- [ ] **步骤 5：写失败的接口测试**

`web/src/api/client.test.ts`：

```ts
import { describe, expect, it, vi } from "vitest";
import { getJson, listAllPapers } from "./client";
import { NETWORK_DOWN, failure, installFakeApi } from "../test/fakeApi";
import { ALLOWED_PAPER, DENIED_PAPER, page } from "../test/fixtures";

describe("getJson", () => {
  it("returns a v1 body and sends only GET", async () => {
    const calls = installFakeApi({ "/v1/runs": { items: [] } });

    await expect(getJson("/v1/runs", "http://api.test")).resolves.toEqual({
      api_version: "v1",
      items: [],
    });
    expect(calls).toEqual([{ url: "/v1/runs", method: "GET" }]);
  });

  it("rejects a body from another API version", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(JSON.stringify({ api_version: "v2" }), { status: 200 })),
    );

    await expect(getJson("/v1/runs", "http://api.test")).rejects.toMatchObject({
      kind: "version_mismatch",
    });
  });

  it.each<[number, string, string]>([
    [404, "not_found", "not_found"],
    [400, "invalid_request", "invalid_request"],
    [500, "internal_error", "internal_error"],
  ])("maps HTTP %s to %s", async (status, code, kind) => {
    installFakeApi({ "/v1/runs": failure(status, code, "message") });

    await expect(getJson("/v1/runs", "http://api.test")).rejects.toMatchObject({ kind });
  });

  it("reports an unreachable API", async () => {
    installFakeApi({}, NETWORK_DOWN);

    await expect(getJson("/v1/runs", "http://api.test")).rejects.toMatchObject({
      kind: "unreachable",
      message: "连不上本地 API（http://api.test）",
    });
  });

  it("treats a body that is not JSON as a server error", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response("<html>", { status: 502 })));

    await expect(getJson("/v1/runs", "http://api.test")).rejects.toMatchObject({
      kind: "internal_error",
    });
  });
});

describe("listAllPapers", () => {
  it("reads every page", async () => {
    installFakeApi({
      "/v1/runs/run-1/papers?limit=100&offset=0": page([ALLOWED_PAPER], 100, 0, 2),
      "/v1/runs/run-1/papers?limit=100&offset=1": page([DENIED_PAPER], 100, 1, 2),
    });

    const papers = await listAllPapers("run-1");

    expect(papers.map((paper) => paper.id)).toEqual(["paper-1", "paper-2"]);
  });
});
```

`web/src/api/cache.test.ts`：

```ts
import { describe, expect, it, vi } from "vitest";
import { createResourceCache } from "./cache";

describe("createResourceCache", () => {
  it("loads one key once", async () => {
    const cache = createResourceCache();
    const load = vi.fn(async () => "value");

    await cache.get("key", load);
    await cache.get("key", load);

    expect(load).toHaveBeenCalledTimes(1);
  });

  it("loads again after a failure", async () => {
    const cache = createResourceCache();
    const load = vi
      .fn<() => Promise<string>>()
      .mockRejectedValueOnce(new Error("first"))
      .mockResolvedValueOnce("second");

    await expect(cache.get("key", load)).rejects.toThrow("first");
    await expect(cache.get("key", load)).resolves.toBe("second");
    expect(load).toHaveBeenCalledTimes(2);
  });
});
```

`web/src/api/evidence.test.ts`：

```ts
import { describe, expect, it } from "vitest";
import { createResourceCache } from "./cache";
import { loadEvidence } from "./evidence";
import { installFakeApi } from "../test/fakeApi";
import { viewerRoutes } from "../test/fixtures";

describe("loadEvidence", () => {
  it("does not request a file for abstract evidence", async () => {
    const calls = installFakeApi(viewerRoutes());

    const bundle = await loadEvidence(createResourceCache(), "span-1");

    expect(bundle.paper.id).toBe("paper-1");
    expect(bundle.record.source).toBe("openalex");
    expect(bundle.file).toBeNull();
    expect(bundle.document).toBeNull();
    expect(calls.some((call) => call.url.startsWith("/v1/files/"))).toBe(false);
  });

  it("loads the file and document for full-text evidence", async () => {
    installFakeApi(viewerRoutes());

    const bundle = await loadEvidence(createResourceCache(), "span-2");

    expect(bundle.file?.id).toBe("file-1");
    expect(bundle.document?.id).toBe("document-1");
  });
});
```

- [ ] **步骤 6：确认测试失败**

在 `web/` 运行：`npm run test -- src/api`

预期：失败，提示找不到 `./client`、`./cache`、`./evidence`。

- [ ] **步骤 7：写实现**

`web/src/api/client.ts`：

```ts
import type {
  Claim,
  DocumentRecord,
  EvidenceSpan,
  FileRecord,
  Items,
  Page,
  Paper,
  PlanStep,
  RunDetail,
  RunSummary,
  SourceRecord,
  SourceSummary,
  Versioned,
} from "./types";

export type ApiErrorKind =
  | "unreachable"
  | "not_found"
  | "invalid_request"
  | "internal_error"
  | "version_mismatch";

export class ApiError extends Error {
  readonly kind: ApiErrorKind;

  constructor(kind: ApiErrorKind, message: string) {
    super(message);
    this.name = "ApiError";
    this.kind = kind;
  }
}

export const API_BASE: string = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8765";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function kindForStatus(status: number): ApiErrorKind {
  if (status === 404) {
    return "not_found";
  }
  if (status === 400) {
    return "invalid_request";
  }
  return "internal_error";
}

function errorMessage(body: Record<string, unknown>): string {
  const error = body.error;
  if (isRecord(error) && typeof error.message === "string") {
    return error.message;
  }
  return "request failed";
}

export async function getJson<T extends Versioned>(
  path: string,
  base: string = API_BASE,
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${base}${path}`, {
      method: "GET",
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new ApiError("unreachable", `连不上本地 API（${base}）`);
  }
  let body: unknown;
  try {
    body = await response.json();
  } catch {
    throw new ApiError("internal_error", "服务器出错");
  }
  if (!isRecord(body) || body.api_version !== "v1") {
    throw new ApiError("version_mismatch", "API 版本不匹配，前端需要 v1");
  }
  if (!response.ok) {
    throw new ApiError(kindForStatus(response.status), errorMessage(body));
  }
  return body as unknown as T;
}

const segment = encodeURIComponent;

export const api = {
  listRuns: (limit: number, offset: number) =>
    getJson<Page<RunSummary>>(`/v1/runs?limit=${limit}&offset=${offset}`),
  getRun: (runId: string) => getJson<RunDetail & Versioned>(`/v1/runs/${segment(runId)}`),
  listSteps: (runId: string) => getJson<Items<PlanStep>>(`/v1/runs/${segment(runId)}/steps`),
  listSources: (runId: string) =>
    getJson<Items<SourceSummary>>(`/v1/runs/${segment(runId)}/sources`),
  listPapers: (runId: string, limit: number, offset: number) =>
    getJson<Page<Paper>>(`/v1/runs/${segment(runId)}/papers?limit=${limit}&offset=${offset}`),
  listClaims: (runId: string, limit: number, offset: number) =>
    getJson<Page<Claim>>(`/v1/runs/${segment(runId)}/claims?limit=${limit}&offset=${offset}`),
  getClaim: (claimId: string) => getJson<Claim & Versioned>(`/v1/claims/${segment(claimId)}`),
  getPaper: (paperId: string) => getJson<Paper & Versioned>(`/v1/papers/${segment(paperId)}`),
  getEvidenceSpan: (evidenceSpanId: string) =>
    getJson<EvidenceSpan & Versioned>(`/v1/evidence-spans/${segment(evidenceSpanId)}`),
  getSourceRecord: (sourceRecordId: string) =>
    getJson<SourceRecord & Versioned>(`/v1/source-records/${segment(sourceRecordId)}`),
  getFile: (fileId: string) => getJson<FileRecord & Versioned>(`/v1/files/${segment(fileId)}`),
  getDocument: (documentId: string) =>
    getJson<DocumentRecord & Versioned>(`/v1/documents/${segment(documentId)}`),
};

export async function listAllPapers(runId: string): Promise<Paper[]> {
  const papers: Paper[] = [];
  for (;;) {
    const result = await api.listPapers(runId, 100, papers.length);
    papers.push(...result.items);
    if (result.items.length === 0 || papers.length >= result.total) {
      return papers;
    }
  }
}
```

`web/src/api/cache.ts`：

```ts
export interface ResourceCache {
  get<T>(key: string, load: () => Promise<T>): Promise<T>;
}

export function createResourceCache(): ResourceCache {
  const entries = new Map<string, Promise<unknown>>();
  return {
    get<T>(key: string, load: () => Promise<T>): Promise<T> {
      const existing = entries.get(key);
      if (existing !== undefined) {
        return existing as Promise<T>;
      }
      const pending = load().catch((error: unknown) => {
        entries.delete(key);
        throw error;
      });
      entries.set(key, pending);
      return pending;
    },
  };
}
```

`web/src/api/evidence.ts`：

```ts
import type { ResourceCache } from "./cache";
import { api } from "./client";
import type { DocumentRecord, EvidenceSpan, FileRecord, Paper, SourceRecord } from "./types";

export interface EvidenceBundle {
  span: EvidenceSpan;
  paper: Paper;
  record: SourceRecord;
  file: FileRecord | null;
  document: DocumentRecord | null;
}

export async function loadEvidence(
  cache: ResourceCache,
  evidenceSpanId: string,
): Promise<EvidenceBundle> {
  const span = await cache.get(`evidence-span:${evidenceSpanId}`, () =>
    api.getEvidenceSpan(evidenceSpanId),
  );
  const [paper, record] = await Promise.all([
    cache.get(`paper:${span.paper_id}`, () => api.getPaper(span.paper_id)),
    cache.get(`source-record:${span.source_record_id}`, () =>
      api.getSourceRecord(span.source_record_id),
    ),
  ]);
  const fileId = span.file_id;
  const documentId = span.document_id;
  if (span.evidence_level !== "full_text" || fileId === null || documentId === null) {
    return { span, paper, record, file: null, document: null };
  }
  const [file, document] = await Promise.all([
    cache.get(`file:${fileId}`, () => api.getFile(fileId)),
    cache.get(`document:${documentId}`, () => api.getDocument(documentId)),
  ]);
  return { span, paper, record, file, document };
}
```

- [ ] **步骤 8：确认测试通过**

在 `web/` 运行：`npm run test -- src/api`

预期：3 个测试文件全部通过。

- [ ] **步骤 9：检查点**

在 `web/` 运行：`npm run check`。预期：lint、类型检查、测试、构建都通过。不提交。

---

### 任务 2：网址、文字对照与格式化

**文件：**
- 新建：`web/src/routing.ts`、`web/src/labels.ts`、`web/src/format.ts`
- 测试：`web/src/routing.test.ts`、`web/src/labels.test.ts`、`web/src/format.test.ts`

**接口：**
- 产出：`Tab = "overview" | "papers" | "claims"`、`TABS`、`Route`、`RunRoute`、`RUN_LIST`、`parseRoute(hash)`、`formatRoute(route)`、`useRoute(): [Route, (next: Route) => void]`。
- 产出：`Tone = "ok" | "bad" | "warn" | "neutral"`、`LabelKind`、`Label = { text, code, tone }`、`labelFor(kind, value): Label`。
- 产出：`formatTime(value: string | null): string`、`formatBytes(size: number): string`、`formatConfidence(value: number): string`、`formatLocator(locator: Record<string, unknown>): string`。

- [ ] **步骤 1：写失败的测试**

`web/src/routing.test.ts`：

```ts
import { describe, expect, it } from "vitest";
import { RUN_LIST, formatRoute, parseRoute, type Route } from "./routing";

describe("parseRoute", () => {
  it.each<[string, Route]>([
    ["", RUN_LIST],
    ["#/runs", RUN_LIST],
    ["#/runs/run-1", { runId: "run-1", tab: "overview", claimId: null }],
    ["#/runs/run-1/papers", { runId: "run-1", tab: "papers", claimId: null }],
    ["#/runs/run-1/claims/claim-1", { runId: "run-1", tab: "claims", claimId: "claim-1" }],
    ["#/runs/run%2F1/claims", { runId: "run/1", tab: "claims", claimId: null }],
  ])("reads %s", (hash, route) => {
    expect(parseRoute(hash)).toEqual(route);
  });

  it.each([
    "#/papers",
    "#/runs/run-1/unknown",
    "#/runs/run-1/papers/claim-1",
    "#/runs/run-1/claims/claim-1/extra",
    "#/runs/%E0%A4%A",
  ])("falls back to the run list for %s", (hash) => {
    expect(parseRoute(hash)).toEqual(RUN_LIST);
  });
});

describe("formatRoute", () => {
  it("round-trips through parseRoute", () => {
    const route = { runId: "run/1", tab: "claims" as const, claimId: "claim 1" };

    expect(parseRoute(formatRoute(route))).toEqual(route);
    expect(formatRoute(RUN_LIST)).toBe("#/runs");
  });
});
```

`web/src/labels.test.ts`：

```ts
import { describe, expect, it } from "vitest";
import { labelFor } from "./labels";

describe("labelFor", () => {
  it("gives Chinese text, the original code, and a tone", () => {
    expect(labelFor("runStatus", "COMPLETED")).toEqual({
      text: "已完成",
      code: "COMPLETED",
      tone: "ok",
    });
    expect(labelFor("relevance", "denied").tone).toBe("bad");
    expect(labelFor("fileStatus", "quarantined").tone).toBe("warn");
    expect(labelFor("stepKey", "route_sources").text).toBe("路由");
  });

  it("shows an unknown value as it is", () => {
    expect(labelFor("runStatus", "ARCHIVED")).toEqual({
      text: "ARCHIVED",
      code: "ARCHIVED",
      tone: "neutral",
    });
    expect(labelFor("stepKey", "export_results").text).toBe("export_results");
  });
});
```

`web/src/format.test.ts`：

```ts
import { describe, expect, it } from "vitest";
import { formatBytes, formatConfidence, formatLocator, formatTime } from "./format";

describe("formatTime", () => {
  it("shows UTC times in Beijing time", () => {
    expect(formatTime("2026-10-12T13:40:00Z")).toBe("2026-10-12 21:40");
    expect(formatTime("2026-10-12T20:05:00Z")).toBe("2026-10-13 04:05");
  });

  it("keeps missing and unreadable values visible", () => {
    expect(formatTime(null)).toBe("—");
    expect(formatTime("not a time")).toBe("not a time");
  });
});

describe("formatLocator", () => {
  it("joins the known locator fields", () => {
    expect(formatLocator({ section: "Abstract" })).toBe("Abstract");
    expect(formatLocator({ page: 3, paragraph_index: 2, char_start: 120, char_end: 198 })).toBe(
      "第 3 页 · 段落 2 · 字符 120–198",
    );
    expect(formatLocator({})).toBe("—");
  });
});

describe("numbers", () => {
  it("formats sizes and confidence", () => {
    expect(formatBytes(512)).toBe("512 B");
    expect(formatBytes(204800)).toBe("200.0 KB");
    expect(formatBytes(3 * 1024 * 1024)).toBe("3.0 MB");
    expect(formatConfidence(0.8)).toBe("0.80");
  });
});
```

- [ ] **步骤 2：确认测试失败**

在 `web/` 运行：`npm run test -- src/routing.test.ts src/labels.test.ts src/format.test.ts`

预期：失败，找不到 `./routing`、`./labels`、`./format`。

- [ ] **步骤 3：写实现**

`web/src/routing.ts`：

```ts
import { useCallback, useEffect, useState } from "react";

export type Tab = "overview" | "papers" | "claims";

export const TABS: readonly Tab[] = ["overview", "papers", "claims"];

export type Route = { runId: null } | { runId: string; tab: Tab; claimId: string | null };

export type RunRoute = Extract<Route, { runId: string }>;

export const RUN_LIST: Route = { runId: null };

function isTab(value: string): value is Tab {
  return (TABS as readonly string[]).includes(value);
}

export function parseRoute(hash: string): Route {
  const parts = hash
    .replace(/^#/, "")
    .split("/")
    .filter((part) => part !== "");
  if (parts[0] !== "runs" || parts.length === 1 || parts.length > 4) {
    return RUN_LIST;
  }
  let decoded: string[];
  try {
    decoded = parts.map((part) => decodeURIComponent(part));
  } catch {
    return RUN_LIST;
  }
  const runId = decoded[1];
  const tab = decoded[2] ?? "overview";
  if (!isTab(tab)) {
    return RUN_LIST;
  }
  const claimId = decoded[3] ?? null;
  if (claimId !== null && tab !== "claims") {
    return RUN_LIST;
  }
  return { runId, tab, claimId };
}

export function formatRoute(route: Route): string {
  if (route.runId === null) {
    return "#/runs";
  }
  const base = `#/runs/${encodeURIComponent(route.runId)}/${route.tab}`;
  return route.claimId === null ? base : `${base}/${encodeURIComponent(route.claimId)}`;
}

export function useRoute(): [Route, (next: Route) => void] {
  const [route, setRoute] = useState<Route>(() => parseRoute(window.location.hash));

  useEffect(() => {
    const onChange = () => setRoute(parseRoute(window.location.hash));
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);

  const navigate = useCallback((next: Route) => {
    const hash = formatRoute(next);
    if (window.location.hash !== hash) {
      window.location.hash = hash;
    }
    setRoute(next);
  }, []);

  return [route, navigate];
}
```

`web/src/labels.ts`：

```ts
export type Tone = "ok" | "bad" | "warn" | "neutral";

export type LabelKind =
  | "runStatus"
  | "stepStatus"
  | "stepKey"
  | "supportStatus"
  | "evidenceLevel"
  | "extractionMethod"
  | "relevance"
  | "fileStatus";

export interface Label {
  text: string;
  code: string;
  tone: Tone;
}

const TABLES: Record<LabelKind, Record<string, string>> = {
  runStatus: {
    CREATED: "已创建",
    PLANNED: "已规划",
    RUNNING: "运行中",
    WAITING_CONFIRMATION: "待确认",
    PAUSED: "已暂停",
    COMPLETED: "已完成",
    FAILED: "失败",
    CANCELLED: "已取消",
  },
  stepStatus: {
    PENDING: "等待",
    READY: "就绪",
    RUNNING: "运行中",
    RETRYING: "重试中",
    SUCCEEDED: "成功",
    FAILED: "失败",
    SKIPPED: "跳过",
  },
  stepKey: {
    route_sources: "路由",
    search_sources: "检索",
    persist_results: "入库",
    judge_relevance: "相关性判断",
    synthesize_claims: "结论综合",
    validate_citations: "引用校验",
    generate_report: "生成报告",
  },
  supportStatus: {
    supported: "有证据",
    partially_supported: "部分支持",
    unsupported: "无证据",
    disputed: "有争议",
  },
  evidenceLevel: {
    metadata: "元数据",
    abstract: "摘要",
    full_text: "全文",
    external: "外部材料",
  },
  extractionMethod: {
    rule: "规则抽取",
    pdf_parser: "PDF 解析",
    llm: "模型抽取",
    human: "人工",
  },
  relevance: {
    allowed: "保留",
    denied: "被过滤",
    not_judged: "未判定",
  },
  fileStatus: {
    stored: "已保存",
    quarantined: "已隔离",
    missing: "缺失",
    deleted: "已删除",
  },
};

const TONES: Record<string, Tone> = {
  COMPLETED: "ok",
  SUCCEEDED: "ok",
  supported: "ok",
  allowed: "ok",
  stored: "ok",
  FAILED: "bad",
  CANCELLED: "bad",
  unsupported: "bad",
  disputed: "bad",
  denied: "bad",
  missing: "bad",
  deleted: "bad",
  RUNNING: "warn",
  RETRYING: "warn",
  WAITING_CONFIRMATION: "warn",
  PAUSED: "warn",
  partially_supported: "warn",
  quarantined: "warn",
};

export function labelFor(kind: LabelKind, value: string): Label {
  return {
    text: TABLES[kind][value] ?? value,
    code: value,
    tone: TONES[value] ?? "neutral",
  };
}
```

`web/src/format.ts`：

```ts
const BEIJING = new Intl.DateTimeFormat("en-CA", {
  timeZone: "Asia/Shanghai",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  hourCycle: "h23",
});

export function formatTime(value: string | null): string {
  if (value === null || value === "") {
    return "—";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  const parts = Object.fromEntries(
    BEIJING.formatToParts(date).map((part) => [part.type, part.value]),
  );
  return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}`;
}

export function formatBytes(size: number): string {
  if (size < 1024) {
    return `${size} B`;
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

export function formatConfidence(value: number): string {
  return value.toFixed(2);
}

export function formatLocator(locator: Record<string, unknown>): string {
  const parts: string[] = [];
  if (typeof locator.section === "string" && locator.section !== "") {
    parts.push(locator.section);
  }
  if (typeof locator.page === "number") {
    parts.push(`第 ${locator.page} 页`);
  }
  if (typeof locator.paragraph_index === "number") {
    parts.push(`段落 ${locator.paragraph_index}`);
  }
  if (typeof locator.char_start === "number" && typeof locator.char_end === "number") {
    parts.push(`字符 ${locator.char_start}–${locator.char_end}`);
  }
  return parts.length > 0 ? parts.join(" · ") : "—";
}
```

- [ ] **步骤 4：确认测试通过**

在 `web/` 运行：`npm run test -- src/routing.test.ts src/labels.test.ts src/format.test.ts`

预期：全部通过。

- [ ] **步骤 5：检查点**

在 `web/` 运行：`npm run check`。不提交。

---

### 任务 3：加载 Hook、通用组件与 Run 列表

**文件：**
- 新建：`web/src/useAsync.ts`、`web/src/usePaged.ts`
- 新建：`web/src/components/StatusBadge.tsx`、`Details.tsx`、`ErrorBox.tsx`、`Skeleton.tsx`、`Card.tsx`、`ConnectionStatus.tsx`、`RunList.tsx`
- 新建：`web/src/styles.css`
- 修改：`web/src/App.tsx`、`web/src/main.tsx`
- 测试：`web/src/App.test.tsx`（替换现有内容）
- 修改：`AGENTS.md`（目录树加入 `styles.css`）

**接口：**
- 消费：任务 1 的 `api`、`API_BASE`、`ApiError`；任务 2 的 `useRoute`、`labelFor`、`formatTime`。
- 产出：`AsyncState<T>`、`toApiError(error)`、`useAsync<T>(key, load): { state, retry }`。
- 产出：`PAGE_SIZE = 20`、`usePaged<T>(loadPage): { items, total, status, error, hasMore, loadMore, retry }`。
- 产出组件：`StatusBadge({ kind, value })`、`Details({ rows })`（`DetailRow = { label, value }`）、`ErrorBox({ error, notFoundText, onRetry? })`、`Skeleton({ lines })`、`Card({ title, children })`、`ConnectionStatus({ state, onRetry })`、`RunList({ selectedRunId, onSelect })`。

- [ ] **步骤 1：写失败的测试**

`web/src/App.test.tsx`（整体替换）：

```tsx
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "./App";
import { NETWORK_DOWN, installFakeApi } from "./test/fakeApi";
import { RUN, SECOND_RUN, page, viewerRoutes } from "./test/fixtures";

describe("run list", () => {
  it("shows runs and opens one", async () => {
    installFakeApi(viewerRoutes());
    render(<App />);

    const run = await screen.findByRole("button", { name: /What are the main evaluation methods/ });
    expect(run.textContent).toContain("已完成");
    expect(run.textContent).toContain("2026-10-12 21:40");
    expect(run.textContent).toContain("2 篇论文 · 2 条证据 · 3 条结论");
    expect(await screen.findByText("已连接 http://127.0.0.1:8765")).toBeTruthy();

    fireEvent.click(run);

    await waitFor(() => expect(window.location.hash).toBe("#/runs/run-1/overview"));
  });

  it("appends the next page instead of replacing the list", async () => {
    installFakeApi({
      ...viewerRoutes(),
      "/v1/runs?limit=20&offset=0": page([RUN], 20, 0, 2),
      "/v1/runs?limit=20&offset=1": page([SECOND_RUN], 20, 1, 2),
    });
    render(<App />);

    fireEvent.click(await screen.findByRole("button", { name: "加载更多" }));

    expect(await screen.findByRole("button", { name: /How do agentic tool-use methods plan/ })).toBeTruthy();
    expect(screen.getByRole("button", { name: /What are the main evaluation methods/ })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "加载更多" })).toBeNull();
  });

  it("explains how to create the first run", async () => {
    installFakeApi({
      "/v1/runs?limit=1&offset=0": page([], 1),
      "/v1/runs?limit=20&offset=0": page([], 20),
    });
    render(<App />);

    expect(await screen.findByText(/还没有 Run/)).toBeTruthy();
  });

  it("tells the user to start the API when it is unreachable", async () => {
    installFakeApi({}, NETWORK_DOWN);
    render(<App />);

    expect(await screen.findByText(/连不上本地 API（http:\/\/127\.0\.0\.1:8765）/)).toBeTruthy();
    expect((await screen.findAllByText(/请先运行 research-agent serve/)).length).toBeGreaterThan(0);
  });
});
```

- [ ] **步骤 2：确认测试失败**

在 `web/` 运行：`npm run test -- src/App.test.tsx`

预期：失败，脚手架页面里没有 Run 列表。

- [ ] **步骤 3：写加载 Hook**

`web/src/useAsync.ts`：

```ts
import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "./api/client";

export type AsyncState<T> =
  | { status: "loading" }
  | { status: "error"; error: ApiError }
  | { status: "ready"; data: T };

export function toApiError(error: unknown): ApiError {
  return error instanceof ApiError ? error : new ApiError("internal_error", "服务器出错");
}

export function useAsync<T>(
  key: string,
  load: () => Promise<T>,
): { state: AsyncState<T>; retry: () => void } {
  const loadRef = useRef(load);
  loadRef.current = load;
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<AsyncState<T>>({ status: "loading" });

  useEffect(() => {
    let active = true;
    setState({ status: "loading" });
    loadRef.current().then(
      (data) => {
        if (active) {
          setState({ status: "ready", data });
        }
      },
      (error: unknown) => {
        if (active) {
          setState({ status: "error", error: toApiError(error) });
        }
      },
    );
    return () => {
      active = false;
    };
  }, [key, attempt]);

  const retry = useCallback(() => setAttempt((value) => value + 1), []);
  return { state, retry };
}
```

`web/src/usePaged.ts`：

```ts
import { useEffect, useRef, useState } from "react";
import type { ApiError } from "./api/client";
import type { Page } from "./api/types";
import { toApiError } from "./useAsync";

export const PAGE_SIZE = 20;

export interface PagedList<T> {
  items: T[];
  total: number;
  status: "loading" | "ready" | "error";
  error: ApiError | null;
  hasMore: boolean;
  loadMore: () => void;
  retry: () => void;
}

export function usePaged<T>(
  loadPage: (limit: number, offset: number) => Promise<Page<T>>,
): PagedList<T> {
  const loadRef = useRef(loadPage);
  loadRef.current = loadPage;
  const [items, setItems] = useState<T[]>([]);
  const [total, setTotal] = useState(0);
  const [status, setStatus] = useState<PagedList<T>["status"]>("loading");
  const [error, setError] = useState<ApiError | null>(null);
  const [request, setRequest] = useState({ offset: 0, attempt: 0 });

  useEffect(() => {
    let active = true;
    setStatus("loading");
    loadRef.current(PAGE_SIZE, request.offset).then(
      (result) => {
        if (!active) {
          return;
        }
        setItems((current) =>
          request.offset === 0 ? result.items : [...current, ...result.items],
        );
        setTotal(result.total);
        setError(null);
        setStatus("ready");
      },
      (failure: unknown) => {
        if (!active) {
          return;
        }
        setError(toApiError(failure));
        setStatus("error");
      },
    );
    return () => {
      active = false;
    };
  }, [request]);

  return {
    items,
    total,
    status,
    error,
    hasMore: items.length < total,
    loadMore: () =>
      setRequest((current) => ({ offset: items.length, attempt: current.attempt + 1 })),
    retry: () => setRequest((current) => ({ ...current, attempt: current.attempt + 1 })),
  };
}
```

- [ ] **步骤 4：写通用组件**

`web/src/components/StatusBadge.tsx`：

```tsx
import { labelFor, type LabelKind } from "../labels";

export function StatusBadge({ kind, value }: { kind: LabelKind; value: string }) {
  const label = labelFor(kind, value);
  return (
    <span className={`badge tone-${label.tone}`}>
      {label.text}
      {label.text !== label.code ? <span className="badge-code"> {label.code}</span> : null}
    </span>
  );
}
```

`web/src/components/Details.tsx`：

```tsx
export interface DetailRow {
  label: string;
  value: string | number | boolean | null;
}

function show(value: DetailRow["value"]): string {
  if (value === null || value === "") {
    return "—";
  }
  return String(value);
}

export function Details({ rows }: { rows: DetailRow[] }) {
  return (
    <details className="details">
      <summary>详细信息</summary>
      <dl>
        {rows.map((row) => (
          <div key={row.label} className="detail-row">
            <dt>{row.label}</dt>
            <dd className="mono">{show(row.value)}</dd>
          </div>
        ))}
      </dl>
    </details>
  );
}
```

`web/src/components/ErrorBox.tsx`：

```tsx
import type { ApiError } from "../api/client";

function errorText(error: ApiError, notFoundText: string): string {
  switch (error.kind) {
    case "unreachable":
      return "连不上本地 API。请先运行 research-agent serve。";
    case "not_found":
      return notFoundText;
    case "version_mismatch":
      return "API 版本不匹配，前端需要 v1。";
    case "invalid_request":
      return "请求参数不合法。";
    case "internal_error":
      return "服务器出错。";
  }
}

export function ErrorBox({
  error,
  notFoundText,
  onRetry,
}: {
  error: ApiError;
  notFoundText: string;
  onRetry?: () => void;
}) {
  return (
    <div className="error" role="alert">
      <p>{errorText(error, notFoundText)}</p>
      {error.kind === "not_found" ? <a href="#/runs">回到 Run 列表</a> : null}
      {onRetry !== undefined && error.kind !== "version_mismatch" ? (
        <button type="button" onClick={onRetry}>
          重试
        </button>
      ) : null}
    </div>
  );
}
```

`web/src/components/Skeleton.tsx`：

```tsx
export function Skeleton({ lines }: { lines: number }) {
  return (
    <div className="skeleton" role="status" aria-label="加载中">
      {Array.from({ length: lines }, (_, index) => (
        <span key={index} />
      ))}
    </div>
  );
}
```

`web/src/components/Card.tsx`：

```tsx
import type { ReactNode } from "react";

export function Card({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="card">
      <h3 className="card-title">{title}</h3>
      {children}
    </section>
  );
}
```

`web/src/components/ConnectionStatus.tsx`：

```tsx
import { API_BASE } from "../api/client";
import type { AsyncState } from "../useAsync";

export function ConnectionStatus({
  state,
  onRetry,
}: {
  state: AsyncState<unknown>;
  onRetry: () => void;
}) {
  if (state.status === "loading") {
    return <p className="connection">正在连接 {API_BASE}</p>;
  }
  if (state.status === "ready") {
    return <p className="connection tone-ok">{`已连接 ${API_BASE}`}</p>;
  }
  const text =
    state.error.kind === "unreachable"
      ? `连不上本地 API（${API_BASE}）`
      : state.error.kind === "version_mismatch"
        ? "API 版本不匹配，前端需要 v1"
        : "本地 API 出错";
  return (
    <p className="connection tone-bad" role="alert">
      {text}
      <button type="button" onClick={onRetry}>
        重试
      </button>
    </p>
  );
}
```

- [ ] **步骤 5：写 Run 列表**

`web/src/components/RunList.tsx`：

```tsx
import { api } from "../api/client";
import { formatTime } from "../format";
import { usePaged } from "../usePaged";
import { ErrorBox } from "./ErrorBox";
import { Skeleton } from "./Skeleton";
import { StatusBadge } from "./StatusBadge";

export function RunList({
  selectedRunId,
  onSelect,
}: {
  selectedRunId: string | null;
  onSelect: (runId: string) => void;
}) {
  const runs = usePaged((limit, offset) => api.listRuns(limit, offset));

  if (runs.items.length === 0) {
    if (runs.status === "loading") {
      return <Skeleton lines={3} />;
    }
    if (runs.error !== null) {
      return <ErrorBox error={runs.error} notFoundText="找不到 Run 列表。" onRetry={runs.retry} />;
    }
    return (
      <p className="empty">
        还没有 Run。先运行 <code>{'research-agent research "<问题>"'}</code>，再刷新本页。
      </p>
    );
  }

  return (
    <div className="run-list">
      <label className="run-select">
        <span>选择 Run</span>
        <select
          value={selectedRunId ?? ""}
          onChange={(event) => {
            if (event.target.value !== "") {
              onSelect(event.target.value);
            }
          }}
        >
          <option value="">（未选择）</option>
          {runs.items.map((run) => (
            <option key={run.id} value={run.id}>
              {run.question_text}
            </option>
          ))}
        </select>
      </label>
      <ul className="run-items">
        {runs.items.map((run) => (
          <li key={run.id}>
            <button
              type="button"
              className="run-item"
              aria-pressed={run.id === selectedRunId}
              onClick={() => onSelect(run.id)}
            >
              <span className="run-question">{run.question_text}</span>
              <span className="run-meta">
                <StatusBadge kind="runStatus" value={run.status} /> {formatTime(run.started_at)}
              </span>
              <span className="run-meta">
                {`${run.paper_count} 篇论文 · ${run.evidence_count} 条证据 · ${run.claim_count} 条结论`}
              </span>
            </button>
          </li>
        ))}
      </ul>
      {runs.error !== null ? (
        <ErrorBox error={runs.error} notFoundText="找不到更多 Run。" onRetry={runs.retry} />
      ) : null}
      {runs.hasMore ? (
        <button
          type="button"
          className="load-more"
          disabled={runs.status === "loading"}
          onClick={runs.loadMore}
        >
          加载更多
        </button>
      ) : null}
    </div>
  );
}
```

- [ ] **步骤 6：写页面骨架与样式**

`web/src/App.tsx`（整体替换；任务 4、5 会继续修改）：

```tsx
import { api } from "./api/client";
import { ConnectionStatus } from "./components/ConnectionStatus";
import { RunList } from "./components/RunList";
import { useRoute } from "./routing";
import { useAsync } from "./useAsync";

export function App() {
  const [route, navigate] = useRoute();
  const connection = useAsync("connection", () => api.listRuns(1, 0));

  return (
    <div className="app" data-chain-open="false">
      <header className="topbar">
        <h1>证据链查看器</h1>
        <ConnectionStatus state={connection.state} onRetry={connection.retry} />
      </header>
      <nav className="runs-pane" aria-label="Run 列表">
        <RunList
          selectedRunId={route.runId}
          onSelect={(runId) => navigate({ runId, tab: "overview", claimId: null })}
        />
      </nav>
      <main className="content-pane">
        <p className="empty">从左侧选择一个 Run。</p>
      </main>
    </div>
  );
}
```

`web/src/main.tsx` 在 `import { App } from "./App";` 之后加一行：

```ts
import "./styles.css";
```

`web/src/styles.css`：

```css
:root {
  --surface: #ffffff;
  --surface-muted: #fafaf9;
  --border: #e7e5e4;
  --text: #1f2937;
  --text-muted: #78716c;
  --accent: #1e3a8a;
  --accent-soft: #eff6ff;
  --ok: #166534;
  --ok-soft: #dcfce7;
  --bad: #991b1b;
  --bad-soft: #fee2e2;
  --warn: #92400e;
  --warn-soft: #fef3c7;
  --neutral-soft: #f5f5f4;
  --font-body: "Segoe UI", "Microsoft YaHei", system-ui, sans-serif;
  --font-quote: Georgia, "Songti SC", SimSun, serif;
  --font-mono: Consolas, "Cascadia Mono", monospace;
  --radius: 8px;
  color: var(--text);
  background: var(--surface-muted);
  font: 14px/1.55 var(--font-body);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
}

h1,
h2 {
  font-size: 18px;
  margin: 0;
}

h3 {
  font-size: 14px;
  margin: 16px 0 8px;
}

button,
select {
  font: inherit;
  color: inherit;
}

button {
  cursor: pointer;
}

:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

code,
.mono {
  font-family: var(--font-mono);
  font-size: 12px;
  overflow-wrap: anywhere;
}

.app {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr) 380px;
  grid-template-rows: auto minmax(0, 1fr);
  height: 100dvh;
}

.topbar {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
}

.connection {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
}

.connection.tone-ok {
  color: var(--ok);
}

.connection.tone-bad {
  color: var(--bad);
}

.runs-pane,
.content-pane,
.chain-pane {
  overflow-y: auto;
  padding: 16px;
}

.runs-pane {
  border-right: 1px solid var(--border);
}

.content-pane {
  background: var(--surface);
}

.chain-pane {
  border-left: 1px solid var(--border);
  background: var(--surface-muted);
}

.chain-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.chain-head h2 {
  font-size: 14px;
}

.run-select {
  display: none;
  flex-direction: column;
  gap: 4px;
}

.run-items,
.claims,
.steps,
.sources {
  list-style: none;
  margin: 0;
  padding: 0;
}

.run-item,
.claim-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  width: 100%;
  margin-bottom: 8px;
  padding: 10px 12px;
  text-align: left;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
}

.run-item[aria-pressed="true"] {
  border-color: var(--accent);
  box-shadow: inset 3px 0 0 var(--accent);
}

.claim-item[aria-pressed="true"] {
  border-color: var(--accent);
  background: var(--accent-soft);
}

.run-question {
  font-weight: 600;
  overflow-wrap: anywhere;
}

.run-meta,
.claim-meta,
.meta {
  font-size: 12px;
  color: var(--text-muted);
}

.load-more {
  width: 100%;
  padding: 8px;
  border: 1px dashed var(--border);
  border-radius: var(--radius);
  background: transparent;
}

.badge {
  display: inline-block;
  padding: 1px 8px;
  border-radius: 999px;
  font-size: 12px;
  background: var(--neutral-soft);
}

.badge-code {
  font-family: var(--font-mono);
  font-size: 11px;
}

.badge.tone-ok {
  background: var(--ok-soft);
  color: var(--ok);
}

.badge.tone-bad {
  background: var(--bad-soft);
  color: var(--bad);
}

.badge.tone-warn {
  background: var(--warn-soft);
  color: var(--warn);
}

.tabs {
  display: flex;
  gap: 4px;
  margin: 12px 0;
  border-bottom: 1px solid var(--border);
}

.tabs [role="tab"] {
  padding: 6px 14px;
  border: 0;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: var(--text-muted);
}

.tabs [role="tab"][aria-selected="true"] {
  color: var(--accent);
  border-bottom-color: var(--accent);
  font-weight: 600;
}

.steps {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 8px;
}

.step {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.step-name {
  font-weight: 600;
}

.step-error,
.error-code {
  font-size: 12px;
  color: var(--bad);
  overflow-wrap: anywhere;
}

.sources li {
  margin-bottom: 10px;
}

.source-head {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 13px;
}

.bar {
  height: 8px;
  margin-top: 4px;
  border-radius: 4px;
  background: var(--neutral-soft);
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  background: var(--accent);
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.filters button {
  padding: 4px 12px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
}

.filters button[aria-pressed="true"] {
  border-color: var(--accent);
  background: var(--accent);
  color: #ffffff;
}

.papers {
  width: 100%;
  border-collapse: collapse;
}

.papers th,
.papers td {
  padding: 8px;
  text-align: left;
  vertical-align: top;
  border-bottom: 1px solid var(--border);
  overflow-wrap: anywhere;
}

.papers th {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}

.papers tr.is-denied td {
  color: var(--text-muted);
  background: var(--surface-muted);
}

.reason {
  display: block;
  margin-top: 2px;
  font-size: 12px;
}

.card {
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
}

.card-title {
  margin: 0 0 6px;
  font-size: 12px;
  color: var(--accent);
  letter-spacing: 0.02em;
}

.relation {
  margin: 4px 0;
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
}

.quote {
  margin: 4px 0 8px;
  padding-left: 10px;
  border-left: 3px solid var(--accent);
  font-family: var(--font-quote);
  font-size: 15px;
  overflow-wrap: anywhere;
}

.paper-title,
.claim-text {
  margin: 4px 0;
  overflow-wrap: anywhere;
}

.evidence-group {
  margin-top: 12px;
}

.evidence-group > summary {
  margin-bottom: 4px;
  font-weight: 600;
  cursor: pointer;
}

.details {
  margin-top: 6px;
  font-size: 12px;
}

.details summary {
  color: var(--accent);
  cursor: pointer;
}

.details dl {
  display: grid;
  grid-template-columns: max-content minmax(0, 1fr);
  gap: 2px 8px;
  margin: 6px 0 0;
}

.detail-row {
  display: contents;
}

.details dt {
  color: var(--text-muted);
}

.details dd {
  margin: 0;
}

.warning {
  margin: 4px 0;
  padding: 4px 8px;
  border-radius: 4px;
  background: var(--warn-soft);
  color: var(--warn);
  font-size: 12px;
}

.error {
  padding: 8px 12px;
  border-radius: var(--radius);
  background: var(--bad-soft);
  color: var(--bad);
}

.error p {
  margin: 0 0 6px;
}

.error a {
  margin-right: 8px;
  color: var(--bad);
}

.error button,
.connection button,
.close {
  padding: 2px 10px;
  border: 1px solid currentColor;
  border-radius: 4px;
  background: transparent;
}

.empty {
  color: var(--text-muted);
}

.skeleton {
  display: grid;
  gap: 8px;
}

.skeleton span {
  display: block;
  height: 16px;
  border-radius: 4px;
  background: var(--neutral-soft);
}

@media (max-width: 1199px) {
  .app {
    grid-template-columns: 240px minmax(0, 1fr);
  }

  .chain-pane {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    z-index: 10;
    width: min(420px, 100%);
    visibility: hidden;
    transform: translateX(100%);
    transition:
      transform 200ms ease-out,
      visibility 200ms;
  }

  .app[data-chain-open="true"] .chain-pane {
    visibility: visible;
    transform: none;
  }
}

@media (max-width: 899px) {
  .app {
    grid-template-columns: minmax(0, 1fr);
    grid-template-rows: auto auto minmax(0, 1fr);
  }

  .runs-pane {
    border-right: 0;
    border-bottom: 1px solid var(--border);
  }

  .run-select {
    display: flex;
  }

  .run-items,
  .runs-pane .load-more {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .chain-pane {
    transition: none;
  }
}
```

`AGENTS.md` §4 `web/src/` 下 `App.tsx` 一行之后加：

```text
│       ├── styles.css           # 颜色、字体与布局
```

- [ ] **步骤 7：确认测试通过**

在 `web/` 运行：`npm run test -- src/App.test.tsx`

预期：4 个测试通过。

- [ ] **步骤 8：检查点**

在 `web/` 运行：`npm run check`；在项目根运行 `uv run python scripts/check_docs.py`。不提交。

---

### 任务 4：Run 视图、概览与候选论文

**文件：**
- 新建：`web/src/components/RunView.tsx`、`RunOverview.tsx`、`PaperTable.tsx`
- 修改：`web/src/App.tsx`（`<main>` 内容）
- 测试：`web/src/App.test.tsx`（追加）

**接口：**
- 消费：`api.getRun`、`api.listSteps`、`api.listSources`、`listAllPapers`、`useAsync`、`StatusBadge`、`ErrorBox`、`Skeleton`、`RunRoute`、`Route`、`Tab`、`TABS`、`formatTime`。
- 产出：`RunView({ route: RunRoute, navigate: (next: Route) => void })`、`RunOverview({ runId })`、`PaperTable({ runId })`。任务 5 会在 `RunView` 的结论标签页里放入 `ClaimList`。

- [ ] **步骤 1：写失败的测试**

在 `web/src/App.test.tsx` 末尾追加：

```tsx
describe("run view", () => {
  it("shows plan steps and source counts", async () => {
    installFakeApi(viewerRoutes());
    window.location.hash = "#/runs/run-1/overview";
    render(<App />);

    expect(await screen.findByRole("heading", { name: RUN.question_text })).toBeTruthy();
    expect(await screen.findByText("路由")).toBeTruthy();
    expect(screen.getByText("upstream_unavailable · 尝试 3 次")).toBeTruthy();
    expect(await screen.findByText("4 次调用 · 成功 4 · 失败 0 · 2 篇论文")).toBeTruthy();
    expect(screen.getByRole("tab", { name: "概览" }).getAttribute("aria-selected")).toBe("true");
  });

  it("shows why a paper was filtered and filters by decision", async () => {
    installFakeApi(viewerRoutes());
    window.location.hash = "#/runs/run-1/papers";
    render(<App />);

    expect(await screen.findByText("Chip Floorplanning with Reinforcement Learning")).toBeTruthy();
    expect(screen.getByText("out of scope")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: /^被过滤/ }));

    expect(screen.queryByText("RAGAs: Automated Evaluation of Retrieval Augmented Generation")).toBeNull();
    expect(screen.getByText("Chip Floorplanning with Reinforcement Learning")).toBeTruthy();
  });

  it("says when the run in the address does not exist", async () => {
    installFakeApi(viewerRoutes());
    window.location.hash = "#/runs/missing/overview";
    render(<App />);

    expect(await screen.findByText("找不到这个 Run。")).toBeTruthy();
    expect(screen.getByRole("link", { name: "回到 Run 列表" })).toBeTruthy();
  });
});
```

- [ ] **步骤 2：确认测试失败**

在 `web/` 运行：`npm run test -- src/App.test.tsx`

预期：新增的 3 个测试失败，`<main>` 里只有提示文字。

- [ ] **步骤 3：写概览**

`web/src/components/RunOverview.tsx`：

```tsx
import { api } from "../api/client";
import type { SourceSummary } from "../api/types";
import { labelFor } from "../labels";
import { useAsync } from "../useAsync";
import { ErrorBox } from "./ErrorBox";
import { Skeleton } from "./Skeleton";
import { StatusBadge } from "./StatusBadge";

export function RunOverview({ runId }: { runId: string }) {
  const steps = useAsync(`steps:${runId}`, () => api.listSteps(runId));
  const sources = useAsync(`sources:${runId}`, () => api.listSources(runId));

  return (
    <div className="overview">
      <section aria-labelledby="steps-title">
        <h3 id="steps-title">计划步骤</h3>
        {steps.state.status === "loading" ? <Skeleton lines={2} /> : null}
        {steps.state.status === "error" ? (
          <ErrorBox error={steps.state.error} notFoundText="找不到这个 Run。" onRetry={steps.retry} />
        ) : null}
        {steps.state.status === "ready" && steps.state.data.items.length === 0 ? (
          <p className="empty">没有记录。</p>
        ) : null}
        {steps.state.status === "ready" && steps.state.data.items.length > 0 ? (
          <ol className="steps">
            {steps.state.data.items.map((step) => (
              <li key={step.id} className="step">
                <span className="step-name">{labelFor("stepKey", step.step_key).text}</span>
                <span className="mono">{step.step_key}</span>
                <StatusBadge kind="stepStatus" value={step.status} />
                {step.error_code !== null ? (
                  <span className="step-error">{`${step.error_code} · 尝试 ${step.attempt_count} 次`}</span>
                ) : null}
              </li>
            ))}
          </ol>
        ) : null}
      </section>
      <section aria-labelledby="sources-title">
        <h3 id="sources-title">来源分布</h3>
        {sources.state.status === "loading" ? <Skeleton lines={2} /> : null}
        {sources.state.status === "error" ? (
          <ErrorBox error={sources.state.error} notFoundText="找不到这个 Run。" onRetry={sources.retry} />
        ) : null}
        {sources.state.status === "ready" && sources.state.data.items.length === 0 ? (
          <p className="empty">没有记录。</p>
        ) : null}
        {sources.state.status === "ready" && sources.state.data.items.length > 0 ? (
          <SourceBars items={sources.state.data.items} />
        ) : null}
      </section>
    </div>
  );
}

function SourceBars({ items }: { items: SourceSummary[] }) {
  const largest = Math.max(1, ...items.map((item) => item.call_count));
  return (
    <ul className="sources">
      {items.map((item) => (
        <li key={item.source}>
          <div className="source-head">
            <span className="mono">{item.source}</span>
            <span>{`${item.call_count} 次调用 · 成功 ${item.success_count} · 失败 ${item.failed_count} · ${item.paper_count} 篇论文`}</span>
          </div>
          <div className="bar" aria-hidden="true">
            <div className="bar-fill" style={{ width: `${(item.call_count / largest) * 100}%` }} />
          </div>
        </li>
      ))}
    </ul>
  );
}
```

- [ ] **步骤 4：写候选论文**

`web/src/components/PaperTable.tsx`：

```tsx
import { useState } from "react";
import { listAllPapers } from "../api/client";
import type { Paper, RelevanceDecision } from "../api/types";
import { useAsync } from "../useAsync";
import { ErrorBox } from "./ErrorBox";
import { Skeleton } from "./Skeleton";
import { StatusBadge } from "./StatusBadge";

type Filter = "all" | RelevanceDecision;

const FILTERS: { value: Filter; label: string }[] = [
  { value: "all", label: "全部" },
  { value: "allowed", label: "保留" },
  { value: "denied", label: "被过滤" },
  { value: "not_judged", label: "未判定" },
];

function identifier(paper: Paper): string {
  if (paper.doi !== null) {
    return `doi:${paper.doi}`;
  }
  if (paper.arxiv_id !== null) {
    return `arXiv:${paper.arxiv_id}`;
  }
  return "—";
}

export function PaperTable({ runId }: { runId: string }) {
  const papers = useAsync(`papers:${runId}`, () => listAllPapers(runId));
  const [filter, setFilter] = useState<Filter>("all");

  if (papers.state.status === "loading") {
    return <Skeleton lines={4} />;
  }
  if (papers.state.status === "error") {
    return <ErrorBox error={papers.state.error} notFoundText="找不到这个 Run。" onRetry={papers.retry} />;
  }
  const all = papers.state.data;
  if (all.length === 0) {
    return <p className="empty">没有候选论文。</p>;
  }
  const count = (value: Filter) =>
    value === "all" ? all.length : all.filter((paper) => paper.relevance.decision === value).length;
  const shown = filter === "all" ? all : all.filter((paper) => paper.relevance.decision === filter);

  return (
    <div>
      <div className="filters" role="group" aria-label="按相关性筛选">
        {FILTERS.map((item) => (
          <button
            key={item.value}
            type="button"
            aria-pressed={filter === item.value}
            onClick={() => setFilter(item.value)}
          >
            {`${item.label} ${count(item.value)}`}
          </button>
        ))}
      </div>
      <table className="papers">
        <thead>
          <tr>
            <th scope="col">标题</th>
            <th scope="col">年份</th>
            <th scope="col">标识</th>
            <th scope="col">开放获取</th>
            <th scope="col">相关性</th>
          </tr>
        </thead>
        <tbody>
          {shown.map((paper) => (
            <tr key={paper.id} className={paper.relevance.decision === "denied" ? "is-denied" : undefined}>
              <td>{paper.title}</td>
              <td>{paper.year ?? "—"}</td>
              <td className="mono">{identifier(paper)}</td>
              <td>{paper.open_access_status ?? "—"}</td>
              <td>
                <StatusBadge kind="relevance" value={paper.relevance.decision} />
                {paper.relevance.reason !== null ? (
                  <span className="reason">{paper.relevance.reason}</span>
                ) : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {shown.length === 0 ? <p className="empty">没有符合筛选条件的论文。</p> : null}
    </div>
  );
}
```

- [ ] **步骤 5：写 Run 视图并接入页面**

`web/src/components/RunView.tsx`：

```tsx
import type { KeyboardEvent } from "react";
import { api } from "../api/client";
import { formatTime } from "../format";
import { TABS, type Route, type RunRoute, type Tab } from "../routing";
import { useAsync } from "../useAsync";
import { ErrorBox } from "./ErrorBox";
import { PaperTable } from "./PaperTable";
import { RunOverview } from "./RunOverview";
import { Skeleton } from "./Skeleton";
import { StatusBadge } from "./StatusBadge";

export function RunView({ route, navigate }: { route: RunRoute; navigate: (next: Route) => void }) {
  const run = useAsync(`run:${route.runId}`, () => api.getRun(route.runId));

  if (run.state.status === "loading") {
    return <Skeleton lines={4} />;
  }
  if (run.state.status === "error") {
    return <ErrorBox error={run.state.error} notFoundText="找不到这个 Run。" onRetry={run.retry} />;
  }
  const detail = run.state.data;
  const labels: Record<Tab, string> = {
    overview: "概览",
    papers: `候选论文 ${detail.paper_count}`,
    claims: `结论 ${detail.claim_count}`,
  };

  const openTab = (tab: Tab) => navigate({ runId: route.runId, tab, claimId: null });

  const onTabKey = (event: KeyboardEvent<HTMLButtonElement>, index: number) => {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") {
      return;
    }
    event.preventDefault();
    const step = event.key === "ArrowRight" ? 1 : -1;
    const next = TABS[(index + step + TABS.length) % TABS.length];
    openTab(next);
    document.getElementById(`tab-${next}`)?.focus();
  };

  return (
    <section className="run-view" aria-labelledby="run-title">
      <h2 id="run-title">{detail.question_text}</h2>
      <p className="run-meta">
        <StatusBadge kind="runStatus" value={detail.status} />{" "}
        {`开始 ${formatTime(detail.started_at)} · 结束 ${formatTime(detail.finished_at)}`}
      </p>
      {detail.error_code !== null ? (
        <p className="error-code">
          失败原因：<code>{detail.error_code}</code>
        </p>
      ) : null}
      <div className="tabs" role="tablist" aria-label="Run 内容">
        {TABS.map((tab, index) => (
          <button
            key={tab}
            id={`tab-${tab}`}
            type="button"
            role="tab"
            aria-selected={route.tab === tab}
            aria-controls={`panel-${tab}`}
            tabIndex={route.tab === tab ? 0 : -1}
            onClick={() => openTab(tab)}
            onKeyDown={(event) => onTabKey(event, index)}
          >
            {labels[tab]}
          </button>
        ))}
      </div>
      <div role="tabpanel" id={`panel-${route.tab}`} aria-labelledby={`tab-${route.tab}`}>
        {route.tab === "overview" ? <RunOverview runId={route.runId} /> : null}
        {route.tab === "papers" ? <PaperTable runId={route.runId} /> : null}
      </div>
    </section>
  );
}
```

`web/src/App.tsx`：在文件顶部加 `import { RunView } from "./components/RunView";`，并把 `<main>` 改为：

```tsx
      <main className="content-pane">
        {route.runId === null ? (
          <p className="empty">从左侧选择一个 Run。</p>
        ) : (
          <RunView key={route.runId} route={route} navigate={navigate} />
        )}
      </main>
```

- [ ] **步骤 6：确认测试通过**

在 `web/` 运行：`npm run test -- src/App.test.tsx`

预期：7 个测试通过。

- [ ] **步骤 7：检查点**

在 `web/` 运行：`npm run check`。不提交。

---

### 任务 5：结论列表与证据链

**文件：**
- 新建：`web/src/components/ClaimList.tsx`、`EvidenceChain.tsx`
- 修改：`web/src/components/RunView.tsx`（结论标签页）
- 修改：`web/src/App.tsx`（右栏、`Esc`、焦点）
- 测试：`web/src/App.test.tsx`（追加）

**接口：**
- 消费：`api.listClaims`、`api.getClaim`、`createResourceCache`、`ResourceCache`、`loadEvidence`、`EvidenceBundle`、`usePaged`、`useAsync`、`Card`、`Details`、`ErrorBox`、`Skeleton`、`StatusBadge`、`formatBytes`、`formatConfidence`、`formatLocator`、`formatTime`。
- 产出：`ClaimList({ runId, selectedClaimId, onSelect })`，每条结论按钮的 `id` 为 `claim-<结论 ID>`；`EvidenceChain({ claimId, cache })`。

- [ ] **步骤 1：写失败的测试**

在 `web/src/App.test.tsx` 顶部的 import 中加入 `within`，从 `./test/fakeApi` 加入 `failure` 和 `type FakeRoutes`，从 `./test/fixtures` 加入 `ABSTRACT_SPAN`、`CLAIMS`、`FILE`。末尾追加：

```tsx
describe("evidence chain", () => {
  it("follows a claim to its evidence, paper, and source record", async () => {
    const calls = installFakeApi(viewerRoutes());
    window.location.hash = "#/runs/run-1/claims/claim-1";
    render(<App />);

    const chain = screen.getByRole("complementary", { name: "证据链" });
    expect(await within(chain).findByText(ABSTRACT_SPAN.quote)).toBeTruthy();
    expect(within(chain).getByText("RAGAs: Automated Evaluation of Retrieval Augmented Generation")).toBeTruthy();
    expect(within(chain).getByText(/openalex · 抓取于 2026-10-12 21:38/)).toBeTruthy();
    expect(within(chain).queryByText("文件 File")).toBeNull();
    expect(calls.every((call) => call.method === "GET")).toBe(true);
  });

  it("adds the file and parsed text for full-text evidence", async () => {
    installFakeApi(viewerRoutes());
    window.location.hash = "#/runs/run-1/claims/claim-2";
    render(<App />);

    const chain = screen.getByRole("complementary", { name: "证据链" });
    expect(await within(chain).findByText("解析文本 Document")).toBeTruthy();
    expect(within(chain).getByText("data/archive/papers/a.pdf")).toBeTruthy();
    expect(within(chain).getByText("data/archive/parsed/document-1.txt")).toBeTruthy();
    expect(within(chain).getByText("第 3 页 · 段落 2 · 字符 120–198", { exact: false })).toBeTruthy();
  });

  it("marks a quarantined file that was never saved", async () => {
    installFakeApi({
      ...viewerRoutes(),
      "/v1/files/file-1": { ...FILE, status: "quarantined", path: "" },
    });
    window.location.hash = "#/runs/run-1/claims/claim-2";
    render(<App />);

    expect(await screen.findByText("已隔离，不能作为证据。")).toBeTruthy();
    expect(screen.getByText("未保存到磁盘")).toBeTruthy();
  });

  it("labels a claim without evidence", async () => {
    installFakeApi(viewerRoutes());
    window.location.hash = "#/runs/run-1/claims";
    render(<App />);

    expect(await screen.findByText("未关联证据，只能视为待验证")).toBeTruthy();
  });

  it("keeps the other evidence when one request fails, and retries", async () => {
    const routes: FakeRoutes = {
      ...viewerRoutes(),
      "/v1/claims/claim-1": { ...CLAIMS[0], evidence_span_ids: ["span-1", "span-bad"] },
      "/v1/evidence-spans/span-bad": failure(500, "internal_error", "internal error"),
    };
    installFakeApi(routes);
    window.location.hash = "#/runs/run-1/claims/claim-1";
    render(<App />);

    expect(await screen.findByText("服务器出错。")).toBeTruthy();
    expect(screen.getByText(ABSTRACT_SPAN.quote)).toBeTruthy();

    routes["/v1/evidence-spans/span-bad"] = {
      ...ABSTRACT_SPAN,
      id: "span-bad",
      quote: "Recovered quote.",
    };
    fireEvent.click(screen.getByRole("button", { name: "重试" }));

    expect(await screen.findByText("Recovered quote.")).toBeTruthy();
  });

  it("says when the claim in the address does not exist", async () => {
    installFakeApi(viewerRoutes());
    window.location.hash = "#/runs/run-1/claims/missing";
    render(<App />);

    expect(await screen.findByText("找不到这条结论。")).toBeTruthy();
  });

  it("closes the chain with Escape", async () => {
    installFakeApi(viewerRoutes());
    window.location.hash = "#/runs/run-1/claims/claim-1";
    render(<App />);
    await screen.findByText(ABSTRACT_SPAN.quote);

    fireEvent.keyDown(document, { key: "Escape" });

    await waitFor(() => expect(window.location.hash).toBe("#/runs/run-1/claims"));
  });
});
```

- [ ] **步骤 2：确认测试失败**

在 `web/` 运行：`npm run test -- src/App.test.tsx`

预期：新增的 7 个测试失败，页面没有右栏，结论标签页为空。

- [ ] **步骤 3：写结论列表**

`web/src/components/ClaimList.tsx`：

```tsx
import { api } from "../api/client";
import { formatConfidence } from "../format";
import { usePaged } from "../usePaged";
import { ErrorBox } from "./ErrorBox";
import { Skeleton } from "./Skeleton";
import { StatusBadge } from "./StatusBadge";

export function ClaimList({
  runId,
  selectedClaimId,
  onSelect,
}: {
  runId: string;
  selectedClaimId: string | null;
  onSelect: (claimId: string) => void;
}) {
  const claims = usePaged((limit, offset) => api.listClaims(runId, limit, offset));

  if (claims.items.length === 0) {
    if (claims.status === "loading") {
      return <Skeleton lines={3} />;
    }
    if (claims.error !== null) {
      return <ErrorBox error={claims.error} notFoundText="找不到这个 Run。" onRetry={claims.retry} />;
    }
    return <p className="empty">这个 Run 没有生成结论。</p>;
  }

  return (
    <div>
      <ul className="claims">
        {claims.items.map((claim) => (
          <li key={claim.id}>
            <button
              type="button"
              id={`claim-${claim.id}`}
              className="claim-item"
              aria-pressed={claim.id === selectedClaimId}
              onClick={() => onSelect(claim.id)}
            >
              <StatusBadge kind="supportStatus" value={claim.support_status} />
              <span className="claim-text">{claim.claim_text}</span>
              <span className="claim-meta">
                {claim.evidence_span_ids.length > 0
                  ? `${claim.evidence_span_ids.length} 条证据 · 置信度 ${formatConfidence(claim.confidence)}`
                  : "未关联证据，只能视为待验证"}
              </span>
            </button>
          </li>
        ))}
      </ul>
      {claims.error !== null ? (
        <ErrorBox error={claims.error} notFoundText="找不到更多结论。" onRetry={claims.retry} />
      ) : null}
      {claims.hasMore ? (
        <button
          type="button"
          className="load-more"
          disabled={claims.status === "loading"}
          onClick={claims.loadMore}
        >
          加载更多
        </button>
      ) : null}
    </div>
  );
}
```

`web/src/components/RunView.tsx`：加 `import { ClaimList } from "./ClaimList";`，并在 `tabpanel` 中 `PaperTable` 一行之后加：

```tsx
        {route.tab === "claims" ? (
          <ClaimList
            runId={route.runId}
            selectedClaimId={route.claimId}
            onSelect={(claimId) => navigate({ runId: route.runId, tab: "claims", claimId })}
          />
        ) : null}
```

- [ ] **步骤 4：写证据链**

`web/src/components/EvidenceChain.tsx`：

```tsx
import type { ResourceCache } from "../api/cache";
import { api } from "../api/client";
import { loadEvidence, type EvidenceBundle } from "../api/evidence";
import { formatBytes, formatConfidence, formatLocator, formatTime } from "../format";
import { useAsync } from "../useAsync";
import { Card } from "./Card";
import { Details } from "./Details";
import { ErrorBox } from "./ErrorBox";
import { Skeleton } from "./Skeleton";
import { StatusBadge } from "./StatusBadge";

export function EvidenceChain({ claimId, cache }: { claimId: string; cache: ResourceCache }) {
  const claim = useAsync(`claim:${claimId}`, () =>
    cache.get(`claim:${claimId}`, () => api.getClaim(claimId)),
  );

  if (claim.state.status === "loading") {
    return <Skeleton lines={4} />;
  }
  if (claim.state.status === "error") {
    return <ErrorBox error={claim.state.error} notFoundText="找不到这条结论。" onRetry={claim.retry} />;
  }
  const data = claim.state.data;
  const ids = data.evidence_span_ids;

  return (
    <div className="chain">
      <Card title="结论 Claim">
        <StatusBadge kind="supportStatus" value={data.support_status} />
        <p className="claim-text">{data.claim_text}</p>
        <Details
          rows={[
            { label: "claim_id", value: data.id },
            { label: "report_id", value: data.report_id },
            { label: "claim_type", value: data.claim_type },
            { label: "confidence", value: formatConfidence(data.confidence) },
          ]}
        />
      </Card>
      {ids.length === 0 ? (
        <p className="empty">未关联证据，只能视为待验证。</p>
      ) : (
        ids.map((id, index) => (
          <EvidenceGroup
            key={id}
            evidenceSpanId={id}
            index={index}
            total={ids.length}
            cache={cache}
          />
        ))
      )}
    </div>
  );
}

function EvidenceGroup({
  evidenceSpanId,
  index,
  total,
  cache,
}: {
  evidenceSpanId: string;
  index: number;
  total: number;
  cache: ResourceCache;
}) {
  const bundle = useAsync(`evidence:${evidenceSpanId}`, () => loadEvidence(cache, evidenceSpanId));
  return (
    <details className="evidence-group" open>
      <summary>{`证据 ${index + 1} / ${total}`}</summary>
      {bundle.state.status === "loading" ? <Skeleton lines={3} /> : null}
      {bundle.state.status === "error" ? (
        <ErrorBox error={bundle.state.error} notFoundText="找不到这条证据。" onRetry={bundle.retry} />
      ) : null}
      {bundle.state.status === "ready" ? <EvidenceCards bundle={bundle.state.data} /> : null}
    </details>
  );
}

function EvidenceCards({ bundle }: { bundle: EvidenceBundle }) {
  const { span, paper, record, file, document } = bundle;
  const paperMeta = [
    paper.year === null ? null : String(paper.year),
    paper.venue,
    paper.doi === null ? null : `doi:${paper.doi}`,
    paper.arxiv_id === null ? null : `arXiv:${paper.arxiv_id}`,
  ].filter((part): part is string => part !== null && part !== "");

  return (
    <>
      <p className="relation">↓ 由证据支持</p>
      <Card title="证据片段 Evidence Span">
        <blockquote className="quote">{span.quote}</blockquote>
        <p className="meta">
          <StatusBadge kind="evidenceLevel" value={span.evidence_level} />{" "}
          {`位置 ${formatLocator(span.locator)} · `}
          <StatusBadge kind="extractionMethod" value={span.extraction_method} />{" "}
          {`置信度 ${formatConfidence(span.confidence)} · ${span.verified ? "已重新定位" : "未重新定位"}`}
        </p>
        <Details
          rows={[
            { label: "evidence_span_id", value: span.id },
            { label: "locator", value: JSON.stringify(span.locator) },
            { label: "paper_id", value: span.paper_id },
            { label: "source_record_id", value: span.source_record_id },
            { label: "file_id", value: span.file_id },
            { label: "document_id", value: span.document_id },
          ]}
        />
      </Card>
      <p className="relation">↓ 出自</p>
      <Card title="论文 Paper">
        {paper.relevance.decision === "denied" ? (
          <p className="warning" role="note">
            该论文已被相关性过滤。
            {paper.relevance.reason !== null ? ` ${paper.relevance.reason}` : ""}
          </p>
        ) : null}
        <p className="paper-title">{paper.title}</p>
        <p className="meta mono">{paperMeta.length > 0 ? paperMeta.join(" · ") : "—"}</p>
        <Details
          rows={[
            { label: "paper_id", value: paper.id },
            { label: "canonical_key", value: paper.canonical_key },
            { label: "open_access_status", value: paper.open_access_status },
          ]}
        />
      </Card>
      <p className="relation">↓ 来自源站</p>
      <Card title="源站记录 Source Record">
        <p>{`${record.source} · 抓取于 ${formatTime(record.retrieved_at)}`}</p>
        <Details
          rows={[
            { label: "id", value: record.id },
            { label: "source_record_id", value: record.source_record_id },
            { label: "api_endpoint", value: record.api_endpoint },
          ]}
        />
      </Card>
      {span.evidence_level === "full_text" && (file === null || document === null) ? (
        <p className="warning" role="note">
          全文证据缺少文件或解析文本记录。
        </p>
      ) : null}
      {file !== null ? (
        <>
          <p className="relation">↓ 全文文件</p>
          <Card title="文件 File">
            <p>
              <StatusBadge kind="fileStatus" value={file.status} />{" "}
              {`${file.kind.toUpperCase()} · ${formatBytes(file.size_bytes)}`}
            </p>
            {file.status === "quarantined" ? (
              <p className="warning" role="note">
                已隔离，不能作为证据。
              </p>
            ) : null}
            <p className="mono">{file.path === "" ? "未保存到磁盘" : file.path}</p>
            <Details
              rows={[
                { label: "file_id", value: file.id },
                { label: "sha256", value: file.sha256 },
                { label: "content_type", value: file.content_type },
                { label: "source_url", value: file.source_url },
                { label: "retrieved_at", value: formatTime(file.retrieved_at) },
              ]}
            />
          </Card>
        </>
      ) : null}
      {document !== null ? (
        <>
          <p className="relation">↓ 解析为</p>
          <Card title="解析文本 Document">
            <p>{`${document.parser} · ${document.parse_status}`}</p>
            <p className="mono">{document.text_path === "" ? "未保存到磁盘" : document.text_path}</p>
            <Details
              rows={[
                { label: "document_id", value: document.id },
                { label: "parser_version", value: document.parser_version },
                { label: "locator_scheme", value: document.locator_scheme },
              ]}
            />
          </Card>
        </>
      ) : null}
    </>
  );
}
```

- [ ] **步骤 5：接入右栏、`Esc` 与焦点**

`web/src/App.tsx` 整体替换为：

```tsx
import { useCallback, useEffect, useRef, useState } from "react";
import { createResourceCache } from "./api/cache";
import { api } from "./api/client";
import { ConnectionStatus } from "./components/ConnectionStatus";
import { EvidenceChain } from "./components/EvidenceChain";
import { RunList } from "./components/RunList";
import { RunView } from "./components/RunView";
import { useRoute } from "./routing";
import { useAsync } from "./useAsync";

export function App() {
  const [route, navigate] = useRoute();
  const [cache] = useState(createResourceCache);
  const connection = useAsync("connection", () => api.listRuns(1, 0));
  const chainHeading = useRef<HTMLHeadingElement>(null);
  const claimId = route.runId === null ? null : route.claimId;

  const closeChain = useCallback(() => {
    if (route.runId === null || route.claimId === null) {
      return;
    }
    const closed = route.claimId;
    navigate({ runId: route.runId, tab: "claims", claimId: null });
    window.setTimeout(() => document.getElementById(`claim-${closed}`)?.focus(), 0);
  }, [route, navigate]);

  useEffect(() => {
    if (claimId === null) {
      return;
    }
    chainHeading.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        closeChain();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [claimId, closeChain]);

  return (
    <div className="app" data-chain-open={claimId !== null ? "true" : "false"}>
      <header className="topbar">
        <h1>证据链查看器</h1>
        <ConnectionStatus state={connection.state} onRetry={connection.retry} />
      </header>
      <nav className="runs-pane" aria-label="Run 列表">
        <RunList
          selectedRunId={route.runId}
          onSelect={(runId) => navigate({ runId, tab: "overview", claimId: null })}
        />
      </nav>
      <main className="content-pane">
        {route.runId === null ? (
          <p className="empty">从左侧选择一个 Run。</p>
        ) : (
          <RunView key={route.runId} route={route} navigate={navigate} />
        )}
      </main>
      <aside className="chain-pane" aria-labelledby="chain-title">
        <div className="chain-head">
          <h2 id="chain-title" ref={chainHeading} tabIndex={-1}>
            证据链
          </h2>
          {claimId !== null ? (
            <button type="button" className="close" onClick={closeChain}>
              关闭证据链
            </button>
          ) : null}
        </div>
        {claimId === null ? (
          <p className="empty">点一条结论，在这里查看它的证据链。</p>
        ) : (
          <EvidenceChain key={claimId} claimId={claimId} cache={cache} />
        )}
      </aside>
    </div>
  );
}
```

- [ ] **步骤 6：确认测试通过**

在 `web/` 运行：`npm run test -- src/App.test.tsx`

预期：14 个测试通过。

- [ ] **步骤 7：检查点**

在 `web/` 运行：`npm run check`。不提交。

---

### 任务 6：静态检查、文档与真实数据核对

**文件：**
- 新建：`web/src/readOnly.test.ts`
- 修改：`AGENTS.md`、`README.md`、`docs/roadmap.md`、`docs/architecture.md`、`docs/evidence-viewer.md`

**接口：**
- 消费：全部前序任务的源码文件。

- [ ] **步骤 1：写静态检查测试**

`web/src/readOnly.test.ts`：

```ts
import { describe, expect, it } from "vitest";

const sources = import.meta.glob(
  ["./**/*.ts", "./**/*.tsx", "!./**/*.test.ts", "!./**/*.test.tsx", "!./test/**"],
  { query: "?raw", import: "default", eager: true },
) as Record<string, string>;

describe("read-only viewer", () => {
  it("calls fetch only from the API client", () => {
    const offenders = Object.entries(sources)
      .filter(([path, text]) => path !== "./api/client.ts" && /\bfetch\s*\(/.test(text))
      .map(([path]) => path);

    expect(Object.keys(sources).length).toBeGreaterThan(10);
    expect(offenders).toEqual([]);
  });

  it("sends only GET requests", () => {
    const client = sources["./api/client.ts"];

    expect(client).toMatch(/method: "GET"/);
    expect(client).not.toMatch(/method: "(POST|PUT|PATCH|DELETE)"/);
  });

  it("does not contain machine paths", () => {
    const offenders = Object.entries(sources)
      .filter(([, text]) => /[A-Za-z]:\\\\|\/Users\/|\/home\//.test(text))
      .map(([path]) => path);

    expect(offenders).toEqual([]);
  });
});
```

- [ ] **步骤 2：确认测试通过**

在 `web/` 运行：`npm run test -- src/readOnly.test.ts`

预期：3 个测试通过。若第一个测试失败，找到列出的文件，把 `fetch` 调用移到 `api/client.ts`。

- [ ] **步骤 3：更新文档**

- `AGENTS.md` §4：`App.tsx` 注释保持「三栏骨架与网址路由」，删掉「脚手架页面；证据链查看器见 FE-04」字样（若仍存在）。
- `README.md`「快速开始」末尾加：

````markdown
### 证据链查看器

```powershell
uv run research-agent serve --db data/research_agent.db
cd web
npm run dev
```

浏览器打开 `http://127.0.0.1:5173`。页面只读，数据来自本地 API。
````

- `docs/roadmap.md`：FE-04 改为「已完成，2026-10-14」，验证写 `web/src/App.test.tsx` 与 `web/src/readOnly.test.ts`，以及真实数据截图核对。
- `docs/architecture.md` §15：`Interface Layer` 一行改为「只读 `/v1` 与证据链查看器已实现；提问、进度与导出未做」，路线图列为 `FE-05`–`FE-10`。
- `docs/evidence-viewer.md`：状态改为「已实现」。

- [ ] **步骤 4：全部检查**

在项目根运行：

```powershell
uv run python scripts/check_web.py
uv run ruff check .
uv run mypy src scripts
$env:TEMP = "$env:LOCALAPPDATA\Temp"; $env:TMP = "$env:LOCALAPPDATA\Temp"; uv run pytest --basetemp "$env:LOCALAPPDATA\Temp\ra-pytest"
uv run python scripts/check_docs.py
```

预期：全部通过。

- [ ] **步骤 5：用真实数据核对**

已有数据库不能被改写（`AGENTS.md` §7 第 6 条）。先复制一份，再对副本启动 API：

```powershell
New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\Temp\ra-viewer" | Out-Null
Copy-Item data\pilot_v2_adr0015.db "$env:LOCALAPPDATA\Temp\ra-viewer\viewer.db"
uv run research-agent serve --db "$env:LOCALAPPDATA\Temp\ra-viewer\viewer.db"
```

另开一个终端：`cd web; npm run dev`。在浏览器打开 `http://127.0.0.1:5173`，依次核对：

1. Run 列表有数据，时间是北京时间。
2. 概览显示七个步骤和来源横条。
3. 候选论文中被过滤的论文显示原因。
4. 点一条有证据的结论，右栏出现证据、论文、源站记录。
5. 浏览器宽度缩到 1000px，右栏变成抽屉；缩到 800px，左栏变成下拉。
6. 长标题和长引文换行，页面没有横向滚动条。

截图保存并在汇报中展示。核对完关闭两个进程；副本数据库留在临时目录，不进入 Git。

- [ ] **步骤 6：检查点**

不提交。向用户汇报完成情况、截图和仍未覆盖的部分。
