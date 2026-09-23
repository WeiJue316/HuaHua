# ADR-0012：语义相关性过滤

- 状态：Accepted
- 日期：2026-09-24
- 决策者：LYY
- 关联文档：`docs/evaluation.md`, `docs/roadmap.md`, `docs/adr/0006-evaluation-driven-development.md`, `docs/adr/0009-evaluation-scale-and-task-metric-separation.md`

## 背景

pilot 评测集的人工复核暴露了一类系统性失败：**用关键词匹配从开放学术源自动构建候选时，会稳定地把邻域论文收进来**。

复核期间实际发生的误召回：

| 目标问题 | 被误收的论文 | 误收原因 |
|---|---|---|
| 智能体规划与记忆 | 芯片设计 EDA 论文 | 摘要含 planning / agent 等词 |
| 多模态检索基准 | 语音数据集 FLEURS | 摘要含 dataset / benchmark |
| 稠密与稀疏检索对比 | 生物医学检索 MedCPT | 摘要含 retrieval / evaluation |
| 参数高效微调 | RLHF 指令微调 InstructGPT | 摘要含 parameter / training |

这些论文的**标题相邻、词面高度重合**，但都不回答所问的问题。同时还有另一类失败：论文本身对口，被引用的却是摘要开头的背景句（"LLMs have impressive capabilities..."），句子并不支撑其标注的子问题。

两类失败的共同根因是同一个：**词重合只能近似"论文主题相近"，无法判断"这段话是否回答了这个问题"**。前者与后者是两件事，而现有确定性实现只做了前者。

项目设计原则中已经写明 LLM 只介入规划、相关性判断、证据抽取与综合生成，本 ADR 把"相关性判断"这一项落地为具体机制。

## 决策

引入 LLM 语义相关性过滤，作为检索与结论合成之间的一个独立可替换步骤。

### 1. 两层判定

**候选级**：给定研究问题、子问题与候选论文的标题和摘要，判定该论文是否值得进入候选集。

输出三值而非二值，理由是复核中确实出现过"沾边但不直接回答"的情况：

```
relevant      论文直接回答该问题
tangential    主题相邻但不回答该问题（如芯片设计的规划方法之于 LLM 智能体规划）
irrelevant    与本问题无关
```

只有 `relevant` 进入结论合成；`tangential` 与 `irrelevant` 保留在库中但不参与生成。

**证据级**：给定子问题与候选句，判定该句是否支撑该子问题。复用 `claim.support_status` 的既有取值：

```
supported            句子直接回答该子问题
partially_supported  部分相关或需要上下文才能成立
unsupported          不支撑（例如背景句）
```

### 2. 批量调用，不是逐篇调用

一个问题一次调用（候选过多时分批），模型返回结构化判定列表。

理由：720–810 次 Run 的评测规模下，逐篇调用会产生数万次请求，成本和延迟都不可接受。批处理后每次 Run 的 LLM 调用次数与问题数同阶。

### 3. 失败语义：fail-open

模型调用失败、超时或返回不可解析时，**保留候选并进入生成**，同时在 `audit_event` 记录失败。

理由：评测的可信性要求不能因基础设施抖动而静默改变候选集。fail-closed 会让一次 429 变成"这次运行少检索到 3 篇论文"，且事后无法区分是过滤器判定还是调用失败。失败必须可见，与现有 `source_errors` / `variant_errors` 的处理方式一致。

### 4. 落库方式：不新增表，不改 schema

现有 schema 在设计时已为 LLM 预留结构，经核对可直接承载：

| 数据 | 落库位置 |
|---|---|
| 每次 LLM 调用（provider、model、prompt_version、tokens、cost、latency） | `model_call` |
| 每条候选判定（放行 / 拒绝、理由、模型调用 id） | `audit_event`（`actor='system'`，`decision` 取既有值 `allowed` / `denied`，`details_json` 存判定等级与理由） |
| LLM 选定的证据句 | `evidence_span.extraction_method='llm'`，`confidence` 记录判定置信度 |
| 支持状态 | `claim.support_status`（复用既有四值） |

