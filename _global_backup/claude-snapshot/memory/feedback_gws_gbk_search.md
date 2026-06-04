---
name: gws 读取中文内容后关键词搜索失败
description: gws CLI 输出中文时是 GBK 编码，用 decode('utf-8','ignore') 处理后中文变乱码，导致关键词字符串匹配失败
type: feedback
originSessionId: 03f54909-5392-432f-954e-d30d028b3fc8
---
gws 读取含中文的 GSheet 内容时，stdout 是 GBK 编码。用 `decode('utf-8','ignore')` 处理后中文字段变乱码，`any(k in row[x] for k in keys)` 这类关键词匹配会全部失败，误以为数据不存在。

**Why:** 2026-05-25 查 X2 1011 占星节装饰 LC key 时，搜 `astro_2025_wall_decoration_1` 等 key 全部返回空，实际数据在 EVENT!B6503:C6526，用行号范围直接读才找到。

**How to apply:**
- 搜索 GSheet 内容时，不要依赖关键词匹配中文字段
- 正确做法：用用户提供的行号范围或 gid 直接读取（`range='SHEET!A6503:D6526'`）
- 如果必须搜索，先让用户提供精确行号范围，或用 gws_stdin.js 配合 node 处理编码
- 用 `decode('utf-8','ignore')` 只适合读纯 ASCII 字段（如数字 ID、英文 key 名）

## gws 其他用法补强（2026-06）
- **读含中文内容**：python 里把结果写成 UTF-8 文件，再用 Read 工具看（避开 stdout GBK 乱码）。这是默认做法，别直接 print 中文。
- **`spreadsheets.get` 响应过大会截断**导致 `json.loads`/`KeyError 'sheets'`：必须带 `fields` 限定，如 `{"fields":"sheets.properties(sheetId,title)"}` 只取页签名。
- **打开本机图片/文件**：用 PowerShell `Start-Process 路径`（`cmd /c start ""` 经常不弹窗）。
- **建页签/格式**：`['sheets','spreadsheets','batchUpdate']` + `{"requests":[{addSheet:...}/{repeatCell:...}/{updateDimensionProperties:...}]}`；写值 `values.update` + `{values,majorDimension}`。
