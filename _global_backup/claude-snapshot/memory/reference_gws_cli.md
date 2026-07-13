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
- ⚠️ **该命令是交互 TUI**：即使传了 `-s`，仍会停在「Select OAuth scopes」确认页等回车——后台/重定向跑会**永久挂死、连 URL 都不吐**（2026-07-08 实摔）。无头正确姿势：`cmd /c "echo. | gws auth login -s sheets,drive > log 2>&1"`（管道回车确认默认全选 scope），几秒后 log 里就有授权 URL。挂死的旧 gws 进程要先 `Stop-Process` 再重跑（端口/锁）。
- 401 的暴露层级：`gsheet_utils.run_gws` 失败**静默返 None**（list_tabs 返空列表不报错）——读表返回空先用 `gs._call(...)` 看 rc/text，401 invalid_grant 就走重授权，别误判成表没权限。

## 相关指针
- GSheet 读写统一工具（读/写/删/备份全封装，优先用）：[[reference_gsheet_toolkit]]
- gws.cmd 角括号传参失败坑（改用 node+run-gws.js）：[[feedback_gws_angle_bracket]]
- gws 读中文后 stdout 是 GBK 导致搜索失败坑（用行号范围读）：[[feedback_gws_gbk_search]]
