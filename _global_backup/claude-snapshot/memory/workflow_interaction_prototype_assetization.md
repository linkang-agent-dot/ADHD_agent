---
name: "8-9"
description: 让交互原型用真游戏素材而非emoji/CSS糊，做到≈上线8-9成；做X3交互原型/提保真度时用
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e64e6447-8b1d-4f10-9e1a-491ee73228ca
---

让交互原型（活原型+实时说明一体 HTML）≈ 真游戏 **8-9 成**，使 design-merit「表现」支能对真图评、phase3 mockup 少返工。权威工作流文档：`C:\ADHD_agent\KB\方法论\交互原型素材化_工作流.md`（含可复用对照表）。

**★★★最硬教训：自洽>真**：整体硬塞一堆不对应/不同源的真素材(比例光照不统一)=collage感,比干净自洽的占位(emoji/CSS)还差。**第一版(自洽占位)往往就是交互原型该有的样子**(讲清交互,不当美术成品;真实视觉交给②效果图)。**往真走唯一正确姿势=组件级逐个换+精确对应(这玩法确切该用的那张资产,非手边近似)+每换验自洽(比例/光照/风格)+自洽为闸(不搭就先处理或保留占位)+拿②效果图当每组件对照标尺**。别做:一把梭整屏换真素材活DOM(变collage)/效果图当交互底叠浮层(对不齐)——2026-06-05均实测翻车。

**★★交互原型正解(2026-06-05实测纠错)**：①线框→②效果图(AI整体渲染,做"目标图/参照")→③交互原型→④拆分。
⚠️**"效果图当底+叠活件"是错的(实测比CSS还差)**：整张烤好的图把玩法元素冻死,浮层坐标只能瞎猜对不齐=好看图+乱飘鬼火。
**③正解=活DOM+真单体素材PNG,位置代码构造摆放→天生对齐**(格子=真海岛PNG/罗盘/角色/宝箱全活DOM,角色走到的就是摆放点,零猜);三轴(交互/布局/素材)全活,无一块烤死照片。范例`大富翁_..._真菱形版.html`。**②效果图真正用途**:design-merit表现支的视觉目标/参照 + 只取纯背景层(海水珊瑚不含玩法元素)当静态底。元教训:没实测的"看起来对"别当定论写死(我连两轮把"效果图当底"当正解被推翻)。
（注:②效果图整体渲染仍是出"静态目标图/参照"的好办法,只是不能当交互原型的底）。②做法=Morphix线框转效果图/主题转换prompt×真游戏截图参照,过GRFal generate_image;实证深海大富翁1张渲到~9成(`KB\产出-交互原型\X3_2026深海节\03_效果图\board_mockup_v1.png`)。gdesign本就编排此步(02_structure→03_mockups→04_split)别跳。**GRFal坑**:generate_image不自动async→`--submit-only`+`--check-task`轮询(约300-500s)+`curl -H "Cookie:$GRFAL_COOKIE" https://grfal.tap4fun.com<相对路径>`下载;params用C:\绝对路径。

**★保真=三轴，别把换皮当保真（关键认知）**：①交互/逻辑(状态机动线)②布局/构成="质"(元素真实位置/比例/路径形状/层叠)③素材/皮(emoji vs 真PNG)。**最易犯错=只升轴③="换皮不换质"**——在简化线框骨架贴真图，布局还是简化的(如环形赛道拍成4列网格)，出来只是"漂亮线框"。真保真必须先换轴②：**拿真游戏截图/prefab 当参照重建布局**，再填素材。动手前先问"有没有真截图"→去 KB `复用参考图\` 找。实例：大富翁原型 4列网格→对照真截图重建成"中央罗盘+外圈环形赛道"(`pos%N`循环逻辑天然适配环形，零改)=`大富翁_..._真布局版.html`。

**病根**：交互原型默认 emoji+CSS 糊视觉 + **布局线框级简化(网格 vs 真实环道)** = 代码味，保真 2-3 成。

**三步法**：
1. **真素材优先**：6034 库(`C:\x3-project\client\Assets\Res\UI\Spirits`)里有的件一律引真 PNG，禁 CSS 模拟核心控件(button/frame/地块/角色/宝箱/关闭)。
2. **缺的生成**：库内没有的用 Morphix prompt × gdesign token 按 X3 风格生成 → 丢本地 `_assets/`。
3. **KB 自包含**：素材拷进原型同目录 `_assets/`(从 C:\x3-project 拷)、tokens 内联；零 `.designdeck`、零绝对路径，可独立打开。

**找素材姿态**：大富翁/航海→`ActvVoyage/`(地块island_1~4/棋盘Monopoly_bg/罗盘compass/导航btn全在这)；节日角色/box/bg→`ActivityImg_Download/`(mermaid/siren)；通用控件→`Common`/`CommonNew`/`MechaMain`；道具→`ItemIcons`。

**落地范例(2026-06-05)**：`KB\产出-交互原型\X3_2026深海节\大富翁_珍珠贝进度系统_交互原型_保真版.html`——JS走路逻辑不改只换视觉层；棋盘/海岛地块/海妖角色/深海宝箱/关闭/掷骰键全真图；珍珠贝🦪+骰子🎲库内未出、标记走生成补齐。

**接 design-merit**：保真原型=「表现」支的可查实物，渲出来vs真截图比"像不像8成"。相关 [[workflow_design_merit_critique]] [[reference_gdesign_designdeck]] [[reference_morphix_reskin_prompts]] [[reference_x3_voyage_art_chain]]。
