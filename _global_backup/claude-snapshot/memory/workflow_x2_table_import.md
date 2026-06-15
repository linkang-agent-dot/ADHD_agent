---
name: X2导表工作流
description: X2 配置表从 Google Sheets 下载到 x2gdconf 仓库的完整流程，含路由规则和 download skill 路径
type: reference
originSessionId: c62f4c2c-8b51-486f-b004-0ce34c2efe37
---
# X2 导表工作流

## 触发词
X2导表、X2下载表、X2刷表、X2拉取配置

## 执行协议
每次收到"X2导表"类请求，按以下顺序加载：
1. **读路由规则**：`C:\ADHD_agent\.cursor\rules\x2-gsheet.mdc`
2. **读 download skill**：`C:\ADHD_agent\.cursor\skills\x2-config-download\SKILL.md`
3. 按 skill 规则执行具体下载流程

## 关键路径
- 仓库：`D:\UGit\x2gdconf`
- 工具：`D:\UGit\x2gdconf\tools\fwcli.exe`
- GSheet ID：`1z2-AK4dFgdzd7U11uCgYzLpj3Qopkv9Rr-SbA7iLIMc`
- 主 Skill（仓库内）：`D:\UGit\x2gdconf\.cursor\skills\gsheet_sync\SKILL.md`
- Download Skill（ADHD维护）：`C:\ADHD_agent\.cursor\skills\x2-config-download\SKILL.md`
- 合并 Skill：`D:\UGit\x2gdconf\scripts\gsheet_skill_merge.md`
- 冲突 Skill：`D:\UGit\x2gdconf\scripts\gsheet_skill_conflict.md`

## 与 P2 导表的区别
| | P2 | X2 |
|---|---|---|
| 仓库 | `C:\gdconfig` | `D:\UGit\x2gdconf` |
| 工具 | `GSheetDownloader.exe` | `fwcli.exe` |
| 交互方式 | stdin 管道 | 命令行参数 |

## ⚠️ 每次 commit 前必 `git branch --show-current`——x2gdconf 分支会被中途切走（2026-06-10 装饰礼包 show_hud 修复误提交到 master_bugfix）
- x2gdconf 在 `dev_festival`(节日换皮) 与 `master_bugfix`(线上bug) 间**频繁切换**（dev 还会 `Merge master_bugfix into dev_festival`）。会话中途分支可能**被别的进程/用户切走**，不会通知。
- **信号**：跑 fwcli 前发现 `tmp_xlsx/`、`scripts/merge_rows.py` 等 **untracked 文件突然消失** = 极可能刚发生过 `git checkout`(切分支 wipe 了工作区)。一旦看到，**先 `git branch --show-current` 再干活**。
- 本次教训：整个装饰礼包都在 dev_festival，最后 show_hud 修复时分支已被切到 master_bugfix，没查就 commit→落错分支（`[master_bugfix xxx]` + push dev_festival 显示 "Everything up-to-date" 才发现）。**commit 后看输出的 `[分支名 hash]` 核对，push 后看是否真推上去**。
- 落错分支补救（commit 仅本地未推时）：`checkout 目标分支 → cherry-pick <hash> → push`；再 `checkout 错分支 → reset --hard HEAD~1` 撤掉本地误提交。

## ⚠️ 长期没全量同步的表(如3514)必须全表导、禁止行筛选（2026-06-10 X2-43107 踩坑）
- 行筛选上传 = 以本地 HEAD 为基线、只覆盖目标行。**若该表 HEAD 本身就残缺**（从没全量导过、比 GSheet 少一大截行），行筛选会**永久保留这个残缺**——每次只补目标行，缺的行一直缺。
- 实例：3514 metro_minigame_rock_drop 在 dev_festival 只有 1115 行，GSheet/全表是 1332 行，**缺 217 行**（非拓荒的 35142xxx/35143xxx 地下世界/原服等）。我连续几次行筛选上传都把表停在 1115，被用户指出"筛选上传一直有错"。后来别人在 master_bugfix 全表重导(596d15364)→1332 行才补齐（因从 GSheet 拉，自动含我改的 11116402）。
- **判据**：导表前先比 `git show <branch>:fo/config/<表>.tsv | wc -l` vs 全表下载行数。差很多 = 该表整体漏导 → **走全表导**（接受/审别人搭车改动），别行筛选。行筛选只适合"表已基本同步、只想精准改几行避免夹带"。
- 注意：残缺的是无关行，**目标行的值本身对**（11116402 在 dev/master 都正确）；功能不一定坏，但属部署隐患。

## fwcli `-f` 必须用表号前缀、不能用页名（2026-06-09 重导 3514 踩坑）
- `fwcli ... -f metro_minigame_rock_drop`（**页名**过滤）**静默匹配不到任何表**：输出只有 `Getting a list of all files finish`，tsv mtime 不变，看着像成功实则没下载。
- 必须用 **表号前缀** `-f 3514` 才真正下载（`download metro_minigame_rock_drop finish`）。导表后务必核对目标 tsv 的 mtime/行数确认真的下载了，别被"finish"假成功骗过。

