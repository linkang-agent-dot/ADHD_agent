import subprocess
import json
import os
import sys

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SID = '1l96i3_rJL8-7sLUy2pTUATiNZBxkzQjF_JA_emdJGto'
TAB = '配置详情'

def write_rows(start_row, rows):
    if not rows:
        return True
    end_row = start_row + len(rows) - 1
    range_name = f"'{TAB}'!A{start_row}:AF{end_row}"
    params = json.dumps({
        'spreadsheetId': SID,
        'range': range_name,
        'valueInputOption': 'RAW'
    }, ensure_ascii=False)
    body = json.dumps({'values': rows}, ensure_ascii=False)
    r = subprocess.run(
        [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update',
         '--params', params, '--json', body],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if r.returncode != 0 or '"updatedRows"' not in r.stdout:
        print(f"  FAIL R{start_row}: {r.stderr[:150]}")
        return False
    print(f"  OK R{start_row}-{end_row} ({len(rows)} rows)")
    return True

# ── 数据定义 ──
pay = '[{"pay_type":"gplay","product_id":"ape_0499_cd_an"},{"pay_type":"ios","product_id":"ape_0499_cd_ios"},{"pay_type":"alipayv2","product_id":"ape_0499_cd_ali"},{"pay_type":"weixin","product_id":"ape_0499_cd_weixin"},{"pay_type":"huaweihms","product_id":"ape_0499_cd_huawei"},{"pay_type":"weixinh5","product_id":"ape_0499_cd_weixinh5"},{"pay_type":"xiaomi","product_id":"ape_0499_cd_xiaomi"},{"pay_type":"oppo","product_id":"ape_0499_cd_oppo"},{"pay_type":"ninegame","product_id":"ape_0499_cd_ninegame"},{"pay_type":"main","product_id":"ape_0499_cd_cn_group_main"},{"pay_type":"flexion","product_id":"ape_0499_cd_an"},{"pay_type":"aggregate","product_id":"ape_0499_cd_aggregate"},{"pay_type":"huaweihms_oversea","product_id":"ape_0499_cd_huaweihms_oversea"},{"pay_type":"catappult","product_id":"ape_0499_cd_an"}]'
schema = '{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,55]}'
cond_ph = '[{"typ":"recharge_actv","id":{r1},"val":1},{"typ":"recharge_actv","id":{r2},"val":1},{"typ":"recharge_actv","id":{r3},"val":1},{"typ":"recharge_actv","id":{r4},"val":1},{"typ":"recharge_actv","id":{r5},"val":1},{"typ":"recharge_actv","id":{r6},"val":1},{"typ":"recharge_actv","id":{r7},"val":1}]'
day4_items = [('item',11117068,25),('item',11116402,2),('item',11117024,2),('item',11118501,2),('material',19345010,1)]
ids_2013 = [2013511219,2013511220,2013511221,2013511222,2013511223]
ids_2011 = [2011500755,2011500756,2011500757,2011500758,2011500759]
ids_2135 = [21359463,21359464,21359465,21359466,21359467]

row = 1

# ── 2112 ──
print("写 2112...")
write_rows(row, [['【2112】activity_config（1行）  ⚠️ 父活动ID/建筑ID/Banner/hud 待填']]); row+=1
write_rows(row, [['A_INT_id','名称','组件type','col4','col5','父活动ID','前置条件filter','label(col8)','content','rule','2119 hud','col12','col13','Banner路径','col15','col16','col17','A_INT_show_hud','col19']]); row+=1
write_rows(row, [['21127718','异族大富翁-每日礼包','event_gird_gacha_daily','0','49997',
    '{待替换:父活动ID}',
    '{"op":"ge","typ":"building","id":{待替换:建筑ID},"val":5}',
    '{"group_label":"LC_EVENT_2026monoploy_gacha","label":"LC_EVENT_2026monoploy_gacha","title":"LC_EVENT_2026monoploy_gacha"}',
    '[{"typ":"task","id":211587376},{"typ":"package","id":21359463},{"typ":"package","id":21359464},{"typ":"package","id":21359465},{"typ":"package","id":21359466},{"typ":"package","id":21359467}]',
    '{"rule":"LC_EVENT_sci_gacha_daily_packge_rule"}','21191319','1','""',
    '{待替换:Banner路径}','1','0','0','{待替换:A_INT_show_hud}','0 [] "" 0 "" 0 0']]); row+=1
write_rows(row, [['']]); row+=1

# ── 2115 ──
print("写 2115...")
write_rows(row, [['【2115】activity_task（1行）']]); row+=1
write_rows(row, [['col1','A_INT_id','任务名','前置条件','完成条件','col6','奖励','tips LC','tab LC','col10~末']]); row+=1
write_rows(row, [['0','211587376','复活节异族每日gacha-累计购买每日礼包',
    '{"op":"and","args":[{"op":"ge","typ":"actvstarttime","val":0},{"op":"ge","typ":"building","id":111811,"val":3}]}',
    '{"cat":101412163,"arg":{"ids":[2013511219,2013511220,2013511221,2013511222,2013511223]},"val":5,"op":"ge"}',
    '0',
    '[{"asset":{"typ":"item","id":11112900,"val":200},"setting":{"serial_number":5,"ishighlight":false}}]',
    'LC_EVENT_easter_gacha_daily_pkg_tips',
    '{"lc":"LC_IAP_gird_gacha_daily_packge","order":1}',
    '{} 99999 0 {} 0 "" 0 0 0']]); row+=1
write_rows(row, [['']]); row+=1

# ── 2135 ──
print("写 2135...")
write_rows(row, [['【2135】activity_package（5行）']]); row+=1
write_rows(row, [['A_INT_id','名称','2011 ID','col4','col5','col6','col7','col8','col9','col10','col11','col12','col13']]); row+=1
for i, day in enumerate(range(1,6)):
    write_rows(row, [[str(ids_2135[i]), f'异族大富翁-每日礼包-第{day}天', str(ids_2011[i]),
        '{}','[]','0','""','NULL','NULL','{}','1','0','NULL']]); row+=1
write_rows(row, [['']]); row+=1

# ── 2013 ──
print("写 2013...")
write_rows(row, [['【2013】iap_config（5行）']]); row+=1
write_rows(row, [['A_INT_id','type','2011 ID','分类','名称','LC key','空','价格','支付渠道(简写)','限购','价值','GEM价值','...','...','content','...','ROI']]); row+=1
for i, day in enumerate(range(1,6)):
    typ, iid, ival = day4_items[i]
    content = (f'[{{"asset":{{"typ":"item","id":11112765,"val":16}},"setting":{{"serial_number":5,"ishighlight":false}}}},'
               f'{{"asset":{{"typ":"{typ}","id":{iid},"val":{ival}}},"setting":{{"serial_number":4,"ishighlight":false}}}},'
               f'{{"asset":{{"typ":"item","id":11114316,"val":1}},"setting":{{"serial_number":2,"ishighlight":false}}}},'
               f'{{"asset":{{"typ":"xp","id":11161002,"val":1250}},"setting":{{"serial_number":1,"ishighlight":false}}}}]')
    write_rows(row, [[str(ids_2013[i]),'normal',str(ids_2011[i]),'2014001',
        f'2026异族大富翁-每日礼包-第{day}天','LC_EVENT_2026monoploy_gacha','','4.99',
        'gplay/ios/alipay/weixin/huawei/xiaomi/oppo/ninegame/main/flexion/aggregate/...',
        '{"limit_cnt":1,"limit_type":"period"}','1','1250','25150',
        '','','','',content,'','[{"typ":"roi","tag":2,"val":25000}]']]); row+=1
write_rows(row, [['']]); row+=1

# ── 2011 ──
print("写 2011...")
write_rows(row, [['【2011】iap_product（5行）  ⚠️ actv_condition 累充ID 7个待填']]); row+=1
write_rows(row, [['A_INT_id','名称','type','sub_type','空','is_hide','schema','sort','actv_id+day','col10','col11','actv_condition(待填)','购买上限','col13','tag','col15~末']]); row+=1
for i, day in enumerate(range(1,6)):
    write_rows(row, [[str(ids_2011[i]), f'异族大富翁GACHA-每日礼包-第{day}天',
        'special','normal','','False', schema, str(9990+day),
        f'{{"normal":[{{"actv_id":21127718,"day":{day}}}]}}',
        '{}','{}', cond_ph, '1','{}','common','0 "" 0 "" 0']]); row+=1

print(f"\n全部写入完成，共 {row-1} 行")
