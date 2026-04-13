# 配置换皮技能

触发词：换皮、配置换皮、换主题、reskin、这个配置换成XX、帮我分析换皮字段、评估需要哪些配置表

> 本技能负责**分析、评估和生成**配置行。导入到配置表的操作见 `P2-config-upload` 技能。
> 支持 **P2** 和 **X2** 两个项目，大定义一致但列号和子字段有差异，分开维护：
> - P2 → [modules-p2.md](./modules-p2.md)
> - X2 → [modules-x2.md](./modules-x2.md)

---

## 一、执行流程（模块驱动，5 步）

### S-1 确认项目（P2 / X2）

**每次接到换皮任务，第一步必须确认是哪个项目。** 项目决定查哪套 GSheet 表。

| 项目 | 别名后缀 | 示例 | 注册表索引 |
|------|---------|------|-----------|
| **P2** | `_dev` 或 `_P2` | `2112_dev`, `1111_P2` | 内置别名（BUILTIN_ALIASES） |
| **X2** | `_x2_` 或无后缀 | `2112_x2_activity_config`, `2112` | 自动解析（X2 注册表） |

**判断依据**（按优先级）：
1. 用户明确说了项目名 → 直接确定
2. 给了 GSheet 链接 → 对照 [table-index.md](../../config-library/table-index.md) 的 SheetID 判断
3. 任务上下文：P2 导表流程 / X2 导表流程
4. 不确定 → **必须问清楚**

**确认后的动作**：整个任务期间，所有 `gsheet_query.py` 命令统一使用对应项目的别名：

```bash
# P2 项目
python gsheet_query.py search 2112_dev 复活节
python gsheet_query.py row    2011_dev 20118xxxxx

# X2 项目
python gsheet_query.py search 2112_x2_activity_config 复活节
python gsheet_query.py row    2011_x2_iap_config 20118xxxxx
```

### S0 分析任务 → 命中模块

**不再按 ABCD 类型对号入座。** 从任务语义出发，逐条过模块触发条件：

| 模块（表） | 触发条件（何时需要） |
|-----------|-------------------|
| **2112 活动主体** | 有活动入口（玩家能在活动界面看到的东西） |
| **2115 活动任务** | 活动有「做 XX 得 YY」的任务机制 |
| **2135 活动礼包** | 活动中有礼包购买入口 |
| **2011 礼包规则** | 涉及 IAP 付费购买 |
| **2013 礼包内容模板** | 礼包需要道具组合模板（标准礼包；预购连锁不走） |
| **1111 道具定义** | 涉及新道具或需查道具属性 |
| **1118 建筑升级** | 有星级升级机制 |
| **2148 装饰等级** | 涉及装饰物的星级/属性/涂饰 |
| **2171 涂饰技能** | 装饰有涂饰功能（激活后获额外技能） |
| **1127 放置解锁** | 新建筑/新装饰需在建造界面出现 |
| **1168 道具来源** | 需配置道具获取途径展示 |
| **1511 外显资产(DK)** | 有图标/模型需要展示 |
| **1011 本地化(LC)** | 有玩家可见的文字 |

**操作**：把命中的模块列出来，就是本次任务的工作范围。然后去对应项目的模块知识库（P2→[modules-p2.md](./modules-p2.md) / X2→[modules-x2.md](./modules-x2.md)）读每张表的**大定义**（理解这张表是什么）和**子定义**（在当前上下文中具体改什么字段）。

> 如果所有表都不命中 → 可能需要新建配置表或新模块，先评估再动手。

**确认变更性质**：

| 任务类型 | 说明 | 注意 |
|---|---|---|
| **纯换皮** | 结构不变，只换 ID/名称/图片/LC key | 按标准流程走 |
| **换皮 + 新功能** | 在换皮基础上新增字段/typ/关联行 | 新字段需另行确认结构；新道具/组件需同步触发对应模块 |
| **新功能评估** | 全新需求，评估需要哪些模块 | 逐条过触发条件，输出模块清单 + 是否需要新表 |

