---
name: project-x3-flashsale-reskin
description: X3 马戏节第17活动·限时抢购 X2→X3 搬运案——唯一入口=换皮档案2026-07-22_限时抢购
metadata: 
  node_type: memory
  type: project
  originSessionId: 9f82ecf0-9f3b-4222-9ef6-3851bb882c23
  modified: 2026-07-24T12:43:32.188Z
---

# X3 限时抢购（马戏节第 17 活动）X2→X3 搬运（2026-07-22 开案）

- **定性**：用户 2026-07-22 拍板走 **A 方向 = X2→X3 新搬运**（X3 无原生限时抢购，程序要在 X3 实现协议+配置结构，跟扭蛋机 [[project_x2_circus_strong_consume_reskin]] 同套路）。7.29 版本，负责人林康。
- **唯一入口**（进度/决策/坑全在这）：`C:\ADHD_agent\KB\换皮档案\X3\2026-07-22_限时抢购(X2搬运).md`
- **一句话画像**：骨重皮薄。皮=7 张专属图（背景/banner/盒子/宝箱图标，"节日靠 banner 凸显换 banner 即可"）；骨=完整玩法（预告/抢购三场 utc2/10/18 + 全服限量+单人限次 + 分享→助力→抽奖破冰 + 8 礼包/期）。
- **prefab 已自取**：X2 客户端仓在本机 `D:\UGit\x2client`，四件套（FlashSale/Item/Pop/RewardGet）打包成验收 bundle → `D:\newX2\Copy\FlashSale\`（**不用用户手动导出**）。依赖打包器 = `skills\unity-prefab-tools\prefab_dependency_bundler.py`（可复用）。无 assetPath 动态加载盲区。
- **数值基准**：老案子 GSheet `1ceogA-kuwkT9E6r-6S4Bp1OCy77g5vq7aLgO076ICDY`（钻石版 ROI3.13 / 唱片版 5.80，8 档礼包 + 分享奖 + 抽奖池 6 项）。
- **⚠️ 已知雷**（X2-43094 历史，见 [[feedback_x2_flashsale_placeholder_data]]）：①抽奖奖池是 flash_sale_raffle 里的间接引用，必 fork ②累计道具（抽奖券）要连发它的 IAP 包一起换，否则抽不了奖 ③push≠生效，要构建+部署+重开活动才重读奖池。
- **✅ 决策点全部拍板（2026-07-24）**——**P2 ActvType=84+proto tag=67**（纠错：扭蛋机实为 83；proto 聚合 message 是 `ActivityItem`；84/67 dev+dev_festival 双分支都空）；**P3 机制道具 Item 1214=高级抽奖券/1215=皮肤随机宝箱**（纠错：马戏节实占 1207-1213）；**P11 分支=dev_festival**；**P1=单服/schema 组限量**（不动 CenterServer）；**P4=唱片 CD 并入钻石**；**P5=马戏节主题皮肤当抽奖顶奖**（款待选型，先占位）；**P6=单服内任意玩家助力**（保留拉新/不限工会/不跨服→自建破冰状态机单服简化版，免跨服 RPC，另需新做分享触点，不复用 Union Help）；**P7 数值=钻石线 ROI2+直购线 ROI7**。取证+落地 schema 全在代码方案 §七/§八。
- **✅ 数值定稿（2026-07-24 下午，走换皮相对守恒法 + task-checker 过 10/10）**：直购线 4 档=**照抄对标 X2 档(购1←#2/购2←#3/购3←#5/购4←#7)投放结构，数量×k(=7÷ROI_x2)**，ROI=7 由构造守住、**无需道具绝对钻值**；钻石线 ROI2；抽奖池保 X2 权重换道具+加速下调(7,200→800钻)；P8 限购按「场」(核 X2 giftLimitNum，纠真源"三场一期"错)。⚠️**教训**：v1 我手搓凑盘子(自己挑道具+造"待拍 V/W"伪阻塞)被用户纠正——换皮数值必须走守恒缩放,见 [[feedback_x3_progression_price_from_x2_handbook]]。X2 养成线手册单价仅旁证。
- **✅ 代码+配置全部落 dev_festival（2026-07-24 晚,周末用户验收）**：代码三 commit(1a骨架 c329167a/2客户端 abcc2e4f/1b服务端全逻辑 b39aa389,远端HEAD=b39aa389c36)+配置 c43303f7,**jolt 导表 SUCCESS(build #2126)**,GameServer.Hotfix 主Claude亲验 0 error。号段:CID8202/AO101029/Pack211101-08/货架820201-08(Group82021)/奖池820301-05(Group82022)。落地硬知识=[[reference_x3_new_actvtype_playbook]]。worktree:代码 `C:\x3-wt-flashsale`+配置 `C:\x3\gdconfig-wt-flashsale`(两主仓全程未碰)。
- **⚠️ 周末验收关卡与遗留**：①客户端 Unity Editor 编译**未验**(第一关)②prefab 拼装待手操(搬运包 D:\newX2\Copy\FlashSale,Auto_已按真节点预绑;分享按钮节点名待定/Countdown文本语义待核/Top组照扭蛋机移植)③直购线 IAP 占位(Price=0返错)④奖池2道具占位(7001/70003,待映射+P5皮肤选型)⑤i18n 14语+Pack名TXT待跑⑥ActvRule 独立RuleTips待建⑦TC=0 验收时 iGame 手开(AO=101029)。验收指引全文=换皮档案 §五·五。
- **关联**：马戏节整节日 [[project_x3_circus_festival]]（骨架=深海节16活动）。三案在货币架构/hub 挂载交圈别混。
- **接管化范式**：本案走 [[workflow_handover_assetization]] 三件套，收口挂进换皮档案。
