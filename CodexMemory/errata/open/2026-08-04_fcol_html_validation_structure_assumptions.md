# FCOL HTML 验证脚本误判页面结构

- 日期：2026-08-04
- 任务：验证永恒评价页的新卡数据与合体页链接。
- 现象：首版断言把 `el_list.json` 当作顶层列表；`pandas.read_html` 后用纯中文球员名做精确等值；合体页则假定每个 iframe 都有 `src`。三个假设分别触发断言失败和 `NoneType` 路径错误。
- 根因：实际结构为 `el_list.json['db']`；HTML 姓名单元格同时包含中英文，pandas 会拼接为一个字符串；合体页只给首屏 iframe 设 `src`，其余用 `data-src` 懒加载。
- 处理：数据库数量改查 `len(payload['db'])`；球员名用可见中文前缀匹配；iframe 统一取 `src or data-src`。修正后 69 卡、三张新卡、五个 iframe 全部验证通过。
- 状态：resolved
