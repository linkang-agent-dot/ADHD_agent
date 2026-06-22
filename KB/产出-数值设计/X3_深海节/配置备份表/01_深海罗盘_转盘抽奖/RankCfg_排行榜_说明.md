# 深海节 · 01 转盘排行榜（本服积分排名）— 配置说明

> 2026-06-22 配。转盘自带本服排行榜（消费冲榜）。门槛提示用户说已有（程序侧）。

## ⚠️ memory ID 表的 RankCfg186/RankType12 是错的（已查证修正）
- **186 已被「最佳酒馆」占用**（RankType6），不能用。
- **RankType12 的 RankRewardSlotCfg 是空的**（0 档位）；其实 RankType6 的 slot 也是空的——**转盘排行榜奖励不走 RankRewardSlotCfg，走邮件**。
- 转盘排行榜真模板 = **尼罗转盘 RankCfg 169**（RankType6，MaxRankSize100，NeedSendMailReward=1，MailID1000018，MailMaxRankNum3）。

## 已配
- **`Rank__RankCfg.tsv` 新增 1005**（max1004+1）= `RankCfg_新增1005.tsv`：抄 169，RankType6 / RankName深海排名 / MaxRankSize100 / NeedSendMailReward1 / MailMaxRankNum3 / MailID=**待建**。
- **回填**：`ActvLuckyWheel 1025`.ServerRank = **1005** + `ActvOnline 101025`.RankID = **1005**（原 memory 写 186，改 1005；落地时改这两处指向）。

## ⛔ 待补：排名奖励邮件（MailID）
转盘排行榜奖励 = `NeedSendMailReward=1` → 按排名发**邮件**（尼罗走 MailID1000018）。深海需**新建一封排名奖励邮件**，按排名档位发：
- **投放（用户已定）**：传说铭牌·航者徽记（Title 105）给 **Top 段** + 养成料/深海宝珠 1151 按档递减。
- **待定**：① 排名档位怎么分（Top1 / Top2-3 / Top4-10 / …各发啥）② 邮件 MailID 新建（抄尼罗 1000018 结构）③ MailMaxRankNum=3 含义核（前3名特殊？）。
- 邮件/排名奖励配置链路参考尼罗 MailID1000018 的实际内容（落地时拉出来抄）。

## 落地顺序
定排名档位划分 → 新建排名奖励邮件(含传说铭牌Top+养成档) → RankCfg1005.MailID 填上 → ActvLuckyWheel1025.ServerRank + ActvOnline101025.RankID 改 1005 → 过 gate。

_生成 2026-06-22；dev_festival。RankCfg 结构已配(1005抄169)；排名奖励走邮件·档位+邮件待定。_
