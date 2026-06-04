---
name: 批量补发邮件 skill
description: iGame 批量发邮件导入表生成 skill 的位置与关键兼容性约束
type: reference
originSessionId: 2ca32c0f-5c2d-4c7f-b97a-c22e1f54121c
---
## Skill 位置
- 入口：`~/.claude/skills/bulk-mail-reissue/SKILL.md`
- 脚本：`~/.claude/skills/bulk-mail-reissue/generate.py`
- 用法：`python ~/.claude/skills/bulk-mail-reissue/generate.py <源CSV> [--output <路径>] [--map server=...,user=...,asset=...,amount=...]`

## 场景
运营/数据给一张"谁该补发什么道具多少个"的 CSV，要转成 iGame 批量发邮件工具能吃的导入表。

## iGame 导入表格式硬约束（踩过的坑）
1. **文件编码必须 GBK**（不是 UTF-8）
2. **逗号分隔**（不是 Tab，即使口头叫"TSV"）
3. **JSON 字段必须 CSV 引号转义**：外层 `"..."`，内部 `"` → `""`。否则奖励被切到错误列
4. **不聚合** — 同一玩家多条记录保持分行，每行一封邮件
5. 输出 6 列：`服务器 ID,玩家 ID,玩家信息,标题信息,附件资产信息,自定义`，奖励 JSON 在"自定义"列

## 参考模版
`C:\Users\linkang\Downloads\[模版]批量导入玩家和道具附件.csv`（GBK 编码的 CSV）

## ⚠️ 补发前必查：reason 全量核查规则

**背景**：P2 复活节补发事故中，计算补发量时只查了活动系统的 reason（`oap_recharge`），漏查了遗失奖励邮件的 reason（`mail_event_reissue`），导致 265 人收到 2 倍补偿，需事后扣回。

**规则**：每次补发前，必须枚举目标道具**所有可能的来源 reason**，逐一查询已发记录，汇总后再计算差额。

常见 reason 通路（不同活动可能叠加）：
| reason | 来源 |
|--------|------|
| `oap_recharge` | 活动系统自动发放（返还/奖励） |
| `mail_event_reissue` | 遗失奖励邮件系统补发 |
| iGame GM 导入 | 手动补发（reason 视操作类型而定） |

**执行 checklist**：
- [ ] 列出目标道具的所有 reason，SQL 用 `GROUP BY reason` 先确认有哪几种
- [ ] 按每个 reason 分别查已发量，全部加总为 `already_sent`
- [ ] 补发量 = `max(0, owed - already_sent)`，而非直接用 owed
- [ ] 生成导入表后，再用 already_sent + 本次发放量 与 owed 做交叉验证
