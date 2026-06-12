# X3 英雄皮肤展示视频工作流：Spine → AI 视频（足球宝贝案沉淀）

> 2026-06-11 起。X3「新皮肤走视频替代 Spine」方案的 **production 层**：怎么把一张皮肤主稿，做成能进游戏、无缝循环、透明的展示视频。
> 姊妹篇 [[X3_AI出图工作流_角色皮肤换装+活动UI换皮_世界杯案]]（管静态出图）；本篇管**动起来 + 透明 + 循环**。
> 方案立项见 [[project-x3-hero-skin-video]]；recall 速查见 memory `reference_x3_hero_skin_video_production`。
> **核心目标：逐版迭代 prompt，命中要点后做到「换主稿+套模板=一步到位」。**

---

## 0. 这套要解决的三件事
1. **动起来**：一张静态皮肤主稿 → 会呼吸/眨眼的展示动画。
2. **透明**：UI 槽位要叠在背景上 → 视频要带 alpha。
3. **循环**：展示位无限播 → 首尾必须无缝衔接。

工具链同出图篇：`call_grfal.py` + `GRFAL_COOKIE`（`x2-media/config.json`）+ base `https://grfal.tap4fun.com`。
归档：`KB/产出-本地化与美术/X3/{皮肤名}/视频/`；落地：`client/Assets/Res/Video/VideoRes/`。

---

## 1. 先读懂 Spine 精髓（不然做出来是站桩）
实地扒 `client/Assets/Res/Spine/` 103 个骨骼 + prefab 的结论：

- **皮肤展示 = 纯 idle 循环，没有入场。** prefab 的 SkeletonGraphic `startingAnimation: idle/idle2` + `startingLoop: 1`（15/15 一致）。`in` 动画存在于骨骼数据但不是展示起始动画（它属战斗/获得等别处）。→ **视频只做 idle 循环，不做入场段。**
  - ⚠️ 教训：别看到二进制里有 `in` 就脑补"入场播一次"——**必须验播放端**（prefab startingAnimation），以实机为准。
- **idle 是多层二级运动**：rig 切成 20-34 个部件独立绑骨（发片/双节臂/袖/裙摆/眼/胯…），各自不同周期飘摆 → 站姿也"活"。这是视频要复现的"灵魂"，不是整体平移。

---

## 2. 演出脚本：站在角色视角，钩眼为王
做之前先问三句（以足球宝贝为例）：
- **给谁看**：纠结冲不冲榜的付费玩家 + 已拥有反复欣赏的鲸鱼。**视频=转化面/炫耀面，不是壁纸。**
- **什么心态**：我是这届世界杯的奖赏，我知道你在看我、且享受——自信带撩，"你想要我？去赢我。"
- **怎么钩眼**：①眼神(目光扫镜头+了然微笑，最狠) ②招牌 beat 只挑一个做透 ③身段曲线在余光持续撩。

**★ 关键尺度（用户定调）：别动太多，动大循环就假。**
- 必须有：**胸随呼吸微微起伏**（这类皮肤核心卖点，克制不浮夸）。
- beat：**wink 就够**，不要转球/抛接/撩发/大幅身段（全是循环杀手）。
- 道具（足球）完全静止。
- 节奏：基准帧 → 吸气峰值(胸微起/肩微抬) → 中段一次 wink → 呼气回落 → **精确回到基准帧**。有一拍高潮其余松弛，匀速=催眠。

---

## 3. 三件事各自怎么落

### 3a. 动起来 —— generate_video
模型对比（可选 seadance/veo3/sora/vidu/kling/grok/happyhorse…）：

| 模型 | 评价 |
|---|---|
| **kling** ✅ 首选 | 唯一成熟支持**首尾帧 fflf**(无缝循环命门)；角色首帧驱动稳；不强塞音频。最短 5s |
| vidu | fflf 能更短(1-16s)，默认带音频。需 ≤3s 时备选 |
| seadance | 最全能但默认强出音频(UI用不上) |
| happyhorse | 强制音频不可关，排除 |
| veo3 / sora | 渲染慢(>10min占比高)、过杀 |

### 3b. 循环 —— ★首尾帧同图杀招
kling `ref_types="首帧图像,尾帧图像"` + **同一张主稿传两次** → 首尾画面强制一致 → 无缝。
实测 v1 首尾帧像素差仅 **0.64**（肉眼零接缝）。
验法：cv2 抽首帧/尾帧算平均像素差，`<3` 很好、`<8` 可接受。

