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

## 只同步模板，禁止上传运行状态
1. `config.toml`、hooks 配置：同步去密钥模板，不同步机器路径差异和账号信息。
2. Browser/插件配置：同步安装说明，不同步 profile、cookie、登录态。
3. MCP：同步 server 清单和环境变量名，不同步 token。
4. Hooks trust hash、工作/个人 `CODEX_HOME` 配置：只保存生成规则和示例，实际信任状态与账号隔离状态留在各自本机目录。

## 保持本机，不进入 Git
- `auth.json`、cookie、token、浏览器 profile。
- `sessions/`、history、SQLite/WAL、日志、缓存、临时文件。
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
