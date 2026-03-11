# 分支差异汇总到 Google Sheet

## 概述

对比 X2 配置表仓库的两个分支差异，自动创建 Google Sheet 汇总。每个配置表一个页签，逐行展示差异，精确到单元格级别的颜色标注。

**触发词**: "分支差异"、"差异汇总"、"对比分支"、"diff到表格"、"差异GSheet"、"查看分支改动"

---

## 前置条件

1. **gws CLI** 已安装且已认证（参见 `google-workspace-cli/SKILL.md`）
2. **环境变量** `GOOGLE_WORKSPACE_PROJECT_ID` 已设置（值: `calm-repeater-489707-n1`）
3. X2 配置表仓库路径: `D:\UGit\x2gdconf`
4. 已 `git fetch` 拉取最新远程分支

---

## 执行流程

```
确认分支 → 提取差异 → 创建 GSheet → 写入数据 → 精确着色
```

### 步骤 1：确认分支

向用户确认：
- **源分支**（feature 分支，如 `origin/dev_X2-39183`）
- **目标分支**（基准分支，如 `origin/dev`）

分支别名见 `c:\ADHD_agent\.cursor\rules\x2-gsheet.mdc` 中的"分支别名速查"表。

### 步骤 2：获取差异文件列表

```bash
git diff --name-only <target>...<source> -- fo/config/
```

**过滤规则**：
- 排除 `fo/i18n/` 本地化文件
- 仅保留 `.tsv` 配置表

### 步骤 3：提取差异内容

对每个文件，使用 `git diff <target>...<source> -- <filepath>` 提取：
- `+` 开头的行 = 源分支新增/修改的内容
- `-` 开头的行 = 目标分支中被替换的旧内容
- 跳过 `+++` / `---` 文件头

**判断行类型**：取每行 TSV 的第一个非空列作为行 ID
- 如果该 ID 同时出现在 `+` 行和 `-` 行 → **修改**（modified）
- 如果仅出现在 `+` 行 → **新增**（added）

**获取表头**：`git show <source>:<filepath>` 读取源分支的完整文件，优先取 `fwcli_name` 行（字段名行），否则取第一个有效行。

**⚠️ 补齐短行**：TSV 尾部空值列可能没有 tab 分隔符（如 `iap_config` 的 `SubScene` 列），导致 `split('\t')` 少列。必须用表头列数对所有数据行进行 pad：
```python
if len(parts) < header_cols:
    parts.extend([''] * (header_cols - len(parts)))
```

### 步骤 4：创建 Google Sheet

使用 `gws sheets spreadsheets create` 一次性创建带所有页签的表格：

```python
create_body = {
    "properties": {"title": "X2 <分支名> 差异汇总"},
    "sheets": [
        {"properties": {"sheetId": i, "title": sheet_name, "index": i}}
        for i, sheet_name in enumerate(sheet_names)
    ]
}
```

### 步骤 5：写入数据

每个页签的第一行是 `["变更类型"] + 表头`，后续每行是 `["新增"/"修改"] + 单元格数据`。

**分块写入**，避免命令行超长（见下方"Windows 命令行限制"章节）。

### 步骤 6：精确着色

| 区域 | 颜色 | RGB |
|------|------|-----|
| 表头行 | 蓝色 + 加粗 + 冻结 | `(0.75, 0.82, 0.95)` |
| 新增行 | 整行绿色 | `(0.85, 0.95, 0.85)` |
| 修改行中变化的单元格 | 黄色 | `(1.0, 0.93, 0.70)` |
| 修改行中未变化的单元格 | 白色（不着色） | — |

**精确到单元格**：对于修改行，需要获取旧版本内容（`-` 行），逐列对比新旧值，只对实际变化的单元格着黄色。

使用 `batchUpdate` API，每批不超过 50 条 formatting request。

---

## ⚠️ Windows 命令行限制（核心坑点）

### 问题

`gws.cmd` 是一个 cmd.exe 包装脚本，经过 cmd.exe 转发时有 **8191 字符**的命令行限制。直接用 `subprocess.run(['gws.cmd', ...])` 会在大 JSON payload 时报 `WinError 206: 文件名或扩展名太长`。

### 根因

