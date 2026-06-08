---
name: reference-x2-indoor-furniture-assets
description: X2室内装饰家具(装饰柱/地板/墙纸/挂件/柜台等)的客户端资产位置、命名规范、TGA看图法；节日装饰换皮/起名/验收时用
metadata: 
  node_type: memory
  type: reference
  originSessionId: e3fce9d2-73c8-4c84-b61e-26b3f0014e65
---

# X2 室内装饰家具资产链路

主城室内装扮家具（装饰柱/地板/墙纸/墙面挂件/柜台/窗/壁灯/吊饰）的客户端资产，**不是世界地图地块装饰**（那是 `k1/Res/Map/WorldMap/Decoration`）。

## 资产位置（客户端仓 D:\UGit\x2client，分支按节日如 dev_festival）
根目录：`client/Assets/x2/Res/Shop/Indoor/`，按类型分三大目录：
- `Building/` — 建筑结构件：X2_B_Pillar(柱) / X2_B_Floor(地板) / X2_B_Wall(墙) / X2_B_Window(窗) / X2_B_BracketLight(壁灯)
- `Decoration/` — 装饰摆件：X2_D_*_Ornaments(吊饰) / `X2_D_Wall decoration`/*_Pendant0N(墙面挂件)
- `Shelf/` — 柜架：X2_D_Counter/(柜台Counter0N + 地毯Carpet0N + 摆件Prop0N，整组陈设)

## 命名规范
- 前缀 `X2_B_`(building) / `X2_D_`(decoration)，节日段 `Pioneer01`(拓荒) / `Astro`(占星) 等
- 文件如 `X2_B_Pioneer01_Pillar01_D.tga`；后缀 **_D=漫反射(看花色用这个) / _N=法线 / _L=自发光**
- prefab 常一件家具拆多个：柱=Top/Bottom(±_Door)，墙=主体/_Beam横梁/_Skirting踢脚线，地板=a/b/c花色变体
- ⚠️ 偶有拼写错(Window 写成 `Windor01`)；地板贴图可能塞在 Pillar 目录里(美术按套打包)

## 资产格式：3D 网格，无 2D 预览 PNG
- 美术上传的是 **FBX + TGA 贴图 + mat + prefab**，**没有渲染好的成品预览图**
- 看图办法：把 `_D.tga` 漫反射用 PIL 转 PNG（`Image.open(fp).convert('RGBA').save(png)`，路径用 `D:/...` 不用 `/d/...`）。平面件(地板/墙纸/地毯)贴图≈肉眼所见；柱/柜台/挂件是 UV 展开图，能看材质配色但造型要脑补。

## 配置侧对应（节日装饰投放）—— ★一件道具=多prefab「融合」，不是1:1
完整链：`1111 item(道具名/描述LC key) → 1187 FurnitureBuild(FurnitureIds) → 表1105 Furniture def → N个prefab的DK`

**关键：一件可投放装饰 ≠ 一个 prefab**。地板/墙纸/柜台这类把一整组 prefab「融」进单行 Furniture 的数组列：
- **表 1105 Furniture**：SheetID `1e7rK3gkXIMK9gH37zjwBAvPfffZ5UGXGp_tjQ4qXODU`，页签 `Furniture`（表号 1105_x2_Furniture）
- 关键列：**J=DisplayKey(单模型DK) / K=WallDisplayKey(ARR,多子网格) / L=ShopDecorationDkReplace(ARR,换柜台/灯多DK) / E=品类(4装饰物/7地板/8墙上装饰/9墙纸/10柜台皮肤) / G=1柜台功能**
- 占星节先例(2026)：磁盘约37个prefab → 塌缩成**7件**道具：装饰物(1prefab,J单DK)/地板(9变体,K数组9)/墙纸(柱4+墙6+窗1≈14件,K数组14)/墙饰1·2·3(各1挂件,J单DK)/柜台(柜台+变体≈6,L数组6)。占星行 B217-B225，DK全填满(J=1511020830-836)可当照填模板。
- ⚠️ 所以"美术给8类、配置只投5件"**不一定是配漏**：窗/柱融在"墙纸"里、灯融在"地板"里，本就不是独立件。对齐美术要按"融合后件数"算。

## ⚠️ 换皮收尾真正易漏的是「美术接线」不是件数
节日装饰换皮，1111/1187 整行从上一节日复制后件数齐全，但**表1105 Furniture 的 J/K/L DK列常是空/0 或残留旧节日DK** → prefab 没接上、游戏显示空或旧模型。拓荒2026踩此坑：Furniture行110593-110599 的 J全=0、K/L基本空(仅地板/墙纸K复用占星旧DK字符串)。收尾顺序应：**先接线(注册新prefab DK→填表1105 J/K/L,照占星模板)→再据接好的实物推文案命名**。新prefab DK注册走 [[x2-dk-p2-dk-manager]] (P2数字DK系统)。

## ⚠️ 判断「缺件」按 prefab 实数，不按 DK 槽数
对比两节日装饰缺没缺件，必须数客户端**实际 prefab 文件数**，不能数 Furniture 表 K/L 数组的槽数——K/L 里含「基础皮复用槽」(槽位标识指向基础皮 prefab 名/DK)，槽数 > 新 prefab 数。2026拓荒踩坑：按 DK 槽误报"墙14vs11、壁灯2vs1"两处缺口，实际数 prefab 两边都一样、没缺。占星 vs 拓荒真实缺口=地板(9 vs 3,缺6变体)+挂件Pendant(3 vs 2,缺03)+柜台游戏机皮(有 vs 无,缺3)；这 3 处正好对应拓荒"墙面3(355)/舞台(356)没做"。

## 装饰预览图(256×256透明底)缺失时——AI双参考产线(已验证)
节日装饰的 2D 预览图标(商店/UI 显示)在 `client\Assets\x2\Res\UI\TextureNew\Icon\IAP\{节日}_decoration_*.png`(占星=astro_decoration_floor/wall/decoration/01/02/03/counter，256×256 RGBA透明底)。新节日常没做(拓荒2026缺)，原图是 Unity 拿 `_Show` 摆拍 prefab 渲染的——拓荒连 _Show 都没有。
**AI 补图产线(2026-06-05 拓荒验证，质量可用含立体件)**：
1. **双参考**：格式锚=上一节日同件预览图(定构图/45°视角/卡通描边/打光)；内容锚=拓荒该件 `_D.tga` 漫反射转的PNG(定配色/材质/元素)。
2. **生成**：`grfal-api` skill `generate_image` model=gemini，prompt 明确"FIRST ref定构图、SECOND ref定材质配色，保持构图换材质"，**必须 --submit-only + --check-task 轮询**(全模型long_running)。
3. **下载**：结果是相对路径 `/api/output/...`，需 `https://grfal.tap4fun.com`+Bearer(token_store.json的access_token)+`ssl不验证`下载。
4. **抠透明对齐格式**：scipy `ndimage.label` 取**边缘连通的底色区**置alpha=0(保留卡通描边内部，白瓷砖等不被误吃；tol≈30-34)，再 `getbbox` 裁剪居中 → resize 256×256 RGBA。
- 平面件(地板/墙纸)AI还原度高；立体件(柱/柜台/挂件/吊饰)是"构图准+造型AI近似"，验收接受即可用，要严格一致才走Unity渲染。

## 装饰预览图标的引用落点（落地链路，2026-06-05实操确认）
预览图标就是**装饰道具自己的图标**，没有独立"装饰商店/预览"配置表。落地链路：
`PNG放 client\Assets\x2\Res\UI\TextureNew\Icon\IAP\{节日}_decoration_*.png → 录 Icon DK(Display_Icon.asset，key=全局max+1) → item表(1111, SheetID 1pm0nztHsjpHmFBEmx-bLtP7Zjf4GFC67wo-sUmqY7Fs/页签item)第6列 DisplayKey(C_INT_display_key)填该DK号`。
- meta 直接复制同目录占星 astro_decoration_*.png.meta 全文换 guid 即可(Sprite规格 textureType8/spriteMode1/iPhone+Android textureFormat50/overridden1，maxTextureSize2048)。
- 换皮残留坑：拓荒6道具 DisplayKey 原是**占位值 405243**(6件全一样，非0)，换皮整行复制带来的，落地时覆盖成专属DK。
- 顺序硬约束：**先 Ctrl+Shift+E 导出DK(写Path_Icon) → 再 item导表**，否则配置指向未导出DK会断。
- 这是 Icon 层(2D预览)；3D模型层走 Furniture表1105 的 J/K/L(见上)，两层独立。

## ⚠️⚠️ item表(1111)写DisplayKey的列错位坑（2026-06-05 连环踩，务必记）
item 表第1列(A)=`p2_title`(空)、id 在 **B 列**、`C_INT_display_order`=**F列(第6)**、`C_INT_display_key`(图标DK)=**G列(第7)**、display_quality=H列。
- `gsheet_query row` 的 `[5]display_order/[6]display_key` 是**0基数据索引**，换算列字母要 +1（index5→F、index6→G），**别直接拿索引当列号**(否则写成E:F整体左移一列，把图标DK灌进display_order/quest_class、display_key留0→线上图标全不显示)。
- 图标DK必须落 **display_key(G)**，不是 display_order(F)；装饰道具 display_order 固定 405243(占星/拓荒同)、quest_class=0。
- 写前**先读一行线上正常的同类道具**(如占星地板11119508: F=405243/G=1511020780)对齐列，再用 gsheet_utils `update_range` 写 `G{row}` 单点、读回验证；改前那批值从**备份页签**取原值复原，别猜。
- 导表 merge_rows 后**必须逐行核对 tsv 第6/7字段值各就各位**再 commit(行筛选 agent 验 diff 卡住才避免了盲推图标DK进排序列的事故)。

## 命名漂移坑
道具中文名可能跟美术实物/上一节日对不上：占星"柜台"(523)→拓荒换皮改名"舞台"(356)；占星"装饰物"(507)→拓荒"装饰柱"(350)。用户口径可能停在上一节日叫法 → 必须对图+对品类(E列)核实，别照道具名瞎起。

关联 [[project-x2-pioneer-decoration-copy-todo]] [[x2-dk-p2-dk-manager]]
