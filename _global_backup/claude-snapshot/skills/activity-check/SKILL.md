---
name: activity-check
description: 活动配置 ID 引用检查。验证活动配置中的各类 ID（task、drop、exchange、rank、retake、jump_link、actv_show_rank、drop_gacha、exchange_pkg、preview_reward 等）是否在对应的 Google Sheet QA 表中存在。触发条件：(1) 提到"活动检查"、"ID检查"、"引用检查"，(2) 提供一组活动配置 JSON 并要求验证，(3) 提到"检查QA表"、"验证配置"。
---

# Activity Config ID Check Skill

**Skill 路径**: `~/.claude/skills/activity-check`

## 用途

验证活动配置中引用的各类 ID 是否在对应的配置表 QA 页签中存在，防止配置错误导致活动异常。

## 前置依赖

1. **gws CLI** — Google Workspace CLI，用于读取 Google Sheets
   - 安装: `npm i -g @anthropic-ai/gws`
   - 需要 Google OAuth 授权

## 支持的 ID 类型与对应配置表

| typ | 配置表名 | Sheet ID | QA 页签名 |
|-----|---------|----------|-----------|
| task | activity_task | 1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY | activity_task_QA |
| drop | activity_drop | 1V7xDriTe0hGW3SF7ZPtk71-sFGyzpbbO47V6gLoBqVA | activity_drop |
| exchange | activity_item_exchange | 14IDttHNuHx1U2I1kHinkMLIA6Q4cKmZ8MLoMkgdTGfY | activity_item_exchange |
| retake | activity_asset_retake | 1ctEGsAU053iaCCTJeIU1qnp9zfyuURt7k8EzHkKzv2Y | activity_asset_retake |
| rank | activity_rank_rule | 1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M | activity_rank_rule（QA） |
| jump_link | activity_special | 1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc | activity_special_QA |
| actv_show_rank | activity_special | 1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc | activity_special_QA |
| drop_gacha | activity_special | 1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc | activity_special_QA |
| exchange_pkg | activity_special | 1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc | activity_special_QA |
| preview_reward | activity_special | 1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc | activity_special_QA |

## 配置表总索引

所有配置表的索引位于 **p2_gsheet_config** 总表：
- Sheet ID: `1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c`
- 页签: `fw_gsheet_config`
- 结构: `[分类, 表名描述, table_name, sheet_id, ?, 序号]`

如果遇到新的 ID 类型，可从总索引中查找对应的配置表。

## 工作流

### Step 1 — 解析输入

用户提供活动配置 JSON，格式为：
```json
[
  {"typ": "task", "id": 211586837},
  {"typ": "drop", "id": 212452200},
  {"typ": "exchange", "id": 21163351},
  ...
]
```

按 `typ` 分组，统计各类型的 ID 列表。

### Step 2 — 查询 QA 表

对每种类型，使用 gws 读取对应配置表的 QA 页签：

```bash
# 读取 ID 列（通常是 A 列或 B 列）
gws sheets +read --spreadsheet <sheet_id> --range '<qa_tab>!A:B'
```

### Step 3 — 验证 ID 存在性

将用户提供的 ID 与 QA 表中的 ID 进行比对：
- 找到：✅
- 未找到：❌（需要报告）

### Step 4 — 输出结果

汇总表格格式：

| 类型 | ID 范围 | 数量 | 结果 |
|------|---------|------|------|
| task | 211586837-211586868 | 32 | ✅ 全部找到 |
| drop | 212452200-212452201 | 2 | ❌ 未找到: 212452201 |

## 常见问题

### QA 页签名不固定

不同配置表的 QA 页签命名可能不同：
- `activity_task_QA`
- `activity_drop`（直接用表名）
- `activity_rank_rule（QA）`（带括号）
- `activity_special_QA`

先用 `gws sheets spreadsheets get` 获取页签列表，找到包含 "QA" 或 "master" 的页签。

### ID 列位置

- 大多数表的 ID 在 A 列（`A_INT_id`）
- 部分表的 ID 在 B 列
- 读取 A:B 两列，取第一列或第二列中的数字值

### 新增 ID 类型

如果遇到未知的 `typ`，从总索引表搜索：
```bash
gws sheets +read --spreadsheet 1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c \
  --range 'fw_gsheet_config!A1:F1500' | grep -i "<typ_name>"
```

## 示例

```bash
# 1. 获取配置表页签列表
gws sheets spreadsheets get --params '{"spreadsheetId":"1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY"}' \
  | python -c "import sys,json; d=json.load(sys.stdin); print('\n'.join([s['properties']['title'] for s in d.get('sheets',[])]))"

# 2. 读取 QA 表 ID 列
gws sheets +read --spreadsheet 1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY \
  --range 'activity_task_QA!B:B'

# 3. 验证 ID（Python 脚本）
gws sheets +read ... | python -c "
import sys, json
data = json.load(sys.stdin)
ids = set(row[0] for row in data.get('values', []) if row)
check_ids = ['211586837', '211586838']
for cid in check_ids:
    print(f'{cid}: {\"找到\" if cid in ids else \"未找到\"}')"
```
