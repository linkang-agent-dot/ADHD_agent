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
- **活动/礼包/规则常用(2026-06-17世界杯竞猜反复踩4轮)**：活动标题/描述=`TXT_ActvOnline_ActvName_{活动ID}`/`TXT_ActvOnline_ActvDesc_{活动ID}`；礼包名/描述=`TXT_Pack_Name_{礼包ID}`/`TXT_Pack_Desc_{礼包ID}`；规则弹窗=`TXT_RuleTips_Tab/Title/Content_{规则ID}`。**界面文本全空的头号嫌疑=没建对应自动key**(配置表ActvOnline col2/col3、Pack col35/col36、RuleTips的Tab/Title/Content列里填的字面值/key 客户端统统不读,只是编辑器备注)→去 `CfgProtoTextEx.cs` 搜该字段getter确认key名→Text表建。想"多包共享一个文案key"做不到(getter拼死per-ID),除非改客户端读shared key那行。

### 失败现象

字典查不到 key 时客户端显示占位：`{key}_is_null`，例如 `task_type:902_event_text_is_null`。**触发原因**：i18n 多语言表（`data/i18n/Text.xlsx`）里没有这个 key 的翻译。

## ⚠️ Text 表实际是 16 语言（2026-06-17 实测，skill 文档写的 10 种已过时）
`Text__Text.tsv`/`Text.xlsx` 列序（0-indexed）：col0=key(同CN多key用`|`合并) / col1=状态(AI/新增/已修改/已校对) / col2=中文修改备份 / **col3~18=16语言** / col19-22空 / col23-26=各语种校对情况。
16 语言列序：`col3 cn, 4 en, 5 sp, 6 fr, 7 id, 8 de, 9 kr, 10 zh(繁), 11 ru, 12 ua, 13 jp, 14 it, 15 pl, 16 po(pt), 17 tr, 18 th`。补一条新文案要把 col3-18 全填齐（对齐其它 AI 行的填法），col19+ 留空。
**术语锚**：「周卡」X3 统一译 **Weekly Pass**(非 Weekly Card)、繁中=**週卡**；要对齐术语就先拉个已校对的同类 key 全语言行抄句式(如 `TXT_Pack_Name_30002 加速周卡`=Speedup Weekly Pass/加速週卡/加速週間パス…)。

