# X3 Bingo 101831 误关联 TimeCycle 1832

- 日期：2026-08-05
- 任务：切 dev 并在本地 3080 部署新 Bingo 活动。
- 现象：向用户说明配置链时，把同批创建的 `TimeCycle 1832` 表述成 Bingo 101831 的关联项；用户纠正“1832 没有关联就别乱发出来”。
- 根因：沿用了换皮档案里“AO 101831 → Puzzle 1831 → TimeCycle 1832”的错误摘要，没有以实际字段引用复核。实际 `ActvOnline 101831.TimeController=0`，`ActvPuzzle 1831` 表也没有 TimeCycle 引用字段。
- 处理：本轮部署与汇报只使用 `ActvOnline cfgID=101831`；不再把 1832 当作关联 ID。同步修正马戏节换皮档案中的错误链路描述，配置本身不擅自删除。
- 状态：open
