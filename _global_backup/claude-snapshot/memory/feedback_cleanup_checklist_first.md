---
name: feedback-cleanup-checklist-first
description: "Before deleting files, show user a checklist of what to keep vs delete for confirmation"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 03f54909-5392-432f-954e-d30d028b3fc8
---

删除文件/清理中间产物前，先列一个 checklist 给用户确认，标注"保留"和"删除"分类，等用户确认后再执行。

**Why:** 2026-05-25 行军表情清理时误删了「参考」文件夹和已确认的速度预览视频，用户无法恢复。shutil.rmtree 绕过回收站，永久删除。

**How to apply:** 每次用户说"清理/删中间产物"时，先列出目录下所有文件，标注建议保留/删除，等用户确认再执行。绝不擅自判断什么是中间产物。
