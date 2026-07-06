---
name: test-env-prepare-x3
description: X3 测试环境准备工具。支持 GM 指令执行、加道具、改时间、部署活动等。当用户说「帮我执行 GM」「330 服加道具」「X3 开活动」「改服务器时间」等时触发。
---

# X3 测试环境准备 Skill

> 通过 iGame 网关执行 GM 指令，支持 dev/beta 环境。

## 关键规则（必读）

0. **ID 自动记录** — 每次测试过程中查到或用到新的配置 ID（道具、英雄、活动、兵种等），如果 `ID_REFERENCE.md` 中没有，必须主动追加记录，不等用户提醒。

1. **GM JSON 格式** — gmCommand 内部字段：
   ```json
   {"cmd": "additem", "args": ["230004", "50", "0"], "playerIds": "14000", "serverIds": "330"}
   ```
2. **`serverIds` 和 `playerIds` 是字符串**，多个用逗号分隔，不是数组。
3. **不加中文分号** — X3 服务端直接 JSON 反序列化，加 `；` 会报错。
4. **cmd 全小写** — 服务端自动 `.ToLower()` + 补 `gm` 前缀。传 `additem` 等价于 `gmadditem`。
5. **必须确认 playerIds** — 玩家级指令必须有 playerIds，否则走服务器级分支不会对玩家生效。未提供时主动询问。
6. **iGame success 不代表 GM 成功** — 必须查 detail 接口的 `contents[].returnInfo` 判断实际结果。

## 执行方式

### iGame 网关

| 环境 | 前端地址 | 提交地址 | 查询结果 |
|------|----------|----------|----------|
| dev | `https://igame-dev.tap4fun.com` | `https://ms-inner-gateway-dev.tap4fun.com/ark/gm-operate/add` | `.../detail?id=xxx` |
| beta | `https://igame-qa.tap4fun.com` | `https://ms-inner-gateway-qa.tap4fun.com/ark/gm-operate/add` | `.../detail?id=xxx` |

请求体：
```json
{
  "operateType": 3,
  "gmCommand": ["{\"cmd\": \"additem\", \"args\": [\"230004\", \"50\", \"0\"], \"playerIds\": \"14000\", \"serverIds\": \"330\"}"]
}
```

Header 要求：
```
authorization: Bearer <token>
clientid: <clientId>
gameid: 1090
regionid: 201
content-type: application/json
```

### 脚本执行

```bash
cd .claude/skills/test-env-prepare-x3

# 加道具
python3 scripts/gm_execute.py --server 330 --player 14000 --cmd additem --args "230004,50,0" --env beta

# 服务器级指令（不需要玩家 ID）
python3 scripts/gm_execute.py --server 330 --cmd deployserveractivity --args "106002,1786536352,1787141152" --env beta

# 多个玩家
python3 scripts/gm_execute.py --server 330 --player "14000,14001" --cmd additem --args "230004,100,0" --env beta
```

### Python 调用

```python
import sys, os
sys.path.insert(0, os.path.expanduser(".claude/skills/test-env-prepare-x3/scripts"))
from gm_execute import load_auth, make_headers, submit_gm, query_result

token, client_id = load_auth("~/.igame-credentials.json")
headers = make_headers(token, client_id, "beta")

gm_id = submit_gm("beta", headers, "additem", ["230004", "50", "0"], "330", "14000")
result = query_result("beta", headers, gm_id)
print(result)
```

## 查询执行结果

提交后通过 detail 接口查询：

```
GET /ark/gm-operate/detail?id=<id>
```

关键字段：
- `contents[].status`: true=到达服务端, false=转发失败
- `contents[].returnInfo`: GM 执行结果 JSON
- `contents[].errMsg`: 错误信息

returnInfo 示例：
```json
[{"uid":14000,"gmResult":"errcode: 0, itemCfgID: 230004 itemID: 230004 curCount: 50","errCode":0}]
```

## 常用 GM 指令

### 道具/资源

| cmd | args | 说明 |
|-----|------|------|
| `additem` | cfgID, num, quality | 加道具/资源（quality 默认 0） |

常用 ID 见 [ID_REFERENCE.md](ID_REFERENCE.md)。示例：`additem 1002,50000,0` = 加 50000 钻石

### 成长

| cmd | args | 说明 |
|-----|------|------|
| `buildingsmaxlevel` | — | 所有建筑满级 |
| `addsoldier` | type, level, count | 加士兵 |
| `cureallsoldier` | — | 治疗所有士兵 |

### 时间

