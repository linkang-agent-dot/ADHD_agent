# -*- coding: utf-8 -*-
"""生成自包含 HTML 验证报告（截图 base64 内嵌）。"""
import base64, os

SHOT_DIR = r"E:\333\screenshots"
OUT = r"E:\333\unity验证报告_20260716.html"

def b64(name):
    with open(os.path.join(SHOT_DIR, name), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

shots = {
    "hero_en": b64("L3_hero9037_skill_en_final.png"),
    "hero_kr": b64("L3_hero9037_skill_kr_final.png"),
    "hero_jp": b64("L3_hero9037_skill_jp_final.png"),
    "route_en": b64("L3_route_en.png"),
    "route_kr": b64("L3_route_kr.png"),
    "route_jp": b64("L3_route_jp.png"),
}

html = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>X3 兵种术语统一 · Unity 运行时验证报告 2026-07-16</title>
<style>
:root {
  --bg:#f6f4ef; --card:#fff; --ink:#2a2622; --muted:#7a7268;
  --accent:#8a6d2f; --pass:#2e7d46; --warn:#b26a00; --line:#e5e0d6;
}
@media (prefers-color-scheme: dark) {
  :root { --bg:#181512; --card:#221e19; --ink:#e8e2d8; --muted:#9a917f; --accent:#c9a75a; --pass:#5bbd7f; --warn:#e0a04a; --line:#37312a; }
}
* { box-sizing:border-box; margin:0; padding:0; }
body { background:var(--bg); color:var(--ink); font-family:"Microsoft YaHei",system-ui,sans-serif; line-height:1.75; padding:32px 16px 64px; }
.wrap { max-width:1080px; margin:0 auto; }
h1 { font-size:1.5rem; margin-bottom:4px; }
.sub { color:var(--muted); font-size:.85rem; margin-bottom:24px; }
.verdict { background:var(--card); border-left:6px solid var(--pass); border-radius:8px; padding:18px 22px; margin-bottom:28px; font-size:1.05rem; box-shadow:0 1px 4px rgba(0,0,0,.06); }
.verdict b { color:var(--pass); }
h2 { font-size:1.12rem; margin:34px 0 12px; padding-left:10px; border-left:4px solid var(--accent); }
h3 { font-size:.98rem; margin:20px 0 8px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:16px 20px; margin-bottom:14px; }
table { border-collapse:collapse; width:100%; font-size:.88rem; margin:10px 0; }
th,td { border:1px solid var(--line); padding:7px 10px; text-align:left; vertical-align:top; }
th { background:rgba(138,109,47,.08); font-weight:600; }
.ok { color:var(--pass); font-weight:700; }
.warn { color:var(--warn); font-weight:600; }
code { background:rgba(138,109,47,.1); border-radius:4px; padding:1px 6px; font-family:Consolas,monospace; font-size:.85em; }
.gallery { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:14px; margin:12px 0; }
.shot { background:var(--card); border:1px solid var(--line); border-radius:8px; overflow:hidden; }
.shot img { width:100%; display:block; }
.shot .cap { padding:8px 12px; font-size:.82rem; color:var(--muted); border-top:1px solid var(--line); }
.shot .cap b { color:var(--ink); }
ul { padding-left:22px; }
li { margin:4px 0; }
.note { font-size:.85rem; color:var(--muted); }
.tbl-scroll { overflow-x:auto; }
</style>
</head>
<body>
<div class="wrap">

<h1>X3 兵种术语统一 · Unity 运行时验证报告</h1>
<div class="sub">2026-07-16 · gdconfig dev 三笔 i18n merge（40ef0fc8 / 4e33cd3c / 87045049）· 执行环境：Unity Editor Play 模式 → beta 330（玩家 14511）· DebugUtils + feval 桥全自动</div>

<div class="verdict">✅ <b>PASS</b> —— L1 导表产物断言 <b>47/47</b>、L2 运行时全语言扫描 <b>47/47</b>、回归检查全过、L3 UI 抽查 en/kr/jp 两界面 6 张截图全命中、Console 零 FormatException / 零 i18n 加载失败。</div>

<h2>关键过程发现</h2>
<div class="card">
<b class="warn">客户端一开始吃的是旧表</b>（任务书预警的头号假阴性坐实）：验证开始时客户端 <code>i18n/*.bytes</code> 时间戳虽是当天 16:36，内容却仍是旧值（en 9037 = "Brawler Atk/Def"）——那次导表从 dev_festival 分支跑的，不含本批改动。<br>
处理：从 origin/dev 最新（<code>82203943</code>，含全部三笔 merge）建临时 worktree 重新导表，仅替换 i18n 16 个 bytes + 同步 AllTableDataMd5.txt 对应行（原文件已备份至 <code>E:\\333\\scripts\\backup_client_i18n_original\\</code>），未 commit 任何产物、未触碰 ProtoGen 其他在途改动。替换后客户端断言 47/47 全绿。
</div>

<h2>L1 · 导表产物断言 — PASS 47/47</h2>
<div class="card">
worktree 新导产物（origin/dev@82203943）与替换后客户端实际加载的 bytes <b>各 47/47 ✓</b>。断言脚本：<code>E:\\333\\scripts\\l1_assert.py</code>。
</div>

<h2>L2 · 运行时全语言扫描 — PASS 47/47</h2>
<div class="card">
<div class="note">方法：Play 模式下经 DebugUtils 桥逐语言调 <code>LocalizationMgr.Update(lang)</code>（强制从磁盘现读 bytes）→ <code>Get(key)</code> 断言，不重启 Play；扫完恢复原语言。</div>
<div class="tbl-scroll"><table>
<tr><th>Key</th><th>断言范围</th><th>结果</th></tr>
<tr><td><code>TXT_HeroSkillInfo_NewDescUp_9037</code></td><td>15 语言精确值（含未改 tr/pl）</td><td class="ok">✓ 全过</td></tr>
<tr><td><code>TXT_Route_Name_5000 / _6000</code></td><td>en/it/jp/kr/id 精确值 + en 尾缀 —Warrior</td><td class="ok">✓ 全过</td></tr>
<tr><td><code>TXT_HeroSkillInfo_NewDesc_1043</code></td><td>en/sp/ru/de 含「每间隔1回合」新句式</td><td class="ok">✓ 全过</td></tr>
<tr><td><code>TXT_BuffTemplate_AffixName_220613</code></td><td>fr 以 tous les marins sont des guerriers 结尾</td><td class="ok">✓</td></tr>
<tr><td><code>TXT_ActvOnline_ActvName_100546</code></td><td>ru/ua 精确值</td><td class="ok">✓</td></tr>
<tr><td><code>TXT_MemorialCard_GetTips_60</code></td><td>tw 鬥士營地達到14級可獲取</td><td class="ok">✓</td></tr>
</table></div>
<b>Console/异常</b>：Editor.log 0 条 FormatException、0 条 i18n 加载失败；期望值为精确匹配，<code>{0}</code>/<code>{1}</code>/<code>&lt;color&gt;</code> 完整性随之成立。
</div>

<h2>回归检查（必须没变）— 全 PASS</h2>
<div class="card"><div class="tbl-scroll"><table>
<tr><th>项</th><th>结果</th></tr>
<tr><td>职业标签 <code>Text_Soldier_fighter/hunter/shooter</code> en/kr/jp/id 共 12 项</td><td class="ok">✓ 与拍板基准一致</td></tr>
<tr><td><code>TXT_HeroSkillInfo_NewDesc_1046</code> kr 仍含 광전사、不含 광투사</td><td class="ok">✓ 未误伤</td></tr>
<tr><td><code>TXT_BuffTemplate_AffixName_120023</code> id = Serangan prajurit petarung tunggal</td><td class="ok">✓</td></tr>
<tr><td><code>TXT_HeroLabel_Tip_4</code> git 前后（40ef0fc8^ vs origin/dev）</td><td class="ok">✓ 逐字节一致</td></tr>
<tr><td>Key1 未改语言 tr/pl</td><td class="ok">✓ 精确匹配旧值</td></tr>
</table></div></div>

<h2>L3 · UI 抽查（en/kr/jp × 2 界面）— 全命中</h2>

<h3>① 霍普金斯技能页 · 黑金清算（技能 9037）</h3>
<div class="card">
<ul>
<li><b>en</b>：\"…your <b>Warrior</b> attack and defense are boosted by <b>15%</b> simultaneously\"（不再是 Brawler / activate together）；升级预览 <b>Warrior Atk/Def: +15.3%</b> <span class="ok">✓</span></li>
<li><b>kr</b>：\"부대 <b>투사</b>의 공격과 방어가 15% 동시 발동합니다\"；<b>투사 공/방: +15.3%</b> <span class="ok">✓</span></li>
<li><b>jp</b>：\"部隊の<b>ウォリアー</b>攻撃と防御が15%同時発動\"；<b>ウォリアー攻防: +15.3%</b> <span class="ok">✓</span></li>
<li><code>{0}</code> 全部正常代入、color 标签渲染正常绿色。</li>
</ul>
<div class="gallery">
<div class="shot"><img src="__HERO_EN__" alt="en"><div class="cap"><b>en</b> · Warrior + 15% 代入正常</div></div>
<div class="shot"><img src="__HERO_KR__" alt="kr"><div class="cap"><b>kr</b> · 투사 공/방: +15.3%</div></div>
<div class="shot"><img src="__HERO_JP__" alt="jp"><div class="cap"><b>jp</b> · ウォリアー攻防: +15.3%</div></div>
</div>
<div class="note">⚠️ 取证时发现：技能 9037 是<b>皮肤技能</b>（挂皮肤 103405「黑金契约」，不挂英雄 1034 本体）——技能页要显示它必须先解锁该皮肤。</div>
</div>

<h3>② 航线先锋（Route Pioneer）六路线名</h3>
<div class="card">
<ul>
<li><b>en</b>：<b>Commander Route—Warrior</b>（Fighter 已消失），其余五路线正常 <span class="ok">✓</span></li>
<li><b>kr</b>：<b>지휘관 항로-투사</b> <span class="ok">✓</span>（Wavebreaker—투사 被前景船体遮挡半行，其值已在 L2 精确断言）</li>
<li><b>jp</b>：<b>指揮官航路-ウォリアー</b> / 波砕き航路-ウォリアー <span class="ok">✓</span></li>
</ul>
<div class="gallery">
<div class="shot"><img src="__ROUTE_EN__" alt="en"><div class="cap"><b>en</b> · Commander Route—Warrior</div></div>
<div class="shot"><img src="__ROUTE_KR__" alt="kr"><div class="cap"><b>kr</b> · 지휘관 항로-투사</div></div>
<div class="shot"><img src="__ROUTE_JP__" alt="jp"><div class="cap"><b>jp</b> · 指揮官航路-ウォリアー</div></div>
</div>
<div class="note">顺带观察（非本次改动范围）：kr 的 Wavebreaker 系历史命名不统一（사냥꾼线「파도 가르는 항로」vs 소총수线「파도타기 항로」），如需收敛可另开一笔。</div>
</div>

<h2>现场改动清单</h2>
<div class="card"><div class="tbl-scroll"><table>
<tr><th>位置</th><th>改动</th><th>状态</th></tr>
<tr><td>client <code>ProtoGen/i18n/*.bytes</code> ×16 + md5 清单</td><td>替换为 origin/dev@82203943 导表产物</td><td>保留（测试用，勿 commit；备份在 E:\\333\\scripts\\）</td></tr>
<tr><td>beta 330</td><td>Play_330 + Map_331 部署 tag=dev</td><td class="ok">Run ✓</td></tr>
<tr><td>330 测试号 14511</td><td>GM：addhero 1034 / setheromaxlevel / setallheroesmaxstar / unlockheroskin 103405</td><td>beta 测试服未回滚，已知痕迹</td></tr>
<tr><td>客户端语言/窗口</td><td>验证中切 en/kr/jp、开英雄页与航线页</td><td class="ok">已恢复繁中、窗口已关</td></tr>
<tr><td>临时 worktree <code>C:\\X3\\gdconfig-dev-l1</code></td><td>导表验证用</td><td class="ok">已删除</td></tr>
</table></div></div>

<div class="note" style="margin-top:28px">断言明细/脚本：<code>E:\\333\\scripts\\</code> · Markdown 版：<code>unity验证报告_20260716.md</code> · 改动决策在上游会话，本报告只报结果。</div>

</div>
</body>
</html>
"""

html = (html.replace("__HERO_EN__", shots["hero_en"])
            .replace("__HERO_KR__", shots["hero_kr"])
            .replace("__HERO_JP__", shots["hero_jp"])
            .replace("__ROUTE_EN__", shots["route_en"])
            .replace("__ROUTE_KR__", shots["route_kr"])
            .replace("__ROUTE_JP__", shots["route_jp"]))

tmp = OUT + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(html)
os.replace(tmp, OUT)
print("written:", OUT, os.path.getsize(OUT), "bytes")
