# 远端独立分支与 errata README 路径误判

- 日期：2026-08-06
- 任务：为马戏巡游随机奖励修复创建 GitLab MR
- 现象：直接执行 `git log fix/voyage-random-min-reward-0806`，但该分支只有远端 ref，本地不存在；随后误读 `errata/open/README.md`，实际 README 位于 `errata/README.md`。
- 根因：把通过 `commit-tree` + 远端推送生成的分支误当成本地分支；未先用 `rg --files` 核实 errata 目录结构。
- 处理：改用 `git ls-remote --heads origin <branch>` 核验远端提交；按实际路径读取 `C:\ADHD_agent\CodexMemory\errata\README.md`。
- 状态：open；后续涉及远端独立分支先查 `refs/remotes/origin/...` 或 `ls-remote`，读取规范文件先定位真实路径。
