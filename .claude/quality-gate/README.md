# quality-gate — 收工前自动验收

一套"做完活、想收工那一刻自动跳出来帮你对清单"的机制。**两道门**（都在 `pending_verify_gate.py`，全程 fail-open）：
- **道1 · 验收**：有 `status=pending` 的 marker → 拦，派 task-checker 按 type 读对应清单跑验收。**通用：一个验收员 + 多份清单**（已铺 策划案完整性 design-doc / 配置·换皮 config / i18n / **策划案设计质量 design-merit**）。
  - ⚠️ `design-merit`（设计好不好）跟 `design-doc`（文档全不全/对不对）**互补且不同**：前者按需触发的"定稿前设计压测"，只 §1 客观项可 block，主体是顺目的长的递归拆解树（配套 `design-merit-qbank.md` 子问题库）。
- **道2 · 收工自检（反馈循环 + 归档）**（2026-06-04 加）：本次会话**动过文件**(Write/Edit) 且没刚拦过 → 拦一次，提醒过「① 新规律沉淀 ② 产物归档 ③ 复用工具」三问，**不靠用户提醒**。防死循环：时间戳(`.codify_check_ts` 180s) + `stop_hook_active` 双保险；纯对话不拦。无需建 marker，自动触发。

## 组成（分布在两处）

| 组件 | 位置 | 进本仓库 | 说明 |
|---|---|---|---|
| 各类型清单（标准） | `本仓库/<type>-checklist.md` | ✅ | rulebook 单一来源。已有 design-doc / config / i18n |
| 拦门脚本 | `本仓库/pending_verify_gate.py` | ✅ | settings.json 的 Stop hook 调它 |
| 通用验收员 agent | `~/.claude/agents/task-checker.md` | ❌ 留全局 | Claude 只在全局/启动目录找 agent；用户从家目录跑，故留全局。薄壳，运行时按 type 读本仓库对应清单 |
| 运行时标记 | `~/.claude/.pending_verify/*.json` | ❌ 不版本化 | 临时便利贴 |
| 开关 | `~/.claude/settings.json` 的 `Stop` hook | ❌ 全局配置 | command 指向本仓库脚本 |

## 标记格式
`~/.claude/.pending_verify/<任务>.json`：
```json
{"task": "深海节策划案", "type": "design-doc", "sheet_id": "1AbC...", "status": "pending"}
```
- `type`：`design-doc` / `config` / `i18n` / `design-merit`（决定验收员读哪份清单）
- 其余字段随 type 不同（产物位置）：design-doc=sheet_id；config=expected_branch + tsv_changed (+sheet_id)；i18n=text_table + data_dir；design-merit=sheet_id（+ 主目的，可选）
- `status`：`pending`(要拦) / `reviewed`(验收过、有 blocker 待用户定夺，放行)

## 工作流程
1. 主 Claude 开工 → 建 `<任务>.json`（status=pending，带 type + 产物位置）。
2. 想收工 → Stop hook 见 pending 标记 → 拦住。
3. 派 `task-checker`（传 type + 产物位置 + 任务名）→ 它读对应清单跑客观检查，输出 block/warn。
4. 全过 → 删标记 → 收工；有 blocker → 标记改 reviewed，问题列给用户『修/跳』；读不到 → 也改 reviewed + 明示"需人工确认"，不假装通过。

## 加新任务类型 = 只加一份清单
在本仓库写 `<newtype>-checklist.md`（含：怎么读产物 / 客观项表 / 主观项 / fail-closed），
建标记时 type 填 newtype 即可。验收员、脚本、hook 都不用改。

## 安全
- 平时无 pending 标记 → 拦门**完全不触发**。
- 拦门脚本自身出错 → **默认放行**(fail-open)，绝不卡死全部工作。
- 验收结果 fail-closed：读不到产物 = 不通过。

## 关掉 / 取消
- 取消某次拦截：删 `~/.claude/.pending_verify/` 下对应 `.json`。
- 彻底关闭：删 `~/.claude/settings.json` 里的 `Stop` hook 段。

## 重装全局验收员（万一丢了）
`~/.claude/agents/task-checker.md` 不在本仓库。内容 = 沙箱只读验收员 + 按 type 读本仓库 `<type>-checklist.md` + 输出 CHECK_DONE 的 JSON 格式。
