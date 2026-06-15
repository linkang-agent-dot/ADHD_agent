---
name: reference-x3-hero-skin-video-production
description: X3 英雄皮肤展示视频(替代Spine)的生产知识库——Spine精髓/模型选型/透明化流水/Prompt库与迭代日志，目标逐版优化prompt到一步到位
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8472eced-268e-4dc5-8a24-08559cc68e5c
---

X3 英雄/活动皮肤**展示视频**生产专属知识库（替代 Spine 的视频化方案落地production层）。
配套：方案立项见 [[project-x3-hero-skin-video]]；首个消费方=世界杯足球宝贝见 [[project_x3_worldcup_activity]]。
**目的：逐版迭代 prompt，命中后续皮肤一步到位。**

---

## 〇、显示框架与裁切真相（2026-06-15 实测+客户端对齐，最重要先读）
- **皮肤视频显示链**：HeroSkin.DKVideo → EffectDisplay.VideoDisplayKey → 同节点子物体 `VideoRoot`(填满HeroSpine容器) → RawImage，`m_ScaleMode=ScaleToFit`(**保比例、加黑边、不拉伸不裁切**)。
- **历史坑**：旧容器 `HeroSpine`=1024×1536(2:3)，视频是 9:16 → ScaleToFit 两侧留黑边、角色等效缩小 → 我曾用 1.08 裁切放大补偿，结果**把彩球裁出框**（左19/右20/上10帧 被切）。
- **★2026-06-15 客户端拍板：所有皮肤视频统一 1080×1920(9:16)，显示框按此比例**→ 不再 letterbox、不缩、补偿性裁切作废。以后皮肤视频一律原生 1080×1920 直出，不做后期裁切。
- **裁切根因分层**：① 我的补偿裁切（主因，去掉减半）② **AI 生成时大动作本身甩出框**——v8 未裁版举彩球过头(5.2s)/平举到两侧(3.3s)时彩球就出框了(上2/左7/右11)。**所以缩小角色救不了切，是动作够到框外**→ 治本=收敛编舞(彩球只在胸/胯前抖,不举过头不平举到边)，颠球是下半身不受影响。被切的只是彩球pom-poms，身体/头/脚始终完整。
- **角色框定权威参照**：爱莉希雅官方全身立绘 `client/Assets/Res/UI/Spirits/Role/FullLength/Role_F_40.png`(1024×1536,美术按展示框画的标准站位图)=占高95.2%/居中/脚底锚定 → 视频角色按此框定。Spine骨骼实读=890×1467(宽高比0.607)、脚底pivot、SkeletonData scale=0.01(故纯文件算不出屏占比,别试)。

## 一、目标格式（不用猜，游戏已有标准）
- **SBS 透明视频**：左半=彩色画面，右半=alpha 烧成的**白模 on 黑底**，整条并排。Unity 侧 shader 从右半重建 alpha（mp4 存不了原生 alpha，SBS 是标准 trick）。
- **参照物**：`Res/Video/VideoRes/AllianceCard_icon_1_a.mp4`（左绿蛇+右白蛇剪影）= 格式锚。siren/tiamat/egypt 系列同格式。
- 落地：`client/Assets/Res/Video/VideoRes/`，`BubbleVideoPlayer.cs` 播放。
- 现有视频时长基准：4-8s（siren解锁7s/驯化8s、tiamat 5s、egypt 5s、HeroAdvanture 4s）。

## 二、Spine 精髓（实机+代码双证，决定视频怎么演）
> 实地扒了 `client/Assets/Res/Spine/` 103 个 .skel.bytes + prefab。
- **皮肤展示=纯 idle 循环，没有入场**。prefab 的 SkeletonGraphic `startingAnimation: idle/idle2` + `startingLoop: 1`（实测 15/15 一致）。`in` 动画虽存在于骨骼数据(54/103文件)但**不是展示起始动画**（用于战斗/获得等别处）。→ **视频只做 idle 循环段，不做入场**。
  - ⚠️ 教训：别从二进制里看到 `in` 就脑补"入场播一次"——必须验播放端(prefab startingAnimation)。用户实机看到的才算数。
