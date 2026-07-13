---
name: workflow-x3-local-server-gm-telnet
description: X3 本地服调时间/发GM命令的 telnet 链路（端口算法、分包协议坑、设D30），调本地服时间或本地发GM时用
metadata: 
  node_type: memory
  type: project
  originSessionId: bc47406f-de36-414c-b81a-a24b401015f1
---

X3 **本地服**（`-e local`，`Tools/start_local_server.bat`）发 GM 命令、调服务器时间走 telnet。helper 脚本：`C:\Users\linkang\x3_gm.py`（`python x3_gm.py "!gm @<uid> <cmd args>" ...`）。

**关键参数**
- telnet 端口 = `23000 + NodeID`（`TelnetModule.cs`，port = 23*1000+NodeID）。3080 服 `-nid 3080` → **端口 26080**。NodeID 看启动命令行（`Get-CimInstance Win32_Process` 查 GameServer 进程 CommandLine）。
- 时间相关 GM（`GMSetServerTime`/`GMGetServerTime`/`GMSetServerTimeOffset`）都在 `BasicMeta`，是 **player-scope** → 必须 `!gm @<uid> <cmd>`，纯 `!gm <cmd>` 是 server-scope 找不到。uid 随便挑个该服玩家：从 BI 日志 `server\GameServer\bin\Debug\net8.0\logs\game-<sid>.bi.log` 的 user_event/user_login 行取。⚠️**旧记录的 uid 会因清库失效**：2026-06-22 实测 27065 已报 `errCode=1001005 LoadPlayerFail`(清库重建后号没了)，当前有效活跃 uid=**27798**(originSeaArea=8)。报 1001005 就去 bi.log 尾部 grep 一个新 uid 换上。
- **跨天/推进一天**：读 `GMGetServerTime` 拿当前日期 → `GMSetServerTimeOffset <次日同时刻>`(格式 `yyyy-MM-dd/HH:mm:ss`，持久化)。2026-06-22 实例：06-23/12:49(passDay6)→ set `2026-06-24/12:50:00` → passDay7，跨一个自然日；客户端退登重进同步每日刷新。

**❗telnet 分包协议大坑**（`ServerCommon/TelnetServer/Server.cs` receiveData）：服务端**每个 recv 包只看 data[0]**，仅当包**首字节是 CR(0x0D)** 才判定为回车并派发命令。所以 `!cmd\r\n` 一个包发出去 = 首字节是 `!`，CR 被埋在中间，永远只回显不执行。**必须把命令体和 `\r\n` 分两个包发**（先发 body，sleep 0.3s，再发 `b"\r\n"`）。x3_gm.py 已处理。另：首字节 ≥0xF0 的包被当 IAC 丢弃。

**设到 D30 的算法**（D-day = passDay，开服满 N 天）
1. `GMGetServerTime` 读 `ServerOpenDate` + `passDay`。
2. 目标时间 = ServerOpenDate + N 天，格式 `yyyy-MM-dd/HH:mm:ss`。
3. `GMSetServerTimeOffset <目标>`（DEBUG+local 限定，**持久化、重启仍生效**）；只想本次生效用 `GMSetServerTime`。`GMSetServerTimeByDHM day hour min` 是相对当前**加**天数，不是设绝对天。
   - ⚠️**只有 `GMSetServerTimeOffset` 持久化！`GMSetServerTimeByDHM` 和 `GMSetServerTime` 都不持久(2026-06-18 实测打脸)**：用 ByDHM 调了 +1 天(D2)，重启本地服后时间**回真实当天 D1**，调的偏移全丢。所以"调时间后要重启还想保留天数"必须用 `GMSetServerTimeOffset <绝对时间>`(算法见上：ServerOpenDate+N天)，别用 ByDHM/SetServerTime。给用户答"重启后时间还在不在"前先认清用的是哪条命令。
4. 复验 `GMGetServerTime` 看 passDay。

**限制**：时间只能前进，`delta<0` 被拒（`ErrorCodePlayerDisallowRewindTime`）。要回退得 `GMClearServerTimeOffset`(下次重启生效) 或重启清库。

⚠️**测「活动到期结算」(排行榜发奖/道具回收)：直接跳时间过活动end 不一定触发结算**（2026-06-24 用户实测：`GMSetServerTimeOffset` 一把跳到活动窗口外，发奖没跑）。原因：很多结算/发奖挂在**跨天事件(OnNewDay/每日0点 tick)**上，`SetServerTimeOffset` 是**直接跳**目标时刻、不逐日触发跨天，所以日界驱动的结算逻辑没跑。**测发奖的正确姿势（2026-06-24 已实测验证）**：① 先 `GMSetServerTimeOffset` 跳到活动 **end 之后、但下一个午夜之前**（如活动 end=9/26 06:00 → 跳到 `9/26 23:59`）——此时活动已过 end **但仍 `count=1` 没结算**（实证：GMPrint 还在）；② 再 `GMSetServerTimeOffset` **小步跨过一个午夜**（跳到 `9/27 00:05`）——日志立刻出 `DayUpdateNtf` + `ServerRank ... SendRankRewards` + `SendMailImp`（发奖邮件），结算触发。**关键=最后那一下必须干净跨过 00:00**；一把大跳直接到窗口外不会逐日触发跨天=不发奖（用户实测"感觉少了"的根因）。GM 里 daily 系（`GMDailyTaskRefresh`/`GMUpdateAllActivityDailyActivityPlayer`@`ServerActivityDailyRankMeta.cs`）印证日系统 tick/事件驱动。⚠️注意 `ServerRank` 结算行会打印 `sendMailReward: True/False`——**False 的榜不发邮件奖**（排查"某榜没发奖"先看这个标志，可能是该 RankCfg 本就 NeedSendMailReward=0，非 bug）。

实例（2026-06-05）：3080 开服 2026-05-27 09:31:06，D8 → set 2026-06-26/09:31:06 → passDay 30。

## ★清库全服重启（清玩家数据那种，2026-06-16 实操）
工具 `Tools/reset_local_server.bat`（停→drop_db→重编→起），但有 `pause`+`dotnet test` 卡非交互。**手动版**（cwd=`C:\x3-project\server`，比普通重启多一步清库）：
1. 停：`python Tools/stop_gs.py --server_id 3080 --grace 10`
2. **清库**：`python Tools/drop_db.py --server_id 3080`（⚠️**2026-06-24 实测：必须用 `--server_id` 旗标，位置参数 `drop_db.py 3080` 会报 usage error**）— 删 MongoDB `gs_game_3080`(172.20.90.151:27017)整库 + 清 Common.CrossServerActivity 含该 sid 记录；**无交互确认直接删**。控制台输出是 GBK 乱码但能认出「已删除数据库」「完成」。sid<100(Center)才额外清 PrefsInfo 时间偏移；sid≥100(3080)清库=玩家库删→**服务器时间回真实当天**(实测 D30/7-08 回 6-16)。不碰 Center(61)。
3. 重编：`dotnet build GameServer.Hotfix/GameServer.Hotfix.csproj -c Debug` + `MapServer.Hotfix/...`（cascade 主工程；跳 reset.bat 的 dotnet test 省时）
4. 起：**先 Game，再 `python Tools/wait_server_info.py 3080 600` 等 ServerInfo 写入，最后才起 Map**（见下条铁律）。
5. 验：日志 `PlayService started`/`MapService started` + 游戏时间回真实日期 + 6 进程。
- 🔴**清库后起 Map 必须先 `wait_server_info.py`，不能背靠背起（2026-06-29 实证踩坑）**：drop_db 把 `gs_game_3080` 整库删了→**ServerInfo 记录也没了**；MapServer 启动时 `ServerInfoMgr.OnInit` 查 `ServerInfo._id==sid` 查无→`ServerInfo not found! 3080`→`Module ServerInfoMgr init error`→**Server Start Failed**。**ServerInfo 由 GameServer 在空库上自己写,但要等几分钟**(本次 GameServer `PlayService started` 后 DB 仍 0 集合,~5min 后才写出 ServerInfo;可能卡在外部平台服 auth2/guidLost 超时重试后才落)。所以**普通重启(不清库)ServerInfo 已存在→Game/Map 背靠背起 OK**(start_local_server.bat 就这么干);**但清库后必须**起 Game→`python Tools/wait_server_info.py <sid> 600`(轮询 ServerInfo,最多10min)→ServerInfo ready 后再起 Map(canonical `reset_local_server.bat` 正是这个时序)。我用固定 6s gap 起 Map=必失败。Map 失败不影响 Game(Game 照常 PlayService started),补等 ServerInfo 后单独起 Map 即可,不用重起 Game。
- ⚠️**清库后无任何玩家**！GM `@<uid>` 作用在玩家上，清库后 uid 不存在→GM 报 **errCode=1001005 `ErrCodeLoadPlayerFail`**(不是config错)。**必须先让玩家登录(客户端登入会在新库重建该号)，GM 才能 @它**。判在不在：发 `GMPrintServerActivityByCfgId`，日志回 `LoadPlayerFail`=不存在 / `errCode=1017012 no server activity found`=存在(只是没活动,可开)。
- ⚠️**清库重登后号的海域会重置→开活动 originSeaArea 跟着变**(2026-06-24 实测：27798 清库前海域8、清库重登后变海域1)。所以①本 memory 里记的「某 uid=某海域」清库后作废，以重登后实际 `originSeaArea=` 为准；②清库后一律用被测号自己当 @uid 开活动(原本就该这样)，活动建在它当前海域、它自己看得见，不用管旧海域映射。
- ⚠️竞猜类活动(TriggerType=5 的 TC)GMAdd 必须给**显式 durationMinutes**(30天=43200)，`0` 反查会报 errCode=10；绝对/开服相对 TC(累充/签到/BP/开箱)用 `0` 反查周期即可（见下方 cfgID 开活动段）。

