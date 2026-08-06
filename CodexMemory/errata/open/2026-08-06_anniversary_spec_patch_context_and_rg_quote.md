# 周年策划案补丁上下文与 PowerShell rg 引号错误

- 日期：2026-08-06
- 任务：X3 周年限定皮肤表现策划案读者测试后修订
- 现象：首次补丁把 DOM snapshot 中的 `generic:` 文本误当成 HTML 源码上下文，导致 apply_patch 校验失败；随后在 PowerShell 双引号字符串中对 `class="flow"` 转义不当，导致 rg 正则出现未闭合分组。
- 根因：没有先从源文件重新定位精确上下文，同时混用了 JavaScript/PowerShell/正则三层引号规则。
- 处理：先用 PowerShell 单引号包裹 rg 正则读取真实源行，再把修订拆成小补丁；后续 DOM snapshot 只用于页面语义验证，不直接作为源码补丁上下文。
- 状态：open
