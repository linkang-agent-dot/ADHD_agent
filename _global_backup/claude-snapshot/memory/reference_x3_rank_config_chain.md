---
name: x3-containskey
description: X3 排行榜(Rank)完整配置链路 + ErrCodeRankInvalidType(CRankCfg.ContainsKey失败)的排查法
metadata: 
  node_type: memory
  type: reference
  originSessionId: 33fe5727-08d6-48d3-80a0-91952eddfd74
---

## 排行榜完整配置链（新增/换皮排行榜必齐这几张表，缺一不可）

| 环节 | 表 | 说明 |
|---|---|---|
| 榜定义 | `Rank__RankCfg.tsv` | col0=ID(=客户端请求的 rankType)，col3=RankType类别，col14=上榜条件，col6=榜最大长度 |
| 奖励槽 | `Rank__RankRewardSlotCfg.tsv` | col1=RankCfg ID，col2/3=名次区间，col4=Reward组ID |
| 奖励内容 | `Reward__Reward.tsv` | RankRewardSlotCfg.col4 指向的组 |
| 活动挂载 | 各活动表(如 `ActvCrafting`.col6=RankID / `ActvOnline.RankID`) | 把榜挂到具体活动 |

世界杯开箱本服榜实例(2026-06)：RankCfg **1006** + slot 100424-100430(→奖励组30591-30597) + ActvCrafting 1516 col6=1006。

## ★ ContainsKey 报错排查（ErrCodeRankInvalidType）

报错链：客户端 `RankMeta.cs`/`RankData.cs` 和服务端都做 `CRankCfg.ContainsKey(rankType)` 校验，失败→ `ErrCodeRankInvalidType`。
- **key 是 RankCfg 的 ID（col0）**，不是 col3 的 RankType 字段。`CRankCfg.Configs` = `map<int,CRankCfgCfg>` 按 ID 建字典(RankCfg.cs 反序列化 `tmpConfigs.Add(k,v)` 的 k=proto map key=ID)。所以 client 请求的 rankType 值 = 榜的 ID(如1006)。
- 另有 `RankType2TypeIDs` map(RankType类别→ID列表) + 服务端 `RankType.XxxRankTypes.Contains()` 按 col3 类别路由，与 ContainsKey 的 ID 校验是两码事，别混。

**排查顺序（按概率）**：
1. **客户端过校验但服务端报错 = 两边 CRankCfg 不一致**(最常见)：多半**服务端跑的是旧导出 bytes**，没重载含该榜的最新提交。配置在 dev 上≠部署的服已加载。验证=`!gm ReloadGameServer` 热更最新配置(见 [[workflow_x3_local_server_gm_telnet]])，或查服加载的导出版本。
2. 活动过期被清理→客户端还在请求旧 rankType。
3. RankConst.cs 新增了 rankType 常量但 RankCfg 表没对应行。
4. 上层传了不在表中的 rankType 值——**先看客户端日志里实际请求的 rankType 具体值，再去 RankCfg 表确认该 ID 是否存在**。

**关键判据**：配置在 dev 上齐全(RankCfg行+slot+reward+活动挂载) + 导表 SUCCESS ⇒ "配置少了"基本排除，转查**部署/导出同步**(服是否重载)而非配置本身。

**How to apply:** 排行榜报 InvalidType 先确认是不是 ID(col0) 在 dev 配置里存在；存在就别再翻配置，去查服务端有没有加载最新导出。详见 [[reference_x3_score_activity]]。
