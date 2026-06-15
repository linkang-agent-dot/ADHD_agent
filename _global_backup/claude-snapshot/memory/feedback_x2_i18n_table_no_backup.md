---
name: feedback_x2_i18n_table_no_backup
description: X2/P2 本地化表(1011 i18n)改文案时不需要 duplicate 备份页签，直接改
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ae0d870a-2f33-45ca-8d9c-4d2141697c96
---

改 X2/P2 **本地化表 1011（i18n，含 EVENT/METRO/MENU 等页签）**的文案时，**不需要 duplicate 备份页签**，直接在真源页签改即可。

**Why:** 用户 2026-06-09 明确「本地化这张表不备份」。i18n 表改动走导表可回滚、且备份页签多了反而污染（1011 已有 54 个页签、backup 页签会干扰 gsheet_query 默认选中页判断）。

**How to apply:** 改 1011 文案前不再走 `backup_tab`/`duplicateSheet`。注意这条**只覆盖 1011 本地化表**；其它配置表(2112/2013/2135 等)仍按 [[feedback_gsheet_write_safety]] 先备份。

关联：[[x2-config-library]]（i18n 真源页签陷阱）、[[feedback_gsheet_write_safety]]
