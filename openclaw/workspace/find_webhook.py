import re
content = open(r'C:\Users\linkang\.openclaw\workspace\MCP_CONFIG.md', 'r', encoding='utf-8').read()
m = re.search(r'https://open[^\s"\']+feishu[^\s"\']+', content)
print(m.group() if m else 'not found')
