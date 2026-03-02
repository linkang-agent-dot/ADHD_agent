"""
FC Online 传奇球员数据爬虫
目标: 传奇时刻(ICTM)、传奇永恒(ICTMB)、Icon传奇
数据: 完整34项能力值 + 特性技能 + 位置评分
"""

import asyncio
import json
import re
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import pandas as pd
from tqdm import tqdm

# 配置
BASE_URL = "https://cn.fifaaddict.com"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# 目标赛季代码
TARGET_SEASONS = {
    "ictm": "传奇时刻",
    "ictmb": "传奇永恒",
    "icon": "Icon传奇"
}

# 能力值字段映射（英文 -> 中文）
ATTR_MAPPING = {
    "sprintspeed": "速度",
    "acceleration": "加速",
    "finishing": "射术",
    "shotpower": "射门力量",
    "longshots": "远射",
    "positioning": "站位",
    "volleys": "凌空抽射",
    "penalties": "罚点球",
    "shortpassing": "短传",
    "vision": "视野",
    "crossing": "传中",
    "longpassing": "长传",
    "freekickaccuracy": "任意球",
    "curve": "弧线",
    "dribbling": "盘带",
    "ballcontrol": "控球",
    "agility": "灵活",
    "balance": "平衡",
    "reactions": "反应",
    "marking": "人盯人",
    "standingtackle": "抢断",
    "interceptions": "战术意识",
    "headingaccuracy": "头球",
    "slidingtackle": "铲断",
    "strength": "强壮",
    "stamina": "体力",
    "aggression": "侵略性",
    "jumping": "弹跳",
    "composure": "冷静",
    "gkdiving": "GK扑救",
    "gkhandling": "GK手控球",
    "gkkicking": "GK大脚开球",
    "gkreflexes": "GK反应",
    "gkpositioning": "GK防守站位",
}


