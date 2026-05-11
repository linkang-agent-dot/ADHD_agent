---
name: config-bugfix
description: >-
  游戏配置类 BUG 的修复工具（仅修复，巡检由 Windows 定时任务 ClaudeBugScan 负责）。
  触发场景：用户说"改BUG"、"修BUG"、"修 P2DEV-xxxxx"、"修 X2-xxxxx"、给出 Jira BUG 编号、
  说"配置修复"、"config bugfix"、"开始干"、"继续干"时使用。
  也适用于：用户提到"Jira"+"BUG"+"修"、"配置表"+"问题"、"翻译缺失"、"LC key"、"导表"等关键词组合。
  不触发：用户只说"查BUG"、"巡检"、"BUG巡检"、"看看有啥BUG"时，不触发此 skill，巡检结果直接看 _my_bugs_summary.txt。
---

# 配置 BUG 修复工具

## 🚨 强制规则（每次执行前默念一遍）

### R1: 操作前必须用户确认
**所有 Jira/Google Sheet 写操作前，先列方案等用户说 OK 再动手。**
包括：写入 Sheet、加 Jira 评论、转派、关闭、改状态。
唯一例外：用户明确说"直接改"、"都做"、"冲"。

### R2: 翻译暂存区写入前确认目标页签
从 BUG 截图中 raw key 推断：
- `LC_minigame_xxx` → minigame
- `LC_EVENT_xxx` → EVENT
- `LC_ITEM_xxx` → ITEM
**不要默认 EVENT**，先问用户。

### R3: 处理完必须双沉淀
无论修好/转派/搁置，都要更新：
1. **配置知识库** `C:\ADHD_agent\.cursor\config-library\table-index.md`
2. **运维文档** `C:\ADHD_agent\docs\ops_auto_bugfix.md`
未沉淀 = 未完成。

### R4: 翻译走 skill，不手写
翻译类 BUG 必须调用 `/game-localization-translator`，不要在代码中手写 18 语言。

### R5: 规则文案要策划案
活动规则不能猜。读老规则 → 让用户给策划案 → 写新规则 → 用户确认措辞 → 翻译 skill。

### R6: 说人话
每个 BUG 给一句大白话概括（"机甲抽奖打死怪不掉东西"），不堆表编号和字段名。
技术细节放在概括下面的详情里。

---

## 关联知识库

本 skill 的 `references/` 目录包含两份核心知识文档的**副本**，方便快速参考：

| 文件 | 内容 | 何时读 |
|------|------|--------|
| [references/table-index.md](references/table-index.md) | 配置表知识库：表编号→SheetID 索引、字段含义、追踪链、已知活动/道具 ID | 修 BUG 时查表用 |
| [references/ops_auto_bugfix.md](references/ops_auto_bugfix.md) | 运维文档：强制规则、检查清单、Review 问题记录、历史修复记录 | 每次启动先读 |

**注意**：这两份是副本，**活文档在原始路径**：
- 配置知识库原件：`C:\ADHD_agent\.cursor\config-library\table-index.md`
- 运维文档原件：`C:\ADHD_agent\docs\ops_auto_bugfix.md`

沉淀时（R3）**更新原件**，副本作为参考不保证实时同步。如果发现副本和原件不一致，以原件为准。

## 启动检查

每次触发本 skill 时，**两步启动**：

**第一步：读运维文档**
```
Read C:\ADHD_agent\docs\ops_auto_bugfix.md
```
如果读不到原件，降级读 `references/ops_auto_bugfix.md`。

**第二步：刷新本地缓存**（每个 session 首次触发时执行一次）
```bash
python "C:/ADHD_agent/.agents/skills/config-bugfix/scripts/refresh_cache.py"
```
从 `fw_gsheet_config` 索引表获取全部 591 张表的 SheetID 映射，并下载 7 张常用表到 `C:/Users/linkang/_config_cache/`（约 6 秒）。
后续所有查询用本地缓存，不再调 API，**单次查询从 ~12000 token 降到 ~330 token，省 95%+**。

## 本地缓存查询（替代 Google Sheets API）

### 查缓存状态
```bash
python "C:/ADHD_agent/.agents/skills/config-bugfix/scripts/query_cache.py" --list
```

### 按 ID 精确查（~330 token，替代 API 的 ~12000 token）
```bash
python "C:/ADHD_agent/.agents/skills/config-bugfix/scripts/query_cache.py" 1111 11112175
```

### 按关键词模糊搜
```bash
python "C:/ADHD_agent/.agents/skills/config-bugfix/scripts/query_cache.py" 2121 --search "floor_gacha"
```