| cmd | args | 说明 |
|-----|------|------|
| `setservertimebydhms` | day, hour, min, sec, target | 推进服务器时间（target: 0=同步, 1=仅Game, 2=仅Center；不支持回退）。**需要 playerIds**（玩家级 GM），推荐 target=1 |
| `setservertime` | timeStr | 设置 Play+Map 服务器时间，格式 `2023-04-12/12:00:00`。**需要 playerIds** |
| `setcenterandkvkservertime` | timeStr | 设置 Center+KVK 时间，格式 `2023-04-12/12:00:00`。**Center 级 GM**，igame 需路由到 Center 服 |
| `setservertimeoffset` | timeStr | 设置偏移时间（重启后保持），格式同上。**需要 playerIds** |
| `getservertime` | — | 获取当前服务器时间。**需要 playerIds** |
| `setkvkservertime` | kvkServerID, timeStr | 仅改 KVK 时间，格式 `2023-04-12/12:00:00` |
| `clearservertimeoffset` | — | 清除时间偏移，下次重启恢复真实时间 |

#### 改整套集群时间

跨服活动（GVG/KVK/ZVZ）要求 Play、Map、Center、KVK 时间一致。改时间需两个 GM 组合使用，**间隔数秒内**：

1. `setcenterandkvkservertime` timeStr — 改 Center + 所有 KVK（Center 级 GM）
2. `setservertime` timeStr — 改 Play + Map（需要 playerIds）

两条 GM 先后执行，不能间隔太长，否则时间差会导致活动状态判断异常。

注意：`setservertimebydhms` target=0 理论上也能同时推 Game+Center，但需要 CenterService 部署了包含 `GMSetCenterServerTimeByDHMS` 的代码版本（非 Hotfix，需重新部署镜像）。

#### 物理机时间调整

GM 改的是进程内逻辑时间，重启后会丢失（除非用了 `setservertimeoffset`）。如需**永久改时间**（如压测跨天、模拟长周期），可直接改物理机系统时间。

通过 JumpServer SSH 连接物理机执行 `sudo date -s`：

```python
import sys, os
sys.path.insert(0, os.path.expanduser(".claude/skills/test-env-prepare-x3/scripts"))
from jumpserver_client import shift_days_sync, set_absolute_time_sync, disable_ntp_sync, check_time_sync

# 先关 NTP 防止时间被自动同步回来
disable_ntp_sync("x3-beta-qa-001-sv-x3a3")

# 往后推 5 天
shift_days_sync("x3-beta-qa-001-sv-x3a3", 5)

# 或设置绝对时间
set_absolute_time_sync("x3-beta-qa-001-sv-x3a3", "2026-08-15 10:00:00")

# 查看当前时间
check_time_sync("x3-beta-qa-001-sv-x3a3")
```

**可调时间的物理机：**

| JumpServer 主机名 | IP | 对应服务 |
|---|---|---|
| `x3-beta-qa-001-sv-x3a3` | 10.22.64.80 | CenterService_62, Play 210/220/230, Map 211/221/231 |
| `x3-beta-qa-002-sv-x3a3` | 10.22.64.83 | CenterService_65, Play 500/510, Map 501/511, KvkMap 900 |
| `x3-beta-qa-003-sv-x3a3` | 10.22.64.82 | CenterService_63, Play 310/320/330, Map 311/321/331, KvkMap 930 |

**注意事项：**
- 改物理机时间会影响该机器上**所有服务**（同主机多个服同时生效）
- 改前先关 NTP（`disable_ntp_sync`），否则 chronyd 会把时间拉回来
- 改完测试后记得恢复（`reset_time_to_now_sync` 或用绝对时间设回当前真实时间）
- beta-001 不在列表中（非 QA 专属机器，不建议改时间）

### 活动

#### iGame 活动管理（推荐方式，跨服活动必须用这个）

```bash
# 创建跨服活动（220+230 共同参与）
python3 scripts/igame_activity.py create --cfg-id 100702 --name 酒馆争霸 --servers 220,230 --start 1790557200000 --end 1791162000000

# 查询活动列表
python3 scripts/igame_activity.py list --size 5
```

Python 调用：
```python
from igame_activity import load_auth, _headers, submit_activity, list_activities

token, client_id = load_auth()
headers = _headers(token, client_id, "beta")
result = submit_activity("beta", headers, "100702", "酒馆争霸", [["220","230"]], start_ms, end_ms)
```

API：`POST /ark/activity/submit`，body 是**数组**（非对象），每个元素含 activityConfigId/name/servers/startTime/endTime/acrossServer/acrossServerRank/endShowTime/previewTime。

#### GM 命令方式（单服活动或 Center 级 GM 已部署时）

