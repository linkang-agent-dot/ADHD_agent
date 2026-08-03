---
name: project-x3-flashsale-reskin
description: X3 马戏节第17活动·限时抢购 X2→X3 搬运案——唯一入口=换皮档案2026-07-22_限时抢购
metadata: 
  node_type: memory
  type: project
  originSessionId: 9f82ecf0-9f3b-4222-9ef6-3851bb882c23
  modified: 2026-07-31T08:46:45.411Z
---

# X3 限时抢购（马戏节第 17 活动）X2→X3 搬运（2026-07-22 开案）

- **🔴 2026-07-30 配置仓也清了（用户令：删配置 + QA/DEV 同步）**——三分支各一批纯删除提交，**导表全绿**（dev #2330 / qa #2332 / dev_festival #2333 全 SUCCESS）：
  - 分支与提交：`dev` ed5e8921（父 a0fad296）/ `qa` a1236f9b / `dev_festival` f5eeaa13。**master 本来就没有限时抢购配置**（c43303f7 从未进 master，def/tsv 零命中）→ 用户原以为要在 master 提 MR，实际无 diff 可提，MR 不存在。
  - 删的内容（共 105 行，零新增）：AO 101029 / Item 1214,1215 / Pack 211101-211108 / Reward 30 行 12 组(8202101-04 + 211101-08，seq 15930189-15930218) / RuleTips 40003 / i18n 31 key（16 个带数字 ID 的 + 15 个纯前缀的 `TXT_ActvFlashSale_*`·`Text_ErrCodeActivityFlashSale*`，**后者第一轮漏了，靠 `grep -i flashsale` 兜回**）/ 三张专属表 tsv 整文件。
  - **保留**：三个 `*_def.py` schema + `actvonline_def.py` 的 `ACTV_TYPE_FLASH_SALE=84`（占号防复用）+ PostProcessData SKIP_TIMECYCLE。**重做恢复表头 = `git checkout c43303f7 -- tsv/ActvFlashSale__*.tsv`**。
  - ⚠️**"留空表"这条路不通**：导表硬禁只有表头没数据行的 tsv（`PythonWriter.py` X3NEW-20），所以三表只能整文件删或留≥1行占位——见 [[reference_x3_tsv_export_migration]]。
  - x3-project 侧那 18 个生成物（proto/bytes/cs）**导表不会删除既有生成文件，仍在 dev/qa**，与 07-29「拍板不动」一致；已 `git grep` 复核无手写代码引用，删表不引起编译问题。
  - 坑：`csv.writer` 回写 Text__Text.tsv 会把土耳其语 cell 里的**裸引号重新转义**污染无关行 → 改用「csv.reader 定位物理行区间 + 原始字节删行」，diff 才是纯删除。dev_festival 上 Reward 冲突（driver 不敢自动合）＋多一条重复 key `TXT_ActvFlashSale_ComingSoon`，都按「取该分支内容再重跑删除」解，未批量选边。

- **🔴 2026-07-28 用户拍板推倒重做：x3-project 侧代码+prefab 已全量清除，配置仓原样保留。**
  - 清除提交 `973997a92ce`（已推 dev_festival），120 文件 / 19.7 万行**纯删除零新增**；等价 revert 四个提交 c329167a+abcc2e4f+b39aa389+e3122596。
  - **配置仓 gdconfig 一行没动**（新表3张/Item1214,1215/AO101029/Pack211101-08/Reward/i18n 全在）。
  - **✅ 07-29 复核定格**：玩法代码 / prefab / 共享注册（ActivityConst·activity.proto·msgid.def·两份生成 activity.cs·ActivityMeta.cs）**全部零残留**；但导表生成物 18 个文件已被 Jenkins 导表 robot 提交 `edad74aa187` 带回 dev_festival（`Res/Config/Proto/ActvFlashSale{,Pack,Reward}.proto` + `ProtoGen/*.bytes` + `CfgProtos/ActvFlashSale*.cs`，各带 .meta）。**用户拍板不动**——纯数据类无人引用，不影响编译/运行，重做沿用表结构还省事。**看到这 18 个文件不要以为没清干净，也不要再去清。**
  - 旧实现存档：代码 `feature/flash-sale` / 配置 `feature/flashsale-tables`，worktree `C:\x3-wt-flashsale` + `C:\x3\gdconfig-wt-flashsale` 均保留。
  - 只清了 dev_festival；三个代码 commit + 配置 c43303f7 **仍在 origin/dev 上**，等发版 dev_festival→dev 时这个删除才带过去。
  - ⚠️ 主仓 `C:\x3-project` 工作区当时有别人在途的未提交改动（含 ActivityMeta.cs 的 6 处限时抢购挂钩、Display_Activity/Path_Activity 的 DK 注册），**全程未碰**；那部分要自己剥。
  - 踩坑：`328ef08170f`（合并 dev 后 proto 重生成）把 msgid.def/两份生成 activity.cs 重排过，导致 `git apply -R` 打不上补丁 → 对生成代码只能按结构（大括号配平）摘块，不能靠补丁回退。手法见 [[workflow_x3_merge_conflict_audit]]。

