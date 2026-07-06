---
name: project-x3-hero-skin-video
description: X3 新案子——英雄皮肤新皮肤走视频(老皮肤走Spine不变)的客户端改造方案，策划案GSheet位置+核心结论+展示代码链路
metadata: 
  node_type: memory
  type: project
  originSessionId: 9e46b124-6441-4cf7-893a-41b8c4980d42
---

X3 新案子（2026-06-09 立项）：**英雄皮肤新皮肤走视频**。

## 一句话
英雄皮肤核心=Spine骨骼动画，AI(GRFal)做不了(出不了Spine)，但出得了视频→**老皮肤兼容不动继续走Spine，新皮肤改走视频**，AI 可全程量产新皮肤展示。纯客户端展示层改造，服务端无关。

## 策划案（权威产物）
GSheet「X3 英雄皮肤 · 新皮肤视频化方案」：`15Iacryl-uRDzaFUsErqvTvppnqMG0MuA3U1yKLKHuTU`
5页签：方案总览 / 规则说明(含▌界面交互+▌资源生产链路两小节) / 配置表 / 待确认事项 / 变更记录。已过 task-checker(design-doc) 10/10。

## 📦 首个落地视频皮肤实例：足球宝贝·爱莉希雅（2026-07-01 核实·世界杯）
问「某视频皮肤资源在哪」直接抄，别再 grep：
- **皮肤 5304001**（`Hero__HeroSkin.tsv` 行 104001「节庆-世界杯 / 足球宝贝·爱莉希雅」，本体 Hero1040 爱莉希雅）。配置里 **Spine 列空** = 走视频，末列视频 DK=`DK_video_zuqiubaobei_sbs`。
- 资源全在 `C:\x3-project\client\Assets\`：
  - **展示视频(核心)** `Res\Video\VideoRes\HeroSkin\zuqiubaobei_sbs.mp4`（SBS，取代 Spine 循环立绘）
  - 头图 `Res\UI\Spirits\Role\Character Portraits\Img_C_H_40_Skin01.png`（DK_Img_C_H_40_Skin01）
  - 全身立绘 `Res\UI\Spirits\Role\FullLength\Role_F_40_Skin01.png`（DK_Role_F_40_Skin01）
  - 卡面 `Res\UI\Spirits\Role\HeroCard\Role_C_40_Skin01.png`（DK_Role_C_40_Skin01）
- **视频 DK 注册** = `Assets\Res\Config\DisplayKey\Path_Video.asset`（`DK_video_<名>_sbs`→objPath），编辑器侧 `Display_Video.asset`。→ **视频皮肤 DK 走 Path_Video.asset 这一个专表**（非各模块 Path_*）。
- ⚠️只有 头图/立绘/卡面/视频 是皮肤专属；立体 model 仍沿用本体 `DK_Role_M_40`（没做皮肤专属 model）。皮肤属性配置链见 [[reference_x3_cosmetic_attribute_chains]]。

## 机制
每皮肤一个视频字段开关：空=老行为(Spine/静态图)，非空=视频。新旧共存、逐皮肤切换、零回归。
- 配置：HeroSkin 加 `DKVideo`，PackHeroPromotion 加 `AfterHeroVideo`（空=走原 Spine 字段）。
- 视频要透明(SBS/alpha export_sbs_video)+无缝循环，复用 BubbleVideoPlayer.cs。

## 英雄皮肤展示代码链路（验证 client dev 分支）
**所有英雄/皮肤 Spine 展示汇聚到一个咽喉方法** `UIHelper.CreateSpine(dkSpine, go容器, image兜底, dkImage)`（`UIHelper.Hero.cs:696`）。内置二选一：DKSpine 配了→`CreateEffect(dkSpine)` 走 Spine；为空→显示 `DKFullbody` 静态图（`:698-708`）。视频=第三条并列分支。
- 链路A·通用展示（5界面，都经 CreateHeroSkinSpine→CreateSpine，改 CreateSpine 一处全覆盖）：
  皮肤预览 `UIHeroSkinPreview.cs:70`(prefab `Assets/Res/UI/Prefab/Role/UIHeroSkinPreview.prefab`，容器`Root/Hero/HeroSpine`+兜底`Root/Hero/RoleImg`) / 英雄详情皮肤页 `UIHeroInfo.Skin.cs:228` / 详情主面板 `UIHeroInfo.cs:477` / 英雄预览 `UIHeroPreview.cs:88` / 获得展示 `UIGetHeroShow.cs:64,114`。契约统一= (HeroSpine容器 + 兜底Image)。
- 链路B·晋升礼包（独立，不经 CreateSpine）：`UIPackHeroPromotion.cs:104` 用 `EffectDisplay.DisplayKey=promotionCfg.AfterHeroSpine` 加载；`:115-128 PlayToHeroAnim` 抓 SkeletonGraphic 做黑→白渐显——⚠️视频prefab无此组件会静默跳过渐显，视频需单独做淡入。
- 换肤工具：`Utils/Spine/SpineSkinMixer.cs`(把皮肤部件attachment混到skeleton)。
- Spine 只用在「英雄角色立绘展示」一类(详情/预览/抽卡/获得/礼包/几个英雄活动)，**不在战斗本体/主城/行军**。

## 待程序拍板（策划案‘待确认事项’页）
①字段放HeroSkin/PackHeroPromotion/两边 ②播放组件复用BubbleVideoPlayer还是新封 ③透明SBS+shader与循环方案 ④EffectManager.CreateEffect扩展吃视频prefab还是另起路径 ⑤视频包体/性能预算(移动端解码发热)。

## 关联
- 资源路径+GRFal能力边界：[[reference_x3_cosmetic_resource_paths]]
- 视频基建(Res/Video/VideoRes/ + BubbleVideoPlayer)：[[workflow_x3_decoration_video]]
- 策划案模板/流程：[[workflow_x3_festival_design_doc]]

## 视频升级为完整版v8已进游戏(2026-06-13)
- 大哥需求迭代终点：**单条 15s 循环视频含全部**（入场→舞→单颠→兜球→高冷摇晃待机7s），替换原 5s idle 循环（commit a1e75da，同名 zuqiubaobei_sbs.mp4，零配置/程序改动）。生产全过程 13 版踩坑见 [[reference_x3_hero_skin_video_production]]§八。
- **待观察**：①SBS q12 25.7MB（原 3.5MB 的 7 倍）——真机解码+包体看完再定压缩(q16-18 可砍半) ②循环点(待机→再入场)实机感受 ③v8 表演收在 8s 与大哥要的 7s 差一拍，他不满意再用短 prompt 抽。

## ✅首皮肤全链路收官(2026-06-12晚)：视频+2D三件套+道具全落地
- 2D三件套已出图落仓（主稿onnx抠像加工,rembg的pymatting/numba会死循环→直接跑~/.u2net/u2net.onnx绕开）+3个DK注册(client 77057e6)；HeroSkin 104001 已回填 _Skin01 DK+典藏三列(title4/限定/bg3)+ObtainItemID=5304001；Item 表 5304001 道具行已加(icon复用皮肤头像,模板抄5303901)。导表 #841/#842 SUCCESS。
- **遗留**：①皮肤名/道具名/描述多语言——cn+en已手填(Soccer Babe · Alicia)，其余14国空,走 x3-translation-automatic 补 ②道具获取跳转占位「暂无获取渠道」，等世界杯开箱/礼包定了指过去 ③大地图3D模型复用本体(可选不做)。

## 皮肤铭牌显示链+属性档位锚(2026-06-12实测补漏)
- **铭牌=名字+属性两件事**：名字走 `TXT_HeroSkin_Name_{ID}` i18n key（Text表没行=英文客户端空白）；加成行读 HeroSkin `PropType/PropNum/Power` 三列（留空=铭牌缺属性）。配新皮肤这4样必填，我首轮全漏了。
- **PropType**: 220001猎人攻/220002射手攻/220003斗士攻（Property__BuffTemplate）；兵种看 `Hero__Hero.tsv` col8 Soldier(1猎人/2射手/3斗士)。爱莉希雅=3斗士。
- **档位锚（PropNum万分比/Power声望）**：无标 100(1%)/1万 · 史诗 5000/4-5万 · **限定 3000/3.6万**(103901) · 传说 10000/8-12万 · 至尊 15000/15-18万。
- i18n 细节：key 可多键合并共享文案（`TXT_HeroSkin_Name_X|TXT_Item_Name_Y`）；「限定/Limited」典藏标 16 国翻译整行复用 103901；**Text.xlsx 有585个公式→禁让 pre-commit 钩子 openpyxl 自动同步，COM 追加到两侧末尾保行对齐**。
- HeroSkin col17 buff备注=非导出公式列但 gate 比对：COM 填 PropType 后对该格单独 `.Calculate()` 刷缓存，tsv 填相同字符串（如 `斗士攻击 <color=#82b03d>{0}</color>`）。

