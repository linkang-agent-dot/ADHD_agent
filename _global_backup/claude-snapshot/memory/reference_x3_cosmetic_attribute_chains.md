---
name: reference_x3_cosmetic_attribute_chains
description: X3 八大外显模块的属性配置链路（6/8带属性·各表列含义·PropType字典·万分比口径）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 31d5e8dd-416b-4c63-9820-dda4e5b2521d
---

X3 节日外显各模块「属性」配置真源（2026-06-23 配外显图库 HTML 时逐表扒清）。相关：[[reference_x3_cosmetic_resource_paths]]。

## 关键结论：8 模块里 6 个带属性（别再误判"外显零属性"）
| 模块 | 带属性 | 来源表 · 字段 |
|---|---|---|
| ① 英雄皮肤 | ✅ | 皮肤固定加成(HeroSkin) + 本体技能(HeroSkill) |
| ② 岛屿/主城皮肤 | ✅ | `Skin__Skin`(SkinType=1) Power(战力)+Buff(兵种) |
| ③ 家具 | ✅ | `FurnitureDecorate` Power(27)+PropType(32)+PropNum(33) |
| ④ 装饰三件套 | ✅ | `FurnitureSkin` Prestige(5,声望)+Buff(19) |
| ⑤ 行军皮肤 | ✅ | `Ship__ShipSkin` Power(4,声望)+Buff(6) |
| ⑦ 纪念卡 | ✅ | `MemorialCard.PropertyGroup`→`MemorialCardLevel` |
| ⑥ 头像框 / ⑧ 表情 / 航迹(Skin type2) | ❌ 真零属性 | 无属性表 |

⚠️ 教训：判"有无属性"必须用 **Python csv 解析表头**（这些 tsv 有跨行引号单元格，awk 按物理行切会把列名/数据错位，我因此先误判只3个模块带属性、又把列数错）。

## ① 英雄皮肤：皮肤无等级，属性是固定值
`Hero__HeroSkin.tsv` 列(0-indexed)：[0]ID [2]Name [3]Group(hero id) [10]**Regained**(重复获取转钻补偿"单日|累计",**与属性无关**别误读) [11]ObtainItemID [12]**PropType** [13]**PropNum**(兵种加成,万分比) [14]**Power**(战力) [15]SkillList [16]buff备注(属性名) [20]DK_Video。
- 皮肤属性 = `兵种攻击 +PropNum/100% · 战力Power`，**固定值·皮肤没有等级/升级表**。
- 本体技能(HeroSkill) ≠ 皮肤属性，是两个字段：本体随**英雄等级**成长(L1→L100,显示满级值)；hero_id=1000+Role_C_n;HeroSkin id=(1000+n)*100+skinNum。
- ❌曾错把 PropNum(col13)+Power(col14) 当成 min→max 范围 → 显示成假范围"+30%→+360%"，已修。

## ⑦ 纪念卡：真有等级（范围是对的）
集齐同卡升级 L1→L30(MemorialCardLevel)，每级 PropNum 万分比 +2%→+60% 给战力Buff；组1003猎人攻击/1004射手攻击/1011射手防御。

## 属性值口径 = 万分比（÷100 = %），全模块统一
PropType→属性名（从各表内联 buff备注 收集）：
220000 所有水手攻击 / 220001 猎人攻击 / 220002 射手攻击 / 220003 斗士攻击 /
220010 所有水手防御 / 220011 猎人防御 / 220012 射手防御 / 220013 斗士防御 /
120100 部队伤害增加 / 120200 部队受到伤害(减伤,值为负) / 21009 采集速度 等。
`Hero__Hero.tsv` 的 HeroAttributes.DataGroup(col21) 那套(声望/人气/带兵数)是**酒馆经营属性**≠兵种战斗属性，别混。

## 2026 新投放（世界杯/深海节）
- ① 足球宝贝·爱莉希雅(世界杯,HeroSkin 104001,带视频 DK_video_zuqiubaobei_sbs)
- ⑥ 头像框：世界杯48国助威框(80300–80347,同款换队徽) + 金/银/铜樽之冠(80113/114/115) + 深海之冠(80100)
- ⑧ 表情：世界杯48国加油(15420–15467) ⑦ 纪念卡：绿茵之星(79)/远航之歌(80)
- 深海节目前只落地 头像框+纪念卡+头衔(82005航者徽记)；岛屿/家具/装饰/航迹暂无新深海款。头衔不在8模块内。

## 外显图库 HTML 生成脚本（自动读 tsv，加新款自动带属性）
`C:\ADHD_agent\KB\产出-本地化与美术\X3\外显图库_表情头像框铭牌\_gen_festival_cosmetics.py`：
`_proptype`(全局字典) + `skin_attr`/`hero_attr`(①) + `_furn_attr`(③) + `_deco_attr`(④) + `_ship_attr`(⑤)；48国框/表情走 frame_wc/emoji_wc 汇总前6+计数。
