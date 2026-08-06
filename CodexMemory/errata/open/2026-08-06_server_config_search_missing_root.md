# 服务端配置搜索包含不存在的 Config 根

- 日期：2026-08-06
- 场景：定位本地 MongoDB 连接。
- 错误：将不存在的 `C:\x3-project\server\Config` 与有效 Tools 根一起传给 rg。
- 结果：虽得到有效命中，整体仍 exit 1。
- 正确做法：先 Test-Path 每个候选根；本地 Mongo 权威值直接来自存在的 `Tools/drop_db.py`。
- 防复发：多路径 rg 不夹带未经验证的猜测目录，避免假失败。
