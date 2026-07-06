---
name: reference_x3_puzzle_activity
description: X3 拼图活动(ActvType=18)完整配置链路 + 换皮法；含小格子任务vs连线奖励、挂大富翁子活动机制、i18n复合key
metadata: 
  node_type: memory
  type: reference
  originSessionId: 2e8608d3-3d75-4a41-8759-820e1e5f0fb4
---

# X3 拼图活动（ActvType=18 / ActvPuzzle）配置链路 + 换皮法

节日拼图（航海之路-拼图/各节日拼图）= **5 张表 + 挂载**。冷启动接手/换皮先读本条。

## 表结构（5 张 + ActvGroupSchedule）
- **`ActvPuzzle__ActvPuzzle.tsv`（主表）**：`col0`=ContentID（=拼图CID，如1809）｜`col1`=**阶段奖励组**(→ActvPuzzleReward.BD_组)｜`col2`=**任务组**(→ActvPuzzleTask.BD_组)｜`col3`=DK_拼图底图｜`col4`=TXT_拼图名字｜`col5/col6`=网格**行数×列数**(如5×5=25格)｜`col7`=DK_格子图标｜`col8`=DK_背景框｜`col9`=DK_拼图名底图｜`col10`=DK_奖励底图。**美术全是 DK 列，换皮复用即美术不变**。
- **`ActvPuzzle__ActvPuzzleTask.tsv`（小格子任务）**：每个网格格子=一行。`col0`=任务id｜`col2`=**BD_组**(主表col2指它)｜`col3`=任务事件类型ID(如321建造/441-443行军类/271/451/466/800/901)｜`col4`=任务计数(目标值)｜`col8`=**奖励**(→Reward包ID)｜`col10`=行｜`col11`=列(网格坐标)｜`col12`=跳过消耗(钻石,首/末格常空)。**「里面的任务奖励」=这张表 col8**。
- **`ActvPuzzle__ActvPuzzleReward.tsv`（连线/阶段/集齐奖励）**：`col0`=行id｜`col1`=**排布**(1=行连线/2=列连线/3=集齐全图)｜`col2`=序号｜`col3`=**BD_组**(主表col1指它)｜`col4`=奖励(→Reward包ID)。5×5典型=5行连线+5列连线+1集齐=11行。**这≠小格子任务奖励，别混**。
- **`Reward__Reward.tsv`**：奖励包。`col0`=行唯一id｜`col1`=**包ID(组)**｜`col2`=奖励类型(1=道具)｜`col3`=道具id｜`col4`=备注｜`col5/col6`=最小/最大数量｜`col7`=掉落类型(1)｜`col8`=条件参数(10000=100%)｜`col11`=备注。一个包ID可多行(集齐奖励=罗盘+信物+钻石三行同组)。
- **`ActvOnline__ActvOnline.tsv`**：活动壳。`col4`=ContentID(指拼图CID)｜`col5`=18(ActvType拼图)｜`col38`=ActvGroup(HUD分组)｜`col7`=TimeController(**拼图可空**,靠ActvGroupSchedule排期不靠TC,导表不报错)。

## ★挂载机制：拼图=主活动的「子活动」靠 ActvGroupSchedule，不是靠 col38
- **`ActvOnline__ActvGroupSchedule.tsv`**：`col0`=ID｜`col1`=IsOn｜`col2`=**MainActvID(主活动)**｜`col4`=**ActvID(子活动)**｜`col6`=StartTime(0)｜`col7`=DurationType(2)｜`col8`=DurationTime。一行=「把子活动X挂进主活动Y的内部页」。
- **「拼图挂在大富翁里面」= 加一条 schedule：MainActvID=大富翁AO → ActvID=拼图AO**。老航海之路102801 的子活动有：拼图1018091/记录册1022091/兑换101332。**深海大富翁=102802**（深海版航海之路/成就礼包版）。
- `col38`(ActvGroup) 是 **HUD 入口分组**(独立于schedule)：**110=航海之路（老）/141=深海航行（深海大富翁HUD）/140=深海节**。换皮挂深海大富翁=col38 改 141 + schedule 挂 102802，两者都做。
- AO=100000+CID 是深海惯例；但**老 AO 1018091 是历史例外 id**（不等于101809），别套公式去推老活动。

## i18n=复合 key（多 key 共享一行文本）
- Text 表 `col0` 用 `|` 拼多个 key 共享同一行翻译（CompositeI18n）。拼图名 key=`TXT_ActvPuzzle_PuzzleName_{CID}`；AO 名/描述=`TXT_ActvOnline_ActvName_{AO}`/`ActvDesc_{AO}`。
- 换皮新 CID/AO → 新 key 空白。faithful 克隆=新建独立 Text 行，把原复合行的全语种值照抄过来（按 substr 找原行→换单 key→append）。

## 道具锚点
- **罗盘=Item 1057 航海罗盘**（大富翁骰子/拼图连线奖励都用它）｜1058海神罗盘｜1060远洋金币｜1200深海藏宝图(转盘券)｜1204珍珠贝。详见 [[x3]]（深海项目）大富翁段。

## ★换皮实操（2026-06-30 深海大富翁拼图实战，已push dev_festival·本地ExportTable过）
克隆 1809→深海大富翁子活动 AO101828/CID1828，25格任务奖励改罗盘1057×1：
1. **追完整链**：主表1809→任务组108(25行)+阶段奖励组1008(11行)→各自Reward包(任务603701材料票/连线603702罗盘×3/集齐603703罗盘×10+信物+钻石)。RuleTips/ItemObtain 的同号是**无关命中**(公会建筑),拼图不用碰。
2. **新id**：CID1828(1801-1827全占,下一个空)/AO101828/任务组110/阶段奖励组1100/任务行11000-11024/阶段奖励行110000-110010/新Reward包603704(罗盘1057×1,行用高位15904122避占用)。先全表扫空闲再写。
3. **克隆策略**：任务组**必须克隆**(要改奖励)；阶段奖励组克隆但 col4 **仍指原603702/603703(共享不改)**；只新增1个Reward包(603704罗盘×1)给25格任务指。连线/集齐原样。
4. **落地**：worktree(dev_festival多agent在途) + **纯追加行脚本**(读原行全字段list→改id/组/奖励→`'\t'.join`断言无tab/换行→append,不重写已有行=最小diff)。pad到表头宽度,LF写盘。
5. **挂载**：AO col38=141 + ActvGroupSchedule新行(102802→101828)。
6. **验证**：worktree里 `cd Tools/table_exporter && python ExportTable.py`（xlsx缺失不再abort,verify闸门已删）=protoc成功+localization bytes+MD5无Exception即配置干净。push HEAD:dev_festival + `jolt_verify.py dev_festival`。
- 实操脚本范式：纯追加、读原行克隆、断言id不存在。比 tsv_edit(无append) 适合多表批量克隆。
