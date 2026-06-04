# Skill: 活动数值配置 & 换皮

读数值设计表 → 读配置表真实格式 → 生成配置行 → 写入 GSheet → 导表。
覆盖两类场景：**配活动**（同项目内根据数值表生成配置）和**换皮**（P2→X2 跨项目道具替换）。

## 触发条件

**配活动场景**：
- "配活动"、"配数值"、"配一下"、"生成配置"、"活动配置"
- 活动 ID + "配"（如"21127807 配一下"）
- 给了数值表链接 + 要求输出配置

**换皮场景**：
- "换皮"、"换皮数值"、"数值换皮"、"P2换皮"、"X2换皮"
- "P2→X2"、"P2 到 X2"
- 活动名 + "换皮"（如"巨猿换皮"、"大富翁换皮"）

## 前置动作（每次都执行）

```
读取配置表综合知识库（SheetID + 追踪链 + 字段 Schema）：
C:\ADHD_agent\.cursor\config-library\table-reference.md
```

---

## 一、核心换皮流程（S 步骤）

### S-1 确认项目（P2 / X2）

**每次接到任务，第一步必须确认是哪个项目。**

| 项目 | 查询工具别名后缀 | 示例 |
|------|--------------|------|
| **P2** | `_dev` / `_P2` | `2112_dev`, `1111_P2` |
| **X2** | `_x2_` | `2112_x2_activity_config` |

**判断依据**（按优先级）：
1. 用户明确说了项目名 → 直接确定
2. 给了 GSheet 链接 → 对照 table-reference.md 的 SheetID 判断
3. 任务上下文（P2导表流程 / X2导表流程）
4. 不确定 → **必须问清楚**

---

### S0 分析任务 → 命中模块

从任务语义出发，逐条过触发条件，命中的模块就是本次工作范围：

| 模块（表） | 何时需要 |
|-----------|---------|
| **2112 活动主体** | 有活动入口（玩家能在活动界面看到的东西）|
| **2115 活动任务** | 活动有「做 XX 得 YY」的任务机制 |
| **2135 活动礼包** | 活动中有礼包购买入口 |
| **2011 礼包规则** | 涉及 IAP 付费购买 |
| **2013 礼包内容模板** | 礼包需要道具组合模板（标准礼包；预购连锁不走）|
| **1111 道具定义** | 涉及新道具或需查道具属性 |
| **1118 建筑升级** | 有星级升级机制 |
| **2148 装饰等级** | 涉及装饰物的星级/属性/涂饰 |
| **2171 涂饰技能** | 装饰有涂饰功能 |
| **1127 放置解锁** | 新建筑/新装饰需在建造界面出现 |
| **1168 道具来源** | 需配置道具获取途径展示 |
| **1511 外显资产(DK)** | 有图标/模型需要展示 |
| **1011 本地化(LC)** | 有玩家可见的文字 |
| **2130 BP通行证** | 有 Battle Pass 活动 → 同时检查 2131(等级奖励) |
| **2141 无底Gacha奖池** | 有 Gacha 抽奖（主城皮肤gacha等）→ 通过 activity ID 关联，不在 components 里 |
| **2142 无底Gacha奖励** | 同上 → 注意页签可能带后缀（如"天赋投放活动"）|
| **2024 自选礼包坑位** | 有周卡/自选礼包 → 通过 2013 template_id 关联 |
| **2151 大富翁地图** | 有大富翁活动 → 可复用旧地图或新建 |
| **1365 行军特效外观** | 有新行军特效 → 克隆必须全列（19列）|
| **1187 家具/装饰放置** | 有装饰品 → 模型 ID 需美术提供 |
| **2122 排名→2011累充** | 累充排名的 score_rule.ids 必须包含当前节日所有 2011 ID |

> ⚠️ **间接引用必查清单**（不在 2112 components 里但换皮必须检查）：
> - 2121 行内 JSON：`expr`(wonder_egg_drop→2124)、`status`(discount→2011)、`array`(task_group→2115)
> - 2011 行内 JSON：`iap_status.drop`(随机礼包→2124)
> - 1111 行内 JSON：`category_param`(金蛋→2124、周卡解锁→2013)
> - 2013 行内 JSON：`pkg_title`(LC key 需换成新节日)

