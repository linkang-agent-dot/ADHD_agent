# -*- coding: utf-8 -*-
"""paldb 配种表爬虫：/api/breed?type=parents&result=<slug> ×299 → breed_map.json
产物结构:
  pals:  [[slug, 中文名, 图鉴号], ...]  按 paldb 顺序，下标即内部索引
  pairs: {childIdx: [[p1Idx,p2Idx], ...]}  # 每个孩子的全部父母组合(无序对,p1<=p2)
断点续爬：已存在 breed_map.json 时跳过已爬 child。
用法: python -X utf8 breed_crawl.py
"""
import json, urllib.request, gzip, os, time, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'breed_map.json')

def api(q, retry=3):
    for a in range(retry):
        try:
            req = urllib.request.Request('https://paldb.cn/api/breed?' + q,
                                         headers={'User-Agent': 'Mozilla/5.0'})
            raw = urllib.request.urlopen(req, timeout=30).read()
            if raw[:2] == b'\x1f\x8b':
                raw = gzip.decompress(raw)
            return json.loads(raw.decode('utf-8'))
        except Exception as e:
            if a == retry - 1:
                raise
            time.sleep(2 * (a + 1))

def main():
    pal_resp = api('type=pals')['pals']
    pals = [[p['href'], p['name'], p.get('number', '')] for p in pal_resp]
    idx = {p[0]: i for i, p in enumerate(pals)}
    data = {'pals': pals, 'pairs': {}}
    if os.path.exists(OUT):
        old = json.load(open(OUT, encoding='utf-8'))
        if old.get('pals') == pals:
            data = old
            print(f'resume: {len(data["pairs"])} done')
    for i, (slug, name, num) in enumerate(pals):
        if str(i) in data['pairs']:
            continue
        resp = api('type=parents&result=' + slug)
        combos = []
        for c in resp.get('parents', []):
            a, b = idx[c['parent1']['href']], idx[c['parent2']['href']]
            combos.append([min(a, b), max(a, b)])
        # 去重(无序对)
        combos = sorted(set(map(tuple, combos)))
        data['pairs'][str(i)] = [list(c) for c in combos]
        if (i + 1) % 20 == 0 or i == len(pals) - 1:
            json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
            print(f'{i+1}/{len(pals)} {name} combos={len(combos)}', flush=True)
        time.sleep(0.15)
    json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    total = sum(len(v) for v in data['pairs'].values())
    print(f'DONE pals={len(pals)} total_pairs={total}')

if __name__ == '__main__':
    main()
