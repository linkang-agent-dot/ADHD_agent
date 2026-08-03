---
name: codex-cli-docs
description: Codex CLI 官方说明书入口 + 迁移相关关键机制速查（config/skills/hooks/AGENTS.md/exec/MCP/subagents/import）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 5f06fb34-9143-4c03-b749-95fdfb8aadd1
  modified: 2026-08-03T03:41:43.141Z
---

# Codex CLI 官方文档速查（2026-07 抓取）

## 文档入口
- 官方文档站：`https://developers.openai.com/codex/<页名>`（308 跳转到 `https://learn.chatgpt.com/docs/<页名>`，**去掉 codex 前缀**；直接猜 learn 站路径容易 404，从 developers.openai.com 走跳转最稳）
- 关键页：`/docs/import`（从 Claude Code 导入）、`/docs/hooks`、`/docs/build-skills`、`/docs/non-interactive-mode`（codex exec）、`/docs/agent-configuration/agents-md`、`/docs/agent-configuration/subagents`、`/docs/extend/mcp`、`/docs/config-file/config-reference`、`/docs/changelog?type=codex-cli`
- GitHub 仓库：github.com/openai/codex（安装：npm `@openai/codex` / PowerShell 脚本；Windows 原生支持 2026-03 起）

## 迁移相关关键事实（对做 Claude Code → Codex 同步环境）
- **官方导入流**：ChatGPT 桌面应用 Settings > Import，可导 AGENTS.md/config.toml/skills/plugins/MCP/hooks/slash commands/subagents/近30天会话；只增不删。CLI 侧有 `migrate-to-codex` skill（`--scan-only/--plan/--dry-run`，三方资料）。导完必查：skill 工具权限、MCP 鉴权头、hook 行为变化、带文件路径的 prompt 模板。
- **AGENTS.md**：全局 `~/.codex/AGENTS.md`（`AGENTS.override.md` 优先）+ 仓库根→cwd 逐层拼接，近者覆盖远者；合并上限 `project_doc_max_bytes` 默认 **32 KiB**（CLAUDE.md 直搬要注意体积）。
- **Skills**：SKILL.md（frontmatter 要 name/description，兼容 agentskills.io 标准，可带 scripts/references/assets）；位置 `$CWD/.agents/skills` / `$REPO_ROOT/.agents/skills` / `$HOME/.agents/skills`；触发=描述自动匹配 或 `$skill-name` 显式调。
- **Hooks**：比早期三方文章说的强——事件全集含 PreToolUse/PostToolUse/SessionStart/**Stop**/UserPromptSubmit/SessionEnd 等，带 matcher 正则，JSON(`~/.codex/hooks.json`) 或 config.toml 均可；stdin JSON 入、stdout JSON 出（`continue:false` 可拦截）→ **收工 Stop hook 理论上可平移**。限制：SessionEnd 超时仅 1s；非托管 hooks 要 `/hooks` 手动信任。
- **无头执行**：`codex exec "提示"`（对标 `claude -p`）；`--json` JSONL 输出、`-o` 落最终消息、`--output-schema` 结构化、`--sandbox workspace-write|danger-full-access`、`--ephemeral` 不留会话；恢复=`codex exec resume --last`；认证 `CODEX_API_KEY` 环境变量 → 定时任务改造用这套。
- **MCP**：config.toml `[mcp_servers.<id>]`，stdio(command/args/env) 或 HTTP(url/bearer_token_env_var)；`codex mcp add/list/login`；OAuth 用 `codex mcp login <name>`。桌面应用/CLI/IDE 扩展共享同一 config.toml。
- **Subagents**：`~/.codex/agents/` 或项目 `.codex/agents/` 下 TOML，必填 name/description/developer_instructions，可覆盖 model/sandbox/mcp_servers。
- **config.toml 核心键**：model / model_provider / model_reasoning_effort / approval_policy(untrusted|on-request|never) / sandbox_mode(read-only|workspace-write|danger-full-access) / features（多代理、memory 等开关）；`CODEX_HOME` 环境变量换配置目录（→ 对标工作/个人号隔离 [[cc-config-partition]]）。

