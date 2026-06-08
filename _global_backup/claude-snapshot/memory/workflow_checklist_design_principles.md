---
name: double-check
description: 写或优化任何 quality-gate 验收清单、checker prompt、double-check list 时套这四条；让清单同时变可移交+可靠
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e64e6447-8b1d-4f10-9e1a-491ee73228ca
---

写/优化任何验收清单（quality-gate 的 `*-checklist.md`、task-checker/l1-game-ux-checker 喂的 prompt、任何 double-check list）时套这四条。2026-06-05 用它把 config/design-doc/i18n 三份清单升到 v2。

**根因认识**：清单「只有我能用」和「double-check 还漏」是**同一个病**——清单写的是**结论**（"检查引用链"），依赖操作者脑里的上下文。把结论改成「为什么+怎么查+对错长什么样」，就同时变得可移交（别人/agent 能跑）+ 可靠（可证伪）。

**四原则**：
1. **加工作姿态 preamble（最高杠杆）**：把 checker 从"检查是否通过"扭成**默认有罪**——"假设它已经坏了，找不到证据证明没坏才 pass，别找它对的证据"。再加"只信真源不信 producer 摘要""失败模式驱动"。不加新规则就升级了每一条的跑法。
2. **每条 block 强制留证据**：必须**打印实际值/命中位置原文**（分支名、seq 序列、MailID 值、三层各自的值、命中的 key+列）。没贴实际值的 pass 一律记 cannot_verify。= 能"响亮地失败"。
3. **内联「防什么事故(why)」**：把每条防的坑写进条目本身（"seq跳号→服务端静默吞奖励"），不要只指向 memory。条目自包含 → 别人/别的 agent 直接能跑（解决"只有我能用"）。
4. **加开放项 + 剪枝（防老化+防肥胖）**：①开放项=每轮必问"有没有清单**没覆盖**的新失败方式"，捞到的报人确认后才加（不自动膨胀）；②剪枝=每条记"上次命中日期"，连续≥10轮没 fire 的非 P0 项评审降级/删除。清单从此**有进有出**。

**架构层面别动**：producer + 独立 checker agent（沙箱只读、判定与执行物理分离）是对的，优化只在 check 的内容/prompt，不在架构。价值全在第二遍的"视角独立/对抗"，不在"看了两遍"——同一 lens 查两遍只抓错别字。

落地文件：`C:\ADHD_agent\.claude\quality-gate\*-checklist.md`。相关 [[project_quality_gate_and_interaction_module]] [[feedback_verification_end_to_end]] [[feedback_proactive_knowledge_update]]。