## 重启本地服流程（+ 一个大坑）

**停**：`python C:\x3-project\server\Tools\stop_gs.py --server_id 3080 --grace 10`（按 sid 同时停 Game+Map，优雅 CTRL_BREAK→超时强杀）。**依赖 psutil**（已 `pip install` 进 C:\Python314）。
**起**（脱离会话、不重建用 --no-build）：cwd=`C:\x3-project\server`，先 Game 再隔 ~5s 起 Map（Map 的 nid=sid+1，3080→3081）：
```
Start-Process dotnet -ArgumentList 'run --no-build --project GameServer -- -sid 3080 -nid 3080 -csid 61 -e local -ll debug -lf logs/game-3080.log' -WorkingDirectory 'C:\x3-project\server'
Start-Process dotnet -ArgumentList 'run --no-build --project MapServer  -- -sid 3080 -nid 3081 -csid 61 -e local -ll debug -lf logs/map-3080.log'  -WorkingDirectory 'C:\x3-project\server'
```
启动需 ~6s 端口起、~20s telnet 脚本引擎(Roslyn)编译完才能跑 GM（GM 早发会回 `ScriptEngine is not ready`）。看启动结果 grep 日志 `PlayService started`/`Server Start Failed`（`game-3080.<日期>.log`）。

**✅ GMSetServerTimeOffset 真的持久化**：重启后服务器**直接从 D30 起**（日志游戏时间戳 `[2026-06-26 ...]`），不用再 set；也 set 不了（已是 D30，再 set 同一秒=rewind 被拒）。

**❗大坑：导表后裸 --no-build 重启会崩**。本地服 config 读 `server\Resource\Assets\Res\Config\ProtoGen\*.bytes`；这目录被 config 导出/同步覆盖后（一批 .bytes + `AllTableDataMd5.txt` 同一时刻刷新），若 server 二进制没跟着重编 → 启动期 config 预载抛 `InvalidProtocolBufferException: input ended unexpectedly`（栈：`CfgHelper.StartPreloadData → CConstCfg.get_Instance`），日志 `Server Start Failed`。**现象很迷惑**：telnet 端口照常起（crash 在端口之后），连得上、脚本引擎也 ready，但所有 `!gm`/`!dump` 只回显不返结果（游戏逻辑没起来）。老进程没事只因 config 在内存里，一重启就暴露。
## ★「GM 部署某节日整套活动」先怎么找全 AO id（2026-06-23 深海/夏日实测）
要开一个节日的全部活动，**别按行名搜**（`ActvOnline` col1 备注名多是历史复用残留，如夏日恋语活动行名全叫"26情人节-xxx"，按名搜只命中个别行）。**靠节日入口分组 ActvGroup 枚举**：
1. `ActvOnline__ActvGroup.tsv` 找节日组 id（col0=id, col2=节日名）。已知：**138=夏日恋语 / 140=深海节**（97 排序那批）。
2. 在 `ActvOnline__ActvOnline.tsv` 过滤 `col38==<组id>` = 该节日整套活动（用 `csv.reader(delimiter='\t')` 解析，别 awk 按物理行——有多行 cell）。每行取 col0=AO id / col5=ActvType / col7=TimeController。
3. 逐个 `!gm @<uid> GMAddServerActivityByCfgId <AO> <分钟>`（TC=0 必给显式分钟如 43200=30天；非0给显式也行更省事）。
- 预期结果分类：`errCode=0 created`=成功；`errCode=10 already exist N activities`=已开（无需再开）；`errCode=10 cross-server...type=50`=**许愿池等跨服活动本地单服开不了**（硬限制，深海/夏日都是 type50 卡这）；`errCode=1017001 config not found`=该 AO 没在 .bytes 里（需重导，见 [[reference_x3_tsv_export_migration]]）。
- ⚠️不同节日组**模块构成不同**（夏日有开箱/拼图、深海有转盘/每日礼包/周卡/大富翁），对比两节日时先比 col38 成员差异。
- ✅**深海节完整开全套清单(2026-06-30 清库重开实测·15 AO·@被测号开)**：组140深海节8个=累充100598/BP102244/转盘101025/兑换101340/装饰阶梯106103/拜访105605/**酒馆10071704(type7)**/**签到101406(type14)**；组141深海航行=大富翁102802/大富翁兑换101341/航海通行证BP102246/拼图101828；独立(grp空)=周卡109101/深海进度礼包102993(type29)/原版大富翁102801。**许愿池105013(type50跨服)本地开不了跳过**=共14个可本地开。
  - 🪤**易错点**：① **10071704 是酒馆(type7)≠签到**，真签到是 **101406(type14)**，旧记录把 10071704 当签到是错的；② **101828拼图随102802大富翁自动开**(它是102802子活动·开102802后101828报`already exist`无需单开)；③ 周卡109101 grp 原为空(不在深海HUD)，2026-06-30 已把 col38 改 140 进深海面板(commit在dev_festival)。

## 本地服按 cfgID 开/关/查服务器活动（GM，player-scope）

GM 在 `GameServer.Hotfix\PlayerMeta\Activity\ActivityMeta.Gm.cs`，全是 player-scope → 必须 `!gm @<uid> <cmd>`：
- `GMPrintServerActivityByCfgId <cfgId>` — 查该 cfgID 当前开着哪些 activity（含 start/end，UTC 显示）。开任何活动前**先查**：同 cfgID 已存在会被开启命令拒绝。
  - 🔴**判某活动配置在不在当前服=用这个探针实测，别靠 git 分支祖先关系推断**（2026-06-24 踩坑）：曾据 `git merge-base origin/dev_festival origin/dev`=非祖先就断言"切 dev 会丢节日配置、活动失效"，结果实测 dev 上 GMPrint 世界杯 101516 返 `1017012`（配置在、可开）——**配置行可独立存在于多个分支，分支提交祖先关系 ≠ 配置内容是否存在**。所以切分支后某活动能不能开，GMPrint 探一下：`1017012`=配置在可开 / `1017001`=配置真没加载。别用分支拓扑替代实测下结论（会误报）。
- `GMAddServerActivityByCfgId <cfgId> [durationMinutes]` — 开。startTime=当前**服务器时间**(GameTime.Time)；`durationMinutes>0` 则 end=now+时长（7天=10080），**=0 则走 cfg.TimeController 反查 TimeCycle 周期长度**等长开一期。⚠️同 cfgID 已存在直接拒（`already exist N activities, remove them first`），要换窗口先 Remove；跨服类型(`CrossServerActivityTypes`)被拒（须 CenterServer 驱动）。
- `GMRemoveServerActivityByCfgId <cfgId>` — 关该 cfgID 全部 activity。⚠️重开会重置排行/奖励数据（本地测试服无所谓）。

