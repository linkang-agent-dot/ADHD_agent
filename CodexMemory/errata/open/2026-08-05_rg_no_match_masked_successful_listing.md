# 复合诊断命令被 rg 零匹配退出码误报失败

- 日期：2026-08-05
- 任务：接管英雄主动 BUFF 会话的 sub-agent handoff
- 现象：命令前半段已成功列出 `_index` 文件并获得完整 session id，后半段 `rg` 零匹配返回 1，导致整次工具调用标记失败。随后对 5MB 内嵌 HTML 使用带中文、空格和 `class=\"...` 的复杂正则再次零输出/exit 1。
- 根因：把“列目录”和“可选文本搜索”放进同一复合命令，未按既有 `feedback_shell_composite_exitcode` 纪律隔离 `rg` 的零匹配退出码；第二次则是不必要地一次组合过多模式和转义，难以判断是无匹配还是转义偏差。
- 处理：直接使用已列出的完整 session id 执行 claim；以后可选 `rg` 查询单独调用，或显式把 exit 1 归一化为无结果而非失败。大型单行 HTML 先用单个稳定字面量 `Select-String -SimpleMatch` 定位，再逐段扩展，不再先写复杂组合正则。
- 状态：open
