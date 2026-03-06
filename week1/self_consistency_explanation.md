# Self-Consistency Prompting（自一致性提示）详解

## 一、什么是 Self-Consistency？

Self-Consistency（自一致性）是 2023 年由 Wang et al. 提出的一种提示工程技术，发表于论文 *"Self-Consistency Improves Chain of Thought Reasoning in Language Models"*。

核心思想非常直观：**对同一个问题，让 LLM 独立推理多次，然后对多个答案做"多数投票"（Majority Vote），选出最终结果。**

这背后的直觉是：正确的推理路径可能有很多条，但错误的推理路径往往各不相同。如果我们采样足够多次，正确答案会在统计上占据多数。

```
                    ┌──── 推理路径 A ──► Answer: 25 ──┐
                    │                                  │
同一问题 ───► LLM ──┼──── 推理路径 B ──► Answer: 25 ──┼──► 多数投票 ──► Answer: 25 ✓
  (多次采样)         │                                  │
                    ├──── 推理路径 C ──► Answer: 30 ──┤
                    │                                  │
                    ├──── 推理路径 D ──► Answer: 25 ──┤
                    │                                  │
                    └──── 推理路径 E ──► Answer: 25 ──┘
```

与单次推理（Greedy Decoding）相比，Self-Consistency 利用了**采样多样性**来降低随机错误的概率。

## 二、脚本整体流程

`self_consistency_prompting.py` 的任务是让 LLM 解一道数学应用题，并通过多次采样 + 多数投票确保答案的可靠性。

### 2.1 题目分析

```
Henry made two stops during his 60-mile bike trip.
He first stopped after 20 miles.
His second stop was 15 miles before the end of the trip.
How many miles did he travel between his first and second stops?
```

用数轴分析：

```
起点                    第一次停                     第二次停               终点
 0 ──────────────────── 20 ─────────────────────── 45 ────────────────── 60
 |←────── 20 mi ──────→|←──────── 25 mi ────────→|←───── 15 mi ──────→|
```

- 第一次停在第 20 英里处
- 第二次停在距终点 15 英里处，即第 60 - 15 = 45 英里处
- 两次之间距离 = 45 - 20 = **25 英里**

### 2.2 执行流程

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐                   │
│  │ 第 1 次   │     │ 第 2 次   │     │ 第 N 次   │                   │
│  │ 采样调用  │     │ 采样调用  │ ... │ 采样调用  │  ← temperature=1  │
│  │ LLM      │     │ LLM      │     │ LLM      │                   │
│  └────┬─────┘     └────┬─────┘     └────┬─────┘                   │
│       │                │                │                          │
│       ▼                ▼                ▼                          │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐                     │
│  │ 提取答案 │     │ 提取答案 │     │ 提取答案 │   extract_final_   │
│  │ Answer:25│     │ Answer:25│     │ Answer:30│   answer()         │
│  └────┬─────┘     └────┬─────┘     └────┬─────┘                   │
│       │                │                │                          │
│       └───────────┬────┴────────────────┘                          │
│                   ▼                                                │
│           ┌──────────────┐                                         │
│           │  Counter 统计 │  ← collections.Counter                  │
│           │  多数投票     │                                         │
│           └──────┬───────┘                                         │
│                  ▼                                                  │
│         majority_answer                                            │
│         == EXPECTED_OUTPUT ?                                        │
│           是 → SUCCESS                                              │
│           否 → 打印分布，调试                                        │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## 三、关键代码解析

### 3.1 系统提示词（System Prompt）

```python
YOUR_SYSTEM_PROMPT = """You are a precise math problem solver. Follow these rules strictly:

1. Read the problem carefully. Identify every numerical value and what it represents.
2. Break the problem into small, explicit steps. Show your work for each step.
3. For distance/position problems, draw a number line mentally:
   - Mark the starting point as 0.
   - Mark intermediate positions using the given clues.
   - Compute differences between positions to find distances.
4. After solving, verify your answer by checking it against all conditions in the problem.
5. On the very last line, output your final answer in exactly this format: Answer: <number>
"""
```

这是整个方案中**最关键的可调节部分**。下面逐条解释为什么这样设计：

| 规则 | 设计意图 |
|------|----------|
| **规则 1：识别数值** | 防止模型遗漏题目中的关键数字（60、20、15），这是小模型常犯的错误 |
| **规则 2：逐步拆解** | 即 Chain-of-Thought（思维链），让模型展示中间推理步骤，而不是直接跳到答案 |
| **规则 3：数轴思维** | 针对本题类型（距离/位置）给出具体的解题框架：标注起点 → 标注各位置 → 算差值 |
| **规则 4：自我验证** | 让模型回头检查答案是否满足题目所有条件，相当于一个内置的"审查步骤" |
| **规则 5：格式约束** | 确保输出以 `Answer: <number>` 结尾，让正则提取函数能稳定工作 |

### 3.2 高温度采样

```python
options={"temperature": 1, "num_ctx": 8192},
```

- **temperature=1**：这是 Self-Consistency 的关键配置。高温度意味着模型每次生成时有更大的随机性，会探索不同的推理路径。
- 如果用 `temperature=0`（贪心解码），每次输出几乎相同，多次采样就失去了意义。
- 高温度 + 多数投票 = 用**多样性换可靠性**。

