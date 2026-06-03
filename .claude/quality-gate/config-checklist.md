# 配置/换皮验收清单（type=config）

> task-checker 跑 config 验收时对照的**单一来源**。
> 标准真源 = memory `feedback_verification_end_to_end` / `feedback_x3_branch_check` /
> `reference_x3_reward_table_rules` / `feedback_x3_actv_mailid_check` / `reference_x3_tsv_export_migration`。

## 产物位置（marker 应带）
- `expected_branch`：本期预期分支名（如节日分支）
- `tsv_changed`：本次改动的 tsv 表路径（在 `C:\x3\gdconfig\tsv\`）
- `sheet_id`（可选）：设计源 GSheet，用于三层一致比对

## 怎么读产物
- **分支**：`git -C C:\x3\gdconfig branch --show-current`
- **TSV**：直接 Read / Grep `C:\x3\gdconfig\tsv\*.tsv`（真源是 tsv，不读 xlsx）
- **GSheet**（三层比对时）：`node C:\ADHD_agent\scripts\gws_stdin.js`

## 客观项（直接判 pass/fail）
| rule | level | 怎么查 |
|---|---|---|
| `分支正确` | block | `git branch --show-current` == `expected_branch`。不符直接 fail（防 X3NEW-736 类错分支） |
| `引用ID存在` | block | drop / exchange / task / rank / jump 等 ID 在对应 QA 表存在——**直接走现成的 `activity-check` skill**，别重造。它报的缺失项即本规则的 fail |
| `Reward表seq连续` | block | 改动的 Reward 表里，同一 RewardID 内 seq 必须从 1 连续无跳号；DropPara 必填非空 |
| `MailID必填` | block | 改动的 ActvOnline 行，除 ActvType=8 外 MailID 必须填（默认 101109），为 0/空即 fail |
| `三层一致` | warn | 给了 sheet_id 时：GSheet ↔ tsv ↔ 已 push 分支，关键行数/ID 集合一致；没给 sheet_id 跳过并标注 |
| `命名/IDPack段规范` | warn | 新增 Pack/ID 落在节日规定的 ID 段（见 reference_x3_config） |

## 主观项（标 level=human，不计 pass/fail）
- 数值合理性（流量侧该改 / 变现侧不改，权重·floor·期望值）—— 靠你判
- 换皮是否漏了某处美术 Icon（Pack.MainBg / PackTypeInfo.Icon 等多处）

## fail-closed
读不到 tsv / git 报错 / activity-check 跑不了 → 标 passed:false + 「需人工确认」，blocking_failures 带 cannot_verify，不放行。