| cmd | args | 说明 |
|-----|------|------|
| `deployserveractivity` | activityCfgId, startTime, endTime | 部署**单服**活动（服务器级 GM） |
| `addcrossserveractivitybycfgid` | cfgId, durationMinutes, serverID | 部署**跨服**活动（Center 级 GM）。durationMinutes≤0 走配置默认时长，serverID=0 不指定 |
| `removecrossserveractivitybycfgid` | cfgId | 删除跨服活动（测试重跑前清残留） |
| `kvkactivityenternextstate` | activityId | KVK 进入下一状态 |
| `fixonlineactivities` | — | 修复线上活动 |

> 注意：`addcrossserveractivitybycfgid` 需要 CenterServer 镜像包含该 GM 代码，功能分支可能缺失。优先用 igame 方式。

#### 活动时间规则

`deployserveractivity` 的 startTime/endTime 是 **Unix 秒级时间戳**（不是日期字符串）。

**服务器时间可能被推进过**，与本地系统时间不一致。必须：
1. 先执行 `getservertime`（需 playerIds）获取服务器当前时间字符串
2. 将返回的 `CurServerTime: yyyy-MM-dd/HH:mm:ss` 用 `calendar.timegm` 转为准确时间戳
3. 以此为 startTime，加上持续时长得到 endTime

```python
import calendar
from datetime import datetime

# 从 getservertime 返回的字符串解析
server_time_str = "2026-08-12/12:17:03"
dt = datetime.strptime(server_time_str, "%Y-%m-%d/%H:%M:%S")
start_ts = calendar.timegm(dt.timetuple())
end_ts = start_ts + 7 * 86400  # 7天
```

**禁止手动估算时间戳** — 容易算错导致活动时间偏移。

#### 跨服活动开启流程

**GVG（公会对战）** — activityCfgId: `105301`，持续 12 天
1. 在目标服开启活动（跨服/不跨服均可）
2. 参与条件：6 个联盟报名（代码写死不可改）+ 每联盟 10 人报名（可配置改为 1）
3. 创建 6 个联盟，分别报名
4. 依次改时间到每阶段剩余 1 分钟，自然跨过。改时间用组合 GM：
   - `setcenterandkvkservertime` — 改 Center+KVK
   - `setservertime` — 改 Play+Map（间隔数秒内）
5. 每轮胜利邮件发奖，五轮全部完成后按排名发奖

**KVK（跨服战）** — activityCfgId: `102001`，持续 8 天
1. 在**两个服**开启 KVK 跨服活动
2. 同时调 Game 和 Center 时间至活动第 5 天 23:59，自然跨到第 6 天
3. 第 6 天再调时间跨过 15 分钟准备期，通过活动界面入口进入 KVK

**ZVZ（海域争夺）** — activityCfgId: `101901`，持续 9 天
1. 前置：用 GM 开启所有海域 + 合并海域（在 GM 面板搜"海域"，先点"开放海域"多次，再"合并海域"依次合并 101/102/103，共执行 3 次）
2. 在**两个服**开启 ZVZ 跨服活动
3. 调 Game 时间至活动第 5 天 23:59，自然跨到第 6 天
4. 通过活动界面入口进入 ZVZ（遇到"岛屿未创建"提示时进一下世界地图）

### 任务

| cmd | args | 说明 |
|-----|------|------|
| `dailytaskcompleteall` | — | 完成所有日常任务 |
| `completeallguidechapter` | — | 完成所有章节 |

完整 GM 列表见项目根目录 `x3-gm-commands.md`（471 条服务端 + 109 条客户端）。

## 配置表查询

查询道具 ID、活动 ID 等配置信息（需要 `gdconfig/data/` 目录存在）：

```bash
cd .claude/skills/test-env-prepare-x3

# 按名称搜道具
python3 scripts/config_query.py item --name "宝箱"

# 按 ID 查道具
python3 scripts/config_query.py item --id 230004

# 按名称搜活动（同时搜索备注和显示名）
python3 scripts/config_query.py activity --name "转盘"

# 按 ID 查活动
python3 scripts/config_query.py activity --id 101010
```

配置表来源：`gdconfig/data/*.xlsx`

### 常用表速查

| 需求 | 表名 | 关键字段 | 用途 |
|------|------|---------|------|
| 加道具 | Item.xlsx | ID | `additem` 的 cfgID |
| 开活动 | ActvOnline.xlsx | ID, ActvType, ContentID | `deployserveractivity` 的 activityCfgId |
| 活动具体配置 | Actv{类型}.xlsx | ID = ActvOnline.ContentID | 活动内部奖励/规则 |
| 功能解锁条件 | FunctionUnlock.xlsx | ID, PlayerLvLimit, TimeLimit | 判断入口是否可见 |
| 时间周期 | TimeCycle.xlsx | ID, TriggerType, StartTime | 开服天数/绝对时间门槛 |
| 商店道具 | ShopItemCfg.xlsx | ID | 商店相关 GM |
| 英雄 | Hero.xlsx | ID | 英雄相关 GM |
| 士兵 | Soldier.xlsx | ID, Type, Level | `addsoldier` 参数 |

