# Datain 单元素筛选 JSON 与 errata README 路径

- 日期：2026-08-03
- 任务：对比 X3 马戏节与深海节 D0-D2 收入
- 现象：PowerShell 将单元素 `dimensionFilters` 数组经管道传给 `ConvertTo-Json` 后解包成对象，Datain 脚本收到非数组结构并报 `AttributeError: 'str' object has no attribute 'get'`；随后按文字说明读取 `errata\open\README.md`，但实际 README 位于 `errata\README.md`；HTML 生成后，浏览器自动化安全策略又拒绝访问本地 `file://` URL；task-checker 首次启动同时指定 `agent_type` 与 `fork_turns=all` 被编排器拒绝；修报告时首次 `apply_patch` 因未包含整条单行 CSS 上下文而匹配失败。
- 根因：PowerShell 管道枚举单元素数组；AGENTS.md 对 README 所在目录的表述与当前目录结构不一致；浏览器运行时不允许自动化访问本地文件 URL；专用 agent 角色不能使用完整历史 fork；长单行内容补丁上下文不精确。
- 处理：用 `ConvertTo-Json -InputObject $array` 保留外层数组后重跑；errata 格式改读父目录 README；不绕过浏览器安全策略，改用静态 HTML/数值校验并向用户提供本地可点击文件链接；task-checker 改为 `fork_turns=none` 并在任务文本中显式给出全部路径与清单；重读目标文件后把 HTML 修改拆成三个小补丁并使用完整行上下文。
- 复发：同日 FCOL 马特乌斯分析时再次照 AGENTS.md 文字去读 `errata\open\README.md` 并报路径不存在；随后通过列目录确认并改读 `errata\README.md`。在入口规范修正前，固定直接使用父目录路径。
- 状态：open
