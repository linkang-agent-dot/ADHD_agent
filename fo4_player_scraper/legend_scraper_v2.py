"""
FC Online 传奇球员数据爬虫 V2
使用直接API访问方式，更可靠
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

# 目标赛季
TARGET_SEASONS = ["ictm", "ictmb", "icon"]

# 能力值英文名
ATTR_KEYS = [
    "sprintspeed", "acceleration", "finishing", "shotpower", "longshots",
    "positioning", "volleys", "penalties", "shortpassing", "vision",
    "crossing", "longpassing", "freekickaccuracy", "curve", "dribbling",
    "ballcontrol", "agility", "balance", "reactions", "marking",
    "standingtackle", "interceptions", "headingaccuracy", "slidingtackle",
    "strength", "stamina", "aggression", "jumping", "composure",
    "gkdiving", "gkhandling", "gkkicking", "gkreflexes", "gkpositioning"
]


class LegendScraperV2:
    def __init__(self):
        self.all_players = []
        self.processed_ids = set()
        
    async def fetch_player_api(self, page: Page, player_id: str) -> dict | None:
        """通过API获取单个球员数据"""
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
        
        return api_data
    
    def parse_player_data(self, api_data: dict, player_id: str) -> dict:
        """解析球员数据为扁平化字典"""
        result = {"球员ID": player_id}
        
        # 基础信息
        db = api_data.get("db", {})
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
        
        # 6大项汇总
        attrgroup = db.get("attrgroup", {})
        labels = attrgroup.get("labels", [])
        data = attrgroup.get("data", [])
        for i, label in enumerate(labels):
            if i < len(data):
                result[f"六维_{label}"] = data[i]
        
        # 34项能力值（基础）
        attrs = api_data.get("attr", {})
        for attr_key in ATTR_KEYS:
            attr_info = attrs.get(attr_key, {})
            if isinstance(attr_info, dict):
                cn_name = attr_info.get("name", attr_key)
                value = attr_info.get("value", 0)
                result[f"基础_{cn_name}"] = value
        
        # 位置评分
        postlist = db.get("postlist", {})
        for pos_key, pos_info in postlist.items():
            if isinstance(pos_info, dict):
                pos_name = pos_info.get("text", "")
                pos_value = pos_info.get("value", 0)
                if pos_name and pos_value > 0:
                    result[f"评分_{pos_name}"] = pos_value
        
        # 特性技能
        traits = api_data.get("traits", {})
        trait_list = []
        for trait_key, trait_info in traits.items():
            if isinstance(trait_info, dict):
                trait_list.append(trait_info.get("name", trait_key))
        result["特性技能"] = " | ".join(trait_list)
        result["特性数量"] = len(trait_list)
        
        return result
    
    async def discover_players(self, page: Page) -> list[dict]:
        """从网站发现所有球员"""
        print("\n正在发现球员列表...")
        
        players = []
        seen_ids = set()
        
        # 访问主页
        await page.goto(f"{BASE_URL}/fo4db", timeout=60000)
        await asyncio.sleep(3)
        
        # 滚动多次加载更多
        print("滚动加载更多球员...")
        for i in range(20):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(0.5)
        
        # 获取所有球员链接
        links = await page.query_selector_all("a[href*='/fo4db/pid']")
        print(f"找到 {len(links)} 个球员链接")
        
        for link in links:
            try:
                href = await link.get_attribute("href")
                text = (await link.inner_text()).strip()
                
                pid_match = re.search(r"pid(\w+)", href)
                if pid_match:
                    pid = pid_match.group(1)
                    if pid not in seen_ids:
                        seen_ids.add(pid)
                        # 从链接文本中判断赛季
                        season = ""
                        text_upper = text.upper()
                        for s in TARGET_SEASONS:
                            if s.upper() in text_upper:
                                season = s
                                break
                        players.append({
                            "id": pid,
                            "name": text,
                            "season_hint": season
                        })
            except:
                continue
        
        print(f"提取到 {len(players)} 个唯一球员")
        return players
    
    async def run(self, test_mode: bool = False, max_players: int = 10):
        """运行爬虫"""
        print("=" * 70)
        print("FC Online 传奇球员数据爬虫 V2")
        print(f"目标赛季: {', '.join(s.upper() for s in TARGET_SEASONS)}")
        print("=" * 70)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=['--lang=zh-CN', '--disable-blink-features=AutomationControlled']
            )
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                locale="zh-CN",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            # 发现球员
            all_players = await self.discover_players(page)
            
            if test_mode:
                all_players = all_players[:max_players]
                print(f"\n[测试模式] 只处理前 {max_players} 个球员")
            
            # 爬取每个球员
            print(f"\n开始爬取球员详情 ({len(all_players)} 个)...")
            
            legend_count = 0
            for player in tqdm(all_players, desc="爬取进度"):
                player_id = player["id"]
                
                if player_id in self.processed_ids:
                    continue
                
                # 获取API数据
                api_data = await self.fetch_player_api(page, player_id)
                
                if api_data:
                    parsed = self.parse_player_data(api_data, player_id)
                    season_code = parsed.get("赛季代码", "").lower()
                    
                    # 检查是否是目标赛季
                    if season_code in TARGET_SEASONS:
                        self.all_players.append(parsed)
                        self.processed_ids.add(player_id)
                        legend_count += 1
                        tqdm.write(f"  ✓ {parsed['球员名称']} ({parsed['赛季代码'].upper()})")
                
                # 延迟
                await asyncio.sleep(0.8)
            
            await browser.close()
        
        # 保存
        print(f"\n找到 {legend_count} 名传奇球员")
        self.save_data()
    
    def save_data(self):
        """保存数据"""
        if not self.all_players:
            print("没有数据可保存")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON
        json_path = OUTPUT_DIR / f"legends_{timestamp}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.all_players, f, ensure_ascii=False, indent=2)
        print(f"\n✓ JSON: {json_path}")
        
        # Excel
        df = pd.DataFrame(self.all_players)
        
        # 排序
        sort_cols = []
        if "赛季代码" in df.columns:
            sort_cols.append("赛季代码")
        if "评分_OVR" in df.columns:
            sort_cols.append("评分_OVR")
        if sort_cols:
            df = df.sort_values(by=sort_cols, ascending=[True, False])
        
        excel_path = OUTPUT_DIR / f"legends_{timestamp}.xlsx"
        df.to_excel(excel_path, index=False, engine="openpyxl")
        print(f"✓ Excel: {excel_path}")
        
        # 统计
        if "赛季代码" in df.columns:
            print("\n按赛季统计:")
            for season in df["赛季代码"].unique():
                count = len(df[df["赛季代码"] == season])
                print(f"  {season.upper()}: {count} 名")


async def main():
    scraper = LegendScraperV2()
    
    # 测试模式（先运行这个验证功能）
    await scraper.run(test_mode=True, max_players=5)
    
    # 正式运行
    # await scraper.run(test_mode=False)


if __name__ == "__main__":
    asyncio.run(main())
