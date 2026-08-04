# HTML 联合校验中的 Node 语法检查超时

- 日期：2026-08-04
- 任务：静态验证 BINGO 101830 补偿核对页
- 现象：Python 静态检查内嵌调用 `node --check -` 后命令整体超时。
- 根因：将 Node 的标准输入语法检查嵌入 Python 子进程，当前环境下进程未按预期及时退出。
- 处理：拆分数据/DOM 静态检查与 JavaScript 语法检查，避免嵌套标准输入链路；以后不在限时 Python 校验器中嵌套 `node --check -`。
- 状态：open
