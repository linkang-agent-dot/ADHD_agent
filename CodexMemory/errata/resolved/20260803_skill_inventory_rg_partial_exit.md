# Skills 四目录枚举命令部分成功但退出码为 1
- 日期：2026-08-03
- 任务：核对 Claude/Codex skills 是否物理共用。
- 现象：串行执行四次 `rg --files` 时，前三个目录有输出，最后一个目录无匹配使整条命令退出码为 1。
- 处理：不把该退出码误判为已有输出无效；已改用逐目录 Test-Path、目录属性、文件计数和同名文件哈希完成核验。
- 状态：resolved

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 同族归并 feedback_shell_composite_exitcode.md
- 状态：resolved
