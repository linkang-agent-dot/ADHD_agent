---
name: feedback_kb_summarize_dont_ask
description: "归纳/沉淀知识库是默认动作，不要问用户\"要不要回写memory\"，直接做"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 31d5e8dd-416b-4c63-9820-dda4e5b2521d
---

沉淀知识库（回写 memory / 更新 reference 文件 / 记录新链路·列含义·踩坑）是**默认动作，直接做，不征求用户同意**。

**Why**：用户明确说"这种肯定不用问我，直接总结知识库就好了"。我之前在任务收尾反复问"要我把XX回写进memory吗？"——这是把本该自动做的接管化归纳抛回给用户决定，等于没接管。和 [[feedback_proactive_knowledge_update]] + CLAUDE.md 收口④(归纳默认直接做) 一致。

**How to apply**：发现新链路/列含义/纠错/方法论 → 当场更新对应 memory/reference 文件 + MEMORY.md 一行指针，最多一句话带过"已沉淀到 X"，**不要用提问句结尾**。用户把关靠每周归纳清单兜底，不逐次打扰。只有当沉淀涉及"删/改用户手写的内容块"时才先问（见 [[feedback_ask_before_modifying_user_content]]）。
