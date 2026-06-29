---
name: reference_igame_gm_send
description: iGame GM 命令下发 skill(igame-gm-send) 的链路、鉴权双文件坑与刷新法
metadata: 
  node_type: memory
  type: reference
  originSessionId: 392dacb5-9dc0-4a3b-aa91-dda965852581
---

iGame 后台发 GM 指令走 skill `igame-gm-send`，脚本 `C:\Users\linkang\.claude\skills\igame-gm-send\scripts\send_gm.py`。

**链路**：脚本拼 `{server_ids, cmd, players, args}` **纯JSON**(不追任何尾随字符)→ POST `ark/gm-operate/add` 网关。dev(默认)=`ms-inner-gateway-dev.tap4fun.com`，beta=`ms-inner-gateway-qa`。鉴权 header = `Bearer <token>` + `clientid`，默认 gameid=1090 regionid=201。

**✅✅✅ 给玩家发 GM 的正确请求格式(2026-06-25 用户在 iGame UI 验证 + 脚本 API 复现 errCode0·已彻底跑通)**：
- **根因纠正**：之前「operateType=3 自由文本路由到 server 100、必须走 operateType=1 预配置」的判断**是错的**。真因=**字段名/类型写错了**：旧 send_gm.py 用 `server_ids`(数组)+`players`(数组)→网关识别不了→才落到 server 100。**改成正确字段名后 operateType=3 自由文本直接通**。
- **🟢 正确格式(operateType=3 自由文本，最省事)**：`gm-operate/add` 体 = `{"operateType":3,"gmCommand":["<内层JSON>"]}`，**内层 JSON** =
  `{"serverIds":"3080","cmd":"addactivityscore","playerIds":"27877","args":["<活动雪花id>","<分值>"]}`
  - **`serverIds`=字符串**(不是 server_ids 数组) / **`playerIds`=字符串**(多个逗号隔,不是 players 数组) / `cmd`=GM名(大小写均可,服务端 lower+补gm前缀) / `args`=字符串数组 / **绝不要尾随 `；`**(；是 iGame UI 的命令分隔符;走 API 加 ； 会让 ArkModule.Gm.cs:20 JsonConvert 抛 "Additional text" 静默失败,实测带；returnInfo=None/不加分)。
  - 成功判据=`/gm-operate/detail?id=<opid>` 的 `returnInfo=[{"uid":27877,...,"errCode":0}]`(uid=玩家号、errCode0)。错字段时 returnInfo 会是 `uid:100 "entity is not existed"`(服务器级)。
- **🟢 另一条路(operateType=1 预配置操作，iGame UI 走的)**：`{"operateType":1,"players":[{"serverId":3080,"playerId":27877}],"contents":[{"gmConfigId":3023,"params":"<JSON>"}]}`。gmConfigId 来自 `GET /ark/gm-config/all`(211个固定操作)：**3023=增加进度积分(activityid+score=GMAddActivityScore)** / 2975=VIP等级 / 2990=远程执行客户端gm / 3031=建筑折扣积分 / 3039=回忆积分。⚠️type=1 的 params 请求编码没完全试出(列表会把参数名当值、字符串400)——**但 type=3 已通,不需要它**,留记备查。
- **底层 GM cmd = `GMAddActivityScore(活动id 分值)`**(`ActivityMeta.Gm.cs:292`),活动id 必须是**运行时雪花号**(非配置号102243)。⚠️🔴**雪花号每服不同(2026-06-29 prod实证:102243 跨55服=55个distinct雪花)**——每服各自创建活动实例时生成,`7655210947394404352` 只是本地3080那一台。**批量给多服加分必须按服各取各的雪花**(从 iGame `activity/list` cfg=102243 的 responses[].activityId 按 serverId 提取),55服用同一个雪花=54服加错/加不上。
- **🔧 已固化工具(2026-06-25)**：
  - `~/.claude/skills/igame-gm-send/scripts/send_gm.py` 已修成正确格式(serverIds/playerIds字符串、无；),单条:`--server 3080 --players 27877 --cmd addactivityscore --args "<雪花id>,<分>"`。
  - **批量加分 `~/.claude/skills/igame-gm-send/scripts/batch_add_score.py`**：`--csv <服,玩家,活动雪花id,分>` / `--rows "3080,27877,<id>,500;..."` / 单条;逐条发+自动 detail 核 errCode0;`--dry-run` 预览。实测通(op749 errCode0)。**批量加BP分给名单直接喂这个**。

