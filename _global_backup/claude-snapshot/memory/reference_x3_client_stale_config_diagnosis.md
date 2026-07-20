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

## ✅ 直接解码客户端 ProtoGen .bytes 验证配置到没到客户端（2026-07-15，修女礼包案）
不启动 Unity、不靠时间戳猜——直接读二进制确认某配置改动是否已进客户端 build。比 git 断代更硬（断代是推理，解码是实读）。
- **场景**：改了 gdconfig 的 Reward 表（如 7002 美酒→52003 万能信物），客户端展示还是旧的。展示由**客户端本机 ProtoGen 字节**画（`Assets/Res/Config/ProtoGen/Reward.bytes`），要新内容必须 导表→提交进 x3-project→客户端拉取+Unity 重导入。拉之前客户端落后=看到旧配置（本案真因，一 `git pull` 即修）。
- **工具**：`~/.claude/skills/x3-config-export/scripts/decode_protogen_reward.py <Reward.bytes> <RewardID...>`（2026-07-15 固化）。原理=把目标ID编 varint→正则找 `\x10`+varint(RewardID) co-occurrence→顺序解字段。Reward 行 protobuf 字段：field1(0x08)=行ID / field2(0x10)=RewardID / field4(0x20)=ItemID / count 在 field9(0x4a)。一个 RewardID 多行=四格每格一行。同法改字段号可解其它 ProtoGen 表。
- **实测**：pack 19048(RewardID 15900502)解出 51028×10 + **52003×6** + 1002钻石 + 2022VIP，无 7002 → 客户端配置已对。三档 15900502/03/04 全对。
- **配套服务端验证（免真买）**：`endowreward <RewardID>` 投放奖励到测试号 + `additem <item>,1` 探针读 curCount 反推奖励发了几个（详见 [[reference_x3_kadmin_deploy]]「展示 vs 到账」段）。两侧都实读=硬闭环。

## 关联
[[reference_x3_server_activity_duplicate]] · [[reference_x3_config]] · [[workflow_bugfix_ops]] · [[reference_x3_kadmin_deploy]]（服务端 endowreward 验到账 + 热更打断GM网关坑）
