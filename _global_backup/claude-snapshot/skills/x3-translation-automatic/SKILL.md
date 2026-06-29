---
name: x3-translation-automatic
description: >-
  X3游戏多语言文本生成与翻译技能。自动扫描配置表提取TXT_文本、翻译成10种语言、写入Google Sheets翻译文档和Text.xlsx、git提交。
  当用户说"生成多语言"、"导入文本"、"跑i18n"、"翻译文本"、"扫描文本"、"多语言提交"时使用此技能。
  即使用户只是提到需要更新Text表或提交翻译，也应该主动使用这个技能。
---

# X3 多语言文本生成与翻译

> 作者：gongliang

## 路径配置

X3 配置和扫描脚本在同一个 git 仓库内：

| 变量 | 含义 | 默认值 |
|------|------|--------|
| `X3_CONFIG_DIR` | X3 配置 git 仓库根目录 | `E:\x3gdconfig` |

派生路径（自动推导，无需单独配置）：
- 配置 xlsx 目录：`{X3_CONFIG_DIR}\data`
- `TEXT_XLSX`         = `{X3_CONFIG_DIR}\data\i18n\Text.xlsx`
- `LOCAL_LANG_XLSX`   = `{X3_CONFIG_DIR}\data\i18n\LocalLanguage.xlsx`
- `CODER_TID_XLSX`    = `{X3_CONFIG_DIR}\data\i18n\CoderTID.xlsx`
- 扫描脚本目录：`{X3_CONFIG_DIR}\Tools\gen_i18n`

团队共用资源（已写死，跨季度时本文件维护一次即可）：
- Google Sheets 翻译总表 ID：`15WV_P0SLO91E8M_SsWHl5eqoUNxSMLbxpbXhNevf9CQ`
- 当前季度 sheet：`2025Q4`（gid=378526179）

> AI 在生成下面所有代码块前，必须把 `{X3_CONFIG_DIR}` 这个占位符替换成用户确认过的真实值（优先从用户 memory / CLAUDE.md 读取，没有就问用户），**再执行**。占位符没填的情况下不要直接运行代码。

## 概述

X3项目有两种多语言文本来源，本技能处理从扫描到翻译到提交的完整流程。

### 文本来源

| 类型 | Key前缀 | 来源 | 处理方式 |
|------|---------|------|---------|
| 配置表文本 | `TXT_` | xlsx表中Row4标注为TXT_的字段 | CompositeI18n自动扫描提取 |
| 策划案文本 | `Text_` | 策划案中客户端读取的文本 | 需先手动填写到LocalLanguage.xlsx，再运行扫描 |

### 翻译语言（10种）

CN(简中) / EN(英) / SP(西班牙) / FR(法) / ID(印尼) / DE(德) / KR(韩) / ZH(繁中) / RU(俄) / UA(乌克兰)

对应Text.xlsx列：col4=CN, col5=EN, col6=SP, col7=FR, col8=ID, col9=DE, col10=KR, col11=ZH, col12=RU, col13=UA

---

## ⚠️ 已知陷阱（必读）

### 陷阱 1：扫描前 monkey patch updateFile

`CompositeI18n` 内部会调 svn update，git 仓库下必然失败并 return（整个扫描不会执行）。调用前 monkey patch 跳过：

```python
import gen_i18n_imp
gen_i18n_imp.updateFile = lambda path: ('', '')
```

并确保已手动 `git pull` 拉到最新。

### 陷阱 2：LC 占位符不能 AI 翻译

部分新功能（如 Fogfall 雾落隔离区）的 CN 列**不是普通文本**，而是 LC 引用 JSON：

```json
{"typ":"lc","txt":"LC_FOGFALL_quarantine_broadcast_1"}
```

真文本由另一套 LC 系统维护。AI 翻译会破坏 JSON 结构。处理规则：
- **识别**：CN 内容含 `"typ":"lc"`
- **处理**：跳过，保留 status="新增" 不动，提示用户由 LC 负责人补
- **严禁**：把 JSON 翻成"雾落隔离区广播1"之类的文本，会破坏配置

### 陷阱 3：gws 命令在 Windows 受 cmd.exe 8K 限制

