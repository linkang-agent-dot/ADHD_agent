---
name: feedback_x2_merge_driver_drops_remote
description: X2合并两条节日分支进master_bugfix的坑：driver返1丢对方整份改动+预合并方向keep-ours会回退目标分支内容
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b3e6fb3a-0047-4805-9a66-e64930e19551
---

X2 配置仓（x2gdconf）用 gsheet_sync merge skill 合并、且**双方是两条并行节日分支**（如 dev_festival=拓荒节 vs master_bugfix=占星节/科技节）时，有两个非显而易见的坑：

**坑1：merge driver(tsv_merge_pro.py) 返回 1 = 丢掉对方整份改动，不止冲突格。**
- driver 检测到单元格冲突/parallel_fork 时返回 1，Git 标记 UU，但**工作区内容=纯本地(ours)版本，remote 侧所有改动(含非冲突行)全没合进来**，且没有 `<<<<<<<` 标记。
- 所以这些文件**不能简单 keep ours 了事**——必须手动把 remote 的非冲突行/净新增行并回来。看 remote 改了啥：`git diff $(git merge-base HEAD MERGE_HEAD) MERGE_HEAD -- <file>`。

**坑2：决策表"同作者取最新=keep ours"在【预合并(主→子)】方向会埋雷。**
- 流程B"子→主"要求先做"主→子"预合并。此步目的=把主分支(master_bugfix)净内容吸进子分支，否则下一步 子→主 会把主分支独有内容**回退掉**。
- 此时若按优先级5(同一改人取时间更新一方)整文件 keep ours(子分支更新)，子分支就拿不到主分支的内容→反向合并即事故。
- **正确解=并集**：保子分支新行 + 吸收主分支非冲突行；只有"同一行双方都改"的少数格才按优先级选边，跨线改同一道具(如本案 item 11119517 两条线各改各的)**必须让用户拍**，不替他猜。

**坑3(根因)：driver 是【按行位置 index】比较，不是按 ID。** `merge_tsv` 里 `rows_l[i] vs rows_r[i]` 逐位置比 → dev 在表中间插了拓荒新行，后面所有行位全错位 → 把大量【其实值相同】的行误报成 conflict/parallel_fork。`.merge_alert_pending.json` 记的冲突行多半是这种虚报；逐行比对 `git show HEAD:<f>` vs `git show MERGE_HEAD:<f>`（ReadAllBytes+UTF8，别用 Get-Content，见 [[feedback_x2_import_dont_oververify]]）一验就知。

**✅ 正确解法 = ID-keyed cell 级三方合并器**：`C:\ADHD_agent\.cursor\skills\x2-config-download\scripts\id_merge_3way.py`。
- 读 git 三方 stage(`:1:`base/`:2:`ours/`:3:`theirs)，复合 key=col1+col2(对所有X2配置表唯一；activity_rank_rewards 多行共享col1=组ID 必须加col2)，按 ID 对齐后 cell 级判定：`ours==theirs`保留 / `ours==base且theirs变`→吸收master / `theirs==base且dev变`→keepdev / 双方都改→keepdev(冲突取dev)；master净新增行(在theirs不在base/ours)并入；dev删的行(在base/theirs不在ours)尊重删除。
- 用法：先 `git merge origin/master_bugfix`(driver 自动解非冲突+i18n)，对剩下的 UU 配置表跑 `python id_merge_3way.py <无--write先dry-run出报告> ... 确认后加 --write`，再 `git add`。json 冲突走 `refresh_json_from_tsv.py`(tsv变了的)或 `git checkout --ours`(tsv没变的)再 add。
- 前置：三方 header 必须一致(`git show :1:/:2:/:3:` 比对)才能按列位 cell 比；不一致要先按列名对齐。

**合并后异常审查必须 cell 级，不能行级**（2026-06-10 复查教训）：审查"合并是否丢了 master 自己改的值"，工具 `C:\ADHD_agent\.cursor\skills\x2-config-download\scripts\merge_anomaly_audit.py <base> <master> <dev> <result>`。真异常定义=**某格 master≠base(master改过) 且 result≠master(没保留)**。行级/整行比对会大量误报：① master 和 dev 各改同一行的不同列 → 行不等但 master 的格其实都保住了；② 节日换皮会改备注列、排行重排会改组号/档位列 → 按 col2/slot 做 key 时 key 对不上，看着像"整行删除"，实则 master==base 没丢东西。整行删除分支必须加 `master≠base` 守卫才不误报。本次复查：config/json 全干净，唯一被判 dev 的就是用户拍板的那几个真冲突；i18n(1011) 那类异常是 merge driver 按时间戳判(Remote=0 一律 dev 赢)特有的、跟 cell 合并器无关。