### S1 读原始行

从用户给出的配置行（或 GSheet）中提取所有字段。对照对应项目的模块知识库中该表的重点字段说明，理解每个字段的角色。

### S2 按字段角色决定处理方式

每张表在模块知识库的重点字段表中已标注换皮处理方式。通用规则：

| 字段类型 | 换皮处理 |
|---------|---------|
| `A_STR_constant` | **必须新增** — 不能复用 |
| `A_MAP_filter` | **一般不换** |
| 活动行 ID | **换** — 分配新 ID |
| 父活动/关联 ID | **换** |
| 前置条件建筑 ID | **换** |
| 本地化 LC key | **换** — 改为新主题前缀 |
| 内容引用（task/package ID）| **换** |
| Banner 图片路径 | **换** — 新主题素材 |
| `A_INT_show_hud` | **换** |
| 常量数值（0/1/空字符串/空数组）| **不换** |
| 规则 LC key（`rule` 字段）| 同类型活动**可不换** |
| 2119 关联 ID | 同类型活动**可不换** |

#### ⚠️ S2.5 外键 ID 验证（容易漏，曾造成严重遗漏）

配置里凡是 `rewards`、`drop JSON`、`goods_id`、`category_param` 等字段中包含的 **item id**，都是外键引用——它们不在"行 ID"列里，换皮时容易被忽视。

**必须对每一个外键 id 在 1111 表执行验证**：

```bash
# P2 项目 → 用 1111_P2（开发版，含最新道具）
python gsheet_query.py row 1111_P2 {item_id}

# X2 项目 → 用 1111_x2_item（线上版）；查不到再查 1111_P2 兜底
python gsheet_query.py row 1111_x2_item {item_id}
```

检查 `S_STR_comment` 和 `A_MAP_lc_name.txt` 是否含旧节日名称关键词：
- 命中 → 节日专属，**必须换**（如 BP 随机箱 `11119772`、节日卡包 `111110002`）
- 未命中 → 通用道具，**保留**（如进度道具 `11119262`、训练加速 `11111155`）

> ⚠️ **已踩的坑**：不要先下结论再补查。曾因锚定偏差（误以为累充奖励是机甲喷漆）导致结论反复推翻。正确流程：**拿到 ID → 逐个查 1111 → 搞清 class/comment → 再归纳类型 → 最后写结论**。

**先建清单，再逐一核查**，不要凭直觉跳过任何字段。没有跑过的 id 不能默认为正确。

### S3 追踪依赖链

**核心原则**：每张表的模块知识库底部都有「依赖关系」图，按箭头方向逐层追踪，确保所有 ID 引用都指向新行。

以活动礼包为例的完整追踪链：

```
2112
 ├── components.task → 2115 → fincond 内含 2013 ID
 ├── components.package → 2135 → col3 指向 2011 ID
 │                                 └── 2011.time_info.actv_id → 反向引用 2112
 │                                 └── 2011 ← 2013.config_id
 └── show_hud → 换新 ID
```

**关键联动规则**（跨表 ID 必须同步）：

| 场景 | 必须同步更新 |
|------|------------|
| 2011 ID 变了 | 2013 的 `config_id` + 2135 的 `iap` 字段都要改 |
| 2112 ID 变了（或复用旧 ID） | 2011 的 `actv_id` + 2135 chain row 的 `condition.actvstart.id` 都要改 |
| 道具 ID 变了 | 所有引用该道具的表（2115 reward、2013 items、1127 unlock_cost 等）都要改 |
| **集卡册换皮** | 见下方集卡册追踪链 |