实例(2026-06-08)：3080 服 uid=27065，101513 原 14 天窗口 → Remove 后 `GMAddServerActivityByCfgId 101513 10080` 重开 7 天。
实例(2026-06-16)：周卡活动开在 3080。**周卡活动 cfgID 链路**：`ActvWeeklyCard__ActvWeeklyCard.tsv`(ContentID=61001,内容配置=领取天数/每日自选数/奖池数) ← `ActvOnline` 第 109101 行(name=周卡特惠,ActvType=63,ContentID 列指向 61001) 指向它；GM 用的就是 ActvOnline 的 **cfgID=109101**(非内容表 61001)。该活动 TimeController 空→`durationMinutes=0` 反查不出周期,必须给显式时长(7天=10080);非跨服→可本服 GM 开。`GMPrintServerActivityByCfgId` 回 `errCode=1017012 no server activity found`=cfgID 有效但当前无实例(可开)，区别于 `1017001 config not found`(配置真没加载)。
- ⚠️**查 ActvOnline.tsv 必须用 csv 解析,别用 awk/grep 按物理行**：ActvOnline 有带换行的引用字段(如 ActvType 说明那段多行 cell),`awk NR==N` 按物理行会把 109101 错读成 109001。用 `python csv.reader(...,delimiter='\t')` 正确按记录解析。
  - **列号(2026-06-17 实测校正,以表头行为准)**：tsv 前 5 行是元数据(row0=cs/c/s, row1=类型, row2=引用表, row3=描述, row4=字段名),**数据从 row5(index 5)起**。`col0=编号(cfgID)` `col1=备注(中文活动名,如"26情人节-开箱")` `col2/3=TXT_名称` `col4=ContentID(对应应用类型的配置表ID)` `col5=ActvType(应用/UI类型)` `col7=TimeController(TimeCycle id)` `col38=GroupId`。⚠️**比旧记录(曾写 col5=ContentID/col6=ActvType)往前挪了一位,以本条为准**。文件是 UTF-8,但 Windows 控制台 codec 是 GBK→`sys.stdout.reconfigure(encoding='utf-8',errors='replace')` 再打印,否则 � 报 UnicodeEncodeError。
  - **开箱活动(ActvType=15 / ActvCrafting)cfgID 速查表**：`101513`=26元旦开箱「天马福箱」(TC1513) `101514`=26情人节开箱「致她的信」(TC1514) `101515`=26春节开箱「剑舞迎春」(TC1515) `101516`=世界杯开箱「世界杯福箱」(TC1513)。**「夏日(恋语)开箱」复用情人节开箱=`101514`**(夏日恋语节是浪漫主题,沿用情人节开箱皮)。开箱 TC 都是绝对日期型→`GMAddServerActivityByCfgId <id> 0` 能反查出真实窗口(101514 反查≈10天/101516≈14天)。
- ⚠️**`durationMinutes=0` 不是对所有 TC 都能反查**(2026-06-15 竞猜皮肤场 102913 踩坑)：TC 2913(竞猜类,Type/RoundType=5)反查报 `errCode=10 invalid TimeCycle cfgId=2913, start=-1, end=-1`→**改传显式分钟数**(30天=43200/7天=10080)绕过,startTime=当前服务器时间。开测试活动默认直接给显式时长省事。开箱 TC1513 是绝对日期型→`0` 能反查出周期(2026-06-15 实测 errCode=0,durationMs=1209599000≈14天)。
- ⚠️**「本地导表(ExportTable.py)≠更新本地服」(2026-06-16 用户问)**：standalone 仓 `C:\x3\gdconfig` 跑 `Tools/table_exporter/ExportTable.py` 输出到 `C:\x3\gdconfig\temp_dev\ProtoGen`=**纯验证临时产物,本地服不读它**。本地服读的是下条的软链路径。验证服读的那份新不新:`ls -la client/Assets/Res/Config/ProtoGen/<表>.bytes` 看 mtime;服务端读路径常量=`server/ServerCommon/GameService.Reload.cs:18 = Assets/Res/Config/ProtoGen/AllTableDataMd5.txt`。要本地服生效=走下条 jolt→pull client→重启,**不是手动 export-to-client**。
- ✅**「只热更服务器配置、不拉整个客户端」标准链路(2026-06-17 实测,热更而非重启)**：导好的配置 .bytes 由 robot 回写在 **client 远端**,本地服读软链 `Resource/.../ProtoGen → client/Assets/Res/Config/ProtoGen`。要让运行中的服吃到新配置**又不掉玩家、不重启**：① 手术式只取 ProtoGen 一个目录 `cd client && git fetch origin dev_festival && git checkout origin/dev_festival -- Assets/Res/Config/ProtoGen/`(只动这18~N个 .bytes,prefab/DK/代码/子模块指针全不碰) ② 发 `python ~/x3_gm.py "!gm ReloadGameServer"`(server-scope,无@uid)。日志验证:`ReloadAllLoadedCfgByFilenames: <表清单>` + `** ReloadTable finished, N tables reloaded` + `** Reload Finished` 无 `InvalidProtocolBufferException`。纯配置重载仅~20ms,大头是连带的 Hotfix 程序集重编(~7s);期间 `Thread maybe stuck` ERROR 是看门狗对主线程阻塞的正常告警,非真错。**只热服务端,客户端不受影响**(客户端要新配置得自己刷,本地服热更碰不到它)。
- 🔴**手动 cp .bytes 到 client ProtoGen 后 ReloadGameServer 报 `0 tables reloaded`=没生效(2026-06-30 踩坑·本地导表→手动部署链路必看)**：`ReloadGameServer` 靠 **`Assets/Res/Config/ProtoGen/AllTableDataMd5.txt` 清单 diff** 决定重载哪些表（日志 `ReloadAllLoadedCfgByFilenames: <表>` + `N tables reloaded`）。**只 `cp` 新 .bytes 不更新 manifest → 清单没变 → `0 tables reloaded`**（标准 `git checkout origin/... -- ProtoGen/` 流程不踩是因为它把 manifest 一起带了）。修=把本地导表产物 `temp_dev/ProtoGen/AllTableDataMd5.txt` 里对应表的新 MD5 同步进 client manifest 再 reload（manifest 行格式 `Table.bytes : <md5>`）→ reload 即 `N tables reloaded`。
- ⚠️**`0 tables reloaded` 有两种含义别混淆(2026-06-30)**：① **manifest 没更新**(上条·cp 没带 md5)=没生效需修；② **已被前一次 reload 载过**(manifest 已是最新·本轮无新变化)=正常,服已是最新。判别=看该表 .bytes 是否在某次更早的 `ReloadAllLoadedCfgByFilenames: <清单>` 里出现过(出现过=已载·case②)。实例：本地导表 14:57-15:01→15:02 一次 reload 已载 30 表(含 ActvOnline+全 i18n)→15:06 再 reload `0 tables`=已最新非 bug。
- ⚠️**`** Reload Finished` 可能打 ERROR 级但 benign(2026-06-30)**：慢重载(含 Hotfix 脚本 Roslyn 重编~3s)时该汇总行是 ERROR 级(快重载~900ms 是 INFO)。**只要子步骤 `ReloadScript finished`/`OnReload finished`/`Reloading N entities` 全 finished 且无 Exception/堆栈=成功**,别被 ERROR 级吓到误报失败(跟 line80 的 `Thread maybe stuck` ERROR 同属 benign 标记)。
  - **本地导表→热更本地服完整链路(2026-06-30 实测全过)**：① `cd Tools/table_exporter && python ExportTable.py`(读 tsv·verify_xlsx_tsv 闸门已删故不用建 xlsx·成功=protoc+localization bytes+MD5 无 Exception·**这步即等价 jolt 的配置校验**·Jenkins 挂时用它验配置)② `cp temp_dev/ProtoGen/<改的表>.bytes` + `i18n/*.bytes` → `client/Assets/Res/Config/ProtoGen/`(只 cp 改的表·避免动别人 schema 变更的表免 InvalidProtocolBuffer)③ **同步 manifest MD5**(上条)④ `!gm ReloadGameServer` 看 `N tables reloaded`⑤ GM 开活动。BP 这种多 sheet 表 bytes 按 **sheet 名**(BattlePassScore.bytes / BattlePassScoreReward.bytes)不是表名。
  - 🔴🔴**漏跑一步大坑：配置新增了枚举值(新JumpType/TaskType/FunctionType档)时,只 cp bytes 不够——还得跑 `copy_numeric_files.py` 把导表生成的枚举 .cs 搬进 client(2026-07-01 实证)**。ExportTable 会在 `Tools/table_exporter/` 目录**重生成 8 个代码文件**(FunctionJumpType.cs/TaskType.cs/CommonTaskType.cs/FunctionType.cs/NumericType.cs/NumericValueDictionary.API.cs/CfgProtoTextEx.cs + tableResInfo.txt),但**本地导表流程只 cp bytes、没搬这些 .cs**→client 的枚举缺新值→**运行时 `((FunctionJumpType)46).ToString()` 返 "46" 而非 "GuideShopExpand"→按 `46.asset` 找 GuideShopExpand.asset 找不到→跳转/加载失败**。修=`cd Tools/table_exporter && CLIENT_PATH="C:/x3-project/client" python copy_numeric_files.py`(它按 COPY_PLAN 把 8 文件 copy 到 client 对应路径**并 os.remove 源=move**;client_path 从 env `CLIENT_PATH` 或 `local.json` 取)。⚠️搬完 **client 是 .cs 代码改动→必须 Unity 重编**(Editor 检测.cs自动重编)才生效;这些 .cs 会显 `git status M`,待重编+提交。**判据:配置只改数值→只需bytes;配置动了 def/枚举(新增行导致 jumptype_def/tasktype 等 def 产出新 enum)→必跑 copy_numeric_files.py + 客户端重编**。生成器=`GenNumericCode.py`,def 在 `Tools/table_exporter/def/*_def.py`。
  - 🔴**单表导出绕不开别的表的校验错(2026-06-30 实测)**：某表(如 Reward 组内 id 不连续)校验失败会挂掉**全量导表**(all-or-nothing)。想 `export_tables(out,tsv,['ActvOnline__ActvOnline.tsv'])` 只导单表绕过→**对 ActvOnline 失败** `AttributeError: 'NoneType' object has no attribute 'table'`(ActvOnline 的 PostProcessData 要解析它引用的其它表·单表加载不全)。**结论:导表报某表校验错=必须修那个表,没有"只导我要的表"捷径**。修法走正常流程(若错在别人 commit 已修的表→`git checkout origin/<分支> -- tsv/<该表>.tsv` 单取修复版,不动自己的改动)。
  - 🔴**ActvGroup(活动分组/HUD归属)是客户端侧分组,改 group 列后服务端 reload 不让客户端重新分组(2026-06-30)**：`ActvOnline.col38(活动组)` 决定活动在哪个 HUD 面板。改了它导表→`!gm ReloadGameServer` 只更新**服务端**内存配置(服务端本就不按 group 过滤下发);**客户端按它自己加载的 `client/ProtoGen/ActvOnline.bytes` 分组**→必须让**客户端重载/重启**(本地 Unity 客户端读同一份 client/ProtoGen·重启或 reimport 那个 .bytes)才会把活动归到新组。实例:把周卡 109101 col38 空→140(深海节),服务端 reload 了 ActvOnline,但要 Unity 客户端重载才在深海面板看到。**判"改了配置客户端没变"先分清是服务端配置还是客户端分组/显示配置**。
  - ⚠️**X3 隔离闸门(`x3_config_isolation_gate`)放行 marker 必须单独一条命令先建(2026-06-30)**：主仓 `C:\x3\gdconfig` 有未收尾改动时,改 tsv 被闸门拦,给 `New-Item .../.x3_gate/<sessionid>.ok` 放行选项。但闸门是 **PreToolUse**(命令执行前检查)→把"建 marker"和"改 tsv"写在同一条 Bash 里**无效**(检查时 marker 还没建)。必须**先单独一条命令建 marker,再跑改 tsv 的命令**。确认未收尾改动是自己/本任务的才放行,否则开 worktree 隔离。
  - ⚠️**错误码辨义**：`GMPrintServerActivityByCfgId` 返 `1017012 no server activity` **≠ 配置存在**——它只查玩家的活动实例、**不校验 cfg 表**；`GMAddServerActivityByCfgId` 返 `1017001 config not found` 才是 **cfg 真没加载**(reload 没生效的信号)。别拿 Print 的 1017012 当"配置已就绪"。
