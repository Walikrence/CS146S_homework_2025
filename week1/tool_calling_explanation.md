# Tool Calling（工具调用）脚本解析：为什么成功？如何成功？

## 一、什么是 Tool Calling？

Tool Calling（工具调用）是一种让 LLM **不仅能生成文本，还能结构化地调用外部函数/工具**的提示工程技术。其核心流程是：

> 在系统提示词中告诉模型有哪些可用工具及其调用格式，然后让模型根据用户指令，输出一个**结构化的 JSON 调用指令**，而非自然语言回答。程序端解析该 JSON 并执行对应的函数，获得真实结果。

这使 LLM 的能力从"纯文本生成"扩展到了"与外部系统交互"——查数据库、调 API、执行代码分析等。

## 二、脚本整体架构

整个 `tool_calling.py` 的执行流程可以分为 4 个阶段：

```
定义工具 → 提示模型生成调用指令 → 解析并执行 → 验证结果
```

### 流程图

```
┌──────────────────────────────────┐
│     工具定义与注册                 │
│  output_every_func_return_type   │
│  → 注册到 TOOL_REGISTRY          │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│     模型交互                      │
│  YOUR_SYSTEM_PROMPT（工具描述     │
│  + 输出格式约束）                 │
│  + "Call the tool now."          │
│  → 发送给 llama3.1:8b            │
└──────────────┬───────────────────┘
               │ 模型输出 JSON
               ▼
┌──────────────────────────────────┐
│     解析工具调用                   │
│  extract_tool_call()             │
│  → {"tool": "...", "args": {...}}│
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│     执行工具                      │
│  execute_tool_call()             │
│  → 查 TOOL_REGISTRY → 调用函数   │
│  → 返回实际结果                   │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│     验证                          │
│  actual == expected ?            │
│  → SUCCESS / 重试（最多 3 次）    │
└──────────────────────────────────┘
```

## 三、逐模块解析

### 3.1 工具实现——"执行器"

脚本定义了一个可供 LLM 调用的工具函数：

```python
def output_every_func_return_type(file_path: str = None) -> str:
```

它的工作原理：
1. 使用 Python 标准库 `ast` 解析指定文件的源码为抽象语法树
2. 遍历所有顶层函数定义（`ast.FunctionDef`）
3. 提取每个函数的名称和返回类型注解
4. 按函数名字母排序，以 `name: return_type` 格式逐行返回

脚本还定义了两个示例函数 `add` 和 `greet`，确保分析时有多种返回类型可展示。

所有可调用工具统一注册在 `TOOL_REGISTRY` 字典中：

```python
TOOL_REGISTRY: Dict[str, Callable[..., str]] = {
    "output_every_func_return_type": output_every_func_return_type,
}
```

这种注册机制使得程序可以通过**工具名字符串**动态查找并执行对应函数。

### 3.2 `YOUR_SYSTEM_PROMPT` — 系统提示词【已完成的 TODO】

```python
YOUR_SYSTEM_PROMPT = """You are a tool-calling assistant. You have access to the following tool:

Tool name: output_every_func_return_type
Description: Analyzes a Python source file and returns a newline-delimited list of every top-level function's name and its return type annotation, formatted as "name: return_type", sorted alphabetically.
Parameters:
  - file_path (string, optional): Path to the Python file to analyze. Defaults to the current script if omitted or empty.

When the user asks you to call a tool, respond with ONLY a single JSON object (no markdown, no explanation, no extra text) in this exact format:
{"tool": "<tool_name>", "args": {<arguments>}}

Now call output_every_func_return_type on the current script (leave file_path empty to use the default)."""
```

**设计意图——逐句拆解：**

| 提示词片段 | 目的 |
|---|---|
| "You are a tool-calling assistant" | 设定角色：工具调用助手，而非通用聊天机器人 |
| "You have access to the following tool: ..." | **工具声明**：告知模型有哪些工具可用 |
| "Tool name / Description / Parameters" | **工具规格**：名称、功能描述、参数定义，模型据此决定如何构造调用 |
| "Defaults to the current script if omitted or empty" | 引导模型省略 `file_path` 或留空，触发默认值逻辑 |
| "respond with ONLY a single JSON object" | **格式约束**：严格限制输出只能是 JSON，防止夹带自然语言导致解析失败 |
| `{"tool": "<tool_name>", "args": {<arguments>}}` | **格式模板**：给出精确的 JSON 结构，降低模型输出偏差 |
| "no markdown, no explanation, no extra text" | **负面约束**：明确禁止 markdown 代码块包裹、解释文字等干扰项 |
| "Now call output_every_func_return_type on the current script" | **任务指令**：直接告诉模型要调用哪个工具、目标是什么 |

### 3.3 模型交互 `run_model_for_tool_call`

```python
def run_model_for_tool_call(system_prompt: str) -> Dict[str, Any]:
    response = chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Call the tool now."},
        ],
        options={"temperature": 0.3, "num_ctx": 8192},
    )
    content = response.message.content
    return extract_tool_call(content)
```

- 使用 Ollama 本地运行的 `llama3.1:8b` 模型
- 系统消息携带完整的工具描述和格式约束
- 用户消息 `"Call the tool now."` 触发模型输出工具调用
- 温度 0.3（较低随机性）确保输出稳定

