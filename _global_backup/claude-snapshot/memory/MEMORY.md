# Project Memory

## 复盘报告
- [X2 2026占星节模块回归报告](project_x2_star_festival_2026_report.md) — 7页签HTML报告，含R级分层/优化动作，生成脚本 `_gen_full.py`，2026-05-25归档

## Key Directories
- `C:\ADHD_agent\` — 主工作仓库，包含游戏运营数据分析、活动复盘、skill 脚本等
- `C:\ADHD_agent\KB\` — Obsidian 知识库，存放方法论、设计文档等
  - `方法论/` — 游戏数值设计框架、活动设计方法论
- `C:\ADHD_agent\skills\` — 自定义 skill 脚本（generate_event_review, generate_event_review_v2, shop_exchange_analysis）
- `C:\ADHD_agent\.cursor\skills\` — Cursor skill 定义（event-review-overall, event-review-single, generate-event-review, generate-event-review-v2, branch-diff-gsheet）
- `C:\ADHD_agent\KB\产出-数据分析\` — 数据分析报告 + 图表输出（已合并原 report_images/）

## Google Workspace CLI
- GWS CLI 已安装，路径: `C:\Users\linkang\AppData\Roaming\npm\gws`
- 项目ID: `calm-repeater-489707-n1`
- 账号: `linkang@nibirutech.com`
- 读取 Google Sheet 的方式: `node C:\ADHD_agent\scripts\gws_stdin.js`（通过 stdin 传 JSON 参数）
- Token 可能过期，过期时运行 `gws auth login` 重新认证

## Event Review Skill
- 入口: `C:\ADHD_agent\.cursor\skills\event-review-overall\SKILL.md`
- 实际脚本: `C:\ADHD_agent\skills\generate_event_review\`
  - `scripts\chart_generator.py` — 生成3张图表（Revenue Trend / Module Structure / User Growth）
  - `scripts\notion_publisher.py` — 生成 Notion + Wiki 双版本报告
  - `scripts\excel_handler.py` — Excel 模板生成与解析
  - `schema\input_template.json` — 输入数据 schema
  - `schema\example_data.json` — 示例数据
  - `assets\report_template.md` / `report_template_notion.md` — 报告模板

## 2026情人节复盘（已完成）
- 数据源 Google Sheet: `1ATIM20rsvf0sft78fLxeNiUK4CIUm4aabqfYO8ZnYNc`
  - 页签 `AI读：完整数据梳理` (gid=1724090484) — R级分层、历史趋势
  - 页签 `AI读：各礼包收入情况` (gid=1952699462) — 345条礼包明细
- 产出文件:
  - `C:\ADHD_agent\2026情人节活动数据复盘报告.md`
  - `C:\ADHD_agent\KB\产出-数据分析\2026情人节\` — 3张图表 + input_data.json + notion_content.md + wiki_content.md

## Notion MCP
- 已配置到 Claude Code 项目级 MCP: `https://mcp.notion.com/mcp`
- 需要新会话才能加载 Notion 工具

## Jira API
- [Jira API Access](reference_jira.md) — tap4fun 内部 Jira REST API 调用方式