- 🔴🔴**手动 cp 的 client .bytes 会被 `git pull/checkout` 还原成 origin 旧版(2026-06-30 大坑·jolt 坏时手动部署测本地服必看)**：`client/Assets/Res/Config/ProtoGen/*.bytes` 是 **git-tracked**(robot 在 jolt 成功时回写 origin)。**jolt 坏着时 origin 的 bytes 是旧的**(robot 没提交新版)。你手动 `cp` 进去的新 bytes = 未提交的工作区改动(`git status` 显 `M`)→ 一旦在 x3-project 跑 `git pull --rebase`/`git checkout`(哪怕只为拉别人别的提交),**被 pull 命中的那张表 .bytes 会被还原成 origin 旧版**(我的 4035xxx 没了),没被 pull 命中的表(显 `M`)幸存→**客户端加载出「这张表新+那张表旧」的不一致状态→UI 崩**。本次现象=航海通行证 Reward.bytes 被还原成旧版(缺 4035xxx)、BPR.bytes(组144)幸存→BP 奖励界面 NRE。**判定**：`stat -c%s client/.../ProtoGen/X.bytes` vs `temp_dev/ProtoGen/X.bytes` 大小不等=被还原了；`git status` 该文件**不显 M**=已被还原成 HEAD(旧)。**修=重新 cp 我的 temp_dev 版本回去 + 对齐 manifest MD5 + 重载**(客户端要重启 Play)。**根治=修好 jolt**(robot 提交新 bytes 上 origin,pull 就不再覆盖)。**测试期铁律：jolt 没好前,别对 client 仓 ProtoGen 跑 pull/checkout**。
- ⚠️**jolt 宕机期手动回写 client bytes 前,先查 robot 有没有恢复(2026-06-30 险些重复劳动)**：jolt 导表机故障期我手动 cp bytes 测本地服;准备「替 robot 把 bytes commit 上 origin 做持久化」时,`git fetch` 发现 origin 领先的提交全是 `-robot-NNNNN`=**robot 已恢复并把最新 tsv(含我的航海通行证)导出回写 origin 了**。我的手动 commit 反而和 robot 版冲突(ActvOnline.bytes/manifest binary conflict)。**正解=别硬合,`git rebase --abort` → 看 `git log HEAD..origin/dev_festival` 是不是 robot 提交 → 是就 `git reset --hard origin/dev_festival` 取 robot 版(丢自己的手动 commit)**。**判据**：origin 新提交带 `-robot-` 后缀 = jolt 活了、bytes 已正确分发,手动回写多余。**所以手动部署测本地服只是「jolt 真宕」时的临时桥;每次要 commit bytes 前先 fetch 看 robot 恢复没**。恢复后:client `git reset --hard origin` + `!gm ReloadGameServer`(本次 30 表 reloaded 无 proto 错)+ 客户端重启 Play,持久化由 robot 兜底(pull 不再还原)。
- 🔧**「BP/活动奖励界面 NRE 崩」排查链(2026-06-30 验)**：客户端 Editor.log 抓栈→`UIActvBattlePassScore.UIBattlePassScoreItem.RefreshView:131` NRE→`freeEndowItems`(=`EndowHelper.GetPreviewEndowItems(FreeReward)`)为 null→`CheckGIDAvaliable(gid)`=`CReward.RewardInfos.ContainsKey(gid)` 为 false(日志打 `gid X is not existed`)→**该 RewardID 不在客户端 Reward 表**(配置缺/被还原)。⚠️**客户端代码健壮性缺口**:`UIActvBattlePassScore.UIBattlePassScoreItem.cs` 行131(免费轨)/141(至尊轨)取 `.Count` **没空判**,只有行136(进阶轨)是 `?.Count ?? 0`→**任一奖励 gid 缺失 = 整个 BP 界面崩**(非优雅跳过)。建议反馈客户端三处统一加空判;但根因多是 Reward 数据缺(查 gid 在不在客户端 Reward 表)。
- ⚠️**`server_reload.py classify/reload` 看不见 pull 进来的配置(2026-06-17 踩坑)**：该脚本(`.claude/skills/DebugUtils/scripts/server_reload.py`)只扫**工作区**(`git status` + `git diff HEAD`),为"本地手改文件再热更"设计。**pull/导表回写是已提交改动(HEAD已含、工作区干净)→classify 报 `no-server-impact`、reload `skipped: nothing to reload`**,对它毫无作用。且它在 x3-project 根跑,client 是独立子仓更看不进去。→ pull 来的配置别指望这脚本,直接走上一条的手术式 checkout + `!gm ReloadGameServer`。
- ✅**更优:client 仓有别人 WIP 时,别 stash→pull→pop,改手术式 checkout(2026-06-16 实测)**：jolt SUCCESS 后 robot 把 .bytes 回写远端,要拿到本地只需更新 ProtoGen 这一个目录——`cd client && git fetch origin dev_festival && git checkout origin/dev_festival -- Assets/Res/Config/ProtoGen/`。**只碰配置 bytes,完全不动工作区的 prefab/DK/切图/gdconfig 子模块指针等在途 WIP**,规避 stash-pop 冲突 + rebase 子模块指针冲突两个雷。然后直接重启本地服(数据变更无 schema 改 → `--no-build`)。.bytes 是二进制 protobuf,验证更新看 `git status`(ProtoGen 下 .bytes 变 M)或 mtime,别 grep 明文。启动成功标志=日志 `StartPreloadData All Table Data cost` 不抛 `InvalidProtocolBufferException` + `PlayService started`。
- ⚠️**本地服 config 软链 client 仓→新导的配置必须先 pull client 才生效**(2026-06-15 开箱101516 卡 2 轮)：本地服 `Resource/Assets/Res/Config/ProtoGen` 是**符号链接 → `client/Assets/Res/Config/ProtoGen`**(MakeLink.py 的 link_config)。jolt 导表后 config 由 **robot 提交回写 client 仓**(commit 尾 `-robot-NNNNN`),本地 client **没 pull = 本地服读旧 config** → GM `GMAddServerActivityByCfgId` 报 `errCode=1017001 activity config not found`(配置真没有,不是服务端没重载)。修法链:① client 仓 `git stash -u`(护住注册的DK/切图等工作区)→`git pull --rebase origin dev_festival`(拉 robot 回写的 .bytes)→`git stash pop` ② 重启本地服(.bytes 数据更新、schema 没变则 --no-build 即可,CfgProtos 没比 dll 新就不用重编) ③ 再 GM 开。验证 client 是否到位:`ls -la client/Assets/Res/Config/ProtoGen/ActvOnline.bytes` mtime 应=导表时刻。⚠️.bytes 是二进制 protobuf,grep 活动 ID 搜不到(明文不存),别用 grep 判存在。
- ⚠️**telnet 返空≠失败,日志才是真相源**(2026-06-15)：x3_gm.py 在服**刚重启就绪/重负载(debug日志刷屏)**时,GM 命令常"只回显 `>>> ...` 不返结果"(读取窗口被 banner 的 IAC 协商字节/慢响应吃掉),**别据此判 GMAdd 失败重复发**。真相=查服务端日志：成功开活动有 `UID[x] AddNewActivityIds: activityId:..., cfgId:102913, isServer:True` + `PrintServerActivityByCfgId ... count=1` 带 start/end 窗口行。
- ⚠️**判「服是不是停了/死了」别看 telnet 返空,用三条硬证据(2026-06-25 实测,用户报"3080停了"实际没停)**：① **日志在实时推进**(`ls` 看 `game-3080.<日期>.log` mtime 是否=当前时刻附近,或 tail 看末尾时间戳一直在涨)=游戏逻辑活着;② **端口 LISTENING**(`netstat -ano | grep 26080`(=23000+nid) 有监听+对应 GameServer.exe pid)=能连;③ 末尾无 `Server Start Failed`/`InvalidProtocolBufferException`/真 ERROR。三条都满足=服好的,telnet 返空只是读窗口吞响应。**`guidLost`/`GetAsync` HttpClient TimeoutException 是良性**(本地连不到外部平台/TGS 服),不是崩溃。**`[Telnet] skip refs assembly=ℛ*... reason=noLocation` 这条 WARN(带 `at HEngine.TelnetModule.OnClientConnectedAsync` 调用栈)也是噪音**——每次 telnet 连接(含每次 x3_gm.py 探活)都触发,是脚本引擎跳过动态 Roslyn 程序集的正常告警,**不是异常**。用户报"服停了"多半=游戏客户端连不上/登不进(客户端侧或登录握手),先确认是不是 server 进程问题再动手,**别盲目重启好端端的服**(会断连接,虽然已落库的活动/时间offset会保留)。

