# 节日礼包付费评级 Skill

## 一句话描述

从 Trino 查礼包付费数据 → 按活动分组 → 四维评分 → 写入评分表 GSheet，全流程自动化。

## 触发词

"礼包评级"、"活动评级"、"付费评级"、"节日评分"、"评分表更新"、"iap rating"、"写评分表"

---

## 评分体系（评分表四维）

| 维度 | 公式 | 权重 | 阈值逻辑 |
|------|------|------|---------|
| **变现力** | ARPU × 付费率(%) / 10 | 50% | ≥40→100, ≥10→85, ≥2.5→70, ≥1.5→55, ≥0.2→40, 其余→20 |
| **转化力** | 付费率(%) | 25% | ≥20→100, ≥15→80, ≥10→60, ≥5→40, 其余→20 |
| **鲸鱼依赖度** | 超R收入占比(%) | 15% | 50-70%→100(最健康), 45-50/70-75→85, 40-45/75-80→70, 35-40/80-85→55, 其余→40 |
| **分层清晰度** | chaoR付费人数/xiaoR付费人数 | 10% | 3-8x→100, 2-3x/8-15x→80, 1.5-2x/15-30x→60, 1-1.5x/30-50x→40, <1x/>50x→20 |

**综合得分** = 变现力×0.5 + 转化力×0.25 + 鲸鱼依赖度×0.15 + 分层清晰度×0.10

**等级**: ≥73.5 → A, ≥56 → B, ≥41 → C, <41 → D

> **分母**：全量登录活跃付费玩家（需用户提供，或查当期整体付费数据）

---

## 流程总览

```
Step 1  用户给出礼包名列表 + 时间范围 + 活动分组规则
  ↓
Step 2  用 SQL 查 Trino：R级分解（ods_user_order × dim_iap × da_user_rlevel_pay_ratio）
  ↓
Step 3  Python 聚合：每个活动的 pay_total / pay_num / arpu / chaor_pct / fenceng_ratio
  ↓
Step 4  四维评分计算 + 生成 JSON 结果文件
  ↓
Step 5  用 gws.cmd 写入 Google Sheet 评分表（正确列：A-O，共15列）
```

---

## Step 1：收集输入

### 必须从用户处获取

1. **礼包名列表**（`iap_id_name`）：可从 `dim_iap` 查，或用户直接给出
2. **时间范围**：`partition_date` 范围（比时间范围各宽1天）+ `created_at` 精确范围
3. **活动分组 CASE WHEN**：把礼包名映射到活动类别（见下方模板）
4. **分母**（总活跃付费玩家数）：用户提供，或查整体付费数据
5. **GSheet 写入行号**：目标表 + 数据起始行（通常是现有最后行+2，留一行给区块标题）

### 活动分组模板

```sql
CASE
    WHEN d.iap_id_name = 'XXX礼包A'          THEN '活动1-子类型'
    WHEN d.iap_id_name IN ('礼包B','礼包C')   THEN '活动2-子类型'
    -- ...
    ELSE 'other'
END AS activity
```

> **命名规范**：`节日名-活动类型`，跨节日同类型合并时用 `节日-类型`（如"节日-大富翁"、"节日-行军外观"）

---

## Step 2：Trino SQL 模板

**脚本入口**：`C:\ADHD_agent\.agents\skills\ai-to-sql\scripts\_datain_api.py`

```python
import sys
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
from _datain_api import execute_sql

# 时间范围（partition_date 比 created_at 范围各宽1天）
PARTITION_START = '2026-03-11'
PARTITION_END   = '2026-04-04'
DATE_START      = '2026-03-12'
DATE_END        = '2026-04-03'

# 礼包列表（用 iap_id_name 精确匹配）
PACK_NAMES = [...]

name_list = "','".join(PACK_NAMES)

sql = f"""
WITH rlevel_snap AS (
    SELECT user_id, max_by(rlevel, create_date) AS rlevel
    FROM v1041.da_user_rlevel_pay_ratio
    WHERE create_date BETWEEN '{PARTITION_START}' AND '{PARTITION_END}'
    GROUP BY 1
),
orders AS (
    SELECT
        o.user_id,
        -- ↓ 活动分组（按实际情况填写）
        CASE
            WHEN d.iap_id_name = '礼包A' THEN '活动1'
            WHEN d.iap_id_name IN ('礼包B','礼包C') THEN '活动2'
            ELSE 'other'
        END AS activity,
        o.pay_price,
        coalesce(r.rlevel, 'feiR') AS rlevel
    FROM v1041.ods_user_order o
    JOIN v1041.dim_iap d ON o.iap_id = d.iap_id
    LEFT JOIN rlevel_snap r ON o.user_id = r.user_id
    WHERE o.partition_date BETWEEN '{PARTITION_START}' AND '{PARTITION_END}'
      AND date(date_add('hour', -8, o.created_at)) BETWEEN date '{DATE_START}' AND date '{DATE_END}'
      AND o.pay_status = 1
      AND d.iap_id_name IN ('{name_list}')
)
SELECT
    activity,
    rlevel,
    count(distinct user_id) AS pay_cnt,
    round(sum(pay_price), 2)  AS pay_total
FROM orders
GROUP BY 1, 2
ORDER BY activity, pay_total DESC
"""

rows = execute_sql(sql, 'TRINO_AWS')
```

