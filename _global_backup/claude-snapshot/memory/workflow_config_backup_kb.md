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