### 3c. 透明 —— SBS 链路
- **目标格式**：SBS 透明视频（左半彩色 + 右半 alpha 烧成的白模on黑底）。mp4 存不了原生 alpha，SBS 是 Unity 标准 trick，shader 从右半重建。
- **格式锚**：`VideoRes/AllianceCard_icon_1_a.mp4`（左绿蛇+右白蛇剪影）。
- 链路：
  ```
  generate_video(kling fflf, 不透明)
    → video_remove_background  (AI逐帧抠像得alpha)
    → export_sbs_video(quality高) (打包成左彩右白模SBS)
    → 验收: 对比AllianceCard那张, 看右半白模边缘(尤其银白发丝)干不干净/无逐帧闪烁
  ```
- 抠像最大敌人=杂背景/撞色。主稿**纯白底+边缘干净**已规避大半。唯一风险：**银白发丝 vs 白底低对比**→可能吃边。
- 保险：真吃边则重生成时背景换**纯绿/品红**(远离银白)再抠。

---

## 4. Prompt 库（定稿用中文对措辞 → 提交转等价英文，英文对动作约束/seamless 服从更稳）

**当前最优·英文（v1 实跑）**
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

**可调旋钮（每轮只改一处）**
- 呼吸/胸幅度：`subtle, alluring` ↔ 更明显 / 更收敛
- wink：可加"右眼、循环中段触发"
- 粒子/扫光：白底上看不太出且给抠像添边缘噪点 → **可删，等 UI 层另加特效**
- 裙摆：`almost still` ↔ 放开更飘

---

## 5. 工具坑
- generate_video 是 long_running：`--submit-only` 拿 task_id → `--check-task` 轮询，**别 --sync**。video 可能 5-12min。
- 脚本开头 `sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')` 防 GBK 崩。
- result 可能嵌套 list，递归 flat；下载带 cookie header。
- `aspect_ratio` 传 `"auto"`。
- 生产脚本范本：`产出-本地化与美术/X3/足球宝贝爱莉希雅/视频/gen_skin_video.py`。

---

## 6. 迭代日志（命中要点后固化为「一步到位」模板）
| 版本 | 模型/参数 | prompt 要点 | 客观结果 | 判词/教训 |
|---|---|---|---|---|
| v1 | kling fflf 5s 首=尾=主稿 | 极简(胸subtle+wink+粒子) | 无缝✅0.64/121帧24fps/1244×1660/白底✅ | — |
| v2 | 同上, 胸升主角/加腿/删粒子/wink降级 | 压制词偏多 | 无缝✅0.62 但**帧间运动暴跌0.13**(参考0.4-0.9) | 太木。**minimal/never/almost still 压制词叠加会把动作压死** |
| v3 | 整体联动重写, 胸夸张化 | 一条重心线 | 无缝0.64/运动0.27(回升仍偏低) | 氪佬鉴定:色4/吸引3/购买欲2,"像证件照、人是死的" |
| v4 | 高冷冷扫版 | 冷热反差+冷扫镜头+慢 | 等判 | — |

### ★硬教训
1. **糖人病**：动作写成清单(胸一条/腿一条/发一条)→模型各部位独立动、头卡死→"纯糖人没欲望"。**修法=写成"一条贯穿全身的重心线"**(重心→胯→腰→胸→肩→头→眼神)，强调"绝不各动各的"，**头/眼神必须解锁**。
2. **运动幅度带 0.4-0.9**(实机Spine录屏实测)；压制词(minimal/never/almost still)叠加会压死动作，克制用。
3. **★撩不撩的根在起点图**：fflf 锁主稿→主稿端正立绘则视频再调也端正、撩不起来。撩人主稿(有张力姿态+眼神)是地基。要治本动起点(A重出撩人主稿当首帧 / B松开fflf锁)。
4. **★眼神给不给镜头=死活线**：不给=证件照/糖人；给(暖撩 or 冷扫都行)=活。
5. **★情绪要细颗粒可导演**：别用"性感/高冷"糙词，拆成眼睑/嘴角/节奏/重心的具体微行为。例:高冷=冷热反差(身热脸冷)+冷扫镜头三段(斜侧懒飘→慢横扫睥睨不笑→懒飘开)+慢+下巴微抬做静态基线(非动作,否则破循环)。
6. **★高冷反差≠谄媚直球**，是更高级的氪佬撩点(买高傲女神的征服欲)；但**高冷≠呆**(高冷=慵懒冷扫有体态/呆=躲闪空眼神立正)。
7. **氪佬视角验收**(色不色/吸引力/购买欲)比技术指标更接近真实成败——可派 sub-agent 扮氪佬只问这三问。
8. **用户定调：纯prompt死磕出一个好的就通吃，不走动作迁移捷径**。

> 每出一版追一行；措辞稳定命中后把定稿提炼成"一步到位模板"贴 §4 顶部。参考素材库：`产出-本地化与美术/X3/皮肤视频_参考/`(文件名=用户点评)。
