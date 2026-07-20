---
name: x3-push-jolt
description: X3 配置 push 后自动调用 jolt.exe 触发 Jenkins X3导配置任务，用户不用再手动跑 jolt
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9fa379f1-8095-4bed-9a37-401c299ba495
---

## 规则

任何 X3 配置改动（gdconfig 仓库）push 完，**立即**用 wrapper 调用 jolt 触发 Jenkins 导表。

### ★默认自动 jolt·不问用户(2026-06-23 用户定·强化)
**改完配置 → 本地 ExportTable → 只要本地导表成功，就直接 `jolt_verify.py <分支>` 触发，不再逐次问用户。** 只在**本地导表失败**时才停下报告。即：本地导表成功 = jolt 的放行条件，成功即放行、自动触发。（分支随当前活跃分支，如 dev_festival / feature/x3-deepsea-art；jolt 要 gdconfig 分支名==client 分支名。）
**⚠️ feature 分支必先给 client 仓建同名分支再 jolt**（2026-07-14 航海之路案实撞）：job 后半段要把 bytes 推进 x3-project 同名分支，缺=`client remote branch does not exist: xxx` exit -1 FAILURE（gdconfig 侧 gate 全过也照样 FAIL）。修法一条 API：`POST https://git.tap4fun.com/api/v4/projects/2859/repository/branches?branch=feature%2F<名>&ref=dev`（PRIVATE-TOKEN 头），再重跑 jolt_verify。

