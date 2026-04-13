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
 ├── {"typ":"exchange","id":xxx}  → 2116（道具兑换配置）
 │         └── A_ARR_item_give    → 消耗道具（如高级券）
 │         └── A_ARR_item_get     → 获得道具
 ├── {"typ":"xxx_special","id":xxx} → 2121（活动特殊组件，如 high_exchange_shop）
 │         └── A_ARR_array        → 引用的 2116 exchange ID 列表
 └── A_INT_show_hud               → 换新 ID
```

**规则：每层引用都要向下追踪，不能只看当前行。**

### 2112 → 2116 → 2121 联动说明

高级兑换商店类活动的引用链：
1. **2112** `A_ARR_activity_components` 包含 `{"typ":"high_exchange_shop","id":21219536}`
2. **2121** ID=21219536 的行，`A_ARR_array` 字段存放所有 2116 exchange ID
3. **2116** 每个 exchange ID 对应一个兑换商品行

换皮时：
- 新增商品 → 在 2116 新增行 → 更新 2121 的 `A_ARR_array` 追加新 ID
- 2112 的 component 引用通常不变（复用同一个 2121 组件 ID）

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

## 六、奖励道具图标 BUG 排查

### 排查链路

当活动界面出现**道具图标显示错误/空白**时，按以下链路逆向追踪：

```
2112 activity_config
 └── A_ARR_activity_components → {"typ":"task","id":xxx}
       ↓
 2115 activity_task（按任务 ID 定位具体档位行）
       └── A_ARR_reward → [{"asset":{"typ":"item","id":道具ID,"val":数量}}]
             ↓
 1111 x2_item（按道具 ID 查 display_key → 图标是否正确）
```

### 常见 BUG：道具 ID 位数错误（9位 vs 8位）

X2 item 表中存在**9位 ID** 的道具（例：`111110026` 金羽），命名上与 8位 ID（`11110026`）极易混淆。

若配置中写了 8位 ID `11110026`，该 ID 在 item 表中不存在，游戏会显示错误图标或空图标。

| 配置写法 | item 表是否存在 | 实际道具 | 图标结果 |
|---------|--------------|---------|---------|
| `11110026`（8位） | ❌ 不存在 | — | 错误图标 / 空图标 |
| `111110026`（9位） | ✅ 存在 | 金羽，display_key=`1511017635` | 正常显示 |

**修复方式**：在 2115 任务行的 `A_ARR_reward` 中，将错误 ID 改为正确的 9 位 ID。

### 排查用 GWS 脚本要点

- `activity_config` 中的 `A_ARR_activity_components` 字段含全部关联 task ID（如 `2115110159`～`2115110165`）
- `activity_task` 按 `A_INT_id` 列定位（**注意：ID 在列 B，即 `row[1]`，不在列 A**）
- `item` 表同理，道具 ID 在列 B（`A_INT_id`，`row[1]`），列 A（`p2_title`）为空
- 搜索道具时建议用**字符串包含匹配**（`in row_str`），而非精确等于，防止位数或格式差异导致漏搜

### 典型案例（2025-03-23）

- **活动**：`211200084` 夏日节2025-节日累充（新服）
- **问题档位**：100,000 档，任务 `2115110164`
- **错误配置**：`"id":11110026`（8位，item 表不存在）
- **正确 ID**：`111110026`（9位，金羽，`display_key=1511017635`）
- **另一道具**：`11112498` 为"漫游骰子-节日进度活动"（图标是大富翁骰子），若出现在非大富翁活动中需确认是否为意图行为

---

## 七、装饰物换皮（decoration reskin）多表联动规则

装饰物换皮涉及 7 张关联表，必须同步配置。使用 `gsheet_query.py` 工具加速查询。

### 涉及表及作用

| 表号 | 别名 | 作用 | 关键列 |
|------|------|------|--------|
| 1111 | `1111_P2` | 道具定义（主道具/升级道具/涂饰道具）| ID在col[0]，type=`statue_decorate`/`event`/`decorate_paint` |
| 1118 | `1118_dev` | 建筑升级行（每★一行）| col[11]=lvl, col[12]=max_lvl |
| 1127 | — | 建筑/装饰放置解锁 | subtab=4 为装饰，unlock_cost=主道具 |
| 1511 | `1511_dev` | display_key 视觉资源映射 | ID→美术路径 |
| 2148 | `2148_dev` | 装饰等级表（核心）| col[5]=paint标志, col[15]=涂饰道具, col[16]=涂饰buff, col[19]=2171技能行 |
| 2171 | `2171_dev` | 装饰涂饰技能 | group_id 分组，每★一行 |
| 1168 | `1168_dev` | 道具获取途径 | 关联 2148 行 ID |

### ID 编排规则

```
1111:  11112xxx  — 装饰主道具/升级道具/涂饰道具
1118:  1118xxx   — 建筑组 ID（如 1118219），行 ID = 组×100+星级（111821901）
1127:  1127xxxx  — 放置解锁 ID（如 11271111），decoration 条目需 subtab=4
1511:  151105xxx — display_key
2148:  214847    — 装饰组 ID，行 ID = 组×100+星级（21484701）
2171:  2171017   — 技能组 ID，行 ID = 组×10+级别（21710171）
1168:  11684xxx  — 获取途径 ID，每星一行
```

### 换皮查询标准流程

```bash
# 1. 查现有装饰数据（确认已有行结构）
python gsheet_query.py search 2148_dev 复活节 --indexed

