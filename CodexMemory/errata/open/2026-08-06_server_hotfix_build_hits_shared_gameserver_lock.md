# hotfix-only 构建仍命中运行中 GameServer 主程序锁

- 日期：2026-08-06
- 任务：服务端验收航海奖励随机修复。
- 现象：`server_build.py build --hotfix-only --scope game` 还原成功，但构建依赖 `GameServer.csproj` 时复制 `GameServer.exe` 失败；文件被两个本地 GameServer 进程锁定。
- 根因：改动文件属于 CSShared 并编进 GameServer 主程序集；即使入口选 GameServer.Hotfix，项目引用仍会构建主工程，运行中进程锁住 apphost 输出。
- 处理：识别各本地服进程，按非 Hotfix 变更走目标服完整重启/停服构建，不再重复 hotfix-only 原地构建。
- 状态：open。
