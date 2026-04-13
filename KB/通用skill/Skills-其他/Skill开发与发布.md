---
aliases: [skill-creator, writing-skills, publish-skill, mcp-builder, find-skills]
tags: [skill, 元工具, skill开发, mcp]
---

# Skill 开发与发布

## 一、Skill 创建器（skill-creator）
**路径**：`.agents/skills/skill-creator/`
**触发**：`从零写skill` `跑eval` `优化触发描述` `benchmark`

工作流：
1. 草稿编写
2. 并行评测（eval）
3. 基准测试（benchmark）
4. 描述优化
5. 打包

含工具：`agents/`、`assets/`、`eval-viewer/`、`references/`、`scripts/`

---

## 二、写 Skill（writing-skills）
**路径**：`.agents/skills/writing-skills/`
**触发**：`创建/编辑/验证 skill`

TDD 思路：
1. 写 skill 文档
2. 压测子代理
3. RED-GREEN-REFACTOR 迭代

参考文档：
- `anthropic-best-practices.md`
- `persuasion-principles.md`
- `testing-skills-with-subagents.md`

---

## 三、发布 Skill（publish-skill）
**路径**：`.cursor/skills/publish-skill/`
**触发**：`发布skill` `upload skill` `publish skill`

将 skill 规范化并发布到内部 `git.tap4fun.com/skills` / SkillsMP 平台。

---

## 四、MCP 构建（mcp-builder）
**路径**：`.agents/skills/mcp-builder/`
**触发**：`搭建MCP` `接API` `MCP Server`

指导用 Python（FastMCP）或 TypeScript（MCP SDK）搭建 MCP 服务器：
- 工具设计最佳实践
- 评测流程
- 参考实现

---

## 五、发现 Skill（find-skills）
**路径**：`~/.cursor/skills/find-skills/`
**触发**：`how do I do X` `find a skill for X` `扩展能力`

引导使用 Skills CLI（`npx skills`）发现并安装 skills.sh 生态中的技能包。

---

## 六、Cursor 内置元工具

| 工具 | 路径 | 功能 |
|------|------|------|
| create-rule | `~/.cursor/skills-cursor/` | 创建 `.mdc` 规则文件 |
| create-skill | `~/.cursor/skills-cursor/` | 编写 SKILL.md |
| create-subagent | `~/.cursor/skills-cursor/` | 创建自定义 subagent |
| babysit | `~/.cursor/skills-cursor/` | PR 看护（冲突/CI/评论） |
| migrate-to-skills | `~/.cursor/skills-cursor/` | 规则→skill 迁移 |
| shell | `~/.cursor/skills-cursor/` | 字面 shell 执行 |
| statusline | `~/.cursor/skills-cursor/` | CLI 状态栏配置 |
| update-cli-config | `~/.cursor/skills-cursor/` | CLI 配置修改 |
| update-cursor-settings | `~/.cursor/skills-cursor/` | VSCode settings.json |