⚠️**跨服活动本服 GM 开不了**：`CrossServerActivityTypes` 里的 type 会被 `GMAddServerActivityByCfgId` 直接拒（`cross-server activity is not supported via this GM`，逻辑在 `GameServer.Hotfix\PlayerMeta\Activity\ActivityMeta.Gm.cs:79`）。实例(2026-06-09)：105009 26元旦-许愿池 ActvType=50 被拒——许愿池/跨服类活动须 CenterServer 驱动，本地单服测不了。

## ★KVK/跨服活动（如风暴逐鹿）怎么开 — Center 驱动，不走 GameServer GM（2026-06-24 调研）
- **风暴逐鹿 = `ActvOnline` id `102001`，ActvType=20（KVK对战）**，属 `ActvGroup 104`「风暴神殿」系列：备战102402(type24)/BP 102201/兑换101329/积分援助105902(type59)。
- **跨服活动由 CenterServer(节点 csid=61) 驱动**，GameServer 的 `GMAddServerActivityByCfgId` 对它直接拒。开/驱动 GM 都在 **Center 侧**：
  - `GMAddCrossServerActivityByCfgId` / `GMRemoveCrossServerActivityByCfgId` — 开/关跨服活动（`CenterServer\CenterService.Gm.cs` → `CrossActivityModule`，`CrossActivityMgr.Ark.cs:261-372`）；`GMForceRemoveGlobalActivity` 强删实例。
  - `GMSetKvkRoom <kvkID> <serverIDsStr>` / `GMDeleteKvkRoom <kvkID>` — 配 KVK 房间，指定哪些服参战（`CenterServer.Hotfix\Module\ServerMapCenter.cs:429/454`）。
  - `GMKvkActivityEnterNextState <activityId>` / `GMResetKvkActivityState` — 推进/重置 KVK 阶段（备战→对战→结算）（`CenterServer.Hotfix\CrossServerActivityMeta\CrossServerActivityKvkMeta.cs:548/567`）。
  - `GMForceSyncKvkSeasonActivityInfo`（KvkSeasonMeta.cs:369）/ `GMSetKvkServerTime <kvkSvrID> <time>`（GameServer BasicMeta.Gm.cs:252）/ `GMSetCenterAndKvkServerTime`（CenterService.Gm.cs:13）/ `GMReloadKvkServer`（CenterPreloadModule.cs:85）。