# 2. 查表头确认列含义
python gsheet_query.py headers 2148_dev

# 3. 查参考行完整数据（按已有行逐列对照）
python gsheet_query.py row 2148_dev 21482703

# 4. 查 ID 占用情况（确认下一个可用 ID）
python gsheet_query.py tail 2171_dev 10
python gsheet_query.py idrange 1168_dev 11684847 11684900

# 5. 查有涂饰功能的装饰作为参考模板
python gsheet_query.py filter 2148_dev 5 0 --not --indexed
```

### 装饰 BUFF 递增模板（2148 col[14] A_ARR_BUFF）

10★ 装饰的标准 BUFF 递增路径（以 2026 科技节挖矿装饰为参考）：

| ★ | buff_a | buff_b | citybeauty | 规律说明 |
|---|--------|--------|------------|----------|
| 1 | 100 | — | 200 | ★1 只有 1 个 buff |
| 2 | 100 | 100 | 1000 | ★2 起 buff_b 加入 |
| 3 | 200 | 200 | 2000 | ★3-9: 每星 buff +100 |
| 4 | 300 | 300 | 3000 | citybeauty 每星 +1000 |
| 5 | 400 | 400 | 4000 | |
| 6 | 500 | 500 | 5000 | |
| 7 | 600 | 600 | 6000 | |
| 8 | 700 | 700 | 7000 | |
| 9 | 800 | 800 | 8000 | |
| 10 | 1000 | 1000 | 9000 | ★10 buff 跳到 1000（非 900）|

**JSON 原文**（可直接复制替换 buff_id）：

```
★1:  [{"typ":"buff","id":BUFF_A,"val":100},{"typ":"citybeauty","id":12230001,"val":200}]
★2:  [{"typ":"buff","id":BUFF_A,"val":100},{"typ":"buff","id":BUFF_B,"val":100},{"typ":"citybeauty","id":12230001,"val":1000}]
★3:  [{"typ":"buff","id":BUFF_A,"val":200},{"typ":"buff","id":BUFF_B,"val":200},{"typ":"citybeauty","id":12230001,"val":2000}]
★4:  [{"typ":"buff","id":BUFF_A,"val":300},{"typ":"buff","id":BUFF_B,"val":300},{"typ":"citybeauty","id":12230001,"val":3000}]
★5:  [{"typ":"buff","id":BUFF_A,"val":400},{"typ":"buff","id":BUFF_B,"val":400},{"typ":"citybeauty","id":12230001,"val":4000}]
★6:  [{"typ":"buff","id":BUFF_A,"val":500},{"typ":"buff","id":BUFF_B,"val":500},{"typ":"citybeauty","id":12230001,"val":5000}]
★7:  [{"typ":"buff","id":BUFF_A,"val":600},{"typ":"buff","id":BUFF_B,"val":600},{"typ":"citybeauty","id":12230001,"val":6000}]
★8:  [{"typ":"buff","id":BUFF_A,"val":700},{"typ":"buff","id":BUFF_B,"val":700},{"typ":"citybeauty","id":12230001,"val":7000}]
★9:  [{"typ":"buff","id":BUFF_A,"val":800},{"typ":"buff","id":BUFF_B,"val":800},{"typ":"citybeauty","id":12230001,"val":8000}]
★10: [{"typ":"buff","id":BUFF_A,"val":1000},{"typ":"buff","id":BUFF_B,"val":1000},{"typ":"citybeauty","id":12230001,"val":9000}]
```

使用时将 `BUFF_A`/`BUFF_B` 替换为实际 buff ID（如 `12117004`/`12117005`）。

**5★ 装饰截取 ★1-5 即可**，citybeauty 值保持 200/1000/2000/3000/4000 不变。

**已有装饰扩星时**：保持现有 ★1-3 的 buff 不动，★4 起接续现有 buff 值继续递增，buf_a/buff_b 各 +100/星，citybeauty +1000/星。

---

### 已有装饰扩星 + 新增涂饰的注意事项

当需要将已有 3★ 装饰扩充到 10★ 并加涂饰时：
1. **现有行需修改**：1118 的 `max_lvl`(col[12]) 从 3→10，2148 的 `star_max`(col[7]) 从 3→10，`paint`(col[5]) 从 0→1
2. **现有 2148 行追加涂饰字段**：col[15] 加 `[涂饰道具ID]`，col[16] 加涂饰 buff，★3 行的 col[19] 填 2171 起始行 ID
3. **新增行**：1118 的 ★4-10 行、2148 的 ★4-10 行、2171 技能行（★3 起生效，每星一行）、1168 获取途径行
4. **涂饰道具（1111）**：type=`decorate_paint`，effect 字段必须包含 `{"typ":"decorate_paint","id":2148组ID,"val":86400000}` + 自回收 `{"typ":"item","id":自身ID,"val":1}`
5. **升级材料复用**：扩星时的升级道具沿用原有（如 2025 复活节用 `11112502`），不需要新建

### 1127 建筑/装饰放置解锁表

新装饰必须在 1127 中加一行，玩家才能在建造界面放置。**旧装饰扩星不需要加**（原有 1127 行即可）。

**列结构（P2 表，col[0]=p2_title）：**

| 列 | 字段 | 装饰条目典型值 |
|---|---|---|
| [1] | A_INT_id | `11271111` |
| [2] | C_STR_comment | 2026复活节雕像 |
| [3] | （空） | |
| [4] | A_ARR_building_ids | `[1118219]` |
| [5] | C_INT_display_order | `30057` |
| [6] | C_INT_continuous_construct | `0` |
| [7] | A_INT_count | `1` |
| [8] | A_INT_count_max | `1` |
| [9] | C_ARR_display_labels | `["decoration"]` |
| [10] | A_MAP_requirement | `{}` |
| [11] | A_ARR_unlock_cost | `[{"typ":"item","id":主道具ID,"val":1}]` |
| [12] | C_ARR_unlock_desc | `[{"typ":"lc","txt":"LC_EVENT_xxx_get_tips"}]` |
| [13] | C_MAP_show_requirement | `{}` |
| [14] | A_INT_redoverlap | `0` |
| [15] | C_INT_subtab | `4`（装饰固定值） |
| [16] | A_INT_country_use_type | `0` |

**换皮时**：替换 id、comment、building_ids、display_order、unlock_cost 中的道具 ID、unlock_desc 的 LC key。其余列保持不变。

### paint_buff 递增规律（2148 col[16] A_ARR_paint_buff）

涂饰 buff 使用统一 buff ID `121140935`，val 按星级线性递增：

| ★ | paint_buff val |
|---|---|
| 1 | 100 |
| 2 | 200 |
| 3 | 300 |
| 4 | 400 |
| 5 | 500 |
| 6 | 600 |
| 7 | 700 |
| 8 | 800 |
| 9 | 900 |
| 10 | 1000 |

JSON 模板：`[{"typ":"buff","id":121140935,"val":★×100}]`

### 典型案例（2026 复活节装饰换皮）

- 1 个新装饰（5★）+ 2 个旧装饰扩星（3→10★）+ 3 个新涂饰道具
- 涉及 7 张表、约 60 行新增配置 + 1127 新装饰放置行
- 升级材料复用已有道具，涂饰道具和技能行全部新增

---

### QA 变更总结模板（装饰换皮完成后发给测试）

每次装饰换皮完成后，按以下结构整理变更总结发给测试：

```markdown
## {节日名称}装饰配置变更总结

