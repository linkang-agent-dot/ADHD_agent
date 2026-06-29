# X3 iGame 活动批量部署 skill

把活动**一次性批量提交到 iGame 后台**，不用一组一组手动点。支持：

- ✅ 跨服 + 单服两种活动类型
- ✅ **自动聚合**同 cfg+同时间的多组到 1 个活动 ID（实战 17 → 8）
- ✅ 生产/测试双环境
- ✅ dry-run 预览不发 / 批量下架
- ✅ 已实战验证：2026-06-26 一次性上线 17 组 6/29 活动全成功

## 5 分钟上手（用户视角）

### 你需要告诉 Claude 哪些信息

| # | 字段 | 必填？ | 例 |
|---|---|---|---|
| 1 | **环境** | ✅ | "生产" / "线上" / "测试" / "dev" |
| 2 | **活动配置 id (configId)** | ✅ | `102001` 风暴 / `101901` 入侵 / `100702` 酒馆 / `103001` S1 / `300601` S6（活动名也能识别） |
| 3 | **是否跨服** | ✅ | "跨服" / "单服" / "全服"（看活动类型默认能推） |
| 4 | **服务器+分组** | ✅ | 跨服多组：`1870/1880/1890 一组，1900/1910 一组` / 单服全服：`60 服全跑` |
| 5 | **开始时间** | ✅ | "6/29 0 点 UTC" / "北京 6/29 早上 8 点" / "按 sheet 上的时间" |
| 6 | **结束时间** | ✅ | "7/5 23:59:59 UTC" / "7 天" |
| 7 | **活动名称** | ⬜ 可选 | 不给会按模板自动生成，如 `风暴逐鹿OpenServer_1870,1880,1890` |

### 触发样例 1：上跨服活动

> 帮我在 **X3 生产服**上 **6/29-7/5** 的**风暴逐鹿**，分两组：
> **1870/1880/1890** 一组、**1900/1910** 一组

→ Claude 会：组装 payload → dry-run 给你看 → 你说"发" → 它批量 submit → 汇总返回的活动 id

### 触发样例 2：按 sheet 批量

> 把跨服匹配 sheet 6/29 那周三线全上 X3 生产：**风暴+S1+S6+酒馆共 17 组**

→ Claude 自动聚合（17 → 8 个 ID），dry-run 预览，确认后批量发

### 触发样例 3：批量下架

> 把刚才那批活动下架，**id 13713-13729**

→ 17 个 id 逐个 `batch_offline`，跑完汇总成功/失败

### 触发样例 4：先在测试服跑通

> 先在**测试服 (dev)** 上跑一遍验证流程，风暴 cfg=102001 配两组 100,220 和 400,440

→ 用测试服 host + 测试服 auth，不动线上

### 跟 Claude 对话的小提示

- 不确定服 ID 怎么填？直接说"按跨服匹配 sheet 上 6/29 那批"
- 不确定时间窗？说"跟前两周一样"或"按 sheet 时间走"
- 看完 dry-run 不满意？让 Claude 直接改某个组/时间，重新预览

## 文件清单

```
skill-igame-x3-activity-deploy/
├── README.md                          # 本文档
├── SKILL.md                           # 触发词 + 元信息 + 对话样例
├── submit-cross-server.js             # 核心脚本 (单文件, node 直接跑)
└── examples/
    ├── 0629-prod-batch17.json         # 跨服 17 条原始样例
    ├── 0629-aggregated.json           # 聚合后 8 条 (推荐参考)
    └── single-server-template.json    # 单服活动样例
```

## 部署（新机器约 10 分钟）

### 1. Node.js 18+

```bash
node -v   # 需要 v18+ (用 global fetch)
```

### 2. iGame 鉴权文件

iGame token 约 10 天过期, 过期就重新走一遍这套流程。

**生产环境**（操作 X3 真实玩家服）：

1. 浏览器登录 https://igame.tap4fun.com（企业微信扫码）
2. F12 → Console，运行：
   ```js
   copy(JSON.stringify({
     token: localStorage.getItem('ark_token'),
     clientId: localStorage.getItem('ark_clientId') || '<浏览器自动算>',
     gameId: '1090',
     regionId: '201'
   }, null, 2))
   ```
   > clientId 没法纯 JS 取（要算浏览器指纹），从已有的 auth 文件抄一份或运行 igame-skill 的 `setup-auth.sh`
