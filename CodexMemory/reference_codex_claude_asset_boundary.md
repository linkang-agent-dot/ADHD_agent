# Codex 与 Claude 资产边界

## 必须独立并纳入 ADHD_agent Git
1. **Codex memory**：模型能力边界、工具恢复链、行为反馈。
2. **Codex errata**：用户纠错、工具绕道和复核状态；否则只留在本机无法跨设备积累。
3. **Codex 全局规则真源**：Codex 的开工顺序、恢复策略和验收规则；用户目录内只保留薄入口。
4. **Codex agent 定义**：Codex 使用 `.toml` 和自身 agent 类型，不能直接拿 Claude agent 描述当真源。
5. **Codex hooks/config 适配层**：保存无密钥模板、脚本和安装说明；实际启用文件部署到 `.codex`。
6. **Codex skill 适配与覆盖项**：只保存 Codex 特有 wrapper、路由差异和覆盖，不复制业务 skill 全文。

补充约束：全局 `~/.codex/AGENTS.md` 和实际 `~/.codex/agents/*.toml` 仍需留在 Codex 自动发现路径，但其可版本化真源应放在 `CodexRuntime`，通过安装/同步脚本部署；不要直接把 Claude 的 agent Markdown 当成 Codex TOML。Import 后还要审计机械把 `.claude` 错改成 `.Codex` 的历史问题。

## 必须共用单一真源
1. P2/X2/X3/FCOL 项目事实与知识库。
2. 配置表、引用链、数值规则、业务方法论和项目档案。
3. 跨模型都成立的通用 skill 内容；Codex 只做兼容适配。

### D-1：Skill 当前是混合态，不是统一单源（2026-08-03实测）

- `~/.agents/skills`：59 个顶层 skill；`~/.claude/skills`：58 个；同名 58 个。
- Claude 侧 32 个是 Junction，属于实时共用。
- 其余同名实体目录中：14 个 `SKILL.md` 哈希相同、8 个哈希不同。
- 8 个已分叉 skill：`bug-scan`、`bulk-mail-reissue`、`igame-x3-activity-deploy`、`p2-x2-reskin`、`x3-config-export`、`x3-feature-test`、`x3-media`、`x3-translation-automatic`。

因此不能再写“业务 skills 已全部一处修改两边生效”。当前是 Junction 与实体副本并存，缺少统一同步制度。

建议落法：
1. Claude 侧作为指令真源，向 `.agents/skills` 单向同步；Junction 项自动识别并跳过。
2. `SKILL.md` 在 Codex 侧保留显式区块 `<!-- CODEX-ONLY:START -->...<!-- CODEX-ONLY:END -->`，同步时先提取、覆盖公共正文、再回填附注。
3. 同步前强校验 YAML frontmatter 至少含 `name`、`description`；不满足则阻断，避免 Claude 侧合法但 Codex 无法加载。
4. `scripts/`、`references/`、`assets/` 从 Claude 真源做增量复制；默认不删除 Codex 侧独有文件。确需镜像删除时必须单独审计清单。
5. Codex 专属 wrapper 不混入公共脚本，放 `CodexRuntime/skill-overrides/<skill>/`。
6. 同步脚本必须支持 `--dry-run`、差异清单、备份/回滚点，并在同步后扫描错误的 `.Codex` 路径和执行 skill 加载验证。

