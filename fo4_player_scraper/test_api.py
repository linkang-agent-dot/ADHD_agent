"""
测试获取 FIFAaddict API 数据
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def capture_api_data():
    """捕获并解析API数据"""
    
    test_url = "https://cn.fifaaddict.com/fo4db/pidkjgwqwkky"
    
    print("=" * 60)
    print("捕获 FIFAaddict API 数据")
    print("=" * 60)
    
    api_data = None
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(locale="zh-CN")
        page = await context.new_page()
        
        # 捕获所有响应
        async def handle_response(response):
            nonlocal api_data
            url = response.url
            
            if "api2" in url or "api" in url.lower():
                print(f"\n发现API: {url}")
                try:
                    data = await response.json()
                    api_data = data
                    print(f"数据类型: {type(data)}")
                    if isinstance(data, dict):
                        print(f"键: {list(data.keys())[:20]}")
                except Exception as e:
                    print(f"解析失败: {e}")
        
        page.on("response", handle_response)
        
        print(f"\n访问: {test_url}")
        await page.goto(test_url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3)
        
        await browser.close()
    
    if api_data:
        print("\n" + "=" * 60)
        print("API 数据结构")
        print("=" * 60)
        
        # 保存完整数据
        with open("api_sample.json", "w", encoding="utf-8") as f:
            json.dump(api_data, f, ensure_ascii=False, indent=2)
        print(f"\n完整数据已保存到: api_sample.json")
        
        # 分析数据结构
        def analyze_structure(data, prefix="", max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return
            
            if isinstance(data, dict):
                for key, value in list(data.items())[:15]:
                    value_type = type(value).__name__
                    if isinstance(value, (dict, list)):
                        print(f"{prefix}{key}: {value_type}")
                        analyze_structure(value, prefix + "  ", max_depth, current_depth + 1)
                    else:
                        preview = str(value)[:50] if value else "null"
                        print(f"{prefix}{key}: {value_type} = {preview}")
            elif isinstance(data, list) and len(data) > 0:
                print(f"{prefix}[0]: {type(data[0]).__name__}")
                analyze_structure(data[0], prefix + "  ", max_depth, current_depth + 1)
        
        print("\n数据结构分析:")
        analyze_structure(api_data)
        
        # 提取关键数据
        if isinstance(api_data, dict):
            print("\n" + "=" * 60)
            print("关键数据提取")
            print("=" * 60)
            
            # 查找能力值相关字段
            stat_keys = ['sprintspeed', 'acceleration', 'finishing', 'shotpower', 
                        'positioning', 'stamina', 'ovr', 'stats', 'attributes']
            
            for key in stat_keys:
                if key in api_data:
                    print(f"\n{key}: {api_data[key]}")
            
            # 查找嵌套的能力值
            for key, value in api_data.items():
                if isinstance(value, dict) and any(s in str(value).lower() for s in ['sprint', 'finishing', 'shot']):
                    print(f"\n{key} 包含能力值数据:")
                    print(json.dumps(value, ensure_ascii=False, indent=2)[:500])
    
    return api_data


if __name__ == "__main__":
    data = asyncio.run(capture_api_data())
