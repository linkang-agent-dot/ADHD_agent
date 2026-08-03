# FCOL官网新闻列表解析命令出现PowerShell空管道错误
- 日期：2026-08-03
- 任务：从腾讯FCOL官网新闻列表提取2026年7月活动与公告。
- 现象：将 `foreach` 输出直接接管道时多写了结构闭合，PowerShell 报 `An empty pipe element is not allowed`。
- 初判根因：在一行复合命令中混用 `foreach`、脚本块与管道，括号层级不清；改为先累计数组再统一筛选输出。
- 状态：open

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 一次性语法坑(PowerShell管道层级),shell纪律族参考 feedback_shell_composite_exitcode.md
- 状态：resolved