```
gws.cmd → cmd.exe → node.exe run-gws.js  (受 cmd.exe 8191 字符限制)
```

### 解决方案：直接调用 node.exe

绕过 cmd.exe，直接调用 Node.js 运行 `run-gws.js`，走 Windows `CreateProcess` 的 **32767 字符**限制：

```python
import os, subprocess, json

GWS_CMD = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'gws.cmd')  # 仅用于定位路径
NPM_DIR = os.path.dirname(GWS_CMD)
RUN_GWS_JS = os.path.join(NPM_DIR, 'node_modules', '@googleworkspace', 'cli', 'run-gws.js')

def run_gws_direct(args, json_body=None):
    """直接调用 node run-gws.js，绕过 cmd.exe 的 8191 字符限制"""
    cmd = ['node', RUN_GWS_JS] + args
    if json_body is not None:
        cmd.extend(['--json', json.dumps(json_body, ensure_ascii=False)])
    
    result = subprocess.run(
        cmd,
        capture_output=True, text=True, encoding='utf-8',
        errors='replace',
        env={**os.environ, 'GOOGLE_WORKSPACE_PROJECT_ID': 'calm-repeater-489707-n1'}
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout
```

### 分层策略

| JSON payload 大小 | 方法 |
|-------------------|------|
| ≤ 7000 字符 | 直接 `gws.cmd`（走 cmd.exe 没问题） |
| 7000 ~ 30000 字符 | `node run-gws.js`（绕过 cmd.exe） |
| > 30000 字符 | 拆分为更小的批次后用 `node run-gws.js` |

### 数据写入分块

```python
def write_values_chunked(spreadsheet_id, sheet_name, values, chunk_size=20):
    for start in range(0, len(values), chunk_size):
        chunk = values[start:start + chunk_size]
        row_start = start + 1
        body = {"values": chunk, "majorDimension": "ROWS"}
        params = json.dumps({
            "spreadsheetId": spreadsheet_id,
            "range": f"'{sheet_name}'!A{row_start}",
            "valueInputOption": "RAW"
        })
        
        json_str = json.dumps(body, ensure_ascii=False)
        if len(json_str) > 7000:
            # 大 chunk 进一步拆分
            for i, row in enumerate(chunk):
                single_body = {"values": [row], "majorDimension": "ROWS"}
                single_params = json.dumps({
                    "spreadsheetId": spreadsheet_id,
                    "range": f"'{sheet_name}'!A{row_start + i}",
                    "valueInputOption": "RAW"
                })
                run_gws_direct(
                    ['sheets', 'spreadsheets', 'values', 'update',
                     '--params', single_params],
                    single_body
                )
        else:
            run_gws_direct(
                ['sheets', 'spreadsheets', 'values', 'update',
                 '--params', params],
                body
            )
```

### 格式化批处理

`batchUpdate` 格式化请求也需分批，每批 ≤ 50 条 request：

```python
BATCH = 50
for i in range(0, len(format_requests), BATCH):
    batch = format_requests[i:i + BATCH]
    params = json.dumps({"spreadsheetId": spreadsheet_id})
    body = {"requests": batch}
    run_gws_direct(
        ['sheets', 'spreadsheets', 'batchUpdate', '--params', params],
        body
    )
```

---

## 参考脚本

主脚本位于 `c:\ADHD_agent\scripts\create_diff_sheet.py`，包含完整的差异提取、GSheet 创建、数据写入和着色逻辑。

运行方式：

```powershell
cd c:\ADHD_agent
python scripts/create_diff_sheet.py --source origin/dev_X2-39183 --target origin/dev
```

---

## 示例

```
用户：帮我对比一下掉落转付费分支和 dev 的差异，生成一个 GSheet

AI：
1. 确认分支：source = origin/dev_X2-39183, target = origin/dev
2. 提取差异：11 个配置表有改动（排除 i18n）
3. 创建 Google Sheet：[链接]
4. 写入数据 + 精确着色
5. 图例：绿色 = 新增行 | 黄色 = 修改的单元格

用户：帮我看看 hotfix 和 dev 有什么区别

AI：
1. 确认分支：source = origin/hotfix, target = origin/dev
2. 执行同样的流程
```

---

*最后更新：2026-03-09*
