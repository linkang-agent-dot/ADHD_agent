---
tags: [kind/产出, domain/配置换皮, proj/X3, year/2026-06]
---

# 异国美酒储蓄罐 · 每日双档改造 —— 改动包应用指南（FINAL）

> 备份于 2026-06-18，**等切 dev feature 分支时应用**。本目录是即用改动包，不要在当前分支跑。
> 设计依据：上级 `..\异国美酒储蓄罐_可重复购买改造_策划案.md`（v2 每日双档）。

## 〇、最终规格
- 现状：异国美酒储蓄罐每天 1 次、$9.99 得 10 异国美酒(Item 7002)、24h CD。
- 改造：**每天 2 档** —— 档1 $9.99(10) + 档2 $19.99(20)，各自 24h CD（独立），次日重置。买完档1 界面自动切档2。
- 单日付费上限：$9.99 → **$9.99+$19.99=$29.98**。
- **服务端零改动**；改动 = 配置(3 表纯追加) + 客户端 1 处选档。

## 一、改动清单（用到的 ID 都已扫 tsv 防撞号）
| 项 | 文件 | 改动 | 关键值 |
|---|---|---|---|
| 档2 礼包 | `Pack__Pack.tsv` | 新增 1 行(克隆 500031) | ID **500032** / Price 111($19.99) / PackType 21 / ColdTime 24h / **Group 11** / PlayerLv 3 |
| 档2 储蓄罐 | `PiggyBank__PiggyBank.tsv` | 新增 1 行(克隆行46) | ID **51** / ResourceID 7002 / PackID 500032 / **GroupId 261** / MainBg _2 |
| 档2 产出 | `PiggyBank__Grade.tsv` | 新增组 261 | Grade 3-35 / Num **20** / 行ID 736-768 |
| 选档逻辑 | `UIPiggyBankContent.cs`(客户端) | 改 2 处 | 见 `客户端补丁_UIPiggyBankContent.md` |

> 档1(Pack 500031 / PiggyBank 行46 / Grade 组260) **完全不动**。

## 二、应用步骤（在 feature 分支上）
1. **确认分支**：`git -C C:\x3\gdconfig branch --show-current`（必须是 feature 分支，不是 dev/main）。
2. **配置**：把 `apply_config_异国美酒双档.py` 拷到 `C:\x3\gdconfig\tsv\` 跑：
   ```
   cd C:\x3\gdconfig\tsv
   python apply_config_异国美酒双档.py
   ```
   脚本纯追加、幂等(已存在则跳过)。跑完 `git diff` 复核**三张表只新增、未改现有行**。
3. **客户端**：按 `客户端补丁_UIPiggyBankContent.md` 改 `C:\x3-project\client\...\UIPiggyBankContent.cs`（2 处）。
4. **导表**：`python C:\Users\linkang\.claude\skills\x3-config-export\scripts\jolt_verify.py <分支名>` 触发并验证构建。
5. **本地服验证**：开异国美酒(item 7002) 道具获取面板 → 储蓄罐卡，自测「砸档1→自动切档2→砸档2→进CD→次日回档1」(见客户端 patch 自测表)。

## 三、⚠️ xlsx-tsv 一致性闸门（2026-06-04 起，必看）
导表有 `jenkins-xlsx-tsv-gate`：tsv 单边改 → gate 自动同步 xlsx 但**本次 build rc=24 失败需重导**；两边不一致 → 拒绝。两种处理：
- **省事**：先只跑 tsv 脚本导一次(rc=24)，让 gate 回灌 xlsx，再导一次过；或
- **一次过**：在 `Pack.xlsx` / `PiggyBank.xlsx` 手动加同样的 3 处行，与 tsv 一致后再导。
（细节见 memory `reference_x3_tsv_export_migration`。需要我补一个同步 xlsx 的脚本再说。）

## 四、新增行预览（复核用）
- **Pack 500032**（克隆 500031，仅改 4 格）：ID=500032、备注价=19.99、Price=111、Group=11，其余同 500031（PackType21/ColdTime24h/PlayerLv3/IsOn1/Name 异国美酒储蓄罐…）。
- **PiggyBank 51**：`51 | 7002 | 1 | 500032 | 异国美酒储蓄罐 | 折扣 | DK_ui_Howtogetit_piggybank_2 | 200000 | 261`
- **Grade 组261**：33 行 `<id> |  | 261 | <3..35> | 20`。

## 五、验证清单
- [ ] git diff：Pack/PiggyBank/Grade **只新增行**，档1 相关行(500031/46/组260)零改动。
- [ ] 客户端 2 处改动到位（OnRefreshPackGiftUI 加 PrefixData()；PrefixData 选档改"第一个不在CD的档"）。
- [ ] 导表 jolt_verify = SUCCESS（或 rc=24 后重导成功）。
- [ ] 游戏内：砸档1($9.99,10)→自动切档2($19.99,20)→砸档2→24h CD→次日回档1。
- [ ] 单日只能各砸 1 次（服务端 ColdTime 拦，无穿透漏洞）。

## 六、提交规范
commit message 走 `X3NEW-异国美酒储蓄罐每日双档` 或关联单号 `X3-{n} ...`（X3 仓 pre-commit hook 强制，见 memory `reference_x3_project_repo`）。客户端仓走 feature branch + MR（dev 受保护）。
