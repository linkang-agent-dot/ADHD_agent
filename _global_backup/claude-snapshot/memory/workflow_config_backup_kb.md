---
name: workflow-config-backup-kb
description: 配置改动的备份规范——按功能拆成自包含文件归 KB，脚本也进 KB，仓内 staging 导表成功后即删
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2685fb40-c6de-4bcb-93e6-9c6370345015
---

配置类改动（X3/X2/P2 换皮、改数值、配活动等）的**备份与暂存规范**，2026-06-18 周卡案用户拍板，后面所有 agent 照此做。

**Why:** 仓内临时 staging 易被别人 `git reset`/导表清理冲掉、且散落脚本+全表快照+json 没人看得懂；备份必须沉到 KB 且按功能可独立接管。

**How to apply:**
1. **备份归 KB 固定路径**，不留在仓里：`KB\产出-数值设计\{项目}_{节日}\{模块}_备份\`（数值方案路径见 [[reference_output_paths]]）。
2. **一个功能一个自包含备份文件**（`功能N_xxx_备份.md`）：每份含①该功能干了啥②**before→after 精确改动明细**（表/行/列/旧值新值）③恢复/重放方法。判据=**新 agent 单看一份就能恢复或重放该功能**，禁止只留时间线流水账。一个模块多个功能（如周卡=价格名称/本地化/奖池数值）就拆多份。
3. **脚本也进 KB**：apply/fill/i18n 等可执行脚本拷进备份目录的 `脚本\` 子目录（连同 patch_spec.json 等规格）。
4. **仓内 staging 只是临时工作副本**：`_staging_xxx\` 在 git 仓里跑改动→commit→导表；**导表成功(jolt SUCCESS)、产物已进 KB 后即删仓内 staging**（删前列清单，见 [[feedback_ask_before_modifying_user_content]]）。下次开干同模块=从 KB 取脚本+映射，重建临时 staging，循环。
5. 删仓内目录前先 `git status` 确认是未跟踪的 staging（别误删别人 WIP）。

范例：周卡换皮 `KB\产出-数值设计\X3_夏日恋语\周卡_备份\`（功能1价格名称/功能2本地化/功能3奖池数值 各一 .md + 脚本\）。关联收口接管化范式 [[workflow_handover_assetization]]。

## ★备份 snippet 搬进 live tsv 的搬运 checklist（跨节日复用·2026-06-22 深海节首批落地沉淀）
搬 KB 备份的 `新增*.tsv` 进 `C:\x3\gdconfig\tsv\` 时按序扫，每条都卡过导表：
1. **格式防线先扫**：每个 snippet 数据行 **列数==目标表数据行列数** + **新id在目标表不存在**（在**目标分支**上扫——切了分支占用不同！）。不符=补列/换高位id。
2. **数字列里的 TODO 占位文本必 scrub**：备份常把待定值写成 `<深海节抽奖券·待建>`/`【待补…】`(累充白名单col49/RankCfg MailID/抽奖券ItemID)→导表 `ConvertError`/`could not convert to int/float`。搬前全部换成真 id 或清空。
3. **空壳活动撤批**：只有 ActvOnline 行、没配对应 content 表(累充→ActvTask / BP→BattlePassScore)→`depend_checks: ContentID not existed` 挂。配全再搬，否则从批次撤掉。
4. **共享行别漏**：ActvGroup 入口行、被引用的 Reward/ChainPack 组、TC——backup 常只给模块自己的行漏共享行。Pack.TimeCycleID/ChainPack.TimeCycle 不能指不存在的 TC→用 **6001(永久)**；活动级 TC 配0 要 ActvType 在导表 `SKIP_TIMECYCLE_CHECK`(PostProcessData.py)。
5. **导表前必 sync xlsx**：`python scripts/sync_xlsx_tsv.py --from-tsv --files tsv/<改过的>.tsv`（否则 `ExportTable.py` 的 verify_xlsx_tsv 预检 abort）。⚠️openpyxl 重存会污染**同 xlsx 的其他页签**→该 xlsx 的子页签 tsv **带齐一起 sync**。验证用本地 `cd Tools/table_exporter && python ExportTable.py`（0 异常=过）。
6. **push 遇 dev_festival 分叉**：`git rebase origin/dev_festival`——仓内有 `tsv_merge_pro`/`xlsx_merge_pro` 智能合并驱动自动行级合数据；.py 走 git 3-way。rebase 后**重验导表**再 push+jolt。
