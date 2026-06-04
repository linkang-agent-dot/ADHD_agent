---
name: x3-score-activity
description: X3 积分活动配置体系（ActvScore.xlsx 三 sheet 结构、最佳酒馆 ContentID 系列、TaskType 关键编号、Rank/RewardSlotCfg 结构、ScoreID=603 易混淆陷阱）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 2698066a-6dc9-4d48-8e43-b75b32db6c72
---

## 文件路径（改 tsv，不碰 xlsx；下方 sheet 名即 tsv 名）
- ActvScore — 3 sheet：`tsv/ActvScore__ActvScore.tsv` / `__ActvScoreMulti.tsv` / `__ActvScoreTask.tsv`
- Rank — `tsv/Rank__RankCfg.tsv` + `tsv/Rank__RankRewardSlotCfg.tsv`
- Reward — `tsv/Reward__*.tsv`（RewardID 内容定义）
- 改法：`x3-config-export` skill 的 `tsv_edit.py`（先 `show` 定位列再 `set`/`remove`）

## ActvScore.xlsx 三 sheet 结构

| sheet | 用途 | 主键 |
|-------|------|------|
| ActvScore | **本服**积分活动定义，1 行 = 1 个 ScoreID | ScoreID |
| ActvScoreMulti | **跨服**积分活动定义（多阶段），1 行 = 1 个 ContentID×Stage | ContentID + Stage |
| ActvScoreTask | 任务定义池，被 ActvScore / ActvScoreMulti 的 TaskID 列引用 | TaskID |

### ActvScoreTask 列结构（前 7 列有效）
A=ID / B=TaskDesc(TXT_任务描述，存中文字串不是 LC_Key) / C=Score / D=Group / E=TaskType / F=Parameter1 / G=IsHide / 第8列=备注

### ActvScoreMulti 列结构
A=ID / B=备注(中文) / C=ContentID / D=StageName / E=Stage序号 / F=StageDuration / G=ScoreGroup / **H=TaskID(`a | b | c` 拼接串)** / I=RankID

TaskID 串分隔符：` | `（空格-竖线-空格）。修改 TaskID 串时维持分隔符一致。

## TaskType 关键编号
| TaskType | 含义 | 触发位置 |
|---|---|---|
| 440 | 通用"消耗 Parameter1 道具"事件 | 服务端通用钩子，最广泛使用 |
| 441/442/443 | 消耗金/紫/橙技能书 | 升级英雄技能时 |
| 444 | Hero升星消耗 hook | `Hero.HeroStar.UpItem`，**只在升星路径触发** |
| 292 | 提升英雄好感度 | — |
| 900/902 | 充值积分相关 | 见 reference_x3_recharge_isolation.md |

## 最佳酒馆 ContentID 系列（同一活动模板的不同变体）

| ContentID | 名称 | ActvType | 用途 |
|---|---|---|---|
| 701 | 最佳酒馆基底 | 7 (本服) | 模板 |
| 716 | 魔女之夜 | 7 | 已下线节日（万圣节） |
| 717 | 节庆通用-跨服酒馆1 | 7 | 26 元旦/情人/春节复用 |
| 718 | 节庆通用-跨服酒馆2 | 7 | 26 尼罗、夏日恋语 |
| 2401 | 跨服酒馆-入侵 | 24 | 入侵序章备战 |
| 2402 | 跨服酒馆-KVK | 24 | 风暴前夕 |
| 2405 | 远征酒馆-W2 | 24 | 远征 S1-S5 |
| 2406 | 决战前夕-W4 | 24 | 赛季通用决战前夕 |

ActvType=7 是本服最佳酒馆，ActvType=24 是跨服酒馆变体（备战/远征/决战前夕）。

## 英雄信物 Item ID
- 52001 = 通用稀有信物 / 52002 = 通用史诗信物 / 52003 = 通用传奇信物（兑换源头）
- 51001-51058 = 具体英雄信物（"信物-{英雄名}"），HeroStar.UpItem 消耗这套

## ⚠️ 易混淆陷阱：ScoreID=603

ActvScore（本服）sheet 行 8 ScoreID=603 的备注是「**运营大师**」（ActvType=6 声望排名），**不是酒馆活动**。曾被旧 sub-agent 误读为"酒馆大师"。

修最佳酒馆 BUG 时 **不要动 ActvScore.603 这行**，最佳酒馆配置全在 ActvScoreMulti。

## Rank.xlsx 结构

### RankCfg sheet 关键字段
A 列起：A=ID(col1) / B=备注(col2) / C=TXT_名字(col3) / D=**RankType**(col4，6=本服，12=跨服) / E=Sort积分id(col5) / F=DK图标(col6) / G=MaxRankSize(col7) / H=RankRewardTitle(col8) / I=RankRewardTab(col9) / J=NeedSendMailReward(col10) / **K=MailID(col11)** / L=MailMaxRankNum(col12) / M=上榜门槛(col13)

