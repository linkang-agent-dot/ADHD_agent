# -*- coding: utf-8 -*-
import json, datetime, secrets, pathlib
SKILL_ROOT = r'C:\Users\linkang\.claude\skills\x3-media'
out_dir = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\队徽48_勋章FINAL'
pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
anchors = [r'C:\ADHD_agent\.cache_wc_anchor\BRA_badge.png',
           r'C:\ADHD_agent\.cache_wc_anchor\JPN_badge.png',
           r'C:\ADHD_agent\.cache_wc_anchor\CRO_badge.png',
           r'C:\ADHD_agent\.cache_wc_anchor\FRA_badge.png',
           r'C:\ADHD_agent\.cache_wc_anchor\AUS_badge.png']

# 已OK不跑: BRA ARG JPN AUS CRO FRA
done = {'BRA', 'ARG', 'JPN', 'AUS', 'CRO', 'FRA'}
# 全48国 名+国旗描述
ALL = {
 'MEX': ('Mexico', 'green-white-red vertical bands with central eagle-and-snake emblem'),
 'ALG': ('Algeria', 'green and white with a red crescent and star'),
 'AUT': ('Austria', 'red-white-red horizontal bands'),
 'BEL': ('Belgium', 'black-yellow-red vertical bands'),
 'BIH': ('Bosnia and Herzegovina', 'blue with a yellow triangle and white stars'),
 'CAN': ('Canada', 'red-white-red with a central red maple leaf'),
 'CIV': ('Ivory Coast', 'orange-white-green vertical bands'),
 'COD': ('DR Congo', 'sky blue with a yellow star and red diagonal stripe'),
 'COL': ('Colombia', 'yellow top half, blue and red horizontal bands'),
 'CPV': ('Cape Verde', 'blue with white-red stripes and a ring of yellow stars'),
 'CUW': ('Curacao', 'blue with a yellow stripe and white stars'),
 'CZE': ('Czechia', 'white and red with a blue triangle'),
 'ECU': ('Ecuador', 'yellow-blue-red horizontal bands with central emblem'),
 'EGY': ('Egypt', 'red-white-black horizontal bands with a gold eagle'),
 'ENG': ('England', 'white with a red St George cross'),
 'GER': ('Germany', 'black-red-gold horizontal bands'),
 'GHA': ('Ghana', 'red-gold-green horizontal bands with a black star'),
 'HAI': ('Haiti', 'blue and red horizontal bands'),
 'IRN': ('Iran', 'green-white-red horizontal bands with central emblem'),
 'IRQ': ('Iraq', 'red-white-black horizontal bands with green script'),
 'JOR': ('Jordan', 'black-white-green horizontal bands with a red triangle and white star'),
 'KOR': ('South Korea', 'white with a red-blue taegeuk circle and black trigrams'),
 'KSA': ('Saudi Arabia', 'green with white Arabic script and a sword'),
 'MAR': ('Morocco', 'red with a green pentagram star'),
 'NED': ('Netherlands', 'red-white-blue horizontal bands (orange accent)'),
 'NOR': ('Norway', 'red with a blue-and-white Scandinavian cross'),
 'NZL': ('New Zealand', 'black with a white silver fern'),
 'PAN': ('Panama', 'white-red-blue quarters with stars'),
 'PAR': ('Paraguay', 'red-white-blue horizontal bands with emblem'),
 'POR': ('Portugal', 'green and red with the Portuguese armillary emblem'),
 'QAT': ('Qatar', 'maroon and white with a serrated divide'),
 'RSA': ('South Africa', 'green-gold-red-blue-black-white Y-shape multicolor'),
 'SCO': ('Scotland', 'navy blue with a white diagonal saltire cross'),
 'SEN': ('Senegal', 'green-yellow-red vertical bands with a green star'),
 'SUI': ('Switzerland', 'red with a bold white cross'),
 'SWE': ('Sweden', 'blue with a yellow Scandinavian cross'),
 'TUN': ('Tunisia', 'red with a white circle and red crescent-star'),
 'TUR': ('Turkey', 'red with a white crescent and star'),
 'URU': ('Uruguay', 'sky-blue and white stripes with a sun emblem'),
 'USA': ('United States', 'stars and stripes red-white-blue'),
 'UZB': ('Uzbekistan', 'blue-white-green horizontal bands with crescent and stars'),
 'ENG2': None,  # placeholder guard
}
ALL.pop('ENG2', None)

todo = {c: v for c, v in ALL.items() if c not in done}

def build(name, flag):
    return ('Reference images are Brazil and Japan World Cup team medals/emblems. Following the same style and format, '
            'generate another World Cup team emblem for %s: a soccer ball combined with %s flag shield. '
            'The shield is purely %s own flag (%s). Centered, ~80%% of frame, white background.') % (name, name, name, flag)

ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
mani = {}
for code, (name, flag) in todo.items():
    tid = ts + '-' + secrets.token_hex(2)
    params = {'model': 'gpt', 'reference_images': anchors, 'output_dir': out_dir,
              'output_filename': 'WC_Badge_%s.png' % code, 'postprocess': 'remove_background_then_256', 'aspect_ratio': '1:1'}
    task = {'schema_version': 1, 'task_id': tid, 'status': 'pending', 'type': 'general',
            'user_prompt': build(name, flag), 'params': params, 'started_at': None, 'finished_at': None,
            'result': {'saved_to': [], 'history_lines_appended': 0, 'backend': None}, 'error': None, 'retry_count': 0, 'created_by': 'main-agent'}
    pathlib.Path(SKILL_ROOT, 'state', 'tasks', tid + '.json').write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding='utf-8')
    mani[code] = tid
pathlib.Path(out_dir, '_manifest.json').write_text(json.dumps(mani, ensure_ascii=False, indent=2), encoding='utf-8')
print('待跑', len(todo), '队')
for c, t in mani.items():
    print(c, t)
