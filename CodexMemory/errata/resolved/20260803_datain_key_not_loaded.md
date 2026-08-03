# Datain 用户级 API Key 未自动加载到当前进程
- 日期：2026-08-03
- 任务：查询 X3 2026-08-02 大盘总收入与付费人数
- 现象：`query_game.py -c query` 首次报 `请在当前系统的环境变量中设置 DATAIN_API_KEY`；但用户级环境变量实际已设置，手动从 User scope 加载到当前 PowerShell 进程后查询成功。
- 初判根因：当前工具进程启动时未继承用户级环境变量；后续查数前应同时检查 Process 与 User scope，并在不回显密钥的前提下加载。
- 状态：open

---
## 复核结论（2026-08-03，Claude 巡检）
- double-check：**成立**。独立佐证=Claude 侧当天调用 query_game.py 同样需要手动 `[Environment]::GetEnvironmentVariable('DATAIN_API_KEY','User')` 加载（无头/工具子进程不继承 User 域环境变量，通用现象非 Codex 特有）。
- 解决方案：查询前从 User scope 显式加载到进程环境（不回显密钥）。
- 写入位置：`datain-skill/SKILL.md` 「配置与鉴权」节尾新增护栏（Junction 一处改两边生效）。
- 状态：resolved