**🗓️ 世界杯竞猜结算工作流(周末·每比赛日·用户定 2026-06-25)**：① **ai-to-sql** 查购买了**指定订单(竞猜礼包)**的玩家名单(订单→user_id);② 这批玩家=猜中/参与者 → 给世界杯BP(活动雪花号7655210947394404352)加分;③ **🔴用户要求=只生成 GM 命令/名单给他审,别直接部署执行**(遵 [[feedback_production_ops_announce_first]])。**生成器=`~/.claude/skills/igame-gm-send/scripts/gen_gm_commands.py`**(`--players "a,b" 或 --players-file <ai-to-sql导出列> --server 3080 --activity <雪花id> --score 600 --out <txt>`)→ 出审核 txt(含汇总+batch csv+每人gmCommand JSON+确认后运行命令,**不调网关不加分**);用户审完无误才用 `batch_add_score.py --csv` 真发。样例 txt=`C:\Users\linkang\世界杯BP结算_GM命令_样例.txt`。AI-to-SQL skill 见 [[reference_ai_to_sql]]。
- **🔧 iGame↔本地同实例**：本地起的 sid-3080 进程注册进共享 etcd(172.20.90.151),iGame dev 的"3080"=同一台(玩家详情 name/level/vip 与本地库一致、ServerActivity 雪花id 全对得上)。所以本地 telnet 加的分、iGame 查得到。
- **⚠️雪花activityId 别认错(本会话踩)**：iGame 部署的活动运行时 id 是雪花号,同节日多模块易混——世界杯开箱101516=`7655210933718089728` / 世界杯BP102243=`7655210947394404352` / 深海BP102244=`7655146621669212160`。查权威映射=连本地库 `gs_game_3080.ServerActivity` 看 `_id↔cfgId`,或玩家库 `ServerPlayer.activity.activityDict` 看 `key↔cfgID↔progressScore`(pymongo 直连 172.20.90.151:27017)。

**✅✅ 不登号验证 GM 真实执行结果(2026-06-25 发现·强力诊断)**：iGame `add` 只返 success+操作id(如711-716),真执行结果**异步**。用 **`GET .../ark/gm-operate/detail?id=<操作id>`** 查每服执行详情:`data.contents[].returnInfo` = `[{"uid":..,"gmResult":"..","errCode":..}]`(JSON字符串)。`returnInfo` 空 `[]`=没产生结果(玩家没找到/没绑);有 errCode!=0 =执行失败原因。配套 `/ark/gm-operate/getProcess?id=<id>`(查审批/流程状态)。同 auth header。**这是判 GM 到底生没生效的权威途径,取代登号肉眼看**。脚本片段见本会话(urllib GET + Bearer header)。
- 实证对照(同发 GMAddActivityScore 给玩家加分):①只带 `players`(无playerIds)→ returnInfo `[{"uid":100,"gmResult":"entity is not existed","errCode":21}]`=跑成**服务器级**(uid=100是服务器实体)、玩家没绑;②带 `playerIds:"27877"`→ returnInfo `[]`=进了玩家分支但 `GetPlayerByUidAsync(27877)` 查无此人。

**🔴 玩家用 `basic.uid`(账号uid)解析,别传角色/playerID(2026-06-25)**：服务端 `ArkModule.Gm.cs` 对每个 uid 走 `PlayerMgr.GetPlayerByUidAsync(uid)`→`GetPlayerByUIDAsync` 拿 **`basic.uid`** 去 DB 查(`PlayerMgr.cs:460 Eq("basic.uid",uid)`,从DB加载·与在线无关)。**playerIds 里填的必须是账号 uid**;若误填角色ID/playerID(DB `_id`),查 basic.uid 命中不到→返 0→player null→returnInfo 空、静默不加。"玩家在游戏里、活动也在,但 iGame GM 加不上且 detail 返空"=典型传错 id 类型(或 server_ids 路由到的节点没这玩家)。