写 Google Sheets 时如果一次 append 行数多（约 > 15 行，取决于内容长度），命令行会超 cmd.exe 8K 限制报"命令行太长"。解决方案二选一：
1. **分批 append**：每批 ≤ 30 行
2. **Python 直调 node.exe**（推荐，绕开 cmd.exe 包装）：
   ```python
   import shutil, os, subprocess
   # 动态发现 node + gws 入口，兼容 scoop / npm global / nvm
   NODE_EXE = shutil.which('node')
   gws_cmd  = shutil.which('gws')   # gws.cmd 绝对路径
   GWS_JS   = os.path.join(os.path.dirname(gws_cmd),
                           'node_modules', '@googleworkspace', 'cli', 'run.js')
   subprocess.run([NODE_EXE, GWS_JS, 'sheets', 'spreadsheets', 'values', 'append',
                   '--params', params_json, '--json', body_json],
                  capture_output=True, shell=False)
   ```

---

## 文本修复前的判定（非常重要）

如果本次目标是"**修复**已有文本"（而不是为新增配置做翻译），**必须先判断问题层级**，决定走哪条流程：

| 问题层级 | 特征 | 修复流程 |
|---|---|---|
| **场景 A：翻译层 bug** | CN 源文正确，但某一或几种外语翻译错了（如拼写错、翻译反了）。原配置表 CN 无需改动 | 直接改 `Text.xlsx` 对应行的语言列；**不需要跑扫描**；保持 status 不变（原 status 通常是 "已校对" 或 "AI"） |
| **场景 B：配置层 bug** | CN 源文本身有错/歧义/过时（比如文字描述和实际玩法不符、数字不对、遣词让译员误解）。其他语言可能跟着错 | **先改配置表的 CN 源**（走 git 流程单独提交）→ 再跑 CompositeI18n 扫描 → 扫描会把该 key 自动标记为 "已修改" → 按第 3 步翻译 10 语言 → 提交 Text.xlsx |

**判定原则**："CN 正确性" 是分水岭：CN 对就只改翻译；CN 不对/有歧义就先改配置。

**不要跳过"先改配置"直接动 Text.xlsx**——因为：
1. Text.xlsx 的 CN 列是扫描器根据配置表生成的，直接改会在下次扫描时被覆盖
2. 其他人再次在配置层改这个 key，扫描会再次把错误的 CN 标记为 "已修改"，你的翻译修改反而被重翻覆盖
3. 违反"配置 → 生成"的单向数据流

---

## 完整流程

### 第0步：检查是否有Text_开头的策划案文本

两种情况：

**情况A：用户直接在对话中提供了Text_文本**
用户会直接给出 key 和中文内容（如 `Text_Mecha_NewFeature = 海妖新功能`），此时由AI直接写入 LocalLanguage.xlsx：

```python
import openpyxl
wb = openpyxl.load_workbook(r'{X3_CONFIG_DIR}\data\i18n\LocalLanguage.xlsx')
ws = wb.worksheets[0]
# 在最后一行追加
next_row = ws.max_row + 1
ws.cell(next_row, 1, 'Text_xxx_xxx')  # key
ws.cell(next_row, 2, '中文内容')       # 中文
wb.save(r'{X3_CONFIG_DIR}\data\i18n\LocalLanguage.xlsx')
```

写入后继续第1步扫描。

**情况B：用户只是提到有策划案文本但没给内容**
提醒用户提供 Text_ 开头的 key 和中文内容，等用户给出后按情况A处理。

如果用户没有提到任何Text_文本，跳过此步直接进入第1步。

### 第1步：运行文本扫描

**前置**：先 `git pull` 拉最新 dev：

```bash
git -C {X3_CONFIG_DIR} checkout dev
git -C {X3_CONFIG_DIR} pull
```

然后跑 CompositeI18n（注意陷阱 1 的 monkey patch）：

```python
import sys
sys.path.insert(0, r'{X3_CONFIG_DIR}\Tools\gen_i18n')

import gen_i18n_imp
gen_i18n_imp.updateFile = lambda path: ('', '')  # 见陷阱 1

from gen_i18n_imp import CompositeI18n

CompositeI18n(
    r'{X3_CONFIG_DIR}\data',
    r'{X3_CONFIG_DIR}\data\i18n\Text.xlsx',
    [r'{X3_CONFIG_DIR}\data\i18n\LocalLanguage.xlsx',
     r'{X3_CONFIG_DIR}\data\i18n\CoderTID.xlsx'],
)
```

依赖：`xlrd==1.2.0`, `openpyxl`, `xmltodict`（如未安装先 `pip install`）

扫描会遍历所有 xlsx 的 TXT_ 标注字段，合并 LocalLanguage 和 CoderTID，将结果写入 Text.xlsx，新文本标记为"新增"。典型耗时 30 秒左右。

### 第1.5步：自动标记已完整的"新增"为"AI"