## ⚠️ 部分表 googlexlsx 只产 xlsx、必须补转换，真源在 fo/json 不在 fo/config（2026-06-09 重导 2131 踩坑）
- **不是所有表 googlexlsx 都直接写 `fo/config/*.tsv`**。两种行为并存：
  - **直写型**（如 2112 activity_config）：日志 `download activity_config finish`，googlexlsx 一步就改了 `fo/config/<页签>.tsv`，diff 立刻可见。
  - **xlsx 型**（如 2131 ActivityBattlePassLevel）：日志 `download tmp_xlsx\X.xlsx tabname:... finish`，只产出 tmp_xlsx 里的 xlsx，**fo/config 那个 tsv 是不再更新的旧镜像（mtime 老旧）**。必须接着跑 `xlsxtojson` + `s2ctool`，真实落点是 **`fo/json/<CamelName>.tsv` + `fo/json/*.json` + `fo/s2c/*`**。
- **判据**：googlexlsx 后先 `git status`/`git diff --stat`。若 fo/config 无变动但 tmp_xlsx 多了 xlsx → 是 xlsx 型，**别以为"无改动"就收工**，补 `xlsxtojson -t tmp_xlsx -d fo/json -o fo/s2c` + `s2ctool --input fo/s2c --output fo/s2c`，再看 git status 找真实落点。
- 提交对象 = `fo/json/<CamelName>.tsv`+`.json` + `fo/s2c/<CamelName>.cfgData`+`.json`+`md5.json`（不是 fo/config）。
- check_tsv_format.py 直接对 `fo/json/<CamelName>.tsv` 跑即可（`--all-changed` 会自动捡到）。

## ⚠️ 配置在仓库 ≠ 配置上服（2026-06-09 合成小游戏 drop panic 复盘）
- 排查"线上/测试服报配置缺失"类 bug，确认 GSheet 真源 + 仓库分支 tsv 都已修复后，**若服务器仍报同样的错，根因极可能在部署侧**：配置 commit 进仓库不会自动上服，要跑导表构建(s2ctool 打包) + 热更，dev 服才加载新配置。
- 判据：重导比对仓库分支 = 无真实缺口 + 全量关卡→掉落引用 100% 命中 → 配置侧已尽，别再反复改配置/重导，**转去触发/确认构建+热更部署**（x2-kadmin）。
- 别被"报告时间"误导：报告 panic 日志的时间戳可能早于修复 commit 时间——那是修复前的旧日志，不代表修复无效。

## p2_title 前导空列错位坑（2026-06-08 合成小游戏等级表 2160）
- **带 `p2_title` 前导空列的表（如 2160 activity_metro_grade），fwcli 下载的 tsv 比仓库 canonical tsv 多一列**（下载 9 列 / 仓库 8 列），整列右移导致 ID 列错位。
- 直接套 `merge_rows.py` 会按错位的 ID 列匹配 → 报「ID not found」假阴性。
- 修法：merge 前先**剥掉下载 tsv 的前导 `p2_title` 空列、对齐仓库 8 列结构**，再追加/合并目标行。提交前 diff 确认列数与 HEAD 一致。

## merge_rows.py 的 EOL 坑（2026-06-08 挖矿榜奖励 X2-42998）
- **merge_rows.py 以 LF 写出，但部分 X2 config tsv 是 CRLF + 末行无换行符**（如 `activity_rank_rewards.tsv` 2118）。直接合并后 `git diff` 变成整文件全重写（假阳性，看着像要提交全表）。
- 修法：合并结果**转回 CRLF + 去掉脚本多加的末尾换行**以对齐 HEAD，diff 才收敛成真实的目标行数。走行筛选 merge 后 diff 若异常放大，先查 EOL 而不是怀疑数据。
- ✅ **EOL 别折腾——用普通 `git diff`，别加 `-c core.autocrlf=false`（2026-06-09 实测纠正）**：x2gdconf 仓 `core.autocrlf=true` + `.gitattributes` 无 tsv eol 规则，所以 merge_rows 写 LF **完全没问题**——git 会自动把工作区 LF/CRLF 归一化到 LF blob，`git diff`/`git add` 透明处理。**真正会"假爆全表"的是你自己加了 `-c core.autocrlf=false`**：它关掉转换，让 CRLF 工作区 vs LF blob 每行都判为差异（X2-43081 一度 10362 行假 diff、本次 5 表又踩，CR-insensitive `diff <(tr -d '\r')` 一比才发现内容只差目标行）。**结论：merge 后直接 `git diff --stat`(仓库默认) 验，干净就提交，不要 CRLF 转换、不要 `-c autocrlf=false`、不用数 CR。**
- ⚠️ **但上一条不普适：HEAD blob 本身是 CRLF 的表，merge_rows 写 LF 会真假爆（2026-06-12 2122 activity_rank_rule 踩坑）**。`iap_config`/`iap_template` 的 HEAD blob 是 LF → LF 输出干净；但 **`activity_rank_rule`(2122) 的 HEAD blob 是 CRLF**（`git show HEAD:<表> | file -` 显示 `CRLF line terminators`，且 EOF 无末尾换行）→ merge_rows 的 LF 输出让 `git diff --stat` 爆 1642 行(825/825)假 diff。
  - **判据**：merge 后 `--stat` 行数远超目标行 → 先 `git show HEAD:<表> | file -` 看 HEAD 是不是 CRLF；是则**把合并结果转回 CRLF + 去掉末尾换行**对齐 HEAD（python: `'\r\n'.join(去尾空行的lines)`, `newline=''` 写，不加末尾`\n`），`--stat` 即收敛成真实目标行。
  - 用 `diff <(git show HEAD:<表>|tr -d '\r') <(tr -d '\r' <工作区表)` 验真实内容差异——只应剩目标行 + 可能的"No newline at end of file"。
  - **下次导任何表先一句 `git show HEAD:<表>|file -` 看 EOL，CRLF 表 merge 后必转 CRLF**；不要无脑套"LF 没问题"那条。
