# CrossActivityMgr 文件名通配符再次作为 rg 路径

- 日期：2026-08-06
- 场景：确认跨服活动删除/重部署实现。
- 错误：把 `Module\CrossActivityMgr*` 直接作为 rg 路径。
- 结果：Windows os error 123；仅另一个明确文件返回命中。
- 正确做法：先 `rg --files Module | rg 'CrossActivityMgr'` 得到明确文件列表，再逐个传入内容搜索。
- 防复发：路径通配符问题已重复多次，任何 `rg <pattern> <path*>` 都应先改成文件清单管道。
