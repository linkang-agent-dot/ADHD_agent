import sys, re
sys.stdout.reconfigure(encoding='utf-8')

idx = r'C:\Users\linkang\AppData\Local\cursor-agent\versions\2026.03.30-a5d3e17\index.js'
content = open(idx, 'r', encoding='utf-8', errors='replace').read()

patterns = [
    (r'api\d*\.cursor\.com[^\s"\'\\]{0,80}', 'Cursor API host'),
    (r'https://[^\s"\'\\]*openai[^\s"\'\\]{0,60}', 'OpenAI endpoint'),
    (r'https://[^\s"\'\\]*anthropic[^\s"\'\\]{0,60}', 'Anthropic endpoint'),
    (r'"claude[^"]{0,40}"', 'Claude model refs'),
    (r'"gpt[^"]{0,40}"', 'GPT model refs'),
    (r'"gemini[^"]{0,40}"', 'Gemini model refs'),
    (r'defaultModel[^\n]{0,100}', 'defaultModel'),
]

for pattern, label in patterns:
    matches = re.findall(pattern, content)
    if matches:
        unique = list(dict.fromkeys(matches))[:6]
        print(f'=== {label} ===')
        for m in unique:
            print(f'  {m[:120]}')
        print()
