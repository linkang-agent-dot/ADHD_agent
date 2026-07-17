# -*- coding: utf-8 -*-
"""从 breed_map.json 生成《幻兽帕鲁1.0_配种图鉴.html》(自包含)
数据编码：三角矩阵 base36 —— 对 (a,b) a<=b 按 k=a*299-a*(a-1)/2+(b-a) 定位，
CHD 字符串 k*2 处 2 字符 = 子代索引(base36)。缺口用 '~~'，多子代(性别特殊)进 SPECIALS。
用法: python -X utf8 breed_build_html.py [输出路径]
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\linkang\Desktop\幻兽帕鲁1.0_攻略合集\幻兽帕鲁1.0_配种图鉴.html'
data = json.load(open(os.path.join(HERE, 'breed_map.json'), encoding='utf-8'))
pals, pairs = data['pals'], data['pairs']
N = len(pals)

def b36(n):
    s = '0123456789abcdefghijklmnopqrstuvwxyz'
    return s[n // 36] + s[n % 36]

# pair -> children
pc = {}
for c, lst in pairs.items():
    c = int(c)
    for a, b in lst:
        pc.setdefault((a, b), []).append(c)

def kidx(a, b):
    return a * N - a * (a - 1) // 2 + (b - a)

total_slots = kidx(N - 1, N - 1) + 1
arr = ['~~'] * total_slots
specials = []   # 性别相关多子代
missing = 0
for a in range(N):
    for b in range(a, N):
        cs = pc.get((a, b))
        if not cs:
            missing += 1
            continue
        cs = sorted(set(cs))
        arr[kidx(a, b)] = b36(cs[0])
        if len(cs) > 1:
            specials.append([a, b, cs])
print(f'pals={N} slots={total_slots} filled={total_slots-missing} missing={missing} multi_child={len(specials)}')

CHD = ''.join(arr)
PALS_JS = json.dumps([[p[1], p[2]] for p in pals], ensure_ascii=False, separators=(',', ':'))
SPECIALS_JS = json.dumps(specials, ensure_ascii=False, separators=(',', ':'))

html = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>幻兽帕鲁1.0 配种图鉴</title>
<style>
:root{--bg:#0d1117;--panel:#161b22;--line:#30363d;--txt:#e6edf3;--dim:#8fa3b8;--faint:#5c7089;--cyan:#56d4dd;--pink:#ff9ade;--amber:#ffcc55;--green:#7ee787;--red:#ff7b72;--mono:Consolas,monospace}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--txt);font-family:'Microsoft YaHei',sans-serif;font-size:15px;line-height:1.7;padding:26px 4vw 60px;max-width:1100px;margin:0 auto}
h1{font-size:26px;margin-bottom:4px}
.sub{color:var(--dim);font-size:13.5px;margin-bottom:18px}
.mech{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 18px;font-size:13.5px;color:var(--dim);margin-bottom:20px;line-height:1.9}
.mech b{color:var(--txt)}
.tabs{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap}
.tab{cursor:pointer;font-weight:700;font-size:14px;padding:9px 18px;border-radius:10px;border:1px solid var(--line);background:var(--panel);color:var(--dim)}
.tab.on{background:var(--cyan);color:#0d1117;border-color:var(--cyan)}
.pane{display:none}.pane.on{display:block}
.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:14px}
input[type=text]{background:var(--panel);border:1px solid var(--line);border-radius:10px;color:var(--txt);padding:9px 14px;font-size:15px;width:230px}
input[type=text]:focus{outline:none;border-color:var(--cyan)}
.big{font-size:20px;font-weight:900;padding:16px 20px;background:var(--panel);border:1px solid var(--line);border-radius:12px;margin:10px 0}
.big .c{color:var(--pink)}
.tblwrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;margin-top:8px}
table{width:100%;border-collapse:collapse;font-size:14px}
th{background:#1c2230;text-align:left;padding:8px 12px;color:var(--dim);font-size:12px;letter-spacing:1px;position:sticky;top:0}
td{padding:7px 12px;border-top:1px solid var(--line)}
.pn{color:var(--cyan);font-weight:700}
.cnt{font-family:var(--mono);color:var(--faint)}
.hint{color:var(--faint);font-size:12.5px;margin:6px 2px}
.badge{display:inline-block;font-size:11px;font-weight:700;padding:1px 8px;border-radius:99px;margin-left:6px}
.b-self{background:#2a3550;color:#a5d8ff}
.b-rare{background:#4a2a35;color:#ff9ade}
.foot{margin-top:26px;color:var(--faint);font-size:12px;border-top:1px solid var(--line);padding-top:12px}
</style></head><body>
<h1>🥚 幻兽帕鲁 1.0 配种图鉴</h1>
<p class="sub">299 只 · 44,850+ 组合全量收录（源=paldb 配种计算器 API，2026-07-17 抓取）</p>
<div class="mech">
<b>机制速记</b>：配种牧场放 1公+1母+<b>蛋糕(放进牧场自己的格子)</b>→ 出蛋。子代由双亲的"配种力"平均值决定（同样的一对永远出同样的种）；<b>同种×同种=同种</b>（传说帕鲁只能这么出）。
加速件：<b>梁叶龙</b>站据点产蛋+20% · <b>贝菈露法</b>满星+博爱主义者词条≈90秒/蛋 · <b>笑魇猫</b>约75%一蛋变两蛋。单牧场存蛋上限20；<b>大型孵化器(47级)免电免控温</b>。
</div>
<div class="tabs">
<span class="tab on" data-p="p0">📈 推荐路线</span>
<span class="tab" data-p="p1">👪 双亲 → 子代</span>
<span class="tab" data-p="p2">🎯 想要谁 → 怎么配</span>
<span class="tab" data-p="p3">🐣 一只亲代 → 全部后代</span>
<span class="tab" data-p="p4">💎 稀有组合榜</span>
</div>

<div class="pane on" id="p0">
  <p class="hint">按「素材什么等级能凑齐」分段（配种牧场 Lv19 解锁）。点目标名跳反查看全部配法。素材等级=野生最早出现等级。</p>

  <h3 style="margin:14px 0 6px;font-size:16px;color:var(--green)">🥉 Lv19-29 起步段 · 先配加速件和白捡货</h3>
  <div class="tblwrap"><table><thead><tr><th>目标</th><th>推荐配方(素材等级)</th><th>为什么配它</th></tr></thead><tbody>
  <tr><td><span class="pn" style="cursor:pointer" onclick="goT('笑魇猫')">笑魇猫</span></td><td>碧海龙(11) × 雷鸣童子(1)</td><td><b>先配它</b>：约75%一蛋变两蛋，全配种线效率×2</td></tr>
  <tr><td><span class="pn" style="cursor:pointer" onclick="goT('夜幕魔蝠')">夜幕魔蝠</span></td><td>雷鸣童子(1) × 派克龙(15)</td><td>版本答案吸血主C，能一路用到毕业</td></tr>
  <tr><td><span class="pn" style="cursor:pointer" onclick="goT('海誓龙')">海誓龙</span></td><td>冲浪鸭(6) × 连理龙(15)</td><td>全能工，素材白菜；牧场还产羊毛(美露帕线上位)</td></tr>
  <tr><td><span class="pn" style="cursor:pointer" onclick="goT('绸笠蛾')">绸笠蛾</span></td><td>冰刺鼠(1) × 派克龙(15)</td><td>牧场产优质布，装备布料自由</td></tr>
  <tr><td>梁叶龙</td><td>不用配：野生 Lv15 抓</td><td>站据点配种产蛋+20%，配种基地常驻挂件</td></tr>
  </tbody></table></div>

  <h3 style="margin:16px 0 6px;font-size:16px;color:var(--cyan)">🥈 Lv30-45 中坚段 · 覆海龙枢纽链（先配2-3只覆海龙，三条线都吃它）</h3>
  <div class="tblwrap"><table><thead><tr><th>目标</th><th>推荐配方(素材等级)</th><th>为什么配它</th></tr></thead><tbody>
  <tr><td><span class="pn" style="cursor:pointer" onclick="goT('覆海龙')">覆海龙</span> ⭐枢纽</td><td>派克龙(15) × 焰煌(30)</td><td>浇水毕业工，且是下面三条线的公共素材</td></tr>
  <tr><td><span class="pn" style="cursor:pointer" onclick="goT('腾炎龙')">腾炎龙</span></td><td>狱焰王(15) × 覆海龙</td><td>生火毕业工(过渡)，还是燎火舞伶素材</td></tr>
  <tr><td><span class="pn" style="cursor:pointer" onclick="goT('阿努比斯')">阿努比斯</span></td><td>覆海龙 × 桃晶鲸(36)</td><td>手工毕业工，野生要Lv68，配比抓早30级用上</td></tr>
  <tr><td><span class="pn" style="cursor:pointer" onclick="goT('魔渊龙')">魔渊龙</span></td><td>凉晶鲸(36) × 泰锋(30·禁猎区)</td><td>采矿毕业工兼龙系输出</td></tr>
  </tbody></table></div>

  <h3 style="margin:16px 0 6px;font-size:16px;color:var(--amber)">🥇 Lv46-60 毕业段 · 补齐编制</h3>
  <div class="tblwrap"><table><thead><tr><th>目标</th><th>推荐配方(素材等级)</th><th>为什么配它</th></tr></thead><tbody>
  <tr><td><span class="pn" style="cursor:pointer" onclick="goT('燎火舞伶')">燎火舞伶</span></td><td>腾炎龙 × 焰煌(30)</td><td>生火终极毕业工(生火4)</td></tr>
  <tr><td><span class="pn" style="cursor:pointer" onclick="goT('沁莲龙')">沁莲龙</span></td><td>泰锋(30·禁猎区) × 黑月女王(58)</td><td>全图鉴唯一播种7+浇水5双修，分基地农业一只包办</td></tr>
  <tr><td><span class="pn" style="cursor:pointer" onclick="goT('波鲁杰克斯')">波鲁杰克斯</span></td><td>⚠配不出：禁猎区1号岛抓 → 同种自繁</td><td>版本答案挂件(叠30层+150%攻防)+发电毕业工</td></tr>
  <tr><td><span class="pn" style="cursor:pointer" onclick="goT('泰锋')">泰锋</span></td><td>禁猎区抓 → 同种自繁刷4星</td><td>4星解锁+200%自身攻防，55/65级首领战核心</td></tr>
  </tbody></table></div>

  <h3 style="margin:16px 0 6px;font-size:16px;color:var(--pink)">🏆 Lv60+ 终局 · 词条工程</h3>
  <div class="mech" style="margin-bottom:0">
  · <b>贝菈诺娃</b>(配种加速终极件)：配不出来，讨伐召唤打，之后同种自繁传词条<br>
  · <b>传说帕鲁</b>全部只能同种×同种（见稀有组合榜）——先野抓一对，再自繁量产<br>
  · <b>词条四件套定向合成</b>：毕业工标配 神速+工匠+认真汉+对应岗位词条——用后代表模式规划两条词条来源线，逐代合流<br>
  · <b>同种蛋副产物喂浓缩</b>：量产的多余个体全进浓缩机，毕业工冲4星(+2工作等级)</div>
</div>

<div class="pane" id="p1">
  <div class="row">
    <input type="text" id="a1" list="dl" placeholder="亲代 1（输入名字）"><!-- goT() 从推荐页跳转填充 b1 -->
    <span style="color:var(--faint)">×</span>
    <input type="text" id="a2" list="dl" placeholder="亲代 2">
  </div>
  <div id="r1" class="hint">输两只帕鲁的名字，自动算出蛋里是谁。</div>
</div>

<div class="pane" id="p2">
  <div class="row">
    <input type="text" id="b1" list="dl" placeholder="目标帕鲁（想配出谁）">
    <input type="text" id="b2" list="dl" placeholder="筛选：必须包含这只亲代（选填）">
  </div>
  <div id="r2" class="hint">列出全部能配出目标的父母组合。</div>
</div>

<div class="pane" id="p3">
  <div class="row"><input type="text" id="c1" list="dl" placeholder="手里有哪只（亲代）"></div>
  <div id="r3" class="hint">列出它和 299 只分别能配出什么。</div>
</div>

<div class="pane" id="p4">
  <p class="hint">组合数越少越难配——只能同种出的就是传说；1-10 种配法的都是稀罕货。</p>
  <div id="r4"></div>
</div>

<datalist id="dl"></datalist>
<div class="foot">数据：paldb.cn /api/breed 全量抓取 · 子代由配种力平均决定，个别性别相关特殊对已按数据收录 · 刷新脚本 palworld-tools/breed_crawl.py + breed_build_html.py</div>
<script>
var PALS=__PALS__;
var CHD="__CHD__";
var SPECIALS=__SPECIALS__;
var N=PALS.length;
var B36="0123456789abcdefghijklmnopqrstuvwxyz";
function kidx(a,b){if(a>b){var t=a;a=b;b=t}return a*N-a*(a-1)/2+(b-a)}
function childOf(a,b){var s=CHD.substr(kidx(a,b)*2,2);if(s==='~~')return -1;return B36.indexOf(s[0])*36+B36.indexOf(s[1])}
var NAME2I={};PALS.forEach(function(p,i){NAME2I[p[0]]=i});
// reverse index
var REV={};(function(){for(var a=0;a<N;a++)for(var b=a;b<N;b++){var c=childOf(a,b);if(c<0)continue;(REV[c]=REV[c]||[]).push([a,b])}})();
var dl=document.getElementById('dl');
PALS.forEach(function(p){var o=document.createElement('option');o.value=p[0];o.label='#'+p[1];dl.appendChild(o)});
function pi(id){var v=document.getElementById(id).value.trim();return NAME2I.hasOwnProperty(v)?NAME2I[v]:-1}
function nm(i){return '<span class="pn">'+PALS[i][0]+'</span> <span class="cnt">#'+PALS[i][1]+'</span>'}
function calc1(){var a=pi('a1'),b=pi('a2');var r=document.getElementById('r1');
  if(a<0||b<0){r.className='hint';r.innerHTML='输两只帕鲁的名字，自动算出蛋里是谁。';return}
  var c=childOf(a,b);var sp=SPECIALS.filter(function(s){return (s[0]===Math.min(a,b)&&s[1]===Math.max(a,b))});
  var h='<div class="big">'+nm(a)+' × '+nm(b)+' → <span class="c">'+(c<0?'?':PALS[c][0])+'</span>'+(c>=0?' <span class="cnt">#'+PALS[c][1]+'</span>':'')+'</div>';
  if(sp.length){h+='<p class="hint">⚠ 此组合与性别有关，可能子代：'+sp[0][2].map(function(x){return PALS[x][0]}).join(' / ')+'</p>'}
  r.className='';r.innerHTML=h}
function calc2(){var t=pi('b1'),f=pi('b2');var r=document.getElementById('r2');
  if(t<0){r.className='hint';r.innerHTML='列出全部能配出目标的父母组合。';return}
  var lst=(REV[t]||[]).slice();if(f>=0)lst=lst.filter(function(p){return p[0]===f||p[1]===f});
  var self=lst.some(function(p){return p[0]===t&&p[1]===t});
  var h='<p class="hint">共 <b style="color:var(--txt)">'+lst.length+'</b> 种组合'+(self?'（含同种×同种）':'')+(lst.length>400?'，只显示前 400 条，用右边输入框按亲代筛':'')+'</p>';
  h+='<div class="tblwrap"><table><thead><tr><th>亲代 1</th><th>亲代 2</th></tr></thead><tbody>';
  lst.slice(0,400).forEach(function(p){h+='<tr><td>'+nm(p[0])+'</td><td>'+nm(p[1])+'</td></tr>'});
  h+='</tbody></table></div>';r.className='';r.innerHTML=h}
function calc3(){var a=pi('c1');var r=document.getElementById('r3');
  if(a<0){r.className='hint';r.innerHTML='列出它和 299 只分别能配出什么。';return}
  var h='<div class="tblwrap"><table><thead><tr><th>配偶</th><th>子代</th></tr></thead><tbody>';
  for(var b=0;b<N;b++){var c=childOf(a,b);if(c<0)continue;h+='<tr><td>'+nm(b)+'</td><td>'+nm(c)+(c===b&&b===a?'<span class="badge b-self">同种</span>':'')+'</td></tr>'}
  h+='</tbody></table></div>';r.className='';r.innerHTML=h}
(function rare(){var rows=[];for(var c=0;c<N;c++){var n=(REV[c]||[]).length;rows.push([n,c])}
  rows.sort(function(x,y){return x[0]-y[0]});
  var h='<div class="tblwrap"><table><thead><tr><th>帕鲁</th><th>配法数</th><th>说明</th></tr></thead><tbody>';
  rows.slice(0,60).forEach(function(rw){var n=rw[0],c=rw[1];var note=n===0?'<span class="badge b-rare">配不出·只能抓/剧情</span>':(n===1?'<span class="badge b-rare">仅同种×同种·传说级</span>':(n<=10?'特殊固定组合':''));
    h+='<tr><td>'+nm(c)+'</td><td class="cnt">'+n+'</td><td>'+note+'</td></tr>'});
  h+='</tbody></table></div>';document.getElementById('r4').innerHTML=h})();
['a1','a2'].forEach(function(i){document.getElementById(i).addEventListener('input',calc1)});
['b1','b2'].forEach(function(i){document.getElementById(i).addEventListener('input',calc2)});
document.getElementById('c1').addEventListener('input',calc3);
document.querySelectorAll('.tab').forEach(function(t){t.onclick=function(){
  document.querySelectorAll('.tab').forEach(function(x){x.classList.toggle('on',x===t)});
  document.querySelectorAll('.pane').forEach(function(p){p.classList.toggle('on',p.id===t.dataset.p)})}});
function goT(n){document.querySelectorAll('.tab').forEach(function(x){x.classList.toggle('on',x.dataset.p==='p2')});
  document.querySelectorAll('.pane').forEach(function(p){p.classList.toggle('on',p.id==='p2')});
  document.getElementById('b1').value=n;document.getElementById('b2').value='';calc2();window.scrollTo(0,0)}
</script></body></html>
"""
html = html.replace('__PALS__', PALS_JS).replace('__CHD__', CHD).replace('__SPECIALS__', SPECIALS_JS)
open(OUT, 'w', encoding='utf-8').write(html)
print('written', OUT, f'{os.path.getsize(OUT)/1024:.0f}KB')
