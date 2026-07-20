---
name: reference_headless_claude_cli
description: 本机脚本无头调 claude CLI（claude -p）的正确姿势——必须关 Stop hook 否则 JSON 输出被收工自检回复顶掉；走订阅无需 API key
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4462650a-475a-4ef5-b2e1-05b0d53e1bcf
---

本机任何脚本/计划任务无头调用 claude CLI 时的固定姿势（2026-07-02 game-radar 切 Claude 实测）：

```
%APPDATA%\npm\claude.cmd -p --output-format text --model sonnet --settings "{\"hooks\":{\"Stop\":[]}}"
```
prompt 走 stdin。

**⚠️ 核心坑：Stop hook 污染输出**。用户 settings.json 配了 Stop hook（`pending_verify_gate.py` 收工自检），无头 `-p` 模式下它会追加一轮对话，`-p` 返回的"最终输出"变成模型对自检的回复，把真正的 JSON/答案完全顶掉。**必须 `--settings '{"hooks":{"Stop":[]}}'` 覆盖关闭**。

其他要点：
- 走订阅授权（`~/.claude` 凭据），**不需要 ANTHROPIC_API_KEY**（本机也没配）；计划任务以当前用户跑即可读到凭据。
- 副作用（可为加分项）：无头 claude 会加载 CLAUDE.md + memory，回答能结合用户自己的项目经验。
- 输出解析要容错：即便关了 Stop hook，最好仍从输出里正则抠 JSON（`re.search(r"\[.*\]", txt, re.S)`）。
- subprocess 用 `claude.cmd` 全路径（`os.environ["APPDATA"]\npm\claude.cmd`），Windows CreateProcess 可直接跑 .cmd。

活用例：[[reference_game_radar]] 的 `analyze.py analyze_with_claude()`。

## ⚠️ stdin 管道喂 prompt 会乱码，改用参数传或显式设 UTF8（2026-07-17 帕鲁情报巡检实测踩到）

- **现象**：`Get-Content $promptFile -Raw -Encoding UTF8 | & $claude -p ...`（管道喂 stdin）跑出来，claude 收到的 prompt 里中文全变问号（路径/文件名/指令文字乱码），靠上下文反查真实文件才恢复原意；巡检本身仍算"跑成功"（exit 0、报告按时写出），乱码是静默的，不看输出内容根本发现不了。
- **根因**：PowerShell 管道把字符串传给**外部（非 PS）可执行文件**时，用 `$OutputEncoding` 这个 preference 变量重新编码成字节流，而不是直接透传 UTF-8；Windows PowerShell 5.1 下 `$OutputEncoding` 默认常是系统 OEM codepage（中文系统=GBK/936），不是 UTF-8——中文字符经这层编码转换必坏。`-Encoding UTF8` 只管 `Get-Content` **读文件**这一步，管不到**管道传给外部进程**这一步，两处编码互相独立，光设前者没用。
- **两种脚本架构的风险对照**：稳定跑的 `daily_plan_scan.ps1`/`bug_scan.ps1` 都是把 prompt 当**命令行参数**传（`$null | & claude -p $prompt ...`，`$null |` 只是喂空 stdin 防止 CLI 卡死等 stdin，不涉及内容管道），参数走进程创建 API 不经 `$OutputEncoding` 转码，天然安全；`palworld_intel_scan.ps1`、`token_weekly_scan.ps1` 用的是 `Get-Content -Raw | & claude -p`（内容本身走 stdin 管道）架构，才踩到这个坑。
- **修法（已在两处落地，2026-07-17）**：管道架构的脚本在管道前显式 `$OutputEncoding = [System.Text.Encoding]::UTF8`，强制 PowerShell 用 UTF-8 给外部进程编码 stdin 内容。参数架构的脚本不受影响，无需改。
- **排查口诀**：任何 `claude -p` 调度任务如果发现 prompt 里的中文/结果内容莫名其妙"看起来像另一件事"（张冠李戴、指代不明、路径读不通但程序又正常退出写了文件），先怀疑 stdin 管道乱码，而不是模型理解错了——去 `_intel_last_output.txt` / `_handover_review_claude_out.txt` 之类的原始输出文件里肉眼查有没有问号乱码。新写管道架构的调度脚本，开头直接带上这行 `$OutputEncoding` 设置，别等踩坑。
