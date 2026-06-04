---
name: GSheet append 行顺序陷阱
description: 往 Google Sheets 追加行时，INSERT_ROWS 会插到数据区开头而非末尾，导致行顺序颠倒
type: feedback
originSessionId: 5ac7adf1-5a30-46dc-a84b-9b7df231fa05
---
**不要用 `insertDataOption: INSERT_ROWS` 追加数据到表末尾。**

**Why:** INSERT_ROWS 会在 API 检测到的"表格边界"位置插入新行，实际效果是插到数据区开头（表头后第一行），而不是末尾。结果：新行排在旧行前面，ID 顺序颠倒，还可能因 OVERWRITE 补救操作覆盖掉原有数据（本次占星节1107/1123均踩坑）。

**How to apply:** 追加新行到表末尾时，正确做法是两步走：
1. `batchUpdate → insertDimension`：在最后一条数据行的下一个位置插入 N 行（0-based startIndex = last_data_row_index, endIndex = last_data_row_index + N）
2. `values.update`：把数据写入到这 N 行

不要用 `values.append` + `INSERT_ROWS`，也不要用 `values.append` + `OVERWRITE`（OVERWRITE 会从头覆写）。