- **本地跑 KVK 的硬前提（2026-06-24 实测当前环境缺）**：① **CenterServer(节点61) 进程必须在跑**——实测当前只有 GameServer(3080)+MapServer(3081)，**Center 没起**，所以 KVK 一步都起不了（GameServer 带 `-csid 61` 只是指向，Center 进程要单独拉）。② 要**两个 game 服**（如 3080 + 3070，各自 MapServer nid=sid+1）进同一 KVK 房间(GMSetKvkRoom)。③ 可能还要独立 KVK 战斗地图服节点。④ KVK 赛季/模板表（KVKTemplate/KVKSeason 等，`gdconfig\Tools\table_exporter\def\kvk*_def.py`）。
- **本地起服/起 Center 的确切命令（2026-06-24 从 `server\Tools\start_local_*.bat` + `local_conf.ini` 取证）**：
  - Center：先 `dotnet build CenterServer.Hotfix\CenterServer.Hotfix.csproj`，再 `dotnet run --no-build --project CenterServer -- -sid 61 -nid 61 -csid 61 -e local -ll debug -lf logs/center.log`（脚本 `Tools\start_local_center.bat`，读 local_conf.ini 的 centerid）。Center telnet 端口=23000+61=**23061**。
  - 第二个 game 服 3070：`dotnet run --no-build --project GameServer -- -sid 3070 -nid 3070 -csid 61 ...` + MapServer `-sid 3070 -nid 3071 -csid 61 ...`（nid=sid+1，同 3080 套路；DB gs_game_3070 首登自动建）。
- **本服榜 vs 跨服榜 发奖时间口径不同（2026-06-24 实测）**：① **本服排行榜**（如世界杯开箱 CfgID 19，GameServer 侧）结算用 **GameServer 时间**，调 `GMSetServerTimeOffset` 跨午夜即可触发（见上「测活动到期结算」）；② **跨服排行榜/KVK 榜**结算用 **center 时间**，要在 **center 上**跑 `GMSetCenterAndKvkServerTime <时间>`（`CenterServer\CenterService.Gm.cs:13`）推进 center 跨天才发奖——光改 GameServer 时间没用。⚠️**但本地没有 center**（实测 `localhost:23061` 端口关、无 CenterServer.exe），所以**跨服榜发奖本地测不了**，跟 KVK 卡在同一个「无可控 center」坑（共享 etcd node 61 被占，见下）。共享/远程 center 的时间**绝不能动**（影响全团队 dev）。
- 🔴🔴**致命墙：etcd/DB/支付 全在共享远程主机 `172.20.90.151`（etcd:2379 / Mongo:27017），不是隔离本地环境**（2026-06-24 实测）。起 Center 直接 `InitDiscovery Failed`——`WARN NodeID 61 already used, holder is {serverID:61,nodeID:61,service:"CenterService"}`：**node 61 已被一个 CenterService 占用**（本地无 CenterServer.exe 进程→是别的机/共享的 Center 或早先 stale 租约，holder JSON 不含 host 看不出）。**含义**：① 本地起 Center 抢不到 node 61；② 在共享 etcd 上抢节点/清 key 会影响整个团队 dev 环境，**别硬干**；③ 起 3070/3071 也注册到共享 etcd，节点号不能跟别人撞。**所以「本地隔离搭 KVK」这条路在共享 discovery 下走不通**——要么用已有的共享 Center（查它在哪台机、telnet `172.20.90.151:23061`？），要么得隔离的 etcd/db env。**搭 KVK 前必须先跟团队确认 discovery 拓扑（共享 vs 隔离）+ node 号分配**，否则白忙+可能干扰别人。（注：GameServer 重启偶发的 `NodeID already used` 是自己刚停的进程 etcd 租约没过期、等 ~20s 重试即可，跟这个"别人/共享占用"是两回事。）
- 🔑**本地服 ID 段定义（2026-06-24 取证 `client\Assets\TFWCore\Script\Common\CommonConst.cs:93-119`，解释了之前所有 center 卡点）**：`IsLocalServer`=env≠GOLD；**local center 段 = `71~99`**（`LOCAL_CENTER_SERVER_MIN=71/MAX=99`，`IsLocalCenterServer(id)=71≤id≤99`）；**local kvk 段 = `950~999`**（`IsLocalKvkServer`）。
  - 🔴**根因：之前本地 csid=61 不在 71~99 段 → 代码判定 61 是「共享/正式 center」不是本地**。所以：① 本地起 center(61) 在共享 etcd 抢 node 61 失败；② `GMSetLocalClusterServerTime` 内 `IsLocalCenterServer(61)=false` → 直接拒（"dev server not enable change server time"）；③ telnet 直连 61 改时间=动共享 center 影响全团队，禁。**本地 center 必须用 71~99 段**（`start_local_center.bat` 注释默认就是 71）。
  - ✅**本地测跨服榜/KVK 的正路（2026-06-24 定）**：本地 center 取 71~99 内一个号（如 **90**）→ 改 `local_conf.ini centerid=90` → 起本地 CenterServer：`dotnet run --no-build --project CenterServer -- -sid 90 -nid 90 -csid 90 -e local` → 各 game 服挂 `-csid 90`（3080/3070 都改）→ 这时 `IsLocalCenterServer(90)=true`，GM **`GMSetLocalClusterServerTime <kvkSvrID> <时间>`**（`BasicMeta.Gm.cs:291`，会同时设本地 game 时间 + `SendCenterServiceMsg(centerID)` 同步 center + `SendKvkServiceMsg`）才生效、能推 center 跨天结算跨服榜。普通 `GMSetServerTimeOffset` 只改本地 game、碰不到 center（所以之前跨服榜没结算）。
- ⚠️**没有现成的「本地搭 KVK 多服」ops 脚本/文档**（2026-06-24 翻遍 KB/memory/仓库 docs+Tools 只有架构文档，无搭建步骤）。
- 架构原理文档：`C:\x3-project\AIDocs\x3-frameworks\跨服活动框架_Server.md`（CrossServerActivity·Center侧调度）+ 同目录 `主从同步-center-follower_Server.md` / `服务发现-etcd_Server.md`。KVK reload 脚本 `server\Tools\Reload\reload-kvk.bat`。
- ✅**本地 center 90 实操成功（2026-06-24）**：`local_conf.ini centerid=61→90`，`dotnet run --no-build --project CenterServer -- -sid 90 -nid 90 -csid 90 -e local`。结果：**node 90 在共享 etcd 无冲突**（不像 61 被占）、config `--no-build` 干净加载（`StartPreloadData All Table Data cost` 无 `InvalidProtocolBufferException`）、`Telnet server started at localhost:23090`、`CenterService started`。⚠️但 center 90 在共享 etcd 上会 **discover 到全部其他服**（实测 200/220/280/290/1530/3080 等，日志刷 `OnServiceUp`+`SyncCenterCmdInfoToGame`）——这些服 csid=61 仍归 center 61 管，center 90 只是看得见、**不驱动**它们；属共享 discovery 的已知现实，不是故障。
- 🔴**第二个本地服（3070）起不来根因=未 provision（2026-06-24 实测）**：MapServer 报 `ServerInfo not found! 3070`（`Play.ServerInfoMgr.OnInit` 的 DB `FindOneAsync` 查无记录）→ Server Start Failed；GameServer 3070 死得更早（连日志都没建）。center 也只 discover 到既有服、无 3070。**含义：3070 这个 sid 本地从没建过库/ServerInfo**。要本地搭双服测跨服榜/KVK，先解决「新本地服怎么 provision（ServerInfo 记录 + gs_game_<sid> 库怎么建）」——不是改 csid 就能起。下次「换个服」当第二服，优先挑**已 provision 过的服**（但别动别人 csid=61 的共享服）。
- ⚠️**x3-project 里禁跑 `git clean -fd`（2026-06-24 踩坑）**：`git clean -nd` 显示会连带删 `client/Assets/AVProVideo/Editor`、`client/Assets/Domain`、`client/Assets/Res/WeatherSystem`、`client/Assets/Scripts/CSShared*` 等**大量 untracked 但必需的目录**（不在 .gitignore）。要丢某个 untracked WIP 文件就**精确 `rm <具体路径>`**，绝不 blanket clean。
- 🔑**仓库结构（2026-06-24 校正）**：`client` 是 **x3-project 的普通子目录**（无独立 `.git`）→ 切 x3-project 分支 = client 一起切，不用单独切客户端。`gdconfig` 是 **hook 管理的 gitlink**（`.gitmodules` 里没有它，`git submodule` 命令报 `no submodule mapping`），切分支时 **post-checkout 钩子自动把 gdconfig 切到对应 code branch**（日志 `[gdconfig] checked out '<branch>' for code branch '<branch>'`），切完 `git status` 常驻 `M gdconfig (new commits)`=gdconfig 在其分支 tip 领先 superproject 记录的 pin，**这是该仓正常态（gdconfig 跟分支不跟 pin），别去 reset**。
- ⚠️**切 x3-project 分支几乎必被「Unity 本地重导噪音」挡住（2026-07-08 一天撞 3 次）**：本机 Unity 开过工程就会重写一批 .meta（HeroHarmony 视频 meta 的 `userData:` 行尾空格、Club mask 贴图 `textureFormat` 29/50→4、spriteatlas 等），checkout 报 would be overwritten。**固定处理**：①先 `git diff` 抽一个确认是噪音（空格/importer 重写、非人工改动）②`git stash push -u -m "<分支>上Unity重导噪音(<内容>)"` 收起再切（-u 连带未跟踪 meta）③噪音 stash 攒多了征得用户同意后 `git stash clear`。别 checkout -- 直接丢（万一混着真改动），可逆操作直接做不用问。
- **切节日分支标准流程（2026-06-24 实操）**：① 摊 WIP 清单给用户确认处置（在途仓铁律）② 丢 WIP 用精确 rm（见上 clean 禁令）③ `git checkout dev_festival`④ 本地分支若与 origin 分叉且本地那笔是用户自己的 commit→`git pull --rebase`（autostash 会自动 stash 脏文件、replay 用户 commit 到 origin tip 之上，别 `reset --hard` 丢用户 commit）⑤ 切分支=代码变=**必重编 Hotfix**（`dotnet build GameServer.Hotfix.csproj` + `MapServer.Hotfix.csproj`，看 `0 个错误`再起；dev_festival 早上的 GiftMeta CS 错到晚上 origin tip 已修）⑥ 重编前先 `stop_gs.py` 解 dll 锁 ⑦ `--no-build` 起。

