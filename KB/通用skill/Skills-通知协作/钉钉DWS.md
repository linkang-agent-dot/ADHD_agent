---
aliases: [dws, 钉钉, dingtalk]
tags: [skill, 通知, 钉钉, dws]
skill_path: .agents/skills/dws/
trigger: 表格数据、日程会议、通讯录、审批、待办
---

# 钉钉 DWS

## 概述
通过 `dws` CLI 管理钉钉全系产品能力。

## 支持模块
| 模块 | 命令前缀 | 功能 |
|------|---------|------|
| AI 表格 | `dws aitable` | 表格数据管理 |
| 日历 | `dws calendar` | 日程会议管理 |
| 通讯录 | `dws contact` | 查询组织成员 |
| 文档 | `dws doc` | 文档创建编辑 |
| 机器人 | `dws robot` | 消息推送 |
| 待办 | `dws todo` | 任务管理 |
| 邮箱 | `dws mail` | 邮件收发 |
| 听记 | `dws meeting-note` | 会议摘要 |
| AI 应用 | `dws ai-app` | 应用创建 |
| 审批 | `dws approval` | 审批流程 |
| 日志 | `dws journal` | 日报周报 |
| 钉盘 | `dws drive` | 文件管理 |

## 使用约束
- 必须使用 `--format json` 输出
- 禁止编造 ID
- 删除操作需确认