查表方式：用到时按名称/ID 即时查询，不预加载。

## 查询服务器信息

```
GET /ark/maintain/servers?serverId=<id>
```

返回该服的 PlayService、Gate、MapService 等实例信息（hostName、container、status）。

## 查询玩家信息

```
GET /ark/game_info/<userId>/basic?serverId=<serverId>
```

返回玩家基本信息（等级、战力、联盟、注册时间等）。

## 常见失败

| 现象 | 原因 |
|------|------|
| `entity is not existed` | playerIds 为空或格式错误，走了服务器级分支 |
| `errCode: 6` | GM 方法在目标进程上不存在（如 Center 版本太旧缺少新 GM），需重新部署镜像 |
| `endTime already passed` | 活动 endTime 早于服务器当前时间（服务器时间被推进过） |
| `JsonReaderException: Additional text ；` | gmCommand 末尾加了中文分号 |
| `没有权限` (ark_error_10018) | token 没有 X3 权限，需在 igame 申请 |
| `returnInfo: []` 且无报错 | igame 没把 playerIds 正确传到服务端（检查字段名） |
| `itemCfgID: xxx not existed` | 道具配置 ID 不存在 |

## Kadmin 操作

### 认证

两套环境，独立管理：

| 环境 | API 地址 | Access Key | 服务器范围 |
|------|----------|-----------|-----------|
| **beta** | `https://api-kadmin-beta.tap4fun.com` | `5df3d84a-6960-11f1-ac6a-0242ac130002` | 110-510（TeamId=25） |
| **dev (inner)** | `https://api-kadmin-inner.tap4fun.com` | `bcd84309-6f93-11f1-acba-0242ac1f0003` | 100-105, 1530（前端: kadmin.tap4fun.com） |

调用方式（X3 独立模块，不依赖 P2）：
```python
import sys, os
sys.path.insert(0, os.path.expanduser(".claude/skills/test-env-prepare-x3/scripts"))
from kadmin_api import query_app, deploy_app, offline_app, restart_app, execute_workflow, workflow_history
```

**注意**：`kadmin_api.py` 默认连 beta。操作 dev (inner) 环境时需要手动指定 BASE_URL 和 ACCESS_KEY（或直接用 urllib 调用）。

**禁止 import P2 的 `~/.cursor/skills/kadmin-skill-p2/api.py`** — P2 的 `_base_url()` 指向 `api-kadmin-inner.tap4fun.com`，会把请求打到 P2 组织（TeamId=7），X3 的应用在 `api-kadmin-beta.tap4fun.com`（TeamId=25）。

### 部署应用

```python
from kadmin_api import deploy_app, app_history
import time

# 部署 320 服到 dev 分支（Play + Map 都要部署）
result = deploy_app(name=["default_PlayService_320", "default_MapService_321"], tag="dev")
history_ids = [s["applicationDeployHistoryId"] for s in result["info"]["nameStatus"]]

# 轮询结果
time.sleep(15)
status = app_history(ids=history_ids)
# status=1 表示成功
```

### 常用工作流

**每个 workflow 内部参数（应用名、路径、serverId）是写死的，不能跨服复用。** 执行前必须找到目标服对应的 workflow ID。

#### 热更配置+代码

| 服 | workflow id | workflow name |
|----|-----------|--------------|
| 120 | 1230 | beta-120-热更配置+代码 |
| 210 | 1239 | beta-210-配置热更+代码 |
| 310 | 1231 | beta-310-热更配置+代码 |
| 320 | 1249 | beta-320-热更配置+代码 |
| 330 | 1250 | beta-330-热更配置+代码 |
| 500 | 1235 | beta-500-热更配置+代码 |
| 510 | 1236 | beta-510-热更配置+代码 |

缺失：110、220、230 服暂无热更 workflow。

#### 清服

| 服 | workflow id | workflow name |
|----|-----------|--------------|
| 120 | 1232 | beta-120-下线清服 |
| 210 | 1238 | beta-210-清服 |
| 220 | 1240 | beta-220-清服 |
| 230 | 1243 | beta-230-清服 |
| 310 | 1233 | beta-310-清服 |
| 320 | 1248 | beta-320-清服 |
| 330 | 1234 | beta-330-清服 |

缺失：110、500、510 服暂无清服 workflow。

#### Dev (inner) 环境

