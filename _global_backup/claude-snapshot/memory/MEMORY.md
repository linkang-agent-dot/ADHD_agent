# Project Memory

> 索引规则：一行一指针（或一组同主题指针），明细进各 topic 文件，别在本文堆细节。

## 复盘报告 / 方法论
- [X2 2026占星节模块回归报告](project_x2_star_festival_2026_report.md) — 7页签HTML报告(R级分层/优化动作)，生成脚本 `_gen_full.py`
- [X2 两节日开局窗口收入对比方法论](reference_x2_festival_compare_method.md) — 口径三铁律(服数可比/D0-D9对齐/按模块语义归类)+缺口=广度×深度+追平预测；含FEST口径/classify

## 进行中案子
- **7月并行排期甘特(世界杯×深海节)**：`KB\产出-数值设计\X3_7月排期_世界杯+深海节甘特.html` — 两节日并行排期事实入口；SOP=每比赛日两件事(发邮件结算+GM加BP分,末场打完24h内发奖)，GM命令 `GMAddActivityScore <活动id> <分>`(ActivityMeta.Gm.cs:292·player-scope·普通权限);深海节为避世界杯半决(7/15)/决赛(7/19)提前到7/3全服·D1–D10到7/12;按甘特视角不写配置ID([[feedback_activity_doc_gantt_view]])
- [X3 英雄皮肤新皮肤视频化](project_x3_hero_skin_video.md) — 老皮肤Spine不变·新皮肤走视频(AI量产)；含展示代码链路(CreateSpine咽喉点+5界面契约+晋升礼包独立链路)
- [X3 世界杯活动系列](project_x3_worldcup_activity.md) — 飞轮=竞猜+BP产券→世界杯开箱(ActvCrafting/ActvType15)→英雄+足球宝贝皮肤(爱莉希雅Hero1040);零新后端;换人先读全模块交接总文档 `KB\产出-数值设计\X3_世界杯\_世界杯活动_全模块交接总文档.md`
- [X3 英雄养成手册双版本](project_x3_hero_handbook.md) — ActvType=27养成手册加$49.99豪华版·二选一互斥;单档死结构→双档必改程序(ActvLoginPurchase加Pack2/Group2+UIActvLogin加页签);策划案已过验收待程序P1
- [X3 异国美酒储蓄罐改造](../../../../ADHD_agent/KB/产出-数值设计/X3_异国美酒储蓄罐/异国美酒储蓄罐_可重复购买改造_策划案.md) — **已闭环**:每日双档($9.99档1+$19.99档2)·每档每日限购1次自然日0点重置;实现=纯追加配置(Pack500032/PiggyBank行51/Grade组261)+服务端GiftMeta.cs UTC同日分支(按ResourceID==7002圈定,常量GiftConst.DAILY_RESET_PIGGY_RES_ID)+客户端UIPiggyBankContent.cs;MR!525已合dev(玩法测过+sub-agent审过);唯一尾巴=档2标题i18n空白(跑x3-translation-automatic补,不急);实现法详见[[reference_x3_monetization_mechanics]]
- [X3 深海节活动](project_x3_deepsea_festival.md) — 双周双核心(转盘+排行榜/大富翁+BP)主攻付费深度;11模块(程序5/纯配置6);唯一入口=对齐总览HTML `KB\产出-数值设计\X3_深海节\深海节开发对齐总览.html`;ID分配=100000+CID

