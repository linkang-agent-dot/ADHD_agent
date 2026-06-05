# 配置/换皮验收清单（type=config）· v2

> task-checker 跑 config 验收时对照的**单一来源**。v2 改动：①给 checker 一个对抗性工作姿态 ②每条 block 必须**打印实际值当证据** ③加风险标注+命中记录 ④加一条开放项防清单老化。
> 标准真源 memory（背景，不是运行时必读）：`feedback_verification_end_to_end` / `feedback_x3_branch_check` / `reference_x3_reward_table_rules` / `feedback_x3_actv_mailid_check` / `reference_x3_tsv_export_migration` / `feedback_confirm_source_of_truth_before_edit`。

## 0 · 工作姿态（checker 先读，决定怎么跑下面每一条）
- **默认有罪**：假设这次改动**已经坏了**，你的任务是找出它怎么坏的；找不到证据证明它没坏，才给 pass。不要找"它对"的证据。
- **只信真源，不信摘要**：所有判定的输入是实际的 tsv / GSheet / git 状态，**不是 producer 写的"我改了啥"**。marker 字段（`expected_branch`/`changed_ids` 等）只用来定位"该查哪", 不用来当"已经对了"的结论。
- **每条 block 必须留证据**：输出里要带**实际读到的值**（分支名、seq 序列、MailID 值、三层各自的值）。不能只写 "pass"——没有贴出实际值的 pass 一律视为 cannot_verify。
- **失败模式驱动**：下表每条都对应一次真实事故；逐条按"它这次有没有再犯"去查，不是泛泛"看一眼对不对"。

## 1 · 认清 project（决定真源，错了全盘错）
| project | 真源 | 一句话为什么 |
|---|---|---|
| **X3** | `tsv`（`C:\x3\gdconfig\tsv\`），直接改 tsv | 导表只认 tsv，xlsx 仅备份 |
| **X2 / P2** | **QA GoogleSheet** | `GSheet→导表→本地tsv`；`D:\UGit\x2gdconf\fo\config\*.tsv` 是导表产物，**手改会被下次导表覆盖=白干** |

## 2 · 怎么读真源（命令自带，不依赖操作者记忆）
- 分支：X3 `git -C C:\x3\gdconfig branch --show-current`；X2/P2 `git -C D:\UGit\x2gdconf branch --show-current`
- X3 tsv：直接 Read/Grep `C:\x3\gdconfig\tsv\*.tsv`（不读 xlsx）
- X2/P2 GSheet：SheetID **现解** `python C:\ADHD_agent\.cursor\skills\google-workspace-cli\gsheet_query.py resolve <表号>`（禁硬抄 P2 KB id，id 空间重叠会静默返错数据）；读写经 `node C:\ADHD_agent\scripts\gws_stdin.js`

## 3 · 客观项（block/warn，直接判 pass/fail）
> 每行四列：**防什么事故(why)** / **怎么查(命令)** / **必须输出的证据** / **风险档·上次命中**。
> 证据列是硬要求：checker 输出里没有这一列对应的实际值 = 该项记 cannot_verify，不算 pass。

### block（任一 fail → 不放行）
| rule | 防什么事故(why) | 怎么查 | 必须输出的证据 |
|---|---|---|---|
| `改对地方(真源)` | X2/P2 手改 tsv 被导表冲掉，改了等于没改 | X2/P2：`git -C D:\UGit\x2gdconf diff --name-only`；看是否手改 `fo/config/*.tsv`、`fo/i18n/*.tsv` 且无对应 QA GSheet 写入证据。X3：N/A | diff 的文件列表 + （X2/P2）对应 GSheet 写入凭证；X3 标注 "tsv即真源,N/A" |
| `分支正确` | 错分支提交（X3NEW-736 事故） | `git branch --show-current` | **打印实际分支名 + expected_branch，两个值并列**；不等=fail |
| `引用ID存在` | drop/exchange/task/rank/jump 等 ID 在 QA 表不存在→线上报错/空奖励 | **直接跑 `activity-check` skill**，别重造 | activity-check 报告原文 + 缺失 ID 清单（空=pass） |
| `Reward表seq连续` | 同 RewardID 内 seq 跳号→服务端静默吞奖励；DropPara 空→发放异常 | Grep 改动的 Reward 表，按 RewardID 分组取 seq 列 | **每个改动 RewardID 的 seq 实际序列**（如 `1,2,3`）+ 断号/缺 DropPara 的行号 |
| `MailID必填` | ActvOnline 漏配 MailID→4 处 `MailID==0` 守卫静默吞未领奖励 | 读改动的 ActvOnline 行 MailID 列（除 ActvType=8） | **每行的 ActvType + MailID 实际值**；为 0/空=fail（默认应 101109） |
| `换皮无退役ID引用` | 整行替换/复用旧表时引用了已退役 id（city_skin→item、drop chain 等），线上指向空资源 | 对本次新增/改动的引用字段，反查被引 id 在当前 QA 表是否仍活跃（非退役段） | **被检查的引用字段 → 目标 id → 该 id 在表中的存活状态**逐条列出 |

### warn（不阻断，但必须报出来）
| rule | 防什么 | 怎么查 | 证据 |
|---|---|---|---|
| `三层一致` | 只改一层→线上跑旧值 | 给了 sheet_id 时：GSheet ↔ tsv ↔ 已 push 分支，比对关键行数/ID 集合 | **三处各自的值/行数并列贴出**；没给 sheet_id 则标 "skipped:no_sheet_id" |
| `导表无夹带` | X2/P2 全表模式夹带他人未验证改动 | 导表后 commit diff 应只含本次 `changed_ids` | diff 里的行 ID 集合 vs changed_ids；超出部分列出 |
| `命名/IDPack段规范` | 新 Pack/ID 落错节日 ID 段 | 对照 `reference_x3_config` 的 ID 段 | 新增 id + 应落段 + 实际段 |

## 4 · 开放项（防清单老化 —— 每次必跑，结果回灌清单）
- **`清单外失败方式`**（level=warn）：跑完上面所有项后，问一句——
  > "这次改动有没有上面 9 条**没覆盖**的失败方式？（新表类型 / 新引用链 / 这个活动形式特有的坑）"
  - 找到 → 在 review_summary 里写明，并**作为候选新规则**报给人；人确认后才加进 §3（不是自动膨胀）。
  - 这条保证：清单只装已知坑，但每轮都在主动找未知坑。

## 5 · 风险记录与剪枝（防清单肥胖 —— 有进有出）
- §3 每条结尾的「上次命中」由人维护：命中一次就记日期。
- **连续 ≥10 轮 config 验收都没 fire 过的 block 项 → 评审是否降级为 warn 或删除**（除非它防的是 P0 事故，P0 永久保留）。
- 当前命中记录（初始）：`分支正确`=X3NEW-736 / `MailID必填`=2026-05 / `Reward表seq连续`=2026-05夏日210921 / 其余=待记录。

## 6 · fail-closed
读不到 tsv / git 报错 / activity-check 跑不了 / 该出的证据值拿不到 → 标 `passed:false` + 「需人工确认」，`blocking_failures` 带 `cannot_verify`，**不放行**。
