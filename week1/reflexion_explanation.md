# Reflexion（反思）提示技术详解

## 一、什么是 Reflexion？

Reflexion 是一种提示工程技术，其核心思想是：**让 LLM 在生成结果后，接收外部反馈（如测试结果），然后基于反馈对自身输出进行"反思"和修正**。

这类似于人类的学习过程——做错题后查看错误原因，再重新作答。与一次性生成（one-shot generation）不同，Reflexion 引入了一个显式的**"评估 → 反馈 → 改进"**闭环。

## 二、脚本整体流程

`reflexion.py` 的任务是让 LLM 生成一个密码验证函数 `is_valid_password`。整个流程分为两大阶段：

```
┌─────────────────────────────────────────────────────────┐
│                   阶段一：初始生成                         │
│                                                         │
│  SYSTEM_PROMPT ──► LLM ──► 初始代码 ──► 测试评估         │
│                                           │              │
│                                    通过？──┤              │
│                                    是 → 结束（成功）      │
│                                    否 ↓                  │
│                                                         │
│                   阶段二：反思迭代                         │
│                                                         │
│  REFLEXION_PROMPT                                       │
│       +                                                 │
│  上次代码 + 失败信息 ──► LLM ──► 改进代码 ──► 再次测试    │
│                                                │        │
│                                         通过？──┤        │
│                                         是 → 结束（成功） │
│                                         否 → 结束（失败） │
└─────────────────────────────────────────────────────────┘
```

## 三、逐模块解析

### 3.1 系统提示词 `SYSTEM_PROMPT`（第 11-15 行）

```python
SYSTEM_PROMPT = """
You are a coding assistant. Output ONLY a single fenced Python code block that defines
the function is_valid_password(password: str) -> bool. No prose or comments.
Keep the implementation minimal.
"""
```

这是初始生成阶段的系统提示词，要求模型：
- 角色：编码助手
- 输出格式：仅输出一个 Python 代码块
- 目标函数：`is_valid_password(password: str) -> bool`
- 约束：不要多余文字，保持简洁

### 3.2 测试用例 `TEST_CASES`（第 30-36 行）

```python
SPECIALS = set("!@#$%^&*()-_")
TEST_CASES = [
    ("Password1!", True),       # 合法密码：大写 + 小写 + 数字 + 特殊字符
    ("password1!", False),      # 缺少大写字母
    ("Password!", False),       # 缺少数字
    ("Password1", False),       # 缺少特殊字符
]
```

这是**外部评估器**——Reflexion 的关键组件。它提供客观的对错判断，而不依赖模型自身判断。
密码需要同时满足：包含大写字母、小写字母、数字、特殊字符，长度 ≥ 8。

### 3.3 代码提取 `extract_code_block`（第 39-46 行）

从 LLM 的回复中用正则提取 `` ```python ... ``` `` 代码块。因为模型可能返回带有 markdown 格式的回复，需要把纯代码部分抽取出来。

### 3.4 动态加载 `load_function_from_code`（第 49-55 行）

通过 `exec()` 执行模型生成的代码字符串，并从命名空间中取出 `is_valid_password` 函数。这让我们能直接调用模型生成的函数进行测试。

### 3.5 评估函数 `evaluate_function`（第 58-87 行）

对生成的 `is_valid_password` 函数逐一运行测试用例：
- 如果某个测试的结果与预期不符，会生成**诊断信息**，指出具体缺少了哪些检查（如"missing uppercase"）
- 返回 `(是否全部通过, 失败列表)`

**诊断信息是 Reflexion 的核心**——它让模型不仅知道"哪个测试失败了"，还知道"为什么失败了"。

### 3.6 初始生成 `generate_initial_function`（第 90-99 行）

向 Ollama 本地运行的 `llama3.1:8b` 发送请求，用 `SYSTEM_PROMPT` 指导模型生成初始实现。温度设为 0.2（较低随机性）。

### 3.7 反思提示词 `YOUR_REFLEXION_PROMPT`（第 18-26 行）【已完成的 TODO】

```python
YOUR_REFLEXION_PROMPT = """
You are a coding assistant that improves Python code based on test feedback.
You will receive a previous implementation of is_valid_password(password: str) -> bool
along with a list of failing test cases and their diagnostics.

Analyze the failures carefully, identify what checks are missing or incorrect,
and output ONLY a single fenced Python code block with the corrected implementation.
No prose or comments. Keep the implementation minimal.
"""
```

与初始提示词不同，反思提示词明确告诉模型：
1. 你的任务是**改进**代码，而非从零开始
2. 你会收到上一次的实现和失败信息
3. 要**分析失败原因**，找出缺失或错误的检查
4. 依然只输出代码，不要多余文字

