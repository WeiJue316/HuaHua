# ADR-0004：每源独立 MCP + 自研联邦

- 状态：Accepted
- 日期：2026-09-23
- 决策者：LYY
- 关联文档：`docs/mcp-contract.md`, `docs/architecture.md`

## 背景

arXiv、OpenAlex、Crossref、Semantic Scholar 和 DBLP 的 API、认证、限流、字段和错误语义不同。如果只做一个“学术 MCP”，源站适配会混在一个服务中，工作量不清晰，也难以独立测试。如果为每个源站重复复制代码，又会造成维护成本。

## 决策

采用“每个源站一个独立 MCP server + 自研 Federation/Router”：

- 每个源站独立实现 server、capability manifest、认证、限流和契约测试。
- 公共代码只放在 `mcp-common`，包含协议初始化、错误、重试、限流和 envelope 校验。
- 禁止 MCP server 之间互相调用。
- Federation 负责并行调用、超时、重试、归一化、去重和 provenance 合并。
- Router 负责能力选择，不把“调用所有源站”当默认策略。

## 后果

正面：

- 源站适配工作量可独立说明和测试。
- 单个源站故障不会污染其他适配器。
- 可以逐步扩展 OpenReview、ACL Anthology、CVF 等源站。
- Federation 成为可评测的支撑贡献。

负面：

- 五个 server 增加启动、配置和版本管理成本。
- 公共字段和错误码需要严格契约。
- 容易退化为五个重复 HTTP wrapper，必须通过 capability 和契约测试避免。

## 备选方案

1. 单个通用学术 MCP：实现快，但工作量集中且接口模糊，拒绝。
2. 每个源站直接由 Agent Core 调用：耦合高，无法体现 MCP 边界，拒绝。
3. 只接一个聚合服务：覆盖有限，无法验证联邦，拒绝。

## 约束

- 未声明的 capability 必须返回 `capability_not_supported`。
- 源站原始字段和错误语义必须保留。
- 去重和合并不得在单个 MCP server 内完成。
- 新增源站不得要求修改 Evidence 数据模型。
