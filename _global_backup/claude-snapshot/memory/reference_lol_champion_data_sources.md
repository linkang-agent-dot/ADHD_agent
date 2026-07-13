---
name: lol-champion-data-sources
description: 查英雄联盟全英雄技能数值的三个数据源与各自的坑（Data Dragon 伤害字段清零，需 CommunityDragon 补）
metadata: 
  node_type: memory
  type: reference
  originSessionId: ff07c402-6c8c-47f3-8ec0-5d837713f9ff
---

# LoL 全英雄技能数值数据源（2026-07 实测）

**需求场景**：拉取英雄联盟全部英雄（当前 173 个）的技能属性数值。

## 三个数据源与分工

1. **Riot Data Dragon（官方，免费无 key，有 zh_CN）** — 骨架层
   - 版本列表：`https://ddragon.leagueoflegends.com/api/versions.json`（取 [0] 即最新，实测 16.13.1）
   - 全量数据：`https://ddragon.leagueoflegends.com/cdn/{ver}/data/zh_CN/championFull.json`
   - 有：英雄基础属性成长、技能冷却/消耗/射程（cooldownBurn/costBurn/rangeBurn，按级列出）、描述文本
   - ⚠️ **坑（实测确认）**：`effect`/`effectBurn` 伤害数值字段全是 0/空——Riot 多年前改服务端下发 tooltip，官方接口只剩占位符。**别指望官方接口拿伤害数**。

2. **CommunityDragon（社区解包）** — 伤害数值层
   - `https://raw.communitydragon.org/latest/game/data/characters/{champ}/{champ}.bin.json`（champ 小写英文名，如 ahri）
   - ⚠️ 路径坑：是 `game/data/characters/`，不是 `game/characters/`（后者 404）
   - 有真实 `BaseDamage` 按技能等级数组 + AP/AD 加成系数（SpellDataValue / mSpellCalculations 结构）
   - 格式是游戏引擎原始 bin 结构，一英雄一文件，需脚本解析

3. **LoL 官方 Wiki**（`wiki.leagueoflegends.com`）— 人工校准层，含隐藏机制；底层有结构化 Lua 数据模块（Module:ChampionData/data）可程序化抓

**推荐组合**：Data Dragon 出英雄列表+冷却消耗，CommunityDragon 逐英雄补伤害与系数。

## 已落地产物（2026-07-08 全量合并版）

- **生成器**：`C:\Users\linkang\Downloads\build_lol_champions_html.py`（主入口：英雄+装备+公式计算器三页签，**全 173 英雄伤害公式实算已合并进英雄页签**，覆盖 615/692 主动技能 + 大部分被动）
- **产物**：`C:\Users\linkang\Downloads\lol_champions.html`（461KB 单文件）
- 全量化两个缺口的解法：①伤害类型=「公式名英文hint → 公式吃的属性 → 技能中文描述『X伤害』字样」三级推断（含治疗盾类）；②展示公式=自动评估该技能全部 mSpellCalculations，过滤条件=(名称含damage/heal/shield等) or (公式吃攻击/法强/目标最大生命)，哈希名{...}公式只被引用不展示
- `build_lol_damage_demo.py` 为 6 英雄打样版（含未启用的实战系数 coef/why），单英雄深挖时用；日常查数用主页面

## bin 解析实测坑（写解析器前必读）

1. **urllib 默认 UA 会被 CommunityDragon 403**，必须带 `User-Agent: Mozilla/5.0`（PowerShell Invoke-WebRequest 不用）。
2. 技能数值字段是 `mSpell.DataValues`（**不是** mDataValues，那个恒为空）；元素结构 `{name/mName, values/mValues, __type:SpellDataValue}`，两种命名都要兼容。
3. **数值数组下标 0 是占位**，真实值取 `[1 : 1+maxrank]`（maxrank 从 DataDragon spells[i].maxrank 拿）。
4. **DataDragon 的 `spells[i].id`（如 AhriQ）≈ bin 里技能脚本名**，可直接精确匹配 + 前缀模糊兜底，实测 173 英雄 692 技能匹配 668 个（96.5%）。
5. AP/AD 加成系数大多在 DataValues 里（如 APRatio），更复杂的公式在 `mSpellCalculations`（本次未解析）。
6. **字段名中文化**：3225 个唯一字段 / 1048 个驼峰词根，用「短语先替换(AoE/PerSecond) → 驼峰拆词 → ~250 词根映射表拼回」方案，生僻专有名词保留原文（映射表在生成器脚本里）。
7. **装备**：DataDragon `item.json`（zh_CN）过滤 `maps['11'] && gold.purchasable`=222 件；⚠️ 其 `stats` 字段不全（缺穿甲/技能急速等），做伤害计算器要用 **Meraki Analytics items.json**（社区维护、结构化字段全）。