### 按指定列搜索
```bash
python "C:/ADHD_agent/.agents/skills/config-bugfix/scripts/query_cache.py" 1111 --col 2 "floor_gacha"
```

### 查索引（591 张表的 SheetID 全在本地）
```bash
# 列出所有表（[C]=已缓存）
python query_cache.py --index
# 精确查一张表的 SheetID
python query_cache.py --index 2116
# 模糊搜表名
python query_cache.py --index coinpush
```

### 按需下载未缓存的表
```bash
# 发现 2116 没缓存，单独拉一张
python refresh_cache.py 2116
```

### 直接读 JSON（最省 token，适合复杂查询）
```python
import json
with open("C:/Users/linkang/_config_cache/1111.json", "r", encoding="utf-8") as f:
    data = json.load(f)
# data["header"] = 表头, data["rows"] = 数据行（不含表头）
for row in data["rows"]:
    if row[0] == "11112175":
        print(row)
```

### Token 开销对比

| 操作 | API 方式 | 本地缓存 | 节省 |
|------|---------|---------|------|
| 单次查询 | ~12000 token | ~330 token | 97% |
| 单个 BUG（查 4 次） | ~50000 token | ~1300 token | 97% |
| 一天处理 5 个 BUG | ~250000 token | ~6500 token | 97% |
| 缓存刷新（一次性） | — | ~2000 token | — |

### 默认缓存的 7 张高频表
| 编号 | 名称 | 行数 |
|------|------|------|
| 1111 | item（道具）| ~3200 |
| 2111 | activity_calendar | ~2000 |
| 2112 | activity_config | ~1900 |
| 2115 | activity_task | ~12500 |
| 2121 | activity_special | ~3300 |
| 2154 | activity_without_gacha_floor | ~460 |
| 2182 | coinpusher | ~10 |

### 索引覆盖全部 591 张表
即使没缓存的表，也能通过 `--index` 查到 SheetID，再按需 `refresh_cache.py <表编号>` 单独拉。

### 什么时候还是要用 Sheets API
- **写入**（修改配置值）→ 必须在线改
- **缓存过期**（别人改了表且影响当前 BUG）→ `refresh_cache.py` 或 `refresh_cache.py <表编号>`
- 用户说 "刷新缓存" → 重跑 `refresh_cache.py`

---

## 巡检与修复的分工

巡检已拆到独立的 Windows 定时任务，不在本 skill 中：
- **巡检 Agent**：Windows Task Scheduler `ClaudeBugScan`，工作日 9:23-20:23 每小时自动跑
  - 脚本：`C:\Users\linkang\.claude\scripts\bug_scan.ps1` → `claude -p` 非交互模式
  - 产出：`C:\Users\linkang\_my_bugs_summary.txt`（当前 BUG 快照）、`_bug_scan_log.txt`（日志）、`_bugs_to_fix.txt`（待修配置类清单）
  - 只读不改，零上下文积累，每次 ~$0.5

当用户说"查BUG"、"看看有啥BUG"时，直接读 `_my_bugs_summary.txt` 展示即可，不需要调 Jira API。

---

## 修复流程（用户说"改 P2DEV-xxxxx/修这个/开始干"）

### 步骤

1. **拉详情** — Jira API 获取标题、描述、评论、截图
2. **分类** — 判断 BUG 类型（见下方分类表）
3. **追踪配置（参考什么）**：
   - **第一步读知识库** — `Read C:\ADHD_agent\.cursor\config-library\table-index.md`
     - 查 SheetID（知道去哪个 Google Sheet 找数据）
     - 查已有的追踪链（比如活动 ID → 哪些子表会用到）
     - 查字段含义（比如 `display_labels` 控制背包、`use_now` 控制即时使用）
     - 查已知的活动/道具 ID（比如新版机甲 21127807、惊喜锤 11112175）
   - **第二步读运维文档** — `Read C:\ADHD_agent\docs\ops_auto_bugfix.md`
     - 查历史记录（同类 BUG 之前怎么修的，直接复用思路）
     - 查 Review 问题记录（别重蹈覆辙）
   - **第三步查配置表** — 用 Google Sheets API 按追踪链逐表查
     - 从 BUG 截图/标题定位涉及哪个活动 → 查 2112 找 activity_id
     - 从 activity_id 向下追踪子表（2111 日历 / 2115 任务 / 2121 特殊参数 / 2154 爬塔 / 2135 礼包）
     - 从道具名/截图 → 查 1111 找道具 ID 和字段
     - 从 raw LC key → 查 i18n 表看翻译是否存在
4. **展示查询结果** → ⚠️ 等用户确认（R1）
   - 用大白话说"我查到了什么"
   - 列出涉及的表、行 ID、当前值
