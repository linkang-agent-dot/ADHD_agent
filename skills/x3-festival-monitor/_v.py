# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join("..", "ai-to-sql", "scripts"))
from _datain_api import execute_sql
DS = "TRINO_HF"
# 1880-1900 开服 + 在该批夏日 D0(06-09) 的服龄
sql1 = """
SELECT server_id, open_time,
  date_diff('day', try(date(open_time)), DATE '2026-06-09') AS age_at_D0
FROM v1090.dim_open_server
WHERE TRY_CAST(server_id AS INTEGER) BETWEEN 1880 AND 1900
ORDER BY TRY_CAST(server_id AS INTEGER)
"""
print("=== 1880-1900 open / age at summer D0(06-09) ===")
for r in execute_sql(sql1.strip(), DS) or []: print(r)
