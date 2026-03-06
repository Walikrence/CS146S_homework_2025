# 行动项提取器

一个基于 FastAPI + SQLite 的 Web 应用，可将自由格式的笔记转换为结构化的可操作清单项。同时支持基于启发式规则和 LLM 驱动的两种提取方式。

## 项目结构

```
week2/
├── app/
│   ├── main.py              # FastAPI 入口，使用 lifespan 管理生命周期
│   ├── db.py                # SQLite 数据库访问层
│   ├── schemas.py           # Pydantic 请求/响应模型
│   ├── routers/
│   │   ├── notes.py         # 笔记 CRUD 端点
│   │   └── action_items.py  # 行动项提取与管理端点
│   └── services/
│       └── extract.py       # 启发式 + LLM 提取逻辑
├── frontend/
│   └── index.html           # 单页 HTML 前端
├── tests/
│   └── test_extract.py      # 提取函数的单元测试
└── data/
    └── app.db               # SQLite 数据库（运行时自动创建）
```

## 安装与运行

### 前置条件

- Python 3.10+
- [Conda](https://docs.conda.io/) 并已创建 `cs146s` 环境
- [Ollama](https://ollama.com/) 已安装并运行（用于 LLM 提取）

### 安装与启动

1. 激活 conda 环境：
   ```bash
   conda activate cs146s
   ```

2. 拉取 Ollama 模型（仅首次需要）：
   ```bash
   ollama run llama3.2
   ```

3. 在项目根目录下启动服务器：
   ```bash
   poetry run uvicorn week2.app.main:app --reload
   ```

4. 在浏览器中打开 http://127.0.0.1:8000/

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `OLLAMA_MODEL` | `llama3.2` | 用于 LLM 提取的 Ollama 模型名称 |

## API 端点

### 笔记

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/notes` | 创建新笔记（`{"content": "..."}）` |
| `GET`  | `/notes` | 获取所有已保存的笔记 |
| `GET`  | `/notes/{note_id}` | 根据 ID 获取单条笔记 |

### 行动项

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/action-items/extract` | 使用启发式规则提取行动项 |
| `POST` | `/action-items/extract-llm` | 使用 Ollama LLM 提取行动项 |
| `GET`  | `/action-items` | 获取所有行动项（可选 `?note_id=` 过滤） |
| `POST` | `/action-items/{id}/done` | 切换完成状态（`{"done": true/false}`） |

两个提取端点均接受以下请求体：
```json
{
  "text": "你的笔记内容...",
  "save_note": true
}
```

## 运行测试

在项目根目录下执行：

```bash
poetry run pytest week2/tests/ -v
```

测试套件覆盖：
- 启发式提取（项目符号、复选框、编号列表）
- LLM 提取（模拟 Ollama 调用，覆盖项目符号列表、关键词前缀行、自由格式段落、空输入、异常处理）
