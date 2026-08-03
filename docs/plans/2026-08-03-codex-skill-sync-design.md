# Claude → Codex Skill 同步器设计

## 目标

为当前“Junction 与实体副本并存”的 Skills 建立安全、可审计的单向同步机制：Claude 侧公共指令为真源，实体副本同步到 Codex；Junction 保持直连；Codex 模型适配内容通过显式附注区块保留。

## 非目标

- 不拆除或重建现有 Junction。
- 不把全部 Skill 迁移到新的中央目录。
- 不自动删除 Codex 侧独有文件。
- 不同步账号、缓存、会话或其他运行状态。
- 第一版不自动挂入会话开工 Hook，只提供显式 `--dry-run` 与 `--apply`。

## 路径与所有权

- 公共真源：`C:\Users\linkang\.claude\skills\<skill>\`
- Codex 目标：`C:\Users\linkang\.agents\skills\<skill>\`
- 版本化工具：`C:\ADHD_agent\CodexRuntime\skills\sync_claude_to_codex.py`
- 自动化测试：`C:\ADHD_agent\tests\codex_runtime\test_skill_sync.py`
- 本机备份：`C:\Users\linkang\.codex\tmp\skill-sync-backups\<timestamp>\`

## 分类规则

每个 Claude 顶层 Skill 先分类：

1. Claude Skill 是 Junction/ReparsePoint：标记 `shared-junction`，跳过同步。
2. Claude 与 Codex 均为实体目录：标记 `physical-pair`，进入差异计算。
3. Claude 存在、Codex 不存在：标记 `missing-destination`，dry-run 报告；仅 `--apply --allow-create` 才允许创建。
4. Codex 独有 Skill：标记 `codex-only`，永不删除或回写 Claude。
5. 任一路径解析后越出声明的 source/destination 根目录：立即阻断。

## SKILL.md 合并协议

Codex 专属内容只能放在唯一一对标记内：

```markdown
<!-- CODEX-ONLY:START -->
Codex 专属调用、恢复或工具复用要求。
<!-- CODEX-ONLY:END -->
```

同步时：

1. 从 Codex 目标文件提取该区块。
2. 以 Claude `SKILL.md` 公共正文为基础。
3. 在正文结尾回填原 Codex 区块；若目标无区块则不新增空区块。
4. 多个区块、缺失结束标记或嵌套标记均视为格式错误并阻断该 Skill。
5. 合并后校验 YAML frontmatter：只要求存在合法的 `name`、`description`，且 name 与目录名一致；失败则不写入。

## 其他文件同步

- `scripts/`、`references/`、`assets/` 及 Skill 根目录普通文件按相对路径增量复制。
- 内容哈希相同则跳过。
- Codex 目标独有文件仅报告，不删除。
- 符号链接、Junction、超出 Skill 根目录的链接目标不跟随、不复制，并报告为阻断项。
- 不复制常见运行产物：`__pycache__`、`*.pyc`、日志、临时文件和输出目录。

## 执行模式

### `--dry-run`（默认）

只读扫描并输出：分类统计、将新增/修改/保留/跳过/阻断的文件、SKILL.md 附注状态及最终退出码。不得创建备份或改写目标。

### `--apply`

仅在扫描无阻断项时执行：

1. 把所有将修改的目标文件备份到带时间戳的本机目录。
2. 逐文件写临时文件，再用原子替换落地。
3. 任一文件失败即停止；已写文件按本轮备份回滚。
4. 写完重新扫描，确认计划差异归零；Codex 独有文件与 CODEX-ONLY 区块仍存在。

## 输出与退出码

- `0`：扫描或应用成功，无阻断项。
- `2`：存在需要人工处理的阻断项，未写入。
- `3`：应用失败但回滚成功。
- `4`：应用失败且回滚不完整，必须人工介入。

终端输出人类可读摘要；`--json-report <path>` 可额外输出结构化报告，供 Hook 或定时任务消费。

## 测试策略

使用临时目录构造最小 Skill 树，覆盖：

1. Junction 跳过。
2. 相同文件无操作。
3. 公共正文更新且 CODEX-ONLY 区块保留。
4. 缺失/重复/未闭合附注标记阻断。
5. frontmatter 缺字段或 name 不匹配阻断。
6. 新文件复制、目标独有文件保留。
7. `--dry-run` 零写入。
8. apply 前备份、原子写入、失败回滚。
9. 路径越界与链接拒绝。
10. 对真实目录执行 dry-run，确认只报告预期的实体副本差异。

## 验收标准

- dry-run 对真实目录不产生任何文件变更。
- 32 个现有 Junction 被识别为跳过，不被遍历覆盖。
- 8 个已知分叉 Skill 被列入差异报告。
- 模拟 apply 后公共内容与 Claude 一致，Codex 附注逐字节保留。
- 任何阻断项出现时，真实 Skills 零写入。