**服务器拓扑：**

| 应用 | ID | 默认分支 | 备注 |
|------|-----|---------|------|
| default_PlayService_100 | 688 | dev | |
| default_MapService_101 | 762 | dev | |
| default_PlayService_102 | 887 | dev | |
| default_MapService_103 | 888 | dev | |
| default_PlayService_104 | 1230 | master | |
| default_MapService_105 | 1231 | dev | |
| default_PlayService_1530 | 1326 | dev_union_recommend | |
| default_MapService_1531 | 1327 | dev_union_recommend | |
| default_CenterService_61 | 917 | dev | Play 100/102 共用 |
| default_CenterService_62 | 943 | dev | Play 104/1530 共用 |
| default_Gate_1 | 686 | dev | |
| default_Door_51 | 730 | dev | |
| KvkMapService 901-912 | 916/942-956 | dev/master | |

**关键 Workflow：**

| ID | 名称 | 用途 |
|----|------|------|
| 847 | clear_db | 清服（清数据库） |
| 830 | init_etcd | 初始化 etcd 注册 |
| 1314 | dev-100-定时重启 | 100 服定时重启 |
| 1339 | x3-hotupdate-flow | 热更新流程 |
| 1295 | Dockerfile-构建服务器镜像-Debug | Debug 镜像构建 |
| 1318 | Dockerfile-构建服务器镜像-Release | Release 镜像构建 |

**API 差异：** inner kadmin 的 workflow 查询用 `/api/workflow-key/query`，需要 `page` + `limit` 参数；执行用 `/api/workflow-key/execute`。

#### 其他

| workflow id | name | 用途 |
|------------|------|------|
| 815 | 部署beta服 | 部署新服 |
| 1245 | 合服-1,4-设置某服维护时间 | 合服前设维护 |
| 1244 | 合服-2-指定服务器db和tgs | 合服合库 |
| 1246 | 合服-3-重启 | 合服后重启 |
| 1247 | 合服-5-给主城加护盾 | 合服后保护 |

#### 执行规则

1. **workflow 按 name 执行**，不是按 id：`execute_workflow` API 实际用 `name` 字段（但 `kadmin_api.py` 封装为 `id` 参数自动转换）
2. **不能跨服复用** — workflow 内部的 task 绑定了具体应用名（如"下线map"绑定 `default_MapService_331`）和路径（如 `/data/x3/reload/Resource/330`）
3. **缺失的服需要在 kadmin 界面手动创建 workflow**（复制已有的改参数）
4. **清服会丢数据** — 下线 Play+Map 后清 MongoDB，不可逆
5. **热更不重启** — 同步配置+代码到物理机的 `/data/x3/reload/Resource/{serverId}/`，然后触发 Hotfix DLL 热加载

### 工作流执行步骤

**热更配置+代码**（不需要重启，运行时生效）：
1. `[同步配置+代码]` — 拉最新 gdconfig + 代码到服务器
2. `[热更]` — 触发 Hotfix DLL 热加载 + 配置重读

**清服**（会下线服务器）：
1. `[下线]` — 同时下线 MapService + PlayService（并行）
2. `[清服]` — 清理 MongoDB 数据

**部署**（拉取已构建的镜像，无独立构建步骤）：
- `[部署]` — 按 tag（分支名）拉取镜像并上线容器

**部署规则（必须遵守）：**
1. **Play 和 Map 必须同时部署** — MapService ID = PlayService ID + 1（如 Play 310 → Map 311）。任何时候部署 Play 都必须同时部署对应的 Map，反之亦然。
2. **换分支时 Center 也要一起** — 如果是切换分支部署，同主机的 CenterService 也必须一起更新，确保代码版本一致。
3. **同一批 deploy_app 调用** — Play + Map（+ Center）放在一次 deploy_app 调用中，不要分开调用。
4. **部署后必须复查状态** — `deploy_app` 返回成功（history status=1）不代表服务存活。必须等待 20 秒后用 `query_app` 确认所有目标服务 `Status=Run`。若发现 `Down` 则自动重试一次，重试仍 Down 则报告用户排查。

```python
# 正确：Play + Map + Center 一起部署
deploy_app(name=["default_PlayService_320", "default_MapService_321", "default_CenterService_63"], tag="dev")

# 错误：只部署 Play 不带 Map
deploy_app(name=["default_PlayService_320"], tag="dev")
```

**合服流程**（按顺序执行多个 workflow）：
1. `id=1245` 设置维护时间 → 2. `id=1244` 合 db + 合 tgs → 3. `id=1246` 重启 → 4. `id=1247` 加护盾

### 操作示例

