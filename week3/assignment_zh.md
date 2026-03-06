# 第三周 — 构建自定义 MCP 服务器

设计并实现一个封装真实外部 API 的 Model Context Protocol（MCP）服务器。你可以：
- **本地运行**（STDIO 传输）并与 MCP 客户端（如 Claude Desktop）集成。
- 或者**远程运行**（HTTP 传输）并从模型代理或客户端调用。这更有难度，但可以获得额外加分。

如果添加了符合 MCP 授权规范的认证机制（API Key 或 OAuth2），可获得额外加分。

## 学习目标
- 理解 MCP 的核心能力：工具（tools）、资源（resources）、提示（prompts）。
- 实现带有类型化参数和健壮错误处理的工具定义。
- 遵循日志记录和传输的最佳实践（STDIO 服务器不得使用 stdout 输出日志）。
- （可选）为 HTTP 传输实现授权流程。

## 要求
1. 选择一个外部 API 并记录你将使用哪些端点。示例：天气、GitHub Issues、Notion 页面、影视数据库、日历、任务管理、金融/加密货币、旅行、体育数据等。
2. 暴露至少两个 MCP 工具。
3. 实现基本的容错能力：
   - 针对 HTTP 失败、超时和空结果进行优雅的错误处理。
   - 尊重 API 速率限制（例如，简单退避策略或面向用户的警告）。
4. 打包和文档：
   - 提供清晰的安装说明、环境变量配置和运行命令。
   - 包含一个示例调用流程（说明在客户端中输入/点击什么来触发工具）。
5. 选择一种部署模式：
   - 本地：STDIO 服务器，可在你的机器上运行，能被 Claude Desktop 或 Cursor 等 AI IDE 发现。
   - 远程：HTTP 服务器，可通过网络访问，能被 MCP 感知的客户端或代理运行时调用。如果已部署且可访问，可获得额外加分。
6. （可选）额外加分：认证
   - 通过环境变量和客户端配置支持 API Key；或
   - 为 HTTP 传输实现 OAuth2 风格的 Bearer Token，验证 token 的 audience，且不将 token 透传到上游 API。

## 交付内容
- 源代码放在 `week3/` 目录下（建议：`week3/server/`，入口文件如 `main.py` 或 `app.py`）。
- `week3/README.md` 需包含：
  - 前置要求、环境配置和运行说明（本地和/或远程）。
  - 如何配置 MCP 客户端（本地模式下以 Claude Desktop 为例）或远程模式下的代理运行时。
  - 工具参考：名称、参数、示例输入/输出及预期行为。

## 评分标准（满分 90 分）
- 功能性（35 分）：实现 2+ 个工具、正确的 API 集成、有意义的输出。
- 可靠性（20 分）：输入验证、错误处理、日志记录、速率限制意识。
- 开发者体验（20 分）：清晰的安装/文档说明、易于本地运行、合理的目录结构。
- 代码质量（15 分）：代码可读性、描述性命名、最小复杂度、适当使用类型提示。
- 额外加分（10 分）：
  - +5 分：远程 HTTP MCP 服务器，可被 OpenAI/Claude SDK 等代理/客户端调用。
  - +5 分：正确实现认证（API Key 或带有 audience 验证的 OAuth2）。

## 参考资料
- MCP 服务器快速入门：[modelcontextprotocol.io/quickstart/server](https://modelcontextprotocol.io/quickstart/server)
*注意：不可直接提交该示例项目。*
- MCP 授权（HTTP）：[modelcontextprotocol.io/specification/2025-06-18/basic/authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- Cloudflare 上的远程 MCP（Agents）：[developers.cloudflare.com/agents/guides/remote-mcp-server/](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)。在部署之前，请使用 modelcontextprotocol inspector 工具在本地调试你的服务器。
- Vercel 部署 MCP 服务器：[vercel.com/docs/mcp/deploy-mcp-servers-to-vercel](https://vercel.com/docs/mcp/deploy-mcp-servers-to-vercel)。如果你选择远程部署 MCP，Vercel 是一个不错的选择，提供免费额度。
