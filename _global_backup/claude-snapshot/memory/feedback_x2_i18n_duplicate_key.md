---
name: x2-i18n-key
description: X2 1011 i18n 表同一 LC key 出现多行时，fwcli 生成取首条，常显示成旧/错值；排查皮肤名等显示异常时必查重复 key
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f5d0e986-b7f5-42c6-ab46-30c79d5d6a9b
---

X2 的 1011 i18n 表（SheetID `1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg`，文案在 EVENT 页签）里，**同一个 LC key 可能被写了多行**（换皮/复制模板时遗留：模板占位行 + 节日主题行各一条）。

**两层危害（后者更狠）：**
1. **构建成功时**：fwcli 生成 cn.tsv 按 key 取**首条（行号靠前那条，通常是占位旧值）**，游戏里显示成占位/旧值。
2. **构建失败时（更隐蔽）**：cn 列只要有重复 key，fwcli i18n 阶段直接 **`download i18n fail` 整表不落盘**，cn.tsv/各语言 tsv 全保持上一次旧版——**整个节日文案都进不去游戏**。而 xlsx 下载那步仍显示 successful、EXITCODE=0，极易误判导表成功。

2026-06 拓荒节实例：EVENT 页签 labor_2026 系列有 **17 个重复 key**（city_skin/march_skin/floor/wall/decoration 的 title+desc），规律=小行号(7365~7399)占位通用值（装饰物/墙纸/行军特效…）+ 大行号(7476~7492)拓荒节主题值（拓荒节舞台/拓荒先锋…）。这 17 个重复让 i18n 构建一直失败，**整个拓荒节文案从没进过游戏**。修复=删掉 17 条占位行（**从大到小删避免行号漂移**），重跑导表即 finish。

**Why:** 换皮后"文案改对了但游戏里还是旧/占位值"的头号根因是重复 key——可能是取首条显示错，更可能是导表整表失败而你以为成功了。
**How to apply:**
- 排查 X2 任何文案显示成旧值/占位值时，先整列读 EVENT!A:C 按 key 精确匹配，确认该 key 是否有 >1 行。
- 删重复行前二次确认行的 key+cn，i18n 按 key 取值非按行号引用，删错值条是正解。
- 真实 key **无 `EVENT_` 前缀**（EVENT 是页签名）；resolver 默认页签是污染备份页签，读写必须显式指定 EVENT。
- 改既有 key 用 `values.update` 按行覆写，禁止 append（否则再造重复）。详见 [[workflow_x2_table_import]]。
- **每次 X2 i18n 导表后必看 fwcli 输出有没有 `download i18n fail`**——有就是 cn 列有重复 key，报的 key 全列出来去重再重跑；别只看 xlsx successful / EXITCODE=0 就当导成功。
- 删重复行时按行号**从大到小**删（deleteDimension startIndex 0-based），避免删上面的行导致下面行号漂移。

**换皮"整套 LC key 家族漏搬"（2026-06-04 拓荒节挖矿累积任务 21127383 实例）：**
- 症状：活动名称/rule/全部任务描述在游戏里显示原始 key。根因不是重复 key，而是换皮时把 P2 的配置(含 LC key)照搬进 X2 的 2112/2115，但**对应翻译从没搬进 X2 的 1011 i18n 表**——X2 表里那套 key 0 条命中（EVENT/METRO/minigame 全查过）。
- **最稳修法 = 去 P2 源活动回填，不重新翻译**：X2 换皮活动的 `constant`(如 `metro_minigame_labor26_task`) 通常和 P2 源活动**完全相同** → 在 P2 2112(`2112_dev`) 按 constant 搜到源活动 → 它引用的 LC key 在 P2 1011 i18n 里有线上验证过的全语言翻译 → 整行(去掉 P2 的 ID_int 列、改用 X2 EVENT 的 max ID_int+1)回填进 X2 1011 EVENT。
- **P2 1011 i18n SheetID = `11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY`**（未注册别名，用 `gsheet_query.py alias set 1011_p2_i18n <sid>` 临时注册即可查；X2 1011 = `1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg`）。两边 EVENT 页签结构相同(20列: ID_int/ID/cn/18语言/cns)，key 列存**去掉 `LC_EVENT_` 前缀的裸 key**。
- 这类 `metro_minigame_normal_task_*`(title/rule/通关任务) 是 P2 **全节日共用**的通用文案，只有 group_label 按节日换；分隔符 P2 源头就不统一(`_1_1` 下划线 vs `_4-1` 连字符)，回填时照抄勿"修正"。
- 导表：fwcli `googlexlsx -f 1011_x2_i18n` 后看到 `download i18n finish`(非 fail) + EVENT 已 `i18n_process` + diff 是 17 语言各 +N 行纯新增即成功；`has error value` 若是别的历史 index(非本次 key)可忽略。
- **⚠️ X2 活动任务(2115)显示读哪列 = 按 ui_template 模块不同而不同，别一概而论（2026-06-05 我 grep 误判被用户在游戏里证伪）**：
  - 「每日刷新循环活动模板」**ui_template=21191021** 的任务面板**显示读 `task_title`(col9, A_MAP)**，不是 task_desc。换皮从 P2 搬过来时 task_title 全空 `{}`（P2 的 2115 根本没这列），导致游戏里任务标题不显示——这是 21127383 拓荒挖矿任务的实际 BUG。
  - 修法：给每个任务 task_title 填 `{"lc":"<该任务task_desc的同一个key>","args":[1]}`，复用已录入的 i18n key，**不用新翻译**。⚠️ **args 必须非空**：`args:[]` 空数组会被当无效/空 A_MAP，标题不渲染（用户实测踩坑）；文案无占位符时填 `[1]` 占位即可（值不影响显示文字，extra arg 被 string.Format 忽略）。
  - 反面教训：我先 grep 客户端只看到 GangRise/GangSport 等模块读 `TaskDesc` 就断言"显示读 task_desc"——那是**别的活动模板**；不同 ui_template 用不同 UI 模块、读不同列。**结论性判断前要么找到该 template 对应的确切模块，要么直接信用户的游戏内观察**，别拿部分 grep 当全量。
  - task_desc 仍要照样填对(它也是引用同一批 key，i18n 回填覆盖了)，两列都填最稳。
- **⚠️ 改 GSheet + 导表 push ≠ 游戏生效（2026-06-04 漏这步被用户"游戏内没成功"打回）**：X2 的 i18n(`fo/i18n/*.tsv`)随配置走 CDN 下发，push 到 config 分支只是改了配置仓源，测试服不会自动拿到。完整链路第三段 = **kadmin 导配置热更**：`x2-kadmin` skill `workflow_execute.py --keyword hot_reload_config --server_id <服> --env <dev/beta> --config_branch <你push的分支>` → 然后**客户端重新登录**重拉 i18n 才显示。热更前先 `find.py -e <env> -q <server>` 确认该服当前部署的**配置分支 == 你 push 的分支**，否则白跑。报"改完本地化"别停在 push，必须问环境+服务器 ID 把热更也跑了(或明确告知用户这步要他自己跑)才算闭环。
