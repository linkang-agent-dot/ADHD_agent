import subprocess
import json
import os

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SID = '1l96i3_rJL8-7sLUy2pTUATiNZBxkzQjF_JA_emdJGto'

def gws_run(params_dict, body_dict=None, action='values update'):
    cmd = [GWS_CMD, 'sheets', 'spreadsheets'] + action.split()
    cmd += ['--params', json.dumps(params_dict, ensure_ascii=False)]
    if body_dict:
        cmd += ['--json', json.dumps(body_dict, ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    try:
        return json.loads(r.stdout)
    except:
        print(f"ERR: {r.stderr[:100]}")
        return None

def add_sheet(name):
    r = gws_run({'spreadsheetId': SID},
                {'requests': [{'addSheet': {'properties': {'title': name}}}]},
                action='batchUpdate')
    if r:
        return r['replies'][0]['addSheet']['properties']['sheetId']
    return None

def write_row(tab, row_num, values):
    r = gws_run(
        {'spreadsheetId': SID, 'range': f"'{tab}'!A{row_num}", 'valueInputOption': 'RAW'},
        {'values': [values]}
    )
    ok = r and 'updatedRows' in r
    if not ok:
        print(f"  FAIL {tab} R{row_num}")
    return ok

# ── 删旧的配置详情，新建5个表页签 ──
# 先获取现有 sheetId
r = gws_run({'spreadsheetId': SID, 'fields': 'sheets.properties'}, action='get')
existing = {s['properties']['title']: s['properties']['sheetId'] for s in r['sheets']}
print("现有页签:", list(existing.keys()))

for name in ['2112', '2115', '2135', '2013', '2011']:
    if name not in existing:
        sid2 = add_sheet(name)
        print(f"  新建 {name}: {sid2}")
    else:
        print(f"  已有 {name}")

# 删旧的配置详情
if '配置详情' in existing:
    gws_run({'spreadsheetId': SID},
            {'requests': [{'deleteSheet': {'sheetId': existing['配置详情']}}]},
            action='batchUpdate')
    print("  删除 配置详情")

# ── 数据 ──
pay = '[{"pay_type":"gplay","product_id":"ape_0499_cd_an"},{"pay_type":"ios","product_id":"ape_0499_cd_ios"},{"pay_type":"alipayv2","product_id":"ape_0499_cd_ali"},{"pay_type":"weixin","product_id":"ape_0499_cd_weixin"},{"pay_type":"huaweihms","product_id":"ape_0499_cd_huawei"},{"pay_type":"weixinh5","product_id":"ape_0499_cd_weixinh5"},{"pay_type":"xiaomi","product_id":"ape_0499_cd_xiaomi"},{"pay_type":"oppo","product_id":"ape_0499_cd_oppo"},{"pay_type":"ninegame","product_id":"ape_0499_cd_ninegame"},{"pay_type":"main","product_id":"ape_0499_cd_cn_group_main"},{"pay_type":"flexion","product_id":"ape_0499_cd_an"},{"pay_type":"aggregate","product_id":"ape_0499_cd_aggregate"},{"pay_type":"huaweihms_oversea","product_id":"ape_0499_cd_huaweihms_oversea"},{"pay_type":"catappult","product_id":"ape_0499_cd_an"}]'
schema = '{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,55]}'
cond_ph = '[{"typ":"recharge_actv","id":{待替换1},"val":1},{"typ":"recharge_actv","id":{待替换2},"val":1},{"typ":"recharge_actv","id":{待替换3},"val":1},{"typ":"recharge_actv","id":{待替换4},"val":1},{"typ":"recharge_actv","id":{待替换5},"val":1},{"typ":"recharge_actv","id":{待替换6},"val":1},{"typ":"recharge_actv","id":{待替换7},"val":1}]'
day4 = [('item',11117068,25),('item',11116402,2),('item',11117024,2),('item',11118501,2),('material',19345010,1)]
ids_2013 = [2013511219,2013511220,2013511221,2013511222,2013511223]
ids_2011 = [2011500755,2011500756,2011500757,2011500758,2011500759]
ids_2135 = [21359463,21359464,21359465,21359466,21359467]

# ── 2112（1行）──
print("\n写 2112...")
row_2112 = [
    '21127718','异族大富翁-每日礼包','event_gird_gacha_daily','0','49997',
    '{待替换:父活动ID}',
    '{"op":"ge","typ":"building","id":{待替换:建筑ID},"val":5}',
    '{"group_label":"LC_EVENT_2026monoploy_gacha","label":"LC_EVENT_2026monoploy_gacha","title":"LC_EVENT_2026monoploy_gacha"}',
    '[{"typ":"task","id":211587376},{"typ":"package","id":21359463},{"typ":"package","id":21359464},{"typ":"package","id":21359465},{"typ":"package","id":21359466},{"typ":"package","id":21359467}]',
    '{"rule":"LC_EVENT_sci_gacha_daily_packge_rule"}',
    '21191319','1','""','{待替换:Banner路径}','1','0','0','{待替换:A_INT_show_hud}',
    '0','[]','""','0','""','0','0'
]
write_row('2112', 1, row_2112)

# ── 2115（1行）──
print("写 2115...")
row_2115 = [
    '0','211587376','复活节异族每日gacha-累计购买每日礼包',
    '{"op":"and","args":[{"op":"ge","typ":"actvstarttime","val":0},{"op":"ge","typ":"building","id":111811,"val":3}]}',
    '{"cat":101412163,"arg":{"ids":[2013511219,2013511220,2013511221,2013511222,2013511223]},"val":5,"op":"ge"}',
    '0',
    '[{"asset":{"typ":"item","id":11112900,"val":200},"setting":{"serial_number":5,"ishighlight":false}}]',
    'LC_EVENT_easter_gacha_daily_pkg_tips',
    '{"lc":"LC_IAP_gird_gacha_daily_packge","order":1}',
    '{}','99999','0','{}','0','""','0','0','0'
]
write_row('2115', 1, row_2115)

# ── 2135（5行）──
print("写 2135...")
for i in range(5):
    row = [str(ids_2135[i]), f'异族大富翁-每日礼包-第{i+1}天', str(ids_2011[i]),
           '{}','[]','0','""','NULL','NULL','{}','1','0','NULL']
    write_row('2135', i+1, row)

# ── 2013（5行，每行单独写）──
print("写 2013...")
for i in range(5):
    typ, iid, ival = day4[i]
    content = (f'[{{"asset":{{"typ":"item","id":11112765,"val":16}},"setting":{{"serial_number":5,"ishighlight":false}}}},'
               f'{{"asset":{{"typ":"{typ}","id":{iid},"val":{ival}}},"setting":{{"serial_number":4,"ishighlight":false}}}},'
               f'{{"asset":{{"typ":"item","id":11114316,"val":1}},"setting":{{"serial_number":2,"ishighlight":false}}}},'
               f'{{"asset":{{"typ":"xp","id":11161002,"val":1250}},"setting":{{"serial_number":1,"ishighlight":false}}}}]')
    row = [
        str(ids_2013[i]),'normal',str(ids_2011[i]),'2014001',
        f'2026异族大富翁-每日礼包-第{i+1}天','LC_EVENT_2026monoploy_gacha','','4.99',
        pay,'{"limit_cnt":1,"limit_type":"period"}','1','1250','25150',
        '[]','[]','[]','[]',content,'[]','[{"typ":"roi","tag":2,"val":25000}]',
        '0','','','{}','0','','','','{}','0','[]'
    ]
    write_row('2013', i+1, row)

# ── 2011（5行）──
print("写 2011...")
for i in range(5):
    row = [
        str(ids_2011[i]), f'异族大富翁GACHA-每日礼包-第{i+1}天',
        'special','normal','','False', schema, str(9991+i),
        f'{{"normal":[{{"actv_id":21127718,"day":{i+1}}}]}}',
        '{}','{}', cond_ph, '1','{}','common','0','','0','','0'
    ]
    write_row('2011', i+1, row)

print("\n完成")
