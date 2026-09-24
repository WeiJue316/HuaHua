# ADR-0014：纯 ReAct baseline 使用独立受限循环

- 状态：Accepted
- 日期：2026-09-24
- 关联文档：`docs/evaluation.md`, `docs/adr/0002-state-machine-plan-and-execute.md`

## 背景

RQ3 需要比较完整系统的状态机 + Plan-and-Execute 与纯 ReAct baseline。
如果把 B2 实现成“关闭 Planner 的完整 runtime”，状态机、持久化步骤和证据链
仍会暗中参与执行，baseline 不再是纯 ReAct；如果让 B2 直接复用完整运行时，
又会把 A2（去规划器）与 B2（纯 ReAct）混为一谈。

## 决策

B2 使用独立的 `PureReActBaseline`：

- LLM 在受限循环中选择 `search` 或 `finish`。
- 搜索工具复用与完整系统相同的源站 client、限流、缓存和统一 `PaperCandidate`。
- 每轮只允许一个搜索动作；最大步数、单次结果数、模型输出预算均有硬限制。
- 不创建 Plan，不经过 Executor 状态机，不强制 Evidence Span、Claim 或引用校验。
- 每轮保存结构化 trace，最终报告单独归档。
- 指标记录检索 key、模型调用、token、延迟、步数和是否生成报告。

B2 的目标是评测“自由工具循环”这一运行方式，不是实现一个更弱的完整系统。
因此它允许搜索失败后继续探索，也允许 LLM 自行决定何时结束；最大步数到达而
没有 `finish` 时，该 case 明确失败。

## 后果

正面：

- B2 与 B3 的区别集中在 Plan/状态机，而不是偷偷改变源站或候选结构。
- 工具循环可离线测试，步数和成本可审计。
- A2 仍可在后续实现为“固定检索流水线”，不与 B2 重复。

负面：

- B2 没有证据链，不能参与 Evidence Compliance 等主贡献指标。
- ReAct 的轨迹不稳定，正式评测需要固定 prompt、模型版本、步数和缓存。
- 多次搜索会产生更高 token 与 API 调用成本，因此必须记录预算和失败原因。

## 备选方案

1. 复用完整 runtime 并关闭 Planner：拒绝，状态机和确定性步骤仍在。
2. 让 LLM 生成可执行 Python：拒绝，安全和可重复性不可接受。
3. 多 Agent 协作：超出 v1 范围。