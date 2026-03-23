# 换皮操作规则

## 一、列类型处理规则

| 列类型 | 换皮处理 |
|--------|---------|
| `base-ID` | **不换** |
| `A_STR_constant` | **必须新增**，不能复用 |
| `A_MAP_filter` | 一般不换 |
| 活动行 ID | 换 — 分配新 ID |
| 父活动 / 关联 ID | 换 |
| 前置条件建筑 ID | 换 |
| 本地化 LC key | 换（改为新主题前缀） |
| content 里的 task/package ID | 换 |
| Banner 图片路径 | 换 |
| 规则 LC key（`rule` 字段） | 同类型活动可不换 |
| 2119 关联 ID | 同类型活动可不换 |
| `A_INT_show_hud` | 换 |
| 常量数值 / 空值 / NULL | 不换 |

---

## 二、换皮完整追踪链（以 2112 为起点）

```
2112（主活动配置）
 ├── {"typ":"task","id":xxx}      → 2115（检查 condition 里的 2013 ID）
 ├── {"typ":"package","id":xxx}   → 2135（检查 2011 引用）
 │         └── col3 (2011 ID)    → 2011（检查 actv_id、recharge_actv）
 │                  └── condition (2013 ID) → 2013（确认道具配置）
 └── A_INT_show_hud               → 换新 ID
```

**规则：每层引用都要向下追踪，不能只看当前行。**

---

## 三、预购连锁礼包（pre-chain package）的特殊规则

预购连锁礼包是 2135 类型中结构最复杂的，与普通礼包有以下区别：

| 字段 | 普通礼包 | 预购连锁礼包 |
|------|---------|------------|
| 2135 head row col2 | 2011 ID | 2011 ID（相同，但该行不走 2013） |
| 2013 模板行 | 需要 | **不需要**（iap_template 不介入） |
| 2011 `A_MAP_time_info` | `actv_id` 指向 2112 | `actv_id` 指向 2112，换皮时必须同步修改 |
| 2135 chain row col11 | 模板 ID | 1111 道具对应的 `C_INT_display_key`（1511 表中查） |

**2135 chain row col11 获取方法**：用 gws 读 1111 表（`item` sheet），列 G 为 `C_INT_display_key`，按道具 ID 匹配即可。

---

## 四、已知注意事项

- `A_STR_constant` 字段（2011 ID）是必须新增的，不能沿用旧节日的
- 2115 的 condition 里直接引用 2013 ID，2013 换了 2115 也要同步更新
- 累充条件（`recharge_actv`）在 2011 表里，换皮时需单独确认新活动的累充 ID
- **复用 2112 ID 时**：2011 的 `actv_id` 和 2135 的 `condition.actvstart.id` 必须一起改，否则两处仍指向废弃 ID
- 预购连锁礼包的 2011 行 iap_status 中有大量 `recharge_actv` ID，这些是本活动的累充任务 ID，换皮时保留（已随活动一起配好）

---

## 五、配置行 Google Sheets 输出格式

在输出供粘贴到 Google Sheets 的 Tab 分隔配置行时，所有**单独成格**的 `""` 字段必须替换为 `'""` 。

原因：TSV 粘贴时 `""` 会被 Sheets 解析为空单元格；而 `'` 是 Sheets 的文本强制前缀，粘贴后单元格显示和存储的都是 `""` 字符串，符合配置表导出要求。

判断规则：
- `\t""\t`（前后都是 Tab）→ 替换
- `\t""` 位于行尾 → 替换
- JSON 内部的引号（不是独立字段）→ 保持原样