## 本机实测状态（2026-07-31 安装）
- CLI 已装：`npm i -g @openai/codex` → codex-cli 0.146.0；`codex doctor` 全绿（网络直连 OK 无需代理）
- **本机早有 Codex 环境**：桌面版/VS Code 扩展在用（89 个历史会话），ChatGPT 账号已登录，`~/.codex/config.toml` 已有 unityMCP + 官方插件；**`~/.agents/skills` 已同步 57 个 Claude skill**（之前导入流干的，迁移大头已完成）
- **模型坑**：config 里 `gpt-5.6-sol` 是桌面版专属，CLI+ChatGPT 账号不支持（400）；CLI 默认模型=`gpt-5.6-terra` 可用。解法=profile 独立文件 `~/.codex/cli.config.toml`（内容 `model = "gpt-5.6-terra"`），用 `codex exec --profile cli` 调；⚠️新版 profile 必须独立文件，写 config.toml 里 `[profiles.X]` 会报 legacy 错
- 修过：`.agents/skills/p2-x2-reskin/SKILL.md` 缺 YAML frontmatter 加载失败 → 已补 name/description（修复后验证被配额挡住，下次跑通看有无 `failed to load skill` 日志）
- **🔴 头号阻塞：账号是免费档**，3 次冒烟测试（各 ~13k tokens）即耗尽配额，2026-08-25 重置。真要并行用需 Plus/Pro 订阅，或 `CODEX_API_KEY` 走 API 计费
- **配额撞限后 auth.json 消失**（未人为删除，疑似 token 刷新失败被 CLI 清掉）→ 需重跑 `codex login`（浏览器交互流程）
- **桌面版/网页换号 ≠ CLI 已登录**：CLI 凭据独立存 `~/.codex/auth.json`，换号后必须单独 `codex login`（本地起 localhost:1455 授权服务，headless 机器用 `codex login --device-auth`）

## 环境搬迁完成度（2026-07-31 收工状态）
- ✅ 已完成：CLI 装好 · 57+2 个 skill 同步（补了 url-reader/x2-dk-manager）· hooks.json（隔离闸门/开工flag/收工自检+通知，脚本共用 Claude 侧真身，4 个脚本路径已验存在）· 3 个 subagent TOML · **全局 `~/.codex/AGENTS.md` 薄壳**（开工先读 CLAUDE.md + MEMORY.md，真源不复制）
- **⚠️ 导入流的机械改名 bug（污染范围比初判大）**：桌面版 Import 会把文件内容里的 `.claude` 路径错改成 `.Codex`——3 个 subagent TOML（4 处）+ `.agents\skills` 下 **16 个 SKILL.md**（08-03 由 Codex 自报 errata 暴露，已批量修复 grep=0）。以后再跑 Import 后必对 `~/.codex` + `~/.agents` 全域 grep `\.Codex` 复查
- ✅ 08-03 新账号已 `codex login` 跑通（纯回复类 exec 正常，~15k tokens/次；skill 加载零报错，p2-x2-reskin 修复生效）
- **🔴 workspace-write 沙箱全机不可用（08-03 定性）**：`SetTokenInformation(TokenDefaultDacl) failed: 1344`（=安全信息更新内存不足，疑似域账号令牌组太多超 DACL 配额）；用户自己终端同报错，排除嵌套因素。只读沙箱正常。复现（不耗token）=`codex sandbox -c sandbox_mode="workspace-write" -- cmd /c "echo hello"`。**elevated 路线也不通**：UAC 跑过 codex-windows-sandbox-setup.exe 后仍报 `orchestrator_helper_launch_canceled: 1223`。可行解=`--sandbox danger-full-access`（信任档同 Claude Code 直跑 PowerShell；Claude 会话内被 classifier 拦，须用户自己终端跑/写进 cli profile）
- 新账号=ChatGPT Max 档（08-03 用户确认），配额不再是约束
- **日常启动**：交互=`codex`、无头=`codex exec "任务"`（08-03 已把桌面版写死的 `model="gpt-5.6-sol"` 从 config.toml 顶层删掉，裸命令直接用 CLI 默认 terra；桌面版下次启动若模型不对在其界面重选即可；`--profile cli` 仍可用作备份）；TUI 内：调 skill=`$skill名`、信任hooks=`/hooks`（首次一次）、续会话=`codex resume --last`、临时放开沙箱=启动加 `--sandbox danger-full-access`（仅当次）
- **✅ 08-03 TUI 实测：薄壳架构全线生效**——用户交互会话里 Codex 按 AGENTS.md 开工读了 CLAUDE.md+MEMORY.md（还主动播报 Token 周报/在途案子），用户问命令它自己找到本 memory 文件来答（Claude 沉淀→Codex 消费闭环成立）；命令经其 node 运行时通道执行成功（读操作，76s 偏慢），**未撞 1344**（该通道绕开进程沙箱路径）
- ⏸️ 待办：TUI 写文件验证（让 codex 建删一个 test 文件）→ 若读写都通则 1344 只影响 `codex exec` 无头场景（定时任务再议 danger-full-access）→ TUI `/hooks` 手动信任 hooks

