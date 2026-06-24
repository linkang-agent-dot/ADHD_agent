# 航海之路(大富翁 ActvVoyage)换皮 可复用脚本 — 2026深海节实现

下次节日换皮大富翁照搬，改名称/id偏移即可。判据=隔离不动老配置。

| 脚本 | 作用 | 关键 |
|---|---|---|
| cfg_voyage_deepsea.py | 结构隔离: 克隆IslandGroup1→2(+100) + EventGroup99-106→199-206(行id+100000) + repoint ActvVoyage/ActvOnline | EG→岛型→DK映射;老配置零改动;断言+dry-run |
| dk_voyage_deepsea.py | 6个DK入库(Display+Path纯追加双补·meta克隆换guid) | 不动现有/损坏条目;入库后必Unity Ctrl+T |
| island_names_cn.py | 改ActvVoyageIsland group2母版为深海cn(按IslandType) | 母版不读·只为i18n源+编辑器可读 |
| island_i18n.py | Text表追加i18n(同名岛**合并key** TXT_A\|TXT_B·16语言) | 老岛同类故事最小改;status=AI |

落地顺序: cfg → island_names → island_i18n → (ExportTable验证) → dk入库 → commit → push → jolt → 用户Ctrl+T。
唯一入口=memory project_x3_deepsea_festival.md「大富翁(102802)岛屿换皮」章节。
