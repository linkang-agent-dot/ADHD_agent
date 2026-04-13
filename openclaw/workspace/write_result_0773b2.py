import sys, json, os
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

result = {
    "task_id": "task_20260331_152317_0773b2",
    "title": "机票脚本：实现真正的直飞价格抓取",
    "status": "done",
    "result": "已实现。方案：携程页面每个搜索结果页顶部有'直飞¥XXXX'标记，每次加载特定日期页面即可获取该日直飞最低价。新增 fetch_direct_price() + scan_route_direct_prices() 函数，--direct 参数现在真正触发直飞价格抓取。验证：--direct --dest 日本 --from 2026-04-01 --to 2026-06-30。结果：东京最低直飞¥1980(5月17日,川航3U)；大阪无直飞(符合实际)。直飞价比含转机价贵约50%（东京含转机¥1353 vs 直飞¥1980）。",
    "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

outbox = r"C:\ADHD_agent\openclaw\workspace\cursor_outbox"
os.makedirs(outbox, exist_ok=True)
out_path = os.path.join(outbox, "task_20260331_152317_0773b2.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("结果已写入:", out_path)