`evidence_span.extraction_method` 的既有取值已包含 `'llm'`，无需扩展。

### 5. 位置与开关

流水线插入一个步骤：

```
route_sources → search_sources → persist_results
  → judge_relevance → synthesize_claims → validate_citations → generate_report
```

`persist_results` 仍写入全部候选，判定不删除任何记录——被拒候选留在库中，使过滤器本身的精度可被事后分析。`synthesize_claims` 只使用放行候选。

过滤默认开启，可通过配置关闭，关闭即为消融条件 A6。

### 6. 新增消融 A6

| 编号 | 消融项 | 移除内容 | 预期观察 |
|---|---|---|---|
| A6 | 去语义过滤 | 移除 judge_relevance 步骤 | Precision@K 下降、Citation Accuracy 下降、Unsupported Claim Rate 上升 |

A6 与 A1–A4 的区别：A1–A4 验证证据链、规划、路由与引用约束；A6 验证语义相关性判断这一独立能力。

### 7. 模型与可复现性

- provider、model ID、prompt version、温度（0）全部写入配置并随 Run 记录。
- prompt 模板纳入版本管理，文件路径与哈希写入 `model_call.prompt_hash` / `prompt_version`。
- 单元测试与 CI 使用**离线桩**，不访问真实模型 API，与现有源站 fixture 策略一致。

## 后果

正面：

- 直接回应人工复核中发现的真实失败，而非凭空增加功能。
- 判定过程全部落库，过滤器自身的精度/召回可被独立评估，构成一项可发表的实验。
- 复用既有 schema 与既有枚举值，不引入数据迁移风险。
- fail-open 保证评测结果不因基础设施抖动而失真。

负面：

- 这是项目第一次引入 LLM 调用，需要新增模型客户端抽象、密钥管理与成本记录。
- 增加每次 Run 的 token 成本，需纳入 H3b（token 成本不超过纯 ReAct 的 1.5 倍）的核算。
- 模型随机性虽已设温度 0，仍需记录方差。
- 批量判定的候选数上限需要调参，候选过多时须分批。

## 备选方案

1. **继续改进关键词启发式**（扩充停用词、加权、同义词表）：已尝试到收益拐点，且本质是拟合 pilot 的 10 道题，换题即失效。拒绝。
2. **引入向量检索与语义相似度**：需要嵌入模型与向量库，项目 v1 明确不引入向量数据库。拒绝。
3. **只用 LLM 做最终引用校验，不做候选过滤**：无法解决"论文不对口"这一半失败（不对口的论文仍会进入候选并可能生成结论）。拒绝。
4. **fail-closed（调用失败即丢弃候选）**：会静默改变候选集，损害评测可信性。拒绝。

## 约束

- 不得在未记录 `model_call` 的情况下发起 LLM 调用。
- 判定结果不得删除已有记录，只能新增 `audit_event`。
- 正式评测开始后不得修改 prompt；修改必须新版本并重跑受影响配置。
- 过滤器精度必须用 pilot v1 冻结集作为参照报告，不得只报告个案。
- 若 A6 显示过滤无显著增益，必须如实报告。

## 实证结果（2026-09-24 预实验）

在写任何实现代码之前，用 DeepSeek `deepseek-v4-flash` 对 41 条已标注样本做了一次候选级判定实验。

样本构造：pilot v1 的 24 篇 gold paper 作正样本；复核过程中被移除的论文作负样本。
原始 19 篇中剔除 2 篇——一篇因 OpenAlex 该 DOI 返回他文（元数据错误），
一篇（Plan-and-Solve Prompting）经核查确为 CoT 推理论文，不属于负样本。
最终 24 正 + 17 负。

结果（零调用失败）：

| 样本 | relevant | tangential | irrelevant |
|---|---:|---:|---:|
| 正样本（24） | 15 | 9 | 0 |
| 负样本（17） | 0 | 10 | 7 |

按不同阈值使用该判定：

| 阈值 | 保留数 | 真正例 | 假正例 | 漏放 | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|
| 严格（仅 relevant） | 15 | 15 | 0 | 9 | **1.00** | 0.62 |
| 宽松（relevant + tangential） | 34 | 24 | 10 | 0 | 0.71 | **1.00** |

