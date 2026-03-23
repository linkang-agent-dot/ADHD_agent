# 配置换皮技能

触发词：换皮、配置换皮、换主题、reskin、这个配置换成XX、帮我分析换皮字段

> 本技能只负责**分析和生成**换皮后的配置行。导入到配置表的操作见 `config-upload` 技能。

---

## 换皮工作流（4步）

**S1 读原始行**

从用户给出的配置行（或 GSheet）中提取所有字段，识别每个字段的列类型。

**S2 按列类型决定处理方式**

| 列类型 | 换皮处理方式 |
|--------|------------|
| `base-ID` | **不换** — 沿用原值 |
| `A_STR_constant` | **必须新增** — 不能复用 |
| `A_MAP_filter` | **一般不换** |
| 活动行 ID | **换** — 分配新 ID |
| 父活动/关联 ID | **换** |
| 前置条件建筑 ID | **换** |
| 本地化 LC key | **换** — 改为新主题前缀 |
| 内容引用（task/package ID） | **换** |
| Banner 图片路径 | **换** |
| `A_INT_show_hud` | **换** |
| 常量数值（0/1/空字符串/空数组） | **不换** |
| 规则 LC key（`rule` 字段） | 同类型活动可不换 |
| 2119 关联 ID | 同类型活动可不换 |

**S3 追踪依赖链，不能只看当前表**

以 2112 为起点的完整追踪链：

```
2112
 ├── {"typ":"task","id":xxx}     → 2115（检查 condition 里的 2013 ID）
 ├── {"typ":"package","id":xxx}  → 2135（检查 head row col2 的 2011 ID）
 │         └── 2135 head row col2 (2011 ID) → 2011（检查 actv_id、recharge_actv）
 │                   └── 2011.condition (2013 ID) → 2013（确认道具 ID）
 │                   ⚠ 预购连锁礼包类型不走 2013，无需追踪
 └── A_INT_show_hud              → 换新 ID
```

每层都要向下追踪，漏追任意一层会导致新配置引用旧 ID。

**⚠ 特别注意：2112 ID 复用旧活动 ID 时**

如果新活动的 2112 行复用了旧活动 ID（而不是新分配），必须同步检查并修改：
1. `2135` 链式行 `condition.actvstart.id` → 改为复用的 2112 ID
2. `2011` 对应行 `A_MAP_time_info.actv_id` → 改为复用的 2112 ID

初始规划的新 ID 一旦废弃改为复用，2011 里 `actv_id` 仍指向废弃的旧规划 ID，是隐蔽的漏点。

**S4 输出换皮后的完整配置行**

- 待填字段用 `{待替换:说明}` 占位
- 列出所有需要新增的 LC key（给本地化同步）
- 列出所有整型 ID（`int id`，便于另外导表）
- **空字符串字段输出格式**：Tab 分隔行中，所有单独成格的 `""` 字段必须输出为 `'""` （加单引号前缀）。原因：直接粘贴 TSV 时 Sheets 会把 `""` 解析为空单元格；`'` 是 Sheets 的文本强制前缀，可确保单元格存储和显示都是 `""` 字符串，符合导表要求。

---

## 配置资源库

完整案例和 ID 对照存于：`c:\ADHD_agent\.cursor\config-library\`

```
config-library/
├── README.md              — 快速导航
├── reskin-rules.md        — 换皮规则详版
├── table-index.md         — 编号→页签速查
└── cases/
    ├── 2026_alien_monopoly_daily_pack/   — 异族大富翁每日礼包，5表完整配置
    │   ├── overview.md   — ID 对照总表 + 待填字段清单
    │   ├── 2112.md
    │   ├── 2115.md
    │   ├── 2135.md
    │   ├── 2013.md
    │   └── 2011.md
    └── 2026_easter_card_collection/
        └── localization.md
```

做新活动换皮时，先读 `overview.md` 对照 ID，再按需读各表 `.md` 文件。

---

## 收尾步骤（每次完成后必做）

每次换皮+导表完成后，主动检查并更新以下文件，把本次遇到的新情况、新 ID 规律、新坑沉淀进去：

| 文件 | 更新内容 |
|------|---------|
| `config-library/cases/<节日>/overview.md` | 补充本次活动的 ID 对照表、关键决策 |
| `config-library/reskin-rules.md` | 补充新规则或特殊处理方式 |
| `skills/config-reskin/SKILL.md` | 更新工作流（新增步骤/注意项） |
| `skills/P2-config-upload/SKILL.md` | 补充导表过程中遇到的新问题及解法 |

> 如果本次遇到了新问题（比如 GSheet 格式报错、tab 不对、ID 复用），一定要写进对应文件，不要等下次重踩。

---

## 导表注意事项（P2 导表）

换皮配置完成后，使用 `P2-config-upload` 技能导表。关键注意点：

- **已有行（updated）**：直接 `merge_rows.py` 按行 ID 替换，从 GSheet 重新拉取最新版本覆盖本地
- **新增行（added）**：`merge_rows.py` 只能处理 GSheet 里已有的行。若目标行尚未写入 GSheet，脚本会输出 `[WARN] not found anywhere`，此时需先让用户把行粘贴入 GSheet，再重新下载执行 merge
- 2135 等活动表的新行通常是换皮产出的全新 ID，用户需要先手动粘贴进 GSheet，才能走正常导表流程
