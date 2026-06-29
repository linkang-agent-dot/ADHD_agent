---
name: x3-tsv-export-migration
description: X3 导表演进——2026-05-29迁tsv缓存→2026-06-04 jenkins-xlsx-tsv-gate→🔴2026-06-22终态:xlsx工作流废弃,data/*.xlsx全删,tsv唯一权威源,hook软化,本地别跑ExportTable(orphan abort)改用pre_push_check。改X3配置/导表/合并dev前必读顶部
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6d162bb7-4b67-48ce-a1e5-225a2fab7f22
---

## 🔴 2026-06-22 终态：xlsx 工作流废弃，tsv 唯一权威源（推翻下方所有 gate 章节）

commit `1cdf4c8`（changxiaoyun, dev）"refactor(workflow): xlsx 工作流单向化，tsv 是唯一权威源头"。**dev 已删除全部 `data/*.xlsx`（440个）**，仓库进入 tsv-only。合并 dev 后本地仓库也变 tsv-only。核心规则（2026-06-23 世界杯合并实测）：
- **改配置只改 tsv，根本不存在 xlsx 了**。别再 `sync_xlsx_tsv --from-tsv`（无 xlsx 可同步）。
- **pre-commit / pre-push 由硬阻断改为软告警（永远 exit 0）**：xlsx 漂移只钉钉提醒不阻塞；commit/push 不会被 gate 拦。
- **⚠️ 本地别再跑 `Tools/table_exporter/ExportTable.py`**：它的 `verify_xlsx_tsv_before_export`（line 86）调 `sync_xlsx_tsv --check`，xlsx 全删→`orphan=440`→非零→`RuntimeError: XLSX/TSV are not synchronized; abort export`。dev 没改这个旧 verify，tsv-only 流程不走它。
- **新校验入口 = `python scripts/pre_push_check.py`**（tsv 数据源：列结构 + RewardID 连续性 + 冲突标记），退出0=过。导表正确性最终靠 jolt/CI（读 tsv）。
- **xlsx3way merge driver 已下线**；`install_hooks.py` 会自动清理残留 `merge.xlsx3way` section。**tsv3way driver 保留**（`tsv_merge_pro.py`，cell级3路合并，合并 dev 不再打散行序——2026-06-23 实测 Reward 273断点合并后仍0断点）。
- 合并 dev 时 xlsx 出现 `CONFLICT (modify/delete)`（dev删、本地之前还在改）→ 一律 `git rm` 接受删除。
- 合并/换机器第一件事：`python scripts/install_hooks.py` 注册 tsv3way driver（`git config --get merge.tsv3way.driver` 为空=没装，没装会退化 line-merge 打散 RewardID，见 [[workflow_x3_merge_conflict_audit]]）。

### 🟢 2026-06-23 cxy 正式操作说明书（合 dev 到开发分支照此做）
合 dev 时 xlsx 全删已是定稿流程，cxy 给的标准动作：
- **A. 合并报 xlsx 冲突 `CONFLICT (modify/delete): data/X.xlsx` → 全部选删**：`git status` 看哪些 xlsx 冲突 → `git rm` 把它们都删掉 → `git commit` 完成合并。
- **B. 合完 data/ 里 xlsx 都没了 = 正常，不用慌**。
- **C. 想用 Excel 看表但文件找不到 → 本地重生成一份（只自己看、不上传）**：`python scripts/sync_xlsx_tsv.py --from-tsv --all`。（⚠️澄清上面 line13「别再 --from-tsv」：那是指别拿它做"同步进 git"，但**本地重生成 xlsx 给自己看 / 给本地 ExportTable 用是正当用途**。）
- **D. 之前卡在导表的分支（如 dev_X3NEW-1287_refund / 我的 feature/x3-deepsea-art jolt #1142）→ 合完 dev 再跑一次导表就好**（jolt CI 已适配·会自重建 xlsx）。
- **以后改表：✅ 只改 tsv · ❌ 不改 xlsx**（改 xlsx 不生效也不进版本）。
- **🔧 实测纠正 line15「本地别跑 ExportTable」**：先 `sync_xlsx_tsv --from-tsv --all` 把 xlsx 重建到工作树后，`Tools/table_exporter/ExportTable.py` **能正常跑过**（verify_xlsx_tsv 比的是工作树 xlsx↔tsv，重建后一致 → mismatch=0 → protoc/MD5 全绿）。2026-06-23 深海纪念卡斗士属性+许愿池改动即用此本地导表验证通过。所以本地导表验证流程 = **`--from-tsv --all` 重建 xlsx → ExportTable.py**（不是不能跑，是要先重建 xlsx）。
- **⚠️ sync 增量 patch 对多行 cell 表（ActvOnline/MemorialCard 等 col 含长文本）不生效**：`--auto`/`--from-tsv --files` 走 cell patch 遇多行 cell 行坐标错位 → 改的 cell 没写进 xlsx → --check mismatch=1。解 = 删该 xlsx + `--from-tsv --all` 整表重建（--files 对删掉的文件不重建，tsv_to_xlsx patch 需 base 存在）。
- **⚠️⚠️ 两个 `--from-tsv --all` 并发 → openpyxl MemoryError + 损坏 xlsx（2026-06-23 合 dev 后踩）**：合 dev 时 **post-merge hook 会自动后台 `--from-tsv` 重建 xlsx 视图**（`[post-merge] xlsx 视图缺失，后台从 tsv 重建中`），此时**别再手动跑 `--from-tsv --all`**——两个 openpyxl 同时建 440 个 xlsx 撑爆内存 → `MemoryError`，中断时留下写一半的损坏 xlsx（如 TaskType.xlsx 2KB）→ 之后 `--check`/`ExportTable` 读到它报 `KeyError: no item named '[Content_Types].xml'`。**修法**：①找损坏 xlsx（`zipfile.ZipFile` 打不开或缺 `[Content_Types].xml` 的）删掉 ②确认无残留 sync 进程（`ps|grep sync_xlsx`）③**单进程**重跑 `--from-tsv --all`。**合 dev 后想本地导表：先等 post-merge hook 自己重建完（监控 data/xlsx 数到位），别并发抢。**
- **★合 dev 后本地导表非必需的判据**：若 `git log origin/dev..HEAD`（dev 带来的提交）全是工具脚本/hook/无关代码、**没碰你改的配置表 tsv**，则合 dev 前的本地导表验证仍有效，合 dev 后配置正确性不变（dev 没动你的表）。本地 xlsx 重建只是「看表」用，不阻塞 push/jolt（jolt 自重建 xlsx 导表）。

---

## ⚠️ 2026-06-04 重大变化：jenkins-xlsx-tsv-gate（推翻下方"xlsx下周删/只改tsv"）

xlsx **没删**，反而新增了 Jenkins gate（导表 job `X3导配置` 内置 stage），**强制 xlsx 与 tsv 保持一致**。提交者署名 `jenkins-xlsx-tsv-gate`，commit msg `Keep XLSX and TSV synchronized for dev`。本次会话（夏日装饰礼包 210917/918/919 补钻石/VIP）实测观察到的规则：

| 改动方式 | gate 行为 |
|----------|-----------|
| **只改一边**（单边漂移，如只改 tsv） | gate `auto-safe decision direction=tsv->xlsx`，自动把改动同步到另一边、生成同步提交；**但本次 build `gate_rc=24` 标 FAILURE**，需基于 gate 同步提交再导一次才 SUCCESS（两步） |
| **两边都改且不一致**（divergent dual-sided） | gate **拒绝**：`Rejected: Auto-merging divergent dual-sided edits \| direction is ambiguous` |
| **两边一致** | 通过（无漂移，`gate_rc=0`） |

`gate_rc` 速查：`0`=一致通过；`24`=单边漂移已 auto-fix 同步、需基于同步提交重导；`21`=**手动 jolt 触发时 before==after 没 diff、退化成纯一致性检查发现 `mismatch=1`**（xlsx≠tsv 但 gate 拿不到方向 → `FAIL Safe formatted-diff sync failed`）。rc=21 的解法：本地跑 `python scripts/sync_xlsx_tsv.py --from-tsv --files data/<表>.xlsx` 把 tsv 同步进 xlsx，或等 gate 处理真实 push diff 时自动同步（会生成 `Keep XLSX and TSV synchronized` 提交，pull 下来即一致）。

gate 日志关键行：`[sync_xlsx_tsv] auto-safe decision group=data/Reward.xlsx direction=tsv->xlsx reason=one-sided ... refs <old>-><new>` + 末尾 `gate_rc=24` / `exit 24` → `marked build as failure`。校验 `mismatch=0 crlf=0` 表示数据已同步一致。提交信息明写 **`Directive: Do not bypass the Jenkins XLSX/TSV gate for config branches`**。

**实操结论（覆盖下方旧指引）**：
- 想一次过 → **xlsx 和 tsv 两边同时改成完全一致**（同一提交），gate 看一致直接放行。
- 嫌改 xlsx 麻烦 → **只改 tsv**，接受 gate 两步：第一次导表 rc=24 失败+自动同步 xlsx 生成提交 → `git pull` 后基于该同步提交再触发导表才 SUCCESS。
- 副作用：gate 会产生大量自动提交 + 偶发 `Revert "...rebase 残留"`，dev 顶端会很乱；push 前先 `git pull --rebase`。
- ⚠️ 旧 `jolt_verify.py` **不认识 gate 两步**，只会报第一次的 FAILURE(rc=24)——需手动判断是不是 gate 同步导致的"假失败"，再追同步后的那次 build（待把 gate 逻辑并入脚本）。
- ⚠️**多页签 xlsx 必须把全部子页签 tsv 一起喂 sync(2026-06-15 实测)**：如 `ActvCrafting.xlsx` 含 3 页签(ActvCrafting/Reward/OtherReward)。`sync_xlsx_tsv.py --from-tsv` 只传其中 2 个子页签 → 重存 xlsx 时**没传的那个页签被清空** → 本地 pre-commit gate 报 `Both XLSX and TSV changed... formatted diffs differ`(divergent)/`mismatch=1` 拒提交。修法=该 xlsx 的**所有子页签 tsv 一次性传齐**(没改的也带上)，sync 输出 `mismatch=0` 才能过。
- ⚠️**改 gdconfig 前先关 WPS/Excel(2026-06-15 踩坑)**：`data\*.xlsx` 被 WPS/Excel 打开时，git stash/checkout 对该 xlsx 报 `Permission denied: unable to write file ... mode 100644` → **stash 半途失败、index 与工作区错乱**(status 出 MM/MD 混合态)。stash list 里残留的 `WPS-dirty-...` 条目=历史同款。处理：先关 WPS→`git reset -q HEAD -- <files>` 取消半暂存回到干净态(stash 仍在不丢)→重做。**护别人在途 WIP 用 stash 前务必先确认没 WPS 开 data 表**。
  - ⚠️**变体(2026-06-25 切qa踩):WPS 锁住某 tsv 时 `git checkout/merge 切分支`会"切一半"**——git 对被锁文件 `unable to unlink old '...tsv': Invalid argument` 然后 `Aborting`，但**已切的文件(如 xlsx 切到新分支版)不回滚**，留下 xlsx=新分支/tsv=旧分支的**混合工作树** → pre-push gate `sync_xlsx_tsv --check` 报 `mismatch=1`(expected_rows来自xlsx≠actual_rows来自tsv)，极易误判成"配置表本身坏了/origin有问题"。**真因是本地工作树污染，非分支内容问题**。判别：`git show origin/<branch>:tsv/<表>.tsv|wc -l` vs 工作树 `wc -l`，不等=切一半。修法：关占用进程(WPS `et.exe`/Excel)→`git reset --hard origin/<branch>` 干净重切。**gate 检查的是工作树而非你 push 的 commit**，所以脏工作树会拦住内容完全正确的提交。绕开脏工作树推送的 plumbing 法(不碰工作树)：`GIT_INDEX_FILE=<tmp> git read-tree origin/<b>` + `update-index --cacheinfo` 换 blob + `write-tree` + `commit-tree -p origin/<b>` + `push origin <sha>:<b>`——但这只绕 checkout 锁，绕不过 gate(gate 仍读工作树)，故根治还是关进程+reset。
- ⚠️**未提交改动会被别人 reset 冲掉**：dev_festival 多人并行，有人 `git reset --hard origin/dev_festival` 把你**未 commit** 的工作区改动清掉。教训=阶段改动尽快本地 commit(commit 即安全,reset 只冲未提交的)。

**★push 前先跑本地导表自测（2026-06-16 实测最省事）**：改完 tsv 别急着 push 等 Jenkins——先本地跑导表，能在**不依赖 Jenkins、不撞并发 push、不烧构建**的前提下当场抓出 `ID不连续`/`depend_keys not existed` 这类转换错。命令：`cd Tools/table_exporter && python ExportTable.py`（main 里硬编码相对路径 `../../temp_dev` 输出 + `../../tsv` 输入，**必须 cd 到该目录跑**；会先 `sync_xlsx_tsv.py` 再转换，跟 Jenkins 同一套 def 检查）。报错看 `[Table] ERROR`/`Traceback`。Jenkins 导表是同样的 ExportTable.py，本地过了远端基本就过。

**⚠️ net6.0 运行时依赖（2026-06-18 实测）**：纯 `python ExportTable.py`（数据校验/转换）**不需要 .NET**。但**连带生成客户端 C# proto 代码**那步——`python GenCSharp.py`（= `export_table_and_cp_to_client.bat`）——会调 `Tools/table_exporter/protogen-csharp/win/TableProtoGen.exe`，其 `runtimeconfig.json` 写死 **`tfm=net6.0` / `Microsoft.NETCore.App 6.0.0`**。机器只有 .NET 8 时这步报「找不到 6.0 运行时」。修法：`winget install --id Microsoft.DotNet.SDK.6`（含 6.0.x 运行时；只需运行时也可单装 `Microsoft.DotNet.Runtime.6`）。`dotnet --list-runtimes` 出现 `Microsoft.NETCore.App 6.0.x` 即可。另：`GenCSharp.py` 还要求 `table_exporter/local.json`（从 `local.json.temp` 复制，把 `client_path` 改成本机客户端仓路径）。

**★全本地链路：本地导表 → 导入本地服（不走 jolt/Jenkins，2026-06-18 实测打通）**。`ExportTable.py` 输出到 `gdconfig/temp_dev/ProtoGen`，本地服**不读它**（本地服读 `client/Assets/Res/Config/ProtoGen`，由 `server/Resource/.../ProtoGen` 软链指向）。手动导入三步：
1. `cd C:/x3/gdconfig/Tools/table_exporter && python ExportTable.py`（产出 `temp_dev/ProtoGen/*.bytes`，本次 406 个）。
2. `cp -r C:/x3/gdconfig/temp_dev/ProtoGen/* C:/x3-project/client/Assets/Res/Config/ProtoGen/`（覆盖 .bytes + AllTableDataMd5.txt + i18n/，保留 .meta；ProtoGen 本是 git-clean，要还原 `git checkout`；只碰 ProtoGen 不动别人 WIP）。
3. 热更运行中的服（不掉玩家、不重启）：`python ~/x3_gm.py "!gm ReloadGameServer"`（server-scope 无 @uid，port=23000+nid，3080→26080）。验证日志 `ReloadAllLoadedCfgByFilenames: <变化的表>` + `ReloadTable finished, N tables reloaded` + `Reload Finished` + `[Notify]reload[N] success`，**无 `InvalidProtocolBufferException`** 即成功（schema 兼容，data-only 不用重编）。末尾 `** Reload Finished` 标 ERROR 但写 success 是日志等级怪癖非真错。仅当出现 `InvalidProtocolBufferException`（schema 变了）才需停服重编 Hotfix 再起（见 [[workflow_x3_local_server_gm_telnet]]）。

**⚠️ dev_festival 导表当前会卡 ActvType=64 世界杯竞猜（2026-06-18 实测）**：76 个竞猜活动故意 `ActvOnline.TimeCycle=0`（走 iGame/外部控时，commit `4291166`），但 `PostProcessData.py:1765` 的 TimeCycle=0 硬校验的豁免名单 `SKIP_TIMECYCLE_CHECK_ACTIVITY_TYPE`（line 1644）**没含 64** → 本地导表和 Jenkins 都会 `raise ActvOnline配置错误：活动ID:102911 时间控制器ID:0 不能是0`。commit 作者「导表脚本无需改」只验了 FK/depend，漏了这个 PostProcess 校验。绕法 = 给该 set 加 `64`（本地为跑通临时加，**未提交**；这其实是 dev_festival 真实缺口，应正式补进导表工具）。2026-06-16 世界杯开箱阶梯换皮：本地导表先抓出并发 agent 的 59812 `depend_keys:{3101} not existed`（ItemType 误填序号 1/2/3，加速/资源袋应都=1），省了一轮 Jenkins。

**导表 FAILURE 归因（别被 build 红叉误导成"我改错了"）**：导表 job 串了多个独立检查，FAILURE 要看 console 末尾真正报错分类——
- `data_name:X, depend_keys:{id} not existed` → 某行引用的 id（嵌套子包/外键）在被依赖表里不存在；常见坑=**Reward 表 ItemType(col2) 填错**：1=道具(ItemID=Item)/2=蓝图/3=嵌套子包(ItemID=另一个RewardID)。把道具误填 type3 → 导表去找同名 RewardID → 报 not existed。修=确认是道具就改回 ItemType=1。
- `gate_rc=21/24` → xlsx/tsv 一致性问题（见上）
- `rewardID:xxx ID不连续, minID/maxID` → Reward 表同 RewardID 内行 ID 断号（见 [[reference_x3_reward_table_rules]]）
- **def 脚本浮点塞 Int 域崩**（2026-06-25 深海大富翁岛屿换皮 EventGroupID=206 实测）→ `actvvoyageevent_def.py` 把概率百分比 `(weight-now)*10000/totle` 算成 float 后塞进 `WeightPercent` 的 `Int()` 域；当一组权重和**不能整除 10000** 时结果是 425.53 这种非整数 → 崩。一年没暴露是因以前所有组权重和都恰好整除 10000(float `2000.0` 是整值能进 Int)。**已根治**：line42 改 `/`→`//`(整数除)，差额由已有 `if all>0` 兜底补到最后一项；全表验证只有不整除的组被改变结果、老数据零变化、不动策划数据/proto。**通用规律**：任何 def 用 `/` 算后塞 Int 域、且分母来自策划可填的权重/总和的，都有此雷——策划填任意权重和都该安全，靠 def `//`+余补兜底，不该要求策划凑整除。
- `Pack.xlsx column order changed; hot update may not support it; programmer confirmation is required` → **另一个独立 push 钩子**（`pre_push_check.py`/`excel_diff`）检测到列顺序/类型漂移（如 `#礼包表备份` sheet '10011'字符串→数字），常由**别人合并/openpyxl 重存**引入，**与你的改动无关**，需程序员确认放行。2026-06-04 实测：我只改 Reward，gate_rc=0/mismatch=0 全过，但龚亮海妖3合 dev 带进 Pack.xlsx 列漂移 → 整个 dev 导表 FAILURE。先 `git log -- data/<报错表>.xlsx` 看是不是自己改的，不是就别背锅、找对应改动人。
- `! [rejected] HEAD -> dev (fetch first)` + `failed to push some refs to 'git@git.tap4fun.com:x3/x3-project.git'` → **导表 job 末尾把生成的配置推回 x3-project(client_master)仓时撞了并发 push**（别人同时也在 push x3-project/dev）。**表转换/depend_checks 全过了，纯下游 push race，跟你的数据无关**。解法：直接**重新触发导表**（job 会重新 fetch 再 push）；可能 build 已在队列中（`触发失败:任务已在队列`），轮询那个 build 号即可。2026-06-05 实测：#612 因此 FAILURE，重触发 #613 SUCCESS。
- **本地 pre-commit 钩子已自动同步**：只改 tsv 时，gdconfig 的 `git commit` 本地 pre-commit hook (`sync_xlsx_tsv`) 会当场 `direction=tsv->xlsx` 把改动同步进 data/<表>.xlsx 并**把重生成的 xlsx 一起 add 进本次 commit**（输出末尾 `mismatch=0 crlf=0`）→ 提交即 xlsx/tsv 一致，导表一步过，**不再是旧版的 rc=24 两步**。副作用：commit 会顺带带进 xlsx 里别人之前只改 tsv 攒下的历史漂移（一次性刷掉，正常）。

## ★xlsx 需要插行/改值时的安全编辑法（2026-06-12 HeroSkin 104001 实测）

**先说结论：xlsx 千万别用 openpyxl 写，也别跑 `sync_xlsx_tsv.py --from-tsv`**——两者都用 openpyxl 重存整个工作簿，会**丢掉全簿所有公式单元格的缓存值**（文件瘦 40KB+ 即中招）。更毒的连锁：缓存空了之后 commit 时 pre-commit gate 自动 `xlsx->tsv` 同步，会把空值灌进 tsv 的公式列——实测把 `Hero__HeroSkill.tsv` 的 **Id 列整列清空**（6948行），还好没 push，`git reset --hard` 救回。校验器是**按字符串比对**不是数值比对（`95.3020134228188` ≠ `95.30201342281879` 也算 mismatch）。

**安全姿势（插行，一次过 gate）**：
1. **Excel/WPS COM 编辑**（保公式缓存）：`win32com Dispatch('Excel.Application')`，`xl.Calculation=-4135`(manual)+`CalculateBeforeSave=False`，`ws.Rows(n).Insert()` 填值，保存。表内插行会自动扩 table ref + 自动填计算列公式。
2. COM 保存仍会"规范化"少量浮点缓存串（17位→15位 shortest repr，本次 15 个格子）→ **zip 手术**改回：遍历 `xl/worksheets/sheetN.xml` 的 `<c r="X"><v>num</v>`，与同坐标 tsv 串比对，**数值相等但字符串不同的，把 xlsx 串替换成 tsv 串**。已固化成工具 `~/.claude/skills/x3-config-export/scripts/xlsx_cache_repair.py`（用法见脚本 docstring）。
3. `python scripts/sync_xlsx_tsv.py --check --files data/<表>.xlsx` 到 **mismatch=0**，再把 tsv 改成与 xlsx 完全一致 → commit。gate 输出 `both sides changed, formatted diffs are identical; no sync needed` = 理想通过形态。

**只改一个字符串单元格**（如换 DK 名）不用 COM：直接 zip 手术 `xl/sharedStrings.xml` 字符串替换 + tsv 同串替换，零重算噪声，秒过。

> 下面 2026-05-29 的"只改 tsv 不碰 xlsx / xlsx 下周删"是 gate 出现**之前**的旧流程，保留作沿革；以本章节为准。

---

## 核心变化（2026-05-29，廖强/zhangli/常潇允 推动）

X3 导表（Jenkins **X3导配置**）已从「读 xlsx 现导」迁移为「**读提交的 tsv 缓存**」。三个主分支已同步。

**所有配置改动以 tsv 为准。** xlsx 下周删除，目前仅作备份过渡（`改表和实际生效都走 tsv`）。

| 项 | 说明 | 来源 commit |
|----|------|------|
| 导表改读 tsv 缓存 | 不再从 xlsx 现导 | `ec5c043` Route config export through TSV cache |
| tsv 生成手动化 | pre-push hook 明写 "TSV cache generation is manual-only" | `7538887` |
| 脚本递归镜像子目录 | `data/i18n/Text.xlsx → tsv/i18n/Text__Text.tsv` | `240e944` Cover nested i18n workbooks |
| push 自动跑一次 xlsx→tsv | 常潇允补充，**但后续会干掉，别依赖** | — |

## 主流程：直接改 tsv（非翻译配置）

实践已确认（zhangli 屏蔽尼罗/夏日礼包、林康改数值都如此）：**非翻译的配置改动直接改 `tsv/` 下文件，不碰 xlsx**。一条龙 skill + 工具：

- **Skill `x3-config-export`**（`C:\Users\linkang\.claude\skills\x3-config-export\`）：定位→安全改tsv→提交→导表→验证全流程，含「屏蔽礼包」等列位置速查表。触发词「改X3配置/屏蔽礼包/改timecycle/改tsv/导X3配置」。
- `scripts/tsv_edit.py`：安全改 tsv（`show`定位列 / `set`断言旧值改单元格 / `remove`从管道列表删ID；保LF、dry-run）。替代每次临时写脚本。
- `scripts/jolt_verify.py`：jolt 触发 + 自动轮询构建 + 报 SUCCESS/FAILURE+分支。替代裸 `jolt_export.py`。

⚠️ **对已 tsv-直接改过的表，绝不能再 `xlsx_to_tsv.py` 重生成**——xlsx 是旧的，重生成会覆盖回去（尼罗/夏日屏蔽只在 tsv，一重生成就还原）。

## 唯一仍碰 xlsx 的窄例外：i18n 翻译扫描

只有翻译走 `x3-translation-automatic` 的扫描工具链（CompositeI18n）时会读/写 `data/i18n/Text.xlsx`。**即便这样，导入仍只读 `tsv/i18n/Text__Text.tsv`**——改完 Text.xlsx 必须 `python scripts/xlsx_to_tsv.py --files data/i18n/Text.xlsx` 重生成那一个 tsv 并提交。或干脆直接改 tsv 的语言列（状态列标 `AI`）。**除此之外任何配置都不碰 xlsx。**

- tsv 命名：`tsv/{data下相对目录}/{xlsx文件名}__{Sheet名}.tsv`（顶层 data/ 无子目录前缀）。
- tsv **是入库的**（不是 .gitignore），导表直接吃它。
- ⚠️ 重生成只针对「确实从 xlsx 改的那个文件」；**绝不全量 `--all` 或对已 tsv-直接改过的表重生成**，否则覆盖回旧值。

## 血泪教训（2026-05-29 X3NEW-734 / 礼包timecycle）

**只改 xlsx 不重生成 tsv = 修复完全无效**，因为导表读旧 tsv：
- 礼包 timecycle 修复改了 `Pack.xlsx`（commit 84f59ff），但 tsv 还是旧 timecycle 1096 → 导出仍旧错。
- ActvScoreTask 208/209/213 翻译写进 `Text.xlsx`（commit 5e738e7），但 `tsv/i18n/Text__Text.tsv` 仍是 `新增`+空翻译 → 俄服仍显中文。
- 重生成 tsv（zhangli 96ed6d0 / 我本地同结果）后两个修复才真正落地。

会话开头的 Jenkins 报错 `tsv/i18n/Text__Text.tsv file not exist，无法正常多语言转换` 根因也在此：i18n 子目录 tsv 没被旧脚本覆盖生成（240e944 修脚本递归后解决）。

## 隐性坑

- openpyxl/merge 驱动碰过 xlsx 后，`data/*.xlsx` 可能出现 +几字节的假阳性改动（zip 元数据，`0 insertions/0 deletions`）。提交前 `git hash-object` 对比 HEAD，确认是假阳性就 `git checkout HEAD -- <xlsx>` 还原，再从干净 xlsx 重生成 tsv。
- 多人会并行做同一份 tsv 重生成 → push 可能被拒（rejected, fetch first）。先 fetch 比对 blob 哈希，若与远端逐字节相同直接 `git reset --hard origin/<branch>` 丢掉重复提交，无内容损失。

## ⚠️ data/*.xlsx 损坏(invalid XML)挡提交时,从 tsv 重建(2026-06-17 ItemObtain.xlsx 实证)
某个 `data/<表>.xlsx` 被别的进程写坏(openpyxl `normal load`/sync 报 `could not read worksheets ... invalid XML`,但 `read_only=True` 反而能读)→ pre-commit 钩子的 sync 读不了它、**卡住所有人对该表的提交**(导入只认tsv不受影响,纯卡同步闸)。这通常是别人的损坏、HEAD 里就坏(git status 不显示改动)。
- **修法=从 tsv 重建干净 xlsx**：`openpyxl.Workbook()` 新建→**按原页签顺序**(先 read_only 读旧 xlsx 拿 sheetnames)逐页签 `csv.reader` 读对应 tsv→`ws.append([c or None for c in row])`→save。多页签表(如 ItemObtain 4页签:ItemObtain/JumpType/#现阶段道具跳转/#废弃)要**全页签重建**。重建后 normal load 能读=XML 修复。
- 再 `sync_xlsx_tsv --check` 确认 mismatch=0(重建是按 tsv 来的,本就一致),提交即过。

## ⚠️ tsv 含「引号多行单元格」时禁用 split/join 脚本(2026-06-17 世界杯兑换商店血泪)
有些 tsv 单元格内含**换行**、按 CSV 规则用引号包起来跨**多个物理行**(如 ActvExchange Label=`"<size=40>50%</size>\n每日刷新"`,占2行)。**clone/改这类表时,建表脚本若用 `open().read().split('\n')` 读 + `'\t'.join(row)` 写=必坏**：读时多行单元格被 split 成两行、过滤 `f[1]==组号` 只命中前半行→克隆出的行**被截断、引号不闭合**;写回后整张 tsv 结构坏,`sync_xlsx_tsv` 校验 xlsx↔tsv **永远 mismatch=1 同步不掉**(反复 --from-tsv 也没用,因为 tsv 本身坏了)。
- **症状**:某表持续 `mismatch=1` 怎么同步都不消;csv.reader 解析该组行数比预期少(被截断行 col1 错位不匹配);raw `grep ^新ID` 看到行尾是半截引号 `..."<size=40>50%</size>` 下一行直接是下一条记录(续行 `每日刷新"\t..` 丢了)。
- **根治**:①改含多行单元格的表**必须用 `csv.reader/csv.writer`(delimiter='\t')**,它正确处理引号多行,别用 split/join。②已被截断的:raw 文本里把丢失的续行补回(`...</size>\n` 后插 `每日刷新"\t<剩余列>\t\n`),让引号闭合,再 csv 验证行数/字段对，再 sync xlsx。③验证别只数行:用 csv.reader 数该组 SKU 数==源数 + 关键字段(币/道具)对。

## ⚠️⚠️ 批量删行(中间删行)同步 xlsx 的大坑(2026-06-17 世界杯竞猜池迁移,删146包血泪)
**sync_xlsx_tsv 工具只会 append/update、不能删 xlsx 行**(tsv_to_xlsx 有 _insert_row 无 _delete_row)。所以从 tsv **中间删了一批行**后,`--check` 死活 mismatch、`--auto`/`--from-tsv` 都修不好(xlsx 残留旧行/卡在旧行数)。必须**手动 openpyxl 重建那个 sheet**,且三个坑全踩中才过:
1. **多sheet xlsx 不能整本重建**(Pack.xlsx 有18个sheet!)→ 只能 `wb.remove(wb[sheet])` + `wb.create_sheet(sheet, 原idx)` 重建目标sheet,保留其他sheet。
2. **解析 tsv 必须用 `csv.reader(delimiter='\t')` 不能 `split('\n')`**——Pack 等表有 CSV 引号包裹的**多行单元格**(如表头注释含真换行),split('\n') 会把一行拆成多行→行数全错(实测 csv.reader=2301 而 split=2380)。
3. **写 xlsx 单元格全部当字符串、不要 cast int/float**——openpyxl 写 float `10.0` 存读回变 `10`(丢.0),与 tsv "10.0" 不一致→ gate `cell_mismatch`。直接 `cell=原字符串`(空→None),gate 只比 `csv_string(value)`==tsv,字符串必然 round-trip。(sync 工具用裸XML `<v>10.0</v>` 才能保,openpyxl 写值做不到)
- **openpyxl `delete_rows`+save 还有坑**:in-memory max_row 对了但存盘 XML 维度没收缩,`ws.iter_rows()`(gate按维度数)仍读到残留空行→remove+recreate sheet 才彻底干净。
- 验流程:重建后 `sync_xlsx_tsv.py --check` mismatch=0 → 本地 ExportTable.py 过 → commit(pre-commit gate再验) → push → jolt。范式脚本 `C:\Users\linkang\migrate_wc_packs.py`(删行/重指,注意它删tsv用split可行因只删整行不碰多行单元格续行)+ 重建逻辑见本条。

## ⚠️⚠️⚠️ 本地导表热更本地服失败=protobuf 版本踩坑（2026-06-22 血泪，jolt排队时的快路子被这个坑废掉）

**背景**：jolt 要排队，所以用「本地导表→拷 client→重编重启」热更本地服(不走 jolt)。但本机 `python`=Python 3.14 → 强制 protobuf **5.29.6**，而导表工具链 `Tools/table_exporter/requirements.txt` 钉死 **protobuf==3.20.3**。

**症状**：本地导出的 config 部署后，服务器启动崩 `Server Start Failed`，栈 `ServerMapUtils.GetServerMapLevel → CServerSegment.Instance.SortIDs[0]` **ArgumentOutOfRangeException**（SortIDs 空）。但 config 预载本身成功(`StartPreloadData ... cost` 无 InvalidProtocolBuffer)、Python 解码 .bytes 数据完全正常(13行+SortIDs全在)——**极具迷惑性**。

**根因**：`Tools/table_exporter/GenProto.py:243` 判 repeated 字段是否 packed 用 `getattr(field.file,"syntax","")=="proto3"`。**protobuf>=4 删了 `FileDescriptor.syntax` 属性** → 返回 `""` → 判成 **unpacked** → 导出的 .bytes 里 repeated int32(如 ServerSegment.SortIDs=field5) 用 unpacked 编码(每元素带tag)。**X3 的 C# 自定义读取器(TableProtoGen生成)只认 packed** → 读 unpacked repeated 得 0 个 → SortIDs 空 → 崩。robot(jolt) 在 Jenkins 用 protobuf 3.20.3 → `.syntax` 在 → packed → 正常。**同一份配置：本地导=1064字节(unpacked)、robot导=1021字节(packed)、数据完全相同**。

**诊断手法(下次直接抄)**：① 解码 `.bytes`：`import ServerSegment_pb2; c=CServerSegment(); c.ParseFromString(open(p,'rb').read())` 看 Configs/SortIDs——**数据正常≠能用**。② 数 field tag：packed=`(field<<3)|2`、unpacked varint=`(field<<3)|0`(如 field5: packed=0x2a、unpacked=0x28)；`d.count(b'\x2a')`==0 = 全 unpacked = 坏。③ 比本地 vs robot(client committed)的 .bytes 大小：本地大几十字节=unpacked。④ `python -c "import google.protobuf;print(google.protobuf.__version__)"` ≠ 3.20.3 即雷。

**修复(已落地 embedded `C:\x3-project\gdconfig\Tools\table_exporter\GenProto.py`)**：`.syntax` 取不到时对 proto3 packable repeated 默认 packed——
```python
syntax = getattr(field.file, "syntax", "")
if syntax: return syntax == "proto3"
return True  # protobuf>=4 移除 FileDescriptor.syntax；本工具链全 proto3，packable repeated 默认 packed
```
改完重导：ServerSegment.bytes 从 1064(unpacked)→1021(packed,与robot一致)、`0x2a` 出现=packed ✓，服务器 `PlayService started` 无崩。Python 3.14 装不了 protobuf 3.20.3(无wheel)，故只能改代码不能降版本。

**★此补丁故意【不提交进仓】(用户 2026-06-22 定)，落在本地自愈**：本地 helper `C:\Users\linkang\x3_ensure_genproto_packed.py`(幂等,按逻辑特征 `syntax = getattr(field.file,"syntax","")` 检测是否已打,没打则改;不依赖注释措辞)。它被一键脚本(见下)在每次导表前调用——**即使 git checkout/reset 把 GenProto.py 还原成原版,下次本地热更会自动补回**。所以不需要也不要 commit 这个补丁(它是本机 protobuf 版本的环境补丁,非业务改动,提交反而污染仓/影响 robot)。

## ⚠️ 一键脚本两个前置坑(2026-06-23 深海节 GM 部署实测,跑前必查)
`x3_local_redeploy.ps1` 写于 2026-06-22,跑前要先补两步,否则导出错配置或在 gate 中断:
1. **它从【内嵌】gdconfig(`C:\x3-project\gdconfig`)导出,不是标准仓`C:\x3\gdconfig`**——两个是**独立 clone,会分叉**(实测内嵌 dev_festival 停在旧 tip、且常被切到别的 feature 分支如 newbie-recharge,根本没你要的节日配置)。**跑前必须把内嵌 gdconfig 切到有目标配置的分支**:`cd C:\x3-project\gdconfig && git checkout -- Tools/table_exporter/GenProto.py && git fetch origin dev_festival && git checkout dev_festival && git reset --hard origin/dev_festival`,然后用 `python3 csv` 验证目标行在 tsv 里(如深海 BP=102244/累充=100598)再继续。不查直接跑=导出的还是旧/错配置,白忙。
2. **脚本不重建 xlsx → tsv-only 世界里 ExportTable 必在 gate abort**(orphan=440)。跑脚本**前**先 `cd C:\x3-project\gdconfig && python scripts/sync_xlsx_tsv.py --from-tsv --all`(440表,~1min,出 `mismatch=0 orphan=0`),让 verify_xlsx_tsv 能过。
- 判**该不该重导**:GM `GMPrintServerActivityByCfgId <id>` 报 `errCode=1017001 config not found`、但该 id **在 tsv 里有**(csv 验证)= .bytes 没导出该行(jolt CI 坏/久没导)→ 重导。报 `1017012 no server activity found`=配置在、只是没实例(可直接 GM 开,不用重导)。
- 跑完判完成:服务器进程 CreationDate 刷新到新时刻 + 日志末段 `PlayService started` 无异常 + 残留的 MSBuild dotnet 进程是 **node-reuse 守护**(start time 早于重启时刻=空闲不是在编,别误判"还在跑")。pwsh 输出常 buffer 到退出才落盘,output 文件空 ≠ 没干活,直接验进程/日志/GM探测更靠谱。

## ✅ 本地导表热更本地服 完整流程(不走jolt,2026-06-22 验证通)
**一键(首选)**：`pwsh C:\Users\linkang\x3_local_redeploy.ps1 -Sid 3080 -CenterId 61`(`run_in_background` 跑,含 dotnet build ~3min)。**⚠️ 跑前先做上面「两个前置坑」**。它串起：确保local.json → **调 x3_ensure_genproto_packed.py 自愈补丁** → ExportTable → GenCSharp → **★packed守卫(导后检测 ServerSegment 是否 packed,unpacked 就 abort 并提示 protobuf 版本根因)** → x3_redeploy.ps1 -ForceBuild。jolt 排队时就用它。
前提(脚本已自动处理)：server `CSSharedCommon`→client `CSShared/Common` 软链、config 软链→client ProtoGen，所以 GenCSharp 生成到 client = 服务器吃到；需 .NET6 运行时给 TableProtoGen.exe。
**手动等价步骤(排障时)**：① `python x3_ensure_genproto_packed.py`(确保补丁) ② `cd C:\x3-project\gdconfig\Tools\table_exporter && python ExportTable.py` ③ `python GenCSharp.py` ④ 验 packed：抽含 repeated 的表 .bytes 数 `b'\x2a'`(field5 packed tag) 应>0、size≈robot 版 ⑤ `pwsh x3_redeploy.ps1 -Sid 3080 -CenterId 61 -ForceBuild` ⑥ 验 26080/26081 在线 + game-3080.<date>.log 末段 `PlayService started` 无 `ArgumentOutOfRange`/`InvalidProtocolBuffer`
- 崩了的还原：`cd client && git checkout HEAD -- Assets/Res/Config/ProtoGen/ Assets/Scripts/CSShared/Common/Cfg/` + redeploy
- ⚠️别只 `ExportTable.py` 就手拷 .bytes 到 client(跳过 GenCSharp)：CfgProtos 不重生成→schema/packed 对不上必崩。([[workflow_x3_local_server_gm_telnet]] §65 旧记"本地导表≠更本地服"指的就是漏了 GenCSharp+重编这步)

## 关联
- [[reference_x3_gdconfig_repo]] [[workflow_x3_auto_jolt_export]] [[reference_x3_i18n_workflow]] [[project_x3_worldcup_activity]] [[workflow_x3_local_server_gm_telnet]]
