# 定时查BUG / 改BUG 运维文档

> 最后更新: 2026-04-10
> 适用项目: P2DEV (P2), X2

---

## 一、流程概述

```
定时触发 → Jira查BUG → 分类筛选 → 下载截图分析 → 查配置表定位 → 用户确认 → 修复 → 导表
```

## 二、已知问题与注意事项（每次必查清单）

### 2.1 Jira 连接

| 问题 | 解决方案 |
|------|---------|
| SSL 证书吊销检查失败 (`CRYPT_E_REVOCATION_OFFLINE`) | curl 加 `--ssl-no-revoke`；Python 用 `ssl.CERT_NONE` |
| 项目 key 不是 "P2"，是 **P2DEV** | JQL 中用 `project = P2DEV` |
| X2 项目 key 是 **X2** | 正常 |
| Bash 终端中文乱码 | 不用 print 直接输出，改为 Python 写文件再 Read |
| BUG 描述字段几乎都为空 | QA 习惯只写标题+截图，必须下载附件图片分析 |

### 2.2 配置表查询

| 问题 | 解决方案 |
|------|---------|
| `gws_stdin.js` 脚本 args 解析报错 | 待修复脚本，或直接用 gws CLI / Python google-auth 方式 |
| gws token 过期 | 运行 `gws auth login` 重新认证 |
| 查表前必须先查 table-index.md | 获取 SheetID 映射，否则不知道查哪个 spreadsheet |

### 2.3 1011 (i18n) 表处理流程

1011 类 BUG（LC key 缺失/文案错误）是最常见的配置类问题。使用 `game-localization-translator` skill 处理。

```
截图识别 LC key → check_duplicates.py 查重 → lookup_tm.py 查翻译记忆
  → 生成 18 语言翻译 → 写入「AI翻译暂存」页签 → 通知 linkang → linkang review/导表/关 Jira
```

**具体步骤：**

1. **定位 LC key** — 从截图中识别显示为原始 key 的文本（如 `LC_EVENT_xxx`），确定中文应该是什么
2. **Key 查重** — 运行 `python check_duplicates.py <key1> <key2> ...`
   - 脚本目录: `C:\Users\linkang\.agents\skills\game-localization-translator\scripts\`
   - 有冲突 → 复用已有 key 或换名
   - 无冲突 → 继续
3. **翻译记忆查询** — 运行 `python lookup_tm.py "中文文本1" "中文文本2" ...`
   - 精确匹配 → 直接复用已有 18 语言翻译
   - 部分匹配 → 沿用已有术语（如"探测"→SCAN）
   - 无匹配 → AI 生成全新翻译
4. **生成 18 语言** — 翻译顺序: cn → en → fr → de → po → zh → id → th → sp → ru → tr → vi → it → pl → ar → jp → kr → cns
   - `cns` = `cn` 内容
   - `\n` 保留为字面量，不拆行
   - 参数 `{0}` 各语言数量一致
5. **写入暂存区** — 用 Python Google Sheets API 写入「AI翻译暂存」页签
   - 目标表格: `11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY`
   - 每行格式: [目标页签, ID, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns]
   - A 列设 checkbox（默认 false）
6. **通知 linkang** — 汇报写了哪些 key，linkang 去暂存页签 review → 勾选 → 菜单提交

**linkang 后续操作：**
- 在「AI翻译暂存」review 翻译质量
- 勾选确认的行 → 菜单 "本地化工具 > 提交选中行"
- Apps Script 自动追加到目标页签、生成 ID_int、标粉红背景
- 导表、关 Jira

**注意：**
- 索引过期时运行 `python scan_all_keys.py` 刷新（46000+ key）
- 翻译记忆过期时运行 `python build_translation_memory.py` 刷新（40000+ 条）
- ID 格式: `[a-z0-9_]` 全小写语义化，不加页签前缀

### 2.4 截图分析

| 注意点 | 说明 |
|--------|------|
| 截图命名不规范 | 有些是 Cursor 自动生成的超长路径名 |
| 截图可能是手机录屏截图 | 分辨率和比例可能不同 |
| 红圈/箭头标注 | QA 会用红色标注问题区域，注意识别 |

## 三、BUG 分类标准

### 可自动修复类型
1. **LC key 翻译缺失/文案错误** — 1011 表补中文 → 翻译 skill 扩 18 语言 → 交 linkang
2. **ID 引用错误** — 如 2011 的 actv_id 指向错误活动
3. **字段值配置错误** — 数值、条件配置不对
4. **缺失配置行** — 需要在 2111/2112/2115 等表新增行
5. **道具 icon 引用错误** — 1111 表 icon 字段指向错误资源
6. **排名奖励引用错误** — 2118 表奖励指向旧活动

### 需人工处理类型
1. **代码逻辑 BUG** — 进度计算、领取判断、跳转逻辑等
2. **美术资源问题** — 需要设计出新图
3. **交互/UX 问题** — 需要策划确认方案

## 四、定时任务配置

### JQL 查询模板
```
# 查 linkang 的未解决 BUG
assignee = linkang AND issuetype = Bug AND resolution = Unresolved ORDER BY priority DESC, created DESC

# 查所有配置类 BUG（通过 component 筛选）
project = P2DEV AND issuetype = Bug AND resolution = Unresolved AND component in ("J 节日", "C 常规其他") ORDER BY created DESC
```

### Python 查询模板
```python
import urllib.request, base64, ssl, json, urllib.parse

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

