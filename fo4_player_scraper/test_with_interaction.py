"""
测试页面交互后获取详细数据
"""

import asyncio
from playwright.async_api import async_playwright
import json
import re

async def test_interaction():
    """测试页面交互"""
    
    test_url = "https://cn.fifaaddict.com/fo4db/pidkjgwqwkky"
    
    print("=" * 60)
    print("测试页面交互获取完整数据")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--window-size=1920,1080']
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN"
        )
        page = await context.new_page()
        
        # 监听所有网络请求
        api_data = []
        
        async def on_response(response):
            url = response.url
            if 'api' in url.lower() or 'stat' in url.lower() or 'player' in url.lower():
                try:
                    if 'json' in response.headers.get('content-type', ''):
                        data = await response.json()
                        api_data.append({'url': url, 'data': data})
                except:
                    pass
        
        page.on('response', on_response)
        
        print(f"\n访问: {test_url}")
        await page.goto(test_url, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(3)
        
        # 滚动页面触发更多加载
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(2)
        
        # 查看页面上是否有能力值显示
        print("\n分析页面能力值区域...")
        
        # 获取页面HTML并查找能力值模式
        html = await page.content()
        
        # 查找包含数字的能力值模式
        patterns = [
            r'sprintspeed["\s:]+(\d+)',
            r'acceleration["\s:]+(\d+)',
            r'finishing["\s:]+(\d+)',
            r'shotpower["\s:]+(\d+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f"找到模式 {pattern[:20]}...: {matches}")
        
        # 检查是否有隐藏的数据
        hidden_data = await page.evaluate('''() => {
            const result = {};
            
            // 检查所有script标签
            const scripts = document.querySelectorAll('script');
            for (const script of scripts) {
                const text = script.textContent || script.innerText;
                
                // 查找能力值数据
                if (text.includes('sprintspeed') || text.includes('finishing')) {
                    // 尝试提取JSON
                    const jsonMatches = text.match(/\\{[^{}]*"sprintspeed"[^{}]*\\}/g);
                    if (jsonMatches) {
                        result.jsonMatches = jsonMatches.slice(0, 3);
                    }
                }
                
                // 查找数组格式的能力值
                if (text.includes('[') && (text.includes('134') || text.includes('131'))) {
                    const arrMatches = text.match(/\\[[\\d,\\s]+\\]/g);
                    if (arrMatches) {
                        result.arrayMatches = arrMatches.filter(m => m.length > 20 && m.length < 500).slice(0, 5);
                    }
                }
            }
            
            return result;
        }''')
        
        if hidden_data:
            print(f"\n隐藏数据: {json.dumps(hidden_data, ensure_ascii=False, indent=2)}")
        
        # 尝试从页面描述中提取能力值
        description = await page.query_selector('meta[name="description"]')
        if description:
            desc_content = await description.get_attribute('content')
            print(f"\n页面描述: {desc_content}")
            
            # 从描述中提取能力值
            stat_matches = re.findall(r'([^：]+)[：:]?\s*(\d+)', desc_content)
            if stat_matches:
                print("从描述中提取的能力值:")
                for name, value in stat_matches:
                    print(f"  {name.strip()}: {value}")
        
        # 查看API数据
        if api_data:
            print(f"\n捕获到 {len(api_data)} 个API请求")
            for item in api_data:
                print(f"  - {item['url'][:60]}...")
        
        # 保存页面截图
        await page.screenshot(path="interaction_test.png", full_page=True)
        print("\n截图已保存: interaction_test.png")
        
        # 保持浏览器打开以便手动查看
        print("\n保持浏览器打开15秒...")
        await asyncio.sleep(15)
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_interaction())