**易错点**：MailID **在 col 11 不是 col 13**。我曾因列号定位错把 MailID 读成 None 误判（X3NEW-735 修复后核验时踩坑）。

### ActvOnline 跨服字段
- col 19 = `CrossServerRank`（1=跨服，空=本服）
- col 21 = `RankID`（指向 RankCfg 的总榜）
- 其他没有 `CrossServerType / ServerGroup / IsMultiServer` 字段，只有 CrossServerRank 单一开关

**没有"显示奖励 vs 实发奖励"分列字段**。每档奖励统一在 RankRewardSlotCfg 用同一个 RewardID（既显示也实发）。

### RankRewardSlotCfg sheet
A=SlotID, B=**RankID**, C=StartRank, D=EndRank, **E=RewardID**

修排名奖励 BUG = 改这张表的 E 列。

## 节日 RewardID 复用规则
**不同节日的最佳酒馆活动复用同一套 RewardID 系列**（策划确认）。例：

| 节日 | 总榜 RewardID 序列 | 数值 |
|---|---|---|
| 春节"千灯贺新岁" RankID=131（跨服） | 30391-30398（8档） | 第1名：高阶技能书×120 + 1H建造/招募/研究令×30 各 |
| 夏日恋语 RankID=160（本服） | 修复后= 30391-30398 | 同上（X3NEW-736 修） |

8 档分布：1/2/3/4-5/6-10/11-20/21-50/51-100

## 写入注意（实操踩坑总结）
1. **改 tsv 不碰 xlsx**：用 `tsv_edit.py`（`set` 断言旧值 / `remove` 删管道列表ID），别再用 Excel COM/openpyxl。
2. **先 `tsv_edit.py show` 读现值再改**，不要凭印象写 TaskID 串。
3. **双重 ID 校验**（用 SlotID + RankID 两个值确认是目标行，避免串行）。
4. **不要复用已被引用的 TaskID 编号**——同一 TaskID 可能被多个 ScoreID/Multi 行引用，新建必须用未占用 ID。
5. **写前 `git branch --show-current` 确认分支**——见 [[feedback_x3_branch_check]]。
6. **写后看 `git diff`**（行级 diff = 没串列、LF 没坏），再 commit → push → `jolt_verify.py` 验证 SUCCESS。

## 实战参考（2026-05-25 X3NEW-734/735/736）
- **X3NEW-734**：消耗通用信物兑换不加分 → 新增 TaskID 208/209/213 (TT=440) 挂到 ActvScoreMulti 7 行
  - ⚠️ **收尾教训（2026-05-29）**：当时只 commit 了 ActvScore.xlsx，**没补 Text.xlsx 翻译** → 208/209/213 的 `TXT_ActvScoreTask_TaskDesc_*` 只有 cn、10 语言全空，俄服面板显中文母版。后补全（commit `5e738e7`，对齐升星兄弟 201/202/203）。**新增带 TXT_ 字段的任务必须同 commit 补翻译**，见 [[reference_x3_i18n_workflow]]「新增任务漏翻」
- **X3NEW-735**：最佳酒馆排行榜应跨服却只显本服 → 方案 C 新建独立跨服 RankID 619-625(阶段) + 626(总)，RankType=12；改 ActvOnline.10071801 CrossServerRank=1 + RankID=626；ActvScoreMulti R27-R33 改 RankID 619-625。**避开与启程补给站(131/601-607)、KVK(601-607)冲突**
- **X3NEW-736**：排行奖励显示与实发不符 → Rank.xlsx RankRewardSlotCfg RankID=160 八档 RewardID 由 785301-785308 → 30391-30398（735 修完后 RankID=160 变孤儿，但保留有占位价值）

## 跨服活动配套表清查结论（X3NEW-735 验证后）
- `ActvScoreMultiServer` sheet：**仅 KVK/远征类活动登记**，最佳酒馆系列不需要登记
- `ActvScoreGroup` 71811-71874：本服/跨服共用，无需修改
- `ActvScoreTask` / `ActvScoreTaskGroup` / `ActvScoreGuild` / `SpecialRewardSettlement`：与活动跨服属性无关
- X3 跨服活动只需改 4 处：ActvOnline (1行) + ActvScoreMulti (各 stage) + RankCfg 新增 + RankRewardSlotCfg 新增

## TimeCycle TT 与跨服活动兼容性
- ActvType=7 最佳酒馆历史只用 TT=1（绝对时间）或 TT=4，**无 TT=2 (开服+D20 相对时间) 先例**
- 跨服活动调度可能依赖"所有服在同一绝对时间窗口"做服务器分组匹配
- TT=2 + 跨服 = 未验证组合，X3NEW-735 修完后 QA 验证若仍不显示跨服玩家，先改 TimeCycle 该行为 TT=1

## 关联
- [[reference_x3_gdconfig_repo]] [[reference_x3_tsv_export_migration]] [[reference_x3_reward_table_rules]] [[feedback_x3_branch_check]]
- [[feedback_jira_bug_ticket_field_swap]] — BUG customfield 实际/预期可能被 QA 填反，看标题
