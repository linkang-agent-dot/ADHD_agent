"""
FC Online 球员数据爬虫
目标: 爬取传奇时刻(ictm)和传奇永恒(ictmb)卡片的完整能力值
包含: 基础能力值、强化后能力值、球队加成、等级加成
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
SEASONS = ["ictm", "ictmb", "icon"]  # 传奇时刻、传奇永恒、icon
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# 34项能力值字段（英文key -> 中文名）
ATTRIBUTE_MAPPING = {
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


async def get_season_player_list(page: Page, season: str) -> list[dict]:
    """获取指定赛季的所有球员列表"""
    players = []
    
    # 访问球员列表页面
    url = f"{BASE_URL}/fo4db?season={season}"
    print(f"\n正在获取 {season} 球员列表: {url}")
    
    await page.goto(url, wait_until="networkidle", timeout=60000)
    await asyncio.sleep(2)
    
    # 等待球员列表加载
    try:
        await page.wait_for_selector("table tbody tr", timeout=10000)
    except:
        print(f"  警告: {season} 没有找到球员数据")
        return players
    
    # 获取所有球员行
    rows = await page.query_selector_all("table tbody tr")
    print(f"  找到 {len(rows)} 名球员")
    
    for row in rows:
        try:
            # 获取球员链接
            link_elem = await row.query_selector("a[href*='/fo4db/pid']")
            if not link_elem:
                continue
            
            href = await link_elem.get_attribute("href")
            name = await link_elem.inner_text()
            
            # 提取球员ID
            pid_match = re.search(r"/fo4db/pid(\w+)", href)
            if pid_match:
                player_id = pid_match.group(1)
                players.append({
                    "id": player_id,
                    "name": name.strip(),
                    "url": f"{BASE_URL}/fo4db/pid{player_id}",
                    "season": season
                })
        except Exception as e:
            continue
    
    return players


async def get_player_details(page: Page, player: dict) -> dict | None:
    """获取单个球员的完整详情"""
    try:
        await page.goto(player["url"], wait_until="networkidle", timeout=30000)
        await asyncio.sleep(1.5)  # 等待JS渲染
        
        data = {
            "球员ID": player["id"],
            "球员名称": player["name"],
            "赛季": player["season"],
            "URL": player["url"],
        }
        
        # 1. 获取基础信息
        try:
            # 卡片全名（如 "Harry Kane 26TY"）
            title = await page.title()
            data["卡片名称"] = title.split(" - ")[0] if " - " in title else player["name"]
            
            # 位置
            pos_elem = await page.query_selector("h1 + div")
            if pos_elem:
                data["位置"] = await pos_elem.inner_text()
            
            # 俱乐部和国籍
            club_elem = await page.query_selector("a[href*='team=']")
            if club_elem:
                data["俱乐部"] = await club_elem.inner_text()
            
            country_elem = await page.query_selector("a[href*='country=']")
            if country_elem:
                data["国籍"] = await country_elem.inner_text()
                
        except:
            pass
        
        # 2. 获取能力值 - 基础能力值
        for attr_key, attr_name in ATTRIBUTE_MAPPING.items():
            try:
                # 尝试多种选择器
                selectors = [
                    f"[class*='{attr_key}'] + *",
                    f"div:has-text('{attr_key}') span",
                    f"*[data-stat='{attr_key}']",
                ]
                
                value = None
                for selector in selectors:
                    try:
                        elem = await page.query_selector(selector)
                        if elem:
                            text = await elem.inner_text()
                            if text and text.isdigit():
                                value = int(text)
                                break
                    except:
                        continue
                
                data[f"基础_{attr_name}"] = value
            except:
                data[f"基础_{attr_name}"] = None
        
        # 3. 尝试获取强化/加成数据（如果页面有这些选项）
        # 这些数据通常需要点击不同的tab或选项
        
        # 检查是否有强化等级选项
        try:
            level_selector = await page.query_selector("[class*='level'], [class*='enhance'], select[name*='level']")
            if level_selector:
                # 有强化选项，尝试获取不同等级的数据
                data["支持强化"] = True
            else:
                data["支持强化"] = False
        except:
            data["支持强化"] = False
        
        # 4. 获取OVR等基础数值
        try:
            ovr_elem = await page.query_selector("[class*='ovr'], [class*='overall']")
            if ovr_elem:
                ovr_text = await ovr_elem.inner_text()
                ovr_match = re.search(r'\d+', ovr_text)
                if ovr_match:
                    data["OVR"] = int(ovr_match.group())
        except:
            pass
        
        return data
        
    except Exception as e:
        print(f"    获取球员详情失败 {player['name']}: {e}")
        return None


async def scrape_via_api(page: Page, season: str) -> list[dict]:
    """
    通过监听网络请求来获取API数据
    这是更可靠的方式，因为网站的能力值是通过API加载的
    """
    players_data = []
    
    # 监听API请求
    api_responses = []
    
    async def handle_response(response):
        if "/api/" in response.url or "player" in response.url.lower():
            try:
                data = await response.json()
                api_responses.append({"url": response.url, "data": data})
            except:
                pass
    
    page.on("response", handle_response)
    
    # 访问页面
    url = f"{BASE_URL}/fo4db?season={season}"
    await page.goto(url, wait_until="networkidle", timeout=60000)
    await asyncio.sleep(3)
    
    print(f"捕获到 {len(api_responses)} 个API响应")
    for resp in api_responses:
        print(f"  - {resp['url']}")
    
    return api_responses


async def main():
    """主函数"""
    print("=" * 60)
    print("FC Online 球员数据爬虫")
    print("目标: 传奇时刻(ictm) + 传奇永恒(ictmb) + Icon")
    print("=" * 60)
    
    all_players = []
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=False,  # 设为True可隐藏浏览器窗口
            args=["--lang=zh-CN"]
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN"
        )
        
        page = await context.new_page()
        
        # 第一步：获取每个赛季的球员列表
        print("\n[步骤1] 获取球员列表...")
        all_player_list = []
        
        for season in SEASONS:
            players = await get_season_player_list(page, season)
            all_player_list.extend(players)
            print(f"  {season}: {len(players)} 名球员")
        
        print(f"\n总计: {len(all_player_list)} 名球员")
        
        # 第二步：获取每个球员的详细数据
        print("\n[步骤2] 获取球员详情...")
        
        # 限制数量用于测试（正式运行时注释掉这行）
        # all_player_list = all_player_list[:5]
        
        for player in tqdm(all_player_list, desc="爬取进度"):
            details = await get_player_details(page, player)
            if details:
                all_players.append(details)
            
            # 添加延迟避免被封
            await asyncio.sleep(0.5)
        
        await browser.close()
    
    # 第三步：保存数据
    print("\n[步骤3] 保存数据...")
    
    if all_players:
        # 保存为Excel
        df = pd.DataFrame(all_players)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        excel_path = OUTPUT_DIR / f"fc_online_legends_{timestamp}.xlsx"
        df.to_excel(excel_path, index=False, engine="openpyxl")
        print(f"  Excel保存至: {excel_path}")
        
        # 保存为JSON
        json_path = OUTPUT_DIR / f"fc_online_legends_{timestamp}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_players, f, ensure_ascii=False, indent=2)
        print(f"  JSON保存至: {json_path}")
        
        print(f"\n成功爬取 {len(all_players)} 名球员数据!")
    else:
        print("  未获取到任何数据")
    
    print("\n爬取完成!")


if __name__ == "__main__":
    asyncio.run(main())
