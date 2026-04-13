---
name: x2-config-download
description: >
  X2 GSheet 配置表下载子流程（ADHD仓库维护版）。支持全表下载和行筛选两种模式。
  含 fwcli 下载命令、本地化表(i18n)特殊处理、多表匹配规则、变动检查清单、
  格式校验脚本、ID 重复检测、跨表引用校验、精准行合并、条件子集（关键词筛选）正确顺序、表号→页签速查。
  由主 Skill gsheet_sync_skill.md 路由调用，不单独触发。
---

# X2 GSheet Skill - 下载配置表

> 由主 Skill `D:\UGit\x2gdconf\.cursor\skills\gsheet_sync\SKILL.md` 路由调用。
> 本文件维护于 ADHD 仓库（`c:\ADHD_agent\.cursor\skills\x2-config-download\SKILL.md`）。

---

## 两种模式识别

| 用户输入 | 模式 | 示例 |
|---------|------|------|
| 4 位数字编号（或逗号分隔多个） | **全表模式** | `2112`、`2011 2135` |
| 7 位及以上数字（行 ID） | **行筛选模式** | `211551451`、`211551451,211551452` |

> 行 ID 前 4 位即为表编号（如 `211551451` → 表 `2115`）。同一批多个 ID 若前缀不同，需分表处理。

---

## ⛔ NEVER 规则

| 禁止行为 | 原因 |
|---------|------|
| 页签-分支不匹配时直接提交 | dev 分支下载了 master 页签数据会导致版本混乱，必须先报警让用户确认 |
| 跳过格式校验直接 commit | 格式错误的配置上线后会导致客户端崩溃或数据异常 |
| i18n 表下载后手动运行 `gen_i18n.py` | fwcli 已内置 i18n 处理，手动运行会覆盖正确结果 |
| 多表匹配时不经用户确认全部提交 | 用户可能只需要其中部分表 |
| 条件子集提交时 **顺序搞反**（见 **第二节末「补遗：条件子集」**） | 应始终以 **HEAD 为合并主本**，从 GSheet 全表结果中 **只覆盖目标行**；禁止「整表覆盖工作区后再慢慢筛」导致 diff/暂存区像要提交全表 |

---

## 一、全表模式（5 步）

**流程**：
```
确认分支 → 下载 → 转换 → 检查变动 → 等待确认 → commit + push
```

### S1 确认分支
```powershell
git -C D:\UGit\x2gdconf branch --show-current
```
切换（如需）：
```powershell
git -C D:\UGit\x2gdconf checkout -q <branch>
git -C D:\UGit\x2gdconf pull -q
```

### S2 下载
```powershell
# 清空临时目录
if (!(Test-Path D:\UGit\x2gdconf\tmp_xlsx)) { New-Item -ItemType Directory D:\UGit\x2gdconf\tmp_xlsx }
Remove-Item D:\UGit\x2gdconf\tmp_xlsx\* -Force -ErrorAction SilentlyContinue

# 下载（多表用逗号分隔，fwcli 按表名模糊匹配）
.\tools\fwcli.exe googlexlsx -a . -d tmp_xlsx -r 1z2-AK4dFgdzd7U11uCgYzLpj3Qopkv9Rr-SbA7iLIMc -f <表名>

# 转换为 json
.\tools\fwcli.exe xlsxtojson -s fo/json -t tmp_xlsx -d fo/json -g all -o fo/s2c

# 生成配置数据
.\tools\s2ctool_win.exe --input fo/s2c --output fo/s2c
```
工作目录：`D:\UGit\x2gdconf`

### 本地化表（1011）
```powershell
.\tools\fwcli.exe googlexlsx -a . -d tmp_xlsx -r 1z2-AK4dFgdzd7U11uCgYzLpj3Qopkv9Rr-SbA7iLIMc -f 1011_x2_i18n
```
- 表名必须小写 `1011_x2_i18n`；耗时约 70 秒；**无需**运行 `gen_i18n.py`

### S3 检查变动（见第三节）

### S4 等待用户确认

### S5 提交推送
```powershell
git add .
python -c "msg = '[配置表] 更新 <页签> 配置\n\n变动摘要:\n- 新增: N 条\n- 修改: N 条\n- 删除: N 条'; open('commit_msg.txt', 'w', encoding='utf-8').write(msg)"
git commit -F commit_msg.txt
Remove-Item commit_msg.txt -Force
git push origin <branch>
```

---

