---
name: p2-config-upload
description: P2配置表上传工具。支持全表下载和行筛选两种模式，从 Google Sheet 下载配置表并提交到 gdconfig 仓库。内置 898 张表的编号→页签映射。**表 1011（i18n）暂不由 Agent 自动上传**（见 Skill 正文禁令）。当用户提到"P2导表"、"传表"、"导表"、"上传配置"、或给出数字编号+分支时使用。
---

# P2 配置表上传工具

触发词：P2导表、传表、导表、上传配置、用户给数字编号+分支

## ⛔ 临时禁令：表 **1011（i18n）**

**在用户明确书面解禁前，Agent 禁止对 1011 / i18n 执行「下载并写入 `fo/i18n` + `git commit` / `push`」全流程**，包括：

- 使用 `GSheetDownloader.exe` 拉取 1011；
- 使用 `i18n_dl_utf8.py` 或其它脚本生成 `fo/i18n/*.tsv` 后提交推送。

**原因（简述）**：当前自动化路径上传 1011 易产生与预期不一致的问题（Downloader 编码/部分失败、脚本与官方导出差异等），先由负责人在本机按团队流程处理。

**用户仅要求传 1011 时**：礼貌说明禁令，请对方本机导出并提交，或对话中**明确写「解禁 1011」**后再执行。

**一批多张表且含 1011 时**：**跳过 1011**，对其余表号照常走 S1–S5；回复中必须列出「已跳过 1011（临时禁令）」。

---

## 两种模式

- **全表模式**：用户只给表编号（如 `2115`），下载整张表并提交
- **行筛选模式**：用户给出具体行 ID（如 `211552039`），只更新指定行，其余行保持不变

> 识别方式：若用户给出的数字位数 ≥ 7 位，则视为行 ID，触发行筛选模式；否则为表编号。

---

## 执行顺序（全表模式，5步）

**S1 确认分支**
```powershell
git -C C:\gdconfig branch --show-current
```
切换：`git -C C:\gdconfig checkout -q <branch>; git -C C:\gdconfig pull -q`

**S2 下载**

多个编号用**空格分隔**，一次性下载：

```powershell
# 单个表
echo "1`n1111`nn" | & "C:\gdconfig\scripts\GSheetDownloader.exe"

# 多个表（空格分隔，一次下载）
echo "1`n1168 1111`nn" | & "C:\gdconfig\scripts\GSheetDownloader.exe"
```

> 用户输入如 `1168 1111`（空格分隔），直接拼成空格分隔的编号串一次传入。

**S3 校验下载结果 ⚠️ 必须执行，不得跳过**

每次 GSheetDownloader 执行完毕后，**必须**读取输出日志的最后 15 行，检查是否下载成功：

```powershell
# 读取下载日志末尾（日志路径为 Shell 工具返回的 agent-tools/*.txt）
# 在末尾找以下关键词：
#   成功: X  → X 应等于下载表数量
#   失败: X  → X 应为 0
#   ! json error on row  → 表示 GSheet 数据有 JSON 格式错误
#   下载完成: <页签名>  → 用于页签名检测
```

**判定规则**：
- ✅ `成功: N, 失败: 0` 且 N > 0 且**无** `json error` → 下载成功，继续 S3.5
- ❌ 出现 `! json error on row X col Y : 列名` → **下载失败**，立即停止并报告：
  ```
  ⚠️ 下载失败：<表编号>(<页签>) 第 X 行 列 Y (列名) JSON 格式错误
  错误详情：<错误描述>
  请在 GSheet 中修正该行后重新下载。
  ```
- ❌ `成功: 0` 或 `失败: X>0` → **下载失败**，报告错误，不提交
- ⚠️ **绝对禁止**：当下载失败时，因为 `git diff` 无变动就告诉用户"已是最新"。无变动 + 下载失败 = 下载没生效，必须告知用户下载出错了。

**S3.5 页签名检测 ⚠️ 必须执行**

> **页签历史不落仓库**：`tab_history.py` 将记录写入本机目录（Windows：`%LOCALAPPDATA%\P2GSheetTabHistory\tab_history.json`），**禁止**提交到 gdconfig 分支。若环境变量 `P2_TAB_HISTORY_FILE` 已设置，则使用该路径。若仓库根目录曾误生成过 `tab_history.json`，应从版本库移除并加入 `.gitignore`：`git rm --cached tab_history.json`（如已跟踪）。

从日志末尾提取每张表的实际页签名（日志格式：`下载完成: <页签名>`），然后运行检测脚本：

```powershell
# 禁止把 tab_history 放进 gdconfig 仓库（不要 Copy 到 C:\gdconfig\scripts\）。直接调用个人项目脚本，JSON 落在 %LOCALAPPDATA%\P2GSheetTabHistory\
python "c:\ADHD_agent\.cursor\skills\P2-config-upload\scripts\tab_history.py" check <table_id> <tab_name>
```

**判定规则**：
- ✅ exit 0 → 页签名未变化或首次记录，继续 S4
- ❌ exit 1（输出 `⚠️ 页签名变化！`）→ **立即停止并询问用户**：
  ```
  ⚠️ 检测到表 <table_id> 的页签名发生变化：
  上次：<old_tab>
  本次：<new_tab>
  
  请确认是否继续？这可能意味着表结构已调整。
  ```
  等待用户确认后再继续。

下载成功且用户确认后，更新记录：
```powershell
python "c:\ADHD_agent\.cursor\skills\P2-config-upload\scripts\tab_history.py" update <table_id> <tab_name>
```

**S4 查看改动 ⚠️ 必须输出摘要给用户**

```powershell
# 1. 统计文件变动
git -C C:\gdconfig diff --stat

# 2. 列出变动行 ID（带注释字段，截断到 80 字符）
git -C C:\gdconfig diff fo/config/<页签>.tsv | Select-String "^[-+][0-9]" | ForEach-Object { $_.Line.Substring(0, [Math]::Min(80, $_.Line.Length)) }
```

> - `A_INT_group` 在第0列时：取 `$cols[0]` 为行标记，`$cols[1]` 为 ID
> - `A_INT_id` 在第0列时：取 `$cols[0]` 为行标记，后续列为字段
> - diff 极长（>50行）时加 `| Select-Object -First 60`

**提交前必须向用户输出**（格式见"回复格式"节）：变动了哪些 ID、字段改动是什么。