## 配置表知识库
- [节日活动形式知识图谱](reference_festival_knowledge_graph.md) — 39种活动形式的机制、数值、历史数据回归，节日设计时先读
- [Config Library](reference_config_library.md) — 表编号索引、换皮规则、常用 SheetID（P2/X2）
- [X3 Config Library](reference_x3_config_library.md) — X3专属换皮知识库 `.cursor/x3-config-library/`，含 table-reference(表字典+9条必检) + activity-forms(51组活动形式/13种换皮主力)，x3-reskin skill 地基
- [配置表字段 Schema](../../../ADHD_agent/.cursor/config-library/table-schema.md) — 2011/2013/2112/2115/2116/2121/2135/2141/2142/2154 全字段定义+跨表追踪链
- 挖矿 35xx 表清单已写入 table-index.md — 27张表含 3510→3517→3516 追踪链、ID编码规则、26复活节案例
- [数值换皮决策框架](../../../ADHD_agent/.cursor/config-library/reskin-numerical-framework.md) — 道具层(系统/节日/配置)+数值层(流量侧改/变现侧不改)判断标准
- [节日换皮完整工作流](reference_reskin_workflow.md) — 脚本用法+JSON模板+必检表清单+写入安全规范+行军表情AI生成链路+下次换皮checklist
- [P2 养成线知识体系](reference_p2_progression_kb.md) — 数值手册 + 制作人梳理 + 数据现状档案 三件套，含跨项目搬运参考(§九)
- [X2 养成线付费价值手册](reference_x2_progression_kb.md) — 7 条养成线付费价值 + 4 份活动明细，demo: x2-value-manual_5185
- [X3 TimeCycle](reference_x3_timecycle.md) — X3 项目 TimeCycle↔ActvOnline 绑定、TriggerType 隐性限制、openpyxl 加载坑
- [xlsx git 差异对比脚本](reference_xlsx_git_diff_tool.md) — `C:\Users\linkang\xlsx_git_diff.py`，看 xlsx 配置表 HEAD vs 工作区单元格变更，问"看diff/改了啥"时调用
- [X3 仓库路径](reference_x3_gdconfig_repo.md) — X3 配置仓 `C:\x3\gdconfig\`；**导入只认 tsv\（改 tsv 不碰 xlsx）**，data\xlsx 仅备份下周删，旧 `C:\X3\`/`C:\x3dev\` 弃用
- [X3 代码仓](reference_x3_project_repo.md) — `C:\x3-project\` 服务端+客户端代码仓，含 server 目录结构/高频路径/GitLab API 访问，触发"查X3代码/X3服务端/X3代码库"先读
- [X3 配置知识库](reference_x3_config.md) — Item ID规则、asset_id格式、配置真源 tsv\(改tsv不碰xlsx)、节日Pack ID段
- [X3 Reward 表写入规则](reference_x3_reward_table_rules.md) — DropPara 必填+同 RewardID 内 seq 必须连续，2026-05 夏日 210921 踩坑总结
- [X3 累充隔离机制](reference_x3_recharge_isolation.md) — TaskType 902 + ActvOnline.RechargePointPackWhitelist + ActvTask 全档位 Parameter1 三表协同
- [X3 i18n 本地化工作流](reference_x3_i18n_workflow.md) — TXT_ key 命名规则(TXT_{Table}_{Field}_{ID}) + CompositeI18n monkey patch + gws.js 实际路径(run-gws.js) + 翻译术语对齐 + `_backup_*.xlsx` 污染扫描器
- [X3 礼包弹窗背景渲染优先级](reference_x3_pack_panel_rendering.md) — Pack.MainBg 覆盖 ActvOnline.ActvImg；拜访礼包 MainBg 必须空否则顶替节日 banner
- [X3 装饰阶梯礼包 tab 图来源](reference_x3_pack_tab_icon.md) — 底部商城页签 tab 图读 PackTypeInfo.Icon 不是 ChainPack.Icon，节日换皮必查 3 处 Icon
- [X3 客户端资源位置 & DK 注册](reference_x3_client_resources.md) — .png 实际位置(ActivityImg/Pack)、DK→GUID asset 注册、tableResInfo.txt 名单可能过期
- [X3 航海之路地块美术链路](reference_x3_voyage_art_chain.md) — 大富翁式活动(ActvType=28)；地块图写在 ActvVoyageEvent.DKImg(按事件组×等级换图,约4套岛图)，24格位置prefab写死；含配置表/GridItem.cs渲染链/换皮清单/开启链路
- [X3 付费机制速查](reference_x3_monetization_mechanics.md) — 重复外显转钻补偿(Regained,通用所有外显/头衔) + 储蓄罐PiggyBank(可重复绑养成货币深度款) + 自选周卡WeeklyCard(原生复用,自选4项+7天+打包)
- [X3 节日付费表现](reference_x3_festival_performance.md) — 单服收益排名(尼罗$1127最高)、尼罗重上D17-D35窗口、饱和度速查、数仓SQL模板
- [P2 付费深度经验(X3第二轮借鉴)](reference_p2_depth_lessons_for_x3.md) — P2养成线深度诊断(价格断层/高价值无低门槛/订阅抗衰退/中R扩品类不提价/深度梯度/重铸保养无底洞) + 节日变现结构(三层:外显+小游戏增量+养成/GACHA深度引擎/宽口浅底病名/4阶段排期/情感外显)
- [X3 积分活动配置体系](reference_x3_score_activity.md) — ActvScore.xlsx 三 sheet + 最佳酒馆 ContentID 系列 + TaskType 440/444 + Rank/RewardSlot 结构 + ScoreID=603 易混淆陷阱
- [X3 导表迁移到 TSV 缓存](reference_x3_tsv_export_migration.md) — 2026-05-29起导入只认tsv不读xlsx；**配置改动直接改tsv不碰xlsx**(用 x3-config-export skill 的 tsv_edit.py)；xlsx仅历史备份下周删；改X3配置/导表前必读

## 数据查询
- [X3 节日收入日监控+日报](reference_x3_festival_monitor.md) — 移植自X2，`skills\x3-festival-monitor\`，全服，**节日礼包口径=ActvOnline累充白名单(不能用Pack前缀猜)**，模块按PackType，计划任务ClaudeX3FestivalMonitor每天09:00
- [X3 节日日报模板完整说明](reference_x3_festival_report_template.md) — 12区块结构+JS数据结构+6数据源+硬口径决策(成熟服1000-1540/付费玩家付费率/R级快照+累充兜底/同期对齐)+维护校验(f-string转义查stray{{)，2026夏日大改版沉淀，改报告前必读
- [AI-to-SQL Skill](reference_ai_to_sql.md) — Datain 数仓 Trino SQL 技能，在 `C:\ADHD_agent\.claude\skills\ai-to-sql\`，查玩家明细/建筑/付费订单
- [X3 数仓外显/道具拥有率查法](reference_x3_datain_asset_query.md) — asset_id 带类型前缀(Item_/Hero_/Skin_/FurnitureSkin_)是最大坑(裸ID全返0)；含拥有率/R级分布/付费额SQL + dim_asset反查 + 用ai-to-sql不用datain-skill
- [挖矿回归漏斗模板](reference_mining_funnel_template.md) — 分R级关卡漏斗HTML模板，`C:\Users\linkang\mining_funnel_template.html`，修改CONFIG对象即可复用
- [BINGO卡包日志查询](reference_bingo_asset_logging.md) — BINGO连线奖励白/绿包用任务ID查（不是活动ID），任务ID映射表+科技节发放汇总
- [P2数仓时区](feedback_p2_datain_timezone.md) — P2 ods_user_asset 的 created_at 是北京时间，不做UTC转换

## 活动设计产出路径规范
- [全链路产出路径](reference_output_paths.md) — 数值方案/美需/出图/数据分析四环节固定路径，数值方案在 `产出-数值设计\{项目}_{节日}\`

## 美术需求生成
- [X2 美需生成 skill](../../../.claude/skills/x2-art-requirement/SKILL.md) — 主城特效参考图+美需文档全流程，含 GRFal async API 踩坑记录，触发词"美需/主城特效/出美需"
- [X3 美术资源规范](reference_x3_art_resource_spec.md) — 4维度：A出美需颗粒度/B落地交付(命名DK_/路径)/C格式现状(★尺寸不统一·跟复用源对齐;HUD icon124×136/铭牌752×192/头像框256×256)/D★换皮必双参考(老图=格式结构+新图=实际投放物元素;投放物多是现成资源去配置表+client搜不是生成,搜不到才新出;路径必验存在)
- 美需本地存档路径：`KB/产出-本地化与美术/{项目}_{年份节日}_{类型}_美需.md`（P2/X2 两个 skill 均写此路径）
- GRFal 参考图：`KB/产出-本地化与美术/ref-images/{节日}/`
- **x2-media 生图保存路径**：`C:\ADHD_agent\KB\产出-本地化与美术\{项目}\{类型子文件夹}\{类型}_{模型}_{日期时间}.png`
  - 项目：X2 / P2 / 通用；类型子文件夹：行军表情、技能图标、集卡册、活动图标等

## 节日开发周期
- [节日开发月度周期](project_festival_dev_cycle.md) — 第2周三部署、周四灰度D0、D14回归、D21出下期方案
- [X3 下期节日优化待办](project_x3_nile_next_phase.md) — 第二轮优化输入：夏日恋歌回归(breadth成功/depth没起来) + 5模块清单(付费深度=最高优先)
- [X3 英雄皮肤投放调整](project_x3_skin_deployment_adjustments.md) — 双皮肤改保底概率+跨服排行榜保留，本服排名门槛太低($15获取)是ARPPU低于P2的根因

## API Provider
- [API Provider 切换记录](project_api_provider_switch.md) — 2026-05-22 切到 one-hub，2026-05-25 周一切回 Anthropic 官方 API

## 工作流
- [quality-gate验收系统+交互模块工作流](project_quality_gate_and_interaction_module.md) — 收工自动验收(task-checker+清单+Stop hook，有标记会拦收工) + 交互模块「活原型+实时说明一体HTML」工作流；改X3配置/写策划案/做交互原型时相关，2026-06-03搭建
- [P2导表工作流](workflow_p2_table_import.md) — GSheetDownloader管道运行，表号空格分隔，触发词"P2导表/传表/导表到bugfix"
- [X2导表工作流](workflow_x2_table_import.md) — fwcli+x2gdconf，先读路由规则再读download skill，触发词"X2导表/X2下载表/X2刷表"
- [X2 i18n 重复key取首条](feedback_x2_i18n_duplicate_key.md) — 同一LC key多行时fwcli取首条→显示旧/错值；文案显示异常先查重复key
- [X2 限时抢购礼包占位数据](feedback_x2_flashsale_placeholder_data.md) — 限购2222/价555/默认头像=跑旧配置；vm包正常+IAP包占位=iap跨表没加载；重开活动/重热更即修
- [配置BUG工作流(双Agent)](workflow_config_bug_fix.md) — 巡检(Win定时任务ClaudeBugScan)+修复(按需启动)拆分架构
- [BUG修复运维规范](workflow_bugfix_ops.md) — 检查清单、Review问题记录、翻译流程（每次改BUG前必读）
- [批量补发邮件 skill](reference_bulk_mail_reissue.md) — `~/.claude/skills/bulk-mail-reissue`，iGame 导入表格式硬约束（GBK+逗号+JSON转义）；**P2/X2 专用，X3 不是这套**
- [X3 iGame 批量补发导入格式](reference_x3_igame_mail_import.md) — X3 专用：GBK+「道具信息」列写`[ID*数量]`，无标题列，跟P2的assetType JSON完全不同；样例在 Pictures\X3验收\
- [补发邮件固定产出路径](reference_mail_reissue_kb_path.md) — `KB\产出-补发邮件\{项目}\`，两件套(邮件导入多语言UTF8BOM / 补偿导入GBK)，模板沉淀在 _模板\，按项目分
- [补偿邮件文案先确认再输出](feedback_compensation_mail_text_confirm.md) — 补发邮件标题/正文先跟用户商量，不自拟定稿；补偿导入可先出
- [X2 IAP→主数据同步 skill](reference_iap_sync_to_master.md) — `C:/Users/linkang/skills/iap-sync-to-master/`，QA 礼包表增量同步到主数据表礼包维表，触发词"同步礼包/sync iap"
- [X3 TimeCycle 名字可能是历史复用残留](feedback_x3_timecycle_name_legacy.md) — 看 StartTime/Duration 实际值判断而非名字
- [Unity 图标提取与归档](workflow_unity_icon_extraction.md) — 从 Unity Inspector 截图提取图标，直接保存到 KB（禁止桌面中转），触发词"提取图标/复制图标/归档到KB"
- [X3 push 后自动跑 jolt 导表](workflow_x3_auto_jolt_export.md) — gdconfig push 后自动调 `~/.claude/jolt_export.py <branch>` 触发 Jenkins X3导配置
- [X3 策划案撰写模板与流程](workflow_x3_festival_design_doc.md) — **权威模板(6范本提炼)**：一切=「活动模块」组合；活动模块标准结构(设计目的/玩法说明/规则说明逐功能点/配置表内嵌4行schema/界面交互逐prefab逐元素/本地化)+三种顶层组合(单玩法/节日包装/系统rollout)+配套页签+范本库+checklist
- [X3 受保护分支 + MR 流程](workflow_x3_protected_branch_mr.md) — x3-project dev 受保护，feature branch + MR + GitLab API 创建 MR + LFS 大文件坑 + commit msg 强制 X3NEW-/X3- 前缀
- [X3 GRFal 生图工作流](workflow_x3_grfal_generate_image.md) — call_grfal.py 调用 / GRFAL_COOKIE / async polling / reference 注入 / 落地到 X3 客户端 DK 全链路
- [X3 分支合并冲突审计](workflow_x3_merge_conflict_audit.md) — 节日分支合 dev 后 3 方对比模板 + 假阳性识别 + CalculateFull 修公式缓存丢失
- [X3 i18n 扫描 backup 文件坑](feedback_x3_i18n_backup_files.md) — 跑 CompositeI18n 前临时把 data/_backup_*.xlsx 移出 data 目录，否则 key 冲突中断扫描
- [X3 分支策略](feedback_x3_branch_strategy.md) — 直接在当前活跃分支(dev-summer-love-song 等)上改 + push，不要自作主张新建专属分支
- [X3 礼包美术全链路(装饰+拜访)](workflow_x3_decoration_video.md) — 两类礼包对比(装饰有视频/拜访MainBg必空)+各自产出物+通用环节(HUD图标124×136/DK注册/GRFal踩坑)+产出记录

## User Preferences
- 语言: 中文
- 分析报告风格: 数据驱动，含模块/R级分层分析，关注节日整体ARPU（模块收入/节日付费人数）而非仅人次ARPPU

## Feedback
- [节日ARPU分母用当日总付费人数](feedback_x3_festival_arpu_denominator.md) — 节日ARPU=节日流水/当日总付费人数(所有付费玩家)，不是节日付费人数；覆盖旧"模块收入/节日付费人数"表述
- [X3 TOKEN actual_charge 单位坑](feedback_x3_token_actual_charge_unit.md) — TOKEN货币actual_charge自2026-06-02改记代币单位(=USD×100)；收入口径只有usd取actual_charge其余取pay_price；日报数据"暴涨"先查这条
- [GSheet 写入兼容性陷阱](feedback_gsheet_write.md) — API 能跑，坑在双引号/撇号/换行等字符转义
- [GSheet append 行顺序陷阱](feedback_gsheet_append_order.md) — INSERT_ROWS 插到开头不是末尾；正确做法：insertDimension + values.update
- [GSheet 配置表写入前置清单](feedback_gsheet_config_write_checklist.md) — 写前确认页签/表头/参考行逐列全比，写后验证行数+列完整性+位置
- [配置前先追完整链路](feedback_config_chain_first.md) — 先追两层引用链再写，含占星节drop_topay和集卡册实战案例
- [配置校验必须端到端](feedback_verification_end_to_end.md) — GSheet+本地TSV+分支推送三层验证，不过早下结论
- [DK 资源层工作流](feedback_dk_resource_workflow.md) — DK区间规划→GUID从.meta读→脚本追加→Unity导出→push client→再导配置表
- [碎片化并行工作节奏](feedback_fragmented_time.md) — 任务拆分要细粒度、弱耦合、可随时捡起
- [说人话少用术语](feedback_plain_language.md) — 规划/笔记文档用功能动词+人话解释，不堆代号和技术黑话
- [iGame cancel vs recall](feedback_igame_cancel_vs_recall.md) — "下线活动"任务，部署申请状态 → recall；上线中状态 → cancel
- [igame-actv recall/cancel 待实测](project_igame_actv_recall_cancel_pending_test.md) — 下次"下活动/撤回活动"时主动验证这块判断
- [数据回归必须先问设计方案](feedback_data_regression_ask_design_first.md) — 不能纯看购买数据反推礼包结构，先反咨询设计方案再用数据验证
- [数据回归分析方法论](feedback_data_regression_methodology.md) — 锚点是价格锚不需优化购买率；进度断崖要用全量/付费停留曲线验证而非归因免费资源
- [随机礼包期望值调整原则](feedback_numerical_design_random_pkg.md) — 无数据支撑不调整 drop 权重，floor/锚点变动不自动联动期望值
- [美需动画脚本写法](feedback_art_brief_script.md) — 元素只写定性描述，不写透明度/px/秒等参数
- [X3 主城皮肤=岛屿皮肤](feedback_x3_island_skin_terminology.md) — Item_81xxx非FurnitureSkin三件套；每次讨论X3皮肤先确认品类
- [配置写完必须反查验证](feedback_plan_index_must_be_fixed.md) — 写配置表后必须反查上下游一致性，写完不检查是根因
- [发现新规律必须立即更新知识库](feedback_proactive_knowledge_update.md) — 修BUG发现新链路/必检表时，当场更新SKILL.md，不等用户提醒
- [GSheet 写入安全规范](feedback_gsheet_write_safety.md) — 写前必须 duplicateSheet 备份页签；禁止按行号盲删；脚本崩溃后先验证实际状态再重跑
- [X3 写配置前必须确认分支](feedback_x3_branch_check.md) — 每次 commit 前 `git branch --show-current`，2026-05-25 X3NEW-736 错分支踩坑
- [X3 ActvOnline.MailID 必填](feedback_x3_actv_mailid_check.md) — 除 ActvType=8 外都填 101109，漏配时服务端 4 处 `MailID==0` 守卫静默吞未领奖励
- [拓荒节换皮踩坑总结](feedback_reskin_lessons_learned.md) — 三模块(脚本/写入/知识库)17个问题+优化项，下次换皮前必读
- [拓荒节换皮第二轮踩坑](feedback_reskin_round2_lessons.md) — 测试阶段：引用链遗漏9处+写入BUG5处+新增必检表6张
- [gws.cmd 角括号传参失败](feedback_gws_angle_bracket.md) — JSON body 含 `<>` 被 CMD.EXE 解析为重定向；改用 `node + run-gws.js` 绕过
- [GSheet 策划案格式规范](feedback_gsheet_design_doc_format.md) — 写节日优化策划案的格式标准：配色/字号/列宽/颜色语义，写完必须对照 checklist 确认
- [禁止参考图放TEMP](feedback_no_temp_for_ref_images.md) — 角色立绘等参考图严禁放%TEMP%，必须用持久路径
- [gws 读取中文内容后关键词搜索失败](feedback_gws_gbk_search.md) — gws stdout 是 GBK，utf-8 ignore 处理后中文变乱码，关键词匹配全失败；必须用行号范围直接读
- [Unity 图标提取全自动归档](feedback_unity_icon_auto_archive.md) — 看到截图+提取/归档关键词→直接执行，从上下文判断项目，不询问中间步骤
- [删文件前先出checklist确认](feedback_cleanup_checklist_first.md) — 清理中间产物必须先列保留/删除清单给用户确认，不自行判断（仅限用户的/已有文件）
- [自己产生的临时文件默认清不要问](feedback_temp_file_auto_cleanup.md) — 我本次任务造的中间产物(脚本/中间图/分析json)做完默认直接删、不问；清错用户会反馈
- [X3 手工启服 cwd 必须用 server\Resource](feedback_x3_server_launch_cwd.md) — RunWorkingDirectory=../Resource，cwd 错了启动期 log4net 抛 DirectoryNotFoundException 进程僵尸
