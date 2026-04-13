---
aliases: [youtube-analyzer, YouTube分析, 视频分析]
tags: [skill, 其他, youtube, gemini, 视频]
skill_path: .agents/skills/youtube-analyzer/
trigger: analyze this youtube、分析这个视频
---

# YouTube 视频分析

## 概述
使用 Gemini 原生视频理解能力分析 YouTube 视频内容。

## 适用场景
- 理解视频内容
- 提取关键信息
- 总结/描述视频画面
- 分析游戏录屏、教程、演示

## 限制
- 仅支持 YouTube URL
- 最长约 1 小时视频
- 需公开或不公开列出的视频

## 触发词
`analyze this youtube` `what's in this video` `summarize this video` `分析这个视频` `这个视频讲了什么` `youtube视频内容`

## 关键文件
- `scripts/analyze_youtube.py` — 分析脚本
- `references/gemini-video-limits.md` — Gemini 视频限制说明
