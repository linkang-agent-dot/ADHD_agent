# 全局 ~/.claude 备份快照 · 2026-06-03

这是 2026-06-03 那轮（DesignDeck 学习 → 搭工具）里，**存在全局 `~/.claude`、不在 ADHD 仓库**的东西的备份。
**这是备份快照，不是活源**——活源在下面「活源位置」，改要改活源，这里仅供丢失时还原/查阅。

> 仓库内已版本化、不在此备份的：`.claude/quality-gate/`、`KB/方法论/X3交互模块工作流.md`+范本、`KB/GDesign学习.md`。

## 内容 & 活源位置

| 备份文件 | 是什么 | 活源位置 |
|---|---|---|
| `agents/task-checker.md` | 通用独立验收员 agent（quality-gate 用） | `~/.claude/agents/task-checker.md` |
| `x3-media-scripts/transparify_asset.py` | 双底差分**整机**（生成透明资产一条龙） | `~/.claude/skills/x3-media/scripts/` |
| `x3-media-scripts/transparify_dual_bg.py` | 双底差分底层（白底+黑底→alpha） | 同上 |
| `x3-media-scripts/make_bbox_mask.py` | 精细拆图：画反向 mask | 同上 |
| `x3-media-scripts/chroma_key.py` | 精细拆图：去绿→透明 | 同上 |
| `x3-media-scripts/ui_extract_fine.py` | 精细拆图**整机**（含 --preview 人工确认节点） | 同上 |
| `settings_Stop_hook.json` | 收工拦门 Stop hook 配置片段 | `~/.claude/settings.json` 的 `hooks.Stop` |

## 还原方法
把对应文件拷回上面的活源位置即可。Stop hook 把 `settings_Stop_hook.json` 内容塞回 `settings.json` 的 `hooks.Stop`（command 指向 `C:\ADHD_agent\.claude\quality-gate\pending_verify_gate.py`，那个脚本在仓库里）。

## 说明
- 透明化两条路子的来龙去脉、用法、场景区分：见 memory `project_quality_gate_and_interaction_module`。
- quality-gate 整套机制说明：见仓库 `.claude/quality-gate/README.md`。
