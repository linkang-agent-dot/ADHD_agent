# 荣耀之路头像框（=每队四强专属框）— 国家特色美需 prompt（草稿·待打样验证）

> **正名（用户 2026-07-07 拍板）**：这套「每支进 8 强队一个」的框，游戏内正式名 = **荣耀之路头像框**。**不是**通用里程碑款（晋级之路框 80348 / 世界之巅框 80349 是另一档，全员共用、不分国家）。荣耀之路 = 按队做、带国家特色，文件仍 `WC_SF_Frame_{码}.png`。

> 状态：🟡 **草稿·待用户挑 1 国打样验证方向**。方向获认可后升进 `KB\产出-数值设计\X3_世界杯\_世界杯_决策记录_按模块.md`。
> 背景：当初 4 个框（FRA/MAR/NOR/ENG）走 x3-media/media-worker 直接生成，**没留 prompt**（接手白手起家坑）。本文件补这个空缺。
> 用户口径（2026-07-07）：**不要公式化套色**，每个框从骨子里长出该国特色——国家元素要"长"成框的结构本身，不是把国旗贴在通用环上。
> 命名：`WC_SF_Frame_{FIFA码}.png`。**产出目录 = `半决赛决赛外显\荣耀之路头像框_国家特色版\`**（国家特色版单独放·跟父目录旧公式版分开·2026-07-07 用户要求）。管线：x3-media uiframe 类型 · gemini · media-worker 异步。参考锚：`flags_48/{code}.png`（真旗配色）+ 既有 FRA 框（格式/四强金标/圆规格锚·**别挂旧 `头像框_48_FINAL` 会拉回公式化**）。
> **打样已验证（MAR·2026-07-07）**：泽利吉马赛克方向获认可·透明过闸门。批量前 prompt 再收两处瑕疵——① 禁环身嵌小人踢球剪影（`no tiny footballer pictogram silhouettes on the ring`）② 禁类阿拉伯花体涂鸦（`no faux-Arabic scribbles or calligraphy, absolutely no text`）。

## 🔴 反模板铁律（2026-07-07 用户点透·批量前必读）
- **不要给所有国家套同一种异形模子**（无论是"国旗足球球+金翅+宝石"还是"统一圆环换色换纹"）——一国国套同一形 = 还是模板 = 没意思。这是用户否掉的核心。
- **每个国家的"破形/异形"必须从它自己的文化长出来**，8 个框 = 8 种不同轮廓，谁也不像谁：MAR=马蹄拱/muqarnas 建筑破形 / FRA=Art Nouveau 铁艺曲线扭出轮廓 / NOR=龙首船头+绳结探出 / ENG=纹章盾+皇冠顶冠 / ESP=摩尔拱+弗拉门戈裙摆弧动 / BEL=霍塔鞭线铁艺不对称甩摆 / (M7/M8 同理各自文化)。
- **国旗试点**（`头像框_国旗化试点/` `头像框_国旗球_试点/` `头像框_国旗球_环纹理试点/`）只当**"异形的度"参考**（优雅、秒读国家、不炸开轮廓），**不是**统一形来源。
- 破形度参照 MAR 定标：A『建筑破形』/B『飘带炸开』两版探边界·用户认可的度定为基准·各国按此度+各自文化破形。

## 统一骨架（8 个框只统一"骨"，皮和形各国定制）
**统一的只有骨**：能套进头像位的框 + 顶部金色「四强」等级标（月桂+足球）+ 半写实厚涂 + PNG 透明底 + 中间留空透明。**皮（纹样）和形（轮廓/异形）都各国定制**，见上「反模板铁律」。

## 6 支已定队（M1-M6 胜者）

### 🇫🇷 法国 FRA — 新艺术运动铸铁优雅
埃菲尔/巴黎地铁口 Art Nouveau 锻铁曲线当框身 + 鸢尾花节点 + 顶部高卢雄鸡冠饰 + 蓝白红珐琅嵌线
`Circular game avatar frame, the ring itself built from elegant Art Nouveau wrought-iron scrollwork (Eiffel/Guimard metro style), fleur-de-lis ornaments as nodes, a proud Gallic rooster crest at the top, blue-white-red enamel inlays, gold Final-Four laurel-and-football tier badge, semi-realistic thick paint, transparent center for portrait, PNG transparent background, symmetrical`

### 🇲🇦 摩洛哥 MAR — 泽利吉马赛克 + 马蹄拱
Zellige 几何马赛克镶框身 + 八角星交错 + 顶部马蹄拱托绿色五角星 + 雕花雪松木质感
`Circular game avatar frame, the ring composed of intricate Moroccan zellige geometric mosaic tessellation (interlocking 8-point stars) in red/green/gold, a horseshoe-arch cartouche at the top holding the green pentagram star, carved cedar-wood texture, gold Final-Four laurel tier badge, semi-realistic thick paint, transparent center, PNG transparent background, symmetrical`

### 🇳🇴 挪威 NOR — 维京绳结 + 极光
乌尔内斯风格维京兽形绳结当框身、锡银质 + Rosemaling 花卉卷草 + 顶部双龙首船头(drakkar)相接 + 背后淡极光 + 内圈卢恩符文
`Circular game avatar frame, the ring formed from interlaced Viking Urnes-style beast knotwork in pewter-silver, flowing Norwegian rosemaling floral scrollwork along it, two carved dragon-prow (drakkar) heads meeting at the top, faint aurora borealis glow behind, runic engraving on the inner rim, gold Final-Four laurel tier badge, semi-realistic thick paint, transparent center, PNG transparent background, symmetrical`

### 🏴 英格兰 ENG — 三狮纹章
中世纪金色纹章框 + 三狮绕框行进 + 都铎玫瑰节点 + 顶部圣乔治十字盾徽 + 皇冠
`Circular game avatar frame, medieval heraldic gold ring with three lions passant guardant marching around it, Tudor rose nodes, a St George's Cross shield crest with a royal crown at the top, embossed gold-and-crimson enamel, gold Final-Four laurel tier badge, semi-realistic thick paint, transparent center, PNG transparent background, symmetrical`

