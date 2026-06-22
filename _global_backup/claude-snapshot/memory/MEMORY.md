# Project Memory

## 复盘报告
- [X2 2026占星节模块回归报告](project_x2_star_festival_2026_report.md) — 7页签HTML报告，含R级分层/优化动作，生成脚本 `_gen_full.py`，2026-05-25归档
- [X2 两节日开局窗口收入对比方法论](reference_x2_festival_compare_method.md) — 「为啥这期比上期少/差哪几个模块/能否追平」：口径三铁律(服数可比/D0-D9对齐/按模块语义归类剔往期残留)+缺口=广度×深度拆解+渗透率用节日付费人分母(DAC两期不可比)+追平预测算法；含FEST口径/classify；占星vs拓荒案(缺口$8.4k=付费人数塌方)

## 进行中案子
- [X3 英雄皮肤新皮肤视频化](project_x3_hero_skin_video.md) — 老皮肤走Spine不变·新皮肤走视频(AI可量产)；策划案GSheet `15Iacryl...`；含英雄皮肤展示代码链路(CreateSpine咽喉点+5界面契约+晋升礼包独立链路)，2026-06-09立项
- [X3 世界杯活动系列](project_x3_worldcup_activity.md) — 深度付费；飞轮=竞猜+BP产抽奖券→主抽奖=世界杯开箱(ActvCrafting/ActvType15,非转盘)→英雄+足球宝贝皮肤(爱莉希雅Hero1040)；竞猜=独立Actv活动(挂礼包)买礼包规避博彩+防对冲一场选一个；★零新后端(付费=订单/免费=$0领取，结算走运营查日志+bulk-mail，砍赛果界面)；BP走ActvScore；含X3抽奖/BP/竞猜可复用资产盘点；**换人交接先读全模块交接总文档`KB\产出-数值设计\X3_世界杯\_世界杯活动_全模块交接总文档.md`**(竞猜界面ActvType64已落地,余5模块设计定稿待配)，2026-06-09立项

