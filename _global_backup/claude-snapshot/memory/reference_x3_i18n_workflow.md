---
name: x3-i18n
description: X3 配置中 TXT_ 字段从配置写入→扫描→翻译→Text.xlsx/GSheet 全流程，含 i18n key 命名规则和触发占位符现象
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9fa379f1-8095-4bed-9a37-401c299ba495
---

## 已接入 quality-gate 自动验收（i18n 类）
跑 i18n/生成多语言**开工时建标记** `~/.claude/.pending_verify/<任务>.json` = `{"task":"<名>","type":"i18n","text_table":"<Text表ID或路径>","data_dir":"<跑CompositeI18n的data目录>","status":"pending"}`；
**收工被拦时**派 `task-checker`(type=i18n) 跑验收（清单见 `C:\ADHD_agent\.claude\quality-gate\i18n-checklist.md`：key命名规范/`_backup_*.xlsx`未移出 等客观项 + 重复key warn）；全过删标记，有 blocker 列给用户定。

## 客户端如何读 i18n（来源：CfgProtoTextEx.cs）

配置表（TaskType.xlsx 等）里的 EventTxt/Name/Desc 等 **TXT_** 字段，**配置表里写的中文只是母版**——运行时客户端通过 i18n key 查多语言字典。

i18n key 命名规则（在 `Tools/table_exporter/CfgProtoTextEx.cs` 生成）：
- `TaskType.EventTxt` → `TXT_TaskType_EventTxt_{ID}`
- `TaskType.EventTxt2` → `TXT_TaskType_EventTxt2_{ID}`
- 其他表同模式：`TXT_{TableName}_{FieldName}_{ID}`

### 失败现象

字典查不到 key 时客户端显示占位：`{key}_is_null`，例如 `task_type:902_event_text_is_null`。**触发原因**：i18n 多语言表（`data/i18n/Text.xlsx`）里没有这个 key 的翻译。

## 完整工作流（必走 8 步）

> ⚠️ **导入只认 tsv**（2026-05-29 迁移，见 [[reference_x3_tsv_export_migration]]）。i18n 扫描工具链是**唯一**仍读/写 xlsx 的场景，但导表读的是 `tsv/i18n/Text__Text.tsv`——所以改完 Text.xlsx **必须重生成那一个 tsv 并提交**，否则翻译不生效（X3NEW-734 踩过：翻译进了 xlsx 没进 tsv，俄服仍显中文）。也可跳过 xlsx 直接改 tsv 语言列。

| 步 | 动作 | 工具 |
|----|------|------|
| 1 | 改配置表 TXT_ 字段写中文母版 | tsv_edit.py（或 xlsx，仅扫描需要时）|
| 2 | 跑 CompositeI18n 扫描（monkey patch updateFile） | `Tools/gen_i18n/gen_i18n_imp.py` |
| 3 | 检查 Text.xlsx 状态：新文本=`新增`，CN 变了=`已修改` | openpyxl |
| 4 | AI 翻译 10 语言（参考同表同类 key 的历史翻译做术语对齐） | — |
| 5 | 写回 Text.xlsx 对应行，status 改 `AI` | openpyxl |
| 6 | 写 Google Sheet 当前季度 sheet（当前 `2025Q4`） | gws CLI / Python+node |
| 7 | **重生成 tsv**：`python scripts/xlsx_to_tsv.py --files data/i18n/Text.xlsx` | xlsx_to_tsv.py |
| 8 | git commit `data/i18n/Text.xlsx` + **`tsv/i18n/Text__Text.tsv`** 一起 push → 导表 | git |

skill 入口：`Skill: x3-translation-automatic`

## 关键坑 / 实战补充

### 1. CompositeI18n monkey patch
扫描脚本内部调 `updateFile()` 想 svn update，git 仓库下会失败。**调用前必须 patch**：
```python
import gen_i18n_imp
gen_i18n_imp.updateFile = lambda path: ('', '')
```

### 2. gws.js 入口路径
skill 文档写的 `run.js` 不存在，**实际是 `run-gws.js`**：
```python
GWS_JS = r'C:\Users\linkang\AppData\Roaming\npm\node_modules\@googleworkspace\cli\run-gws.js'
```

### 3. Key 合并机制
扫描器会把 CN 内容相同的多个 key 合并到 Text.xlsx 同一行，存为 `TXT_A|TXT_B|TXT_C` 形式。查找定向 key 时用 `marker in key_str` 而非 `==`。例：902 的 EventTxt 与 EventTxt2 CN 一样 → 合并为 `TXT_TaskType_EventTxt2_902|TXT_TaskType_EventTxt_902`。

### 4. 复用 vs 差异化文案
- 默认：通用类 TaskType（如 902 通用累充任务）EventTxt **可复用同类 ID 的文案**（直接抄 900）→ 扫描器合并到同 key 行，无需新增翻译。
- 差异化：单一活动想显示自己文案 → 在 `ActvTask.CustomTaskText` 填，不要去改 TaskType.EventTxt。

### 5. Text.xlsx 性能
~2 万行 ~7 MB。完整 load_workbook 7 秒、save 7 秒。批量写入时一次 load 一次 save，不要反复读写。

### 6. 翻译术语对齐
翻译前在 Text.xlsx 搜同道具/同任务结构的旧翻译做基线，**不要直接机器翻**。
- "充值积分" → `purchase points / 충전 포인트 / очков покупок`（来源：900）
- "礼包" → `pack / paquete / lot / paket / Paket / 패키지 / пакет`（来源：901）
- "活动" → `event`（多语言项目标准）

