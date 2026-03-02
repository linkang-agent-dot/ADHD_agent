"""
捕获并分析API响应
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def capture_api():
    """捕获API响应的原始内容"""
    
    test_url = "https://cn.fifaaddict.com/fo4db/pidkjgwqwkky"
    
    print("=" * 60)
    print("捕获API响应原始内容")
    print("=" * 60)
    
    api_responses = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN"
        )
        page = await context.new_page()
        
        # 捕获所有响应的原始内容
        async def on_response(response):
            url = response.url
            
            # 只关注api2请求
            if 'api2' in url:
                print(f"\n发现API2请求: {url}")
                try:
                    # 获取响应体
                    body = await response.body()
                    text = body.decode('utf-8')
                    print(f"响应长度: {len(text)} 字符")
                    print(f"前200字符: {text[:200]}")
                    
                    api_responses.append({
                        'url': url,
                        'body': text
                    })
                except Exception as e:
                    print(f"获取响应体失败: {e}")
        
        page.on('response', on_response)
        
        print(f"\n访问: {test_url}")
        await page.goto(test_url, timeout=60000)
        await asyncio.sleep(5)
        
        await browser.close()
    
    # 分析API响应
    if api_responses:
        print("\n" + "=" * 60)
        print("分析API响应")
        print("=" * 60)
        
        for resp in api_responses:
            body = resp['body']
            
            # 保存原始响应
            with open("api_response_raw.txt", "w", encoding="utf-8") as f:
                f.write(body)
            print(f"\n原始响应已保存到 api_response_raw.txt")
            
            # 尝试解析
            # 看起来可能是JavaScript代码或特殊格式
            if body.startswith('{') or body.startswith('['):
                try:
                    data = json.loads(body)
                    print("成功解析为JSON")
                    print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])
                except:
                    print("不是标准JSON格式")
            
            # 检查是否是JSONP
            if '(' in body and body.strip().endswith(')'):
                print("可能是JSONP格式")
                # 提取JSON部分
                start = body.find('(')
                end = body.rfind(')')
                if start != -1 and end != -1:
                    json_str = body[start+1:end]
                    try:
                        data = json.loads(json_str)
                        print("JSONP解析成功!")
                        print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])
                    except:
                        print("JSONP解析失败")


if __name__ == "__main__":
    asyncio.run(capture_api())
