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
- `2135` X2 默认页签带 `(qa)`；`2142` 页签带后缀「（天赋投放活动）」；`1118` 含「严禁手改」
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
| 掉落转付费 | 2112×3+2116(兑换)+2121(discount→2011) |
| 大富翁 | 2112+2135+2011+2013+2115+2116+2121+2151(地图) |

**X2 集卡册三层结构（2026-06-05 拓荒集卡册改奖励实测）**：Book(1108)→GroupID数组→Group(1107)→CardID数组→Card(1123)，外加 Store(1109)。奖励字段位置：
- **1108 CardGallaryBook**：`Rewards`(col13/N列)=**集齐全部卡组的总奖励**(=「全部卡册收集完成奖励」)；GroupID(col3)挂该册所有卡组；CardPackID(col12)。
- **1107 CardGallaryGroup**：`RewardsFirst`(col10/K列)=单个卡组首次集齐奖励，`RewardsFollow`(col11/L列)=重复集齐奖励。**「最后一个卡册/卡组」=该 Book 的 GroupID 数组里 ID/DisplayOrder 最大的那行**(拓荒=11074009「拓荒盛典」)。
- 1107/1108 两表 **Id 都在 col[1]**(查询须 `--id-col 1`)；两表页签名都叫 `CardGallaryGroup`(Book 表也是这名，非笔误)。
- 拓荒 Book=11081004「拓荒传奇」，9 卡组 11074001~11074009。两个头像框道具：111111325(普通)/111111327(Wonder)；5+装饰 111111350~354 及 111111332「墙饰2」等。

**大富翁节日换皮必检（2026-06-05 拓荒大富翁三礼包 bug 踩坑）**：节日大富翁=占星节模板逐字 reskin，复制时**最易在 2013(iap_template) 模板层漏拷 + 存钱罐组件 pkg id 打错**，三处全静默不报错：
- ① **骰子红包包**(2135 红包49.99/99.99 → 2011 red_pack_pkg → 2013)：2013 里按 `config_id` 极易整组漏建 → 游戏里**整块不显示**。查法 `gsheet_query.py filter 2013 3 <2011的iap_id>`，0 条=漏。
- ② **锚点礼包**(2011 一个 id 对应 2013 **多档** 4.99/9.99/19.99/49.99/99.99)：占星 5 档，拓荒只拷了 49.99/99.99 两档 → **缺低档**。同一 config_id 在 2013 应有 5 行。
- ③ **存钱罐**(2121 type=monopoly_piggy_bank)：`reward` 列 pkg id 易把 `2135213_3_09`(存钱罐通用包) 错写成 `2135213_2_09`(占星抢购包，存在但绑别的活动→**无法购买**)。对照占星 piggy 21217038→213521117 校验。
- 链路：2135.iap→2011.id→2013.config_id；存钱罐 2121.reward→2135→2011→2013。**节日换皮后必按 config_id 在 2013 逐 id 数行数、和占星节同档对齐**。

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

**BP集结/基金通行证(actv_growth_invest)换皮必fork购买包（2026-06-08 拓荒"集结通行证默认已购买"踩坑）**：
- `event_bp_buy_number_bp`(BP集结奖励/基金) 的购买/解锁状态 = `actv_growth_invest` 组件(2121) 的 **`arg2`(col H)** 指向的 2013 包 → 其 config_id 的 2011 包。"已购买"由 2011 包的 **`iap_status`(recharge_actv)** 和 period 购买记录决定。
- ⚠️ 换皮时 invest 组件 `arg2` **极易整列复制上一节日不改**——拓荒 invest `212101140` 与占星 `212101109` arg2 都=占星包 `2013920101`，整条包链(2011920101)的 `time_info.actv_id`、`iap_status` 全绑占星活动+占星累充。结果：**任何在占星节充过值的回流玩家，拓荒活动一开即"已购买"**，无法付费。三层静默不报错。
- 正解=**给新节日 fork 独立 2011+2013 包**（占星 wonder/每日礼包都正确 fork 了，唯独 BP 集结漏）：新 2011 `time_info.actv_id`=本节日活动 + `iap_status` 只留本节日累充 id；新 2013 `config_id`→新 2011；invest 组件 `arg2`→新 2013。占星旧包不动。
- 自检：invest 组件的 arg2 → 2013 → 2011 这条链的 `actv_id`/`iap_status` 累充 id 必须全是**当前节日**的，出现上一节日的累充 id = 没 fork。

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
- 2122 的 `section_lc`/`rank_title` 常留上一活动的文案 key（踩到 `LC_EVENT_sport_person_rank` 运动会残留挂在合成榜上）。
- rank 的奖励档位真正落在 **2118 的 `Group` 列 = 2122.rank_components 的值**（不是 rank id），追奖励先按 Group 过滤。

