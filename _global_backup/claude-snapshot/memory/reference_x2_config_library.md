---
name: x2-config-library
description: X2 配置表查询权威源——SheetID 必用 gsheet_query.py resolve 现解（禁硬抄 P2）；含别名约定/换皮组装模式/追踪链/gacha内外圈/踩坑
metadata: 
  node_type: memory
  type: reference
  originSessionId: bd0fa84a-a021-477f-a7de-6a4623c89ffb
---

⚠️ **X2 配置表 SheetID 的唯一权威源 = 解析器 `gsheet_query.py`，不是任何硬编码 KB。**

## 一、为什么（2026-06-04 踩坑根因）
`reference_config_library.md` 和 `C:\ADHD_agent\.cursor\config-library\*`（table-reference / table-index / table-schema / reskin-rules）**全是 P2 项目的 SheetID**。X2 与 P2 子表 **id 空间高度重叠**（如 2141 里两边都有 `21410117`），硬抄 P2 SheetID 去查 X2 会**静默返回 plausible-but-wrong 的 P2 数据、完全不报错**。
- 实例：拓荒 gacha 内圈排查，P2 `21410117`=「S300累充BP宝箱」，X2 `21410117`=「2025拓荒节-第1段奖池-不放回」，同 id 两套内容。
- ⚠️ 连 `p2-x2-reskin` skill 的「前置动作」都让人读 P2 的 `table-reference.md`——**那份的字段 Schema / 追踪链可借（结构 P2/X2 通用），但 SheetID 一律不用**，X2 走 resolve/别名。

## 二、正确做法：gsheet_query.py（X2 任何表 查/改/诊断 第一步）
工具：`C:\ADHD_agent\.cursor\skills\google-workspace-cli\gsheet_query.py`（解码干净无 GBK 乱码，优先于 gws/gsheet_utils 裸读）

**别名约定（最关键）**：
- **X2 = bare 表号默认就是 X2**（`2141` 直接命中 X2），或显式 `<表号>_x2_<name>`（如 `2112_x2_activity_config`）
- **P2 必须加后缀** `_dev` / `_P2`（如 `2112_dev`、`1111_P2`）——不加 = X2

```
python gsheet_query.py resolve  2141                 # 表号→SheetID+页签（必做第一步）
python gsheet_query.py headers  2112_x2_activity_config
python gsheet_query.py row      2112_x2_activity_config <ID>
python gsheet_query.py idrange  <表号> <起ID> <止ID>
python gsheet_query.py filter   2142 1 607           # col[1](group)==607
python gsheet_query.py search   2112_x2_activity_config 拓荒
python gsheet_query.py tabs <表号>  /  list          # list=全部1070张注册表
```

**查询踩坑**：
- `2115` 活动任务：**ID 在 col[1]**（col[0] 是 group），查询须加 `--id-col 1`
- 🪤 **`gsheet_query` 的 `row N` ≠ GSheet 真实表行号，是数据相对序号（2026-06-10 改 2122 score_rule 踩坑）**：filter/idrange 输出的 `row 816` 不能直接拿去 `update_range E816`——2122 实测 `row 816`(id 21223204) 的真实表行是 **817**(差 1，因首行表头/p2_title 偏移)。**写回前必须先用 `gsheet_utils.get_values(SID,TAB,'<idcol>1:<idcol>2000')` 扫 id 列定位真实行号**（2122 id 在 C 列；找到行后写 `E<行>`），写完再读回该 cell + 读 id 列确认行没串、列没右移。别信 `row N` 当行号。
- `2135` X2 默认页签带 `(qa)`；`2142` 页签带后缀「（天赋投放活动）」；`1118` 含「严禁手改」
- ⚠️ **同名/master 干扰页签陷阱（2026-06-08，让一个 sub-agent 整轮跑偏）**：单张表的 spreadsheet 里常有一堆相似名页签——如 `2013(iap_template)` 有 **21 个**页签：`iap_template_x2（qa）`(gid 1938706798,导表首页签) / `iap_template_x2master` / `iap_template_Master` / `template_master` / `iap_template_x2（qa）（25大富翁）` / 各种 `_bak_*` 等。**真源/导表只认 `（qa）` 页签**（`gsheet_query.py resolve`/`row` 默认命中它，导表也只导 index0 最左页签）。**别去读 master 页签**——master 是另一套（QA→主数据 sync 的下游，见 `reference_iap_sync_to_master`），里面没有新节日的行，读错了会误判"行根本不存在"。诊断"行在不在/值对不对"时，先 `tabs <表号>` 确认自己读的 gid 是 `（qa）` 那个。
- X2 导表链路闭环：改 `（qa）` GSheet → 导表(下载 GSheet→`D:\UGit\x2gdconf\fo\config\*.tsv`) → commit+push(pre-push 钩子自动查配置冲突) → 构建/部署。**导表前本地 tsv 还是旧值是正常的**，导表就是来刷新它的，不是冲突。
- 🪤 **行筛选导表别盲跑 merge_rows——它的 LF 输出会把整表炸成假 diff（2026-06-10 改 2122 单行实测）**：① `merge_rows.py` 用 `newline="\n"`(LF) 重写整表，而 x2gdconf **实测 autocrlf 是关的、HEAD 存 CRLF** → merge 后 `git diff` 直接炸成 **821/821 全表假 diff**（纯行尾噪音，`git add` 也不归一化）。⚠️ 纠正旧 KB「merge 后用普通 git diff 验就行」那条——本仓不归一化，merge_rows 的 LF 会留全表假 diff。② **更省事的正路**：`googlexlsx -f <表> → xlsxtojson -g all → s2ctool` 这套**下载工具直出 CRLF**，跑完先 `git diff --stat`——**若已只差你改的目标行**（说明 GSheet 除你那行外与 HEAD 一致），**直接提交下载产物即可、根本不用 merge_rows**。只有「全量下载夹带了他人未验证改动」时才需 merge_rows 行筛选。③ 真用了 merge_rows 又遇行尾炸：`git checkout HEAD -- <tsv>` 还原后重新下载，或把文件 LF→CRLF 转回再提交。④ `xlsxtojson -g all` 会**重生成所有 tsv**：工作区里别人未提交的 tsv 改动会被还原到 HEAD-json 态；若那些改动早已 commit 则无损(只清掉本地噪音)。⑤ 提交务必**显式 `git add <你这张表>`**，别 `git add .`(会扫进他人/重生成的无关 tsv)。
- ⚠️ **「改了 GSheet ≠ 导了」+ 整张表漏导（2026-06-08 拓荒 BP，2130 停在1月旧版）**：换皮常只导了部分表，**主配置表/低频表极易整张从没导过**——tsv 停在几个月前版本、连新节日的行都没有（本次 `activity_battle_pass.tsv`(2130) 最后提交 2026-01-13，GSheet 有 `213000010` 但 tsv 全是旧 `2130000x`+旧 iap）。⚠️ 整张漏导是**部署风险**（直接部署可能用旧表覆盖服务器）。**部署前逐表自检**：① `git log -1 --format=%ci -- fo/config/<表>.tsv` 看时间戳是否晚于换皮日期；② `grep <新节日关键行id> fo/config/<表>.tsv` 确认新行在 tsv 里。这是导表卫生，值得做。
- ✅ **本次结案修正（别被上面误导）**：拓荒 BP「解锁了没法领奖」的**真因是测试端客户端没更新**（旧客户端没有新 BP 道具/逻辑），更新客户端后即正常——配置侧（2013 修复+2130/2131）本来就是通的，2130 tsv 停在1月**不是这次的领奖卡点**（服务端 2130 是别的分支早先部署的，已含 213000010）。**教训：客户端类活动「解锁了/显示异常/领不了奖」先确认测试端客户端是不是最新版，别一头扎进配置深挖**——这次从 IAP 一路查到 2130 漏导，最后是客户端版本。配置自检照做，但客户端版本要先排掉。
- 写回 X2 QA 表强规则见 `C:\ADHD_agent\.cursor\rules\x2-gsheet.mdc`（resolve→idrange复查→update指定range→再复查；不能只改本地tsv/分支）

## 三、换皮组装模式速查（哪种活动动哪些表，结构 P2/X2 通用）
> 新任务先走 skill 的 S0 触发条件命中模块，别硬对号。完整流程见 `p2-x2-reskin` skill。

| 活动类型 | 命中模块 |
|---------|---------|
| 普通活动礼包 | 2112+2115+2135+2013+2011+1011(i18n)+1511(DK) |
| 预购连锁礼包 | 2112+2135+2011+1011+1511（**跳过 2013**）|
| 装饰物 | 1111+1118+1127+2148+2171+1168+1011+1511+1187 |
| 集卡册 | 1111(卡包)+**1108/1107/1123/1109**+1011+2112（2112复用不新建）⚠️**X2不是6001-6004**|
| **主城皮肤 Gacha** | 2112+2121(5组件)+**2124(外圈drop)**+2135→2011→2013+**2141+2142(内圈)**+2137+1111 |
| 自选周卡 | 2112+2135→2011→2013+2024(自选坑位)+1111(subscription) |
| Wonder 砸金蛋 | 2112+2121(15组件)+2115+2124(掉落)+2135→2011→2013+2122+1111(金蛋) |
| BP 通行证 | 2112+2130+2131(25级)+2121+2122→2118(排名奖)+2137+1365(行军特效)+1111 |
| 节日累充 | 2112+2115(档位)+2121(跳转/大乐透/show_rank)+2122(score_rule含全部2011)+2137 |
| 掉落转付费 | 2112×3(掉落/礼包/主活动)+2116(兑换)+2121(actv_links跳转+discount→2011) |
| 大富翁 | 2112+2135+2011+2013+2115+2116+2121+2151(地图) |
| 装饰礼包(轻) | 2112(壳,components只1个)+2121(**discount**组件,status=[{iap:2011}])+2011+2013(同config_id**多档**按价分,other_items装装饰item)+2111日历。夏日范例 211200077→212100051→2011910027→2013910035($4.99地板+墙纸)/036($9.99墙饰4件)。装饰本体走 [[reference-x2-indoor-furniture-assets]] 三层；玩家"获取途径"另配 1168(见下) |