**集卡册依赖追踪链**：
```
6001 (book)
 ├── A_ARR_group_id → 6002 (group)
 │    ├── A_ARR_card_id → 6003 (card) → col[2] A_INT_star 判断5★
 │    └── A_ARR_rewards → 每个 item id → 1111 验证节日归属 ⚠️
 └── A_ARR_rewards → 每个 item id → 1111 验证节日归属 ⚠️

6004 (集卡商店)
 └── goods_id → 指向当前节日保底卡包 ID → 每次换节日必须同步更新 ⚠️
```

> ⚠️ 集卡册换皮详细操作见 `card-collection-config` 技能，含 gws 别名注册、8组结构说明、奖励道具换皮记录。

> ⚠ ID 建议 vs 用户实际分配不一致时：用户确认实际 ID 后，**立即一次性重新输出所有受影响表的完整行**。

### S4 输出换皮后的完整配置行

> 进入 **第二节：输出规范** 执行输出。

---

## 已知组装模式速查（常见类型的模块组合）

> 以下是已积累经验的组装模式，仅供参考。新任务应先走 S0 触发条件，而非直接对号入座。

| 组装模式 | 命中模块 | 典型案例 | 专项规则 |
|---------|---------|---------|---------|
| **普通活动礼包** | 2112 + 2115 + 2135 + 2013 + 2011 + 1011 + 1511 | [2026异族大富翁每日礼包](../config-library/cases/2026_alien_monopoly_daily_pack/overview.md) | — |
| **预购连锁礼包** | 2112 + 2135 + 2011 + 1011 + 1511（跳过 2013） | [2026复活节预购连锁](../config-library/cases/2026_easter_pre_chain/overview.md) | [reskin-rules.md §三](../config-library/reskin-rules.md) |
| **装饰物** | 1111 + 1118 + 1127 + 2148 + 2171 + 1168 + 1011 + 1511 | 2026复活节装饰 | [reskin-rules.md §七](../config-library/reskin-rules.md) |
| **集卡册** | 1111(卡包道具) + 6001(book) + 6002(group rewards) + 6003(card星级) + 6004(集卡商店) + 1011 | [2026复活节集卡册](../config-library/cases/2026_easter_card_collection/localization.md) | `card-collection-config` 技能；**rewards 里外键 id 必须逐一验证（见 S2.5）**；6004 每次换节日必改 |
| **机甲累充** | 2112 + 2115(11档任务) + 2121(jump_link) + 1111(奖励道具) | [2026复活节机甲累充](../config-library/cases/2026_easter_mecha_accum/progress.md) | 2112 含 `iap_show` + `mecha_skin_select` 组件；主奖是**节日玩法货币**（不是喷漆）；每节日换货币道具 ID + group_label LC；**11 档结构跨节日一致** |
| **多条件连锁礼包** | 2115(仅改 reward) — 2112 **整行复用不改** | [2026复活节连锁任务](../config-library/cases/2026_easter_chain_task/overview.md) | 只替换 2115 reward 中的节日绑定道具（BP 箱/卡包），保留通用道具（进度道具/加速）；94 行级可用 Python 批量 str replace；**2115 ID 在 col[1]，查询须加 `--id-col 1`** |

> 同一活动可能跨多个模式（如主活动+装饰），各自命中的模块取并集即可。

---

## 二、输出规范

### 2.1 TSV 输出格式铁律（必须遵守）

> **所有配置行必须输出为可一键复制粘贴进 Google Sheets 的完整 TSV 行。**
> 禁止以下两种错误输出方式：
> - ❌ 输出"把 X 替换为 Y"的说明表，让用户手动操作
> - ❌ 只输出变更的字段，而非完整行

正确做法：
- ✅ 每张表一个代码块，每行包含所有列，Tab 分隔，直接复制即可粘贴
- ✅ 新增行与覆盖行都给完整行，不允许省略任何列
- ✅ 所有单独成格的 `""` 字段输出为 `'""` （Sheets 粘贴规则）

### 2.2 本地化检查清单（每次必做，容易漏）

换皮生成配置行后，必须同步检查以下 4 类本地化，每类都要直接输出可粘贴内容：