**关键经验：net_new=0 全表 → dev 早已⊇ master**。本案合并器报告所有表 master净新增=0、只需吸收12格零散修正，证明 dev_festival 早含 master 的占星/科技节内容；之前按"行位 diff"看 master 像有大量独有内容、担心反向合并回退，是**行位错位造成的虚惊**。判分叉规模别信 `git diff`(行位)，要信 ID-keyed 比对。

**合并收尾【默认标准步骤·用户确认有效】：非节日改动审查 + 按行还原。** 凡节日分支合进 master_bugfix(或任何主分支)后，**不等用户要求、默认主动跑一次**。默认只对 🔴 采取行动(报给用户确认是否还原)，🟡 只informational列一下不处理(用户 2026-06-10 明确"中风险不用管")。做法：diff `<旧master_bugfix>..<新>` -- fo/config/，按 ID 比对分三类：① 🔴 **改动了非节日的现有配置**(改非新增)=最高风险，会覆盖线上/其他活动——本案揪出首充礼包(iap_template 2013670001)加料、cycle包(2013699146)奖励缩水、储蓄罐(2013680004)改用途、首充破冰(activity_config 211200012)加排除服条件、试用打造队列(item 11119555-557)等被节日分支误带改动；② 🟡 新增其他节日内容(科技/登月/春节…新ID休眠)=中风险，确认该不该现在进主版本；③ 🟢 节日本体+挖矿=预期。关键词过滤(拓荒/labor/pioneer/挖矿/metro)分流，metro_minigame 行备注是"阶N"不含拓荒会被误判非节日，需人工归类。
**误带行还原**：取合并前 ref 的该行覆盖工作区同 ID 行(`git show 51620db02:<f>` 找同 col1 行替换)，只动目标行不碰其余合并内容；还原后验字段数异常数 == HEAD(meta短行是固有的、非引入) + pre_push_check dry-run。
**⚠️还原只是权宜，会被重导复活**：X2 这些表真源=GSheet，把行还原成 master 值后 GSheet 仍是节日值；下次重导同一表会把还原的行**又冲回节日值**。所以①重导任何还原过的表前，先 diff 查这些行是否又出现在变动里，是则只导其余行、保还原行不动(并提示用户去 GSheet 永久改)；②永久修复=改 GSheet 本身。
**已还原行清单(GSheet未改, 每次重导对应表都要排除)**：iap_template `2013670001/2013680004/2013699146`；activity_config(2112) `211200012`；item(1111) `11119555/11119556/11119557`；**get_access_group(1168) `11683015/11683017/11683021`**(2026-06-11 master_bugfix→master 合并后回退, b7c1cd163, access_group 被改成拆 entry, 回退到单entry双args；⚠️真源GSheet/1168 可能仍是拆分版, 重导会复活, master(b7c1cd163)与master_bugfix(a10cc662d)两分支均已回退并对齐)。
**固化工具**：保还原行别再手写一次性脚本，用 `C:\ADHD_agent\.cursor\skills\x2-config-download\scripts\restore_rows_to_ref.py <tsv> <id1,id2,..> [ref默认HEAD]`——导表后跑它把还原行恢复成 HEAD、其余保留 GSheet 导入值，再 git diff 复核+提交。2026-06-10 已对 2013/1111/2112 实操多次。

**⚠️【两个操作坑·每次合并必踩】** ① **`git merge` 被 `scripts/.merge_alert_pending.json` 挡住 abort**：该文件在某些主分支被 tracked、另一些没 tracked，merge driver 跑 i18n 时又会把它当 untracked 重新写出 → git 报 `untracked working tree files would be overwritten by merge, Aborting`。删了也没用（driver 当场重建）。解：`echo 'scripts/.merge_alert_pending.json' >> .git/info/exclude`（git 对 ignored 文件直接覆盖、不再 abort），纯本地无副作用，再重跑 merge。② **`git show :0:<file>` / `git cat-file -p :0:<file>` 对刚 auto-merge 的大文件会返回空**（不是文件真空！`git ls-files -s` 能看到 stage0 blob 有 hash）→ 验证合并后内容**别信 `:0:`，直接读 worktree 文件**（`open(path,'rb')`）或用 `git cat-file -p <blob_hash>`。我两次合并都被这个假象骗以为 i18n 全丢，实际 worktree 正确。

