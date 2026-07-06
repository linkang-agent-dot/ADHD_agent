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

## ★补单个缺失i18n key走skill的实战坑（2026-06-29·补TXT_ActvOnline_ActvName_106103实录）
跑 x3-translation-automatic 补「某AO/配置漏的单个TXT key」时连环踩：
1. **CompositeI18n只读xlsx不读tsv**(`gen_i18n_imp.py:74` 只认.xls/.xlsx)→xlsx已下线gitignore→**必先`python scripts/sync_xlsx_tsv.py --from-tsv --all`重建全部xlsx**(本地throwaway·不提交)喂扫描器。
2. **重建的xlsx把数字id列写成文本**→`gen_i18n_imp.py:118` 对Research表做`value%100`(取模)→`TypeError: not all arguments converted`崩(只Research做取模·别的表id用作字符串拼接没事)。**修=`openpyxl`把`data\Research.xlsx`数据行(row7+)col1文本id转int**(本次5362个)再重扫。
3. **不能"移走崩溃表绕过"**:`writeFinalExcel`(`gen_i18n_imp.py:279`)对**现有Text里、本轮没扫到的key标FieldStatus.Deleted**→移走Research会把它全部key误标删除。**必须全表扫完**。
4. **扫描会标一堆"已修改"噪音**(本次1600个·重建漂移/历史未译gap·jp缺/zh未转繁)。补单key时**别同步整个Text.xlsx→tsv**(会带进1600噪音)→**只把目标key一行手写进`tsv/i18n/Text__Text.tsv`**(克隆同主题已译行如`TXT_Pack_Name_211016`「深海居所/Abyssal Abode」16语言术语·改key+把"特惠"换"装饰"逐语言)。验证=`git diff --stat`只1行 + `i18n_leak_audit.py --grep <key>`✅无泄漏(注:`--changed`是全表口径会刷屏预存噪音·别被吓到)。
5. **翻译skill的SKILL.md流程含`git checkout dev`**→工作目录被切到dev分支→commit误落dev(`[dev xxx]`)→**cherry-pick回dev_festival**(`git checkout dev_festival && git cherry-pick <hash>`)。补深海i18n务必确认在dev_festival提交。
6. i18n表16语言列:key/status/note/**cn,en,sp,fr,id,de,kr,zh,ru,ua,jp,it,pl,po,tr,th**(skill旧doc写10语言已过时·实际16)。

## ⚠️ worktree 里跑 i18n_leak_audit 必带 --tsv（2026-07-03 实证）
`i18n_leak_audit.py --changed` 的 tsv 路径**默认写死 `C:\x3\gdconfig\...`**，在 worktree（如 `C:\x3\wt_i18n_dev`）里 cd 过去跑不带 `--tsv` 会**静默审计主仓** → 报「改动行: 0 / ✅无泄漏」的**假通过**。必须 `--tsv <worktree>\tsv\i18n\Text__Text.tsv`。判据：改了 1 行却报 0 改动行 = 审错了仓。

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

## ★「裸文本缺 i18n key」扫描的正确判读法（2026-07-02 批量查 219 条 dev 状态实证）
某 bug-scan 会报 `<表>__<sheet>.tsv | <id> | 裸文本缺 i18n key（<字段>）：<中文>`。**判读铁律**：
- **这条 scan 只是说「配置单元格里写了中文字面值」——本身不是问题**（X3 所有 TXT_ 字段的单元格中文都只是编辑器母版，客户端运行时不读，见下节机制）。真问题是「该行的**自动 key 建没建**」。
- **自动 key = `TXT_{Sheet}_{Field}_{ID}`，Sheet = 文件名 `__` 后半段**（=proto message 名，如 `ActvScore__ActvScoreTask.tsv`→`TXT_ActvScoreTask_TaskDesc_{id}`；`Pack__PackTypeInfo.tsv`→`TXT_PackTypeInfo_Name_{id}`，**不是** `TXT_Pack_...`）。批量判定=对每行拼 key → `grep -F "<key>"` 查 `tsv/i18n/Text__Text.tsv`（-F 兼容 `|` 合并行）。
- **key 不存在 = 漏建 = 游戏该字段显空白/`_is_null`（全语言含中文都空，因单元格cn只是母版）**；key 存在=再看语言列判空缺/泄漏（走 i18n_leak_audit.py）。
- ⚠️**别用 `_{Field}_{ID}` 后缀模糊匹配兜底**：不同表会撞同后缀（如 `ActvLogin.Name 455` 会撞到无关的 `TXT_ChainPack_Name_455`、`Pack.Name 211001` 撞 `TXT_UnitConfigWonder_Name_211001`）→ 假阳性误报"已存在"。**只认 `TXT_{Sheet}_{Field}_{ID}` 精确 key**。
- **先验 prefix 存活**：对每个 `TXT_{Sheet}_{Field}_*` 全表 `grep -c`，若>0 说明命名对、只是这些具体 id 缺；若=0 才怀疑命名/该字段不走自动key。（219 条实测：16 个 prefix 全存活，命名规则确认无误。）
- **补 key 前先挑「重复通用词」复用现成译文**（免费礼包/金币/专属/永久/排名奖励/世界杯冠军抽奖券/航海罗盘/48国队名`wc_country_table.json`）——只有长句描述才真需新翻。整节日体检用 `festival_i18n_completeness.py`（母版门控，见文末）；给定任意 scan 清单查 dev 状态=上述 grep -F 法。
- **主仓脏时纯只读查 dev**：隔离闸门会拦所有主仓 Bash（含只读），走 `git worktree add ../gdconfig-<名> -b <tmp> origin/dev`（闸门放行此命令）抽干净 Text tsv 查，查完 `worktree remove --force`。

## ★两层模型 + 漏建vs漏翻（2026-07-02 兑换商店角标实操提炼，判缺key先套这个）
X3 文本有**两层**，判「缺 key」先分清动的是哪层：
- **第一层=配置母版格**（如 `ActvExchange.tsv` Label 列填「专属」）：决定「这个投放**要不要**这段文本/角标、填什么」。**这是产品/策划判断**（尤其可选装饰角标：不是每个投放都要角标），不是 agent 能替拍的。母版格不下发客户端、不显示（proto 剥离，见下节）。
- **第二层=Text 本地化表**（`Text__Text.tsv` 的 `TXT_{表}_{字段}_{id}` key 行，存全16语言）：真正下发显示的。**一旦第一层说"要"，补 key+译文是机械执行、直接改**（同 cn 常有现成兄弟译文整行可复用，零翻译成本）。
- **漏建 vs 漏翻（表现不同、补法不同）**：
  - **漏建**=Text 表**连 key 行都没有**（`grep -F <key>` hits=0，含 `|` 合并行展开后仍无）→ getter 返回空串 → **全语言含简中都空/隐藏**。中文只在第一层母版格里（不显示）。这不是"填了cn漏外语"。
  - **漏翻**=Text 表**有 key 行、cn 填了、外语列空**（状态"新增"）→ 简中显 cn、**海外显 cn 或空**。
  - 判哪种：`grep -F` 精确查该 key 在不在 Text（合并行也算在）。在=漏翻(补外语列)；不在=漏建(整行建，先过第一层产品判断决定要不要建)。
- **典型误判**：把「第一层母版格填了中文」当成「cn 已就绪、只差翻译」——错。母版格 ≠ Text 表；母版填了但 Text 没建 key = 漏建 = 全语言都不显示。

## ★★「裸文本缺 key」的真实失败模式=空白，不是"海外显中文"（2026-07-02 proto实证，纠正常见误判）
有 bug-scan 会把这类报成「XX列直接写死中文没走翻译key→海外语种原样显示这段中文」。**这个失败模式判断是错的**，证据链：
- **配置文本列在导表时被剥离，根本不进 client config bytes**：proto 生成类（`client/Assets/Scripts/CSShared/Common/Cfg/CfgProtos/<表>.cs`，如 `CActvExchangeCfg`）里**没有** Label/Name/Desc/ObtainTips/Tag/RankName 等文本字段的原始 string 成员——只有 int/bool/数组等非文本字段。单元格里的中文（"专属"/"金币"）客户端**拿不到**，谈不上"原样显示"。
- **文本的唯一访问器 = `CfgProtoTextEx.cs` 生成的 key-getter**（`TXT_{Sheet}_{Field}_{ID}`）→ `CfgHelper.CheckAndConvertCfgTxtToEmpty(key)`（`CfgHelper.cs:90`）：客户端分支 `IsNullOrEmpty(LocalizationMgr.Get(key)) ? "" : key`。**key 没建 → getter 返回空串**。
- UI 消费点是 `TFWText.text = getter结果`；`TFWText.text` setter（`TFWText.cs:312`）**空串→直接显空、无兜底**，非空才当 key 去查译文。
- **∴ 缺 key = 该位置空白，且影响所有语言（含简中/母语），不是"只坑海外、中文没事"**。（若某字段 UI 压根不读 getter=废字段，则无害，见下）。
- **推论**：判「裸文本缺 key」的真实影响要两步——①`CfgProtoTextEx.cs` 确认该字段是 TXT key-getter 字段（几乎都是）→ 缺 key 会空白而非漏中文；②扫客户端 UI 有没有真读这个 getter（`CRankCfg.I(id).RankName` 之类）+ 有无 RankType/条件门槛 → 读了才真空白，没读=假警报。别停在"配置层缺 key"就下"海外显中文"结论。
- 实证字段（均确认 key-getter、无原始 string 字段）：ActvExchange.Label / ActvLogin.Name / ActvScoreTask.TaskDesc / Item.{Name,Desc,ObtainTips,Subtitle} / ItemObtain.{ObtainName,ObtainDesc} / Pack.{Name,Desc,Tag} / PackTypeInfo.Name / RankCfg.{RankName,RankRewardTitle,RankRewardTab}。

### ★缺 key 的三档真实影响（2026-07-02 四路 UI 消费扫描实证，"隐藏≠无害"）
「缺 key」的表现分三档，**别一律当空白、也别把"隐藏"当无害**（隐藏=策划写在单元格、想显示的角标/描述对**全语言含简中**都没显示=设计意图静默丢失）：
- **① 真空白（渲染破损·必修）**：UI 直接 `TFWText.text=getter` 无保护 → 空标题/空框。
  - `Item.Name`（ItemUnitView 详情/tooltip，无兜底）、`ItemObtain.ObtainName`/`ObtainDesc`（获取途径面板条目，ObtainDesc 功能未解锁分支会被 FunctionUnlock.Prompt 覆盖）、`ActvScoreTask.TaskDesc`（积分任务列表标题，无兜底且不走 UIHelper.GetTaskDesc 的 TaskType 回退）、`RankCfg.RankName/RankRewardTitle/RankRewardTab`（UIRank/UIRankList/UIRankReward/UIActvKvkRank；RewardTitle 仅榜有奖励按钮时显、RewardTab 仅多榜合一时显；国王之路榜用通用key不读RankName）、`PackTypeInfo.Name`（商城页签/弹窗标题，无兜底）、`Pack.Desc`（无别的源，fallback 只是空串）、`Pack.Name`（多数无兜底空白；**例外**：阶梯/机甲阶梯礼包首档 Name 空时回退 `CChainPack.Name`=`TXT_ChainPack_Name_{ID}`，故阶梯类 Pack.Name 缺 key 未必空白，需按 id 核 ChainPack key 建没建）。
- **② 内容静默丢失（不崩但该显示的没了·取舍）**：UI 有 `if(!IsNullOrEmpty) SetActive(true) else SetActive(false)` → 空则**隐藏该元素**（不是空框）。缺 key = 角标/副标题/描述对所有人都不显示。
  - `ActvExchange.Label`（兑换项角标 GoodsTips 隐藏）、`Pack.Tag`（礼包价值角标"限定/120倍"隐藏；仅组合/三选一/多档累充/成就礼包 widget 才有此角标；周特惠"%折扣"角标走 `CPackWeek.Tag` 数值 int、不吃 TXT_Pack_Tag）、`Item.Subtitle`（隐藏）、`Item.Desc`（描述整行 SetActive(false)）、`Item.ObtainTips`（**不是**获取面板的源；面板读 ItemObtain 表；ObtainTips 只在"无可用途径"时弹 toast，空则 fallback 到通用 `Text_Item_Not_Enough_Quantity`+道具名）。
  - ⚠️**营销角标（Pack.Tag/ActvExchange.Label）虽属②但商业上该修**——价值钩子不显示=变现损失；低价值文本（48国表情 Desc、宝箱 ObtainTips）可放最后。
- **③ 真零影响（误报·可忽略）**：客户端根本不读该 getter。
  - `ActvLogin.Name`（登录奖励格显示的是奖励道具自身 `CItem.Name`，全客户端零消费；这是死字段）。
- **★scan 盲点：某字段可能整个没进扫描（2026-07-02 ChainPack.Name 实证）**：bug-scan 未必覆盖所有文本字段。修某字段缺口时**连带查同功能的关联文本字段**——如阶梯礼包一套有 `Pack.Name`(各档名)+`ChainPack.Name`(链头/组标题)+`PackTypeInfo.Name`(商城页签)，原 219 扫描只含 Pack.Name/PackTypeInfo.Name，**整个 ChainPack.Name 字段没进扫描**→修完 Pack.Name 211001-011 才发现其链头 `TXT_ChainPack_Name_678` 也缺、组标题空白。收尾对某功能做 i18n 完整性=列全该功能的所有文本字段逐个查覆盖（用 `festival_i18n_completeness.py` 的母版门控思路），别只信 scan 给的字段。
- **排查 SOP**：拿到「裸文本缺 key」清单 → 每字段先按上表定档（新字段查 `CfgProtoTextEx.cs` 确认是 key-getter + grep 客户端消费点看有无 `IsNullOrEmpty` 保护/替代源）→ 只①必修、②按价值取舍、③划掉。**别停在配置层就报"海外显中文"或"全是空白漏建"**。
- **★②档"补不补"别拿"有多少行有值"当理由；覆盖率也只是参考，装饰性角标最终是策划取舍（2026-07-02 两轮纠正）**：
  - 错误指标：「该字段全表有 N 行有值」（有值行多≠这几条该补）。
  - 参考指标：**同字段所有"有母版值"的 id 里 `TXT_{表}_{字段}_{id}` 已建 key 的占比**（查法=配置 tsv 取该字段非空 id 集 ∩ Text 该 prefix 已建 id 集，Text 按 `|` 合并行展开）。如 ActvExchange.Label 实测 167 个有值 id 中 156 个=93% 已建。
  - ⚠️**但覆盖率高 ≠ 这几条必补**：像兑换商店角标(Label)、礼包角标(Tag)、道具副标题这类**逐投放可选的装饰元素**——"填本地化才出角标、不是每个投放都要角标"。这几条 cell 填了值只代表"当初有人想给角标"(intent)，key 没建=没生效(render)；**要不要这个角标本身是策划取舍**，不是本地化完整性 bug。正确姿势=**别当"必补"自动建，把"这些投放要不要显示角标"抛给 owner/策划定**（要→补 key，同 cn 大量现成译文可复用；不要→保持现状/清 cell 都行）。真正"必补"的是①档渲染破损(空标题/空框)和②档里**功能性文本**(如 ObtainTips 无途径提示、Subtitle 时效信息)，不是可选装饰角标。
  - **★判"漏建疏忽 vs 有意省略"的最强信号=同容器内一致性（2026-07-02 兑换所实证）**：看同一容器（兑换所/礼包组/同 ContentID）内**同类角标**的建 key 是否一致。若同所里别的角标项 key 已建、正常显示，唯独这几个精品项没建（如兑换所里 50%/83% 折扣标都显示、"专属"外观精品标却掉了；甚至同值"50%"一个所显示一个所不显示）→**同容器一半显示一半不显示=漏建疏忽，该补**（不是策划有意不给）。反之全容器都没角标=可能有意省略。评估时先解析这几条属哪个活动/容器、标在什么上（外观精品 vs 大宗材料），再看容器内一致性。兑换所实证：荣耀兑换所(1339)/深海宝藏集市(1340)/深海珍宝集市(1341) 三个 ActvType=13 兑换活动，"专属"专标头像框/纪念卡/英雄皮肤等外观精品，规律一致=刻意设计，缺的是漏建。
- **★ObtainTips 类"兜底字段"要查替代源覆盖再定（2026-07-02 实测）**：`Item.ObtainTips` 只在道具"无可用获取途径"时弹 toast；道具详情"获取途径"面板真源是 **ItemObtain 表**（由 `Item__Item.tsv` 的 ItemObtain 引用列=col8 的 int[] 挂载）。判 ObtainTips 缺 key 要不要补=查该道具 col8 有没有 ItemObtain 引用：**有引用→面板走 ItemObtain 显真实途径、ObtainTips 死路径不触发=跳过**（世界杯头像框80300-80347/表情15700-15747 实测 100 条都有引用可跳）；**col8 空→ObtainTips 是实际 toast、缺则退化通用"数量不足"=补**（如珍珠贝1150、大富翁道具1202/1204）。

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

## ★换皮残留语义检查 = leak_audit 的 `--reskin-residue` 模式(2026-06-29 世界杯规则本地化复查固化)
**洞**:换皮 clone 复用源活动的带文本ID(RuleTips/Title/Content/Pack名)时,i18n 译文**完整但节日主题错**——EN_LEAK/CJK_LEAK/EMPTY 三类完整性审计**全部漏判**(单元格非空、非泄漏、各语言都译了,只是写的是源节日名)。实证:世界杯**累充 15013** 全16语言译好却写"尼罗之辉/Nile Radiance/니로의 빛";**开箱 16031** 乌克兰语整段还是元旦"Скриня Фортуни Астри/旧年终结"。
- **新模式**(已加进 `i18n_leak_audit.py`):`--reskin-residue --src-festival <nile/newyear/spring/valentine/deepsea/summer> --grep/--prefix <新ID范围>`。内置 `FESTIVAL_RESIDUE` 多语言源节日词表,扫范围内每个 key 的全16语言 cell 是否含源节日名→命中=RESIDUE(block,exit1)。或 `--source-terms "词1,词2,..."` 自定义。
- **换皮收尾SOP**:①列全部复用的带文本ID(RuleTips ID=ActvOnline col13;Pack名=新Pack ID段)→②按范围 `--grep/--prefix` 跑 residue→③命中的逐语言重写为目标节日(从干净兄弟key抄各语言标准译法)。已挂进 `i18n-checklist.md`(换皮任务才查·block) + SKILL 第5.9b步。
- **★规律**:换皮活动若复用源活动RuleTips/Reward等带文本ID,**正文每条逐语言核语义**(光换道具名不够,获取途径/玩法描述/节日名会留源活动);**多语言别只信中英**(本例累充全语言错、开箱独漏乌克兰语)。同根因坑见 [[project-x3-worldcup-activity]] 开箱16031段。

## 世界杯规则本地化复查结论(2026-06-29·commit 26125af→rebase 509c045·导表#1361 SUCCESS)
逐活动查 RuleTips(客户端读 `TXT_RuleTips_Title/Content/Tab_{规则ID}`):开箱101516→16031 / 累充100597→15013 / 签到101403=无规则 / 兑换101339=无规则 / BP102243→1017 / 竞猜73个→全用1190。**3处已修**:①累充15013 Content 全16语言尼罗→世界杯 ②竞猜1190 Tab 全语言中文"规则"泄漏→各语言Rules ③开箱16031 乌克兰语整段元旦残留→世界杯。**RuleTips ID 在 ActvOnline col13(0-idx)**;RuleTips表单元格只是母版备注不进客户端。

## ★节日全量 i18n 体检工具 = `festival_i18n_completeness.py`(2026-07-01 深海节固化·补 leak_audit 查不到的洞)
`i18n_leak_audit.py` 只审「Text 里已有的行」(空缺/英文泄漏/中文泄漏/换皮残留),**查不到「config 引用了 key 但 Text 根本没这行→游戏空白」的漏建**。新脚本 `~/.claude/skills/x3-translation-automatic/scripts/festival_i18n_completeness.py` 补这个:
- **母版门控**:收集深海 AO(组140/141)名/描述 + RuleTips + Pack(深海ID段)名/描述 + Item + ActvGroup 的全部 TXT key → 逐个查 Text tsv → **只在「配置母版非空」时才报漏建**(母版空=本就无该字段=正常,不误报)。② 对存在的 key 跑简版泄漏检查(空缺/英泄/中泄)。
- **复用**:改脚本里 `DEEP`(Pack ID段) + `AO 组号` 即可换节日。跑法 `python festival_i18n_completeness.py`(默认指主仓,改 ROOT)。
- **深海实战**:一轮扫出真缺口=大富翁/装饰 desc、藏宝图/宝珠 desc、深海节名(组140)、周卡 desc、队友规则16040-42 只cn。排除 207201-211(ChainPack677「成就礼包版」·staged未挂AO)。

## ★★并发孤儿坑:基于旧 worktree 视图重复造修复(2026-07-01 深海累充/转盘残留亲踩)
**现象**:我在 worktree 里审计出「累充100598 rt=15013 写世界杯 / 转盘101025 rt=16032 写尼罗」残留,回主仓 clone 独立规则 15018/15019 + repoint。但**主仓 dev_festival 上队友早已把同一残留修好了(建 16040累充/16041转盘,已 repoint)**→我的 replace('15013'/'16032') 在主仓是**空操作**(主仓 AO 早不指 15013/16032)→我白造了 15018/15019 = **孤儿(没 AO 指向)**。
- **根因**:worktree 是 dev_festival 某旧时点的快照,**shared 分支上别的 agent 的修复不会自动进你 worktree**。你按 worktree 的「残留态」去修,实际主仓已不是那个态。
- **铁律**:**在 shared 分支(dev_festival)上做「修复类」改动前,先在主仓最新态复核问题还在不在**——`git fetch` + 直接查目标字段现值(如 AO col13 现在指哪个 RuleTips),别信 worktree/旧审计的「问题快照」。残留/漏建这类,队友可能已修。
- **收尾**:发现孤儿→删干净(RuleTips 母版行 + Text 的 Content/Title 行 + 撤合并行挂),别留(会有两套深海累充规则让后人懵)。队友的 repoint 没被我破坏(空操作没改 AO)是走运,不是设计。
- **正确姿势**:这种「shared 分支 + 可能并发」的修复,能直接在主仓最新态干就别在旧 worktree 干;真用了 worktree 要先 `git pull --rebase` 拉平再审。

## ★i18n 结构损坏坑:多语言写成"无键转置行"(2026-07-01 深海RuleTips16040实证)
症状:Text__Text.tsv 里某 `TXT_RuleTips_Content_XXXX` 行**非中文列只剩标题、缺正文**,紧随其后夹着 **16 行没有 key 的坏行**(col0 直接是各语言正文、col1 是错位一格的标题),再接 `TXT_RuleTips_Title_XXXX`。=本该是 Content 行的 16 个语言列,被写成了 16 行、**行列转置**。Excel/WPS 打开就是"一坨"错位。
- **检测**:扫 col0 不以 `TXT_`/`Text_` 开头的行(=无键坏行);或对着本地化清单 HTML 跑「present+16语完整」核对(csv 解析要处理 `|` 合并key + 多行单元格)。
- **修复**:16 坏行的 col0 **按语种顺序正好=列序**(cn,en,sp,fr,id,de,kr,zh,ru,ua,jp,it,pl,po,tr,th)→依次回填进 Content 行 col3..18 + 删掉 16 坏行。用 csv QUOTE_MINIMAL 重写、diff 只该动 ~17 行(上千=重排全表了要回退)。
- **完整性核对法**:拿本地化清单 HTML 抽全部 TXT_/Text_ key,比对 tsv 查①缺失②某语言列空。范例:深海清单 130 key→119全/11缺(补)/1损坏(修)。

- 触发 skill：`x3-translation-automatic`
- 配套 push 自动跑 jolt 导表：[[workflow_x3_auto_jolt_export]]
- 配置改动走 tsv 不碰 xlsx：[[reference_x3_tsv_export_migration]]
- TaskType ParamCount 不在 Excel：[[reference_x3_recharge_isolation]]