**合成小游戏等级/段位系统（CActivityMetroGrade = 表 2160 activity_metro_grade，2026-06-08 schema3「缺少等级配置」排查沉淀）**：
- 从 24 科技节起，合成小游戏新增**分段位玩法**：一个节日拆 schema3/4/5 三档（普通/精英/冠军），由 2121 的 `metro_minigame_actv_grade_type` 组件分组（如 26拓荒 212101360，`array`=[三个2112活动id]，三个活动 components 都挂同一个 grade 组件）。
- 服务端 `CActivityMetroGrade.FindInValues(el => el.ActvGrade==level && m_GradeTyp==el.ActvType)` → 表 **2160** 按 `(ActvGrade, ActvType)` 两键查行，查不到返回 null → 报「**缺少等级配置**」。
- 🔑 **ActvType 来源 = grade 组件(2121)的 `arg1`**：0=常规、1=节日…13=24感恩节，每个新节日 +1（26拓荒=**14**）。2160 表每个 ActvType 配 3 行（ActvGrade 3普通/2精英/1冠军）。
- 2160 字段：除 `RankRule`(指 2122 该节日 3 条段位榜规则:普通→grade3/精英→grade2/冠军→grade1) 按节日变，其余全表固定：`LcName`=LC_METRO_actv_grade_name3/2/1；`GradeUpRank/DownRank`= grade3:10/0、grade2:15/16、grade1:0/11。2122 的「加积分用」(末位+1)不进 2160，是活动自己的 rank 组件。
- ⚠️ **节日换皮必检**：建了 grade 组件(arg1=新type)+ 2122 段位榜规则后，**极易漏在 2160 补这 3 行**(全静默,进游戏才报「缺少等级配置」)。查法：读 2160 看最大 ActvType，新节日 type 应 = 上个+1 且有 3 行。SheetID `1lRtb3fvHMvjb9FIPdE5ns4Y12mbxB9quD8O6IM7VfqQ`。

**本族表查询坑（gsheet_query 必加修正）**：
- **2122**：id 在 **col[2]**（col[1]=group），工具会误判「P2 table」自动移到 col[1] 查不到 → 必加 `--id-col 2`。
- **2118**：默认 selected 页签常是备份 `_bak_*`，**线上真源 = `activity_rank_rewards`(gid 0)**；且 X2 导表只读首页签，备份页签置顶=雷，用前先确认页签顺序。
- **3510**：`metro_minigame_activity_group` 页签里 **id 在 col[0]**；表内有大量 `_线上问题`/`已合` 历史页签，真源认 `metro_minigame_activity_group`。

## 六、关联
- 换皮全流程（S0命中→S1-S5→写入checklist→案例沉淀）：`C:\Users\linkang\.claude\skills\p2-x2-reskin\SKILL.md`
- 写回 QA 表 / 导表：`C:\ADHD_agent\.cursor\rules\x2-gsheet.mdc`
- [[配置表知识库路径]]（⚠️那份是 **P2**，只借结构不借 SheetID）、[[X2 养成线付费价值手册]]、[[X2 DK 录入正确链路]]、[[X2 主城皮肤换皮完整链路]]