> **注意**：执行脚本时需 `cd C:\ADHD_agent\.agents\skills\ai-to-sql\scripts`

---

## Step 3：Python 聚合模板

```python
from collections import defaultdict

TOTAL_PAYERS = 12474  # ← 从用户处获取

data = defaultdict(lambda: {'pay_total': 0, 'rlevel': {}})
for r in rows:
    act, rl = r['activity'], r['rlevel']
    pay, cnt = float(r['pay_total'] or 0), int(r['pay_cnt'] or 0)
    data[act]['pay_total'] += pay
    if rl not in data[act]['rlevel']:
        data[act]['rlevel'][rl] = {'cnt': 0, 'pay': 0}
    data[act]['rlevel'][rl]['cnt'] += cnt
    data[act]['rlevel'][rl]['pay'] += pay
```

---

## Step 4：四维评分函数

```python
def score_xianli(v):   # v = ARPU × 付费率(%) / 10
    if v >= 40:  return 100
    if v >= 10:  return 85
    if v >= 2.5: return 70
    if v >= 1.5: return 55
    if v >= 0.2: return 40
    return 20

def score_zhuanhua(v): # v = 付费率(%)
    if v >= 20:  return 100
    if v >= 15:  return 80
    if v >= 10:  return 60
    if v >= 5:   return 40
    return 20

def score_jingyu(v):   # v = 超R收入占比(%)，50-70%最健康
    if 50 <= v <= 70:  return 100
    if (45 <= v < 50) or (70 < v <= 75): return 85
    if (40 <= v < 45) or (75 < v <= 80): return 70
    if (35 <= v < 40) or (80 < v <= 85): return 55
    return 40

def score_fenceng(v):  # v = chaoR人数/xiaoR人数；xiaoR=0 时 v=99
    if 3 <= v <= 8:   return 100   # 最佳梯度
    if (2 <= v < 3) or (8 < v <= 15):    return 80
    if (1.5 <= v < 2) or (15 < v <= 30): return 60
    if (1 <= v < 1.5) or (30 < v <= 50): return 40
    return 20   # <1x（无分层）或>50x（纯鲸鱼）

def grade(s):
    if s >= 73.5: return 'A'
    if s >= 56:   return 'B'
    if s >= 41:   return 'C'
    return 'D'

# 每个活动计算
for act, d in data.items():
    total_pay  = round(d['pay_total'], 2)
    rl = d['rlevel']
    total_num  = sum(v['cnt'] for v in rl.values())
    arppu      = round(total_pay / total_num, 2) if total_num > 0 else 0
    pay_rate   = round(total_num / TOTAL_PAYERS * 100, 2)
    arpu       = round(total_pay / TOTAL_PAYERS, 2)
    chaor_pay  = rl.get('chaoR', {}).get('pay', 0)
    chaor_cnt  = rl.get('chaoR', {}).get('cnt', 0)
    xiaor_cnt  = rl.get('xiaoR', {}).get('cnt', 0)
    chaor_pct  = round(chaor_pay / total_pay * 100, 1) if total_pay > 0 else 0
    fenceng_ratio = round(chaor_cnt / xiaor_cnt, 2) if xiaor_cnt > 0 else 99.0

    xianli_val  = round(arpu * pay_rate / 10, 3)
    s_xianli    = score_xianli(xianli_val)
    s_zhuanhua  = score_zhuanhua(pay_rate)
    s_jingyu    = score_jingyu(chaor_pct)
    s_fenceng   = score_fenceng(fenceng_ratio)
    total_score = round(s_xianli*0.5 + s_zhuanhua*0.25 + s_jingyu*0.15 + s_fenceng*0.10, 1)
    lv = grade(total_score)
```