## 二、行筛选模式（6 步）

用于只更新表中特定几行，其余行保持不变。

**流程**：
```
确认分支 → 备份 → 下载全表 → 精准行合并 → 验证 → commit + push
```

### S1 确认分支（同全表模式）

### S2 备份原始 TSV
```powershell
Copy-Item "D:\UGit\x2gdconf\fo\config\<页签>.tsv" "D:\UGit\x2gdconf\fo\config\<页签>.tsv.bak"
```

### S3 下载对应全表（同全表模式，按表编号下载）

### S4 精准行合并

先将脚本同步到 x2gdconf：
```powershell
Copy-Item "c:\ADHD_agent\.cursor\skills\P2-config-upload\scripts\merge_rows.py" "D:\UGit\x2gdconf\scripts\merge_rows.py" -Force
```

执行合并（只替换/新增目标行）：
```powershell
python D:\UGit\x2gdconf\scripts\merge_rows.py `
  "D:\UGit\x2gdconf\fo\config\<页签>.tsv" `
  "行ID1,行ID2,行ID3"
```

脚本输出：
- `[updated]` — 原文件有该行，已替换
- `[added]` — 原文件无该行，已追加
- `[WARN] not found anywhere` — GSheet 也没有，需检查

### S5 验证
```powershell
git -C D:\UGit\x2gdconf diff --stat
# 确认只有目标表有变动，且行 ID 正确：
git diff D:\UGit\x2gdconf\fo\config\<页签>.tsv | Select-String "^[-+][0-9]"
```

### S6 提交推送 + 清理备份
```powershell
Remove-Item "D:\UGit\x2gdconf\fo\config\<页签>.tsv.bak"
git add .
python -c "msg = '[配置表] 更新 <页签>-行筛选 配置\n\n变动摘要:\n- 更新行: <ID列表>'; open('commit_msg.txt', 'w', encoding='utf-8').write(msg)"
git commit -F commit_msg.txt
Remove-Item commit_msg.txt -Force
git push origin <branch>
```

### 补遗：条件子集（按关键词/列筛选，非用户手填行 ID）

典型需求：「先从 GSheet 拉全表，**再只提交**某类道具 / 名称含某某关键词的行」。

**正确顺序（必须）**

| 顺序 | 动作 |
|------|------|
| 1 基线 | 当前分支 **`HEAD` 的 `fo/config/<页签>.tsv` 为真值**；导表前先 **`Copy-Item` → `.bak`**（与上文 S2 一致）。 |
| 2 拉表 | `fwcli` → `xlsxtojson` → `s2ctool`，得到 GSheet **最新全表**（通常会写入 `fo/config/<页签>.tsv`）。可选：将全表结果 **另存** 为 `*.tsv.full` 再合并，避免与主本混淆。 |
| 3 合并（同一轮内完成） | 用脚本从全表结果中按规则解析出目标行（如 Comment 列含「限时抢购」），**仅这些行**覆盖进以 **HEAD（或 .bak）为主本** 的文件；其余行 **一字不改** 保留 HEAD。 |
| 4 验证 | `git diff` **只应出现**目标行，不应出现整表大规模 insert/delete。 |
| 5 提交推送 | `git add` → `commit` → `push`。 |

**错误顺序（禁止）**：先让 **整表** 长期占据工作区、与 HEAD 形成 **整张表级 diff**，再事后合并 —— 易误提交无关行，且与用户「只提交子集」的意图 **顺序相反**。

**与上文「行 ID 列表」的关系**：用户给 **规则/关键词** 时，脚本从全表结果 **解析出 ID** 后，仍按「HEAD 主本 + 行级覆盖」操作；逻辑同 `merge_rows.py`，**不要**先 commit 全表。

---

## 三、变动检查清单

### 1. 文件大小异常检测
```powershell
git diff --stat
```
- `Bin X → Y bytes`，若 **Y < X × 0.5** → ⚠️ **高亮报警，等待用户确认**
- 大量删除（deletions 远大于 insertions）→ ⚠️ **报警**

### 2. 详细变动分析
- **新增条目**：列出新增的 ID 和名称
- **修改条目**：对比修改前后差异
- **删除条目**：列出删除的 ID 和名称（⚠️ 重点关注）

### 3. 异常检测
- ⚠️ 文件大小骤降
- ❌ 活动配置、触发器被删除
- ❌ 空字段、测试数据（非 test1）
- ❌ ID/Key 重复
- ❌ 格式错误
- ⚠️ 名称含 "test"/"测试"（非 test1 页签）
- ⚠️ 活动触发器从自动循环改为手动

