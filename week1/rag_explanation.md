# RAG（检索增强生成）脚本解析：为什么成功？如何成功？

## 一、什么是 RAG？

RAG（Retrieval-Augmented Generation，检索增强生成）是一种将**外部知识检索**与**大语言模型生成**相结合的技术范式。其核心思想是：

> 在向 LLM 提问之前，先从知识库中检索出与问题相关的文档片段，将其作为上下文注入到 Prompt 中，使模型能够基于**真实、具体的信息**来生成回答，而非仅依赖模型自身的训练数据。

## 二、脚本整体架构

整个 `rag.py` 的执行流程可以分为 5 个阶段：

```
加载语料库 → 检索上下文 → 构造 Prompt → 调用 LLM → 验证输出
```

### 流程图

```
┌─────────────────────┐
│  api_docs.txt 文件   │  ← 外部知识库（语料库）
└─────────┬───────────┘
          │ load_corpus_from_files()
          ▼
┌─────────────────────┐
│     CORPUS 列表      │  ← 内存中的文档集合
└─────────┬───────────┘
          │ YOUR_CONTEXT_PROVIDER()
          ▼
┌─────────────────────┐
│   相关上下文文档      │  ← 检索出的相关文档子集
└─────────┬───────────┘
          │ make_user_prompt()
          ▼
┌─────────────────────┐
│  System Prompt       │  ← YOUR_SYSTEM_PROMPT（角色与约束）
│  +                   │
│  User Prompt         │  ← 上下文 + 任务要求
└─────────┬───────────┘
          │ ollama chat (llama3.1:8b)
          ▼
┌─────────────────────┐
│   模型生成的代码      │
└─────────┬───────────┘
          │ extract_code_block() + 片段匹配
          ▼
┌─────────────────────┐
│  SUCCESS / FAIL      │
└─────────────────────┘
```

## 三、我们填写了什么？

脚本中有两处需要完成的 TODO：

### 3.1 `YOUR_SYSTEM_PROMPT` — 系统提示词

```python
YOUR_SYSTEM_PROMPT = (
    "You are a Python developer. Generate code strictly based on the provided context documentation. "
    "Use only the Base URL, endpoints, and authentication method described in the context. "
    "Do not invent or assume any details not present in the context. "
    "Return your answer as a single fenced Python code block."
)
```

**设计意图：**

| 提示词片段 | 目的 |
|---|---|
| "You are a Python developer" | 设定角色，让模型以开发者视角回答 |
| "strictly based on the provided context documentation" | **核心约束**：强制模型只使用我们提供的上下文信息 |
| "Use only the Base URL, endpoints, and authentication method described in the context" | 明确指出需要从上下文中提取哪些具体信息 |
| "Do not invent or assume any details not present in the context" | 防止模型"幻觉"，避免编造不存在的 API 细节 |
| "Return your answer as a single fenced Python code block" | 约束输出格式，便于后续用正则提取代码 |

### 3.2 `YOUR_CONTEXT_PROVIDER` — 上下文检索函数

```python
def YOUR_CONTEXT_PROVIDER(corpus: List[str]) -> List[str]:
    """Return all available API documentation as context."""
    return corpus
```

**设计意图：**

- 本例中语料库只有一篇文档（`api_docs.txt`），内容简短（15行），直接全部返回即可。
- 在真实 RAG 系统中，这里会使用向量相似度搜索、BM25 等算法从海量文档中检索出最相关的 Top-K 片段。

## 四、为什么成功？— 逐步分析

### 4.1 上下文注入是关键

API 文档 `api_docs.txt` 提供了以下关键信息：

| 信息 | 文档内容 | 对应的必需代码片段 |
|---|---|---|
| Base URL | `https://api.example.com/v1` | `/users/` |
| 认证方式 | `X-API-Key: <your key>` | `X-API-Key` |
| 端点 | `GET /users/{id}` | `requests.get`, `/users/` |
| 响应格式 | `{"id": <string>, "name": <string>}` | `return` (提取 name 字段) |