| 检查项 | 在哪里 | 输出内容 |
|---|---|---|
| **活动标题/描述 LC key** | 2112 主活动行 col7 | 完整替换后的 2112 整行 |
| **活动规则 LC key** | 2112 主活动行 col9 | 同上 |
| **礼包标题 LC key** | 2013 模板 `pkg_title` 列 | 完整替换后的 2013 各行 |
| **新道具名/描述 LC key** | 道具表（item i18n）+ 道具行本身引用 | 道具行完整更新行 + LC key 文本汇总 |
| **集卡册卡包描述正文** | 本地化页签「卡包 Key 本地化」区域2（Col K-L，R2-R25）| 逐行确认中英文描述里的游戏名已换成当前节日 |

> ⚠️ **集卡册卡包描述专项坑（2026复活节踩坑）**：换节日时只把 Key 前缀（`tech_fest_pack_` → `easter_fest_pack_`）批量替换，会漏掉 Col K/L 描述正文里的具体游戏名（如"寻找破译器"、"矿场日常"等仍残留科技节子游戏名）。正确做法：对照 group 映射逐行核对描述正文里的游戏名。详见 `card-collection-config/references/gotchas.md`。

道具行额外要检查：
- `actv_open` effect 列表是否需要追加新活动 ID
- 道具行引用的 LC key 前缀是否需要从旧活动换成新活动

### 2.3 LC Key 文本汇总格式

最终输出一个可复制的 TSV 块，**标准四列格式**（LC_KEY / key / 中文 / 英文），每行一条：

```
LC_ITEM_xxx_name	xxx_name	道具名称中文	Item Name EN
LC_ITEM_xxx_desc	xxx_desc	道具描述中文	Item description EN.
LC_ITEM_xxx_paint_name	xxx_paint_name	"道具名"粉刷	"Item Name" Paint
LC_ITEM_xxx_paint_desc	xxx_paint_desc	使用后可激活"道具名"装饰物带来的增益状态。	Activate the buff provided by the "Item Name" decoration upon use.
```

**涂饰道具描述句式（中英固定模板）：**
- 中文：`使用后可激活"{装饰名}"装饰物带来的增益状态。`
- 英文：`Activate the buff provided by the "{Decoration Name}" decoration upon use.`

**升级道具描述句式（中英固定模板）：**
- 中文：`{道具描述}。首次获得可以解锁{装饰名}，后续获得可用于升级{装饰名}。`
- 英文：`{desc}. The first one unlocks the {Decoration Name} decoration; additional ones can be used to upgrade it.`

**引号字段说明：**
- `paint_name` 格式：`"{装饰名}"粉刷` / `"{Decoration Name}" Paint`（装饰名用引号包裹）
- 文本内部的引号**不是独立字段**，不在 `'""` 保护规则范围内，直接原样输出即可

- 待填字段用 `{待替换:说明}` 占位
- 列出所有整型 ID（`int id`，便于另外导表）

### 2.4 典型案例（2026复活节装饰 LC Key，共14条）