**🪤 礼包/弹窗 banner 的真源是 2013 不是 2112（2026-06-10 X2-43116「装饰礼包Banner未换」沉淀）**：
- **购买弹窗顶部 banner = 表 2013(iap_template) 的 `pop_banner_url`(col27/AB列)**；`banner_url`(col26)是商城列表 banner。**2112 的 `banner_url`(col14) 只是活动入口/日历 banner，不是购买弹窗**。换礼包 banner 只改 2112 没用，必须改 2013.pop_banner_url（拓荒装饰礼包=2013 id 2013920401, config_id 2011920191）。
- **礼包弹窗 banner 图存在 `Assets/X2/operation/PackBanner/` 文件夹**（不是 EventBanner！），配置写法 `assets/x2/operation/PackBanner/GiftPack_bg_<name>.png`（如 GiftPack_bg_city/cloak/Research…全是弹窗 banner）。EventBanner 是活动横幅，两个文件夹别混。拓荒装饰礼包弹窗图=`GiftPack_bg_PioneerDecorations.png`。⚠️本次还发现 2112.banner_url 把它写成 EventBanner 文件夹(文件不在那)→2112 那张也坏。
- 链路：2112 → 2121(discount,status→iap) → 2011 → 2013(filter col3=config_id)。弹窗图在最末层 2013。
- ⚠️ **2013 页签行号陷阱（差点写错行）**：`gsheet_query.py row 2013 <id>` 报的"row N"是它默认读的页签的行号，**与真源页签 `iap_template_x2（qa）` 的行号不一致**！本次 gsheet_query 报 row6606，但 （qa）页签 row6606 是夏日的 2013910036，目标 2013920401 实际在 row6607。**写 2013 前必须在 （qa）页签自己扫 id 列定位真实行号**(读 B 列 match)，绝不能拿 gsheet_query 的行号直接 update，否则覆盖错行。

**X2 集卡册三层结构（2026-06-05 拓荒集卡册改奖励实测）**：Book(1108)→GroupID数组→Group(1107)→CardID数组→Card(1123)，外加 Store(1109)。奖励字段位置：
- **1108 CardGallaryBook**：`Rewards`(col13/N列)=**集齐全部卡组的总奖励**(=「全部卡册收集完成奖励」)；GroupID(col3)挂该册所有卡组；CardPackID(col12)。
- **1107 CardGallaryGroup**：`RewardsFirst`(col10/K列)=单个卡组首次集齐奖励，`RewardsFollow`(col11/L列)=重复集齐奖励。**「最后一个卡册/卡组」=该 Book 的 GroupID 数组里 ID/DisplayOrder 最大的那行**(拓荒=11074009「拓荒盛典」)。
- 1107/1108 两表 **Id 都在 col[1]**(查询须 `--id-col 1`)；两表页签名都叫 `CardGallaryGroup`(Book 表也是这名，非笔误)。
- 拓荒 Book=11081004「拓荒传奇」，9 卡组 11074001~11074009。两个头像框道具：111111325(普通)/111111327(Wonder)；5+装饰 111111350~354 及 111111332「墙饰2」等。

**X2 集卡册卡片格渲染链路 + 「卡片图标消失/未展示立绘」诊断（2026-06-10 X2-43104 沉淀）**：客户端 `Assets/x2/Runtime/TreasureAppreciation/MiniGameCardItem.cs::RefreshCard()`：
- **卡立绘 = `1123 CardGallary.DisplayKey`(col6)，走 `DKType.Portrait`(散图，路径 `Assets/x2/Res/UI/TextureNew/MiniGame/pic/CardGallary_B{册}_P{组}_{序}.png`)**；卡框 = `DisplayKey1`(col7,全册共用如1511094002)走 `DKType.Icon`(图集)。小图 Icon 在 `NewSprite/icon/MiniGameCard/`(进 `MiniGameCard.spriteatlas`)，大图 Portrait 在 `TextureNew/MiniGame/pic/`(散图按路径加载)。卡组缩略图=`1107.DisplayKey/1/2`(Icon)、卡册主题图=`1108.DisplayKey/2/3`(Icon)。
- 🔑 **核心逻辑：`hasCard = Num>0 && CfgID>0` → `Card.SetActive(hasCard)` / `None.SetActive(!hasCard)`。卡立绘只在「玩家拥有该卡(Num>0)」才显示；没拥有 → 隐藏立绘、显示通用 `None` 占位(灰底徽章卡 + 顶部稀有度色条)**。所以**集卡界面里没集到的卡格 = 设计内占位，不是图标丢失**。占位上稀有度色条(`cfg.Star`)仍正常渲染=cfg配置读取正常的反证。
- 🪤 **「部分卡组图标消失/未展示立绘」十有八九是误判**：报单人多在「已集到卡的组(显立绘) vs 0/N 的组(显占位)」间对比，把未集齐占位当成 bug。判据：截图卡组进度若是 `0/N`(一张没集)→全是正常占位。**先看进度数字**，别一头扎进配置/资源。
- **真要排资源**：① `gsheet_query row 1123 <cardid> --id-col 1` 取 DisplayKey；② 在 `Path_Portrait.asset` grep 该 key 拿 objPath、确认 PNG 存在；③ 同册各组 PNG/.meta/导入设置逐项对比(同 commit 提交则通常逐字节一致、无单组差异)。**若仓里 9 组资源完全一致、却只报某几组**——基本排除配置/资源 bug，根因在**客户端构建/打包没含最新散图**(客户端类显示异常先验测试包是不是最新，见 §二)，需重打包/热更后用最新客户端复测，不是改配置表。

**大富翁节日换皮必检（2026-06-05 拓荒大富翁三礼包 bug 踩坑）**：节日大富翁=占星节模板逐字 reskin，复制时**最易在 2013(iap_template) 模板层漏拷 + 存钱罐组件 pkg id 打错**，三处全静默不报错：
- ① **骰子红包包**(2135 红包49.99/99.99 → 2011 red_pack_pkg → 2013)：2013 里按 `config_id` 极易整组漏建 → 游戏里**整块不显示**。查法 `gsheet_query.py filter 2013 3 <2011的iap_id>`，0 条=漏。
- ② **锚点礼包**(2011 一个 id 对应 2013 **多档** 4.99/9.99/19.99/49.99/99.99)：占星 5 档，拓荒只拷了 49.99/99.99 两档 → **缺低档**。同一 config_id 在 2013 应有 5 行。
- ③ **存钱罐**(2121 type=monopoly_piggy_bank)：`reward` 列 pkg id 易把 `2135213_3_09`(存钱罐通用包) 错写成 `2135213_2_09`(占星抢购包，存在但绑别的活动→**无法购买**)。对照占星 piggy 21217038→213521117 校验。
- 链路：2135.iap→2011.id→2013.config_id；存钱罐 2121.reward→2135→2011→2013。**节日换皮后必按 config_id 在 2013 逐 id 数行数、和占星节同档对齐**。

**掉落转付费 actv_links 跳转必 fork（2026-06-08 拓荒"跳转没跟礼包匹配"踩坑）**：掉落转付费=3 个 2112(掉落/礼包/主活动)。主活动 components 里有个 `actv_links`(2121) 组件，`expr.args`=`[{drop:掉落活动id},{drop_pkg:礼包活动id}]`，**客户端靠它把"掉落活动↔礼包活动"配成一对取数据**。每个节日/schema 都应有自己独立的 actv_links 指向自己那对(前期 212100317→211201001/002；占星 212101119→21127359/360)。⚠️**换皮整套复制上个节日 2121 组件(actv_links/discount/drop_topay_show)时极易不 fork**——拓荒主活动 21127371 直接复用占星 212101119，导致跳转仍指占星的掉落+礼包(占星下线即指向不存在活动)。正解=新建 actv_links(全局max+1)指本节日的 drop+drop_pkg 活动 id，再改主活动 components 引用它；旧节日那条不动(仍被旧主活动引用)。同理 discount(指 2011 iap)/drop_topay_show 也常残留上个节日，按需 fork。

**节日大富翁(monopoly)装饰品奖励换皮必检（2026-06-09 X2-43081「装饰品奖励未更换/仍显示星盘装饰」沉淀）**：节日大富翁(2112 const `event_fes_*_monopoly_gacha_*`, base=占星/夏日母版)的「装饰品奖励」有**两处独立配置**，换皮极易漏改其一或两处都误用旧资产：
- ① **棋盘中央装饰展示** = components 里 `statue_preview`(2121) 组件，其 `arg1`(col6/G) = 一个 **1187 FurnitureBuild id**(中央展示哪件装饰本体)。拓荒误填 11871059(=「装饰物-占星节-2025」build)，应改 11871066(=「装饰柱-拓荒节-2026」build)。注意组件 comment 写着"(拓荒节)"也可能 arg1 仍是旧 build——以 arg1 实际指向为准。
- ② **顶部圈数进度奖励** = components 里一组 `task`(2115, group 119)，达成圈数 5/10/20/30...200 各发奖；其中装饰道具档(母版圈30/150/200 发装饰 item ×1/×6/×6)的 `A_ARR_reward`(col H) 里的 item id。
- 🪤 **孤儿批陷阱**：拓荒这几档误发 `111111328`——它名字是拓荒(`LC_EVENT_labor_2026_wall_decoration_1`)但 **display_key=1511020779 套的是占星装饰图标**、且无 1187/1105 build 无法搭建(废弃孤儿批 328-335)。所以玩家看到"拓荒名+占星图标"=报「仍是星盘装饰」。正确装饰柱=`111111350`(图标 1511094086 + FurnitureBuild 11871066 可搭建)。**换皮校验法**：① statue_preview.arg1 的 1187 build 必须是本节日(`search 1187 <节日>`)；② 圈数 task 装饰档 reward item 的 display_key 必须=本节日图标、且该 item 在 1187 有可搭建 build(别用 328-335 孤儿批)。母版 21127225(夏日)对照：statue_preview 21217039 arg1=11871039、圈30/150/200 发 item 11119463。

**🪤 新增配置行前必先"查存量"+真实 max-id（2026-06-09 拓荒装饰礼包 1168 撞号踩坑）**：
- **id 不按行号排序**：`gsheet_query.py tail`/末行 id **≠** max id（1168 末行 id=11684594，但表中间还有 11684596-604）。按"末行 id+1"分配会**撞已存在 id**→GSheet 出**重复 id**、merge_rows 显示 `[updated]` 而非 `[added]`（撞号信号！）。求 max 要**扫整列** `sort -n | tail -1`。
- **"没配"常是"配了但值错"**：用户说"1168 拓荒装饰都没配"，实际早有完整拓荒块(11684596-604, asset 350-356、拓荒 DK 1511094086+)，只是 access_group 是旧残留(350→占星大富翁/351·352→集卡册/353·354→夏日装饰礼包)。**先 `search`/`filter` 查 asset_id 在不在，在=改值(fix access)不是新建**。本次误当没配去 insert→撞号→删 5 行重来。
- merge 后用普通 `git diff` 验（别 `-c core.autocrlf=false`，详见 [[X2导表工作流]]）。
- **1168 速查**：每件装饰一行，`access_group`(col F)=`[{"id":11531181,"args":["<2112活动id>"]}]`(11531181=活动跳转)；拓荒2026 装饰柱350→大富翁21127364 / 地板351·墙纸352→BP21127375 / 墙饰353·354→装饰礼包21127384。