### ★标准节奏(2026-06-16 用户定)：每次传表 = 本地导表自测 → 修干净 → push → jolt 触发
**push 前必先本地导表自测**(不依赖 Jenkins、不撞并发 push、不烧构建,跟 Jenkins 同一套 def 检查)：
```
cd C:/x3/gdconfig/Tools/table_exporter && python ExportTable.py
```
(main 硬编码相对路径 `../../temp_dev` 输出 + `../../tsv` 输入,**必须 cd 到该目录跑**;会先 sync_xlsx_tsv 再转换)。看 `[Table] ERROR`/`Traceback`——**本地报错就实时改到全过,再 push+jolt**,别把已知会失败的表 push 上去烧 Jenkins。常抓错类:`ID不连续`/`depend_keys:{id} not existed`(ItemType 误填,1=道具/2=蓝图/3=嵌套子包)/字段定义。详见 [[reference_x3_tsv_export_migration]]「push 前先跑本地导表自测」。
**Why:** 2026-06-16 世界杯开箱阶梯换皮,本地导表当场抓出并发 agent 的 59812 错(若直接 jolt 会白烧 #950/#951 两个失败构建)。用户原话"后面每次传表都做一次本地导表+jolt触发,本地导表有问题实时改"。

> ⚠️ **前置（2026-05-29 起）**：导表读「提交的 tsv 缓存」不读 xlsx。改完 xlsx 必须先 `python scripts/xlsx_to_tsv.py --files <xlsx>` 重生成 tsv 并 commit，再 push+jolt，否则导出的是旧数据。详见 [[reference_x3_tsv_export_migration]]。

## 工具

- 入口：`C:\Users\linkang\.claude\jolt_export.py`
- 用法：`python C:\Users\linkang\.claude\jolt_export.py <branch>`（默认 `dev-summer-love-song`）
- 底层：jolt.exe (`C:\x3-project\Tools\Jolt\jolt.exe`) 是 Jenkins 快捷构建客户端，REPL 模式，wrapper 用 stdin 喂 `excel branch=... code_branch=...\nexit`

## Jenkins 任务

- 名称：**X3导配置**
- 入口：http://172.20.110.29:8080/job/X3%E5%AF%BC%E9%85%8D%E7%BD%AE/

## 输出语义

- `触发失败: 任务正在执行中 (#N) <URL>` → **不是错误**，说明已有 build 在跑（push 后 Jenkins 通常已自动触发），重复触发被拒；这种情况无需 retry，等当前 build 完即可。
- 正常触发会给新 build URL，把链接报给用户。

**Why:** 用户原话"后面我就不用再去导表烧脑了"——把"push → 跑 jolt → 等导表"这一段委托给我。2026-05-25 累充隔离需求 commit 042daba 后落地。

**How to apply:**
1. 改完 X3 任何 xlsx 或 Tools/* 代码 → git push → 立即 `python C:\Users\linkang\.claude\jolt_export.py <分支>`
2. 把 jolt 输出里的 build URL 报给用户
3. 不需要用户点头确认（已是默认工作流）
4. 用户在别的分支或临时改也可以传分支参数

**⚠️ 已有构建在跑时触发会失败(2026-06-17 世界杯实证)**：Jenkins 同时只跑一个 X3导配置 build。若上一次提交触发的 build 还在跑，`jolt_verify.py` 再触发会报 **`触发失败: 任务不存在: X3导配置`**（不只是"任务正在执行"那句）并退回显示 `lastBuild #N building=True`——这**不是真失败**，是被在跑的 build 占用。处理：**别反复硬触发**(撞同一报错)，等当前 build 跑完再触发一次即可（新触发会拉最新 HEAD，一次覆盖期间所有提交）。
- 可复用脚本 `C:\Users\linkang\monitor_then_jolt.py`：匿名查 `http://172.20.110.29:8080/job/X3%E5%AF%BC%E9%85%8D%E7%BD%AE/lastBuild/api/json`(get_json无需鉴权)轮询当前 build 到 building=False→报结果→自动重触发 jolt_verify 验证 HEAD。盯构建/排队用它,别现写。
- **build↔分支对账（2026-07-03 实证，多分支连推必用）**：连推 dev+qa 两分支后 jolt 都报"任务不存在"，别慌——push webhook 已各自排队。查 `{JOB}/<N>/api/json?tree=number,result,building,actions[parameters[name,value]]`，`actions.parameters` 里的 `branch` 值能把每个 build 对到分支（如 #1544=dev SUCCESS / #1545=qa），比只看 lastBuild 准。

## ★导表 FAILURE：`push rejected(fetch first)` → 自动 `rebase origin/dev` 冲突 → exit128（2026-07-01 实证）
**症状**：Jenkins 导表日志末尾一串 `CONFLICT (content): ...ProtoGen/i18n/{zh,en,jp...}.bytes` + `Item.bytes` + `ABTestSplit.*.meta(add/add)`，收尾 `Encountered N files that should have been pointers, but weren't`，最后 `git rebase origin/dev returned exit 128` → FAILURE。
**根因 = 并发撞车，不是配置写错**：`checktsv.py` 的 `git_auto_commit → push_with_rebase_retry` 想把生成物 push 到 dev，但**导表期间别人先合了分支进 dev**（如本次 `dev_X3_1393_ABConfig`＝AB框架+黑金契约皮肤+首充三选一礼包）。push 被拒→脚本自动 `rebase origin/dev`→撞在**两边都重新生成的二进制 proto 产物**（i18n 逐语言 .bytes + Item.bytes）上。Git 合不了二进制 + 这些 .bytes 本该是 LFS 指针却被当真实内容提交 → rebase-retry 自动解不了 → 炸。
**判据**：冲突文件全是 `ProtoGen/*.bytes`（导表自动产物）而非手写 tsv/xlsx → 撞车，不是你的错。冲突在 tsv/schema → 才是真配置问题。
**处理**：`origin/dev` 已在日志里 fetch 到最新 → **直接重触发一次导表**（`jolt_verify.py <分支>`），无并发即顺过。**重触发仍撞同样二进制冲突** = 那波产物是真差异，须人工 rebase，机器人解不了别硬重试。
**预防**：并发多 agent 改 X3 配置时错开 push、或走 worktree 隔离（见 [[workflow_x3_multiagent_worktree]]），避免同时重生成 i18n/Item proto。

## ★★导表后"什么生效、在哪生效"——热更边界(2026-06-17 世界杯实证,改配置前必判)
**X3 热更只热服务端,不热客户端**。导表产出的配置分两份:客户端那份(`client\Assets\Res\Config\ProtoGen\{表}.bytes` + i18n逐语言 `cn/en/...bytes`语言包)是**客户端打包进app的资源**——每张表 `CfgProtos` 里写死 `AssetPath="Assets/Res/Config/ProtoGen/X.bytes"`,客户端从自己bundle读、**不是服务器运行时下发**;i18n 走 `LocalizationMgr` 客户端加载。
- **所以服务端热更改不动客户端显示**:i18n文案、UI显示字段(DK图标/队标/面板)、客户端算的展示(如开箱概率公示WeighStr)、客户端弹窗逻辑(cfg.DailyPopup)——这些**改了+导表+热服务端=玩家端不变**,要客户端重打包或客户端资源热更才生效。
- **服务端热更只覆盖服务端权威逻辑**:活动上线时间/调度、礼包购买&限购、发奖/积分(ActvScore/BP结算)、累充白名单等——这些服务端读,改server config热更即生效。
- **判据**:问"这字段谁读"——客户端UI/显示读→客户端侧(热更够不到);服务端逻辑读→服务端侧(可热更)。同一张表里字段可能分属两边(如Pack:价格/限购=服务端权威, DK图标/Name=客户端显示)。
- **设计启示**:要让某个"会变的数据"能靠热服务端运营,就别让客户端直接读客户端配置,改成**客户端读服务端下发的值**(服务端从它自己可热更的配置读+下发)。世界杯竞猜换对阵就靠这个思路落地,见 [[project_x3_worldcup_activity]]。
