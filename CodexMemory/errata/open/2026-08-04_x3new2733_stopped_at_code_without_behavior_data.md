# X3NEW-2733 排查停在代码层，漏查线上行为数据

- 时间：2026-08-04
- 用户纠正：还应检查线上已合服玩家是否仍有节日相关行为数据。
- 错误：初轮只证明了合服脚本会迁移 `ServerActivity` 与玩家活动数据，并核了 `ServerMergeShield`；这只能说明设计/持久化链路，不能证明线上玩家实际仍在参与活动或日志正常上报。
- 正确证据链：圈定已合服玩家或合服服段 → 取马戏节行为事件 → 比较合服前后与未合服 cohort → 检查事件量、人数、最近发生时间及关键模块覆盖。
- 后续规则：用户问“线上是否有数据”时，代码/配置只能作机制佐证，必须补实际线上数据查询后才可下结论。

## 同轮工具异常：Datain 初始化超时

- 现象：`get_game_info.py` 返回 `datain-api.tap4fun.com read timeout=15`，但进程 exit code 为 0。
- 判断：这是 API 初始化超时，不代表无权限或无数据；脚本把错误包成 JSON，不能只看退出码。
- 处理：检查输出中的 `error` 字段并重试；必要时按已知 X3=1090/TRINO_HF 权限执行最小只读查询，同时继续补权限/表结构验证。

## 同轮工具异常：误给 search_tables 传 datasource

- 现象：`search_tables.py` 报 `unrecognized arguments: --datasource TRINO_HF`。
- 原因：`--datasource` 只属于 `explore_tables.py` / `query_trino.py`；`search_tables.py` 仅接 `--keyword`。
- 后续规则：按脚本各自 help/Skill 参数表传参，不把查询执行器参数套到元数据搜索脚本。

## 同轮外部状态：Trino 队列拥堵

- 现象：`explore_tables.py` 对 5 张表的 DESCRIBE 均返回 `Too many queued queries for "datain"`。
- 判断：平台队列拥堵，不是表不存在；一次并发探索多表会进一步增加队列压力。
- 处理：改成单条最小 SELECT 分批执行，优先验证 `dl_user_login.server_id/real_server_id` 合服 cohort，再查活动/订单/资产；错误输出不得当成 0 行。

- 追加：5 日 `dl_user_login` 去重映射查询排队 601.8 秒后 HTTP read timeout=600。后续降级为 Jira 反馈日（2026-08-03）单日有限样本先取映射，再按映射做行为聚合；不要在队列拥堵时直接做多日全量 distinct。

## 用户要求更换执行方式

- 用户判断：怀疑当前 CLI 参数导致跑不出，要求不要继续沿用当前方式。
- 已知证据：同一 `TRINO_HF` 参数下 `SELECT 1` 成功，单日查询也返回两名 `server_id != real_server_id` 玩家；但为排除 CLI 封装/参数路径差异，后续改用马戏节日报生产脚本同款 `_datain_api.execute_sql` 直连调用。
- 规则：用户对取数执行面提出疑虑时，应换一条独立执行路径交叉验证，不能只反复重试同一 wrapper。

## 用户纠正：Datain 网页入口选错

- 现象：自动打开 `datain.tap4fun.com/` 后进入普通游戏数据页，又猜了 `/sql-lab` 空壳路由，未进入用户实际使用的查数页面。
- 用户处理：已手动挂好正确网页。
- 后续规则：用户说已挂好页面时，必须重新列出真实打开标签页并按标题/URL认领，禁止继续猜路由；以用户当前页面为真源。

- 追加工具异常：认领正确页 `https://datain.tap4fun.com/chart/sql?create=0` 后立即请求全页 `domSnapshot()`，页面较重导致 JS 执行超时并重置内核。后续重新连接后应先取轻量可见 DOM/截图或局部控件，避免对 SQL 编辑页做整页大快照。

- 再次异常：改用 `dom_cua.get_visible_dom()` 仍在 `claimTab` 后超时并重置，说明瓶颈在重复认领重页面而非快照类型。下一步应先查 `browser.tabs.list()`，若页面已进入浏览器管理标签，直接 `tabs.get(id)` 复用，禁止第三次重复 claim。
