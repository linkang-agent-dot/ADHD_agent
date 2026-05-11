---
name: p2-config-upload
description: P2配置表上传工具。支持全表下载和行筛选两种模式，从 Google Sheet 下载配置表并提交到 gdconfig 仓库。内置 898 张表的编号→页签映射。表 1011（i18n）**使用 GSheetDownloader.exe 处理，`成功: 0` 是正常的（i18n 不计入常规表计数）**。当用户提到"P2导表"、"传表"、"导表"、"上传配置"、或给出数字编号+分支时使用。
---

# P2 配置表上传工具

触发词：P2导表、传表、导表、上传配置、用户给数字编号+分支

## 表 1011（i18n）说明

**1011 使用 GSheetDownloader.exe 正常处理，与其他表走相同流程（S1–S5）。**

**关键点**：
- `成功: 0, 失败: 0` 是**正常输出**——这两个计数只统计非 i18n 的普通表，i18n 表另路处理，不影响结果
- GSheetDownloader 处理 1011 后会输出各页签（LEADERBOARD/STORY/QUEST/EVENT 等）的 `i18n_process` 日志，正常结束后提交推送

**⛔ 禁止替代方案**：
- `i18n_dl_utf8.py` 输出格式与 GSheetDownloader **不同**（行排序不同、`\n` 处理不同），会产生大量无效 diff，**禁止用作替代**（2026-04-29 验证）

---

## 两种模式

- **全表模式**：用户只给表编号（如 `2115`），下载整张表并提交
- **行筛选模式**：用户给出具体行 ID（如 `211552039`），只更新指定行，其余行保持不变

> 识别方式：若用户给出的数字位数 ≥ 7 位，则视为行 ID，触发行筛选模式；否则为表编号。

---

## 执行顺序（全表模式，5步）

**S1 确认分支**
```powershell
git -C C:\gdconfig branch --show-current
```
切换：`git -C C:\gdconfig checkout -q <branch>; git -C C:\gdconfig pull -q`

**S2 下载**

多个编号用**空格分隔**，一次性下载：

```powershell
# 单个表
echo "1`n1111`nn" | & "C:\gdconfig\scripts\GSheetDownloader.exe"

# 多个表（空格分隔，一次下载）
echo "1`n1168 1111`nn" | & "C:\gdconfig\scripts\GSheetDownloader.exe"
```

> 用户输入如 `1168 1111`（空格分隔），直接拼成空格分隔的编号串一次传入。

**S3 校验下载结果 ⚠️ 必须执行，不得跳过**

每次 GSheetDownloader 执行完毕后，**必须**读取输出日志的最后 15 行，检查是否下载成功：

```powershell
# 读取下载日志末尾（日志路径为 Shell 工具返回的 agent-tools/*.txt）
# 在末尾找以下关键词：
#   成功: X  → X 应等于下载表数量
#   失败: X  → X 应为 0
#   ! json error on row  → 表示 GSheet 数据有 JSON 格式错误
#   下载完成: <页签名>  → 用于页签名检测
```

**判定规则**：
- ✅ `成功: N, 失败: 0` 且 N > 0 且**无** `json error` → 下载成功，继续 S3.5
- ❌ 出现 `! json error on row X col Y : 列名` → **下载失败**，立即停止并报告：
  ```
  ⚠️ 下载失败：<表编号>(<页签>) 第 X 行 列 Y (列名) JSON 格式错误
  错误详情：<错误描述>
  请在 GSheet 中修正该行后重新下载。
  ```
- ❌ `成功: 0` 或 `失败: X>0` → **下载失败**，报告错误，不提交
- ⚠️ **绝对禁止**：当下载失败时，因为 `git diff` 无变动就告诉用户"已是最新"。无变动 + 下载失败 = 下载没生效，必须告知用户下载出错了。

**S3.5 页签名检测 ⚠️ 必须执行**

