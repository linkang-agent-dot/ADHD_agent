# -*- coding: utf-8 -*-
import json, datetime, secrets, pathlib, shutil, os

SKILL_ROOT = r'C:\Users\linkang\.claude\skills\x3-media'
final_dir = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\头像框_48_FINAL'
pathlib.Path(final_dir).mkdir(parents=True, exist_ok=True)
ringtex_dir = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\头像框_国旗球_环纹理试点'

anchor_paradigm = ringtex_dir + r'\Img_Player_AvatarFrame_WC_JPN.png'
anchor_skeleton = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\头像框_X3风格试点\Img_Player_AvatarFrame_WC_France_mid_v2_alt1.png'

# 已做4队 -> 拷进FINAL
done = {'JPN': 'Img_Player_AvatarFrame_WC_JPN.png', 'FRA': 'Img_Player_AvatarFrame_WC_FRA.png',
        'CRO': 'Img_Player_AvatarFrame_WC_CRO.png', 'BRA': 'Img_Player_AvatarFrame_WC_BRA.png'}
for code, fn in done.items():
    src = os.path.join(ringtex_dir, fn)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(final_dir, fn))

# 44队: code -> (队名, 环色队色优先, 国旗球描述)
teams = {
 'MEX': ('Mexico', 'green with subtle red and white accent', 'MEXICO flag: green-white-red vertical panels with eagle emblem in white center, simplified'),
 'RSA': ('South Africa', 'green', 'SOUTH AFRICA flag: distinctive Y-shape green gold red blue black white, simplified bold'),
 'KOR': ('South Korea', 'red', 'SOUTH KOREA flag: white ball with red-blue taegeuk circle and black trigrams'),
 'CZE': ('Czechia', 'red', 'CZECH flag: white-red horizontal with a blue triangle'),
 'CAN': ('Canada', 'red', 'CANADA flag: red-white-red with a red maple leaf center'),
 'BIH': ('Bosnia', 'royal blue', 'BOSNIA flag: blue with a yellow triangle and white stars'),
 'QAT': ('Qatar', 'maroon', 'QATAR flag: maroon and white with serrated divide'),
 'SUI': ('Switzerland', 'red', 'SWITZERLAND flag: red ball with a bold white cross center'),
 'MAR': ('Morocco', 'red', 'MOROCCO flag: red with a green pentagram star center'),
 'HAI': ('Haiti', 'royal blue', 'HAITI flag: blue and red horizontal bands'),
 'SCO': ('Scotland', 'navy blue', 'SCOTLAND flag: navy with a white diagonal X cross saltire'),
 'USA': ('United States', 'navy blue', 'USA flag: stars and stripes, simplified bold'),
 'PAR': ('Paraguay', 'red', 'PARAGUAY flag: red-white-blue horizontal bands'),
 'AUS': ('Australia', 'golden yellow with green', 'AUSTRALIA flag: blue with union jack and white stars, simplified'),
 'TUR': ('Turkey', 'red', 'TURKEY flag: red ball with a white crescent and star'),
 'GER': ('Germany', 'black with red and gold', 'GERMANY flag: black-red-gold horizontal bands'),
 'CUW': ('Curacao', 'royal blue', 'CURACAO flag: blue with yellow horizontal stripe and white stars'),
 'CIV': ('Ivory Coast', 'orange with green', 'IVORY COAST flag: orange-white-green vertical bands'),
 'ECU': ('Ecuador', 'golden yellow', 'ECUADOR flag: yellow-blue-red horizontal bands with emblem, simplified'),
 'NED': ('Netherlands', 'bright orange', 'NETHERLANDS flag: red-white-blue horizontal bands, ring is team ORANGE'),
 'SWE': ('Sweden', 'golden yellow with blue', 'SWEDEN flag: blue ball with a yellow cross'),
 'TUN': ('Tunisia', 'red', 'TUNISIA flag: red ball with white circle and red crescent-star'),
 'BEL': ('Belgium', 'red with black and yellow', 'BELGIUM flag: black-yellow-red vertical bands'),
 'EGY': ('Egypt', 'red', 'EGYPT flag: red-white-black with gold eagle center'),
 'IRN': ('Iran', 'green with red', 'IRAN flag: green-white-red horizontal with central emblem, simplified'),
 'NZL': ('New Zealand', 'white with black', 'NEW ZEALAND flag: black with a white silver fern'),
 'ESP': ('Spain', 'red with gold', 'SPAIN flag: red-yellow-red horizontal with crest, simplified'),
 'CPV': ('Cape Verde', 'royal blue', 'CAPE VERDE flag: blue with white-red stripes and ring of yellow stars, simplified'),
 'KSA': ('Saudi Arabia', 'green', 'SAUDI flag: green ball with white Arabic script and sword, simplified'),
 'URU': ('Uruguay', 'sky blue', 'URUGUAY flag: white-blue stripes with sun emblem, simplified'),
 'SEN': ('Senegal', 'green', 'SENEGAL flag: green-yellow-red vertical bands with green star'),
 'IRQ': ('Iraq', 'white with red and green', 'IRAQ flag: red-white-black horizontal with green script'),
 'NOR': ('Norway', 'red', 'NORWAY flag: red with a blue-and-white cross'),
 'ALG': ('Algeria', 'green with white', 'ALGERIA flag: green-white with red crescent and star'),
 'AUT': ('Austria', 'white with red', 'AUSTRIA flag: red-white-red horizontal bands'),
 'JOR': ('Jordan', 'white with black and green', 'JORDAN flag: black-white-green with red triangle and white star'),
 'POR': ('Portugal', 'red with green', 'PORTUGAL flag: green-red with national emblem, simplified'),
 'COD': ('DR Congo', 'royal blue', 'DR CONGO flag: sky blue with yellow star and red diagonal stripe'),
 'UZB': ('Uzbekistan', 'royal blue', 'UZBEKISTAN flag: blue-white-green horizontal with crescent and stars'),
 'COL': ('Colombia', 'golden yellow', 'COLOMBIA flag: yellow-blue-red horizontal bands'),
 'ENG': ('England', 'white with red', 'ENGLAND flag: white ball with a bold red cross St George'),
 'GHA': ('Ghana', 'red with gold and green', 'GHANA flag: red-gold-green horizontal with black star center'),
 'PAN': ('Panama', 'red with blue', 'PANAMA flag: four quarters white red blue with stars'),
}