## 本地服开/推礼包（Pack，≠活动，player-scope）

礼包不走活动 GM，走 `GameServer.Hotfix\PlayerMeta\Gift\GiftMeta.cs` 的 `GMOpenGiftNtf <packCfgID>`：取当前服务器时间为 start，若 `TriggerType=时间点(TIME_POINT)` 则 endTime 按 `TriggerParamVals[0]`(=触发 TimeCycle ID)算，再 `TriggerNewGiftOpenNtf` 把开包推送给玩家。**player-scope** → `!gm @<uid> GMOpenGiftNtf <packID>`，**只推给那一个玩家**（换账号测要对该 uid 再推一次）。要求 packType ∈ `GiftConst.TriggerPackTypes`。
实例(2026-06-09)：210516/210517 两个 26元旦礼包(触发 TimeCycle=1824) → `!gm @27065 GMOpenGiftNtf 210516`/`210517`，errCode=0。
其余礼包 GM：`GMTriggerChainPack`(链式)、`GMResetGiftPurchaseNum`(重置购买次数)、`GMTriggerRecommendGift`(推荐礼包)。礼包按什么机制开看 [[reference_x3_pack_open_mechanisms]]。

## ❗GM 开了活动但客户端看不见——根因链（2026-06-09 排查）

服务端 `GMPrintServerActivityByCfgId` 查得到、窗口有效 ≠ 客户端能看见。下发给客户端要过两道，缺一个就静默不显示（日志零条 `SendToClient` 活动 Ntf）：
1. **推送时机**：GM 造活动(`CreateNewServerActivity`)只**实时推给"创建那刻已在线+海域匹配"的玩家**(`PlayerMgr.OnSeaAreaActivityCreate`→player 端 `ActivityMeta.OnSeaAreaActivityCreate`)。其余玩家靠**重新登录**触发 `HandleServerActivityInfo` 重新拉列表。→ **测试号当时不在线/没刷新 = 看不见；让它退登重进即可重新同步**（最常见，先试这个）。
2. **解锁闸 `CheckActivityIsUnlock`**(`ActivityMeta.cs:343`)：推送/登录同步前都过它，任一不满足就 `continue`(不下发)——查 `ActvOnline` 这几列：`PlayerLv`(区间[min,max]，**测试号被GM顶到>max 会被卡**)、`RechargeAmount`(累充额)、`RequireFunction`(功能解锁)、`FinshTask`(前置任务)。
3. ⚠️**timecycle 不在服务端同步路径里查**：`HandleServerActivityInfo`/`OnSeaAreaActivityCreate` 都**不**调 `CheckActivityTimeCycleIsOpen`，所以服务端会照常下发——但**客户端日历 UI 可能自己按 `ActvOnline.TimeController` 的 TimeCycle 窗口过滤**。若 GM 把活动开在了 TimeCycle 配置窗口之外（如元旦档 TimeCycle 1824 配的是 2026-01-01 起14天，却在服务器时间7月强开），重登后客户端可能仍不显示。修法：临时把该 TimeCycle 的 StartTime 改到覆盖当前服务器时间、重导配置。
4. **❗海域匹配（最阴的坑，2026-06-09 实测命中）**：`GetSeaAreaActivityList`(`ActivityMgr.cs:264`) 按 `activity.SeaArea` vs 玩家 `OriginSeaArea` 过滤(`SeaAreaConst.IsMatched`)。而 `GMAddServerActivityByCfgId` 建活动时 `originSeaArea = 执行者(Master=@uid).OriginSeaArea`——**用谁的号跑 GM，活动就建在谁的海域**。若拿 A 号(海域1)开、B 号(海域4)测，B 登录同步时被海域过滤器挡掉，activityId 全程零 `SendToClient`，怎么重登都看不见。**修法：用被测号自己当执行者重开**（`!gm @<被测uid> GMRemoveServerActivityByCfgId <id>` 再 `GMAddServerActivityByCfgId <id>`），重建日志里 `originSeaArea=` 会变成被测号的海域，重登即可见。实例：27065=海域1、27530=海域4，按27065开的27530看不见；以@27530删重建(originSeaArea=4)后解决。

排查顺序：①日志 grep 活动 activityId 看有无 `SendToClient`（零=服务端就没下发）②**海域**：确认开活动的执行者 uid 和被测 uid 是不是同一海域（不同就用被测号重开）③查 PlayerLv 等解锁列+对玩家等级 ④仍不行才查客户端 TimeCycle 窗口。**经验默认值：开本地服测试活动直接用被测号当 @uid 跑 GM，省掉海域坑。**

## 重启本地服流程（+ 一个大坑）

**停**：`python C:\x3-project\server\Tools\stop_gs.py --server_id 3080 --grace 10`（按 sid 同时停 Game+Map，优雅 CTRL_BREAK→超时强杀）。**依赖 psutil**（已 `pip install` 进 C:\Python314）。
**起**（脱离会话、不重建用 --no-build）：cwd=`C:\x3-project\server`，先 Game 再隔 ~5s 起 Map（Map 的 nid=sid+1，3080→3081）：
```
Start-Process dotnet -ArgumentList 'run --no-build --project GameServer -- -sid 3080 -nid 3080 -csid 61 -e local -ll debug -lf logs/game-3080.log' -WorkingDirectory 'C:\x3-project\server'
Start-Process dotnet -ArgumentList 'run --no-build --project MapServer  -- -sid 3080 -nid 3081 -csid 61 -e local -ll debug -lf logs/map-3080.log'  -WorkingDirectory 'C:\x3-project\server'
```
启动需 ~6s 端口起、~20s telnet 脚本引擎(Roslyn)编译完才能跑 GM（GM 早发会回 `ScriptEngine is not ready`）。看启动结果 grep 日志 `PlayService started`/`Server Start Failed`（`game-3080.<日期>.log`）。

**✅ GMSetServerTimeOffset 真的持久化**：重启后服务器**直接从 D30 起**（日志游戏时间戳 `[2026-06-26 ...]`），不用再 set；也 set 不了（已是 D30，再 set 同一秒=rewind 被拒）。

