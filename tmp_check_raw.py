import sys

fname = sys.argv[1]
target_line = int(sys.argv[2]) if len(sys.argv) > 2 else 8

with open(fname, 'rb') as f:
    content = f.read()

if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]

lines = content.split(b'\r\n')
# Show a few lines around target
for i in range(max(0, target_line-3), min(len(lines), target_line+3)):
    print(f'Line {i+1}: {repr(lines[i])}')