3. `~/.igame-auth.json` 写入这段 JSON

**测试环境**（先调试用，无玩家影响）：

1. 浏览器登录 https://igame-dev.tap4fun.com
2. 同样取 token，写到 `~/.igame-auth-dev.json`（注意是 `-dev` 后缀，跟生产分开）

文件示例：

```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "clientId": "1Z7rjoIGwH5ZOFkPCiMLfng==IrPWyuO79OVJzo5XlDAHOQ==",
  "gameId": "1090",
  "regionId": "201"
}
```

### 3. 验证鉴权

```bash
node submit-cross-server.js --env dev --dry-run --file examples/0629-prod-batch17.json
```

只读取 payload 列表 + 时间换算预览，不发送。如果报 `auth 文件不存在` 或后续 401，回到步骤 2。

## 使用流程

### 一、批量上线

**第 1 步：准备 payload JSON 数组**

按下面 schema 写一个 JSON 文件（参考 `examples/0629-prod-batch17.json`）：

```json
[
  {
    "activityConfigId": "102001",
    "previewTime": 0,
    "startTime": 1782691200000,
    "endTime": 1783295999000,
    "endShowTime": 0,
    "acrossServerRank": 1,
    "acrossServer": 1,
    "name": "风暴逐鹿OpenServer_1870,1880,1890",
    "servers": [["1870", "1880", "1890"]]
  }
]
```

字段说明：
| 字段 | 类型 | 说明 |
|---|---|---|
| `activityConfigId` | string | 活动配置 ID（见下方常用 cfg） |
| `previewTime` | int | 预告时长（毫秒），通常 0 |
| `startTime` | int | **UTC 时间戳（毫秒）** — `Date.UTC(2026,5,29)` |
| `endTime` | int | UTC 时间戳 |
| `endShowTime` | int | 活动结束后展示时长，通常 0 |
| `acrossServerRank` | int | 跨服排名，1=是 |
| `acrossServer` | int | 跨服活动，1=是 / 0=单服 |
| `name` | string | iGame 后台显示名，建议 `"<活动名>OpenServer_<服列表>"` |
| `servers` | `[[string]]` | **二维数组**：外层=独立活动组，内层=服 ID 字符串列表 |

**第 2 步：预览（dry-run，无副作用）**

```bash
node submit-cross-server.js --env prod --file payloads.json --dry-run
```

打印所有 payload 的时间换算 + 服列表，确认无误后继续。

**第 3 步：正式上线**

```bash
node submit-cross-server.js --env prod --file payloads.json
```

执行后：
- 逐条 POST 到 `webgw-cn.tap4fun.com/ark/activity/submit`
- 每条间隔 200ms（避免压库）
- 终端打印每条成功的 id 或失败原因
- 完整结果存到 `payloads-results-<时间戳>.json`（含全部 id，可用于下线）

### 二、批量下线

```bash
node submit-cross-server.js --env prod --offline --ids 13713,13714,13715
```

把要下架的 id 用逗号分隔传给 `--ids`。

### 三、自动聚合（推荐！默认开启，节省大量活动 ID）

**iGame 支持 1 个活动 ID 包含多组 servers**——如果你提供多条 payload，**同 cfg + 同 startTime + 同 endTime** 的会自动合并到 1 个 submit、1 个活动 ID。

实战数据：6/29 周 17 条 payload → 聚合后 **8 个活动 ID**（节省 9 个，56% 缩减）：

| 类型 | 原 ID 数 | 聚合后 | 原因 |
|---|---|---|---|
| 102001 风暴 | 2 | **1** | 时间相同，2 组 servers 合并 |
| 103001 S1 | 6 | **1** | 时间相同，6 组合并 |
| 300601 S6 | 4 | **1** | 时间相同，4 组合并 |
| 100702 酒馆 | 5 | **5** | 时间各不相同（D33 节奏），无法聚合 |

