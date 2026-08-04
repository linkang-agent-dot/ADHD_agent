import argparse
import csv
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent


def load_data(detail_name="BINGO101830_受影响玩家明细.csv", summary_name="summary.json"):
    with (BASE / detail_name).open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        players = list(csv.DictReader(handle))
    summary = json.loads((BASE / summary_name).read_text(encoding="utf-8"))
    content = json.loads((BASE / "content_draft_cn_en.json").read_text(encoding="utf-8"))
    return players, summary, content


def build_html(players, summary, content):
    payload = json.dumps(
        {"players": players, "summary": summary, "content": content},
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    return r'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>BINGO 101830｜误上线补偿核对台</title>
  <style>
    :root{--ink:#171815;--paper:#f3eedf;--paper2:#e8dfca;--signal:#ed4b2f;--lime:#b6d73f;--muted:#69695f;--line:#c9bea7;--white:#fffdf6;--shadow:8px 8px 0 var(--ink)}
    *{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:var(--paper);font-family:"Microsoft YaHei UI","PingFang SC",sans-serif}
    body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.24;background-image:linear-gradient(rgba(23,24,21,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(23,24,21,.06) 1px,transparent 1px);background-size:28px 28px;mask-image:linear-gradient(to bottom,#000,transparent 80%)}
    .wrap{width:min(1480px,calc(100% - 36px));margin:22px auto 70px;position:relative}.mast{border:2px solid var(--ink);background:var(--signal);box-shadow:var(--shadow);padding:22px 26px 19px;display:grid;grid-template-columns:1fr auto;gap:20px;align-items:end}
    .eyebrow{font:800 12px/1.2 ui-monospace,Consolas,monospace;letter-spacing:.17em;text-transform:uppercase}.mast h1{font-family:STKaiti,KaiTi,serif;font-size:clamp(34px,5vw,66px);line-height:.95;margin:10px 0 5px;letter-spacing:-.04em}.status{border:2px solid var(--ink);background:var(--lime);padding:12px 16px;font-weight:900;transform:rotate(-1deg);white-space:nowrap}.status small{display:block;font:700 11px ui-monospace,Consolas,monospace;margin-top:3px}
    .strip{margin:22px 0;display:grid;grid-template-columns:repeat(4,1fr);border:2px solid var(--ink);background:var(--ink);gap:2px}.metric{background:var(--white);padding:18px 20px;min-height:112px}.metric .label{font-size:12px;font-weight:800;color:var(--muted);letter-spacing:.08em}.metric strong{display:block;margin-top:9px;font:900 clamp(28px,3vw,43px)/1 ui-monospace,Consolas,monospace}.metric em{font-style:normal;color:var(--signal);font-weight:900}
    .section{margin-top:26px}.section-title{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:3px solid var(--ink);padding-bottom:8px;margin-bottom:14px}.section-title h2{font:900 22px/1 STKaiti,KaiTi,serif;margin:0}.section-title span{font:700 11px ui-monospace,Consolas,monospace;color:var(--muted)}
    .scope-grid{display:grid;grid-template-columns:1.25fr .75fr;gap:18px}.card{border:2px solid var(--ink);background:rgba(255,253,246,.88);padding:20px;box-shadow:4px 4px 0 var(--paper2)}.timeline{display:grid;grid-template-columns:auto 1fr;gap:8px 16px;margin-top:16px}.timeline b{font:800 12px ui-monospace,Consolas,monospace;color:var(--signal)}.timeline p{margin:0 0 7px;font-size:14px;line-height:1.6}.rule{background:var(--ink);color:var(--white);padding:18px}.rule strong{color:var(--lime);display:block;font-size:20px;margin-bottom:7px}.rule p{margin:0;line-height:1.65;font-size:13px}.warning{border-left:7px solid var(--signal);margin-top:12px}.warning b{color:var(--signal)}
    .distribution{height:210px;display:flex;align-items:flex-end;gap:5px;padding:20px 8px 4px;border-left:2px solid var(--ink);border-bottom:2px solid var(--ink);overflow-x:auto}.bar-wrap{min-width:42px;flex:1;text-align:center}.bar{background:var(--signal);border:1px solid var(--ink);min-height:4px;transition:.2s}.bar-wrap:hover .bar{background:var(--lime);transform:translateY(-4px)}.bar-n{font:800 10px ui-monospace,Consolas,monospace;margin-bottom:5px}.bar-x{font:700 9px ui-monospace,Consolas,monospace;margin-top:6px;writing-mode:vertical-rl;height:38px}.mail{display:grid;grid-template-columns:170px 1fr;gap:18px}.mail-title{background:var(--lime);border:2px solid var(--ink);padding:15px;font-weight:900}.mail-body{border-left:2px solid var(--ink);padding:2px 0 2px 18px;line-height:1.75;font-size:14px}
    .toolbar{display:grid;grid-template-columns:minmax(240px,1fr) 150px 150px auto auto;gap:9px;margin-bottom:12px}.control{border:2px solid var(--ink);background:var(--white);height:42px;padding:0 12px;font:700 13px ui-monospace,Consolas,"Microsoft YaHei UI",sans-serif;color:var(--ink);outline:none}.control:focus{box-shadow:3px 3px 0 var(--signal)}button.control{cursor:pointer;background:var(--ink);color:var(--white)}button.control.alt{background:var(--lime);color:var(--ink)}
    .table-shell{border:2px solid var(--ink);background:var(--white);overflow:auto;max-height:660px}.table-meta{padding:11px 13px;background:var(--ink);color:var(--white);position:sticky;top:0;z-index:3;font:700 12px ui-monospace,Consolas,monospace;display:flex;justify-content:space-between}table{border-collapse:collapse;width:100%;font-size:12px;white-space:nowrap}th{position:sticky;top:37px;z-index:2;background:var(--paper2);text-align:left;border-bottom:2px solid var(--ink);padding:11px 10px;cursor:pointer}td{border-bottom:1px solid var(--line);padding:9px 10px;font-family:ui-monospace,Consolas,monospace}tbody tr{cursor:pointer}tbody tr:hover{background:#fff2b7}td.money{font-weight:900;color:var(--signal)}.ok{color:#37751e;font-weight:900}.bad{background:#ffd2c9;color:#9d1d09;font-weight:900}.empty{padding:40px;text-align:center;color:var(--muted)}
    .drawer{position:fixed;right:0;top:0;height:100vh;width:min(440px,94vw);background:var(--ink);color:var(--white);z-index:20;padding:28px;transform:translateX(105%);transition:.28s cubic-bezier(.2,.9,.2,1);box-shadow:-12px 0 0 rgba(237,75,47,.75);overflow:auto}.drawer.open{transform:none}.drawer button{float:right;background:none;border:1px solid var(--white);color:var(--white);padding:6px 10px;cursor:pointer}.drawer h3{clear:both;font:900 30px STKaiti,KaiTi,serif;padding-top:28px;margin-bottom:8px}.drawer .big{font:900 42px ui-monospace,Consolas,monospace;color:var(--lime);margin:18px 0}.detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#555;border:1px solid #555}.detail-grid div{background:#242520;padding:12px}.detail-grid small{display:block;color:#aaa;margin-bottom:6px}.drawer .check{margin-top:20px;padding:14px;border:1px solid var(--lime);color:var(--lime);font-weight:800}
    footer{display:flex;justify-content:space-between;gap:20px;margin-top:24px;padding-top:14px;border-top:2px solid var(--ink);font:700 11px/1.6 ui-monospace,Consolas,monospace;color:var(--muted)}
    @media(max-width:900px){.mast{grid-template-columns:1fr}.strip{grid-template-columns:1fr 1fr}.scope-grid{grid-template-columns:1fr}.toolbar{grid-template-columns:1fr 1fr}.toolbar input{grid-column:1/-1}.mail{grid-template-columns:1fr}.mast h1{font-size:42px}}@media(max-width:520px){.wrap{width:calc(100% - 20px)}.strip{grid-template-columns:1fr}.toolbar{grid-template-columns:1fr}.toolbar>*{grid-column:auto!important}.metric{min-height:90px}.mast{padding:18px}.distribution{height:180px}}
    @media print{body:before,.toolbar,.drawer{display:none}.wrap{width:100%;margin:0}.mast,.card,.strip,.table-shell{box-shadow:none}.table-shell{max-height:none;overflow:visible}th,.table-meta{position:static}}
  </style>
</head>
<body>
<main class="wrap">
  <header class="mast"><div><div class="eyebrow">Incident restitution audit / X3 / 2026-08-04</div><h1>拼图误上线补偿核对台</h1><div>ACTV ONLINE <b>101830</b> · ACTV PUZZLE <b>1830</b> · <b id="subsetLabel">全部受影响玩家</b></div></div><div class="status">待人工确认<small>NOT SENT · DRY-RUN PASSED</small></div></header>
  <section class="strip" id="metrics"></section>
  <section class="section"><div class="section-title"><h2>01 / 取数口径</h2><span>SCOPE &amp; EXCLUSIONS</span></div><div class="scope-grid"><div class="card"><b>精确查询窗口（北京时间）</b><div class="timeline"><b>START</b><p>2026-07-30 15:23:00 — 101830 玩家实例首次出现</p><b>END</b><p>2026-07-31 13:43:56 — 正式拼图 101829 首次出现</p><b>MATCH</b><p>同一玩家、服务器、会话中：获得马戏勋章 1210，同时发生拼图任务立即完成扣钻。</p></div></div><div><div class="rule"><strong>唯一有效扣款：1,000 钻 / 次</strong><p>101830 使用任务组 109；所有可跳过任务 FinishCost 均为 1,000 钻。补偿金额 = 有效立即完成次数 × 1,000。</p></div><div class="card warning"><b>已排除</b><br>2 名玩家的 4 笔 1,500 钻扣除。任务组 109 不存在该价格，判定属于同会话内其他拼图。</div></div></div></section>
  <section class="section"><div class="section-title"><h2>02 / 补偿分布</h2><span>DIAMOND REFUND DISTRIBUTION</span></div><div class="card"><div class="distribution" id="distribution"></div></div></section>
  <section class="section"><div class="section-title"><h2>03 / 邮件预览</h2><span>DRAFT · CN</span></div><div class="card mail"><div class="mail-title" id="mailTitle"></div><div class="mail-body" id="mailBody"></div></div></section>
  <section class="section"><div class="section-title"><h2>04 / 玩家逐笔核对</h2><span>CLICK ROW FOR DETAIL · CLICK HEADER TO SORT</span></div><div class="toolbar"><input id="search" class="control" placeholder="搜索 server_id / user_id"><select id="server" class="control"><option value="">全部服务器</option></select><select id="amount" class="control"><option value="0">全部金额</option><option value="10000">≥ 10,000</option><option value="20000">≥ 20,000</option></select><button class="control alt" id="reset">重置筛选</button><button class="control" onclick="window.print()">打印 / PDF</button></div><div class="table-shell"><div class="table-meta"><span id="visibleCount"></span><span id="visibleSum"></span></div><table><thead><tr><th data-key="server_id">服务器 ↕</th><th data-key="user_id">玩家 ID ↕</th><th data-key="fast_finish_count">立即完成 ↕</th><th data-key="diamonds_consumed">返还钻石 ↕</th><th data-key="medals_received">勋章</th><th data-key="cards_received">纪念卡</th><th>公式核验</th><th data-key="diamond_first">首次扣钻 ↕</th><th data-key="diamond_last">末次扣钻 ↕</th></tr></thead><tbody id="tbody"></tbody></table></div></section>
  <footer><div>数据源：Datain v1090.ods_user_asset / v1090.ods_user_activity<br>公共 reason 已通过会话内 Item 1210 产出收窄。</div><div>本页仅用于核对 · 不连接 iGame · 不执行发送<br>生成时间：<span id="generatedAt"></span></div></footer>
</main>
<aside class="drawer" id="drawer"><button id="closeDrawer">关闭 ×</button><h3>玩家补偿明细</h3><div id="drawerContent"></div></aside>
<script id="auditData" type="application/json">__PAYLOAD__</script>
<script>
const D=JSON.parse(document.getElementById('auditData').textContent), players=D.players.map(p=>Object.fromEntries(Object.entries(p).map(([k,v])=>[k,/^(server_id|user_id|fast_finish_count|diamonds_consumed|medals_received|cards_received)$/.test(k)?Number(v):v]))), fmt=n=>Number(n).toLocaleString('zh-CN');
document.getElementById('subsetLabel').textContent=D.summary.subset_label||'全部受影响玩家';
document.getElementById('metrics').innerHTML=[['受影响玩家',fmt(D.summary.affected_players),'人'],['覆盖服务器',fmt(D.summary.affected_servers),'服'],['有效立即完成',fmt(D.summary.fast_finish_count),'次'],['应返钻石',fmt(D.summary.diamonds_to_return),'钻']].map((x,i)=>`<div class="metric"><div class="label">${x[0]}</div><strong${i===3?' class="money"':''}>${x[1]} <em>${x[2]}</em></strong></div>`).join('');
const dist=D.summary.diamond_distribution,max=Math.max(...Object.values(dist));document.getElementById('distribution').innerHTML=Object.entries(dist).map(([x,n])=>`<div class="bar-wrap" title="${fmt(x)} 钻：${n} 人"><div class="bar-n">${n}</div><div class="bar" style="height:${Math.max(4,n/max*135)}px"></div><div class="bar-x">${fmt(x)}</div></div>`).join('');
document.getElementById('mailTitle').textContent=D.content.cn.title;document.getElementById('mailBody').textContent=D.content.cn.body;document.getElementById('generatedAt').textContent=new Date().toLocaleString('zh-CN',{hour12:false});
const server=document.getElementById('server');[...new Set(players.map(p=>p.server_id))].sort((a,b)=>a-b).forEach(id=>server.add(new Option(id+' 服',id)));let sortKey='diamonds_consumed',sortDir=-1;
function filtered(){const q=document.getElementById('search').value.trim(),s=server.value,min=Number(document.getElementById('amount').value);return players.filter(p=>(!q||String(p.server_id).includes(q)||String(p.user_id).includes(q))&&(!s||String(p.server_id)===s)&&p.diamonds_consumed>=min).sort((a,b)=>{const av=a[sortKey],bv=b[sortKey];return (typeof av==='number'?av-bv:String(av).localeCompare(String(bv)))*sortDir})}
function render(){const rows=filtered(),sum=rows.reduce((a,p)=>a+p.diamonds_consumed,0);document.getElementById('visibleCount').textContent=`显示 ${rows.length} / ${players.length} 人`;document.getElementById('visibleSum').textContent=`当前合计 ${fmt(sum)} 钻`;document.getElementById('tbody').innerHTML=rows.length?rows.map(p=>{const ok=p.diamonds_consumed===p.fast_finish_count*1000;return `<tr data-user="${p.user_id}" data-server="${p.server_id}"><td>${p.server_id}</td><td>${p.user_id}</td><td>${p.fast_finish_count}</td><td class="money">${fmt(p.diamonds_consumed)}</td><td>${p.medals_received}</td><td>${p.cards_received}</td><td class="${ok?'ok':'bad'}">${ok?'✓ 正确':'✕ 异常'}</td><td>${p.diamond_first}</td><td>${p.diamond_last}</td></tr>`}).join(''):'<tr><td colspan="9" class="empty">没有匹配的玩家</td></tr>';document.querySelectorAll('tbody tr[data-user]').forEach(tr=>tr.onclick=()=>openPlayer(Number(tr.dataset.server),Number(tr.dataset.user)))}
function openPlayer(s,u){const p=players.find(x=>x.server_id===s&&x.user_id===u),ok=p.diamonds_consumed===p.fast_finish_count*1000;document.getElementById('drawerContent').innerHTML=`<div>SERVER ${p.server_id} / USER ${p.user_id}</div><div class="big">${fmt(p.diamonds_consumed)} 钻</div><div class="detail-grid"><div><small>立即完成</small>${p.fast_finish_count} 次</div><div><small>马戏勋章</small>${p.medals_received}</div><div><small>纪念卡</small>${p.cards_received}</div><div><small>返还公式</small>${p.fast_finish_count} × 1,000</div><div><small>首次扣钻</small>${p.diamond_first}</div><div><small>末次扣钻</small>${p.diamond_last}</div><div><small>首次勋章</small>${p.medal_first}</div><div><small>末次勋章</small>${p.medal_last}</div></div><div class="check">${ok?'✓ 金额复算一致':'✕ 金额复算不一致，请拦截'}</div>`;document.getElementById('drawer').classList.add('open')}
['search','server','amount'].forEach(id=>document.getElementById(id).addEventListener(id==='search'?'input':'change',render));document.getElementById('reset').onclick=()=>{document.getElementById('search').value='';server.value='';document.getElementById('amount').value='0';render()};document.querySelectorAll('th[data-key]').forEach(th=>th.onclick=()=>{if(sortKey===th.dataset.key)sortDir*=-1;else{sortKey=th.dataset.key;sortDir=1}render()});document.getElementById('closeDrawer').onclick=()=>document.getElementById('drawer').classList.remove('open');render();
</script>
</body>
</html>'''.replace("__PAYLOAD__", payload)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--detail", default="BINGO101830_受影响玩家明细.csv")
    parser.add_argument("--summary", default="summary.json")
    parser.add_argument("--output", default="BINGO101830_补偿核对台.html")
    args = parser.parse_args()
    players, summary, content = load_data(args.detail, args.summary)
    output = BASE / args.output
    output.write_text(build_html(players, summary, content), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
