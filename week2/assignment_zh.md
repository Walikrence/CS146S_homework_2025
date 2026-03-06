# 第二周 – 行动项提取器

本周，我们将在一个最小化的 FastAPI + SQLite 应用基础上进行扩展，实现将自由格式的笔记转换为枚举式行动项的功能。

***建议在开始之前通读整份文档。***

提示：预览此 Markdown 文件
- Mac 用户按 `Command (⌘) + Shift + V`
- Windows/Linux 用户按 `Ctrl + Shift + V`


## 开始之前

### Cursor 设置
按照以下步骤设置 Cursor 并打开你的项目：
1. 兑换 Cursor Pro 免费一年资格：https://cursor.com/students
2. 下载 Cursor：https://cursor.com/download
3. 启用 Cursor 命令行工具：打开 Cursor，Mac 用户按 `Command (⌘) + Shift + P`（非 Mac 用户按 `Ctrl + Shift + P`）打开命令面板，输入 `Shell Command: Install 'cursor' command`，选择并回车。
4. 打开新的终端窗口，导航到项目根目录，运行：`cursor .`

### 当前应用
以下是启动当前初始应用的步骤：
1. 激活你的 conda 环境：
```
conda activate cs146s 
```
2. 在项目根目录下运行服务器：
```
poetry run uvicorn week2.app.main:app --reload
```
3. 打开浏览器，访问 http://127.0.0.1:8000/
4. 熟悉应用的当前状态。确保你能够成功输入笔记并生成提取的行动项清单。

## 练习
对于每个练习，使用 Cursor 帮助你实现对当前行动项提取器应用的指定改进。

在完成作业的过程中，请使用 `writeup.md` 记录你的进展。务必包含你使用的提示词（prompt），以及你或 Cursor 所做的更改。我们将根据报告内容进行评分。同时请在代码中添加注释以记录你的更改。

### TODO 1：搭建新功能脚手架

分析 `week2/app/services/extract.py` 中现有的 `extract_action_items()` 函数，该函数目前使用预定义的启发式规则来提取行动项。

你的任务是实现一个 **基于 LLM 的**替代方案 `extract_action_items_llm()`，利用 Ollama 通过大语言模型来执行行动项提取。

一些提示：
- 要生成结构化输出（即 JSON 字符串数组），请参考此文档：https://ollama.com/blog/structured-outputs
- 要浏览可用的 Ollama 模型，请参考此文档：https://ollama.com/library 。注意较大的模型会占用更多资源，建议从小模型开始。拉取并运行模型：`ollama run {模型名称}`

### TODO 2：添加单元测试

在 `week2/tests/test_extract.py` 中为 `extract_action_items_llm()` 编写单元测试，覆盖多种输入情况（例如：项目符号列表、关键词前缀行、空输入等）。

### TODO 3：重构现有代码以提升可读性

对后端代码进行重构，重点关注以下方面：明确定义的 API 契约/模式（schema）、数据库层清理、应用生命周期/配置管理、错误处理。

### TODO 4：使用 Agent 模式自动化小型任务

1. 将基于 LLM 的提取功能集成为一个新的 API 端点。更新前端，添加一个"LLM 提取"按钮，点击后通过新端点触发提取流程。

2. 暴露一个最终端点用于获取所有笔记。更新前端，添加一个"列出笔记"按钮，点击后获取并展示所有笔记。

### TODO 5：从代码库生成 README 文件

***学习目标：***
*学生了解 AI 如何审视代码库并自动生成文档，展示 Cursor 解析代码上下文并将其转化为人类可读形式的能力。*

使用 Cursor 分析当前代码库并生成结构良好的 `README.md` 文件。README 至少应包含：
- 项目简要概述
- 如何设置和运行项目
- API 端点及功能说明
- 运行测试套件的说明

## 提交物
根据提供的说明填写 `week2/writeup.md`。确保所有更改都记录在你的代码库中。

## 评分标准（总分 100 分）
- 第 1-5 部分每部分 20 分（生成的代码 10 分，提示词 10 分）。
