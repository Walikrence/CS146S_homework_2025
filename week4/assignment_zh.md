# 第四周 — 自主编程代理的实际应用

> ***建议在开始之前通读整篇文档。***

本周，你的任务是在本仓库中使用以下任意 **Claude Code** 功能组合，构建至少 **2 个自动化工作流**：

- 自定义斜杠命令（提交到 `.claude/commands/*.md`）

- `CLAUDE.md` 文件，用于提供仓库级别的上下文指导

- Claude 子代理（SubAgents，按角色分工的专用代理协同工作）

- 集成到 Claude Code 中的 MCP 服务器

你构建的自动化工作流应当切实改善开发者的工作流程——例如，简化测试、文档编写、代码重构或数据相关任务。随后，你需要利用所创建的自动化工具来扩展 `week4/` 中的初始应用。


## 了解 Claude Code
为深入理解 Claude Code 并探索自动化选项，请阅读以下两份资料：

1. **Claude Code 最佳实践：** [anthropic.com/engineering/claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices)

2. **子代理概述：** [docs.anthropic.com/en/docs/claude-code/sub-agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

## 探索初始应用
一个极简的全栈初始应用，旨在作为 **"开发者的命令中心"**。
- FastAPI 后端 + SQLite（SQLAlchemy）
- 静态前端（无需 Node 工具链）
- 基础测试（pytest）
- Pre-commit 钩子（black + ruff）
- 用于练习代理驱动工作流的任务

以此应用作为你的实验场，测试和运行你构建的 Claude 自动化工具。

### 目录结构

```
backend/                # FastAPI 应用
frontend/               # 由 FastAPI 提供服务的静态前端
data/                   # SQLite 数据库 + 种子数据
docs/                   # 代理驱动工作流的任务文档
```

### 快速开始

1) 激活 conda 环境。

```bash
conda activate cs146s
```

2) （可选）安装 pre-commit 钩子

```bash
pre-commit install
```

3) 运行应用（在 `week4/` 目录下）

```bash
make run
```

4) 打开 `http://localhost:8000` 访问前端界面，打开 `http://localhost:8000/docs` 查看 API 文档。

5) 体验初始应用，熟悉其现有功能。


### 测试
运行测试（在 `week4/` 目录下）
```bash
make test
```

### 代码格式化 / 静态检查
```bash
make format
make lint
```

## 第一部分：构建自动化工具（至少选择 2 项）
熟悉初始应用后，下一步是构建自动化工具来增强或扩展它。以下是你可以选择的几类自动化方案，可自由组合搭配。

在构建自动化工具的过程中，将你的更改记录在 `writeup.md` 文件中。暂时将 *"如何使用自动化工具增强初始应用"* 部分留空——你将在作业的第二部分回来填写。

### A) Claude 自定义斜杠命令
斜杠命令是用于重复性工作流的功能，允许你在 `.claude/commands/` 中创建 Markdown 文件来定义可复用的工作流。Claude 通过 `/` 前缀来暴露这些命令。

- 示例 1：带覆盖率的测试运行器
  - 名称：`tests.md`
  - 意图：运行 `pytest -q backend/tests --maxfail=1 -x`，若通过则继续执行覆盖率检测。
  - 输入：可选的标记或路径。
  - 输出：汇总失败信息并建议下一步操作。
- 示例 2：文档同步
  - 名称：`docs-sync.md`
  - 意图：读取 `/openapi.json`，更新 `docs/API.md`，并列出路由变更。
  - 输出：类似 diff 的摘要和待办事项。
- 示例 3：重构辅助
  - 名称：`refactor-module.md`
  - 意图：重命名模块（例如 `services/extract.py` → `services/parser.py`），更新导入，运行静态检查和测试。
  - 输出：修改文件的清单和验证步骤。

> *提示：保持命令聚焦、使用 `$ARGUMENTS`、优先选择幂等操作。可考虑设置安全工具白名单，并使用无头模式以确保可重复性。*

### B) `CLAUDE.md` 指导文件
`CLAUDE.md` 文件在启动对话时自动读取，允许你提供仓库特定的指令、上下文或指导信息来影响 Claude 的行为。在仓库根目录（以及可选地在 `week4/` 子文件夹中）创建 `CLAUDE.md` 来引导 Claude 的行为。

- 示例 1：代码导航和入口
  - 包含：如何运行应用、路由所在位置（`backend/app/routers`）、测试位置、数据库的种子数据加载方式。
- 示例 2：风格和安全防护
  - 包含：工具链要求（black/ruff）、安全执行的命令、应避免的命令、静态检查/测试门控。
- 示例 3：工作流片段
  - 包含："当被要求添加端点时，先编写一个失败的测试，再实现代码，最后运行 pre-commit。"

> *提示：像迭代提示词一样迭代 `CLAUDE.md`，保持简洁且可操作，记录你希望 Claude 使用的自定义工具和脚本。*

### C) 子代理（按角色分工）

子代理是配置为处理特定任务的专用 AI 助手，拥有独立的系统提示、工具和上下文。设计两个或多个协作代理，每个代理负责单一工作流中的不同步骤。

- 示例 1：TestAgent + CodeAgent
  - 流程：TestAgent 为某项更改编写/更新测试 → CodeAgent 编写代码使测试通过 → TestAgent 进行验证。
- 示例 2：DocsAgent + CodeAgent
  - 流程：CodeAgent 添加新的 API 路由 → DocsAgent 更新 `API.md` 和 `TASKS.md`，并对照 `/openapi.json` 检查偏差。
- 示例 3：DBAgent + RefactorAgent
  - 流程：DBAgent 提出 Schema 变更方案（修改 `data/seed.sql`）→ RefactorAgent 更新模型/Schema/路由并修复静态检查问题。

> *提示：使用清单/草稿板，在角色切换间重置上下文（`/clear`），对于独立任务可并行运行代理。*

## 第二部分：运用你的自动化工具
完成 2 个以上自动化工具的构建后，让我们投入使用！在 `writeup.md` 的 *"如何使用自动化工具增强初始应用"* 部分，描述你如何利用每个自动化工具来改进或扩展应用的功能。

例如：如果你实现了自定义斜杠命令 `/generate-test-cases`，请说明你是如何使用它来与初始应用交互和测试的。


## 交付物
1) 两个或以上的自动化工具，可能包括：
   - `.claude/commands/*.md` 中的斜杠命令
   - `CLAUDE.md` 文件
   - 子代理的提示/配置（文档清晰，附上相关文件/脚本）

2) `week4/` 目录下的 `writeup.md`，需包含：
  - 设计灵感（例如引用最佳实践和/或子代理文档）
  - 每个自动化工具的设计，包括目标、输入/输出、步骤
  - 如何运行（完整命令）、预期输出以及回滚/安全说明
  - 前后对比（即手动工作流 vs. 自动化工作流）
  - 如何使用自动化工具增强初始应用



## 提交说明
1. 确保所有更改已推送到远程仓库以便评分。
2. **确保已将 brentju 和 febielin 添加为你的作业仓库的协作者。**
3. 通过 Gradescope 提交。
