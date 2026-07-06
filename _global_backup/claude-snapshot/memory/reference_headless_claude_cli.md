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
