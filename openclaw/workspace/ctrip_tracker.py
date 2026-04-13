#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
携程国际机票价格追踪器
成都出发 -> 10条热门航线
利用携程日历条获取每天最低价（无需通过验证码）
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
import re
import time
import random
import argparse
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
]

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1536, "height": 864},
    {"width": 1680, "height": 1050},
]

WORKSPACE = r"C:\ADHD_agent\openclaw\workspace"
HISTORY_FILE = os.path.join(WORKSPACE, "flight_data", "flight_history.json")
UPLOADS_DIR = os.path.join(WORKSPACE, "uploads")
TREND_CHART = os.path.join(UPLOADS_DIR, "flight_trend.png")

ROUTES = [
    {"name": "东京",     "code": "tyo", "country": "日本",     "direct": True,  "direct_airlines": "川航3U"},
    {"name": "大阪",     "code": "osa", "country": "日本",     "direct": False, "direct_airlines": ""},
    {"name": "曼谷",     "code": "bkk", "country": "泰国",     "direct": True,  "direct_airlines": "川航3U/春秋9C/国航CA/成都航EU/泰航TG"},
    {"name": "新加坡",   "code": "sin", "country": "新加坡",   "direct": True,  "direct_airlines": "川航3U/国航CA/新航SQ"},
    {"name": "首尔",     "code": "sel", "country": "韩国",     "direct": True,  "direct_airlines": "川航3U/国航CA/韩亚OZ"},
    {"name": "香港",     "code": "hkg", "country": "中国香港", "direct": True,  "direct_airlines": "川航3U/国航CA/国泰CX/港航HX"},
    {"name": "台北",     "code": "tpe", "country": "中国台湾", "direct": True,  "direct_airlines": "长荣BR/国航CA/华航CI/川航3U"},
    {"name": "胡志明市", "code": "sgn", "country": "越南",     "direct": True,  "direct_airlines": "川航3U/越捷VJ"},
    {"name": "吉隆坡",   "code": "kul", "country": "马来西亚", "direct": True,  "direct_airlines": "川航3U/国航CA/亚航X D7/马航MH"},
    {"name": "巴厘岛",   "code": "dps", "country": "印尼",     "direct": True,  "direct_airlines": "川航3U"},
]

COUNTRY_ALIASES = {
    "日本": ["东京", "大阪"],
    "泰国": ["曼谷"],
    "韩国": ["首尔"],
    "东南亚": ["曼谷", "新加坡", "胡志明市", "吉隆坡", "巴厘岛"],
}

ORIGIN = "ctu"
HISTORY_DAYS = 30
PRICE_MIN = 400
PRICE_MAX = 30000
CALENDAR_SPAN = 7  # days visible in calendar bar per page load


def load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_history(history: dict):
    cutoff = (datetime.now() - timedelta(days=HISTORY_DAYS)).strftime("%Y-%m-%d")
    for k in [k for k in history if k < cutoff]:
        del history[k]
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def parse_calendar_prices(visible_text: str, year: int, target_start: str, target_end: str):
    """
    Parse date-price pairs from the calendar bar visible text.
    Calendar shows lines like: "04-22周三\n¥1150低\n\t\n04-23周四\n¥1342"
    Returns list of {date: YYYY-MM-DD, price: int} within the target range.
    """
    pattern = r'(\d{2})-(\d{2})\s*[\u5468][一二三四五六日]\s*\n\s*[¥\uffe5]\s*(\d+)'
    results = []

    for m in re.finditer(pattern, visible_text):
        month, day, price = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if PRICE_MIN <= price <= PRICE_MAX:
            date_str = f"{year}-{month:02d}-{day:02d}"
            if target_start <= date_str <= target_end:
                results.append({"date": date_str, "price": price})

    # Also try .price selector data (format: "¥1212")
    price_only = re.findall(r'[¥\uffe5](\d{3,5})', visible_text)
    for p_str in price_only:
        p = int(p_str)
        if PRICE_MIN <= p <= PRICE_MAX:
            already = any(r["price"] == p for r in results)
            if not already:
                pass  # skip standalone prices without date context

    seen = set()
    deduped = []
    for r in results:
        key = (r["date"], r["price"])
        if key not in seen:
            seen.add(key)
            deduped.append(r)
    return deduped


def fetch_calendar_prices(page, route_code: str, route_name: str, anchor_date: str,
                          target_start: str, target_end: str, year: int) -> list:
    """Load one page and extract calendar bar prices."""
    url = f"https://flights.ctrip.com/online/list/oneway-{ORIGIN}-{route_code}?depdate={anchor_date}"
    try:
        page.goto(url, timeout=25000)
        time.sleep(random.uniform(2.5, 5.0))
        visible = page.inner_text('body')
        return parse_calendar_prices(visible, year, target_start, target_end)
    except Exception as e:
        print(f"  ✗ {route_name} (anchor={anchor_date}): {e}")
        return []