### 7. `_backup_*.xlsx` 污染扫描器（重坑）

`gen_i18n_imp.py` line 73-78 只跳 `~$` 临时文件，**不跳 `_backup_` 前缀**。如果 `data/` 目录有 `_backup_Text_*.xlsx`（Text 主表的本地备份）或类似 i18n 主表副本，扫描器会把它当成普通配置表扫，i18n 主表的合并 key (`TXT_A|...|TXT_Z`) 被读成 row 4 annotation，造成同 key 不同中文冲突 → 在 `addKeyAndChinese` 第 185 行 raise。

**症状**：扫描报错形如
```
key = TXT_Text_TXT_IntelligenceTask_TXTTitle_xxx|...|TXT_TaskType_EventTxt_NNN
chinese = TXT_TaskType_EventTxt2_XXX|TXT_TaskType_EventTxt_XXX
Key2ChineseDict[key] = <乱码>
```
key 长得越离谱（含 `|` 拼接 + `TXT_Text_` 双 TXT 前缀），越说明是 i18n 主表自指污染。

**临时解法**：把 `data/_backup_*.xlsx` 全部送回收站或移到 `data/_backups/` 子目录（扫描器用 `os.listdir` 不递归）。`_backup_Text_*` 是核心污染源；其他 `_backup_ActvScore_*` / `_backup_Rank_*` 等是真正配置表的备份，扫描不会爆——但留着也容易混淆，统一移走更干净。

**长期解法**：PR 改 `Tools/gen_i18n/gen_i18n_imp.py` line ~76：
```python
if file.startswith('_backup'):
    continue
```

## Text.xlsx 表结构 & 状态列（2026-05-29 实测）

`data/i18n/Text.xlsx` 唯一 sheet 名就叫 `Text`（导表生成 `tsv/i18n/Text__Text.tsv`）。列布局（openpyxl 1-based）：

| col | 含义 | col | 含义 |
|-----|------|-----|------|
| 1 | key（`TXT_{Table}_{Field}_{ID}`，可能 `\|` 拼接合并） | 9 | de |
| 2 | **状态列** | 10 | kr |
| 3 | optional（多为空） | 11 | zh（繁体） |
| 4 | cn（简体母版） | 12 | ru |
| 5 | en | 13 | ua |
| 6 | sp | 14 | jp |
| 7 | fr | 15-18 | 校对子标记（已校对行填 `已校对`） |
| 8 | id | | |

**10 个翻译语言** = en/sp/fr/id/de/kr/zh/ru/ua/jp（col 5-14），cn 是母版不算翻译。

### 状态列语义（col 2）
- `新增` = 扫描器收录了 key、只写了 cn 母版，**翻译还没补** → 游戏内显示中文母版。
- `AI` = AI 翻译已填（写回时用这个）。
- `已校对` = 人工校对过。

### 「新增任务漏翻」故障模式（高频）
新增 TaskType/ActvScoreTask 等带 TXT_ 字段的任务后，只 commit 了配置表（如 ActvScore.xlsx），**没补 Text.xlsx 翻译** → CompositeI18n 扫描把 key 加进 Text.xlsx 标 `新增`，但 10 语言全空 → 客户端查不到、回退显 cn 母版。
- **症状**：活动面板里个别行是中文、其余正常翻译。
- **定位**：Text.xlsx 按 `状态==新增` 或「col 5-14 全空」过滤即漏翻行。
- **修复**：找**同结构已翻译兄弟 key**抄术语（见下表），填 col 5-14、状态改 `AI`，commit Text.xlsx → push → jolt 导表。改已存在行的空单元格，openpyxl 直接 load/save 安全（Text.xlsx 非公式 Table，~7s load/~7s save）。

### 信物/稀有度术语对齐表（最佳酒馆等通用）
| 中文 | en | ru | sp | fr | de | kr | jp |
|------|----|----|----|----|----|----|----|
| 信物(token) | token | жетон | ficha | jeton | Token | 증표 | 証 |
| 稀有 | rare | редкий | rara | rare | selten | 희귀 | レア |
| 史诗 | epic | эпический | épica | épique | episch | 영웅급 | エピック |
| 传奇 | legendary | легендарный | legendaria | légendaire | legendär | 전설급 | レジェンダリー |
| 兑换(动作) | exchange | для обмена | canjear | échanger | eintauschen | 교환 | 交換 |

## 实战案例

| 任务 | Commit |
|------|--------|
| 902 EventTxt 从"累计获得活动充值积分{0}"改"通过节日礼包获取充值积分{0}" + 10 语言 | `3b6d072` |
| RuleTips 拆分 15013/15014 + ActvOnline 100594/595 引用切换 + 10 语言（含 backup 污染绕过：手动 append） | `88ca9da` |
| 删除 `_backup_Text_X3NEW-738_and_735.xlsx`（送回收站）让扫描恢复正常 | 本地操作，未 commit |
| X3NEW-734 收尾：734 新增 ActvScoreTask 208/209/213(稀有/史诗/传奇信物兑换)只有 cn、10 语言全空，俄服显中文。对齐升星兄弟 201/202/203 补全 | `5e738e7`(master_fix_fes_pack) |

## 相关

- 触发 skill：`x3-translation-automatic`
- 配套 push 自动跑 jolt 导表：[[workflow_x3_auto_jolt_export]]
- 配置改动走 tsv 不碰 xlsx：[[reference_x3_tsv_export_migration]]
- TaskType ParamCount 不在 Excel：[[reference_x3_recharge_isolation]]
