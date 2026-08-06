# DebugUtils reporter-filter 在无 Reporter 时假成功

- 日期：2026-08-06
- 场景：检查 Unity 客户端是否收到新邮件通知。
- 现象：`probe.py reporter-filter` 外层返回 `ok:true`，但 `FindObjectOfType<Reporter>()` 为 null，后续全是 NullReference，filtered_count 也是错误文本。
- 原因：当前 Editor 场景没有 Reporter 组件，probe 未将嵌套失败提升为外层失败。
- 正确做法：先跑 `reporter-count`/检查 `__r != null`；无 Reporter 时改查 Editor.log、客户端真实邮箱 UI 或 TGS 数据，不信外层 ok。
- 防复发：probe reporter 系命令必须同时验证 reporter 对象和 filtered_count 的数值类型。