- **idle 是多层二级运动，不是整体呼吸**：rig 切成 20-34 部件独立绑骨（实测 Role_F_14：body/Face/eye/HairB后发/Larm1+Larm2双节臂/LXiu袖/QunB裙摆/kua胯/RLeg）。发飘+袖摆+裙摆+手臂微移+眨眼各自不同周期叠加→站姿也"活"。
- Spine 版本 4.1.17；展示只用于"角色立绘展示"（详情/预览/抽卡/获得/礼包），不在战斗/主城/行军。

## 三、演出脚本（角色视角，钩眼为王）
- **看的人**：纠结要不要冲榜的付费玩家 + 已拥有反复欣赏的鲸鱼。视频=转化面/炫耀面，不是壁纸，不能站桩。
- **心态(以足球宝贝为例)**：我是世界杯的奖赏，我知道你在看我且享受——自信带撩，"你想要我？去赢我。"
- **钩眼三板斧**：①眼神(目光扫镜头+了然微笑，最狠)②招牌beat只挑一个做透③身段曲线在余光持续撩。
- **★用户定调(2026-06-11)：别动太多**。≤3-5s 循环要自然，**动太大循环就假**。
  - 必须有：**胸随呼吸微微起伏**（这类皮肤核心卖点，要克制不浮夸）。
  - beat：**能做出 wink 就够了**，不要转球/抛接/撩发/大幅身段（全是循环杀手）。
  - 足球：完全静止（转动破坏循环）。
- **节奏(3-5s无缝)**：基准帧(主稿姿势)→吸气峰值(胸微起/肩微抬)→中段一次wink→呼气回落→精确回到基准帧。有一拍高潮其余松弛，全程匀速=催眠。

## 四、模型选型 & 透明化流水
**生成模型（generate_video，可选 seadance/hailuo/veo3/sora/vidu/kling/wan/runway/grok/happyhorse）：**
- ✅ **kling = 首选**：唯一成熟支持**首尾帧 fflf**——无缝循环命门(首=尾=同图)；角色首帧驱动稳；不强塞音频。**最短 5s**(到不了3s)。
- vidu：fflf 能更短(1-16s)，但默认带音频。需≤3s时备选。
- seadance：最全能但默认强出音频(UI用不上)。
- happyhorse：强制音频不可关，排除。
- veo3/sora：渲染慢(>10min占比高)、过杀。

**★无缝循环杀招**：kling `ref_types="首帧图像,尾帧图像"` + 同一张主稿传两次 → 首尾画面强制一致。实测首尾帧像素差仅 0.64（肉眼零接缝）。

**透明化链路**（白底主稿→抠像友好）：
```
generate_video(kling fflf, 不透明白底)
  → video_remove_background   (AI逐帧抠像得alpha; 参数 video_path)
  → export_sbs_video(quality高) (打包SBS左彩右白模, 参数 input_videos+quality)
  → 验收: 抽帧比对AllianceCard那张, 右半白模边缘(尤其银白发丝)干不干净/无逐帧闪烁
```
- 抠像最大敌人=杂背景/撞色。主稿纯白底+边缘干净已规避大半。
- **★透明化已实测跑通(2026-06-11 足球宝贝v7)**：① video_remove_background → **.webm原生alpha**(7MB清晰,通用透明) ② export_sbs_video → **SBS mp4**(2160×1920=2×宽,左彩右白模,游戏格式,对口AllianceCard)。实测白模干净、银白发丝没吃边。脚本`gen_transparent.py`。验SBS:左半BGR std高(彩色)/右半三通道差≈0(灰阶白模)。
- ★★**export_sbs_video 的 quality = CRF(越低越清晰),不是0-100百分比!** 实测:q=1→23MB锐度527 / **q=12→7MB锐度509(甜点,肉眼无损,正式用这个)** / q=23→1.9MB锐度434 / q=95→145KB锐度46(被截成51=糊成马赛克)。**之前传95糊掉就是这个坑**。15s片新数据(2026-06-13):q12=25.7MB锐度136 / **q19=11.9MB锐度132(-3%肉眼无差,要"10MB左右"用这档)**。
- ★**本地视频处理用项目自带 ffmpeg**：`C:/x3-project/client/Tools/VideoTools/ffmpeg/ffmpeg.exe`(含ffprobe；官方 compress_video.py 的内核,移动端策略=crf28/slower/yuv420p,有提交合规hook)。cv2 写不了可控码率 H.264(openh264 下到 cwd 能编但码率失控56MB)，一律 ffmpeg。
- **★镜头拉近定式(治"缩ref后人物变小")**：SBS 双半同窗裁切放大一步到位——`-filter_complex "[0:v]crop=w:h:x:y,scale=1080:1920[L];[0:v]crop=w:h:x+1080:y,scale[R];[L][R]hstack" -crf 19`，从最清晰 SBS 源单次重编码。**倍率用 alpha(右半)逐帧 bbox 扫描找拐点**(入场段贴边合法排除；v8实测1.08=27帧轻微出画可接受,1.10跳到108帧)。底部锚定保脚位。zoom 后锐度数值天然降(插值稀释高频)，别误判为压缩损失。
- ★**export_sbs_video 禁并发**(2026-06-13实测)：同账号两个 export 任务并发会**互相覆盖服务端输出路径**——下到两个字节级相同且 NAL 损坏的废文件(md5 一致)。SBS 导出永远串行跑。
- ★crossfade治循环踩坑:**对高帧间运动视频(seedance~3)做crossfade会重影且首尾差反变大**(循环点被挪进运动段)。高运动治接缝应改"最小差异帧对trim"或接受fflf自然seam,别crossfade。
- 银白发丝若真吃边的保险:重生成背景换**纯绿/品红**(远离银白)再抠。

