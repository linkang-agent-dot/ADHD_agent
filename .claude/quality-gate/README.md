# quality-gate — 收工前自动验收

一套"做完活、想收工那一刻自动跳出来帮你对清单"的机制。
**通用：一个验收员 + 多份清单**，按任务类型(type)选清单。已铺：策划案 / 配置·换皮 / i18n。

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
- `type`：`design-doc` / `config` / `i18n`（决定验收员读哪份清单）
- 其余字段随 type 不同（产物位置）：design-doc=sheet_id；config=expected_branch + tsv_changed (+sheet_id)；i18n=text_table + data_dir
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
