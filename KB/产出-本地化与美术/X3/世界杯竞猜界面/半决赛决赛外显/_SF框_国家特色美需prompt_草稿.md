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

## 下一步
用户挑 1 国先打样（推荐 FRA 或 MAR，特色最强、最能验证"国家化"方向）→ 味儿对了照此批量 → 升决策记录 + 建 Item/Frame 行 + DK 注册。
