# 组合命令退出码纪律（rg/Select-String/git check-ignore 家族）

- 日期：2026-08-03（由 Claude 巡检自 4 条 errata 归并：rg_no_match_exit1、skill_inventory_rg_partial_exit、worktree_preference_probe_exit1、git_check_ignore_expected_exit1）
- 规律：**探索性搜索命令的 exit 1 = 零匹配，不是执行失败**。`rg`、`Select-String`、`git check-ignore` 无匹配都返回 1；放在组合命令末尾会把整条 shell 判成 Script failed。
- How to apply：①探索性搜索单独调用，别做组合命令收尾；②或显式接住：`rg ...; if ($LASTEXITCODE -le 1) { exit 0 }`；③判断"是不是真失败"看 stderr 有无报错，不看退出码。
- 同族：并行写入中的 rollout jsonl 用 `FileStream(FileShare.ReadWrite)` 读或只处理已关闭会话（jsonl_shared_read_lock）；headless 截图后等文件就绪再检查，加轮询（chrome_headless_screenshot_race）。
