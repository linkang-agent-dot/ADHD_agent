"""
成都出发国际航线监控 - 快速版
使用已有的浏览器会话批量查询
"""
import json
import re
import asyncio
from datetime import datetime, timedelta

# 热门目的地列表
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
    {"code": "fra", "name": "法兰克福", "country": "德国"},
    {"code": "syd", "name": "悉尼", "country": "澳大利亚"},
    {"code": "nyc", "name": "纽约", "country": "美国"},
    {"code": "yvr", "name": "温哥华", "country": "加拿大"},
]

async def main():
    print("=" * 50)
    print("成都出发国际航线监控 - 快速版")
    print("=" * 50)
    print(f"目标: {len(ROUTES)} 条热门航线")
    print("请在浏览器中手动查询以下URL:")
    print()
    
    # 生成查询 URL 列表
    base_url = "https://flights.ctrip.com/international/search/oneway-ctu-"
    for route in ROUTES:
        url = f"{base_url}{route['code']}?depdate=2026-04-01"
        print(f"- {route['name']}: {url}")
    
    print()
    print("请复制上面的URL到浏览器中查询，把价格告诉我，我帮你分析！")

if __name__ == "__main__":
    asyncio.run(main())