---

## Step 5：写入 Google Sheet

### 目标表

```
Spreadsheet ID: 1ElKLw7zvz2-vjcgNkjpC54d6nW04lke_NWOPQs0Uq0Q
Sheet Tab:      评分表（每月更新）
```

### 列映射（A-O，共 15 列，每期新增区块标题+表头 2 行）

| 列 | 字段 | 说明 |
|----|------|------|
| A | 活动（短名） | 去掉节日前缀的玩法名，如"挖孔小游戏" |
| B | 上线次数 | 本次统计的期数（通常为1） |
| C | 原始活动 | 所含礼包名完整列表 |
| D | 综合得分 | total_score |
| E | 等级 | A/B/C/D |
| F | 变现力得分 | s_xianli |
| G | 转化力得分 | s_zhuanhua |
| H | 鲸鱼依赖度得分 | s_jingyu |
| I | 分层清晰度得分 | s_fenceng |
| J | 付费ARPU | arpu（总付费÷总活跃付费玩家） |
| K | 付费率 | pay_rate(%) |
| L | 超R收入占比 | chaor_pct(%) |
| M | 总付费额 | pay_total（实际收入，RMB） |
| N | 投放内容 | 留空（人工填写） |
| O | 节日时间 | 节日标识，如"2026科技节" |

> ⚠️ 写入前在表头行上方加一行**区块标题**（节日名），再加一行**列头**（复制第9行表头）

### 写入命令

```python
import json, subprocess

GWS_CMD     = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET = "1ElKLw7zvz2-vjcgNkjpC54d6nW04lke_NWOPQs0Uq0Q"
SHEET       = "评分表（每月更新）"

# rows_data: [[A,B,...,O], ...]  -- 15列
DATA_START = 36   # 数据行号（区块标题在DATA_START-2，列头在DATA_START-1）
end_row    = DATA_START + len(rows_data) - 1
range_str  = f"'{SHEET}'!A{DATA_START}:O{end_row}"

params = json.dumps({"spreadsheetId": SPREADSHEET})
body   = json.dumps({
    "valueInputOption": "USER_ENTERED",
    "data": [{"range": range_str, "majorDimension": "ROWS", "values": rows_data}]
}, ensure_ascii=False)

result = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'batchUpdate',
     '--params', params, '--json', body],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print(result.stdout)
```

---

## 参考脚本（本次执行生成）

| 文件 | 用途 |
|------|------|
| `_tmp_multi_rating_final_v4.py` | 完整查询+评分脚本（含 CASE WHEN 模板） |
| `_tmp_rating_v4.json` | 评分结果缓存 |
| `_tmp_fix_rating_cols.py` | 写入 GSheet 脚本（A36:O58，15列） |

---

## 常见问题

### Q: 礼包找不到 / 查出0行？

`ods_user_order` 存储的 `iap_id` 带后缀（如 `_normal`），通过 `JOIN dim_iap` 匹配 `iap_id_name` 时已处理，无需手动加后缀。如仍无结果，先执行：
```sql
SELECT DISTINCT d.iap_id_name
FROM v1041.ods_user_order o
JOIN v1041.dim_iap d ON o.iap_id = d.iap_id
WHERE o.partition_date BETWEEN '...' AND '...'
  AND d.iap_id_name LIKE '%关键词%'
LIMIT 50
```

### Q: 分母如何确定？

优先使用"全量登录活跃付费玩家"（当期登录过且有过付费记录的用户数）。
查询方式：读取整体付费数据报告（如 `P2_节日活动付费数据情况_图表SQL.sql`），取其中的 `总付费玩家数`。

### Q: 分层清晰度 fenceng_ratio 异常？

- **比例 = 1.0x**：超R和小R以相同比率参与，活动普惠性强但无分层（低价礼包常见，如"挖矿小游戏"）
- **比例 > 50x**：小R几乎不参与，属于鲸鱼专属活动（如"改造猴特权"92x）→ D级
- **xiaoR = 0**：取 ratio = 99，自动归为 D

### Q: GSheet 写入报错 "Invalid --params JSON"？

`@filepath` 语法在此版本 `gws` 不支持。必须将 JSON 作为字符串直接传参，且必须使用 `subprocess.run([GWS_CMD, ...])`（list方式），**不能用 shell=True**。

---

## 历史评级结果

| 时期 | 分母 | 结果文件 | GSheet 行 |
|------|------|---------|----------|
| 3.12-4.03（科技节） | 12,474 | `_tmp_rating_v4.json` | Row 36-58 |
