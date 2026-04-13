# -*- coding: utf-8 -*-
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import rag_search

result = rag_search.search_metrics(
    query="节日活动礼包付费情况 礼包名称 iap_name iap_id 各礼包",
    game_cds=["1041"],
    top_n=5
)
print(json.dumps(result, ensure_ascii=False, indent=2))
