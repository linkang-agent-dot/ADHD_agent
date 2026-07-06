---
name: reference_x3_kadmin_deploy
description: X3 测试环境部署/GM/构建/数据查询权威 skill=test-env-prepare-x3(QA官方)；含kadmin双key+部署铁律+拓扑
metadata:
  node_type: memory
  type: reference
  originSessionId: 017c4e8e-3703-4ff7-860a-ac0f2c07151e
---

# X3 测试环境部署链路（kadmin/GM/Jenkins/Mongo）

## ✅ 权威工具 = `test-env-prepare-x3`（QA 官方 skill，2026-06-25 装好）
位置 `~\.claude\skills\test-env-prepare-x3\`，源 `git@git.tap4fun.com:skills/qa/test-env-prepare-x3.git`。
**X3 测试环境的唯一入口**，一站覆盖：kadmin 部署/workflow、GM 指令(iGame 网关)、改时间(GM+物理机 JumpServer)、跨服活动(GVG/KVK/ZVZ)、Jenkins 构建打包、Mongo 玩家数据查询、Jira。脚本全在 `scripts/`：kadmin_api / gm_execute / jenkins_api / mongo_query / igame_activity / jira_api / jumpserver_client / config_query。
- ⚠️ `npx skills add` 会**只拷 SKILL.md 且因 cwd 装歪**到 `.agents/`；正确做法=直接 `git clone` 到 `~\.claude\skills\test-env-prepare-x3`（带 scripts）。
- 前置（SETUP.md）：`~/.igame-credentials.json`(token+clientId，会过期)；`~/.jira-credentials.json`；依赖 `pip install openpyxl asyncssh requests pymongo`(2026-06-25 asyncssh 已补装)；Jenkins(172.20.110.29:8080)/Mongo(x3-beta-nlb.a3games.com:27017) 需内网/VPN；kadmin/Mongo 凭证已内置脚本。
- 🪤 **iGame dev/beta 是两套独立登录/token，不通用**（2026-06-25 实测）：`.igame-auth.json`（igame-gm-send 用，默认 dev）是 **dev token**，拿去打 beta 网关(`ms-inner-gateway-qa`)→**401**（非过期，JWT exp 还在；是环境不对）。beta token 要单独登 **https://igame-qa.tap4fun.com** F12 取 `ark_token`/`ark_clientId`。test-env skill：beta 读 `~/.igame-credentials.json`、dev 读 `~/.igame-credentials-dev.json`（igame_activity.py:110 按 env 选文件）。kadmin 不受影响（走自己的 access_key）。
- **`.igame-credentials.json` 可从同环境 `.igame-auth.json` 派生**（仅当两者同环境时）：（后者是 igame-gm-send 用的，含 token/clientId/gameId1090/regionId201，就是 X3 token）：`$a=gc .igame-auth.json|ConvertFrom-Json; @{token=$a.token;clientId=$a.clientId}|ConvertTo-Json|sc .igame-credentials.json`。token 过期时先更新 .igame-auth.json 再重跑这句，不用单独登 igame-qa 取。

## kadmin_api.py 实操调法(2026-06-26 部 master 到 220 实测)
- **是函数模块、无 CLI**：`python kadmin_api.py query` 不工作；必须 `import`：`sys.path.insert(0,"scripts"); import kadmin_api as k; k.query_app(name=[...])`。
- **查现状**：`k.query_app(name=["default_PlayService_220","default_MapService_221","default_CenterService_62"])` → `r["info"]["list"]`，每项关键字段 **`Name` / `LastDeployTag`(=分支tag) / `Status`(Run/Down) / `ConfigStatus` / `LastDeployTime`**（`ApplicationImages` 常为 None,看不到可用tag）。
- **部署**：`k.deploy_app(name=["default_PlayService_220","default_MapService_221"], tag="master")` → 返回 `nameStatus[].status=false`(=已提交未确认,**不是失败**)+`applicationDeployHistoryId`。**别信即时返回**,等~20s `query_app` 看 `LastDeployTag==目标 && Status=="Run"` 才算成(铁律3);`app_history(ids=[...])` 看 `status:1`=成。tag 直接用分支名(master/qa/dev/dev_festival)。
- **220 现状基线(2026-06-26)**：220/221/Center62 默认在 **`qa`**(非旧 memory 写的 dev_festival,那条已过时);Play_220+Map_221 部 master 成功 Run,Center_62 留 qa。⚠️镜像 commit 从 kadmin 拿不到→无法确认某 tag 镜像含哪个提交(取决于 Jenkins 构建时间),要确认配置含某改动得另查构建/导表时间。

## kadmin 双 key（SKILL.md；kadmin_api.py 只内置 beta，dev 要手改 BASE_URL+ACCESS_KEY）
- **beta = `5df3d84a-6960-11f1-ac6a-0242ac130002`**（TeamId=25，服 110-510，api-kadmin-beta.tap4fun.com）
- **dev(inner) = `bcd84309-6f93-11f1-acba-0242ac1f0003`**（服 100-105/1530，api-kadmin-inner.tap4fun.com）
- ⚠️ 禁 import P2 的 kadmin api（P2 是 TeamId=7，会打错组织）
- kadmin_api.py 函数：query_app / deploy_app(name,tag) / offline_app / restart_app / app_history(ids) / execute_workflow(name=) / query_workflow / workflow_history。execute_workflow **只认 name 不认 id**。

## ⚠️ 部署铁律（我 2026-06-25 部 22 区漏过 Center，记牢）
1. **Play+Map 必须同批部署**：MapID=PlayID+1（Play 320→Map 321），一次 deploy_app 调用一起发。
2. **换分支时同主机 Center 也要一起**保证版本一致。死结：Center 被同主机多区共用，多区不同分支时 Center 只能一个版本→必然不一致。单服测试这种不一致**被容忍**（部前 220 在 dev、Center_62 在 qa 就已混）；只要目标分支没改 Center 侧跨服协议/序列化就 OK。
3. **部署后必复查**：deploy 返回成功≠存活，等 ~20s 用 query_app 确认 Status=Run，Down 重试一次。
4. workflow（热更/清服）**内部参数写死按服绑定不能跨服复用**；清服会清 MongoDB 不可逆。

## Beta 拓扑（主机→Center/Play/Map/Kvk）
| 主机 | Center | Play | Map | Kvk |
|---|---|---|---|---|
| beta-001 | 61 | 110,120 | 111,121 | — |
| beta-qa-001 | 62 | 210,220,230 | 211,221,231 | — |
| beta-qa-002 | 65 | 500,510 | 501,511 | 900 |
| beta-qa-003 | 63 | 310,320,330 | 311,321,331 | 930 |
igame serverId == kadmin PlayService 编号（serverId 330 = PlayService_330）。物理机改时间走 JumpServer(x3-beta-qa-00N-sv-x3a3)，改前先 disable_ntp。

## X3 微服务架构（与 X2 的 default_game_<id> 不同）
`default_PlayService_<N0>`(逻辑)+`default_MapService_<N1>`(地图)成对=一个区；`default_CenterService_<id>`跨区；`default_KvkMapService_<id>`；基础设施 webtool/beta-door/beta-gate。query name 过滤用 `default_PlayService` 等前缀，`default_game_`/`x3` 返 0。

## GM 关键规则（gm_execute.py / iGame 网关 ark/gm-operate/add）
- gmCommand 内 `serverIds`/`playerIds` 是**字符串**逗号分隔非数组；cmd 全小写(服务端补 gm 前缀)；**禁中文分号**(JSON 反序列化报错)；玩家级指令必须带 playerIds 否则走服务器级分支(`entity is not existed`)。
- **iGame success≠GM 成功**，必查 detail 接口 `contents[].returnInfo`。errCode:6=该进程缺此 GM(版本旧需重部署)。
- 改时间：单服 `setservertime`(Play+Map,需playerIds)+`setcenterandkvkservertime`(Center,数秒内组合)；永久改走物理机 JumpServer。完整 GM 列表见仓库根 `x3-gm-commands.md`(471服务端+109客户端)，常用 ID 见 `ID_REFERENCE.md`。

## 🔴 iGame 部署活动用 110 服当「配置校验源」（2026-06-25 破案·重大坑）
现象：iGame 部署世界杯 5 活动(开箱101516/累充100597/签到101403/兑换101339/BP102243)到 220，提交 success 但 deploy detail = `deploy:"failed", deployMsg:"cfg is empty", serverId:"110"`，活动不落 220 的 ServerActivity。
根因：**iGame(X3 beta)拿 110 服的已载配置来校验活动 activityConfigId**。110 当时跑 `master`(无世界杯 dev_festival 配置)→校验"cfg is empty"失败→连带不部到目标服。serverId:110 是**校验源服**不是部署目标。
**修复**=把 110 切到含该活动配置的分支：`deploy_app(name=['default_PlayService_110','default_MapService_111'], tag='dev')`(dev/dev_festival 都有 WC 配置)→ 再重发活动到 220(failed 记录不自动重试，必须重 submit)→ 5 个全部 OK 落 220(ark 10462-66)、GM `GMPrintServerActivityByCfgId 101516` count=1。
**铁律**：iGame 部署任何 **dev_festival/feature 分支独有的活动**前，先确保 **110 服在含该配置的分支**(查 `find`/query_app 看 110 的 LastDeployTag)，否则 cfg-empty 静默失败。110 是 X3 beta 的 iGame 配置参照服。
附：活动落库验证=Mongo `gs_game_<服>.ServerActivity` 查 cfgId(有 `arkActivityId`=iGame 部的)；窗口按服游戏时间(getservertime,需 playerId)设、宽窗避时区歧义。

## 竞猜(type71)iGame 部署配方(2026-06-25 跑通·可复用)
ark/activity/submit 提交体每个活动项加字段 **`customParam`**(JSON **字符串**)=`{"packIdA":<A队base+档>,"packIdB":<B队base+档>}`。服务端链路:iGame `customParam`→`activityData.customParam`→`arkCustomParam`(存 ServerActivity)→`WorldCupGuessCustomParam`反序列化(内层 key=`packIdA`/`packIdB` camelCase,ServerActivityWorldCupGuessMeta.cs:39)。
- activityConfigId = ActvOnline 6位号 **102920-102992**(73实例,≠ContentID 2920)。一实例=一场一档两包。
- 礼包号=`894000+队号×10+档位`(队号=FIFA三码字母序1-48,ALG=1…UZB=48;档 0免费/1=$4.99/2=$9.99/3=$19.99)。生成器 `KB\产出-数值设计\X3_世界杯\世界杯竞猜_对阵生成器.html`(脚本 `_gen_对阵生成器.py` 读 live Pack 验证)。
- igame_activity.py 的 submit_activity **没有 customParam 字段**,要直接拼 body urllib POST(_headers 复用)。验证:Mongo 查 ServerActivity.arkCustomParam 有值 + GM `GMPrintServerActivityByCfgId <cfg>` count=1。本地 GM `GMAddServerActivityByCfgId` 不带 customParam→开不出对阵,竞猜只能走 iGame 测。
- 已部 4 测试场到 220:102920 巴西vs德国免费/102921 阿根廷vs法国4.99/102922 英格兰vs西班牙9.99/102923 葡萄牙vs荷兰19.99。
- 竞猜礼包奖励=**按档共享、与队伍无关**(Pack.Reward[col13]:免费→291335/4.99→291101/9.99→291330/19.99→291399,任意队同档同奖)。$9.99(291330)=40券1146+5000钻+50VIP+**1148世界杯自选助威头像框宝箱**(开箱291201,任选各队框)。**小组赛档位发的是自选框宝箱1148,队伍专属框803xx是淘汰赛轮次才按队投**。

## 🔴🔴 iGame 部署 deploy:failed 错误码速查 + beta 服时钟时移坑（2026-06-27 破案）
- **`deployMsg` 是数字=服务端 ErrCode**(定义 `client/Assets/Scripts/CSShared/Common/ErrCode/ErrCode.Activity.cs`)。常见：**1017050=`ErrCodeArkIdActivityEndTimeLessNow`(结束时间<服务器当前时间)** / 1017001=ActivityCfgNotFound / 1017011=ActivityCreateFailedServerNotSupported(CreateNewServerActivity返null) / 1017045=ArkIdActivityNotExisted / 1017048= DataError / 1017049=NoActivityConfigId。
- **★beta 服游戏时钟被时移到未来(测节日用)**：2026-06-27 实测 **220 时钟≈2026年8月底**(现存活动窗口 08-15~08-29 status=5进行中、酒馆到09/10月)。**iGame 部署窗口必须设在目标服游戏时钟的未来**,用真实当前日期(如06-28)=对该服是过去→`deploy:failed 1017050`。**查目标服当前游戏时钟法**=读该服现存活动窗口(`activity/list` 看 status=5/进行中那批的 start/end 区间)或 GM `getservertime`(需playerId)。
- 🔴🔴**中文name乱码坑(2026-06-27·prod实锤)**：官方 `submit-cross-server.js` 用 node `JSON.stringify` 发**原始UTF-8中文**body→iGame服务端按**GBK**解→后台活动name全乱码(`ʤ��Ԥ�...`)。UI/其他工具部署的中文name正常(读回`name`字段对照:别人的13726"酒馆争霸"正常、我的13733乱码)。**修=body里中文转`\uXXXX`纯ASCII**(编码无歧义,服务端怎么解都对)：**最稳=改用python提交 `json.dumps(payload,ensure_ascii=True).encode('ascii')` urllib POST**(原生输出\uXXXX,实测name读回正常),或给node脚本submit body加 `.replace(/[-￿]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'))`(注意JS源里是`'\\u'`双反斜杠·易写错)。⚠️注:iGame读回`name`字段是准的(乱码就是真乱码),但读回`cn`字段(活动配置名)永远GBK乱码=API读取quirk别混淆。
- 🔴🔴**血泪教训:prod 绝不能用 API `batch_offline` 清理活动(2026-06-27踩坑)**:prod **submit 免审批**(即生效),但 **`batch_offline` 提交的是「下线申请」→status=8 进审批队列**,**API 撤不掉、连提交者UI也撤不掉**(`batch_offline`再调返success但还8;`submit`带id只会新建一条不更新原记录·徒增垃圾)。**status=8 只能由有下线审批权的人在 iGame 后台审批队列 通过/驳回**才能离开。**所以:prod 清理测试/误部署活动一律走后台UI下线,别用API batch_offline**(beta可以·beta下线直接生效无审批)。误造的status8实例若只在个别测试服(如1910)且与正式批重复=基本无害,等审批人处理即可,别再API折腾。
- ✅**部署前 double-check 已固化进 `submit-cross-server.js`(2026-06-28,防重复+判B状态)**：每次 submit 前自动拉 activity/list 查：①**重复**=同 activityConfigId + 同 serverId + **时间窗重叠**(`s1<e2&&s2<e1`) + 对方 status∈{2待开,5进行中} → 真发 ABORT(exit3)。⚠️**时间不重叠不算重复**(同cfg顺序复用如R32用完R16再用是合法的,只按cfg拦会误杀)。②**B状态**=同cfg+server 有 status8 卡单(下线申请待审批·API清不了·需UI审批)→ 一并拦+提示。dry-run 只报不拦;`--force` 强过。**实测:对已有13750(live)+13792(status8)的cfg102920 dry-run 正确报出两者**。→ 杜绝"没核实旧的就重上撞一堆重复"(2026-06-28 撞16重复的根因)。
- 🔴🔴🔴**铁律(用户2026-06-28定):每次下线/撤回活动必做三步审查,违反=事故**：① **操作前查 status**(`activity/list` 按 id/cfgId 看当前状态);② **按 status 选对接口**(未上线/审批态 status2→**recall** `/activity/recall/{id}` / 上线中 status5→**cancel** `batch_cancel` 或 offline;**严禁无脑 batch_offline**——它对 status2 会造成 status8 审批卡单更难清);③ **操作后复查 status 确认真生效**(prod batch_offline→status8≠完成;recall/cancel 后该变 19/7)。别只看接口返回 success(网关 success≠真生效)。
- ✅**X3 活动操作正确接口(2026-06-28 审查·权威源=`~\.claude\skills\igame-skill\igame-routes.json`)**：均 webgw-cn + `/ark` 前缀。
  - **下线 offline**：POST `/ark/activity/batch_offline` {ids,reason} →prod 进 **status8(下线申请待审批)**。
  - **撤回 recall**：POST **`/ark/activity/recall/{id}`(id 在 URL 路径,不是 body!)** ,单 id。←之前 404 是因为我用错路径 `/activity/operation/recall`+body。
  - **取消 cancel**：POST `/ark/activity/batch_cancel` {ids,reason}（上线中用）。
  - **删除 del**：DELETE `/ark/activity/{ids}` {reason}。
  - 调用可走 `~\.claude\skills\igame-skill\scripts\igame-query.js`(自动加 /ark + 填 {id} + 用 .igame-auth.json 的 gameId1090):`node igame-query.js write activity/recall/{id} '{"id":13792}'`。
  - **状态→操作映射**：未上线/审批态(status2)→**recall**(撤回申请);上线中(status5)→**cancel**或offline。**误部署的 status2 该 recall 不该 batch_offline**(batch_offline 会进 status8 审批态更难清)。
  - ⚠️旧 memory `[[feedback_igame_cancel_vs_recall]]`(operation/recall 路径)是别项目旧口径,X3 别用,以本条 igame-routes.json 为准。
- 🔴**prod 重部署活动前必查旧实例真 status=19,别信"已撤回"(2026-06-28 撞16重复踩坑)**：prod 撤回只到 **status8(下线申请待审批,不终结)**,用户说"撤回了"可能只撤了部分/没生效。不核实就重上→旧的还 live(status5)+新的=**整批重复**。**铁律:重上前 `activity/list` 按 activityConfigId 查,确认旧实例都 status19 才上;残留 status5/8/2 的先处理**。误造的重复用 `--offline` 提下线(进status8 审批队列拦住不激活,但终结仍需审批人/UI)。
- **status=11 = 下线申请被驳回后的死状态(2026-06-28实测)**：deploy=0、无运行时activityId、没落到任何服=**不 live、废条目**。下线申请(status8)被审批人驳回→status11。判一个实例是否真 live 别只看 status,看 **responses[].deploy=='success' + 有运行时雪花 activityId**(真落服)才算 live;status5+deploy55/55+雪花id=真 live。
- **iGame 活动 status 码**：**2=已排期待开始(startTime未到,per-server responses还空·正常)** / 5=进行中live / 14=? / 19=已下线/撤回。**未来开启时间的活动提交后=status2**,per-server deploy结果到startTime激活才回写→要核deploy成功须等激活后复查(别看到status2/responses空就以为失败)。
- **★gateway success / activity/list 里有 customParam ≠ 部署成功**：必看 responses[].deploy=="success" + activityId 非空(雪花号),或 Mongo `gs_game_<服>.ServerActivity`。deploy:"failed"+activityId:""=服务端建活动失败,看 deployMsg 错误码定位。
- ✅**竞猜 API customParam 部署 220 实证成功**：现存 10467-10470(cfg102920-923,customParam齐,deploy=success,窗口08-15~08-29)。失败案 10500=同 cfg102922 但 endTime 用了06-28(过去)→1017050。**修=窗口改对齐220时钟(如08月)重发**。
- ✅**2026-06-27 整套竞猜 beta220 跑通(B方案)**：首批4场窗口取 **08-15~09-20(开启=220已过去→马上生效·结束=220未来→保持开)**,deploy全success(各自customParam正确)。**最终结构=4场×4档=16实例**(用户定:每场都4档免费+4.99+9.99+19.99)=活动ID 102920-102935,部署单号10513-10528。批量改结构流程=`--offline --ids <旧全部>`下线→python行表生成16实例payload→`--env beta --no-aggregate`重发→读回校验deploy=success。免费档packId=队基号(队号×10+894000),+1/2/3=$4.99/9.99/19.99。**"跑配置/马上上线"逻辑=不必精确对齐服钟,窗口设(过去开~足够未来关)即可全绿**(220当前钟∈08-15~09-28之间:08-15活动live、09-28活动status4未开)。批量payload生成法=python按(cfg,对阵,packIdA,packIdB)行表+统一窗口→喂 submit-cross-server.js `--env beta --no-aggregate`。
- 🔴**拨真实时间(A方案)被JumpServer权限挡**(2026-06-27):`reset_time_to_now_sync`/`check_time_sync` 连 JumpServer 成功但主机资产 `x3-beta-qa-001-sv-x3a3` 报"没有资产/不存在"(林康账号无该资产授权或名变)→改不了物理机时间。GM回拨路:`setservertimebydhms`不支持回退、`setservertime`绝对时间需220的playerId且往回拨有风险。**要拨真实时间得先解决JumpServer资产授权/正确资产名**。

## 深海节 iGame 部署记录（2026-06-25·220 beta·10/10 OK）
深海节 10 个 AO 全部部到 220(窗口同 WC 08-15→08-29,acrossServer=0)：累充100598/BP102244/转盘101025/兑换101340/大富翁兑换101341/装饰阶梯106103/拜访105605/酒馆10071704/大富翁102802/许愿池105013。前置=110(dev)有全部 10 AO(校验过)。
- ✅ **许愿池(type50 跨服)在 beta 能 iGame 部署成功**(220 有 CenterService_62)——区别于本地单服开不了(缺 Center,见 [[project_x3_deepsea_festival]])。跨服活动 iGame 部署会 forward 到 center(ActivityMgr.Ark.cs:152)。
- 大富翁 102802 = TimeController=0 deploy-驱动,靠 iGame 部署控时(非自动开)。

## 🪤 排查坑：客户端连错环境 → 追错服的状态（2026-06-25 实例）
现象：beta 220 部了 dev_festival 后，Unity 里看到「航海之路大富翁(102802)开了」，但 Mongo 查 beta gs_game_220 的 ServerActivity **没有 102801/102802 记录**。
根因：**Unity 客户端当时连的是 dev 环境**，看到的是 dev 服状态，不是 beta 220。一路顺着服务端 Type28/空 TimeController 逻辑挖是白挖。
教训：排查「为啥某服显示某状态」**第一步先确认客户端(Unity)连的环境(dev/beta)与你查的服务端环境一致**，再往服务端逻辑挖；客户端连 dev 时 beta Mongo 查无记录是正常的（不是 BUG）。
附带学到的 Type28 开启逻辑(ActivityMeta.cs:418-458)：按绑定 TimeCycle.TriggerType 分支——TT=4 海域开放走 IsOpen(海域时钟)；TT=5 触发后计时走 firstTriggerTime；其它走 IsTimeCycleOpen。**空 TimeController→triggerType=0→走 else 分支 IsTimeCycleOpen(空,now)**(待确认空 cycle 返回);102802(深海航行/成就礼包版)TimeController 空,102801 绑 TC2702。

## ⚠️ feature/dev_festival 分支测不了 beta（无 docker 镜像）→ 用本地服（2026-06-28 实证）
- `deploy_app(tag='dev_festival')` 报 `manifest ...:dev_festival not found`=**不存在该分支 docker 镜像**。`x3-server_rebuild` job **不建镜像**,只编译+把 bin 提交到 `game-server-bin` 仓对应分支并触发下游 `x3-server_local_rebuild`(常卡巨长队列)→feature/dev_festival 分支镜像短期拿不到。**结论:要在 beta 测 feature/dev_festival 代码或配置,基本走不通;改用本地服 3080。**
- 🔬**镜像产线真相(2026-06-29 查清·已写进 `test-env-prepare-x3` SKILL.md「单独分支构建部署流程」段)**：kadmin 部署=拉 `t4f.io/x3/gameserver-new:<分支>`;**没有任何 Jenkins job 直接 docker build/push 这镜像**(实测 x3-server_rebuild/x3-server_local_rebuild/x3-server_rebuild_qamaster/x3-serverbuild2 控制台都无 docker/buildx/gameserver-new 推送)。镜像由 GitLab 仓 **`x3/deploy/game-server-bin` 的 CI** 构建,**CI 大概率只 gate dev/qa/master**→feature 分支 push 进去不一定建镜像=manifest not found 的根因。
- 🧪**"硬试建 feature 镜像"流程(用户 2026-06-29 要走)**：①X3导配置 branch=目标分支(~3min) ②x3-server_rebuild branch=目标分支 publish=Debug(~8-14min,push bin 到 game-server-bin 同名分支) ③等 game-server-bin CI 异步出镜像 ④`deploy_app(tag=目标分支)` 带重试。**赌点=步骤③的 CI 会不会给非主干分支建镜像**;若④仍 manifest not found 即坐实 CI 不覆盖 feature 分支→转本地服。🔴**本次 dev_festival 硬试结论(2026-06-29·失败)**：导配置#1370 OK→rebuild **#26841 FAILURE**,失败点**不在 CI gating 而更早**=`git push` bin 到 `game-server-bin` 被 **pre-receive hook 拒**(`LFS objects are missing, try "git lfs push --all"`→`remote rejected dev_festival (pre-receive hook declined)`)→bin 没进仓→无镜像。Jenkins push 步骤没跑 `git lfs push --all`。**硬试走不通,feature/dev_festival 用本地服 3080 测**;220 未受影响(deploy 步因 rebuild 失败自动跳过,仍 master/Run)。
- **JumpServer 林康账号对 `x3-beta-qa-00N-sv-x3a3` 报"没有资产"→读不了 beta 服日志**(只能 Mongo 间接证)。要字面日志只能本地服。
- **本地服验 dev_festival 配置最快**：`cd Tools/table_exporter && python ExportTable.py`(从 `C:\x3\gdconfig\tsv` 当前分支导出)→`cp temp_dev/ProtoGen/<改的>.bytes client/Assets/Res/Config/ProtoGen/`(schema没变仅加数据行就行)→重启本地 Game+Map(`--no-build`)或 `!gm ReloadGameServer` 热更。日志验 `StartPreloadData...` 无 `InvalidProtocolBufferException`=配置干净。
  - 🪤**导表产物在 gdconfig 仓根 `C:\x3\gdconfig\temp_dev\ProtoGen\`,不是 `Tools\table_exporter\temp_dev\`**(EXPORT 输出路径相对仓根,别在 cwd=Tools 下找会扑空)。i18n 16 语言 bytes 在 `temp_dev/ProtoGen/i18n/*.bytes`→对应 client `Assets/Res/Config/ProtoGen/i18n/`。ExportTable 打印 `protoc 成功/generate localization bytes success/MD5 written` 且无 Exception=成功(红色的 `Import CustomMessage.proto unused` 是 warning 非错)。
- ✅**「部署 feature 分支到本地服 3080」完整流程(2026-07-01 X3NEW-hero-handbook-deluxe 实操)**：① `cd /c/x3-project && git pull --ff-only origin <分支>`(client 是子目录一起更新;gitlink gdconfig 跟 hook 走)② 本地导表(上条,从 `C:\x3\gdconfig` 当前分支)→ cp 有差异的表+i18n+`AllTableDataMd5.txt` 到 `client/Assets/Res/Config/ProtoGen/`(只 cp 差异表·i18n 大文件跳 cmp 直接全量 cp 省时)③ `stop_gs.py --server_id 3080`④ 重编 `GameServer.Hotfix.csproj`+`MapServer.Hotfix.csproj`(**必看 0 错误**)⑤ 先起 Game 等 `PlayService started` 再起 Map 等 `MapService started`⑥ 复查:两进程在+telnet 端口 26080/26081 LISTENING+启动段无 `InvalidProtocolBufferException`。⚠️**并发合并坑**:若正好有人/别进程在同仓 `git merge dev_festival`(有 `UU` 未解文件/`VersionControl.cs` 冲突标记 `<<<<<<<`),重编会报 `CS8300 遇到合并冲突标记`——**先等冲突解完(git diff --diff-filter=U 空)再编**,别硬改冲突文件(在途合并·`[[feedback_confirm_before_touching_inflight_repo]]`)。⚠️配置源若选「C:\x3\gdconfig 现状」而它落后 origin N 提交=测试服跑的是本地 WIP 非最新全量,口径要跟用户说清。
- 🐛**stop_gs.py 杀不干净**：只杀 `dotnet run` wrapper,不杀子进程 `GameServer.exe`/`MapServer.exe`→老服仍占端口跑旧配置。必须 `Stop-Process -Name GameServer,MapServer -Force` 按名杀。
- 📁**本地服真实日志在进程 cwd**：`server/GameServer/bin/Debug/net8.0/logs/game-3080.<真实日期>.log`(不是 `server/logs/`);文件名真实日期、行内带 game-time 戳(本地服钟在未来)。

## 历史：手搓的 `x3-kadmin` skill 已被官方覆盖（冗余，建议删）
本会话曾手搓 `~\.claude\skills\x3-kadmin\`（仅 deploy/find，单 beta key）。官方 test-env-prepare-x3 全面覆盖且更完整，x3-kadmin 冗余。
