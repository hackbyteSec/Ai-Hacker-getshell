# ai-chat.html ↔ MCP 后端对接说明

## 访问与启动

- 后端启动（默认端口 5000）：
  - `python e:\POC\fofa\mcp\main.py --no-banner --host 127.0.0.1 --port 5000`
- 前端页面：
  - [ai-chat.html](file:///e:/POC/fofa/aibug/ai-chat.html)

## 后端接口（Flask）

基础健康与工具：
- `GET /health`：健康检查
- `GET /tools`：列出所有工具（从 `mcp/modules/*` 注册）
- `GET /tools/<tool_name>`：工具详情
- `GET /tools/search?q=keyword`：搜索工具
- `GET /tools/stats`：工具统计
- `POST /execute`：执行指定工具
  - body：`{ "tool": "tool_name", "params": { ... }, "session_id": "optional" }`

对话聚合（页面默认使用）：
- `POST /chat`
  - body：`{ "message": "...", "tools": ["..."], "context": { "session_id": "...", ... } }`
  - 行为：
    - `tools` 非空：按顺序执行工具（自动从消息中提取 URL/IP/域名并推断参数），返回 `results`
    - `tools` 为空：若消息中包含目标，返回 `ai/analyze` 的分析结果
  - 支持在 `message` 末尾附加 JSON 以补充参数：
    - `{"tool_params":{"sqlmap":{"target":"https://a.com","risk":3}}}`

AI / 工作流 / 报告 / 攻击链：
- `POST /ai/analyze`
- `POST /ai/plan`
- `POST /workflow/auto`
- `POST /report/generate`
- `POST /chain/create`
- `POST /chain/<chain_id>/execute`
- `GET /chain/<chain_id>`
- `GET /chain/<chain_id>/suggestions`

服务端事件流（用于右侧日志面板）：
- `GET /events?since=<id>`
  - 返回 `text/event-stream`，事件为 JSON，包含：
    - `id`, `ts`, `level`, `status`, `service`, `tool`, `params`, `duration`, `error`, `session_id`

## 前端使用说明（ai-chat.html）

### 1) 工具选择与执行

- 页面启动后会从 `GET /tools` 自动加载工具，显示在「全部工具」区域（支持搜索）。
- 点击工具卡片可将其加入“已选工具”。
- 输入任务描述并发送：
  - 前端会调用 `POST /chat`，并携带 `tools: 已选工具列表`。

### 2) 直接调用命令（聊天输入框以 / 开头）

- `/tools`：查看工具列表（前 30 个）
- `/tool <tool_name> <json_params>`：直接执行工具（等价于 `/execute`）
  - 示例：`/tool whois_lookup {"target":"example.com"}`
- `/analyze <target>`：调用 `/ai/analyze`
- `/plan <target>`：调用 `/ai/plan`
- `/workflow <target> <json_options>`：调用 `/workflow/auto`
- `/report <session_id> <format>`：调用 `/report/generate`

### 3) 右侧日志面板

- 前端对所有请求会自动记录日志：请求参数、HTTP 状态、耗时、错误信息。
- 同时通过 `EventSource(/events)` 订阅服务端事件，记录工具执行状态与耗时。
- 支持：
  - 自动滚动
  - SERVICE / STATUS / 时间范围 / 关键词筛选
  - 复制筛选 / 复制全部
  - 导出筛选（下载 .log）