## 五、调用 & 工具坑
- ★★**认证正解(2026-06-12实测)：用 `~/.config/grfal-api/token_store.json` 的 Bearer access_token（长效到2036），别再注入 `GRFAL_COOKIE`**。call_grfal 优先级=GRFAL_COOKIE > token_store，设了过期 cookie 反而把好 token 顶掉→401。浏览器 session cookie 内嵌的 access_token 只活几天(x2-media config.json 那份 06-05 就过期了)。下载结果文件也用 `Authorization: Bearer` 头。验活：`GET /api/tasks?page=1&page_size=1` 带 Bearer 应 200。
- ★★**还有一处暗雷：`GRFAL_COOKIE` 曾被设成 Windows User 级环境变量**（每个新进程自动继承，脚本里不设也会中招）——2026-06-12 已删（`[Environment]::SetEnvironmentVariable('GRFAL_COOKIE',$null,'User')`）。生成脚本统一开头 `os.environ.pop('GRFAL_COOKIE', None)` 兜底。
- ★cookie/token 失效症状=**轮询整场空状态**(check-task 返 `{"success":false,"error":"...401"}`,脚本解析不到 status 空转到超时像"还在跑")。轮询必须对 `success:false` fail-fast；后台跑生成脚本**别加 `| tail -N`**(截掉 task_id 断线无法续查)。
- generate_video 是 long_running：`--submit-only` 拿 task_id 再 `--check-task` 轮询，**别 --sync**。轮询间隔 20s，video 可能 5-12min。
- 脚本开头 `sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')` 防 GBK 崩。
- ★**cv2.imwrite 写不了中文路径(Windows,静默失败返回False不报错)**——KB 路径全中文必中招；写帧一律 `cv2.imencode('.png',fr)[1].tofile(path)`（读 VideoCapture 中文路径反而没事）。
- result 可能嵌套 list，递归 flat 展开；下载带 cookie header。
- `aspect_ratio`：~~永远传 auto~~ **(2026-06-12修正)auto 会抽风**——竖版首帧 ref 也可能随机出 1920×1080 横屏(seedance 实测)；**纵向视频显式传 `'9:16'`**，auto 只在无所谓画幅时用。
- 验无缝循环：cv2 抽首帧/尾帧算平均像素差，<3 很好 <8 可接受。
- 生产脚本：`KB/产出-本地化与美术/X3/足球宝贝爱莉希雅/视频/gen_skin_video.py`（kling版,改 REF/PROMPT 复用）+ `gen_skin_video_seedance.py`(seedance版)。
- **循环预览**：`_loop播放.html`(引同目录mp4,可切版对比;别人单收HTML打不开,要连mp4一起)。⚠️HTML里只能引 GRFal 原片(H.264)；**cv2 VideoWriter('mp4v') 重编码的文件浏览器播不了**，本地播放器才认。
- **透明抠像验证**：`_透明验证.html`——把带alpha的webm同时叠在棋盘格/绿/深蓝三背景上循环播,直观看发丝/碎边/残底干不干净(换webm名复用)。
- **★视频单文件分享**：要发群/给别人看循环效果,把mp4 base64内嵌进HTML(`<video src="data:video/mp4;base64,...">`)生成自包含单文件,谁都能双击循环播,不依赖外部文件(3MB mp4→~3.8MB html,IM当文件发OK)。

