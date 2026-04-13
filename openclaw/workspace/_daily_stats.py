import sys, json, os, re
sys.stdout.reconfigure(encoding='utf-8')

inbox = r'C:\ADHD_agent\openclaw\workspace\cursor_inbox'
outbox = r'C:\ADHD_agent\openclaw\workspace\cursor_outbox'

total = 0; done = 0; error = 0
for f in os.listdir(inbox):
    if f.startswith('task_20260402') and f.endswith('.json') and not f.startswith('_'):
        total += 1
        try:
            d = json.load(open(os.path.join(inbox, f), encoding='utf-8'))
            st = d.get('status', '')
            if st == 'done':
                done += 1
            elif st == 'error':
                error += 1
        except:
            pass

log_path = r'C:\ADHD_agent\openclaw\workspace\daemon_autoexec.log'
lines = open(log_path, 'r', encoding='utf-8', errors='replace').readlines()
today_lines = [l for l in lines if '2026-04-02' in l]
if today_lines:
    first = re.search(r'\d{4}-\d{2}-\d{2} (\d{2}:\d{2})', today_lines[0])
    last = re.search(r'\d{4}-\d{2}-\d{2} (\d{2}:\d{2})', today_lines[-1])
    if first and last:
        print(f'daemon运行区间: {first.group(1)} ~ {last.group(1)}')

print(f'今日任务: {total} 个 | 完成 {done} | 失败 {error}')
print()

print('--- 完成的任务 ---')
for f in sorted(os.listdir(outbox)):
    if f.startswith('task_20260402') and f.endswith('.json') and not f.startswith('_'):
        try:
            raw = open(os.path.join(outbox, f), 'rb').read().decode('utf-8', errors='replace')
            d = json.loads(raw)
            if d.get('status') == 'done':
                title = d.get('title', '?')
                print(f'  ✓ {title}')
        except:
            pass