**聚合规则**：
- 跨服活动（acrossServer=1）：保留多组结构 → `servers:[["a","b"],["c","d"]]`（iGame UI 显示"共 2 组"）
- 单服活动（acrossServer=0）：所有服合 1 大组 → `servers:[["a","b","c","d"]]`（iGame UI 显示"共 N 个"）

**关闭聚合**（如果你需要每组独立 ID）：

```bash
node submit-cross-server.js --env prod --file payloads.json --no-aggregate
```

**实战样例**：

- `examples/0629-prod-batch17.json` 原始 17 条
- `examples/0629-aggregated.json` 聚合视角 8 条（同输入，预聚合好的产物）

跑 dry-run 看聚合效果：

```bash
node submit-cross-server.js --env prod --file examples/0629-prod-batch17.json --dry-run
# 会打印: 📦 自动聚合: 17 条 → 8 条 (节省 9 个活动 ID)
```

### 四、切换测试服

把所有 `--env prod` 改成 `--env dev` 即可，会自动切：
- host → `ms-inner-gateway-dev.tap4fun.com`
- auth → `~/.igame-auth-dev.json`
- origin → `https://igame-dev.tap4fun.com`

## 常用 X3 cfg（**跨服 vs 单服**两种类型）

### 跨服活动 (acrossServer=1, acrossServerRank=1)

| configId | 名称 | 时长 | 说明 |
|---|---|---|---|
| 102001 | 风暴逐鹿 | 7 天 | 周轮替之一 |
| 101901 | 世界入侵 | 8 天 | 周轮替之一 |
| 100702 | 酒馆争霸 | 6 天 | 跨服酒馆 |
| 103001 | 魔海回声 S1 | 28 天 | KVK 赛季 |
| 103002~5 | S2~S5 | 28 天 | KVK 赛季 |
| 300601 | 魔海回声 S6 | 28 天 | 最新赛季 |
| 106502 | 疯狂夺宝总动员 | 跨服 | |

### 单服活动 (acrossServer=0, acrossServerRank=0)

| configId | 名称 | 说明 |
|---|---|---|
| 100701 | 最佳酒馆 | 单服酒馆 |
| 109001 | 飞速发展 | 新服礼包，每个服 1 份 |
| 100597 | 世界杯累充 | 全服活动 |
| 101403 | 世界杯签到 | 全服活动 |
| 101339 | 荣耀兑换所 | 全服活动 |
| 102243 | 世界杯通行证 | 全服活动 |
| 101826 | 承诺的碎片 | 全服活动 |
| 102236 | 为誓言而战 | 全服活动 |
| 105011 | 许愿池 | 全服活动 |
| 105603 | 夏日柔情海湾 | 全服活动 |
| 106101 | 夏日装饰礼包 | 全服活动 |
| 101337 | 绽放之礼 | 全服活动 |

### 跨服 vs 单服 payload 对比

```json
// 跨服: 一组多服打跨服 (acrossServer=1)
{
  "activityConfigId":"102001","name":"风暴逐鹿OpenServer_1870,1880,1890",
  "previewTime":0,"startTime":<utc>,"endTime":<utc>,"endShowTime":0,
  "acrossServer":1,"acrossServerRank":1,
  "servers":[["1870","1880","1890"]]
}

// 单服: 一组里多个服各跑一份独立活动 (acrossServer=0)
{
  "activityConfigId":"109001","name":"飞速发展OpenServer_2280,2290",
  "previewTime":0,"startTime":<utc>,"endTime":<utc>,"endShowTime":0,
  "acrossServer":0,"acrossServerRank":0,
  "servers":[["2280","2290"]]
}

// 单服全服: 60 服共同活动 (acrossServer=0)
{
  "activityConfigId":"101403","name":"世界杯签到",
  "previewTime":0,"startTime":<utc>,"endTime":<utc>,"endShowTime":0,
  "acrossServer":0,"acrossServerRank":0,
  "servers":[["1170","1270","1310","1350",...60个服]]
}
```

**关键差异只 2 个字段**：`acrossServer` + `acrossServerRank`。servers 结构完全一样（都是 `[["serverId",...]]` 二维字符串）。

