import re

with open(r'C:\ADHD_agent\_tmp_task_qa.json', 'rb') as f:
    raw = f.read()

# File starts with UTF-16 BOM (FF FE), so decode as utf-16
content_utf16 = raw.decode('utf-16')

# The content was originally UTF-8 JSON, but PS captured it as UTF-16
# So each original UTF-8 byte became a separate UTF-16 character
# To recover: encode back to bytes treating chars as byte values, then decode as utf-8

# Test with first garbled comment
# "鐜╁绱鐧婚檰澶╂暟" -> should be "玩家累计登陆天数"

test = "鐜╁绱鐧婚檰澶╂暟"
# Re-encode as latin-1 to get back raw bytes
try:
    recovered = test.encode('latin-1').decode('utf-8')
    print(f'Recovered: {recovered}')
except Exception as e:
    print(f'Latin-1 failed: {e}')

# Try direct bytes
try:
    test_bytes = test.encode('utf-16-le')
    # Take every other byte (the low bytes of each UTF-16 char)
    raw_bytes = bytes(test_bytes[i] for i in range(0, len(test_bytes), 2))
    print(f'Raw bytes: {raw_bytes}')
    print(f'UTF-8 decode: {raw_bytes.decode("utf-8")}')
except Exception as e:
    print(f'Failed: {e}')
