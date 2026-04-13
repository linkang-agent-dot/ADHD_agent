---
name: game-localization-translator
description: >-
  游戏本地化翻译全流程工具。从UX截图或原始文本提取UI文本，自动查重、复用翻译记忆、生成18语言翻译，
  支持写入暂存区review或直接写入目标页签。触发场景：游戏多语言配置、本地化翻译表、i18n配置、UI文本提取、
  多语言扩散翻译、LC_Key生成、翻译存入表格、UX截图翻译、翻译LC、直出i18n。
---

# 游戏本地化翻译全流程工具

## 核心能力

从 **UX截图** 或 **原始文本** 出发，经过 Key查重 → 翻译记忆复用 → 18语言翻译 → 写入目标的完整流程。

支持两种写入模式：
- **暂存区模式**（默认）：写入「AI翻译暂存」页签，用户 review 后提交
- **直接写入模式**：跳过 review，直接写入目标页签

## 前置条件

| 依赖 | 说明 |
|------|------|
| Python 3 | `google-api-python-client`, `google-auth` |
| gws CLI | 已认证（`gws auth login`），用于获取 OAuth 凭据 |
| Google Sheet | 需有编辑权限 |
| Apps Script | 已部署 `localization_tool.gs`（见 [setup-apps-script.md](setup-apps-script.md)） |

### 目标表格

```
spreadsheetId: 11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY
链接: https://docs.google.com/spreadsheets/d/11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY
```

### 工作目录

所有脚本和缓存文件位于：`C:\Users\linkang\.agents\skills\game-localization-translator\scripts\`

---

## 完整执行流程

收到用户的 UX 截图或文本后，**严格按以下步骤执行**：

### Step 1: 提取 UI 文本

- 截图：仔细识别所有可见的 UI 文本（按钮、标题、提示、Tab名等）
- 纯文本：直接使用用户提供的中文原文
- 输出一张表格列出所有提取到的文本

### Step 2: Key 重复检测

运行脚本检查新生成的 key 是否与现有 46000+ key 冲突：

```bash
cd "C:\Users\linkang\.agents\skills\game-localization-translator\scripts"
python check_duplicates.py key1 key2 key3 ...
```

- **有冲突** → 告知用户该 key 已在哪个页签，建议换名或复用
- **无冲突** → 继续

> 索引文件 `all_existing_keys.json` 如过期，运行 `python scan_all_keys.py` 刷新

### Step 3: 翻译记忆查询

查询 40000+ 条已有翻译，复用已有词汇保持风格一致：

```bash
python lookup_tm.py "中文文本1" "中文文本2" ...
```

- **精确匹配** → 直接复用已有翻译的所有 18 语言
- **部分匹配** → 参考已有词汇（如"探测"→SCAN），新翻译中使用同样的词
- **无匹配** → AI 生成全新翻译

> 记忆库 `translation_memory.json` 如过期，运行 `python build_translation_memory.py` 刷新

### Step 4: 推断目标页签

根据文本内容自动推断目标页签，详见 [reference.md](reference.md) 的页签映射表。

### Step 5: 生成 ID

- **格式**：`[a-z0-9_]`，全小写，语义化命名
- **不加页签前缀**：如 `cool_treasure_title`，不是 `event_cool_treasure_title`
- **暂存区不填 ID_int**：提交到目标页签时由 Apps Script 自动顺延生成

### Step 6: 生成 18 语言翻译

翻译顺序：cn → en → fr → de → po → zh → id → th → sp → ru → tr → vi → it → pl → ar → jp → kr → cns

**关键规则**：
- `\n` 作为文本字面量保留在同一行，不拆成多行
- 精确匹配 TM 的文本直接复用，不重新翻译
- 部分匹配 TM 的词汇必须沿用（如"探测"已有翻译 SCAN，则所有含"探测"的新翻译都用 Scan）
- `cns` 列（简体中文备份）= `cn` 列内容

### Step 7: 写入数据

根据用户需求选择写入模式：

#### 模式 A：写入暂存区（默认，需 Review）

当用户未明确要求直接写入时，使用此模式。

```python
import json, subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"

# 每行格式: [目标页签, ID, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns]
ROWS = [
    ["EVENT", "explore_record", "探索记录", "EXPLORE LOG", ...其他16语言...],
]

def get_credentials():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8", shell=True,
    )
    creds_data = json.loads(result.stdout.strip())
    return Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )

def main():
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheets_api = service.spreadsheets()

    # 获取暂存页签 sheetId
    spreadsheet = sheets_api.get(
        spreadsheetId=SPREADSHEET_ID, fields="sheets.properties"
    ).execute()
    staging_sheet_id = None
    for s in spreadsheet["sheets"]:
        if s["properties"]["title"] == STAGING_SHEET:
            staging_sheet_id = s["properties"]["sheetId"]
            break

    # 定位追加起始行
    result = sheets_api.values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{STAGING_SHEET}'!A:A"
    ).execute()
    existing = result.get("values", [])
    next_row = max(len(existing) + 1, 2)
    end_row = next_row + len(ROWS) - 1

    # 写入数据到 B~U 列（A 列留给 checkbox）
    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!B{next_row}:U{end_row}",
        valueInputOption="RAW",
        body={"values": ROWS},
    ).execute()

    # 为 A 列设置 checkbox
    sheets_api.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [{
            "repeatCell": {
                "range": {
                    "sheetId": staging_sheet_id,
                    "startRowIndex": next_row - 1,
                    "endRowIndex": end_row,
                    "startColumnIndex": 0, "endColumnIndex": 1,
                },
                "cell": {
                    "dataValidation": {"condition": {"type": "BOOLEAN"}, "strict": True},
                    "userEnteredValue": {"boolValue": False},
                },
                "fields": "dataValidation,userEnteredValue",
            }
        }]},
    ).execute()
    print(f"Done! Wrote {len(ROWS)} rows (row {next_row}-{end_row})")

