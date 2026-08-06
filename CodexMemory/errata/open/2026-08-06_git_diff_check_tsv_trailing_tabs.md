# git diff --check 将 TSV 固定空列误判为尾随空白

- 时间：2026-08-06
- 场景：X3 马戏节文案推送前，组合运行 `git fetch/status/diff/check`。
- 现象：远端与本地基线一致、定向 TSV 校验通过，但 `git diff --check` 因改动行末固定空列（tab）返回 exit 1，导致整条只读组合命令显示失败。
- 原因：X3 TSV 行尾保留固定数量的空字段，`git diff --check` 的通用尾随空白规则不适合作为该格式的硬阻断。
- 绕道：TSV 改用列数、主键唯一、引用/内容定向校验和 `ExportTable.py` exit 0 作硬证据；组合命令中不要把 `git diff --check` 放在最终退出码位置，或明确过滤仅 TSV 的固定尾空列告警。
