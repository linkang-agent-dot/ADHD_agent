# Errata README 路径误写到 open 子目录

- 日期：2026-08-03
- 任务：记录 10 月万圣节美需用户纠错
- 现象：读取 `C:\ADHD_agent\CodexMemory\errata\open\README.md` 失败。
- 根因：误以为模板说明位于 `open` 子目录，实际文件位于 `C:\ADHD_agent\CodexMemory\errata\README.md`。
- 处理：用 `rg --files` 定位后读取正确路径；后续固定从 errata 根目录读取说明。
- 状态：open