def build_prompt(name, ringcolor, ball):
    return (
        'X3 game circular avatar frame, World Cup / soccer theme, ' + name + '. '
        'Use reference image 1 as the EXACT target paradigm (a detailed team-color ring with gradient, metallic sheen and engraved texture, plus a flag-textured soccer ball at bottom-center) and reference image 2 for the skeleton/ornaments (top gold crest with gem, side gold diamond clips, bottom gold wings). '
        'RING band = ' + ringcolor + ' team color, but NOT flat: give it a smooth light-to-dark gradient, subtle metallic sheen and rim light, and fine engraved geometric texture so it reads as an ornate metal-and-enamel frame (match reference image 1 ring quality). Slim gold edge trim. '
        'Bottom-center soccer ball = ' + ball + '. Keep cel-shaded glossy highlight on top of the ball so it reads as a real ball, not a flat 2D disc. The flag-ball is the single identity focus; national identity must be instantly recognizable. '
        'Keep the EXACT same skeleton, layout, proportions and ornaments and clean cel-shaded X3 game-UI art style. Square 1:1, circular hollow center fully transparent for avatar, fully transparent background, NO text, NO national flag cloth draped over the frame, NO scene background, readable at 256x256.'
    )

manifest = {'template': '环=队色渐变纹理+国旗球+骨架不变', 'paradigm': anchor_paradigm, 'done4': list(done), 'teams': {}}
mapping = {}
ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
for code, (name, rc, ball) in teams.items():
    tid = ts + '-' + secrets.token_hex(2)
    params = {'model': 'gpt', 'reference_images': [anchor_paradigm, anchor_skeleton],
              'output_dir': final_dir, 'output_filename': 'Img_Player_AvatarFrame_WC_' + code + '.png',
              'postprocess': 'uiframe_transparent', 'aspect_ratio': '1:1'}
    task = {'schema_version': 1, 'task_id': tid, 'status': 'pending', 'type': 'uiframe',
            'user_prompt': build_prompt(name, rc, ball), 'params': params,
            'started_at': None, 'finished_at': None,
            'result': {'saved_to': [], 'history_lines_appended': 0, 'backend': None},
            'error': None, 'retry_count': 0, 'created_by': 'main-agent'}
    pathlib.Path(SKILL_ROOT, 'state', 'tasks', tid + '.json').write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding='utf-8')
    manifest['teams'][code] = {'task_id': tid, 'name': name, 'status': 'pending'}
    mapping[code] = tid

pathlib.Path(final_dir, '_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print('TOTAL', len(teams), 'tasks')
print(json.dumps(mapping, ensure_ascii=False))
