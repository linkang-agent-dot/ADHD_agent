# x3-feature-test HTML 生成器不支持 --help

- 日期：2026-08-06
- 任务：生成航海随机修复 HTML 验收报告。
- 现象：调用 `make_html_report.py --help` 时，脚本把 `--help` 当作 spec 文件路径并抛 FileNotFoundError。
- 根因：该脚本是单位置参数入口，没有 argparse/help 分支。
- 处理：读取样例 spec，直接以 `<spec.json> [output.html]` 方式调用。
- 状态：open。
