# ADR-0008：证据链基数与 provenance

- 状态：Accepted
- 日期：2026-09-23
- 决策者：LYY
- 关联文档：`docs/PRD.md`, `docs/architecture.md`, `docs/data-model.md`, `docs/adr/0003-evidence-chain-as-primary-contribution.md`

## 背景

原设计把主链统一写成 `Claim → Evidence Span → Paper → File`，但摘要和元数据证据通常没有可下载 File。若强制所有证据都关联 File，会与实际科研调研流程冲突，也会让摘要级证据无法进入证据链。与此同时，Evidence Span 缺少对具体 Source Record 的引用，摘要证据无法回答“这条证据来自哪个源站的哪条原始记录”。

## 决策

v1 的规范证据链定义为：

```text
Claim
  → Evidence Span
      → Paper
          → Source Record*
          → File → Document       # 仅 full_text 证据必需
```

具体要求：

- 所有系统生成的 Evidence Span 必须关联 Paper 和 Source Record。
- `metadata` 和 `abstract` 证据必须关联 Source Record，但不要求 File 和 Document。
- `full_text` 证据必须同时关联 Source Record、File 和 Document。
- `external` 证据在 v1 中必须挂接到某个 Paper 和 Source Record；无 Paper 的外部材料留到 v2 再引入 `ExternalSource`。
- Claim 的支持状态和证据级别必须分开判断，不能因为存在摘要证据就声称支持全文细节。
- 报告中的支持性或部分支持性关键结论必须绑定 Evidence Span；无证据结论必须显式标记为 `unsupported` 或待验证。

## 后果

正面：

- 证据链覆盖摘要、元数据和全文三种真实情况。
- 摘要证据也能追溯到具体源站记录。
- 论文中的主贡献定义更严谨，不再暗含“所有论文都能获得全文”。

负面：

- Evidence Span 增加 Source Record 关联，数据模型和校验逻辑更复杂。
- 同一 Paper 的多个来源摘要可能产生多条 Evidence Span，需要去重和排序。

## 备选方案

1. 强制所有证据关联 File：不符合摘要级证据现实，拒绝。
2. 允许 Evidence Span 只关联 Paper：provenance 不足，拒绝。
3. 为外部材料建立独立 ExternalSource：v1 范围过大，延后到 v2。

## 约束

- `source_record_id` 是系统生成 Evidence Span 的必需字段。
- full_text 证据缺少 File 或 Document 时，不得标记为 validated。
- 摘要证据不得支持需要全文才能确认的数字、实验设置或限制性结论。