## 后台自动任务
- [后台计划任务清单](reference_background_scheduled_tasks.md) — 本机所有 Claude Windows 计划任务(触发/脚本/产出);含晨间简报合并+新鲜度闸门坑;问"后台有什么自动任务"或增改停任务先读
- [策略游戏雷达](reference_game_radar.md) — 每天抓中/美/日热门+飙升策略游戏出HTML(App Store+Google Play+YouTube无key+Reddit);工具在 `C:\Users\linkang\game-radar\`,计划任务 GameRadar-Daily 09:00

## Key Directories
- `C:\ADHD_agent\` 主工作仓 · `C:\ADHD_agent\KB\` Obsidian知识库(方法论/设计文档) · `KB\产出-数据分析\` 数据分析报告+图表
- `C:\ADHD_agent\skills\` 自定义skill脚本 · `C:\ADHD_agent\.cursor\skills\` Cursor skill定义
- [Obsidian KB 5维标签体系](reference_obsidian_kb_tag_taxonomy.md) — kind/domain/proj/fest/year 嵌套命名空间，归档新笔记按它打标签

## 平台 / 工具入口
- [GRFal 工具实现+内部Prompt逻辑](reference_grfal_implementation.md) — 问"grfal怎么实现/内部有没有prompt/Morphix"先读;三层架构(客户端纯HTTP无prompt/服务端@tool埋prompt/外部模型后端);唯一入口文档 `KB\方法论\GRFal工具实现与内部Prompt逻辑总览.html`(含Morphix 8段prompt全文+设计7模式,Morphix已并入)
- **GWS CLI**: 路径 `C:\Users\linkang\AppData\Roaming\npm\gws`,项目ID `calm-repeater-489707-n1`,账号 linkang@nibirutech.com;读GSheet=`node C:\ADHD_agent\scripts\gws_stdin.js`;Token过期(401)重授权=`gws auth login -s sheets,drive`后cat日志抓URL贴用户手点(不自动弹浏览器)
- **GSheet读写统一工具**: [gsheet-toolkit](reference_gsheet_toolkit.md) — `C:\ADHD_agent\scripts\gsheet_utils.py`(读/写/删/备份/按内容定位全封装,先import别现写)
- **Event Review Skill**: 入口 `.cursor\skills\event-review-overall\SKILL.md`,脚本 `skills\generate_event_review\`(chart_generator/notion_publisher/excel_handler + schema + 模板)
- **x3-media skill 位置**: [x3-media skill位置与版本控制](reference_x3_media_skill_location.md) — 活skill在 `~\.claude\skills\x3-media\`(加type=写type-*.md+SKILL.md Router表加行);⚠️不在git仓只有ADHD_agent旧快照,改完要手动同步`_global_backup`否则丢;已加ui_reskin type(改造界面出效果图五步法)
- **Notion MCP**: 已配项目级 `https://mcp.notion.com/mcp`(需新会话加载)
- **Jira API**: [Jira API Access](reference_jira.md) — tap4fun 内部 REST API 调用方式
- **X3 测试环境(部署/GM/构建/数据)**: [X3 测试环境部署链路](reference_x3_kadmin_deploy.md) — 权威工具=`test-env-prepare-x3`(QA官方skill,git clone装不能npx);含kadmin双key+部署铁律(Play+Map+Center同批·部后复查)+beta拓扑+GM规则;X3微服务非default_game_<id>;手搓x3-kadmin已冗余
- **iGame GM 下发**: [igame-gm-send 链路+鉴权](reference_igame_gm_send.md) — skill默认读`.igame-auth.json`(另有`.igame-auth-dev.json`两套token各自过期);JWT约15天;401=过期贴新token写回默认文件;`__probe_noop__`探针验通断不改状态
- **2026情人节复盘(已完成)**: 数据源 GSheet `1ATIM20rsvf0sft78fLxeNiUK4CIUm4aabqfYO8ZnYNc`;产出在 `KB\产出-数据分析\2026情人节\`

## X2 客户端 / 美术链路
- [X2 室内装饰家具资产链路](reference_x2_indoor_furniture_assets.md) — 资产在 `x2\Res\Shop\Indoor\`,命名X2_B/D_{节日}_XXX,只给3D+TGA无预览(美术常投子集易配漏)
- [X2 主城皮肤换皮完整链路](reference_x2_city_skin_chain.md) — 美术三族+2D图标→DK一键5型→city_skin(1312)→item(1111);city_skin只留活跃皮肤·新id必扫item引用避退役
- [X2 活动banner换皮直出链路](reference_x2_operation_banner.md) — banner走路径不走DK,真源 `in-game-remote-assets\...\X2\operation\EventBanner\`,2112 banner_url列直接写路径

## 配置表知识库（P2/X2/X3）
- [节日活动形式知识图谱](reference_festival_knowledge_graph.md) — 39种活动形式机制/数值/历史回归,节日设计先读
- [Config Library](reference_config_library.md)(⚠️**P2专用**表编号/换皮/SheetID) · [X2 配置表查询权威源](reference_x2_config_library.md)(🔒X2任何表SheetID必用 `gsheet_query.py resolve` 现解禁硬抄,含gacha内外圈) · [X3 Config Library](reference_x3_config_library.md)(`.cursor/x3-config-library/` table-reference+activity-forms,x3-reskin地基)
- [配置表字段Schema](../../../ADHD_agent/.cursor/config-library/table-schema.md)(2011/2013/2112…全字段+追踪链) · 挖矿35xx表清单已写入 table-index.md(3510→3517→3516链)
- [数值换皮决策框架](../../../ADHD_agent/.cursor/config-library/reskin-numerical-framework.md)(道具层+数值层:流量侧改/变现侧不改) · [节日换皮完整工作流](reference_reskin_workflow.md)(脚本/JSON模板/必检表/安全规范/checklist) · [Morphix换皮工具逆向+prompt库](reference_morphix_reskin_prompts.md)(=GRFal前处理层,8功能prompt已归档;**已并入** [[reference_grfal_implementation]] 总览文档)
- [P2 养成线知识体系](reference_p2_progression_kb.md)(数值手册+制作人梳理+数据档案) · [X2 养成线付费价值手册](reference_x2_progression_kb.md)(7养成线+4活动明细) · [P2 付费深度经验(X3借鉴)](reference_p2_depth_lessons_for_x3.md)(价格断层/订阅抗衰退/节日变现三层)
- [X2 服务器schema查法](reference_x2_server_schema_lookup.md)(按服龄迁移,真源=数仓日报) · [X2 挖矿小游戏掉落链路](reference_x2_metro_minigame_rock_drop.md)(level→rock_drop表3514,漏导致miningDrop nil panic)
- **X3 仓库/导表**: [X3 gdconfig仓](reference_x3_gdconfig_repo.md)(`C:\x3\gdconfig\`,导入只认tsv不碰xlsx) · [X3 代码仓](reference_x3_project_repo.md)(`C:\x3-project\`server+client,含GitLab API) · [X3 导表迁移TSV缓存](reference_x3_tsv_export_migration.md)(⚠️2026-06-04起 jenkins-xlsx-tsv-gate 强制xlsx≡tsv,两边同改) · [X3 unity-mcp现状起法](reference_x3_unity_mcp.md) · [xlsx git差异对比脚本](reference_xlsx_git_diff_tool.md)(`C:\Users\linkang\xlsx_git_diff.py`)
- **X3 排行榜**: [X3 排行榜配置链+ContainsKey排查](reference_x3_rank_config_chain.md)(RankCfg+RankRewardSlotCfg+Reward+活动挂载;CRankCfg.ContainsKey的key=RankCfg ID(col0)非RankType列;InvalidType报错先排服务端旧导出而非配置缺失)
- **X3 活动类型**: [X3 ActvType权威枚举](reference_x3_actvtype_enum.md)(数字↔玩法真源=client CSShared ActivityConst.cs;64=三选一礼包/71=世界杯竞猜/70=周卡/63=链式礼包;server handler注释会过时;世界杯重编号64→71误扫109002坑)
- **X3 配置/字段**: [X3 配置知识库](reference_x3_config.md)(Item ID/asset_id/真源tsv/Pack ID段) · [X3 TimeCycle](reference_x3_timecycle.md)(↔ActvOnline绑定/TriggerType/openpyxl坑) · [X3 Reward表写入规则](reference_x3_reward_table_rules.md)(DropPara必填+seq连续) · [X3 累充隔离机制](reference_x3_recharge_isolation.md)(TaskType902+白名单+ActvTask三表) · [X3 积分活动配置体系](reference_x3_score_activity.md)(ActvScore三sheet+TaskType440/444+ScoreID=603陷阱) · [X3 customParam驱动可热部署活动](reference_x3_customparam_activity_pattern.md)(参数搬iGame部署=零代码换参数)
- **X3 数仓主数据**: [X3 dim.iap 节日礼包添加](reference_x3_dim_iap_master.md)(数仓维表SheetID `1Pblig...ntCqU`/dim.iap;源=Pack tsv+i18n名;分类照抄尼罗210601-615:PackType11=链式套装/15=道具弹窗,节日礼包标H列note留空;行非连续按id定位;先backup;深海211016-031待补)
- **X3 礼包/弹窗**: [X3 礼包开启机制速查](reference_x3_pack_open_mechanisms.md)(OpenActv空时靠啥触发+Pack表头row5坑) · [X3 礼包弹窗背景渲染优先级](reference_x3_pack_panel_rendering.md)(Pack.MainBg覆盖ActvImg,拜访礼包MainBg必空) · [X3 装饰阶梯礼包tab图来源](reference_x3_pack_tab_icon.md)(读PackTypeInfo.Icon) · [X3 付费机制速查](reference_x3_monetization_mechanics.md)(转钻补偿Regained/储蓄罐PiggyBank/自选周卡)
- **X3 文案排查**: [X3 自动文案/邮件名字空白排查](reference_x3_autotext_empty_debug.md)(自动key文本空白:服务端CheckAndConvertCfgTxtToEmpty在key缺失返空;先grep含合并行确认key在不在dev,在就查服务端旧导出;买礼包邮件=模板3000000正文{0}=TXT_Pack_Name)
- **X3 客户端/界面**: [X3 i18n本地化工作流](reference_x3_i18n_workflow.md)(TXT_key命名+CompositeI18n+backup污染扫描) · [X3 客户端资源位置&DK注册](reference_x3_client_resources.md) · [X3 新增活动界面链路](reference_x3_client_new_ui_workflow.md)(UI框架4件套+复用ActvType按ContentID分流+day锁坑) · [X3 航海之路地块美术链路](reference_x3_voyage_art_chain.md)(ActvType=28,地块图写ActvVoyageEvent.DKImg)
- **X3 外显**: [X3 八大外显模块→资源路径总表](reference_x3_cosmetic_resource_paths.md)(8模块对应资源类型+路径) · [X3 纪念卡/英雄皮肤属性配置链路](reference_x3_cosmetic_attribute_chains.md)(纪念卡集卡升级万分比战力Buff/英雄属性走HeroSkill hero_id=1000+Role_C_n属本体;外显图库HTML生成脚本_gen_festival_cosmetics.py)
- [X3配置知识库交接文档](reference_x3_config_handover_doc.md)(给同事的整合版,KB留底+推gdconfig dev_festival根)

## 数据查询 / 数仓
- [AI-to-SQL Skill](reference_ai_to_sql.md) — Datain 数仓 Trino SQL,在 `C:\ADHD_agent\.claude\skills\ai-to-sql\`,查玩家/建筑/订单
- [X3 数仓外显/道具拥有率查法](reference_x3_datain_asset_query.md)(asset_id带类型前缀Item_/Hero_/Skin_是最大坑,裸ID全返0) · [X2 数仓资产流水/被回收名单查法](reference_x2_datain_asset_query.md)(asset_id裸数字无前缀,change_type 1增2减,北京时间) · [P2数仓时区](feedback_p2_datain_timezone.md)(created_at北京时间不转UTC)
- **X3节日数据**: [X3 节日收入日监控+日报](reference_x3_festival_monitor.md)(`skills\x3-festival-monitor\`,礼包口径=ActvOnline累充白名单) · [X3 节日基线月环比分析法](reference_x3_baseline_mom_compare.md)(同生命周期月环比+合服踩坑) · [X3 节日日报模板完整说明](reference_x3_festival_report_template.md)(12区块+6数据源+硬口径) · [X3 节日上线服龄覆盖+DAU查法](reference_x3_server_coverage_query.md)(开服用真实首登/合服作废id近7日登录过滤) · [X3 节日付费表现](reference_x3_festival_performance.md)(单服收益排名/饱和度/SQL模板)
- **X2节日数据**: [X2 节日收入日监控](reference_x2_festival_monitor.md)(`skills\x2-festival-monitor\`,口径=dim_iap节日类型+累充白名单兜底)
- [X2 周卡「没领到7次」工单数仓核查口径](reference_x2_weekly_card_datain_query.md) — 先分节日自选周卡(festival_time_card_reward,sub_id=活动ID)vs普通时长卡(iap_week_card_claim_all);领取次数=秒级时间戳聚session别count(*);先查order确认买没买
- [挖矿回归漏斗模板](reference_mining_funnel_template.md)(`C:\Users\linkang\mining_funnel_template.html`,改CONFIG复用) · [BINGO卡包日志查询](reference_bingo_asset_logging.md)(用任务ID查不是活动ID)

## 产出路径 / 生产
- [全链路产出路径](reference_output_paths.md) — 数值方案/美需/出图/数据分析四环节固定路径
- [X3英雄皮肤视频生产知识库](reference_x3_hero_skin_video_production.md) — 替代Spine展示视频:目标SBS+Spine精髓(idle循环)+模型选型(kling fflf首尾帧)+透明化流水+Prompt库
- [X3 AI出图工作流(角色换装+UI换皮)](../../../../ADHD_agent/KB/方法论/X3_AI出图工作流_角色皮肤换装+活动UI换皮_世界杯案.md) — 世界杯案全程:两条线+逐轮只改一处+14条踩坑;§8策划案内嵌出图流程S1-S5;§12改造现有界面=真组件拼装→AI reskin五步法
- [X2 美需生成 skill](../../../.claude/skills/x2-art-requirement/SKILL.md)(主城特效参考图+美需全流程) · [X3 美术资源规范](reference_x3_art_resource_spec.md)(出美需颗粒度/落地交付/格式现状/换皮必双参考) · [gdesign(.designdeck)位置与陷阱](reference_gdesign_designdeck.md)(素材库真实在 `C:\x3-project\client\Assets\Res\UI\Spirits` 6034张PNG)
- 美需本地存档 `KB/产出-本地化与美术/{项目}_{年份节日}_{类型}_美需.md` · GRFal参考图 `KB/产出-本地化与美术/ref-images/{节日}/` · x2-media生图 `KB\产出-本地化与美术\{项目}\{类型子文件夹}\{类型}_{模型}_{时间}.png`
- [透明资源必须差分法验真透明](feedback_transparent_asset_diff_check.md)(白底vs黑底相减,防GPT假透明)

## 待办 / 周期
- [X2拓荒节装饰文案重写(等图)](project_x2_pioneer_decoration_copy_todo.md) — 5装饰(350-354)文案雷同要重写,含表坐标/key
- [节日开发月度周期](project_festival_dev_cycle.md)(第2周三部署/周四灰度D0/D14回归/D21出方案) · [X3 下期节日优化待办](project_x3_nile_next_phase.md)(夏日breadth成功depth没起来+5模块) · [X3 英雄皮肤投放调整](project_x3_skin_deployment_adjustments.md)(改保底概率+跨服排行榜,本服门槛低是ARPPU低根因)
- [播客下载+转文字链路](reference_podcast_download_transcribe.md)(iTunes lookup→RSS→yt-dlp;faster-whisper须ffmpeg切10min段) · [API Provider切换记录](project_api_provider_switch.md)(2026-05-25切回Anthropic官方)

## 工作流
- [项目收口接管化归纳范式](workflow_handover_assetization.md) — 判据=新agent冷启动能否在修BUG/接模块/换皮入口秒懂;大案子产三件套禁流水账;已进CLAUDE.md收口④
- [配置改动备份规范](workflow_config_backup_kb.md)(备份沉KB,一功能一份自包含.md含before→after+恢复法,导表成功删staging) · [配置BUG工作流(双Agent)](workflow_config_bug_fix.md)(巡检ClaudeBugScan+按需修复) · [BUG修复运维规范](workflow_bugfix_ops.md)(检查清单/Review/翻译,改BUG前必读)
- [quality-gate验收系统+交互模块](project_quality_gate_and_interaction_module.md)(收工自动验收+活原型一体HTML) · [验收清单/double-check设计四原则](workflow_checklist_design_principles.md) · [策划案设计质量验收(design-merit)](workflow_design_merit_critique.md)(好=对声明目的实现到位,目的→模块→表现递归拆) · [交互原型素材化工作流](workflow_interaction_prototype_assetization.md)(真素材优先6034库→缺则Morphix)
- **导表**: [P2导表](workflow_p2_table_import.md)(GSheetDownloader,表号空格分隔) · [X2导表](workflow_x2_table_import.md)(fwcli+x2gdconf) · [导表只导第一个页签](feedback_table_export_first_tab_only.md) · [X3 push后自动跑jolt导表](workflow_x3_auto_jolt_export.md)
- **X3工作流**: [X3 策划案撰写模板与流程](workflow_x3_festival_design_doc.md)(权威模板:一切=活动模块组合) · [X3 受保护分支+MR流程](workflow_x3_protected_branch_mr.md)(feature branch+MR+commit前缀X3NEW-) · [X3 GRFal生图工作流](workflow_x3_grfal_generate_image.md) · [X3 分支合并冲突审计](workflow_x3_merge_conflict_audit.md)(3方对比+假阳性识别) · [X3 本地服GM/调时间telnet链路](workflow_x3_local_server_gm_telnet.md)(端口23000+NodeID,telnet分包协议,helper `~/x3_gm.py`) · [X3 礼包美术全链路](workflow_x3_decoration_video.md)(装饰有视频/拜访MainBg必空) · [X3 多agent并发改配置=git worktree](workflow_x3_multiagent_worktree.md)(每agent一个worktree取代备份文件夹;坑=post-checkout钩子重建xlsx锁目录,刚建完别马上拆)
- **X2节日上线**: [X2节日活动上线表写法](workflow_x2_festival_launch_table.md)(GSheet每节日一页签,灰度/正式双批次)
- **补发邮件**: [批量补发邮件skill](reference_bulk_mail_reissue.md)(`~/.claude/skills/bulk-mail-reissue`,GBK+逗号+JSON转义,**P2/X2专用**) · [X3 iGame批量补发导入格式](reference_x3_igame_mail_import.md)(GBK+「道具信息」列`[ID*数量]`无标题列,跟P2不同) · [补发邮件固定产出路径](reference_mail_reissue_kb_path.md)(`KB\产出-补发邮件\{项目}\`) · [补偿邮件文案先确认](feedback_compensation_mail_text_confirm.md)
- [Unity图标提取与归档](workflow_unity_icon_extraction.md)(从Inspector截图提取直接存KB禁桌面中转) · [X2 IAP→主数据同步skill](reference_iap_sync_to_master.md)(`skills/iap-sync-to-master/`)
- [X3 i18n扫描backup文件坑](feedback_x3_i18n_backup_files.md)(跑前临时移出data) · [X3 TimeCycle名字可能是历史复用残留](feedback_x3_timecycle_name_legacy.md) · [X2 i18n重复key取首条](feedback_x2_i18n_duplicate_key.md) · [X2 限时抢购礼包占位数据](feedback_x2_flashsale_placeholder_data.md)(iap跨表没加载,重热更即修) · [X2道具单价看白皮书不用X3钻石折算](feedback_x2_item_pricing_whitepaper.md)

## User Preferences
- 语言中文;分析报告=数据驱动+模块/R级分层,关注节日整体ARPU(=节日流水/当日总付费人数,见[[feedback_x3_festival_arpu_denominator]])
- [HTML产物直接本地打开不发Artifact](feedback_html_open_local_not_artifact.md) — 验收清单/报告/原型/甘特等.html一律`start`本机浏览器打开，永远不开claude.ai界面（仍归档KB）

## Feedback（协作姿态）
- [遇问题先反馈别硬怼工具](feedback_surface_problems_not_thrash.md) · [生产操作先报再动](feedback_production_ops_announce_first.md)(失败后重试=新操作必停下报告) · [删改用户内容模块前先问](feedback_ask_before_modifying_user_content.md) · [动在途仓库前先摊清单确认](feedback_confirm_before_touching_inflight_repo.md) · [常规可逆操作直接做不要墨迹](feedback_decisive_on_reversible_ops.md) · [归纳知识库是默认动作别问](feedback_kb_summarize_dont_ask.md)
- [碎片化并行工作节奏](feedback_fragmented_time.md) · [说人话少用术语](feedback_plain_language.md) · [删文件前先出checklist确认](feedback_cleanup_checklist_first.md)(仅限用户的/已有文件) · [自己产生的临时文件默认清不要问](feedback_temp_file_auto_cleanup.md) · [发现新规律必须立即更新知识库](feedback_proactive_knowledge_update.md) · [活动文档用甘特图视角](feedback_activity_doc_gantt_view.md)
- [教学/交接包必须自包含](feedback_teaching_pack_self_contained.md) — 链路上调用到的KB搬副本进包并标"对应流程哪一步",别只留指针;走流程扫引用→搬副本分目录→脚本搬真身→闭包一层不无脑全搬

## Feedback（配置 / 数据 / 真源）
- [改sheet/策划案过审提速少返工](feedback_sheet_edit_review_efficiency.md) · [配置前先追完整链路](feedback_config_chain_first.md) · [配置校验必须端到端](feedback_verification_end_to_end.md)(GSheet+TSV+分支三层) · [改配置前先确认真源与落地路径](feedback_confirm_source_of_truth_before_edit.md)(X3真源=tsv,X2/P2=GSheet) · [配置写完必须反查验证](feedback_plan_index_must_be_fixed.md) · [DK资源层工作流](feedback_dk_resource_workflow.md)
- [X3 写配置前必须确认分支](feedback_x3_branch_check.md) · [X3 分支策略](feedback_x3_branch_strategy.md)(在当前活跃分支改+push别自建专属分支) · [X3 ActvOnline.MailID必填](feedback_x3_actv_mailid_check.md)(101109,漏配静默吞奖励) · [X3 主城皮肤=岛屿皮肤](feedback_x3_island_skin_terminology.md)(Item_81xxx非三件套)
- [节日ARPU分母用当日总付费人数](feedback_x3_festival_arpu_denominator.md) · [X3 TOKEN actual_charge单位坑](feedback_x3_token_actual_charge_unit.md)(2026-06-02改记代币=USD×100) · [数据回归必须先问设计方案](feedback_data_regression_ask_design_first.md) · [数据回归分析方法论](feedback_data_regression_methodology.md) · [随机礼包期望值调整原则](feedback_numerical_design_random_pkg.md)
- **GSheet**: [写入兼容性陷阱](feedback_gsheet_write.md)(双引号/撇号/换行转义) · [append行顺序陷阱](feedback_gsheet_append_order.md)(insertDimension+values.update) · [配置表写入前置清单](feedback_gsheet_config_write_checklist.md) · [写入安全规范](feedback_gsheet_write_safety.md)(duplicateSheet备份,例外[1011本地化表不备份](feedback_x2_i18n_table_no_backup.md)) · [策划案格式规范](feedback_gsheet_design_doc_format.md)

## Feedback（换皮 / 环境 / 脚本坑）
- [拓荒节换皮踩坑总结](feedback_reskin_lessons_learned.md) · [拓荒节换皮第二轮踩坑](feedback_reskin_round2_lessons.md) · [美需动画脚本写法](feedback_art_brief_script.md)(只写定性不写px/秒) · [禁止参考图放TEMP](feedback_no_temp_for_ref_images.md) · [Unity图标提取全自动归档](feedback_unity_icon_auto_archive.md)
- [X2通行证复用id限购坑](feedback_x2_pass_reuse_limit_trap.md)(limit_cnt+1) · [X2导表别过度验证](feedback_x2_import_dont_oververify.md) · [X2合并两节日分支进master坑](feedback_x2_merge_driver_drops_remote.md)(用id_merge_3way.py) · [手改X2 i18n tsv两坑](feedback_x2_i18n_tsv_handedit.md)(CRLF+LC id含数字子串)
- [gws.cmd角括号传参失败](feedback_gws_angle_bracket.md)(改node+run-gws.js) · [gws读中文后搜索失败](feedback_gws_gbk_search.md)(stdout是GBK,用行号范围读) · [X3 手工启服cwd必须用server\Resource](feedback_x3_server_launch_cwd.md) · [hook路径必须用正斜杠](feedback_hook_path_forward_slash.md) · [含中文.ps1必须存带BOM UTF-8](feedback_ps_script_needs_bom.md) · [别把一次性成本误当硬约束](feedback_constraint_framing_onetime_cost.md)
- [igame cancel vs recall](feedback_igame_cancel_vs_recall.md)(部署申请态→recall/上线中→cancel) · [igame-actv recall/cancel已实测(X2)](project_igame_actv_recall_cancel_pending_test.md)
- [每日报告HTML化+通用渲染器](reference_daily_report_html.md)(render_report_html.py复用) · [工作日报跨天污染根因+修复](feedback_daily_report_crossday_bleed.md)(按消息真实北京时间过滤)
