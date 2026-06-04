---
name: igame-actv
description: 从 Google Sheet 甘特图读取节日活动排期，通过 iGame API 批量部署活动。支持 schema 分服、灰度服、跨服分组、多期活动。触发条件：(1) 提到"部署活动"、"活动部署"、"甘特图"、"排期"，(2) 提到"节日活动"+"上线/部署/提交"，(3) 需要从 Google Sheet 读取活动配置并部署到 iGame。
---

# iGame Activity Deployment Skill

**Skill 路径**: `~/.claude/skills/igame-actv`

## 前置依赖

使用前请确认以下工具已安装，缺少则提示用户自行安装：

1. **igame-skill** — iGame 平台 API 查询工具（`~/.claude/skills/igame-skill`）
   - 提供 `igame-query.js`，用于调用 iGame 接口
   - 需要认证文件 `~/.igame-auth.json`，过期时运行 `bash ~/.claude/skills/igame-skill/scripts/setup-auth.sh`
2. **gws CLI** — Google Workspace CLI，用于读取 Google Sheets
   - 安装: `npm i -g @anthropic-ai/gws`
   - 需要 Google OAuth 授权

检查方式：
```bash
# 检查 gws
which gws || echo "请安装 gws: npm i -g @anthropic-ai/gws"
# 检查 igame-skill
ls ~/.claude/skills/igame-skill/scripts/igame-query.js || echo "请安装 igame-skill"
# 检查认证
cat ~/.igame-auth.json || echo "请运行 bash ~/.claude/skills/igame-skill/scripts/setup-auth.sh"
```

## 工作流

### Step 1 — 列出活动

```bash
node ~/.claude/skills/igame-actv/deploy-from-gantt.js \
  --sheet <spreadsheet_id> --tab "<页签名>" --list
```

从 Google Sheet URL 提取 spreadsheet_id（`/d/<id>/edit`）。输出所有活动的序号、configId、名称、负责人、跨服类型、schema、排期。

### Step 2 — 确认部署参数（必须）

**部署前必须向用户确认以下参数，不得自行猜测：**
- 活动名称和 configId
- 排期（startTime / endTime）
- 服务器范围（schema + 是否含灰度）
- acrossServer（0=单服 / 1=跨服）
- acrossServerRank（0=无跨服排名 / 1=有跨服排名）

### Step 3 — 部署

**部署前必须阅读并逐项检查 `DEPLOY_CHECKLIST.md`，不可跳过。**

确认后通过 igame-query.js 调用 `/activity/submit` API 部署：

```bash
node ~/.claude/skills/igame-actv/deploy-from-gantt.js \
  --sheet <id> --tab "<页签名>" --deploy 1,3,5-8
```

加 `--dry-run` 仅预览不实际部署。

## 服务器配置

`server-config.json` 包含 schema 分服、灰度服列表、跨服分组数据。

**注意：server-config.json 不会自动更新。** 每次节日活动开始前，请提醒用户确认服务器分组数据是否为最新版本。如果有新开服、合服、schema 调整或跨服分组变更，需要用户提供新的 yych-tools 分享链接并重新拉取：

```bash
node ~/.claude/skills/igame-actv/scripts/fetch-server-config.js <share_id>
# 例: node ~/.claude/skills/igame-actv/scripts/fetch-server-config.js y6m1kl
```

拉取后务必检查各 schema 服务器数量是否符合预期。

### Schema 服务器规则

| Schema | 服务器数 | 灰度处理 |
|--------|---------|---------|
| 6（纯） | 81（排除灰度） | 灰度单独部署 |
| 4-6 | 126（含灰度） | 灰度属于 schema6，不排除 |
| 3-5 | 51 | 无灰度服 |
| 5 | 11 | 无灰度服 |
| 4 | 22 | 无灰度服 |
| 3 | 18 | 无灰度服 |
| 全服（无标识） | 132（排除灰度） | 灰度单独部署 |

### 跨服类型

- **单服**: `acrossServer=0`, 所有服务器放一个组 `[allServers]`
- **跨服-全服**: `acrossServer=1`, 所有服务器放一个组 `[allServers]`
- **跨服-分组**: `acrossServer=1`, 使用 `crossGroups` 预定义分组

### 关键 API 细节

- 部署端点: `activity/add_activity/submitActivity`（POST）
- 请求体必须是**直接 JSON 数组** `[{...}]`，不是 `{"activities":[...]}`
- `previewTime` 和 `endShowTime` 是 int32（分钟），默认用 `0`
- **时间戳必须用 UTC**，不是北京时间。例如 `4-08 00:00 UTC` = `Date.UTC(2026, 3, 8, 0, 0, 0)` = `1775606400000`
- 单服格式: 所有服务器在一个数组 `[[s1,s2,...]]`，不是 `[[s1],[s2],...]`
- 限时抢购等多期活动: 每期单独提交，各自 24h（startTime ~ startTime+24h）

### 直接调用 igame-query.js 部署单服活动

当需要部署到指定单服（如测试服 2000302）时，可以直接调用 API，无需使用 deploy-from-gantt.js：