## 缺失 key 在共享分支上「精准补 tsv N 行」优于跑全局扫描（2026-06-17 周卡4名实测）
新 key 在 Text 表完全不存在(且 CN 各异无需合并)时，**别在 dev_festival 这种多人分支上跑全局 CompositeI18n**——它会把别人所有 pending 待译文本一并卷进你的提交。改走精准追加：直接往 `Text__Text.tsv` append N 行(col0=key/col1=AI/col2=空/col3-18=16语言)，`git commit` 时本地 pre-commit hook 会 `direction=tsv->xlsx` 把新行同步进 Text.xlsx(实测 21k 行表加 4 行 mismatch=0 一步过，Text 表纯字符串无公式，openpyxl 重存无缓存丢失风险)。前提：key 形如 `TXT_Pack_Name_<id>` 必须与 `CfgProtoTextEx.cs` getter 拼出的名完全一致(见上节)。

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
> ⚠️**更新(2026-06-15)**：tsv 真源 `tsv/i18n/Text__Text.tsv` 实测**15 个语言列**=en/sp/fr/id/de/kr/zh/ru/ua/jp/**it/pl/po/tr/th**(col5-19,意/波兰/葡/土/泰)，列序: col1=key/col2=状态/col3=opt/col4=cn/col5-19=15语。补新行要填全15语,只填10语会缺意波葡土泰。(xlsx 列布局可能与tsv不同,以tsv为准)

### 状态列语义（col 2）
- `新增` = 扫描器收录了 key、只写了 cn 母版，**翻译还没补** → 游戏内显示中文母版。
- `AI` = AI 翻译已填（写回时用这个）。
- `已校对` = 人工校对过。

### 「换皮 clone 漏建 key」故障模式（2026-06-23 深海节实证·与漏翻不同）
**漏翻**=key 建了（扫描器收录）但语言列空→显 cn 母版（中文）；**漏建 key**=换皮 clone 新建活动/礼包/道具的**新 id，i18n key 根本没建**→客户端查不到→标题/名称显**空白**（或 `{key}_is_null`）。换皮最易漏：客户端不读配置表的 cn（只是母版），读 `TXT_{Table}_{Field}_{新id}`；搬配置时只复制配置行没建 i18n key；**导表不校验 key 存在**（导表绿但标题掉）。**复用活动也要建**（新 id≠模板 id，key 不继承）。深海一次扫出缺 22 条（6 活动标题+描述/4 礼包名+描述/2 道具名）。**换皮收尾必做 i18n 审计**：列全换皮 id → 扫 `TXT_{Table}_{Field}_{新id}` 是否在 Text 表 → 缺的按新 id 建（复用同 cn 现成译文）。详见 [[x3]] 深海换皮清单「四之补」。

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

## ⚠️ 换皮 clone i18n 的"多语言残留"坑(2026-06-17 世界杯连锁礼包名实证)
clone 节日活动时若用"字符串替换"换 i18n(如 尼罗→世界杯),**只在 cn/en 上替有效是不够的**：Text 每个 key 的**16语言列各有该节日名的本地化译法**(如"尼罗之辉"=sp"Resplandor del Nilo"/fr"Radiance du Nil"/jp"ナイルの輝き"/**繁中"尼羅之輝"(繁体字!)**…),你的 swap 只匹配了简体"尼罗之辉"和英文"Nile"→**其余14语言(含繁中,因简繁字不同)全残留原节日名**。游戏按玩家语言读→非简中/英玩家看到旧节日名。
- **症状**:配置/cn 都对,但用户(或某语言客户端)说"还叫旧节日名"。排查=`csv` 读该 key 全语言列,扫各语言的节日译法残留(英Nile/西Nilo/繁尼羅/日ナイル等)。
- **修法**:别靠 swap,**逐语言重新翻译**(每语言用该节日的正确本地化译法)。范式脚本 build_wc_i18n_translate.py(唯一文本→15语言表)。clone 时最稳=直接给目标节日的16语言译法,不做源节日文本的字符串替换。

## ⚠️ x3-translation-automatic skill 假设已过时(2026-06-17 实证,翻译少量已知key时绕开它)
该 skill(gongliang)按**旧环境**写,三处对不上当前,改少量已知 key 时**别套它的 xlsx 流程,直接翻 tsv**：
- **路径**:skill 默认 `E:\x3gdconfig`,实际 = `C:\x3\gdconfig`。
- **语言数**:skill 只管 **10 语言**(到 col13 UA),当前 Text 表实际 **16 语言**(cn + en/sp/fr/id/de/kr/zh/ru/ua/jp/it/pl/po/tr/th)。
- **真源**:skill 走 `data/i18n/Text.xlsx`(CompositeI18n 扫描),当前**导入只认 tsv**。
- **Text tsv 列布局(0-indexed,权威)**:`0=key 1=校对结果(状态AI) 2=中文修改备份 3=cn 4=en 5=sp 6=fr 7=id 8=de 9=kr 10=zh(繁) 11=ru 12=ua 13=jp 14=it 15=pl 16=po 17=tr 18=th`。
- **少量已知 key 翻译法(推荐)**:不跑扫描,python 直接改 `tsv/i18n/Text__Text.tsv` 这些 key 的 col5-18(en已有则校),状态保持 AI,提交走钩子同步 Text.xlsx(见 [[reference_x3_tsv_export_migration]])。范式脚本 `C:\Users\linkang\build_wc_i18n_translate.py`(唯一文本→15语言表+key→cn映射,保留【】/{0}标签,繁中=简繁转换)。skill 的"AI自译+比对历史保术语"原则仍照用。
- skill 适合**全表扫描批量**新增 key;手上就几个已知 key 直接翻 tsv 更快更稳。

## ⚙️ 节日大批量 i18n 补译工具链(2026-06-17 世界杯 183→0缺口实证, 可复用)
节日活动(尤其含**N国队伍**的世界杯/奥运类)i18n 动辄 100~400 条缺口,纯手翻不现实。固化工具在 `C:\Users\linkang\`(数据确定性,备份被 git-clean 也能重生):
- `apply_wc_i18n.py` — 主应用脚本,4级填充(优先级递进):①Title合并行**拆分**(某key混在多key合并行、需独立不同译时,从合并key摘出+新增独立行)②单条 IND 按完整key填 ③**模板族**(头像框/表情/Cfg名等同句式)按 cn **正则解析国家名→查表填** ④**CN-MAP**(同cn重复行,如竞猜分场次73个活动都是"胜负预言·32强"等9个去重cn→按cn值复用译文)。
- `wc_country_table.json` — **48国×16语种**标准译名表(世界杯队名),复用核心资产。坑:①刚果民主共和国(DR Congo)≠刚果(Congo)②简称别名(沙特↔沙特阿拉伯)③**表情和头像框国家顺序可能不一致→必须从每行cn解析国家,不能按ID索引位置硬套**。
- `wc_individual_translated.json`/`wc_supplement.json` — 单条/新增唯一文本(规则正文等)16语译文。
- **★fill-missing 模式(should_fill)**:只在 **空 / 中文泄漏(列值==cn) / 旧节日残留(天马等)** 时填,**保留并发 agent 已翻好的真译文不覆盖**——多 agent 并行改同一 Text 表时安全。
- **★i18n 审计必查三类**(`audit_wc_i18n.py`):缺语种(空) + **中文泄漏**(en/其他列含汉字=没翻,**en列=中文是最易漏判的"伪完整"**) + **英文泄漏**(2026-06-24世界杯抽奖券1146实证:cn之外14语列**全等于en英文原文**=只翻了中英、其余照抄英文,空缺/中文泄漏审计都查不出,看着"15语已填"其实伪完整)。**坑**:①jp(日语汉字)/zh(繁中)是中文检测假阳性必须排除;②英文泄漏审计必须排"符号/数字/短码"假阳性(`21倍=21x`/`VIP{0}`/`-40%`/罗马数字/语言选择器Français…本就各语言相同)→只认**成句en**(含≥6字母且有空格或长>12)且≥多数列==en。圈定 = 新增ID段 ∪ 主题词 ∪ **key前缀(如 `_WC_`)**(cn像"胜负预言·32强"无主题词、key又不在ID段,只靠主题词会漏)。修英文泄漏=从**同义已正确翻译的兄弟行**(如券名去`ActvDesc`里摘【…】现成逐语言译名)抄术语。
- 用法:`python apply_wc_i18n.py <目标tsv>`(默认作用备份副本验证→0缺口后再传live)。

## ⛔ 提交前泄漏审计脚本(2026-06-24 固化, 替代肉眼检查)
**起因**:世界杯抽奖券1146(名+描述14语全照抄英文)、深海节16行(13语照抄英文+zh未转繁)都是"伪完整"——单元格非空、看着15语已填,实际只中英。空缺审计和肉眼都漏判,所以做成**确定性脚本**:
- 脚本:`C:\Users\linkang\.claude\skills\x3-translation-automatic\scripts\i18n_leak_audit.py`,退出码0/1(供hook/CI)。
- 三类 block:`EN_LEAK`(cn之外列==en英文原文) / `CJK_LEAK`(非中日列含汉字,已排zh繁/jp假阳性) / `EMPTY`(空缺);`ZH_RAW`(warn)=zh==cn简体疑未转繁。
- 自动排假阳性:符号/数字/标签/百分比/`union_language_`语言选择器/`ServerName_`等"各语言本就相同"的;EN_LEAK只判"成句en"(≥6字母+有空格或长>12)。
- 用法:`--changed`(只审 git diff HEAD 改动行,**按行号位置对比**绕开空key/重复key塌缩坑,行数变了退回全表) / `--grep <词>` / `--prefix <key前缀>`。提交前必跑(SKILL第5.9步)。
- **未接 git pre-commit**:gdconfig 钩子走 `core.hooksPath=git-hooks`(仓库内共享、全队生效),擅改属动在途共享仓→改走我自己的 quality-gate(Stop hook `pending_verify_gate.py`→task-checker type=i18n→`i18n-checklist.md` 已写"泄漏审计走此脚本")兜底 + skill 自觉跑。

- 触发 skill：`x3-translation-automatic`
- 配套 push 自动跑 jolt 导表：[[workflow_x3_auto_jolt_export]]
- 配置改动走 tsv 不碰 xlsx：[[reference_x3_tsv_export_migration]]
- TaskType ParamCount 不在 Excel：[[reference_x3_recharge_isolation]]
