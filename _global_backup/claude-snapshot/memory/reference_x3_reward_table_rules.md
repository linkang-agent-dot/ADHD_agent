---
name: x3-reward
description: X3 gdconfig/data/Reward.xlsx 新增行的字段必填约束与 reward_def.py 校验规则，避免导表报错
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9fa379f1-8095-4bed-9a37-401c299ba495
---

## Reward.xlsx 关键列

| Col | 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|------|
| 1 | seq (行编号) | int | ✅ | 表内唯一编号；同一 RewardID 内必须连续 |
| 2 | RewardID | int | ✅ | 关联键；Pack/活动等外部表引用此值 |

> ⚠️**查某 RewardID 是否存在，要 grep RewardID 列（tsv 0-indexed col1）不是行首 col0**（col0=seq 唯一行号，RewardID 几乎不在行首）。2026-06-23 排查拜访礼包用 `grep "^211020\t"`（查 col0）→ 0 行 → 虚报"Reward 211020 没了/拜访礼包搞挂"，实际 RewardID=211020 完整在（seq 40000-40004，门头三件套 152017/18/19+钻+VIP）。正确：`grep "\t211020\t"` 或 csv 读 col1==211020。
| 3 | ItemType | int | ✅ | 1=道具，其他类型见 def |
| 4 | ItemID | int | ✅ | 道具 ID |
| 5 | Note | string | — | 备注（道具中文名） |
| 6 | Num | int | ✅ | 数量 |
| 8 | DropType | int | ✅ | 1=单独概率（必掉）等 |
| 9 | DropPara | int | ✅ | 概率参数，必掉时填 `10000` |