> 单服活动里那些 60 服列表会**逐服独立部署**——iGame 内部把它当成 60 个单服活动，但 submit 时打包成 1 个 payload。所以**一行 servers 列表 = 1 个 submit，不需要拆成 60 行**。

## ⚠️ 关键坑（踩过的，别再踩）

### 1. iGame 时间是 UTC 不是北京时间

**最容易翻车的点**。iGame 后台 UI 显示和录入都按 UTC。

- ❌ 错：`new Date(2026, 5, 29).getTime()` → 北京 6/29 0:00 → UTC 6/28 16:00 → UI 显示 06.28 16:00（错位 8h）
- ✅ 对：`Date.UTC(2026, 5, 29)` → UTC 6/29 0:00 → UI 显示 06.29 00:00 → 玩家实际 北京 6/29 08:00 看到活动

跨服匹配 sheet 上写的 `2026.06.29 00:00:00` **本来就是 UTC**，按 UTC 算时间戳。

### 2. payload 顶层是数组不是包装对象

- ❌ `{"activities":[{...}], "regionId":""}` → HTTP 400「请求参数验证错误」
- ✅ `[{...}]` 直接数组

### 3. servers 是二维字符串数组

外层=活动组（独立部署的一组），内层=该组的服 ID。

- ✅ `[["1870","1880","1890"]]` — 1 个跨服组、3 个服一起打
- ❌ `["1870","1880","1890"]` — 一维数组会报错
- ❌ `[[1870,1880,1890]]` — 整数也会报错

### 4. previewTime / endShowTime 写 0

iGame UI 默认就是 0，别自作主张填 startTime/endTime（之前试过会 400）。

### 5. iGame token 约 10 天过期

每次脚本报 401，先去 iGame UI 刷一下 token（F12 Console 取 `ark_token`），写到 auth 文件。

### 6. 生产环境免审批直接生效（X3 龚亮权限）

**X3 iGame submit 出去立刻对玩家可见**，没有"待审核"二次拦截。所以：
- 上线前**用 dry-run** 看一遍 payload
- 大批量上线前先**单组试跑**（如 1 个 cfg + 1 组），UI 上核对无误再批发剩下
- 测试环境（dev）随便玩，不影响线上

## 故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| `auth 文件不存在` | 没建/路径错 | 见「部署 步骤 2」|
| HTTP 401 | token 过期 | 重新去 iGame UI 取 token |
| HTTP 400 「请求参数验证错误」 | payload 字段不对 | 对照「字段说明」+「关键坑」逐项核 |
| HTTP 404 | host 或路径错 | 确认 `--env` 选对了；prod=webgw-cn, dev=ms-inner-gateway-dev |
| 时间显示比预期少 8h | UTC vs 北京时间混淆 | 见「关键坑 1」 |
| 同一组 servers 拆成多个活动 | servers 应该是二维 | 见「关键坑 3」 |

## 跨服匹配 sheet 转 payload

跨服匹配 sheet 上"后台分组输出"列里每行 `[1870,1880,1890]` 就是一组 `servers[0]`。手工转一下：

| sheet 列 | payload 字段 |
|---|---|
| 活动 id | `activityConfigId` |
| 活动开始时间 | `startTime`（注意 UTC 转换） |
| 活动结束时间 | `endTime` |
| 后台分组输出每行 `[X,Y]` | 每行变成 1 个 payload，`servers:[["X","Y"]]` |

举例：sheet 的 S1 雷娜 6 组分组 → 6 个 payload。

## 已实战部署样例

`examples/0629-prod-batch17.json` 是 2026-06-26 批量部署的 17 组 6/29 跨服活动完整 payload，可直接拿来改时间戳/服列表/cfg 复用。

部署结果：
- 风暴逐鹿（102001）×2 → id 13713-13714
- S1 雷娜（103001）×6 → id 13715-13720
- S6 魔海回声（300601）×4 → id 13721-13724
- 酒馆争霸（100702）×5 → id 13725-13729

## 联系人

X3 项目原作者：龚亮。skill 改自 x2 项目 `igame-auto-deploy`。有问题在 SkillsMP 评论或 GitLab issue。
