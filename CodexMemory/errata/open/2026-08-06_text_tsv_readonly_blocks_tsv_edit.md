# Text TSV 只读属性阻断安全编辑器写入

- 日期：2026-08-06
- 任务：更新马戏团寻宝 AO103101 / RuleTips40001 多语言文案
- 现象：`tsv_edit.py` 对 `tsv/i18n/Text__Text.tsv` 的 16 列 dry-run 全部通过，但首个实际写入报 `PermissionError: [Errno 13] Permission denied`；此前非 i18n 两表写入正常。
- 根因：不是只读属性（Attributes=Archive、IsReadOnly=False），也不是外部进程长期占用。PowerShell 的 `Current()` helper 使用 `[IO.File]::ReadLines()` 惰性枚举并在返回后未及时释放句柄；同一 PowerShell 进程随即调用 Python 写文件，造成自锁。独占打开复查已成功。
- 处理：改为一次性 `[IO.File]::ReadAllLines()` 取原始目标行并释放句柄，再调用 `tsv_edit.py`；禁止在写入前保留 ReadLines 惰性枚举器，且不重跑扫描或改 xlsx 覆盖 TSV。
- 状态：open
