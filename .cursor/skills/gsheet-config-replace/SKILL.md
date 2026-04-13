---
name: gsheet-config-replace
description: P2/X2 配置表批量替换工具。在 GSheet 单元格内做字符串替换（支持 JSON 内的 ID 替换），写回 GSheet。触发词："批量替换"、"ID替换"、"配置替换"、"gsheet replace"。
---

# GSheet 配置表批量替换

在 P2/X2 配置表的 GSheet 中批量替换字符串（如道具 ID），支持精确匹配避免误替换。

## 输入协议

调用方需提供 JSON：

```json
{
  "project": "P2",
  "tables": ["2115", "2013"],
  "sheets": "*",
  "columns": "A:AZ",
  "replacements": {
    "111110002": "111110305",
    "111110003": "111110306"
  },
  "matchMode": "exact",
  "dryRun": true
}
```

| 字段 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| project | ✓ | - | `P2` 或 `X2` |
| tables | ✓ | - | 表编号数组，如 `["2115", "2013"]` |
| sheets | - | `*` | 页签名数组或 `*`（所有未隐藏页签） |
| columns | - | `A:AZ` | 扫描列范围 |
| replacements | ✓ | - | 替换映射 `{旧值: 新值}` |
| matchMode | - | `exact` | `exact`=精确边界匹配，`simple`=简单替换 |
| dryRun | - | `true` | `true`=只报告不写入，`false`=实际写入 |

## 执行流程

```
S1 解析输入 → S2 查表索引获取 SheetID → S3 获取页签列表 → S4 扫描替换 → S5 写回/报告
```

### S1 解析输入

从调用方获取 JSON，校验必填字段。

### S2 查表索引获取 SheetID

**P2 索引表**：
```powershell
$env:GOOGLE_WORKSPACE_PROJECT_ID = 'calm-repeater-489707-n1'
gws sheets spreadsheets values get --params '{"spreadsheetId": "1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c", "range": "fw_gsheet_config!A1:F900"}'
```
- A列=编号，B列=页签名，C列=SheetID

**X2 索引表**：
```powershell
gws sheets spreadsheets values get --params '{"spreadsheetId": "1z2-AK4dFgdzd7U11uCgYzLpj3Qopkv9Rr-SbA7iLIMc", "range": "fw_gsheet_config!A1:E600"}'
```
- A列=编号，C列=表名(编号_x2_标识)，D列=页签名，E列=SheetID

### S3 获取页签列表

```powershell
gws sheets spreadsheets get --params '{"spreadsheetId": "<SheetID>"}'
```

从返回的 `sheets` 数组中筛选：
- `sheets` = `*` 时：取所有 `sheetProperties.hidden != true` 的页签
- `sheets` = 数组时：只取指定页签

### S4 扫描替换

对每个页签读取数据：
```powershell
gws sheets spreadsheets values get --params '{"spreadsheetId": "<SheetID>", "range": "<页签名>!<columns>"}'
```

遍历每个单元格，执行替换：

**exact 模式**（推荐）：
```python
import re
# 精确边界匹配，避免 111110002 匹配到 1111100021
pattern = r'(?<![0-9])' + re.escape(old_value) + r'(?![0-9])'
new_cell = re.sub(pattern, new_value, cell)
```

**simple 模式**：
```python
new_cell = cell.replace(old_value, new_value)
```

记录所有变更：`{sheetId, 页签, 行号, 列号, 原值, 新值}`

### S5 写回/报告

**dryRun=true**：输出变更报告，不写入
```
📊 扫描完成
表 2115 (activity_task):
  - activity_task_QA!C15: "111110002" → "111110305"
  - activity_task_QA!F23: "111110003,111110004" → "111110306,111110307"
表 2013 (iap_template):
  - iap_template_QA!D8: ...
总计: X 个单元格将被修改
```

**dryRun=false**：批量写入
```powershell
gws sheets spreadsheets values batchUpdate --params '{"spreadsheetId": "<SheetID>", "valueInputOption": "RAW"}' --json '{
  "data": [
    {"range": "页签!A1", "values": [["新值"]]},
    {"range": "页签!B2", "values": [["新值"]]}
  ]
}'
```

## 脚本

主脚本：`scripts/gsheet_replace.py`

```powershell
# 执行替换（dryRun）
python C:\ADHD_agent\.cursor\skills\gsheet-config-replace\scripts\gsheet_replace.py --config replace_config.json

# 实际写入
python C:\ADHD_agent\.cursor\skills\gsheet-config-replace\scripts\gsheet_replace.py --config replace_config.json --write
```

## 回复格式

**dryRun 模式**：
```
📊 扫描完成（dry-run，未写入）

表 2115 (activity_task) - SheetID: xxx
  页签 activity_task_QA: 15 处替换
  页签 activity_task_dev: 3 处替换

表 2013 (iap_template) - SheetID: xxx
  页签 iap_template_QA: 8 处替换

总计: 26 处替换，涉及 2 张表 3 个页签

确认写入请重新执行并设置 dryRun: false
```

**写入模式**：
```
✅ 批量替换完成

表 2115 (activity_task): 18 处已写入
表 2013 (iap_template): 8 处已写入

总计: 26 处替换已写入
```

## 注意事项

1. **务必先 dryRun**：确认替换范围正确后再实际写入
2. **精确匹配**：默认 `exact` 模式避免 `111110002` 误匹配 `1111100021`
3. **备份**：写入前建议在 GSheet 创建版本历史
4. **权限**：需要 GWS 写入权限（`gws auth login` 已授权）

## 示例

**科技节→复活节 ID 替换**：
```json
{
  "project": "P2",
  "tables": ["2115", "2013"],
  "sheets": "*",
  "columns": "A:AZ",
  "replacements": {
    "111110002": "111110305",
    "111110003": "111110306",
    "111110004": "111110307",
    "111110005": "111110308",
    "111110006": "111110309"
  },
  "matchMode": "exact",
  "dryRun": true
}
```
