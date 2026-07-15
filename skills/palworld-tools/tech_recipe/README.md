# 帕鲁 科技树 + 配方 数据（可复用刷新）

给「生产流水线一图流」HTML 供数据。1.x 版本更新时重跑刷新。

## 文件
- `tech_data.js` — 80级/588项科技逐级索引 `TECHIDX=[[lv,[[名,类],...]]]`
- `tech_clean.json` — 同上的 JSON 源
- `recipe_data.js` — **1366项真配方** `RECIPE={名:[[料,量]]}` + `KNOWN`(1988物品集)，页面直接内联这个
- `recipe_map.json` — 配方 JSON 源（含空配方=原料）
- `_fetch_cats.py` — 抓 catalog 分类配方（断点续，读/写 recipe_map.json）

## 数据源（全 paldb.cn，浏览器UA urllib 直抓，不挡）
1. **科技树**：`/technologies` — Next.js，`<h2>Lv.<!-- -->N</h2>`分级 + `<img alt="科技名" src=".../类型/...">`。⚠过滤 footer "公安备案"。
2. **配方**：`/catalog/<slug>` — 配方内嵌 self.__next_f JSON：`{"name":"X","attributes":{"科技":"N"},"recipes":[{"material":"Y","count":"Z"}]}`

## ⚠️ 关键坑
- **23个 catalog slug 从 `sitemap.xml` 的 `<loc>` 挖**，别猜！页面导航只露 material/production/weapon 三个。
- **鞍具(112项)在 `/catalog/key-item`**（归"关键道具"，不叫 saddle）。
- 带连字符 slug：`construction-schematic` / `sphere-module` / `pal-building` / `key-item`。
- 解析用 `(?="name":")` 切块，每块找 `"recipes":\[(.*?)\]`——**别用 `[^\[]*?`**（物品描述里的 `[` 会截断导致漏解析）。
- 剩 61 项 "XX套组/套装" = 打包解锁，本就无单一配方（组内部件在 foundation/furniture 分类各自有配方）。

## 刷新流程
```
python _fetch_cats.py   # 断点续；先删 recipe_map.json/_cats_done.json 从零跑
# 全 23 slug: material production weapon armor accessory food sphere ammo furniture
#   foundation defense infrastructure lighting storage glider consumable other
#   ingredient key-item construction-schematic sphere-module pal-building schematic
# 再从 recipe_map.json 生成 recipe_data.js（见 memory project_palworld_guide）
```
