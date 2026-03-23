# MEMORY.md - 持久化记忆

此文件记录跨会话需要保留的关键信息。每次对话都会自动加载。

## 已部署的 MCP 服务

### 小红书 MCP
- 端口：18060
- 地址：http://localhost:18060/mcp
- 用途：搜索小红书笔记、获取笔记详情、评论
- Cookie：见 workspace/MCP_CONFIG.md
- **运行方式：Docker 容器**
- 镜像：xpzouying/xiaohongshu-mcp
- 容器名：xiaohongshu-mcp
- 启动命令：`docker start xiaohongshu-mcp`（容器已创建，直接 start 即可）
- 如果容器不存在：`docker run -d --name xiaohongshu-mcp -p 18060:18060 xpzouying/xiaohongshu-mcp`

### 微博 MCP
- 端口：4200
- 地址：http://localhost:4200/mcp
- 用途：搜索微博内容
- 需要 Cookie 才能使用
- 安装方式：pip install mcp-server-weibo，后台常驻进程

### MediaCrawler 全平台 MCP（新！）
- 端口：18080
- 地址：http://127.0.0.1:18080/sse（SSE 模式）
- 用途：7 平台内容爬取（小红书、抖音、快手、B站、微博、贴吧、知乎）
- 安装路径：`C:\ADHD_agent\media-crawler-mcp`
- 启动命令：`cd C:\ADHD_agent\media-crawler-mcp && uv run python main.py`
- 存储模式：json（不需要 MySQL）
- 工具：crawl_search / crawl_detail / crawl_creator
- platform 参数：xhs / dy / ks / bili / wb / tieba / zhihu
- 首次使用需登录（扫码），登录状态会缓存

## Cron 定时任务

- 每日旅游攻略推送：每天 18:00（Asia/Shanghai）
- 任务内容：搜集小红书+微博高赞旅游攻略，汇总推送到飞书

## 定时推送模板

### 小红书旅游热度每日推送
- **脚本**：`C:\Users\linkang\.openclaw\workspace\xiaohongshu_push.py`
- **定时**：工作日 11:30（cron: 30 11 * * 1-5）
- **内容**：小红书旅游热度Top5
- **格式**：每条包含标题 + 点赞/收藏数 + 作者 + 一句话摘要 + 封面图片

**推送消息模板**：
```
📊 小红书旅游热度Top5（{日期}）

1. {标题}
   👍{点赞} | ⭐{收藏} | @{作者}
   📝 {一句话摘要}

2. ...

---每日11:30自动推送
```
Cron job ID: f988438d-d7a0-4f08-acae-eba56c7c1271

## 重要历史决策

- 模型选择：MiniMax-M2.5（从 Text-01 升级，Text-01 不会调用工具）
- 通信渠道：飞书（主要）+ Telegram
- 工作时间：工作日 9:30-11:30, 13:30-18:00
- 用户偏好：中文交流、简短直接、可以催进度