**🪤 节日活动 `show_hud`(2112 col S/idx18) 必挂当期节日 HUD 组 id，否则活动入口不显示=「开不了」（2026-06-10 装饰礼包踩坑）**：新建节日活动别把 show_hud 留 0 或抄上个节日。拓荒2026 全活动(大富翁21127364/BP21127375/BP礼包/基金/掉落转付费主活动)的 show_hud **统一=`21121491`**(拓荒节 HUD 活动组)。我新建装饰礼包时设 0(为避开夏日 HUD)→活动没挂进拓荒 HUD 组→玩家找不到入口=开不了。**换皮新建活动：show_hud 取"同节日其他活动"的值(它们都一样)**。注：当时一度怀疑 discount 礼包 `time_info` 字段名(夏日用 `actv_base_id`、我抄成 `actv_id`)是主因，其实不是——真因是 show_hud；time_info 沿用同模板即可。

**外显表**：1111 item / 1142 avatar_frame / 1173 chat_skin / 1180 map_emoji / 1312 city_skin / 1126 city_building_skin / 1365 行军特效

**X2 房间装饰（地板/墙纸/墙面/柜台/舞台类）三层链路 + "能否运行"判据**（2026-06-05 拓荒装饰两套排查）：
- 真正的链路 = `1111 item → 1187 FurnitureBuild(搭建配方,col3 FurnitureIds指模型,col10 Requirement指item) → 1105 Furniture(家具模型+等级+DisplayKey/WallDisplayKey/StrArray美术贴图+buff+citybeauty)`。
- **判据**：三层全通=能搭建放置=正常运行；**只在 1111 有 item 定义、1187/1105 无引用=孤儿，玩家拿到也无法搭建**（拓荒 A 套 111111328-335 即孤儿，B 套 111111350-356 三层全通才是线上跑的）。孤儿 item 反而可能配了 1111.display_key 背包图标，别被图标误导。
- ⚠️ 这套 ≠ 2148 event_decroation_level（那是**雕像升星**装饰，另一系统，2023/2024 雕像在那）。装饰排查先分清是哪套系统。
- 模型表是 **1105_x2_Furniture**（Id=col1, FurnitureID=col2 即 1187 引用的值, LcName=col12, LcDesc=col13）。

**i18n 表查询页签陷阱**（2026-06-05）：`gsheet_query.py` 只读 GSheet 当前 "selected" 页签。`1011_x2_i18n` 有 54 个页签，当前 selected 常是 backup 页签（如 `EVENT_backup_dropkey_20260601`）——**线上事件文案真源在 `EVENT` 页签**（gid 550403607），各品类有专属页签(ITEM/BUILDING/MENU/EVENT…)。查 i18n 不能信 gsheet_query 默认页签，要用 `gsheet_utils.get_values(SID,'EVENT','B1:D20000')` 指定页签复核；SID=`1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg`。家具模型 LcName/LcDesc 与 item lc_name 可能是不同 key（如墙纸 item=labor_2026_wall_1_title 齐、模型=labor_2026_wall_decoration_2 缺），换皮要两边都查。

**头像框(avatar_frame=1142)换皮链路**（2026-06-05 拓荒头像框踩坑）：
- 框体视觉 = `DisplayKey` 列指向的 DK 的 **HeadFrame type**（不是单独字段）；`display_order` 列实际填的是**绑定的解锁道具 item id**；`unlock_cost` 也指该道具。
- item 表(1111)侧：头像框道具 class=`avatar_frame`，`CategoryParam.effect` 内 `{"typ":"avatar_frame","id":<frameid>}` + `UseLabels`=`["<frameid>"]` 双处引用 frame id；item 自身 `DisplayKey`=背包图标。改 frame 要同步改这三处 + 新建 1142 条目。
- ⚠️**节日复制残留高频坑**：新节日头像框道具常整列复制上一节日，导致**发的是旧节日的 frame id**（如拓荒道具 111111325 发占星 frame 11422002）。且同一 frame id 被新旧两个节日道具**共享**——直接改它的 DisplayKey 会误伤旧节日，必须**新建独立 frame 条目**再让新道具改指，旧的不动。
- DK 侧：一张图被错挂成 HeadFrame 占了某 key，要独立时给环形图**新建 key**(全局max+1)建 HeadFrame+Icon，从原 key 移除错挂条目；详见 [[X2 DK 录入正确链路]]。
- 🏷️ **头像框"本地化没包装"真因=i18n key 在但值是占位词，不是 key 缺失（2026-06-09 拓荒头像框）**：头像框 item(1111) `lc_name` 指 `LC_EVENT_{节日}_avatar_title`，换皮时这个 key **常被建出来但译文填的是通用占位「头像框 / Avatar Frame」**(没填主题名)→ 游戏显示没包装的通用名(不是显示原始键值)。修法=**UPDATE 该 i18n 行的 18 语言**为主题名(对标占星 `astro_2025_avatar_title`="星海漫游/Galactic Wanderer";拓荒填"拓荒先驱/Frontier Trailblazer",沿用节日装饰命名调性)，不是新建 key。`lc_desc`=`LC_MENU_forever`(永久)**是头像框设计常态**(占星 item 也这样)、不用主题化。⚠️ **诊断坑**：① x2-localization skill 的 `all_existing_keys.json` 索引**会过期**(本次报 `labor_2026_avatar_title` NOT_FOUND,实际 GSheet EVENT 行 7364 早有)→查 key 存在性/译文必**实读 GSheet** 别只信索引;② **普通框+Wonder 框(如 111111325/327)常共用同一 `lc_name` key**→改一处两个都变(要各自独立名才需新建 key)。i18n 行 UPDATE 用 `update_range C{行}:T{行}`(18语言=C..T列),行号先 `get_values B{行}` 验 ID 再写。

**行军特效(marching_effect=1365)换皮残留坑（2026-06-09 X2-43085「节日BP行军特效未替换」沉淀）**：节日新行军特效道具(1111, class=`marching_effect`)常**整批从上个节日道具直接拷、只改了 lc_name/comment 文案，视觉字段没换**，表现=游戏里显示**旧节日的拖尾特效+旧图标**（报告常写"仍是旧版XX特效，时长1d"）。两处必改、全静默：
- ① `category_param.effect` 内 `{"typ":"marching_effect","id":<1365id>}` 的 **id** —— 决定实际拖尾特效。换皮极易残留指上个节日 1365 行（拓荒 111111345-349/321 全指占星 `13650128`，应指拓荒 `13650130`）。⚠️ `val` 是时长(ms: 1d=86400000/3d/7d/14d/30d, 永久=-1)、`vm` 是消耗值，**只换 effect id，val/vm 原样保留**。
- ② item 自身 `display_key`(col6/G) = 背包&BP面板图标，也常残留旧节日图标(占星1511020871→拓荒应 15119315，与对应 1365 行 display_key 一致)。
- 🔑 **bug 不在 2131/BP 表**：2131 的 FreeRewards/PayRewards 早已换成本节日道具 id，问题在道具定义层(1111)——**换成哪个本节日行军道具都没用，因为整批 6 个都坏**。改法=在 1111 批量 repoint，2131 不动。
- **正确节日 1365 行怎么找**：`gsheet_query.py search 1365 <节日中文名>`（如"拓荒"→13650130「行军特效-高级-拓荒节」，其 `items` 列=该节日全部时长变体道具 id）。节日行军特效常**复用上上代视觉**(拓荒 13650130 复用 2024 淘金 effect_key 15120705/display_key 15119315)，正常。
- **换皮校验法**：节日新行军道具的 `category_param.marching_effect.id` 必须 = `search 1365 <节日>` 出的那行 id、且 `display_key` = 该 1365 行的 display_key；对照上个节日同系道具(占星 1d=11119498) 字段是否被原样拷来。同理适用 chat_skin/map_emoji 等其它 cosmetic 道具的 effect-id 残留。

**🛑 X2-43088 结案更正（2026-06-10，下面整段诊断方向被实战推翻，先读这条）**：这单**真因是配置侧没配全**（客户端/美术那边发现并处理），**不是**下面写的客户端资源/meta 问题。我一路扎进 png/meta/spriteMode/打包白名单全是带偏方向、白忙。**教训：报"新表情不显示"时，"配置全不全"和"客户端资源"两条线要并行查、且优先回去问报单人/美术有没有配套配置没配**，别一看是图就认定纯客户端问题。下面的客户端链路知识本身没错（可留作参考），但**它不是 43088 的根因**。另外结论反复（撕裂图≠空格子那套占位图分流）也没能定位真因，说明光靠客户端侧推断不够，要拿到「到底哪张配置表没配」才算闭环——具体表号待用户补。
- ⚙️ **最终结论(2026-06-10 用户拍板)：`11800011` 这个表情本身没问题(动态原版就是好的)，真正显示出错的是「另一个」表情(具体 id 用户未告)**。我对 11800011 做的所有改动(改 256 单帧静态等)最终**全部撤销/删除**、三分支(dev_festival/master_bugfix/pioneer)均还原成 1024 多帧原版。**别再把 11800011 当问题表情**——下次类似单先确认到底是哪个 emoji id 坏再动手。(裁单帧静态那套技术上能跑，但这单根本不需要、是空忙。)
- 🧨 **x2client(D:\UGit\x2client) git 操作两大坑(43088 实摔)**：① **`master_bugfix` 是受保护分支，禁止直接 push**(`pre-receive hook declined: not allowed to push to protected branches`)——资产要进 master_bugfix 必须走 **feature 分支 + MR**(或 cherry-pick)，日志里全是 `Merge branch 'cherry-pick-xxx' into master_bugfix`。② **用户/Unity 会在你操作中途切分支、且 Unity 常自动改一堆 `.mat`(材质重序列化)挂在工作区**——我就因此把 commit 误落到 `fix/pioneer-...` 分支、还把它 rebase 乱了。**铁律：x2client 每次 `git add/commit/rebase/push` 前先 `git branch --show-current` 卡一道；push 只显式 `git add` 自己那几个文件(别 -A，躲开 .mat)；rebase 前若工作区有 .mat 先 `git stash -u`、完事 `git stash pop`；落错了用 `git reset --hard origin/<该分支>` 还原(远端没被 push 污染时这招干净)**。③ **GitLab MR API 到 master_bugfix 目标稳定报 `500 Internal Server Error`(2026-06-10 实测，project id=3254)，但 target=dev 返 201 正常**——master_bugfix 走 cherry-pick 合并、常规 MR 被服务端挡。正解：feature 分支 push 后**给用户预填 Web MR 链接手动建**(`/-/merge_requests/new?merge_request[source_branch]=<分支>&merge_request[target_branch]=master_bugfix`)或 cherry-pick；**别用 API POST 探测不同 target(会误建到 dev 的 MR)**，且 token `can_merge=false`/无删 MR 权限(只能 PUT `state_event=close`)。④ **`Ctrl+Shift+E` 会顺带刷 `Path_UIPrefab.asset` 等别人遗留条目**(本次 5 行无关改动)→commit 前逐个 `git status`，无关的 `git checkout -- <file>` 排除，只 add 自己那套(Display_Icon/IconBg + Path_Icon/IconBg + png + meta)。

