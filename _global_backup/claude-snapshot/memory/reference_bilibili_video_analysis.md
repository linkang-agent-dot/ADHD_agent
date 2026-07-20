---
name: bilibili-video-analysis
description: B站视频内容分析链路（复刻Sider）：无cookie拿流+本地whisper转写，绕过412风控的关键=html5 playurl接口
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8e352cc4-7d37-4b01-b14c-02c0969a2111
---

# B站视频内容分析链路（无需登录 cookie）

已实测跑通（2026-07-13，BV12XNT6mEfz）。效果等同 Sider 的视频总结，且可批量+可深挖。

## 四步链路

1. **元数据**：`https://api.bilibili.com/x/web-interface/view?bvid=<BV号>`（urllib 直调即可，带 UA+Referer）→ 标题/UP主/播放/点赞/cid/简介
2. **拿流（关键一步）**：`https://api.bilibili.com/x/player/playurl?bvid=<BV>&cid=<cid>&platform=html5&high_quality=1&qn=16` → 返回 mp4 直链（360/480p，转写够用）。下载时带 `Referer: https://www.bilibili.com/`
3. **抽音频**：`ffmpeg -i in.mp4 -vn -ar 16000 -ac 1 out.wav`
4. **转写**：`faster_whisper` 本地缓存有 `small`/`medium` 模型（`~/.cache/huggingface/hub`），必须 `local_files_only=True`（本机连不上 HuggingFace，getaddrinfo 失败）

## 踩坑记录（按序）

- **curl 直调 api.bilibili.com 静默无输出** → 用 Python urllib 就通（Git Bash curl 的问题）
- **CC字幕接口 `x/player/wbi/v2` 游客返回空** → AI字幕必须登录 cookie（SESSDATA），游客拿不到；所以走音频转写兜底
- **yt-dlp 下载 412 Precondition Failed** → 游客 playurl（yt-dlp 走的 wbi 版）被风控，加 buvid cookie 也没用；**不是代理问题**（`x/web-interface/zone` 确认出口=国内IP）。解法=改用 html5 playurl 接口（步骤2），不走 yt-dlp
- **`--cookies-from-browser chrome` 失败** → Chrome 运行中锁 cookie 库
- **whisper `base` 模型现下失败** → 本机 HF 不通，用已缓存的 `small`（转写4分钟视频约1-2分钟）
- 控制台中文乱码 → GBK 问题，加 `-X utf8` 并把结果写文件再 Read

## 批量扫描扩展（07-13 实测）

- **搜索 API 可用**：`x/web-interface/search/type?search_type=video|article&keyword=<urlencode>`，带 buvid cookie（spi 接口现领）即通，返回 bvid/title/play/duration/pubdate
- **批量转写工具（已固化）**：`C:\ADHD_agent\skills\bilibili-transcribe\bili_transcribe.py <BV号...>` = view→html5 playurl→ffmpeg→whisper 一条龙，断点续传（已有 transcript 跳过），后台 Bash 跑；⚠️ **view 接口连续请求会限流超时，脚本已带重试(4次递增)**
- **B站专栏(cv号)正文抓取难**：桌面页纯 JS 渲染(无 SSR)、Jina 只拿到壳；**移动页 `bilibili.com/read/mobile?id=<cv号>` 短文可拿全文**，长文被"展开阅读全文"截断 → 专栏不作为主力源
- UP主视频列表：`x/space/wbi/arc/search`（需 wbi 签名）
- 评论：`x/v2/reply?type=1&oid=<aid>`；弹幕：`x/v1/dm/list.so?oid=<cid>`（protobuf 新版 `x/v2/dm/web/seg.so`）
- 小红书笔记正文游客抓不到（Google 不索引+登录墙），需用户给 cookie 才能补这个源

相关：`youtube-analyzer` skill（仅 YouTube）、`url-reader` skill（只能抓页面壳，拿不到B站视频正文/字幕）