```python
from kadmin_api import execute_workflow, workflow_history

# 热更 330 服（可用 id 或 name）
execute_workflow(id=1250)
execute_workflow(name="beta-330-热更配置+代码")

# 清服 330
execute_workflow(id=1234)

# 查执行结果
workflow_history(workflow_id=1250, page=1, limit=1)
```

## 服务器拓扑（Beta）

### 架构说明

每个游戏服 = PlayService + MapService（必须同主机）。MapService ID = PlayService ID + 1。
每台主机共享一个 CenterService。新建服按 10 递增编号。

### 拓扑表

| 主机 | CenterService | PlayService | MapService | KvkMapService |
|------|:---:|:---:|:---:|:---:|
| beta-001 | 61 | 110, 120 | 111, 121 | — |
| beta-qa-001 | 62 | 210, 220, 230 | 211, 221, 231 | — |
| beta-qa-002 | 65 | 500, 510 | 501, 511 | 900 |
| beta-qa-003 | 63 | 310, 320, 330 | 311, 321, 331 | 930 |

其他服务：Gate(beta-001)、Door(beta-001)、webtool(beta-001)

### 新建服规则

1. 选目标主机，找下一个 10 位编号（如 beta-qa-003 下一个是 340）
2. 同时创建 PlayService_340 + MapService_341
3. 参数指向该主机的 CenterService（如 beta-qa-003 → CenterService_63）
4. Play 和 Map 必须在同一台主机上

### igame serverId 映射

igame 的 serverId 直接对应 kadmin PlayService 编号（如 serverId=330 = PlayService_330）。

## Jenkins 构建

Jenkins 地址：`http://172.20.110.29:8080`，账号 `admin` / `Adminpwd99`

### 服务器构建

| Job | 关键参数 | 用途 |
|---|---|---|
| `x3-server_rebuild` | branch(default=dev), publish(Debug) | dev 分支服务器镜像构建 |
| `x3-server_rebuild_qamaster` | branch(default=qa), publish(Release) | qa/master 分支镜像构建 |

构建产物为 Docker 镜像，kadmin `deploy_app(tag=分支名)` 拉取部署。

**单独分支构建部署流程（非 dev/qa/master）：**

1. 先导配置：触发 `X3导配置`，branch=目标分支，code_branch=目标分支，等成功（~3min）
2. 再构建：触发 `x3-server_rebuild`，branch=目标分支，publish=Debug，等成功（~8-14min）
3. 等镜像：rebuild 成功后 **还要等 GitLab CI 异步出镜像**（不是即时，下面有解释）
4. 最后部署：`kadmin deploy_app(name=[...], tag=目标分支)`，带重试（镜像可能刚 push 完）

dev、qa、master 分支有 CI 自动触发，不需要手动走这个流程。

> ⚠️ **镜像产线真相（2026-06-29 查清）——这条决定 feature 分支能不能部 beta：**
> - kadmin 部署 = 拉 docker 镜像 `t4f.io/x3/gameserver-new:<分支>`。
> - **没有任何 Jenkins job 直接 docker build/push 这个镜像**（实测 `x3-server_rebuild` / `x3-server_local_rebuild` / `x3-server_rebuild_qamaster` / `x3-serverbuild2` 的控制台都没有 docker/buildx/gameserver-new 推送）。`x3-server_rebuild` 只做：编译 server bin → push 到 GitLab 仓 **`x3/deploy/game-server-bin`** 的同名分支 → 触发下游 `x3-server_local_rebuild`。
> - **镜像实际由 `game-server-bin` 仓的 GitLab CI 构建**，CI 大概率只 gate dev/qa/master 分支 → feature 分支（如 `dev_festival`）push 进去也不一定建镜像 → kadmin 拉报 **`manifest for t4f.io/x3/gameserver-new:dev_festival not found`**。
> - 旁证：下游 `x3-server_local_rebuild` 当前**卡死**（队列有等了 100+ 天的僵尸项，执行器空闲但项被阻塞），即便触发也不可靠。
> - **所以"硬试构建 feature 分支镜像"是赌 game-server-bin 的 CI 会不会给非主干分支建镜像**。若构建后部署仍 `manifest not found`，即坐实 CI 不给 feature 分支建镜像 → **转本地服 3080 测**（feature/dev_festival 测试的稳妥路；见 memory `reference_x3_kadmin_deploy.md`）。
> - 🔴 **本次实测结论（dev_festival·2026-06-29·硬试失败）**：X3导配置 #1370 SUCCESS → x3-server_rebuild **#26841 FAILURE**。失败点**不在 CI gating，而更早**——编译+commit 了 bin，但 `git push` 到 `game-server-bin` 仓被 **pre-receive hook 拒绝**：`GitLab: LFS objects are missing. Ensure LFS is properly set up or try "git lfs push --all"` → `! [remote rejected] dev_festival -> dev_festival (pre-receive hook declined)`。即 bin 没进 game-server-bin → 无镜像。Jenkins 的 push 步骤没跑 `git lfs push --all`，feature 分支这条路就断在这。**→ 硬试此路（至少 2026-06-29 状态）走不通，feature/dev_festival 老老实实用本地服 3080 测。** 部署步骤因 rebuild 失败自动跳过，220 未受影响（仍 master/Run）。