**⚠️【流程坑·先于一切】master_bugfix→master 也是「子→主」，必须走 skill 流程B 两步、禁止直接单向 merge。** 正确序：①**先** `git merge origin/master`（站在 master_bugfix 上，主→子预合并）解冲突+提交+push master_bugfix —— 这步同时把 master 独有提交「往回合」进 master_bugfix（客户端主版本），否则 master_bugfix 会落后；②**再**站 master 上 `git merge origin/master_bugfix`（此时 master_bugfix⊇master，干净）。2026-06-11 我直接在 master 上单向 merge master_bugfix，跳过①→虽然 master 结果审计 0 真异常（内容对），但 master_bugfix 仍缺 master 的 27 提交、且违背 skill。被用户当场点「master 没往回合，没走 skill」。判据：合并前先 `git rev-list --count origin/master_bugfix..master`>0 就说明 master 有独有提交、必须先预合并往回。

**⚠️【方向反转坑】master_bugfix→master 合并时 i18n driver 会丢节日翻译（与 dev_festival→bugfix 相反）。** i18n merge driver 按时间戳判，节日侧(master_bugfix) `Remote Time=0` 一律输给有真实时间戳的一侧 → 在 `git merge origin/master_bugfix`（站在 master 上）时 **ours=master 赢**，结果 i18n = master 原样（仅重排），**master_bugfix 的 154 个节日新 key 全没合进来**（`EVENT_labor_2026_*`/`EVENT_item_card_*`/`EVENT_metro_*`/BP/city_skin…），活动在游戏里显示裸 LC key。`git diff --stat` 看 i18n 大改是**重排假象**，不代表合进了节日文案。判据：比 staged i18n 的 keyset vs MERGE_HEAD——`festival-only(bugfix-master)` 应全在 staged，否则被丢。**正确解**：i18n 走 ID(LC key)级 union——`master-only key` 通常=0（bugfix 是 master 的 key 超集），所有 value 差异多是 `master==base & bugfix改`（节日编辑，如 占星ASTROLOGY→拓荒RallyPass、闪购60→180min），故 **直接取 MERGE_HEAD(bugfix) 全量 i18n** 即正确（再兜底 append 任何 master-only 行）。config/json 走 id_merge_3way 不受此坑影响（那是 cell 级 ID 比对，非时间戳）。2026-06-11 master_bugfix→master 拓荒节发布合并实测：17/18 langs 被 driver 误判保留 master，手动改回 bugfix 超集修复。

**收尾审计套路（本次验证有效）**：合并 commit 后跑 ① `merge_anomaly_audit.py <base> <master(pre)> <bugfix> <merge-result>` → `真异常=0` 证 master 独有改动(本次27提交)全保住；② `pre_push_check.py --dry-run` → `无列结构异常` 证无 trivial-merge 静默丢列。两者只覆盖 config/json，**i18n 必须另行 keyset 比对**（见上）。ActivityCalendar.json 等 fo/json 的 .json 冲突：`refresh_json_from_tsv.py` 会因旧 json 带 `<<<<<<<` 标记而 crash（它读旧 json 当类型模板）——先用两 parent(`HEAD:`/`MERGE_HEAD:`) 的干净 json 合成模板覆盖掉带标记的文件，再 `tsv_to_json.py <tsv>` 重建。⚠️别像我一样过早 `git add` json——会塌掉 `:1/:2/:3` merge stages，之后只能用 HEAD/MERGE_HEAD 取 parent。

2026-06-09→10 拓荒节(117提交)→master_bugfix 合并**全程实战完成**：预合并解9冲突(并集+dev赢, id_merge_3way.py) → ff合并(afc308f40) → 非节日审查揪出7行误带改动、还原到master原值(420e6174f)推送。关联 [[workflow_x2_table_import]] [[feedback_x2_import_dont_oververify]]
