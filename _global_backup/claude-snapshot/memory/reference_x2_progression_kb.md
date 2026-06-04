---
name: X2 养成线付费价值手册
description: X2 全养成线付费价值手册的目录结构、数据源、当前完成状态，以及活动明细文件位置
type: reference
originSessionId: 72fa2f23-a99a-4c90-bc9a-f1289a5844dc
---
## 手册位置

`C:\ADHD_agent\.cursor\x2-numerical-design\养成线深度手册.md`

Demo 地址：`https://demo.tap4fun.com/x2-value-manual_5185/`（需登录）

## 目录结构

```
C:\ADHD_agent\.cursor\x2-numerical-design\
├── 养成线深度手册.md          ← 主手册（精简版，P2 风格）
├── 宝石_活动明细.md           ← 宝石详细礼包/周产出
├── 机甲_活动明细.md           ← 11 只机甲名单 + 12 类 397 条礼包 + 投放思路
├── 军备_活动明细.md           ← 3 品质×7 级逐级消耗 + 礼包清单 + T6 红
└── 英雄_活动明细.md           ← 25 英雄汇总 + 天赋 10 级 + 锚点/触发礼包
```

## 7 条养成线完成状态

| § | 章节 | 状态 | 单位坑深 |
|---|---|:---:|---|
| 一 | 宝石 | ✅ | $1,585/英雄（仅升级，洗练⛔不投放）|
| 二 | 武器（金羽打造）| ✅ | $875(Lv.5~8) / $2,000+(Lv.5~11), Lv.9 待定 |
| 三 | 机甲 | ✅ | 紫 $16,671 / 橙 $50,013；通用机甲芯片⛔不投放 |
| 四 | 英雄（含天赋）| ✅ | $3,395/英雄 / $84,875(25英雄) |
| 五 | 军备 | ✅ | $1,770/兵种 / $7,078(4兵种), T6 红 TODO |
| 六 | 收藏品 | ✅ | $3,362(红满/件) / $60,516(18件全红) |
| 七 | SLG | ⚠️ 缺坑深 | 资源+加速单价齐（$0.50/小时），T级/科研坑深 TODO |

## 关键数据源 SheetID

| 用途 | SheetID |
|---|---|
| 礼包道具付费价值表 | `1aV8VL-81C_VDQfzBhTvqiRbQUOGQuvV3WrcFrk2z3UU` (gid=1593930563) |
| 道具锚点价值表（1111 运营用）| `1pm0nztHsjpHmFBEmx-bLtP7Zjf4GFC67wo-sUmqY7Fs` (gid=862716542) |
| 养成线汇总表 | `1vsQ0GV-crQ1im7QNHrAGwnhMuyjDXlPJkuPpxi-kgFA` |
| 2013 iap_template | `1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E` |
| 活动投放主表 | `1aV8VL-81C_VDQfzBhTvqiRbQUOGQuvV3WrcFrk2z3UU`（31 页签）|
| 收藏品基础设定 | `13T-gJYCzaYD2XRc5c9EugCYwvFWUVcA_18OOe-uHtKs` |
| 机甲细化数值 | `127u1z5J27UkSFxN1Ig9gEnDZVKIoFvYKjW8KOJ5b5OQ` |
| X2 全数值文档库 (Drive) | `https://drive.google.com/drive/folders/1KhZJxj7sxBQhX3abyl0LCjgJfUW_mr8P` |

## 不投放道具（涉及时需提示使用者）

- 宝石洗练道具（未收录于付费价值表）
- 通用机甲芯片 (11118201)

## How to apply

- **查某养成线道具单价** → 主手册各章节「关键材料单价」表，统一格式：道具名 / 付费价值表 ID / 美金单价
- **查某养成线详细礼包/活动** → 对应的 `xxx_活动明细.md`
- **做活动/礼包定价** → 先查主手册确认道具单价，再参照活动明细里的 ROI 区间
- **P2 → X2 换皮** → 用主手册定价口径表做坑深对照，参考 `p2-numerical-design/养成线深度手册.md` §九 跨项目搬运参考
