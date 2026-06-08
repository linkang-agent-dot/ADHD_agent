---
name: x2-city-skin
description: X2 节日主城皮肤从美术资源→DK→city_skin→item 的完整配置链，含表号/字段/陷阱，节日换主城皮肤时套用
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0a30c6e6-6e39-49a1-a271-b75401d58a68
---

X2 节日**主城皮肤**(大地图建筑外观)换皮完整链路。2026-06 拓荒节(labor)实战沉淀，对齐占星节(astrology)样板。

## 美术资源三族(每节日一套，美术交付)
client 路径 `Assets/x2/Res/`：
- `map/CityBuilding/X2_Map_{Theme}01/` — 大地图远景建筑(单模型)
- `Shop/Town/Building/X2_T_Shop/X2_T_Shop_{Theme}01/` — 主城详细建筑(LOD0/Mesh_LOD0/1/Base + 阴影 + 4级变体01-04)
- `Effect/Prefab/Shop/Fx_Shop_Map_{Theme}.prefab` + `Fx_Shop_{Theme}_Glow.prefab` — 大地图/主城特效
- **2D 道具图标**：`UI/TextureNew/Decoration/{Theme}_icon_building.png`(单张方形 PNG, Sprite/2048/格式50) — 易漏，美术常只给3D不给这张；可用 grfal 拿建筑模型生图→抠图代生
  - ⚠️ **{Theme} 美术前缀≠配置前缀**：拓荒节配置用 `labor`(event_labor/LC_EVENT_labor_2026)，但**美术资源前缀是 `Pioneer`**(占星=Astrology)。找图按美术前缀，别用配置惯性猜 `Labor`。
  - ⚠️ **gacha 皮肤奖励界面的这张 icon 是 prefab 里写死的贴图引用，不走 DK**：`Assets/x2/Res/UI/Prefab/Activity/UIActivityLaborGacha.prefab` 内 `m_Sprite` 直接指 `Decoration/{Theme}_icon_building.png` 的 GUID。换节日要手动在 Unity 把这个 sprite 引用换成新主题图（2026-06-04 拓荒 commit 1eecfe36）。

## DK = P2 数字系统，一个 key 挂 5 型(见 [[x2-dk-p2-dk-manager]])
占星节样板 key=1511020867；拓荒节=1511094083(全局max+1)。同一 key 在 5 个 Display_*.asset + Path_*.asset：
| Type | 指向 |
|---|---|
| Prefab | X2_Map_{Theme}01.prefab |
| PrefabShow | X2_T_Shop_{Theme}01_Base.prefab |
| Icon / IconBg / UIPrefab | {Theme}_icon_building.png(都指同一张2D图) |
- Display_Prefab/PrefabShow 文件内混用两种格式(单引号`- '{...}'` / 双引号转义`- "{\"...\"}"`)，追加时匹配该文件末行格式即可，Edit 工具能跨 unicode 转义匹配
- 录完必须 Unity Ctrl+Shift+E 导出 → 验证 Path_*.asset 有该 key

## 配置两表
- **city_skin 表号 1312**，QA GSheet `187tnelpSQv_QxT6RKysEKMS5V_Xs2XjScydRl2AX_UQ`/tab city_skin
  - 列：Id/Comment/Class/DisplayKey/Quality/SkinLevel/LcName/LcDesc/DisplayOrder/CollisionRadius/ExclusionRadius/StatusActive/InnateEffect/Awards/Items/UserLabels/CanTransformation/TransformationCost/Preview/ActivityId
  - GSheet 数据有前导 marker 列(A空)，Id 在 B；tsv 同样首列空
  - DisplayKey=SkinLevel skin=新DK；LcName/Desc=`LC_EVENT_{theme}_2026_city_skin_title/desc`(本地化常已就绪)；Items=该皮肤的 item ids；UserLabels=皮肤自身id；数值(StatusActive建造/训练加速+citybeauty / InnateEffect / TransformationCost 11119056×50)换皮原样复用
  - ⚠️ **city_skin 表只留当前活跃皮肤(~5行)，旧节日皮肤会被删**；但 item.tsv 里旧节日皮肤item仍引用旧 city_skin id → **新皮肤 id 不能挑"看起来空"的，必须扫 item.tsv 全部 city_skin 引用取真正没用过的**(拓荒踩坑：13121048/49 是退役万圣节、仍被万圣item引用)
- **item 表号 1111**，QA GSheet `1pm0nztHsjpHmFBEmx-bLtP7Zjf4GFC67wo-sUmqY7Fs`/tab item
  - 皮肤item(永久版+限时版)：col G DisplayKey=图标DK、col R UseLabels=`["bag",cityskinId]`、col S CategoryParam effect=`{"effect":[{"typ":"city_skin","id":cityskinId,...}]}`
  - 换皮即改这3处指向新DK+新cityskin id；不同节日的同型item(永久/2天)bag+effect串可能完全相同 → tsv 编辑必须**整行替换(靠Id锚定)**，不能按子串replace

## 写入与导表
- X2 真源是 QA GSheet，但**配置改动只 commit tsv**(CI 重新生成 bytes，类 X3)；近期 commit `f18ddd775` 改 item 只动 item.tsv 证实
- GSheet 写用 [[gsheet-toolkit]] gsheet_utils.py(写前 backup_tab、写后读回验证)；tsv 用 Edit 整行替换/追加(注意 CRLF)
- 表号→QA表用 `gsheet_query.py resolve <表号|表名>`
- 提交前 `python scripts/check_tsv_format.py <files>` 跑格式+跨表校验

关联 [[x2-dk-p2-dk-manager]] [[gsheet-toolkit]] [[配置表知识库路径]]
