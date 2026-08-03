# git add 包含已删除且从未跟踪的 errata 路径导致整批 staging 中止

- 日期：2026-08-03
- 任务：提交 hook 信任审计记录
- 现象：`git add` 同时传入修改文件、新 resolved 文件和一个已删除但从未被 Git 跟踪的 open 文件；不存在的 pathspec 使整条 add 失败，随后 commit 无内容。
- 根因：误以为 apply_patch 的 delete 一定会在 Git 中形成删除项，未先用 `git ls-files` 判断源文件是否已被跟踪。
- 处理：只 stage 实际存在的修改/新增文件；以后对“移动”类提交先检查源路径是否在 index，未跟踪源不加入 pathspec。
- 状态：open