- [X3 英雄养成手册双版本](project_x3_hero_handbook.md) — 新一期3活动之第1个；现有ActvType=27养成手册(102701/付费登录30天单档$29.99)加$49.99豪华版·二选一互斥·每日2.0×加厚+第30天专属大奖·新页签；★ActvType=27单档死结构(每ContentID只挂1 Pack/Group)→双档必改程序(扩ActvLoginPurchase加Pack2/Group2+UIActvLogin加页签)；策划案GSheet`15NKt8gF...`已过验收·待程序P1后配表，2026-06-18立项
- [X3 异国美酒储蓄罐改造](../../../../ADHD_agent/KB/产出-数值设计/X3_异国美酒储蓄罐/异国美酒储蓄罐_可重复购买改造_策划案.md) — 新一期3活动之第2个；★定型「每日2档」(v2,旧5档永久方案废弃)：现状每天1次$9.99→每天2档$9.99(10)+$19.99(20)·各档独立24h CD(都能买·非小中大互斥)·服务端零改动。**最终实现=纯追加配置(档1不动·克隆Pack500031→500032 Group11/Price111·PiggyBank行51 GroupId261·Grade组261 Num20)+客户端UIPiggyBankContent 2处(OnRefreshPackGiftUI加PrefixData()·选档改「第一个不在CD的档」→CD状态=本周期已砸)+界面零新增**；改动包备份`改动包_每日双档_FINAL\`(README+apply脚本+client patch)；★**2026-06-18已落地到两个feature分支`X3NEW-wine-piggy-daily-dual`(gdconfig+x3-project,均基origin/dev·用户明确要dev基底·dev与dev_festival大分叉见[[feedback_x3_branch_strategy]]):配置三表+客户端2处已应用·本地导表验证通过(ExportTable.py exit0·xlsx已sync闸门解)·**配置已拷ProtoGen+热重载到3080服(26080)live(errCode=0,data-only无需重启服)**·均未commit(用户要先自测不走MR);dev_festival原WIP已stash在gdconfig待恢复;剩客户端重建+自测玩法。⚠️**2026-06-18用户转去做newbie-recharge,x3-project已切走到`feature/x3-newbie-recharge-firstpay-popup`,储蓄罐客户端改动(UIPiggyBankContent.cs+2个不明prefab)已stash在piggy分支(`WIP_piggy_cs+unknown_2prefab_before_newbie_switch`),返工=`cd x3-project&&git checkout X3NEW-wine-piggy-daily-dual&&git stash pop`;gdconfig仍在piggy分支配置原样;3080服配置仍live**。遗留:dev基底客户端报`ConstCfg CustomerToRefreshProbability is empty`卡住,查实该常量dev/dev_festival都有值(0.75|0.5|0.25,酒馆顾客刷新)非本改动致,疑dev基底版本不匹配,待排**；机制见[[reference_x3_monetization_mechanics]]，2026-06-18立项
- [X3 深海节活动](project_x3_deepsea_festival.md) — 双周双核心循环主攻付费深度(一周转盘+排行榜/二周大富翁+BP)；11模块(需程序5/纯配置6)；**唯一入口=对齐总览HTML`KB\产出-数值设计\X3_深海节\深海节开发对齐总览.html`**+策划案GSheet`1mC0yssL...`；ID分配总表已落地(扫tsv防撞,AO=100000+CID)；下一步B类配置/美术fleet，2026-06-18进入配置落地

## 后台自动任务
- [后台计划任务清单](reference_background_scheduled_tasks.md) — 本机所有 Claude Windows 计划任务(触发/脚本/产出)；含晨间简报合并(09:00 MorningPriority并入10:00 DailyPlan)+新鲜度闸门坑+工作line.md闭环；问"后台有什么自动任务"或增改停任务先读

## Key Directories
- `C:\ADHD_agent\` — 主工作仓库，包含游戏运营数据分析、活动复盘、skill 脚本等
- `C:\ADHD_agent\KB\` — Obsidian 知识库，存放方法论、设计文档等
  - `方法论/` — 游戏数值设计框架、活动设计方法论
  - 标签规范见 [Obsidian KB 5维标签体系](reference_obsidian_kb_tag_taxonomy.md) — kind/domain/proj/fest/year 嵌套命名空间，归档新笔记按它打标签
- `C:\ADHD_agent\skills\` — 自定义 skill 脚本（generate_event_review, generate_event_review_v2, shop_exchange_analysis）
- `C:\ADHD_agent\.cursor\skills\` — Cursor skill 定义（event-review-overall, event-review-single, generate-event-review, generate-event-review-v2, branch-diff-gsheet）
- `C:\ADHD_agent\KB\产出-数据分析\` — 数据分析报告 + 图表输出（已合并原 report_images/）

## Google Workspace CLI
- GWS CLI 已安装，路径: `C:\Users\linkang\AppData\Roaming\npm\gws`
- 项目ID: `calm-repeater-489707-n1`
- 账号: `linkang@nibirutech.com`
- 读取 Google Sheet 的方式: `node C:\ADHD_agent\scripts\gws_stdin.js`（通过 stdin 传 JSON 参数）
- Token 过期(401 invalid_grant)时重新授权。⚠️**实测(2026-06-22)`gws auth login` 用 run_in_background 不弹浏览器、无输出**；正确做法=`gws auth login -s sheets,drive > /tmp/gws_login.log 2>&1 &` 后 sleep 几秒 `cat` 日志**抓出打印的授权 URL 贴给用户手点**(浏览器不自动弹)，回调端口由这次进程接收；点完 `gws auth status` / 重试原查询验证。`gws auth status` 看 has_refresh_token/encryption_valid
- **GSheet 读写统一工具**: [gsheet-toolkit](reference_gsheet_toolkit.md) — `C:\ADHD_agent\scripts\gsheet_utils.py`，读/写/删/备份/**按内容定位**全封装；操作 GSheet 先 import 它，别再现写一次性脚本（5个坑已固化）

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

## X2 客户端
- [X2 室内装饰家具资产链路](reference_x2_indoor_furniture_assets.md) — 装饰柱/地板/墙纸/挂件/柜台等资产在 `x2\Res\Shop\Indoor\`(Building/Decoration/Shelf)，命名X2_B/D_{节日}_XXX，只给3D+TGA无预览图(_D漫反射PIL转PNG看花色)；美术常给整套配置只投子集→易配漏；节日装饰换皮/起名/验收用
- [X2 DK 录入正确链路](reference_x2_dk_system.md) — 新增/换DK必走 P2数字系统(Display_*.asset/Path_*.asset, key=全局max+1) + x2-dk-manager skill；不是k1字符串系统；活动界面图配 2112 col17 icon_displaykey + col24 title_icon
- [X2 主城皮肤换皮完整链路](reference_x2_city_skin_chain.md) — 美术三族(大地图X2_Map/主城X2_T_Shop/特效Fx_Shop)+2D图标 → DK一键5型 → city_skin(表1312) → item(表1111)；含字段/QA表ID/陷阱(city_skin只留活跃皮肤·新id必须扫item引用避退役id·整行替换)，节日换主城皮肤套用
- [X2 活动 banner 换皮直出链路](reference_x2_operation_banner.md) — banner不走DK走路径：真源`C:\ADHD_agent\in-game-remote-assets\...\Assets\X2\operation\EventBanner\`，2112的banner_url列直接写`assets/x2/operation/EventBanner/x.png`；占星节同槽=格式锚+拓荒节同族=元素锚→GRFal生成(gpt现是long_running必须submit-only轮询)→upscale→PIL裁原尺寸→覆盖(留.meta)

## 配置表知识库
- [X3配置知识库交接文档](reference_x3_config_handover_doc.md) — 整合版单份交接doc(给同事)，KB留底+推到gdconfig仓dev_festival根目录；约定不主动update喊了再改
- [节日活动形式知识图谱](reference_festival_knowledge_graph.md) — 39种活动形式的机制、数值、历史数据回归，节日设计时先读
- [Config Library](reference_config_library.md) — ⚠️**P2专用**表编号索引、换皮规则、常用 SheetID
- [X2 配置表查询权威源](reference_x2_config_library.md) — 🔒X2任何表SheetID必用 `gsheet_query.py resolve <表号>` 现解，禁硬抄P2 KB（id空间重叠会静默返P2数据）；含X2 gacha内外圈结构
- [X2 服务器schema查法](reference_x2_server_schema_lookup.md) — schema按服龄动态迁移(新服1→老服4+)，真源=数仓日报表(server_id/schema_id/schema_time)找用户要；⚠️igame-actv/skill的server-config.json全是P2服、fo/config schema表=国服死快照、iGame接口无schema字段
- [X2 挖矿小游戏掉落链路](reference_x2_metro_minigame_rock_drop.md) — level(两套布局col2主/col3备,design_b会被加载)→rock_drop(表3514)；fo/cn坑(cn是2024死快照,真源=GSheet)；换皮漏导rock_drop→服务端miningDrop空配置nil panic→矿占格放不了工人(X2-43003)；重导前先验真源有没有行；查"空地放不了工人/挖完不发奖"先读；含挖矿全表地图(3510/13/14/15/16/17/18各管啥)+科研面板重复诊断(X2-43058判非配置/客户端未去重)+3514拓荒掉落核查
- [X3 Config Library](reference_x3_config_library.md) — X3专属换皮知识库 `.cursor/x3-config-library/`，含 table-reference(表字典+9条必检) + activity-forms(51组活动形式/13种换皮主力)，x3-reskin skill 地基
- [配置表字段 Schema](../../../ADHD_agent/.cursor/config-library/table-schema.md) — 2011/2013/2112/2115/2116/2121/2135/2141/2142/2154 全字段定义+跨表追踪链
- 挖矿 35xx 表清单已写入 table-index.md — 27张表含 3510→3517→3516 追踪链、ID编码规则、26复活节案例
- [数值换皮决策框架](../../../ADHD_agent/.cursor/config-library/reskin-numerical-framework.md) — 道具层(系统/节日/配置)+数值层(流量侧改/变现侧不改)判断标准
- [节日换皮完整工作流](reference_reskin_workflow.md) — 脚本用法+JSON模板+必检表清单+写入安全规范+行军表情AI生成链路+下次换皮checklist
- [Morphix 换皮工具逆向+prompt库](reference_morphix_reskin_prompts.md) — 内部Morphix网页=GRFal前处理层；8功能换皮prompt全文已归档`KB\方法论\Morphix换皮工具逆向_prompt库.html`，做UI换皮/节日换皮/图标/拆图前先读、prompt直接复用
- [P2 养成线知识体系](reference_p2_progression_kb.md) — 数值手册 + 制作人梳理 + 数据现状档案 三件套，含跨项目搬运参考(§九)
- [X2 养成线付费价值手册](reference_x2_progression_kb.md) — 7 条养成线付费价值 + 4 份活动明细，demo: x2-value-manual_5185
- [X3 TimeCycle](reference_x3_timecycle.md) — X3 项目 TimeCycle↔ActvOnline 绑定、TriggerType 隐性限制、openpyxl 加载坑
- [xlsx git 差异对比脚本](reference_xlsx_git_diff_tool.md) — `C:\Users\linkang\xlsx_git_diff.py`，看 xlsx 配置表 HEAD vs 工作区单元格变更，问"看diff/改了啥"时调用
- [X3 仓库路径](reference_x3_gdconfig_repo.md) — X3 配置仓 `C:\x3\gdconfig\`；**导入只认 tsv\（改 tsv 不碰 xlsx）**，data\xlsx 仅备份下周删，旧 `C:\X3\`/`C:\x3dev\` 弃用
- [X3 代码仓](reference_x3_project_repo.md) — `C:\x3-project\` 服务端+客户端代码仓，含 server 目录结构/高频路径/GitLab API 访问，触发"查X3代码/X3服务端/X3代码库"先读
- [X3 unity-mcp 现状与起法](reference_x3_unity_mcp.md) — X3客户端工程已装unity-mcp包+本机已装uv；Windows起法(Unity Start Server+Auto-Configure，必须在C:\x3-project根起cc)；做X3客户端Unity自动化先读
- [X3 customParam驱动可热部署活动·代码决策模板](reference_x3_customparam_activity_pattern.md) — 可变运营参数从配表搬到iGame部署参数=零代码/零热更换参数；9条代码决策+文件checklist(KB全文);逆向大哥竞猜重构;加同类活动/学活动代码架构先读
- [X3 配置知识库](reference_x3_config.md) — Item ID规则、asset_id格式、配置真源 tsv\(改tsv不碰xlsx)、节日Pack ID段
- [X3 Reward 表写入规则](reference_x3_reward_table_rules.md) — DropPara 必填+同 RewardID 内 seq 必须连续，2026-05 夏日 210921 踩坑总结
- [X3 累充隔离机制](reference_x3_recharge_isolation.md) — TaskType 902 + ActvOnline.RechargePointPackWhitelist + ActvTask 全档位 Parameter1 三表协同
- [X3 i18n 本地化工作流](reference_x3_i18n_workflow.md) — TXT_ key 命名规则(TXT_{Table}_{Field}_{ID}) + CompositeI18n monkey patch + gws.js 实际路径(run-gws.js) + 翻译术语对齐 + `_backup_*.xlsx` 污染扫描器
- [X3 礼包弹窗背景渲染优先级](reference_x3_pack_panel_rendering.md) — Pack.MainBg 覆盖 ActvOnline.ActvImg；拜访礼包 MainBg 必须空否则顶替节日 banner
- [X3 装饰阶梯礼包 tab 图来源](reference_x3_pack_tab_icon.md) — 底部商城页签 tab 图读 PackTypeInfo.Icon 不是 ChainPack.Icon，节日换皮必查 3 处 Icon
- [X3 礼包开启机制速查](reference_x3_pack_open_mechanisms.md) — OpenActv 常为空时礼包靠什么触发显示：英雄晋升(PackHeroPromotion)/道具获取弹窗(ItemObtain,PackType15)/拜访礼包(ActvVisitPack,ActvType56)/链式；含 Pack tsv 表头在 row5 坑 + TimeCycle 名复用陷阱；问"礼包怎么开/不显示"先读
- [X3 客户端资源位置 & DK 注册](reference_x3_client_resources.md) — .png 实际位置(ActivityImg/Pack)、DK→GUID asset 注册、tableResInfo.txt 名单可能过期
- [X3 新增活动界面链路](reference_x3_client_new_ui_workflow.md) — UI框架4件套(业务类/手写Auto绑定/prefab/路由)、复用ActvType换UI按ContentID分流、可复用组件清单(UIBtnPurchase/ItemUnitView/StartTiming)、day锁纯客户端坑；做X3新界面/界面换皮前先读
- [X3 八大外显模块→客户端资源路径总表](reference_x3_cosmetic_resource_paths.md) — 白皮书8模块(英雄皮肤/岛屿/家具/装饰三件套/航迹/头像框/纪念卡/表情)逐一对应资源类型+实际路径；前5模块3D/Spine/特效(重)后3模块纯2D(轻)；配活动/出美需/判换皮工作量时查
- [X3 航海之路地块美术链路](reference_x3_voyage_art_chain.md) — 大富翁式活动(ActvType=28)；地块图写在 ActvVoyageEvent.DKImg(按事件组×等级换图,约4套岛图)，24格位置prefab写死；含配置表/GridItem.cs渲染链/换皮清单/开启链路
- [X3 付费机制速查](reference_x3_monetization_mechanics.md) — 重复外显转钻补偿(Regained,通用所有外显/头衔) + 储蓄罐PiggyBank(可重复绑养成货币深度款) + 自选周卡WeeklyCard(原生复用,自选4项+7天+打包)
- [X3 节日付费表现](reference_x3_festival_performance.md) — 单服收益排名(尼罗$1127最高)、尼罗重上D17-D35窗口、饱和度速查、数仓SQL模板
- [P2 付费深度经验(X3第二轮借鉴)](reference_p2_depth_lessons_for_x3.md) — P2养成线深度诊断(价格断层/高价值无低门槛/订阅抗衰退/中R扩品类不提价/深度梯度/重铸保养无底洞) + 节日变现结构(三层:外显+小游戏增量+养成/GACHA深度引擎/宽口浅底病名/4阶段排期/情感外显)
- [X3 积分活动配置体系](reference_x3_score_activity.md) — ActvScore.xlsx 三 sheet + 最佳酒馆 ContentID 系列 + TaskType 440/444 + Rank/RewardSlot 结构 + ScoreID=603 易混淆陷阱
- [X3 导表迁移到 TSV 缓存](reference_x3_tsv_export_migration.md) — 导入只认tsv；**2026-06-04起新增 jenkins-xlsx-tsv-gate 强制 xlsx 与 tsv 一致**(旧"只改tsv/xlsx下周删"已推翻)：单边改→gate自动同步另一边但本次build rc=24失败需重导；两边不一致→拒绝；想一次过就 xlsx+tsv 两边同改成一致。改X3配置/导表前必读

## 数据查询
- [X2 节日收入日监控](reference_x2_festival_monitor.md) — `skills\x2-festival-monitor\`，新节日只改脚本顶部配置区；口径=dim_iap节日类型(抓复用旧id)+累充白名单段兜底；2026拓荒节在用
- [X3 节日收入日监控+日报](reference_x3_festival_monitor.md) — 移植自X2，`skills\x3-festival-monitor\`，全服，**节日礼包口径=ActvOnline累充白名单(不能用Pack前缀猜)**，模块按PackType，计划任务ClaudeX3FestivalMonitor每天09:00
- [X3 节日基线月环比分析法](reference_x3_baseline_mom_compare.md) — 评"节日有没有把基本盘做起来"：同生命周期(各窗口各取当时D35+成熟服)月环比、服数不同只比率、节日/非节日按累充白名单拆、基线窗口验无藏活动；含**合服踩坑(配置89服但只~50活跃出单服,按id区间聚合不丢数但单服指标用活跃服数)** + 夏日蚕食基本盘结论
- [X3 节日日报模板完整说明](reference_x3_festival_report_template.md) — 12区块结构+JS数据结构+6数据源+硬口径决策(成熟服1000-1540/付费玩家付费率/R级快照+累充兜底/同期对齐)+维护校验(f-string转义查stray{{)，2026夏日大改版沉淀，改报告前必读
- [X3 节日上线服龄覆盖+DAU查法](reference_x3_server_coverage_query.md) — 给上线日反推D35+可覆盖服+当期DAU；两坑：开服时间用真实首登(dl_server_login_info.min_register_time，非dim_open_server配置值)、合服作废id用近7日有登录过滤剔除(名义99服实际61活跃)；含一条可复用SQL+6.19/6.29基准
- [AI-to-SQL Skill](reference_ai_to_sql.md) — Datain 数仓 Trino SQL 技能，在 `C:\ADHD_agent\.claude\skills\ai-to-sql\`，查玩家明细/建筑/付费订单
- [X3 数仓外显/道具拥有率查法](reference_x3_datain_asset_query.md) — asset_id 带类型前缀(Item_/Hero_/Skin_/FurnitureSkin_)是最大坑(裸ID全返0)；含拥有率/R级分布/付费额SQL + dim_asset反查 + 用ai-to-sql不用datain-skill
- [X2 数仓资产流水/被回收名单查法](reference_x2_datain_asset_query.md) — v1089,asset_id裸数字无前缀(不同X3),change_type 1增2减,北京时间;回收=reason_id='item_recycle'+change_type='2',含补偿名单SQL;⚠️asset_id==cfgId但event道具发邮件可能报illegal
- [挖矿回归漏斗模板](reference_mining_funnel_template.md) — 分R级关卡漏斗HTML模板，`C:\Users\linkang\mining_funnel_template.html`，修改CONFIG对象即可复用
- [BINGO卡包日志查询](reference_bingo_asset_logging.md) — BINGO连线奖励白/绿包用任务ID查（不是活动ID），任务ID映射表+科技节发放汇总
- [P2数仓时区](feedback_p2_datain_timezone.md) — P2 ods_user_asset 的 created_at 是北京时间，不做UTC转换

## 活动设计产出路径规范
- [全链路产出路径](reference_output_paths.md) — 数值方案/美需/出图/数据分析四环节固定路径，数值方案在 `产出-数值设计\{项目}_{节日}\`

## 皮肤视频化生产
- [X3英雄皮肤视频生产知识库](reference_x3_hero_skin_video_production.md) — 替代Spine的展示视频production层：目标格式SBS(AllianceCard锚)+Spine精髓(idle循环非in/多层联动)+模型选型(kling fflf首尾帧=无缝循环命门)+透明化流水(generate_video→remove_bg→export_sbs)+★Prompt库与迭代日志(逐版优化到一步到位)；做/优化皮肤视频先读

## 美术需求生成
- [X2 美需生成 skill](../../../.claude/skills/x2-art-requirement/SKILL.md) — 主城特效参考图+美需文档全流程，含 GRFal async API 踩坑记录，触发词"美需/主城特效/出美需"
- [X3 美术资源规范](reference_x3_art_resource_spec.md) — 4维度：A出美需颗粒度/B落地交付(命名DK_/路径)/C格式现状(★尺寸不统一·跟复用源对齐;HUD icon124×136/铭牌752×192/头像框256×256)/D★换皮必双参考(老图=格式结构+新图=实际投放物元素;投放物多是现成资源去配置表+client搜不是生成,搜不到才新出;路径必验存在)
- [gdesign(.designdeck)位置与陷阱](reference_gdesign_designdeck.md) — X3设计系统+工作流基础设施在`.designdeck\projects\X3\`；⚠️文档里E:\路径全是旧的(本机不可达)，全量素材库真实在`C:\x3-project\client\Assets\Res\UI\Spirits`(6034张PNG)；交互原型保真(8-9成像)=禁CSS糊·引真PNG+缺则Morphix prompt生成
- 美需本地存档路径：`KB/产出-本地化与美术/{项目}_{年份节日}_{类型}_美需.md`（P2/X2 两个 skill 均写此路径）
- GRFal 参考图：`KB/产出-本地化与美术/ref-images/{节日}/`
- **x2-media 生图保存路径**：`C:\ADHD_agent\KB\产出-本地化与美术\{项目}\{类型子文件夹}\{类型}_{模型}_{日期时间}.png`
  - 项目：X2 / P2 / 通用；类型子文件夹：行军表情、技能图标、集卡册、活动图标等
- [透明资源必须差分法验真透明](feedback_transparent_asset_diff_check.md) — 我生成/处理的需透明图片入库前必跑差分法(白底vs黑底合成相减)，防 GPT 假透明(RGB无alpha肉眼像透明)；含 alpha 统计+PIL copy.py shadow 坑
- [X3 AI出图工作流(角色皮肤换装+活动UI换皮)](../../../../ADHD_agent/KB/方法论/X3_AI出图工作流_角色皮肤换装+活动UI换皮_世界杯案.md) — 世界杯案全程沉淀：两条线(本人立绘换装/原UI多图参考换皮)+逐轮只改一处+14条踩坑(long_running轮询·GBK控制台·多图--file·gpt保身份gemini保布局·角色易画太大顶UI文字·角色道具居中叠·质量锚+逐条改设计·IP风格化奖杯·先商量再出图)；**§8=策划案内嵌出图完整流程S1-S5**(参考拆基因→结构稿→Morphix职责切分换本游戏UI风格→只改一处迭代→回填策划案)+Morphix 8功能挂点表；**§12=改造现有界面效果图首选「真组件拼装→AI reskin五步法」**(拆prefab真sprite→CSS拼装定精确布局[=图#1,胜线框]→AI buildReskinPrompt职责切分[图#2=真实界面design system]合成统一成品；各取所长:拼装保位置/AI保观感统一·验证于养成手册双版本案)；做英雄皮肤概念图/活动界面换皮/策划案出效果图/给现有界面加改元素先读

## 待办
- [X2拓荒节装饰文案重写(等图)](project_x2_pioneer_decoration_copy_todo.md) — 5个装饰(350-354)文案太雷同要重写，等美术约06-05给正式图，含全部表坐标/key/遗留问题，明天接着干

## 节日开发周期
- [节日开发月度周期](project_festival_dev_cycle.md) — 第2周三部署、周四灰度D0、D14回归、D21出下期方案
- [X3 下期节日优化待办](project_x3_nile_next_phase.md) — 第二轮优化输入：夏日恋歌回归(breadth成功/depth没起来) + 5模块清单(付费深度=最高优先)
- [X3 英雄皮肤投放调整](project_x3_skin_deployment_adjustments.md) — 双皮肤改保底概率+跨服排行榜保留，本服排名门槛太低($15获取)是ARPPU低于P2的根因

## API Provider
- [API Provider 切换记录](project_api_provider_switch.md) — 2026-05-22 切到 one-hub，2026-05-25 周一切回 Anthropic 官方 API

## 工作流
- [配置改动备份规范(归KB·按功能·脚本进KB·导表成功删staging)](workflow_config_backup_kb.md) — 配置类改动备份沉KB固定路径，一个功能一份自包含.md(含before→after+恢复法)，脚本也进KB，仓内staging导表成功后即删；2026-06-18周卡案拍板
- [项目收口接管化归纳范式](workflow_handover_assetization.md) — 每次任务完成收口，判据=新agent冷启动能否在修BUG/接模块/换皮入口秒懂；大案子产三件套(决策记录按模块/换皮清单/目录FINAL标注)禁只留流水账；已进CLAUDE.md收口④
- [节日What's New出稿流程](workflow_whats_new_festival.md) — 喊"what's new"=①写活动总览公告文(范本X3夏日WhatsNew_夏日恋语.txt·模块名玩法读验收文件夹截图) + ②拷美术资源进验收文件夹(装饰=Pictures\{节日}装饰资源\·主城皮肤走DK提·前缀拓荒=Pioneer) + ③节日预告邮件(占星范本骨架·挑5主打·描述严格取What's New原文禁自编)
- [quality-gate验收系统+交互模块工作流](project_quality_gate_and_interaction_module.md) — 收工自动验收(task-checker+清单+Stop hook，有标记会拦收工) + 交互模块「活原型+实时说明一体HTML」工作流；改X3配置/写策划案/做交互原型时相关，2026-06-03搭建
- [验收清单/double-check设计四原则](workflow_checklist_design_principles.md) — 写/优化任何验收清单或checker prompt时套：①默认有罪姿态preamble ②强制留实际值证据 ③内联防什么坑 ④开放项+剪枝；2026-06-05 config/design-doc/i18n三份清单升v2
- [策划案设计质量验收(design-merit)方法](workflow_design_merit_critique.md) — 判"设计好不好"≠查文档全不全：好=对自己声明目的实现到位；硬gate=必须声明目的；目的→模块→表现&数值递归拆细到可查叶子(不套固定分类)；必带因果假设/基线/副作用三维；2026-06-05落地
- [交互原型素材化工作流(≈真游戏8-9成)](workflow_interaction_prototype_assetization.md) — 原型别用emoji/CSS糊：真素材优先(6034库C:\x3-project)→缺则Morphix生成→KB自包含三步；范例深海大富翁保真版；接design-merit表现支；工作流全在KB不在.designdeck；2026-06-05
- [P2导表工作流](workflow_p2_table_import.md) — GSheetDownloader管道运行，表号空格分隔，触发词"P2导表/传表/导表到bugfix"
- [导表只导第一个页签](feedback_table_export_first_tab_only.md) — P2/X2导表只读GSheet首页签；导非首页签要置顶，全部导完后还原页签顺序+删备份表
- [X2导表工作流](workflow_x2_table_import.md) — fwcli+x2gdconf，先读路由规则再读download skill，触发词"X2导表/X2下载表/X2刷表"
- [X2节日活动上线表写法](workflow_x2_festival_launch_table.md) — GSheet 1QfV-hLx... 每节日一页签；灰度[1002102]/正式双批次17列、日期整体平移、灰度先发的正式剔1002102、服务器从iGame现拉；写"上活动表/上线时间表"先读
- [X2 i18n 重复key取首条](feedback_x2_i18n_duplicate_key.md) — 同一LC key多行时fwcli取首条→显示旧/错值；文案显示异常先查重复key
- [X2 限时抢购礼包占位数据](feedback_x2_flashsale_placeholder_data.md) — 限购2222/价555/默认头像=跑旧配置；vm包正常+IAP包占位=iap跨表没加载；重开活动/重热更即修
- [X2道具单价看白皮书不用X3钻石折算](feedback_x2_item_pricing_whitepaper.md) — X2道具美金单价查养成线白皮书/付费价值表，禁用「钻石值×比例」(那是X3口径)；装饰券=$0.5，X2.42998替换踩坑
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
- [X3 本地服 GM/调时间 telnet 链路](workflow_x3_local_server_gm_telnet.md) — 端口=23000+NodeID、player-scope GM 要 @uid、❗telnet 分包协议(命令体与\r\n分两包发)、GMSetServerTimeOffset 设D30持久化；调本地服时间/本地发GM时用，helper `~/x3_gm.py`
- [X3 礼包美术全链路(装饰+拜访)](workflow_x3_decoration_video.md) — 两类礼包对比(装饰有视频/拜访MainBg必空)+各自产出物+通用环节(HUD图标124×136/DK注册/GRFal踩坑)+产出记录

## User Preferences
- 语言: 中文
- 分析报告风格: 数据驱动，含模块/R级分层分析，关注节日整体ARPU（模块收入/节日付费人数）而非仅人次ARPPU

## Feedback
- [X2通行证复用id限购坑](feedback_x2_pass_reuse_limit_trap.md) — 复用旧iap id+limit_cnt=1+period≈100年=终身限购，老玩家上期已用名额→本期买不了；修复=limit_cnt+1；上线前用老玩家账号实购验证
- [遇问题先反馈别硬怼工具](feedback_surface_problems_not_thrash.md) — 工具异常/自己不确定立刻一句话问用户，别手搓一次性脚本/混用工具输出/跳过现成skill硬干；2026-06-09把X2限时抢购抽奖改崩+越查越乱被批
- [生产操作先报再动](feedback_production_ops_announce_first.md) — 活动提交/取消/下线/邮件每步先说再干；**失败后的重试=新操作必须停下报告**；2026-06-12累充失败私自重试被批
- [删改用户内容模块前先问](feedback_ask_before_modifying_user_content.md) — 删/改用户做的内容块前先单独问，授权范围精确对齐不连带删；2026-06-03误删了给制作人看的一句话总览
- [动在途仓库前先摊清单确认](feedback_confirm_before_touching_inflight_repo.md) — 仓库有未推送提交/WIP时，merge/pull/rebase前列在途清单+方案给用户确认，承诺不push就不push；2026-06-12被打断纠正
- [改sheet/策划案过审提速与少返工](feedback_sheet_edit_review_efficiency.md) — 复用gsheet工具不现写/按内容定位不手算行号/改前全量扫一次批量改/checker喂dump约束输出
- [节日ARPU分母用当日总付费人数](feedback_x3_festival_arpu_denominator.md) — 节日ARPU=节日流水/当日总付费人数(所有付费玩家)，不是节日付费人数；覆盖旧"模块收入/节日付费人数"表述
- [X3 TOKEN actual_charge 单位坑](feedback_x3_token_actual_charge_unit.md) — TOKEN货币actual_charge自2026-06-02改记代币单位(=USD×100)；收入口径只有usd取actual_charge其余取pay_price；日报数据"暴涨"先查这条
- [GSheet 写入兼容性陷阱](feedback_gsheet_write.md) — API 能跑，坑在双引号/撇号/换行等字符转义
- [GSheet append 行顺序陷阱](feedback_gsheet_append_order.md) — INSERT_ROWS 插到开头不是末尾；正确做法：insertDimension + values.update
- [GSheet 配置表写入前置清单](feedback_gsheet_config_write_checklist.md) — 写前确认页签/表头/参考行逐列全比，写后验证行数+列完整性+位置
- [配置前先追完整链路](feedback_config_chain_first.md) — 先追两层引用链再写，含占星节drop_topay和集卡册实战案例
- [配置校验必须端到端](feedback_verification_end_to_end.md) — GSheet+本地TSV+分支推送三层验证，不过早下结论
- [改配置前先确认真源与落地路径](feedback_confirm_source_of_truth_before_edit.md) — 动手前先答"真源是啥+改动走啥管线进游戏"；X3真源=tsv，X2/P2真源=GSheet(改tsv会被导表冲掉)；2026-06-04把X3习惯错套X2
- [DK 资源层工作流](feedback_dk_resource_workflow.md) — DK区间规划→GUID从.meta读→脚本追加→Unity导出→push client→再导配置表
- [碎片化并行工作节奏](feedback_fragmented_time.md) — 任务拆分要细粒度、弱耦合、可随时捡起
- [说人话少用术语](feedback_plain_language.md) — 规划/笔记文档用功能动词+人话解释，不堆代号和技术黑话
- [iGame cancel vs recall](feedback_igame_cancel_vs_recall.md) — "下线活动"任务，部署申请状态 → recall；上线中状态 → cancel
- [igame-actv recall/cancel 已实测(X2)](project_igame_actv_recall_cancel_pending_test.md) — X2提交即直发无审批态:recall空操作(success是假象)、cancel才生效(ids逗号字符串,status 20→7)；P2审批流场景待验
- [数据回归必须先问设计方案](feedback_data_regression_ask_design_first.md) — 不能纯看购买数据反推礼包结构，先反咨询设计方案再用数据验证
- [数据回归分析方法论](feedback_data_regression_methodology.md) — 锚点是价格锚不需优化购买率；进度断崖要用全量/付费停留曲线验证而非归因免费资源
- [随机礼包期望值调整原则](feedback_numerical_design_random_pkg.md) — 无数据支撑不调整 drop 权重，floor/锚点变动不自动联动期望值
- [美需动画脚本写法](feedback_art_brief_script.md) — 元素只写定性描述，不写透明度/px/秒等参数
- [X3 主城皮肤=岛屿皮肤](feedback_x3_island_skin_terminology.md) — Item_81xxx非FurnitureSkin三件套；每次讨论X3皮肤先确认品类
- [配置写完必须反查验证](feedback_plan_index_must_be_fixed.md) — 写配置表后必须反查上下游一致性，写完不检查是根因
- [发现新规律必须立即更新知识库](feedback_proactive_knowledge_update.md) — 修BUG发现新链路/必检表时，当场更新SKILL.md，不等用户提醒
- [GSheet 写入安全规范](feedback_gsheet_write_safety.md) — 写前必须 duplicateSheet 备份页签；禁止按行号盲删；脚本崩溃后先验证实际状态再重跑（例外：1011本地化表不备份 → [X2/P2本地化表不备份](feedback_x2_i18n_table_no_backup.md)）
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
- [常规可逆操作直接做不要墨迹](feedback_decisive_on_reversible_ops.md) — git stash/pull/rebase/push 等可逆操作直接执行，别当高风险决策反复请示（本次被批"墨迹/变笨"）
- [X2导表别过度验证](feedback_x2_import_dont_oververify.md) — diff是真改动直接列清楚报给用户定夺，不反复刨缓存/真源；含PS5.1编码比对正确姿势(别用Get-Content)+清tmp_xlsx被拦的绕法
- [X2合并两节日分支进master_bugfix的坑](feedback_x2_merge_driver_drops_remote.md) — driver按行位比较非IDkeyed→插行就误报冲突+返1丢对方整份改动；正确解=ID-keyed cell级三方合并器 id_merge_3way.py(在x2-config-download/scripts)；net_new=0全表证dev⊇master,别信行位diff判分叉
- [X3 手工启服 cwd 必须用 server\Resource](feedback_x3_server_launch_cwd.md) — RunWorkingDirectory=../Resource，cwd 错了启动期 log4net 抛 DirectoryNotFoundException 进程僵尸
- [hook 路径必须用正斜杠](feedback_hook_path_forward_slash.md) — Windows hook command 反斜杠被 POSIX shell 吃掉，报"脚本丢失"其实没丢；报错路径反斜杠全没了=转义问题
- [含中文的.ps1必须存带BOM的UTF-8](feedback_ps_script_needs_bom.md) — PS5.1按GBK读无BOM UTF-8脚本，中文吃掉引号报"missing terminator"，定时任务LastResult=1；Write建脚本后用Out-File -Encoding utf8重存
- [每日报告HTML化+通用渲染器](reference_daily_report_html.md) — 每日日报/工作节点已渲染HTML每天浏览器弹出；通用 render_report_html.py 吃日报卡片格式+轻markdown，复用别现写
- [工作日报跨天污染根因+修复](feedback_daily_report_crossday_bleed.md) — 别按jsonl文件mtime挑会话(长会话跨天续用会把多天历史误算成今天)；已加 extract_today_sessions.py 按消息真实北京时间过滤，6-08"全错"根因
- [手改 X2 i18n tsv 两个坑](feedback_x2_i18n_tsv_handedit.md) — i18n tsv 是 CRLF(text 模式写 LF 整文件 diff，须二进制读写) + LC id 末尾含目标数字子串(只改 value 列不能整行 replace)
- [别把一次性成本误当硬约束](feedback_constraint_framing_onetime_cost.md) — 红线先分"永久"还是"一次性"；竞猜复盘:我把"新增proto=动客户端"当死墙绕成hack,大哥识别出只是一次性成本付一次买永久干净架构;警惕红线范围蔓延
