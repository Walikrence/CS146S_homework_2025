# 第二周 报告
提示：预览此 Markdown 文件
- Mac 用户按 `Command (⌘) + Shift + V`
- Windows/Linux 用户按 `Ctrl + Shift + V`

## 说明

请填写本文件中所有的 `TODO` 项。

## 提交信息

姓名：**Jiaxiang** \
SUNet ID：**jiaxiang** \
参考引用：Ollama 结构化输出文档 https://ollama.com/blog/structured-outputs ；FastAPI 官方文档 https://fastapi.tiangolo.com/ ；Pydantic V2 文档 https://docs.pydantic.dev/

本次作业大约花费了 **3** 小时。


## 你的回答
对于每个练习，请包含你用于生成答案的提示词（prompt），以及生成结果所在的位置。请务必在代码中添加清晰的注释，标注哪些部分是生成的。

### 练习 1：搭建新功能脚手架
提示词：
```
分析 week2/app/services/extract.py 中现有的 extract_action_items() 函数。
实现一个基于 LLM 的替代方案 extract_action_items_llm()，利用 Ollama 通过大语言模型来执行行动项提取。
使用 Pydantic 模型配合 Ollama 的 format 参数实现结构化 JSON 输出。
模型名称通过环境变量 OLLAMA_MODEL 配置，默认使用 llama3.2。
空输入直接返回空列表，异常时抛出 RuntimeError。
``` 

生成的代码片段：
```
week2/app/services/extract.py（第 9 行、第 93-129 行）：
  - 第 9 行：新增 from pydantic import BaseModel
  - 第 93 行：OLLAMA_MODEL 环境变量配置
  - 第 96-97 行：ActionItems Pydantic 模型，定义结构化输出 schema
  - 第 100-128 行：extract_action_items_llm() 函数，使用 Ollama chat API，
    通过 format=ActionItems.model_json_schema() 强制结构化输出，
    Pydantic model_validate_json() 解析并验证返回结果
```

### 练习 2：添加单元测试
提示词：
```
在 week2/tests/test_extract.py 中为 extract_action_items_llm() 编写单元测试。
使用 unittest.mock.patch 模拟 Ollama chat 调用，避免依赖真实的 LLM 服务。
覆盖以下场景：项目符号列表、关键词前缀行（todo:/action:）、空输入、
纯空白输入、无行动项的普通文本、自由格式段落、Ollama 连接异常。
``` 

生成的代码片段：
```
week2/tests/test_extract.py（全文，第 1-119 行）：
  - 第 1-5 行：导入 pytest、unittest.mock、提取函数
  - 第 10-22 行：保留原有 test_extract_bullets_and_checkboxes 测试
  - 第 27-32 行：_mock_chat_response() 辅助函数，构建模拟的 Ollama 响应
  - 第 35-53 行：test_llm_extract_bullet_list — 测试项目符号列表输入
  - 第 56-70 行：test_llm_extract_keyword_prefixed — 测试 todo:/action: 前缀
  - 第 73-77 行：test_llm_extract_empty_input — 测试空字符串输入
  - 第 80-84 行：test_llm_extract_whitespace_only — 测试纯空白输入
  - 第 87-93 行：test_llm_extract_no_action_items — 测试无行动项的文本
  - 第 96-111 行：test_llm_extract_freeform_paragraph — 测试自由格式段落
  - 第 113-118 行：test_llm_extract_raises_on_ollama_error — 测试异常处理
```

### 练习 3：重构现有代码以提升可读性
提示词：
```
对 week2 后端代码进行全面重构，重点关注：
1. API 契约/Schema：创建 Pydantic 模型替代所有路由中的 Dict[str, Any]，
   定义明确的请求和响应类型。
2. 数据库层清理：简化 db.py，使用 executescript 合并建表语句，
   启用 PRAGMA foreign_keys，精简函数实现。
3. 应用生命周期/配置：将 main.py 中模块级的 init_db() 调用替换为
   FastAPI lifespan 上下文管理器，提取 FRONTEND_DIR 常量。
4. 错误处理：在路由中增加适当的异常捕获和 HTTP 错误响应。
``` 

