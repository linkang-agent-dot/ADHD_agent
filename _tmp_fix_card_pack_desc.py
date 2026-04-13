# -*- coding: utf-8 -*-
"""修正复活节卡包描述 — 将科技节游戏名替换为复活节对应游戏名"""

import subprocess, json, os, shutil, sys

GWS_CMD = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'gws.cmd')
if not os.path.exists(GWS_CMD):
    GWS_CMD = shutil.which('gws') or 'gws'

os.environ.setdefault('GOOGLE_WORKSPACE_PROJECT_ID', 'calm-repeater-489707-n1')

SPREADSHEET_ID = '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw'
SHEET_NAME = '卡册key（复活节）+本地化'

# 需要更新的 K2:L9（Col K=中文，Col L=英文）
# 顺序：R2 core_decipher_name, R3 core_decipher_desc,
#       R4 underground_name,   R5 underground_desc,
#       R6 lucky_marble_name,  R7 lucky_marble_desc,
#       R8 coin_pusher_name,   R9 coin_pusher_desc
UPDATES = [
    # [中文, 英文]
    ["矿洞寻宝卡包",
     "Mine Treasure Hunt Card Pack"],
    ['乐趣无穷的游戏主题卡包，至少获得一张\u201c矿洞寻宝\u201d游戏卡片。',
     'A fun-filled game-themed card pack. Guarantees at least one "Mine Treasure Hunt" game card.'],
    ["极速飞车卡包",
     "Speed Racing Card Pack"],
    ['惊喜满满的游戏主题卡包，至少获得一张\u201c极速飞车\u201d游戏卡片。',
     'A surprise-filled game-themed card pack. Guarantees at least one "Speed Racing" game card.'],
    ["彩蛋大亨卡包",
     "Easter Tycoon Card Pack"],
    ['好运相随的游戏主题卡包，至少获得一张\u201c彩蛋大亨\u201d游戏卡片。',
     'A luck-filled game-themed card pack. Guarantees at least one "Easter Tycoon" game card.'],
    ["异族探秘卡包",
     "Alien Exploration Card Pack"],
    ['珍宝云集的游戏主题卡包，至少获得一张\u201c异族探秘\u201d游戏卡片。',
     'A treasure-filled game-themed card pack. Guarantees at least one "Alien Exploration" game card.'],
]

RANGE = f"'{SHEET_NAME}'!K2:L9"

params = {
    "spreadsheetId": SPREADSHEET_ID,
    "range": RANGE,
    "valueInputOption": "RAW"
}

body = {
    "range": RANGE,
    "majorDimension": "ROWS",
    "values": UPDATES
}

print(f"[写入] range={RANGE}")
print(f"[写入] 共 {len(UPDATES)} 行")
for i, row in enumerate(UPDATES, 2):
    print(f"  R{i}: {row[0][:20]}... | {row[1][:30]}...")

result = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update',
     '--params', json.dumps(params, ensure_ascii=False),
     '--json', json.dumps(body, ensure_ascii=False)],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)

if result.returncode != 0:
    print(f"[错误] stderr: {result.stderr}")
    sys.exit(1)

print(f"[成功] stdout: {result.stdout[:300]}")
print("✅ 卡包描述已修正写入 GSheet")
