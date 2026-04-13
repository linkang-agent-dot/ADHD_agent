"""
成都出发国际航线低价推送 - 轻量版
使用浏览器工具批量查询
"""
import json
import re
from datetime import datetime, timedelta
import asyncio

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
    {"code": "lon", "name": "伦敦", "country": "英国"},
    {"code": "par", "name": "巴黎", "country": "法国"},
    {"code": "syd", "name": "悉尼", "country": "澳大利亚"},
    {"code": "nyc", "name": "纽约", "country": "美国"},
    {"code": "yvr", "name": "温哥华", "country": "加拿大"},
]

def generate_report(results):
    """生成推送报告"""
    if not results:
        return "未获取到航班数据"
    
    # 按价格排序
    sorted_results = sorted(results, key=lambda x: x['min_price'])
    
    report = f"✈️ 成都出发国际航线低价（{datetime.now().strftime('%m-%d')}）\n\n"
    
    # 最便宜 Top 10
    report += "🔥 最便宜 Top10：\n"
    for i, r in enumerate(sorted_results[:10], 1):
        report += f"{i}. {r['name']} Y{r['min_price']} ({r['best_date'][5:]})\n"
    
    return report

def save_data(results):
    """保存数据"""
    with open("flight_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

# 手动运行的占位脚本
# 实际执行需要用浏览器工具查询后手动整理
if __name__ == "__main__":
    print("请使用浏览器工具查询携程国际线价格")
    print("URL格式: https://flights.ctrip.com/international/search/oneway-ctu-{code}?depdate=2026-04-01")
    print("\n可用目的地代码:")
    for r in ROUTES:
        print(f"  {r['name']}: {r['code']}")
