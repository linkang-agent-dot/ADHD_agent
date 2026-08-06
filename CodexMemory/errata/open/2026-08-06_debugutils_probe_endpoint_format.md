# DebugUtils probe endpoint 不接受 HTTP URL

- 日期：2026-08-06
- 场景：通过 `probe.py windows` 读取 Unity 当前窗口。
- 错误：传入 `--endpoint http://127.0.0.1:21891`。
- 结果：底层 feval 返回 `Invalid address`，probe 外层仍显示 `ok: true` 和空窗口，容易形成假成功。
- 正确做法：先检查 `probe.py` 的 endpoint 参数约定，使用其接受的地址格式；同时以 `feval_response.output/returncode` 和实际窗口计数判断是否有效，不能只看外层 `ok`。
- 防复发：DebugUtils probe 的外层成功不等于底层连接有效；遇到空结果必须检查嵌套响应。
