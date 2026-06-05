# 配置/换皮验收清单（type=config）

> task-checker 跑 config 验收时对照的**单一来源**。
> 标准真源 = memory `feedback_verification_end_to_end` / `feedback_x3_branch_check` /
> `reference_x3_reward_table_rules` / `feedback_x3_actv_mailid_check` / `reference_x3_tsv_export_migration` /
> `feedback_confirm_source_of_truth_before_edit`（各项目真源不同）。

> ⚠️ **真源因项目而异，验收前先认清 `project`**：
> - **X3** → 真源 = `tsv`（`C:\x3\gdconfig\tsv\`），直接改 tsv。
> - **X2 / P2** → 真源 = **GoogleSheet**，`GSheet → 导表 → 本地 tsv`；`D:\UGit\x2gdconf\fo\config\*.tsv` 是**导表产物**，手改会被下次导表覆盖（=白干）。改动必须落在 QA GSheet。

## 产物位置（marker 应带）
- `project`：x2 / x3 / p2 —— **决定真源**（x3=tsv真源；x2/p2=GSheet真源），路由下面的「改对地方」判定
- `expected_branch`：本期预期分支名（如节日分支）
- `tsv_changed`：本次改动的 tsv 表路径（X3 在 `C:\x3\gdconfig\tsv\`）
- `sheet_id`（可选）：设计源 / QA GSheet，用于三层一致比对

## 怎么读产物
- **分支**：X3 `git -C C:\x3\gdconfig branch --show-current`；X2 `git -C D:\UGit\x2gdconf branch --show-current`
- **TSV**：X3 直接 Read / Grep `C:\x3\gdconfig\tsv\*.tsv`（真源是 tsv，不读 xlsx）
- **X2/P2 真源 GSheet**：SheetID **现解** `python C:\ADHD_agent\.cursor\skills\google-workspace-cli\gsheet_query.py resolve <表号>`（禁硬抄 P2 KB 的 id），读写经 `node C:\ADHD_agent\scripts\gws_stdin.js`
- **GSheet**（三层比对时）：`node C:\ADHD_agent\scripts\gws_stdin.js`

## 客观项（直接判 pass/fail）
| rule | level | 怎么查 |
|---|---|---|
| `改对地方(真源)` | block | **X2/P2(project=x2/p2)**：跑 `git -C D:\UGit\x2gdconf diff --name-only` —— 若 `fo/config/*.tsv` / `fo/i18n/*.tsv` 出现手改、且无对应 QA GSheet 写入证据 → **fail**（X2/P2 真源是 GSheet，手改 tsv 会被导表覆盖）。X3 此项 N/A（X3 tsv 即真源） |
| `分支正确` | block | `git branch --show-current` == `expected_branch`。不符直接 fail（防 X3NEW-736 类错分支） |
| `引用ID存在` | block | drop / exchange / task / rank / jump 等 ID 在对应 QA 表存在——**直接走现成的 `activity-check` skill**，别重造。它报的缺失项即本规则的 fail |
| `Reward表seq连续` | block | 改动的 Reward 表里，同一 RewardID 内 seq 必须从 1 连续无跳号；DropPara 必填非空 |
| `MailID必填` | block | 改动的 ActvOnline 行，除 ActvType=8 外 MailID 必须填（默认 101109），为 0/空即 fail |
| `三层一致` | warn | 给了 sheet_id 时：GSheet ↔ tsv ↔ 已 push 分支，关键行数/ID 集合一致；没给 sheet_id 跳过并标注 |
| `导表无夹带` | warn | X2/P2 功能验证/bugfix 类任务：导表后的 commit diff 应**只含本次改动的行ID**。若 diff 里出现大量与本任务无关的行（他人 GSheet 改动）→ warn：疑似误用「全表模式」夹带未验证改动，应改用行筛选模式（merge_rows 只合目标行）。marker 带 `changed_ids` 时按它核对 |
| `命名/IDPack段规范` | warn | 新增 Pack/ID 落在节日规定的 ID 段（见 reference_x3_config） |

## 主观项（标 level=human，不计 pass/fail）
- 数值合理性（流量侧该改 / 变现侧不改，权重·floor·期望值）—— 靠你判
- 换皮是否漏了某处美术 Icon（Pack.MainBg / PackTypeInfo.Icon 等多处）

## fail-closed
读不到 tsv / git 报错 / activity-check 跑不了 → 标 passed:false + 「需人工确认」，blocking_failures 带 cannot_verify，不放行。
