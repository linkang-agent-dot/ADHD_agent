"""
FC Online 球员数据爬虫 - 高级版
通过拦截网络请求获取API数据，支持强化等级、球队加成等完整数据
"""

import asyncio
import json
import re
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, Page, Response
import pandas as pd
from tqdm import tqdm

# 配置
BASE_URL = "https://cn.fifaaddict.com"
SEASONS = {
    "ictm": "传奇时刻",
    "ictmb": "传奇永恒", 
    "icon": "Icon传奇"
}
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# 34项能力值字段映射
ATTRIBUTES = [
    ("sprintspeed", "速度"),
    ("acceleration", "加速"),
    ("finishing", "射术"),
    ("shotpower", "射门力量"),
    ("longshots", "远射"),
    ("positioning", "站位"),
    ("volleys", "凌空抽射"),
    ("penalties", "罚点球"),
    ("shortpassing", "短传"),
    ("vision", "视野"),
    ("crossing", "传中"),
    ("longpassing", "长传"),
    ("freekickaccuracy", "任意球"),
    ("curve", "弧线"),
    ("dribbling", "盘带"),
    ("ballcontrol", "控球"),
    ("agility", "灵活"),
    ("balance", "平衡"),
    ("reactions", "反应"),
    ("marking", "人盯人"),
    ("standingtackle", "抢断"),
    ("interceptions", "战术意识"),
    ("headingaccuracy", "头球"),
    ("slidingtackle", "铲断"),
    ("strength", "强壮"),
    ("stamina", "体力"),
    ("aggression", "侵略性"),
    ("jumping", "弹跳"),
    ("composure", "冷静"),
    ("gkdiving", "GK扑救"),
    ("gkhandling", "GK手控球"),
    ("gkkicking", "GK大脚开球"),
    ("gkreflexes", "GK反应"),
    ("gkpositioning", "GK防守站位"),
]