## 六、Prompt 库（中文定稿对措辞 → 提交转等价英文，英文对动作约束/seamless服从更稳）

### 当前最优·英文（v1 实跑版）
```
Subtle looping idle animation of the same character, identical to the reference image.
Locked camera, the character stays standing in the exact same pose and position, no walking, no turning, no big gestures.
Motion budget — keep it MINIMAL and natural:
1) gentle breathing: chest rises and falls softly (a subtle, alluring breathing dynamic), shoulders lift and settle very slightly;
2) ONE single natural wink (one eye closes and opens once, smoothly);
3) hair tips drift faintly as if in a light breeze; the skirt is almost still with only a faint sway;
4) soft golden ambient particles float slowly upward in the background, gentle gold rim-light shimmer.
The football under her arm stays completely still.
Everything returns exactly to the starting pose — seamless perfect loop, first and last frame identical.
Preserve the character's face, outfit, colors and art style exactly. High quality, smooth, no flicker.
```
### 当前最优·中文（对措辞用）
```
同一个角色的轻微待机循环动画，与参考图完全一致。镜头锁死，角色站定保持完全相同的姿势和位置，不走动、不转身、不做大动作。
动作幅度——保持最小、自然：
1) 轻柔呼吸：胸部柔和地微微起伏（微妙、撩人的呼吸动态），肩膀极轻微抬落；
2) 一次自然的 wink（单眼缓缓闭合再睁开，仅一次）；
3) 发梢如微风轻拂般细微飘动；裙摆几乎静止仅一丝轻摆；
4) 背景柔和金色粒子缓缓上浮，金色轮廓光微微流动。
腋下足球完全静止。一切精确回到起始姿势——无缝完美循环，首尾帧完全一致。
精确保留面部/服装/配色/画风。高质量、流畅、无闪烁。
```
### 可调旋钮（每轮只改一处）
- 呼吸/胸幅度：`subtle, alluring` ↔ 更明显/更收敛
- wink：可加"右眼、循环中段触发"
- 粒子/扫光：白底上看不太出且给抠像添边缘噪点→**可删，等UI层另加特效**
- 裙摆：`almost still` ↔ 放开更飘

## 七、迭代日志（命中要点后固化为"一步到位"模板）
- **v1**（kling fflf 5s）：无缝✅(0.64)/121帧24fps/1244×1660/白底✅。
- **v2**（同上+胸升主角/加腿/删粒子/wink降级）：无缝✅(0.62) 但**帧间运动暴跌 avg0.13峰0.23**（参考是0.4-0.9）→ 太木。**根因：minimal/never/almost still 等压制词叠加把动作压死**。
- **v3**（治糖人:整体联动重心线+解锁头眼神+胸夸张）：无缝0.64/运动0.27(回升但仍偏低)。
  - ★糖人病：**动作写成清单(胸一条/腿一条/发一条)→模型各部位独立动、头卡死=糖人无欲望**。修法=**写成"一条贯穿全身的重心线"**(重心移→胯→腰→胸→肩→头→眼神)，强调"整体协调、绝不各动各的"。
  - ★运动幅度带=**0.4-0.9**(用户认可实机Spine录屏实测)，prompt压太狠跌到0.1太木。