### 3.8 构建反思上下文 `your_build_reflexion_context`（第 102-113 行）【已完成的 TODO】

```python
def your_build_reflexion_context(prev_code: str, failures: List[str]) -> str:
    failure_details = "\n".join(f"- {f}" for f in failures)
    return (
        f"Here is my previous implementation:\n"
        f"```python\n{prev_code}\n```\n\n"
        f"It failed the following test cases:\n{failure_details}\n\n"
        f"Please fix the implementation so that all test cases pass."
    )
```

这个函数负责将**上一次代码**和**失败的测试详情**拼装成结构化的用户消息。模型收到的消息大致如下：

> Here is my previous implementation:
> ```python
> def is_valid_password(password: str) -> bool:
>     return len(password) >= 8 and any(c.isalpha() ...) ...
> ```
>
> It failed the following test cases:
> - Input: password1! → expected False, got True. Failing checks: missing uppercase
> - Input: Password1 → expected False, got True. Failing checks: missing special
>
> Please fix the implementation so that all test cases pass.

### 3.9 执行反思 `apply_reflexion`（第 116-132 行）

将 `YOUR_REFLEXION_PROMPT`（系统提示）和 `your_build_reflexion_context` 构建的上下文（用户消息）一起发送给模型，获取改进后的代码。

### 3.10 主流程 `run_reflexion_flow`（第 135-163 行）

编排整个流程：生成 → 评估 → （若失败）反思 → 再评估 → 输出最终结果。

## 四、为什么之前跑不通？

在填写 TODO 之前，两个关键部分都是空字符串：

| 组件 | 填写前 | 后果 |
|------|--------|------|
| `YOUR_REFLEXION_PROMPT` | `""` | 模型没有反思角色指引，不知道自己该修复代码 |
| `your_build_reflexion_context` | `return ""` | 模型收到的用户消息为空，不知道之前的代码是什么、哪些测试失败了 |

两者都为空时，模型实际收到的是：
- 系统提示：（空）
- 用户消息：（空）

模型不知道要做什么，回复了一段闲聊文字（"It seems like you were about to ask a question..."），不是有效的 Python 代码。当脚本尝试用 `exec()` 执行这段文字时，自然触发了 `SyntaxError`。

## 五、为什么填写后能跑通？

填写后，反思步骤的完整信息链条被建立起来：

```
反思系统提示词（YOUR_REFLEXION_PROMPT）
    → 告诉模型："你是代码改进助手，要根据测试反馈修复代码"

反思上下文（your_build_reflexion_context 的返回值）
    → 告诉模型：
      1. 上一次的代码是什么
      2. 哪些测试失败了
      3. 失败的具体原因（如 missing uppercase）
      4. 请修复
```

模型拥有了足够的上下文，因此能够：
1. 理解自己的角色（修复代码）
2. 看到之前有缺陷的实现
3. 根据诊断信息（如"missing uppercase"、"missing special"）定位缺陷
4. 输出格式正确的改进代码

改进后的代码能被 `extract_code_block` 正确提取、被 `exec()` 正确执行、被 `evaluate_function` 正确评估——流程顺利跑通。

## 六、实际运行结果分析

在我们的运行中：

**初始生成：**
```python
def is_valid_password(password: str) -> bool:
    return len(password) >= 8 and any(c.isalpha() for c in password) and any(c.isdigit() for c in password)
```
只检查了长度、是否有字母、是否有数字。缺少大写字母检查和特殊字符检查，2 个测试失败。

**反思改进后：**
```python
def is_valid_password(password: str) -> bool:
    return (len(password) >= 8
            and any(c.isalpha() for c in password)
            and any(c.isdigit() for c in password)
            and any(not c.isalnum() for c in password))
```
模型增加了特殊字符检查（`not c.isalnum()`），但仍未区分大小写，还剩 1 个测试失败。

这说明 `llama3.1:8b` 作为较小模型，一轮反思可能不足以完全修复所有问题。但反思机制本身是有效的——从 2 个失败减少到 1 个失败，代码质量确实得到了提升。

## 七、Reflexion 的核心思想总结

| 要素 | 说明 |
|------|------|
| **外部评估器** | 不依赖模型自身判断，用客观的测试用例来评估输出质量 |
| **结构化反馈** | 不仅告诉模型"错了"，还告诉"错在哪里、为什么错" |
| **迭代改进** | 将反馈注入新一轮对话，让模型有机会修正 |
| **提示词分离** | 初始生成和反思修复使用不同的系统提示词，各司其职 |

Reflexion 体现的是一种**"生成-评估-反馈-改进"的闭环范式**，是让 LLM 从自身错误中学习的实用技术。
