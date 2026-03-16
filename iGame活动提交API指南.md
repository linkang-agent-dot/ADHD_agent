# iGame 活动提交 API 指南

## 概述

本文档记录了通过 iGame API 批量提交活动部署申请的正确方法。

---

## 1. 核心 API 端点

### 1.1 提交活动（Submit）

```
POST https://webgw-cn.tap4fun.com/ark/activity/submit
```

**重要**：这是"提交部署申请"，不是"直接部署活动"。提交后活动进入审批流程。

### 1.2 撤回活动（Recall）

```
POST https://webgw-cn.tap4fun.com/ark/activity/recall/{id}
```

### 1.3 查询活动详情

```
GET https://webgw-cn.tap4fun.com/ark/activity/{id}/detail
```

### 1.4 查询活动列表

```
GET https://webgw-cn.tap4fun.com/ark/activity/list?page=1&size=50
```

---

## 2. 请求格式

### 2.1 Headers

```python
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token,
    'clientid': clientId,
    'gameid': '1041',        # P2=1041, X2=1089, X9=1108
    'regionid': '201',
    'origin': 'https://igame.tap4fun.com',
    'referer': 'https://igame.tap4fun.com/',
}
```

认证信息来自 `~/.igame-auth.json`（Windows: `%USERPROFILE%\.igame-auth.json`）

### 2.2 Payload 格式（关键！）

**正确格式**：直接传 JSON 数组，不要包裹在 `{"activities": [...]}` 里

```python
payload = [{
    "activityConfigId": "21115696",    # 活动配置ID（字符串）
    "name": "推币机",                   # 活动名称（应使用 iGame 配置名称）
    "acrossServer": 1,                  # 1=跨服, 0=单服
    "acrossServerRank": 0,              # 固定为 0
    "previewTime": 0,                   # 固定为 0（不是时间戳！）
    "startTime": 1773194400000,         # 开始时间（毫秒时间戳）
    "endTime": 1774382400000,           # 结束时间（毫秒时间戳）
    "endShowTime": 0,                   # 固定为 0（不是时间戳！）
    "servers": [["2006502", "2054002", ...]],  # 服务器分组
}]
```

### 2.3 关键字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `activityConfigId` | string | 活动配置ID，来自 Google Sheet |
| `name` | string | **必须使用 iGame 配置中的名称**，不是文档里的别名 |
| `acrossServer` | int | 0=单服，1=跨服 |
| `acrossServerRank` | int | 固定填 0 |
| `previewTime` | int | **固定填 0**，不是时间戳 |
| `endShowTime` | int | **固定填 0**，不是时间戳 |
| `startTime` | int | 毫秒时间戳 |
| `endTime` | int | 毫秒时间戳 |
| `servers` | array | 二维数组，每个子数组是一个服务器分组 |

---

## 3. 服务器分组规则

### 3.1 单服活动 (acrossServer=0)

每个服务器单独一组：

```python
servers = [["2006502"], ["2054002"], ["2600202"], ...]
```

### 3.2 跨服-全服 (acrossServer=1)

所有服务器放一组：

```python
servers = [["2006502", "2054002", "2600202", ...]]
```

### 3.3 跨服-分组 (acrossServer=1)

按业务逻辑分组（如 Schema6 分组、Schema3-5 分组等）：

```python
servers = [
    ["2016902", "2012402", "2007202", ...],  # 分组1
    ["2077102", "2037402", "2054202", ...],  # 分组2
    ...
]
```

---

## 4. 常见错误

### 4.1 "活动配置校验失败" (HTTP 400)

**原因**：Payload 格式错误

**排查**：
1. 检查是否直接传数组（不要包裹 `{"activities": [...]}`）
2. 检查 `previewTime` 和 `endShowTime` 是否为 0
3. 检查 `acrossServerRank` 是否为 0

### 4.2 活动名称不对

**原因**：使用了文档中的别名，而不是 iGame 配置的实际名称

**解决**：
- iGame 无法通过 API 查询 `activityConfigId` 对应的配置名称
- 需要手动在 iGame 新建活动页面输入 configId 查看实际名称
- 或者提交时不传 `name` 字段（会显示为空）

---

## 5. 完整示例代码

```python
#!/usr/bin/env python3
import json, os, requests

# 加载认证
auth_file = os.path.expanduser("~/.igame-auth.json")
with open(auth_file, 'r', encoding='utf-8') as f:
    auth = json.load(f)

API_HOST = "https://webgw-cn.tap4fun.com"
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + auth["token"],
    'clientid': auth['clientId'],
    'gameid': auth.get('gameId', '1041'),
    'regionid': auth.get('regionId', '201'),
    'origin': 'https://igame.tap4fun.com',
    'referer': 'https://igame.tap4fun.com/',
}

# 构建 payload
payload = [{
    "activityConfigId": "21115696",
    "name": "推币机",  # 使用 iGame 配置名称
    "acrossServer": 1,
    "acrossServerRank": 0,
    "previewTime": 0,
    "startTime": 1773194400000,
    "endTime": 1774382400000,
    "endShowTime": 0,
    "servers": [["2006502", "2054002", "2600202"]],
}]

# 提交
url = API_HOST + "/ark/activity/submit"
resp = requests.post(url, json=payload, headers=headers, timeout=30)
data = resp.json()

if data.get("success"):
    print("提交成功! ID:", data["data"])
else:
    print("失败:", data.get("message"))
```

---

## 6. 活动状态码

| status | 含义 |
|--------|------|
| 2 | 待审批 |
| 5 | 已部署 |
| 9 | 已结束 |
| 10 | 已下线 |
| 19 | 已撤回 |

---

## 7. 注意事项

1. **名称问题**：`name` 字段应使用 iGame 活动配置的实际名称，而非 Google Sheet 文档中的别名。否则在 iGame 列表中显示的名称会与配置不一致。

2. **时间字段**：`previewTime` 和 `endShowTime` 在浏览器提交时都是 0，不要误填时间戳。

3. **Payload 格式**：必须是直接的 JSON 数组 `[{...}]`，不是 `{"activities": [{...}]}`。

4. **撤回后无法删除**：撤回的活动状态变为 19，但 DELETE 接口路径格式可能不同，暂未找到正确的删除方式。

---

## 8. 相关工具

- **iGame Skill**：`~/.agents/skills/igame-skill/`
- **认证配置**：`~/.igame-auth.json`
- **API 探索**：`node igame-query.js ls "activity"` 查看活动模块接口