- 同源坑见 [[X2 手改 i18n tsv 两个坑]]（i18n tsv 也是 CRLF）。

## ⚠️ 用户在 GSheet 删行/改结构 → 公式 id 列断成 #REF! → 整表导不出（2026-06-08 X2-42998）
- 现象：fwcli 报 `int error on row N col 4: A_INT_id ... invalid literal for int(): '#REF!'`，**整张表拒导**（行筛选也绕不过，它得先下载全表）。
- 根因：GSheet 配置表的 id 列常是**公式引用**（非字面数字）。用户删行/重排结构时，会把**别的 group** 的 id 公式打断成 `#REF!`（本次挖矿榜重排误伤了 group 168/169/170 周年庆BP/军备/战装榜共 21 行）。
- 处理：① 导前可先扫 id 列有无 `#REF!`（`gsheet_utils` 读 id 列）；② 有则**让用户/原编辑人修回真实数字 id**再导（改用户 GSheet 内容要先问，别擅自填）；③ 可从本地 HEAD 良好 tsv 反查那些未改 group 的真实 id 协助恢复。
- 教训：节日换皮"重排某活动排行榜"时，**删行是高风险动作**，易跨 group 连带断公式，导表前先验全表无 #REF!。

## ⚠️ 2118 等表「备份页签占最左」雷确证（2026-06-08 命中）
- 导表只读最左页签的雷**真实会触发**：2118 导表时 `activity_rank_rewards` 不在 index 0，被旧备份 `_bak_20260521_activity_rank_rewards` 占着最左 → 不置顶直接导会读到旧脏数据。
- 凡导 2118（及任何历史上建过 `_bak_*` 的表）前，**必先拉 `sheets[].title/index` 确认目标页签在最左**，不在就临时置顶、导完还原顺序。备份页签平时不删但要确保不在 index 0。

## 行筛选导表踩坑（2026-06-05 挖矿镐 title_icon）
- **fwcli googlexlsx 直接把全表 GSheet 写进 `fo/config/<页签>.tsv`**（`-d tmp_xlsx` 那个目录会是空的，别等 xlsx 产物）。全表会夹带别人在 GSheet 上的改动 → 必须 `merge_rows.py` 用 HEAD 基线收敛只留目标行。
- **PowerShell 沙箱会预拦 `Remove-Item tmp_xlsx\*`（误判保护路径）整条命令不执行** → 备份 `.bak` 可能没真建成。补救：`git show HEAD:fo/config/<页签>.tsv > <页签>.tsv.bak` 取干净基线；或建议带 `dangerouslyDisableSandbox`。
- **行筛选=整行替换，目标行的其它列改动会一起带进来**：merge_rows 把 GSheet 的整行覆盖 HEAD 行，所以目标行若在 GSheet 上还有别的列被人改过（本次 3 个合成行的 `A_INT_show_hud` 21121491→211200212），会**搭车进 commit**。提交前必须**逐字段 diff**（按 id 比 .bak vs 现值，列出每个变化的列名）确认每处改动都是预期的，再决定一起传还是回退非目标列。
- title_icon 落地链路全程：出图(x2-media)→真透明(remove_background)→录 DK(Display_Icon+IconBg 同 key 同 GUID)→Ctrl+Shift+E 导出 Path→写 2112 GSheet X 列(C_INT_title_icon)→行筛选导表→push。见 [[x2-dk-p2-dk-manager]]。
- ⚠️ **DK 的 Display/Path .asset 改动易被 `git checkout` 误回退**（png+meta 是 untracked 不受影响，但 .asset 是 tracked 会被还原）→ 录完 DK 别对 DisplayKey 目录做 git 丢弃；被回退了就重追加 Display 条目 + 重新 Ctrl+Shift+E。