生成/修改的代码片段：
```
week2/app/schemas.py（新建，第 1-54 行）：
  - 第 12-13 行：NoteCreateRequest — 笔记创建请求 schema
  - 第 16-19 行：NoteResponse — 笔记响应 schema
  - 第 24-26 行：ExtractRequest — 提取请求 schema（text + save_note）
  - 第 29-30 行：ActionItemResponse — 行动项响应 schema
  - 第 33-36 行：ExtractResponse — 提取响应 schema
  - 第 39-44 行：ActionItemDetail — 行动项详情 schema
  - 第 47-48 行：MarkDoneRequest — 标记完成请求 schema
  - 第 51-53 行：MarkDoneResponse — 标记完成响应 schema

week2/app/main.py（重写，第 1-35 行）：
  - 第 18-21 行：使用 @asynccontextmanager lifespan 管理 init_db() 生命周期
  - 第 24 行：FastAPI 实例使用 lifespan 参数
  - 第 15 行：FRONTEND_DIR 提取为模块级常量

week2/app/db.py（重构，第 1-99 行）：
  - 第 24 行：启用 PRAGMA foreign_keys = ON
  - 第 30-48 行：使用 executescript 合并建表语句
  - 第 53-80 行：精简 insert_note、list_notes、get_note，使用 conn.execute 替代
    cursor 变量
  - 第 85-99 行：精简 insert_action_items、list_action_items、mark_action_item_done

week2/app/routers/notes.py（重构，第 1-39 行）：
  - 第 10 行：导入 NoteCreateRequest, NoteResponse schema
  - 第 15-21 行：create_note() 使用 Pydantic 模型替代 Dict[str, Any]
  - 第 24-30 行：新增 list_all_notes() 端点（GET /notes）
  - 第 33-38 行：get_single_note() 使用 response_model=NoteResponse

week2/app/routers/action_items.py（重构，第 1-74 行）：
  - 第 10-17 行：导入所有 Pydantic schema
  - 第 23-34 行：extract() 使用 ExtractRequest + ExtractResponse 替代 Dict
  - 第 55-67 行：list_all() 使用 response_model=List[ActionItemDetail]
  - 第 70-73 行：mark_done() 使用 MarkDoneRequest + MarkDoneResponse
```


### 练习 4：使用 Agent 模式自动化小型任务
提示词：
```
在 Cursor Agent 模式下完成以下任务：
1. 将基于 LLM 的提取功能集成为新端点 POST /action-items/extract-llm，
   复用 ExtractRequest/ExtractResponse schema，调用 extract_action_items_llm()，
   Ollama 异常时返回 HTTP 502。
2. 暴露 GET /notes 端点获取所有笔记。
3. 更新前端 index.html：新增 "Extract LLM" 按钮调用 /action-items/extract-llm，
   新增 "List Notes" 按钮调用 GET /notes 并展示笔记卡片列表。
   提取逻辑抽取为 doExtract(endpoint) 公共函数避免重复代码。
``` 

生成的代码片段：
```
week2/app/routers/action_items.py（第 37-52 行）：
  - 第 37-52 行：extract_llm() 端点 — POST /action-items/extract-llm，
    调用 extract_action_items_llm()，RuntimeError 时返回 HTTP 502

week2/app/routers/notes.py（第 24-30 行）：
  - 第 24-30 行：list_all_notes() 端点 — GET /notes，返回所有笔记列表

week2/frontend/index.html（第 1-114 行）：
  - 第 31 行：新增 "Extract LLM" 按钮
  - 第 32 行：新增 "List Notes" 按钮
  - 第 37-40 行：新增笔记展示区域 #notes-section
  - 第 46-82 行：doExtract(endpoint) 公共提取函数，提升错误提示
  - 第 84 行：Extract 按钮绑定 /action-items/extract
  - 第 85 行：Extract LLM 按钮绑定 /action-items/extract-llm
  - 第 87-110 行：List Notes 按钮点击事件，获取并渲染笔记卡片
```


### 练习 5：从代码库生成 README 文件
提示词：
```
分析当前 week2 代码库，生成结构良好的 README.md 文件，包含：
- 项目简要概述
- 项目目录结构
- 前置条件和安装运行说明（conda、Ollama、Poetry）
- 环境变量说明
- 所有 API 端点及功能说明（表格形式）
- 运行测试套件的说明
``` 

生成的代码片段：
```
week2/README.md（新建，全文）：
  - 项目概述：FastAPI + SQLite 行动项提取应用
  - 目录结构：完整的 tree 展示
  - Setup & Run：conda 环境、Ollama 模型拉取、uvicorn 启动命令
  - 环境变量表：OLLAMA_MODEL
  - API 端点表：Notes（3 个）+ Action Items（4 个）
  - 测试说明：poetry run pytest 命令及测试覆盖范围
```


## 提交说明
1. 按 `Command (⌘) + F`（或 `Ctrl + F`）搜索本文件中是否还有未完成的 `TODO`。如果没有搜索结果，恭喜——你已完成所有必填项。
2. 确保所有更改已推送到远程仓库以供评分。
3. 通过 Gradescope 提交。