**🔴🔴 玩家 GM 必须带 `playerIds` 字段(2026-06-25 实证·send_gm.py 原 bug)**：服务端 `ArkGMModel.cs:6` 把玩家字段 `uids` 绑定 JSON 属性 **`playerIds`(逗号分隔字符串)**;`ArkModule.Gm.cs` 只有 `gmModel.uids` 非空才走 `foreach uid → HandlePlayerGMAsync(player,...)` 按玩家执行,空了就走服务器级分支、**玩家 GM 根本不落到玩家身上(静默不执行,网关仍 success)**。原 `send_gm.py` 只发 `players`(int数组)、不发 `playerIds` → `uids` 永远空 → **所有"给玩家"的 GM 实际都没作用到玩家**。判定法:游戏内 GM 能加分/生效、但 iGame 同命令不生效 = 玩家没绑上。**修=gm_line 同时带 `playerIds`(字符串,服务端真读)+`players`(兼容网关)**(已改脚本)。`server_ids` 供网关路由、`cmd`/`args` 服务端读、`playerIds` 服务端绑玩家——四个都要对。

**🐛 尾随 `；` bug(2026-06-25 修)**：旧脚本/旧 SKILL.md 在 gm JSON 末尾强补全角 `；`。服务端 `ArkModule.Gm.cs:20` 用 `JsonConvert.DeserializeObject` 严格解析整条 body，遇尾随 `；` 抛 `Additional text encountered after finished reading JSON content: ；` → **GM 静默不执行，但网关仍返回 `success:true`**(网关只登记不校验游戏侧解析)。已删 `send_gm.py` 补尾逻辑 + 纠正 SKILL.md。**通用教训**：iGame 网关 `success:true` 只代表「已登记」，真执行结果/报错**异步回 iGame 后台**，下发后必须查后台 GM 结果/登号/查数仓核实，别凭网关 success 判生效。GM 给玩家加积分的完整链路+雪花id两步法+时间窗gate见 [[reference_x3_score_activity]] 「GM 给玩家加 BP/活动积分」段。

