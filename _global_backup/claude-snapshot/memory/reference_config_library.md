---
name: 配置表知识库路径
description: 游戏运营配置知识库，含表编号索引、换皮规则、活动案例
type: reference
originSessionId: 59183ca4-8092-4018-98e1-f8b0db78970d
---
> ⚠️ **本文件及 `.cursor\config-library\*` 全是 P2 项目专用。X2 任务别用这里的 SheetID**（P2/X2 子表 id 重叠，抄错静默返回 P2 数据不报错）。X2 用 `gsheet_query.py resolve <表号>` 现解，见 [[x2-config-library]]。

配置表知识库位于 `C:\ADHD_agent\.cursor\config-library\`

## 核心文件
- `table-index.md` — 表编号→页签速查 + 常用 SheetID + 养成线数值 SheetID + 战装材料道具 ID 段
- `reskin-rules.md` — 换皮操作规则、追踪链、装饰换皮多表联动
- `cases/` — 活动配置案例存档

> 养成线深度手册已移至 `.cursor/p2-numerical-design/养成线深度手册.md`，详见 [P2 养成线知识体系](reference_p2_progression_kb.md)

## 常用表 SheetID（P2 项目）
| 编号 | 页签 | SheetID |
|------|------|---------|
| 2011 | iap_config | `1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc` |
| 2112 | activity_config | `1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E` |
| 2115 | activity_task | `1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY` |
| 2135 | activity_package | `1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc` |
| 1111 | item | `1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws` |

## 换皮追踪链（2112 为起点）
```
2112 → {"typ":"package","id":xxx} → 2135
         └── col3 (2011 ID) → 2011
                  └── condition (2013 ID) → 2013
```

**How to apply:**
- 查配置问题时先读 table-index.md 获取 SheetID，再用 gws 查询具体数据
- **数值设计验证 / 按养成线找投放对应 ID**：见 [P2 养成线知识体系](reference_p2_progression_kb.md)（已迁出本目录）
