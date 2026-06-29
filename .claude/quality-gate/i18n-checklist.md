# i18n 多语言验收清单（type=i18n）

> task-checker 跑 i18n 验收时对照的**单一来源**。
> 标准真源 = memory `reference_x3_i18n_workflow` / `feedback_x3_i18n_backup_files` /
> `feedback_x2_i18n_duplicate_key`。

## 产物位置（marker 应带）
- `text_table`：改动的 Text 表（GSheet ID 或本地 Text.xlsx 路径）
- `data_dir`：跑 CompositeI18n 的 data 目录（用于 backup 污染扫描）

## 怎么读产物
- **GSheet/Text.xlsx**：gws / Read
- **data 目录**：Glob / Grep 扫文件名

## 客观项（直接判 pass/fail）

> **★泄漏审计走确定性脚本，别肉眼看**（2026-06-24 起）：X3 跑
> `python C:\Users\linkang\.claude\skills\x3-translation-automatic\scripts\i18n_leak_audit.py --changed`
> （只审本次 git diff HEAD 改动过的行；也可 `--grep <主题词>` / `--prefix <key前缀>` 按范围查）。
> 退出码 0=通过、1=有 block 泄漏。脚本一次覆盖下面 `泄漏审计` 三类 + `zh未转繁`(warn)，
> 自动排除符号/数字/标签/百分比/语言选择器等"各语言本就相同"的假阳性。**这条取代旧的肉眼 `未翻译占位`。**

| rule | level | 怎么查 |
|---|---|---|
| `key命名规范` | block | 新增 TXT_ key 必须符合 `TXT_{Table}_{Field}_{ID}` 命名；不符列出 |
| `backup隔离` | block | `data_dir` 下**不得**有 `_backup_*.xlsx`（跑 CompositeI18n 前必须移出，否则 key 冲突中断扫描）。命中即 fail |
| `泄漏审计·EN_LEAK` | block | 改动行 **cn之外的语言列==en英文原文**=只翻了中英、其余照抄英文（"伪完整"：单元格非空但没翻，`语言齐全` 查不出，肉眼最易漏）。`i18n_leak_audit.py --changed` 报 EN_LEAK 即 fail。2026-06 世界杯抽奖券1146/深海节16行高发 |
| `泄漏审计·CJK_LEAK` | block | 改动行 **非中日语言列含汉字**=中文泄漏没翻（脚本已排除 zh繁/jp日语汉字假阳性）。报 CJK_LEAK 即 fail |
| `泄漏审计·EMPTY` | block | 改动行目标语言列为空。报 EMPTY 即 fail（注意：只审**改动行**，不会被全表历史 jp 缺口刷屏） |
| `zh未转繁` | warn | 脚本 ZH_RAW：zh列==cn简体疑似未做简繁转换（换皮 clone 高发）。列出复核 |
| `无重复key` | warn | 同一 LC key 不应出现多行（fwcli/导入取首条 → 显示旧/错值）。发现重复列出 |
| `改名对齐` | warn | 道具/实体若改过名（换皮残留）：新名必须在 **title(全语言) + desc + drop/获取途径文案** 全部一致；旧名残留列出。2026-06 拓荒节"墨水盒"只改了 title-cn/zh，desc+drop 仍是旧名"纪念钻头"、其余语言抄英文，踩坑 |
| `换皮残留·RESIDUE` | block（换皮任务才查） | **换皮 clone 活动/礼包/规则时必查**：复用了源活动带文本ID（RuleTips/Title/Content/Pack名等）→ i18n 译文**完整但写的是源节日名**（世界杯累充 15013 全16语言译好却写"尼罗"；开箱 16031 乌克兰语整段元旦残留）。**完整性三类(EN/CJK/EMPTY)和肉眼都漏判**（非空、非泄漏、纯主题错）。跑 `i18n_leak_audit.py --reskin-residue --src-festival <源节日> --grep/--prefix <新ID范围>`（内置 nile/newyear/spring/valentine/deepsea/summer 词表，或 `--source-terms` 自定义多语言词）。报 RESIDUE 即 fail。2026-06-29 世界杯实证 |

## 主观项（标 level=human，不计 pass/fail）
- 译文质量 / 术语对齐
- 文案是否符合 UI game-copy 风格（短、祈使、无整句）

## fail-closed
读不到 Text 表 / 扫不了 data 目录 → 标 passed:false + 「需人工确认」，blocking_failures 带 cannot_verify，不放行。
