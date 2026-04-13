"""
成都出发国际航线低价推送
使用 Playwright 浏览器自动化
"""
import json
import re
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# 热门目的地
ROUTES = [
    {"code": "osa", "name": "大阪", "country": "日本"},
    {"code": "tyo", "name": "东京", "country": "日本"},
    {"code": "sinh", "name": "新加坡", "country": "新加坡"},
    {"code": "bkk", "name": "曼谷", "country": "泰国"},
    {"code": "tpe", "name": "台北", "country": "中国台湾"},
    {"code": "hkg", "name": "香港", "country": "中国香港"},
    {"code": "sgn", "name": "胡志明市", "country": "越南"},
    {"code": "sel", "name": "首尔", "country": "韩国"},
]

def get_flights_data(route_code, route_name):
    """获取单条航线的航班数据"""
    url = f"https://flights.ctrip.com/online/list/oneway-ctu-{route_code}"
    
    try:
        with sync_playwright() as p:
            # 启动非 headless 模式调试
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            # 设置默认超时
            page.set_default_timeout(30000)
            
            # 访问页面
            response = page.goto(url, wait_until="domcontentloaded")
            
            # 等待页面加载
            time.sleep(3)
            
            # 尝试等待价格元素出现
            try:
                page.wait_for_selector('text=¥', timeout=5000)
            except:
                pass
            
            # 滚动页面触发加载
            page.evaluate('window.scrollBy(0, 300)')
            time.sleep(2)
            
            # 获取页面内容
            content = page.content()
            
            # 提取价格
            price_pattern = r'¥(\d{3,5})'
            prices = re.findall(price_pattern, content)
            
            # 过滤有效价格 (1000-30000)
            valid_prices = [int(p) for p in prices if 1000 <= int(p) <= 30000]
            
            browser.close()
            
            if valid_prices:
                min_price = min(valid_prices)
                
                # 提取日期价格
                date_price_pattern = r'(\d{1,2}-\d{1,2})(?:周[一二三四五六日])?\s*[^¥]*¥(\d{3,5})'
                date_prices = re.findall(date_price_pattern, content)
                
                best_date = "最近"
                if date_prices:
                    # 找最便宜的
                    date_prices_sorted = sorted([(d, int(p)) for d, p in date_prices], key=lambda x: x[1])
                    if date_prices_sorted:
                        best_date = date_prices_sorted[0][0]
                
                # 判断直飞
                has_direct = "直飞" in content and "仅看直飞" in content
                
                # 提取中转地
                transit_pattern = r'转\d次.*?转([^\s<]{2,6})'
                transits = re.findall(transit_pattern, content)
                transit = transits[0] if transits else None
                
                return {
                    "route": route_name,
                    "min_price": min_price,
                    "best_date": best_date,
                    "has_direct": has_direct,
                    "transit": transit
                }
                
    except Exception as e:
        print(f"Error {route_name}: {type(e).__name__}: {str(e)[:50]}")
    
    return None

def scan_all_routes():
    """扫描所有航线"""
    results = []
    
    for route in ROUTES:
        print(f"查询 {route['name']}...", end=" ", flush=True)
        data = get_flights_data(route['code'], route['name'])
        
        if data:
            results.append(data)
            transit_str = f" (中转{data['transit']})" if data.get('transit') else ""
            direct_str = "🛫" if data.get('has_direct') else ""
            print(f"¥{data['min_price']}{transit_str}{direct_str}")
        else:
            print("无数据")
    
    return results

def generate_report(results):
    """生成推送报告"""
    if not results:
        return "⚠️ 未获取到航班数据，请稍后重试"
    
    sorted_results = sorted(results, key=lambda x: x['min_price'])
    today = datetime.now().strftime("%m-%d")
    
    report = f"✈️ 成都出发国际航线低价（{today}）\n\n"
    report += "🔥 最便宜 Top8：\n"
    
    for i, r in enumerate(sorted_results[:8], 1):
        if r.get('transit'):
            transit = f" 🔄中转{r['transit']}"
        elif r.get('has_direct'):
            transit = " 🛫直飞"
        else:
            transit = ""
        
        report += f"{i}. {r['route']} ¥{r['min_price']} ({r['best_date']}){transit}\n"
    
    return report

def main():
    print("=" * 50)
    print("成都国际航线低价推送")
    print("=" * 50)
    
    results = scan_all_routes()
    report = generate_report(results)
    
    print("\n" + "=" * 50)
    print(report)
    
    with open("flight_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return report

if __name__ == "__main__":
    main()
