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

## 待建（x3-reskin skill 后续）
- `reskin-rules.md`（换皮操作规则）· `must-check.md`（必检细则展开）· `id-conventions.md` · `cases/`（换皮案例）
- `numerical-manual.md` 的**养成线付费价值**部分（X3缺，X2有手册/P2有深度手册可参考；纯礼包换皮用不到，仅"换皮+深度调养成数值"才需要）
- SKILL.md：编排 S0-S12，调度 [[reference_x3_config]] 改tsv→[[reference_x3_i18n_workflow]]翻译→x3-media出图→jolt验证
- SKILL.md：编排 S0-S12，调度 [[reference_x3_config]] 改tsv→[[reference_x3_i18n_workflow]]翻译→x3-media出图→jolt验证

## 理念
模板化换皮(copy-and-swap，最小diff)：找上一期最接近的活动形式整段复制，只换 ID/皮肤/文案/少量数值。
内容收编自 [[reference_x3_config]] [[reference_x3_score_activity]] [[reference_x3_reward_table_rules]] [[reference_x3_recharge_isolation]] [[reference_x3_timecycle]] [[reference_x3_pack_panel_rendering]] [[reference_x3_pack_tab_icon]] [[reference_x3_tsv_export_migration]] 等全集 + 实际 tsv 扫描。
