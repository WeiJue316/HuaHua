# ADR-0007：MCP 协议层采用官方 SDK，源站适配与联邦自研

- 状态：Accepted
- 日期：2026-09-23
- 决策者：LYY
- 关联文档：`docs/mcp-contract.md`, `docs/architecture.md`, `docs/adr/0004-per-source-mcp-and-federation.md`

## 背景

MCP 是 Agent 与外部工具或数据源之间的协议。重新实现协议传输层不会直接增加论文贡献，却会引入兼容性、鉴权和错误语义风险。项目真正需要自研的是源站适配、能力声明、联邦路由、去重、provenance 合并和证据链。

对 Pi 的源码核验也表明：Pi 的核心是 TypeScript/Node Agent Runtime，MCP 通过扩展包接入，并不是 Pi Core 的内置协议实现。因此本项目不应把“实现了 MCP 协议”当作主要工作量。

## 决策

- MCP 协议层使用官方 Python SDK，不自行重写协议传输层。
- 每个源站独立实现 MCP server，负责源站 API、认证、限流、字段映射和错误语义。
- Federation、Router、去重、provenance 合并和证据链由本项目自研。
- MCP server 必须声明协议版本、SDK 版本、上游 API 版本和 capability manifest。
- 第三方 MCP SDK 必须处于可替换位置，不能渗透到领域模型和证据链。

## 后果

正面：

- 降低协议兼容性和调试成本。
- 自研工作量集中在源站适配和系统语义上。
- 可以在论文中清楚区分“协议实现”和“作者贡献”。

负面：

- 需要跟随官方 SDK 的版本变化。
- 公共契约仍需自行维护，不能把 SDK 能力等同于系统能力。

## 备选方案

1. 自行实现 MCP 协议层：兼容性风险高，论文收益低，拒绝。
2. 只做一个通用学术 MCP：无法体现每源独立适配和联邦贡献，拒绝。
3. 让 Agent Core 直接调用源站 HTTP API：耦合高，无法体现 MCP 边界，拒绝。

## 约束

- 论文不得把官方 MCP SDK 的能力声称为作者自研。
- 源站 server 不得依赖 Agent Core 内部类型。
- MCP 版本升级必须记录 ADR 或变更说明，并运行契约测试。
