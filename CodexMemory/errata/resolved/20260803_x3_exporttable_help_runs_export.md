# X3 ExportTable.py 忽略 --help 并直接执行导表
- 日期：2026-08-03
- 任务：为 qa/master 的马戏主数据单提交传播确认本地导表命令参数
- 现象：执行 `python ExportTable.py --help` 没有输出帮助，而是直接开始完整导表；shell 20 秒超时后进程被终止，未得到有效验收结果。
- 初判根因：`ExportTable.py` 未实现 argparse/help 分支，未知参数被忽略；后续不要用 `--help` 探测，直接按知识库从 `Tools/table_exporter` 运行 `python ExportTable.py`，并给足至少 120 秒超时。
- 状态：open

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 成立(跨模型)。护栏已写入 reference_x3_tsv_export_migration.md:禁--help探测,直接跑,超时≥120s
- 状态：resolved