> **页签历史不落仓库**：`tab_history.py` 将记录写入本机目录（Windows：`%LOCALAPPDATA%\P2GSheetTabHistory\tab_history.json`），**禁止**提交到 gdconfig 分支。若环境变量 `P2_TAB_HISTORY_FILE` 已设置，则使用该路径。若仓库根目录曾误生成过 `tab_history.json`，应从版本库移除并加入 `.gitignore`：`git rm --cached tab_history.json`（如已跟踪）。

从日志末尾提取每张表的实际页签名（日志格式：`下载完成: <页签名>`），然后运行检测脚本：

```powershell
# 禁止把 tab_history 放进 gdconfig 仓库（不要 Copy 到 C:\gdconfig\scripts\）。直接调用个人项目脚本，JSON 落在 %LOCALAPPDATA%\P2GSheetTabHistory\
python "c:\ADHD_agent\.cursor\skills\P2-config-upload\scripts\tab_history.py" check <table_id> <tab_name>
```

**判定规则**：
- ✅ exit 0 → 页签名未变化或首次记录，继续 S4
- ❌ exit 1（输出 `⚠️ 页签名变化！`）→ **立即停止并询问用户**：
  ```
  ⚠️ 检测到表 <table_id> 的页签名发生变化：
  上次：<old_tab>
  本次：<new_tab>
  
  请确认是否继续？这可能意味着表结构已调整。
  ```
  等待用户确认后再继续。

下载成功且用户确认后，更新记录：
```powershell
python "c:\ADHD_agent\.cursor\skills\P2-config-upload\scripts\tab_history.py" update <table_id> <tab_name>
```

**S4 查看改动 ⚠️ 必须输出摘要给用户**

```powershell
# 1. 统计文件变动
git -C C:\gdconfig diff --stat

# 2. 列出变动行 ID（带注释字段，截断到 80 字符）
git -C C:\gdconfig diff fo/config/<页签>.tsv | Select-String "^[-+][0-9]" | ForEach-Object { $_.Line.Substring(0, [Math]::Min(80, $_.Line.Length)) }
```

> - `A_INT_group` 在第0列时：取 `$cols[0]` 为行标记，`$cols[1]` 为 ID
> - `A_INT_id` 在第0列时：取 `$cols[0]` 为行标记，后续列为字段
> - diff 极长（>50行）时加 `| Select-Object -First 60`

**提交前必须向用户输出**（格式见"回复格式"节）：变动了哪些 ID、字段改动是什么。

**S5 提交推送**
```powershell
# 默认只 add fo/，避免误将根目录工具状态文件（如历史遗留的 tab_history.json）提交进分支；若本次还改了其它已跟踪路径再显式 git add 该路径
git -C C:\gdconfig add fo/
# ⚠️ 不能用 -m 直接传中文（PowerShell 编码不保证 UTF-8 → 乱码），必须写临时文件再用 -F
$msg = "[配置更新]<页签>-<分支>-<五字>"
$tmpFile = "$env:TEMP\git_commit_msg.txt"
[System.IO.File]::WriteAllText($tmpFile, $msg, [System.Text.Encoding]::UTF8)
git -C C:\gdconfig commit -F $tmpFile; git -C C:\gdconfig pull -q --rebase; git -C C:\gdconfig push
```

---

## 执行顺序（行筛选模式，6步）

行 ID 前缀即表编号（如 `211552039` → 表 `2115`），注意同一批里**不同前缀要分表处理**。

**S1 确认分支**（同全表模式）

**S2 备份原始 TSV**
```powershell
Copy-Item "C:\gdconfig\fo\config\<页签>.tsv" "C:\gdconfig\fo\config\<页签>.tsv.bak"
```

**S3 下载对应表**（同全表模式，按表编号下载）

> ⚠️ 下载完成后**必须**按全表模式 S3 的校验规则检查日志末尾，确认下载成功。若出现 `json error` 或 `成功: 0`，立即停止并报告错误，不执行后续步骤。
> 同样执行全表模式 **S3.5 页签名检测**，若页签名变化则先询问用户确认。

**S4 精准行合并**

脚本存放于 `c:\ADHD_agent\.cursor\skills\P2-config-upload\scripts\merge_rows.py`（个人项目源），使用前先同步到 gdconfig：