### 🇪🇸 西班牙 ESP — 阿尔罕布拉金饰 + 弗拉门戈
安达卢西亚/阿尔罕布拉金色阿拉伯藤蔓框身 + 一侧弗拉门戈荷叶褶裙卷起 + 两侧海格力斯之柱 + 红色康乃馨 + 冠饰隐公牛角剪影
`Circular game avatar frame, ornate Andalusian Alhambra gold arabesque ring, a flamenco ruffle flourish sweeping up one side, Pillars of Hercules flanking the sides, a red carnation, a subtle bull-horn silhouette in the top crest, red-and-gold palette, gold Final-Four laurel tier badge, semi-realistic thick paint, transparent center, PNG transparent background, symmetrical`

### 🇧🇪 比利时 BEL — 霍塔新艺术 + 红魔
Victor Horta 鞭线式金色锻铁框身、黑金红 + 顶部红魔犄角冠饰 + 布鲁塞尔大广场哥特行会金箔纹理
`Circular game avatar frame, Belgian Art Nouveau (Victor Horta) golden whiplash ironwork ring in black-gold-red, a Red Devil horned crest at the top, Grand Place gothic guild-hall gold-leaf filigree texture, gold Final-Four laurel tier badge, semi-realistic thick paint, transparent center, PNG transparent background, symmetrical`

## ⏳ 待今晚 M7/M8 打完补（方向备忘）
- M7 胜者：**阿根廷 ARG**（潘帕斯太阳+马黛/太阳五月纹）或 **埃及 EGY**（法老金饰+象形文字纹+圣甲虫）
- M8 胜者：**瑞士 SUI**（白十字+阿尔卑斯几何雪晶）或 **哥伦比亚 COL**（金黄+El Dorado 金饰+咖啡花/兰花）

