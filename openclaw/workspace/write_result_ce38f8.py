import sys, json, os
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

result = {
    "task_id": "task_20260331_113356_ce38f8",
    "title": "BUG: 机票脚本 ctrip_tracker.py 查错",
    "status": "done",
    "result": "修复成功：价格解析正则缺少空格匹配。页面实际格式为 '04-26 周日\\n¥ 1369'，但原正则未处理日期与周之间的空格及¥后的空格。在正则中添加 \\s* 后，10条航线20个价格点全部成功抓取（最低价：吉隆坡¥670，曼谷¥691，香港¥802）。修复位置：parse_calendar_prices函数第92行。",
    "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

outbox = r"C:\ADHD_agent\openclaw\workspace\cursor_outbox"
os.makedirs(outbox, exist_ok=True)
out_path = os.path.join(outbox, "task_20260331_113356_ce38f8.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("结果已写入:", out_path)