```powershell
Copy-Item "c:\ADHD_agent\.cursor\skills\P2-config-upload\scripts\merge_rows.py" "C:\gdconfig\scripts\merge_rows.py" -Force
```

然后执行，只替换/新增目标行，其余行保持不变：

```powershell
python C:\gdconfig\scripts\merge_rows.py `
  "C:\gdconfig\fo\config\<页签>.tsv" `
  "行ID1,行ID2,行ID3"
```

脚本会输出每行的处理状态：
- `[updated]` — 原文件有该行，已用新版本替换
- `[added]` — 原文件无该行，已追加到末尾
- `[WARN] not found anywhere` — 新下载的 TSV 中也没有该行，跳过（需检查 GSheet）

> **注意**：脚本自动检测 `A_INT_id` 所在列（支持第1列或第2列），无需手动指定。

---

## 常见问题排查

### GSheetDownloader 显示"成功: 0"但无报错

原因：目标表的 GSheet 中存在 JSON 格式错误的行，Downloader 解析到该行时停止，整张表 0 成功。

**排查步骤**：
1. 看错误信息中的 `row X col Y : 列名`，定位到出错的行号和列名
2. 用 gws 读取 GSheet 对应行：
```powershell
$env:GOOGLE_WORKSPACE_PROJECT_ID = 'calm-repeater-489707-n1'
python -c "
import subprocess, json
GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
params = json.dumps({'spreadsheetId': '<sheet_id>', 'range': '<tab>!A<row-2>:F<row+2>'})
r = subprocess.run([GWS, 'sheets', 'spreadsheets', 'values', 'get', '--params', params], capture_output=True, text=True, encoding='utf-8')
data = json.loads(r.stdout)
for row in data.get('values', []):
    print(row[0], '|', row[4][:100] if len(row) > 4 else '')
"
```
3. 常见原因：配置行中有 `{填数量}` 等占位符未替换，导致 JSON 数值字段是字符串
4. 让用户在 GSheet 里修正后重新下载

### 1011 i18n：策划说「线上表」有改，但 `fo/i18n` 无 git diff

> **Agent 行为**：可用 GSheetDownloader.exe 正常传 1011，`成功: 0` 不代表失败（i18n 不计入常规表计数）。

**原因（机制）**：GSheetDownloader **不会**自动去读你口头说的「线上一张表」。它只读 `C:\gdconfig\scripts\gsheet_config.ini` 里 **`gsheet_config_id` 指向的那份「配置索引表」**，从中解析 **1011 → i18n** 绑定的 **Spreadsheet ID + 各语言子页签 gid**，再逐 tab 下载并 **merge** 进 `fo/i18n/*.tsv`。

若差异实际写在 **另一本 Spreadsheet**、或 **同一本里未挂进索引的子表**、或 **索引行仍指向旧 sheet**，则导出结果会与当前 hotfix 仓库里已有文件 **完全一致** → `成功: 0`（无新写入）且无 diff。**这不是「没传」而是「工具读的数据源就不是你以为的那张线上表」。**

**排查**：
1. 打开索引表，找到 **1011 / i18n** 对应行，核对 **sheet_id 与各 tab** 是否与策划正在改的「线上」为**同一链接**。
2. 若线上已换表或新增 tab：需 **改索引** 或 **把内容合并进索引已指向的 tab**，再重下 1011。
3. 若索引正确仍无 diff：用 gws 对 **索引里的 sheet** 拉一行 key 与本地 `cn.tsv` 同一 key 对比，确认 API 导出是否真与表上所见一致（排除看错 tab / 未保存 / 权限视图）。

**原因（导出层，易与「索引指错表」混淆）**：1011 会按 **很多子页签** 异步拉取；日志里若出现 **`400 Bad Request`**、**某个 gid/tab 导出失败**、或仅部分语言更新，Downloader 仍可能对整批打出 **「成功: N, 失败: 0」** 之类汇总，但 **`fo/i18n` 实际未写入新行** → `git diff fo/i18n` 为空。**禁止**在「用户明确说表上已加 key」时，仅凭 **无 diff** 就结论「表上没变动」；必须先 **通读当次下载日志**（检索 `400`、`Bad Request`、失败 tab 名），并遵守上文 S3：**无 diff + 日志里有导出失败 = 下载未生效，不是策划没改。**