## 🔴🔴 反模板纠错（2026-07-07 晚·用户验批量后否掉·血泪教训·接管最优先读）
- **翻车**：把 10 框全锚定 MAR-A 的格式（圆环+拱顶窗+两侧托臂+底部奖杯盾）→ 纹样各国不同，但**骨架/构图全一样 = 换皮式模板**，用户一眼识破"都有明显模板化特征"。**只有 ESP v2 巴洛克获认可**——因为它跑脱了这副骨架（涡卷框+皇冠+牛角外张+扇子，是另一种构图/剪影）。
- **★核心规律（换皮/成套设计通用）**：**元素(纹样/符号) vs 构图(骨架/剪影) 要分开**。元素按国换=对的；但**若所有件共用同一构图骨架，换再多元素还是模板**。反模板 = **每件给一套自己的构图/剪影原型**（圆环 / 非对称藤蔓 / 盾牌徽章 / 建筑立面 / 巴洛克涡卷…各不同），不是同一个框换花。用户"挪威二元素很不错"=元素对、构图错，佐证此拆分。
- **★锚定的坑**：拿某一件当"格式锚"批量 = 主动制造模板。批量只共享**抽象约束**（是头像框+有透明窗+四强等级感+半写实厚涂），**不共享具体构图**。各国构图各写各的。
- **🔴🔴 中心圆窗尺寸铁律（2026-07-07 用户拍板·量老批定标）**：游戏头像圆形固定槽→**每框中心必须是正圆透明窗**·参数锁：**中心(50%,48%)（横居中·纵略偏上48%）· 直径≈65%框宽（半径≈32.5%·2048图≈半径666px·容差直径62-68%）**。老批48队框(`头像框_48_FINAL`)标准是直径74%/半径37.4%·中心(49.8%,48%)；SF框取65%(比老批略收·给华丽外围留环带空间·用户拍的)。**反模板只改外围装饰(教堂/藤蔓/盾牌…各国不同)·圆窗尺寸/位置全框统一不变**。
  - **🔴 gemini 缩小圆窗极狠(实测)**：不指定=画到46%·**prompt 说 55% 只画到 29.5%**(NOR r2c 实测)→要 65% 得 prompt **要到 ~80%**("HUGE PERFECT CIRCLE ~80% of frame width, filling MOST of the frame, leaving only a thick border, NO doors NO arch NO oval")。出图后用 `_量圆窗.py`(已固化 KB)量·落在 62-68% 才收·超范围重出(可能要再往上顶到 85%)。
  - 踩坑=NOR 木教堂第一版把中心做成半闭木门/尖拱→透明口只剩163px窄缝头像塞不进。
- **🔴 二次校准(2026-07-07·别再矫枉过正)：反模板 ≠ 松散/不对称/丢框体**。**框体必须结实、像个正经框**（参认可的 MAR-A 建筑框 / ESP v2 巴洛克涡卷框——都是实打实厚重的框）。变化来自**各国"框的风格/结构"不同**（摩尔拱 / 洛可可鎏金框 / 教堂立面 / 纹章盾 / 巴洛克涡卷 / 新艺术铁框…），**不是把框溶成松散藤蔓**。**FRA Mucha 藤蔓版=丢了框体·丑·已毙**。即两个极端都错：①同一骨架换纹样=模板 ②溶成松散有机装饰=没框体丑。**取中=结实框体 + 各国不同的框风格**。
- **修法(进行中·2026-07-07晚·当前候选=校准后重批·待用户终选)**：六国当前候选框(都在国家特色版目录·`_预览_*_游戏内感.png`看效果)：
  - FRA=`WC_SF_Frame_FRA_r3_洛可可.png`(结实鎏金框·雄鸡+鸢尾+三色·圆窗58%)✓
  - NOR=`WC_SF_Frame_NOR_r2c_木教堂圆窗.png`(木教堂立面·留v2元素·圆窗**仅29%太小·待放大**)
  - MAR=`WC_SF_Frame_MAR_r2_圆窗.png`(zellige建筑框·圆窗54%)✓
  - ENG=`WC_SF_Frame_ENG_r2_纹章.png`(三狮+皇冠+圣乔治盾·圆窗54%)✓
  - BEL=`WC_SF_Frame_BEL_r2_铁框.png`(霍塔铁框+红魔·圆窗63%最佳)✓
  - ESP=`WC_SF_Frame_ESP_v2_巴洛克.png`(皇冠+牛角+扇子·**透明坏了8%棋盘格·待补修removebg**)
  - **✅ 用户终选(2026-07-07晚)**：**FRA洛可可 / MAR zellige / ENG纹章 / BEL铁框 = 认可定稿**(其他没问题)。**NOR** 教堂太高瘦→改**圆形维京框**(整框圆·维京圆盾/绳结+龙首+符文+极光·`WC_SF_Frame_NOR_r3_圆形维京.png`·大圆窗80%)。**ESP** v2 透明坏→**v3 重出**(同巴洛克设计:皇冠+牛角+扇子+康乃馨·纯绿幕务必抠净·`WC_SF_Frame_ESP_v3_巴洛克.png`)。两张已派(NOR=…713f / ESP=…8d5a)。
  - **待收尾**：NOR/ESP 两张出来验合格后→六国齐→标 FINAL(建 `_目录说明` 或决策记录·五定稿+NOR r3+ESP v3)→窗口尺寸目前 54-63% 用户认可(不强求统一到65)→M7/M8 明晚定队补最后 2 国(同"结实框体+各国风格+大圆窗80%"配方)。旧首批 10 框全废(仅留思路)。