```javascript
const { execSync } = require('child_process');
const IGAME_QUERY = 'C:/Users/linkang/.claude/skills/igame-skill/scripts/igame-query.js';

const payload = [{
  activityConfigId: '21115750',  // 注意是 activityConfigId，不是 configId
  name: '活动名称',
  startTime: 1775606400000,      // UTC 毫秒时间戳
  endTime: 1775865600000,
  previewTime: 0,
  endShowTime: 0,
  acrossServer: 0,               // 0=单服, 1=跨服
  acrossServerRank: 0,
  servers: [[2000302]]           // 注意是 servers，不是 serverIds；单服用 [[id]]
}];

// 必须用命令行参数传递 JSON，不支持 stdin
const payloadStr = JSON.stringify(JSON.stringify(payload));
const cmd = `node "${IGAME_QUERY}" write "activity/add_activity/submitActivity" ${payloadStr}`;
const result = execSync(cmd, { encoding: 'utf8' });
const json = JSON.parse(result);
// json.success === true && json.data 包含活动 id
```

**重要**：
- 参数名是 `activityConfigId`（不是 `configId`）
- 参数名是 `servers`（不是 `serverIds`）
- JSON 必须通过命令行参数传递，不支持 stdin 输入
- Windows 下需要双重 JSON.stringify 来正确转义

### 下线活动：撤回 vs 取消

**任务分两类：**
- **部署申请** —— `submit` 接口（前面工作流已覆盖）
- **下线活动** —— 看活动当前状态分两种：

| 活动当前状态 | 用什么 | 接口 | 批量？ | 后续 |
|------|--------|------|-------|------|
| **部署申请状态**（未上线，审核中/已审未到时间） | **撤回（recall）** | `activity/operation/recall` | ❌ 单 id | 申请退回，可改可弃，需要的话重新走审批 |
| **上线中状态**（活动已经在跑） | **取消（cancel）** | `activity/operation/cancel` | ✅ 批量 | 活动作废，无法恢复，要再上需重新部署 |

> ⚠️ 历史事故：2026-04-08 把"还在审批中、应该撤回"的活动错用了 cancel，
> 导致申请被作废。**未上线 → recall，已上线 → cancel，不要混。**

#### recall（撤回未上线的部署申请）

适用于活动还在 **部署申请状态**（审核中、已审核但未到 startTime）。撤回后申请回到可编辑/重提状态。

```javascript
// recall 一次只能撤一个 id
const params = { id: 7840 };
const cmd = `node "${IGAME_QUERY}" write "activity/operation/recall" ${JSON.stringify(JSON.stringify(params))}`;

// 多个申请需循环调用
for (const id of [7840, 7841, 7842]) {
  const p = JSON.stringify(JSON.stringify({ id }));
  execSync(`node "${IGAME_QUERY}" write "activity/operation/recall" ${p}`);
}
```

#### cancel（取消已上线的活动）

适用于活动已经处于 **上线中状态**。取消后活动彻底作废，玩家侧立即下线。

```javascript
const params = {
  ids: '7840,7841,7842',  // 逗号分隔
  reason: '活动需提前下线'
};
const cmd = `node "${IGAME_QUERY}" write "activity/operation/cancel" ${JSON.stringify(JSON.stringify(params))}`;
```

**注意**：`del` 接口（DELETE 方法）对待审核状态的活动无效。下线活动请按上表选 recall 或 cancel。

## 部署检查清单（必须遵守）

### 提交前二次校验

**在提交任何活动之前，必须对照预览文件逐项核对：**

1. **服务器数量校验** - 提交时打印的服务器总数必须与预览一致
   - 如果预览显示"147服"，提交时必须是147服
   - 如果数量不符，立即停止，排查原因

2. **分组数量校验** - 跨服分组活动的分组数必须与预览一致
   - 如果预览显示"12组"，提交时必须是12组

3. **日期校验** - startTime/endTime 必须与预览的排期一致

### 灰度服处理规则

**CSV 分组数据结构说明：**
- `Schema 6 分组`：7组共81服，**不含灰度服**
- `Schema 3-5 分组`：5组共54服，无灰度服
- `灰度分组`：1组共12服，**单独存放**
- `全服一组`：147服，含灰度服

**非灰度活动（含灰度服）的正确处理：**

| 活动类型 | 正确做法 | 服务器数 |
|---------|---------|---------|
| S6分组活动 | Schema 6 分组(7组81服) + 灰度分组(1组12服) = 8组93服 | 93 |
| S6+S3-5分组活动 | Schema 6 分组 + 灰度分组 + Schema 3-5 分组 = 13组147服 | 147 |
| S5+S6分组活动 | Schema 5 分组 + Schema 6 分组 + 灰度分组 | 107 |

**错误示例（已发生过）：**
```javascript
// ❌ 错误：直接用 Schema 6 分组，漏掉灰度服
const servers = groups["Schema 6 分组"]; // 只有81服

// ✓ 正确：合并灰度分组
const servers = [...groups["Schema 6 分组"], groups["灰度分组"][0]]; // 93服
```

**灰度活动（排除灰度服）的处理：**
- 从分组中过滤掉灰度服：`servers.filter(s => !grayServers.includes(s))`

### 提交后验证

每次提交后检查返回的 id，确认 success=true。如果服务器数与预期不符，立即取消重新提交。

### 常见错误及教训

| 错误 | 原因 | 正确做法 |
|-----|------|---------|
| 服务器数少了12个 | CSV分组不含灰度服，直接使用未合并 | 非灰度活动需合并灰度分组 |
| 时间错误 | 用北京时间而非UTC | 始终用 Date.UTC() |
| 跨服类型错误 | 未仔细看甘特图的跨服列 | 逐条核对跨服类型 |
| 多期活动只提交一期 | 未注意甘特图的多期标记 | 检查是否有 `|` 分隔的多期 |
| cancel 和 recall 混淆 | 不了解状态机 | 都是"下线活动"，按状态分：**部署申请状态 → recall**；**上线中状态 → cancel** |