5. **提修复方案** → ⚠️ 等用户确认（R1）
   - 明确说"改哪个表、哪一行、哪个字段、从什么改成什么"
   - 翻译类还要确认目标页签（R2）
6. **执行修改**：
   - 翻译类 → 调 `/game-localization-translator`（R4）
   - 配置类 → Google Sheets API 直接改
   - 导表类 → 调 P2-config-upload skill
7. **展示结果** → ⚠️ 等用户确认 Jira 操作（R1）
8. **Jira 操作** — 评论/转派（用户确认后）
9. **双沉淀（怎么沉淀）**：

### 沉淀详细说明（R3 展开）

每个 BUG 处理完后，**必须做以下两件事**再算完：

#### 沉淀 1：更新配置知识库 `table-index.md`

**路径**：`C:\ADHD_agent\.cursor\config-library\table-index.md`
**沉淀什么**（根据本次处理中新发现的信息）：

| 发现了什么新东西 | 沉淀到哪里 | 举例 |
|-----------------|-----------|------|
| 新的表编号/SheetID | 表编号索引 + SheetID 索引 | 2154 SheetID 首次发现 |
| 新的活动 ID | 对应活动的"关键信息"段 | 新版机甲 21127807 |
| 新的道具 ID / display_key | 对应活动的"关键信息"段 | 惊喜锤 11112175 / dk 15119532 |
| 新的字段含义 | "1111 常用字段"等字段说明段 | display_labels 控制背包 |
| 新的配置追踪链 | 追踪链章节 | 2154 的 use_item 告诉你每层用什么道具 |
| 新的 LC key 命名约定 | 对应模块的命名约定段 | 推币机 key = `coin_pusher_xxx` |
| 新发现的"图标一致性检查点" | 图标一致性章节 | HUD/按钮/礼包三处要查 |

**判断标准**：如果这个信息下次遇到同类 BUG 时能帮你跳过搜索直接用，就值得沉淀。

#### 沉淀 2：更新运维文档 `ops_auto_bugfix.md`

**路径**：`C:\ADHD_agent\docs\ops_auto_bugfix.md`
**沉淀什么**：

| 要更新的位置 | 内容 |
|-------------|------|
| **历史记录表** | 追加一行：BUG 编号 + 做了什么操作 + 当前状态（✅/转派/搁置） |
| **Review 问题记录**（如果踩了新坑）| 场景 + 问题 + 正确做法 + Why |
| **当前未解决列表** | 更新剩余 BUG 编号 |

#### 沉淀示例

比如修完"福利弹珠进了背包"（P2DEV-141613）后：

**table-index.md 加了**：
```
1111 背包显示控制：
- C_ARR_display_labels 和 A_ARR_use_labels 两个都要改，缺一不可
```

**ops_auto_bugfix.md 加了**：
```
| P2DEV-141613 | 1111 item 111111017 去掉 bag 标签 → bugfix 推送 | ✅ |
```

如果还踩了新坑（比如发现写暂存区没确认页签），则在 Review 问题记录里加一条。

### Jira API 模板

```python
# 评论
url = f'https://jira.tap4fun.com/rest/api/2/issue/{KEY}/comment'
body = json.dumps({'body': '...'}).encode('utf-8')
# POST + Content-Type: application/json

# 转派
url = f'https://jira.tap4fun.com/rest/api/2/issue/{KEY}/assignee'
body = json.dumps({'name': 'username'}).encode('utf-8')
# PUT + Content-Type: application/json

# 查用户
url = f'https://jira.tap4fun.com/rest/api/2/user/search?username=xxx'
```

### Google Sheets API 连接

```python
import subprocess, json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

result = subprocess.run(
    ['gws', 'auth', 'export', '--unmasked'],
    capture_output=True, text=True, encoding='utf-8', shell=True
)
creds_data = json.loads(result.stdout.strip())
credentials = Credentials(
    token=None,
    refresh_token=creds_data['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret'],
    scopes=['https://www.googleapis.com/auth/spreadsheets'],
)
sheets_api = build('sheets', 'v4', credentials=credentials).spreadsheets()
```

---

## BUG 分类判断

根据标题关键词 + 截图快速分类：

| 关键词 | 类型 | 能自动修吗 |
|--------|------|-----------|
| 显示键值、显示英文、LC_、key | LC 翻译缺失 | ✅ 用翻译 skill |
| 图标不一致、图标反了 | icon 配置 | ✅ 改 display_key |
| 无法开启、后台开不了 | 缺 2111 行 | ✅ 追加行 |
| 规则、说明、文案 | 规则文案 | ✅ 但需策划案（R5） |
| 字段值、数值、触发条件 | 配置数值 | ✅ 改对应表字段 |
| 未替换、需替换 | 等新数值 | ⏳ 等策划给值 |
| 进度、判断、跳转、逻辑 | 代码 BUG | ❌ 转派程序 |
| 背景图、banner、资源 | 美术资源 | ❌ 等新图 |
| 交互、UX | 交互问题 | ❌ 需策划方案 |

