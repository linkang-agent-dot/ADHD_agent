"""
成都出发国际航线监控脚本
定时抓取携程国际线价格，并分析最优惠航线
"""
import json
import re
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

# 需要查询的国际航线（出发地:CTU）
ROUTES = [
    {"code": "nrt", "name": "东京(成天)", "country": "日本"},
    {"code": "osa", "name": "大阪", "country": "日本"},
    {"code": "kix", "name": "关西", "country": "日本"},
    {"code": "sapporo", "name": "札幌", "country": "日本"},
    {"code": "okinawa", "name": "冲绳", "country": "日本"},
    {"code": "fuk", "name": "福冈", "country": "日本"},
    {"code": "sinh", "name": "新加坡", "country": "新加坡"},
    {"code": "bkk", "name": "曼谷", "country": "泰国"},
    {"code": "pus", "name": "釜山", "country": "韩国"},
    {"code": "sel", "name": "首尔", "country": "韩国"},
    {"code": "tpe", "name": "台北", "country": "中国台湾"},
    {"code": "hkg", "name": "香港", "country": "中国香港"},
    {"code": "mfm", "name": "澳门", "country": "中国澳门"},
    {"code": "sgn", "name": "胡志明市", "country": "越南"},
    {"code": "han", "name": "河内", "country": "越南"},
    {"code": "kul", "name": "吉隆坡", "country": "马来西亚"},
    {"code": "dxb", "name": "迪拜", "country": "阿联酋"},
    {"code": "lon", "name": "伦敦", "country": "英国"},
    {"code": "par", "name": "巴黎", "country": "法国"},
    {"code": "fra", "name": "法兰克福", "country": "德国"},
    {"code": "ams", "name": "阿姆斯特丹", "country": "荷兰"},
    {"code": "mad", "name": "马德里", "country": "西班牙"},
    {"code": "rom", "name": "罗马", "country": "意大利"},
    {"code": "syd", "name": "悉尼", "country": "澳大利亚"},
    {"code": "mel", "name": "墨尔本", "country": "澳大利亚"},
    {"code": "auc", "name": "奥克兰", "country": "新西兰"},
    {"code": "hnd", "name": "东京(成天)", "country": "日本"},
    {"code": "tyo", "name": "东京", "country": "日本"},
    {"code": "nyc", "name": "纽约", "country": "美国"},
    {"code": "lax", "name": "洛杉矶", "country": "美国"},
    {"code": "sfo", "name": "旧金山", "country": "美国"},
    {"code": "sea", "name": "西雅图", "country": "美国"},
    {"code": "yvr", "name": "温哥华", "country": "加拿大"},
    {"code": "yto", "name": "多伦多", "country": "加拿大"},
]

def fetch_flight_price(route_code, date_str):
    """获取单条航线价格"""
    url = f"https://flights.ctrip.com/international/search/oneway-ctu-{route_code}?depdate={date_str}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=20000)
        
        # 提取价格
        content = page.content()
        browser.close()
        
        # 查找价格
        prices = re.findall(r'¥(\d+)', content)
        if prices:
            return min(int(p) for p in prices)
    return None

def scan_all_routes():
    """扫描所有航线未来30天的价格"""
    results = []
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 31)]
    
    print(f"开始扫描 {len(ROUTES)} 条航线...")
    
    for route in ROUTES:
        print(f"查询 {route['name']}...", end=" ")
        min_price = None
        best_date = None
        
        for date_str in dates[:7]:  # 只查7天内的价格
            price = fetch_flight_price(route['code'], date_str)
            if price and (min_price is None or price < min_price):
                min_price = price
                best_date = date_str
        
        if min_price:
            results.append({
                "name": route['name'],
                "country": route['country'],
                "min_price": min_price,
                "best_date": best_date
            })
            print(f"Y{min_price} ({best_date})")
        else:
            print("无数据")
    
    return results

def analyze_and_report(results):
    """分析数据并生成报告"""
    if not results:
        return "未获取到数据"
    
    # 按价格排序
    sorted_results = sorted(results, key=lambda x: x['min_price'])
    
    report = f"📊 成都出发国际航线低价报告（{datetime.now().strftime('%Y-%m-%d')}）\n\n"
    
    # 最便宜 Top 10
    report += "🔥 **最便宜 Top 10：**\n"
    for i, r in enumerate(sorted_results[:10], 1):
        report += f"{i}. {r['name']} ({r['country']}) - Y{r['min_price']} ({r['best_date']})\n"
    
    # 按国家分组
    report += "\n📍 **按国家/地区：**\n"
    countries = {}
    for r in results:
        c = r['country']
        if c not in countries:
            countries[c] = []
        countries[c].append(r)
    
    for country, routes in sorted(countries.items(), key=lambda x: min(x[1], key=lambda r: r['min_price'])['min_price']):
        best = min(routes, key=lambda x: x['min_price'])
        report += f"- {country}: {best['name']} Y{best['min_price']}\n"
    
    return report

def main():
    print("=" * 50)
    print("成都出发国际航线监控")
    print("=" * 50)
    
    results = scan_all_routes()
    
    # 保存原始数据
    with open("flight_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 生成分析报告
    report = analyze_and_report(results)
    print("\n" + "=" * 50)
    print(report)
    
    return report

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    main()
