# -*- coding: utf-8 -*-
"""paldb.cn 全帕鲁抓取：列表页(已存) + 301个详情页 -> pals_full.json"""
import re, json, time, urllib.request, os, sys

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}
OUT = os.path.dirname(os.path.abspath(__file__))

raw = open(os.path.join(OUT, "paldb_pals.html"), encoding="utf-8").read()
parts = re.split(r'(?=<img alt="[^"]+" loading="lazy"[^>]*PalIcon)', raw)

# href 错位修正: 卡片 i 的 href 出现在 parts[i-1] 尾部(parts[0]=头部)
pals = []
for idx, seg in enumerate(parts[1:], start=1):
    m = re.match(r'<img alt="([^"]+)"', seg)
    if not m:
        continue
    name = m.group(1)
    body = seg[:4000]
    num = re.search(r'#[^0-9]{0,80}?(\d{1,3})', body)
    elems = re.findall(r'alt="(无|草|火|水|雷|冰|土|地|暗|龙)属性"', body)
    hrefs_prev = re.findall(r'href="(/pals/[^"]+)"', parts[idx - 1][-3000:])
    pals.append({
        "name": name,
        "num": int(num.group(1)) if num else None,
        "href": hrefs_prev[-1] if hrefs_prev else None,
        "elems": elems,
    })
print("cards:", len(pals), flush=True)

WORKS = "播种|生火|浇水|发电|手工作业|采集|伐木|采矿|制药|冷却|搬运|牧场"

def parse_detail(html):
    text = re.sub(r"<[^>]+>", "|", html)
    d = {}
    m = re.search(r'<img alt="([^"]{1,20})"[^>]*T_icon_ski', html)  # 图标alt最可靠
    if not m:
        m = re.search(r"伙伴技能：(.+?)。", html)  # meta兜底(约19只会漏)
    d["skill"] = m.group(1) if m else ""
    eff = ""
    if d["skill"]:
        mm = re.search(re.escape(d["skill"]) + r"\|+([^|{]{6,200}?)(?:\{[^}]*\})?科技(\d+)", text)
        if mm:
            eff = mm.group(1).strip()
            d["skill_tech"] = int(mm.group(2))
        else:
            mm2 = re.search(re.escape(d["skill"]) + r"\|+([^|]{6,200})", text)
            eff = mm2.group(1).strip() if mm2 else ""
    d["skill_desc"] = eff
    d["ride"] = ("骑" in eff) or ("坐骑" in eff)
    d["fly"] = ("飞" in eff and d["ride"])
    for key, pat in [("hp", r"\|HP\|+(\d+)"), ("atk", r"\|攻击\|+(\d+)"), ("def", r"\|防御\|+(\d+)")]:
        mm = re.search(pat, text)
        d[key] = int(mm.group(1)) if mm else None
    d["works"] = [(w, int(l)) for w, l in re.findall(r"(" + WORKS + r")\|+Lv \|(\d+)", text)]
    # 去重保序
    seen = set(); ws = []
    for w, l in d["works"]:
        if w not in seen:
            seen.add(w); ws.append((w, l))
    d["works"] = ws
    # 野外最早出现等级(出现地点段的 Lv. a–b 区间取最小)
    i1 = text.find("出现地点")
    if i1 >= 0:
        lvs = re.findall(r"Lv\.\s*(\d+)\s*[–\-]\s*\d+", text[i1:i1+4000])
        d["minlv"] = min(int(x) for x in lvs) if lvs else None
    else:
        d["minlv"] = None
    return d

out_path = os.path.join(OUT, "pals_full.json")
done = {}
if os.path.exists(out_path):
    done = {p["name"]: p for p in json.load(open(out_path, encoding="utf-8"))}

results = []
for i, p in enumerate(pals):
    if p["name"] in done and "minlv" in done[p["name"]]:
        results.append(done[p["name"]]); continue
    rec = dict(p)
    if p["href"]:
        for attempt in range(3):
            try:
                url = "https://paldb.cn" + p["href"]
                html = urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30).read().decode("utf-8", "ignore")
                rec.update(parse_detail(html))
                break
            except Exception as e:
                if attempt == 2:
                    rec["error"] = repr(e)[:60]
                time.sleep(4 * (attempt + 1))
    results.append(rec)
    if (i + 1) % 25 == 0:
        print(f"{i+1}/{len(pals)}", flush=True)
        json.dump(results, open(out_path, "w", encoding="utf-8"), ensure_ascii=False)
    time.sleep(0.8)

# 去重(列表页变体区会重复收录, 如派克龙/雷胖达)
seen=set(); results=[r for r in results if not ((r["name"],r.get("href")) in seen or seen.add((r["name"],r.get("href"))))]
json.dump(results, open(out_path, "w", encoding="utf-8"), ensure_ascii=False)
ok = sum(1 for r in results if r.get("hp") is not None)
print(f"DONE {ok}/{len(results)} with stats", flush=True)