```
LC_ITEM_2026easter_dec2_item_2	2026easter_dec2_item_2	转运老虎机	Lucky Slot Machine
LC_ITEM_2026easter_dec2_item_2_desc	2026easter_dec2_item_2_desc	投币，拉闸，等待幸运降临。	Insert a coin, pull the lever, and wait for luck to arrive.
LC_EVENT_2026easter_dec2_item_3_get_tips	2026easter_dec2_item_3_get_tips	{待填:获取提示}	{待填:EN}
LC_ITEM_2026easter_upgrade_item_name	2026easter_upgrade_item_name	转运老虎机	Lucky Slot Machine
LC_ITEM_2026easter_upgrade_item_desc	2026easter_upgrade_item_desc	投币，拉闸，等待幸运降临。首次获得可以解锁转运老虎机，后续获得可用于升级转运老虎机。	Insert a coin, pull the lever, and wait for luck to arrive. The first one unlocks the Lucky Slot Machine decoration; additional ones can be used to upgrade it.
LC_ITEM_2026easter_paint_dec2_name	2026easter_paint_dec2_name	"转运老虎机"粉刷	"Lucky Slot Machine" Paint
LC_ITEM_2026easter_paint_dec2_desc	2026easter_paint_dec2_desc	使用后可激活"转运老虎机"装饰物带来的增益状态。	Activate the buff provided by the "Lucky Slot Machine" decoration upon use.
LC_ITEM_2025easter_paint_name	2025easter_paint_name	"彩蛋叠叠乐"粉刷	"Egg Stacking Fun" Paint
LC_ITEM_2025easter_paint_desc	2025easter_paint_desc	使用后可激活"彩蛋叠叠乐"装饰物带来的增益状态。	Activate the buff provided by the "Egg Stacking Fun" decoration upon use.
LC_ITEM_2024easter_paint_name	2024easter_paint_name	"缤纷满篮"粉刷	"Colorful Basket" Paint
LC_ITEM_2024easter_paint_desc	2024easter_paint_desc	使用后可激活"缤纷满篮"装饰物带来的增益状态。	Activate the buff provided by the "Colorful Basket" decoration upon use.
LC_EVENT_2026easter_dec_paint_skill_name	2026easter_dec_paint_skill_name	{待填:2026涂饰技能名称}	{待填:EN}
LC_EVENT_2025easter_dec_paint_skill_name	2025easter_dec_paint_skill_name	{待填:2025涂饰技能名称}	{待填:EN}
LC_EVENT_2024easter_dec_paint_skill_name	2024easter_dec_paint_skill_name	{待填:2024涂饰技能名称}	{待填:EN}
```

---

## 三、工具与资源

### 3.1 配置表查询工具（gsheet_query.py）

换皮过程中需要频繁查 GSheet 数据（表头、ID 范围、关键字搜索等）：

**工具位置**：`.cursor/skills/google-workspace-cli/gsheet_query.py`

```bash
# ── P2 项目（用 _dev / _P2 后缀） ──
python gsheet_query.py headers  2112_dev
python gsheet_query.py search   2112_dev 复活节
python gsheet_query.py row      2112_dev 21127284

# ── X2 项目（用注册表自动解析的 _x2_ 名称） ──
python gsheet_query.py headers  2112_x2_activity_config
python gsheet_query.py search   2112_x2_activity_config 复活节

# ── 通用操作 ──
python gsheet_query.py idrange  1168_dev 11684847 11684874
python gsheet_query.py tail     2171_dev 10
python gsheet_query.py filter   2148_dev 5 0 --not
python gsheet_query.py tabs     2112_dev
```

**内置别名**（全部指向 P2 项目的开发版表）：

| 别名 | 说明 |
|------|------|
| `1111_P2` | 道具表 |
| `1118_dev` | 建筑升级表（装饰星级）|
| `1168_dev` | 道具来源/获取途径表 |
| `1511_dev` | display_key 视觉资源表 |
| `2148_dev` | 装饰物等级表（核心表）|
| `2171_dev` | 装饰涂饰技能表 |
| `2011_dev` | 礼包规则表 (iap_config) |
| `2013_dev` | 礼包内容模板表 (iap_template) |
| `2112_dev` | 活动主体表 (activity_config) |
| `2115_dev` | 活动任务表 (activity_task) |
| `2135_dev` | 活动礼包表 (activity_package) |

> ⚠️ 注意：**注册表自动解析的 `_x2_` 表是 X2 项目的，我们是 P2 项目。** 必须使用上述 `_dev` 别名，不要直接用 `2112_x2_activity_config` 等。

可通过 `alias set` 添加自定义别名。

**表特殊参数（踩过的坑）**：