auth = base64.b64encode(b'linkang:<TOKEN>').decode()
jql = 'assignee = linkang AND issuetype = Bug AND resolution = Unresolved'
params = urllib.parse.urlencode({'jql': jql, 'maxResults': 30, 'fields': 'key,summary,status,priority,created,description,attachment,components'})
url = f'https://jira.tap4fun.com/rest/api/2/search?{params}'
req = urllib.request.Request(url, headers={'Authorization': f'Basic {auth}'})
resp = urllib.request.urlopen(req, context=ctx)
data = json.loads(resp.read().decode('utf-8'))
```

### 截图下载模板
```python
# 下载附件
att_url = 'https://jira.tap4fun.com/secure/attachment/{id}/{filename}'
req = urllib.request.Request(att_url, headers={'Authorization': f'Basic {auth}'})
resp = urllib.request.urlopen(req, context=ctx)
```

## 五、每次执行检查清单

- [ ] Jira 能连上吗？（SSL 问题、VPN 问题）
- [ ] gws token 是否过期？
- [ ] 有没有新增的 BUG？（对比上次查询结果）
- [ ] 新 BUG 中哪些是配置类？
- [ ] 配置类 BUG 中哪些可以自动修？
- [ ] 截图都下载分析了吗？
- [ ] 修复方案提交用户确认了吗？
- [ ] **翻译类问题必须走 game-localization-translator skill**，不要手写 18 语言

## 六、Review 问题记录

### 问题1: 不要手写 18 语言翻译
- **场景**: 处理 LC key 翻译时，直接在 Python 代码中硬编码 18 语言的翻译文本
- **问题**: 代码太长导致 JSON 解析失败、shell 引号冲突、翻译质量不可控
- **正确做法**: 必须调用 `game-localization-translator` skill（/game-localization-translator），走完整的 check_duplicates → lookup_tm → 生成翻译 → 写入暂存区流程
- **Why**: skill 有 TM 查重、术语一致性保障、标准写入模板，手写容易出错且不可复现

### 问题2: 更新已有 key vs 新建 key 的写入方式不同
- **已有 key**（如 `2025anni_marble_gacha_rule`）: 直接更新目标页签对应行（如 EVENT row 7380），用 `sheets_api.values().update()` 覆盖 C~T 列
- **新建 key**（如 `marble_master_box_name`）: 写入「AI翻译暂存」页签，等用户 review 后提交

### 问题3: 修改配置前必须等用户确认
- **场景**: 查到问题后直接写入 Google Sheet + 导表 + 推送，跳过了用户确认
- **正确做法**: 严格遵守两个确认点：
  - **确认点1（查询结果）**: 展示"我查到了什么、问题在哪"，问"查询方式是否正确？"
  - **确认点2（修复方案）**: 展示"要改哪个表、哪行、什么值"，问"确认后我执行修改并导表"
  - 两个确认都通过后才能写入 Google Sheet → 导表 → 推送
- **Why**: 配置改错了会影响线上，不可逆。用户需要在关键节点把关。
- **唯一例外**: 用户明确说"直接改"时可以跳过确认

### 问题4: 2111 缺配置行的排查流程
- **症状**: "无法后台开启"、"2111表没有对应活动配置"
- **排查步骤**:
  1. 从 BUG 标题确定活动类型（如"机甲抽奖"）
  2. 在 2112 (activity_config) 表模糊搜索新活动 ID（关键词：活动名/constant/注释）
     - SheetID: `1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E`，tab: `activity_config_qa`
  3. 确认该 activity_id 在 2111 中不存在
  4. 找同类型老版行作为模板（相同 activity_id 的老行，或同类活动的行）
  5. 新 ID = 最后一行 ID + 1，其余字段照抄模板
  6. 用 `sheets_api.values().append()` 追加（表可能满行，不能用 update）
  7. 导表到 bugfix 分支
- **关键表**:
  - 2111 SheetID: `1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g`，tab: `activity_calendar_QA`
  - 2112 SheetID: `1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E`，tab: `activity_config_qa`

### 问题4: 规则文案类 BUG 需要策划案输入
- 规则文案不能靠猜，必须拿到策划案（Google Sheet / 文档）再写
- 流程: 读老规则 → 让用户提供策划案链接 → 基于策划案写新规则 → 用户确认措辞 → 翻译 skill 生成 18 语言

## 七、历史记录

### 2026-04-10 首次试跑
- 查到 linkang 18 个未解决 BUG
- 5 个高优先级是代码逻辑类（机甲抽奖）
- 6 个是 LC key 翻译缺失
- 2 个是缺配置行（2111/2116）
- 3 个是 icon/资源引用问题
- gws_stdin.js 脚本报错，未能通过配置表验证

### 2026-04-10 修复记录
| BUG | 操作 | 状态 |
|-----|------|------|
| P2DEV-141612 | 4 个 2026pioneer item key 补翻译 → 暂存区 row 112-115 | 待 review |
| P2DEV-141613 | 1111 item 111111017 去掉 bag 标签 → bugfix 分支已推送 | ✅ 已完成 |
| P2DEV-141157 | 2026pioneer_marble_gacha_title 改为"庆典弹弹乐" → 直接更新 EVENT | ✅ 已完成 |
| P2DEV-141128 | 2025anni_marble_gacha_rule 新增福利关卡/高级商店/里程碑规则 → 直接更新 EVENT row 7380 | ✅ 已完成 |
| P2DEV-141128 | marble_master_box_name/_desc 新建 → 暂存区 row 101-102 | 待 review |
| P2DEV-141381 | mecha_gacha_rule 改为金字塔爬塔7条规则 → 直接更新 EVENT row 4996 | ✅ 已完成 |
| P2DEV-141394 | 2111 新增 21117153→21127807 新版机甲gacha → bugfix 已推送 | ✅ 已完成 |
