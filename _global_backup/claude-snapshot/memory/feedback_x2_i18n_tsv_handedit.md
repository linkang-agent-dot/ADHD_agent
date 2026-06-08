---
name: feedback_x2_i18n_tsv_handedit
description: 手改 X2 i18n tsv 的两个坑——文件是 CRLF 行尾(text 模式写 LF 会整文件 diff)，且 LC id 末尾数字可能含目标数字子串(必须只改 value 列)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 75aa701b-913c-46bf-9e55-3ca3f40d281d
---

直接手改 X2 配置仓 `D:\UGit\x2gdconf\fo\i18n\*.tsv`（绕过 fwcli，做单行定向改文案）时两个坑：

1. **文件是 CRLF 行尾**。Python `io.open(text)` 读会把 `\r\n` 归一成 `\n`，再 `newline=''` 写出就是 LF → git 看成**整文件 8.5 万行全改**（实际只动 1 行）。**必须用二进制读写**（`open(p,'rb')` → `split(b'\n')` 保留行尾 `\r` → 改后 `b'\n'.join` 写回 `'wb'`），CRLF 才不被破坏。

2. **不能整行 `replace`**。i18n 行格式 `key\tvalue\tLC_id`，LC_id 末尾数字可能含你要替换的数字子串（如把"60分钟"改"180分钟"时，id `1011131602` 里也有 "60"，整行 replace 会把 id 改成 `10111311802`）。**只对按 `\t` split 后的 value 列(index 1) 做替换**。

**Why**：2026-06-04 改限时抢购时长 60→180，第一版 text 模式写出导致 17 个 i18n 文件全文件 diff，重做才发现 CRLF + id 含子串两个坑。

**How to apply**：手改 X2 i18n tsv → 二进制读写 + 只改 value 列；改完 `git diff --stat` 确认每文件只 `2 +-`（1 行）才提交。配置 tsv（fo/config）本身多是 LF，没这问题。X2 真源是 GSheet，手改 tsv 前先把 GSheet 改成同值（见 [[feedback_confirm_source_of_truth_before_edit]]）。相关：[[x2-flashsale-placeholder]]。
