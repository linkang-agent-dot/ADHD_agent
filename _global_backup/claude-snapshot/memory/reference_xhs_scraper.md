---
name: xhs-scraper
description: 小红书抓取链路：单篇笔记(带xsec_token分享链)可免登录httpx直抓正文+视频mp4直链；搜索/批量才需playwright持久profile+扫码登录；⚠️headless必被风控(300012)必须headed；工具在ADHD_agent/skills/xhs-scraper
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8e352cc4-7d37-4b01-b14c-02c0969a2111
---

# 小红书抓取链路（2026-07-13 打通登录；07-14 补免登录直抓视频）

## 单篇笔记免登录直抓（最轻路径，优先用）
适用：用户直接甩来的**分享链接**（URL 自带 `xsec_token`）。2026-07-14 实测（视频笔记）：
1. 正文/文案：`fetch.py`（url-reader skill）走 Firecrawl 能拿到；或直接第 2 步的 HTML 里也有。
2. **视频 mp4 直链**：普通 `httpx.get(分享URL, UA=Chrome, Referer=xiaohongshu.com)` 返回 200，页面内嵌 `__INITIAL_STATE__`，正则 `"masterUrl":"..."` 或直接搜 `https?://[^"'\s\\]+\.mp4[^"'\s\\]*`（`/` 需 unescape）→ `curl -H "Referer: https://www.xiaohongshu.com/"` 下载即可。
- 无需登录、无需 playwright、headless 风控不触发（不是搜索页）。
- ⚠️ 仅对带 xsec_token 的链接验证过；无 token 的裸 note URL 未验。
- 脚本范本：会话 scratchpad `xhs_video_grab.py`（20 行，可随手重写）。

## 搜索/批量抓取（需登录态）

工具目录：`C:\ADHD_agent\skills\xhs-scraper\`
- `xhs_login.py` — 弹出带界面浏览器让用户扫码，登录态存**持久化 profile** `C:\Users\linkang\.xhs-profile`（主）+ `xhs_cookies.json` 快照（备）。已登录过一次，profile 里有 `web_session` cookie。
- `xhs_search.py "<关键词>" [篇数]` — 搜索+抓笔记正文出 md。**状态：headed 模式验证到能拿到 explore 链接，正文抓取 selector 未完整验证**（做帕鲁手册时用户转需求中断了）。

## 关键坑
- **headless 必被风控**：无头访问 search_result 直接跳「安全限制」页（error_code=300012「IP存在风险」）——不是真 IP 问题（同 IP headed 正常），是无头特征检测。**脚本必须 `headless=False`**（会闪浏览器窗口，可接受）。
- 搜索结果卡片选择器：`a[href*='/explore/']` / `a[href*='/search_result/']`，笔记 id = 24 位 hex。
- 登录判定：cookie 出现 `web_session` 即成功。

相关：[[bilibili-video-analysis]]（B站同类链路）
