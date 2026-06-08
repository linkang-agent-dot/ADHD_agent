---
name: feedback_ps_script_needs_bom
description: 给 Windows 定时任务/PS5.1 写含中文的 .ps1 必须存成带 BOM 的 UTF-8，否则解析崩
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c63c1018-eea1-4f38-a96b-ff6e2ad0358e
---

用 Write 工具新建含中文的 `.ps1`（无 BOM 的 UTF-8）后，Windows PowerShell 5.1（powershell.exe）默认按 GBK 读取，中文字节被错解，常把字符串结尾的 `"` 吃掉 → 报 "The string is missing the terminator" / "Missing closing '}'"，定时任务 LastTaskResult=1。

**How to apply:** 写完含中文的 .ps1 后，立刻用 PS 重存为带 BOM 的 UTF-8：`$c | Out-File -FilePath xxx.ps1 -Encoding utf8 -Force`（PS5.1 的 utf8 即带 BOM）。纯 ASCII 的 .ps1 不受影响。相关：[[feedback_hook_path_forward_slash]]、[[feedback_x2_i18n_tsv_handedit]]。
