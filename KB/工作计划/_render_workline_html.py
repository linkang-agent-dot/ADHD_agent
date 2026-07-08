# -*- coding: utf-8 -*-
"""工作line 可视化渲染器
读 工作line_tree.json → 出 工作line_可视化.html（自包含、本地直开）。
层级：主工作流 → 点击展开分支工作流 → 再展开到最底层每件事。
每晚 21:00 日报回写工作line.md 时同步改 json 后重跑本脚本即可。
用法: python _render_workline_html.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "工作line_tree.json")
OUT = os.path.join(HERE, "工作line_可视化.html")

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>工作 Line 可视化</title>
<style>
  :root{
    --bg:#0d1117; --panel:#161b22; --border:#30363d; --text:#e6edf3; --dim:#8b949e;
    --grid:#1c2128;
  }
  *{box-sizing:border-box; margin:0; padding:0;}
  body{background:var(--bg); color:var(--text); font-family:"Segoe UI","Microsoft YaHei",sans-serif; padding:24px;}
  h1{font-size:20px; margin-bottom:4px;}
  .meta{color:var(--dim); font-size:12px; margin-bottom:16px;}
  .toolbar{margin-bottom:12px; display:flex; gap:8px; align-items:center; flex-wrap:wrap;}
  .toolbar button{background:var(--panel); color:var(--text); border:1px solid var(--border);
    border-radius:6px; padding:4px 12px; cursor:pointer; font-size:12px;}
  .toolbar button:hover{border-color:#58a6ff;}
  .legend{display:flex; gap:14px; font-size:12px; color:var(--dim); margin-left:auto; flex-wrap:wrap;}
  .legend i{display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:4px; vertical-align:-1px;}
  .chart{background:var(--panel); border:1px solid var(--border); border-radius:10px; overflow-x:auto;}
  .inner{min-width:980px;}
  .axis{display:flex; border-bottom:1px solid var(--border); position:sticky; top:0; background:var(--panel); z-index:5;}
  .axis .label-col{flex:0 0 var(--lw); padding:6px 10px; font-size:12px; color:var(--dim); border-right:1px solid var(--border);}
  .axis .tl-col{flex:1; position:relative; height:34px;}
  .axis .tick{position:absolute; top:4px; font-size:10px; color:var(--dim); transform:translateX(-50%); white-space:nowrap;}
  .axis .tick.mon{color:var(--text); font-weight:600;}
  .row{display:flex; border-bottom:1px solid #21262d; align-items:stretch;}
  .row:hover{background:#1b212a;}
  .label-col{flex:0 0 var(--lw); padding:7px 10px; border-right:1px solid var(--border);
    font-size:13px; display:flex; align-items:center; gap:6px; cursor:default; overflow:hidden;}
  .has-kids .label-col{cursor:pointer;}
  .caret{width:14px; flex:0 0 14px; color:var(--dim); font-size:10px; transition:transform .15s; text-align:center;}
  .open > .row .caret{transform:rotate(90deg);}
  .no-kids .caret{visibility:hidden;}
  .lv0 > .row .label-col{font-weight:700; font-size:14px;}
  .lv1 > .row .label-col{padding-left:28px;}
  .lv2 > .row .label-col{padding-left:48px; color:#c9d1d9;}
  .lv3 > .row .label-col{padding-left:68px; color:#c9d1d9;}
  .name{white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
  .tl-col{flex:1; position:relative; min-height:32px;
    background-image:linear-gradient(to right, var(--grid) 1px, transparent 1px);
    background-size:var(--dayw) 100%;}
  .bar{position:absolute; top:50%; transform:translateY(-50%); height:14px; border-radius:7px;
    min-width:6px; opacity:.95;}
  .lv0 .bar{height:18px; border-radius:9px;}
  .pt{position:absolute; top:50%; width:11px; height:11px; transform:translate(-50%,-50%) rotate(45deg);
    border-radius:2px;}
  .today-line{position:absolute; top:0; bottom:0; width:2px; background:#f8514966; z-index:3;}
  .today-tag{position:absolute; top:18px; transform:translateX(-50%); font-size:10px; color:#f85149; white-space:nowrap;}
  .st-done{background:#2ea043;} .st-done.bar{opacity:.45;}
  .st-active{background:#1f6feb;}
  .st-critical{background:#da3633; box-shadow:0 0 6px #da363388;}
  .st-pending{background:#bb8009;}
  .st-external{background:#8957e5;}
  .st-auto{background:#6e7681;} .st-auto.bar{opacity:.4;}
  .st-paused{background:#484f58;}
  .children{display:none;}
  .open > .children{display:block;}
  .foot{color:var(--dim); font-size:11px; margin-top:10px;}
</style>
</head>
<body>
<h1>工作 Line 可视化（主工作流 → 分支 → 每件事）</h1>
<div class="meta">数据更新：__UPDATED__ ｜ 窗口：__RSTART__ ~ __REND__ ｜ 单一事实源=工作line.md，本页由 工作line_tree.json 渲染</div>
<div class="toolbar">
  <button onclick="setAll(true)">全部展开</button>
  <button onclick="setAll(false)">全部收起</button>
  <span class="legend">
    <span><i style="background:#da3633"></i>今日必做/硬时限</span>
    <span><i style="background:#1f6feb"></i>进行中</span>
    <span><i style="background:#bb8009"></i>待到期节点</span>
    <span><i style="background:#8957e5"></i>等外部(放行/合并/图)</span>
    <span><i style="background:#2ea043"></i>已完成</span>
    <span><i style="background:#6e7681"></i>自动跑</span>
  </span>
</div>
<div class="chart"><div class="inner" id="inner"></div></div>
<div class="foot">点击带 ▶ 的行展开下一层。菱形=单日节点，条=时间段。红竖线=今天。悬停看备注。</div>
<script>
const DATA = __DATA__;
const MS = 86400000;
const t0 = new Date(DATA.range.start + "T00:00:00");
const t1 = new Date(DATA.range.end + "T00:00:00");
const DAYS = Math.round((t1 - t0) / MS) + 1;
document.documentElement.style.setProperty('--dayw', (100 / DAYS) + '%');
document.documentElement.style.setProperty('--lw', '360px');
const todayStr = new Date().toISOString().slice(0,10);
function pct(dstr, endOfDay){
  const d = new Date(dstr + "T00:00:00");
  let days = (d - t0) / MS + (endOfDay ? 1 : 0);
  return Math.max(0, Math.min(100, days / DAYS * 100));
}
function bar(node, lv){
  const s = node.status || 'pending';
  const tip = (node.name) + (node.start ? `\n${node.start} ~ ${node.end || node.start}` : (node.date ? "\n" + node.date : "")) + (node.note ? "\n" + node.note : "");
  if (node.date && !node.start){
    return `<div class="pt st-${s}" style="left:${pct(node.date) + 100/DAYS/2}%" title="${esc(tip)}"></div>`;
  }
  const l = pct(node.start), r = pct(node.end || node.start, true);
  return `<div class="bar st-${s}" style="left:${l}%; width:${Math.max(r-l, .8)}%" title="${esc(tip)}"></div>`;
}
function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;'); }
let uid = 0;
function renderNode(node, lv){
  const kids = node.children || [];
  const id = 'n' + (uid++);
  const icon = {critical:'🔴', done:'✅', external:'🟣', auto:'⚙️', paused:'⏸'}[node.status] || '';
  let h = `<div class="node lv${lv} ${kids.length ? 'has-kids' : 'no-kids'}" id="${id}">`;
  h += `<div class="row"><div class="label-col" ${kids.length ? `onclick="toggle('${id}')"` : ''}>` +
       `<span class="caret">▶</span><span class="name" title="${esc(node.name + (node.note ? '\n' + node.note : ''))}">${icon} ${esc(node.name)}</span></div>` +
       `<div class="tl-col">${todayMark()}${bar(node, lv)}</div></div>`;
  if (kids.length){
    h += `<div class="children">` + kids.map(k => renderNode(k, lv+1)).join('') + `</div>`;
  }
  return h + `</div>`;
}
function todayMark(){
  const p = pct(todayStr) + 100/DAYS/2;
  if (p <= 0 || p >= 100) return '';
  return `<div class="today-line" style="left:${p}%"></div>`;
}
function axis(){
  let ticks = '';
  for (let i = 0; i < DAYS; i++){
    const d = new Date(t0.getTime() + i*MS);
    if (d.getDate() % 2 === 1){
      const cls = d.getDate() === 1 ? 'tick mon' : 'tick';
      ticks += `<div class="${cls}" style="left:${(i + .5) / DAYS * 100}%">${d.getMonth()+1}/${d.getDate()}</div>`;
    }
  }
  const p = pct(todayStr) + 100/DAYS/2;
  const todayTag = (p > 0 && p < 100) ? `<div class="today-line" style="left:${p}%"></div><div class="today-tag" style="left:${p}%">今天</div>` : '';
  return `<div class="axis"><div class="label-col">工作流</div><div class="tl-col" style="background:none">${ticks}${todayTag}</div></div>`;
}
document.getElementById('inner').innerHTML = axis() + DATA.workflows.map(w => renderNode(w, 0)).join('');
function toggle(id){ document.getElementById(id).classList.toggle('open'); }
function setAll(open){ document.querySelectorAll('.has-kids').forEach(n => n.classList.toggle('open', open)); }
</script>
</body>
</html>
"""

def main():
    with open(SRC, encoding="utf-8") as f:
        data = json.load(f)
    html = (TEMPLATE
            .replace("__UPDATED__", data.get("updated", "?"))
            .replace("__RSTART__", data["range"]["start"])
            .replace("__REND__", data["range"]["end"])
            .replace("__DATA__", json.dumps(data, ensure_ascii=False)))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("OK ->", OUT)

if __name__ == "__main__":
    sys.exit(main())
