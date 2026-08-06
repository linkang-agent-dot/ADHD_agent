# DebugUtils probe 点击路径不能擅自去掉窗口状态后缀

- 日期：2026-08-06
- 场景：点击活动页的 `ActvRank/BtnRank` 真实入口。
- 错误：从 MCP 返回的完整 path 中删除了 ` [state: ..., layer: ...]` 后缀再传给 `probe.py click`。
- 结果：`GameObject.Find(...) returned null`。
- 原因：运行时窗口 GameObject 名称/path 包含状态后缀，probe 使用精确路径查找。
- 正确做法：优先原样复制 MCP 返回的 `path`；若仍失败，再逐级 GetChild 核对节点名。
- 防复发：UI 引用序列化结果里的 path 视为权威精确路径，不自行“清理”状态标注。
