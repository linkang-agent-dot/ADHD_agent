---
name: x3-config-library
description: X3 专属换皮知识库（config-library），含表参考字典+活动形式目录，X3换皮/配活动前先读
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0f488380-f14d-4985-815b-177d4667fb0b
---

X3 节日换皮专属知识库位于 `C:\ADHD_agent\.cursor\x3-config-library\`（与 P2 的 `.cursor/config-library/` 平级，互不污染）。为待建的 **x3-reskin skill** 打的地基。

## 已建文件（2026-05-29）
- `table-reference.md` — X3 配置表参考字典：tsv 写入铁律 + tsv 7行表头结构 + 核心表速查(ActvOnline/Pack族/Reward/Rank/TimeCycle/皮肤族字段) + ID编码规则(Item_81xxx等/节日Pack ID段) + **9条必检清单**(MailID/Reward三铁律/累充隔离/MainBg/装饰3处Icon/TimeCycle TT限制/ScoreID=603/翻译同步) + 跨表ID联动
- `activity-forms.md` — X3 活动形式目录：51 组 Actv* 模块编目 + 节日装配模板 + **13种高适配换皮主力形式**(积分/酒馆/许愿池/许愿/双类转盘/兑换/合成/捐赠/拼图/航行/累登/拜访礼包/放置)各自的玩法/表/换皮可改项/历史实例
- `numerical-manual.md` — 换皮数值手册(礼包侧已建/养成线TODO)：以**「X3礼包投放整理」表**为锚。SheetID `1gOCYBTtnxUiviDNiGwIX1vMAGRgQIyv76Nmd7ngBDF0`(46页签/礼包总览4006行/1657礼包/道具表1728道具)。三层=道具表(钻石价值基准,填充不全)+类型统计+礼包总览(逐道具算ROI)。**ROI公式=礼包总钻石价值÷(售价USD×500)**；换皮铁律=ROI落模板同档区间(水手招募$49.99~$99.99档约17~19x)。礼包总览「奖励组ID」=配置 Reward.RewardID 连接键。**钻石↔美刀：1 USD=500钻石(官方兑换比例,用户确认；钻石充值页签 Pack 1001-1006 佐证)，美刀价值=钻石价值÷500，ROI本身即"美刀价值倍数"**

## 活动级数值真锚：尼罗道具循环白皮书（2026-06-18 配周卡换皮实证）
做开箱/转盘/周卡等**活动奖励数值**时，除 numerical-manual 的礼包钻石表外，更直接的活动级锚 = **`C:\ADHD_agent\KB\产出-数据分析\26尼罗河活动道具循环.html`**（X3开箱/转盘活动数值真锚，比夏日表细）。干净口径（与 numerical-manual 的 1USD=500钻 自洽）：
- **抽奖券/转盘券 = $0.25/张**（B线纯券包 20/$4.99…400/$99.99；=125钻）；累充附赠券按 **$0.50/张**（低ROI档）；"券面价$0.25"夏日/尼罗/世界杯三案一致。
- **宝石 = $0.002/个**（=1USD/500钻，与基准一致；A线 $99.99→50000宝石佐证）。
- **A线礼包范式 = 券+宝石+VIP经验**（ChainPack pack_type=11，ROI最高的投放结构；纯券=B线 pack_type=15，ROI偏低=直购券底）；A线全通 ROI≈2.25×=X3节日付费线基准。
- 兑换积分→兑换商店分层：基础(碎片/表情)200 / 中(装饰/家居)1200 / 高(历史皮肤/养成)1500 积分；兑换币≈$0.01/个。
- ⚠️**养成/加速类道具 X3 无逐项美金价**（礼包钻石表填充不全）；配奖池时价值主体用**券+宝石**（可精确算ROI），养成/加速当等值resource偏好坑。
- 实例：尼罗转盘 ActvLuckyWheel ContentID=1023，券=女王恩典卷(1128)单抽1张，奖池组319(10项权重1万)。周卡换皮方案见 [[x3]](monetization,WeeklyCard段) 的链路。

## 已建 ②（2026-07-09）
- `must-check.md` — **X3 克隆活动换皮正序自查清单**（三节日世界杯/夏日/深海 30+ 实战坑收编，按环节：配置克隆/i18n/美术DK/数值/部署/结算/分支协作）。**X3 换皮开工必过这份清单**；头号条目=c33/c44 展示道具残留（深海撞4次）。来源审计=`KB\换皮档案\X3\_X3三节日换皮全景与坑梳理_20260709.md`（含三节日克隆谱系表+知识库缺口清单）。

## 待建（x3-reskin skill 后续）
- `reskin-rules.md`（换皮操作规则）· `id-conventions.md` · `cases/`（换皮案例）——以 must-check.md 为地基，下次 X3 换皮实战时长出
- `numerical-manual.md` 的**养成线付费价值**部分（X3缺，X2有手册/P2有深度手册可参考；纯礼包换皮用不到，仅"换皮+深度调养成数值"才需要）
- SKILL.md：编排 S0-S12，调度 [[reference_x3_config]] 改tsv→[[reference_x3_i18n_workflow]]翻译→x3-media出图→jolt验证

## 理念
模板化换皮(copy-and-swap，最小diff)：找上一期最接近的活动形式整段复制，只换 ID/皮肤/文案/少量数值。
内容收编自 [[reference_x3_config]] [[reference_x3_score_activity]] [[reference_x3_reward_table_rules]] [[reference_x3_recharge_isolation]] [[reference_x3_timecycle]] [[reference_x3_pack_panel_rendering]] [[reference_x3_pack_tab_icon]] [[reference_x3_tsv_export_migration]] 等全集 + 实际 tsv 扫描。