### 一、变更概览
| 装饰 | 变更类型 | 星级 | group | building |
|---|---|---|---|---|
| 新装饰名 | 全新增 | 1-N★ | 2148组ID | 1118组ID |
| 旧装饰名 | 扩星+加涂饰 | 原M★→N★ | 2148组ID | 1118组ID |

### 二、涉及配置表及变更明细
按表列出：修改行数 + 新增行数 + ID 范围
- 1111 道具表 — 新增 X 条（列出每个道具 ID 和说明）
- 2148 装饰等级表 — 修改 X 条 + 新增 Y 条
- 1118 建筑升级表 — 修改 X 条 + 新增 Y 条
- 2171 装饰技能表 — 新增 X 条
- 1168 来源表 — 新增条目
- 1127 放置解锁表 — 新增 X 条（仅新装饰需要）
- 1511 display_key — 新增

### 三、测试要点
1. 新装饰放置：道具使用→建筑放置→升级到满星
2. 扩星：原有装饰继续升级，材料消耗正确
3. 涂饰：涂饰道具使用后外观切换、buff 生效
4. retake：仅满星显示回收选项
5. BUFF 递增：每星 buff +100、citybeauty +1000
6. 图标/外观：各星 display_key 资源正常
```

---

## 五、配置行 Google Sheets 输出格式

在输出供粘贴到 Google Sheets 的 Tab 分隔配置行时，所有**单独成格**的 `""` 字段必须替换为 `'""` 。

