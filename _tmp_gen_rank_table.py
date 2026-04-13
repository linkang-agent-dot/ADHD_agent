# -*- coding: utf-8 -*-
"""
用 iap_type2 重新生成科技节礼包排名表
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

SQL = """
SELECT
    b2.iap_id_name,
    b2.iap_type2,
    COUNT(DISTINCT b1.user_id) AS pay_user_cnt,
    COUNT(*) AS buy_times,
    CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue
FROM (
    SELECT user_id, iap_id, pay_price
    FROM v1041.ods_user_order
    WHERE partition_date BETWEEN '2026-03-12' AND '2026-04-03'
      AND date(date_add('hour',-8,created_at)) BETWEEN date '2026-03-13' AND date '2026-04-03'
      AND pay_status = 1
      AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
) b1
INNER JOIN (
    SELECT iap_id, iap_id_name, iap_type2
    FROM v1041.dim_iap
    WHERE iap_type = '混合-节日活动'
) b2 ON b1.iap_id = b2.iap_id
GROUP BY b2.iap_id_name, b2.iap_type2
ORDER BY revenue DESC
"""
rows = api.execute_sql(SQL)

TYPE2_MAP = {
    "混合-节日活动-节日特惠": ("节日特惠", "tag-game"),
    "混合-节日活动-节日皮肤": ("节日皮肤", "tag-visual"),
    "混合-节日活动-节日BP":   ("节日BP",  "tag-hybrid"),
    "混合-节日活动-挖矿小游戏": ("挖矿",  "tag-mine"),
}

total_rev = sum(float(r['revenue'] or 0) for r in rows)

# top 20 (main table) + rest (collapsed)
top20_html = []
rest_html = []

for i, r in enumerate(rows):
    rank = i + 1
    name = r['iap_id_name']
    t2 = r.get('iap_type2', '') or ''
    label, css_cls = TYPE2_MAP.get(t2, (t2, 'tag-hybrid'))
    rev = float(r.get('revenue', 0) or 0)
    buyers = int(r.get('pay_user_cnt', 0) or 0)
    times = int(r.get('buy_times', 0) or 0)
    pct = rev / total_rev * 100 if total_rev > 0 else 0
    freq = times / buyers if buyers > 0 else 0
    avg_price = rev / times if times > 0 else 0
    arpu = rev / buyers if buyers > 0 else 0

    is_highlight = rank <= 3
    row_cls = ' class="highlight-row"' if is_highlight else ''

    bold_rev = ' bold' if rank <= 10 else ''
    bold_name = ' class="bold"' if rank <= 10 else ''
    high_arpu = f' style="color:var(--accent2)"' if arpu >= 70 else ''

    if rank <= 20:
        top20_html.append(
            f'        <tr{row_cls}>'
            f'<td>{rank}</td>'
            f'<td{bold_name}>{name}</td>'
            f'<td><span class="tag {css_cls}">{label}</span></td>'
            f'<td class="num{bold_rev}">${rev:,.0f}</td>'
            f'<td class="num">{pct:.1f}%</td>'
            f'<td class="num">{times:,}</td>'
            f'<td class="num">{buyers:,}</td>'
            f'<td class="num">{freq:.1f}x</td>'
            f'<td class="num">${avg_price:.2f}</td>'
            f'<td class="num{bold_rev}"{high_arpu}>${arpu:.2f}</td>'
            f'</tr>'
        )
    else:
        pad = ' style="padding:11px 14px"'
        rest_html.append(
            f'          <tr>'
            f'<td{pad}>{rank}</td>'
            f'<td{pad}>{name}</td>'
            f'<td{pad}><span class="tag {css_cls}">{label}</span></td>'
            f'<td class="num"{pad}>${rev:,.0f}</td>'
            f'<td class="num"{pad}>{pct:.2f}%</td>'
            f'<td class="num"{pad}>{times:,}</td>'
            f'<td class="num"{pad}>{buyers:,}</td>'
            f'<td class="num"{pad}>{freq:.1f}x</td>'
            f'<td class="num"{pad}>${avg_price:.2f}</td>'
            f'<td class="num"{pad}>${arpu:.2f}</td>'
            f'</tr>'
        )

with open(r'C:\ADHD_agent\_tmp_rank_top20.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(top20_html))

with open(r'C:\ADHD_agent\_tmp_rank_rest.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(rest_html))

print(f"总计 {len(rows)} 种礼包，total ${total_rev:,.0f}")
print(f"Top20 行: {len(top20_html)}, 其余: {len(rest_html)}")
print("✅ 已生成 _tmp_rank_top20.html 和 _tmp_rank_rest.html")
