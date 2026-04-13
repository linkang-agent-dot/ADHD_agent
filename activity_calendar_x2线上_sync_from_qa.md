# 页签对比说明（QA 为准 → 同步到 线上）

**表格**：https://docs.google.com/spreadsheets/d/1x-kAjIEox-JX_CQffEVw1shKZZlUpxR_fe0flTz2Iuk/edit

| 页签名 | gid | 角色 |
|--------|-----|------|
| `activity_calendar_x2（线上）` | 1459407900 | 线上 |
| `activity_calendar_x2（QA）` | 681415886 | QA |

- **为准（源）**：`activity_calendar_x2（QA）`（QA）
- **待对齐（目标）**：`activity_calendar_x2（线上）`（线上）
- 线上 数据行数：**1807**；QA 数据行数：**1809**
- 仅 QA 有、需整行复制到 线上：**4** 行
- 仅 线上 有、QA 无：**2** 行
- 两边同 Key 但单元格不同：**8** 处

---

## 一、仅 QA 有（整行从 `activity_calendar_x2（QA）` 复制到 `activity_calendar_x2（线上）`）

在 **QA** 页签按 `Id` 搜索，选中整行复制到 **线上**；勿覆盖 meta 行。

| # | Id | 描述列（PkgDesc/第二列） |
|---|-----|--------------------------|
| 1 | 211110461 | 阶梯礼包-三代骑 |
| 2 | 211110542 | 前期节日-限时抢购（沙滩节包装 |
| 3 | 211110543 | 占星节-2026-wonder恶狼-砸金蛋 |
| 4 | 211110544 | 节日通用自选周卡（前期节日） |

---

## 二、仅 线上 有（QA 无，是否删除由你决定）

| # | Id | 描述列 |
|---|-----|--------|
| 1 | 211110461 | 阶梯礼包-修女替代英雄-德鲁伊 |
| 2 | 211110542 | 阶梯礼包-金修女-ark上 |

---

## 三、同 Key 不同单元格（线上 应改成与 QA 一致）

| Id | 描述 | 列 | 线上（当前） | QA（为准） |
|----|------|-----|-------------------|-------------------|
| 211110418 | 首充礼包-任务版 | Trigger | {"typ":"afcutc","val":"0h","is_ark":1} | {"typ":"time","is_ark":1} |
| 211110418 | 首充礼包-任务版 | Times | {"fcastdur":"0h", "closedur":"0h","typ":"permanent"} | {"fcastdur":"0h","closedur":"0h","typ":"permanent"} |
| 211110530 | 阶梯礼包-首充接档裁缝-付费能力值版本 | Schema | {"typ":"schema","id":[1,2,3,4,5,6]} | {"typ":"schema","id":[0]} |
| 211110535 | 救美女——寻找线索 | Trigger | {"typ":"adventure_main","val":"281510009"} | {"typ":"adventure_main","val":"211110535"} |
| 211110540 | 阶梯礼包-金修女 | Trigger | {"typ":"hero_get","val":"19201080"} | {"typ":"time","is_ark":1} |
| 211110540 | 阶梯礼包-金修女 | Times | {"fcastdur":"0h", "closedur":"0h","typ":"permanent"} | {} |
| 211110541 | 美妮登场-（德鲁伊）-替换二代修女 | Trigger | {"typ":"afcutc","val":"912h","is_ark":1} | {"typ":"time","is_ark":1} |
| 211110541 | 美妮登场-（德鲁伊）-替换二代修女 | Times | {"fcastdur":"0h", "actvdur":"168h", "closedur":"0h"} | {} |

---

## 四、说明

- 对齐 Key：`fwcli_name` 行中 **Id** 列 + 第 **4** 列（A=1）作为描述；若表结构特殊请人工核对。
- 读取范围：`A1:AZ8000`；列过多可改脚本 `--range`。