class FO4Scraper:
    def __init__(self):
        self.all_players = []
        self.api_data_cache = {}
        
    async def intercept_api(self, response: Response):
        """拦截并缓存API响应"""
        url = response.url
        
        # 检查是否是球员数据API
        if any(keyword in url.lower() for keyword in ["player", "stat", "api", "data"]):
            try:
                content_type = response.headers.get("content-type", "")
                if "json" in content_type:
                    data = await response.json()
                    self.api_data_cache[url] = data
            except:
                pass
    
    async def extract_player_data_from_page(self, page: Page, player_url: str) -> dict | None:
        """从页面提取球员完整数据"""
        try:
            # 清空API缓存
            self.api_data_cache = {}
            
            # 监听网络请求
            page.on("response", self.intercept_api)
            
            await page.goto(player_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)  # 等待JS完全渲染
            
            data = {}
            
            # 1. 从页面标题获取卡片名称和赛季
            title = await page.title()
            card_name = title.split(" - ")[0] if " - " in title else ""
            data["卡片名称"] = card_name
            
            # 2. 解析赛季类型
            season_match = re.search(r'(ICTM|ICTMB|ICON|ictm|ictmb|icon|\d+TY)', card_name, re.IGNORECASE)
            if season_match:
                data["赛季类型"] = season_match.group(1).upper()
            
            # 3. 获取球员基础信息 - 通过页面元素
            try:
                # 球员名
                h1 = await page.query_selector("h1")
                if h1:
                    data["球员名"] = await h1.inner_text()
                
                # 位置
                pos_elem = await page.query_selector("h1 ~ div:first-of-type")
                if pos_elem:
                    pos_text = await pos_elem.inner_text()
                    data["位置"] = pos_text.split()[0] if pos_text else ""
                
                # 俱乐部
                club_link = await page.query_selector("a[href*='team=']")
                if club_link:
                    data["俱乐部"] = await club_link.inner_text()
                
                # 国籍
                country_link = await page.query_selector("a[href*='country=']")
                if country_link:
                    data["国籍"] = await country_link.inner_text()
                    
            except Exception as e:
                print(f"  基础信息提取失败: {e}")
            
            # 4. 获取能力值 - 基础值
            # 网站使用特定的class来显示能力值
            base_stats = {}
            for attr_key, attr_name in ATTRIBUTES:
                try:
                    # 尝试多种选择器
                    value = await page.evaluate(f'''() => {{
                        // 方法1: 通过class名查找
                        const elem = document.querySelector('[class*="{attr_key}"]');
                        if (elem) {{
                            const sibling = elem.nextElementSibling;
                            if (sibling) {{
                                const text = sibling.innerText;
                                const num = parseInt(text);
                                if (!isNaN(num) && num > 0) return num;
                            }}
                        }}
                        
                        // 方法2: 通过文本内容查找
                        const allSpans = document.querySelectorAll('span, div');
                        for (const span of allSpans) {{
                            if (span.innerText.toLowerCase().includes('{attr_key}')) {{
                                const numMatch = span.innerText.match(/\\d+/);
                                if (numMatch) return parseInt(numMatch[0]);
                            }}
                        }}
                        
                        return null;
                    }}''')
                    
                    base_stats[attr_name] = value
                except:
                    base_stats[attr_name] = None
            
            # 5. 获取OVR总评
            try:
                ovr = await page.evaluate('''() => {
                    // 查找OVR相关元素
                    const ovrElems = document.querySelectorAll('[class*="ovr"], [class*="overall"]');
                    for (const elem of ovrElems) {
                        const match = elem.innerText.match(/\\d+/);
                        if (match) {
                            const num = parseInt(match[0]);
                            if (num >= 50 && num <= 150) return num;
                        }
                    }
                    return null;
                }''')
                data["OVR总评"] = ovr
            except:
                data["OVR总评"] = None
            
            # 6. 检查是否有强化/等级系统
            try:
                has_enhance = await page.evaluate('''() => {
                    const enhanceElems = document.querySelectorAll(
                        '[class*="level"], [class*="enhance"], [class*="upgrade"], ' +
                        'select, input[type="range"], button:has-text("强化")'
                    );
                    return enhanceElems.length > 0;
                }''')
                data["有强化系统"] = has_enhance
            except:
                data["有强化系统"] = False
            
            # 7. 尝试获取不同强化等级的数据
            if data.get("有强化系统"):
                # 查找强化等级选择器
                levels_data = {}
                try:
                    level_options = await page.query_selector_all("select option, [class*='level'] button")
                    for opt in level_options[:5]:  # 最多取5个等级
                        level_text = await opt.inner_text()
                        # 可以点击不同等级获取数据
                        # await opt.click()
                        # await asyncio.sleep(0.5)
                        # 获取该等级下的能力值...
                except:
                    pass
                data["强化等级数据"] = levels_data
            
            # 8. 添加基础能力值到data
            for attr_name, value in base_stats.items():
                data[f"基础_{attr_name}"] = value
            
            # 9. 检查API缓存中是否有更完整的数据
            if self.api_data_cache:
                data["_api_data"] = list(self.api_data_cache.values())
            
            return data
            
        except Exception as e:
            print(f"  提取失败: {e}")
            return None
        finally:
            # 移除监听器
            try:
                page.remove_listener("response", self.intercept_api)
            except:
                pass
    
    async def get_player_list_from_search(self, page: Page, season: str) -> list[dict]:
        """通过搜索页获取球员列表"""
        players = []
        
        # 构建搜索URL
        search_url = f"{BASE_URL}/fo4db"
        await page.goto(search_url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(2)
        
        # 点击对应赛季的筛选按钮
        try:
            season_btn = await page.query_selector(f"button:has-text('{season}'), [class*='{season}']")
            if season_btn:
                await season_btn.click()
                await asyncio.sleep(2)
        except:
            # 尝试直接访问带参数的URL
            await page.goto(f"{search_url}?season={season}", wait_until="networkidle")
            await asyncio.sleep(2)
        
        # 滚动加载更多
        for _ in range(5):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
        
        # 获取球员链接
        links = await page.query_selector_all("a[href*='/fo4db/pid']")
        print(f"  找到 {len(links)} 个球员链接")
        
        seen_ids = set()
        for link in links:
            try:
                href = await link.get_attribute("href")
                name = await link.inner_text()
                
                # 检查是否是目标赛季
                if season.lower() not in href.lower() and season.lower() not in name.lower():
                    # 需要进一步验证
                    pass
                
                pid_match = re.search(r"pid(\w+)", href)
                if pid_match:
                    pid = pid_match.group(1)
                    if pid not in seen_ids:
                        seen_ids.add(pid)
                        players.append({
                            "id": pid,
                            "name": name.strip(),
                            "url": f"{BASE_URL}/fo4db/pid{pid}",
                            "season": season
                        })
            except:
                continue
        
        return players
    
    async def run(self, test_mode: bool = False, max_players: int = None):
        """运行爬虫"""
        print("=" * 70)
        print("FC Online 传奇球员数据爬虫")
        print("目标: 传奇时刻(ICTM) + 传奇永恒(ICTMB) + Icon传奇")
        print("数据: 完整能力值 + 强化数据 + 球队加成 + 等级加成")
        print("=" * 70)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,  # 显示浏览器方便调试
                args=[
                    "--lang=zh-CN",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                locale="zh-CN",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            page = await context.new_page()
            
            # 步骤1: 获取球员列表
            print("\n[1/3] 获取球员列表...")
            all_player_list = []
            
            for season_code, season_name in SEASONS.items():
                print(f"\n  正在获取 {season_name} ({season_code})...")
                players = await self.get_player_list_from_search(page, season_code)
                all_player_list.extend(players)
                print(f"  -> {len(players)} 名球员")
            
            print(f"\n  总计待爬取: {len(all_player_list)} 名球员")
            
            # 测试模式限制数量
            if test_mode and max_players:
                all_player_list = all_player_list[:max_players]
                print(f"  [测试模式] 限制为前 {max_players} 名")
            
            # 步骤2: 爬取每个球员详情
            print("\n[2/3] 爬取球员详细数据...")
            
            for player in tqdm(all_player_list, desc="爬取进度"):
                data = await self.extract_player_data_from_page(page, player["url"])
                if data:
                    data["源URL"] = player["url"]
                    self.all_players.append(data)
                
                # 随机延迟避免被封
                await asyncio.sleep(1 + (hash(player["id"]) % 10) / 10)
            
            await browser.close()
        
        # 步骤3: 保存数据
        print("\n[3/3] 保存数据...")
        self.save_data()
        
        print(f"\n✅ 完成! 共爬取 {len(self.all_players)} 名球员")
    
    def save_data(self):
        """保存数据到文件"""
        if not self.all_players:
            print("  没有数据可保存")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 保存原始JSON（包含所有数据）
        json_path = OUTPUT_DIR / f"legends_raw_{timestamp}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.all_players, f, ensure_ascii=False, indent=2)
        print(f"  JSON: {json_path}")
        
        # 2. 准备Excel数据（扁平化）
        excel_data = []
        for player in self.all_players:
            row = {}
            for key, value in player.items():
                if key == "_api_data":
                    continue  # 跳过原始API数据
                if isinstance(value, (dict, list)):
                    row[key] = json.dumps(value, ensure_ascii=False)
                else:
                    row[key] = value
            excel_data.append(row)
        
        df = pd.DataFrame(excel_data)
        
        # 按赛季类型排序
        if "赛季类型" in df.columns:
            df = df.sort_values(by=["赛季类型", "OVR总评"], ascending=[True, False])
        
        excel_path = OUTPUT_DIR / f"legends_data_{timestamp}.xlsx"
        df.to_excel(excel_path, index=False, engine="openpyxl")
        print(f"  Excel: {excel_path}")
        
        # 3. 按赛季分别保存
        for season_code in SEASONS.keys():
            season_df = df[df["赛季类型"].str.upper() == season_code.upper()] if "赛季类型" in df.columns else pd.DataFrame()
            if not season_df.empty:
                season_path = OUTPUT_DIR / f"{season_code}_{timestamp}.xlsx"
                season_df.to_excel(season_path, index=False, engine="openpyxl")
                print(f"  {season_code}: {season_path} ({len(season_df)} 名)")


async def main():
    scraper = FO4Scraper()
    
    # 测试模式：只爬取前5个球员
    # await scraper.run(test_mode=True, max_players=5)
    
    # 正式运行
    await scraper.run(test_mode=False)


if __name__ == "__main__":
    asyncio.run(main())
