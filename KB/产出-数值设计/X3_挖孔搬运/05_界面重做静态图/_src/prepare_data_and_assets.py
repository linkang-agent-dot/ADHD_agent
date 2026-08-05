# -*- coding: utf-8 -*-
"""出图前置：从 03_横转竖demo\挖孔竖屏交互demo_v02_单文件版.html 里
   ①抽真配置数据 D5.json  ②抽内嵌 base64 图素到 assets\
   （只读 demo，不修改它）。跑完再跑 gen.py，然后跑 shot.ps1。"""
import re, os, json, base64

DEMO = r'C:\ADHD_agent\KB\产出-数值设计\X3_挖孔搬运\03_横转竖demo\挖孔竖屏交互demo_v02_单文件版.html'
HERE = os.path.dirname(os.path.abspath(__file__))
s = open(DEMO, encoding='utf-8').read()

# ① 真配置数据（P2 配置仓导出，含 120 关 / 40 宝物 / 8 名次段 / 5 兑换 / 23 礼包）
m = re.search(r'const D5=(\{.*?\});\n', s, re.S)
json.dump(json.loads(m.group(1)), open(os.path.join(HERE, '..', 'D5.json'), 'w', encoding='utf-8'),
          ensure_ascii=False)

# ② 图素：X3 官方 UI 件 35 + P2 玩法图素 45 + 宝物 DK 40 + 道具图标 12
os.makedirs(os.path.join(HERE, 'assets'), exist_ok=True)
n = 0
for k, mime, b64 in re.findall(r'"([A-Za-z0-9_.]+)"\s*:\s*"data:image/([a-z+]+);base64,([A-Za-z0-9+/=]+)"', s):
    name = k if '.' in k else '%s.%s' % (k, 'jpg' if mime == 'jpeg' else mime)
    open(os.path.join(HERE, 'assets', name), 'wb').write(base64.b64decode(b64))
    n += 1
print('assets:', n)