## mSpellCalculations 公式解析（期望伤害计算器核心，2026-07 已跑通）

- 打样产物: `Downloads\lol_damage_demo.html` + 生成器 `Downloads\build_lol_damage_demo.py`（6英雄覆盖物理/魔法/真实/混伤/被动/%生命，固定面板600AP/300AD/双抗100/目标3000血已损50%）
- 打样数值 = 面板伤害 → 实际伤害(×减伤)，**按最高值算**（满层单次·全额命中）。实战系数层做过一版后用户拍板取消（2026-07-07）：**系数没法通用，只适合单一英雄分析时用**——评估数据仍留在脚本 DEMO 配置的 coef/why 字段（未渲染），单英雄要用时再启用
- **面板口径（2026-07-07 用户纠正）**：攻击力=各英雄自身18级基础(吃各自成长)+固定装备额外(+200)，**不能定死总值**（会抹掉基础成长高的英雄的优势）；法强无基础值仍固定600。实现=CUR_TOTAL_AD 逐英雄写入
- 每行伤害附**人话公式串**（eval_part/eval_calc 返回 (值,串)）：`= 260 + 110%额外攻击(220)`，随等级项标 `(1~18级 13→30)`，层数标 `×5层`
- ⚠️ **CommunityDragon 会临时不可达**（TLS握手被断/超时，urllib和PowerShell都挂，非客户端问题，实测挂过~10分钟自行恢复）——脚本已内置磁盘缓存（`.lol_cache/` 在脚本同目录，下载成功落盘、失败用缓存兜底），跑批前别删缓存目录
- **改解析器后交付前必抽检**：从缓存取原始 DataValues 手拆一条公式对账（例: 图奇E满层=60+6×35+0.35×6×额外AD，与页面输出核对到个位）；重构前后数字有出入时以手算为准定对错，别默认旧的对
- **属性编号**: `StatBy*Part` 里 `mStat:2`=攻击力（`mStatFormula:2`=额外AD，缺省=总AD）；**不带 mStat = 法强**
- 部件类型: NamedDataValue(查DataValues) / StatByCoefficient(系数×属性) / StatByNamedDataValue(DataValues里的系数×属性) / StatBySubPart / Sum/ProductOfSubParts / Number / ByCharLevelInterpolation(1~18级线性插值) / EffectValue(旧版mEffectAmount按下标) / GameCalculationModified(=另一公式×倍率, tooltipOnly标记仅展示用)
- ⚠️ **公式引用的字段名大小写可能和 DataValues 不一致**（rAPCoefficient vs RAPCoefficient），查找必须大小写不敏感，否则静默得0
- **被动/DoT 的公式在 Marker/被动子技能上**（DariusHemoMarker、TwitchDeadlyVenomMarker），别在主技能名下找；五个打样被动全有公式结构，无需手写
- 追加部件: `ByCharLevelBreakpoints`(1级值+每级增量+断点改增量/一次性加成) / `mSpellCalculationKey`引用其他公式(认字段不认哈希__type) / `GameCalculationConditional`(取 default 分支) / GameCalculation 自带 mMultiplier 要乘
- `mStat:12` = **目标最大生命**（泽德被动%HP）；%生命类公式只出比例(mDisplayAsPercent)
- **百分比伤害呈现口径（2026-07-07 用户拍板）**：不折算默认血量，面板/实际都直接给百分比，减伤同样作用在百分比上（10%最大生命魔法 → 实际5%最大生命）；泽德被动这种公式内部×了目标血量的，除回 TARGET_HP 还原比例（div_hp 标记）
- 伤害类型（物理/魔法/真实）**公式里没有**，在 tooltip/spell标记里，打样为手动标注；全量化需另想办法

## 伤害公式核心结论（2026-07 wiki 核实，做计算器直接用）

- 等级成长：`属性(n) = 基础 + 成长×(n−1)×(0.7025+0.0175×(n−1))`；攻速成长是百分比。
- 技能伤害 = 基础值[技能等级] + Σ(系数×属性)；减伤 = `100/(100+有效抗性)`，负护甲用 `2−100/(100−护甲)`。
- 穿透顺序：固定削减 → %削减 → %穿透 → 固定穿透(穿甲)；**穿甲 V14.1 起 1:1 不随等级**；穿透不能穿到负，削减可以。
- **暴击 V26.01 起从 175% 改回 200%**。攻速 = 基础×(1+额外%)，上限 2.5。
- 完整公式和计算流程已写进产物 HTML 的「伤害公式」页签（第六节=出装算伤害步骤）。
- 页签顶部已内置**简易伤害计算器**（输入面板伤害+目标护甲/魔抗+可选穿透，实时出物理/魔法/真实三种实际伤害与减伤%）；下一步升级方向=选英雄+技能等级+出装自动算（数据都在页面 JSON 里，装备结构化数值需换 Meraki）。
