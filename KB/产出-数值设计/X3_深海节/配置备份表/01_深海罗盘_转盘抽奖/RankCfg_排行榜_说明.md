---
tags: [kind/产出, domain/配置换皮, proj/X3, fest/深海节, year/2026]
---

# 深海节 · 01 转盘 美术DK修正 + 排名奖励 — 配置备份（待应用到 feature/x3-deepsea-art）

> 2026-06-23。这批是**我在 dev_festival 上验过、但按用户要求改到 feature/x3-deepsea-art 分支**（配置走 feature·别在 dev_festival 配）。
> ⚠️ **现 live tsv 有另一 agent 在干活——本批只落 KB 备份，不碰 live tsv**；待协调好在 feature 上应用。

## A. 转盘美术 DK 修正（3 处·改现有行）
| 表/行 | 字段 | 改为 | 备份文件 |
|---|---|---|---|
| ActvOnline 101025 | ActvImg | `DK_img_Activity_deepsea_turntable_bg`（大潜艇背景·原误=bg_wheel撞底台） | `ActvOnline_新增101025.tsv` |
| ActvOnline 101025 | ActvIcon | `DK_img_Activity_deepsea_hud_icon`（潜艇HUD·原误=turntable_icon未注册） | 同上 |
| ActvLuckyWheel 1025 | ServerRank | `2000`（深海RankCfg·原误=169尼罗） | `ActvLuckyWheel_新增1025.tsv` |

## B. 排名奖励（4 部分·新增/改）
| 内容 | 文件 | 说明 |
|---|---|---|
| **Item 82005 航者徽记头衔道具** | `Item_新增82005_航者徽记头衔道具.tsv` | 抄82004·Type9/UseEffect18/**UseParameter`105|-1`**永久→用后获 Title105（铭牌就靠这种道具发；82001-04 同理） |
| **8 档 Reward 30910-30917** | `Reward_新增排名档30910-30917.tsv` | 铭牌82005 给 **Top3**(rank1/2/3) + 深海宝珠1201 + 加速(11014/11024/11034)·镜像尼罗169梯度·DropPara必填10000·col0续Reward表max+1 |
| **8 档 RankRewardSlotCfg（RankID 2000）** | `RankRewardSlotCfg_新增2000.tsv` | 名次档 1/2/3/4-5/6-10/11-20/21-50/51-100 → 30910-17。⚠️该表第2列名"RankType"**实为 RankID** |
| **RankCfg 2000 改** | `RankCfg_新增2000.tsv` | NeedSendMailReward=**1** + MailID=**1000018**(复用尼罗rank邮件模板) + MailMaxRankNum=3（2000行已存在·只改这3字段） |

## 机制要点
- **排名奖励走邮件**：RankCfg.NeedSendMailReward=1 + MailID → 按名次发邮件；档位内容在 RankRewardSlotCfg(按 RankID)。设了 MailID 必须 NeedSend=1（否则 `rankcfg_def` 报错）。
- **铭牌发放**=头衔 Item(Type9·UseParameter`titleID|-1`)，不是直接发 Title。
- 数值（各档宝珠/加速量·铭牌给 Top 几）为草案·待数值核。

## 应用步骤（在 feature/x3-deepsea-art·待 live tsv 空闲）
1. 切到 feature/x3-deepsea-art（gdconfig·与 client 同名分支·jolt 要求）。
2. 按上表把 A(3 改) + B(4 增/改) 落进 live tsv（注意：**写 tsv 用 LF·csv.writer 默认 CRLF 要转**）。
3. `python scripts/sync_xlsx_tsv.py`（同步 xlsx）→ `Tools/table_exporter/ExportTable.py` 验 0 异常。
4. commit + push feature → MR/jolt。

_2026-06-23；recipe 已在 memory + 本备份。live tsv 有他人活跃故只落备份，待协调应用。_