## ⚠️ 旧「赢家配方」已被上条否掉（保留仅作反面参考·别再照做）
> 下面这套"锚定 MAR-A 格式"就是制造模板的元凶，**接管勿用**，看上面反模板纠错。

### ✅ 验证结论 + 赢家配方（2026-07-07·MAR/FRA 已验·接管直接照做）
- **MAR 定案 = 建筑破形 A 版**（`WC_SF_Frame_MAR_vA_建筑破形.png`）。B 飘带炸开=毙（盖进头像窗、抢戏）；v1 规整圆环=弃（破形不够）。
- **★赢家配方（每国照此，只换文化）**：① 富纹样环身（该国标志纹样：MAR=zellige/FRA=Art Nouveau 铁艺/各国见反模板铁律表）② **顶部国家符号冠顶破圆轮廓**（星/雄鸡/龙首/皇冠…）③ 两侧建筑托臂/壁龛/灯笼外探 ④ 底部**金色四强等级盾（月桂+奖杯）** ⑤ 拱顶透明头像窗。半写实厚涂+金。**破形度=MAR-A 那种"破得有型但头像窗干净"**，别学 B 炸开。
- **批量落地(2026-07-07 已派 10 框)**：5 国×2 版走 `_批量框task生成器.py`（改 JOBS 换国家重跑·M7/M8 定队后同法补 2 国×2）→ 派 media-worker → gemini。锚=MAR-A 框(丰富度/金标/拱窗格式)+`flags_48/{code}.png`(配色)。产物=本目录 `WC_SF_Frame_{code}_v1/v2_*.png`。
- **★预览工具 `_头像预览合成.py`**（通用·任意框复用）：`python _头像预览合成.py <框png> [英雄立绘png]` → 出透明版+深色UI底"游戏内感"版。默认英雄=足球宝贝爱莉希雅FINAL。**两个坑(已修进工具)**：① 头像蒙版必须用**框自身真实透明窗口形状**(BFS flood fill)·别人工画圆(对不进拱窗露缝) ② 头像缩放用 **cover 铺满窗口**(max(hw/cw,hh/ch))·否则白底立绘露方形硬边。换英雄需重标 `CROP_BOX`+`FACE_FRAC`。

## 待办(图齐后)
- 用户按国家 v1/v2 并排选 FINAL → 标 FINAL/废弃(本目录) → 升 `_世界杯_决策记录_按模块.md`。
- 落地：建 Item/Frame 行 + DK 注册（X3 dev DK 注册即用不过包·见世界之巅铭牌段）。