- **v3 鉴定（sub-agent 扮氪佬，只问色不色/吸引力/购买欲，不碰技术指标）**：色4 吸引3 购买欲2/10。批"像拍证件照、人是死的、性张力为零"。
  - ★★**根因暴露**：v1-v3 用 **fflf 首尾=主稿**锁死，而**主稿是端正立正立绘**→姿势/表情被框死,动作只能在"立正"上微调,撩不起来。要治本得动起点(A:重出有张力的撩人主稿当首帧 / B:松开fflf锁)。
- **v4**（高冷冷扫版）：见用户判。
  - ★★方向之争结论(真心讨论)：**高冷反差≠谄媚直球,是更高级的氪佬撩点**(买"高傲女神"的征服欲)。但 **高冷≠呆**:静帧看着像,气场相反——高冷=慵懒冷扫+睥睨+有体态;呆=躲闪+空眼神+立正。v3不是高冷是"没被导演到"。
  - ★高冷可导演的细颗粒(别写"高傲冷冽"这种糙词)：**冷热反差**(身热=呼吸曲线/脸眼冷=漠然)+**冷扫镜头三段**(目光斜侧懒飘→慢悠悠横扫到镜头停半拍睥睨不笑→懒懒飘开)+**慢**(慢半拍=高冷内核)+**下巴微抬做静态高傲基线(非动作,否则破循环)**+不笑。

- **v4 嘴部踩坑**：v4 给"嘴角微不屑"许可→AI 把嘴做成一张一合/露齿/warp,循环放大成"抽象脸"。
- **★真Spine脸部配方(扒参考录屏分区量化得出,已验证)**：
  - 运动量级 **胸(2.3-4.3) > 脸/头(0.9-2.2) > 下身(0.6-1.9)**,胸=呼吸是绝对主角。
  - **嘴=一个闭合的稳定形状,从不张开/不变形/不露齿**;脸部"活气"主来源是**头微侧倾/晃 + 眨眼**,不是嘴。(汉服参考实证:两帧嘴同形,只是随头平移)
  - ★所以锁嘴要**锁"形状"不锁"位置"**:嘴形全程不变但可随头平移。v5前我误写"嘴完全不动"→会连头部自然侧倾一起锁死成呆脸,错。
- **v5(脸修正:运动优先级胸>头>眼+锁嘴形状)**：✅**嘴根治**(抽帧两帧同闭合形,不再抽象)+脸高冷+眨眼冷扫出来了。⚠️但运动仅0.15(比v3/v4更低)——**精细脸部约束会连带把胸/头幅度压低=又偏木**。下版方向:保持锁嘴形,单推胸呼吸+头侧倾幅度(目标运动0.3-0.4)。
  - ★通则:**立绘视频脸部=头微侧倾+眨眼给活气,嘴锁形状(非锁死位置),五官变形慎给**。

- **v6(求自然/不锁嘴)**：运动跌到0.11(最低,太木)且嘴仍微张。→ **★kling 纯prompt撞墙(模型级,措辞绕不过)**：① kling 给2D立绘做脸,**嘴必张/warp**(锁也张不锁也张);② 一压"自然温柔"就几乎不动(0.1),一推动作就warp,**俩近乎互斥**。结论=该换工具层解,不是再调prompt:A换模型(seedance/vidu试2D脸是否更稳) B后处理冻脸(kling出动作+脚本把下半脸用主稿原图盖回,镜头固定头微晃可对齐) C推幅度认嘴动。
- **v7(seedance,只换模型/prompt同v6)**：★★**破局**——seedance 一发解决困了6版的两墙：**嘴稳了**(抽帧闭合不变形,远好于kling)+**运动3.2**(真Spine量级,终于活,kling才0.1-0.27)。代价=**首尾差1.79**(kling是0.6,seedance的fflf首尾同图锁得没kling紧,循环接缝可能轻微跳)。1080×1920/默认带音频。
  - ★★**模型选型修正(推翻§四"kling首选")**：**角色立绘idle视频改首选 seedance**——kling 给2D立绘脸必张嘴/warp且压不动是模型级硬伤;seedance 脸稳+动得足。kling 的强项只剩"fflf首尾锁得紧(0.6)循环无缝";seedance 接缝(1.79)需后续治(强化fflf/crossfade/视频循环工具)。
  - 脚本:`gen_skin_video_seedance.py`(model=seadance)。

