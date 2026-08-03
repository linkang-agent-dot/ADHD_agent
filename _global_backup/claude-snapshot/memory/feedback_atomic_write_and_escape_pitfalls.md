---
name: atomic-write-and-escape-pitfalls
description: 两个实测事故坑：python写文件中途抛异常会把目标文件截成0字节(重要产物必须原子写入)；Bash工具JSON层吃一层反斜杠导致\uXXXX代理对变裸代理崩编码(emoji用字面字符)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8e352cc4-7d37-4b01-b14c-02c0969a2111
  modified: 2026-07-29T07:13:48.981Z
---

# 写文件截断 + 转义层事故（2026-07-14 帕鲁图鉴 HTML 被清零实录）

**事故**：用 python 对 84KB 的 HTML 做字符串替换后 `io.open(p,'w').write(s)`，s 里混入了裸代理字符 → write 时 UnicodeEncodeError → **目标文件已被打开截断，留下 0 字节**，整个产物没了（靠上下文里的内容重建才救回）。

**Why（两层根因）**：
1. **裸代理来源**：经 Bash 工具下发的 heredoc 脚本，**工具的 JSON 编码层会吃掉一层反斜杠**——脚本里写 `'\\ud83c\\udfed'`（期望 JS 收到字面 `\ud83c`），实际 python 收到 `'🏭'` 被解析成两个裸代理字符，写 utf-8 必崩。
2. **截断机制**：`open(p,'w')` 在打开瞬间就清空文件，write 抛异常=内容没写进去=文件留 0 字节。

**How to apply**：
- 往脚本/HTML 里塞 emoji：**直接用字面字符（🏭🐎🥚），永远别用 `\uXXXX` 代理对转义**。
- 对**重要产物文件**做程序化改写：**原子写入**——`write(tmp)` 成功后 `os.replace(tmp, target)`；或改用 Write/Edit 工具（自带保护）。
- 改写前重要产物值得先留 `.bak`（大改时）。

---

## 第三坑：Bash 工具里 `cmd /c` 的 `/c` 被 MSYS 改写成 `C:/`（2026-07-29 实证，连踩 4 次）

**现象**：Bash 工具跑 `cmd /c "some.bat args"` → 报 `'some.bat' is not recognized as an internal or external command`，或者更隐蔽——**进程挂着不动、脚本压根没执行**。查进程命令行看到的是：
```
cmd.exe C:/ "start_local_server.bat skip-link"     ← /c 变成了 C:/
```

**Why**：Git Bash 的 MSYS 路径转换把**看起来像绝对路径的 `/c`** 自动翻成 Windows 路径 `C:/`。于是 cmd 收不到 `/c` 开关，把后面整串当普通参数，退化成一个什么都不干的交互式 shell 挂在那里——**不报错、不退出**，比直接报错更难发现。

**How to apply**：
- 在 Bash 工具里调 bat/cmd，一律**改用 PowerShell 工具**：`& cmd.exe /c "C:\完整\路径\x.bat"`（本次唯一跑通的姿势）。
- 非要在 Bash 里调，用 `cmd //c`（双斜杠是 MSYS 的转义写法）。
- **判据**：bat 迟迟没输出时，先 `Get-CimInstance Win32_Process` 看它真实的 CommandLine——参数被改写过一眼就看出来，别盲等超时。
- 同源坑：`.bat` 末尾常有 `pause`，非交互下会永久挂住；`start /wait` 调需要 UAC 提权的子脚本同理（见 [[reference_x3_local_server_launch_repair]] 的 MakeLink 事故）。

## 追加：python 生成器里插 HTML 的两个坑（2026-07-29 各踩一次）
- **HTML 属性一律用单引号**：`<span style='color:#f87171'>`。往 python 双引号字符串里塞双引号属性会提前闭合 → SyntaxError；事后全局改单引号又会误伤模板里正常的 f-string 单引号，只能用正则精确修回。**写的时候用单引号，比事后修便宜一个数量级。**
- **批量 replace 必须收集并打印 MISS 清单**：匹配长中文串时，文案里一个「·」「限定」的差异就 miss；不打印就是静默漏改（本轮 12 条替换漏 1 条，靠 MISS 输出才发现）。模板：`if a in s: s=s.replace(a,b,1) else: miss.append(a[:36])`，收尾 `if miss: print("MISS:",miss)`。
- **生成器代码里禁止出现反斜杠转义**（2026-07-30 又踩）：往 heredoc/Bash 工具里写 python 时，`\\n` 会被转义层吃成真换行 → 写出去的文件里字符串被换行截断，报 `unterminated string literal`。**改用 `chr(10)`／`os.linesep` 代替一切 `\n` 字面量**（`chr(10).join(x)` 而不是 `"\n".join(x)`）；同理 `\t`、正则里的 `\d` 也要么走 `chr()`、要么用字符类 `[0-9]` 绕开。
- **往 f-string 模板里注入 JS必须双写花括号**（2026-07-30）：生成器的 HTML 模板是 f-string，注入的 JS 里每个 `{` `}` 都要写成 `{{` `}}`，否则 python 把 JS 的代码块当插值表达式 → `SyntaxError: invalid syntax`。**只有真正要插值的 `{VAR}` 保持单层。**批量修法：抽出注入段 → 先把 `{VAR}` 换占位符 → 全局 `{`→`{{`/`}`→`}}` → 还原占位符。
- **本地 file:// 页面的剪贴板要降级**：`navigator.clipboard` 在 file: 下不是 secureContext，直接用会静默失败；判 `window.isSecureContext` 再 fallback 到临时 textarea + `document.execCommand('copy')`。产物要本地打开就必须带这层。
- **用 grep 做"零错误检查"会把成功误判成失败**（2026-07-30）：`grep -c -i "error"` 在**无匹配时返回 exit 1**，放在命令链末尾会让整条命令 exit 1，后台任务直接报 `failed`——而无匹配恰恰是想要的结果（零错误）。修法：`grep -c ... || true`，或改用 `grep -c ... ; echo "count=$?"` 分开看，或用 python 统计。
