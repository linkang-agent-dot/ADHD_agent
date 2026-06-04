---
name: Jira API Access
description: Jira REST API 访问配置 - tap4fun 内部 Jira，用于查询 issue、项目等
type: reference
originSessionId: c8c91af7-37ba-4a38-b27d-fffc7da80bcd
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