扫描后，部分"新增"条目可能已有完整的10种语言翻译（例如：之前已提交过翻译但被扫描器重新检测，或像Tag文本 `1000%`、`1200%` 这类所有语言值相同、不需要翻译的纯数字/符号文本）。这些条目应自动标记为"AI"，不再保留"新增"状态：

```python
import openpyxl
wb = openpyxl.load_workbook(r'{X3_CONFIG_DIR}\data\i18n\Text.xlsx')
ws = wb.worksheets[0]
changed = 0
for row in range(5, ws.max_row + 1):
    status = ws.cell(row, 2).value
    if status and str(status).strip() == '新增':
        # 检查10种语言列(col4-col13)是否全部已填
        all_filled = all(
            ws.cell(row, col).value and str(ws.cell(row, col).value).strip()
            for col in range(4, 14)
        )
        if all_filled:
            ws.cell(row, 2).value = 'AI'
            changed += 1
wb.save(r'{X3_CONFIG_DIR}\data\i18n\Text.xlsx')
```

**常见触发场景：**
- Pack.xlsx 的 Tag 列（TXT_标注）：值如 `1000%`、`1500%`、`FREE` 等，所有语言显示一致，扫描时会合并到已有的同值行中，翻译天然完整
- 之前已翻译提交过的文本，因配置变动被扫描器重新检测为"新增"

### 第2步：提取待处理文本（"新增" + "已修改"，自动跳过 LC 占位符）

扫描完成后，读取Text.xlsx找出所有 status="新增" 或 "已修改" 的行，**并按陷阱 2 跳过 LC 占位符**：

```python
import openpyxl
wb = openpyxl.load_workbook(r'{X3_CONFIG_DIR}\data\i18n\Text.xlsx', read_only=True)
ws = wb.worksheets[0]
pending = []
skipped_lc = []
for row_idx, row in enumerate(ws.iter_rows(min_row=5, values_only=True), start=5):
    if not row:
        continue
    status = (row[1] or '').strip() if isinstance(row[1], str) else (row[1] or '')
    if status not in ('新增', '已修改'):
        continue
    key = row[0]
    cn = row[3] if len(row) > 3 else None
    # 陷阱 2：LC 占位符不能 AI 翻译
    if isinstance(cn, str) and '"typ":"lc"' in cn:
        skipped_lc.append((row_idx, key, cn))
        continue
    pending.append((row_idx, status, key, cn))
wb.close()

print(f'真实 pending: {len(pending)} 条')
print(f'跳过 LC 占位符: {len(skipped_lc)} 条 (留 status=新增，由 LC 负责人补)')
```

**两种状态的区别**（非常重要，影响翻译策略）：
- **新增**：Key 首次出现，其他 9 列为空，需要从零翻译 10 语言
- **已修改**：Key 已存在但 CN 内容被更新，**其他 9 列仍保留旧翻译**——这是宝贵的术语/风格基线，应基于旧翻译做最小化修改

如果两种状态都没有（pending 为空），告知用户并结束。

> ⚠️ Text.xlsx 很大（~2 万行，~7 MB）。完整 load_workbook 大约 7 秒，save 大约 7 秒。read_only 模式下遍历可能很慢。定点查询特定 Key 时用 `marker in key_str` 判断（因为 Text.xlsx 会把同值的多个 Key 合并成 `TXT_A|TXT_B|TXT_C` 形式存一行）。

### 第3步：翻译（自己翻译，但必须比对历史记录保持术语一致）

**翻译方法**：由 AI 自己翻译（不依赖 Google Sheets 自动翻译机制），但**翻译前必须比对 Text.xlsx 中相关条目的历史翻译**，确保术语、风格一致。

翻译规则：

1. **保留游戏标签不翻译**：`<color=#xxx>`, `</color>`, `<quad .../>`, `{0}`, `{1}` 等参数占位符和富文本标签必须原样保留
2. **繁中(ZH)不是翻译而是简繁转换**

**术语一致性策略**（按状态区分）：

**对"已修改"状态**：
1. 先读出该行旧的 9 语言翻译作为术语基线
2. 定位 CN 新旧内容的差异点（通常是数字、时间、具体参数变化）
3. 仅对各语言版本做**最小化修改**，对应 CN 的变化点
4. 不变的句子结构、术语、风格**原样保留**