**🔑 x2 配置仓(x2gdconf)单行改 = 「下载全表→git checkout HEAD 还原→精确改单行」最干净(2026-06-10 改 item 111111326 display_key 实做)**：① x2gdconf 的 `master_bugfix` **不受保护**(可直接 commit+push，与 x2client 相反)。② 单行/单格改别走 merge_rows(LF 炸全表)：`fwcli googlexlsx -f <表> → xlsxtojson -g all → s2ctool` 下载全表后 `git diff --stat`——若夹带了**他人在 GSheet 改的其它行**(本次除目标行外还夹带 3 行 11119555-557 试用打造队列)，**`git checkout HEAD -- <tsv>` 整体还原，再用 python 按 id 定位精确改目标行那一列**(`f=ln.split(b'\t'); f[col]=新值`，保留 CRLF 用 `wb`/`split(b'\n')`)→ diff 只剩 1 行。③ **x2gdconf 只跟踪 `fo/config/*.tsv`**(json/s2c 是构建期再生、未入 git，磁盘上夹带的旧数据不进提交、无害)，commit 只需 `git add fo/config/<表>.tsv`。④ 改前 GSheet 真源若已是新值(本次用户已手改 display_key→1511094121)，直接改 tsv 这行**不会被下次导表冲掉**(GSheet 一致)。⑤ 提交前 `python scripts/check_tsv_format.py <tsv> --no-xref` 过一遍。

**地图/行军表情(map_emoji=1180)显示链路 + 新表情"不显示/占位图"诊断（2026-06-09 X2-43088，⚠️见上方更正：非本单真因，仅参考）**：注意这是**纯客户端资源链路、无 DisplayKey 列、不归配表**——报"新表情显示不出来"先别只查客户端，配置侧也要查。
- **表 1180 map_emoji**：SID 用 `resolve 1180`；列=`id/constant/comment/unlock_requirement/lc_name/lc_desc/emoji_type/last_time/priority/access_group`，**没有 DisplayKey**。id 在 col[1]。节日新表情接最大值(如拓荒=11800011 `map_emoji_prospect`)。`access_group` 指 1168 获取途径(见 §三 X2-43086)。
- 🏷️ **表情/外显道具「本地化没填/显示空」第三种成因=i18n 整行缺失（2026-06-10 拓荒 map_emoji_prospect）**：前两种已记(头像框=key在但值是占位词；marching_effect=指错旧节日id)。这次 1180 的 11800011 `lc_name={"typ":"lc","txt":"LC_ITEM_map_emoji_x2_prospect"}`/`lc_desc=..._desc`，配置对得上，但 **`1011_x2_i18n` 的 ITEM 页签里根本没有 `map_emoji_x2_prospect` 这行**(stripped key=去掉 `LC_ITEM_` 前缀)→游戏显示空。`LC_<TAB>_<id>` 必须在对应 TAB 页签有行才能解析；缺=**新增行(`gsheet_utils.append_rows_safe(SID,'ITEM',rows,id_col='B')`，1011 不备份)**，不是 update。诊断:实读 ITEM 页签按 stripped key 找(`get_values(SID,'ITEM','A1:T100000')` 扫 col B)——有=改值/查占位词，无=补行。🔑 **补行前必先「全页签搜该 key」——官方译文常已存在、只是被错填进别的页签**：本次 ITEM 缺行，但 **EVENT 页签早有 `map_emoji_x2_prospect`=「淘金热/GOLD RUSH」全 18 语言齐全的官方文案**(`LC_<TAB>_<id>` 里 TAB 不同=不同 key,EVENT 那条配置根本没引用=孤儿)。真因=**译文当初错填进 EVENT 页签、配置要的是 LC_ITEM**→错配显示空。正解=**把那套官方文案复制进 ITEM 行(`update_range C{行}:T{行}` 整段搬 18 语言)**,别自己另写一套(会和设计好的文案分叉)。判别:导出后 grep `fo/i18n/<lang>.tsv` 看同名 `<id>` 出现在哪些 `<TAB>_` 前缀下,有完整异 TAB 版=搬过来复用。i18n SID=`1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg`，列序 `ID_int,ID,cn,en,fr,de,po,zh,id,th,sp,ru,tr,vi,it,pl,ar,jp,kr,cns`(20列,cns=cn备份)。⚠️ **x2-localization-translator skill 的缓存索引当前损坏**(`check_duplicates.py` 报 JSON 错、`lookup_tm.py` 报 MemoryError)→查重/TM 复用全崩，只能实读 GSheet 绕过；下次本地化前先 `scan_all_keys.py`/`build_translation_memory.py` 重建。
- **资源按 config id 命名**（不是 constant、不是 DK）：客户端 `UIHelperCommon.SetEmojiMultiSprites`(渲染入口 `UIEmojiHudHelper.RenderEmojiListItem`)先找 spine `Assets/P2/Res/Emoji/Hud/{id}.prefab`→没有→走帧动画 `Hud/{id}.png`(加载成 `MultipleSprite`)→**两者都缺/Exists=false→替换成 `Emoji/emojiEmpty.png`(灰底撕裂照片占位图)**。`UIEmojiResRoot=Assets/P2/Res/Emoji/`。
- ⚠️ **X2 实际所有地图表情都退化走静态单帧 png**：spine 路径找 `{id}.prefab` 但库里 P2 残留的都是 `{id}_p2.prefab`(及 `Hud/{节日}/` 下 .skel.bytes spine)，X2 代码找不到 → 全部回退到 `Hud/{id}.png`。所以**正确规格 = 256×256 单帧 sprite(spriteMode 1)**，跟 11800001~010 一致；X2 没有会动的地图表情(spine 没接线)。
- 🔑 **两种"不显示"要分清(决定查哪)**：① **格子里是撕裂照片图(emojiEmpty)** = 资源运行期 Exists=false = 资源没打进客户端包/构建未含/LFS 没拉 → 查打包、重 build/热更；② **格子正常边框但角色区整个空白(无撕裂图)** = 资源在、但 `MultipleSprite` 加载出 **0 帧** → 查 .meta。X2-43088 是第②种。
- 🔴 **X2-43088 真因 = .meta 多帧子资源没烤好**：新表情 11800011 被美术做成 **1024×1024 十六帧 sheet(spriteMode 2)**（全表唯一一个多帧），png 本身合法、alpha 真透明、16 帧 256px 切帧 rect 也对，但 **`.meta` 顶层 `internalIDToNameTable` 是空 `[]`**（多帧子资源「内部ID↔帧名」绑定表没生成）→ 运行期 `LoadResource<MultipleSprite>` 解析出 0 帧 → 表情区空白。**对照正常多帧表情(聊天 1525000/010/020, spriteMode 2)其 `internalIDToNameTable` 都非空**(classID 213→帧名)。单帧表情该表空[]无所谓(11800010 空也正常)——**空 internalIDToNameTable 只对多帧致命**。典型成因=meta 脚本批量生成/旧格式拷贝/没经 Unity Sprite Editor 正经切片 Apply。
- **校验法**：新表情 png 若 `spriteMode:2`，其 meta `internalIDToNameTable` 必须非空(用 Unity Sprite Editor 切片 Apply 后才会烤出来)；**最稳=直接导成 256×256 单帧静态(spriteMode 1)** 跟其它 10 个一致。假透明用差分法另查([[transparent-asset-diff-check]])，本例 alpha 正常非假透明。
- ⚠️ **教训**：报"显示异常"别急着下"客户端没打包"结论——先看占位图是撕裂图(缺包)还是空格子(meta/加载)，再据此分流，否则会错路由给出包侧。
- ✅ **修复配方（X2-43088 实做，多帧动图→单帧静态，程序不兼容动图时用）**：① PIL 从 sheet 裁一帧最有代表性的(`Image.open(sheet).crop((x,y,x+256,y+256)).save('{id}.png')`，Unity 帧坐标 y 是 bottom-up→PIL `py=1024-uy-256`)；② meta 直接拷一个正常单帧表情(如 `11800010.png.meta`)、只 `re.sub('guid: ...', 本图原 guid)` 换回原 GUID(避免断引用)——**单帧不需要 Unity 重导入**(单帧 meta `internalIDToNameTable: []` 本就空、合法)；③ `git add`(png 自动转 LFS 指针) → commit(msg 带 `X2-43088`) → push `dev_festival` → **资源类改动必须重打客户端包 QA 才能验**。验收法：`diff` 新 meta 与 11800010 应**仅 GUID 不同**。
- 🧩 **X2 客户端「打包白名单」机制（资源能不能加载的总闸，X2-43088 排查暴露）**：X2 不是把工程里所有资源都打进包——`client/Assets/Editor/BuildConfig/BuildConfigCommon.asset`(+ `BundleConfigFTE.asset`/`x2/TFWConfig/BuildConfig/BundleConfig.asset`) 里有一份 **filters 白名单**(`- path: <目录> / filter: '*.png;*.prefab;...' / abname: <bundle名>`)。**不在白名单的资源运行期被 `ResourceMgr` 直接拒载**，控制台报 `[BuildConfigValidator] 资源"X"不在打包配置中，手机端无法加载此资源` + `[ResourceMgr] Failed to load ...`。表情走 `- path: Assets/P2/Res/Emoji / filter:'*.png;...' / abname: p2.emoji.ab`(整个 Emoji 目录 glob，新增 png 自动覆盖、无需手加白名单)。
- 🔑 **「散图按路径加载」≠「随便加个文件就能加载」**：地图表情虽不进 SpriteAtlas(散图)，但仍被打进 bundle `p2.emoji.ab`。所以**改/加散图后，单纯重开游戏/重进 Play 若走旧 bundle 还是看不到**——必须**重打对应 bundle(或全量 build/热更)**；编辑器 AssetDatabase 模式才是 Reimport 即可。**新资源加载失败先 grep `BuildConfigCommon.asset` 看路径在不在白名单 filter 覆盖内**(在=只差重打包；不在=要先加 filter 再打)。