- **定性**：用户 2026-07-22 拍板走 **A 方向 = X2→X3 新搬运**（X3 无原生限时抢购，程序要在 X3 实现协议+配置结构，跟扭蛋机 [[project_x2_circus_strong_consume_reskin]] 同套路）。7.29 版本，负责人林康。
- **唯一入口**（进度/决策/坑全在这）：`C:\ADHD_agent\KB\换皮档案\X3\2026-07-22_限时抢购(X2搬运).md`
- **一句话画像**：骨重皮薄。皮=7 张专属图（背景/banner/盒子/宝箱图标，"节日靠 banner 凸显换 banner 即可"）；骨=完整玩法（预告/抢购三场 utc2/10/18 + 全服限量+单人限次 + 分享→助力→抽奖破冰 + 8 礼包/期）。
- **📌 X2 侧 prefab↔代码 映射（2026-07-30 GUID 反查，全清单+节点路径在换皮档案「X2 侧 prefab ↔ 代码 绑定映射」段）**：四件套一对一＝`FlashSale.prefab`←`x2/Runtime/UI/Activity/UIActivityFlashSale.cs`(+Auto_) / `FlashSaleItem`←`UIActivityMayFestivalLimitTimeBuyPkgItem.cs` / `FlashSalePop`←`UIActivityMayFestivalLimitTimeBuyModulePop.cs` / `FlashSaleRewardGet`←`UIFlashSaleRewardBox.cs`(继承UIValentineBox)。**三条硬结论**：①四 prefab 互不嵌套、各自 assetPath 独立加载 ②prefab 上**零专属脚本**，绑定全靠代码 `GetChild("节点路径")`，节点改名即断 ③真逻辑在 module `UIActivityMayFestivalLimitTimeBuyModule.cs`(530行,P2五月节「限时购」命名,活动ID 21201441)，**别按 FlashSale 搜逻辑代码**；module 自己不出 prefab、直接挂主面板。⚠️`...RewardShow.cs` 指的 `Activity/Module/Ui21201400RewardGet` **x2client 全仓查无**（但第395行真被调用）→ 重做走 FlashSaleRewardGet 那条。工具＝`skills\unity-prefab-tools\prefab_code_binding_map.py`（本次新建，GUID 双向反查+节点路径清单，换皮开工先跑）。
- **prefab 已自取**：X2 客户端仓在本机 `D:\UGit\x2client`，四件套（FlashSale/Item/Pop/RewardGet）打包成验收 bundle → `D:\newX2\Copy\FlashSale\`（**不用用户手动导出**）。依赖打包器 = `skills\unity-prefab-tools\prefab_dependency_bundler.py`（可复用）。无 assetPath 动态加载盲区。
- **🔑 X3 侧只加载 `FlashSale.prefab` 一个（2026-07-30 grep 存档分支实证）**：`FlashSaleItem`/`Pop`/`RewardGet` 在 X3 代码里**零引用**——货架用主面板内静态节点 `Content/Grid/Item1..9`（`FlashSaleShelfItem` 包装，不 Instantiate 子 prefab）、详情用面板内子节点 `Pop`。⇒ **手动拼装只需动 FlashSale.prefab 一个**，另外三个是备用参考件（上一版落 4 个是整包迁移副产物，非必需）。Auto_ 节点契约清单（含 `BtnShare` 名字必须叫这个、Top 组五个路径）已列进换皮档案「Auto_ 节点契约」段。
- **👐 用户选手动走一遍（2026-07-30）**：路线 C（导出清单 + C-1 重导 diff + C-2 手动落地五步）已进换皮档案。
- **✅ C-1 已完成（2026-07-31）·翻车根因改判**：4 包走**断链路线**（Unpack，X3 侧要重写不保 x2 guid；`[Prefabs 0]` 是正确结果）导出至 `D:\newX2\{FlashSale,FlashSaleItem,FlashSalePop,FlashSaleRewardGet}\`，全线 `UNRESOLVED 0`。合并 160 guid，**X3 已有 108（零拷贝）/ 必须拷 52**；X3 侧无 FlashSale 残留。逐件 diff 上次 AI 落地（36 件）⇒ **AI 漏 19 个＝9 Textures + 7 Materials + 1 Shader + 2 anim，全在特效三层链上**，另多搬 3 个公共件 prefab。**⚠️ 改判：A 类外显翻车不是"AI 全自动"的锅，是用错工具**（路B 正则扫不见 .mat/.shader 内部引用）——同一个 AI 拿路A 包搬也不漏。文案 34 条唯一 key（繁中+英齐），`LC_EVENT_strong_consume_info_desc_2` X2 侧本就空。产物归档 `KB\换皮档案\X3\2026-07-22_限时抢购_导出包分析\`（52 件清单/19 件漏项/34 条文案/4 份 manifest）。⚠️ FlashSaleItem 导了两遍有 44 个 `_1` 孪生，落地只取不带 `_1` 的；`D:\newX2\Copy\FlashSale\` 是旧路B包+误导出的混合体别用。
- **🔧 重做操作单已成稿（2026-07-30，客户端 prefab 侧）**＝换皮档案「🔧 重做操作单」段，动手前照它走。三条硬结论：①**上一版落地成果可整包 git 取回**＝`git checkout 973997a92ce~1 -- <7 prefab + Res/UI/Sprite/UIActvFlashSale + 5 anim>`（37 资产/74 文件；权威清单＝`git show --name-status 973997a92ce | awk '$1=="D"'` 的 Res/UI 段；`Public/ProgressBarTemp.prefab` 是 X3 原生件别取），比从 bundle 重落省半天以上，因为**上次翻车点是 A 卡片外显+B 直购 IAP，不是 prefab 迁移**②**本案不适用录屏那套 Unpack Completely**（prefab 零专属脚本、绑定全靠代码节点路径，节点一改就断；打包器已保留嵌套 prefab 结构）③DK 7 条从未进远端（`973997a92ce` 没动 DK 表、dev_festival 的 DisplayKey 零 flashsale 命中）＝必重注册，且 DK 表多人共用**按 hunk 提**。
- **数值基准**：老案子 GSheet `1ceogA-kuwkT9E6r-6S4Bp1OCy77g5vq7aLgO076ICDY`（钻石版 ROI3.13 / 唱片版 5.80，8 档礼包 + 分享奖 + 抽奖池 6 项）。
- **⚠️ 已知雷**（X2-43094 历史，见 [[feedback_x2_flashsale_placeholder_data]]）：①抽奖奖池是 flash_sale_raffle 里的间接引用，必 fork ②累计道具（抽奖券）要连发它的 IAP 包一起换，否则抽不了奖 ③push≠生效，要构建+部署+重开活动才重读奖池。
- **✅ 决策点全部拍板（2026-07-24）**——**P2 ActvType=84+proto tag=67**（纠错：扭蛋机实为 83；proto 聚合 message 是 `ActivityItem`；84/67 dev+dev_festival 双分支都空）；**P3 机制道具 Item 1214=高级抽奖券/1215=皮肤随机宝箱**（纠错：马戏节实占 1207-1213）；**P11 分支=dev_festival**；**P1=单服/schema 组限量**（不动 CenterServer）；**P4=唱片 CD 并入钻石**；**P5=马戏节主题皮肤当抽奖顶奖**（款待选型，先占位）；**P6=单服内任意玩家助力**（保留拉新/不限工会/不跨服→自建破冰状态机单服简化版，免跨服 RPC，另需新做分享触点，不复用 Union Help）；**P7 数值=钻石线 ROI2+直购线 ROI7**。取证+落地 schema 全在代码方案 §七/§八。
- **✅ 数值定稿（2026-07-24 下午，走换皮相对守恒法 + task-checker 过 10/10）**：直购线 4 档=**照抄对标 X2 档(购1←#2/购2←#3/购3←#5/购4←#7)投放结构，数量×k(=7÷ROI_x2)**，ROI=7 由构造守住、**无需道具绝对钻值**；钻石线 ROI2；抽奖池保 X2 权重换道具+加速下调(7,200→800钻)；P8 限购按「场」(核 X2 giftLimitNum，纠真源"三场一期"错)。⚠️**教训**：v1 我手搓凑盘子(自己挑道具+造"待拍 V/W"伪阻塞)被用户纠正——换皮数值必须走守恒缩放,见 [[feedback_x3_progression_price_from_x2_handbook]]。X2 养成线手册单价仅旁证。
- **✅ 代码+配置全部落 dev_festival（2026-07-24 晚,周末用户验收）**：代码三 commit(1a骨架 c329167a/2客户端 abcc2e4f/1b服务端全逻辑 b39aa389,远端HEAD=b39aa389c36)+配置 c43303f7,**jolt 导表 SUCCESS(build #2126)**,GameServer.Hotfix 主Claude亲验 0 error。号段:CID8202/AO101029/Pack211101-08/货架820201-08(Group82021)/奖池820301-05(Group82022)。落地硬知识=[[reference_x3_new_actvtype_playbook]]。worktree:代码 `C:\x3-wt-flashsale`+配置 `C:\x3\gdconfig-wt-flashsale`(两主仓全程未碰)。
- **⚠️ 周末验收关卡与遗留**：①客户端 Unity Editor 编译**未验**(第一关)②prefab 拼装待手操(搬运包 D:\newX2\Copy\FlashSale,Auto_已按真节点预绑;分享按钮节点名待定/Countdown文本语义待核/Top组照扭蛋机移植)③直购线 IAP 占位(Price=0返错)④奖池2道具占位(7001/70003,待映射+P5皮肤选型)⑤i18n 14语+Pack名TXT待跑⑥ActvRule 独立RuleTips待建⑦TC=0 验收时 iGame 手开(AO=101029)。验收指引全文=换皮档案 §五·五。
- **关联**：马戏节整节日 [[project_x3_circus_festival]]（骨架=深海节16活动）。三案在货币架构/hub 挂载交圈别混。
- **接管化范式**：本案走 [[workflow_handover_assetization]] 三件套，收口挂进换皮档案。