def fetch_direct_price(page, route_code: str, route_name: str, dep_date: str) -> dict | None:
    """
    Load a specific date page and extract the direct flight price.
    Ctrip shows a '直飞¥XXXX' badge on each search results page for the minimum
    non-stop price on that departure date. The calendar bar always shows the
    cheapest price including connecting flights, so we must use this badge instead.
    Returns {"date": dep_date, "price": int} or None if no direct flight found.
    """
    url = f"https://flights.ctrip.com/online/list/oneway-{ORIGIN}-{route_code}?depdate={dep_date}"
    try:
        page.goto(url, timeout=25000)
        time.sleep(random.uniform(2.5, 4.5))
        visible = page.inner_text('body')
        m = re.search(r'直飞[¥\uffe5]\s*(\d+)', visible)
        if m:
            price = int(m.group(1))
            if PRICE_MIN <= price <= PRICE_MAX:
                return {"date": dep_date, "price": price}
    except Exception as e:
        print(f"  ✗ {route_name} direct ({dep_date}): {e}")
    return None


def scan_route_direct_prices(page, route: dict, days_start: int, days_end: int,
                             num_samples: int = 4) -> dict | None:
    """
    Scan direct-flight prices for a route across a date range.
    Samples `num_samples` evenly-spaced dates and returns the cheapest direct price found.
    Each page load gives only one direct price (for the queried date), so sampling
    is necessary to find the window minimum.
    """
    today = datetime.now()
    start_date = today + timedelta(days=days_start)
    end_date = today + timedelta(days=days_end)
    span = (end_date - start_date).days
    step = max(1, span // num_samples)

    sample_dates = []
    d = start_date + timedelta(days=3)
    while d <= end_date and len(sample_dates) < num_samples:
        sample_dates.append(d)
        d += timedelta(days=step)

    best = None
    for sample in sample_dates:
        date_str = sample.strftime("%Y-%m-%d")
        result = fetch_direct_price(page, route["code"], route["name"], date_str)
        if result:
            print(f"  ✓ {route['name']} 直飞 ({date_str}): ¥{result['price']}")
            if best is None or result["price"] < best["price"]:
                best = result
        else:
            print(f"  ✗ {route['name']} 直飞 ({date_str}): 无直飞")
        time.sleep(random.uniform(2.0, 4.0))

    return {"price": best["price"], "dep_date": best["date"]} if best else None


def scan_route_in_range(page, route: dict, days_start: int, days_end: int,
                        test_mode: bool = False, direct_only: bool = False) -> dict | None:
    """
    Scan one route across a date range.
    Uses calendar bar for all-flight mode, or per-date '直飞¥' badge for direct-only mode.
    """
    if direct_only:
        samples = 2 if test_mode else 4
        return scan_route_direct_prices(page, route, days_start, days_end, num_samples=samples)
    today = datetime.now()
    start_date = today + timedelta(days=days_start)
    end_date = today + timedelta(days=days_end)
    target_start = start_date.strftime("%Y-%m-%d")
    target_end = end_date.strftime("%Y-%m-%d")
    year = start_date.year

    all_prices = []

    if test_mode:
        anchors = [start_date + timedelta(days=3)]
    else:
        anchors = []
        current = start_date + timedelta(days=3)
        while current <= end_date:
            anchors.append(current)
            current += timedelta(days=CALENDAR_SPAN)

    consecutive_fail = 0
    for anchor in anchors:
        if consecutive_fail >= 3:
            print(f"  ⚠️ {route['name']}: 连续失败，跳过")
            break

        anchor_str = anchor.strftime("%Y-%m-%d")
        prices = fetch_calendar_prices(
            page, route["code"], route["name"], anchor_str,
            target_start, target_end, year
        )
        if prices:
            all_prices.extend(prices)
            consecutive_fail = 0
            best = min(prices, key=lambda x: x["price"])
            print(f"  ✓ {route['name']} ({anchor_str}): 获取{len(prices)}个价格，最低¥{best['price']}({best['date']})")
        else:
            consecutive_fail += 1
            print(f"  ✗ {route['name']} ({anchor_str}): 未获取到价格")

        time.sleep(random.uniform(2.0, 4.5))

    if all_prices:
        cheapest = min(all_prices, key=lambda x: x["price"])
        return {"price": cheapest["price"], "dep_date": cheapest["date"]}
    return None


def scan_all_routes(routes: list, windows: list, test_mode: bool = False,
                    direct_only: bool = False) -> dict:
    """Launch one browser and scan all routes across all windows."""
    today_data = {}
    route_fail_count = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ua = random.choice(USER_AGENTS)
        vp = random.choice(VIEWPORTS)
        context = browser.new_context(
            user_agent=ua,
            viewport=vp,
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
        )
        page = context.new_page()

        route_counter = 0
        for label, days_start, days_end, suffix, window_key in windows:
            today_d = datetime.now()
            start_d = (today_d + timedelta(days=days_start)).strftime("%m.%d")
            end_d = (today_d + timedelta(days=days_end)).strftime("%m.%d")
            mode_tag = "直飞模式" if direct_only else "全价模式"
            print(f"\n📅 {label} ({start_d} ~ {end_d}) [{mode_tag}]")

            for route in routes:
                if route_fail_count >= 3:
                    print("  🛑 连续3条航线失败，停止扫描")
                    break

                if route_counter > 0:
                    delay = random.uniform(3.0, 7.0)
                    time.sleep(delay)
                route_counter += 1

                result = scan_route_in_range(page, route, days_start, days_end, test_mode,
                                             direct_only=direct_only)
                if result:
                    key = route["name"] + suffix
                    today_data[key] = {
                        "price": result["price"],
                        "dep_date": result["dep_date"],
                        "window": window_key,
                    }
                    route_fail_count = 0
                else:
                    route_fail_count += 1

        browser.close()

    return today_data


def generate_trend_chart(history: dict):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        print("⚠️ matplotlib 未安装，跳过绘图")
        return

    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

    if not history:
        print("⚠️ 无历史数据，跳过绘图")
        return

    sorted_dates = sorted(history.keys())[-7:]
    if not sorted_dates:
        return

    fig, axes = plt.subplots(2, 1, figsize=(12, 10), dpi=150)
    window_labels = ["30-60", "60-90"]
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6',
              '#1abc9c', '#e67e22', '#34495e', '#c0392b', '#8e44ad']

    for ax_idx, window in enumerate(window_labels):
        ax = axes[ax_idx]
        route_prices = {}

        for date in sorted_dates:
            day_data = history.get(date, {})
            for route_name, data in day_data.items():
                if isinstance(data, dict) and data.get("window") == window and data.get("price"):
                    clean_name = route_name.replace("_early", "")
                    if clean_name not in route_prices:
                        route_prices[clean_name] = []
                    route_prices[clean_name].append(
                        (datetime.strptime(date, "%Y-%m-%d"), data["price"])
                    )

        for idx, (rname, points) in enumerate(route_prices.items()):
            if not points:
                continue
            points.sort(key=lambda x: x[0])
            x = [pt[0] for pt in points]
            y = [pt[1] for pt in points]
            color = colors[idx % len(colors)]

            if len(x) == 1:
                ax.scatter(x, y, color=color, label=rname, zorder=5, s=60)
            else:
                ax.plot(x, y, marker='o', color=color, label=rname, linewidth=1.5, zorder=5)

            min_pt = min(points, key=lambda pt: pt[1])
            ax.annotate(
                f"Y{min_pt[1]}\n{min_pt[0].strftime('%m-%d')}",
                xy=(min_pt[0], min_pt[1]),
                xytext=(5, 8), textcoords='offset points', fontsize=7, color=color
            )

        title_text = f"成都出发 - {'1-2个月' if window == '30-60' else '2-3个月'}窗口机票趋势"
        ax.set_title(title_text, fontsize=13, fontweight='bold')
        ax.set_ylabel("价格 (RMB)", fontsize=10)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        if route_prices:
            ax.legend(loc='upper right', fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    plt.savefig(TREND_CHART, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n📊 趋势图已保存: {TREND_CHART}")


def format_change(price: int, yesterday_data: dict, route_name: str) -> str:
    yen = "\u00a5"
    if not yesterday_data or route_name not in yesterday_data:
        return "\U0001f195"
    yp = yesterday_data[route_name].get("price")
    if not yp:
        return "\U0001f195"
    diff = price - yp
    if abs(diff) < 50:
        return "\u2192\u5e73"
    return f"\u2193{-diff}" if diff < 0 else f"\u2191{diff}"


def get_direct_tag(route_name: str, max_airline_len: int = 72) -> str:
    """航线是否常有直飞的静态说明（来自 ROUTES，与当日抓取到的价格是否直飞无关）。"""
    route = next((r for r in ROUTES if r["name"] == route_name), None)
    if not route:
        return ""
    if route.get("direct"):
        air = (route.get("direct_airlines") or "").strip()
        if air:
            if len(air) > max_airline_len:
                air = air[: max_airline_len - 1] + "\u2026"
            return f" \u2708\ufe0f\u76f4\u98de({air})"
        return " \u2708\ufe0f\u76f4\u98de"
    return ""


def build_push_text(today_str: str, today_data: dict, yesterday_data: dict = None,
                    show_route_tags: bool = True, calendar_cheapest: bool = True) -> str:
    yen = "\u00a5"
    month_day = datetime.strptime(today_str, "%Y-%m-%d").strftime("%m-%d")
    today_d = datetime.now()
    lines = [f"\u2708\ufe0f \u6210\u90fd\u51fa\u53d1\u56fd\u9645\u673a\u7968\u65e5\u62a5\uff08{month_day}\uff09", ""]

    for window_key, label in [("30-60", "1-2\u4e2a\u6708\u5185"), ("60-90", "2-3\u4e2a\u6708\u5185")]:
        if window_key == "30-60":
            rs = (today_d + timedelta(days=30)).strftime("%m.%d")
            re_ = (today_d + timedelta(days=60)).strftime("%m.%d")
        else:
            rs = (today_d + timedelta(days=60)).strftime("%m.%d")
            re_ = (today_d + timedelta(days=90)).strftime("%m.%d")
        lines.append(f"\U0001f4c5 {label}\uff08{rs}-{re_}\uff09\u4f4e\u4ef7 Top5\uff1a")

        entries = []
        for rname, data in today_data.items():
            if data.get("window") == window_key and data.get("price"):
                change = format_change(data["price"], yesterday_data, rname)
                clean_name = rname.replace("_early", "")
                direct_info = get_direct_tag(clean_name) if show_route_tags else ""
                entries.append({
                    "route": clean_name,
                    "price": data["price"],
                    "dep_date": data["dep_date"],
                    "change": change,
                    "direct_info": direct_info,
                })

        entries.sort(key=lambda x: x["price"])
        for i, e in enumerate(entries[:5], 1):
            lines.append(f"{i}. {e['route']} {yen}{e['price']} ({e['dep_date']}) {e['change']}{e.get('direct_info', '')}")
        if not entries:
            lines.append("   \u6682\u65e0\u6570\u636e")
        lines.append("")

    if calendar_cheapest:
        lines.append(
            "\u26a0\ufe0f \u4ee5\u4e0a\u4e3a\u65e5\u5386\u6700\u4f4e\u4ef7\uff08\u542b\u8f6c\u673a\uff09\uff0c"
            "\u822a\u7ebf\u65c1\u2708\ufe0f\u4e3a\u8be5\u76ee\u7684\u5730\u5e38\u89c1\u76f4\u98de\u822a\u53f8\u53c2\u8003\uff1b"
            "\u76f4\u98de\u7968\u4ef7\u901a\u5e38\u66f4\u9ad8"
        )
    else:
        lines.append(
            "\u2708\ufe0f \u4ee5\u4e0a\u4e3a\u76f4\u98de\u91c7\u6837\u4f4e\u4ef7\uff08\u65e5\u5386\u680f\u53ef\u80fd\u542b\u66f4\u4f4e\u8f6c\u673a\uff09"
        )
    lines.append("---\u6bcf\u65e511:30\u81ea\u52a8\u63a8\u9001")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Ctrip flight tracker")
    parser.add_argument("--dest", type=str, help="Destinations, comma-separated")
    parser.add_argument("--from", dest="date_from", type=str, help="Start date YYYY-MM-DD")
    parser.add_argument("--to", dest="date_to", type=str, help="End date YYYY-MM-DD")
    parser.add_argument("--test", type=str, nargs="+", help="Test mode: route names")
    parser.add_argument("--quick", action="store_true", help="Quick mode: all 10 routes, 1 sample per window (~3min)")
    parser.add_argument("--full", action="store_true", help="Full scan: all routes, all date samples (cron only)")
    parser.add_argument(
        "--direct",
        action="store_true",
        help="抓取直飞参考价（逐日「直飞¥」采样）；与推送里是否展示航线直飞说明无关",
    )
    parser.add_argument("--only-direct", action="store_true", help="同 --direct，仅保留别名")
    parser.add_argument(
        "--no-route-tag",
        action="store_true",
        help="推送文案中不附加 ✈️直飞(航司) 静态标签",
    )
    args = parser.parse_args()

    print("=" * 50)
    print("CTU Flight Tracker Start")
    print("=" * 50)

    today_str = datetime.now().strftime("%Y-%m-%d")
    history = load_history()

    def resolve_dest(dest_str):
        """Resolve country aliases and city names to route list."""
        names = []
        for d in dest_str.split(","):
            d = d.strip()
            if d in COUNTRY_ALIASES:
                names.extend(COUNTRY_ALIASES[d])
            else:
                names.append(d)
        return [r for r in ROUTES if r["name"] in names]

    if args.test:
        routes = [r for r in ROUTES if r["name"] in args.test]
        is_quick = True
        print(f"TEST mode: {[r['name'] for r in routes]}")
    elif args.dest:
        routes = resolve_dest(args.dest)
        if not routes:
            print(f"Unknown dest: {args.dest}")
            print(f"Available: {', '.join(r['name'] for r in ROUTES)}")
            print(f"Country aliases: {', '.join(COUNTRY_ALIASES.keys())}")
            return
        is_quick = not args.full
        print(f"Custom query: {[r['name'] for r in routes]} ({'quick' if is_quick else 'full'})")
    elif args.full:
        routes = ROUTES
        is_quick = False
        print(f"Full scan: {len(routes)} routes")
    else:
        routes = ROUTES
        is_quick = True
        print(f"Quick mode: {len(routes)} routes (1 sample/window)")

    if args.dest and args.date_from and args.date_to:
        today_d = datetime.now()
        start_d = datetime.strptime(args.date_from, "%Y-%m-%d")
        end_d = datetime.strptime(args.date_to, "%Y-%m-%d")
        days_start = (start_d - today_d).days
        days_end = (end_d - today_d).days

        if days_start < 0:
            print(f"Start date {args.date_from} is in the past")
            return

        windows = [
            (f"Custom ({args.date_from} ~ {args.date_to})", days_start, days_end, "", "custom"),
        ]
        today_data = scan_all_routes(routes, windows, direct_only=(args.direct or args.only_direct))

        print("\n" + "=" * 50)
        print("Query result:")
        print("=" * 50)
        for rname, data in sorted(today_data.items(), key=lambda x: x[1]["price"]):
            clean_name = rname.replace("_early", "")
            route_info = next((r for r in ROUTES if r["name"] == clean_name), None)
            direct_tag = ""
            if (args.direct or args.only_direct) and route_info:
                if route_info.get("direct"):
                    direct_tag = f" [直飞: {route_info['direct_airlines']}]"
                else:
                    direct_tag = " [无直飞]"
            print(f"  {clean_name}: \u00a5{data['price']} ({data['dep_date']}){direct_tag}")

        if args.direct or args.only_direct:
            print("\n✈️ 以上均为直飞价格")
        else:
            print("\n⚠️ 以上为日历最低价（含转机），直飞通常贵2-5倍")
        return

    direct_only = args.direct or bool(getattr(args, "only_direct", False))
    windows = [
        ("30-60 days (1-2 months)", 30, 60, "", "30-60"),
        ("60-90 days (2-3 months)", 60, 90, "_early", "60-90"),
    ]
    today_data = scan_all_routes(routes, windows, test_mode=is_quick, direct_only=direct_only)

    if args.test:
        print("\n(TEST 模式：跳过写入 flight_history.json 与趋势图更新，避免覆盖当日完整数据)")
    else:
        history[today_str] = today_data
        save_history(history)

        print("\nGenerating trend chart...")
        generate_trend_chart(history)

    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_data = history.get(yesterday_str, {})

    push_text = build_push_text(
        today_str,
        today_data,
        yesterday_data,
        show_route_tags=not args.no_route_tag,
        calendar_cheapest=not direct_only,
    )

    print("\n" + "=" * 50)
    print("Push text:")
    print("=" * 50)
    print(push_text)
    print("=" * 50)

    try:
        _scripts = r"C:\ADHD_agent\.cursor\skills\async-notify\scripts"
        if _scripts not in sys.path:
            sys.path.insert(0, _scripts)
        from feishu_helper import send_text, send_image, get_token

        token = get_token()
        tr = send_text(push_text, token)
        if tr.get("code") != 0:
            print(f"飞书文字推送失败: {tr}", file=sys.stderr)
        else:
            print("飞书文字推送成功")
        if os.path.isfile(TREND_CHART):
            ir = send_image(TREND_CHART, token)
            if ir.get("code") != 0:
                print(f"飞书趋势图推送失败: {ir}", file=sys.stderr)
            else:
                print("飞书趋势图推送成功")
    except Exception as fe:
        print(f"飞书推送异常: {fe}", file=sys.stderr)


if __name__ == "__main__":
    main()
