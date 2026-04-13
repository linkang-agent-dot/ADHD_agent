import subprocess, json

GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

# Test the exact data for the failing sheet
test_data = [
    ['X2节日-第一期循环（前35天）甘特图'],
    ['策略：不改变X2基本节日循环，新增已验证P2形式，预期新增ARPC +7.8'],
    [],
    ['分类', '付费模块', '开发类型', '负责人', '活动ID', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', '备注'],
    ['累充', '累充', '复用', 'liusiyi', '211201012', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
]

params = json.dumps({
    'spreadsheetId': SPREADSHEET_ID,
    'range': '前期循环-甘特!A1',
    'valueInputOption': 'USER_ENTERED'
}, ensure_ascii=False)
body = json.dumps({'values': test_data}, ensure_ascii=False)

result = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update',
     '--params', params, '--json', body],
    capture_output=True
)
stdout = result.stdout.decode('utf-8', errors='replace')
stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''

open(r'C:\ADHD_agent\_tmp_debug_stdout.txt', 'w', encoding='utf-8').write(stdout)
open(r'C:\ADHD_agent\_tmp_debug_stderr.txt', 'w', encoding='utf-8').write(stderr)

print(f"rc={result.returncode} stdout_len={len(stdout)} stderr_len={len(stderr)}")
print(f"body_len={len(body)}")
