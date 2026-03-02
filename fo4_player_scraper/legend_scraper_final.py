"""
FC Online 传奇球员数据爬虫 - 最终版
通过页面交互筛选传奇球员，然后获取完整数据
"""

import asyncio
import json
import re
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, Page
import pandas as pd
from tqdm import tqdm

# 配置
BASE_URL = "https://cn.fifaaddict.com"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# 目标赛季及对应的按钮文本
TARGET_SEASONS = {
    "ictm": "ICTM",      # 传奇时刻
    "ictmb": "ICTMB",    # 传奇永恒
    "icon": "ICON"       # Icon传奇
}

# 能力值字段
ATTR_KEYS = [
    "sprintspeed", "acceleration", "finishing", "shotpower", "longshots",
    "positioning", "volleys", "penalties", "shortpassing", "vision",
    "crossing", "longpassing", "freekickaccuracy", "curve", "dribbling",
    "ballcontrol", "agility", "balance", "reactions", "marking",
    "standingtackle", "interceptions", "headingaccuracy", "slidingtackle",
    "strength", "stamina", "aggression", "jumping", "composure",
    "gkdiving", "gkhandling", "gkkicking", "gkreflexes", "gkpositioning"
]


class LegendScraperFinal:
    def __init__(self):
        self.all_players = []
        self.processed_ids = set()
        
    async def click_season_filter(self, page: Page, season_btn_text: str) -> bool:
        """点击赛季筛选按钮"""
        try:
            # 等待页面加载
            await asyncio.sleep(2)
            
            # 尝试多种选择器找到按钮
            selectors = [
                f"button:has-text('{season_btn_text}')",
                f"span:has-text('{season_btn_text}')",
                f"[class*='season']:has-text('{season_btn_text}')",
                f"div:has-text('{season_btn_text}')"
            ]
            
            for selector in selectors:
                try:
                    btn = await page.query_selector(selector)
                    if btn:
                        await btn.click()
                        print(f"  点击了 {season_btn_text} 按钮")
                        await asyncio.sleep(2)
                        return True
                except:
                    continue
            
            # 尝试使用JavaScript点击
            clicked = await page.evaluate(f'''() => {{
                const btns = document.querySelectorAll('button, span, div');
                for (const btn of btns) {{
                    if (btn.textContent.trim().toLowerCase() === '{season_btn_text.lower()}') {{
                        btn.click();
                        return true;
                    }}
                }}
                return false;
            }}''')
            
            if clicked:
                print(f"  通过JS点击了 {season_btn_text} 按钮")
                await asyncio.sleep(2)
                return True
                
            return False
        except Exception as e:
            print(f"  点击按钮失败: {e}")
            return False
    
    async def get_player_ids_from_page(self, page: Page) -> list[str]:
        """从当前页面获取所有球员ID"""
        player_ids = []
        
        # 滚动加载更多
        for _ in range(10):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(0.5)
        
        # 获取所有球员链接
        links = await page.query_selector_all("a[href*='/fo4db/pid']")
        
        for link in links:
            try:
                href = await link.get_attribute("href")
                pid_match = re.search(r"pid(\w+)", href)
                if pid_match:
                    player_ids.append(pid_match.group(1))
            except:
                continue
        
        return list(set(player_ids))
    
    async def fetch_player_data(self, page: Page, player_id: str) -> dict | None:
        """获取单个球员的API数据"""
        api_data = None
        
        async def on_response(response):
            nonlocal api_data
            if f"fo4pid=pid{player_id}" in response.url:
                try:
                    body = await response.body()
                    api_data = json.loads(body.decode('utf-8'))
                except:
                    pass
        
        page.on('response', on_response)
        
        try:
            await page.goto(f"{BASE_URL}/fo4db/pid{player_id}", timeout=30000)
            await asyncio.sleep(1.5)
        except:
            pass
        
        try:
            page.remove_listener('response', on_response)
        except:
            pass
        
        if api_data:
            return self.parse_player_data(api_data, player_id)
        return None
    
    def parse_player_data(self, api_data: dict, player_id: str) -> dict:
        """解析API数据"""
        result = {"球员ID": player_id}
        
        db = api_data.get("db", {})
        
        # 基础信息
        result["球员名称"] = db.get("name", "")
        result["简称"] = db.get("name_short", "")
        result["赛季全称"] = db.get("season_full", "")
        result["赛季代码"] = db.get("season_name", "")
        result["位置"] = db.get("pos1", "")
        result["俱乐部"] = db.get("team_name", "")
        result["国籍"] = db.get("nation_name", "")
        result["身高"] = db.get("height", 0)
        result["体重"] = db.get("weight", 0)
        result["年龄"] = db.get("age", 0)
        result["惯用脚"] = db.get("foot_pref", "")
        result["逆足等级"] = db.get("foot_weak", "")
        result["花式等级"] = db.get("skill_level", 0)
        result["体型"] = db.get("bodytype_name", "")
        result["工资"] = db.get("salary", 0)
        result["能力总和"] = db.get("allstat", 0)
        
        # 六维汇总
        attrgroup = db.get("attrgroup", {})
        labels = attrgroup.get("labels", [])
        data = attrgroup.get("data", [])
        for i, label in enumerate(labels):
            if i < len(data):
                result[f"六维_{label}"] = data[i]
        
        # 34项能力值
        attrs = api_data.get("attr", {})
        for attr_key in ATTR_KEYS:
            attr_info = attrs.get(attr_key, {})
            if isinstance(attr_info, dict):
                cn_name = attr_info.get("name", attr_key)
                value = attr_info.get("value", 0)
                result[f"能力_{cn_name}"] = value
        
        # 位置评分
        postlist = db.get("postlist", {})
        for pos_key, pos_info in postlist.items():
            if isinstance(pos_info, dict):
                pos_name = pos_info.get("text", "")
                pos_value = pos_info.get("value", 0)
                if pos_name:
                    result[f"位置_{pos_name}"] = pos_value
        
        # 特性
        traits = api_data.get("traits", {})
        trait_list = [t.get("name", k) for k, t in traits.items() if isinstance(t, dict)]
        result["特性技能"] = " | ".join(trait_list)
        result["特性数量"] = len(trait_list)
        
        return result
    
    async def scrape_all_legends(self, page: Page):
        """爬取所有传奇球员"""
        
        for season_code, season_btn in TARGET_SEASONS.items():
            print(f"\n{'='*60}")
            print(f"正在处理: {season_btn} ({season_code})")
            print(f"{'='*60}")
            
            # 访问搜索页
            await page.goto(f"{BASE_URL}/fo4db", timeout=60000)
            await asyncio.sleep(3)
            
            # 点击赛季筛选
            if not await self.click_season_filter(page, season_btn):
                print(f"  无法找到 {season_btn} 按钮，尝试手动筛选")
            
            # 获取当前页面的球员ID
            player_ids = await self.get_player_ids_from_page(page)
            print(f"  找到 {len(player_ids)} 个球员ID")
            
            # 爬取每个球员
            season_players = 0
            for pid in tqdm(player_ids, desc=f"爬取{season_btn}"):
                if pid in self.processed_ids:
                    continue
                
                data = await self.fetch_player_data(page, pid)
                if data:
                    # 验证赛季
                    if data.get("赛季代码", "").lower() == season_code.lower():
                        self.all_players.append(data)
                        self.processed_ids.add(pid)
                        season_players += 1
                
                await asyncio.sleep(0.5)
            
            print(f"  {season_btn} 共爬取 {season_players} 名球员")
    
    async def run(self, test_mode: bool = False, max_per_season: int = 5):
        """运行爬虫"""
        print("=" * 70)
        print("FC Online 传奇球员数据爬虫")
        print("目标: ICTM(传奇时刻) + ICTMB(传奇永恒) + ICON(传奇)")
        print("=" * 70)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=['--lang=zh-CN']
            )
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                locale="zh-CN"
            )
            page = await context.new_page()
            
            await self.scrape_all_legends(page)
            
            await browser.close()
        
        self.save_data()
        
        print(f"\n完成! 共爬取 {len(self.all_players)} 名传奇球员")
    
    def save_data(self):
        """保存数据"""
        if not self.all_players:
            print("没有数据")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON
        json_path = OUTPUT_DIR / f"fc_legends_{timestamp}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.all_players, f, ensure_ascii=False, indent=2)
        print(f"\n✓ JSON: {json_path}")
        
        # Excel
        df = pd.DataFrame(self.all_players)
        if "赛季代码" in df.columns and "位置_OVR" in df.columns:
            df = df.sort_values(by=["赛季代码", "位置_OVR"], ascending=[True, False])
        
        excel_path = OUTPUT_DIR / f"fc_legends_{timestamp}.xlsx"
        df.to_excel(excel_path, index=False, engine="openpyxl")
        print(f"✓ Excel: {excel_path}")
        
        # 按赛季统计
        if "赛季代码" in df.columns:
            print("\n赛季统计:")
            for s in df["赛季代码"].unique():
                print(f"  {s.upper()}: {len(df[df['赛季代码']==s])} 名")


async def main():
    scraper = LegendScraperFinal()
    await scraper.run()


if __name__ == "__main__":
    asyncio.run(main())
