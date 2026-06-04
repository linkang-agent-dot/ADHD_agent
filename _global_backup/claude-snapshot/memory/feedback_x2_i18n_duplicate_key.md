---
name: x2-i18n-key
description: X2 1011 i18n 表同一 LC key 出现多行时，fwcli 生成取首条，常显示成旧/错值；排查皮肤名等显示异常时必查重复 key
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f5d0e986-b7f5-42c6-ab46-30c79d5d6a9b
---

X2 的 1011 i18n 表（SheetID `1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg`，文案在 EVENT 页签）里，**同一个 LC key 可能被写了多行**（换皮/复制模板时遗留：模板占位行 + 节日主题行各一条）。

**两层危害（后者更狠）：**
1. **构建成功时**：fwcli 生成 cn.tsv 按 key 取**首条（行号靠前那条，通常是占位旧值）**，游戏里显示成占位/旧值。
2. **构建失败时（更隐蔽）**：cn 列只要有重复 key，fwcli i18n 阶段直接 **`download i18n fail` 整表不落盘**，cn.tsv/各语言 tsv 全保持上一次旧版——**整个节日文案都进不去游戏**。而 xlsx 下载那步仍显示 successful、EXITCODE=0，极易误判导表成功。

2026-06 拓荒节实例：EVENT 页签 labor_2026 系列有 **17 个重复 key**（city_skin/march_skin/floor/wall/decoration 的 title+desc），规律=小行号(7365~7399)占位通用值（装饰物/墙纸/行军特效…）+ 大行号(7476~7492)拓荒节主题值（拓荒节舞台/拓荒先锋…）。这 17 个重复让 i18n 构建一直失败，**整个拓荒节文案从没进过游戏**。修复=删掉 17 条占位行（**从大到小删避免行号漂移**），重跑导表即 finish。

**Why:** 换皮后"文案改对了但游戏里还是旧/占位值"的头号根因是重复 key——可能是取首条显示错，更可能是导表整表失败而你以为成功了。
**How to apply:**
- 排查 X2 任何文案显示成旧值/占位值时，先整列读 EVENT!A:C 按 key 精确匹配，确认该 key 是否有 >1 行。
- 删重复行前二次确认行的 key+cn，i18n 按 key 取值非按行号引用，删错值条是正解。
- 真实 key **无 `EVENT_` 前缀**（EVENT 是页签名）；resolver 默认页签是污染备份页签，读写必须显式指定 EVENT。
- 改既有 key 用 `values.update` 按行覆写，禁止 append（否则再造重复）。详见 [[workflow_x2_table_import]]。
- **每次 X2 i18n 导表后必看 fwcli 输出有没有 `download i18n fail`**——有就是 cn 列有重复 key，报的 key 全列出来去重再重跑；别只看 xlsx successful / EXITCODE=0 就当导成功。
- 删重复行时按行号**从大到小**删（deleteDimension startIndex 0-based），避免删上面的行导致下面行号漂移。