原因：TSV 粘贴时 `""` 会被 Sheets 解析为空单元格；而 `'` 是 Sheets 的文本强制前缀，粘贴后单元格显示和存储的都是 `""` 字符串，符合配置表导出要求。

判断规则：
- `\t""\t`（前后都是 Tab）→ 替换
- `\t""` 位于行尾 → 替换
- JSON 内部的引号（不是独立字段）→ 保持原样

---

## 八、配置生成器 HTML 规范

换皮时应生成一个交互式 HTML 配置生成器，存放在 `config-library/cases/{活动名}/config-output.html`，方便策划填写道具ID后直接复制配置行。

### 8.1 生成器必备功能

| 功能 | 说明 |
|------|------|
| 实际表头 | 必须从 Google Sheet 读取真实表头，不能硬编码猜测 |
| 商品增删 | 左侧商品列表支持添加/删除行 |
| 列选择器 | 每个输出表格可勾选需要的列，隐藏不需要的列 |
| 一键复制 | 每个表格有复制按钮，复制为 Tab 分隔格式可直接粘贴到 Sheet |
| 预填已知ID | 已确认的道具ID直接填入，只留待填项为空 |
| 实时生成 | 修改输入后点击生成按钮立即更新输出 |

### 8.2 输出表格要求

每个涉及的配置表（如 2112/2115/2116/2121）单独一个表格区块：
- 显示完整表头（从实际 Sheet 读取）
- 显示行数 × 列数统计
- 支持列可见性切换
- 复制时包含表头行

### 8.3 表头获取方法

```bash
# 获取表头示例
GOOGLE_WORKSPACE_PROJECT_ID='calm-repeater-489707-n1' gws sheets spreadsheets values get \
  --params '{"spreadsheetId": "SHEET_ID", "range": "TAB_NAME!A1:Z1"}'
```

常用表的 Sheet ID 见 `table-index.md`。

### 8.4 HTML 模板结构

```
config-output.html
├── 左侧输入面板（sticky）
│   ├── 商品列表（可增删）
│   ├── 关联ID输入（cat_id等）
│   └── ID范围设置
├── 右侧输出面板
│   ├── 2116 表格 + 列选择器 + 复制按钮
│   ├── 2115 表格 + 列选择器 + 复制按钮
│   ├── 2121 修改说明
│   └── 2112 表格 + 列选择器 + 复制按钮
└── Toast 提示
```

### 8.5 参考实现

完整示例见：`config-library/cases/2026_pioneer_marble_gacha/config-output.html`

