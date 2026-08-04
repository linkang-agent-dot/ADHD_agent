# X3 节日策划文档开工重复命中知识库路径漂移

- 日期：2026-08-03
- 任务：起草 X3 8–10 月节日需求文档2
- 现象：按会话 AGENTS.md 的 `.Codex\projects\...` 路径读取 X3/节日 memory 失败；随后又误读 `errata\open\README.md`，第二次报路径不存在。
- 根因：本机共享项目 memory 真源仍在 `.claude\projects\...`；错误仓说明位于 `CodexMemory\errata\README.md`。虽已有同类 resolved 记录，本轮开工未先复用其纠偏结论。
- 处理：改读 `.claude` 共享真源与 `errata\README.md`；后续读取项目 memory/错误仓说明前先检查实际路径，并优先复用已有 resolved 结论。
- 状态：open

## 补充：同类路径漂移再次命中

- 现象：在“新增 10 月美需 HTML”任务中，再次按 AGENTS.md 的 `.Codex\projects\...` 读取失败，并再次误读 `errata\open\README.md`。
- 根因：本会话的上游指令仍给出了两个已知漂移路径，开工时未先查阅已有 errata 的纠偏结论。
- 处理：后续本机共享 memory 直接使用已验证的 `.claude\projects\...`，errata 格式直接读 `CodexMemory\errata\README.md`；不再重试已知错路径。

## 补充：静态验收组合命令被浏览器探测 exit 1 污染

- 现象：HTML 结构与链接检查均输出正常，但末尾 `Get-Command msedge,chrome` 未命中并返回非零，使整条组合命令被标为失败；占位正则 `换.*主题` 还把“替换……同主题”误报为占位。
- 根因：把允许零匹配的环境探测与强断言放在同一组合命令；占位模式过宽，跨中文标点吞掉无关文本。
- 处理：后续把环境探测独立执行并显式容忍零匹配；占位扫描用精确词组而不是 `换.*主题` 贪婪模式。

## 补充：Chrome 截图落盘与同步断言竞态

- 现象：Chrome 输出“554583 bytes written”且文件随后真实存在，但紧跟进程返回的 `Test-Path` 当刻为 false，命令被自定义异常误判失败。
- 根因：headless Chrome 报完成与 PowerShell 观察到文件之间存在极短落盘可见性竞态。
- 处理：截图命令与文件存在性检查拆成两步；不在同一进程返回瞬间做 fail-closed 断言。

- 2026-08-03 再次复现：10 月万圣美需 HTML 截图时，Chrome 已输出 `591304 bytes written`，但同一组合命令内的 `Get-Item` 仍瞬时报不存在。后续本任务已改为独立检查。

## 补充：等待子任务低于工具最小超时

- 现象：调用 `wait_agent(timeout_ms=1000)` 被拒，工具要求至少 10000 ms。
- 根因：沿用短轮询习惯，未遵守 collaboration wait 的参数下限。
- 处理：后续该工具等待统一使用 `timeout_ms>=10000`。

## 补充：Windows `rg` 位置参数误用通配路径

- 现象：把 `ActvRank*` / `*Rank*` 作为 `rg` 的路径参数，Windows 返回路径语法错误，组合命令 exit 1。
- 根因：Windows 下 `rg` 不负责展开位置参数中的文件通配符。
- 处理：先用 `rg --files <目录> | rg <文件名模式>` 找到真实文件，再对明确路径检索内容。
