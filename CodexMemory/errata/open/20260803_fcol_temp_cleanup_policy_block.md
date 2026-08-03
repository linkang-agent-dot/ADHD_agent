# FCOL第三方临时资料清理命令被策略拦截
- 日期：2026-08-03
- 任务：完成国服官网分析后清理本次误抓的第三方网页临时目录。
- 现象：对已校验的 `C:\ADHD_agent\_tmp_scripts\fcol_ev_20260803` 执行 PowerShell `Remove-Item -Recurse -Force` 时被工具策略拒绝，命令未执行。
- 处理：不再尝试绕过策略；该目录内容未用于结论，后续按允许的清理方式处理。
- 状态：open
