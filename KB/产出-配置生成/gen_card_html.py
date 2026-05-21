import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>X2_2026拓荒节_集卡册 配置预览</title>
<style>
body { font-family: 'Segoe UI', Arial, sans-serif; background:#1a1a2e; color:#e0e0e0; margin:0; padding:20px; }
h1 { color:#ffd700; border-bottom:2px solid #ffd700; padding-bottom:8px; }
h2 { color:#87ceeb; margin-top:30px; border-left:4px solid #87ceeb; padding-left:10px; }
h3 { color:#98fb98; margin-top:20px; }
table { border-collapse:collapse; width:100%; margin:10px 0 20px 0; font-size:13px; }
th { background:#2d2d5e; color:#ffd700; padding:8px 10px; text-align:left; border:1px solid #444; }
td { padding:6px 10px; border:1px solid #333; vertical-align:top; }
tr:nth-child(even) { background:#1e1e3a; }
tr:hover { background:#2a2a4a; }
.star3 { color:#aaaaaa; }
.star4 { color:#6699ff; }
.star5 { color:#ffd700; font-weight:bold; }
.id { font-family:monospace; color:#98fb98; font-size:12px; }
.lc { font-family:monospace; color:#dda0dd; font-size:11px; }
.dk { font-family:monospace; color:#87ceeb; font-size:11px; }
.json-cell { font-size:11px; font-family:monospace; word-break:break-all; }
.tag { display:inline-block; padding:2px 8px; border-radius:3px; font-size:11px; margin:1px; }
.tag-reward { background:#1a4a2a; border:1px solid #2a7a3a; }
.tag-item { background:#1a2a4a; border:1px solid #2a4a7a; }
.section { background:#16213e; border:1px solid #2d2d5e; border-radius:6px; padding:15px; margin:15px 0; }
.group-card { background:#0f3460; border-radius:8px; padding:12px; margin:8px 0; }
.group-title { font-size:16px; font-weight:bold; color:#ffd700; margin-bottom:8px; }
.stat-box { display:inline-block; background:#2d2d5e; border-radius:4px; padding:3px 10px; margin:2px; font-size:12px; }
.toc a { color:#87ceeb; text-decoration:none; display:block; padding:3px 0; }
.toc a:hover { color:#ffd700; }
</style>
</head>
<body>
<h1>X2 2026拓荒节 集卡册 — 配置预览</h1>
<p style="color:#aaa">生成日期: 2026-05-21 | 总行数: 70行 (1111×3 + 1108×1 + 1107×9 + 1123×54 + 1109×3)</p>

<div class="toc section">
<b>目录</b>
<a href="#sec1111">1111 卡包道具覆盖行（3行）</a>
<a href="#sec1108">1108 CardGallaryBook 新增行（1行）</a>
<a href="#sec1107">1107 CardGallaryGroup 新增行（9组）</a>
<a href="#sec1123">1123 CardGallary 卡片配置（54张）</a>
<a href="#sec1109">1109 CardGallaryStore 商店行（3行）</a>
<a href="#seclc">LC Key 汇总</a>
<a href="#secstat">星级分布统计</a>
</div>

<!-- ====== 1111 ====== -->
<h2 id="sec1111">1111 卡包道具 — 覆盖行（3行）</h2>
<div class="section">
<table>
<tr>
  <th>ID</th><th>名称</th><th>DK</th><th>LC名/描述</th><th>概率分布</th><th>random_add(book)</th>
</tr>
<tr>
  <td class="id">111111339</td>
  <td>拓荒节2026<br>1-2星卡包</td>
  <td class="dk">1511094006</td>
  <td class="lc">LC_EVENT_item_card_pack_name_15<br>LC_EVENT_item_card_pack_desc_15</td>
  <td><span class="star3">★3: 9000</span> / <span class="star4">★4: 1000</span></td>
  <td class="id">11081004</td>
</tr>
<tr>
  <td class="id">111111340</td>
  <td>拓荒节2026<br>1-3星卡包</td>
  <td class="dk">1511094007</td>
  <td class="lc">LC_EVENT_item_card_pack_name_16<br>LC_EVENT_item_card_pack_desc_16</td>
  <td><span class="star3">★3: 8000</span> / <span class="star4">★4: 1300</span> / <span class="star5">★5: 200</span></td>
  <td class="id">11081004</td>
</tr>
<tr>
  <td class="id">111111341</td>
  <td>拓荒节2026<br>2-3星卡包</td>
  <td class="dk">1511094008</td>
  <td class="lc">LC_EVENT_item_card_pack_name_17<br>LC_EVENT_item_card_pack_desc_17</td>
  <td><span class="star4">★4: 9500</span> / <span class="star5">★5: 500</span></td>
  <td class="id">11081004</td>
</tr>
</table>
</div>

<!-- ====== 1108 ====== -->
<h2 id="sec1108">1108 CardGallaryBook — 新增行（1行）</h2>
<div class="section">
<table>
<tr><th>字段</th><th>值</th></tr>
<tr><td>ID</td><td class="id">11081004</td></tr>
<tr><td>名称</td><td>拓荒传奇</td></tr>
<tr><td>GroupID</td><td class="id">11074001 ~ 11074009（9组）</td></tr>
<tr><td>DK封面</td><td class="dk">1511094005（封面）/ 1511094009（开启后）/ 1511094003（底图）/ 1511094004（标题底图）</td></tr>
<tr><td>FX特效</td><td class="dk">1511020681</td></tr>
<tr><td>LC名称</td><td class="lc">LC_EVENT_item_card_book_title_4</td></tr>
<tr><td>LC描述</td><td class="lc">LC_ASSET_card_gallary_desc（通用）</td></tr>
<tr><td>卡包ID</td><td class="id">111111339 / 111111340 / 111111341</td></tr>
<tr><td>完成奖励</td><td>
  <span class="tag tag-item">拓荒节头像框(111111327) ×1</span>
  <span class="tag tag-item">特殊天赋道具(11111082) ×10</span>
  <span class="tag tag-item">宝石升级道具(11111083) ×20</span>
</td></tr>
<tr><td>OpenTime</td><td>[-1,-1]（不限时间）</td></tr>
</table>
</div>

<!-- ====== 1107 ====== -->
<h2 id="sec1107">1107 CardGallaryGroup — 新增行（9组）</h2>
<div class="section">
<table>
<tr>
  <th>ID</th><th>组名</th><th>卡片ID范围</th><th>DK</th><th>LC</th><th>完成奖励(Rewards)</th><th>跟随奖励(RewardsFollow)</th>
</tr>
<tr>
  <td class="id">11074001</td><td>启程准备</td><td class="id">11235001-006</td>
  <td class="dk">1511094010</td>
  <td class="lc">_collection_title_35</td>
  <td><span class="tag tag-item">探测券(11117024)×5</span><span class="tag tag-item">英雄经验(11116402)×5</span></td>
  <td><span class="tag tag-reward">英雄经验×5 + 食物资源×30000</span></td>
</tr>
<tr>
  <td class="id">11074002</td><td>荒野行军</td><td class="id">11235011-016</td>
  <td class="dk">1511094011</td>
  <td class="lc">_collection_title_36</td>
  <td><span class="tag tag-item">探测券(11117024)×5</span><span class="tag tag-item">英雄经验(11116402)×5</span></td>
  <td><span class="tag tag-reward">英雄经验×5 + 食物资源×30000</span></td>
</tr>
<tr>
  <td class="id">11074003</td><td>扎营落脚</td><td class="id">11235021-026</td>
  <td class="dk">1511094012</td>
  <td class="lc">_collection_title_37</td>
  <td><span class="tag tag-item">探测券(11117024)×5</span><span class="tag tag-item">英雄经验(11116402)×5</span></td>
  <td><span class="tag tag-reward">英雄经验×5 + 食物资源×30000</span></td>
</tr>
<tr>
  <td class="id">11074004</td><td>矿脉勘探</td><td class="id">11235031-036</td>
  <td class="dk">1511094013</td>
  <td class="lc">_collection_title_38</td>
  <td><span class="tag tag-item">宝石升级(11111083)×2</span><span class="tag tag-item">橙碎片(11116304)×2</span></td>
  <td><span class="tag tag-reward">英雄经验×5 + 食物资源×30000</span></td>
</tr>
<tr>
  <td class="id">11074005</td><td>河谷淘金</td><td class="id">11235041-046</td>
  <td class="dk">1511094014</td>
  <td class="lc">_collection_title_39</td>
  <td><span class="tag tag-item">宝石升级(11111083)×2</span><span class="tag tag-item">橙碎片(11116304)×2</span></td>
  <td><span class="tag tag-reward">英雄经验×5 + 食物资源×30000</span></td>
</tr>
<tr>
  <td class="id">11074006</td><td>前哨筑城</td><td class="id">11235051-056</td>
  <td class="dk">1511094015</td>
  <td class="lc">_collection_title_40</td>
  <td><span class="tag tag-item">宝石升级(11111083)×2</span><span class="tag tag-item">橙碎片(11116304)×2</span></td>
  <td><span class="tag tag-reward">英雄经验×5 + 食物资源×30000</span></td>
</tr>
<tr>
  <td class="id">11074007</td><td>荒原猎踪</td><td class="id">11235061-066</td>
  <td class="dk">1511094016</td>
  <td class="lc">_collection_title_41</td>
  <td><span class="tag tag-item">宝石升级(11111083)×3</span><span class="tag tag-item">橙碎片(11116304)×3</span></td>
  <td><span class="tag tag-reward">英雄经验×5 + 食物资源×30000</span></td>
</tr>
<tr>
  <td class="id">11074008</td><td>地底秘境</td><td class="id">11235071-076</td>
  <td class="dk">1511094017</td>
  <td class="lc">_collection_title_42</td>
  <td><span class="tag tag-item">宝石升级(11111083)×3</span><span class="tag tag-item">橙碎片(11116304)×3</span></td>
  <td><span class="tag tag-reward">英雄经验×5 + 食物资源×30000</span></td>
</tr>
<tr>
  <td class="id">11074009</td><td>拓荒盛典</td><td class="id">11235081-086</td>
  <td class="dk">1511094018</td>
  <td class="lc">_collection_title_43</td>
  <td><span class="tag tag-item">橙碎片(11116304)×3</span><span class="tag tag-item">头像框(111111327)×1</span></td>
  <td><span class="tag tag-reward">英雄经验×5 + 食物资源×30000</span></td>
</tr>
</table>
<p style="color:#aaa;font-size:12px">BG DK(背景底图): 1511094019 / 1511094020（全9组共用）</p>
</div>

<!-- ====== 1123 ====== -->
<h2 id="sec1123">1123 CardGallary — 卡片配置（54张）</h2>
<div class="section">

"""

groups = [
    ("G1 启程准备", [
        ("11235001", "整理行囊", 3, "309", "1511094021"),
        ("11235002", "晨起伸懒腰", 3, "310", "1511094022"),
        ("11235003", "打扫工坊", 3, "311", "1511094023"),
        ("11235004", "调校日晷", 3, "312", "1511094024"),
        ("11235005", "仰望星河", 3, "313", "1511094025"),
        ("11235006", "指点星图", 3, "314", "1511094026"),
    ]),
    ("G2 荒野行军", [
        ("11235011", "攀岩探路", 3, "315", "1511094027"),
        ("11235012", "涉水渡河", 3, "316", "1511094028"),
        ("11235013", "树下小憩", 3, "317", "1511094029"),
        ("11235014", "雨中赶路", 3, "318", "1511094030"),
        ("11235015", "发现脚印", 3, "319", "1511094031"),
        ("11235016", "悬崖远眺", 4, "320", "1511094032"),
    ]),
    ("G3 扎营落脚", [
        ("11235021", "选址插旗", 3, "321", "1511094033"),
        ("11235022", "搭建帐篷", 3, "322", "1511094034"),
        ("11235023", "挖井取水", 3, "323", "1511094035"),
        ("11235024", "砍伐木材", 3, "324", "1511094036"),
        ("11235025", "升起篝火", 4, "325", "1511094037"),
        ("11235026", "第一顿饭", 4, "326", "1511094038"),
    ]),
    ("G4 矿脉勘探", [
        ("11235031", "采集矿样", 3, "327", "1511094039"),
        ("11235032", "洞口初探", 3, "328", "1511094040"),
        ("11235033", "矿壁采集", 3, "329", "1511094041"),
        ("11235034", "矿车推运", 4, "330", "1511094042"),
        ("11235035", "矿脉闪光", 4, "331", "1511094043"),
        ("11235036", "标记矿脉", 4, "332", "1511094044"),
    ]),
    ("G5 河谷淘金", [
        ("11235041", "河边淘洗", 3, "333", "1511094045"),
        ("11235042", "筛选矿砂", 3, "334", "1511094046"),
        ("11235043", "发现金粒", 4, "335", "1511094047"),
        ("11235044", "搭建水渠", 4, "336", "1511094048"),
        ("11235045", "称量收获", 4, "337", "1511094049"),
        ("11235046", "满载而归", 5, "338", "1511094050"),
    ]),
    ("G6 前哨筑城", [
        ("11235051", "绘制蓝图", 3, "339", "1511094051"),
        ("11235052", "夯实地基", 4, "340", "1511094052"),
        ("11235053", "竖起围墙", 4, "341", "1511094053"),
        ("11235054", "瞭望塔成", 4, "342", "1511094054"),
        ("11235055", "铁匠开炉", 4, "343", "1511094055"),
        ("11235056", "升旗时刻", 5, "344", "1511094056"),
    ]),
    ("G7 荒原猎踪", [
        ("11235061", "追踪足迹", 3, "345", "1511094057"),
        ("11235062", "布置陷阱", 4, "346", "1511094058"),
        ("11235063", "正面对峙", 4, "347", "1511094059"),
        ("11235064", "驯服坐骑", 4, "348", "1511094060"),
        ("11235065", "荒原伙伴", 5, "349", "1511094061"),
        ("11235066", "原野奔驰", 5, "350", "1511094062"),
    ]),
    ("G8 地底秘境", [
        ("11235071", "深渊入口", 4, "351", "1511094063"),
        ("11235072", "水晶密林", 4, "352", "1511094064"),
        ("11235073", "地底暗河", 4, "353", "1511094065"),
        ("11235074", "远古化石", 5, "354", "1511094066"),
        ("11235075", "熔岩之心", 5, "355", "1511094067"),
        ("11235076", "上古宝藏", 5, "356", "1511094068"),
    ]),
    ("G9 拓荒盛典", [
        ("11235081", "丰收集市", 4, "357", "1511094069"),
        ("11235082", "凯旋巡游", 4, "358", "1511094070"),
        ("11235083", "丰饶之宴", 4, "359", "1511094071"),
        ("11235084", "授勋仪式", 5, "360", "1511094072"),
        ("11235085", "烟火之夜", 5, "361", "1511094073"),
        ("11235086", "新世界黎明", 5, "362", "1511094074"),
    ]),
]

star_colors = {3: "star3", 4: "star4", 5: "star5"}
star_labels = {3: "★★★", 4: "★★★★", 5: "★★★★★"}
honor_vals = {3: 100, 4: 200, 5: 400}
recycle_vals = {3: 1, 4: 2, 5: 10}

for group_name, cards in groups:
    html += f'<h3>{group_name}</h3>\n<table>\n'
    html += '<tr><th>卡片ID</th><th>卡名</th><th>星级</th><th>DK(卡面)</th><th>LC Key</th><th>Honor</th><th>Recycle</th><th>首获奖励</th></tr>\n'
    for card_id, card_name, star, lc_num, dk in cards:
        css = star_colors[star]
        stars = star_labels[star]
        honor = honor_vals[star]
        recycle = recycle_vals[star]
        html += f'<tr><td class="id">{card_id}</td>'
        html += f'<td>{card_name}</td>'
        html += f'<td class="{css}">{stars}</td>'
        html += f'<td class="dk">{dk}</td>'
        html += f'<td class="lc">LC_EVENT_item_card_name_{lc_num}</td>'
        html += f'<td>{honor}</td>'
        html += f'<td>{recycle}</td>'
        html += f'<td class="lc">vm:11151001 ×5</td>'
        html += '</tr>\n'
    html += '</table>\n'

html += """
</div>

<!-- ====== 1109 ====== -->
<h2 id="sec1109">1109 CardGallaryStore — 商店行（3行）</h2>
<div class="section">
<table>
<tr>
  <th>ID</th><th>名称</th><th>商品(goods)</th><th>价格(星尘)</th><th>月限</th><th>DisplayOrder</th><th>解锁条件(actvend)</th>
</tr>
<tr>
  <td class="id">11090031</td>
  <td>拓荒节1-2星活动卡包</td>
  <td class="id">111111339</td>
  <td>15</td><td>20</td><td>1011</td>
  <td class="id">21127380（累充活动）</td>
</tr>
<tr>
  <td class="id">11090032</td>
  <td>拓荒节1-3星活动卡包</td>
  <td class="id">111111340</td>
  <td>30</td><td>15</td><td>1012</td>
  <td class="id">21127380（累充活动）</td>
</tr>
<tr>
  <td class="id">11090033</td>
  <td>拓荒节2-3星活动卡包</td>
  <td class="id">111111341</td>
  <td>150</td><td>10</td><td>1013</td>
  <td class="id">21127380（累充活动）</td>
</tr>
</table>
<p style="color:#f0a000;font-size:12px">⚠️ 待确认: 1109 actvend 当前用 21127380（节日累充），需确认是否为正确的解锁活动 ID</p>
</div>

<!-- ====== LC汇总 ====== -->
<h2 id="seclc">LC Key 汇总</h2>
<div class="section">
<h3>卡册/组/卡包 LC Keys</h3>
<table>
<tr><th>LC Key</th><th>用途</th></tr>
<tr><td class="lc">LC_EVENT_item_card_book_title_4</td><td>册名「拓荒传奇」</td></tr>
<tr><td class="lc">LC_EVENT_item_card_collection_title_35</td><td>G1 启程准备</td></tr>
<tr><td class="lc">LC_EVENT_item_card_collection_title_36</td><td>G2 荒野行军</td></tr>
<tr><td class="lc">LC_EVENT_item_card_collection_title_37</td><td>G3 扎营落脚</td></tr>
<tr><td class="lc">LC_EVENT_item_card_collection_title_38</td><td>G4 矿脉勘探</td></tr>
<tr><td class="lc">LC_EVENT_item_card_collection_title_39</td><td>G5 河谷淘金</td></tr>
<tr><td class="lc">LC_EVENT_item_card_collection_title_40</td><td>G6 前哨筑城</td></tr>
<tr><td class="lc">LC_EVENT_item_card_collection_title_41</td><td>G7 荒原猎踪</td></tr>
<tr><td class="lc">LC_EVENT_item_card_collection_title_42</td><td>G8 地底秘境</td></tr>
<tr><td class="lc">LC_EVENT_item_card_collection_title_43</td><td>G9 拓荒盛典</td></tr>
<tr><td class="lc">LC_EVENT_item_card_pack_name_15 / _desc_15</td><td>1-2星卡包 名/描述</td></tr>
<tr><td class="lc">LC_EVENT_item_card_pack_name_16 / _desc_16</td><td>1-3星卡包 名/描述</td></tr>
<tr><td class="lc">LC_EVENT_item_card_pack_name_17 / _desc_17</td><td>2-3星卡包 名/描述</td></tr>
</table>

<h3>54张卡片 LC Keys（LC_EVENT_item_card_name_309 ~ 362）</h3>
<table>
<tr><th>LC Key</th><th>卡名</th><th>LC Key</th><th>卡名</th><th>LC Key</th><th>卡名</th></tr>
"""

all_cards = []
for group_name, cards in groups:
    for card_id, card_name, star, lc_num, dk in cards:
        all_cards.append((lc_num, card_name))

for i in range(0, len(all_cards), 3):
    row = all_cards[i:i+3]
    html += '<tr>'
    for lc_num, card_name in row:
        html += f'<td class="lc">_name_{lc_num}</td><td>{card_name}</td>'
    if len(row) < 3:
        for _ in range(3 - len(row)):
            html += '<td></td><td></td>'
    html += '</tr>\n'

html += """
</table>
</div>

<!-- ====== 统计 ====== -->
<h2 id="secstat">星级分布统计</h2>
<div class="section">
<table>
<tr><th>星级</th><th>数量</th><th>占比</th><th>Honor</th><th>Recycle</th><th>出现组</th></tr>
<tr><td class="star3">★★★ (3星)</td><td>22</td><td>40.7%</td><td>100</td><td>1</td><td>G1~G6各有 3星卡</td></tr>
<tr><td class="star4">★★★★ (4星)</td><td>22</td><td>40.7%</td><td>200</td><td>2</td><td>G2~G9</td></tr>
<tr><td class="star5">★★★★★ (5星)</td><td>10</td><td>18.5%</td><td>400</td><td>10</td><td>G5:1, G6:1, G7:2, G8:3, G9:3</td></tr>
<tr style="background:#2d2d5e"><td><b>合计</b></td><td><b>54</b></td><td>100%</td><td>—</td><td>—</td><td>9组 × 6卡</td></tr>
</table>

<h3>ID 范围汇总</h3>
<table>
<tr><th>表</th><th>ID范围</th><th>行数</th><th>操作类型</th></tr>
<tr><td>1111</td><td>111111339–111111341</td><td>3</td><td style="color:#ffa500">覆盖现有行</td></tr>
<tr><td>1108</td><td>11081004</td><td>1</td><td style="color:#98fb98">新增</td></tr>
<tr><td>1107</td><td>11074001–11074009</td><td>9</td><td style="color:#98fb98">新增</td></tr>
<tr><td>1123</td><td>11235001–11235086（间隔10）</td><td>54</td><td style="color:#98fb98">新增</td></tr>
<tr><td>1109</td><td>11090031–11090033</td><td>3</td><td style="color:#98fb98">新增</td></tr>
</table>

<h3>DK 范围汇总</h3>
<table>
<tr><th>用途</th><th>DK范围</th></tr>
<tr><td>卡包图标</td><td class="dk">1511094006 / 1511094007 / 1511094008</td></tr>
<tr><td>册封面/背景</td><td class="dk">1511094003 / 1511094004 / 1511094005 / 1511094009</td></tr>
<tr><td>FX特效</td><td class="dk">1511020681</td></tr>
<tr><td>组缩略图 G1-G9</td><td class="dk">1511094010–1511094018</td></tr>
<tr><td>组背景底图（共用）</td><td class="dk">1511094019 / 1511094020</td></tr>
<tr><td>通用卡背(所有卡共用)</td><td class="dk">1511094002</td></tr>
<tr><td>卡面 G1(54021-026)</td><td class="dk">1511094021–1511094026</td></tr>
<tr><td>卡面 G2(54027-032)</td><td class="dk">1511094027–1511094032</td></tr>
<tr><td>卡面 G3(54033-038)</td><td class="dk">1511094033–1511094038</td></tr>
<tr><td>卡面 G4(54039-044)</td><td class="dk">1511094039–1511094044</td></tr>
<tr><td>卡面 G5(54045-050)</td><td class="dk">1511094045–1511094050</td></tr>
<tr><td>卡面 G6(54051-056)</td><td class="dk">1511094051–1511094056</td></tr>
<tr><td>卡面 G7(54057-062)</td><td class="dk">1511094057–1511094062</td></tr>
<tr><td>卡面 G8(54063-068)</td><td class="dk">1511094063–1511094068</td></tr>
<tr><td>卡面 G9(54069-074)</td><td class="dk">1511094069–1511094074</td></tr>
</table>
</div>

<p style="color:#666;text-align:center;margin-top:30px">X2 2026拓荒节 集卡册配置预览 | 生成于 2026-05-21</p>
</body>
</html>
"""

with open("C:/ADHD_agent/KB/产出-配置生成/X2_2026拓荒节_集卡册.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML generated successfully.")
