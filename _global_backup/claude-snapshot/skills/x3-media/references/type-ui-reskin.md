# 改造现有界面效果图（ui_reskin）完整流程 — 真组件拼装 → AI reskin 五步法

给「某个**已上线界面**加/改元素」（如战令加第 3 档、养成手册加双档、商店加页签）出**落地效果图**。
**首选链路**，胜过两种常见错法：

| 错法 | 病症 |
|---|---|
| 纯 AI 整张生成 | 布局飘离真实界面（格阵自重排/主视觉乱画/真实细节丢），程序没法照着实现 = 废图 |
| 纯 CSS / 真素材拼装 | 位置全对但接缝/光影不统一、糙，不能当成品 |
| **✅ 真组件拼装 → AI reskin** | 拼装锁"位置全对"，reskin 换"成品观感统一" |

**核心洞察**：真素材拼装截图 = 远胜线框的「图#1 结构稿」。线框要 AI 猜内容/比例；真组件实摆的拼装，位置/文字/比例全确定，AI 只需换一层皮。

## 何时匹配
用户说：改造界面/在现有界面加东西/给XX活动出效果图/界面加档位·加页签·加格子/UI 换皮出整张效果图/reskin 一个界面/把竞品界面改成我们风格。
> 区别于 `ui_extract`（从图里**拆**元素）——本类型是**出整张改造后的界面效果图**。拆元素仍走 `ui_extract`。

> ⚠️ **别把五步法用错场景**：五步法是「加控件 / 换整套 design system」，STEP 4 会把图#1 视觉**全 ERASE**。
> 若需求是「**保住整屏原样，只给某一个展示位/单个奖励重新包装**」（如：中间大奖太单薄、道具像贴图没融进界面），
> **别套五步法**——直接走 `type=general` 的 **gpt 图生图（img2img）定点修图**：把原截图当唯一 reference，prompt 里
> "KEEP the ENTIRE screenshot exactly as-is，只改中间那块"。五步法会把你想保的整屏一起 ERASE 掉，正好背离目标。
> **实证根因（砰然心动酒馆活动案 2026-07-01）**：用户反复说"中间不自然"，落点=**道具是一张平贴在背景上的抠图、数量硬糊在图案上**，
> 读起来像"占位素材+提额数字"。修法 = 给它一个**展示台/框容器**，让道具 **seated 进去 + 接触阴影**，数量牌从道具身上拿下来**挂到框右下角**；
> 一句话「不是加光/加特效，是给贴图盖个家让它住进去」。**注意题眼**：若原框自带主题语义（心形框呼应"砰然心动"），换成通用金框会丢主题，要么把容器做成主题形状（心形展示框），要么先跟用户确认题眼让不让位。

---

## 五步流程

### STEP 1 · 拆真组件（从 prefab 反查真实 sprite，零 AI）
不要让 AI 画图标/按钮/边框——游戏里全有现成的。
1. 抽 GUID：`grep -oE "m_Sprite: \{fileID: [0-9]+, guid: [a-f0-9]{32}" <prefab> | grep -oE "[a-f0-9]{32}" | sort -u`
2. GUID→PNG：`os.walk` 扫 `Assets/` 下 .meta 头部 `guid:\s*([a-f0-9]{32})`，命中即 `路径[:-5]`
3. 真实 PNG 拷进原型 `_assets/`
> 找件线索：sprite 名常带活动语义（养成手册=`*_nourish*`）；同前缀邻近放（`Activity/` 下 nourish/_1/_2/_3=主视觉/锁格/解锁格/大面板）。原界面没有的新控件→复用同风格真实件（金按钮 `img_cm_anniu1_gold`）或去带该控件的 prefab 抠。详见 `KB\方法论\活动程序开发\X3客户端GUI知识.md` §2。

### STEP 2 · CSS 拼装定精确布局（= 图#1 结构稿）
HTML 用真组件按真实坐标拼出布局，新控件也摆到位。chrome headless 截图 = 图#1。
```bash
chrome --headless --disable-gpu --screenshot="<绝对路径>.png" --window-size=W,H --hide-scrollbars "file:///<URL编码路径>"
```
**⚠️ 布局对就行，别追求好看**（见下方血泪教训）。可顺带加交互（购买/互斥/领取）做活原型供"定交互"。
> ⚠️ chrome 渲染中文路径 file:// 会 ERR_FILE_NOT_FOUND → 拷 html+_assets 到纯 ASCII 临时目录再渲染。

### STEP 3 ·（选）出适配新控件的底图
原界面没地方放新控件时，以老底图 img2img 加槽位。活 DOM 叠"烤死的槽"会对不齐 → PIL 竖扫测槽真实像素坐标再贴（GUI 知识 §3）。多数情况跳过。

### STEP 4 · ★AI reskin 合成成品（关键步，走本 skill 派发）
两图喂 `generate_image`：
- **图#1 = 拼装截图** → 只取布局/文字/控件位置/图标语义，**视觉全 ERASE**
- **图#2 = 真实游戏界面截图** → design system 整套抄（背景/面板/边框/按钮/格子/配色/字体）

参数：`model=gemini`（保布局；要更强风格保真可加跑 gpt 一版对比），`aspect_ratio=9:16`，两个 `reference_images`。
> 图#2 去 `C:\Users\linkang\Pictures\X3验收\` 验收截图库找，**挑与目标界面框架最接近的一张**。

