---
name: reference_x3_customparam_activity_pattern
description: X3「customParam 驱动可热部署活动」代码决策模板 — 可变运营参数从配表搬到 iGame 部署参数，零代码/零热更换参数；逆向自大哥竞猜重构
metadata: 
  node_type: memory
  type: reference
  originSessionId: aa81a569-cf03-433a-becf-37475d030549
---

# X3 customParam 驱动「可热部署活动」代码决策模板

**KB 全文**：`C:\ADHD_agent\KB\方法论\活动开发\X3活动代码架构_customParam驱动可热部署活动_决策模板.md`（+ 同目录 .html 可视化版）
**范例**：世界杯竞猜 ActvType=64；逆向自 zhangli(大哥) X3NEW-1432 commit `f6e2d08768a`；大哥原设计文档 `C:\x3-project\docs\plans\2026-06-18-worldcup-guess-customparam-refactor-design.md`

**模式一句话**：活动的可变运营参数（对阵/礼包ID/目标值/奖池ID…）通过 **iGame 后台 customParam(JSON)** 部署时传入，服务端读它建专属数据结构 → 换参数=改后台重部署，**零代码/零热更/零客户端打包**。替代"参数写死配表→改表→热更"老套路。

**何时套用**：活动结构固定、少量参数按场次/期次变、运营需高频换。

**核心九决策**（详见 KB）：D1 专属 Condition 入口不动通用流程(回滚易) / D2 payload 取最薄只传数据本质 / D3 新建独立 DTO / D4 proto 新 tag 顺序追加(先查最大tag,别复用旧) / D5 字段名贴数据本质(packA 不叫 teamA) / D6 反序列化+校验放 Condition 层不放共享 deploy handler / D7 原始 JSON 持久化到 server entity Data(跨重启复读) / D8 复用底层原语挂专属结构 / D9 配套 GM 命令本地复现 deploy。

**大哥这次优化了啥**：①换对阵 改配表+热更→iGame参数自助 ②数据结构 借进度礼包day0/1 hack→专属 WorldCupGuessData(tag62) ③砍76行ActvPack配表冗余(绕开不读) ④砍最终奖死代码(运营改BI筛名单邮件发奖)。手法=外科手术,通用进度礼包链路物理保留。

关联：[[project_x3_worldcup_activity]]（世界杯唯一入口·配置侧）、[[reference_x3_recharge_isolation]]、[[reference_x3_project_repo]]。GUI 拼界面另见同目录 `KB\方法论\活动程序开发\X3客户端GUI知识.md`。
