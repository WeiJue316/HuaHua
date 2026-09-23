# Pi 底层框架调研记录

- 日期：2026-09-23
- 核验仓库：`https://github.com/earendil-works/pi`
- 核验 commit：`b4588f26af2f74f7b1387b548e04a3c8d81da75b`
- 核验分支：`main`

## 结论

Pi 是 Node.js + TypeScript 的 monorepo，不是建立在 LangChain、AutoGen 等 Agent 框架上的套壳系统。它自行实现 Agent Loop、工具执行、状态管理、事件流和模型适配层。

主要包：

- `@earendil-works/pi-ai`：统一模型接口、Provider、流式输出、工具调用和认证。
- `@earendil-works/pi-agent-core`：Agent Loop、状态、工具执行、上下文转换和事件流。
- `@earendil-works/chord`：通用服务、Facet 和复制状态运行时。
- `@earendil-works/pi-durable`：持久化对话、任务和文档运行时。
- `@earendil-works/pi-coding-agent`：CLI/TUI 产品、工具、扩展、Skill 和 Package 加载。
- `pi-protocol`、`pi-client`、`pi-server`：RPC 和客户端/服务端接口。

## MCP 的位置

当前 Pi 主仓库没有内建 `@modelcontextprotocol/sdk` 依赖，也没有独立的 MCP server/client 包。MCP 通过扩展包接入，例如 `pi-mcp-adapter`。准确表述应为：

> Pi 提供 Agent Runtime、扩展机制和 Skill 机制；MCP 通过扩展接入，不是 Pi Core 的内置能力。

## 对本项目的启示

- Pi 可以作为 Agent Loop、事件流、Session 树、扩展边界和 Provider 抽象的参考。
- 不 fork Pi，不把 Pi 作为运行时依赖。
- MCP 协议层使用官方 Python SDK；自研重点是每源 MCP server、Federation/Router、去重、provenance 和证据链。
- 论文中必须区分“借鉴 Pi 的设计”和“作者实现的模块”。
