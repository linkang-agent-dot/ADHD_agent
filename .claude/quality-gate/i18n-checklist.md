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
| rule | level | 怎么查 |
|---|---|---|
| `key命名规范` | block | 新增 TXT_ key 必须符合 `TXT_{Table}_{Field}_{ID}` 命名；不符列出 |
| `backup隔离` | block | `data_dir` 下**不得**有 `_backup_*.xlsx`（跑 CompositeI18n 前必须移出，否则 key 冲突中断扫描）。命中即 fail |
| `无重复key` | warn | 同一 LC key 不应出现多行（fwcli/导入取首条 → 显示旧/错值）。发现重复列出 |
| `语言齐全` | warn | 新增 key 的目标语言列无空缺（按项目要求的语种数） |
| `未翻译占位` | warn | 改动的 key：**非拉丁语言列(jp/kr/ru/ar/th)若等于 en 值 = 没翻译、只填了英文兜底**（单元格非空但是占位，`语言齐全` 查不出）。命中 ≥4 即列出。X2 EVENT/换皮新增 key 高发：常只填 cn/zh、其余抄 en |
| `改名对齐` | warn | 道具/实体若改过名（换皮残留）：新名必须在 **title(全语言) + desc + drop/获取途径文案** 全部一致；旧名残留列出。2026-06 拓荒节"墨水盒"只改了 title-cn/zh，desc+drop 仍是旧名"纪念钻头"、其余语言抄英文，踩坑 |

## 主观项（标 level=human，不计 pass/fail）
- 译文质量 / 术语对齐
- 文案是否符合 UI game-copy 风格（短、祈使、无整句）

## fail-closed
读不到 Text 表 / 扫不了 data 目录 → 标 passed:false + 「需人工确认」，blocking_failures 带 cannot_verify，不放行。
