# FCOL pandas 表格打印被 PowerShell GBK 控制台编码打断

- 日期：2026-08-03
- 任务：汇总永恒评价体系五个位置页的工资残差与时刻换代增幅。
- 现象：`pandas.read_html` 成功读取表格，但打印中场表含 `Matthäus` 时触发 `UnicodeEncodeError: 'gbk' codec can't encode character`，组合命令退出1。
- 根因：Windows PowerShell 子进程标准输出沿用GBK，而球员名包含GBK不可编码字符。
- 处理：重跑前显式设置 `$env:PYTHONIOENCODING='utf-8'`，随后五位置共54张正式位置卡、36张有时刻对照卡均成功汇总。
- 状态：open
