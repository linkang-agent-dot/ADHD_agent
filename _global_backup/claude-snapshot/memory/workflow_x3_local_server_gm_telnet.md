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
- 时间相关 GM（`GMSetServerTime`/`GMGetServerTime`/`GMSetServerTimeOffset`）都在 `BasicMeta`，是 **player-scope** → 必须 `!gm @<uid> <cmd>`，纯 `!gm <cmd>` 是 server-scope 找不到。uid 随便挑个该服玩家：从 BI 日志 `server\GameServer\bin\Debug\net8.0\logs\game-<sid>.bi.log` 的 user_event 行取（如 3080 服 uid=27065）。

**❗telnet 分包协议大坑**（`ServerCommon/TelnetServer/Server.cs` receiveData）：服务端**每个 recv 包只看 data[0]**，仅当包**首字节是 CR(0x0D)** 才判定为回车并派发命令。所以 `!cmd\r\n` 一个包发出去 = 首字节是 `!`，CR 被埋在中间，永远只回显不执行。**必须把命令体和 `\r\n` 分两个包发**（先发 body，sleep 0.3s，再发 `b"\r\n"`）。x3_gm.py 已处理。另：首字节 ≥0xF0 的包被当 IAC 丢弃。

**设到 D30 的算法**（D-day = passDay，开服满 N 天）
1. `GMGetServerTime` 读 `ServerOpenDate` + `passDay`。
2. 目标时间 = ServerOpenDate + N 天，格式 `yyyy-MM-dd/HH:mm:ss`。
3. `GMSetServerTimeOffset <目标>`（DEBUG+local 限定，**持久化、重启仍生效**）；只想本次生效用 `GMSetServerTime`。`GMSetServerTimeByDHM day hour min` 是相对当前**加**天数，不是设绝对天。
   - ⚠️**只有 `GMSetServerTimeOffset` 持久化！`GMSetServerTimeByDHM` 和 `GMSetServerTime` 都不持久(2026-06-18 实测打脸)**：用 ByDHM 调了 +1 天(D2)，重启本地服后时间**回真实当天 D1**，调的偏移全丢。所以"调时间后要重启还想保留天数"必须用 `GMSetServerTimeOffset <绝对时间>`(算法见上：ServerOpenDate+N天)，别用 ByDHM/SetServerTime。给用户答"重启后时间还在不在"前先认清用的是哪条命令。
4. 复验 `GMGetServerTime` 看 passDay。

**限制**：时间只能前进，`delta<0` 被拒（`ErrorCodePlayerDisallowRewindTime`）。要回退得 `GMClearServerTimeOffset`(下次重启生效) 或重启清库。

实例（2026-06-05）：3080 开服 2026-05-27 09:31:06，D8 → set 2026-06-26/09:31:06 → passDay 30。

## ★清库全服重启（清玩家数据那种，2026-06-16 实操）
工具 `Tools/reset_local_server.bat`（停→drop_db→重编→起），但有 `pause`+`dotnet test` 卡非交互。**手动版**（cwd=`C:\x3-project\server`，比普通重启多一步清库）：
1. 停：`python Tools/stop_gs.py --server_id 3080 --grace 10`
2. **清库**：`python Tools/drop_db.py 3080` — 删 MongoDB `gs_game_3080`(172.20.90.151:27017)整库 + 清 Common.CrossServerActivity 含该 sid 记录；**无交互确认直接删**。sid<100(Center)才额外清 PrefsInfo 时间偏移；sid≥100(3080)清库=玩家库删→**服务器时间回真实当天**(实测 D30/7-08 回 6-16)。不碰 Center(61)。
3. 重编：`dotnet build GameServer.Hotfix/GameServer.Hotfix.csproj -c Debug` + `MapServer.Hotfix/...`（cascade 主工程；跳 reset.bat 的 dotnet test 省时）
4. 起：同下方 Start-Process
5. 验：日志 `PlayService started` + 游戏时间回真实日期 + 6 进程。
- ⚠️**清库后无任何玩家**！GM `@<uid>` 作用在玩家上，清库后 uid 不存在→GM 报 **errCode=1001005 `ErrCodeLoadPlayerFail`**(不是config错)。**必须先让玩家登录(客户端登入会在新库重建该号)，GM 才能 @它**。判在不在：发 `GMPrintServerActivityByCfgId`，日志回 `LoadPlayerFail`=不存在 / `no server activity found`=存在(只是没活动)。
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
## 本地服按 cfgID 开/关/查服务器活动（GM，player-scope）

