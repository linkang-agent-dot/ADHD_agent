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
| 3 | ItemType | int | ✅ | 1=道具，其他类型见 def |
| 4 | ItemID | int | ✅ | 道具 ID |
| 5 | Note | string | — | 备注（道具中文名） |
| 6 | Num | int | ✅ | 数量 |
| 8 | DropType | int | ✅ | 1=单独概率（必掉）等 |
| 9 | DropPara | int | ✅ | 概率参数，必掉时填 `10000` |

## 硬约束规则

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

## 相关

- 改 tsv 不碰 xlsx（导入只认 tsv）见 [[reference_x3_tsv_export_migration]]
- Pack ID 段分配见 [[reference_x3_config]]
- 配置写完必须反查见 [[feedback_plan_index_must_be_fixed]]
- 节日换皮完整工作流 [[reference_reskin_workflow]]