### 客户端打包

| Job | 用途 |
|---|---|
| `x3-apk-mono` | 安卓 APK（测试/beta/俄罗斯） |
| `x3-android-aab` | 安卓 AAB（提审/线上） |
| `x3-ios` | iOS 包（测试/提审/线上） |
| `x3-exe` | PC exe |

**关键参数：**
- `branch`：代码分支（dev/qa/master/功能分支）
- `env_build`：环境配置（dev / beta / qa / gold）
- `channel`：渠道（default / russian）
- `codesign`：iOS 签名（adhoc=测试分发 / dist=正式上架）
- `sync_dlc`：是否同步 DLC（beta 整包设 false，其他 true）
- 其余参数保持默认值

**打包对照表（来自 jolt 配置）：**

| 指令名 | 用途 | Job | branch | env_build | channel | codesign | sync_dlc |
|---|---|---|---|---|---|---|---|
| `apk` | dev 安卓测试包 | x3-apk-mono | dev | dev | default | — | true |
| `apk_ru` | 安卓俄罗斯测试包 | x3-apk-mono | dev | dev | russian | — | true |
| `apk_beta_whole` | beta 安卓整包 | x3-apk-mono | dev | beta | default | — | false |
| `aab` | dev 谷歌商店包 | x3-android-aab | dev | dev | default | — | true |
| `apk_store` | 安卓提审包 | x3-android-aab | qa | gold | default | — | true |
| `apk_ru_store` | 安卓俄罗斯提审包 | x3-android-aab | qa | gold | russian | — | true |
| `apk_gold` | 安卓线上包 | x3-android-aab | master | gold | default | — | true |
| `apk_ru_gold` | 安卓俄罗斯线上包 | x3-android-aab | master | gold | russian | — | true |
| `ipa` | dev iOS 测试包 | x3-ios | dev | dev | default | adhoc | true |
| `ipa_ru` | iOS 俄罗斯测试包 | x3-ios | dev | dev | russian | adhoc | true |
| `ipa_beta_whole` | beta iOS 整包 | x3-ios | dev | beta | default | adhoc | false |
| `ipa_store` | iOS 提审包 | x3-ios | qa | gold | default | dist | true |
| `ipa_ru_store` | iOS 俄罗斯提审包 | x3-ios | qa | gold | russian | dist | true |
| `ipa_gold` | iOS 线上包 | x3-ios | master | gold | default | dist | true |
| `ipa_ru_gold` | iOS 俄罗斯线上包 | x3-ios | master | gold | russian | dist | true |

**规律总结：**
- 测试包：branch=dev, env_build=dev, codesign=adhoc
- beta 整包：branch=dev, env_build=beta, sync_dlc=false
- 提审包：branch=qa, env_build=gold, codesign=dist
- 线上包：branch=master, env_build=gold, codesign=dist
- 俄罗斯包：在对应类型基础上 channel=russian
- 功能分支测试包：branch=功能分支名, env_build=dev

### DLC 资源包

| 指令名 | 用途 | Job | branch | env_build | codesign |
|---|---|---|---|---|---|
| `apk_patch` | dev 安卓 patch | x3_android_res_bundle | dev | dev | — |
| `ipa_patch` | dev iOS patch | x3_ios_res_bundle | dev | dev | adhoc |
| `apk_gold_patch` | 线上安卓 patch | x3_android_res_bundle | master | gold | — |
| `ipa_gold_patch` | 线上 iOS patch | x3_ios_res_bundle | master | gold | dist |

### 导配置

| Job | 用途 |
|---|---|
| `X3导配置` | 导表到指定分支 |

参数：
- `branch`：gdconfig 配置分支名（必填）
- `code_branch`：代码分支名（留空则与 branch 同名）
- `android_patch` / `ios_patch`：patch 版本号（默认 10）
- `cleanup`：是否清理旧产物（默认 false）
- `gate_only`：仅导 gate 配置（默认 false）

dev/qa/master 分支有 CI 自动导配置，无需手动触发。

### 脚本用法

