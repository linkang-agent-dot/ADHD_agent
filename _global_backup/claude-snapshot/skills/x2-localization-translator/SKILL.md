# X2 游戏本地化翻译全流程工具

## 核心能力

从 **UX截图** 或 **原始文本** 出发，经过 Key查重 → 翻译记忆复用 → 18语言翻译 → 写入目标的完整流程。
专用于 **X2 项目**。

## 前置条件

| 依赖 | 说明 |
|------|------|
| Python 3 | `google-api-python-client`, `google-auth` |
| gws CLI | 已认证（`gws auth login`），用于获取 OAuth 凭据 |
| Google Sheet | 需有编辑权限 |

### 目标表格

```
spreadsheetId: 1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg
链接: https://docs.google.com/spreadsheets/d/1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg
```

### 工作目录

所有脚本和缓存文件位于：`C:\Users\linkang\.agents\skills\x2-localization-translator\scripts\`

---

## 完整执行流程

收到用户的 UX 截图或文本后，**严格按以下步骤执行**：

### Step 1: 提取 UI 文本

- 截图：仔细识别所有可见的 UI 文本（按钮、标题、提示、Tab名等）
- 纯文本：直接使用用户提供的中文原文
- 输出一张表格列出所有提取到的文本

### Step 2: Key 重复检测

运行脚本检查新生成的 key 是否与现有 key 冲突：

```bash
cd "C:\Users\linkang\.agents\skills\x2-localization-translator\scripts"
python check_duplicates.py key1 key2 key3 ...
```

- **有冲突** → 告知用户该 key 已在哪个页签，建议换名或复用
- **无冲突** → 继续

> 索引文件 `all_existing_keys.json` 如过期，运行 `python scan_all_keys.py` 刷新

### Step 3: 翻译记忆查询

查询已有翻译，复用已有词汇保持风格一致：

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

### Step 6: 生成 18 语言翻译

翻译顺序：cn → en → fr → de → po → zh → id → th → sp → ru → tr → vi → it → pl → ar → jp → kr → cns

**关键规则**：
- `\n` 作为文本字面量保留在同一行，不拆成多行
- 精确匹配 TM 的文本直接复用，不重新翻译
- 部分匹配 TM 的词汇必须沿用（如"探测"已有翻译 SCAN，则所有含"探测"的新翻译都用 Scan）
- `cns` 列（简体中文备份）= `cn` 列内容

### Step 7: 写入数据

直接追加到目标页签：

```python
import subprocess, json, os

GWS_STDIN = r'C:\ADHD_agent\scripts\gws_stdin.js'
SPREADSHEET_ID = '1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg'
TARGET_SHEET = 'EVENT'  # 根据 Step 4 推断的目标页签

# 先获取目标页签最后一行的 ID_int，用于顺延
get_last_params = json.dumps({
    "spreadsheetId": SPREADSHEET_ID,
    "range": f"{TARGET_SHEET}!A:A"
})
stdin_payload = json.dumps({
    "args": ["sheets", "spreadsheets", "values", "get", "--params", get_last_params]
}, ensure_ascii=False)

r = subprocess.run(
    ["node", GWS_STDIN],
    input=stdin_payload, capture_output=True, text=True, encoding='utf-8'
)
result = json.loads(r.stdout)
values = result.get("values", [])
last_id_int = int(values[-1][0]) if values else 0
next_id_int = last_id_int + 1

# 每行格式: [ID_int, ID, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns]
rows = [
    [next_id_int, "damage_double_phase", "伤害翻倍阶段", "Double Damage Stage", ...],
]

append_params = json.dumps({
    "spreadsheetId": SPREADSHEET_ID,
    "range": f"{TARGET_SHEET}!A1",
    "valueInputOption": "RAW",
    "insertDataOption": "INSERT_ROWS",
})
stdin_payload = json.dumps({
    "args": [
        "sheets", "spreadsheets", "values", "append",
        "--params", append_params
    ],
    "json": {"values": rows}
}, ensure_ascii=False)

r = subprocess.run(
    ["node", GWS_STDIN],
    input=stdin_payload, capture_output=True, text=True, encoding='utf-8'
)
result = json.loads(r.stdout)
print('写入', TARGET_SHEET, '页签')
print('写入范围:', result['updates']['updatedRange'])
print('写入行数:', result['updates']['updatedRows'])
```

### Step 8: 告知用户结果

输出提交概要表格：

| Key | 中文 | 英文 | 翻译策略 |
|-----|------|------|---------|
| `explore_record` | 探索记录 | EXPLORE LOG | 复用 TM |

告知已写入的页签和行范围。

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
| `scan_all_keys.py` | 刷新 key 索引 | `python scan_all_keys.py` |
| `build_translation_memory.py` | 刷新翻译记忆库 | `python build_translation_memory.py` |

所有脚本在 `C:\Users\linkang\.agents\skills\x2-localization-translator\scripts\` 目录下运行。

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

- [ ] 20列全部有值
- [ ] ID 全小写，无页签前缀
- [ ] `\n` 未拆行
- [ ] 参数 `{0}` 各语言数量一致
- [ ] 富文本标签正确闭合
- [ ] TM 匹配词汇已复用
- [ ] Key 无重复

---

## 快速参考

- **X2 i18n Spreadsheet ID**：`1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg`
- **gws_stdin.js 路径**：`C:\ADHD_agent\scripts\gws_stdin.js`
- **GCP 项目 ID**：`calm-repeater-489707-n1`

---

## 详细参考

- 页签映射表、语言列表：[reference.md](reference.md)
