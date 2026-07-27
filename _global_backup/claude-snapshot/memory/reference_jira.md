---
name: Jira API Access
description: Jira REST API 访问配置 - tap4fun 内部 Jira，用于查询 issue、项目等
type: reference
originSessionId: c8c91af7-37ba-4a38-b27d-fffc7da80bcd
modified: 2026-07-24T04:40:15.328Z
---
## Jira 访问信息

- URL: https://jira.tap4fun.com
- 用户: linkang
- 认证方式: Basic Auth (用户名:API Token)

## 调用方式

```bash
curl -u "linkang:DXaUieFe4s2cgObnlH5RxSEX1GFvdx1NMm2NfI" \
  "https://jira.tap4fun.com/rest/api/2/issue/{ISSUE_KEY}"
```

## 常用 API

- 获取 issue: `/rest/api/2/issue/{issueKey}`
- 搜索 JQL: `/rest/api/2/search?jql={jql}`
- 获取项目: `/rest/api/2/project/{projectKey}`

## X3NEW 建 BUG 单规格（2026-07-21 实测）

- X3 项目 key = `X3NEW`，BUG 类型名 = `缺陷/故障`
- POST `/rest/api/2/issue` 必填 5 字段（缺任一会 400）：
  - `customfield_10205` Bug等级：option id `10104=A / 10105=B / 10106=C / 10107=D`，传 `{"id":"10106"}`
  - `customfield_12901` 归属功能：**传字符串 issue key**（非对象）；且只能选带 `labels=测试` 的单——即各需求下的「XX - 测试」子任务（如马戏扭蛋机=X3NEW-2257），选需求单本身会报 "does not fit filter query"
  - `customfield_10206` 预期结果 / `customfield_10207` 实际结果：纯文本
  - `fixVersions`：传 `[{"id":...}]`，未发布版本查 `/project/X3NEW/versions`（0.32.0=id 17300 对应26w35）
- createmeta 查不到 allowedValues（返回空），用现有单的 `/editmeta` 查选项
- 马戏扭蛋机需求树：需求 X3NEW-2243 / 服务器 2258 / 客户端 2259 / 配置 2261 / 测试 2257

## X3NEW 需求树 + 版本（2026-07-24 实测，建需求单/排期用）

- **版本 = 周更**（每周一个，查 `/project/X3NEW/versions`）：0.25.0=07-22 / 0.26.0=07-29 / 0.27.0=08-05 …每周+7天，2026-07-24 时最新到 **0.32.0=09-09**；10月版本(0.33+)尚未创建。节日内容**提前于上线做**（马戏节8月上线，扭蛋机需求在 0.26.0=07-29）。
- **需求树标准结构**：1个「需求」(issuetype=需求) + 子任务(issuetype=子任务)，子任务类型 = **服务器 / 客户端 / 配置 / 测试**（4件标配），按需加 **数值 / 用户体验**。命名 = `{节日}-{模块}`（如「马戏团-马戏扭蛋机」X3NEW-2243 → 子任务 2257测试/2258服务器/2259客户端/2261配置）；数值单如「第三只海妖 - 数值」。
- ⚠️ **JQL `issuetype=需求`（不加引号）静默返回 0**——中文 issuetype 名要么 `issuetype="需求"` 加引号，要么不过滤 issuetype、拿全类型结果客户端按 `issuetype.name` 筛。

## 踩坑

- ⚠️ JQL 里用 `assignee=currentUser()` 会返回 **400 Bad Request**（本 Jira 实例不认）。查"分配给我的"改用显式 `assignee=linkang`。
- ⚠️ JQL 里 `status not in (Done,Closed,...)` 可用，但更稳的是 `statusCategory != Done`（一次覆盖所有完成态，免去枚举各语言/各项目自定义完成状态）。
- curl 直连偶发 SSL handshake 失败（exit 35）；PowerShell `Invoke-RestMethod` + `[Net.ServicePointManager]::SecurityProtocol=Tls12` 可绕过。
