# gdconfig checkout 钩子超时与 errata README 路径误判

- 日期：2026-08-06
- 任务：将马戏节排行榜配置从 dev 单改动传播到 qa/master MR
- 现象：`git checkout qa; git pull; git cherry-pick` 组合命令运行 606 秒后超时；复查显示仅 checkout 完成，HEAD 仍为 origin/qa，cherry-pick 尚未开始。随后错误读取了不存在的 `errata/open/README.md`。
- 根因：gdconfig 的 post-checkout 钩子会同步多个 worktree，耗时可远超普通 Git 操作；将 checkout、pull、cherry-pick 串在同一个前台命令里，无法辨认卡在哪一步。errata 格式说明实际位于 `CodexMemory/errata/README.md`，不是 open 子目录。
- 处理：后续把 checkout、pull、cherry-pick 拆成独立命令，每一步完成后检查分支/HEAD/状态；errata 固定读取 `C:\ADHD_agent\CodexMemory\errata\README.md`。
- 状态：open
