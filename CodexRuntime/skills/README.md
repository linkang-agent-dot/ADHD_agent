# Claude → Codex Skill 同步器

默认只读扫描：

```powershell
python CodexRuntime\skills\sync_claude_to_codex.py --dry-run
```

输出 JSON 报告：

```powershell
python CodexRuntime\skills\sync_claude_to_codex.py --dry-run --json-report CodexMemory\reports\skill-sync.json
```

首次真实应用必须先审阅 dry-run 清单：

```powershell
python CodexRuntime\skills\sync_claude_to_codex.py --apply
```

退出码：`0` 成功；`2` 存在阻断项且未写入；`3` 应用失败但回滚成功；`4` 应用失败且回滚不完整。