if __name__ == "__main__":
    main()
```

#### 模式 B：直接写入目标页签（跳过 Review）

当用户明确说"直接写入"、"不用review"、"跳过暂存"时，使用此模式：

```python
import subprocess, json, os

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'

SPREADSHEET_ID = '11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY'
TARGET_SHEET = 'EVENT'  # 根据 Step 4 推断的目标页签

# 每行格式: [ID_int, ID, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns]
rows = [
    [id_int_1, key_1, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns],
    [id_int_2, key_2, ...],
]

append_params = json.dumps({
    "spreadsheetId": SPREADSHEET_ID,
    "range": f"{TARGET_SHEET}!A1",
    "valueInputOption": "RAW",
    "insertDataOption": "INSERT_ROWS",
})

append_body = json.dumps({"values": rows}, ensure_ascii=False)

r = subprocess.run(
    [GWS, 'sheets', 'spreadsheets', 'values', 'append',
     '--params', append_params,
     '--json', append_body],
    capture_output=True, text=True, encoding='utf-8'
)
result = json.loads(r.stdout)
print('✅ 直接写入', TARGET_SHEET, '页签')
print('写入范围:', result['updates']['updatedRange'])
print('写入行数:', result['updates']['updatedRows'])
```

### Step 8: 告知用户结果

输出提交概要表格：

| Key | 中文 | 英文 | 翻译策略 |
|-----|------|------|---------|
| `explore_record` | 探索记录 | EXPLORE LOG | 复用 TM |

- **暂存区模式**：提示用户去「AI翻译暂存」页签 review，确认后勾选 → 菜单 **"本地化工具 > 提交选中行"**
- **直接写入模式**：告知已写入的页签和行范围

---

## 暂存页签格式（21列）

| A | B | C | D | E~U |
|---|---|---|---|-----|
| ✅复选框 | 目标页签 | ID | cn | en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns |

用户在 Sheet 中 review → 勾选 → 菜单提交 → Apps Script 自动：
1. 读取目标页签最后一行 ID_int 并顺延
2. 追加数据到目标页签（20列：ID_int + ID + 18语言）
3. 新增行标记粉红色背景
4. 从暂存区删除已提交行

---

## 目标页签格式（20列）

| A | B | C | D~T |
|---|---|---|-----|
| ID_int | ID | cn | en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns |

---

## 工具脚本速查

| 脚本 | 功能 | 用法 |
|------|------|------|
| `check_duplicates.py` | 检查 key 是否重复 | `python check_duplicates.py key1 key2` |
| `lookup_tm.py` | 查询翻译记忆 | `python lookup_tm.py "中文1" "中文2"` |
| `scan_all_keys.py` | 刷新 key 索引（46000+） | `python scan_all_keys.py` |
| `build_translation_memory.py` | 刷新翻译记忆库（40000+） | `python build_translation_memory.py` |

所有脚本在 `C:\Users\linkang\.agents\skills\game-localization-translator\scripts\` 目录下运行。

---

## 文本处理规范

| 规则 | 说明 |
|------|------|
| `\n` 处理 | 作为字面量保留，不拆行 |
| 参数格式 | `{0}`, `{1}`... 各语言参数数量一致 |
| 简体中文 | 全角标点（，！：？），禁英文字母 |
| 富文本标签 | `<color=#3ef742>` 闭合正确 |
| ID 格式 | `[a-z0-9_]` 全小写，语义化 |

---

## 自检清单

每次输出前完成以下检查：

- [ ] 20列全部有值（暂存区21列含checkbox）
- [ ] ID 全小写，无页签前缀
- [ ] `\n` 未拆行
- [ ] 参数 `{0}` 各语言数量一致
- [ ] 富文本标签正确闭合
- [ ] TM 匹配词汇已复用
- [ ] Key 无重复

---

## 快速参考

- **P2 i18n Spreadsheet ID（国际服）**：`11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY`
- **P2 i18n Spreadsheet ID（国服）**：`1x7E76B9U2CWzOgbuk60F6oEDo_4Lkz1MnRJYSA9m_CM`
- **gws CLI 路径**：`C:\Users\linkang\AppData\Roaming\npm\gws.cmd`
- **GCP 项目 ID**：`calm-repeater-489707-n1`

---

## 详细参考

- 页签映射表、语言列表、ID_int 编码规则：[reference.md](reference.md)
- Apps Script 安装部署说明：[setup-apps-script.md](setup-apps-script.md)