## ✅首皮肤已落地(2026-06-12,足球宝贝104001,全在 dev_festival)
- **程序实现=X3NEW-1441**（已在 client dev_festival）：`UIHelper.Hero.cs ApplyHeroRoleDisplay(dkSpine,dkVideo,dkFullbody)` 优先级 **DKSpine > DKVideo > DKFullbody静态图**——视频皮肤必须 DK_Spine 留空才走视频。EffectDisplay 加了 `VideoDisplayKey`。
- **透明 SBS 判定=文件名约定**：`UIVideoPlayer.cs:213` `EndsWith("sbs.mp4")` → 文件必须命名 `xxx_sbs.mp4`。
- **资源指定路径（程序已注册 DK，配置照抄不要自创）**：`DK_video_zuqiubaobei_sbs` → `Assets/Res/Video/VideoRes/HeroSkin/zuqiubaobei_sbs.mp4`（Path_Video.asset，mp4走LFS）。程序原放了旧版kling v1(1.1MB 2488×1660)，已替换为正式版 v8无缝循环 SBS 3.5MB 2160×1920（client commit bd097ee）。
- **配置行**：gdconfig dev_festival `Hero__HeroSkin.tsv`+`Hero.xlsx` 加行 **104001 足球宝贝·爱莉希雅**（Group=1040，DK_Spine空，2D套件列暂复用本体40系DK，DK_Video=DK_video_zuqiubaobei_sbs；commit 7a47539+8f2d44e）。2D套件(头像/立绘/英雄卡 _Skin01)美术还没有，后续出图再换。
- ⚠️ gdconfig 改 Hero.xlsx 别用 openpyxl/sync脚本from-tsv（丢全簿公式缓存→毒化tsv），安全法见 [[reference_x3_tsv_export_migration]] 的 Excel COM+zip手术节。
- jolt 导表 race 坑：robot 导完往 client 推时若有人并发推 dev_festival → FAILURE "cannot lock ref"，配置本身没错，重触发即可。
- **★头像格式铁律(2026-06-12行军HUD穿帮实测)**：头像**不是方形满幅**！标准=**圆形徽章构图**——圆直径~208px、圆心(128,132)、内容全部裁进圆内、**画布四边四角必须全透明(margin≥16px)**。行军/航行HUD的圆框直接渲染原图，满幅方图会画到圆框外穿帮。锚=`Img_C_H_39_Skin01`(纯圆形)/`Img_C_H_34_Skin01`(脸占比参考)。验收法：检查png四边四角8px区 alpha 全0。gen_2d_suite.py 已固化此构图。
- **皮肤2D三件套规格（格式锚=本体同名件，全透明底）**：头像 `Img_C_H_{N}_Skin01` 256×256(★圆形徽章,见上条) / 英雄卡 `Role_C_{N}_Skin01` 306×418(头顶到腰胯半身) / 立绘 `Role_F_{N}_Skin01` 1024×1536(全身,人物占高~97%)，路径 `Res/UI/Spirits/Role/{Character Portraits|HeroCard|FullLength}/`。**道具icon直接复用皮肤头像DK**(参5303901)，典藏标签/边框用通用件(title4限定/bg3)不新出；行军3D模型可复用本体(105601先例)。三件套可从主稿纯加工(rembg+裁切)不必重生成，脚本 `KB/.../足球宝贝爱莉希雅/2D套件/gen_2d_suite.py` 可复用。
- **皮肤列表显示规则**（UIHeroInfo.Skin.cs:97-103）：列表=该英雄group全部HeroSkin行，只过滤 `IsHide`，**不要求拥有/ObtainItemID**——配置进客户端就显示(锁定态)。「推完配置看不到皮肤」先查看的那个客户端有没有 pull（配置bytes/代码/视频三样都走 client 仓 dev_festival，编辑器落后几百提交很常见）。

## 首个落地消费方(2026-06-11)
世界杯「足球宝贝·爱莉希雅」皮肤已定全部走视频(制作人拍板),世界杯案v0.23已对齐本方案(2D套件+DKVideo,主稿当原画,AI五步产链)——**本案客户端改造成为世界杯皮肤上线的前置依赖**,优先级提升;待确认事项需尽快跟程序拍板。见 project_x3_worldcup_activity。