**S5 提交推送**
```powershell
# 默认只 add fo/，避免误将根目录工具状态文件（如历史遗留的 tab_history.json）提交进分支；若本次还改了其它已跟踪路径再显式 git add 该路径
git -C C:\gdconfig add fo/
git -C C:\gdconfig commit -m "[配置更新]<页签>-<分支>-<五字>"; git -C C:\gdconfig pull -q --rebase; git -C C:\gdconfig push
```

---

## 执行顺序（行筛选模式，6步）

行 ID 前缀即表编号（如 `211552039` → 表 `2115`），注意同一批里**不同前缀要分表处理**。

**S1 确认分支**（同全表模式）

**S2 备份原始 TSV**
```powershell
Copy-Item "C:\gdconfig\fo\config\<页签>.tsv" "C:\gdconfig\fo\config\<页签>.tsv.bak"
```

**S3 下载对应表**（同全表模式，按表编号下载）

> ⚠️ 下载完成后**必须**按全表模式 S3 的校验规则检查日志末尾，确认下载成功。若出现 `json error` 或 `成功: 0`，立即停止并报告错误，不执行后续步骤。
> 同样执行全表模式 **S3.5 页签名检测**，若页签名变化则先询问用户确认。

**S4 精准行合并**

脚本存放于 `c:\ADHD_agent\.cursor\skills\P2-config-upload\scripts\merge_rows.py`（个人项目源），使用前先同步到 gdconfig：

```powershell
Copy-Item "c:\ADHD_agent\.cursor\skills\P2-config-upload\scripts\merge_rows.py" "C:\gdconfig\scripts\merge_rows.py" -Force
```

然后执行，只替换/新增目标行，其余行保持不变：

```powershell
python C:\gdconfig\scripts\merge_rows.py `
  "C:\gdconfig\fo\config\<页签>.tsv" `
  "行ID1,行ID2,行ID3"
```

脚本会输出每行的处理状态：
- `[updated]` — 原文件有该行，已用新版本替换
- `[added]` — 原文件无该行，已追加到末尾
- `[WARN] not found anywhere` — 新下载的 TSV 中也没有该行，跳过（需检查 GSheet）

> **注意**：脚本自动检测 `A_INT_id` 所在列（支持第1列或第2列），无需手动指定。

---

## 常见问题排查

### GSheetDownloader 显示"成功: 0"但无报错

原因：目标表的 GSheet 中存在 JSON 格式错误的行，Downloader 解析到该行时停止，整张表 0 成功。

**排查步骤**：
1. 看错误信息中的 `row X col Y : 列名`，定位到出错的行号和列名
2. 用 gws 读取 GSheet 对应行：
```powershell
$env:GOOGLE_WORKSPACE_PROJECT_ID = 'calm-repeater-489707-n1'
python -c "
import subprocess, json
GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
params = json.dumps({'spreadsheetId': '<sheet_id>', 'range': '<tab>!A<row-2>:F<row+2>'})
r = subprocess.run([GWS, 'sheets', 'spreadsheets', 'values', 'get', '--params', params], capture_output=True, text=True, encoding='utf-8')
data = json.loads(r.stdout)
for row in data.get('values', []):
    print(row[0], '|', row[4][:100] if len(row) > 4 else '')
"
```
3. 常见原因：配置行中有 `{填数量}` 等占位符未替换，导致 JSON 数值字段是字符串
4. 让用户在 GSheet 里修正后重新下载

### 1011 i18n：策划说「线上表」有改，但 `fo/i18n` 无 git diff

> **Agent 行为**：上文「临时禁令」生效期间，**不得**为排查而自动重下/重传 1011；本节仅供人工排查参考。

**原因（机制）**：GSheetDownloader **不会**自动去读你口头说的「线上一张表」。它只读 `C:\gdconfig\scripts\gsheet_config.ini` 里 **`gsheet_config_id` 指向的那份「配置索引表」**，从中解析 **1011 → i18n** 绑定的 **Spreadsheet ID + 各语言子页签 gid**，再逐 tab 下载并 **merge** 进 `fo/i18n/*.tsv`。

若差异实际写在 **另一本 Spreadsheet**、或 **同一本里未挂进索引的子表**、或 **索引行仍指向旧 sheet**，则导出结果会与当前 hotfix 仓库里已有文件 **完全一致** → `成功: 0`（无新写入）且无 diff。**这不是「没传」而是「工具读的数据源就不是你以为的那张线上表」。**

**排查**：
1. 打开索引表，找到 **1011 / i18n** 对应行，核对 **sheet_id 与各 tab** 是否与策划正在改的「线上」为**同一链接**。
2. 若线上已换表或新增 tab：需 **改索引** 或 **把内容合并进索引已指向的 tab**，再重下 1011。
3. 若索引正确仍无 diff：用 gws 对 **索引里的 sheet** 拉一行 key 与本地 `cn.tsv` 同一 key 对比，确认 API 导出是否真与表上所见一致（排除看错 tab / 未保存 / 权限视图）。

**原因（导出层，易与「索引指错表」混淆）**：1011 会按 **很多子页签** 异步拉取；日志里若出现 **`400 Bad Request`**、**某个 gid/tab 导出失败**、或仅部分语言更新，Downloader 仍可能对整批打出 **「成功: N, 失败: 0」** 之类汇总，但 **`fo/i18n` 实际未写入新行** → `git diff fo/i18n` 为空。**禁止**在「用户明确说表上已加 key」时，仅凭 **无 diff** 就结论「表上没变动」；必须先 **通读当次下载日志**（检索 `400`、`Bad Request`、失败 tab 名），并遵守上文 S3：**无 diff + 日志里有导出失败 = 下载未生效，不是策划没改。**

**原因（编码层，Windows 常见）**：日志若出现 **`'gbk' codec can't encode character`**（例如在 **`HERO`** 页签写 **`po.tsv`** 时遇到阿拉伯文 **`U+0625`** 等），说明 Downloader **按 GBK 写文件**，无法表示该 Unicode 字符 → 该页签处理失败，末尾常伴随 **`一些标签页处理失败`**，且汇总 **`成功: 0`**（整表未计入成功保存）。此时 **`fo/i18n` 无 diff 是工具失败，不是表上无新文案**。修复方向：让维护者把 GSheetDownloader **写出 TSV 改为 UTF-8**（或修正表中错列的字符）；临时可换用能完整跑通导出的环境/版本，或由策划把异常字符改到正确语言列。

### `[WARN] not found anywhere` — 行在 GSheet 存在但找不到

原因有两种：
1. **行在非主表 tab**：GSheetDownloader 只读取主 tab（通常是 `activity_event_pkg` 等第一个 tab）；用户若把新行添加到了临时/审核 tab，Downloader 读不到
2. **GSheetDownloader 因 json 错误提前退出**：同上，先排查 json 格式问题

