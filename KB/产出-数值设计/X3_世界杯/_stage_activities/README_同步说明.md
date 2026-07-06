---
tags: [kind/产出, domain/配置换皮, proj/X3, fest/世界杯, year/2026]
---

# 世界杯竞猜活动配置 — 56实例填真队伍版【已落 live】

> 2026-06-16 落 dev_festival（commit 4783e4d）。生成器：`..\gen_wc_guess_filled.py`（随机种子2026,可复现）。
> 落地脚本：`.._apply_to_live.py`（保LF追加6表）。前一版占位备份生成器=`..\gen_wc_guess_activities.py`（已弃用）。

## 已落内容（56实例 / 12表751行）
| 表 | 量 | ID段 |
|---|---|---|
| ActvOnline (type64) | 56 | 102920-102975 |
| ActvPack (=ContentID) | 56 | 2920-2975 |
| TimeCycle | 56 | 2920-2975 |
| Pack (每实例两队各一包) | 112 | 892001-892112 |
| Reward (48队伍奖励组×5行) | 240 | 组291401-291448 / 行24800-25039 |
| Text (队名+加送+标题 i18n) | 231 | TXT_Pack_Name_/Desc_{packID} + TXT_WC_Guess_* |

## 分布（对齐甘特图）
32强16×$4.99 / 16强8×($4.99+$9.99) / 8强4×三档 / 半决赛2×三档 / 季军1×三档 / 决赛1×三档。

## 关键字段映射（本次破解）
- **Pack 队伍展示**：Head=**col25**=`DK_WC_TeamPanel_{码}`(队伍板) / Icon=**col27**=`DK_WC_Badge_{码}`(队徽) / HeadShowTime=col26(int)。
- **队名/加送文案**=i18n 自动key（非Pack列）：`TXT_Pack_Name_{packID}`(队名) / `TXT_Pack_Desc_{packID}`(加送)。
- **奖励组**=Content=col13。$4.99→共享291101；$9.99→该队组(券40/钻5000/VIP50+该队框道具80300+idx+1148自选框宝箱)；$19.99→该队组(券80/钻10000/VIP100+该队表情15700+idx+1149自选表情宝箱)。
- **商会赠礼**=col40=UnionGiftCfg 随价格档：$4.99→202 / $9.99→203 / $19.99→204（201=0.99~2.99/202=3.99~7.99/203=9.99~14.99/204=17.99~29.99）。
- 队码↔道具索引对齐：PersonalizeAvatarFrameCfg 按cfgID升序 idx → 框道具80300+idx、表情道具15700+idx（已验ECU=80315/15715）。
- 模板残留清理：克隆891101带 col35="巴西"(改按队队名)、col36="猜对加送 +15"(清空)。

## 现为占位/待定（对阵抽签后调）
1. **对阵**：现随机配对48队22-24对（种子2026）。真对阵出来后改 `pairs`/`PLAN` 重跑覆盖。
2. **开球时间**：TC 现相对窗口(TriggerType5,部署起算)；实际按比赛日 igame 部署时定（不改TC）。
3. **i18n**：队名/文案16语言列暂填中文占位，待 x3-translation 跑翻译。
4. **四强专属国旗框 / 决赛行军表情**：客户端资产跟车(7/8 / 7/15)，到时把对应实例奖励组里的框/表情道具换成专属款。

## 落地步骤复盘（下次套用）
1. `git fetch && reset --hard origin/dev_festival`，验ID段全空(注意行号会被别人占→现查max另选)。
2. 生成器→暂存，逐表列数对齐 live（Text 27列易踩，ActvOnline51/Pack54/Reward14/TC12/ActvPack8）。
3. `_apply_to_live.py` 保LF追加→`sync_xlsx_tsv.py --from-tsv --files tsv/<6表>`（传**tsv**路径不是xlsx！openpyxl慢走后台）→`--check` 验 mismatch=0/crlf=0。
4. 只 `git add` 自己6tsv+6xlsx（别碰 `_staging_weeklycard` 等他人在途）→commit(X3NEW-)→push→jolt_verify dev_festival 核分支。

## 依赖（已就绪 live）
- 自选宝箱1148/1149 + 池291201/291202 + 48框道具80300-80347 + 48表情15700-15747（导表#945 SUCCESS）。
- 入口图DK_WC_ActvIcon / 真券1146 / 界面ActvType64。
