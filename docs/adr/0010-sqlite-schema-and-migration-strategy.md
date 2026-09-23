# ADR-0010：SQLite schema、迁移与完整性策略

- 状态：Proposed
- 日期：2026-09-23
- 决策者：LYY
- 关联文档：`docs/data-model.md`, `docs/architecture.md`, `docs/adr/0005-local-first-sqlite-fts5-filesystem.md`

## 背景

`docs/data-model.md` 已定义 v1 的实体、关系和关键不变量，但尚未决定：

1. 初始 schema 如何版本化。
2. SQLite 虚拟表、触发器和索引如何管理。
3. 迁移失败、版本回退和数据库损坏时如何恢复。
4. 如何验证证据链约束没有被迁移破坏。

本项目的数据库属于本地单用户运行时数据，但证据链需要可复现和可审计。迁移策略不能依赖“删除数据库重建”，也不能让 ORM 在运行时静默修改表结构。

## 决策

### 1. 迁移载体

- 使用 SQLite 原生 SQL 迁移文件，目录为 `src/research_agent/storage/migrations/`。
- 文件命名：`NNNN_description.sql`，例如 `0001_initial_schema.sql`。
- v1 采用前向迁移；每个迁移必须有唯一版本号和 SHA-256。
- 使用 Python 标准库 `sqlite3` 实现最小迁移 runner，不引入 ORM 或自动建表框架。
- 迁移 runner 和迁移文件是 Storage 层实现，不进入 Agent 核心决策逻辑。

### 2. 版本记录

建立 `schema_migrations` 表：

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `version` | INTEGER | PK | 迁移版本号 |
| `name` | TEXT | NOT NULL | 迁移文件名 |
| `sha256` | TEXT | NOT NULL | 迁移文件哈希 |
| `applied_at` | TEXT | NOT NULL | UTC ISO 8601 |

同时维护 `PRAGMA user_version`，用于快速判断数据库版本。`schema_migrations` 是审计记录，`user_version` 只是加速缓存；二者不一致时迁移失败并进入恢复流程。

### 3. 连接与事务

数据库连接默认启用：

```sql
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;
```

迁移执行流程：

1. 获取数据库文件级锁。
2. 检查当前版本和迁移文件连续性。
3. 对现有数据库创建备份。
4. 在事务中执行下一个迁移。
5. 运行 `PRAGMA foreign_key_check` 和 `PRAGMA integrity_check`。
6. 写入 `schema_migrations`，更新 `user_version`。
7. 任一阶段失败则回滚事务，并保留备份供恢复。

迁移不得静默删除表、列或证据数据。需要破坏性变更时，必须新建 ADR、提供数据迁移脚本和恢复步骤，并获得用户确认。

### 4. 初始化与恢复

- 新数据库：创建文件后依次执行全部迁移。
- 已有数据库：只执行未应用的连续迁移。
- 迁移失败：优先回滚事务；若数据库文件已经受损，则从迁移前备份恢复。
- 回退：v1 不提供自动 down migration，回退通过恢复备份完成。
- 备份路径：`data/backups/<timestamp>-research_agent.db`。
- 数据库文件、备份和 WAL 文件不得提交到 Git。

### 5. 实体与约束

- 表名、字段名使用 `snake_case`，与 `docs/data-model.md` 一致。
- 主键使用 TEXT UUID；时间字段使用 UTC ISO 8601 TEXT。
- 外键约束必须显式声明，不能只依赖应用层检查。
- `SourceRecord` 采用追加写：禁止原地 UPDATE 和 DELETE。
- `AuditEvent` 采用追加写：禁止 UPDATE 和 DELETE。
- `File` 使用逻辑删除；物理删除必须由用户显式确认。
- 关键唯一约束至少包括：
  - `UNIQUE(paper_id, sha256)` on File。
  - `UNIQUE(step_id, attempt_no)` on StepAttempt。
  - `UNIQUE(source_call_id, attempt_no)` on SourceCallAttempt。
  - `UNIQUE(evaluation_run_id, question_id, system_id, run_number)` on EvaluationCase。
  - `UNIQUE(evaluation_case_id, metric_name)` on EvaluationResult。

### 6. 索引与 FTS5

初始 schema 至少建立：

- 外键索引：`project_id`、`run_id`、`paper_id`、`source_record_id`、`document_id`。
- 运行状态索引：`Run(status, started_at)`。
- 检索索引：`Paper(doi)`、`Paper(arxiv_id)`、`Paper(normalized_title, year)`。
- 评测索引：`EvaluationCase(status, system_id)`。

FTS5 索引：

```text
paper_fts(title, abstract, venue, authors_text)
evidence_fts(quote, section, paper_title)
note_fts(title, body_text)
```

FTS5 一致性由迁移创建的触发器和应用层事务共同维护；重建索引必须提供独立命令，且不得改变原始实体。

### 7. 验证矩阵

初始 schema 和每次迁移都必须测试：

1. 全新数据库可一次迁移到最新版本。
2. 重复运行迁移 runner 不重复应用版本。
3. `foreign_key_check` 和 `integrity_check` 通过。
4. `SourceRecord` 和 `AuditEvent` 的 UPDATE/DELETE 被拒绝。
5. FTS5 插入、更新和重建行为符合预期。
6. 迁移失败不会留下部分 schema。
7. 备份可以恢复并保持证据链可读。
8. 旧版本数据库升级后，Paper、EvidenceSpan 和 File 关联仍然有效。

## 后果

正面：

- schema 变更有明确版本、审计和恢复路径。
- 不引入 ORM，SQLite 行为和 FTS5 约束保持透明。
- 迁移失败不会以“删库重建”方式丢失证据数据。

负面：

- 需要维护迁移 runner、备份和完整性测试。
- 前向迁移策略要求变更设计更谨慎，不能依赖自动 down migration。
- 迁移文件和 schema 需要持续与 `docs/data-model.md` 对齐。

## 备选方案

1. 使用 ORM 自动建表：难以表达 FTS5、触发器和追加写约束，拒绝作为 v1 主方案。
2. 使用 Alembic：适合复杂 schema，但对当前单文件 SQLite + FTS5 引入额外抽象；若后续 schema 复杂度显著上升，再评估替换。
3. 每次启动时比较表结构并自动修补：不可审计且可能静默破坏证据数据，拒绝。
4. 删除数据库并重建：违反证据链和可复现性要求，拒绝。

## 约束

- 本 ADR 处于 Proposed 状态；未获用户确认前不得创建初始数据库或执行迁移。
- 任何 schema 变更都必须更新本 ADR 或新建 ADR，并更新 `docs/data-model.md`。
- 迁移前必须备份，迁移后必须运行完整性和引用链校验。
- 迁移脚本不得修改已归档文件，也不得删除不可变 Source Record。