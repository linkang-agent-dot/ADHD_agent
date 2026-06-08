---
name: reference_obsidian_kb_tag_taxonomy
description: Obsidian KB(C:\ADHD_agent\KB)的5维嵌套标签规范，归档新笔记/整理图谱时按它打标签
metadata: 
  node_type: memory
  type: reference
  originSessionId: d6326058-d80c-462c-9a55-ef696b233269
---

Obsidian 知识库 `C:\ADHD_agent\KB`（vault 根，含 `.obsidian`，约 129 篇）的标签体系。2026-06-04 把原来扁平、同义词各写各的标签统一重做成 **5 维嵌套命名空间**，并开启图谱 `showTags`。归档新笔记或再整理时，frontmatter `tags:` 必须按这 5 维填，别再退回扁平词。

## 5 个维度（前缀固定）
- `kind/` 笔记性质：产出 · 方法论 · skill · 脑图 · 计划 · moc
- `domain/` 领域：数据复盘 · 配置换皮 · 活动部署 · 美术媒体 · 本地化 · 竞品 · 通知协作 · 文档 · agent开发 · 前端 · 运维 · 媒体分析 · 个人助理
- `proj/` 项目：P2 · X2 · X3 · 通用（巨猿=X2 别名）
- `fest/` 节日：春节·情人节·科技节·复活节·夏日节·圣诞节·占星节·推币机·挖矿·拓荒节·深海节·登月节·周年庆·音乐节·万圣节·感恩节·弹珠
- `year/` 时间：2025 · 2026

示例：一篇 X2 夏日节复盘 → `tags: [kind/产出, domain/数据复盘, proj/X2, fest/夏日节, year/2026]`

## 同义词合并（曾经的坑）
- 复盘/数据回归/数据分析/数据复盘/评级 → 统一 `domain/数据复盘`
- 换皮/配置/活动配置/数值设计/活动设计/卡册/养成线 → 统一 `domain/配置换皮`
- 排期/部署/审核/甘特图/igame → `domain/活动部署`

## 打标签的可靠信号（按优先级）
1. **文件夹路径**最可靠（如 `产出-数据分析/`→数据复盘，`产出-数值设计/`→配置换皮，`运营skill/Skills-xxx/` 子目录名直接对应 domain）
2. 文件名里的无歧义名词（换皮/集卡/卡册/美术/本地化/竞品/前端）
3. 旧标签
4. ⚠️**别扫正文前若干字推断 proj/fest/year**——会把"顺带提到"的项目/节日/年份全抓进来造成大量误报（首页索引尤其严重）。proj/fest/year 只从 路径+文件名+旧标签 推。
5. ⚠️domain 关键词别用贪婪词："设计"会误命中前端、"工具/审核"会乱挂——只用无歧义名词。

## 图谱配置
`.obsidian/graph.json`：`showTags:true` + colorGroups 按 proj/P2·X2·X3 和 kind/skill·方法论·产出 上色。改 graph.json 时若 Obsidian 正开着，可能被它退出时覆盖，需重载库。

相关：[[reference_output_paths]]（KB 各产出固定路径）
