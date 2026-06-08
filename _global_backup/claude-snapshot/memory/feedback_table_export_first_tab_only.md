---
name: feedback_table_export_first_tab_only
description: P2/X2 导表只导 GSheet 第一个页签；导非首页签要置顶，全部导完后还原页签顺序+删备份表
metadata: 
  node_type: memory
  type: feedback
  originSessionId: df6396f5-88bf-4819-8a0f-26a5f763f3b5
---

P2（GSheetDownloader）和 X2（fwcli）导表**只读 Spreadsheet 的第一个（最左）页签**。要导某张表的**非首个页签**（临时/审核 tab、多页签表如 2135 的非首页签）时：

1. **导前先记录原始页签顺序**（拉 `sheets[].title/index` 存下来），全程对页签顺序保持清晰。
2. 把目标页签**置顶到第 1 位**（或 duplicateSheet 复制一份置顶当「备份表」导）。
3. 导出。
4. **导完恢复原状 —— 仅当本次要导的页签全部导完后才做**（中途还有别的页签要导就先别还原，攒到最后一次性恢复）：①还原页签顺序 ②删除备份表。

**Why:** 用户 2026-06-04 确认导表默认行为就是导第一个页签；漏还原会污染表结构、留垃圾备份表。P2 已知现象 `[WARN] not found anywhere`/无 diff 多半就是数据在非首页签 Downloader 读不到。

**How to apply:** 已固化进两个导表 skill 的「核心机制」块 —— `C:\ADHD_agent\.cursor\skills\P2-config-upload\SKILL.md` 与 `C:\ADHD_agent\.cursor\skills\x2-config-download\SKILL.md`。X3 走 tsv 缓存不适用本条。相关 [[workflow_p2_table_import]] [[workflow_x2_table_import]]。