**原因（编码层，Windows 常见）**：日志若出现 **`'gbk' codec can't encode character`**（例如在 **`HERO`** 页签写 **`po.tsv`** 时遇到阿拉伯文 **`U+0625`** 等），说明 Downloader **按 GBK 写文件**，无法表示该 Unicode 字符 → 该页签处理失败，末尾常伴随 **`一些标签页处理失败`**，且汇总 **`成功: 0`**（整表未计入成功保存）。此时 **`fo/i18n` 无 diff 是工具失败，不是表上无新文案**。修复方向：让维护者把 GSheetDownloader **写出 TSV 改为 UTF-8**（或修正表中错列的字符）；临时可换用能完整跑通导出的环境/版本，或由策划把异常字符改到正确语言列。

### `[WARN] not found anywhere` — 行在 GSheet 存在但找不到

原因有两种：
1. **行在非主表 tab**：GSheetDownloader 只读取主 tab（通常是 `activity_event_pkg` 等第一个 tab）；用户若把新行添加到了临时/审核 tab，Downloader 读不到
2. **GSheetDownloader 因 json 错误提前退出**：同上，先排查 json 格式问题

解决：让用户把行移到主 tab，或直接在本地 TSV 手动写入后提交。

**S5 验证**
```powershell
git -C C:\gdconfig diff --stat
```
确认只有目标表的 fo/config/<页签>.tsv 有变动。用以下命令检查变更行 ID：
```powershell
git diff C:\gdconfig\fo\config\<页签>.tsv | Select-String "^[-+][0-9]"
```

**S6 提交推送 + 清理备份**
```powershell
Remove-Item "C:\gdconfig\fo\config\<页签>.tsv.bak"
git -C C:\gdconfig add fo/
# ⚠️ 不能用 -m 直接传中文（PowerShell 编码不保证 UTF-8 → 乱码），必须写临时文件再用 -F
$msg = "[配置更新]<页签>-<分支>-行筛选"
$tmpFile = "$env:TEMP\git_commit_msg.txt"
[System.IO.File]::WriteAllText($tmpFile, $msg, [System.Text.Encoding]::UTF8)
git -C C:\gdconfig commit -F $tmpFile; git -C C:\gdconfig push
```

---

## 编号→页签速查

**MUST：** 用 Read 工具按需查询，不要提前加载全表到上下文。

```
Read: c:\ADHD_agent\.cursor\skills\P2-config-upload\references\table_index.md
```

查不到说明是新增表，用 gws 查询索引表：
```powershell
$env:GOOGLE_WORKSPACE_PROJECT_ID = 'calm-repeater-489707-n1'
gws sheets spreadsheets values get --params '{"spreadsheetId": "1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c", "range": "fw_gsheet_config!A1:F600"}'
```

表中也包含每张表的 Google Sheet ID（SheetID 完整索引）。

## 回复格式（⚠️ 每次提交后必须输出，不得省略）
```
✅ <编号>(<页签>) → <分支> 提交成功
commit: [配置更新]<页签>-<分支>-<五字>
📝 +X/-Y行：
  - ID <行ID>：<字段名> 从「旧值摘要」→「新值摘要」
  - ID <行ID>：新增行，<简短描述>
  - ...（每条变动单独一行，自然语言，不贴原始 TSV）
```

**示例**：
```
✅ 2115(activity_task) → bugfix 提交成功
commit: [配置更新]activity_task-bugfix-前置条件修改
📝 +4/-4行：
  - ID 211587297：fincond 新增前置条件 actvtask 211587370 ≥1
  - ID 211587298：fincond 新增前置条件 actvtask 211587371 ≥1
  - ID 211587299：fincond 新增前置条件 actvtask 211587372 ≥1
  - ID 211587300：fincond 新增前置条件 actvtask 211587373 ≥1
```
