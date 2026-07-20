# -*- coding: utf-8 -*-
"""竞猜 SKU 拆到每场比赛：每场 参与人数 + 各档位(尾1/2/3)收入买家 → _jc_match_sku.json"""
import sys, json, os, subprocess
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql as _exec_raw
import time
def execute_sql(sql, **kw):
    for i in range(4):
        try:
            return _exec_raw(sql, **kw)
        except Exception as e:
            if i == 3: raise
            print(f'  [retry {i+1}] {str(e)[:80]}'); time.sleep(8)

HERE = os.path.dirname(os.path.abspath(__file__))
USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
WCD = r'C:\ADHD_agent\KB\产出-数值设计\X3_世界杯'

# 1) 队号→中文名（Pack.tsv 894 尾0 行的 c35）
out_pack = subprocess.run(['git','-C',r'C:\x3\gdconfig','show','origin/dev:tsv/Pack__Pack.tsv'],
                          capture_output=True).stdout.decode('utf-8', errors='replace')
num2cn = {}
for ln in out_pack.split('\n'):
    c = ln.split('\t')
    if c and c[0].isdigit() and 894010 <= int(c[0]) <= 894489 and int(c[0]) % 10 == 0:
        num2cn[(int(c[0]) - 894000) // 10] = (c[35] if len(c) > 35 else '').strip()
print(f"队号映射 {len(num2cn)} 队")

CN2CODE = {'阿尔及利亚':'ALG','阿根廷':'ARG','澳大利亚':'AUS','奥地利':'AUT','比利时':'BEL','波黑':'BIH',
 '巴西':'BRA','加拿大':'CAN','科特迪瓦':'CIV','刚果民主共和国':'COD','刚果(金)':'COD','哥伦比亚':'COL','佛得角':'CPV',
 '库拉索':'CUW','德国':'GER','埃及':'EGY','英格兰':'ENG','西班牙':'ESP','法国':'FRA','加纳':'GHA','海地':'HAI',
 '伊朗':'IRN','意大利':'ITA','日本':'JPN','约旦':'JOR','韩国':'KOR','摩洛哥':'MAR','墨西哥':'MEX','荷兰':'NED',
 '新西兰':'NZL','挪威':'NOR','巴拿马':'PAN','巴拉圭':'PAR','葡萄牙':'POR','卡塔尔':'QAT','沙特阿拉伯':'KSA','沙特':'KSA',
 '塞内加尔':'SEN','南非':'RSA','瑞士':'SUI','突尼斯':'TUN','美国':'USA','乌拉圭':'URU','乌兹别克斯坦':'UZB',
 '苏格兰':'SCO','克罗地亚':'CRO','厄瓜多尔':'ECU','阿联酋':'UAE','塞尔维亚':'SRB','瑞典':'SWE','刚果':'COD','捷克':'CZE','伊拉克':'IRQ','土耳其':'TUR'}
code2num = {}
for num, cn in num2cn.items():
    code = CN2CODE.get(cn)
    if code: code2num[code] = num
print(f"code映射 {len(code2num)} 队; 未映射中文名: {[cn for cn in num2cn.values() if cn not in CN2CODE]}")

# 2) 赛程
sch = json.load(open(os.path.join(WCD, 'wc_dashboard_data.json'), encoding='utf-8'))['schedule']
try:
    r32 = json.load(open(os.path.join(WCD, 'wc_dashboard_data.R32backup.json'), encoding='utf-8'))['schedule']
except Exception:
    r32 = []
for m in r32:
    if m.get('round') == '1/16': m['round'] = 'R32'
matches = [m for m in r32 if m.get('round') == 'R32'] + sch
# SF 的 $9.99/$19.99 走 4强容器包（淘汰队id重配），按队映射会丢——容器映射（memory 07-13 SF包路由）
SF_CONTAINER = {'ARG': (894012, 894013), 'BEL': (894032, 894033), 'ENG': (894042, 894043),
                'ESP': (894062, 894063), 'FRA': (894082, 894083), 'MAR': (894092, 894093),
                'NOR': (894102, 894103), 'SUI': (894122, 894123)}
WINDOWS = {'R32': ('2026-06-26','2026-07-02'), 'R16': ('2026-07-03','2026-07-08'),
           'QF': ('2026-07-09','2026-07-12'), 'SF': ('2026-07-13','2026-07-16'),
           'FINAL': ('2026-07-17','2026-07-20')}

# 3) 每轮：订单/参与 按包×日（供每场按锁盘日精筛，防 pack 跨轮复用/锁盘后残留）
pay_by_pack, part_by_pack = {}, {}
for rd, (a, b) in WINDOWS.items():
    rows = execute_sql(f"""SELECT iap_id, partition_date d, round(sum({USD}),0) rev, count(distinct user_id) u
      FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{a}' AND '{b}'
      AND iap_id LIKE '894%' GROUP BY 1,2""", datasource="TRINO_HF")["data"]
    pay_by_pack[rd] = {}
    for r in rows:
        pay_by_pack[rd].setdefault(r['iap_id'], {})[r['d']] = dict(rev=float(r['rev']), u=r['u'])
    rows = execute_sql(f"""SELECT cast(reason_sub_id as varchar) pid, partition_date d, count(distinct user_id) u
      FROM v1090.ods_user_asset WHERE partition_date BETWEEN '{a}' AND '{b}'
      AND cast(reason_sub_id as varchar) LIKE '894%0' GROUP BY 1,2""", datasource="TRINO_HF")["data"]
    part_by_pack[rd] = {}
    for r in rows:
        part_by_pack[rd].setdefault(r['pid'], {})[r['d']] = r['u']
    print(rd, '订单包数', len(pay_by_pack[rd]), '参与包数', len(part_by_pack[rd]))

# 4) 聚合到场：每场窗口 = 轮开盘日 → 该场锁盘日（partition 日粒度）
res = []
for m in matches:
    rd = m['round']
    if rd not in WINDOWS: continue
    a_n, b_n = code2num.get(m['a_code']), code2num.get(m['b_code'])
    if a_n is None or b_n is None:
        print('⚠️缺队号:', m['key']); continue
    lock_d = (m.get('lock_utc') or m.get('kickoff_utc') or WINDOWS[rd][1])[:10]
    lock_d = min(lock_d, WINDOWS[rd][1])
    rec = dict(key=m['key'], round=rd, kickoff=m.get('kickoff_utc',''), lock=lock_d, part=0,
               t1_rev=0, t2_rev=0, t3_rev=0, t1_u=0, t2_u=0, t3_u=0)
    for n in (a_n, b_n):
        for d, u in part_by_pack[rd].get(str(894000 + n*10), {}).items():
            if d <= lock_d: rec['part'] += u
        code = m['a_code'] if n == a_n else m['b_code']
        for t in ('1','2','3'):
            pid = str(894000 + n*10 + int(t))
            if rd == 'SF' and t in ('2','3') and code in SF_CONTAINER:
                pid = str(SF_CONTAINER[code][int(t)-2])
            for d, v in pay_by_pack[rd].get(pid, {}).items():
                if d <= lock_d:
                    rec[f't{t}_rev'] += v['rev']; rec[f't{t}_u'] += v['u']
    rec['rev'] = rec['t1_rev'] + rec['t2_rev'] + rec['t3_rev']
    res.append(rec)

res.sort(key=lambda r: r['kickoff'])
for r in res:
    print(f"{r['key']:16s} {r['kickoff'][:10]} 参与{r['part']:>6,} 付费${r['rev']:>6,.0f} (尾1 ${r['t1_rev']:,.0f}/尾2 ${r['t2_rev']:,.0f}/尾3 ${r['t3_rev']:,.0f})")
json.dump(dict(matches=res), open(os.path.join(HERE, '_jc_match_sku.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('saved _jc_match_sku.json,', len(res), '场')
