---
name: ""
description: 任何任务（不只是BUG）完成时，遇到的坑/新规律必须立刻写入运维知识库（feedback/reference/SKILL.md），不等用户提醒
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9fa379f1-8095-4bed-9a37-401c299ba495
---

完成任务和更新知识库是同一个闭环，不是两件独立的事。**范围覆盖所有任务**：修 BUG、配置写入、导表、改字段、新功能配表、运维操作——任何一类，只要踩到坑或发现新规律，当场记。

**Why:**
- 2026-05-18 拓荒节换皮时多次"修完BUG就停"，没把新间接引用链/必检表写进 SKILL.md，直到用户追问。
- 2026-05-25 X3 累充隔离需求里，发现 openpyxl `read_only=True` 默认不返回公式缓存值，导致误判 ActvTask 594 只有1行（实际10行），用户提醒"每完成一个任务有坑就记"。

**How to apply:**
1. 任务完成后**立即**复盘：本次有没有踩到 KB 里还没写的坑？有就当场补。
2. 选对存放位置：
   - 字段/字段约束/表结构规律 → `reference_*.md`
   - 操作工具/库的踩坑（openpyxl/gws/COM 等）→ `feedback_*.md`
   - 跨任务的 workflow/规则 → SKILL.md 主文档
3. 不要只写 memory 笔记 — SKILL.md / table-reference.md / reference 是下次执行时实际读取的入口。
4. 判断标准：如果这个发现下次还会重现并影响结果，就必须当场写。
5. 写完同步更新 `MEMORY.md` 索引，否则新文件不会被检索到。
