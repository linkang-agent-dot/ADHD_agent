# Errata 模板 README 路径判断错误

- 日期：2026-08-06
- 任务：记录至尊徽记 UI 纠错
- 现象：首次尝试读取 `errata/open/README.md` 报路径不存在，实际模板位于 `errata/README.md`。
- 根因：把“记录写入 open 子目录”误推为“README 也位于 open 子目录”，未先定位文件。
- 处理：使用 `rg --files C:\\ADHD_agent\\CodexMemory\\errata` 定位并读取实际 README；后续固定读取 `C:\\ADHD_agent\\CodexMemory\\errata\\README.md`。
- 状态：resolved。
