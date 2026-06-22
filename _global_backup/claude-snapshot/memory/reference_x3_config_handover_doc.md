---
name: reference_x3_config_handover_doc
description: X3 配置知识库交接文档（分享给同事用）的位置；用户喊 update 时改这份，平时不主动更新
metadata: 
  node_type: memory
  type: reference
  originSessionId: cb23fa3f-3258-4c76-81e9-3a79ac7e068f
---

把分散的 X3 配置 memory 整合成的**单份交接文档**，给接手 X3 配置的同事看。

- KB 留底：`C:\Users\linkang\KB\X3配置知识库_交接版.md`
- 已推送到配置仓：`C:\x3\gdconfig\` 根目录同名文件，分支 `dev_festival`（2026-06-15，commit `8bc0bef`）
- 范围=核心配置：仓库路径 / 导表+xlsx-tsv gate / 各表写入规则与坑(Reward/TimeCycle/累充902/积分/Rank/Pack开启/MainBg/MailID) / 分支与合并 / 工具索引 / 收尾清单
- 来源 memory：[[reference_x3_config]] [[reference_x3_gdconfig_repo]] [[reference_x3_tsv_export_migration]] [[reference_x3_reward_table_rules]] [[reference_x3_recharge_isolation]] [[reference_x3_timecycle]] [[reference_x3_score_activity]] [[reference_x3_pack_open_mechanisms]] [[reference_x3_pack_panel_rendering]] [[reference_x3_pack_tab_icon]] [[feedback_x3_actv_mailid_check]] [[feedback_x3_branch_check]] [[feedback_x3_branch_strategy]] [[feedback_x3_timecycle_name_legacy]] [[workflow_x3_auto_jolt_export]] [[workflow_x3_protected_branch_mr]] [[workflow_x3_merge_conflict_audit]]

**维护约定**：用户明确说"不持续 update，喊我的时候再 update"——平时别主动改这份；用户要求时，改完 KB 副本同步覆盖仓库那份再 push。