### 4. 格式校验脚本
```powershell
# 只检查本次有变动的文件
python scripts/check_tsv_format.py --all-changed

# 指定文件
python scripts/check_tsv_format.py fo/config/activity_config.tsv

# 跳过跨表引用（加速）
python scripts/check_tsv_format.py --all-changed --no-xref
```

### 5. 页签-分支匹配检查（从下载日志中读 tabname）

| 分支版本 | 页签标注 | 判断 |
|---------|---------|------|
| `dev*` | `master`/`hotfix` | ⚠️ 版本不匹配，报警 |
| `hotfix*` | `master`/`dev` | ⚠️ 版本不匹配，报警 |
| `master*` | `dev`/`hotfix` | ⚠️ 版本不匹配，报警 |

---

## 四、回复格式

```
✅ <编号>(<页签>) → <分支> 提交成功
commit: [配置表] 更新 <页签> 配置
📝 +X/-Y行：<摘要>
```

示例：
```
✅ 2112(activity_config) → dev_25festival 提交成功
commit: [配置表] 更新 2112_activity_config 配置
📝 +2/-2行：新增每日gacha礼包/大富翁活动条目
```

---

## 五、表号→页签速查

> X2 表索引来源：[x2_gsheet_config](https://docs.google.com/spreadsheets/d/1z2-AK4dFgdzd7U11uCgYzLpj3Qopkv9Rr-SbA7iLIMc/edit?gid=499616813)（`fw_gsheet_config` 页签）
> - C列格式：`<编号>_x2_<标识>`（fwcli `-f` 参数按编号模糊匹配）
> - D列：实际页签名（下载后的 `.tsv` 文件名）
> - 该 spreadsheetId 也是 fwcli 下载命令的 `-r` 参数值

| 编号 | 页签 | 编号 | 页签 |
|------|------|------|------|
| 1011 | i18n(x2_i18n) | 1013 | const_config |
| 1014 | statistical_data | 1111 | item |
| 1115 | vm | 1168 | get_access_group |
| 2011 | iap_config | 2012 | iap_param |
| 2013 | iap_template | 2014 | iap_coeffs |
| 2021 | iap_order | 2022 | iap_daily_specials |
| 2111 | activity_calendar | 2112 | activity_config |
| 2113 | activity_schema | 2114 | activity_rank_group |
| 2115 | activity_task | 2116 | activity_item_exchange |
| 2117 | activity_item_recycle | 2118 | activity_rank_rewards |
| 2119 | activity_ui_template | 2120 | activity_ui_module |
| 2121 | activity_special | 2122 | activity_rank_rule |
| 2123 | activity_popwindow | 2124 | activity_drop |
| 2125 | activity_discount | 2126 | activity_donate_lvl_up |
| 2130 | activity_battle_pass | 2131 | activity_battle_pass_level |
| 2134 | activity_create_entity | 2135 | activity_package |
| 2136 | activity_cycle_period | 2137 | activity_asset_retake |
| 2138 | activity_proto_module | 2139 | activity_shoot_hunt |
| 2141 | activity_without_gacha_pool | 2142 | activity_without_gacha_reward |
| 2143 | activity_fes_bp_module | 2144 | activity_hero_achievement |
| 2145 | activity_tips | 2151 | activity_monopoly_gacha_map |
| 2152 | activity_monopoly_gacha_reward | 2153 | activity_monopoly_gacha_dice |
| 2154 | activity_without_gacha_floor | 2156 | activity_floor_gacha |
| 2166 | activity_flash_sale_raffle | 2167 | activity_flash_sale_virtual |
| 2168 | activity_hud_entries | 2169 | activity_hud_entry_style |

> 查不到的新增表，用 gws 查索引（C列=编号_x2_标识，D列=页签名，E列=SheetID）：
> ```powershell
> $env:GOOGLE_WORKSPACE_PROJECT_ID = 'calm-repeater-489707-n1'
> gws sheets spreadsheets values get --params '{"spreadsheetId": "1z2-AK4dFgdzd7U11uCgYzLpj3Qopkv9Rr-SbA7iLIMc", "range": "fw_gsheet_config!A1:E600"}'
> ```
> fwcli `-f` 参数用 C 列的编号前缀（如 `2112`）模糊匹配，下载后的 tsv 文件名 = D 列页签名。
