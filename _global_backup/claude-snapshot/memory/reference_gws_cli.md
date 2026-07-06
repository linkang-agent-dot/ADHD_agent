---
name: reference_gws_cli
description: GWS CLI（Google Workspace CLI）本机安装路径/项目ID/账号、读GSheet入口脚本、Token过期(401)重授权流程
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6662964b-398d-4bbb-a4b2-089beb425648
---

# GWS CLI（Google Workspace CLI）

## 基本信息
- 安装路径：`C:\Users\linkang\AppData\Roaming\npm\gws`
- GCP 项目 ID：`calm-repeater-489707-n1`
- 授权账号：linkang@nibirutech.com

## 读 GSheet
- 入口：`node C:\ADHD_agent\scripts\gws_stdin.js`

## Token 过期（401）重授权
1. 跑 `gws auth login -s sheets,drive`
2. `cat` 日志抓出授权 URL，**贴给用户手点**（不会自动弹浏览器）。

## 相关指针
- GSheet 读写统一工具（读/写/删/备份全封装，优先用）：[[reference_gsheet_toolkit]]
- gws.cmd 角括号传参失败坑（改用 node+run-gws.js）：[[feedback_gws_angle_bracket]]
- gws 读中文后 stdout 是 GBK 导致搜索失败坑（用行号范围读）：[[feedback_gws_gbk_search]]
