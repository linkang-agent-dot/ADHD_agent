---
name: ""
description: 本会话新增的、需要透明背景的图片资源，入库前必须用差分法确认是真透明不是假透明
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0a30c6e6-6e39-49a1-a271-b75401d58a68
---

我(Claude)本次会话**新增的、需要透明背景**的图片资源，入库/交付前**必须验证是真透明**，不能只看着像透明就过。

**Why:** GPT/生图模型常返回"假透明"——把棋盘格直接画成灰白像素(mode=RGB 24bpp 无 alpha 通道)，肉眼看着像透明，进游戏是死白底。2026-06 拓荒节主城皮肤图标 GPT 直出就是假透明(Format24bppRgb)，靠 remove_background 抠成真 RGBA 才可用。

**How to apply:**
- ★**做透明化的标准手段 = GRFal 抠图 `remove_background`（2026-06-17 用户强调:图标做完必须过这道）**：生图模型/worker 直出的图标常带白底或假透明(RGB无alpha),**交付前必须用 GRFal `remove_background` 抠成真 RGBA**,不是"看着透明就过"。⚠️参数坑(coin/兑换商店 icon 实证):`remove_background` 要 `--file image_paths=<图>`(不是 `image=`),错 key 会**静默失败、只在 check-task 才看到报错**。抠完再走下面差分法验真。**例外**:活动**背景图(bg,如 WC_Exchange_Bg 540×500 满幅)本就不透明,不抠**;只有"图标/物件"(HUD icon/道具icon/箱子等自由形状)需透明。
- 验证手段=**差分法**：把图分别 alpha_composite 到纯白底和纯黑底→转RGB→ImageChops.difference。
  - 有透明区域 → 两张底色不同 → diff 有非零值(bbox 非空/extrema>0)
  - 完全不透明(假透明) → 两张一样 → diff 全 0(bbox=None)
- 同时直接读 alpha 通道：四角应为 (_,_,_,0)，统计 alpha=0/255/中间占比，确认 mode=RGBA。
- PIL 脚本从干净 cwd 跑(别在 %TEMP%，那有 copy.py 会 shadow stdlib 导致 PIL 导入崩)。
- 美术自己交付的资源不在此列(默认美术保证)；这是针对**我生成/处理**的资源的自检。

关联 [[X2 主城皮肤换皮完整链路]] [[feedback_proactive_knowledge_update]]

## 反向坑(2026-06-25):好抠图被误判成"50%半透明鬼影"——别用 α==255 判实心率
GRFal `remove_background` 抠出的主体 alpha **常是 240-254（视觉全实心但≠255）**,不是精确255。若用 `α==255` 统计"实心率"会发现只有~4%、半透明~50% → 误判成"主体被抠成半透明鬼影"。**正确判据=分桶**:`α=0`(全透明背景)/`1-127`(真半透·鬼影信号)/`128-239`(中段)/`240-255`(近实心=视觉不透)。好抠图特征=大片α=0 + 大片α≥240 + 仅个位数% 的1-127(植被/珊瑚等细边抗锯齿)。**实心率按 `α≥240` 算,不是 `==255`**(2026-06-25 拜访礼包pack图实证:45%全透明+51.6%实心(≥240)+1.8%真半透=干净真透明,但==255只3.9%差点误杀)。

## 反向坑(2026-06-11):真透明被看成假透明
Read/预览工具渲染 RGBA 时可能**不合成 alpha**——透明区显示 RGB 通道残留色(如去底后残留#B8B8B8灰),看起来像没去底。**判定只信数据不信肉眼**:①alpha统计(np: alpha=0占比+四角采样) ②预览先 alpha_composite 到白底再看。世界杯抽奖券icon案例:alpha=0占54%四角全透明=真透明,但Read直接看是整片灰底。