确认变更性质：

| 任务类型 | 说明 |
|---------|------|
| **纯换皮** | 结构不变，只换 ID/名称/图片/LC key |
| **换皮 + 新功能** | 新字段需另行确认结构；新道具/组件需同步触发对应模块 |
| **新功能评估** | 逐条过触发条件，输出模块清单 + 是否需要新表 |

---

### S1 读原始行

从用户给出的配置行（或 GSheet）中提取所有字段。对照 table-reference.md 中该表的字段说明，理解每个字段的角色。

---

### S2 按字段角色决定处理方式

| 字段类型 | 换皮处理 |
|---------|---------|
| `A_STR_constant` | **必须新增** — 不能复用 |
| `A_MAP_filter` | **一般不换** |
| 活动行 ID | **换** — 分配新 ID |
| 父活动/关联 ID | **换** |
| 前置条件建筑 ID | **换** |
| 本地化 LC key | **换** — 改为新主题前缀 |
| 内容引用（task/package ID）| **换** |
| Banner 图片路径 | **换** |
| `A_INT_show_hud` | **换** |
| 常量数值（0/1/空字符串/空数组）| **不换** |
| 规则 LC key（`rule` 字段）| 同类型活动**可不换** |
| 2119 关联 ID | 同类型活动**可不换** |

#### ⚠️ S2.5 外键 ID 验证（容易漏）

配置里凡是 `rewards`、`drop JSON`、`goods_id`、`category_param` 等字段中包含的 **item id**，换皮时容易被忽视。**必须对每一个外键 id 在 1111 表执行验证**：

```bash
# P2 项目
python gsheet_query.py row 1111_P2 {item_id}

# X2 项目
python gsheet_query.py row 1111_x2_item {item_id}
```

检查 `S_STR_comment` 和 `A_MAP_lc_name.txt` 是否含旧节日名称关键词：
- 命中 → 节日专属，**必须换**
- 未命中 → 通用道具，**保留**

> ⚠️ 先建清单，再逐一核查。没有跑过的 id 不能默认为正确。

---

### S3 追踪依赖链

**核心原则**：每层引用都要向下追踪，确保所有 ID 引用都指向新行。

```
2112
 ├── components.task → 2115 → fincond 内含 2013 ID
 ├── components.package → 2135 → col3 指向 2011 ID
 │                                 └── 2011.time_info.actv_id → 反向引用 2112
 │                                 └── 2011 ← 2013.config_id
 ├── components.weekly_pay_ratio / jump_link / task_group → 2121
 │                                 └── 2121.reward → 1111（若是自选箱，追 category_param.select_box）
 └── show_hud → 换新 ID
```

**关键联动规则（跨表 ID 必须同步）：**

| 场景 | 必须同步更新 |
|------|------------|
| 2011 ID 变了 | 2013 的 `config_id` + 2135 的 `iap` 字段都要改 |
| 2112 ID 变了（或复用旧 ID）| 2011 的 `actv_id` + 2135 chain row 的 `condition.actvstart.id` 都要改 |
| 2011 复用/新建后 | 检查 `A_ARR_iap_status.recharge_actv.id` 是否指向当前节日累充 |
| 道具 ID 变了 | 所有引用该道具的表（2115/2013/1127 等）都要改 |
| X2 `weekly_pay_ratio` | 追 `2121.reward → 1111`，若是 `item_select_box` 继续追 `category_param.select_box` |
| **集卡册换皮** | 见下方集卡册追踪链 |

**集卡册依赖追踪链：**
```
6001 (book)
 ├── A_ARR_group_id → 6002 (group)
 │    ├── A_ARR_card_id → 6003 (card) → col[2] A_INT_star 判断5★
 │    └── A_ARR_rewards → 每个 item id → 1111 验证节日归属 ⚠️
 └── A_ARR_rewards → 每个 item id → 1111 验证节日归属 ⚠️

6004 (集卡商店)
 └── goods_id → 指向当前节日保底卡包 ID → 每次换节日必须同步更新 ⚠️
```

---

### S4 输出完整配置行

> 进入 **五、输出规范** 执行输出。

---

### S5 写入 GSheet（checklist 确认后执行）

S4 输出完成后，**先跑检查、把 checklist 呈现给用户确认，用户说「写入」后才执行**。

