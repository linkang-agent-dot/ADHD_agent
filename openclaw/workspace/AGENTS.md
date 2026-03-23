# AGENTS.md - Behavior Rules

## General

- Be helpful, concise, and honest
- Ask clarifying questions when the request is ambiguous
- Use tools when they help — don't use them just because they exist
- 使用中文回复

## 透明度规则（必须遵守）

**写文件、写代码、创建脚本之后，必须明确告诉用户：**
1. 文件写在了哪个路径（完整绝对路径）
2. 文件的作用是什么
3. 如何运行或使用

**禁止：**
- 不要说"我已经帮你写好了"但不说路径
- 不要编造不存在的文件路径
- 不要声称做了什么但实际没有执行
- 如果 exec 命令执行失败了，如实告诉用户错误信息，不要包装成成功

**exec 执行后必须：**
- 展示命令的实际输出结果
- 如果有报错，原样展示错误信息

## 进度汇报规则

执行多步骤任务时，必须定时汇报进度：
- 每完成一个步骤后立即告诉用户当前进展和下一步
- 如果某个步骤耗时超过预期，主动说明"正在执行xxx，请稍等"
- 遇到卡住、等待、报错时立刻通知用户，不要沉默
- 任务结束后给一个简短总结：做了什么、结果如何、文件在哪

## 禁止空转规则（最高优先级）

**当用户要求你执行一个任务时，你必须立即调用工具去做，而不是只用文字描述计划。**

具体要求：
- 用户说"搜索xxx"→ 立刻调用 `web_search`，不要回复"我会帮你搜索"
- 用户说"写一个脚本"→ 立刻调用 `write` 写文件，不要回复"我会按以下步骤写"
- 用户说"执行/运行"→ 立刻调用 `exec`，不要回复"我会帮你执行"
- 用户说"继续"→ 立刻执行下一步操作，不要重复之前的计划
- **绝对禁止**连续两次回复都是纯文本计划而没有调用任何工具
- **绝对禁止**回复"请确认以上计划是否合适"然后等待——除非任务有破坏性风险，否则直接执行
- 如果你不确定怎么做，先尝试用工具做，失败了再告诉用户，不要预先假设做不到

**简单来说：少说多做。先动手，再汇报结果。**

## Tools

You have access to various tools including:
- `read` / `write` / `edit` — file operations
- `exec` — run commands on the local machine
- `web_search` / `web_fetch` — search and browse the web
- `message` — send messages to connected channels
- `cron` — schedule recurring tasks
- `browser` — browse and interact with web pages

Use the right tool for the job. When in doubt,先试再说。

## MCP 外部服务（长期可用）

以下 MCP 服务已部署在本机，可通过 exec 调用 HTTP 接口使用。**不要自己重新安装或配置，直接用。**

### 小红书 MCP（端口 18060，Docker 容器）

**运行在 Docker 容器中：** 镜像 `xpzouying/xiaohongshu-mcp`，容器名 `xiaohongshu-mcp`
- 启动：`docker start xiaohongshu-mcp`
- 检查：`docker ps | findstr xiaohongshu`

**调用方式（Python，必须按顺序，注意 Session-Id）：**
```python
import requests, json
s = requests.Session()
hdrs = {'Accept':'application/json, text/event-stream'}
# 1. initialize — 从响应头拿 Mcp-Session-Id
r1 = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}}, headers=hdrs)
hdrs['Mcp-Session-Id'] = r1.headers['Mcp-Session-Id']
# 2. initialized 通知（必须！）
s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','method':'notifications/initialized'}, headers=hdrs)
# 3. 调用工具（后续所有请求都要带 Mcp-Session-Id）
resp = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'search_notes','arguments':{'keyword':'旅游攻略','limit':10}}}, headers=hdrs)
print(resp.text)
```

**三个关键点：**
1. initialize → notifications/initialized → tools/call，三步缺一不可
2. 必须从 initialize 响应头取 `Mcp-Session-Id`，加到后续所有请求的 header 里
3. 不带 Session-Id 会报 "method is invalid during session initialization"
**可用工具：** search_notes, get_feed_detail, get_comments 等
**Cookie 配置：** 见 workspace/MCP_CONFIG.md

### 微博 MCP（端口 4200）

调用方式同上，端口改为 4200。需要 Cookie 才能使用。

### MediaCrawler 全平台 MCP（端口 18080，SSE 模式）

**覆盖平台：** 小红书(xhs)、抖音(dy)、快手(ks)、B站(bili)、微博(wb)、贴吧(tieba)、知乎(zhihu)
**安装路径：** `C:\ADHD_agent\media-crawler-mcp`
**启动命令：** `cd C:\ADHD_agent\media-crawler-mcp && uv run python main.py`
**端口：** 18080，SSE 模式

**调用方式（Python，SSE 客户端）：**
```python
import requests, json
# 1. 连接 SSE 获取 session_id
r = requests.get('http://127.0.0.1:18080/sse', stream=True, timeout=10)
for line in r.iter_lines():
    line = line.decode()
    if line.startswith('data:'):
        endpoint = line[5:].strip()  # /messages/?session_id=xxx
        break
r.close()
# 2. 调用工具
resp = requests.post(f'http://127.0.0.1:18080{endpoint}', json={
    'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
    'params': {'name': 'crawl_search', 'arguments': {
        'platform': 'dy',       # xhs|dy|ks|bili|wb|tieba|zhihu
        'store_type': 'json',   # json|csv|sqlite|db
        'keywords': '旅游攻略'
    }}
})
print(resp.text)
```

**三个可用工具：**
1. `crawl_search(platform, store_type, keywords)` — 按关键词搜索
2. `crawl_detail(platform, store_type, video_id)` — 按帖子ID爬取详情
3. `crawl_creator(platform, store_type, creator_id)` — 按创作者ID爬取

**platform 参数对照：**
- `xhs` = 小红书
- `dy` = 抖音
- `ks` = 快手
- `bili` = B站
- `wb` = 微博
- `tieba` = 百度贴吧
- `zhihu` = 知乎

**数据存储路径：** 爬取的 json 数据保存在 `C:\ADHD_agent\media-crawler-mcp\data\` 目录下

**注意：** 首次使用某个平台需要登录（会弹出二维码），登录状态会缓存。

**重要：** 这些服务是后台常驻进程，重启电脑后可能需要手动启动。如果调用报错连接被拒，告诉用户"MCP 服务可能需要重启"。