解决：让用户把行移到主 tab，或直接在本地 TSV 手动写入后提交。

**S5 验证**
```powershell
git -C C:\gdconfig diff --stat
```
确认只有目标表的 fo/config/<页签>.tsv 有变动。用以下命令检查变更行 ID：
```powershell
git diff C:\gdconfig\fo\config\<页签>.tsv | Select-String "^[-+][0-9]"
```

**S6 提交推送 + 清理备份**
```powershell
Remove-Item "C:\gdconfig\fo\config\<页签>.tsv.bak"
git -C C:\gdconfig add fo/
git -C C:\gdconfig commit -m "[配置更新]<页签>-<分支>-行筛选"; git -C C:\gdconfig push
```

---

## 编号→页签速查（全量 898 表，截止 2026-03-20）

| 编号 | 页签 |
|------|------|
| 1011 | i18n ⚠️ **Agent 禁止上传（临时禁令，见文首）** |
| 1012 | val_format |
| 1013 | const_config |
| 1014 | statistical_data |
| 1018 | ab_test |
| 1019 | statistical_data_relation |
| 1020 | dlc_priority |
| 1021 | china_holiday |
| 1022 | function_switch |
| 1023 | popwindow |
| 1024 | merge_server_counter |
| 1025 | hot_const_config |
| 1026 | domestic_channel |
| 1027 | channel_detail |
| 1028 | google_smart_event |
| 1029 | update_tips_version |
| 1030 | iaa_center |
| 1110 | asset |
| 1111 | item |
| 1113 | item_store |
| 1114 | rss |
| 1115 | vm |
| 1116 | xp |
| 1117 | recover |
| 1118 | building |
| 1119 | research |
| 1120 | drop |
| 1121 | soldier |
| 1122 | soldier_category |
| 1124 | speedup |
| 1125 | building_slot |
| 1126 | city_building_skin |
| 1127 | building_build |
| 1128 | instant_price_asset |
| 1129 | instant_price_time |
| 1130 | building_function |
| 1131 | building_bubble |
| 1132 | research_category |
| 1133 | player_avatar |
| 1135 | player_level |
| 1136 | player_fashion |
| 1137 | hero_stationed |
| 1138 | hero_stationed_buff |
| 1139 | hero_stationed_exercise |
| 1140 | city_map_grid |
| 1142 | avatar_frame |
| 1143 | city_wall_flag |
| 1144 | nation_flag |
| 1145 | tavern_login_reward |
| 1146 | tavern_bar_gift |
| 1147 | tavern_story_gift |
| 1148 | tavern_trader_list |
| 1150 | tavern_top_pool |
| 1151 | secret_shop_item |
| 1152 | banana_hologram |
| 1153 | get_access |
| 1154 | vip_shop |
| 1155 | collection |
| 1156 | collection_group |
| 1157 | collection_gacha_package |
| 1158 | collection_gacha_reward |
| 1159 | player_badge |
| 1160 | banana_decorations |
| 1161 | asset_retake |
| 1162 | asset_retake_shop |
| 1163 | inner_coin |
| 1164 | collection_power_buff |
| 1165 | stores |
| 1166 | soldier_arms |
| 1167 | arms_group |
| 1168 | get_access_group |
| 1169 | city_area |
| 1170 | paradeground |
| 1171 | building_reset_v36 |
| 1172 | paradeground_soldiershow |
| 1173 | chat_skin |
| 1174 | daily_growth |
| 1175 | safe_box |
| 1176 | collection_platform |
| 1177 | citybeauty_reward |
| 1178 | battery_research_skill |
| 1179 | capsule_rss_convert_cost |
| 1180 | map_emoji |
| 1181 | collection_filter |
| 1182 | collection_break_achievement |
| 1183 | item_bag_classification |
| 1197 | wonder_reward_retake |
| 1198 | tavern_change |
| 1199 | research_change |
| 1211 | buff |
| 1212 | buff_category |
| 1213 | buff_source |
| 1214 | power |
| 1215 | power_category |
| 1216 | power_source |
| 1217 | power_compare |
| 1218 | player_data |
| 1220 | city_manage |
| 1221 | buff_property |
| 1222 | temporary_buff |
| 1223 | citybeauty |
| 1224 | citybeauty_source |
| 1225 | power_resolve |
| 1312 | city_skin |
| 1313 | map_npc_refresh_zone |
| 1314 | map_npc_refresh_band |
| 1315 | map_npc_moving |
| 1316 | npc_gather |
| 1334 | npc_gather_class |
| 1317 | npc_troop |
| 1333 | npc_troop_class |
| 1318 | npc_city |
| 1319 | search |
| 1320 | intuitive_zoom |
| 1321 | march_type |
| 1323 | special_troop |
| 1324 | special_city_category |
| 1326 | npc_class |
| 1327 | special_building |
| 1328 | troop_show_info |
| 1329 | chasing_distance_time |
| 1330 | ruin_play |
| 1331 | troop_formation |
| 1332 | map_fixed_point |
| 1335 | map_mark |
| 1336 | train_point |
| 1337 | territory_building |
| 1338 | union_rss_spot |
| 1339 | union_tower_cost |
| 1340 | union_center_rank |
| 1341 | loot_be_assigned |
| 1342 | map_unit_filter |
| 1343 | map_unit_legend |
| 1344 | map_player_building |
| 1345 | horde_train |
| 1346 | pass |
| 1347 | explore_relic |
| 1348 | explore_categories |
| 1349 | explore_relic_reward |
| 1353 | fix_rail |
| 1355 | transport_supplies |
| 1356 | transport_mutant_refresh |
| 1357 | all_round_arena_score |
| 1358 | all_round_arena_robot |
| 1359 | elite_arena_robot |
| 1360 | map_unit_render |
| 1361 | hero_arena_score |
| 1362 | hero_arena_robot |
| 1363 | npc_counter_class |
| 1364 | radar_robot |
| 1365 | march_effect |
| 1366 | chat_title |
| 1367 | mist_unlock_reward |
| 1368 | mist_unlock_rank_reward |
| 1369 | mist_unlock_main_quest |
| 1370 | hero_statue |
| 1371 | outbuilding |
| 1372 | building_unit |
| 1373 | elite_arena_map |
| 1374 | elite_arena_building |
| 1375 | elite_arena_ai |
| 1376 | elite_arena_reward |
| 1377 | illustrate_reward |
| 1378 | wonder_attach_buff |
| 1379 | map_unit_sound |
| 1381 | uw_npc_gather |
| 1382 | uw_map_npc_refresh_band |
| 1383 | uw_map_npc_refresh_zone |
| 1384 | uw_search |
| 1385 | uw_map_unit_filter |
| 1386 | uw_map_unit_legend |
| 1387 | city_effect |
| 1388 | city_suit_decoration |
| 1389 | city_suit |
| 1390 | march_effect_decoration |
| 1391 | march_effect_suit |
| 1392 | city_effect_extent |
| 1393 | emoji_reward |
| 1394 | emoji_guide |
| 1411 | quest |
| 1414 | daily_task_box |
| 1415 | achievement |
| 1416 | ui_help |
| 1417 | uranium_quest |
| 1418 | elite_quest |
| 1419 | merit_quest |
| 1420 | daily_quest_list |
| 1421 | chapter_quest |
| 1422 | fte_chapter_quest |
| 1423 | daily_quest |
| 1424 | main_quest |
| 1425 | compare_main_quest_old_and_new |
| 1426 | chapter_quest_chat |
| 1427 | dialogue |
| 1428 | dialogue_details |
| 1429 | dialogue_image |
| 1430 | radar_lv |
| 1431 | radar_task |
| 1432 | radar_photo |
| 1433 | chapter_quest_version |
| 1434 | chapter_plot_review |
| 1435 | radar_cond |
| 1436 | radar_dialog |
| 1437 | radar_refresh_radius |
| 1438 | direction_mask_details |
| 1439 | city_target |
| 1511 | display_key |
| 1512 | effect_list |
| 1514 | skill_act_list |
| 1520 | snapshot_sticker |
| 1521 | snapshot_brush |
| 1522 | audio_list |
| 1523 | bubble_icon |
| 1524 | rocket_part |
| 1525 | emoji |
| 1611 | battle_buff |
| 1612 | battle_skill |
| 1613 | battle_damage |
| 1614 | battle_soldier_restraint |
| 1615 | battle_defense_tower |
| 1616 | battle_mail_config |
| 1617 | battle_damage_show |
| 1711 | mail |
| 1712 | radar |
| 1713 | module |
| 1714 | mail_filter |
| 1715 | mail_category |
| 1716 | special_mail_skill_content |
| 1720 | arena_winning_reward |
| 1731 | horde |
| 1732 | energy_gauge |
| 1733 | horde_store |
| 1734 | horde_elite |
| 1735 | reward_box |
| 1736 | horde_rank_reward |
| 1737 | rocket_reward_time_control |
| 1738 | fte_npc_dialogue |
| 1739 | horde_meta_game |
| 1740 | horde_elite_npc |
| 1741 | horde_elite_right |
| 1742 | rankings |
| 1743 | tap4news |
| 1745 | rocket_energy_speed |
| 1746 | trigger_plot |
| 1747 | direction |
| 1754 | survery_trigger |
| 1748 | horde_rocket_technology |
| 1749 | horde_rocket_technology_category |
| 1750 | horde_rocket_quest |
| 1751 | overlord |
| 1752 | horde_change |
| 1753 | new_horde_elite |
| 1755 | wonder_overlord_reward |
| 1756 | wonder_overlord_buff |
| 1757 | wonder_donate |
| 1758 | wonder_donate_rank |
| 1759 | wonder_donate_buff |
| 1760 | wonder_launch_reward |
| 1761 | wonder_overlord_skill |
| 1762 | merit_rank |
| 1763 | merit_season |
| 1764 | merit_shop |
| 1765 | city_monkey_tips |
| 1766 | world_boss_damage_reward |
| 1767 | world_boss_last_hit_reward |
| 1768 | chapter_quest_function_unlock |
| 1769 | chapter_unlock_show |
| 1770 | mail_merge_config |
| 1771 | mail_battle_buff |
| 1772 | world_boss_history_damage_reward |
| 1773 | cd_bank_plan |
| 1774 | cd_bank_growth |
| 1775 | wonder_boss_damage_reward |
| 1776 | direction_behavior_tree |
| 1776 | direction_behavior_tree_mj9 |
| 1777 | tavern_mail_box |
| 1778 | tavern_reward |
| 1779 | challenge_hud |
| 1780 | server_shielding_words |
| 1781 | intimacy_rank |
| 1782 | intimacy_behavior |
| 1783 | friend_recommend |
| 1784 | wonder_boss_rally_reward |
| 1785 | entrust_choose_march |
| 1786 | citylayout_recommend |
| 1787 | message_board |
| 1788 | player_queue |
| 1789 | fte_game_choose |
| 1790 | intimacy_effect |
| 1791 | collection_platform_maintain |
| 1792 | troop_capacity_rent |
| 1811 | union_class |
| 1812 | union_order |
| 1816 | union_gift_level |
| 1817 | union_gift_quality_drop |
| 1818 | union_research |
| 1819 | union_research_category |
| 1820 | union_research_donation_rank |
| 1821 | union_rss_usagelog |
| 1822 | union_warehouse |
| 1823 | robot_union_name |
| 1824 | gve_hurdle |
| 1825 | gve_monster |
| 1826 | union_level |
| 1827 | union_function |
| 1828 | union_development_quest |
| 1829 | union_development_quest_list |
| 1830 | union_development_quest_box |
| 1831 | union_active_skill |
| 1832 | union_log |
| 1833 | union_rank_change |
| 1834 | union_flag |
| 1835 | union_quest_bigstage |
| 1836 | union_quest_smallstage |
| 1837 | union_quest_task |
| 1838 | senior_gve_hurdle |
| 1839 | senior_gve_hurdle_challenge_event |
| 1840 | senior_gve_hurdle_event_type |
| 1841 | senior_gve_hurdle_event_type_group |
| 1842 | senior_gve_hurdle_scorereward |
| 1843 | senior_gve_hurdle_event |
| 1920 | hero_data |
| 1921 | hero_star_level |
| 1922 | hero_talent |
| 1923 | hero_talent_tree |
| 1924 | hero_skill |
| 1925 | hero_star |
| 1926 | skill_condition |
| 1927 | skill_effect |
| 1928 | hero_fx |
| 1929 | hero_gacha_pool |
| 1930 | hero_gacha_reward |
| 1931 | hero_gacha_special |
| 1932 | skill_render |
| 1933 | hero_double_talent |
| 1934 | hero_equipment_blueprint |
| 1935 | hero_equipment |
| 1936 | hero_equipment_lvl |
| 1937 | equipment_entry_buff |
| 1938 | equipment_entry_library |
| 1939 | equipment_entry_skill |
| 1940 | equipment_entry_skill_effect |
| 1941 | equipment_entry_skill_condition |
| 1942 | equipment_entry_skill_render |
| 1943 | hero_team_score_grade |
| 1944 | hero_statue_skill |
| 1945 | hero_special_description |
| 1946 | skill_summon |
| 1947 | hero_talent_recommend |
| 1948 | hero_filter |
| 1949 | hero_equipment_filter |
| 1950 | hero_skin |
| 1951 | hero_share_skills |
| 1952 | hero_skill_elements |
| 1999 | hero_back_26 |
| 2011 | iap_config |
| 2012 | iap_param |
| 2013 | iap_template |
| 2014 | iap_coeffs |
| 2016 | iap_recharge |
| 2017 | vip |
| 2018 | vip_sign |
| 2019 | vip_buff |
| 2020 | growth_investment |
| 2021 | iap_order |
| 2022 | iap_daily_specials |
| 2023 | iap_daily_receive |
| 2024 | iap_custom_chest |
| 2025 | iap_stage_reward_config |
| 2026 | iap_tavern_membership |
| 2027 | iap_tavern_membership_privilege |
| 2028 | iap_refund |
| 2029 | red_pack |
| 2030 | bi_iap_push |
| 2031 | metro_growth_investment |
| 2032 | tech_achievement |
| 2033 | tech_achievement_task |
| 2034 | mecha_achievement |
| 2035 | iap_pop_first |
| 2036 | time_card_reward |
| 2037 | tavern_exchange_iap |
| 2038 | tavern_iap_point |
| 2039 | tank_achievement |
| 2040 | iap_ads_push |
| 2041 | mecha_driver_achievement |
| 2042 | daily_package |
| 2111 | activity_calendar |
| 2112 | activity_config |
| 2113 | activity_schema |
| 2114 | activity_rank_group |
| 2115 | activity_task |
| 2116 | activity_item_exchange |
| 2117 | activity_item_recycle |
| 2118 | activity_rank_rewards |
| 2119 | activity_ui_template |
| 2120 | activity_ui_module |
| 2121 | activity_special |
| 2122 | activity_rank_rule |
| 2123 | activity_popwindow |
| 2124 | activity_drop |
| 2125 | activity_discount |
| 2126 | activity_donate_lvl_up |
| 2127 | activity_community_link |
| 2128 | activity_gve_call |
| 2129 | activity_escort_buff |
| 2130 | activity_battle_pass |
| 2131 | activity_battle_pass_level |
| 2132 | activity_alliance_competition_package |
| 2133 | activity_alliance_competition_task |
| 2134 | activity_create_entity |
| 2135 | activity_package |
| 2136 | activity_cycle_period |
| 2137 | activity_asset_retake |
| 2138 | activity_proto_module |
| 2139 | activity_shoot_hunt |
| 2140 | activity_history_damage_reward |
| 2141 | activity_without_gacha_pool |
| 2142 | activity_without_gacha_reward |
| 2143 | activity_fes_bp_module |
| 2144 | activity_hero_achievement |
| 2145 | activity_tips |
| 2146 | activity_puzzle |
| 2147 | activity_collection_gacha_add |
| 2148 | event_decroation_level |
| 2149 | activity_upgrade_gachabox |
| 2150 | activity_hoggboss_type |
| 2151 | activity_monopoly_gacha_map |
| 2152 | activity_monopoly_gacha_reward |
| 2153 | activity_monopoly_gacha_dice |
| 2154 | activity_without_gacha_floor |
| 2155 | activity_soldierarm_achievement |
| 2156 | activity_floor_gacha |
| 2157 | activity_equipment_suit |
| 2158 | activity_equipment_achievement |
| 2159 | activity_festival_popwindow |
| 2160 | activity_metro_grade |
| 2161 | activity_soldierskill_achievement |
| 2162 | elite_arena_competition_stage |
| 2163 | activity_survey |
| 2164 | collction_blindbox_period |
| 2165 | activity_anni_report |
| 2166 | activity_flash_sale_raffle |
| 2167 | activity_flash_sale_virtual |
| 2168 | activity_hud_entries |
| 2169 | activity_hud_entry_style |
| 2170 | elite_arena_competition_guessing |
| 2171 | event_decroation_skill |
| 2172 | event_citybeauty_level |
| 2173 | event_citybeauty_shop |
| 2174 | event_hole_digging |
| 2175 | event_hole_type |
| 2176 | activity_fishing_game_guide_group |
| 2177 | activity_fishing_game_guide |
| 2178 | activity_monopoly_monster |
| 2179 | activity_monopoly_magic_dice |
| 2180 | activity_monopoly_monster_buff |
| 2181 | activity_monopoly_monster_skill |
| 2182 | coinpusher |
| 2183 | event_hole_digging_new |
| 2211 | push |
| 2212 | chat_system_message |
| 2213 | new_push |
| 2231 | tip |
| 2232 | tip_goto |
| 2311 | situation_smallstage |
| 2312 | situation_bigstage |
| 2313 | situation_season |
| 2314 | situation_unlock |
| 2315 | situation_task |
| 2316 | situation_rule |
| 2317 | situation_event |
| 2412 | satellite_battleground_city_category |
| 2413 | satellite_battleground_fixed_point |
| 2414 | satellite_battleground_temporary_buff |
| 2415 | satellite_battleground_union_buff_slot |
| 2416 | satellite_battleground_union_buff |
| 2417 | satellite_battleground_gather_buff |
| 2418 | satellite_battleground_my_data |
| 2419 | satellite_battleground_time_line |
| 2420 | satellite_battleground_refresh_group |
| 2421 | satellite_battleground_p_score_box |
| 2422 | satellite_battleground_union_reward |
| 2423 | satellite_battleground_p_score_rank_reward |
| 2424 | satellite_battleground_legend |
| 2425 | satellite_battleground_rule |
| 2426 | satellite_battleground_match |
| 2427 | satellite_battleground_competition_rank_reward |
| 2428 | satellite_battleground_powerstage |
| 2429 | satellite_battleground_league_level |
| 2501 | kvk_merit_quest |
| 2502 | kvk_merit_rank |
| 2503 | kvk_merit_season |
| 2504 | kvk_merit_shop |
| 2511 | kvk_situation_smallstage |
| 2512 | kvk_situation_bigstage |
| 2513 | kvk_situation_unlock |
| 2514 | kvk_situation_task |
| 2515 | kvk_situation_season |
| 2521 | kvk_search |
| 2522 | kvk_special_city_category |
| 2523 | kvk_map_fixed_point |
| 2524 | kvk_map_npc_refresh_zone |
| 2525 | kvk_territory_building |
| 2526 | kvk_map_npc_refresh_band |
| 2527 | kvk_map_unit_filter |
| 2528 | kvk_map_unit_legend |
| 2529 | kvk_union_tower_cost |
| 2530 | kvk_map_player_building |
| 2531 | kvk_radar_lv |
| 2532 | kvk_radar_task |
| 2536 | kvk_pass |
| 2537 | kvk_transport_supplies |
| 2538 | kvk_union_rss_spot |
| 2539 | kvk_rule_desc |
| 2541 | kvk_horde |
| 2542 | kvk_horde_elite |
| 2552 | kvk_plan_story |
| 2554 | kvk_score_rule_desc |
| 2563 | kvk_uw_digger |
| 2564 | kvk_uw_npc_gather |
| 2565 | kvk_uw_map_npc_refresh_band |
| 2566 | kvk_uw_map_npc_refresh_zone |
| 2567 | kvk_uw_search |
| 2568 | kvk_uw_map_unit_filter |
| 2569 | kvk_uw_map_unit_legend |
| 2570 | kvk_uw_randbuilding |
| 2571 | kvk_uw_event |
| 2572 | kvk_gve_hurdle |
| 2573 | kvk_gve_monster |
| 2576 | kvk_uw_rune |
| 2577 | kvk_uw_quest |
| 2581 | kvk_gene_research |
| 2582 | kvk_gene_culture |
| 2583 | kvk_union_research |
| 2584 | kvk_shop |
| 2585 | kvk_union_active_skill |
| 2586 | kvk_history |
| 2587 | kvk_history_detail |
| 2588 | kvk_history_reward |
| 2589 | kvk_history_player |
| 2711 | minigame_chapter |
| 2712 | minigame_level |
| 2713 | minigame_star_reward |
| 2714 | minigame_plot |
| 2801 | defence_game_chapter |
| 2802 | defence_game_level |
| 2803 | defence_game_monster |
| 2804 | defence_game_unit |
| 2805 | defence_game_starfincond |
| 2806 | defence_game_npc_troop |
| 2807 | defence_game_pass |
| 2808 | defence_game_raid |
| 2901 | train_gvg_fixed_point |
| 2902 | train_gvg_city_category |
| 2903 | train_gvg_camp_route |
| 2904 | train_gvg_score |
| 2905 | train_gvg_robot |
| 2906 | train_gvg_robot_name |
| 2910 | train_gvg_season |
| 2911 | train_gvg_grade |
| 2912 | train_gvg_season_kvk |
| 2913 | train_gvg_season_kvk2 |
| 2914 | kvk3_train_gvg_season |
| 2915 | train_gvg_season_kvk4 |
| 2916 | train_gvg_season_kvk5 |
| 2921 | train_gvg_personal_rank |
| 2922 | train_gvg_union_rank |
| 2931 | train_gvg_plus_grade |
| 2932 | train_gvg_plus_task |
| 2933 | train_gvg_plus_leader_skill |
| 2934 | train_gvg_plus_match |
| 2935 | train_gvg_plus_speed_hp |
| 2941 | train_gvg_plus_fixed_point |
| 2942 | train_gvg_plus_city_category |
| 2943 | train_gvg_plus_camp_route |
| 2951 | train_gvg_personal_rank_kvk4 |
| 2952 | train_gvg_plus_grade_kvk4 |
| 2953 | train_gvg_personal_rank_kvk5 |
| 2954 | train_gvg_plus_grade_kvk5 |
| 3001 | takeover_card_hero_data |
| 3002 | takeover_card_hero_star_level |
| 3003 | takeover_card_hero_skill |
| 3004 | takeover_card_level |
| 3005 | takeover_card_boss_level |
| 3006 | takeover_card_const_config |
| 3007 | takeover_card_npc |
| 3008 | takeover_card_takeover_skill |
| 3011 | monkey_takeover_level |
| 3012 | monkey_takeover_tower |
| 3013 | monkey_takeover_tower_category |
| 3014 | monkey_takeover_level_group |
| 3014 | monkey_takeover_level_group_mj1 |
| 3014 | monkey_takeover_level_group_mj2 |
| 3014 | monkey_takeover_level_group_mj3 |
| 3014 | monkey_takeover_level_group_mj4 |
| 3014 | monkey_takeover_level_group_mj5 |
| 3014 | monkey_takeover_level_group_mj6 |
| 3014 | monkey_takeover_level_group_mj9 |
| 3015 | monkey_takeover_ai |
| 3016 | monkey_takeover_skill |
| 3017 | monkey_takeover_teach |
| 3018 | monkey_takeover_race_stage |
| 3019 | monkey_takeover_race_robot |
| 3021 | city_defense_npc |
| 3022 | city_defense_bullet |
| 3023 | city_defense_npc_group |
| 3024 | city_defense_level |
| 3025 | city_defense_skill |
| 3031 | rope_balls_level |
| 3036 | monkey_io_npc |
| 3037 | monkey_io_level |
| 3038 | monkey_io_ai |
| 3039 | monkey_io_props |
| 3040 | monkey_io_skill |
| 3041 | monkey_io_props_drop |
| 3042 | monkey_io_area |
| 3070 | pvp_robot |
| 3080 | evolved_ape_player_lvl |
| 3081 | evolved_ape_model |
| 3082 | evolved_ape_skill |
| 3084 | evolved_ape_level |
| 3085 | evolved_ape_npc_refresh |
| 3086 | evolved_ape_npc_ai |
| 3087 | evolved_ape_const_config |
| 3088 | evolved_ape_effect |
| 3091 | fte_stage |
| 3101 | boss_rush_difficulty |
| 3102 | boss_rush_room |
| 3103 | boss_rush_room_effect |
| 3104 | boss_rush_room_design |
| 3105 | boss_rush_monster |
| 3106 | boss_rush_npc_troop |
| 3107 | boss_rush_drop |
| 3108 | boss_rush_challenge_element |
| 3109 | boss_rush_quest |
| 3110 | boss_rush_map_design |
| 3111 | boss_rush_heal_effect |
| 3112 | boss_rush_random_event |
| 3113 | boss_rush_random_event_option |
| 3114 | boss_rush_skill_contribution |
| 3201 | kvk2_special_city_category |
| 3202 | kvk2_territory_building |
| 3203 | kvk2_map_fixed_point |
| 3204 | kvk2_map_npc_refresh_band |
| 3205 | kvk2_pass |
| 3206 | kvk2_search |
| 3207 | kvk2_map_unit_filter |
| 3208 | kvk2_map_unit_legend |
| 3209 | kvk2_map_npc_refresh_zone |
| 3210 | kvk2_battle_area_config |
| 3211 | kvk2_battle_area_core_center |
| 3220 | kvk2_task_group |
| 3221 | kvk2_task_choose |
| 3222 | kvk2_guild_task_reward |
| 3223 | kvk2_score_rule_desc |
| 3224 | kvk2_plan_story |
| 3225 | kvk2_radar_lv |
| 3226 | kvk2_radar_task |
| 3227 | kvk2_rule_desc |
| 3230 | kvk2_situation_season |
| 3231 | kvk2_situation_unlock |
| 3232 | kvk2_situation_bigstage |
| 3233 | kvk2_situation_smallstage |
| 3234 | kvk2_situation_task |
| 3240 | kvk2_union_tower_cost |
| 3241 | kvk2_map_player_building |
| 3242 | kvk2_transport_supplies |
| 3243 | kvk2_gene_research |
| 3244 | kvk2_gene_culture |
| 3245 | kvk2_union_research |
| 3246 | kvk2_merit_quest |
| 3247 | kvk2_merit_rank |
| 3248 | kvk2_merit_season |
| 3249 | kvk2_union_rss_spot |
| 3250 | kvk2_gve_hurdle |
| 3251 | kvk2_gve_monster |
| 3252 | kvk2_merit_shop |
| 3253 | kvk2_union_active_skill |
| 3264 | kvk2_uw_npc_gather |
| 3265 | kvk2_uw_map_npc_refresh_band |
| 3266 | kvk2_uw_map_npc_refresh_zone |
| 3267 | kvk2_uw_search |
| 3268 | kvk2_uw_map_unit_filter |
| 3269 | kvk2_uw_map_unit_legend |
| 3270 | kvk2_uw_randbuilding |
| 3271 | kvk2_uw_event |
| 3277 | kvk2_uw_quest |
| 3301 | team_boss_difficulty |
| 3302 | team_boss_difficulty_wave |
| 3303 | team_boss_event |
| 3304 | team_boss_npc_troop |
| 3305 | team_boss_rank_rewards |
| 3306 | team_boss_boss_status |
| 3307 | team_boss_boss_skill |
| 3308 | team_boss_skill_effect |
| 3309 | team_boss_map_unit |
| 3310 | team_boss_damage_reward |
| 3311 | team_boss_boss_display |
| 3312 | team_boss_skill_render |
| 3313 | team_boss_boss_buff_show |
| 3314 | team_boss_dynamic_difficulty |
| 3401 | soldier_special_skill |
| 3402 | soldier_skill |
| 3403 | soldier_skill_effect |
| 3510 | metro_minigame_activity_group |
| 3511 | metro_minigame_employ_level |
| 3512 | metro_minigame_employ_times |
| 3513 | metro_minigame_map_units |
| 3514 | metro_minigame_rock_drop |
| 3515 | metro_minigame_production |
| 3516 | metro_minigame_level |
| 3517 | metro_minigame_level_group |
| 3518 | metro_minigame_research |
| 3521 | metro_minigame_buff |
| 3522 | metro_minigame_buff_category |
| 3523 | metro_minigame_buff_source |
| 3524 | metro_minigame_buff_property |
| 3525 | metro_minigame_hero_data |
| 3526 | metro_minigame_hero_level |
| 3527 | metro_minigame_hero_skill |
| 3528 | metro_minigame_shooting_level |
| 3529 | metro_minigame_shooting_npc |
| 3530 | metro_minigame_shooting_weapon |
| 3531 | metro_minigame_shooting_skill |
| 3532 | shooting_teach |
| 3533 | metro_minigame_hero_worker_level |
| 3534 | metro_minigame_hero_worker_power |
| 3535 | metro_minigame_hero_worker_skill |
| 3540 | kvk_uw_metro_minigame_research |
| 3541 | metro_minigame_dragon_rock |
| 3542 | metro_minigame_bargain_iap_rock |
| 3601 | dungeon_warfare_event_trigger |
| 3602 | dungeon_warfare_event |
| 3603 | dungeon_warfare_building_map |
| 3604 | dungeon_warfare_building |
| 3605 | dungeon_warfare_mark |
| 3606 | dungeon_warfare_npc |
| 3607 | dungeon_warfare_ai |
| 3608 | dungeon_warfare_arena_score |
| 3609 | dungeon_warfare_task |
| 3610 | dungeon_warfare_rule_desc |
| 3611 | dungeon_warfare_plus_rule_desc |
| 3612 | dungeon_warfare_grade |
| 3701 | oap_config |
| 3702 | oap_template |
| 3703 | oap_recharge |
| 3801 | kvk3_special_city_category |
| 3802 | kvk3_territory_building |
| 3803 | kvk3_map_fixed_point |
| 3804 | kvk3_map_npc_refresh_band |
| 3805 | kvk3_pass |
| 3806 | kvk3_horde |
| 3807 | kvk3_map_npc_refresh_zone |
| 3808 | kvk3_search |
| 3809 | kvk3_map_unit_filter |
| 3810 | kvk3_map_unit_legend |
| 3811 | kvk3_plan_story |
| 3812 | kvk3_battle_area_config |
| 3813 | kvk3_battle_area_core_center |
| 3814 | kvk3_recommend_play |
| 3815 | kvk3_recommend_play_rule_desc |
| 3820 | kvk3_hero_cabin |
| 3821 | kvk3_hero_cabin_task |
| 3822 | kvk3_hero_cabin_buff |
| 3823 | kvk3_score_rule_desc |
| 3824 | kvk3_rule_desc |
| 3825 | kvk3_hero_cabin_skill |
| 3826 | kvk3_hero_cabin_skill_effect |
| 3830 | kvk3_situation_season |
| 3831 | kvk3_situation_unlock |
| 3832 | kvk3_situation_bigstage |
| 3833 | kvk3_situation_smallstage |
| 3834 | kvk3_situation_task |
| 3835 | kvk3_quest |
| 3840 | kvk3_union_tower_cost |
| 3841 | kvk3_map_player_building |
| 3842 | kvk3_transport_supplies |
| 3843 | kvk3_gene_research |
| 3844 | kvk3_gene_culture |
| 3845 | kvk3_union_research |
| 3846 | kvk3_merit_quest |
| 3847 | kvk3_merit_rank |
| 3848 | kvk3_merit_season |
| 3849 | kvk3_union_rss_spot |
| 3850 | kvk3_gve_hurdle |
| 3851 | kvk3_gve_monster |
| 3852 | kvk3_merit_shop |
| 3853 | kvk3_union_active_skill |
| 3854 | kvk3_horde_donation |
| 3855 | kvk3_horde_donation_rank |
| 3856 | kvk3_horde_research |
| 3857 | kvk3_horde_active_skill |
| 3864 | kvk3_uw_npc_gather |
| 3865 | kvk3_uw_map_npc_refresh_band |
| 3866 | kvk3_uw_map_npc_refresh_zone |
| 3867 | kvk3_uw_search |
| 3868 | kvk3_uw_map_unit_filter |
| 3869 | kvk3_uw_map_unit_legend |
| 3870 | kvk3_uw_randbuilding |
| 3871 | kvk3_uw_event |
| 3872 | kvk3_hero_cabin_skill_pool |
| 3873 | kvk3_uw_quest |
| 3901 | arm_expedition_level |
| 3902 | arm_expedition_store |
| 3903 | arm_expedition_hud |
| 4001 | mecha_data |
| 4002 | mecha_level |
| 4003 | mecha_skill |
| 4004 | mecha_skill_effect |
| 4005 | mecha_unlock_quest_group |
| 4006 | mecha_unlock_quest |
| 4007 | mecha_free_attr |
| 4008 | mecha_inclined |
| 4009 | mecha_soldier_level |
| 4010 | mecha_skin |
| 4011 | mecha_colour |
| 4012 | mecha_driver_data |
| 4013 | mecha_driver_level |
| 4014 | mecha_driver_skill |
| 4015 | mecha_driver_slot |
| 4016 | mecha_driver_skill_effect |
| 4017 | mecha_break_level |
| 4018 | mecha_durability_level |
| 4101 | soldier_bg_fixed_point |
| 4102 | soldier_bg_city_category |
| 4103 | soldier_bg_robot |
| 4104 | soldier_bg_grade |
| 4105 | soldier_bg_personal_rank |
| 4106 | soldier_bg_union_rank |
| 4107 | soldier_bg_season |
| 4108 | soldier_bg_hero |
| 4109 | soldier_bg_task |
| 4110 | soldier_bg_npc |
| 4111 | soldier_bg_rule_desc |
| 4112 | soldier_bg_counter |
| 4113 | soldier_bg_npc_small |
| 4114 | soldier_bg_trap |
| 4201 | mech_bg_fixed_point |
| 4202 | mech_bg_city_category |
| 4203 | mech_bg_level |
| 4204 | mech_bg_rule_desc |
| 4205 | mech_bg_grade |
| 4206 | mech_bg_personal_rank |
| 4207 | mech_bg_season |
| 4208 | mech_bg_npc |
| 4209 | mech_bg_npc_small |
| 4210 | mech_bg_robot |
| 4301 | racegame_level |
| 4302 | racegame_item |
| 4303 | racegame_weapon |
| 4304 | racegame_car |
| 4305 | racegame_skill |
| 4306 | racegame_effect |
| 4308 | racegame_boss |
| 4309 | racegame_const_config |
| 4310 | racegame_hero_data |
| 4311 | racegame_hero_star_level |
| 4312 | racegame_hero_skill |
| 4400 | miniwar_transport_mining |
| 4401 | miniwar_transport_end |
| 4402 | miniwar_map_fixed_point |
| 4403 | miniwar_special_city_category |
| 4404 | miniwar_map_npc_refresh_zone |
| 4405 | miniwar_map_npc_refresh_band |
| 4406 | miniwar_transport_supplies |
| 4407 | miniwar_horde |
| 4408 | miniwar_territory_building |
| 4409 | miniwar_quest |
| 4410 | miniwar_pass |
| 4411 | miniwar_rule_desc |
| 4412 | miniwar_search |
| 4413 | miniwar_map_unit_filter |
| 4501 | kvk4_special_city_category |
| 4502 | kvk4_territory_building |
| 4503 | kvk4_map_fixed_point |
| 4504 | kvk4_map_npc_refresh_band |
| 4505 | kvk4_pass |
| 4506 | kvk4_search |
| 4507 | kvk4_map_unit_filter |
| 4508 | kvk4_map_unit_legend |
| 4509 | kvk4_map_npc_refresh_zone |
| 4510 | kvk4_battle_area_config |
| 4511 | kvk4_battle_area_core_center |
| 4512 | kvk4_rule_desc |
| 4513 | kvk4_recommend_play |
| 4515 | kvk4_score_rule_desc |
| 4516 | kvk4_plan_story |
| 4517 | kvk4_horde |
| 4519 | kvk4_temperature_refresh_zone |
| 4520 | kvk4_temperature |
| 4521 | kvk4_individual_mecha_center_core |
| 4522 | kvk4_temperature_skill |
| 4523 | kvk4_temperature_skill_effect |
| 4524 | kvk4_individual_mecha_attr |
| 4525 | kvk4_individual_mecha_talent |
| 4526 | kvk4_build_skill |
| 4530 | kvk4_situation_season |
| 4531 | kvk4_situation_unlock |

