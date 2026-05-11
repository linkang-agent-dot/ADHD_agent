# 定时查BUG / 改BUG 运维文档

> 最后更新: 2026-04-13
> 适用项目: P2DEV (P2), X2

---

## 🚨 强制规则（必读，违反 = 错误）

### 规则 1：BUG 操作前必须用户确认
**所有 Jira BUG 操作前都要先列方案让用户确认，不能自己点。**

需确认的操作：
- 写入 Google Sheet（暂存区 / 目标页签）
- 加 Jira 评论 / 转派 / 关闭 / 改状态优先级

正确做法：分析完问题 → 列「准备做什么」→ 等用户「OK / 改 / 转吧」再动手。
唯一例外：用户明确说「直接改」「都做」时跳过确认。

### 规则 2：写翻译暂存区前必须确认目标页签
游戏代码引用形式 `LC_<tab>_<key>` 直接暴露页签：
- `LC_minigame_xxx` → 写 minigame
- `LC_EVENT_xxx` → 写 EVENT
- `LC_ITEM_xxx` → 写 ITEM
**不要默认 EVENT**，要先看 BUG 截图里的 raw key 推断目标页签。

### 规则 3：每处理完一个 BUG 必须双沉淀
无论修好/转派/搁置都必须：
1. 更新 **配置知识库** `C:\ADHD_agent\.cursor\config-library\table-index.md` — 新表/新字段/新ID/新追踪链
2. 更新 **本运维文档** `C:\ADHD_agent\docs\ops_auto_bugfix.md` — 历史记录追一行 + 新坑加 Review

未沉淀视为未完成。

### 规则 4：翻译类问题必须用 game-localization-translator skill
不要手写 18 语言（会导致 JSON/shell 引号失败、术语不一致）。
skill 会走完整流程：check_duplicates → lookup_tm → 18 语言 → 写暂存区。
skill 路径: `C:\ADHD_agent\.agents\skills\game-localization-translator\SKILL.md`

### 规则 5：规则文案类 BUG 必须有策划案
不能靠猜。流程：读老规则 → 让用户提供策划案链接 → 写新规则 → 用户确认措辞 → 翻译 skill。

---

## 一、流程概述

```
定时触发 → Jira 查 BUG → 分类筛选 → 下载截图分析 → 查配置表定位
  → ⚠️用户确认查询 → 提修复方案 → ⚠️用户确认方案 → 修复 → 导表 → Jira评论 → ⚠️双沉淀
```

## 二、每次执行检查清单

- [ ] Jira 能连上吗？（SSL / VPN）
- [ ] gws token 是否过期？(`gws auth login`)
- [ ] 对比上次有没有新增 / 关闭 BUG？
- [ ] 新 BUG 中哪些是配置类？哪些可自动修？
- [ ] 截图都下载分析了吗？
- [ ] 修方案给用户确认了吗？（规则 1）
- [ ] 翻译类用 skill 了吗？（规则 4）
- [ ] 修完后双沉淀了吗？（规则 3）

---

## 三、已知问题与解决方案

### 3.1 环境/连接问题

| 问题 | 解决方案 |
|------|---------|
| SSL 证书吊销失败 (`CRYPT_E_REVOCATION_OFFLINE`) | curl 加 `--ssl-no-revoke`；Python 用 `ssl.CERT_NONE` |
| 项目 key 不是 P2，是 **P2DEV** | JQL 用 `project = P2DEV` |
| Bash 终端中文乱码 | 不直接 print，改 Python 写文件再 Read |
| BUG 描述字段几乎都为空 | QA 只写标题+截图，必须下截图分析 |
| `gws_stdin.js` 脚本 args 解析报错 | 改用 gws CLI / Python google-auth |

### 3.2 写 LC key 的两种方式

| 场景 | 写入位置 | API |
|------|---------|-----|
| **新建 key** | 「AI翻译暂存」页签 | `values().update()` 写 B~U 列 |
| **更新已有 key** | 直接更新目标页签对应行 | `values().update()` 覆盖 C~T 列 |

### 3.3 2111 缺配置行排查（活动无法后台开启）

排查步骤：
1. BUG 标题确定活动类型
2. 在 2112 模糊搜活动 ID（关键词：活动名/constant/注释）
3. 确认该 activity_id 在 2111 中不存在
4. 找同类老版行作模板
5. 新 ID = 最后一行 ID + 1
6. 用 `values().append()` 追加（表满行时不能 update）
7. 导表到 bugfix 分支

关键表：
- 2111: `1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g`，tab `activity_calendar_QA`
- 2112: `1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E`，tab `activity_config_qa`

---

## 四、BUG 分类

### 可自动修
1. LC key 翻译缺失 / 文案错误 — 走翻译 skill
2. ID 引用错误 — 如 actv_id 指向旧活动
3. 字段值配置错误 — 数值/条件配错
4. 缺失配置行 — 2111/2112/2115 等表新增
5. 道具 icon 引用错误 — 1111 表 display_key
6. 排名奖励引用错误 — 2118 表
7. 活动规则文案更新 — 走规则 5 流程