## 四、追踪链（每层引用都要追到新行）
```
2112
 ├── components.task    → 2115 → fincond 内含 2013 ID
 ├── components.package → 2135 → col3 → 2011 → (2011.actv_id 反指 2112; 2013.config_id → 2011)
 ├── components.jump_link/task_group/weekly_pay_ratio → 2121 → reward → 1111(自选箱再追 category_param.select_box)
 └── show_hud → 换新 ID
```
**间接引用必查（不在 2112 components 里，换皮必栽）**：
- 2121 行内 JSON：`expr`(wonder_egg_drop→2124)、`status`(discount→2011)、`array`(task_group→2115)
- 2011 行内 JSON：`iap_status.drop`(随机礼包→2124)
- 1111 行内 JSON：`category_param`(金蛋→2124、周卡解锁→2013)
- 2122 累充排名：`score_rule.ids` 必须含当前节日**全部** 2011 ID（每新增 2011 都要加）
- 跨表同步：2011 ID 变→改 2013.config_id + 2135.iap；2112 ID 变→改 2011.actv_id + 2135.condition.actvstart.id

**礼包名"邮件显示键值/没本地化"定位法（2026-06-09 X2-42984 自选周卡邮件露 key 实战）**：购买礼包后发奖邮件正文露原始 `LC_IAP_xxx` = 该 pkg_title key 在 i18n 缺失。定位=① 在 `D:\UGit\x2gdconf` `grep -rn "<key去LC_IAP_前缀>" fo/config/iap_template.tsv` 找哪些礼包行引用它(pkg_title 列)；② `grep "<key>" fo/i18n/en.tsv` 确认 i18n 真没有 → 缺失就在 IAP 页签新建(append_rows_safe 或 appendDimension+update_range，IAP gid=741746194)。🔴 **Jira 单引用的 raw key 可能拼错**(X2-42984 报 `LC_IAP_sic_time_card_all_pkg`，配置里实为 **`sci_`**=科技节，sic 是报单人手误)→**照字面新建会建错 key**。铁律：先 grep 精确 key，**零引用就 fuzzy 搜**(`grep -rohE "[a-z]+_time_card_all_pkg"`)找真 key 再建。礼包名直接用报单标题里的叫法(本次"节日周卡礼包/Festival Weekly Card Pack"，周卡=Weekly Card)。

**改"礼包标题文案"定位（2026-06-08 挖矿礼包"基金冲刺→产量飙升"实战）**：礼包**显示标题 = `iap_template`(2013) 的 `pkg_title` 列**(GSheet 真源 G 列，值=`LC_IAP_<key>`)。⚠️别被这两个同名字段骗到——`iap_config`(2011) 的 `paywall_tab` 列 / `iap_order`(2021) 的 `tab_name` 列常**复用同一个 title-key 字符串当内部分组标识**(无 LC_ 前缀)，**不显示、改标题时别动**(动了破坏付费墙分组)。改一个礼包标题而不连累共享同 key 的其它礼包：① 先 `lookup_tm.py "新文案"` 查 i18n 有没有**现成全译且未被引用的 key**(本次 `metro_special_event_title`=产量飙升 18 语言齐、grep 配置零引用→直接复用，省新建+机翻)；② 把该礼包 `iap_template.pkg_title` 改指它(GSheet 真源改→行筛选导表)。共享 key 的其它礼包不动即不受影响。i18n key 可能多份同值(本次"基金冲刺"有 `metro_special_title`/`metro_special_title_no_use`/`211200048` 三个)，必按"谁被 config 引用"认活跃那个、别改废弃的。
- 🛑 **纠错(2026-06-09 X2-43072「礼包页签标题没换完」续集)**：上面说 `2021.tab_name`/`2011.paywall_tab`「不显示、别动」**是错的**——`iap_order`(2021) 的 `A_STR_tab_name` 列**确实会渲染成礼包界面的页签 tab 标题**(2011.paywall_tab 才是不显示的内部分组指针)。所以**改礼包标题文案是「两处」不是「一处」**：① `2013.pkg_title`=礼包大标题(显示标题)；② `2021.tab_name`=礼包页签 tab 标题。只改 ① 会留下「条件名/大标题=新文案，但页签 tab 还是旧文案」的不一致(=本单 BUG)。换标题 checklist：2013.pkg_title + 2021.tab_name 同步改指新 key，建议 2011.paywall_tab 也一并对齐(分组指针,不显示但留旧 key 是隐患)。本单：挖矿产量礼包 tab_name 真源=2021 行 `20211044`.A_STR_tab_name(SID `1r4-MvDK4KAb9nc_7AHhRSwyKAEd7ND7Q3AYymsl38vM`,页签 `iap_order(master)`)，2011 四行 `2011230001/2/4/6`.paywall_tab。
- 🛑 **i18n 页签纠错**：`metro_special_*` 这批挖矿礼包文案 key 实际在 `1011_x2_i18n` 的 **`IAP` 页签**(gid 741746194)，**不在 `EVENT` 页签**(§三 i18n 页签陷阱那条把它写成 EVENT 是错的)。礼包/IAP 类文案查 IAP 页签，活动事件类才查 EVENT。

**BP集结/基金通行证(event_bp_buy_number_bp)换皮必fork购买包 + "已购买"真正判定（2026-06-08 拓荒"默认已购买/查不到礼包"踩坑，含改错字段教训）**：
- 🔑 **客户端 ground truth（x2client `LIAPGrowthFundManager.cs`+`ActivityGrowthInvestmentModule.cs`）**：节日基金"已购买" = `ActvBoughtFunc = () => iap == null || iap.CounterLeft <= 0`，`iap = LIAPShopMgr.GetPackageByTemplateId(IapCfgID)`，`IapCfgID => m_Module.iapCfg`(服务端下发)。**包找不到(iap==null)就直接判已购买**——"默认已购买"和"查不到礼包"是同一个因：基金指向的 2013 包没被加载成"当前可售活动包"。
- 🔑 **iapCfg 真源 = 活动 components 里「付费 task_group」的 `arg2`(col H)**（comment="节日BP集结奖励-付费"），**不是** actv_growth_invest 组件的 arg2（次要/包装字段，改它无效）。三件套=task_group(免费,arg2=0)+task_group(付费,arg2=2013包id)+actv_growth_invest。⚠️ 第一次只改 actv_growth_invest.arg2 = 白改。
- ⚠️ 换皮时付费 task_group.arg2 **整列复制不改**——拓荒付费组件 `212101139`.arg2 与占星 `212101108`.arg2 都=占星包 `2013920101`（且 array 共用同批 2115 quest 2115114010-019）。占星下线后 `GetPackageByTemplateId(2013920101)` 因包绑的占星活动下线→返 null→**全员默认已购买+查不到礼包**。
- 正解=**fork 独立 2011+2013 包**（新 2011 `time_info.actv_id`=本节日在线活动；新 2013 `config_id`→新 2011）+ **付费 task_group.arg2 改指新 2013**（actv_growth_invest.arg2 一并改保持一致）。占星旧包不动。
- 自检：付费 task_group.arg2 → 2013 → 2011 这条链 `time_info.actv_id` 必须=当前在线本节日活动；出现已下线活动=包必 null=已购买 bug。改完**必须部署/热载到测试服**(导表 push git ≠ 服务器生效)才能验。

**节日自选周卡(fes_weekly_card)「购买后剩余可领取天数=0/领取置灰」必检（2026-06-09 X2-43099 沉淀，活动 21127366）**：自选周卡有**两类 2013**，换皮极易只建一类：
- 链路：活动 components 的 `package`(2135) → `iap`(2011, `function=fes_weekly_card`,`time_info={"time_card":{"duration":604800}}`=7天) → `2013` **购买模板**(config_id=2011那档, `temp_type=fes_weekly_card`)；购买模板的 template_id 又挂一套 **2024 iap_custom_chest**(每日自选坑位)。
- 🔑 **真正的「周卡本体/可领天数」= `item_subscription` 道具(1111, class=`item_subscription`)**，其 `category_param.effect=[{"typ":"item_subscription","id":<2013 id>}]` 指一个 2013 模板。客户端/服务端靠这个 2013 算可领天数+每日自选；**2013 不存在 → 算不出 → 剩余天数=0、领取按钮置灰**(=本单 bug)。
- 🔑 **占星(正常)模式 = 订阅道具与购买共用同一个 2013**：解锁-1(111111310)→2013920107(=29.99 购买模板 config_id 2011920102)，解锁-2→...108(19.99)，解锁-3→...109(9.99)。一个 2013 同时是购买模板+订阅领取模板+2024坑位的key，三位一体。
- 🪤 **换皮高频坑**：拓荒新建了订阅道具 111111342/343/344(拓荒解锁-1/2/3)，但把 category_param 的 2013 id **从占星 2013920107/108/109 改号成 2013930107/108/109(920→930)却没建那些 2013 行**(`gsheet_query row 2013 <id>`=not found)。**正解 ≠ 新建 2013**，而是**让订阅道具指回本节日已存在的购买模板**(拓荒 29.99=2013920150/19.99=2013920151/9.99=2013920152)——它们已带 2024 坑位，复用即天数+自选全对(回到占星三位一体)。49.99 是 discount 档无订阅道具。
- **校验法**：① `search 1111 自选周卡解锁` 找本节日订阅道具；② 逐个 `row 1111 <id>` 取 category_param 的 item_subscription id；③ `row 2013 <那个id>` 必须存在且 config_id=本节日对应价位的 2011 iap；不存在/指旧节日=bug。改 1111 的 S 列(col18=category_param) 即可，写后复查。