关键实现点：
- 表头存储在 `HEADERS` 对象中
- 列可见性用 `colVisible` 数组控制
- `renderTable()` 函数根据可见性过滤列
- `copyTable()` 函数生成 Tab 分隔文本

---

## 九、本地化 LC Key 格式规则

### 9.1 LC Key 完整格式

非 1011 配置表内引用的本地化 key 格式为：`LC_页签名_ID`

例如：
- `LC_EVENT_noumenon_gacha_welfare_title`
- `LC_ITEM_add_food_name`

### 9.2 AI翻译暂存表写入格式

1011 i18n 表的「AI翻译暂存」页签用于提交新 LC 条目，格式如下：

| ✅提交 | 目标页签 | ID | cn | en |
|--------|----------|-----|-----|-----|
| FALSE | EVENT | noumenon_gacha_welfare_title | 福利关卡 | BONUS ROUND |

**关键区别**：
- 「目标页签」列填页签名（如 `EVENT`、`ITEM`）
- 「ID」列只填纯 ID 部分，**不带 `LC_页签名_` 前缀**
- 系统会自动拼接为完整 key：`LC_{页签}_{ID}`

### 9.3 道具 LC Key 查询

道具的 LC key 定义在 1111 item 表的以下列：
- `A_MAP_lc_name`：道具名称 LC，格式 `{"typ":"lc","txt":"LC_EVENT_xxx_item_name_1"}`
- `C_MAP_lc_desc`：道具描述 LC，格式 `{"typ":"lc","txt":"LC_EVENT_xxx_item_desc_1"}`

写入 AI翻译暂存时，从 `txt` 字段提取完整 key，去掉 `LC_EVENT_` 前缀后填入 ID 列。

### 9.4 GWS 写入示例

```bash
# 单行写入
gws sheets +append --spreadsheet "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY" \
  --values 'FALSE,EVENT,noumenon_gacha_welfare_title,福利关卡,BONUS ROUND'

# 批量更新（覆盖指定范围）
gws sheets spreadsheets values update \
  --params '{"spreadsheetId":"11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY","range":"AI翻译暂存!A101:E105","valueInputOption":"RAW"}' \
  --json '{"values":[
    ["FALSE","EVENT","key_id_1","中文1","English1"],
    ["FALSE","EVENT","key_id_2","中文2","English2"]
  ]}'
```

### 9.5 LC 反向确认流程

新增或换皮活动时，必须反向确认所有 LC 引用是否在 1011 表中存在。

**确认链路：**

```
2112 activity_config
├── A_MAP_text → group_label, label, title 等 LC key
├── A_MAP_description → rule, note 等 LC key
│
1111 item（活动相关道具）
├── A_MAP_lc_name → 道具名称 LC key
├── C_MAP_lc_desc → 道具描述 LC key
│
Jira/设计稿 弹窗文案
└── 福利关卡、兑换商店等弹窗 LC key
```

**确认步骤：**

1. 查 2112 活动行的 `A_MAP_text` 和 `A_MAP_description` 字段，提取所有 LC key
2. 查 1111 道具表，找活动相关道具的 `A_MAP_lc_name` 和 `C_MAP_lc_desc` 字段
3. 去 1011 EVENT 页签搜索这些 key（去掉 `LC_EVENT_` 前缀后的 ID 部分）
4. 不存在的 key 写入 AI翻译暂存

**GWS 确认命令：**

```bash
# 查 2112 活动 LC 引用
gws sheets spreadsheets values get --params '{"spreadsheetId":"2112_SHEET_ID","range":"A1:Z5000"}' | grep -E "活动ID"

# 查 1111 道具 LC 引用
gws sheets spreadsheets values get --params '{"spreadsheetId":"1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws","range":"A1:K5000"}' | grep -E "道具ID"

# 在 1011 EVENT 页签搜索 LC key
gws sheets spreadsheets values get --params '{"spreadsheetId":"11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY","range":"EVENT!A1:E50000"}' | grep -E "key_id"
```

**常见复用规则：**
- 同类型活动的 `rule` LC 可复用（如弹珠GACHA复用 `2025anni_marble_gacha_rule`）
- 通用弹窗 LC（如 `noumenon_gacha_*`）跨活动复用
- 活动标题、道具名称/描述必须新增
