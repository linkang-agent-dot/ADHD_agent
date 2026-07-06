---
tags: [kind/交接, domain/配置换皮, proj/X3, year/2026-06]
---

# 《护航令·至尊档（简易战令3档化）改造案》— 内容草稿

> 状态：草稿 v0.1（2026-06-18）。系统/配置/服务端/数值/命名已锁定；**「界面交互」节待用户截图后写实**。
> 落地目标：独立新 GSheet（待截图齐后按 X3 策划案模板誊入）。
> 案子类型：系统改造案（单模块·规则深化）。

---

## 决策锁定（用户已拍板）

| 项 | 决策 |
|---|---|
| 策划案落点 | 新建独立 GSheet |
| 至尊档价值模型 | **仅"更高价的第3条奖励轨"**（不送等级、不双倍免费奖励，最简价值模型） |
| 改造范围 | 简易战令 `ActvType=11` **改成数据驱动可配N档**（一劳永逸，老BP零影响） |
| ❌ 排除项 | **不要"钻石升级"**（积分BP `BattlePassScore.UpgradePrice` 那套花钻石跳级机制）。至尊档纯靠买礼包解锁，不引入花钻跳级 |
| 首期落地 | 用户已在 X3验收表加「多档通行证模板」（待读 sheet 对齐模板结构）→ 据此写实配置/界面 |

**默认值（如需改告诉我）**：命名"护航令"三档 / 至尊档≈2×现价 / 至尊=superset（至尊买家含付费轨）。

---

## 摸底结论（现状真相）

X3 有**两套** BattlePass：
- **简易战令 `ActvType=11`** ← 本案改造对象。配置 `ActvBattlePass`+`BattlePassReward`（**只有 `FreeReward`/`PackReward` 两列=2档**）；客户端 `UIActvBattlePass.BattlePassItem` **prefab 写死2轨**；服务端 `ActivityMeta.BattlePass.cs` **免费/付费两分支硬编码**。
- **积分战令 `ActvType=22/33`**（最佳酒馆/集结令/赛季BP）：配置 `ActvBattlePassScore`（**已有 `FreeReward`/`AdvanceReward`/`SuperReward` 三列**）；服务端数据驱动位标志 `Free=1/Advance=2/Super=4`。**已是3档，本案不动**。

**核心打法**：把简易战令改造成积分战令那套位标志引擎 → 简易BP也能配N档，第3档=至尊轨。

### 当前2档简易BP实例（改造对象）

| ActvOnline | 名称 | 主标题 | 付费包/价格 | 奖励组 | 任务类型 |
|---|---|---|---|---|---|
| 101102 | BP-新手主线 | 海盗猎人的赏金 | 130002 / $14.99 | 102(34级,带英雄spine) | 新手进度 412 |
| 101110 | BP-情报循环 | 猎杀时刻 | 130003 / $9.99 | 100 | 情报任务 410 |
| 101104 | BP-登录循环 | 登录好礼 | 130004 / $9.99 | 101 | 登录天数 321 |
| 101120 | BP-新手英雄-兔女郎 | 会员签到好礼 | 130015 / $3.99 | 107 | 登录 321 |

---

## 〇、包装层

通行证三档（沿用现有界面"档位列头"叫法，对齐积分BP模板）：
- **免费**（FreeReward，所有玩家）← 现有界面列头"免費"不变
- **进阶**（AdvanceReward，付费）← **现有界面列头"至尊"改名为"进阶"**（现 $9.99/$14.99 付费档落这里）
- **终极**（SuperReward，新增·更高价顶档）← 新增列

> 命名 = 免费/进阶/终极（用户拍板）。映射：现 `免費`→免费、现付费档`至尊`→**进阶**、新增顶档=**终极**。
> 每个BP实例的主题名/主标题仍按活动自身（猎杀时刻/海盗猎人的赏金/…），不强加统一品牌名。

## 一、设计目的

深度付费。现简易BP只有免费+付费2档，付费天花板低（$9.99–14.99）。至尊档=给愿意付更多的玩家加一条更高价值轨道，抬高 ARPPU 上限；**不动免费/付费现状，对大盘付费率/留存零冲击**。

- 付费点：至尊护航令礼包（更高价）
- 目标人群：已买高级档、愿意继续加价的中大R
- 因果假设：现付费档天花板 $14.99，加 $19.99–24.99 至尊档→已付费用户中 X% 升档→BP线 ARPPU +Y%
- 副作用控制：至尊=纯增量轨，免费/付费档奖励与解锁逻辑完全不变，老BP不配至尊包即维持2档

## 二、玩法说明