**经典 BP 通行证(ActivityBattlePass=2130/2131)解锁+领奖链 ground truth（2026-06-08 拓荒"解锁了没法领奖"排查，客户端 `ActivityBattlePass.cs`）**：
- 🔑 **PaidTyp 枚举**：`Free=0, Luxury=1(初级付费档), Collection=2(高级付费档)`。`PaidType => m_Data.payTyp`（**服务端下发**）。领奖判定(3档模式)：Free 到等级就领；Luxury 奖励需 `payTyp>=1`；Collection 需 `payTyp>=2`。领奖是 `BattlePassGetRewardReq`→**服务端校验**。
- 🔑 **payTyp 怎么翻**：服务端在玩家**消耗 `2130.QualityUpItem`** 时置位——`QualityUpItem=[初级道具, 高级道具]`，索引0→Luxury(1)，索引1→Collection(2)。所以「买初级包→IAP发QualityUpItem[0]→消耗→payTyp=1→Luxury档奖励解锁」。
- **全链路对齐点**（换皮任一处错=领不了奖，且都静默）：① `2013` IAP 的 `other_items` 发的通行证道具 == `2130.QualityUpItem` 对应档；② `2131(ActivityBattlePassLevel)` 按 `BpID=2130.Id` 配各级 `FreeRewards/PayRewards(Luxury)/PayRewards2(Collection)`；③ 2131 里所有奖励道具 id 必须在 `1111` 真存在；④ BP 升级经验来自 IAP 发的 `xp` 货币(如 11161002)，**不是** `2130.LevelUpItem`(那是 battle_pass_exp 类的手动加经验道具)；2130 任务列(DailyTaskIDs 等)常全空时，升级全靠 IAP 的 xp。
- ⚠️ **「解锁了(买到包)但付费档奖励领不了」= payTyp 没翻 = 服务端 QualityUpItem 没对上**。改完 2013/2130 后若仍复现，**先怀疑没部署到测试服**（`push git ≠ 服务器生效`，X2 配置要 x2-kadmin 构建+部署+重开活动），而不是再改配置——本次根因就是 2013 修复只 push 没部署，服务端仍发旧道具。2130/2131 原换皮时已部署(活动能跑就说明)，唯独后补的 2013 改动卡在 git。

## 四点五、2111 活动日历(activity_calendar) — 换皮必补、KB 旧版漏写的一环（2026-06-09 拓荒节踩坑）
换皮只配 2112 活动配置**还不够**：每个 2112 活动必须在 **2111 activity_calendar** 注册一行(或多行)日历，否则活动**不进排期、游戏里不显示**。这是 2112/2115/2135 链路之外的独立一环，旧 KB 完全没提。
- **2111 解析**：`resolve 2111` → SID `1x-kAjIEox-JX_CQffEVw1shKZZlUpxR_fe0flTz2Iuk`。⚠️ 有 11 个页签，**`（线上）`(gid 1459407900,最左=导表源) 与 `（QA）`(gid 681415886) 基本同步**，两个都要写；resolve 默认命中 `（线上）`。还有 `master`/`弃用`/各联盟战 等干扰页签别碰。
- **列(10)**：`[0]fwcli_name(空) [1]Id(日历行id,2111xxxxx) [2]ActvCfgID(=2112活动id) [3]ActvComment [4]Schema [5]Trigger [6]Times [7]ActvGroup [8]DataCrossType [9]CountryUseType`。Id 现已进 9 位 `21111xxxx` 段，2026-06 时 maxId=211110575,新行顺延。
- **怎么填**：2112 每行有 `base_activity_id`(col6) 指模板活动→照搬该模板在 2111 的日历行,只换 Id/ActvCfgID/ActvComment。**但最省事的是直接套同源节日整块**——2026拓荒=占星节换皮,占星-2026 日历块(line1812-1833)统一格式 `Schema={"typ":"schema","id":[1,2,3,4,5,6]}` + `Trigger={"typ":"time","is_ark":1}` + `Times={}` + `DCT=2 CUT=0`,逐行换 cfgid+comment 即可。
- **盖不住的特例**：① wonder砸金蛋 schema 含金蛋档 `[1,2,3,4,5,6,13,14,15,16,17]`(占星21127302)；② 掉落转付费/BP礼包 若沿用 base 的 `Trigger:activity_start` 依赖,val 要重映射到本节日主活动/BP(占星则直接 time,is_ark 不依赖,更省)；③ 合成小游戏(base 21121618) Times=`{"fcastdur":"-24h","actvdur":"96h","closedur":"24h"}`,别套占星空 Times。
- ⚠️ 老式(2023/24)日历=`schema:[0]`+短 Id(21115xxx)；新式(占星/夏日2025起)=多 schema `[1-6]`+afcutc/time+Times 有 fcastdur,Id 进 21111xxxx 段。换皮跟当前同源节日的式样,别混。
- **导表落点特殊（2026-06-09 实测）**：2111 导表**不落 `fo/config/`**——fwcli `googlexlsx -f 2111`→`xlsxtojson`→`s2ctool` 后只改 `fo/json/ActivityCalendar.tsv`(PascalCase) + `.json`(+cfgData);`cn/config/activity_calendar.tsv` 和 `Gen/tsv/` 是另一套不被 fo 管道触动。fwcli 必须在 `D:\UGit\x2gdconf` 下跑(找 credentials.json)。⚠️ **merge_rows.py 行筛选对这表失效**：它找 `A_INT_id` 表头列,而 ActivityCalendar.tsv 表头是 `fwcli_name/Id/ActvCfgID...`(无 A_INT_id)→fallback 到 col0 错列。验范围只能靠 `git -c core.autocrlf=false diff fo/json/ActivityCalendar.tsv`。
- ⚠️ **2111 tsv 长期不重导→落后线上一大截(2026-06-09)**：本次导拓荒,full download 带出的不止 22 拓荒行,还有 9 个占星行(211110567-575,占星上线后从没导过表)+1 行收藏品盲盒机 actv_periods 被改。即「整张表漏导」(见 §二同名坑)。所以 2111 重导前要 git diff 看带出多少非本次行,跟用户确认「只导本次festival行还是整表同步」,别把别人未验证改动夹进festival commit。

**gacha累计任务「活动说明弹窗露 {0}」换皮坑（2026-06-10 X2-43105 沉淀）**：节日 gacha 累计任务活动(2112, const `event_{节日}_reward_gacha`, base=夏日 211200129)的 `A_MAP_description`(col10/K)=`{"rule":"<key>"}` 是活动说明弹窗文案。⚠️换皮极易把 rule 误指到**任务描述 key** `LC_EVENT_{节日}_gacha_task_desc`——该 key 文案含 `<color=#308f16>{0}</color>` 占位符，**专给任务列表用**(2115 activity_task 每档引用它时带 `{"lc":"...","args":[N]}` 由 args 填 {0}=10/100/.../1400)；活动说明弹窗**裸引用 key 无 args→{0} 字面露出**=bug。正解=rule 必须指**专属静态 rule key**(母版夏日=`summer_2025_gahca_task_title_rule`="活动期间参与{活动}消耗道具达次数奖励后即可领取大礼"、**不含{0}**)。修法:① i18n 新建 `{节日}_gacha_task_title_rule`(套母版静态文案,18语言;母版活动名 key 存全大写但 rule 正文用 Title Case,ru/pl 名有语法变格、po/sp 冠词性别需按译者改,别机械替换)② 2112 该行 K 列改指它。校验:任何带 `{0}` 的 i18n 只能被「有 args 的引用方」(2115 task)用,弹窗/说明类裸引用必须用无占位符的 key。

**节日 BP/通行证「活动说明弹窗空/露占位」补配（2026-06-10 X2-43113 沉淀，两种空法）**：节日有多个 BP 类活动，rule(`A_MAP_description` col10/K)各自独立、换皮常漏配，且有**两种不同的空**：
- ① **集结通行证(基金)** = `event_{节日}_bp_buy_number_bp`(拓荒 21127363, base=占星 21127350)：rule = `{}` **完全空**，且**母版占星本身也是 `{}`**(从没配过)→ 需**新建** rule key。机制=全服集结式，进度由**购买通行证人数**推进(类周年幸运星"全服购买人数")；组件=task_group免费+task_group付费(arg2=2013包)+actv_growth_invest。
- ② **经典BP** = `{节日}_labor_festival_bp`(拓荒 21127375, ActivityBattlePass 2130/2131)：rule **已指 key**(`labor_2026_bp_rule`)但该 **key 值只是占位标题**"拓荒节通行证规则"(非规则正文)→ 同样"标题有正文空"→ 需**改 key 的值**(rule 字段不动)。
- 🔑 **经典BP 规则复用占星母版(`astro_2025_bp_rule`)替换的 3 坑**：(a) 母版规则里经验道具/礼盒的**行内译法 ≠ 道具 key 值**(en 帧"Observation Star" vs 道具 key"Stargazing Orbs")→按各语言帧逐条精确替换,别拿 key 值 find；(b) **解锁档名按节日变**——占星="经典/豪华占星礼盒",拓荒是 **"拓荒节初级/高级通行证"**(Pass 不是礼盒, `{节日}_bp_unlock_name_normal/classic`),经验道具拓荒=**墨水盒**(`{节日}_bp_EVENT_title`,非旧版纪念钻头)；ru/ar/pl 礼盒名变格/异形→机械替换残留,按各语言帧改写；(c) 🪤 **真换行 vs 字面 `\n`**：i18n 单元格必须**字面 `\n`**,真换行破坏 tsv；中文硬编码串写脚本极易混入真换行→写前校验 `s.count(chr(10))==0`。
- ⚠️ **cns.tsv 是子集**：部分 EVENT key(如各节日 BP rule)**不在 fo/i18n/cns.tsv**,改既有 key 时 cns replace 0 命中→脚本要"replace-or-append"幂等,别 assert==1 崩(X2-43113 踩到)。

## 五、X2 拓荒节 gacha 内外圈结构（2026, 活动 21127381 = const event_labor_gacha_2026）
- **外圈**：2124 drop（资源轮）
- **内圈**：multi_gacha(2121) + **不放回两段奖池**(2141, 按 activity ID 关联、不在 components 里) → 奖励组(2142)
  - 第1段 `21410117` = `[{group:606, wgt:5000}]`（纯资源 group606）
  - 第2段 `21410118` = `[{group:606, wgt:9500},{group:607, wgt:500}]`，保底 interval=7
  - 消耗道具 = 内圈道具 `111111316`
- 2142：**group 606 = 资源**（8项养成/资源），**group 607 = 皮肤**（item `111111322` 永久皮肤, special_reward=1）
- ⚠️ 已确认 SheetID（实测可直接用）：2141 `1YKhyxqfyR3ywIYM8JdeHGvJUX1iXv2nP7ZbwEluMeNI` / 2142 `1GxDhto0jjrV-WC9GCyq6jjqImkFlzKKyLm-xNRmXos0`（页签「activity_without_gacha_reward（天赋投放活动）」）——**其余表别背，一律 resolve**

