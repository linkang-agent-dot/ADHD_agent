---
name: DK 资源层工作流规则
description: DisplayKey 资源写入 Unity client 仓库的流程规则：DK 区间规划、GUID 来源、脚本幂等性、提交顺序
type: feedback
originSessionId: 2f9bf6a0-00e5-49b7-8786-0bc10f09587d
---
> ⚠️ **X2 新增 DK 优先走 [[X2 DK 录入正确链路(P2数字系统+dk-manager)]]**（x2-dk-manager skill + P2 数字系统）。本条是占星节集卡册沉淀的通用顺序原则，**不要**据此去手改 `k1/Editor/DisplayKey` 字符串系统。

**DK 资源必须在配置表之前到位，流程有严格顺序依赖。**

**Why:** X2 2026占星节集卡册配置 74 个 DK（54 Portrait + 14 Icon + 6 IconBg），暴露了 DK 区间冲突、GUID 手写、脚本重复追加、导出顺序等问题。

**How to apply:**

## 流程顺序（不能乱）

```
1. 规划 DK 区间 → 查当前最大已用 DK，确认不与其他节日重叠
2. 美术资源导入 Unity → 从 .meta 文件读取 GUID（不能手写/猜）
3. reappend_dk_entries.py 追加 DK→GUID 到 Display_*.asset
4. Unity 重启 → Ctrl+Shift+E 导出（不重启可能读到旧缓存）
5. commit + push client 仓库
6. 然后才能导配置表（配置表引用这些 DK）
```

⚠️ **第5步必须在第6步之前**：client DK 先到位，配置表才能引用正确资源。

## 关键规则

- **DK 区间提前规划**：起始 DK 硬编码在脚本里，改前必须查当前表最大已用 DK
- **GUID 只从 .meta 读**：美术资源导入 Unity 后才有正确 GUID
- **资源顺序 = 配置顺序**：54张 Portrait 按 G1-G9、组内 1-6 排列，和 1123/1107 的 ID 顺序对应
- **脚本不幂等**：reappend 重跑会重复追加，跑前检查目标 DK 是否已存在
- **导出后检查三个 asset 都有更新**：Display_Portrait / Display_Icon / Display_IconBg
- **复用 DK 先确认已存在**：如 FXDisplayKey 复用圣诞 1511020681，确认 client 仓库里该 DK 有对应资源