首次真实 dry-run 审计补充（2026-08-03）：
- `state/`、`state/history.jsonl`、实际 `config.json`、`.env*`、批次输入/结果 JSON 都属于运行态或私密资产，必须在计划阶段直接排除；共享配置只允许无密钥模板。
- 首轮未过滤时曾出现 89 add + 13 modify；修正后为 20 add + 11 modify，且 `x3-media` 的 cookie/token 配置和 69 个运行态/批次文件全部退出计划。
- `x3-feature-test` 的 Unity CLI/MCP/DebugUtils 路由已收进 Codex 侧显式 `CODEX-ONLY` 区块，公共正文仍由 Claude 真源覆盖。
- 首次正式 apply 已于 2026-08-03 完成：备份点 `~/.codex/tmp/skill-sync-backups/20260803T091802.021062Z`；写后 dry-run 为 `preserve=11, skip=322, blockers=0`，无待新增/修改项。证据见 `CodexMemory/reports/skill-sync-post-apply-20260803.json`。
- Codex 原生能力清理（2026-08-03）：`brainstorming`、`writing-plans`、`executing-plans` 等 10 个旧元流程 skill 已从 `~/.agents/skills` 卸载，并在同步器 `DEFAULT_CODEX_EXCLUDED_SKILLS` 中永久排除；Claude 侧改为实体备份，不受 Codex 清理影响。`using-git-worktrees` 与 `systematic-debugging` 因仍有独立标准流程而保留。
- 活跃 skill 根禁止放 `.bak.<timestamp>` 备份和 `*-workspace` 评测目录；前者进入 `CodexMemory/skill-quarantine/`，后者进入 `CodexMemory/skill-workspaces/`，两类运行内容均不进 Git。

### D-1 首轮同步器 dry-run（2026-08-03）

- 工具：`CodexRuntime/skills/sync_claude_to_codex.py`；默认 dry-run，支持 JSON 报告、事务备份和失败回滚。
- 自动化：29 项测试通过，覆盖 Junction、CODEX-ONLY、frontmatter、多行 YAML、路径安全、零删除、备份与回滚。
- 真实分类：`shared-junction=32`、`physical-pair=22`、`non-skill-directory=4`、`codex-only=1`。
- 真实计划：`add=88`、`modify=13`、`preserve=11`、`skip=1052`；其中修改 `SKILL.md=7`、其他文件=6。
- 零写入证明：dry-run 前后 Codex Skills 全树指纹均为 `3CE435C9C3AE29836D62B68071E52390758E84A7BF0F0FA5B6CA6C31E49C620F`。
- 唯一 blocker：`x2-localization-translator` 的 Claude 与 Codex `SKILL.md` 都没有 frontmatter；在补齐 Codex 所需元数据前禁止 apply。
- 7 个真实 SKILL 正文差异：`bug-scan`、`bulk-mail-reissue`、`igame-x3-activity-deploy`、`x3-config-export`、`x3-feature-test`、`x3-media`、`x3-translation-automatic`。目前均无 CODEX-ONLY 标记。
- 差异审计：前六项中，机械把 Claude 改成 Codex 的文案/命令应由 Claude 真源覆盖；`x3-config-export`、`x3-media`、`x3-translation-automatic` 的 Codex 侧主要是落后于 Claude 真源。`x3-feature-test` 含 Unity CLI/Codex 工具路由增量，首次 apply 前需先迁入 CODEX-ONLY 或回流 Claude 真源。
- 报告：`CodexMemory/reports/skill-sync-dry-run-20260803.json`。当前结论为 **apply 不安全**，保持只读。

## 只同步模板，禁止上传运行状态
1. `config.toml`、hooks 配置：同步去密钥模板，不同步机器路径差异和账号信息。
2. Browser/插件配置：同步安装说明，不同步 profile、cookie、登录态。
3. MCP：同步 server 清单和环境变量名，不同步 token。
4. Hooks trust hash、工作/个人 `CODEX_HOME` 配置：只保存生成规则和示例，实际信任状态与账号隔离状态留在各自本机目录。

## 保持本机，不进入 Git
- `auth.json`、cookie、token、浏览器 profile。
- `sessions/`、history、SQLite/WAL、日志、缓存、临时文件。
- `CodexMemory/handoffs/` 下生成的用户原话、checkpoint、final、state、index 与 transcript；该目录只版本化 README 和 `.gitignore`。
- 插件下载缓存、Node REPL 状态和 browser runtime 状态。

## 推荐仓库结构
```
C:\ADHD_agent\CodexMemory\          # 已落地：记忆、复核状态、边界决策
C:\ADHD_agent\CodexRuntime\         # 后续：AGENTS 真源、agents、hooks、config templates
  AGENTS.md
  agents\
  hooks\
  config\
  skill-overrides\
```
