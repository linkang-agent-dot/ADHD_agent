---
name: reference_x3_client_stale_config_diagnosis
description: "X3 客诉排查新范式：客户端配置快照与服务端脱节（旧包/热更未到）导致价格错配/商品缺失，用 gdconfig git 历史给玩家配置\"断代\""
metadata: 
  node_type: memory
  type: reference
  originSessionId: ffe7f705-a0df-4766-baba-1746fa9a0bf2
---

# X3 客户端配置快照断代诊断法（2026-07-06，1910服玩家1691722客诉案）

## 核心规律
X3 客户端的**商品列表/价格/余额校验全读本机配置**（`UIActvExchange.cs:73`、`UIActvExchange.ExchangeItem.cs:87`），服务端按**服务端配置**收费（`ActivityMeta.Exchange.cs:147`）。配置走热更（`Assets/Res/Config/ProtoGen/*.bytes`），**服务端下发活动时不校验客户端版本**（ActvOnline 全 53 列无 minVersion 字段）→ 旧包/热更卡住的玩家会看到旧价格/旧商品，购买时被服务端按新配置拒绝，报「资源不足」等误导性错误。

## 断代方法（实锤玩家配置停在哪天）
玩家看到的**异常配置形态**（商品数量、价格、图标）本身就是指纹：拿 gdconfig `git log` 逐 commit 复算该表的解析结果，找到唯一匹配玩家所见形态的时间窗口。
实案：玩家见「兑换商店只有 1 件商品、月心珍珠卖 25000」→ 只有 6/24(`dd6dd53` clone+游离引号吞行) ~ 6/29(`dc92907` 修复) 窗口的配置解析成这个形态；6/30(`e285838`) 已调价 25000→50000。玩家 30910 深海代币：25000(旧显示价) < 30910 < 50000(服务端真实价)，数字自洽即实锤。

## 已知配套坑
- **tsv 游离引号吞行**：ActvExchange Label 列未闭合引号 `"` 会让 csv 解析把后续多行吞进单元格，整个商店只剩 1 件商品（6/24 dd6dd53 引入、6/29 dc92907 修复）。改表带富文本时注意引号闭合。
- **ark/iGame 部署无同 cfgId 去重**：`ActivityMgr.Ark.cs:192,212-250`，重复部署=玩家端两个一样的活动入口。见 [[reference_x3_server_activity_duplicate]]。
- **深海节两个兑换商店本来就雷同**：101340 深海宝藏集市 / 101341 深海珍宝集市，名字一字之差、同背景图（1341 是 6/24 从航海之路 1332 克隆的，TopResource=1057 航海罗盘残留），玩家极易看成"两个一样的商店"。
- DK 缺失是静默 fallback（`UIHelper.Graphic.cs:30-39` 空 key 直接 return），旧包缺新 icon 会错显不报错。

## 排查口径（同类客诉直接照做）
1. 玩家所见价格/商品数 vs 当前 tsv → 不一致先怀疑客户端配置快照旧。
2. gdconfig git log 断代，找匹配窗口。
3. 待线上确认：玩家客户端资源版本号、背包道具真实数量、该渠道热更 manifest 是否还在推新。
4. 话术：告知服务端真实价格 + 引导更新客户端。

## 关联
[[reference_x3_server_activity_duplicate]] · [[reference_x3_config]] · [[workflow_bugfix_ops]]