| 15 | DisplayOrder | int | ✅ | **组内展示顺序,必填且组内唯一**——惯例=直接填 Col1 行编号(尼罗210612等模板都这么填)。**留空按0解析→组内多行全是0→reward_def 拦截 `DisplayOrder 重复: 0`导表FAILURE**(2026-07-02 深海锚点包13021-024踩坑,jolt #1495)。tsv_edit 0-indexed=col14 |

## 硬约束规则

### 规则-1：★新增 Reward 行落笔后必须逐列 diff 克隆源模板（2026-07-02 连踩两坑的总教训）
- 深海锚点包13021-024共12行，一次克隆连出两错、烧了两次导表构建：①DisplayOrder(col15)漏填→组内重复0 ②ItemType(col3)误当组内序号填2/3→钻石被当蓝图 depend 报错。
- **收尾动作**：加完行，用 awk 把新行和克隆源模板行**同列并排打出来逐列比**（`awk -F'\t' '$2==<新组>||$2==<模板组>{...}'`），除 ItemID/Num/备注/DisplayOrder 这些"应当不同"的列外，**其余列必须一字不差**；有差就是错。别凭记忆填列。

### 规则0：★别把 ItemType(Col3/idx2) 当序号填递增！（2026-06-16 世界杯签到day7踩坑）
- 「同 RewardID 内必须连续」的递增编号是 **Col1=行编号(idx0,全表唯一RowID)**，**不是 ItemType**。
- 多道具同组时 **ItemType(Col3/idx2) 全填 1**(都是道具)，靠 Col1 RowID 区分各行；**误把 idx2 填成 1/2/3** → 导表把 ItemType=3 当**嵌套奖励包**去找 ItemID 对应的 Reward 组(找不到就 `depend not existed` 报错)，ItemType=2 当蓝图。
- tsv_edit 是 **0-indexed**：idx0=行编号 / idx1=RewardID / idx2=ItemType / idx3=ItemID / idx5=Num / idx7=DropPara。（上表是 1-indexed Col，对应 -1）
- 实例：签到 day7 Reward 59812 三行(券1146/加速11003/资源袋3101)误填 idx2=1/2/3 → 导表报 `key:... not existed`/把3101当奖励包；修=全改 1(commit 7ea0a10)。

### 规则1：DropPara 必填（导表 `int('')` 报错根因）

- 即使 DropType=1（单独概率/必掉），DropPara 也**不能为空**
- 通用值：`10000`（同 RewardID 内其他行的取值，表示必掉）
- 报错信号：`reward_def.py line 31, in user_convert_func: item.DropParaVal = int(item.DropPara) ValueError: invalid literal for int() with base 10: ''`

### 规则2：同 RewardID 内 col1 seq 必须连续

- `reward_def.py` 强校验，断号即报错
- 不要求全表 seq 无空洞，只要求**单个 RewardID 内**连续
- 不要求物理 Excel 行连续，但物理连续是惯例做法

## 新增行的正确流程

1. **找空闲 seq 段**：扫描 Reward.xlsx col1，找一段长度 ≥ 待插行数的连续空号（一般在表尾 max(seq) 之后）
2. **物理行写入**：在该 RewardID 的现有行紧邻处插入（用 openpyxl 改字面值即可；Reward.xlsx 没有 ListObject 结构）
3. **每行必填**：seq（取自空闲段，连续递增）+ RewardID + ItemType + ItemID + Num + DropType + DropPara=10000
4. **校验**：保存后用脚本反查 → (a) 同 RewardID 的所有 seq 升序排列后是连续整数 (b) 每行 DropPara 非空

## 实战案例：夏日恋语 210921 拜访礼包

- **背景**：在 RewardID=210921（4 行）中补钻石 + VIP 点数 2 行
- **第一次错误**（commit 92e85ff）：写了 RewardID/ItemType/ItemID/Num，但 col1 自动分配到 24157/24158（跳号 24115→24157），col9 DropPara 留空
- **修复1**（commit 6806603）：补 DropPara=10000
- **修复2**（commit 497da29）：4 行 seq 整段改为 24159-24162（空闲段），同 RewardID 内连续

## 删行操作

### 规则3：删行后剩余 seq 不需要前移
- 删除某 RewardID 内的一行 seq 后，剩余行天然相邻（如 [a,b,c] 删 a 剩 [b,c] 连续不断号），**不需要重排**
- "seq 必须连续" 只指**同 RewardID 内不断号**，不要求从特定值（如 1）起步
- 验证依据：扫描现有 RewardID 发现 2544 个仅 2 行的 RewardID 中**没有一个**从 seq=1 起步，跨 RewardID 跳号普遍存在
- 删行时务必倒序删（先删大行号），避免行号位移错位

## 模板换皮的占位行陷阱

### 现象：客户端面板显示数量 ×0 的空 ICON
节日换皮活动（如 26情人节→夏日恋语、26情人节→尼罗）的累充奖励/任务奖励面板里第一个 ICON 显示 `×0`。

### 根因
- 模板奖励里有一行 `ItemID=52003 (通用传奇英雄信物) MinNum=0` 的**占位行**
- 换皮时这行占位没有清掉
- 客户端按 "有 seq 就渲染一个 ICON 位" 处理，MinNum=0 → 显示 ×0

### 实战修复（2026-05-25/26 尼罗+夏日累充 ICON ×0 两轮）

**第一轮**（commit 3de76da）：删 20 行 ItemID=**52003**（通用传奇英雄信物）MinNum=0
**第二轮**（commit 32195be）：又发现每个 RewardID 还藏一行 ItemID=**11002**（5 分钟通用加速）MinNum=0，再删 20 行

涉及 RewardID：59401-59410（尼罗 10 档）+ 59501-59510（夏日 10 档）。两轮删完每档只剩 1 个 ICON（女武神勋章 1128 / 抽奖券 1134 等主题道具）。

**教训**：模板换皮的占位**不止一种 ItemID**，至少有两种「装饰性占位」（52003 + 11002）。每次只扫一种很容易漏掉另一种。

### 换皮 checklist 必检项（更新版）

新增/复用 RewardID 后，**扫所有 MinNum=0 的行**（不要按特定 ItemID 扫），如：

```python
for row in ws.iter_rows(min_row=7, values_only=True):
    if row[5] == 0 or row[5] is None:  # col6 = MinNum
        print(f'占位嫌疑 RewardID={row[1]} ItemID={row[3]} Note={row[4]}')
```

观察到的占位 ItemID 段（持续扩充）：
- `52003` — 通用传奇英雄信物
- `11002` — 5分钟通用加速

**架构层修复建议**：在客户端 ICON 渲染逻辑加 `MinNum>0 才渲染 ICON`，可一劳永逸避免每期换皮踩坑。属于后端/客户端代码改动，需立项。

## 直接改 tsv 的两个易错坑（2026-06-04 夏日装饰礼包补钻石/VIP 踩坑）

### 坑A：tsv_edit.py 是 0-based，列含义别记错（把 ItemType 当 seq 改了，酿成大错）
`tsv_edit.py show` 输出 `[0]..[13]` 是 **0-based**，但本文上方字段表是 **1-based xlsx 列**，错位 1。0-based 对照：
- `[0]` = ID（行编号/本文"seq"）　`[1]` = RewardID　**`[2]` = ItemType（道具=1）** ← 不是 seq！
- `[3]` = ItemID　`[4]` = Note　`[5]` = Num/MinNum　`[7]` = DropType　`[8]` = DropPara
- 教训：曾把 `[2]`(ItemType) 当 seq 从 1 改成 2/3/4 → 道具类型坏了游戏不发奖；且 ItemType=3/4 的异常行被旁人当垃圾误删。**改前先 `show` 看清，钻石/VIP/券都是普通道具 ItemType 必须=1。**

### 坑B：导表硬校验"同 RewardID 内 ID(col[0]) 连续"，报错信号明确
- 报错：`rewardID:210917 ID不连续, minID:24114 maxID:24297`（reward_def 强校验，build FAILURE 但 gate_rc=0）
- 根因：给 RewardID 补行时用了表尾空闲号(24296)，与原行(24114/24115)断号。
- 修法：**把该 RewardID 的所有行 col[0] 整组重排到一段连续空闲号**（如三礼包各4行 → 24302-24305/24306-24309/24310-24313），物理也挪到表尾连续。col[0] 只是 Reward 内部行号，外部按 col[1] RewardID 引用，改 col[0] 不影响引用。
- ⚠️ 之前误以为跳号没事（被旧导表 SUCCESS 误导）——实际现在强校验，必须连续。
- 改完别忘 [[reference_x3_tsv_export_migration]] 顶部的 xlsx-tsv gate：只改 tsv 会触发 gate 两步同步。

## 坑C：假道具不能投放进 Reward（2026-06-15 世界杯商会赠礼踩坑）
- 报错：`Exception: ID: <rowID> 不能投放预览道具 <itemID>`，build FAILURE。
- 根因：该 item 的 **Item 表 col2(0-based)= "假道具"** —— 是某系统的**展示/预览用占位道具**，不可作奖励发放。典型：**商会赠礼I~V (12101-12105)**(col2=假道具,图标DK_Icon_guild_gift_purchase1)=公会赠礼**购买界面展示图标**，不是真道具。
- 商会赠礼的真相：是「买礼包→给公会送礼」的**系统特权**(UnionGift)，按 IAP 价格档自动挂(UnionGiftCfg 编号201-205,类型2=商会礼物)；公会成员实收=Reward 404001-404005=钻×1+5分钟加速×N。**整套不在礼包 Reward 里配**，礼包侧无需配它。
- **配 Reward 前先验**：`awk -F'\t' '$1==<item>{print $2}' Item__Item.tsv`，col2 是"假道具"的一律不能进 Reward。

## ⚠️改 Reward 表的正确姿势(2026-06-15 血泪：别裸 python 整组重写)
- **单格改(换item/改数量)→ 用 `tsv_edit.py set`**(保LF、单格、不动行结构)，`git add tsv` 后 **pre-commit gate 自动同步 xlsx**(显示"auto action staged"+mismatch=0)，一次过。
- **裸 python 整组重写行(加/删行+重排ID)→ 翻车**：split('\n')/join 易破坏行尾→引入 CRLF(gate crlf≠0 拒)+round-trip 不稳(mismatch),手动 `--from-tsv`/`--from-xlsx` 反复同步只会越弄越糟(mismatch 0→3)。
- 真要加/删行：能用单格替换达成目的就别加减行(如把第5物换成另一道具,而非删行重排)；非加行不可时，**改完用全仓 `python scripts/sync_xlsx_tsv.py` 验 mismatch=0 且 crlf=0 再提交**，崩了立刻 `git reset --hard origin/<branch>` 回纯净态别硬怼。

## ⚠️备注列(Note·idx4/col5)是 stale 垃圾，判道具真身必须查 ItemID(2026-06-29 深海BP差点误改一片好奖励)
- **Note 列(0-based idx4)= 纯人类备注·克隆行时不更新·与真实 ItemID 大面积对不上**。换皮/克隆来的 Reward 组，Note 留着源节日的旧名（如深海BP组142里 item154001 Note 写「争霸奖券」实际=自选家具木匣·item11004 Note「10 Vip点数」实际=1小时通用加速·一片 item 都挂着「一封情书」其实是钻石/加速/技能书）。
- **铁律：判断某奖励格"是不是串味/外来道具"，一律 `awk -F'\t' '$1==<ItemID>{print $2}' Item__Item.tsv` 查真名，绝不信 Reward 的 Note 列**。我曾按 Note 列向用户 flag「BP里有GvG争霸奖券/情人节遗留」→用户授权全改→查真身才发现奖励其实全是正常通用资源(加速/技能书/钻石/信物)+深海藏宝图，**唯一真外来物是表情item15418**(客户端只读 ItemID 渲染·玩家游戏里看到的是真道具图标·Note 不进客户端)。险些把一套合理BP砸成清一色藏宝图。
- **可选清理**：Note 全刷成真名脚本=遍历目标组行·`Note=Item[ItemID].name`·只改 idx4·字节安全(io utf-8 newline=''·split/join '\n')。纯可读性、不影响导表/发奖。深海BP组142(4034101-120/201-220/301-320共80行)已刷43处真名(commit abf25bb·jolt#1370 SUCCESS)。

## 🔁「整组复制翻倍」bug 识别 + 去重修法(2026-06-26 节日礼包翻倍事故·MR!43)
master 上一批奖励组被同一 bug **整组复制**(组内所有行整块复制一份→玩家实得2倍),团队分轮修。识别+修法可复用：
- **识别 signature(比"组内同道具≥2次"更稳)**：`组内每个道具都出现偶数次` → awk 按 RewardID 聚合,某组所有 ItemID 计数全偶=整组复制嫌疑。`{grp[$2]=grp[$2]" "$4;it[$2"|"$4]++} END{逐组判所有item计数%2==0}`。再按 id 段(节日=210xxx/211xxx)过滤。⚠️ "完全相同行(组+item+num+DropPara)重复"扫法**偏保守会漏**(非字节级复制的漏掉),实测 23 vs 团队基线法 106。
- **🔴正确目标来源=该表自己的 git 历史(铁律,2026-06-26 翻车纠正)**：去重要还原到「翻倍前的单份态」，**必须查该表本身的提交历史**找翻倍 commit 前一版(`for c in $(git log origin/master -15 -- Reward.tsv); do git show $c:..|awk '组行数'; done` 看行数 5↔10 震荡,取 5 的那版逐行内容)。**绝不能拿落后主干一大截的旁支当"正确态"**——`master_fix_fes_pack` 落后 1366 提交,它的 210919=4行 是「×10 券还没合进来的远古态」,我误信它把**合法的 ×10 券当脏数据删了**(10→4)，AI 审 MR 抓出，纯去重应是 10→**5**(保留 ×10)。
- **★纯去重原则=只撤销复制,不做"这行像脏数据"的额外判断**：整组复制=`[N行单份]×2`,正确修=**只删后半 N 行**(前半已是连续 seq 块→**不用重排**,更简单)。210632/210919 单份就是 5 行(含 1134/1128 的 ×10 **和** ×80 两条券,合法),别因为"和 tier1/2 单条券不同构"就删 ×10——tier3 本就允许多档券。**少动=安全**。
- **共享组坑**：210521/210632/210919 等组 id 与 `Route__RouteLevels`(海域航线掉落)/UnitConfigMonster 撞车共享(同 RewardID 被礼包+航线掉落都引用)→ 去重是干净2×时,删复制块对两个消费方都对;但务必先确认非"两消费方各自的真实行被合到一组"。
- **WC 不在 master**：世界杯 894/211 全套只在 dev_festival,master=0,故 master 的翻倍 bug 不碰 WC(查 `git show origin/master:tsv/Pack__Pack.tsv|awk '$1+0>=894010'`=0)。

## 🔢 Reward seq(col0) 连续性铁律(2026-06-26 复核确认,改/删行前必读)
- **表头注释自带规则**：Reward__Reward.tsv **第4行 col0 注释=「该列仅保证不重复即可」**,col1=「相同ID为同一个掉落包」;第5-7行是 seq 段位分配注释(8000付费/9000每日特惠/10000治疗)。即 **col0 硬规则=全局唯一(允许空洞)**。
- **叠加 reward_def 强校验**：**同 RewardID 内 seq 必须连续**(max-min+1==count,断号报 `rewardID:X ID不连续`)。
- **删行修法(不全局重排,省巨大diff)**：删组内部分行后若断号,**只把该组保留行 col0 重排回本组自己的连续低位**(如210632删后保留4行→25192-25195),其余全局留空洞=合规(表规则允许)。**别全局renumber**(会动几千行+可能破坏段位语义)。
- **字节安全删行**：读 bytes→`split(b"\n")`→处理→`join(b"\n")`→写 bytes,**绝不 decode/re-encode 行尾**(防 CRLF)。删行+改col0 后必验:①各组组内连续 ②全局无重复 seq ③`grep -c $'\r'`=0。
- **终极校验=本地 `cd Tools/table_exporter && python ExportTable.py`**(纯Python,跑真 reward_def),尾部 `protoc编译成功+bytes生成+MD5`=过。**当前仓 xlsx 已基本退役(git tracked xlsx仅2个,Reward.xlsx不在内)→ Reward 改动纯 tsv commit,无需同步 xlsx**。

### ★最常见触发源=给「已有组」追加道具行时把新 id 追到文件末尾(2026-06-30 深海累充骰子事故)
- **场景**：要给已存在的 reward 组补一种道具(如给累充档加骰子),图省事把新行**追到文件末尾取 全表max+1**→新行 id 落在远离原组其它行的号段→**组内 id 一下从 25488 跳到 15904123 = 断号** → `rewardID:X ID不连续`。
- **正确姿势**：给已有组加行,新行 id **必须紧贴该组现有行(连续)**;原组号段没相邻空位就**整组重排到一段干净连续空号**(每组成连续块),别只图新行取 max+1。
- **实例(深海累充 59850-59858)**：某 agent 给 9 个累充档(原各发 1200券·id 25488-496)追加 9 行骰子 1057(追到末尾 id 15904123-131·复用组号)→ 每组 2 行 id 断号 → 9 组全违规。修=18 行重排进 15904163-180·每组配连续对(commit X3NEW-·feature/reward-seq→dev_festival)。
- **★jolt 绿 ≠ 安全(关键·别被骗)**：此校验在 origin 的 `reward_def.py` 里(commit 70e5013),但**Jenkins jolt 构建机的 exporter 快照可能旧、漏跑这条**——实测坏行在 dev_festival 上 jolt #1400 仍 SUCCESS,而本地 ExportTable(当前代码)必挂。**结论：配完 reward(尤其多道具组/追加行)别只看 jolt 绿,本地按"组内 max==min+count-1"自查或跑本地 ExportTable**。

### 🔀 奖励展示顺序 = 组内行(seq col0)升序(2026-06-30 用户截图"顺序反了")
- 客户端面板里多道具的**显示左右顺序 = 该 RewardID 组内行按 seq(col0) 升序**。要调展示顺序=**调组内两行的 seq 相对大小**(谁想排前给谁小 seq),**不改 item/数量**,seq 仍保持组内连续。
- **多档活动新加档位必须对齐既有档位的 item 排列**:实例深海累充 59859(20000档)罗盘1057/券1200 顺序与其它9档(59850-858=券前罗盘后)相反→把券800排小seq(25496)、罗盘45排大seq(25497)对齐(commit a1cebce)。根因=累充agent加第10档时两行顺序填反。**接管累充/多档奖励改顺序先比对兄弟档,别孤立判断。**

## 🚪 master 受保护→走 MR(2026-06-26 实操路径)
- worktree 隔离: `git worktree add ../gdconfig-<名> -b fix/<名> origin/master`(基于 master 不是 dev_festival);改完 commit(`X3NEW` 前缀)+`git push -u origin <分支>`;完事 `git worktree remove ../gdconfig-<名> --force`(改动已推送则安全),主仓 dev_festival 不受扰。
- **建 MR = GitLab API**(项目 `x3/gdconfig` id=**4454**)：`POST /projects/4454/merge_requests` source/target=master/title。🔴**坑：title/description 含中文走 `--data-urlencode`(form)会 500 Internal Server Error**;先用**纯英文 title** POST 建出 MR,再 **PUT 用 JSON body(`Content-Type: application/json`, utf-8)** 补中文 title+description=成功。Token=`$GITLAB_TAP4FUN_TOKEN`(len20)+`PRIVATE-TOKEN` header。

## 相关

- 改 tsv 不碰 xlsx（导入只认 tsv）见 [[reference_x3_tsv_export_migration]]
- Pack ID 段分配见 [[reference_x3_config]]
- 配置写完必须反查见 [[feedback_plan_index_must_be_fixed]]
- 节日换皮完整工作流 [[reference_reskin_workflow]]
