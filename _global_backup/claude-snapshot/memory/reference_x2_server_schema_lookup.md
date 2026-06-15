---
name: x2-server-schema-lookup
description: "X2 服务器→schema 映射怎么查：本地三处\"现成数据\"全是坑（igame-actv server-config.json=P2、fo/config schema表=国服死快照、iGame接口无schema字段），真源待定"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ff6264eb-1436-4bff-92cf-2ed3438db9ec
---

# X2 服务器 schema 查询（2026-06-11 排查沉淀，真源待补）

问「X2 schema3 的服务器有哪些 / schemaN 后的服」时，以下三处**都不是答案**，别再走一遍：

1. **`~/.claude/skills/igame-actv/server-config.json` 和 `~/.claude/skills/igame-skill/server-config.json`（两份内容相同）= P2 专用数据**（schema3-6、服 ID 形如 2092002）。skill 名字看着通用，里面只有 P2。X2 国际服 ID 形如 `1009602`，根本不在里面。是 [[x2-config-library]]「P2/X2 数据静默混淆」同款坑的服务器版。
2. **`D:\UGit\x2gdconf\fo\config\activity_schema.tsv` / `iap_schema.tsv` = 国服死快照**（200xxxx/201xxxx 段，无国际服），且这两表不在策划 GSheet 注册库里（`gsheet_query.py list` 无 schema 表），不走导表管道。用户确认 activity_schema 不是判断依据。
3. **iGame 接口查不到 schema**：serverMgr 全模块（getServerList/getDetail/开服记录 getPageList 的 params）均无 schema 字段。X2 gameId=1089（注意 auth 文件常驻 1090=X3，查 X2 要临时切、办完切回）。

X2 schema 背景：2111 日历 Schema 字段用 `{"typ":"schema","id":[1,2,3,4,5,6]}`（特殊档 13-17/55）；合成小游戏按 schema3/4/5 分普通/精英/冠军三档活动变体。

**真源 = 数仓日报表（用户 dump，2026-06-11 确认）**：列为 `server_id / schema_id / group_id / schema_time(UTC) / report_time`。问用户要 dump 或走数仓查，别再找配置表。

**🔑 schema 是动态的、按服龄迁移**（和 P2 静态分组完全不同）：新服开服即 schema **1**，随服龄逐级升 2→3→4…（数字越大服越老）。`schema_time` = 该服进入当前 schema 的时刻（例：1009302 于 2026-06-11 当天刚从 1 升 2；1007102 于 2026-06-07 从 3 升 4）。所以 schemaN 名单是**时变的**，每次要现查最新 dump，不能存死名单。
⚠️ **「schema3 后的服」= schema 编号往上（3、4、5、6…），即更老的服**（我曾理解反成"更新的服 s2+s1"被用户纠正）。映射对 id 单调：边界一侧全是 ≥3，另一侧全是 ≤2，所以可用 id 阈值切（2026-06-11 边界：id≤1008402 ⇒ schema≥3，id≥1008502 ⇒ schema≤2）。
2026-06-11 快照：s4=1003702~1007102(8服) / s3=1007302~1008402(7服) / s2=1008502~1009302(9服) / s1=1009402~1009602(3服)。
🔴 **「连续 id 区间」是错的——dump 里列出的服才是全集（2026-06-11 部署实测推翻）**：X2 合服极多，**iGame serverMgr 的 94 服名单含大量合服死 id**，给死 id 部署/发活动会逐服报 `server not found`（如 1000402~1003602 整段、1003802、1004902、1006302 等全死）。**用户 dump 本身 = 活跃服全集（27服），schemaN 名单照抄 dump 该 schema 的行，禁止按 id 区间从 iGame 名单推**。schema≥3 实际=15服：1003702,1004502,1005302,1005702,1006102,1006502,1006902,1007102 + 1007302,1007502,1007702,1007902,1008102,1008302,1008402（与 26占星上线表 15 服同构）。部署响应的 server not found 可反过来当活跃服探针。

## 附带坑：改 `~/.igame-auth.json` 别用 `Out-File -Encoding utf8`
PS5.1 会写 BOM，igame-query.js 解析 JSON 直接炸（`Unexpected token '﻿'`）。要用 `[System.IO.File]::WriteAllText($path,$content,(New-Object System.Text.UTF8Encoding $false))` 写无 BOM。
