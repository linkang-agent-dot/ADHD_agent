import subprocess
import json
import os
import sys

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'

def gws(sub, *args, params=None, body=None):
    cmd = [GWS_CMD] + list(sub.split()) + list(args)
    if params:
        cmd += ['--params', json.dumps(params, ensure_ascii=False)]
    if body:
        cmd += ['--json', json.dumps(body, ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print(f"ERR: {r.stderr[:200]}", file=sys.stderr)
        return None
    try:
        return json.loads(r.stdout)
    except:
        return None

# ── 1. 创建新表格 ──
res = gws('sheets spreadsheets create', body={'properties': {'title': '2026异族大富翁-每日礼包 配置汇总'}})
sid = res['spreadsheetId']
print(f"新建表格 ID: {sid}")
print(f"链接: https://docs.google.com/spreadsheets/d/{sid}/edit")

default_sheet_id = res['sheets'][0]['properties']['sheetId']

# ── 2. 添加页签 ──
def add_sheet(name):
    r = gws('sheets spreadsheets batchUpdate', params={'spreadsheetId': sid},
            body={'requests': [{'addSheet': {'properties': {'title': name}}}]})
    return r['replies'][0]['addSheet']['properties']['sheetId']

loc_sheet_id   = add_sheet('本地化')
config_sheet_id = add_sheet('配置详情')

# 删掉默认 Sheet1
gws('sheets spreadsheets batchUpdate', params={'spreadsheetId': sid},
    body={'requests': [{'deleteSheet': {'sheetId': default_sheet_id}}]})

# ── 3. 写入本地化 ──
LC_HEADER = [['LC Key', '中文', 'English', '备注']]
LC_DATA = [
    ['LC_EVENT_2026monoploy_gacha', '大富翁每日礼包', 'Alien Tycoon Daily Pack',
     '2112 group_label/label/title；2013 显示名'],
    ['LC_EVENT_easter_gacha_daily_pkg_tips', '累计购买大富翁每日礼包5次', 'Purchase the Alien Tycoon Daily Pack 5 times in total',
     '2115 任务提示文本（复活节key沿用，内容可按需调整）'],
    ['LC_EVENT_sci_gacha_daily_packge_rule', '（沿用云上探宝原文）', '（沿用云上探宝原文）',
     '2112 col10 rule key，不换'],
    ['LC_IAP_gird_gacha_daily_packge', '（沿用原文）', '（沿用原文）',
     '2115 col9 tab标签，不换'],
    ['LC_ITEM_monopoly_monster_dice', '（已有）', '（已有）',
     '1111 骰子道具名，不用新增'],
    ['LC_ITEM_monopoly_monster_dice_desc', '（已有）', '（已有）',
     '1111 骰子道具描述，不用新增'],
]

def write_range(sheet_title, range_a1, values):
    gws('sheets spreadsheets values update', params={
        'spreadsheetId': sid,
        'range': f"'{sheet_title}'!{range_a1}",
        'valueInputOption': 'RAW'
    }, body={'values': values})

write_range('本地化', 'A1', LC_HEADER + LC_DATA)

# ── 4. 写入配置详情 ──
SEP = ['']  # 空行分隔

ROWS = []

# 2112
ROWS += [['【2112】activity_config（1行）',
          '⚠️ 父活动ID/建筑ID/Banner/A_INT_show_hud 待填']]
ROWS += [['A_INT_id','名称','组件','col4','col5','父活动ID','前置条件','LC(col8)',
          'content','rule','2119','col12','col13','Banner','col15','col16','col17',
          'A_INT_show_hud','col19','col20','col21','col22','col23','col24','col25']]
ROWS += [['21127718','异族大富翁-每日礼包','event_gird_gacha_daily','0','49997',
          '{待替换:父活动ID}',
          '{"op":"ge","typ":"building","id":{待替换:建筑ID},"val":5}',
          '{"group_label":"LC_EVENT_2026monoploy_gacha","label":"LC_EVENT_2026monoploy_gacha","title":"LC_EVENT_2026monoploy_gacha"}',
          '[{"typ":"task","id":211587376},{"typ":"package","id":21359463},{"typ":"package","id":21359464},{"typ":"package","id":21359465},{"typ":"package","id":21359466},{"typ":"package","id":21359467}]',
          '{"rule":"LC_EVENT_sci_gacha_daily_packge_rule"}','21191319','1','""',
          '{待替换:Banner图片路径}','1','0','0','{待替换:A_INT_show_hud}',
          '0','[]','""','0','""','0','0']]
ROWS += [SEP]

# 2115
ROWS += [['【2115】activity_task（1行）']]
ROWS += [['0','A_INT_id','任务名','前置条件','完成条件','col6','奖励','tips LC','tab LC',
          'col10','col11','col12','col13','col14','col15','col16','col17','col18']]
ROWS += [['0','211587376','复活节异族每日gacha-累计购买每日礼包',
          '{"op":"and","args":[{"op":"ge","typ":"actvstarttime","val":0},{"op":"ge","typ":"building","id":111811,"val":3}]}',
          '{"cat":101412163,"arg":{"ids":[2013511219,2013511220,2013511221,2013511222,2013511223]},"val":5,"op":"ge"}',
          '0',
          '[{"asset":{"typ":"item","id":11112900,"val":200},"setting":{"serial_number":5,"ishighlight":false}}]',
          'LC_EVENT_easter_gacha_daily_pkg_tips',
          '{"lc":"LC_IAP_gird_gacha_daily_packge","order":1}',
          '{}','99999','0','{}','0','""','0','0','0']]
ROWS += [SEP]

# 2135
ROWS += [['【2135】activity_package（5行）']]
ROWS += [['A_INT_id','名称','2011 ID','col4','col5','col6','col7','col8','col9','col10','col11','col12','col13']]
for day, pkg_id, iap_id in [
    (1,21359463,2011500755),(2,21359464,2011500756),(3,21359465,2011500757),
    (4,21359466,2011500758),(5,21359467,2011500759)]:
    ROWS += [[str(pkg_id), f'异族大富翁-每日礼包-第{day}天', str(iap_id),
              '{}','[]','0','""','NULL','NULL','{}','1','0','NULL']]
ROWS += [SEP]

# 2013
ROWS += [['【2013】iap_config（5行）— 每天 serial_number:4 道具不同']]
ROWS += [['A_INT_id','type','2011 ID','分类','名称','LC key','空','价格','支付渠道','限购','...','...','...','...','content','...','ROI','...']]
pay = '[{"pay_type":"gplay","product_id":"ape_0499_cd_an"},{"pay_type":"ios","product_id":"ape_0499_cd_ios"},{"pay_type":"alipayv2","product_id":"ape_0499_cd_ali"},{"pay_type":"weixin","product_id":"ape_0499_cd_weixin"},{"pay_type":"huaweihms","product_id":"ape_0499_cd_huawei"},{"pay_type":"weixinh5","product_id":"ape_0499_cd_weixinh5"},{"pay_type":"xiaomi","product_id":"ape_0499_cd_xiaomi"},{"pay_type":"oppo","product_id":"ape_0499_cd_oppo"},{"pay_type":"ninegame","product_id":"ape_0499_cd_ninegame"},{"pay_type":"main","product_id":"ape_0499_cd_cn_group_main"},{"pay_type":"flexion","product_id":"ape_0499_cd_an"},{"pay_type":"aggregate","product_id":"ape_0499_cd_aggregate"},{"pay_type":"huaweihms_oversea","product_id":"ape_0499_cd_huaweihms_oversea"},{"pay_type":"catappult","product_id":"ape_0499_cd_an"}]'
day4_items = [
    ('item','11117068',25),('item','11116402',2),('item','11117024',2),
    ('item','11118501',2),('material','19345010',1)
]
ids_2013 = [2013511219,2013511220,2013511221,2013511222,2013511223]
ids_2011 = [2011500755,2011500756,2011500757,2011500758,2011500759]
for day in range(1,6):
    typ, iid, ival = day4_items[day-1]
    content = (f'[{{"asset":{{"typ":"item","id":11112765,"val":16}},"setting":{{"serial_number":5,"ishighlight":false}}}},'
               f'{{"asset":{{"typ":"{typ}","id":{iid},"val":{ival}}},"setting":{{"serial_number":4,"ishighlight":false}}}},'
               f'{{"asset":{{"typ":"item","id":11114316,"val":1}},"setting":{{"serial_number":2,"ishighlight":false}}}},'
               f'{{"asset":{{"typ":"xp","id":11161002,"val":1250}},"setting":{{"serial_number":1,"ishighlight":false}}}}]')
    ROWS += [[str(ids_2013[day-1]),'normal',str(ids_2011[day-1]),'2014001',
              f'2026异族大富翁-每日礼包-第{day}天','LC_EVENT_2026monoploy_gacha','','4.99',
              pay,'{"limit_cnt":1,"limit_type":"period"}','1','1250','25150',
              '[]','[]','[]','[]',content,'[]','[{"typ":"roi","tag":2,"val":25000}]',
              '0','','','{}','0','','','','{}','0','[]']]
ROWS += [SEP]

# 2011
ROWS += [['【2011】iap_product（5行）— actv_condition 累充ID待替换']]
ROWS += [['A_INT_id','名称','type','sub_type','空','is_hide','schema','sort',
          'actv_id_day','空','空','actv_condition(待填)','购买上限','空','tag','...']]
schema = '{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,55]}'
cond_placeholder = '[{"typ":"recharge_actv","id":{待替换1},"val":1},{"typ":"recharge_actv","id":{待替换2},"val":1},{"typ":"recharge_actv","id":{待替换3},"val":1},{"typ":"recharge_actv","id":{待替换4},"val":1},{"typ":"recharge_actv","id":{待替换5},"val":1},{"typ":"recharge_actv","id":{待替换6},"val":1},{"typ":"recharge_actv","id":{待替换7},"val":1}]'
for day in range(1,6):
    ROWS += [[str(ids_2011[day-1]),f'异族大富翁GACHA-每日礼包-第{day}天','special','normal','','False',
              schema,str(9990+day),f'{{"normal":[{{"actv_id":21127718,"day":{day}}}]}}',
              '{}','{}',cond_placeholder,'1','{}','common','0','','0','','0']]

# 写配置
write_range('配置详情', 'A1', ROWS)

# 写本地化格式化
print(f"\n✅ 写入完成")
print(f"表格链接: https://docs.google.com/spreadsheets/d/{sid}/edit")
