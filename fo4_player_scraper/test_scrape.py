"""
快速测试脚本 - 验证能否从 FIFAaddict 获取球员数据
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def test_single_player():
    """测试爬取单个球员数据"""
    
    # 一个传奇时刻球员的URL（马拉多纳）
    test_url = "https://cn.fifaaddict.com/fo4db/pidkjgwqwkky"  # 凯恩 26TY
    
    print("=" * 60)
    print("FC Online 球员数据爬取测试")
    print("=" * 60)
    
    async with async_playwright() as p:
        print("\n启动浏览器...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN"
        )
        page = await context.new_page()
        
        # 监听网络请求
        api_responses = []
        
        async def capture_response(response):
            url = response.url
            if "api" in url.lower() or "player" in url.lower() or "stat" in url.lower():
                try:
                    content_type = response.headers.get("content-type", "")
                    if "json" in content_type or "javascript" in content_type:
                        try:
                            data = await response.json()
                            api_responses.append({"url": url, "data": data})
                        except:
                            pass
                except:
                    pass
        
        page.on("response", capture_response)
        
        print(f"\n访问球员页面: {test_url}")
        await page.goto(test_url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3)  # 等待JS渲染
        
        # 获取页面标题
        title = await page.title()
        print(f"页面标题: {title}")
        
        # 尝试获取球员名
        try:
            h1 = await page.query_selector("h1")
            if h1:
                name = await h1.inner_text()
                print(f"球员名: {name}")
        except:
            pass
        
        # 获取能力值
        print("\n尝试获取能力值...")
        
        # 方法1: 直接从页面获取
        stats = await page.evaluate('''() => {
            const result = {};
            
            // 查找所有可能包含能力值的元素
            const statNames = [
                'sprintspeed', 'acceleration', 'finishing', 'shotpower',
                'longshots', 'positioning', 'volleys', 'penalties',
                'shortpassing', 'vision', 'crossing', 'longpassing',
                'freekickaccuracy', 'curve', 'dribbling', 'ballcontrol',
                'agility', 'balance', 'reactions', 'marking',
                'standingtackle', 'interceptions', 'headingaccuracy',
                'slidingtackle', 'strength', 'stamina', 'aggression',
                'jumping', 'composure'
            ];
            
            for (const stat of statNames) {
                // 尝试查找包含该属性的元素
                const elems = document.querySelectorAll(`[class*="${stat}"], [data-stat="${stat}"]`);
                for (const elem of elems) {
                    // 查找相邻的数值元素
                    const sibling = elem.nextElementSibling;
                    if (sibling) {
                        const text = sibling.innerText || sibling.textContent;
                        const num = parseInt(text);
                        if (!isNaN(num) && num > 0 && num < 200) {
                            result[stat] = num;
                            break;
                        }
                    }
                    // 或者数值在元素内部
                    const text = elem.innerText || elem.textContent;
                    const match = text.match(/\\d+/);
                    if (match) {
                        const num = parseInt(match[0]);
                        if (num > 0 && num < 200) {
                            result[stat] = num;
                            break;
                        }
                    }
                }
            }
            
            // 尝试获取OVR
            const ovrElem = document.querySelector('[class*="ovr"], [class*="overall"]');
            if (ovrElem) {
                const match = ovrElem.innerText.match(/\\d+/);
                if (match) result['ovr'] = parseInt(match[0]);
            }
            
            return result;
        }''')
        
        print(f"从页面获取的能力值: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        
        # 方法2: 查看API响应
        print(f"\n捕获到 {len(api_responses)} 个API响应:")
        for resp in api_responses[:5]:
            print(f"  - {resp['url'][:80]}...")
        
        # 方法3: 获取页面HTML中的数据
        print("\n查找页面中的数据结构...")
        
        # 查找script标签中的数据
        script_data = await page.evaluate('''() => {
            const scripts = document.querySelectorAll('script');
            for (const script of scripts) {
                const text = script.textContent;
                // 查找包含球员数据的JSON
                if (text.includes('sprintspeed') || text.includes('acceleration')) {
                    // 尝试提取JSON
                    const match = text.match(/\\{[^{}]*sprintspeed[^{}]*\\}/);
                    if (match) {
                        try {
                            return JSON.parse(match[0]);
                        } catch {}
                    }
                }
            }
            return null;
        }''')
        
        if script_data:
            print(f"从script标签获取: {json.dumps(script_data, indent=2, ensure_ascii=False)[:500]}")
        
        # 方法4: 获取所有显示的数值元素
        all_stats = await page.evaluate('''() => {
            const result = [];
            // 查找所有列表项或带数字的元素
            const items = document.querySelectorAll('li, div[class*="stat"], span[class*="stat"]');
            for (const item of items) {
                const text = item.innerText.trim();
                // 匹配 "属性名 数值" 的模式
                const match = text.match(/([a-z]+)\\s*(\\d+)/i);
                if (match) {
                    result.push({name: match[1], value: parseInt(match[2])});
                }
            }
            return result.slice(0, 50);  // 限制返回数量
        }''')
        
        if all_stats:
            print(f"\n找到的数值元素: {len(all_stats)} 个")
            for stat in all_stats[:10]:
                print(f"  {stat['name']}: {stat['value']}")
        
        # 截图保存
        screenshot_path = "test_screenshot.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n页面截图已保存: {screenshot_path}")
        
        await browser.close()
    
    print("\n测试完成!")


if __name__ == "__main__":
    asyncio.run(test_single_player())