## 五点五、合成小游戏(metro_minigame_actv)排行榜链路（2026-06-05 排行榜排查沉淀）
「合成小游戏」= **`metro_minigame_actv`**（地铁/合成挂机小游戏），主活动 2112 id=21121501「合成小游戏活动1-拓荒节-schema2」(+schema2 变体 21121502)。components 全貌：
```
2112(metro_minigame_actv)
 ├ rank → 2122 排行榜规则（id=21221197「合成小游戏活动排行榜」）
 │        ├ score_rule.cat → 1014 statistical_data 计数器（101412126「合成小游戏-个人本周获得积分」，每+1计1分）
 │        └ rank_components(=147) → **2118 group 列**=该榜奖励档位(7档:1/2/3/4-10/11-20/21-50/51-100)
 ├ metro_minigame_actv → 3510 小游戏本体(关卡/Plan，id=35101201/02)
 ├ retake×N → 2137(科研药水兑换，21371044/45)
 └ metro_minigame_actv_rewards_show → 2121 活动页奖励展示(id=21211975, status列=展示图标)
```
⚠️**易错点（实测）**：
- **`rewards_show`(2121.status) 是「活动页独立宣传位」，本就不必等于 rank 实发奖励(2118 group)——两者对不上≠bug，别误判去对齐**（2026-06-08 制作人确认：周常版21211975/节日版21211976展示同一组固定宣传item，与榜单实发不同属设计如此）。榜单面板档位奖励直接读 2118，display 永远=实发、不可能不一致。玩家若报「奖励数据不对」，优先查的是**数值 vs 策划案**，不是 showcase。
- 2122 的 `section_lc`/`rank_title` 常留上一活动的文案 key。⚠️ 更正旧说法：`LC_EVENT_sport_person_rank` **不是运动会残留**——周年庆/登月/Plan 版所有挖矿榜都共用这个 key，是标准共享文案，别误判去改。
- rank 的奖励档位真正落在 **2118 的 `Group` 列 = 2122.rank_components 的值**（不是 rank id），追奖励先按 Group 过滤。
- ⚠️**挖矿排行榜奖励历来不主题化（X2-42998 沉淀）**：拓荒挖矿榜 rank 21221197→Group **147**，7 档（1/2/3/4-10/11-20/**21-50/51-100**，row 1181-1187，奖励列 `A_ARR_reward`），**与周年庆 Group 167 逐字节相同**——历史上每个节日的挖矿榜都照抄同一套**通用系统道具**奖励，从不换节日主题道具。所以报「排行榜奖励未更换」多半**不是配置 bug 是设计如此**，先确认是否真要主题化（属新增设计非换皮）。SheetID `1bAwu8A-N4j0Wub6wQQ2AImeB958gSaWV-XdU87k8u60`；⚠️`resolve 2118` 默认指 `_bak_*` 备份页签，**真源 = gid 0 `activity_rank_rewards`**。
- ⚠️**`11112030` 装饰券是 P2 血统死道具（X2 无装饰券系统）**：通用挖矿榜奖励里带它，但 X2 没有可消耗它的装饰券系统、付费价值表里也无美金单价=玩家拿到无处用=无效奖励。换皮/巡检遇到要替换成 X2 有效道具。其余 3 件 `11141013`(挖矿药水rss,小游戏内生)/`11116007`(英雄经验5万)/`11111105`(60分加速) 是有效系统道具。

**合成小游戏等级/段位系统（CActivityMetroGrade = 表 2160 activity_metro_grade，2026-06-08 schema3「缺少等级配置」排查沉淀）**：
- 从 24 科技节起，合成小游戏新增**分段位玩法**：一个节日拆 schema3/4/5 三档（普通/精英/冠军），由 2121 的 `metro_minigame_actv_grade_type` 组件分组（如 26拓荒 212101360，`array`=[三个2112活动id]，三个活动 components 都挂同一个 grade 组件）。
- 服务端 `CActivityMetroGrade.FindInValues(el => el.ActvGrade==level && m_GradeTyp==el.ActvType)` → 表 **2160** 按 `(ActvGrade, ActvType)` 两键查行，查不到返回 null → 报「**缺少等级配置**」。
- 🔑 **ActvType 来源 = grade 组件(2121)的 `arg1`**：0=常规、1=节日…13=24感恩节，每个新节日 +1（26拓荒=**14**）。2160 表每个 ActvType 配 3 行（ActvGrade 3普通/2精英/1冠军）。
- 2160 字段：除 `RankRule`(指 2122 该节日 3 条段位榜规则:普通→grade3/精英→grade2/冠军→grade1) 按节日变，其余全表固定：`LcName`=LC_METRO_actv_grade_name3/2/1；`GradeUpRank/DownRank`= grade3:10/0、grade2:15/16、grade1:0/11。2122 的「加积分用」(末位+1)不进 2160，是活动自己的 rank 组件。
- ⚠️ **节日换皮必检**：建了 grade 组件(arg1=新type)+ 2122 段位榜规则后，**极易漏在 2160 补这 3 行**(全静默,进游戏才报「缺少等级配置」)。查法：读 2160 看最大 ActvType，新节日 type 应 = 上个+1 且有 3 行。SheetID `1lRtb3fvHMvjb9FIPdE5ns4Y12mbxB9quD8O6IM7VfqQ`。

**合成小游戏「变现层」三类礼包 + X2 长期缺配（2026-06-08 对比 P2 沉淀）**：小游戏主活动(节日版 21127352-354 等)的 `components` 除 rank/grade/minigame/retake 外，P2 从 **24科技节(sci25)起**加了一整层变现组件，**X2 一直没跟着搬**——节日小游戏换皮时极易整层漏配（X2 拓荒 21127352-354 三档变现组件全空）。三类礼包归属：
- **特权礼包 = `player_recharge_progress` 组件**（累充特权进度，内嵌在小游戏 components 里，P2 拓荒挂 6 个 `21219272-276/278`）→ 背后是表 **2169 ActivityPrestigeProgressbar**（按累充额度 ProgressLvRequirement 发 Rewards，GroupID 分批次）。X2 表 2169 本身有(别的活动在用)，但小游戏没引用。
- **连锁礼包 = 独立 2112 活动 `event_metro_chain_pack`(id 21127136)**，**不在小游戏 components 里**，靠 `building≥5` 与小游戏同期出；内含一长串 `package`(2135) 链。⚠️ 两边同 id 21127136 但 X2 停在「沙滩节版」23 包(`21352370-392`)、P2 已 reskin「拓荒节版」29 包(多 `21359456-461`)→ X2 该连锁礼包**没换皮到当前节日**。
- **砍价礼包 = `package×6` 组件**（P2 拓荒 `21358524-529`，2135「节日挖矿-砍价礼包」原价+5档折扣，挂在小游戏 components 里）。**X2 设计上不配此类属正常**(2026-06-08 用户确认)，缺它不是 bug。
- retake 也配套：P2 拓荒小游戏挂 4 个 retake(`21371044/045/324/325`)，X2 只 2 个(`044/045`)，补特权层时一起补。
- 链路追法：`gsheet_query.py row 2112_x2_activity_config <小游戏活动id>` 看 components → 缺 `player_recharge_progress`=无特权礼包；连锁礼包另查 `search 2112_x2_activity_config metro_chain_pack` 看是否 reskin 到当前节日。

**合成小游戏 drop(3514) 换产出物必改 3 列（2026-06-09 X2-43069 改产出沉淀）**：单个 drop 行的奖励物分散在 3 列，换产出 item 要**三列一起改**才一致：
- `A_MAP_drop`(col5/F)=**实际发放**（`args` 里 typ=item/rss/vm）；`A_ARR_challenge_reward`(col6/G)=**挑战难度档位的额外奖励**（多档 `tivs`，常含同一 item，纯矿这列可能空、通宝/资源矿才有）；`C_ARR_reward_show`(col7/H)=**奖励预览图标**（val 多为0仅展示，且可能填的是另一个近似 item id 如 11116208 而非实发 id）。
- ⚠️ 只改 drop 列会漏：challenge_reward 仍发旧物、reward_show 仍显示旧图标。换产出物先 `get_values A:I` 把 F/G/H 全扫，逐列替换旧 item id。X2-43069 把英雄碎片 11116258→抽卡券 11116402：13 纯碎片矿只 F 列有；2 通宝矿(35142708/712) F+G+H 三列都有。
- 这些 drop **跨节日共享**（同一 35142xxx 被拓荒 + 其它"活动关卡4x_x"复用），直接改会连带改其它活动；要隔离须 fork 新 drop + 改 3516 关卡 tile 的 drop 指向。改前先扫该 drop 被哪些关卡引用。
- 3514 默认页签 `metro_minigame_rock_drop`(gid 1350351111)就是最左/导表真源，可直接改（不像 3510/3518 真源在 festival view 页签）。

**合成小游戏挖矿地图 DK 必检（2026-06-09 X2-43069「英雄碎片矿挖完没掉落」排查沉淀）**：
- 挖矿地图关卡配在 **3516 metro_minigame_level**：`level_design`(col2,plan0) / `level_design_b`(col3,plan1) 是格子布局 JSON，每格 `{"unit":3513id,"displaykey":DKid(可选覆盖),"drop":3514id}`；`hero_in_mine`(col8) 配英雄碎片矿。**拓荒节实际跑 design_b = plan1**（commit「补 design_b」为证）。
- 格子视觉 DK 两个来源都必须在客户端注册：① 格子自带 `displaykey` 覆盖值；② 该格 drop(3514) 的 `display_key` 列里对应 plan 的 displayKey。注册位置 = `D:\UGit\x2client\client\Assets\P2\Editor\DisplayKey\Display_MinigamePrefab.asset`（存成 `"key":<id>`,类型 MinigamePrefab）。
- ⚠️ **缺 DK 表现 = 挖完矿没掉落/矿石不消失/无奖励**（不一定 panic,客户端找不到 prefab）。X2-43069 即此类：拓荒全 11 关(351610821~852) BP积分矿(drop 35143801/02/04/05)的 tile displaykey **151104356/357/363 在客户端及 x2client 所有分支都没建过**。英雄碎片矿 DK 15115659 反而是好的——排查先确认 QA 截图那格到底哪类矿,别对错位置。
- **审计法（换皮后必跑）**：① 正则抓 `Display_*.asset` 的 `"key":(\d+)` 建客户端 DK 全集；② 解析 3516 节日关卡 design/design_b JSON 收集每格 displaykey + drop plan1 display_key；③ 求差集列缺失 DK,交程序在 Display_MinigamePrefab 补建（走 [[X2 DK 录入正确链路]]）。

**合成小游戏「通关解锁科研」必检（2026-06-09「弹窗显示解锁新科研但通关后没解锁」沉淀）**：
- 科研系统：表 **3518 metro_minigame_research**（`Id`col1=科研等级行如351811701/702/703；`ResearchId`col2=科研组id如3518117，关卡引用的是这个 col2）。关卡(3516)三个字段触发解锁：`research_mineshaft_actv`(col9,挖矿井解锁)/`research_checkpoint_actv`(col10,通关检查点)/`research_exitdoor`(col7,通关大门)，值=`{"坐标":[{"typ":"metro_minigame_research","id":<ResearchId>}]}`。
- 🔑 **解锁的硬门 = 该 ResearchId 必须在所属 schema 活动(3510)的 `research`(col8) 池里**。关卡说"通关解锁X"→弹窗照配置显示"解锁新科研"，但 X 不在活动 research 池 → 科研树无此节点 → **通关后实际解锁不了**（科研本体3518配得再全也没用）。
- ⚠️ **reskin 高频坑**：复制活动时 `research` 数组没拷全，漏掉部分关卡的通关解锁科研。本次拓荒 3 schema(35103322/422/522,池完全相同)漏了 3518119/123/126(833/842/841 的 checkpoint/exitdoor 解锁项)。
- **校验法**：收集所有节日关卡的 research_checkpoint_actv+research_exitdoor 的 ResearchId → 必须全部 ∈ 该 schema 的 3510.research 数组（mineshaft 解锁项同理）。3518 默认页签是「69万圣节」非真源，导表认 `metro_minigame_research`(gid 1350351111)，查具体科研走 fo tsv（col2=ResearchId）别信 GSheet 默认页签。
- ⚠️ **矿井"新科研"显示≠实发，且会重复（2026-06-09 X2-43069「最后一关元素都显示新科研但未获得」沉淀）**：矿井(mineshaft)的"破旧物资箱"奖励里的「新科研」——**显示**源自矿井 production 表 **3515 `C_ARR_research_id`(col12)**，**实发**靠关卡 `research_mineshaft_actv[坐标]`。矿种科研(3518101-115)只能解锁一次，但**后段关卡的矿井常重复映射到早已解锁的矿种**（拓荒中段831-833 就把矿种全解锁完，841-852 全是重复）→ 最后几关每个矿井都显示"新科研"实则已拥有=未获得。① 校验：按播放顺序(group 82→83→84→85)每矿种只首关卡发、后续重复应清。② 清法=清关卡侧 `research_mineshaft_actv` 重复坐标(本次清 841坐标76/842坐标266,220/843,851,852全清)。③ ⚠️ **production.research_id(显示) 跨关共享**(如矿井351528001被833+852共用)，清关卡侧实发后显示可能仍亮→治本要客户端判玩家已拥有再决定显不显示。④ 节日关卡(3516,名"6月X节关卡")是**节日专属**(只被本节日 group/schema 引用)，清它安全；但 drop(35142xxx)是跨节日共享通用配置，区别对待。

**本族表查询坑（gsheet_query 必加修正）**：
- 🔴 **`gsheet_query` 报的「row N」≠ 表格真实行号，少 1（2026-06-09 X2-43094 差点改坏邻行）**：`row <id>` 输出的 `row N` 是它内部数组下标，**比 GSheet A1 真实行号少 1**（实测 212101146 报 row 2339，真实在 2340；2339 是相邻的 212101145）。**严禁拿这个 N 直接拼 A1 range 写单元格**——会写到上一行、覆盖邻行数据。**写前铁律**：先 `get_values(SID,TAB,'B<起>:B<止>')` 读 id 列、按 B 值匹配定位真实行号再写；写后必 `get_values` 复查目标格 + 邻行 id 没被动。本次信了 row 2339 改了 212101145(flash_sale_buy_duration) 的 E/H，幸而 get_values 复查 B 列发现 id 不对、及时回滚(原值 reward=[]/arg2=0)。⚠️ `backup_tab` 偶发返 False(本次)，别只靠它兜底。
- **2122**：id 在 **col[2]**（col[1]=group），工具会误判「P2 table」自动移到 col[1] 查不到 → 必加 `--id-col 2`。
- **2118**：默认 selected 页签常是备份 `_bak_*`，**线上真源 = `activity_rank_rewards`(gid 0)**；且 X2 导表只读首页签，备份页签置顶=雷，用前先确认页签顺序。
- **3510**：`metro_minigame_activity_group` 页签里 **id 在 col[0]**；表内有大量 `_线上问题`/`已合` 历史页签，真源认 `metro_minigame_activity_group`。

**外显「获取途径/Go 按钮」链路 = 表 1168 get_access_group（2026-06-09 X2-43086「行军特效未配置获取途径」沉淀）**：
- 外显物（行军特效/主城皮肤/头像框/装饰/铭牌等）在背包或预览里点底部「Go」弹出「在哪获取」，数据全读 **1168 get_access_group**（SheetID `1h41LnADf4B6iuCRHvbc-NaTMyH892IzAPF_5j1jbPZc`，页签 `get_access_group`）。**没配/配错 → 弹窗 "There are currently no ways available to obtain XXX."**
- 表头：`A_INT_id`(行键) / `S_STR_comment` / `C_STR_item_label`(固定串"item") / `C_INT_asset_id`(★**真正的外显物 item id 在这列**，如行军特效=`1365xxxx`、主城皮肤=`1312xxxx`、装饰=`111111xxx`) / `C_ARR_access_group`(产出来源数组 `[{"id":11531xxx,"args":["来源id"]}]`,11531 是「来源类型」字典：**181=活动产出**(args=2112活动id,最常见) / **230=集卡册**(args=1108册id)) / `C_MAP_lc_name` / `C_MAP_label_name` / `C_INT_DisplayKey`。前 6 行(0-5)是 fwcli 头(p2_title/Id/INT/template/group/check)，数据从第 7 行起。
- 🔑 **来源类型决定 args 指什么**：`11531181`(活动产出)→args 填 2112 活动 id；`11531230`(集卡册)→args 填 1108 册 id。换皮残留常表现为「源类型对但 args 是旧节日的」**或**「源类型都错」——2026-06-09 拓荒节-柜台(row636/id11684604,asset111111356)access 残留 `[{"id":11531181,"args":["211200077"]}]`(沙滩节柜台活动,源类型也错成活动)，而它本应同占星柜台走集卡册=`[{"id":11531230,"args":["11081004"]}]`(拓荒传奇册,集齐总奖=柜台356)。判据：① 看同件上一节日(占星柜台 11684549)的源类型；② lc_name 已是 `LC_EVENT_card_book_title_2_get_access`(通过集卡册获取)却配活动源=自相矛盾=必走集卡册。装饰柜台/集卡册集齐奖类外显物走 230,普通活动产出走 181。
- 🔄 **反向背离坑（2026-06-09 柜台续，「导表」前必查 tsv HEAD）**：常规假设是「GSheet 真源对、tsv 滞后→导表刷 tsv」，但**前一会话可能只改了 tsv 并 commit/push、没同步 GSheet 真源**，造成**反向背离：tsv(HEAD)对、GSheet 错**。本次柜台 tsv 636 行早在 commit `5c3d8b979`(20:45)就已是正确集卡册值并 push，GSheet 却还停在沙滩节残留——我改 GSheet 是把真源拉回跟 tsv 一致，对 tsv 是**零-diff no-op**。⚠️ 这种情形下若 naive 跑**全表导**，会用 GSheet 上的残留/他人未验证改动**反向覆盖已正确的 tsv**（即 §二「整表漏导/夹带」反方向）。**铁律：收到「导表」先 `git show HEAD:fo/config/<表>.tsv | sed -n '<行>p'` 看 tsv HEAD 是否已是目标值 + `git status -sb` 看是否已 push**；若 tsv 已对且已 push，则不需导表，缺的是构建/部署(x2-kadmin)或客户端更新，别盲目全表导。背离可能任一方向，导表前两边都验。
- 客户端按 **item_label** 查这张表拿来源；s2ctool **按 `A_INT_id` 建 map**，所以 id 必须全表唯一。
- ⚠️ **节日换皮必检（新外显物必须在 1168 加一行 access_group，且 id 接最大值递增）**：行军特效一路是 `116841xx`+item_label `1365010x~13650130`，每个节日皮肤一行指向产出它的活动。
- 🔴 **重复主键坑（X2-43086 真因）**：2026 拓荒节新增的一批外显行 **id 没递增、连撞 5 对**（11684594/596/597/598/599 各 2 行）。`A_INT_id` 重复 → s2ctool 建表时一条吞另一条 → 被吞那条的获取途径整条丢失 → 报 "no ways to obtain"。行军特效-拓荒(13650130) 跟头像框撞 11684598 被吞即此 bug。**导前必跑重复 id 扫描**（`Counter(r[1])`），有重复先在 GSheet 把后出现的行重排到全表 max+1 起的唯一 id 再导，否则格式校验「ID 重复」会拦 / 推坏配置上服。
- 🔴 **「对得上号」深层核对（2026-06-09 X2-43086 续，比结构检查更重要）**：换皮新外显行常是**整行从上个节日 copy**，结构（唯一 id/格式）全对、但**值仍是上个节日残留**——且残留藏在两处：① `access_group` 的活动/集卡册 id 仍指上个节日（占星 211200214 gacha / 11081003 占星奇遇册 等）；② **连 `item_label` 道具本身都是上个节日的**（本次 11684595「主城皮肤-拓荒」item_label=13121047 竟是占星城皮肤，真拓荒城皮肤是 13121050）。**核对法**：逐行把 access 的活动 id 丢进 `gsheet_query.py row 2112_x2_activity_config <id>` 看 comment/constant 是不是本节日(labor_2026)；集卡册 id 丢 `row 1108 <id> --id-col 1` 看是不是本节日册；item_label 丢对应外显表(1312城皮肤/1365行军特效/1142头像框…)确认 lc_name 是本节日。拓荒真活动段：大富翁21127364/BP21127375/装饰礼包21127384/gacha21127381/累充21127380；拓荒集卡册=11081004拓荒传奇(非11081003占星奇遇)。
- ⚠️ **别导用户还在改的表**：本次先导了一版(094bc5427)，用户随后又在 GSheet 改了 6 行 access 值 → 推上去的成了过时值，得重导。导表前确认用户已改完定稿，或改完立即重导，别中途抢导。

## 六、关联
- 换皮全流程（S0命中→S1-S5→写入checklist→案例沉淀）：`C:\Users\linkang\.claude\skills\p2-x2-reskin\SKILL.md`
- 写回 QA 表 / 导表：`C:\ADHD_agent\.cursor\rules\x2-gsheet.mdc`
- [[配置表知识库路径]]（⚠️那份是 **P2**，只借结构不借 SheetID）、[[X2 养成线付费价值手册]]、[[X2 DK 录入正确链路]]、[[X2 主城皮肤换皮完整链路]]