## 五任务流程匹配实测（2026-08-03，验收基线）
- 一页验收纪要（FINAL）：`C:\ADHD_agent\KB\方法论\Codex CLI环境五任务验收纪要_20260803.md`
- 5 个高频任务全过（X3配置速查/grfal生图/Datain查询/Jira清单/补发表生成），**PreToolUse+Stop hook 实弹触发**，KB 触发规则、skill 路由、外部鉴权（Jira token/DATAIN_API_KEY/GRFal）、GBK 写文件规范全对齐；合计 ~30 万 tokens
- **两个已知短板（重要活盯这两点）**：①偏好现写不复用 skill 封装工具（X3 速查没用 actv_lookup.py 自己解析 tsv，结果对但违反复用原则）②数据口径细腻度弱（把 `_0d` 当日新增付费 cohort 当大盘总付费人数报，$34k/139人=ARPPU$247 明显异常没自查）
- grfal 组合任务全匹配范式：先读 reference_grfal_implementation.md → call_grfal.py 异步提交→轮询→下载→自验尺寸

## 工作/个人隔离（Codex 版，2026-08-03 建，对齐 [[reference_cc_config_partition]]）
- 个人启动=`codex-personal`（`%APPDATA%\npm\codex-personal.cmd`，设 `CODEX_HOME=~/.codex-personal`）；工作=裸 `codex`
- `~/.codex-personal`：config.toml（钉 terra 模型防 sol 400、无工作 MCP）+ AGENTS.md（指向**个人** memory=`~/.claude-personal/projects/C--Users-linkang/memory/`，禁写工作侧）+ hooks.json（含**GRFal 禁令** block_grfal.py，镜像 Claude 个人侧）
- skills 走 `$HOME/.agents/skills` 天然两号共享（对齐 Claude junction 设计）；**个人号需自行 `codex-personal login` 登个人 ChatGPT 账号**（凭据独立）
- 失败安全同 Claude 侧：工作 `~/.codex` 物理无个人内容

## Codex 错误仓库 + 每日纠错闭环（2026-08-03 建）
- **仓库**：`~/.codex/errata/`（README=规则卡，open\=待复核一条一文件，resolved\=已复核归档）；AGENTS.md 已强制 Codex 被纠错/结果被推翻/工具绕道时**当场写一条**
- **闭环**：错误先隔离在 errata（不污染正式 KB）→ 每天 21:00 ClaudeDailyReport 步骤 6d 扫描复核（≤3条/天，double-check 独立验证）→ 成立的按归口写入正式知识库（skill/must-check/memory）→ 日报出【Codex 巡检】四件套（问题/复核/方案/写入位置）给用户过目
- 首个入库案例：Datain cohort 指标坑 → 护栏已写 `datain-skill/SKILL.md`（.agents 下是 Junction，一处改两边生效）+ `workflow_data_analysis_must_check.md`

## 审计 Codex 会话实际行为（独立于模型自述的验证法）
- 会话日志=`~/.codex/sessions/<年>/<月>/<日>/rollout-*.jsonl`（按 LastWriteTime 排序取最新），逐行 JSON
- 关键事件类型：`user_message`/`agent_message`（对话）、`custom_tool_call`+`custom_tool_call_output`（工具调用，name=exec 的 input 里有真实 shell 命令）、`session_meta`（cwd/模型/沙箱模式）
- 用途：验证它真读了哪些文件/真跑了什么命令/有没有沙箱报错——和 Claude 侧「交付验证独立于 agent 自述」同一原则

- ✅ 08-03 权限最终裁决：用户批准本机全盘读写；全局配置已设 approval_policy=never、sandbox_mode=danger-full-access，doctor 验证 approval Never / filesystem unrestricted。后续不再修 workspace-write 1344；删除和生产操作仍按 AGENTS.md 确认。

## 相关
- 迁移总体评估（四类清单：零迁移共用/自动迁/手动改造/需重验）见本次对话结论；架构原则=**知识真源(KB/memory)不复制，两边薄壳入口指同一批路径**。
- [[workflow_handover_assetization]]