## 八、入场片方向(2026-06-12晚,大哥定调；终态=单条直出带循环)
- **★终选架构(v4,用户逐步收敛)**：~~两条视频+程序切换~~ → **一条 10s 片含全部**（入场1.2s→舞2.3s→踩球0.5s→颠球2.2s→兜球0.8s→落定+表情渐变1s→高冷idle呼吸2s），fflf 首=入场版图/尾=高冷循环基准帧，客户端**循环播整条**（循环点=待机→再次入场，叙事自洽）。三大优势：①无拼接缝（拼接版缝处光影漂移 diff 32-36 用户嫌过渡不自然）②**程序零改动**（直接替换原循环mp4走现有链路，"入场播一次→切循环"需求作废）③seedance 单镜 10s 七阶段时序 prompt 实测扛得住（颠球/表情弧线都在拍上）。
- **★用户铁律(2026-06-12定死)：皮肤视频全部一条直出，不拼接**。拼接方案(SegA+SegB+渐变缝)技术终缝0.0但缝内光影漂移肉眼仍突兀，被毙两次。时长不够就先探 submit 是否接受更长 duration（seedance 15s 实测可提交），别想当然按 10s 上限切段。idle 加长也写进同一镜的 Phase 时序里。
- **超框治理(v6实测)**：①检测=`check_video_edges.py`(每帧四边3px条带扫暗像素,对照v8基线全0；right前几帧=入场合法/bottom=阴影合法/top+left大量命中=真超框)；②**prompt 写 CRITICAL FRAMING RULE 模型不听**(v6照样left 118帧超框)——**治根=把首尾参考帧人物整体缩90%再喂**(画幅不变四周让出安全边距,模型全片继承构图尺度)+甩臂限肩高措辞。两张 ref 必须同比例缩(只缩一张会造成全片缓慢缩放漂移)。缩放 ref 的副作用：ref 原底色(视频帧灰调)≠填充白边 → 成片有灰色内框，**去背后消失无害**；介意就缩前把 ref 底色统一成填充色。v7 实测缩90%后超框从160+帧降到个位数真命中(球最高点蹭1px,圆形+运动无感)。
- v7→v8：idle 段又被压制词写木（"only soft/very slight"复犯§七5号坑）→用户要"摇晃+突出胸部"。v8 Phase7 配方：**髋部主导左右摇+一条波传导(腰→胸→肩→头)+胸部呼吸明写成 visual centerpiece+发穗滞后半拍**——idle 段措辞永远从"动态感"起笔，别从"安静"起笔。
- **★时序控制真相(v9实测)**：prompt 里的 Phase 秒数 seedance 基本不遵守（写"7s内完成表演"实跑9.5s）——**压时长=砍动作内容**（舞砍成单组合/颠球砍成单触），模型按内容量自然铺时长，数字只是参考。验时序=抽目标秒数处的帧看演到哪了。
- **★动作要可数才会被执行(v10→v11)**：氛围形容词("lively sway/rhythmic"之类)模型常直接丢弃——v10 idle 运动量掉到2.91(比老循环3.72还低)。要某个动作必现就写成**可数节拍**："左…右…左…右，约2秒一个周期、共3个周期、NEVER frozen"。idle 运动量尺子：<3.5=木头, 4-7=正常活, 量法=帧间平均像素差。
- **抽卡操作法(用户定)**：单条直出框架下"只改某段"=基于上一好版微调该段 prompt 后**整条重摇抽奖**（接受其他段走样风险，walk back 就回上一版 prompt）；**同 prompt 并行双发**翻倍中奖率（成本=时间不变）。
- **★★prompt 长度=注意力预算(v11→v12 决定性实验)**：七阶段+一堆铁律的 350 词长 prompt 里，可数节拍照样被丢（v11 摇晃 1.20 史上最木）——**瘦身到 200 词（表演段压成两句、把摇晃段标 THIS IS THE MOST IMPORTANT PART）→ 摇晃 7.89 复活**且时序/球可见全保住。定式：**已验证模型会演的内容只给短提示，token 预算砸给最容易被丢的那一段**；每段诉求竞争注意力，堆细节=自我稀释。
- 道具消失坑：长 idle 段里被夹的球可能被彩球挡住或短暂"消失"→prompt 加"from this moment until the very end the football stays clearly VISIBLE tucked, never vanishing"。
- idle 加长直接写进同一镜 Phase 时序(用户铁律禁拼接)；gen_idle_tail.py 仅作历史 fallback 保留。
- **架构升级=Spine in+idle 搬到视频**：入场片(播一次,首帧自由) + 现有idle循环片。入场尾帧必须=主稿帧(循环入点)→无缝交棒。⚠️**需程序支持"入场播一次→切循环"**(现链路单视频循环)，命名约定提议 `xxx_in_sbs.mp4`。
- 大哥两反馈：①视频人物比spine靠下靠左(实测视频帧内人物居中满幅→是容器适配vs Spine锚点的系统性差异,治本=客户端加offset,**平移暂缓**) ②夹着球跳舞不合理→入场叙事=入场拿彩球跳舞→颠球→夹腋下→落定主稿→接循环。
- **三步生成链**：①开场版图(gpt改图保身份:人移右缘迈步+球放地面+腋下球去掉) ②SegA 0-5s(首帧=版图,seedance:入场两步→原地舞2.5s→舞收脚尖抵球定格,尾帧自由→抽实际尾帧) ③SegB 5-10s(fflf 首=A尾/尾=主稿:脚尖挑球→膝颠→脚背颠两触→兜进左腋→落定)。concat 零接缝(段间帧严格相同)。
- 颠球=最高崩险(球物理+脚接触),两触起步崩了减一触；逐秒分镜含动画原则(预备/跟随重叠/缓出)在会话2026-06-12,脚本 `视频/入场/gen_intro_*.py`。
- **★缝处理定式(v1实测)**：fflf 锁帧只锁姿势锁不住渲染光影(缝处人物区diff 32-36/背景区<6)。解法=`assemble_intro.py`：缝1(段间同姿势)4帧 crossfade；缝2(入场→循环交棒)**10帧渐变到循环首帧真像素+终帧=循环首帧本体**→终缝diff 0.0,客户端切视频零跳变。同姿势缝才可 crossfade(高运动缝仍禁用)。SegB 尾帧 ref 用**循环视频实际首帧**(不是原始主稿——那不是交棒点真像素)。
- v1实测亮点：SegA 尾帧自然演成"脚踩球"(比分镜的脚尖抵球更顺)→ SegB 顺势改踩球回拨挑起;seedance 颠球(挑起→膝颠→脚背→兜进左腋)一发可用。
- **★表情连续性原则(v1用户反馈)**：入场片表情要为"交棒进循环脸"服务——循环是高冷脸则入场全程笑容收弱(克制闭口浅笑)+落定段写"表情用整整一秒连续渐变到终帧的高冷沉静"，禁突切。曾想反向改循环成微笑营业版，用户拍板**循环高冷表现好不动，改入场迁就循环**——定式：先定循环的脸，入场表情弧线倒推。
- 包体账:入场10s(~7MB)+循环5s(3.5MB)≈10MB,成片后跟大哥确认值不值。

### ★皮肤视频撩人 prompt 心法（跨版总结）
1. **撩不撩的根在起点图**：fflf 锁主稿→主稿端正则视频再调也端正。撩人主稿(有张力姿态+眼神)是地基。
2. **眼神给不给镜头 = 死活线**：不给=证件照/糖人;给(无论暖撩还是冷扫)=活。
3. **写"一条动作线"不写零件清单**：否则各动各的成糖人。
4. **情绪要细颗粒可导演**：别用"性感/高冷"糙词,拆成眼睑/嘴角/节奏/重心的具体微行为。
5. **压制词(minimal/never/almost still)会叠加压死动作**,克制用。
6. **氪佬视角验收**(色不色/吸引力/购买欲)比技术指标(联动/幅度)更接近真实成败。
- 用户定调：**纯prompt死磕出一个好的就通吃,不走动作迁移捷径**。
- 参考素材：`皮肤视频_参考/`(文件名=用户点评:胸部好×4/姿势自然/腿不错/整体都好,实机Spine录屏900×1600;_分析/有抽帧)。
