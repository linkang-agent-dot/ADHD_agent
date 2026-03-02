"""
获取完整的34项能力值
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def get_full_stats():
    """获取完整能力值数据"""
    
    # 测试一个传奇时刻球员
    test_url = "https://cn.fifaaddict.com/fo4db/pidkjgwqwkky"
    
    print("=" * 60)
    print("获取完整34项能力值")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN"
        )
        page = await context.new_page()
        
        print(f"\n访问: {test_url}")
        await page.goto(test_url, timeout=60000)
        await asyncio.sleep(5)
        
        # 获取NUXT数据
        nuxt_data = await page.evaluate('''() => {
            return window.__NUXT__;
        }''')
        
        # 检查数据结构
        if nuxt_data and 'data' in nuxt_data and len(nuxt_data['data']) > 0:
            player_data = nuxt_data['data'][0]
            print("\n数据结构中的键:")
            print(list(player_data.keys()))
            
            if 'foPlayerPre' in player_data:
                pre = player_data['foPlayerPre']
                print("\nfoPlayerPre 中的键:")
                print(list(pre.keys()))
        
        # 在页面上点击"登录"后可能会显示更多数据
        # 或者需要查看网络请求
        
        # 监听更多数据请求
        print("\n等待页面加载完整数据...")
        
        # 获取页面上的所有能力值数据
        full_stats = await page.evaluate('''() => {
            const result = {};
            
            // 从NUXT获取
            if (window.__NUXT__ && window.__NUXT__.data && window.__NUXT__.data[0]) {
                const data = window.__NUXT__.data[0];
                
                // 复制所有数据
                result.nuxt_data = data;
            }
            
            // 从DOM获取能力值
            const statList = {};
            const allLis = document.querySelectorAll('li');
            
            for (const li of allLis) {
                const className = li.className.toLowerCase();
                const text = li.textContent.trim();
                
                // 检查是否是能力值相关的li
                const statNames = [
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
                
                for (const stat of statNames) {
                    if (className.includes(stat)) {
                        // 找数值
                        const numMatch = text.match(/\\d+/);
                        if (numMatch) {
                            statList[stat] = parseInt(numMatch[0]);
                        }
                    }
                }
            }
            
            result.dom_stats = statList;
            
            // 尝试从Vue/Nuxt组件获取
            const app = document.querySelector('#__nuxt') || document.querySelector('#app');
            if (app && app.__vue__) {
                result.has_vue = true;
                // Vue 2
                try {
                    const vm = app.__vue__;
                    if (vm.$data) {
                        result.vue_data = JSON.parse(JSON.stringify(vm.$data));
                    }
                } catch (e) {
                    result.vue_error = e.message;
                }
            }
            
            return result;
        }''')
        
        # 保存完整数据
        with open("full_stats_data.json", "w", encoding="utf-8") as f:
            json.dump(full_stats, f, ensure_ascii=False, indent=2)
        print(f"\n完整数据已保存到 full_stats_data.json")
        
        # 提取关键信息
        if 'nuxt_data' in full_stats:
            nuxt = full_stats['nuxt_data']
            if 'foPlayerPre' in nuxt:
                pre = nuxt['foPlayerPre']
                print(f"\n球员: {pre.get('name')}")
                print(f"赛季: {pre.get('season_full')}")
                print(f"OVR: {pre.get('ovr_ori')}")
                
                # 看看有没有详细能力值
                for key in pre.keys():
                    if 'stat' in key.lower() or 'attr' in key.lower():
                        print(f"{key}: {pre[key]}")
        
        if 'dom_stats' in full_stats:
            print(f"\nDOM获取的能力值: {len(full_stats['dom_stats'])} 项")
            for k, v in sorted(full_stats['dom_stats'].items()):
                print(f"  {k}: {v}")
        
        # 截图
        await page.screenshot(path="full_page.png", full_page=True)
        print("\n截图已保存: full_page.png")
        
        await asyncio.sleep(5)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(get_full_stats())
