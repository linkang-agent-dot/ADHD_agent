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

## ★Furniture(1105) 换皮三种填法 + K/L 机制（代码核实，换皮必懂）
装饰在游戏里换主题皮，靠 1105 三列，按家具复杂度选填法：
- **J DisplayKey（单DK）**：整件换模型。装饰柱/墙面挂件等简单件——直接填主题DK，无需映射。
- **K WallDisplayKey（`[原,新]`数组）**：局部换。①地板=`[基础地板DK,主题地板DK]`整块花色换(RShopMgr.Area.cs);②墙纸=`[墙预制体子节点名,主题小件DK]`(RWall.cs:441-526)——墙是一个FBX拼很多小件,按**节点名**定位子件换,不换整块。
- **L ShopDecorationDkReplace（`[原,新,原,新...]`扁平）**：整件换带功能家具(柜台/壁灯),拿家具自身基础DK匹配(RFurniture.cs:320,RShopLightMgr.cs:74)。
- **铁律：A位(原)=基础皮对象(基础DK/节点名),占星拓荒共用、固定照抄不动；只换B位(新)成本节日新DK。** 不碰占星行。
- **数组长度跟"基础皮slot数"走，不是跟本节日做了几个prefab**。本节日prefab少于slot时:有资源的slot填新DK,没资源的slot保留占星B值或删(删=该slot不换皮,玩家用到时回落基础皮)。
- 代码字段:CfgGenerated.cs J=col"在场景中的模型"/K=col39 WallDisplayKey(List<CWallSkin>=StrArray)/L ShopDecorationDkReplace(List<int>,注释"替换壁灯和柜台的DK")。

## 占星→拓荒 逐资源 slot 数事实（2026核实,下次换皮直接参考基础slot数）
- **地板**:基础**9种独立花色**(X2_B_P_Floor01a~i,9独立GUID,非冗余),占星做满9个。换皮要9个floor prefab才full(少则部分地板回落基础皮)。
- **墙纸**:基础墙14个节点slot,但**3个是复用**(无前缀Pillar01_Bottom/Top复用P_版、Wall01c复用Wall01b),实际只需**11个独立prefab**(4柱+6墙+1窗)即全覆盖。
- **壁灯**:基础2个灯slot,但占星只做1个灯prefab服务俩slot(2DK→同GUID),本节日1个灯即够(副作用:基础02灯外形被统一,设计接受)。
- **柜台**:L 3对,3件柜台prefab。
- ⚠️**陷阱**:节日floor文件夹里常混入别节日残留(如拓荒文件夹有`X2_B_P_Summer_Floor01d~i`夏日残留),填DK别误用。

## Furniture(1105)/FurnitureBuild(1187) 是 json 配置表，导表落 fo\json\（非 fo\config\）
- 导表：`fwcli googlexlsx`(表名 `1105_x2_Furniture`/`1187_x2_FurnitureBuild`) → `fwcli xlsxtojson`(转 json+tsv) → s2ctool(这俩表不产 s2c)。产物=`fo\json\Furniture.{json,tsv}` + `FurnitureBuild.{json,tsv}`。
- **行筛选**：全表导会带入废弃行(如墙面3)。json 表没有 fo/config 的 merge_rows，靠**按 Id 从 json+tsv 4 文件精准剜除**目标外行(保留各文件原换行: tsv=LF / json=CRLF)，剜后用 json 模块验证对象数合法。
- 验证：拓荒行 DK 必须是新拓荒段(1511094092-118)，非占星残留(1511020840-866)。

## ⚠️ 换皮收尾真正易漏的是「美术接线」不是件数
节日装饰换皮，1111/1187 整行从上一节日复制后件数齐全，但**表1105 Furniture 的 J/K/L DK列常是空/0 或残留旧节日DK** → prefab 没接上、游戏显示空或旧模型。拓荒2026踩此坑：Furniture行110593-110599 的 J全=0、K/L基本空(仅地板/墙纸K复用占星旧DK字符串)。收尾顺序应：**先接线(注册新prefab DK→填表1105 J/K/L,照占星模板)→再据接好的实物推文案命名**。新prefab DK注册走 [[x2-dk-p2-dk-manager]] (P2数字DK系统)。