---

## 配置表速查

### 常用表 SheetID

| 编号 | 名称 | SheetID | QA 页签 |
|------|------|---------|---------|
| 1111 | item（道具） | `1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws` | `item` |
| 2011 | iap_config | `1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc` | — |
| 2111 | activity_calendar | `1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g` | `activity_calendar_QA` |
| 2112 | activity_config | `1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E` | `activity_config_qa` |
| 2115 | activity_task | `1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY` | `activity_task_QA` |
| 2116 | activity_item_exchange | — | — |
| 2118 | activity_rank_rewards | `1Nb23s9iVOiDzWGQlpHSRW5O0gIqd1ZiYNx9kYrDps2M` | — |
| 2121 | activity_special | `1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc` | `activity_special_QA` |
| 2135 | activity_package | `1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc` | — |
| 2154 | activity_without_gacha_floor | `1XfENodZsKFH-hit2TWrxt8mmJSPqnn8qM2Cv2iIl2vo` | `activity_without_gacha_floor` |
| i18n | P2 翻译表 | `11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY` | 多页签 |
| i18n (X2) | X2 翻译表 | `1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg` | 暂存=`AI翻译页签` |
| X2 索引 | X2 fw_gsheet_config | `1z2-AK4dFgdzd7U11uCgYzLpj3Qopkv9Rr-SbA7iLIMc` | `fw_gsheet_config` |

### 配置追踪链

```
2112 activity_config (活动总配置，找 activity_id)
 ├── 2111 activity_calendar (日历，后台开启)
 ├── 2115 activity_task (任务，阶段奖励条件)
 ├── 2116 activity_item_exchange (兑换商店)
 ├── 2121 activity_special (特殊参数，如爬塔升层)
 ├── 2135 activity_package (礼包)
 └── 2154 activity_without_gacha_floor (爬塔层数配置)

1111 item (道具表)
 ├── C_INT_display_key → 图标
 ├── A_MAP_lc_name → 翻译 key
 ├── C_ARR_display_labels → 背包分类显示
 ├── A_ARR_use_labels → 背包使用标签
 └── S_INT_use_now → 获得即用（1=是）
```

### 1111 道具表关键字段

| 字段 | 含义 |
|------|------|
| `C_ARR_display_labels` | 背包显示分类，`["bag_other"]` = 在背包显示 |
| `A_ARR_use_labels` | 使用标签，`["bag"]` = 背包可见 |
| `S_INT_use_now` | 1 = 获得后立即使用 |
| `C_INT_display_key` | 图标引用 ID |

**不进背包** = `display_labels` 和 `use_labels` 两个都要清空，缺一不可。

### LC key 页签推断

游戏代码引用 `LC_<tab>_<key>`，i18n 表的 ID 列存 `<key>`（不含前缀）：
- `LC_minigame_coin_pusher_xxx` → 存在 **minigame** 页签，ID 为 `coin_pusher_xxx`
- `LC_EVENT_2025anni_xxx` → 存在 **EVENT** 页签，ID 为 `2025anni_xxx`
- `LC_ITEM_mecha_gacha_item` → 存在 **ITEM** 页签，ID 为 `mecha_gacha_item`

推币机 key 风格：`coin_pusher_xxx`（不加 minigame_ 前缀）。

---

## 导表流程（简化版）

修改 Google Sheet 后需要导表到 gdconfig 仓库：

1. 切分支：`git -C C:/gdconfig checkout -q bugfix && git -C C:/gdconfig pull -q`
2. 下载：`echo "1\n<表编号>\nn" | GSheetDownloader.exe`
3. 校验：日志末尾 `成功: N, 失败: 0`，无 `json error`
4. 查 diff：`git -C C:/gdconfig diff --stat`
5. 提交推送（⚠️ 需用户确认 R1）

详细流程见 P2-config-upload skill。

---

## 更多参考

- **完整运维文档**（含历史记录、所有踩坑点）：`C:\ADHD_agent\docs\ops_auto_bugfix.md`
- **配置表知识库**（含活动 ID、道具 ID、追踪链详情）：`C:\ADHD_agent\.cursor\config-library\table-index.md`
- **翻译 skill**：`C:\ADHD_agent\.agents\skills\game-localization-translator\SKILL.md`
- **导表 skill**：`C:\ADHD_agent\.cursor\skills\P2-config-upload\SKILL.md`