#### S5.1 写入前检查（自动跑，结果呈现给用户）

对每张涉及的表依次执行：

```
1. 读 tab 列表，确认 QA tab 名
   gws sheets spreadsheets get --params '{"spreadsheetId":"<ID>","fields":"sheets.properties"}'

2. 读表头行，确认列数
   gws sheets spreadsheets values get --params '{"spreadsheetId":"<ID>","range":"<QA_TAB>!A1:AZ1"}'

3. 读参考行（同 ID 段最后 1 行），逐列比对格式
   — 重点检查：JSON 格式是否一致、末尾列是否有占位

4. 确认写入位置（同 ID 前缀末尾行号，不是表格末尾）
   — 2135 等有空行的表：扫描 B 列找到最后一个非空 ID
```

**输出 checklist（每张表一块，等用户确认）：**

```
─────────────────────────────────────
📋 写入前 Checklist — <表编号>(<表名>)
─────────────────────────────────────
目标 tab：<QA_TAB>               ← 请确认是 QA 而非线上
表头列数：<N> 列                  ✓
参考行 ID：<行ID>（第 <M> 行）
写入位置：第 <K> 行之后（共插 <N行> 行）

逐列比对：
  col[0] <字段名>  参考=<值>  生成=<值>  ✓/⚠️
  col[1] <字段名>  参考=<值>  生成=<值>  ✓/⚠️
  ...（有差异的列单独标 ⚠️ 并说明原因）

待写入行 ID 范围：<起始ID> – <结束ID>
─────────────────────────────────────
✅ 全部通过 / ⚠️ 有异常项需说明

确认写入请回复「写入」，如有问题请说明。
```

⛔ **checklist 输出后停止，等用户回复「写入」才继续 S5.2。**

#### S5.2 执行写入（用户确认后）

```bash
# Step 1：插入空行
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"<ID>"}' --json '{
  "requests": [{
    "insertDimension": {
      "range": {"sheetId":<GID>,"dimension":"ROWS",
                "startIndex":<行号>,"endIndex":<行号+N>},
      "inheritFromBefore": false
    }
  }]
}'

# Step 2：写入数据（RAW mode，不解析公式）
gws sheets spreadsheets values batchUpdate \
  --params '{"spreadsheetId":"<ID>","valueInputOption":"RAW"}' \
  --json '{"data":[{"range":"<QA_TAB>!A<行号>:<末列>","values":[...]}]}'
```

**工程注意：**
- JSON body 超 ~5KB 时分批，单批 ≤ 5 复杂行
- 双引号字段直接传 `"\""` （不是 `'""` ，那是 TSV 粘贴专用）
- A 列空的表用明确 range，不用 append（防列偏移）
- TLS 偶发失败加指数重试（1→2→4→8s），不因 stderr 有报错就放弃

#### S5.3 写入后验证（必做）

```
1. 行数：读回写入区域，确认 N 行都在
2. 行顺序：读前后各 3 行 ID，确认递增连续
3. 列完整性：列数 = 表头列数，末尾空列有占位
4. 抽查 JSON：至少 1 行核对关键字段内容
5. 换皮场景：全表搜索旧 ID 残留（如旧 recharge_actv）
```

**输出格式：**
```
✅ <表编号>(<QA_TAB>) 写入完成
新增 N 行：ID <起始>–<结束>
验证：行数 ✓ / 行顺序 ✓ / 列完整性 ✓ / JSON ✓
```

---

## 二、已知组装模式速查

> 新任务应先走 S0 触发条件，而非直接对号入座。