## ⚠️ 判断「缺件」按 prefab 实数，不按 DK 槽数
对比两节日装饰缺没缺件，必须数客户端**实际 prefab 文件数**，不能数 Furniture 表 K/L 数组的槽数——K/L 里含「基础皮复用槽」(槽位标识指向基础皮 prefab 名/DK)，槽数 > 新 prefab 数。2026拓荒踩坑：按 DK 槽误报"墙14vs11、壁灯2vs1"两处缺口，实际数 prefab 两边都一样、没缺。占星 vs 拓荒真实缺口=地板(9 vs 3,缺6变体)+挂件Pendant(3 vs 2,缺03)+柜台游戏机皮(有 vs 无,缺3)；这 3 处正好对应拓荒"墙面3(355)/舞台(356)没做"。

## ⚠️ AI 占位图标 ≠ 实际 prefab 模型（2026拓荒 1511094092 踩坑）
美术官方图标没到位前用 AI(贴图+上一节日格式)生的预览图标，**可能跟真实 3D prefab 长得完全不是一个东西**——拓荒摆件：AI图标生成了"木浑天仪/星盘"，但实际 Ornaments prefab 是"仙人掌戴草帽抱吉他"(西部摆件)，DK 的 Icon 和 Prefab 对不上。**AI 图标只能当占位**；官方美术图标(由做模型的美术出、跟 prefab 匹配)一到位就**必须替换**(覆盖 client 同名 png、保 .meta/GUID、DK 路径不变→自动显示官方图)。验收装饰必查"图标 vs prefab 是不是同一件"。官方图标存放：用户验收文件夹(如 `Pictures\X3验收\西部皮肤室内图标\`)。

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

## ⚠️ Unity 开着时 git mv prefab → meta 重生坑（2026-06-05拓荒地板改名踩）
拓荒地板 d~i 被美术误命名 `X2_B_P_Summer_Floor01d~i`（实际引用拓荒材质 X2_B_Pioneer_Floor01_Mat，是拓荒件、不是夏日残留——别误删！）。批量 `git mv Summer→Pioneer` 时，**Unity 正开着**：git mv 完 .prefab 的瞬间 Unity 发现 prefab 没 meta，立刻自动生成一个**新 GUID 的 meta**→ 随后 git mv .prefab.meta 因"destination exists"失败 → 该件 GUID 被换成 Unity 新生成的值（如 g: f93965b→9015d2c）。GUID 变了但配对合法、无引用故无害，用新 GUID 录 DK 即可。**规避：改 prefab 名最好在 Unity Project 视图里改，或先关 Unity 再 git mv。** 判断地板是否本节日件：看 prefab 引用的 _Mat 是不是本节日材质，不看文件名前缀。

## ⚠️ 换皮新建行漏填尾部列坑（2026 拓荒 Furniture ContentType BUG）
新建/换皮配置行常**只填前半截列、尾部整段漏填**（拓荒 Furniture 行填了A~Z含DK、但 AA~AQ 17列 ContentType/Size/CollisionSize/SizeFloor/SizeWall/Move/RemoveTime/FurnitureAction(死亡/放置/新建/选中/升级×3) 全空）。
- **空单元格导表后果按字段类型分**：`[][]int32`/`[]int`(数组,如 **ContentType**=TwoDArr) 留空→导出成 null/`{}`→服务端报错(数组不接受{})；`Vector2Int`结构体(Size/SizeFloor/SizeWall)留空→容错成{x:0,y:0}不报错。所以**数组列必须显式填 `[]`**。
- **判断范围别只看报告点名的一个字段**：全列对比同类占星行(astro有值/拓荒空)，一次找全所有漏填列。
- **修法**：从**对应占星行(同家具类型+同等级)整段照抄尾列**(Size/CollisionSize/Action各类型不同,装饰柱{2,2}/柜台{6,5}/地板墙{0,0});照抄不影响已填的DK列(J/K/L在前半截)。改完重导。
- 教训：换皮建行要**整行照抄源行所有列**,别只填前半截+DK。

## ⚠️ 装饰本地化有两处 name 来源、key 可能不一致（X2-43077 墙纸踩坑）
装饰标题/描述本地化有**两套引用**，验本地化要两处都查：
- **item(1111).lc_name/lc_desc**：背包/道具名。
- **Furniture(1105).LcName/LcDesc**(M/N列)：精品家具-装饰 UI 里的标题/描述。
- 二者**可能用不同 key**！墙纸：item 用 `wall_1_title`，Furniture 却用 `wall_decoration_2`（占星历史遗留的双key）。换皮做文案时若只按 item 的 key 做、Furniture 的 key 没文案 → **装饰 UI 标题显示原始键值 `LC_EVENT_labor_2026_...`**（X2-43077）。
- 修法：把 Furniture.LcName/LcDesc 改成 i18n 里存在的 key（如对齐 item 的 wall_1_title）。**验装饰本地化必须逐个 Furniture 行的 LcName+LcDesc key 都查 i18n 存在**。
- 注意例外：柜台(功能家具) Furniture.LcDesc 用通用 `lc_building_counter_desc`(非节日 key)，占星也这样、能显示、是设计如此，**默认**不算 bug 不用改。
- 🔧 **若策划要求柜台 desc 改成"通过节日集卡册获取"(2026-06-09)**：`lc_building_counter_desc` 被 **20 行柜台共享**(基础11051101-15/沙滩/前期/初始/占星11054901/拓荒11059901)——**绝不能改 i18n 本体**(误伤全部柜台)。正解=**新建独立 key 只改该节日柜台那一行的 Furniture.LcDesc 引用**(同 1142 头像框/1365 行军特效"共享视觉需新建独立条目"规律)。拓荒柜台 Furniture 行=**A1行233 / Id 11059901 / "柜台-拓荒节"**。
- 🔑 **X2 i18n 配置引用格式 = `lc_{页签小写}_{id}`，i18n 表 ID 列(B)存的是去前缀的 id**(`lc_building_counter_desc` → BUILDING 页签 B 列存 `counter_desc`)。所以**在 i18n 表搜 key 别搜全名**(搜 `lc_building_xxx` 必落空)，搜去前缀的短 id 或用 skill 的 `all_existing_keys.json`(索引也存短 id)。新建 key:在某页签建短 id→配置引用 `lc_{页签}_{id}`(如建 BUILDING.`counter_card_book_desc` → 引用 `lc_building_counter_card_book_desc`)。文案别乱造,捞现成同义专业范本(如 `card_book_title_2_get_access`="通过X集卡册获得"全18语)逐语言改造。
- 🪤 **i18n 页签写新行用 `append_rows_safe` 不能裸 `update_range`**(2026-06-09)：GSheet 页签**网格行数=实际数据行数**(BUILDING 仅1463行)，`update_range` 写第1464行报 `exceeds grid limits`→静默 False 不写入。必须 `gsheet_utils.append_rows_safe(SID,TAB,[row],id_col='B')`(它 insertDimension 扩网格再写,且避开 INSERT_ROWS 插到表头的坑)。⚠️ **append_rows_safe 本身也可能静默失败 return 0（2026-06-09 EVENT 页签）**：它开头 `gid=get_sheet_gid(); if gid is None: return 0`，而 `get_sheet_gid` 偶发返 None(BUILDING 能拿到、EVENT 拿不到,原因未定)→ 直接 return 0 不写、不报错。兜底=手动扩行：`_call(['sheets','spreadsheets','batchUpdate'...], jb={'requests':[{'appendDimension':{'sheetId':<gid>,'dimension':'ROWS','length':1}}]})` 再 `update_range(SID,TAB,'A{新行}:T{新行}',[row])`(EVENT gid=550403607,从 `tabs <表>` 拿 gid)。验 append 是否真写了:看返回值>0 且 get_values 回读,别只调不验。1011 i18n 表 SID `1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg`,20列=ID_int/ID/cn/en/fr/de/po/zh/id/th/sp/ru/tr/vi/it/pl/ar/jp/kr/cns。改完 i18n(1011)+Furniture(1105) 两表都需各导一次才进游戏。
- 📦 **两表导表落点不同(2026-06-09 实测)**：① **i18n**：`fwcli googlexlsx -f 1011_x2_i18n`(约120s) **直接处理写入 `fo/i18n/{lang}.tsv`(17语言文件)**,无需 xlsxtojson/s2ctool;导出后 runtime key = `{页签大写}_{id}`(配置引用 `lc_building_counter_card_book_desc` → tsv 里 `BUILDING_counter_card_book_desc`)。② **Furniture**：`googlexlsx -f 1105_x2_Furniture` → `xlsxtojson`(转 `fo/json/Furniture.{json,tsv}`) → `s2ctool`。两者全表导,但本次 diff 都干净(i18n 仅+我的key;Furniture 仅 11059901 一行=LcDesc 改动+Comment 真源回正),验 diff 范围确认无他人改动夹带即可 commit。push gdconf 仅入库,生效仍需 x2-kadmin 构建部署(i18n 还要客户端热更文案)。

## 装饰 UIPrefab DK 唯一正确做法 = 指 `_Show` 摆拍 prefab（2026-06-10 张力纠错：我之前"两种做法/轻量占位"分析全错）
Furniture 主件 DK = **Icon+Prefab+UIPrefab 三件套**（同一 key 在 client `Display_Icon`/`Display_Prefab`/`Display_UIPrefab` 三个 asset 各注册一次；objPath 分别记在 `Path_Icon`/`Path_Prefab`/`Path_UIPrefab.asset`）。三型分工：Icon=2D 背包图标、Prefab=可放置 3D 本体、**UIPrefab=商城/装饰展示 UI 里那个会转的 3D 摆拍模型**。
- 🔴🔴 **铁律：装饰 UIPrefab 的 objPath 必须指美术的 `_Show` 摆拍 prefab，这是唯一做法，没有"2D 占位"这条路**。实测全节日都如此：占星 1511020830-836 全指 `X2_D_Astrology01_*_Show`；夏日 Anchor/Photo/Rudder/Swimmingring/Floor_Summer/Wall05/Counter 全 `_Show`；初始 Floor/Wall/Flag/Gear/Counter 全 `_Show`。**美术必出 `_Show`**（房间装饰本来就要在展示位转着看）。
- 🔴 **我2026拓荒的错（别再犯）**：我臆造了一个"轻量 TFWImage 2D 占位做法"(挂 TFWImage 的 `Ui*.prefab` 填图标 sprite)，还误判"拓荒缺 _Show"→把 6 个 UIPrefab DK(1511094092装饰物/093地板/106墙/114墙饰1/115墙饰2/116柜台)**全指了 `UIPrefab/UiLaborDecoration_*.prefab` 占位** → 装饰展示 UI 显示平面图标而非 3D 模型(降级肉眼可见)。**实际拓荒美术 6 个 `_Show` 全出了**：`X2_D_Pioneer01_Ornaments01_Show`/`X2_D_Pioneer01_Pendant01·02_Show`/`X2_B_Pioneer01_Floor01_Show`/`X2_B_Pioneer01_Wall_Show`/`X2_D_Pioneer01_Counter01_Show`(各自 Decoration/Building/Shelf 子目录)。程序已返工把 objPath 改回各自 `_Show`。**那批 `UiLaborDecoration_*.prefab` + p2-uiprefab-create 的 TFWImage 占位法 = 不适用于房间装饰，别再用**。
- ✅ **装饰换皮配 UIPrefab DK 的正确流程**：先 `find client/Assets/x2/Res/Shop/Indoor -iname "*<节日英文>*Show*.prefab"` 列出美术给的全部 `_Show`(占星=Astrology01/夏日=Summer/拓荒=Pioneer01)，**每件装饰的 UIPrefab objPath 直接指对应 `_Show`**。若某件暂时 `find` 不到 `_Show`=美术还没出→**催美术补，别拿 2D 占位顶**(顶了就是 bug)；美术分批补齐后回头把 objPath 全指上。
- 🔑 **objPath 落点**：`Path_UIPrefab.asset` 里每条 `- key: <id>` + `objPath: <prefab路径>` + `intAre: 0`。张力给的 diff 就是这行：旧(我)`UIPrefab/UiLaborDecoration_decoration.prefab` → 新(程序)`Decoration/X2_D_Pioneer01_Ornaments01/X2_D_Pioneer01_Ornaments01_Show.prefab`。
- 🔍 **核 DK key 归属用 `Path_Prefab.asset`(指可放置本体)最可靠**：同一 key 在 Icon/Prefab/UIPrefab 三型共用，`Path_Prefab` 的 objPath 指真模型(如 1511094093→`X2_B_P_Pioneer_Floor01a`=地板)，据此确认每个 UIPrefab key 该指哪件的 `_Show`，别只信占位文件名(那是我当初可能配错的命名)。拓荒映射(已核)：093地板/106墙/114墙饰1/115墙饰2/116柜台。
- ⚠️ **程序修这类问题可能只改被点名那一件、其余同类漏**(2026-06-10 实测：程序只把 092 装饰物改成 `_Show`，093/106/114/115/116 五件仍露占位)。验收要**逐件核全部同批 key**，别因"程序说改了"就假设全改了。改法=Edit `Path_UIPrefab.asset` 把占位 objPath 直接换成 `_Show` 路径(注意 `X2_D_Wall decoration` 目录名带空格)，改完逐条 `[ -f client/Assets/x2/Res/Shop/Indoor/<去Assets前缀路径> ]` 验目标 prefab 真存在。
- 🔒 **x2client `master_bugfix` 是受保护分支(2026-06-10)**：DK/.asset 改动 commit 后直接 `git push` 被 `pre-receive hook declined: not allowed to push to protected branches` 拒。要落地走 **feature 分支 + MR**(`git push -u origin <新分支>` 再 GitLab API/网页开 MR 合 master_bugfix)，或把本地 commit 交有权限的程序 push。别在 master_bugfix 上指望直推。

## ⚠️ FurnitureBuild.DisplaySubLabels = 品类页签图标(共享,别按节日改)
FurnitureBuild(1187) 的 **DisplaySubLabels(J列)** 不是单件装饰图标，是 **specialdeco 商城页签的"品类分类图标"**——按家具品类共享、跨节日固定不变：摆件/柜台→`1511018769`、地板→`1511018770`、墙面→`1511018771`、墙纸→`1511018772`。占星拓荒**用同一批值**。**换皮别动它、别改成 per-装饰图标**(2026拓荒我误改成086-091被打回)。单件装饰图标是 item.display_key(1111) 和 Furniture.J 的 Icon,跟这个无关。

## 命名漂移坑
道具中文名可能跟美术实物/上一节日对不上：占星"柜台"(523)→拓荒换皮改名"舞台"(356)；占星"装饰物"(507)→拓荒"装饰柱"(350)。用户口径可能停在上一节日叫法 → 必须对图+对品类(E列)核实，别照道具名瞎起。

关联 [[project-x2-pioneer-decoration-copy-todo]] [[x2-dk-p2-dk-manager]]
