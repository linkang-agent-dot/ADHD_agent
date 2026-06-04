---
name: 2026拓荒节换皮踩坑总结与优化项
description: 占星节→拓荒节全套换皮过程中暴露的三类问题及修复方案
type: feedback
originSessionId: 03f54909-5392-432f-954e-d30d028b3fc8
---
## 模块一：活动换皮脚本（activity_reskin.py / run_all.py）

### 已修复

| # | 问题 | 修复 |
|---|------|------|
| 1 | 子表 ID 跨活动碰撞（每个活动独立查 tail，GSheet 没写入 tail 不变）| run_all.py 累积 next_id 传给下个活动 |
| 2 | 2116/2122/2118 的 id_col 配错（ID 不在 col[1]）| 逐表确认 id_col 修正到 X2_TABLES |
| 3 | base_activity_id 被全局替换（应保留源值）| clone_rows 增加 preserve_cols=[6] |
| 4 | 2013 反向查 idrange 范围过大（630 行污染）| Step 2 加 target ID 过滤 + Step 4 按跨度分段读 |
| 5 | tail 命令传了 --id-col 参数（tail 不支持）| get_tail_max_id 只传 --tab 不传 --id-col |

### 待优化

| # | 问题 | 优化方向 |
|---|------|---------|
| 6 | ID 替换链式错误（354→355→356...全变 359）| 替换时先建完整映射 dict，一次性 re.sub，禁止 for 循环逐个替换 |
| 7 | 不同活动对"哪些子表新建/哪些复用旧组件"没有配置入口 | JSON 配置增加 `reuse_types: ["drop","retake",...]` 字段，脚本根据此字段自动跳过对应子表 |
| 8 | Wonder 金蛋、BP 2130/2131/2118、行军特效等表不在自动追踪链路内 | COMPONENT_TABLE_MAP 补全：wonder_egg_drop→2124、battle_pass→2130→2131、rank→2122→2118 |
| 9 | 手动补配的行容易跟自动分配的 ID 碰撞 | 手动补配后把 next_id 写回 next_ids.json，或统一走脚本生成 |

---

## 模块二：GSheet 写入流程（write_activity.py）

### 已修复

| # | 问题 | 修复 |
|---|------|------|
| 1 | append INSERT_ROWS 插到表头而非表尾 | 禁用 append，改用 insertDimension + values.update |
| 2 | 备份页签命名 `xxx_bak_` 被 gsheet_query 优先选中 | 改为 `_bak_` 前缀命名 |
| 3 | 2115 写错页签（装备打造 vs 线上）| 修正 TABLES 配置为线上页签 |

### 待优化

| # | 问题 | 优化方向 |
|---|------|---------|
| 4 | 写前没检查目标行是否已存在，导致重复写入 | 写前读 B 列 ID，跳过已存在的行 |
| 5 | 删行按行号盲删，行号偏移导致误删 | 删前读目标行内容确认，或从后往前删 |
| 6 | 崩溃后未验证 GSheet 实际状态就重跑 | 脚本崩溃后强制验证模式：先检查已写入行数再决定续写/跳过 |
| 7 | 备份在首次写入之后才创建（污染后备份无效）| 备份必须在 **第一次写入任何行之前** 创建，且每个 spreadsheet 只备份一次 |
| 8 | JSON 太长超 Windows 命令行 8000 字符上限 | 超长行自动 fallback 到逐 cell 写入，或用临时文件 |
| 9 | 新行缺少 p2_title 空列导致列偏移 | 写入前校验列数 = 表头列数，不足则前补空列 |
| 10 | 克隆行列数不完整（源行 19 列只复制了 10 列）| 克隆时强制读源行全列（A:AZ），不截断 |
| 11 | 2118/2130/2131/行军特效不在 TABLES 配置里，手动写入绕过了安全机制 | TABLES 配置补全所有可能涉及的表 |

---

## 模块三：知识库 / 规则

### 待补充

| # | 内容 | 位置 |
|---|------|------|
| 1 | X2 各表的 id_col 和 QA 页签名完整对照表 | table-reference.md 补充 id_col 和 tab 映射 |
| 2 | 每个活动类型的子表依赖链（哪些新建/哪些复用）| config-library/cases/2026_pioneer_reskin_from_astrology/ 下存档具体复用决策 |
| 3 | GSheet 写入安全规范（备份→写入→验证→清理备份）| feedback_gsheet_write_safety.md 已建，需补充本次新教训 |
| 4 | 掉落转付费/强消耗/累充等"部分复用"活动的复用规则 | config-library/cases/ 下存档具体决策 |
| 5 | Wonder 金蛋追踪链：2112→2121(wonder_egg_drop)→2115(task)→2124(drop) | table-reference.md 追踪链补充 |
| 6 | BP 追踪链：2112→2130→2131 + 2122→2118 | table-reference.md 追踪链补充 |
| 7 | 行军特效表(1365)/FurnitureBuild(1187)/大富翁地图(2151) 的 SheetID 和字段 | table-reference.md 补充 |

---

**Why:** 2026-05-18~19 拓荒节换皮，20个活动553行配置，过程中暴露了脚本、写入、知识库三个层面的系统性问题。

**How to apply:** 下次换皮前先过这份 checklist，按模块逐一确认优化项是否已落地。