| 组装模式 | 命中模块 | 典型案例 | 专项规则 |
|---------|---------|---------|---------|
| **普通活动礼包** | 2112 + 2115 + 2135 + 2013 + 2011 + 1011 + 1511 | 2026异族大富翁每日礼包 | — |
| **预购连锁礼包** | 2112 + 2135 + 2011 + 1011 + 1511（跳过 2013）| 2026复活节预购连锁 | reskin-rules.md §三 |
| **装饰物** | 1111 + 1118 + 1127 + 2148 + 2171 + 1168 + 1011 + 1511 + **1187** | 2026复活节装饰 | reskin-rules.md §七；1187 需要模型 ID |
| **集卡册** | 1111(卡包道具) + 6001 + 6002 + 6003 + 6004 + 1011 + 2112 | 21127803/21127804 已固定复用 | `card-collection-config` 技能；2112 复用无需新建 |
| **机甲累充** | 2112 + 2115(11档) + 2121(jump_link) + 1111 | 2026复活节机甲累充 | 主奖是节日玩法货币（不是喷漆）；每节日换货币道具 ID |
| **多条件连锁礼包** | 2115(仅改 reward) — 2112 **整行复用不改** | 2026复活节连锁任务 | 只替换节日绑定道具；2115 ID 在 col[1]，查询加 `--id-col 1` |
| **主城皮肤 Gacha** | 2112 + 2121(5组件) + 2124(外圈drop) + 2135→2011→2013 + **2141 + 2142** + 2137 + 1111 | 2026占星节/拓荒节 gacha | 2141 通过 activity ID 关联；2142 注意页签名可能带后缀（天赋投放活动）；2011.iap_status.drop 引用随机礼包奖池 2124 |
| **自选周卡** | 2112 + 2135→2011→2013 + **2024**(自选坑位) + 1111(subscription道具) | 2026占星节/拓荒节周卡 | 2024 通过 2013 template_id 关联；1111 subscription 的 category_param.effect 指向 2013 ID |
| **Wonder 砸金蛋** | 2112 + 2121(15组件) + 2115(7金蛋任务+15积分任务) + 2124(14掉落) + 2135→2011→2013 + 2122 + 1111(金蛋道具) | 2026拓荒节 Wonder | 2121.wonder_egg_drop.expr 引用 2124；task_group.array 引用 2115；1111 金蛋 category_param 引用 2124 |
| **BP 通行证** | 2112 + **2130 + 2131**(25级) + 2121 + 2122→**2118**(排名奖励) + 2137 + **1365**(行军特效) + 1111 | 2026拓荒节 BP | 2130 引用 1111 通行证道具；2131 reward 含节日道具；2122 score_rule 需包含所有节日 2011 ID；1365 全列克隆(19列) |
| **节日累充** | 2112 + 2115(档位任务) + 2121(跳转+大乐透+show_rank) + **2122**(score_rule含全部2011) + 2137 | 2026拓荒节累充 | 2122.score_rule.ids 必须包含当前节日所有 2011 ID；每新增 2011 都要加 |
| **掉落转付费** | 2112×3 + 2116(兑换) + 2121(discount→2011) | 2026拓荒节掉落转付费 | discount 的 status 引用 2011 IAP，需新建 2011+2013；2124/2121(progress)/2137 可复用旧行 |
| **大富翁** | 2112 + 2135(17礼包) + 2011 + 2013 + 2115 + 2116(兑换) + 2121 + **2151**(地图) | 2026拓荒节大富翁 | 2151 地图可复用旧的；1111 骰子道具通用不换 |

---

## 三、场景A：配活动（同项目）

### A1 收集输入

| 信息 | 必须 | 说明 |
|------|:---:|------|
| 数值表 URL | ✓ | Google Sheet 链接（含 gid）|
| 活动 ID | ✓ | 2112 表的活动 ID |
| 活动名/注释 | ✓ | 用于配置行注释 |

### A2 读数值表，理解活动结构

```bash
# 获取页签列表
gws sheets spreadsheets get --params '{"spreadsheetId":"<ID>","fields":"sheets.properties"}'

# 读取数值页签
gws sheets spreadsheets values get --params '{"spreadsheetId":"<ID>","range":"<页签>!A1:Z300"}'
```

从数值表提取：活动类型、涉及配置表清单、每格/每级的道具 ID/数量/权重/价值。

### A3 → 执行 S0–S5

确认活动类型后，按 S0 命中模块，走 S1→S2→S3→S4→S5 完整流程。

### A4 案例沉淀

