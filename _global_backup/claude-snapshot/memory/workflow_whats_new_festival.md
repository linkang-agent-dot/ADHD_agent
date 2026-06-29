---
name: workflow-whats-new-festival
description: "用户喊\"what's new\"时的固定流程——写节日活动总览公告文+拷验收文件夹的装饰/主城资源图"
metadata: 
  node_type: memory
  type: project
  originSessionId: d6ba3279-22f0-4120-8797-0b98478ebab0
---

用户说 **"出/做 what's new"**（节日 What's New）时，默认两件事：① 写一份节日活动总览公告文（每个活动模块一段：主题渲染句+玩法说明），② 把该节日的美术资源图拷进验收文件夹。2026-06-09 X2 拓荒节落地，路径如下。

## ① 公告文（版式权威范本）
- **范本**：`C:\Users\linkang\Pictures\X3验收\夏日\WhatsNew_夏日恋语.txt`
- **结构**：装饰边框标题(中文节日名+EN) → 开场氛围 3 句 → 每模块一段「★ N、中文模块名 EN名 / 一句主题渲染 / 玩法说明 2 行」→ 结尾「活动期间」三条提示 + 收束句
- **模块名 & 玩法从哪来**：读验收文件夹 `C:\Users\linkang\Pictures\{项目}-{节日}验收\` 里的活动截图，**每张 png = 一个活动模块**，模块英文名直接用截图里的游戏内 in-game 名（如拓荒：7日=Pioneer 7-Day Event / 大富翁=Roaming Adventure / GACHA=Pioneer City / 挖矿=Pioneer Mine / 强消耗=Lucky Ball / 周卡=Festival Custom Weekly Card / 累充=Pioneer Grand Prize / 限时抢购=Limited-Time Flash Sale / 装饰=Pioneer Decor Deal）
- **输出位置**：存进同一个验收文件夹，命名 `WhatsNew_{节日}.txt`

## ② 美术资源拷进验收文件夹（建子文件夹 装饰资源\ + 主城资源\）
- **装饰资源**（室内家具）：源在 `C:\Users\linkang\Pictures\{节日}装饰资源\` 主目录的编号成品图(01_装饰柱…15_摆件)；只拷 `^\d` 开头的成品，跳过 `_AI测试`/`_占星对比` 中间件
- **主城皮肤资源**（走 DK，从客户端提，见 [[x2-city-skin]]）：客户端真实路径 **`D:\UGit\x2client\client`**（注意：`D:\x2client` 是空壳）。美术前缀 拓荒=`Pioneer`、占星=`Astrology`、夏日=`Xiarijie`。DK 对应的可视图：
  - DK 图标(Icon/IconBg/UIPrefab 三型都指它)：`Assets\x2\Res\UI\TextureNew\Decoration\{Theme}_icon_building.png` ← **最具代表性的主城皮肤图**
  - 大地图远景建筑贴图：`Assets\x2\Res\map\CityBuilding\X2_Map_{Theme}01\Tex\X2_Map_{Theme}01.png`
  - 主城详细建筑贴图(4级变体 D/N/L/Sand)：`Assets\x2\Res\Shop\Town\Building\X2_T_Shop\X2_T_Shop_{Theme}01\Tex\*.png/.tga`
  - ⚠️ 主城皮肤 3D 本体是 .prefab/.FBX 没单张预览图；.tga 贴图系统看图器不一定能预览，能直接看的只有 DK图标 png + 大地图建筑 png。特效族 `Fx_Shop_*`(前缀 `Xibu`)是 prefab 不是图，不拷。

## ③ 节日预告邮件（通知玩家活动即将上线，2026-06-11 拓荒节沉淀）
- **范本 = 占星节预告邮件**，固定骨架（别自由发挥）：
  ```
  亲爱的玩家：
  为了给大家带来更好的游戏体验，我们即将在<color=#ffa200>UTC时间{年月日}</color>上线{节日}活动。
  【{节日}活动上线内容】
  {一句渲染}！{活动一、二、三、四、五}五大新活动限时上线，还有其他活动等你来参加！
  {活动名}：{一行式描述，两三短句+感叹号}！   ← 共5条
  错过等一年，快来加入{节日}！
  感谢各位玩家的支持与反馈！我们会继续努力，带来更好的游戏体验。
  我们将继续修复游戏中的一些问题，同时给大家带来更多的新内容。敬请期待！
  Shop & Goblin 工作室
  ```
- 称呼=「亲爱的玩家」（不是指挥官）；日期用 UTC + `<color=#ffa200>` 高亮（占星原件没闭合 `</color>`，X3世界杯版已两端补全）。
- ⚠️**落款工作室署名按项目分**：X2=「Shop & Goblin 工作室」；**X3=「Tavern Legend」**（2026-06-24 世界杯用户确认）。范本是X2来的别照抄署名。
- X3 多语言导入模板=`C:\ADHD_agent\KB\产出-补发邮件\X3\_模板\邮件导入模板.csv`（转置：行=空/标题/内容/超链接文本/超链接地址，列=20语言 en/cn/zh/fr/de/ru/jp/kr/sp/id/th/ar/ro/nl/tr/po/it/vi/fa/pls；UTF-8 BOM）。世界杯成品+构建脚本 `_build_preview_mail_csv.py` 在 `Pictures\X3验收\世界杯\`。
- 只挑 **5 个主打活动**（占星挑了大富翁/抢购/通行证/劫匪/卡册；拓荒对位=大冒险/集卡/挖矿/转球/抢购），不全列。
- ⚠️ **每条活动描述严格取自 What's New 原文卖点，禁止自编**（被纠偏过：自己加了"节日限定装饰手到擒来"等不在 What's New 里的内容）。
- 定稿后翻多语言。⚠️ **iGame 多语言邮件导入格式是转置布局**（自创"一行一语言"会报「导入数据有误」）：行1=20个语言列头(en/cn/zh/fr/de/ru/jp/kr/sp/id/th/ar/**ro/nl**/tr/po/it/vi/**fa**/pls)，行2=标题、行3=内容、行4/5=超链接；utf-8 BOM。比 LC 表 18 语言多 ro罗马尼亚/nl荷兰/fa波斯 要补翻，pl 对到 pls 列。模板已存 `KB\产出-补发邮件\X2\_模板\模版_导入多语言邮件内容.csv`（X3 同款在 X3\_模板\邮件导入模板.csv）。正文内嵌真实换行（CSV引号包裹）；2026拓荒成品+字面\n备用版在 `KB\产出-补发邮件\X2\`。
- 运营邮件**不进 LC 表**（i18n 表的 Operation Mail 页签是 AoA 时代废弃模板库，仅10语言列且标注不进游戏），别往里写。

关联 [[x2-city-skin]] [[x2-indoor-furniture-assets]]
