---
name: 配置校验必须端到端，不能只验 GSheet
description: 配置写入后的校验要覆盖 GSheet + 本地 TSV + 分支推送三个环节，不能只确认 GSheet 就说"完成"
type: feedback
originSessionId: 2f9bf6a0-00e5-49b7-8786-0bc10f09587d
---
**GSheet 写对了 ≠ 配置落地了。校验要走完全链路。**

**Why:** 拓荒节（2026-04）出现过：GSheet 行顺序正确，但导表到 dev_26festival 分支后 TSV 里行在表底部；2011 的 GSheet 正确但本地 TSV 少了末尾 SubScene 空列。校验脚本的 `--all-changed` 参数实际只打印 usage 没有真正校验，没第一时间发现问题。

**How to apply:**

## 三层校验（每次配完必做）

1. **GSheet 层**：读回写入行，确认行数、顺序、内容
2. **本地 TSV 层**：导表后打开 TSV 文件，确认：
   - 新增行在正确位置（不在表底部）
   - 列数 = 表头列数（末尾空列不能被截断）
   - 关键 JSON 字段内容正确
3. **分支推送层**：git diff 确认变更文件和行数符合预期

## 不要过早下结论

- 没走完三层校验，不说"已写入"/"没问题"
- 如果用了校验脚本，先确认脚本实际执行了什么（读输出，不要只看退出码）
- 结论附上证据：读回了哪些行、diff 了哪些文件

## 已接入 quality-gate 自动验收（config 类）
改配置/换皮**开工时建标记** `~/.claude/.pending_verify/<任务>.json` = `{"task":"<名>","type":"config","expected_branch":"<预期分支>","tsv_changed":["<改动tsv>"],"sheet_id":"<可选设计源>","status":"pending"}`；
**收工被拦时**派 `task-checker`(type=config) 跑验收（清单见 `C:\ADHD_agent\.claude\quality-gate\config-checklist.md`：分支正确/引用ID/Reward seq/MailID 等客观项 + 三层一致 warn）；全过删标记，有 blocker 列给用户定。这套是上面三层校验的自动守门版。
