# i18n 多语言验收清单（type=i18n）· v2

> task-checker 跑 i18n 验收时对照的**单一来源**。v2 改动：①加 §0 工作姿态 ②每条 block 必须**贴出实际 key/值**当证据 ③内联「防什么坑」 ④加开放项 + 剪枝。
> 标准真源 = memory `reference_x3_i18n_workflow` / `feedback_x3_i18n_backup_files` / `feedback_x2_i18n_duplicate_key`。

## 0 · 工作姿态（checker 先读）
- **默认有罪**：假设这次翻译**有 key 没翻、有重复、有改名残留**，去揪出来；找不到才 pass。
- **只信 Text 表/data 目录实际内容**，不信 producer "我翻全了"。
- **每条必须贴证据**：命中要列出**具体 key + 实际值**（哪个 key、哪几列、值是什么）。只写 "fail" 不贴 key、或只写 "pass" 不说扫了哪些 key = cannot_verify。
- **失败模式驱动**：下表每条对应一次真实坑（墨水盒改名案等），逐条查"这次有没有再犯"。

## 1 · 产物位置（marker 应带）
- `text_table`：改动的 Text 表（GSheet ID 或本地 Text.xlsx 路径）
- `data_dir`：跑 CompositeI18n 的 data 目录（用于 backup 污染扫描）

## 2 · 怎么读产物
- **GSheet/Text.xlsx**：gws / Read（中文按行号范围读，gws stdout 是 GBK 关键词易乱码）
- **data 目录**：Glob / Grep 扫文件名

## 3 · 客观项（直接判 pass/fail）
### block
| rule | 防什么坑(why) | 怎么查 + 该贴的证据 |
|---|---|---|
| `key命名规范` | 命名不符→导入/查找对不上 | 新增 TXT_ key 须符合 `TXT_{Table}_{Field}_{ID}`。**证据：不符的 key 逐个列出 + 它错在哪段**。 |
| `backup隔离` | `_backup_*.xlsx` 在 data 目录→key 冲突中断 CompositeI18n 扫描 | Glob `data_dir` 下 `_backup_*.xlsx`，有即 fail。**证据：命中的文件全路径**。 |

### warn
| rule | 防什么坑(why) | 怎么查 + 该贴的证据 |
|---|---|---|
| `无重复key` | 同 LC key 多行→fwcli/导入取首条→显示旧/错值 | 扫同一 LC key 是否多行。**证据：重复的 key + 各行所在位置/值**。 |
| `语言齐全` | 目标语言列空缺→线上缺字 | 新增 key 目标语言列无空缺(按项目语种数)。**证据：有空列的 key + 缺哪几列**。 |
| `未翻译占位` | 非拉丁语列(jp/kr/ru/ar/th)=en 值=只填英文兜底没真翻；`语言齐全`查不出(非空) | 改动的 key：比对非拉丁列是否等于 en 值，命中 ≥4 即列出。**X2 EVENT/换皮新增 key 高发(常只填 cn/zh、其余抄 en)**。**证据：占位的 key + 哪几列=en**。 |
| `改名对齐` | 道具/实体改名(换皮残留)只改了部分文案 | 改过名的实体：新名须在 **title(全语言)+desc+drop/获取途径文案** 全一致，旧名残留列出。**证据：旧名残留的 key+列+原文**。2026-06 拓荒节"墨水盒"只改 title-cn/zh，desc+drop 仍是旧名"纪念钻头"、其余语言抄英文——典型。 |

## 4 · 开放项（防老化，每轮必跑）
- **`清单外失败方式`**（warn）：跑完上面后问——"这次翻译有没有上面 6 条没覆盖的坑？(新语种规则/新的导入工具行为/这个表特有的 key 结构)"。找到 → 写 review_summary + 报人确认是否加成正式规则（人确认才加，不自动膨胀）。

## 5 · 剪枝 + 命中记录（防肥胖）
- 每条命中记日期。连续 ≥10 轮没 fire 的非 P0 项 → 评审降级/删除。
- 当前记录：`改名对齐`=2026-06拓荒节墨水盒 / `backup隔离`=见 feedback_x3_i18n_backup_files / 其余=待记录。

## 6 · 主观项（标 level=human，不计 pass/fail）
- 译文质量 / 术语对齐；文案是否符合 UI game-copy 风格（短、祈使、无整句）

## 7 · fail-closed
读不到 Text 表 / 扫不了 data 目录 / 该贴的证据拿不到 → 标 passed:false + 「需人工确认」，blocking_failures 带 cannot_verify，不放行。