做任务攒积分→升级→每级可领 免费/付费/至尊 三档奖励。至尊档需购买至尊护航令礼包解锁，解锁后**同时享付费轨+至尊轨**（superset，至尊买家不丢付费轨）。

## 三、规则说明（核心=数据驱动N档改造）

**1）基础设定**
- 改造对象：简易战令 `ActvType=11`。
- 由"免费/付费两分支硬编码"→**数据驱动多档**，对齐积分战令 `BattlePassScore` 位标志引擎（`Free=1 / Advance=2 / Super=4 / …可扩展`）。

**2）档数由配置决定**
- `BattlePass.Pack` 由单包 → **管道列表** `[付费包 ｜ 至尊包]`。
- 服务端按 Pack 列表 index 映射档位：index0→Advance(付费)位、index1→Super(至尊)位、…。
- 配 1 包 = 2 档（**老BP行为不变**）；配 2 包 = 3 档；未来加列即 N 档。

**3）至尊解锁**
- 买至尊礼包 → `purchased |= (Advance | Super)` 双位（superset，至尊买家含付费轨）。
- 买高级礼包 → `purchased |= Advance` 单位。

**4）领奖校验**（沿用积分BP三层，数据驱动）
- ① 该档已购（`purchased & rewardType`；免费档恒可领）
- ② 任务/等级达成（`subItem.finished`）
- ③ 未领过（`receivedIds & rewardType`，位标志去重）

**5）兼容性铁律**
- 老BP（101102/101104/101110/101120）不配至尊包 + 不填 `SuperReward` 列 = 保持2档，零回归。

## 四、配置表（schema 改动）

| 表 | 改动 | 说明 |
|---|---|---|
| `ActvBattlePass__BattlePass.tsv` | `Pack` 列：int → 管道串 `付费包｜至尊包` | 第8列。空第2段=无至尊档=2档 |
| `ActvBattlePass__BattlePassReward.tsv` | **新增 `SuperReward` 列**（类型 cs/int，引用 Reward） | 现有 `ID/Group/Count/FreeReward/PackReward` 之后追加 |
| `Pack__Pack.tsv` | 新增至尊礼包行 | 礼包类型 13（BP专用UI）沿用；价格≈2× |
| `Reward__*.tsv` | 新增至尊轨 RewardID 系列 | 具体ID建配置时扫tsv分配防撞 |

> 4行schema（程序对接，建配置时补完整类型行/引用行/中文名/英文名）。

## 五、界面交互（据真实截图 `Pictures\X3验收\BP新增档位\` 写实）

### 现状界面（简易BP `UIActvBattlePass.prefab`，截图：猎杀时刻/海盗猎人的赏金/登入豪礼/会员签到豪礼）
- ① 顶部活动标题栏「酒館活動」+ 右侧英雄 spine 立绘（大图）。
- ② 副标题文案 + 价格按钮（$9.99/$14.99/$3.99）+ 右上折扣%徽章（3600%/3030%等）。
- ③ 奖励区 = **双列轨道**，列头 `免費` ｜ `至尊`（右列带锁图标=未购）。
- ④ 中间纵向等级条（1/2/3… 黄线连接当前进度），**横向滑动**翻等级。
- ⑤ 每格奖励槽（`BattlePassRwdItem`）三态：锁(`mGoLock`)/可领(`mGoEffect`)/已领(`mGoReceive`)。
- ⑥ 底部活动 tab 栏。

### 目标形态参考（积分BP `世界盃通行證`，截图：节日BP模板 = 现成3列）
- 三列轨道并排 + 列头 + 等級列在左 + 顶部「一鍵領取」+「X段 / 0/3000」进度条。
- **三档UI在积分BP里已实现**，作简易BP改造的视觉/交互参照。

### 改动逐项（简易BP 双列→三列：免费/进阶/终极）
| # | 文件 | 改动 |
|---|---|---|
| 1 | `UIActvBattlePass.prefab` | `BattlePassItem` 内 `Free`/`Pack` 两轨容器 → 加第3轨容器 `Super`（终极），**改为按配置档数动态生成轨道**；列头文案 `至尊`→`进阶`、新增 `终极` 列头+锁态 |
| 2 | `Auto_UIActvBattlePass.BattlePassItem.cs` | prefab 改后重新生成，新增 `mChildGroupSuper` 绑定 |
| 3 | `UIActvBattlePass.BattlePassItem.cs` | 加 `mChildGroupSuper`/`mSuperEndowItems` + `BindSuperItemData`；`RefreshView` 读 `SuperReward` 渲染第3轨 |
| 4 | `BattlePassRwdItem.cs` | 枚举 `BattlePassRwdItemType` 加 `Super`；`RefreshView`(锁/可领/已领) + `ClaimBattlePassReward` 加 Super 分支（未购→弹购买） |
| 5 | `UIActvBattlePassPop.cs`（购买弹窗） | `FromType` 加终极档；顶部购买区支持**进阶+终极两个购买入口**（价格/折扣分别读各自 Pack） |
| 6 | proto `ActivityBattlePassData` | `purchased` 位标志扩展支持第3档（Super 位） |

