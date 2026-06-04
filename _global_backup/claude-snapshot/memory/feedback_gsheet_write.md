---
name: GSheet 写入的兼容性陷阱
description: 做 GSheet append/write 类工具时，API 本身能跑，真正的坑在字符转义（双引号等）兼容问题
type: feedback
originSessionId: e0adffc2-7b6d-42f1-bc24-6770a5feec9d
---
GSheet 的写入 API（gws sheets values append 等）本身是稳定可用的，**不要把时间花在"能否写入"的验证上**。真正的坑集中在字符转义兼容性：

- 双引号、单引号在 JSON payload → GSheet cell 的传递中经常被吃掉或变形
- 多行文本、换行符 `\n` 可能被渲染成实际换行或原文
- 英文缩写 `'s`、撇号经常出问题
- 公式前缀 `=` 会被当成公式执行

**Why:** 用户明确说过"gsheet 这边肯定是能跑的，就是兼容问题比较多，比如双引号啥的"。花时间验证连通性是浪费，应该直接把精力放在转义处理和边界情况测试。

**How to apply:** 做任何 GSheet 写入类 skill 时：
1. 跳过"API 能不能通"的自证环节，直接认为能通
2. 把测试重心放在脏数据样本上 — 带双引号的活动名、带撇号的英文 LC、带换行的描述字段
3. dryRun 时重点比对"写入前 JSON"和"写入后实际 cell"的字符差异，不只看成功状态码

## 工程坑（独立于字符转义）

**a) bash heredoc 长度限制**：单次 gws 写入超 ~5KB JSON body 会触发 `Argument list too long` 或 `ENAMETOOLONG`。即使不是写复杂数据（比如回填整列简单字符串）也会撞上。
- 解决：分批写，单批 ≤ 500 短字符串 / ≤ 5 复杂行
- 参考实现：`C:/Users/linkang/skills/iap-sync-to-master/sync_iap.js`（5/批，9 列）和 `backfill_note.js`（500/批，1 列）

**b) gws → Google API transient `tls handshake eof`**：高频出现在大写入或刚启动连接时，单次重试通常即过。
- 解决：read/write 都加指数退避重试（1s → 2s → 4s → 8s → 16s），且**不要因 stdout 包含 error 就放弃**——异常时实际可能写入成功了
- 经验：5 次重试足够覆盖 99% 的 transient

**c) range 字符串里的单引号**：在 Windows bash 下 `--range "'sheet'!A1:B2"` 会被 shell 错误解析，应该写成 `--range "sheet!A1:B2"`（不带内层单引号）