**buildReskinPrompt 骨架**（复用，改 LAYOUT 段）：
```
You are a game-UI RESKIN engine. Two reference images are given.
IMAGE #1 = LAYOUT/CONTENT reference ONLY. Take strictly its STRUCTURE: position & arrangement of every element,
all Chinese text labels, column/slot counts, icon placement, the progress rail.
EVERY visual aspect of image #1 (flat colors, rough edges, placeholder/collage look) MUST be ERASED. Only the WHAT and WHERE survive.
IMAGE #2 = DESIGN SYSTEM source (a real in-game screenshot). Copy its ENTIRE visual language:
board texture, golden slot frames, column-header labels, level nodes, gold buttons, discount badges, hero painting, backdrop, lighting, materials, ornate gold trim and fonts.
OUTPUT: ONE cohesive seamless GAME-QUALITY UI = image #1's layout fully re-rendered in image #2's style.
LAYOUT: <逐项把列数/槽位/文案/按钮/价格写死>. Keep ALL Chinese text verbatim.
STYLE: ornate golden mobile-game UI matching image #2. NO painterly or brush-stroke look, crisp clean UI. Vary gold ornamentation naturally; do not flatten.
```
**新元素显式声明**：图#1 有而图#2 没有的（切换栏/封顶宽格）→ prompt 明确"按图#2 视觉语言原生渲染"。
**X3 调优必加**：NO painterly/笔触；金饰列举多种别单点名；中文逐字保留；参考图能说明的别写进 prompt。
> 可复用脚本：`scripts/gen_ui_reskin_template.py`（submit-only + 轮询 + 双候选下载）。改 IMG1/IMG2/PROMPT 复跑。

### STEP 5 · S6 拆槽交付
成品认可后 → 四层拆解（F固定/T主题/B背景/TXT文本）+ 槽位规格表给美术/程序。已有真组件 PNG 的，拆槽=组织真组件清单+标"需新出"项，不必再 AI 切（拆元素走 `ui_extract`）。详见 `KB\方法论\X3_AI出图工作流…世界杯案.md` §9。

---

## ★血泪教训（最值钱，护航令 BP 案实证）
拼装（图#1）做到 STEP 2 就当成品交 → 被连判几版"烂完了/痛苦"。根因 = **漏了 STEP 4 reskin**。
**拼装看着糙（手拼/CSS 兜底木板/道具重复/接缝）完全没关系——它的视觉在 STEP 4 会被全 ERASE，只取布局。** 把结构锚当成品交=必烂。**别在 STEP 2 死磕拼装精度，赶紧进 STEP 4。** STEP 4 一跑即神：质量主力是图#2 的 design system，prompt 只需说清布局+新元素+保中文+禁 painterly。

---

## 变体 · 横竖转换（竞品参考方向不对时，reskin 前先转）
当图#1 来源是**竞品截图且方向不对**（竞品横屏 BP，我们要竖屏弹窗）：别直接 reskin（硬塞变形），两段式：
1. **第一段·横竖转换**（Morphix `buildFlipPrompt`）：reference=竞品截图，gemini，aspect=目标方向，**只翻布局不换风格**——关闭键/货币/标题按目标方向重排、网格列数 reflow（横 4-6 列→竖 2-3 列）、轴向翻转、保两选项并列、文字逐字留、禁"只拉宽不翻轴"。产出竖屏结构稿。
2. **第二段·X3 reskin**：竖屏结构稿当图#1，真实 X3 界面当图#2，走 STEP 4。可顺带套内容映射（竞品档位名→我方版本名）+删/改元素（删价格）+加新文案行。
> 坑：竞品奖励图标会残留→第二段 prompt 强调用图#2 格子风格，真道具配置时换；竞品业务文案（"达到45级返还"）改我方口径。`buildFlipPrompt` 全文见 `KB\方法论\Morphix换皮工具逆向_prompt库.html`（D 段）。

---

## 关键规则
1. **拼装别死磕精度**：STEP 2 布局对即可，观感交给 STEP 4。
2. **图#1 视觉全 ERASE**：reskin 的本质是"只取布局，换图#2 的皮"；图#2 当成品交=必烂。
3. **图#2 选最接近的真实界面**：去 `Pictures\X3验收\` 找框架最接近的一张当 design system 源。
4. **新元素显式声明**：图#1 有图#2 没有的控件，prompt 点名按图#2 风格原生渲染。
5. **X3 调优必加**：禁 painterly/笔触、金饰列举多种、中文逐字保留。
6. **中文路径坑**：chrome 渲染拼装 HTML 拷到纯 ASCII 临时目录。
7. **拆元素不归这**：要把界面拆成一件件素材→走 `ui_extract` / `ui_extract_fine`，不在本类型。

## Reference Images
- 图#1 = 真组件拼装截图（必须，本流程 STEP 1-2 产出）
- 图#2 = 真实游戏界面截图（必须，design system 源，`Pictures\X3验收\`）
- 横竖转换变体第一段：竞品截图（1 张）

## 文件命名
| 阶段 | 后缀/示例 |
|---|---|
| 真组件 | `_assets/<sprite名>.png` |
| 图#1 拼装 | `<主题>_拼装布局.png` / 原型 `<主题>_真素材拼装_v1.html` |
| reskin 成品 | `<主题>_效果图_AIreskin_v1_a.png`（多候选 _a/_b） |
| 横竖中间稿 | `<主题>_竖屏转换_stage1.png` |

> 权威方法论：`KB\方法论\X3_AI出图工作流…世界杯案.md` §12/§12b + `KB\方法论\活动程序开发\X3客户端GUI知识.md` §2/§3 + `KB\方法论\Morphix换皮工具逆向_prompt库.html`。实证产物：养成手册 / 护航令 BP / 世界杯竞猜界面。