**❗大坑：导表后裸 --no-build 重启会崩**。本地服 config 读 `server\Resource\Assets\Res\Config\ProtoGen\*.bytes`；这目录被 config 导出/同步覆盖后（一批 .bytes + `AllTableDataMd5.txt` 同一时刻刷新），若 server 二进制没跟着重编 → 启动期 config 预载抛 `InvalidProtocolBufferException: input ended unexpectedly`（栈：`CfgHelper.StartPreloadData → CConstCfg.get_Instance`），日志 `Server Start Failed`。**现象很迷惑**：telnet 端口照常起（crash 在端口之后），连得上、脚本引擎也 ready，但所有 `!gm`/`!dump` 只回显不返结果（游戏逻辑没起来）。老进程没事只因 config 在内存里，一重启就暴露。
**修**：重编 Hotfix 工程再起（即 start_local_server.bat 干的事）——
`dotnet build GameServer.Hotfix\GameServer.Hotfix.csproj` + `MapServer.Hotfix\MapServer.Hotfix.csproj`（会连带编主工程，别用 server.sln——CLAUDE.md 警告它会还原未提交代码）。**重编前必须先 stop**：崩溃的 GameServer 是僵尸进程仍锁着 bin 里的 dll，不杀会 `MSB3021 文件被锁` 编译失败。server 工作树干净时重编零风险。

**✅ 起服/重启前预检（每次必做，省一次崩溃来回）**：config regen 不一定是「导表」显式触发，**会话中途别人/别的流程也可能 regen**（2026-06-12 实测：会话开头 15:50 编过、起服成功；3h 后重启崩了，因 16:06 有人 regen 刷新了 ProtoGen `.bytes` + `CfgProtos\*.cs`，旧二进制对不上）。所以**不能靠「这次会话编过」判断安全**。预检 = 比 mtime：
- `Resource\Assets\Res\Config\ProtoGen\AllTableDataMd5.txt`（config 刷新时间标志）
- `server\GameServer\CSSharedCommon\Cfg\CfgProtos\*.cs` 最新 mtime（schema 生成代码刷新时间）
- `server\GameServer\bin\Debug\net8.0\GameServer.Hotfix.dll`（上次 build 时间；不存在/找不到也当过期）

**任一 config/CfgProtos mtime > dll mtime → 必须重编再起**（裸 --no-build 会崩 `CConstCfg.get_Instance` 解析）；否则 --no-build 直接起即可。崩溃栈精确指向具体 cfg 类（如本次 `CUserScorePackBuyRule`，属 ConstCfg），是「二进制 ↔ .bytes 格式不匹配」而非文件物理截断（0 字节 .bytes 多是空表正常，别误判）。
- ⚠️**第二类重启拦路：切/合节日分支后重编 Hotfix 可能直接编译失败（别人合进的编译错）**（2026-06-24 实测）。切到 dev_festival 重启时 `GameServer.Hotfix` build 报 `1 个错误`（`GiftMeta.Activity.cs CS1503 long→string`），根因=别人 review 改动「日志 Info→Debug」把 `Logger.DebugFormat` 的**格式字符串参数弄丢了**（第一个参数变成 long）。**所有人 pull 该分支都编不过**。处理：① build 必须看到 `0 个错误`再起，别只看 mtime；② `dotnet build ... 2>&1 | grep error` 抓具体行；③ 纯日志/无业务逻辑的（缺格式串这类）可**本地补一行 unblock**（补回格式串，参照相邻 `WarnFormat` 的写法），但**这是未提交本地补丁→下次 rebuild/别人 pull 还会断**，必须 surface 给提交作者在分支正式修，别默默扛。④ 真业务逻辑编译错=别硬改，停下报告。
- ⚠️**当天 dated log 跨重启共用 → grep 判就绪会假阳性**(2026-06-15)：日志名是 `game-3080.YYYYMMDD.log`,同一天多次重启**全写同一文件**。grep `PlayService started`/`Server Start Failed` 可能命中**更早那次重启**的行=假就绪/假失败。判本次起好要看**最新一段**的 `StartPreloadData All Table Data cost N ms`(config 预载成功) 且其后无 `InvalidProtocolBufferException`/`CConstCfg`。配合 `tail` 看日志是否仍在持续输出(活着)+进程 PID 变了(确认是新进程)。
- ✅**标准重启=`Tools/start_local_server.bat` 的事**(读 `Tools/local_conf.ini` 的 sid/centerid)：make-links→`dotnet build GameServer.Hotfix.csproj`+`MapServer.Hotfix.csproj`(build.py 自动把 dll 部署到 `Resource/Hotfix/Debug`)→清日志→`dotnet run --no-build` 起 Game/Map。⚠️bat 末尾 `pause` 会卡非交互→手动跑时**别直接调 bat**,照它的步骤手动来(先 `stop_gs.py` 再 build 再 Start-Process)。运行时真正加载的 Hotfix dll 在 `Resource/Hotfix/Debug/GameServer.Hotfix.dll`,不是 `GameServer/bin/...`。


## 🔴ReloadGameServer 不编译源码！(2026-07-02 手册豪华礼包实证·纠正旧认知)
- 旧记录说"reload 连带 Hotfix 程序集重编"——**错**。reload 的 ReloadScript = `CopyFiles`(拷 bin 里**已编好**的 DLL) + ModifyWithCecil + TryLoadHotfixAssembly，**全程不碰源码**。源码改了/合了新代码 → 必须先 `dotnet build GameServer.Hotfix -c Debug` 再 reload 才生效。
- **判据**：reload 日志 `** Reload Start: copyFiles=True` + `CopyFiles finished 3ms` = 只拷DLL；改代码后想验证是否真生效，先 `ls -la GameServer.Hotfix/bin/Debug/net8.0/GameServer.Hotfix.dll` 看 mtime 是否新于代码改动。
- **服跑着时 build 会撞文件锁**（TfwProtobuf/ServerCommon.dll 被 GameServer 进程锁 → MSB3021/3027 共4错，**不是代码错**）→ 停服(stop_gs.py)→build→起服。
- **活动礼包只在 OnAddActivity 挂载瞬间创建**：玩家在旧 DLL 时期领过活动 → 新 DLL 起来重登**不会**重建礼包(活动已持久化在身上)。补救=`GMRemoveServerActivityByCfgId <id>`(只删玩家侧实例·ServerActivity 实体仍在会自动重推)→玩家重登→重推时走新代码创建礼包。⚠️`GMTakedownServerOrCrossActivityByCfgId` 本地 PlayService **无 handler**(no handler found)，别用。
- 实例：手册102702豪华礼包(Pack2)不出现——服务端 CreateActivityPaySignLuxuryGift 代码在源码里但DLL是旧的；重编+删玩家实例+重登后正常。


## 「GM开了活动但玩家看不到」诊断链(2026-07-03 手册102702实战)
1. **海域隔离**：服务器活动按海域各一份(GMAdd时锚定@uid的originSeaArea)。玩家跟实例不同海域=收不到；`GMPrintServerActivityByCfgId` **不分海域**能查到,别被骗。看玩家海域=登录日志 `OnInit new player, originSeaArea: West` 之类。
2. **GMAdd全局查重缺陷已修(本地Hotfix·未提交)**：原查重不分海域→海域1开过则海域2永远开不了(而type27等非服务器类型 GMRemove 又删不掉实体=死锁)。已改 ActivityMeta.Gm.cs 查重按 `SeaAreaConst.IsMatched` 海域匹配(对齐下发口径)。⚠️改动在 x3-project 本地未提交。
3. **玩家侧门禁拦截**：日志 `OnSeaAreaActivityCreate blocked: cfgId=X` = 玩家没过 `CheckActivityIsUnlock` 四门禁:**等级(AO col10=PlayerLv"5,99")/累充(col12=RechargeAmount,proto tag11)/功能解锁(col11)/前置任务(col13)+互斥ExcludeActvIDs**。手册102701/102702 col12=999=历史累充≥999才可见(**正式设计**·付费向活动只对付费玩家曝光·老版同款)。
4. **一键过门禁**：`!gm @<uid> GMBypassActivityUnlock <cfgId>`(测试用GM·功能/任务/累充三门禁齐过)。⚠️副作用:它是真把 TotalPayMoney 充到门槛值(全局账号属性)→其他按累充触发的活动/礼包全会冒出来,要干净零充号别用它、改临时清配置门槛。
5. **编译不停服**：只改 Hotfix 源码用 `dotnet build GameServer.Hotfix -c Debug --no-dependencies`(跳过 GameServer 主工程依赖拷贝=不撞运行中进程的文件锁)→ ReloadGameServer 热载即生效。全量 build 才需要停服。