**对"新增"状态**：
1. 列出文本涉及的所有专有名词/术语（如物品名、英雄名、活动名、功能名）
2. 在 Text.xlsx 中搜已有条目的翻译（例如 `TXT_Item_Name_1143 = 渊海秘币 = Deepsea Medallion`）
3. 查相似场景的翻译风格（例如翻译"消耗 1 个 X"类任务，参考 `TXT_ActvScoreTask_TaskDesc_100` "每消耗1钻石 = Spend 1 diamond"；但"消耗 1 个英雄信物"是 `Use 1 rare heroine token`，用 Use 而非 Spend——要区分"消耗货币"vs"使用道具"的动词）
4. 基于查到的术语+风格翻译新文本

**参考案例 1（X3NEW-380 已修改）**：
旧版 1901 描述 "2 war phases" 配置改为 6 轮后，CN 更新为 "6 war phases 在 UTC 0/4/8/.../20 点"。处理方法：
- 读旧版 EN/SP/FR/…/UA 翻译
- 仅在每种语言对应位置改：数字 2→6、时间字符串、第 5 条"switch in the second phase"→"alternate every phase"
- 术语（war phase/invader/defender/post-war recovery）完全保留

**参考案例 2（X3NEW-337 新增）**：
新增 `TXT_ActvScoreTask_TaskDesc_1802 = 消耗1个渊海秘币`。处理方法：
- 搜 "渊海秘币" 在 Text.xlsx：找到 `TXT_Item_Name_1143 = Deepsea Medallion / Medallón de las Profundidades / …`（10 语言完整）
- 搜"消耗1个 X"风格：找到 `TXT_ActvScoreTask_TaskDesc_201 = 消耗1个稀有英雄信物进行英雄升星 = Use 1 rare heroine token to star up`
- 组合：`Use 1 Deepsea Medallion` / `Usa 1 Medallón de las Profundidades` / …

### 第4步：写入Text.xlsx

将翻译结果写入对应行的各语言列（col4=CN, col5=EN, col6=SP, col7=FR, col8=ID, col9=DE, col10=KR, col11=ZH, col12=RU, col13=UA），并把 status 从"新增/已修改"改为"AI"。

```python
LANG_COLS = {'CN':4, 'EN':5, 'SP':6, 'FR':7, 'ID':8, 'DE':9, 'KR':10, 'ZH':11, 'RU':12, 'UA':13}
# ... 写入每列后
ws.cell(row, 2).value = 'AI'   # 标记状态
```

**性能建议**：把所有翻译累积到内存（dict / jsonl），最后一次 `load_workbook` + 一次 `save`，避免反复读写大文件。完整流程 241 条写回实测约 15 秒。

> ⚠️ 换行符：Text.xlsx 里换行用字面两字符 `\n`（反斜杠+n），不是真换行符。Python 写入时用 `'\\n'`（字符串字面）。openpyxl 读出时显示为 `\\n`（repr 形式）。

### 第5步：写入Google Sheets翻译文档

当前使用的翻译sheet为 **2025Q4**（gid=378526179）。每行10列对应10种语言，顺序：CN, EN, SP, FR, ID, DE, KR, ZH, RU, UA。

**追加新行（10列完整数据）**：

⚠️ **Windows 重要**：行数多时 cmd.exe 8K 命令行限制会触发（见陷阱 3）。推荐用 Python 分批 + node.exe 直调：

```python
import json, os, shutil, subprocess
# 动态发现 node + gws 入口（兼容 scoop / npm global / nvm）
NODE_EXE = shutil.which('node')
_gws_cmd = shutil.which('gws')
GWS_JS   = os.path.join(os.path.dirname(_gws_cmd),
                        'node_modules', '@googleworkspace', 'cli', 'run.js')
SHEET_ID = '15WV_P0SLO91E8M_SsWHl5eqoUNxSMLbxpbXhNevf9CQ'

def append_rows(rows, sheet='2025Q4', batch=30):
    """rows: List[List[str]]，每个 inner list 10 个值（CN,EN,SP,FR,ID,DE,KR,ZH,RU,UA）"""
    for i in range(0, len(rows), batch):
        chunk = rows[i:i + batch]
        params = json.dumps({'spreadsheetId': SHEET_ID, 'range': f'{sheet}!A1',
                             'valueInputOption': 'USER_ENTERED'}, ensure_ascii=False)
        body = json.dumps({'values': chunk}, ensure_ascii=False)
        r = subprocess.run([NODE_EXE, GWS_JS, 'sheets', 'spreadsheets', 'values', 'append',
                            '--params', params, '--json', body],
                           capture_output=True, shell=False)
        assert r.returncode == 0, r.stderr.decode('utf-8', errors='replace')
```

