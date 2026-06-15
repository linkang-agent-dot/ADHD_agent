import json, sys

history_line = {
    'ts': '2026-06-15T10:36:26+08:00',
    'type': 'march_emoji',
    'model': 'gpt-image-1',
    'saved_to': r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\应援表情48_脸彩\WC_FaceEmote_AUT.png',
    'backend': 'grfal',
    'task_id': '20260615-103626-7748'
}

history_path = r'C:\Users\linkang\.claude\skills\x3-media\state\history.jsonl'
with open(history_path, 'a', encoding='utf-8') as f:
    f.write(json.dumps(history_line, ensure_ascii=False) + '\n')

with open(r'C:\Users\linkang\.claude\skills\x3-media\state\_history_result_7748.txt', 'w', encoding='utf-8') as f:
    f.write('history appended OK\n')