GM 在 `GameServer.Hotfix\PlayerMeta\Activity\ActivityMeta.Gm.cs`，全是 player-scope → 必须 `!gm @<uid> <cmd>`：
- `GMPrintServerActivityByCfgId <cfgId>` — 查该 cfgID 当前开着哪些 activity（含 start/end，UTC 显示）。开任何活动前**先查**：同 cfgID 已存在会被开启命令拒绝。
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
- ⚠️**`server_reload.py classify/reload` 看不见 pull 进来的配置(2026-06-17 踩坑)**：该脚本(`.claude/skills/DebugUtils/scripts/server_reload.py`)只扫**工作区**(`git status` + `git diff HEAD`),为"本地手改文件再热更"设计。**pull/导表回写是已提交改动(HEAD已含、工作区干净)→classify 报 `no-server-impact`、reload `skipped: nothing to reload`**,对它毫无作用。且它在 x3-project 根跑,client 是独立子仓更看不进去。→ pull 来的配置别指望这脚本,直接走上一条的手术式 checkout + `!gm ReloadGameServer`。
- ✅**更优:client 仓有别人 WIP 时,别 stash→pull→pop,改手术式 checkout(2026-06-16 实测)**：jolt SUCCESS 后 robot 把 .bytes 回写远端,要拿到本地只需更新 ProtoGen 这一个目录——`cd client && git fetch origin dev_festival && git checkout origin/dev_festival -- Assets/Res/Config/ProtoGen/`。**只碰配置 bytes,完全不动工作区的 prefab/DK/切图/gdconfig 子模块指针等在途 WIP**,规避 stash-pop 冲突 + rebase 子模块指针冲突两个雷。然后直接重启本地服(数据变更无 schema 改 → `--no-build`)。.bytes 是二进制 protobuf,验证更新看 `git status`(ProtoGen 下 .bytes 变 M)或 mtime,别 grep 明文。启动成功标志=日志 `StartPreloadData All Table Data cost` 不抛 `InvalidProtocolBufferException` + `PlayService started`。
- ⚠️**本地服 config 软链 client 仓→新导的配置必须先 pull client 才生效**(2026-06-15 开箱101516 卡 2 轮)：本地服 `Resource/Assets/Res/Config/ProtoGen` 是**符号链接 → `client/Assets/Res/Config/ProtoGen`**(MakeLink.py 的 link_config)。jolt 导表后 config 由 **robot 提交回写 client 仓**(commit 尾 `-robot-NNNNN`),本地 client **没 pull = 本地服读旧 config** → GM `GMAddServerActivityByCfgId` 报 `errCode=1017001 activity config not found`(配置真没有,不是服务端没重载)。修法链:① client 仓 `git stash -u`(护住注册的DK/切图等工作区)→`git pull --rebase origin dev_festival`(拉 robot 回写的 .bytes)→`git stash pop` ② 重启本地服(.bytes 数据更新、schema 没变则 --no-build 即可,CfgProtos 没比 dll 新就不用重编) ③ 再 GM 开。验证 client 是否到位:`ls -la client/Assets/Res/Config/ProtoGen/ActvOnline.bytes` mtime 应=导表时刻。⚠️.bytes 是二进制 protobuf,grep 活动 ID 搜不到(明文不存),别用 grep 判存在。
- ⚠️**telnet 返空≠失败,日志才是真相源**(2026-06-15)：x3_gm.py 在服**刚重启就绪/重负载(debug日志刷屏)**时,GM 命令常"只回显 `>>> ...` 不返结果"(读取窗口被 banner 的 IAC 协商字节/慢响应吃掉),**别据此判 GMAdd 失败重复发**。真相=查服务端日志：成功开活动有 `UID[x] AddNewActivityIds: activityId:..., cfgId:102913, isServer:True` + `PrintServerActivityByCfgId ... count=1` 带 start/end 窗口行。

⚠️**跨服活动本服 GM 开不了**：`CrossServerActivityTypes` 里的 type 会被 `GMAddServerActivityByCfgId` 直接拒（`cross-server activity is not supported via this GM`）。实例(2026-06-09)：105009 26元旦-许愿池 ActvType=50 被拒——许愿池/跨服类活动须 CenterServer 驱动，本地单服测不了。

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
- ⚠️**当天 dated log 跨重启共用 → grep 判就绪会假阳性**(2026-06-15)：日志名是 `game-3080.YYYYMMDD.log`,同一天多次重启**全写同一文件**。grep `PlayService started`/`Server Start Failed` 可能命中**更早那次重启**的行=假就绪/假失败。判本次起好要看**最新一段**的 `StartPreloadData All Table Data cost N ms`(config 预载成功) 且其后无 `InvalidProtocolBufferException`/`CConstCfg`。配合 `tail` 看日志是否仍在持续输出(活着)+进程 PID 变了(确认是新进程)。
- ✅**标准重启=`Tools/start_local_server.bat` 的事**(读 `Tools/local_conf.ini` 的 sid/centerid)：make-links→`dotnet build GameServer.Hotfix.csproj`+`MapServer.Hotfix.csproj`(build.py 自动把 dll 部署到 `Resource/Hotfix/Debug`)→清日志→`dotnet run --no-build` 起 Game/Map。⚠️bat 末尾 `pause` 会卡非交互→手动跑时**别直接调 bat**,照它的步骤手动来(先 `stop_gs.py` 再 build 再 Start-Process)。运行时真正加载的 Hotfix dll 在 `Resource/Hotfix/Debug/GameServer.Hotfix.dll`,不是 `GameServer/bin/...`。
