# PowerShell Get-Process 空结果导致组合检查误报失败

- 日期：2026-08-06
- 任务：修改 X3 dev 马戏团寻宝玩家可见文案
- 现象：组合状态检查中 `Get-Process git -ErrorAction SilentlyContinue` 在无 git 进程时使整条 shell 命令以 exit 1 返回，尽管前面的 git status/branch 均成功。
- 根因：把“可为空”的进程探测放在组合命令末尾，PowerShell 将空目标视为非零退出状态。
- 处理：以后用 `Get-Process ... -ErrorAction SilentlyContinue | ...; exit 0`，或先赋值后显式输出，避免把“没有进程”当工具错误。
- 状态：open
