# ADR-0003：证据链作为主贡献

- 状态：Accepted
- 日期：2026-09-23
- 决策者：LYY
- 关联文档：`docs/PRD.md`, `docs/data-model.md`, `docs/evaluation.md`

## 背景

科研 Agent 很容易退化为“搜索 + LLM 总结”：结果看似流畅，但无法确认结论来自哪篇论文、哪一段、通过什么方法抽取。多源 MCP、规划器和 Web UI 都能体现工作量，但不足以构成清晰的论文主贡献。

## 决策

把证据链作为论文主贡献，定义为：

```text
Claim
  → Evidence Span
      → Paper
          → Source Record*
          → File → Document       # 仅 full_text 证据必需
```

具体要求：

- Claim 必须标记支持状态。
- Evidence Span 必须包含原文、locator、抽取方法、置信度、来源版本和 `source_record_id`。
- Paper 必须保留多个 Source Record 和 provenance。
- metadata/abstract 证据必须关联 Source Record；全文证据必须关联 File 和 Document。
- 报告生成后执行引用和 locator 校验。
- 无支撑 Claim 必须显式标记。

多源 MCP 联邦与路由作为支撑贡献；Plan-and-Execute 作为系统支撑，不作为第一创新点。

## 后果

正面：

- 论文贡献边界清晰，可围绕 RQ1 设计实验。
- 与普通 RAG 或文献搜索工具形成可验证差异。
- 能通过引用准确率、无支撑结论率和 locator 有效率评测。

负面：

- PDF 解析和 locator 稳定性成为关键风险。
- 数据模型和报告流程更复杂。
- 需要人工抽样验证引用支持关系。

## 备选方案

1. 以多源 MCP 为主贡献：工作量可见，但容易被视为接口封装，拒绝作为主贡献。
2. 以 Agent 规划为主贡献：容易与通用 Agent 工作重叠，作为支撑。
3. 以 UI 为主贡献：与科研问题关联弱，拒绝。

## 约束

- 报告不得输出无法追溯的关键结论。
- 摘要级证据不能支持全文细节结论。
- 本 ADR 由 ADR-0008 进一步细化证据链基数和 provenance 规则。
- 证据链校验失败时，报告状态不得为 `validated`。
