# X3 克隆本地跨服测试玩家时 BSON ID 宽度错误

- 日期：2026-08-06
- 任务：为 3080/3090 马戏寻宝世界榜验证准备第二服测试玩家。
- 现象：从 3080 克隆 ServerPlayer 到 3090 后，玩家级 GM 加载报 `InvalidCastException: BsonInt32 -> BsonInt64`。
- 根因：Python 写入的新 `_id`/`basic.uid` 数值落成 BSON Int32；服务端模型要求玩家 ID 是 Int64。虽然数值范围能放进 Int32，序列化类型仍不兼容。
- 处理：第一次把 `_id` 和 `basic.uid` 都改成 Int64 后又出现反向的 `BsonInt64 -> BsonInt32`；结构对比确认混合口径为 `_id=Int64`、`basic.uid=Int32`。最终只让 `_id` 用 `bson.int64.Int64`，`basic.uid` 保持 Python int/BSON Int32，再重跑玩家加载 GM。
- 状态：open