| 表 | 注意事项 |
|----|---------|
| `2115` | **ID 在 col[1]**（col[0] 是 group），`idrange`/`row` 须加 `--id-col 1` |
| `1118` | P2 页签名含「不要直接修改」，X2 含「严禁手改」，tab 选择注意 |
| `2135` | P2 默认页签 `activity_event_pkg`；X2 默认页签带 `(qa)` |

```bash
# 2115 按 ID 范围查（必须 --id-col 1）
python gsheet_query.py idrange 2115_dev 211560390 211560483 --id-col 1

# 2115 按单行查（同样）
python gsheet_query.py row 2115_dev 211552010 --id-col 1
```

**装饰换皮额外涉及的表**（无需别名，直接用表号查注册表）：

| 表号 | 说明 | 装饰换皮要点 |
|------|------|------------|
| `1127` | 建筑/装饰放置解锁 | 新装饰需加一行（subtab=4），旧装饰扩星不需要 |

### 3.2 配置资源库

完整案例和 ID 对照存于：`c:\ADHD_agent\.cursor\config-library\`

```
config-library/
├── README.md              — 快速导航
├── reskin-rules.md        — 换皮规则详版（§三=预购连锁, §六=图标BUG, §七=装饰物）
├── table-index.md         — 编号→页签速查
└── cases/
    ├── [类型A] 2026_alien_monopoly_daily_pack/   — 普通活动礼包，5表完整配置
    │   ├── overview.md   — ID 对照总表 + 待填字段清单
    │   ├── 2112.md / 2115.md / 2135.md / 2013.md / 2011.md
    ├── [类型B] 2026_easter_pre_chain/            — 预购连锁礼包，2112 ID 复用场景
    │   └── overview.md   — ID 对照 + actv_id 修正示例
    └── [类型D] 2026_easter_card_collection/      — 集卡册本地化
        └── localization.md   — 6+1 区域结构 + Key 命名规则 + 坑点汇总
```

> **类型C（装饰物）** 暂无独立 cases 目录，完整规则见 `reskin-rules.md §七`，内含 2026 复活节装饰典型案例。

做新活动换皮时，先读对应类型的 `overview.md` 对照 ID，再按需读各表 `.md` 文件。

装饰换皮完成后，使用 `reskin-rules.md` 中的 **QA 变更总结模板**整理变更发给测试。

---

## 四、收尾与导表

### 4.1 收尾步骤（每次完成后必做）

每次换皮+导表完成后，主动检查并更新以下文件，把本次遇到的新情况、新 ID 规律、新坑沉淀进去：

| 文件 | 更新内容 |
|------|---------|
| `config-library/cases/<节日>/overview.md` | 补充本次活动的 ID 对照表、关键决策 |
| `config-library/reskin-rules.md` | 补充新规则或特殊处理方式 |
| `skills/config-reskin/SKILL.md` | 更新工作流（新增步骤/注意项） |
| `skills/config-reskin/modules-p2.md` 或 `modules-x2.md` | 补充新表的大定义/子定义，或更新现有表的子定义（按项目分别更新） |
| `skills/P2-config-upload/SKILL.md` | 补充导表过程中遇到的新问题及解法 |

> 如果本次遇到了新问题（比如 GSheet 格式报错、tab 不对、ID 复用），一定要写进对应文件，不要等下次重踩。

### 4.2 导表注意事项（P2 导表）

换皮配置完成后，使用 `P2-config-upload` 技能导表。关键注意点：

- **已有行（updated）**：直接 `merge_rows.py` 按行 ID 替换，从 GSheet 重新拉取最新版本覆盖本地
- **新增行（added）**：`merge_rows.py` 只能处理 GSheet 里已有的行。若目标行尚未写入 GSheet，脚本会输出 `[WARN] not found anywhere`，此时需先让用户把行粘贴入 GSheet，再重新下载执行 merge
- 2135 等活动表的新行通常是换皮产出的全新 ID，用户需要先手动粘贴进 GSheet，才能走正常导表流程
