---
name: project-x3-circus-festival
description: X3 马戏节整节日换皮案——骨架=深海节16活动一模一样；扭蛋机等新开发归另一agent；唯一入口=换皮清单方案稿
metadata: 
  node_type: memory
  type: project
  originSessionId: 7f62bc78-a352-4bc4-a781-fbebf7babf20
---

# X3 2026 马戏节整节日换皮（2026-07-09 开案·方案稿待过审）

- **用户拍板口径（2026-07-09）**：整个结构跟**深海节**一模一样（X3 内换皮，16 活动骨架全克隆）；**额外开发内容（扭蛋机等）另一 agent 负责**——扭蛋机 X2→X3 搬运案见 [[project_x2_circus_strong_consume_reskin]]（勿混，两案在货币架构/hub 挂载处交圈）。
- **唯一入口** = `C:\ADHD_agent\KB\产出-数值设计\X3_马戏节\_马戏节_换皮清单与复用说明.md`（方案稿 v1：模块 copy-and-swap 表 + ID 段位已按 origin/dev 核过空闲 + 7 个待拍板决策点 + 工作量估算 + 开工流程）。
- **ID 段位速记（07-09 核实）**：ActvGroup 142/143；Pack 211032+；ChainPack 702/703；RankCfg 2002/2003；Item 新道具 1209+（1207/1208 已被扭蛋机预定，1203/1205 勿占）；⚠️ AO 101342/102247-249 已被占，BP 用 102250 起。
- **✅拍板结果（2026-07-09 用户过审）**：①货币=方案A（1207 扭蛋币不兼任·转盘券对单独建 1209/1210·大富翁沿用 1057/1202）②扭蛋机挂主 hub 142 ④双 BP 保留→**满级分重算必做** ⑤装饰家具复用已有 ⑥许愿池原位改共享组105 ⑦周卡/签到复用。**仍待定**：③大奖外显（占位不阻塞）+ 券对 1209/1210 定名（候选已给用户）。
- 排期未定 → TC 全填 0；开工前必过 `.cursor\x3-config-library\must-check.md`。
- **进度（2026-07-09 当天全速）**：方案稿✅→过审✅→档案✅→**15 模块配置克隆全部完成**（批次1-9 全推 origin/dev_festival，commit 链见档案，尾=016770b）→circus_scan 收口扫描全绿→本地 ExportTable 全绿×8轮。**定名**：1209马戏门票/1210马戏勋章/邀请函**1213**(1211/1212被扭蛋机agent实占,非原定1207/08!)/BP=马戏手记+巡游通行证/纪念卡81欢乐颂歌/铭牌106欢庆之星。
- **②大奖外显进展(2026-07-10)**：主城/岛屿皮肤客户端资源已落地——P2 anniversary2024 Lv2(马戏团旋转木马)整套搬为 `Homeland_Circus`，commit `5c503fe26bf` + Layer19隐形修复 `48a8ff4e85b` + 55°前倾站姿修复 `13605e592e2` + 贴图2048全分辨率 `296a249b881` + **贴图换 P2 Low 档烘焙版 `43b1f96db15`（07-13：High albedo 配 unlit 显平，Low 档光影烘进图才对；P2 shader 全家依赖全局日夜 uniform 不可搬，详见 [[workflow_p2_to_x3_asset_port]] 三号坑）** 已推 x3-project **dev_festival**；**给同事的独立资源包（07-13）**=`Desktop\Homeland_Circus_资源包_20260713(.zip)`：X3可用版20文件+P2原始双档59文件（High PBR/Low unlit 双档+3 shader+include+公共动画，原guid原路径）+自包含说明.txt（含shader全黑警告/DK自行注册提示/同guid勿双导）（评审分支 circus-homeland-port 同步至尾；**在途待用户反馈**：①顶部飞碟悬空——Blender基准图已证正确姿态=贴合紫棚（scratchpad/renders/AnnivLv2_f1.png），等用户 Scene 点选定位节点名+Y值回填 ②嵌套节点微调数值 ③~~火箭转不转~~✅会转=Animator正常 ④白模=Unity导入缓存吃到换图中间态（磁盘PNG已验真），等用户Reimport确认恢复；DK=`DK_Homeland_Circus` 已 Display+Path 双注册；搬运手法=[[workflow_p2_to_x3_asset_port]]；client worktree 已清理，调缩放直接在主工程改。**远端分支 `circus-homeland-port`**（07-10 从 dev_festival 拉出并推远端，尖=5c503fe26bf）=给其他职能同学看模型的评审分支，非开发线——后续皮肤改动仍走 dev_festival，评审完这个分支可删）。⚠️**主工程 `C:\x3-project` 分支随用户在 dev_festival ↔ circus-homeland-port 间切换**（07-10 晚在 circus-homeland-port@296a249b881=与dev_festival同内容；动仓库前先 `git branch --show-current` 现查别信本条）；原 dev 在途 churn（35视频meta空白+2图集自动注册）在 **git stash**（切回 dev 后 `git stash pop` 恢复或 drop）；此前的 untracked 预览拷贝已删（现为分支正式文件）。用户在主工程调缩放可直接 commit push dev_festival。**剩余接线**：gdconfig 配 Skin__Skin(SkinType=1, DK_Prefab=DK_Homeland_Circus, DK_Head=图标待出) + Item_81xxx 道具行 + 换掉15065占位；Unity 里 Ctrl+R+Ctrl+T(先LoadFromDisk后Save) 验证，嵌套实例 scale0.9/y-2.06 可视调。
- **待办尾巴（档案「上线前必做清单」6项）**：①组105许愿池+周卡奖池=**深海7/16下线后**才能原位改 ②大奖外显定案换15065占位 ③美术31+张（清单=`_马戏节_美术需求清单.md`）④长文本14语补翻 ⑤排期定了配TC ⑥数值终审。**jolt 全天 Jenkins 拒连，网络恢复补 `jolt_verify.py dev_festival` 一次覆盖**。
- **🔄批次10 玩法返工（2026-07-10 用户纠正）**：抽奖=**开箱非转盘**（克隆世界杯101516）——拆转盘三件→建 ActvCrafting 1517+奖池116（**大奖=英雄皮肤待定英雄**，5304001占位）+累抽1016 复用 30940-46；AO101026 原位转 type15；**改名：马戏福箱 / BP102250=马戏通行证**。commit c19d1bb·扫描全绿。**工作流铁律（用户教）：核心道具图先行→再出背景**（背景批v1 有 3-4 张中心物件错要重做，QA 结论在档案）；道具定稿 4 张（箱开/关+门票+勋章）生成中。
- **美需两单已提（2026-07-10，HTML 在 KB\产出-本地化与美术\）**：①`X3_2026八月庆典_主城皮肤_美需.html`（马戏团旋转木马正式版：**单档**·岛座整合+修缮清单+256图标+获取活动展示大图三项；展示视频归我方AI管线；低级档图已按用户要求删除）②`X3_2026九月海盗节_主城皮肤+三件套_美需.html`（海盗船**只出高级黑金档**·低级木船已删+海盗三件套横梁/地板/墙纸，P2 源模型可取）。生成脚本=scratchpad/gen_art_briefs.py（范式：A颗粒度/B交付/C尺寸/D双参考四维表+参考图内嵌）。
- **✅大奖外显全定案（07-10 终态·配置侧零待定项）**：开箱大奖=**阿米娜「猛兽驯服者」皮肤**（HeroSkin 102001/Item 5302001·批次12 commit 61d42e8·奖池116+c33钩子已接线·主稿出图中）；跨服榜大奖=主城皮肤**梦幻旋转木马**（Skin 1017/Item 81152·批次11 commit 7c6e68d·gdconfig 侧"剩余接线"已闭环，2D头图标仍占位待出）。选人依据=D35 渠道开放判据（27英雄合格清单+SQL查法在档案）；设计依据=`X3_马戏节\_马戏节_英雄皮肤设计brief_庆典x性张力.md`（尘白+碧蓝研究合成）。剩美术生产+上线前尾巴（见待办①③④⑤⑥，②已闭环）。
- 工作区=worktree `C:\x3\gdconfig-circus`（feature/circus-festival，push 用 `HEAD:dev_festival`）。
- **✅岛座卡片（2026-07-13 已推 dev_festival，commit `1f594a9b428`）**：用户反馈皮肤漂海上怪→根因=原生岛屿全是 2.5D 卡片岛座画在图里（实锤+解法见 [[workflow-p2-to-x3-asset-port]] 新段）。落地=Homeland_Circus 补 `island_base_card` Quad 节点（初值 scale5.8/y-2.8 **待用户 Unity 可视调**）+ `Homeland_Circus_Base.png`（AI 空岛座：岩石托盘+空草坪+马戏三角旗，1024 已去绿边，guid c1a5b0d2e6f3479a8b4c5d6e7f80a1b2）+ 材质克隆 homeland_1 卡片材质（X3_World_City 透明双面，guid d2b6c1e3f70458ab9c5d6e7f80a1b2c3）。worktree 已清理；用户主工程在 feature/skin-moment，预览=fetch 后 `git checkout FETCH_HEAD -- ...Homeland/Homeland_Circus*` 三路径（看完 restore），或切回 dev_festival 自见。此为过渡方案，正式岛座整合在八月庆典美需单里美术出；若要重出图，x3-media 任务 `20260713-101115-d1c9` 的 prompt 可复用。