class LegendScraper:
    def __init__(self):
        self.all_players = []
        self.player_ids = set()
        
    async def get_player_list_from_page(self, page, season_code: str) -> list[str]:
        """从搜索页获取指定赛季的球员ID列表"""
        player_ids = []
        
        # 访问球员列表页面
        url = f"{BASE_URL}/fo4db"
        print(f"\n访问搜索页: {url}")
        await page.goto(url, timeout=60000)
        await asyncio.sleep(2)
        
        # 点击赛季筛选按钮
        try:
            # 找到赛季按钮并点击
            season_btn = await page.query_selector(f"button:has-text('{season_code}'), [class*='{season_code}'], span:has-text('{season_code}')")
            if season_btn:
                await season_btn.click()
                await asyncio.sleep(2)
                print(f"  已点击 {season_code} 筛选")
            else:
                # 尝试直接在URL中添加赛季参数
                print(f"  未找到 {season_code} 按钮，尝试URL参数")
        except Exception as e:
            print(f"  点击赛季按钮失败: {e}")
        
        # 滚动加载更多
        for i in range(10):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1)
        
        # 获取所有球员链接
        links = await page.query_selector_all("a[href*='/fo4db/pid']")
        print(f"  找到 {len(links)} 个球员链接")
        
        for link in links:
            try:
                href = await link.get_attribute("href")
                text = await link.inner_text()
                
                # 检查是否是目标赛季
                if season_code.lower() in text.lower() or season_code.upper() in text.upper():
                    pid_match = re.search(r"pid(\w+)", href)
                    if pid_match:
                        player_ids.append(pid_match.group(1))
            except:
                continue
        
        return list(set(player_ids))
    
    async def get_player_data_from_api(self, page, player_id: str) -> dict | None:
        """通过API获取球员完整数据"""
        api_data = None
        
        async def capture_response(response):
            nonlocal api_data
            url = response.url
            if f"fo4pid=pid{player_id}" in url:
                try:
                    body = await response.body()
                    text = body.decode('utf-8')
                    api_data = json.loads(text)
                except:
                    pass
        
        page.on('response', capture_response)
        
        # 访问球员页面触发API请求
        url = f"{BASE_URL}/fo4db/pid{player_id}"
        try:
            await page.goto(url, timeout=30000)
            await asyncio.sleep(2)
        except:
            pass
        
        page.remove_listener('response', capture_response)
        
        if api_data:
            return self.parse_api_data(api_data, player_id)
        return None
    
    def parse_api_data(self, api_data: dict, player_id: str) -> dict:
        """解析API返回的数据"""
        result = {
            "球员ID": player_id,
            "URL": f"{BASE_URL}/fo4db/pid{player_id}"
        }
        
        # 解析基础信息
        db = api_data.get("db", {})
        result["球员名称"] = db.get("name", "")
        result["球员简称"] = db.get("name_short", "")
        result["赛季全称"] = db.get("season_full", "")
        result["赛季代码"] = db.get("season_name", "")
        result["位置"] = db.get("pos1", "")
        result["俱乐部"] = db.get("team_name", "")
        result["国籍"] = db.get("nation_name", "")
        result["身高"] = db.get("height", 0)
        result["体重"] = db.get("weight", 0)
        result["年龄"] = db.get("age", 0)
        result["惯用脚"] = db.get("foot_pref", "")
        result["逆足"] = db.get("foot_weak", "")
        result["花式"] = db.get("skill_level", 0)
        result["体型"] = db.get("bodytype_name", "")
        result["工资"] = db.get("salary", 0)
        result["能力总和"] = db.get("allstat", 0)
        
        # 解析6大项汇总能力值
        attrgroup = db.get("attrgroup", {})
        labels = attrgroup.get("labels", [])
        data = attrgroup.get("data", [])
        for i, label in enumerate(labels):
            if i < len(data):
                result[f"汇总_{label}"] = data[i]
        
        # 解析34项详细能力值
        attrs = api_data.get("attr", {})
        for attr_key, attr_info in attrs.items():
            if isinstance(attr_info, dict):
                cn_name = attr_info.get("name", ATTR_MAPPING.get(attr_key, attr_key))
                value = attr_info.get("value", 0)
                result[f"能力_{cn_name}"] = value
        
        # 解析位置评分
        postlist = db.get("postlist", {})
        for pos_key, pos_info in postlist.items():
            if isinstance(pos_info, dict):
                pos_name = pos_info.get("text", "")
                pos_value = pos_info.get("value", 0)
                if pos_name:
                    result[f"位置评分_{pos_name}"] = pos_value
        
        # 解析特性技能
        traits = api_data.get("traits", {})
        trait_names = []
        for trait_key, trait_info in traits.items():
            if isinstance(trait_info, dict):
                trait_names.append(trait_info.get("name", trait_key))
        result["特性技能"] = ", ".join(trait_names)
        result["特性数量"] = len(trait_names)
        
        return result
    
    async def scrape_season(self, page, season_code: str, season_name: str):
        """爬取指定赛季的所有球员"""
        print(f"\n{'='*60}")
        print(f"开始爬取: {season_name} ({season_code.upper()})")
        print(f"{'='*60}")
        
        # 获取球员列表
        # 由于筛选可能不精确，我们需要遍历所有球员并检查赛季
        # 这里使用一个更直接的方法：从已知的传奇球员页面开始
        
        # 先访问主页获取一些球员
        url = f"{BASE_URL}/fo4db"
        await page.goto(url, timeout=60000)
        await asyncio.sleep(3)
        
        # 滚动加载更多
        for _ in range(5):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1)
        
        # 获取所有球员链接
        links = await page.query_selector_all("a[href*='/fo4db/pid']")
        print(f"页面上找到 {len(links)} 个球员链接")
        
        # 提取所有球员ID
        all_player_ids = set()
        for link in links:
            try:
                href = await link.get_attribute("href")
                pid_match = re.search(r"pid(\w+)", href)
                if pid_match:
                    all_player_ids.add(pid_match.group(1))
            except:
                continue
        
        print(f"提取到 {len(all_player_ids)} 个唯一球员ID")
        
        # 遍历每个球员，获取数据并检查赛季
        season_players = []
        for player_id in tqdm(all_player_ids, desc=f"检查球员"):
            if player_id in self.player_ids:
                continue
            
            data = await self.get_player_data_from_api(page, player_id)
            if data:
                # 检查是否是目标赛季
                season = data.get("赛季代码", "").lower()
                if season == season_code.lower():
                    season_players.append(data)
                    self.player_ids.add(player_id)
                    print(f"  ✓ {data.get('球员名称')} ({data.get('赛季全称')})")
            
            await asyncio.sleep(0.5)  # 避免请求过快
        
        print(f"\n{season_name} 共找到 {len(season_players)} 名球员")
        self.all_players.extend(season_players)
    
    async def run(self, test_mode: bool = False, max_players: int = 10):
        """运行爬虫"""
        print("=" * 70)
        print("FC Online 传奇球员数据爬虫")
        print("目标: 传奇时刻(ICTM) + 传奇永恒(ICTMB) + Icon传奇")
        print("数据: 34项完整能力值 + 特性技能 + 位置评分")
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
            
            # 爬取每个赛季
            for season_code, season_name in TARGET_SEASONS.items():
                if test_mode and len(self.all_players) >= max_players:
                    break
                await self.scrape_season(page, season_code, season_name)
            
            await browser.close()
        
        # 保存数据
        self.save_data()
        
        print(f"\n{'='*70}")
        print(f"爬取完成! 共获取 {len(self.all_players)} 名传奇球员数据")
        print(f"{'='*70}")
    
    def save_data(self):
        """保存数据"""
        if not self.all_players:
            print("没有数据可保存")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存JSON
        json_path = OUTPUT_DIR / f"legends_{timestamp}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.all_players, f, ensure_ascii=False, indent=2)
        print(f"\nJSON保存至: {json_path}")
        
        # 保存Excel
        df = pd.DataFrame(self.all_players)
        
        # 按赛季和位置评分排序
        if "赛季代码" in df.columns and "位置评分_OVR" in df.columns:
            df = df.sort_values(by=["赛季代码", "位置评分_OVR"], ascending=[True, False])
        
        excel_path = OUTPUT_DIR / f"legends_{timestamp}.xlsx"
        df.to_excel(excel_path, index=False, engine="openpyxl")
        print(f"Excel保存至: {excel_path}")
        
        # 按赛季分别保存
        if "赛季代码" in df.columns:
            for season_code in df["赛季代码"].unique():
                season_df = df[df["赛季代码"] == season_code]
                if not season_df.empty:
                    season_path = OUTPUT_DIR / f"{season_code}_{timestamp}.xlsx"
                    season_df.to_excel(season_path, index=False, engine="openpyxl")
                    print(f"  {season_code}: {season_path} ({len(season_df)} 名)")


async def main():
    scraper = LegendScraper()
    
    # 测试模式
    # await scraper.run(test_mode=True, max_players=5)
    
    # 正式运行
    await scraper.run(test_mode=False)


if __name__ == "__main__":
    asyncio.run(main())
