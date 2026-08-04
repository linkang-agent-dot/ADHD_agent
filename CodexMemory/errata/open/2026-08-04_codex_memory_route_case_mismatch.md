# Codex memory 路由目录不一致

- 时间：2026-08-04
- 场景：会话开工后按 AGENTS.md 加载 Jira 知识库。
- 现象：读取 `C:\Users\linkang\.Codex\projects\C--Users-linkang\memory\reference_jira.md` 报路径不存在。
- 原因：当前共享 memory 真源仍位于 `.claude\projects\...\memory`，而会话指令写成了 `.Codex\projects\...\memory`；Windows 虽不区分大小写，但目录名本身不同。
- 绕道：改读 `C:\Users\linkang\.claude\projects\C--Users-linkang\memory\reference_jira.md`。
- 后续规则：按路由路径读取失败时，先在 `.claude` 共享真源定位同名文件；不要把缺失误判为知识库不存在。

## 同轮追加：X3 TSV 重复表头

- 现象：PowerShell `Import-Csv` 读取 `ActvOnline__ActvOnline.tsv` 报 `The member "cs" is already present`。
- 原因：该 TSV 存在重复列名，`Import-Csv` 要求属性名唯一。
- 绕道：用位置索引解析原始制表符行，或用 Python `csv.reader`；不要用 `Import-Csv` 读取 X3 导表 TSV。

## 同轮追加：PowerShell here-string 不能放在管道右侧

- 现象：`$content | @'... '@ | python -` 报 `Expressions are only allowed as the first element of a pipeline`。
- 原因：PowerShell here-string 是字符串表达式，不能直接作为管道中段的命令。
- 绕道：让 Python 用 `subprocess` 直接执行只读 `git show`，或先把脚本文本赋给变量再调用；不再拼这种管道。

## 本会话复发：AGENTS 路由仍指向不存在的 `.Codex` 目录

- 时间：2026-08-04
- 现象：按本会话 AGENTS.md 读取 `reference_x3_timecycle.md` 与 `reference_jira.md` 时再次报路径不存在。
- 绕道：改读 `.claude\projects\C--Users-linkang\memory\` 下同名共享真源。
- 额外工具错误：误按指令文字去 `errata\open\README.md` 找格式，实际 README 在 `errata\README.md`；后续先检查父目录。