`YOUR_CONTEXT_PROVIDER` 将这份文档完整地传入了 `make_user_prompt`，使其成为 Prompt 中 `Context` 部分的内容。

### 4.2 Prompt 最终形态

经过 `make_user_prompt` 组装后，发送给模型的完整用户提示词如下：

```
Context (use ONLY this information):
- API Reference

Base URL: https://api.example.com/v1

Authentication:
  Provide header X-API-Key: <your key>

Endpoints:
  GET /users/{id}
    - Returns 200 with JSON: {"id": <string>, "name": <string>}

Task: Write a Python function `fetch_user_name(user_id: str, api_key: str) -> str`
that calls the documented API to fetch a user by id and returns only the user's
name as a string.

Requirements:
- Use the documented Base URL and endpoint.
- Send the documented authentication header.
- Raise for non-200 responses.
- Return only the user's name string.

Output: A single fenced Python code block with the function and necessary imports.
```

### 4.3 模型生成的代码

```python
import requests

def fetch_user_name(user_id: str, api_key: str) -> str:
    url = f"https://api.example.com/v1/users/{user_id}"
    headers = {"X-API-Key": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise requests.exceptions.RequestException(
            f"Failed to fetch user: {response.text}"
        )
    data = response.json()
    return data["name"]
```

### 4.4 验证通过的原因

脚本通过检查 5 个必需代码片段来验证生成质量：

| 必需片段 | 生成代码中的对应部分 | 来源 |
|---|---|---|
| `def fetch_user_name(` | `def fetch_user_name(user_id: str, api_key: str) -> str:` | 任务描述中的函数签名 |
| `requests.get` | `requests.get(url, headers=headers)` | 文档中 `GET` 方法 → 模型选择 `requests.get` |
| `/users/` | `f"https://api.example.com/v1/users/{user_id}"` | 文档中的 Base URL + 端点路径 |
| `X-API-Key` | `{"X-API-Key": api_key}` | 文档中的认证方式 |
| `return` | `return data["name"]` | 文档中响应格式含 `name` 字段 |

**5 个片段全部命中，第 1 次运行即通过，输出 `SUCCESS`。**

## 五、对比：没有上下文时会怎样？

如果 `YOUR_CONTEXT_PROVIDER` 返回空列表 `[]`（即不提供任何上下文），Prompt 中的 Context 部分会变成：

```
Context (use ONLY this information):
(no context provided)
```

此时模型只能依赖自身训练数据"猜测" API 细节，可能出现的问题：

| 问题 | 说明 |
|---|---|
| URL 错误 | 可能编造 `https://api.users.com` 等不存在的地址 |
| 认证方式错误 | 可能使用 `Authorization: Bearer` 而非 `X-API-Key` |
| 端点路径错误 | 可能使用 `/api/users/` 而非 `/users/{id}` |
| 响应解析错误 | 不知道返回的 JSON 结构，无法正确提取 `name` 字段 |

**这正是 RAG 的核心价值：通过注入外部知识，消除模型的信息盲区，确保生成内容的准确性。**

## 六、总结

```
成功 = 正确的上下文检索 + 精准的系统提示词 + 结构化的用户提示词
```

| 组件 | 作用 | 我们的实现 |
|---|---|---|
| `YOUR_CONTEXT_PROVIDER` | 将相关文档从知识库中检索出来 | 返回完整语料库 `corpus` |
| `YOUR_SYSTEM_PROMPT` | 约束模型行为：只用上下文、不编造、格式规范 | 角色设定 + 严格约束 + 格式要求 |
| `make_user_prompt` | 将上下文和任务组装为结构化 Prompt | 脚本已提供（无需修改） |
| `extract_code_block` | 从模型输出中提取代码块 | 脚本已提供（无需修改） |
| 片段验证 | 检查生成代码是否包含关键 API 细节 | 脚本已提供（无需修改） |

RAG 的本质是**让模型"开卷考试"**——不是考验模型记住了多少知识，而是考验它能否正确理解并运用我们提供的参考资料。在本例中，我们提供了完整的 API 文档作为"参考资料"，模型准确地从中提取了所有必要信息，一次性生成了正确的代码。
