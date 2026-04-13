import sys, json, os
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
from _datain_api import execute_sql

iap_ids = [
    '2013100235_cycle','2013505016_normal','201350104_new_daily_specials',
    '2013505014_normal','2013505017_normal','201390111_battle_pass',
    '2013505028_normal','201390092_battle_pass','2013501083_normal',
    '2013500480_normal','2013410003_battle_pass','2013501505_normal',
    '2013500481_normal','201390029_battle_pass','2013100234_cycle',
    '2013505015_normal','2013505006_normal','2013505013_normal',
    '2013505020_normal','2013210001_subscription','2013410002_battle_pass',
    '2013510220_random','201390089_battle_pass','2013500507_normal',
    '2013510227_normal','2013510222_random','201310095_normal',
    '201320040_normal','201320360_normal','201390129_battle_pass'
]
id_list = "','".join(iap_ids)
sql = f"SELECT iap_id, iap_id_name FROM v1041.dim_iap WHERE iap_id IN ('{id_list}') ORDER BY iap_id"
rows = execute_sql(sql, 'TRINO_AWS')
out = {row['iap_id']: row['iap_id_name'] for row in rows}
with open(r'C:\ADHD_agent\_tmp_iap_names.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print('done, rows:', len(out))