配置完成后，在 `C:\ADHD_agent\.cursor\config-library\cases\{年份}_{节日}_{活动类型}\` 下存档。**以下三类文件每次都必须生成，缺一不可：**

| 文件 | 输出路径 | 用途 | 内容规范 |
|------|---------|------|---------|
| `overview.md` | `config-library/cases/{节日}/` | 活动总览 | ID 对照总表（旧ID→新ID）+ 待填字段清单 + 关键决策说明 |
| `{表号}.md`（每张涉及的表一个）| `config-library/cases/{节日}/` | **Agent 读** — 机器检索、后续换皮引用、bug-fix agent 默认查找路径 | 完整 TSV 行（代码块）+ ID 范围 + 关联 ID + 固定字段说明 |
| `{项目}_{年份节日}_{活动类型}[_{用途}].html` | `KB/产出-配置生成/`（平铺，无子目录）| **人读** — 可视化 debug，排查字段问题时打开 | 所有涉及表的配置行，按表分 section，支持搜索 |

**HTML 命名规则**：`{项目}_{年份节日}_{活动类型}.html`，同一活动有多个功能不同的 HTML 时才加后缀（`_填写表` / `_LC确认` 等）。
示例：`X2_2026拓荒节_弹珠Gacha.html`、`X2_2026占星节_集卡册.html`、`P2_机甲皮肤_巨象丛林.html`

⚠️ **版本管理规则：同名文件直接覆盖，不保留中间产物。** 配置过程中产生的草稿/预览版不得用不同文件名存档，更新时用相同文件名覆盖即为新版。

> ⚠️ 两条路径职责不同，不能互替：
> - **查 BUG（人工）** → `KB/产出-配置生成/` 按文件名找对应 HTML
> - **查配置数据（Agent）** → `config-library/cases/{节日}/{表号}.md`

---

## 四、场景B：P2→X2 换皮

### B1 收集输入

| 信息 | 必须 | 说明 |
|------|:---:|------|
| P2 数值表 URL | ✓ | Google Sheet 链接（含 gid）|
| 目标节日名 | ✓ | X2 的节日名称 |
| BP 道具 ID | ✓ | 目标节日的 BP 道具 ID |

**不要一次问完所有信息。** 先问 P2 数值表 URL，读完再追问。

### B2 读 P2 数值 + 核实 X2 道具

```bash
# 读 P2 数值表
gws sheets spreadsheets values get --params '{"spreadsheetId":"<ID>","range":"<页签>!A1:AB200"}'

# 核实 X2 1111 道具表
gws sheets spreadsheets values get \
  --params '{"spreadsheetId":"1pm0nztHsjpHmFBEmx-bLtP7Zjf4GFC67wo-sUmqY7Fs","range":"item!A1:B3233"}'
```

道具分类结果：
- **直接沿用**：X2 存在且无需替换
- **需要替换/讨论**：替换原因 + 推荐替代品 + 单价对比 + 历史案例参考

**道具判断参考（reskin-numerical-framework.md）：**
- 游戏系统道具（研究药水/加速/资源箱等）→ 沿用
- 节日品牌道具（装饰物/涂饰/BP积分/卡包）→ 换 ID
- 变现侧参数（价格/ROI/连锁结构）→ 不改

### B3 提出替换方案，等用户确认

⛔ **用户明确确认之前，不得进入 B4。**

### B4 → 执行 S1–S5

用确认后的方案走 S1→S2→S3→S4→S5 完整流程。

### B5 案例沉淀

生成以下三类文件（同 A4，缺一不可）：
- `config-library/cases/{节日}/{表号}.md` — Agent 读，每张表的完整 TSV 行
- `KB/产出-配置生成/{节日}/config-output.html` — 人读，可视化 debug 入口
- `config-library/cases/{节日}/reskin-log.md` — 换皮决策记录

```markdown
# {节日} {活动类型} 换皮记录

- 日期：{YYYY-MM-DD}
- P2 源表：{Sheet URL}
- 活动类型：{类型}
- 目标节日：{节日名}

## 替换决策

| # | P2 道具 | P2 ID | → X2 道具 | X2 ID | 原因 |
|---|---------|-------|---------|-------|------|

## 价值影响

- P2 ROI：{X}x → X2 ROI：{X}x
```

---

## 五、输出规范

### 5.1 TSV 输出格式铁律

> **所有配置行必须输出为可一键复制粘贴进 Google Sheets 的完整 TSV 行。**

- ✅ 每张表一个代码块，每行包含所有列，Tab 分隔
- ✅ 新增行与覆盖行都给完整行，不允许省略任何列
- ✅ 所有单独成格的 `""` 字段输出为 `'""` （Sheets 粘贴规则，API 写入不需要）
- ❌ 禁止输出"把 X 替换为 Y"的说明表
- ❌ 禁止只输出变更的字段