### 3.3 答案提取

```python
def extract_final_answer(text: str) -> str:
    matches = re.findall(r"(?mi)^\s*answer\s*:\s*(.+)\s*$", text)
    if matches:
        value = matches[-1].strip()          # 取最后一个匹配
        num_match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if num_match:
            return f"Answer: {num_match.group(0)}"  # 归一化格式
        return f"Answer: {value}"
    return text.strip()
```

设计要点：
- 取**最后一个** `Answer:` 行——因为模型可能在推理中途写出中间答案，只有最后一个才是最终结论
- 移除逗号后提取数字——处理模型可能输出 `Answer: 25,` 或 `Answer: 1,000` 的情况
- 归一化为统一格式——确保 `Counter` 统计时不会因为空格、格式差异而把相同答案当成不同答案

### 3.4 多数投票

```python
counts = Counter(answers)
majority_answer, majority_count = counts.most_common(1)[0]
```

`Counter.most_common(1)` 返回出现频率最高的答案及其出现次数。例如 5 次采样中有 4 次回答 "Answer: 25"、1 次回答 "Answer: 30"，则最终选择 "Answer: 25"。

## 四、为什么这套方案能成功？

### 4.1 Self-Consistency 的数学直觉

假设模型单次回答正确的概率为 $p$（例如 $p = 0.7$），采样 $n = 5$ 次后做多数投票，最终答案正确的概率为：

$$P(\text{正确}) = \sum_{k=\lceil n/2 \rceil}^{n} \binom{n}{k} p^k (1-p)^{n-k}$$

当 $p = 0.7, n = 5$ 时：

$$P(\text{正确}) = \binom{5}{3}(0.7)^3(0.3)^2 + \binom{5}{4}(0.7)^4(0.3)^1 + \binom{5}{5}(0.7)^5 \approx 0.837$$

即单次 70% 的正确率，经过 5 次投票可提升到约 **83.7%**。如果通过优化提示词把单次正确率提升到 0.85，投票后正确率可达约 **97.4%**。

### 4.2 提示词与投票的协同作用

本方案的成功依赖两层保障：

```
第一层保障：优质的系统提示词
─────────────────────────────
  ↓ 提升每次采样的单次正确率 p
  ↓ （从可能的 0.5 提升到 0.8+）

第二层保障：多数投票机制
─────────────────────────────
  ↓ 将单次正确率 p 放大为投票正确率
  ↓ （0.8 → 0.94+）

最终结果：高可靠性的答案
```

- **仅靠好的提示词**：单次正确率可能到 80-90%，但仍有 10-20% 的失败概率
- **仅靠多数投票**（提示词差）：如果单次正确率低于 50%，投票反而会放大错误
- **两者结合**：好的提示词确保 $p > 0.5$，投票机制将 $p$ 指数级放大

### 4.3 为什么我们的提示词有效？

| 问题 | 没有提示词引导时 | 有提示词引导后 |
|------|------------------|----------------|
| 模型跳步推理 | 直接算 60-20=40 或 60-15=45，然后不知道下一步该做什么 | 逐步拆解，先标出所有位置再算差值 |
| 混淆"距终点 15 英里"和"第 15 英里处" | 容易把第二次停靠理解为第 15 英里处 | 数轴思维迫使模型将"距终点"转换为绝对位置 |
| 输出格式不一致 | 可能输出 "The answer is 25" 或 "25 miles" | 明确格式要求，正则提取更稳定 |
| 粗心计算错误 | 一次算完就输出 | 自我验证步骤增加了纠错机会 |

## 五、Self-Consistency vs 其他提示技术对比

| 技术 | 核心机制 | 适用场景 | 本项目中的对应 |
|------|----------|----------|---------------|
| **K-Shot Prompting** | 提供示例让模型学习模式 | 格式/风格模仿 | `k_shot_prompting.py` |
| **RAG** | 检索外部知识注入上下文 | 需要外部知识的问答 | `rag.py` |
| **Reflexion** | 评估 → 反馈 → 迭代修正 | 代码生成等可自动测试的任务 | `reflexion.py` |
| **Self-Consistency** | 多次采样 → 多数投票 | 有明确答案的推理问题 | `self_consistency_prompting.py` |

Self-Consistency 的独特优势：
- **不需要外部评估器**（Reflexion 需要测试用例）
- **不需要外部知识库**（RAG 需要文档检索）
- **不需要多轮交互**（只需并行采样，无反馈循环）
- 代价是**计算成本线性增长**（N 次调用 = N 倍 token 消耗）

## 六、总结

| 要素 | 说明 |
|------|------|
| **高温度采样** | `temperature=1` 保证每次推理路径不同，产生多样性 |
| **结构化提示词** | 引导模型逐步推理、使用数轴思维、自我验证，提升单次正确率 |
| **答案归一化** | 正则提取 + 格式统一，确保相同答案不会因格式差异被误判为不同 |
| **多数投票** | 利用统计规律，将多个"大概率正确"的答案聚合为"高概率正确"的最终结果 |

Self-Consistency 的核心洞察：**正确答案的推理路径虽然各不相同，但殊途同归；错误答案则各有各的错法。** 多数投票天然能过滤掉那些"各有各的错法"的噪声，保留收敛到同一结果的正确推理。
