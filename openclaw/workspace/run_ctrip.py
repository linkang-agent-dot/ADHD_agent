import subprocess, sys, os

p = subprocess.Popen(
    [sys.executable, r'C:\ADHD_agent\openclaw\workspace\ctrip_tracker.py', '--quick'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT
)

output = b''
for chunk in p.stdout:
    output += chunk

p.wait()

# Write raw output to file
with open(r'C:\Users\linkang\.openclaw\workspace\uploads\ctrip_output.txt', 'wb') as f:
    f.write(output)

with open(r'C:\Users\linkang\.openclaw\workspace\uploads\ctrip_output.txt', 'r', encoding='utf-8') as f:
    print(f.read())

print(f'\nExit code: {p.returncode}')
