---
name: atomic-write-and-escape-pitfalls
description: 两个实测事故坑：python写文件中途抛异常会把目标文件截成0字节(重要产物必须原子写入)；Bash工具JSON层吃一层反斜杠导致\uXXXX代理对变裸代理崩编码(emoji用字面字符)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8e352cc4-7d37-4b01-b14c-02c0969a2111
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
