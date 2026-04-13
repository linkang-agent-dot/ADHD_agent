"""测试数据源：GitHub API + 小红书搜索"""
import sys
import requests
import json
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

# === GitHub: 最近7天更新的AI热门仓库 ===
print('=== GitHub Trending AI ===')
week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
url = 'https://api.github.com/search/repositories'
params = {
    'q': f'AI agent OR LLM tool pushed:>{week_ago} stars:>500',
    'sort': 'stars',
    'order': 'desc',
    'per_page': 5
}
try:
    r = requests.get(url, params=params, timeout=15,
                     headers={'Accept': 'application/vnd.github.v3+json'})
    data = r.json()
    for item in data.get('items', [])[:5]:
        name = item['full_name']
        stars = item['stargazers_count']
        desc = (item.get('description') or '')[:80]
        link = item['html_url']
        updated = item.get('pushed_at', '')[:10]
        print(f'  {name} | {stars} stars | updated {updated}')
        print(f'    {desc}')
        print(f'    {link}')
        print()
except Exception as e:
    print(f'  GitHub API error: {e}')

# === 小红书: 通过搜索引擎抓取 ===
print('=== 小红书 AI 热点 ===')
# 用 Bing search API 搜索小红书AI相关内容
bing_url = 'https://www.bing.com/search'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
try:
    r = requests.get(bing_url, params={'q': '小红书 AI工具 提效 2026 site:xiaohongshu.com'},
                     headers=headers, timeout=15)
    print(f'  Bing status: {r.status_code}, length: {len(r.text)}')
    # 看看能不能提取到小红书链接
    import re
    xhs_links = re.findall(r'https?://www\.xiaohongshu\.com/\S+', r.text)
    print(f'  找到 {len(xhs_links)} 个小红书链接')
    for link in xhs_links[:3]:
        print(f'    {link[:80]}')
except Exception as e:
    print(f'  Bing search error: {e}')
