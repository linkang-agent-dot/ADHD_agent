---
name: gsheet-toolkit
description: GSheet 读写统一工具 gsheet_utils.py 的位置/函数/封装的坑——所有 GSheet 读写先用它，别再现写一次性脚本
metadata: 
  node_type: memory
  type: reference
  originSessionId: b8252c09-48d4-4775-920f-56c1d0a8a710
---

GSheet 读写**统一工具**：`C:\ADHD_agent\scripts\gsheet_utils.py`（与 gws_stdin.js 同目录）。
**任何 GSheet 读写先 import 它，别再现写一次性脚本**——下面 5 个坑反复踩过（[[feedback_gws_gbk_search]] / [[feedback_gsheet_write_safety]] / [[feedback_gws_angle_bracket]]），已全部固化进工具。2026-06-03 大富翁策划案过审时建立（之前每次现写脚本、重踩 batchGet 崩 / 控制台乱码 / 手算行号错位）。

## 用法（库）
```python
import sys; sys.path.insert(0, r'C:\ADHD_agent\scripts'); import gsheet_utils as gs
gs.list_tabs(SID)                               # [(gid,title,rows,cols),...]
gs.get_values(SID, '页签', 'A1:K90')             # 读 → 二维数组（空范围 []）
gs.dump_tabs(SID, [('页签','A1:I90')], out)      # 多页签 dump 到 UTF-8 文件（带坐标，避乱码）
gs.find_row_by_value(SID, '页签', 'B', '某项')    # ★按内容定位行号(1-indexed)，改格前用它，别手算
gs.update_cell(SID, '页签', 'B17', '新值')
gs.update_range(SID, '页签', 'A48:K64', rows2d)  # 写矩形
gs.append_rows_safe(SID, '页签', rows)           # 追加到表尾（禁 append INSERT_ROWS）
gs.backup_tab(SID, '页签')                       # 备份 → _bak_MMDD_页签（写前必做）
gs.delete_rows(SID, '页签', [(218,227),(2,139)]) # 删行（闭区间·自动从后往前）
gs.ensure_grid(SID, '页签', rows=72, cols=11)    # 扩展行列（写超范围前调）
sid, url = gs.create_spreadsheet('表标题', tabs=['页签1','页签2'])  # 新建表（tabs可选），返回(id,url)
```

## 用法（命令行只读速查）
```
python C:\ADHD_agent\scripts\gsheet_utils.py tabs <SID>
python C:\ADHD_agent\scripts\gsheet_utils.py dump <SID> "<页签>!A1:K90" [out.txt]
```

## 封装的 5 个坑（别再踩）
1. 传输走 **node + gws_stdin.js**（stdin 传 payload），不用 gws.cmd —— gws.cmd 角括号 `<>` 被 CMD 当重定向毁 JSON。
2. raw stdout **本身就是 UTF-8**，直接 decode，不试 gbk；中文"乱码"只在 print 到控制台时，读结果用 dump_tabs **写文件**看。
3. 读用 **single get**，不用 batchGet —— ranges 数组里中文页签名被 gws 序列化破坏，报 "Unable to parse range"。
4. 改格用 **find_row_by_value 按内容定位**，别手算行号（大富翁验收 #14/#15 被改到错行的教训）。
5. 写禁 append INSERT_ROWS；找末行遍历 ID 列不用 len(values)（空行截断）；删行从后往前；写前 backup_tab。

## ★update_range 行宽 > A1范围列数 = 整块静默失败（2026-06-18 教训）
`update_range(SID,tab,'A11:F20',rows)`：若 rows 里**任何一行的列数 > 范围列数**（这里 F=6 列，但某行有 7 个元素），values API **整块拒绝、`update_range` 返回 False**——脚本若不检查返回值就以为写成功了（实为 0 行落地）。两个防线：①范围列数 = `max(len(r) for r in rows)`，别写死；②**检查 update_range 的返回值**，False 就排查。同源坑：手动 `[r+['']*(N-len(r))]` 补齐时若某行已超 N，`['']*(负数)=[]` 不会截断，行仍超宽。

## 批量写：整行 update_range，别逐格 update_cell（2026-06-04 教训）
改一行的多个语言/字段时，**读出整行 → 内存改 → 一次 `update_range` 整行写回**；不要对每格调 `update_cell`。逐格写 = 每格一次 node 启动，几百格要数分钟、且**放后台跑会随 turn 结束被杀**（拓荒节本地化 280 格逐写跑了一半被中断；改整行批量 22 次调用秒级跑完）。`backup_tab` 别在可能重跑的脚本里反复调（会建多份同名备份）。

## 旧工具
`.cursor\skills\gsheet-config-replace\scripts\gsheet_utils.py` 是旧版（gws.cmd + 只有写），gsheet-config-replace skill 仍用它。新工具是其超集，**新场景一律用新的**。