### 3.4 JSON 解析 `extract_tool_call`

从模型输出中解析 JSON 对象。即使模型用 `` ```json ... ``` `` 代码块包裹了 JSON（小模型常见行为），也能做兼容处理。

### 3.5 工具执行 `execute_tool_call`

根据解析出的 JSON：
1. 通过 `tool` 字段在 `TOOL_REGISTRY` 中查找对应函数
2. 处理 `file_path` 参数：若未传或为空，默认使用当前脚本路径（`__file__`）
3. 用 `**args` 展开参数并调用函数

### 3.6 验证逻辑 `test_your_prompt`

1. 先调用 `compute_expected_output()` 直接执行工具获取**基准答案**
2. 最多尝试 3 次让模型生成工具调用
3. 每次将模型触发的工具执行结果与基准答案做**字符串精确比较**
4. 完全一致则判定成功

## 四、为什么之前跑不通？

在填写 TODO 之前，`YOUR_SYSTEM_PROMPT` 是空字符串 `""`。此时模型实际收到的消息是：

| 角色 | 内容 |
|---|---|
| system | （空） |
| user | "Call the tool now." |

模型不知道：
- 有哪些工具可用
- 工具调用的 JSON 格式是什么
- 要对哪个文件执行什么操作

它会把 "Call the tool now." 当成一句普通的聊天指令，回复自然语言文本。`extract_tool_call` 尝试用 `json.loads()` 解析这段文本时必然抛出 `JSONDecodeError`，导致测试失败。

## 五、为什么填写后能成功？

填写后，完整的信息传递链条被建立：

```
系统提示词（YOUR_SYSTEM_PROMPT）
  ├── 工具声明：告诉模型 "你有一个工具叫 output_every_func_return_type"
  ├── 工具规格：描述功能、参数、默认值
  ├── 格式约束：必须输出 {"tool": "...", "args": {...}} 格式的 JSON
  └── 任务指令：对当前脚本调用此工具

用户消息："Call the tool now."
  └── 触发模型立即执行
```

模型据此生成的输出（预期）：

```json
{"tool": "output_every_func_return_type", "args": {}}
```

程序端处理流程：
1. `extract_tool_call` 成功将其解析为 Python 字典
2. `execute_tool_call` 在 `TOOL_REGISTRY` 中找到对应函数
3. 因 `args` 中无 `file_path`，自动补充为 `__file__`（当前脚本）
4. 工具执行，用 `ast` 分析当前脚本，返回所有函数的返回类型
5. 该结果与 `compute_expected_output()` 的基准答案一致 → **SUCCESS**

## 六、预期输出示例

对 `tool_calling.py` 自身执行分析，基准答案为（按字母排序）：

```
_annotation_to_str: str
_list_function_return_types: List[Tuple[str, str]]
add: int
compute_expected_output: str
execute_tool_call: str
extract_tool_call: Dict[str, Any]
greet: str
output_every_func_return_type: str
resolve_path: str
run_model_for_tool_call: Dict[str, Any]
test_your_prompt: bool
```

模型触发的工具调用执行后得到相同结果，验证通过。

## 七、System Prompt 设计的关键原则

本例的系统提示词体现了 Tool Calling 场景下提示词设计的几个核心原则：

### 7.1 工具描述要完整精确

模型需要知道：
- **工具名称**：用于构造 `"tool"` 字段
- **功能描述**：理解工具做什么，决定何时使用
- **参数规格**：知道传什么参数、哪些可选、默认值是什么

缺少任何一项，模型都可能构造出错误的调用指令。

### 7.2 输出格式要严格限定

LLM 天性倾向于生成自然语言解释。在 Tool Calling 场景中，必须通过明确的约束（"respond with ONLY a single JSON object"）和反面限制（"no markdown, no explanation, no extra text"）来抑制这种倾向。

### 7.3 提供格式模板

给出 `{"tool": "<tool_name>", "args": {<arguments>}}` 这样的模板，比纯文字描述更直观，大幅降低模型输出格式偏差的概率。

### 7.4 任务意图要清晰

不能只描述工具，还要明确告诉模型**现在就调用它**，以及**调用的目标是什么**（当前脚本）。

## 八、Tool Calling 的核心思想总结

| 要素 | 说明 |
|---|---|
| **工具注册表** | 将可调用函数按名称注册，支持动态查找和执行 |
| **结构化输出** | 要求模型输出 JSON 而非自然语言，使程序能可靠解析 |
| **提示词即接口文档** | 系统提示词相当于"API 文档"——告诉模型有什么工具、怎么调用 |
| **解耦生成与执行** | 模型只负责"决定调用什么"，实际执行由程序端完成 |
| **容错与重试** | 小模型可能偶尔输出格式不符，通过多次重试（本例 3 次）提高成功率 |

Tool Calling 的本质是**让 LLM 成为"调度员"**——它不直接执行操作，而是理解用户意图后，生成结构化的调用指令，由程序端的执行器去完成真正的工作。这种模式是构建 AI Agent、函数调用型聊天机器人、自动化工作流的基础能力。