### 关键发现（完整摘要 + 子问题口径的最终结果）

| 样本 | relevant | tangential | irrelevant |
|---|---:|---:|---:|
| 正样本（24） | 18 | 6 | 0 |
| 负样本（17） | 1 | 8 | 8 |

严格阈值（仅 relevant）：**precision 0.95，recall 0.75**。

**发现一：`irrelevant` 干净地分开了跨领域论文。**
8 篇被判 irrelevant 的负样本全部来自无关领域；24 篇正样本无一被判 irrelevant。
该档可直接用于候选过滤，无需阈值调参。

**发现二：`answer_role` 是程度差异，不是对错。**
6 篇被判 tangential 的 gold paper 中，3 篇（Precise Zero-Shot、SciFact-Open、
ML lifecycle artifacts）提供支持性证据但不逐字回答问题——这正是文学综述需要的第二类
材料，应当保留。**结论：pilot v1 无需替换论文。**

**发现三（新）：部分源站没有真实摘要，过滤器会因此误拒。**

RAGAs 与 ARES 在 OpenAlex 中的 abstract 字段只有作者名单与会议名称，没有正文摘要。
两篇都被模型以"摘要仅含作者与出版信息"为由判为 tangential——**判定正确，但结论错误**，
因为问题出在数据源而不是论文。

这解释了 seed 生成器当初为何拒绝这两篇，也意味着：**过滤器必须区分"摘要不可用"与
"摘要表明不相关"**，否则会静默丢弃好论文。这是 fail-open 原则在候选级的直接延伸。

**发现四（新）：温度 0 仍有运行间波动。**

同一 prompt、同一输入、`temperature=0`，两轮之间有 2 条判定发生变化（RAGAs、ARES，
均在摘要未变的情况下从 relevant 变为 tangential），约占 5%。评测记录必须包含重复运行的
方差，与 `docs/evaluation.md` 第 8.1 节的既有要求一致。

**发现五：工程参数。**

- `max_tokens=300` 时 3/41 条返回 `finish_reason=length` 且 content 为空——推理内容占用
  同一预算。**该模型需要 ≥900 的输出预算。**
- 单次判定约消耗 506 输入 token、245 输出 token（完整摘要口径）。
- **摘要不得截断**：截断到 2400 字符时，唯一超长的 MKVSE 摘要末句（列出 Flickr30k 与
  MSCOCO）被切掉，导致一次事实性误判。修正后该条从 tangential 变为 relevant。
- 即便要求 JSON 输出格式，仍需容错解析与重试。

### 对设计的影响

原设计的三值判定需要重新审视。两个维度应当分别建模：

- `domain_scope`：in_scope / out_of_scope —— 可靠，可直接用于候选过滤。
- `answer_role`：direct / supporting / none —— 用于证据选择与结论支撑强度，
  不单独作为剔除候选的依据。
- **摘要可用性**必须是独立状态，不能与 `domain_scope` 混淆：源站缺失摘要时不得据此
  拒绝候选，应标记为 `abstract_unavailable` 并按 fail-open 处理，或转而从其他源补全。

同时，通过阈值必须成为配置项：严格阈值 precision 高但 recall 低，宽松阈值反之。
二者都应进入 A6 的消融对比。

**该实验同时暴露了 pilot v1 的标注问题，与过滤器设计是两件事，不应混为一谈。**

## 待决问题

以下三项需在实施前确认：

1. **模型选型**：使用哪个 provider 与模型？需可配置，并记录成本。低成本模型足以胜任三值判定，但需实验确认。
2. **A6 是否计入核心配置**：当前核心为 8 配置共 720 次 Run。纳入 A6 后为 9 配置共 810 次 Run，需评估时间与成本预算。
3. **过滤器精度评测方案**：pilot v1 的 24 篇 gold paper 可作为正样本；复核期间被替换的 9 篇论文（芯片设计、语音数据集、生物医学检索、RLHF 等）可作为负样本。样本量小，只能作为冒烟验证，正式评测需在 30 题集上重新构造。