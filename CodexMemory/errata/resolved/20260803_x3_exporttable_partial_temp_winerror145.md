# X3 本地导表被上次中断留下的 temp_dev 阻塞
- 日期：2026-08-03
- 任务：验证 qa 分支的马戏礼包主数据配置
- 现象：前一次导表被 shell timeout 中止后，再跑 `python ExportTable.py` 在清理 `temp_dev/Proto` 时抛 `OSError: [WinError 145] 目录不是空的`。
- 初判根因：中断时仍有文件句柄或并发产物残留，默认导出目录的 `shutil.rmtree` 无法一次删除；由于工作规范禁止未确认删除中间产物，本次应改用新的独立输出目录完成验证，而不是强删 `temp_dev`。
- 状态：open

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 成立(跨模型)。护栏已写入 reference_x3_tsv_export_migration.md:中断残留改用独立输出目录,不强删temp_dev
- 状态：resolved