> 如以上查不到，说明是新增表，用 gws 查询索引表：
> ```powershell
> $env:GOOGLE_WORKSPACE_PROJECT_ID = 'calm-repeater-489707-n1'
> gws sheets spreadsheets values get --params '{"spreadsheetId": "1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c", "range": "fw_gsheet_config!A1:F600"}'
> ```

## SheetID 完整索引

包含每张表的 Google Sheet ID，见 `references/table_index.md`。

## 回复格式（⚠️ 每次提交后必须输出，不得省略）
```
✅ <编号>(<页签>) → <分支> 提交成功
commit: [配置更新]<页签>-<分支>-<五字>
📝 +X/-Y行：
  - ID <行ID>：<字段名> 从「旧值摘要」→「新值摘要」
  - ID <行ID>：新增行，<简短描述>
  - ...（每条变动单独一行，自然语言，不贴原始 TSV）
```

**示例**：
```
✅ 2115(activity_task) → bugfix 提交成功
commit: [配置更新]activity_task-bugfix-前置条件修改
📝 +4/-4行：
  - ID 211587297：fincond 新增前置条件 actvtask 211587370 ≥1
  - ID 211587298：fincond 新增前置条件 actvtask 211587371 ≥1
  - ID 211587299：fincond 新增前置条件 actvtask 211587372 ≥1
  - ID 211587300：fincond 新增前置条件 actvtask 211587373 ≥1
```
