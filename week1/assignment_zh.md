# 第 1 周 — 提示技术

你将通过设计提示词完成特定任务来练习多种提示技术。每个任务的说明位于其对应源文件的开头。

## 安装
请确保已按照项目根目录下 `README.md` 中的说明完成安装。

## Ollama 安装
我们将使用 [Ollama](https://ollama.com/) 在本地运行不同的前沿大语言模型。请使用以下任一方式安装：

- macOS（Homebrew）：
  ```bash
  brew install --cask ollama 
  ollama serve
  ```

- Linux（推荐）：
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

- Windows：
  从 [ollama.com/download](https://ollama.com/download) 下载并运行安装程序。

验证安装：
```bash
ollama -v
```

在运行测试脚本之前，请确保已拉取以下模型。只需执行一次（除非之后删除模型）：
```bash
ollama run mistral-nemo:12b
ollama run llama3.1:8b
```

## 技术与源文件
- K-shot 提示 — `week1/k_shot_prompting.py`
- 思维链（Chain-of-thought）— `week1/chain_of_thought.py`
- 工具调用 — `week1/tool_calling.py`
- 自洽提示 — `week1/self_consistency_prompting.py`
- RAG（检索增强生成）— `week1/rag.py`
- Reflexion — `week1/reflexion.py`

## 提交内容
- 阅读每个文件中的任务描述。
- 设计并运行提示词（在代码中查找所有标有 `TODO` 的位置）。这是你唯一需要修改的部分（即不要改动模型相关代码）。
- 迭代改进直到测试脚本通过。
- 保存每种技术的最终提示词和输出。
- 提交时请包含每种提示技术对应的完整代码。***请再次确认所有 `TODO` 均已完成。***

## 评分标准（共 60 分）
- 完成 6 种不同提示技术中的每一种提示，各得 10 分