### 5.2 本地化检查清单（每次必做）

| 检查项 | 在哪里 | 输出内容 |
|---|---|---|
| **活动标题/描述 LC key** | 2112 主活动行 col7 | 完整替换后的 2112 整行 |
| **活动规则 LC key** | 2112 主活动行 col9 | 同上 |
| **礼包标题 LC key** | 2013 模板 `pkg_title` 列 | 完整替换后的 2013 各行 |
| **新道具名/描述 LC key** | 道具表 + 道具行本身引用 | 道具行完整更新行 + LC key 文本汇总 |
| **集卡册卡包描述正文** | 本地化页签 Col K-L，R2-R25 | 逐行确认游戏名已换成当前节日 |

> ⚠️ 集卡册换节日时，不能只批量替换 Key 前缀——Col K/L 描述正文里的具体游戏名（如"寻找破译器"）也要逐行核对。

道具行额外检查：
- `actv_open` effect 列表是否需要追加新活动 ID
- LC key 前缀是否需要从旧活动换成新活动

### 5.3 LC Key 文本汇总格式

标准四列格式（LC_KEY / key / 中文 / 英文）：

```
LC_ITEM_xxx_name	xxx_name	道具名称中文	Item Name EN
LC_ITEM_xxx_desc	xxx_desc	道具描述中文	Item description EN.
LC_ITEM_xxx_paint_name	xxx_paint_name	"道具名"粉刷	"Item Name" Paint
LC_ITEM_xxx_paint_desc	xxx_paint_desc	使用后可激活"道具名"装饰物带来的增益状态。	Activate the buff provided by the "Item Name" decoration upon use.
```

固定句式：
- 涂饰描述中文：`使用后可激活"{装饰名}"装饰物带来的增益状态。`
- 涂饰描述英文：`Activate the buff provided by the "{Decoration Name}" decoration upon use.`
- 升级道具描述中文：`{描述}。首次获得可以解锁{装饰名}，后续获得可用于升级{装饰名}。`
- 升级道具描述英文：`{desc}. The first one unlocks the {Decoration Name} decoration; additional ones can be used to upgrade it.`

---

## 六、工具与资源

### 6.1 配置表查询工具（gsheet_query.py）

**工具位置**：`C:\ADHD_agent\.cursor\skills\google-workspace-cli\gsheet_query.py`

```bash
# ── P2 项目（用 _dev / _P2 后缀） ──
python gsheet_query.py headers  2112_dev
python gsheet_query.py search   2112_dev 复活节
python gsheet_query.py row      2112_dev 21127284

# ── X2 项目 ──
python gsheet_query.py headers  2112_x2_activity_config
python gsheet_query.py search   2112_x2_activity_config 复活节

# ── 通用操作 ──
python gsheet_query.py idrange  1168_dev 11684847 11684874
python gsheet_query.py tail     2171_dev 10
python gsheet_query.py filter   2148_dev 5 0 --not
python gsheet_query.py tabs     2112_dev
```

**P2 内置别名：**

| 别名 | 说明 |
|------|------|
| `1111_P2` | 道具表 |
| `1118_dev` | 建筑升级表（装饰星级）|
| `1168_dev` | 道具来源/获取途径表 |
| `1511_dev` | display_key 视觉资源表 |
| `2148_dev` | 装饰物等级表 |
| `2171_dev` | 装饰涂饰技能表 |
| `2011_dev` | 礼包规则表 |
| `2013_dev` | 礼包内容模板表 |
| `2112_dev` | 活动主体表 |
| `2115_dev` | 活动任务表 |
| `2135_dev` | 活动礼包表 |

**表特殊参数（踩坑记录）：**

| 表 | 注意事项 |
|----|---------|
| `2115` | **ID 在 col[1]**（col[0] 是 group），查询须加 `--id-col 1` |
| `1118` | P2 页签名含「不要直接修改」，X2 含「严禁手改」|
| `2135` | P2 默认页签 `activity_event_pkg`；X2 默认页签带 `(qa)` |

