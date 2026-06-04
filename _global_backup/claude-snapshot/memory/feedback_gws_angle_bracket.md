---
name: gws.cmd 角括号传参失败
description: gws.cmd JSON body 含 < > 时被 CMD.EXE 解析为重定向符，导致 rc=1；需用 node.exe 直接调用绕过
type: feedback
originSessionId: 83c813cc-9f8e-4c24-87d5-22fd7565133c
---
gws.cmd 写入含 `<color=#...>` 等 HTML/color tag 的 JSON body 时，CMD.EXE 把 `<` 解析为 stdin 重定向符，gws 收到截断的 JSON，返回 rc=1 报"系统找不到指定的文件"。

**解决方法**：直接调用 Node.js 可执行文件，绕过 .cmd 包装器和 CMD.EXE：

```python
NODE = 'node'
GWS_JS = r'C:\Users\linkang\AppData\Roaming\npm\node_modules\@googleworkspace\cli\run-gws.js'
cmd = [NODE, GWS_JS, 'sheets', 'spreadsheets', 'values', 'batchUpdate',
       '--params', params_str, '--json', body_str]
r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
```

**Why:** CMD.EXE 进程解析 .cmd 文件时会处理整行命令中的 `<` 和 `>`，即便它们在 Python 传入的参数字符串里也不例外。直接用 node 调用 run-gws.js 绕开了 CMD.EXE，参数原样传入，角括号安全。

**How to apply:** 凡是 JSON body 含 `<` 或 `>`（color tag、HTML 富文本等）的 GSheet 写入调用，必须用 `node + GWS_JS` 替代 `gws.cmd`。其他不含角括号的调用可继续用 gws.cmd 以保持简洁。
