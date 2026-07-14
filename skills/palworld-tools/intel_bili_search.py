# -*- coding: utf-8 -*-
"""帕鲁情报扫描·B站搜索助手（自包含：现领游客buvid，无需cookie文件）
输出: JSON 数组 [{bvid,title,play,duration,pubdate_ts,pubdate}]，只含 state 里 last_ts 之后发布的视频。
用法: python -X utf8 intel_bili_search.py
"""
import urllib.request, urllib.parse, json, time, datetime, os, sys

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "intel_state.json")
KEYWORDS = ["幻兽帕鲁 1.0", "幻兽帕鲁 更新", "幻兽帕鲁 最强", "幻兽帕鲁 毕业"]

state = {}
if os.path.exists(STATE):
    try:
        state = json.load(open(STATE, encoding="utf-8"))
    except Exception:
        state = {}
last_ts = state.get("bili_last_ts", int(time.time()) - 86400)

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
     "Referer": "https://www.bilibili.com/"}

def get(url, headers):
    req = urllib.request.Request(url, headers=headers)
    return json.load(urllib.request.urlopen(req, timeout=30))

# 现领游客 buvid
try:
    spi = get("https://api.bilibili.com/x/frontend/finger/spi", {"User-Agent": H["User-Agent"]})["data"]
    H["Cookie"] = f"buvid3={spi['b_3']}; buvid4={spi['b_4']}"
except Exception as e:
    print(json.dumps({"error": "buvid fail: " + repr(e)[:80]}), flush=True)

seen, out = set(), []
for kw in KEYWORDS:
    url = ("https://api.bilibili.com/x/web-interface/search/type?search_type=video&order=pubdate&keyword="
           + urllib.parse.quote(kw))
    for attempt in range(3):
        try:
            r = get(url, H)
            for v in (r.get("data", {}).get("result") or []):
                if v["bvid"] in seen:
                    continue
                seen.add(v["bvid"])
                if v["pubdate"] > last_ts:
                    out.append({
                        "bvid": v["bvid"],
                        "title": v["title"].replace('<em class="keyword">', "").replace("</em>", ""),
                        "play": v["play"], "duration": v["duration"],
                        "pubdate_ts": v["pubdate"],
                        "pubdate": datetime.datetime.fromtimestamp(v["pubdate"]).strftime("%m-%d %H:%M"),
                    })
            break
        except Exception:
            if attempt == 2:
                pass
            time.sleep(5)
    time.sleep(2)

out.sort(key=lambda x: -x["play"])
print(json.dumps(out, ensure_ascii=False, indent=1))