```bash
# 2115 特殊用法
python gsheet_query.py idrange 2115_dev 211560390 211560483 --id-col 1
python gsheet_query.py row     2115_dev 211552010 --id-col 1
```

### 6.2 配置资源库

```
C:\ADHD_agent\.cursor\config-library\
├── table-reference.md     — SheetID + 追踪链 + 字段 Schema（综合字典）
├── reskin-rules.md        — 换皮操作规则（§三=预购连锁, §六=图标BUG, §七=装饰物）
├── reskin-numerical-framework.md — P2→X2 数值决策框架
└── cases\
    ├── 2026_alien_monopoly_daily_pack\   — 普通活动礼包
    ├── 2026_easter_pre_chain\            — 预购连锁礼包
    ├── 2026_easter_card_collection\      — 集卡册本地化
    └── 2026_pioneer_marble_gacha\        — 弹珠Gacha
```

### 6.3 关键参考 SheetID

| 资料 | SheetID / 路径 |
|------|--------------|
| X2 1111 道具表 | `1pm0nztHsjpHmFBEmx-bLtP7Zjf4GFC67wo-sUmqY7Fs` |
| X2 付费价值表 | `1aV8VL-81C_VDQfzBhTvqiRbQUOGQuvV3WrcFrk2z3UU` |
| P2 养成线手册 | `C:\ADHD_agent\.cursor\p2-numerical-design\养成线深度手册.md` |
| X2 养成线手册 | `C:\ADHD_agent\.cursor\x2-numerical-design\养成线深度手册.md` |

---

## 七、节日集卡册换皮专项

每次节日集卡册换皮时，以下步骤**必须**操作：

### 2112 + 2121 的 fes_card_gallary

新建活动行时，`constant` 加节日后缀（如 `_labor`），`fes_card_gallary` 组件引用新 2121 ID。

**2121 fes_card_gallary 必须更新的两个字段：**

| 列名 | 字段 | 说明 | 踩坑案例 |
|------|------|------|---------|
| `A_INT_arg1` | col[5] | 节日专属 `6001x` ID | 拓荒节(21217586) 沿用了复活节的 `60011005` |
| `A_ARR_array` | col[10] | 节日专属 `6004x` ID 数组 | 拓荒节(21217586) 沿用了 `[60040036~40]` |

历史 arg1 对照：
- 通用版 21217583 → `60011004`
- 复活节 21217584 → `60011005`
- 拓荒节 21217586 → 应为新 6001x ID（**未配导致集卡册内容未触发**）

### 三合一礼包冲突

2112 的三合一礼包活动（`event_fes_card_packgae_labor`）和通用版（`event_fes_card_packgae`）会引用相同 2135 package ID，**两个活动不能同时上线**，否则礼包冲突无法触发。

---

## 八、收尾与导表

### 8.1 收尾步骤（每次完成后必做）

| 文件 | 更新内容 |
|------|---------|
| `config-library/cases/<节日>/overview.md` | 补充本次活动的 ID 对照表、关键决策 |
| `config-library/reskin-rules.md` | 补充新规则或特殊处理方式 |
| `~/.claude/skills/p2-x2-reskin/SKILL.md` | 更新工作流（新增步骤/注意项）|
| `P2-config-upload/SKILL.md` | 补充导表过程中遇到的新问题 |

### 8.2 导表注意事项

换皮配置完成后，使用 `P2-config-upload` 技能导表：

- **已有行**：`merge_rows.py` 按行 ID 替换，从 GSheet 重新拉取覆盖本地
- **新增行**：`merge_rows.py` 只能处理 GSheet 里已有的行。GSheet 写入（S5）完成后才能走导表流程
- 2135 等活动表的新行必须先完成 S5 写入，再触发导表

---

## 九、历史案例索引

| 日期 | 节日 | 类型 | 场景 | 案例路径 |
|------|------|------|------|---------|
| 2026-04-16 | 占星节 | 巨猿金蛋 | 换皮 | `cases/2026_astrology_giant_ape/` |
| 2026-04-20 | 节日通用 | 机甲金字塔gacha | 配活动 | — |
| 2026-04-28 | 拓荒节 | 节日集卡册 | BUG复盘 | 2121 arg1+array 未换，三合一包与通用版冲突 |