**🌐 iGame 环境↔网关↔auth 映射（2026-06-27 用于活动部署 igame-activity-deploy）**：
- **dev**：UI `igame-dev.tap4fun.com` / 网关 `ms-inner-gateway-dev.tap4fun.com` / auth=`.igame-auth.json`（igame-activity-deploy 默认）。`activity/submit` 实测通(推 102920→1970 返单号)。
- **beta/qa**：UI `igame-qa.tap4fun.com` / 网关 `ms-inner-gateway-qa.tap4fun.com` / auth=`.igame-credentials.json`（test-env-prepare-x3 的 igame_activity.py 默认）。
- **prod/正式**：UI `igame.tap4fun.com` / 网关 **`webgw-cn.tap4fun.com`**（≠ms-inner-gateway!）/ auth=`.igame-auth.json`。2026-06-27实测prod query OK(342活动)。
- 🛠️**官方批量部署 skill=`igame-x3-activity-deploy`**(git `https://git.tap4fun.com/skills/x3/igame-x3-activity-deploy`,作者龚亮;已装到`~/.claude/skills/igame-x3-activity-deploy/`,核心=单文件`submit-cross-server.js` node无依赖)。`--env prod`(webgw-cn/.igame-auth.json)/`--env dev`(ms-inner-gateway-dev/.igame-auth-dev.json);`--file <payloads.json> --dry-run`预览/不加--dry-run真发/`--offline --ids a,b`下线;**默认自动聚合**同cfg+同时间多组到1活动ID。payload=数组,时间UTC毫秒(Date.UTC),servers二维字符串`[["1970"]]`,acrossServer 1=跨服/0=单服。**⚠️生产免审批,submit即对玩家可见→必先dry-run+单组试**。**此工具也不带customParam**(竞猜推它=空壳)。
- ⚠️**prod token ≠ dev token,互不通用**:dev的`.igame-auth.json`token打prod webgw-cn返401请登录。prod token取法=登 igame.tap4fun.com(企微扫码)→F12 Console `copy(JSON.stringify({token:localStorage.getItem('ark_token'),clientId:localStorage.getItem('ark_clientId')||''}))`→写回`.igame-auth.json`(先备份dev到`.devbak`)。
- 📌 auth 文件各自过期不通用：`.igame-auth.json`(随用途装dev或prod token) / `.igame-auth-dev.json`(igame-x3-activity-deploy的dev用) / `.igame-credentials.json`(beta/qa)。
- ✅**活动submit权限(2026-06-27实测)**：林康账号 prod + beta **都有submit权限**(prod 13731/13732、beta 10500 均成功)。
- 🐛**「没有权限」假象根因=auth文件缺 gameId/regionId(强力坑)**：`.igame-credentials.json` 原本只有 token+clientId 两个字段,而 submit-cross-server.js 直接读 `auth.gameId`/`auth.regionId`(无默认)→header发出 `gameid:undefined/regionid:undefined`→网关返 **HTTP200 `没有权限`(ark_error_10018)**(不是真没权限!)。补上 `"gameId":"1090","regionId":"201"` 即成功。**判定:submit返『没有权限』先查auth文件四字段(token/clientId/gameId/regionId)齐不齐,别急着怀疑权限/网关**。(query没报错是因查询代码带了默认1090。)
- 🔑**JWT `systemId` ↔ 环境/权限(解token payload可见)**：林康三token都是 employeeId 1957 但 systemId 不同——**101=prod(能写)** / **44=beta-qa(只读·submit没权限)** / **7=dev**。「submit 返『没有权限』而非401」= token 有效但 systemId/scope 不对(不是真没权限就是 token 串环境/旧)。**修=去对应环境UI(如 igame-qa.tap4fun.com)重新登录取该会话token**(F12 Console取ark_token,或真点一次部署 Copy as cURL 拿网关+写token一次到位),写回对应auth文件。别假设一个环境的token能写另一个环境。
- 🔧**已给 submit-cross-server.js 加 beta 环境**(本地)：`beta:{host:ms-inner-gateway-qa,ui:igame-qa,auth:.igame-credentials.json}`。但林康beta无写权限,加了也submit不了(留着以后有权限的人用)。脚本ENV_TAG有显示bug:beta会标成🟢DEV(实际打对了qa网关,无害)。
- 🔑**API 发 customParam 的法子(2026-06-27敲定)**：customParam = **JSON 字符串**(读回13732实测 type=str,值`'{"packIdA":894390,"packIdB":894080}'`)。submit-cross-server.js **不用改**——它 `JSON.stringify([p])` 发整个payload对象,只要 payload JSON 里加 `"customParam":"{\"packIdA\":xxx,\"packIdB\":yyy}"` 字段就一起发;配 `--no-aggregate` 防聚合。✅**API发customParam已实证落iGame(2026-06-27)**:beta推102922到220返id10500,读回`/ark/activity/list`其`customParam`=`{"packIdA":894071,"packIdB":894271}`原样落库。⚠️但**iGame记录里customParam落对≠服务端真建出活动**:10500的responses[].deploy=`"failed"`/activityId=`""`(因220在master无竞猜配置,详见[[reference_x3_kadmin_deploy]]);判活动真生效要看 deploy字段/Mongo ServerActivity,别只看activity/list有customParam。

**鉴权双文件坑（重要）**：
- skill 默认读 `C:\Users\linkang\.igame-auth.json`；另有 `C:\Users\linkang\.igame-auth-dev.json`（结构略不同，含 `version`）。两套 token **各自独立、各自过期**，别假设一个有效另一个就有效。
- token 是 JWT，有效期约 15 天。过期时网关返回 `{"success":false,"code":"401","message":"请登录"}`（GBK 乱码显示）。
- 刷新：让用户从 iGame 后台贴新 `token` + `clientId`，写回**默认文件** `.igame-auth.json` 的对应字段（保留 gameId/regionId），之后默认路径即可用、无需 `--auth-file`。
- 验有效期：解 JWT payload 的 `exp`（base64url，注意补 `=` padding）。

**链路探针（不改游戏状态验通断）**：用不存在的 cmd 如 `__probe_noop__` 发一条，网关只登记不执行任何 GM。返回 `success:true`=链路+鉴权全通；`401`=token 过期。
```
python C:/Users/linkang/.claude/skills/igame-gm-send/scripts/send_gm.py --server 402 --cmd __probe_noop__ --args "" --env dev
```

**常用**：加 10 万钻石 `--server 402 --players 123456 --cmd paddassets --args 11151001,100000`；multicmd `--cmd multicmd --args d2`；全服指令不填 `--players`。生产风险指令(删号/清档/重置)先跟用户确认。

相关：[[reference_jira]]