### 逐元素状态机（第3轨"终极"）
- **未购终极**：终极列整列显 `mGoLock`，点击任意终极奖励槽 → 弹购买弹窗（终极档）。
- **已购终极**（superset：购终极 = 解锁进阶+终极两轨）：进阶+终极列按"等级达成→`mGoEffect`可领 / 已领→`mGoReceive`"。
- **一键领取**（可选，模板有）：一次领完所有已解锁档已达成未领奖励。
- Text key：列头/按钮走自动key管线（见本地化节）。

## 六、服务端改造

| 文件 | 改动 |
|---|---|
| `server\GameServer.Hotfix\PlayerMeta\Activity\ActivityMeta.BattlePass.cs` | 2分支硬编码 → 位标志引擎（**抄 `ActivityMeta.BattlePassScore.cs` 现成范式**）。Pack列表 index→tier位；至尊包置 Advance\|Super 双位；领奖/解锁/校验数据驱动 |
| proto `activityBattlePass`（client `Assets\Scripts\Protos\activityBattlePass.cs`） | `ActivityBattlePassRewardType` 枚举加 `Super`/`Ultra` 位；`ActivityBattlePassData.purchased` 支持多位 |
| `GiftMeta.cs`（礼包购买回调） | 至尊礼包 → `ReceiveActivityBattlePassReward(..., Super)`；已支持任意档位，基本零改 |

> 改动量：中。`BattlePassScore.cs` 已有完整可抄范式（位标志 purchased / 三层领奖校验 / `ReceiveAll` foreach 遍历 realRewardTypes）。

## 七、本地化（Text keys）

| Key | 中文 | 说明 |
|---|---|---|
| `TXT_…_FreePass` | 免费 | 列头（现"免費"沿用） |
| `TXT_…_AdvancePass` | 进阶 | 列头（**现"至尊"改名"进阶"**） |
| `TXT_…_SuperPass` | 终极 | 列头（新增） |
| `TXT_Pack_Name_{终极包ID}` | 终极礼包名 | 新增终极礼包 |
| `TXT_Pack_Desc_{终极包ID}` | 终极礼包描述 | 新增终极礼包 |

> X3 配置文本走**自动key管线**（单元格字面值客户端不读，proto拼 `TXT_{表}_{字段}_{行ID}`）；新增文本必须同 commit 把自动key写进 Text 表，补全 16 语种，否则非中文客户端显空/中文母版。

## 八、美术需求

| 类型 | 内容 | 参考 |
|---|---|---|
| 至尊轨视觉 | 轨道底/锁态/已领态/特效 | 复用现有 Free/Pack 槽样式，配至尊金/紫色调 |
| 至尊购买按钮 | 主界面"至尊护航令"购买入口 | 复用现购买按钮 |
| 至尊礼包 banner | 购买弹窗至尊档展示 | 复用现弹窗布局 |

## 数值范式

| 档 | 价格 | 奖励轨 |
|---|---|---|
| 免费 | $0 | 现 FreeReward 不变 |
| 进阶 | 沿用现价 $9.99 / $14.99 | 现 PackReward 不变（现界面"至尊"列改名"进阶"） |
| **终极** | **≈2× → $19.99 / $24.99** | 终极买家=进阶轨+终极轨（superset）；终极轨与进阶轨同槽位结构，品质/数量上提（蓝→紫，量 ×1.5–2） |

> ❌ 不含「钻石升级」（积分BP `UpgradePrice` 花钻跳级），终极档纯靠买礼包解锁。

---

## 配套页签（落 GSheet 时产出）

变更记录 / 开发配置需求(模块·ActvType·复用源·新ID) / 配置表(schema 4行) / 数值设计 / 界面交互 / 本地化 / 美术需求 / 验收Checklist。

## 待办

- [ ] 用户开 2档BP实例(建议101110/101102)截图主界面+购买弹窗
- [ ] 据截图写实「界面交互」逐元素表
- [ ] 建独立 GSheet 誊入全文 + 格式
- [ ] task-checker(design-doc) 验收
