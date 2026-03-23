---
name: mcp-services
description: MCP 服务工具集，支持小红书、微博等平台的内容搜索、发布、互动操作。需要 Docker 容器运行。
---

# MCP 服务 Skill

本 Skill 用于调用各种 MCP 服务，包括小红书、微博等平台。

## When to Use This Skill

当用户需要：
- 搜索小红书笔记、查看详情、点赞、收藏、评论
- 获取微博热搜、搜索用户/内容
- 操作任何配置的 MCP 服务

## 配置文件

MCP 配置位于：`C:\ADHD_agent\mcporter.json`

配置格式：
```json
{
  "mcpServers": {
    "xiaohongshu": {
      "baseUrl": "http://localhost:18060/mcp"
    },
    "weibo": {
      "baseUrl": "http://localhost:4200/mcp"
    }
  }
}
```

## 前置要求

使用这些 MCP 服务前，需要先启动 Docker 容器：

```powershell
# 小红书服务 (端口 18060)
docker run -d --name xiaohongshu-mcp -p 18060:18060 xpzouying/xiaohongshu-mcp

# 微博服务 (端口 4200)
# 需要先配置 Cookie，否则不可用
```

## 调用方式

使用 `mcporter` CLI 调用：

```powershell
# 搜索小红书笔记
mcporter call xiaohongshu search_feeds keyword=关键词

# 获取笔记详情
mcporter call xiaohongshu get_feed_detail feed_id=笔记ID xsec_token=令牌

# 点赞
mcporter call xiaohongshu like_feed feed_id=笔记ID xsec_token=令牌

# 收藏
mcporter call xiaohongshu favorite_feed feed_id=笔记ID xsec_token=令牌

# 评论
mcporter call xiaohongshu post_comment_to_feed content=评论内容 feed_id=笔记ID xsec_token=令牌

# 获取微博热搜
mcporter call weibo get_trendings limit=10

# 搜索微博用户
mcporter call weibo search_users keyword=关键词 limit=5
```

## 查看可用工具

```powershell
# 列出所有 MCP 服务器
mcporter list

# 列出某个服务器的可用工具
mcporter list xiaohongshu
```

## 常见问题

1. **服务无法连接**：检查 Docker 容器是否运行 `docker ps`
2. **工具调用失败**：检查参数是否正确
3. **微博需要 Cookie**：需要登录微博后导出 Cookie 配置
