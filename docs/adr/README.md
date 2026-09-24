# Architecture Decision Records

本目录记录影响项目架构、论文贡献、数据模型、评测和实现边界的决策。

## 状态定义

- `Proposed`：已提出，尚未接受。
- `Accepted`：已接受，作为当前实现约束。
- `Superseded`：已被后续 ADR 替代。
- `Deprecated`：不再推荐，但仍需保留历史背景。

## 编号规则

- 文件名：`NNNN-kebab-case.md`。
- 编号按创建顺序递增，不重复使用。
- 替代旧决策时新建 ADR，并在旧 ADR 中标记 `Superseded by ADR-XXXX`。
- 修改已接受决策必须新建 ADR，不直接重写历史。

## 当前决策

| 编号 | 标题 | 状态 |
|---|---|---|
| 0001 | 独立 Agent，Pi 仅作参考 | Accepted |
| 0002 | 状态机 + Plan-and-Execute | Accepted |
| 0003 | 证据链作为主贡献 | Accepted |
| 0004 | 每源独立 MCP + 自研联邦 | Accepted |
| 0005 | Local-first、SQLite + FTS5 + 文件系统 | Accepted |
| 0006 | 评测驱动开发与消融实验 | Accepted |
| 0007 | MCP 协议层采用官方 SDK，源站适配与联邦自研 | Accepted |
| 0008 | 证据链基数与 provenance | Accepted |
| 0009 | 正式评测规模与任务指标拆分 | Accepted |
| 0010 | SQLite schema、迁移与完整性策略 | Accepted |
| 0011 | 可移植性与 GitHub 分发 | Accepted |
| 0012 | 语义相关性过滤 | Accepted |
| 0013 | 源站响应缓存 | Accepted |
| 0014 | 纯 ReAct baseline 使用独立受限循环 | Accepted |
