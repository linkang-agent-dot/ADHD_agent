"""
专门捕获球员数据API
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def capture_player_api():
    """捕获球员数据API"""
    
    test_url = "https://cn.fifaaddict.com/fo4db/pidkjgwqwkky"
    
    print("=" * 60)
    print("捕获球员数据API")
    print("=" * 60)
    
    player_api_data = None
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN"
        )
        page = await context.new_page()
        
        # 只捕获球员API
        async def on_response(response):
            nonlocal player_api_data
            url = response.url
            
            # 只关注fo4pid请求
            if 'fo4pid=' in url:
                print(f"\n发现球员API: {url}")
                try:
                    body = await response.body()
                    text = body.decode('utf-8')
                    print(f"响应长度: {len(text)} 字符")
                    
                    # 解析JSON
                    data = json.loads(text)
                    player_api_data = data
                    
                    # 保存
                    with open("player_api_data.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print("已保存到 player_api_data.json")
                    
                except Exception as e:
                    print(f"处理失败: {e}")
        
        page.on('response', on_response)
        
        print(f"\n访问: {test_url}")
        await page.goto(test_url, timeout=60000)
        await asyncio.sleep(5)
        
        await browser.close()
    
    # 分析数据结构
    if player_api_data:
        print("\n" + "=" * 60)
        print("API数据结构分析")
        print("=" * 60)
        
        print(f"\n顶层键: {list(player_api_data.keys())}")
        
        for key, value in player_api_data.items():
            if isinstance(value, list):
                print(f"\n{key}: 列表，{len(value)} 个元素")
                if len(value) > 0:
                    if isinstance(value[0], dict):
                        print(f"  元素键: {list(value[0].keys())[:15]}...")
            elif isinstance(value, dict):
                print(f"\n{key}: 字典，{len(value)} 个键")
                print(f"  键: {list(value.keys())[:15]}...")
            else:
                print(f"\n{key}: {type(value).__name__} = {str(value)[:100]}")


if __name__ == "__main__":
    asyncio.run(capture_player_api())
