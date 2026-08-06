# 搜索 EffectDisplay 时带入不存在的 Unity 目录

- 日期：2026-08-06
- 任务：核查英雄主页视频展示生命周期
- 现象：`rg --files` 成功定位 `Scripts\Utils\EffectDisplay.cs`，但因同时传入不存在的 `Assets\GameMainLogic` 返回 exit 1。
- 根因：依据程序集命名猜测了目录，未先验证路径存在。
- 处理：使用已定位的真实文件继续检查；后续先 `Test-Path` 或只对已确认目录搜索。
- 状态：open
