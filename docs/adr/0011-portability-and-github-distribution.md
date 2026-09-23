# ADR-0011：可移植性与 GitHub 分发

- 状态：Accepted
- 日期：2026-09-23
- 决策者：LYY
- 关联文档：`README.md`, `pyproject.toml`, `docs/adr/0005-local-first-sqlite-fts5-filesystem.md`

## 背景

项目需要上传到 GitHub 供其他用户安装和验证。当前开发环境是 Windows，但公开项目必须避免依赖本机盘符、用户目录、IDE 配置或单一 shell。用户克隆仓库后，应能用统一命令完成环境初始化和基线验证。

同时，科研数据、PDF、SQLite 数据库、API 密钥和本地缓存不能进入公开仓库。

## 决策

### 1. 运行时与依赖

- 运行时基线为 Python 3.12。
- 使用 `uv` 管理虚拟环境、Python 版本和依赖。
- 提交 `pyproject.toml` 和 `uv.lock`，不提交 `.venv/`。
- 用户初始化命令固定为：

```powershell
uv sync --dev
```

### 2. 跨平台约束

- 代码使用 `pathlib.Path`，不使用硬编码盘符、反斜杠或用户目录。
- 配置中的路径相对项目根目录解析。
- CLI、测试和脚本不得依赖 PowerShell 专有行为；需要平台差异时提供明确的跨平台分支。
- 文件编码统一为 UTF-8。
- `.editorconfig` 统一编辑器行为，`.gitattributes` 统一换行规则和二进制文件处理。

### 3. 分发内容

公开仓库可以包含：

- 源代码、测试、评测脚本和文档。
- `configs/` 中的非密钥默认配置。
- `evaluation/` 中的问题集、标注规范和可公开脚本。
- `LICENSE`、README 和 ADR。

公开仓库不得包含：

- `data/` 下的数据库、下载文件、解析文本和缓存。
- `reports/` 下的运行结果。
- `.env`、API key、Cookie、Authorization header 或机构凭据。
- 本机绝对路径、IDE 配置和 `.venv/`。

### 4. 许可证

- 采用 MIT License，文件为根目录 `LICENSE`。
- 如果作者要求更严格的专利条款，可在首次公开发布前改为 Apache-2.0；发布后变更必须保留旧版本历史。

### 5. GitHub 发布边界

- 创建远程仓库、首次 push、添加 GitHub Actions 或发布包都属于公开发布，必须由用户明确确认。
- 发布前必须运行完整验证，并检查暂存文件不包含密钥、数据库和本机路径。
- v1 不把 CI/CD 作为运行依赖；是否添加 GitHub Actions 单独决策。

## 后果

正面：

- 其他用户可以用统一命令安装和运行。
- 代码和数据边界清晰，降低误提交科研数据的风险。
- Windows 开发环境与 Linux/macOS 使用环境可以共存。

负面：

- 需要维护锁文件和跨平台测试。
- 某些平台特有能力需要封装，不能直接写进核心逻辑。
- 公开发布前需要额外做许可证、密钥和数据审计。

## 备选方案

1. 只提供 Windows 运行说明：限制用户范围，拒绝。
2. 提交 `.venv` 或完整本地数据：不可复现、体积大且可能泄露数据，拒绝。
3. 不提交锁文件：用户可能获得不同依赖版本，拒绝。
4. 默认使用 GPL：约束更强，但与本项目希望便于教学和二次开发的定位不符；当前不采用。

## 约束

- 本 ADR 已接受；MIT License 已确认。创建远程仓库、push 和公开发布仍需单独确认。
- 任何公开发布前必须运行 `python scripts/check_docs.py`、Ruff、mypy 和 pytest。
- 任何 CI/CD、远程仓库或发布流程改动都必须遵守 `AGENTS.md` 红线。