---
name: reference_x3_pack_open_mechanisms
description: "X3 礼包靠什么触发/显示——OpenActv 常为空时的 4 类开启机制速查；问\"礼包怎么开/为啥不显示\"先读"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 83315ed9-056a-42dd-a38f-ffd420801357
---

X3 一个 Pack 能不能在玩家端弹出来，**不只看 `Pack.IsOn` 和 `OpenActv`**——很多节日包 `OpenActv`/`ContentID` 都是空的，靠**外部表反向引用 + TimeCycle 窗口**才显示。问"这个礼包怎么开 / 为啥不显示"时，按 PackType 反查下面 4 张绑定表（用全仓 grep 礼包 ID，排除 `Route__RouteLevels`/`UnitConfigMonster` 的 ID 撞车命中）。

## 四类开启机制（按 PackType 判断）

| PackType | 类型 | 靠什么开 | 绑定表 |
|----------|------|---------|--------|
| **1**（UIType=3） | 英雄晋升礼包 | 玩家持有该英雄 + 进晋升界面触发；售卖窗口走 TimeCycle | `PackHeroPromotion__PackHeroPromotion`（行=某英雄某段晋升→PackID）+ 可能挂 `PackTypeInfo` 商城推荐位 |
| **15** | 道具获取弹窗礼包 | 玩家在"道具获取"入口点对应道具时弹出；常驻看 TimeCycleID | `ItemObtain__ItemObtain`（行=某道具获取入口→引用 PackID）+ `Pack.TimeCycleID` |
| **16** | 活动礼包（拜访礼包等） | 靠独立活动开启，**ActvType=56=拜访礼包** | `ActvVisitPack__ActvVisitPack`（行 `PackID` 列指向 Pack）→ 对应 `ActvOnline` type=56 活动需部署 |
| 11 / 15 | 链式/锚点 | 父链或活动面板引用 | `Pack__ChainPack.PackList` / `ActvOnline.ChainPackID` |

## 触发字段（Pack__Pack 自身）
- `TriggerType=1` → `TriggerParameter` 填 **TimeCycle ID**（不是单独的 TimeCycleID 列）；其余 TriggerType 见表内说明行（2=等级 5=买指定包 9=获得英雄 12=任务计数…）。

## ★TriggerType=1（timecycle推送）只看 TC 配置窗口，跟"活动在不在用这条TC"无关（2026-06-30 代码实证·深海头像框案）
**结论：把礼包挂在某活动用的 TC 上，部署/触发那个活动 ≠ 能把礼包带出来**。礼包 `TriggerType=1` 是否推送 = `IsTimeCycleOpen(TC, now)` 是否 true，而它**只读 TimeCycle 表配置的 StartTime/Duration**，不看有没有 ServerActivity 实例在用这条 TC：
- 链路：`GiftMeta.cs:2621`(取 TriggerParamVals[0]=TimeCycleID) → `TimePointCondition.cs:40/59`(`IsTimeCycleOpen`) → `TimeCycleMeta.cs:118-148` → `TimeCycleMgr.IsOpen`(`TimeCycleMgr.cs:92-110`：查 `mStartTimes/mEndTimes`，这俩**只由 TC 表配置算出**)。
- 活动创建 `ActivityMeta.cs:1642-1643` 只是**读** TC 窗口给活动实例当 start/end，**不反写** TC 开放状态。
- **深海头像框实证**：Pack 211019(TriggerType=1/TriggerParameter=1830·黑猫standalone·无ActvOnline) 挂 TC1830，而 TC1830 配置窗口=2020-01-01+14d(过期占位·备注"iGame部署带上")→ `IsTimeCycleOpen(1830)` 恒 false → **转盘101025(TimeController=1830)即便 iGame 部署上线，也带不出头像框**。"iGame部署带上"对 standalone 礼包是一厢情愿。
- **要让 standalone(TriggerType=1)礼包出现**：必须让它的 TC **配置窗口真覆盖目标时间**（生产=新建/改 TC 填节日正式档期；本地测试=指永久 TC 6001 或把该 TC 窗口改到当前服钟）。**这类包没法跟 iGame 动态档期联动**——节日靠 iGame 控时(TC=0)的活动，standalone 包蹭不到。
- **想"真跟活动一起上下线"只有一条路**：被活动引用（如 ChainPack 被 ActvType=63 活动挂，见本文 §四类机制 + 装饰106103/ChainPack700 案），代价=礼包变成那个活动 UI 里的一档，不再是独立弹窗。
- `TimeCycleID` 列（col19）= 礼包自身**售卖循环窗口**，与 TriggerType 的推送是两回事。
- ⚠️ **`Pack__Pack.tsv` 表头在 row5（英文字段名），数据 row6 起**——不是标准 7 行头！脚本定位列别套通用 row7。

## 实战陷阱（2026-06-08 情人节包 210716/210717/210718 查询）
- 三个同节日包开法各不同：210716=英雄晋升触发 / 210717=拜访礼包活动(ActvVisitPack 5603,type=56) / 210718=道具获取弹窗(ItemObtain 100329)+TimeCycle 6001(礼包-永久)常驻。
- **TimeCycle 名字是历史复用残留**：TC 1826 名"白色花嫁活动"(2026-02-06起10天,情人节)，却被"夏日柔情海湾"拜访礼包活动(ActvOnline 105603,type=56)复用绑定——看 StartTime 实际值判断窗口，别信名字（见 [[feedback_x3_timecycle_name_legacy]]）。
- 节日过期后这些包玩家端开不出来=TimeCycle 窗口已过；想重开要新建/改 TimeCycle 到目标日期，别直接改被其他活动复用的 TC。

## ★锚点礼包/PackType15「道具获取」靠 ItemObtain 表触发显示（2026-06-17 世界杯实证，查"锚点不显示"先看这）
PackType=15 的"抽奖券-道具获取"锚点礼包(纯券、4档$4.99-99.99)**自身 Pack 行的 TriggerType/Param 全空**，不靠 Pack 行触发——靠 **`ItemObtain__ItemObtain.tsv`(道具获取途径表)** 挂出来：
- 机制：`ItemObtain` 一行 = 某道具的一条"获取途径"。`ObtainType=7`(礼包快捷购买) + `Value=礼包id数组(竖线分隔,如 210612|210613|210614|210615)` + `ObtainName=道具名`。玩家在该道具的"获取途径/在哪买"面板看到这4档锚点礼包。
- **双向挂钩缺一不可**：① ItemObtain 表有这行(Value=锚点包ids) ② **道具(券) Item 行的 `ObtainID`(col10) 列出这个 ItemObtain 行 id**(尼罗券1128 ObtainID=`503|504|599|100313|100310|...`,100310 就是锚点包那行)。少②=道具不引用→锚点不显示。
- **换皮坑(世界杯实证)**：clone 锚点 Pack(PackType15)只复制 Pack 表，**漏了 ItemObtain 注册 + 券 ObtainID**→锚点永不显示。修=新建 ItemObtain 行(clone 尼罗100310,Value换WC锚点包ids,ObtainName换券名) + 把新行id写进券 Item.ObtainID。ObtainType 速查(ItemObtain row3注释):1宝箱/2快捷购买/3礼包/4商店/5界面/6兑换/7礼包快捷购买。

## 关联
- [[reference_x3_config_library]] §2.2 礼包族 · [[reference_x3_timecycle]] · [[reference_x3_pack_panel_rendering]] · [[reference_x3_pack_tab_icon]]
