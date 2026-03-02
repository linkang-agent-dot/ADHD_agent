"""
直接从页面解析球员数据
"""

import asyncio
from playwright.async_api import async_playwright
import json
import re

async def extract_player_data():
    """直接从页面提取数据"""
    
    test_url = "https://cn.fifaaddict.com/fo4db/pidkjgwqwkky"
    
    print("=" * 60)
    print("从页面提取球员数据")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 显示浏览器
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN"
        )
        page = await context.new_page()
        
        print(f"\n访问: {test_url}")
        await page.goto(test_url, timeout=60000)
        await asyncio.sleep(5)  # 等待JS渲染
        
        # 获取页面标题
        title = await page.title()
        print(f"页面标题: {title}")
        
        # 方法1: 从页面直接读取渲染后的能力值
        print("\n方法1: 读取渲染后的能力值...")
        
        stats = await page.evaluate('''() => {
            const result = {};
            
            // 能力值列表的英文名称
            const attrs = [
                'sprintspeed', 'acceleration', 'finishing', 'shotpower',
                'longshots', 'positioning', 'volleys', 'penalties',
                'shortpassing', 'vision', 'crossing', 'longpassing',
                'freekickaccuracy', 'curve', 'dribbling', 'ballcontrol',
                'agility', 'balance', 'reactions', 'marking',
                'standingtackle', 'interceptions', 'headingaccuracy',
                'slidingtackle', 'strength', 'stamina', 'aggression',
                'jumping', 'composure',
                'gkdiving', 'gkhandling', 'gkkicking', 'gkreflexes', 'gkpositioning'
            ];
            
            // 遍历查找每个属性
            for (const attr of attrs) {
                // 查找包含属性名的li元素
                const lis = document.querySelectorAll('li');
                for (const li of lis) {
                    const classes = li.className.toLowerCase();
                    if (classes.includes(attr)) {
                        // 找到后，获取数值
                        // 数值通常在相邻元素或子元素中
                        const text = li.textContent.trim();
                        const match = text.match(/(\\d+)/);
                        if (match) {
                            const num = parseInt(match[1]);
                            if (num > 0 && num < 200) {
                                result[attr] = num;
                            }
                        }
                    }
                }
            }
            
            return result;
        }''')
        
        print(f"获取到 {len(stats)} 个能力值:")
        for k, v in sorted(stats.items()):
            print(f"  {k}: {v}")
        
        # 方法2: 读取页面中的所有数字元素
        print("\n方法2: 分析页面结构...")
        
        page_structure = await page.evaluate('''() => {
            const result = {
                lists: [],
                statElements: []
            };
            
            // 找到所有ul/li结构
            const uls = document.querySelectorAll('ul');
            for (const ul of uls) {
                const items = [];
                const lis = ul.querySelectorAll('li');
                for (const li of lis) {
                    const text = li.textContent.trim();
                    const classes = li.className;
                    if (text.length < 50 && text.length > 0) {
                        items.push({text, classes});
                    }
                }
                if (items.length > 0 && items.length < 50) {
                    result.lists.push(items);
                }
            }
            
            // 找到所有带stat相关class的元素
            const statElems = document.querySelectorAll('[class*="stat"], [class*="attr"]');
            for (const elem of statElems) {
                const text = elem.textContent.trim();
                if (text.length < 30) {
                    result.statElements.push({
                        class: elem.className,
                        text: text
                    });
                }
            }
            
            return result;
        }''')
        
        print(f"找到 {len(page_structure['lists'])} 个列表")
        print(f"找到 {len(page_structure['statElements'])} 个stat元素")
        
        # 方法3: 截取整个页面的HTML分析
        print("\n方法3: 获取页面HTML片段...")
        
        # 获取能力值区域的HTML
        stat_html = await page.evaluate('''() => {
            // 尝试找到能力值区域
            const containers = document.querySelectorAll('[class*="stat"], [class*="attr"], ul');
            let relevantHtml = '';
            
            for (const container of containers) {
                const text = container.textContent.toLowerCase();
                if (text.includes('sprint') || text.includes('finishing') || 
                    text.includes('shot') || text.includes('passing')) {
                    relevantHtml += container.outerHTML + '\\n\\n';
                }
            }
            
            return relevantHtml.slice(0, 5000);  // 限制长度
        }''')
        
        if stat_html:
            print(f"能力值区域HTML长度: {len(stat_html)}")
            # 保存HTML用于分析
            with open("stat_html_sample.html", "w", encoding="utf-8") as f:
                f.write(stat_html)
            print("已保存到 stat_html_sample.html")
        
        # 方法4: 通过React/Vue的state获取数据
        print("\n方法4: 尝试获取框架数据...")
        
        framework_data = await page.evaluate('''() => {
            // 检查是否有React
            if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
                return {framework: 'React', hint: '页面使用React'};
            }
            // 检查Vue
            if (window.__VUE__) {
                return {framework: 'Vue', hint: '页面使用Vue'};
            }
            // 检查Next.js的数据
            if (window.__NEXT_DATA__) {
                return {framework: 'Next.js', data: window.__NEXT_DATA__};
            }
            // 检查Nuxt的数据
            if (window.__NUXT__) {
                return {framework: 'Nuxt', data: window.__NUXT__};
            }
            return {framework: 'Unknown'};
        }''')
        
        print(f"框架检测: {framework_data.get('framework', 'Unknown')}")
        if 'data' in framework_data:
            print("找到框架数据!")
            with open("framework_data.json", "w", encoding="utf-8") as f:
                json.dump(framework_data['data'], f, ensure_ascii=False, indent=2)
        
        # 方法5: 截图查看
        await page.screenshot(path="player_page.png", full_page=True)
        print("\n页面截图已保存: player_page.png")
        
        # 给用户一些时间查看页面
        print("\n保持浏览器打开10秒以便查看...")
        await asyncio.sleep(10)
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(extract_player_data())
