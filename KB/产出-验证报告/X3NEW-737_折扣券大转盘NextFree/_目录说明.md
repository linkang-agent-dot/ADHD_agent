---
aliases: [X3NEW-737验证, 折扣券大转盘NextFree验证]
tags: [kind/产出, proj/X3, type/实机验证, module/活动转盘]
created: 2026-06-24
---

# X3NEW-737 · 折扣券大转盘「Next free」误显示修复 — 实机验证

- **类型**：客户端 BUG 修复实机验证（Unity Editor + 本地服）
- **MR**：!545 → dev（发起人 Zoe）
- **分支**：`fix/x3new-737-luckywheel-nextfree`
- **改动文件**：`client/Assets/Scripts/UI/Actv/UIActvLuckyWheel.cs`（仅 1 文件，+9 −1）
- **结论**：✅ 三项全部通过，可合 MR

## 一句话
折扣券大转盘（LuckyWheel 1024，`CloseDailyFree=true`）配置无每日免费，但 UI 一直误显示 "Next free" 倒计时。修复按 `CloseDailyFree` 隐藏倒计时控件 + `ShowNextRefreshTime` 开头加守卫。验证：1024 倒计时已消失、付费抽正常；正常转盘 1023（`CloseDailyFree=false`）免费抽/用完免费后倒计时两态均正常，未被误伤。

## 证据（运行时实读，非静态推断）
| 项 | 结论 | 关键实证 |
|---|---|---|
| ① 编译/启动 | ✅ | 分支代码 recompile 成功 1.61s 无报错，玩家 27877 登录正常 |
| ② 1024 折扣券 | ✅ | `mTFWTextRefreshTime.activeInHierarchy=false`、`text=""`；`mGoUIBtnGem=true` |
| ③ 1023 回归 | ✅ | 未用免费 `mGoUIBtnFree=true`；真实免费抽后倒计时 `activeInHierarchy=true`、`text="下次免費：23:00:53"→22:50:40` 实时递减 |

## 文件
- `X3NEW-737_luckywheel_verify_report.html` — 自包含报告（4 张截图已内嵌，双击即看，可直接转发）
- `wheel_1024.png` / `wheel_1023_state1_free.png` / `wheel_1023_state2_countdown.png` / `wheel_1023_state2_retry.png`

## 关联
- 验证方法论与坑点 → [[X3客户端功能实机验证_DebugUtils桥]]
- 验证用配方（live skill）→ `x3-feature-test/references/recipes.md` 配方 12（折扣券/装扮大转盘 UI 验证）
