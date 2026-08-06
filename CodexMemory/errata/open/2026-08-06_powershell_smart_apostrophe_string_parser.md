# PowerShell 将弯引号视为单引号导致多语言脚本解析失败

- 日期：2026-08-06
- 任务：写入 RuleTips40001 的 16 语言更新
- 现象：包含法语 `d’île` / `l’événement` 等 U+2019 弯引号的 PowerShell 单引号字符串触发 ParserError，脚本在任何写入前失败。
- 根因：PowerShell 解析器会把部分 Unicode smart quote 当作字符串定界符，不能假设 U+2019 在单引号字符串中始终安全。
- 处理：把文案中的 U+2019 统一改为 ASCII 撇号并在 PowerShell 单引号串中写成双单引号，或改用不受引号影响的结构化传参；重跑前确认本轮 RuleTips Text 行尚未发生部分写入。
- 状态：open