```bash
cd .claude/skills/test-env-prepare-x3

# 查打包机占用
python3 scripts/jenkins_api.py status

# 触发服务器构建
python3 scripts/jenkins_api.py trigger x3-server_rebuild --branch dev

# 触发后监听结果
python3 scripts/jenkins_api.py watch x3-server_rebuild --build 123

# 查单个构建状态
python3 scripts/jenkins_api.py check x3-server_rebuild --build 123

# 触发安卓测试包
python3 scripts/jenkins_api.py trigger x3-apk-mono --branch dev --env_build dev

# 触发 iOS 包
python3 scripts/jenkins_api.py trigger x3-ios --branch dev --env_build dev --codesign adhoc

# 触发导配置
python3 scripts/jenkins_api.py trigger X3导配置 --branch feature/xxx --code_branch feature/xxx
```

### Python 调用

```python
import sys, os
sys.path.insert(0, os.path.expanduser(".claude/skills/test-env-prepare-x3/scripts"))
from jenkins_api import trigger_build, check_build, watch_build

# 单独分支完整流程：导配置 → 构建 → 部署
num = trigger_build("X3导配置", {"branch": "feature/xxx", "code_branch": "feature/xxx"})
watch_build("X3导配置", num)  # 等导配置完成

num = trigger_build("x3-server_rebuild", {"branch": "feature/xxx"})
watch_build("x3-server_rebuild", num)  # 等构建完成

from kadmin_api import deploy_app
deploy_app(name=["default_PlayService_320", "default_MapService_321"], tag="feature/xxx")
```

## Jira 查询

```bash
cd .claude/skills/test-env-prepare-x3

# 查 issue 详情
python3 scripts/jira_api.py query X3NEW-1518

# 添加评论
python3 scripts/jira_api.py comment X3NEW-1518 "已在 beta-320 复现，日志见附件"
```

Python 调用：
```python
from jira_api import load_token, query_issue, add_comment, print_issue

token = load_token()
data = query_issue(token, "X3NEW-1518")
print_issue(data)
```

## MongoDB 数据查询

连接 Beta 环境 MongoDB 查询玩家数据、服务器状态等。

连接串：`mongodb://root:M6D6YJLwPsC5RDZrpCmLx3jqaFeRp8Ye@x3-beta-nlb.a3games.com:27017/?directConnection=true&authSource=admin`

数据库命名：`gs_game_{serverId}`（如 `gs_game_310`）

### 脚本用法

```bash
cd .claude/skills/test-env-prepare-x3/scripts

# 查询玩家全部数据
python3 mongo_query.py player --server 310 --id 14074

# 查询玩家指定字段（如英雄、士兵）
python3 mongo_query.py player --server 310 --id 14074 --fields hero soldier

# 列出数据库所有 collection
python3 mongo_query.py collections --server 310

# 查询指定 collection
python3 mongo_query.py find --server 310 --collection ServerActivity --filter '{"_id": 1}' --limit 5
```

### Python 调用

```python
from mongo_query import get_db, query_player

# 查玩家英雄
player = query_player(310, 14074, fields=["hero"])
heroes = player.get("hero", {}).get("heroes", {})

# 直接用 pymongo
db = get_db(310)
activity = db["ServerActivity"].find_one({"_id": 1})
```

### 常用 Collection

| Collection | 说明 |
|---|---|
| ServerPlayer | 玩家全量数据（英雄、士兵、建筑、资源等） |
| ServerActivity | 服务器活动状态 |
| ServerUnion | 联盟数据 |
| ServerRank | 排行榜 |
| ServerInfo | 服务器信息 |
| Unit | 地图单位 |

### 玩家常用字段

| 字段 | 内容 |
|---|---|
| hero | 英雄列表（cfgID、level、starLevel） |
| soldier | 士兵数据 |
| building | 建筑数据 |
| resource | 资源 |
| item | 道具背包 |

### 前置依赖

```bash
pip install pymongo
```

## 前置条件

- `~/.igame-credentials.json` 包含 `token` 和 `clientId`
- token 需有 X3 项目（gameId=1090）的 GM 操作权限
- 获取方式：
  - beta: igame-qa.tap4fun.com 登录 → F12 Console → `localStorage.getItem("ark_token")`
  - dev: igame-dev.tap4fun.com 登录 → F12 Console → `localStorage.getItem("ark_token")`
- Kadmin access key 已内置于 `scripts/kadmin_api.py`，无需额外配置
- Jenkins 需能访问内网 `172.20.110.29:8080`（公司网络或 VPN）
- MongoDB 需能访问内网 `x3-beta-nlb.a3games.com:27017`（公司网络或 VPN）
- `~/.jira-credentials.json` 包含 Jira Personal Access Token
- `pip install pymongo`（MongoDB 查询用）