**条目少（≤ 15 行）也可直接用 gws CLI**：
```bash
gws sheets spreadsheets values append \
  --params '{"spreadsheetId": "15WV_P0SLO91E8M_SsWHl5eqoUNxSMLbxpbXhNevf9CQ", "range": "2025Q4!A1", "valueInputOption": "USER_ENTERED"}' \
  --json '{"values": [["中文","English","Spanish","French","Indonesian","German","Korean","繁中","Russian","Ukrainian"]]}'
```

### 第5.9步：⛔ 提交前泄漏审计（强制门禁，2026-06-24 新增，别跳）

> **背景**：翻译最坑的不是"漏填"（空缺审计能查），而是 **cn之外的语言列照抄英文/中文**——
> 单元格非空、看着"15语已填"，其实只有中英（"伪完整"）。世界杯抽奖券、深海节都因此漏了一大片，
> 肉眼和"语言齐全"检查都查不出。**必须跑确定性脚本**：

```bash
python C:\Users\linkang\.claude\skills\x3-translation-automatic\scripts\i18n_leak_audit.py --changed
```

- 只审本次 `git diff HEAD` 改动过的行（不会被全表历史 jp 缺口刷屏）。退出码 1=有泄漏，**修完再提交**。
- 三类 block：`EN_LEAK`(列==en英文原文) / `CJK_LEAK`(非中日列含汉字) / `EMPTY`(空缺)；`ZH_RAW`(warn)=zh疑未转繁。
- 按范围查（非 git 改动场景）：`--grep <主题词>` 或 `--prefix <key前缀>`，如 `--grep 世界杯`。
- 修法：从**同义已正确翻译的兄弟行**抄术语逐语言重译（如券名去 `ActvDesc` 摘【…】现成译名），en 保留。
- 收工 Stop hook 的 quality-gate(type=i18n) 会用同一脚本兜底（见 `C:\ADHD_agent\.claude\quality-gate\i18n-checklist.md`），但**以自觉先跑为主**。

### 第6步：git 提交

> ⚠️ 当前 X3 真源 = **tsv**（`tsv/i18n/Text__Text.tsv`，导入只认它；`data/i18n/*.xlsx` 已于 commit 68685d2 下线出 git，本地钩子自动 tsv→xlsx 同步即可）。下面的 `git add data/i18n/Text.xlsx` 是旧环境写法，**实际应 `git add tsv/i18n/Text__Text.tsv`**。

```bash
cd {X3_CONFIG_DIR}
git checkout dev
git pull
git add data/i18n/Text.xlsx
git commit -F msg.txt     # Windows 必须 -F 避免中文乱码
git push                  # 触发 pre-push 检查 + 钉钉通知
```

`msg.txt` 内容格式：`X3NEW-{ticket号} 多语言文本更新`，如果没有ticket号则用通用描述。

如果 LocalLanguage.xlsx 也有更新，一起提交：
```bash
git add data/i18n/Text.xlsx data/i18n/LocalLanguage.xlsx
git commit -F msg.txt
git push
```

---

## 注意事项

- Python执行时如遇中文输出乱码，加 `-u -X utf8` 参数并设置 `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')`
- Text.xlsx前4行是表头（从第5行开始是数据），col1=TXT_Key, col2=状态(AI/新增/已修改/已删除), col3=备注, col4=CN, col5=EN...col13=UA
- **Key 合并机制**：扫描工具会把 CN 内容相同的多个 Key 合并到同一行存储，Key 字段形如 `TXT_A|TXT_B|TXT_C`。查找特定 Key 时用 `marker in key_str` 而不是 `key_str == marker`
- **换行符**：Text.xlsx 里存的是字面 `\n`（两字符），Python 写入用 `'\\n'`，repr 输出显示为 `'\\\\n'`。切勿误写成真换行符，否则客户端解析异常
- **同一 ContentID 被复用**：赛季活动（如 S1-S5 的"最佳酒馆-W2"）可能共用同一个 ContentID/任务模板，改一次会影响所有复用它的活动。改前先确认复用范围（搜 ActvOnline 里相同 ContentID 的活动）
- 翻译量大时（超过20条），可以考虑批量处理，但每条都要确保术语准确
- gws CLI 认证状态可用 `gws auth status` 检查

## 最佳实践：翻译风格 ≠ 机器翻译

- **自己翻译+比对 Text 历史记录**是标准做法，不是简单贴中文等表格自动翻译
- 每次翻译前先做"术语调研"：搜相关物品/英雄/功能的现有翻译，抄术语
- 对"已修改"条目，**务必基于旧翻译做 diff 式改动**，不要整段重新翻——否则术语和风格会漂移
- 翻译完不要跳过 `status: 新增/已修改 → AI` 这一步，否则下次扫描会再次命中