### 需人工
1. 代码逻辑 BUG
2. 美术资源（需设计出图）
3. 交互/UX（需策划方案）

---

## 五、1011 翻译流程详解（最常见 BUG 类型）

```
截图识别 raw key → ⚠️确认目标页签 → check_duplicates 查重
  → lookup_tm 查记忆 → 生成 18 语言 → 写暂存区 → linkang/转派人 review/导表/关 Jira
```

具体步骤见翻译 skill 的 SKILL.md，关键点：
- ID 全小写、不加页签前缀（`coin_pusher_xxx` 不是 `LC_minigame_coin_pusher_xxx`）
- `\n` 保留为字面量
- 参数 `{0}` 各语言数量一致
- `cns` = `cn`
- 索引/记忆过期：`scan_all_keys.py` / `build_translation_memory.py`

---

## 六、定时任务配置

### JQL 模板
```
assignee = linkang AND issuetype = Bug AND resolution = Unresolved ORDER BY priority DESC, created DESC
```

### Python 查询模板
```python
import urllib.request, base64, ssl, json, urllib.parse
ctx = ssl.create_default_context()
ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
auth = base64.b64encode(b'linkang:<TOKEN>').decode()
jql = 'assignee = linkang AND issuetype = Bug AND resolution = Unresolved'
params = urllib.parse.urlencode({'jql': jql, 'maxResults': 30, 'fields': 'key,summary,priority'})
url = f'https://jira.tap4fun.com/rest/api/2/search?{params}'
req = urllib.request.Request(url, headers={'Authorization': f'Basic {auth}'})
data = json.loads(urllib.request.urlopen(req, context=ctx).read().decode('utf-8'))
```

### 截图下载
```python
att_url = 'https://jira.tap4fun.com/secure/attachment/{id}/{filename}'
```

### Jira 评论 / 转派
```python
# Comment
url = f'https://jira.tap4fun.com/rest/api/2/issue/{KEY}/comment'
body = json.dumps({'body': '...'}).encode('utf-8')
# 用 POST + Content-Type: application/json

# Reassign
url = f'https://jira.tap4fun.com/rest/api/2/issue/{KEY}/assignee'
body = json.dumps({'name': 'username'}).encode('utf-8')
# 用 PUT + Content-Type: application/json
```

---

## 七、历史记录

### 2026-04-10 首次试跑
- linkang 18 个未解决 BUG
- 5 个高优先级代码逻辑（机甲抽奖）
- 6 个 LC key 翻译缺失
- 2 个缺配置行（2111/2116）
- 3 个 icon/资源问题

### 2026-04-10 修复
| BUG | 操作 | 状态 |
|-----|------|------|
| P2DEV-141612 | 4 个 2026pioneer item key 补翻译 → 暂存区 row 112-115 | 待 review |
| P2DEV-141613 | 1111 item 111111017 去掉 bag 标签 → bugfix 推送 | ✅ |
| P2DEV-141157 | 2026pioneer_marble_gacha_title 改为"庆典弹弹乐" → 直接更新 EVENT | ✅ |
| P2DEV-141128 | 2025anni_marble_gacha_rule 新增福利关卡/高级商店/里程碑规则 → EVENT row 7380 | ✅ |
| P2DEV-141128 | marble_master_box_name/_desc 新建 → 暂存区 row 101-102 | 待 review |
| P2DEV-141381 | mecha_gacha_rule 改为金字塔爬塔7条规则 → EVENT row 4996 | ✅ |
| P2DEV-141394 | 2111 新增 21117153→21127807 新版机甲gacha → bugfix 推送 | ✅ |

### 2026-04-13 后续
| BUG | 操作 | 状态 |
|-----|------|------|
| P2DEV-141128 | 弹珠规则 v2（措辞调整：触发福利关卡 → 激活高级福利弹珠关卡）→ EVENT row 7380 | ✅ v2 |
| P2DEV-141374 | 锤子图标不一致：2154 确认配置正确 → 客户端写死 → 转派 moqi | ✅ 转派 |
| P2DEV-141823 | 小丑宝箱怪虚弱描述显示 `LC_minigame_coin_pusher_monster_new_name`（用户已改）→ Jira 评论 → 已解决待验证(转 安春旭) | ✅ 已解决 |
| P2DEV-141800 | 至尊宝箱缺文案：新建 `coin_pusher_ultimate_box_received_tip`(minigame 页签) → 转派 fanglingjia | ✅ 转派 |

### 当前未解决（截至 2026-04-13）
7 个：141816 / 141776 / 141772 / 141824 / 141395 / 141128 / X2-41742
（141382 转 zhouyaoxu，141800 转 fanglingjia，141374 转 moqi，141823 已解决）
