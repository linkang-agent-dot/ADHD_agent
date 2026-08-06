# 服务端搜索误假设 HEngine 源目录存在

- 日期：2026-08-06
- 场景：定位 Entity 的字符串 GetMeta API。
- 错误：把 `C:\x3-project\server\HEngine` 作为搜索根。
- 结果：该目录不存在，rg exit 1，虽然另一个有效根已有命中。
- 正确做法：先用 `rg --files C:\x3-project\server` 定位 `EntityMetaBase/EntityBase`，再搜明确候选文件；第三方 HEngine 可能只以程序集/包存在。
- 防复发：多根搜索前先 Test-Path，每个根必须确认存在，避免一个坏根污染命令结果。
