---
name: X3 节日付费表现与饱和度数据
description: X3各节日单服收益排名、尼罗最佳上线服龄窗口、道具饱和度速查、X3数仓SQL模板
type: reference
originSessionId: 7f1d10e6-76c8-46b3-b30d-957a641cda96
---

## 各节日单服收益排名（截至2026-05）

| 排名 | 节日 | 单服收益(USD) | Pack ID前缀 |
|------|------|-------------|------------|
| 1 | 尼罗之辉 | ~$1,127 | 2106xx |
| 2 | 圣诞 | ~$811 | — |
| 3 | 感恩节 | ~$705 | — |
| 4 | 情人节 | ~$605 | 2107xx |
| 5 | 凛冬 | ~$444 | — |
| 6 | 春节 | ~$428 | 2108xx |

> 单服收益 = 节日期间总营收 / 参与服务器数量；是节日重上优先级的核心评估指标。

## 尼罗之辉重上：最佳服龄窗口

- **最佳窗口**：D17–D35（服务器开服后第17–35天）
- **建议策略**：D21 入场、D35 出场、活动时长14天
- **依据**：
  - 首批服（高付费、大服）在 D17-D25 区间贡献了最高单服收益
  - 第二批服同服龄下收益明显低于首批，说明不同批次服体量差异大
  - D35后玩家付费意愿下降，主要内容基本完成

## 核心道具饱和度速查（截至2026Q1）

### 纪念卡（Item_180xxx）
| ID | 名称 | 节日 | 饱和度 |
|----|------|------|-------|
| 180076 | 尼罗回响 | 26尼罗 | 待查 |
| 180077 | 我对你的誓言 | 26情人节 | 待查 |
| 180078 | 新春特辑 | 26春节 | 待查 |

### 英雄晋升皮肤（Item_530xxxx）
| ID | 名称 | 节日 |
|----|------|------|
| 53017 | 热浪尤物·赛米拉 | 25海滨假日 |
| 5301501 | 甜心咖啡师·海泽尔 | 26情人节 |
| 530202 | 红绸剑姬·阿米娜 | 26春节 |

### 岛屿皮肤（Item_81xxx）
| ID范围 | 节日 | 备注 |
|--------|------|------|
| 81001 | 南瓜灯岬 | 永久款 |
| 81051 | 柔情海湾 | 永久款 |
| 81151 | 金字塔之城 | 永久款 |

### 家具/装饰（Item_151xxx / Item_152xxx）
| ID范围 | 类型 | 节日 |
|--------|------|------|
| 151057-151058 | 家具摆件/地毯 | 26尼罗 |
| 151059-151061 | 家具摆件/地毯 | 26情人节 |
| 152027-152029 | 主城装饰三件套 | 26春节新春典藏 |
| 152024-152026 | 主城装饰三件套 | 25圣诞庆典 |

---

## X3数仓SQL速查

### 关键表（TRINO_HF，v1090视图）
```sql
v1090.ods_user_daily      -- 玩家每日快照
v1090.ods_user_order      -- 付费订单（pay_status=1为成功）
v1090.ods_user_asset      -- 资产变动（asset_id格式见下）
v1090.ods_user_activity   -- 活动参与
```

### ods_user_order 关键字段
- ⚠️ 用户列名是 `user_id`（VARCHAR），**不是 `uid`**（本文模板里历史写的 `uid` 会报 Column cannot be resolved，2026-06-22 查尼罗踩坑）。`server_id` 也是 VARCHAR，排序/比较前 `cast(... as integer)`。
- `iap_id` VARCHAR — Pack ID（如 '210716'）
- `pay_status` INT — 1=成功
- `actual_charge` — USD实际扣款额
- `pay_price` — 标价
- `currency_type` — 'usd'/'TOKEN'/其他货币

### USD收益计算公式
```sql
SUM(CASE WHEN currency_type IN ('usd','TOKEN') 
    THEN actual_charge 
    ELSE pay_price END) AS revenue_usd
```

### ods_user_asset 关键字段
- `asset_id` VARCHAR — 资产ID（格式见下）
- `change_type` INT — 变动类型
- `server_id` — 服务器ID

### asset_id 前缀格式
| 前缀 | 品类 |
|------|------|
| `Item_81xxx` | 岛屿皮肤（主城皮肤） |
| `Item_530xxxx` | 英雄晋升皮肤 |
| `Item_151xxx` | 家具摆件/地毯 |
| `Item_152xxx` | 主城装饰三件套道具 |
| `Item_180xxx` | 纪念卡 |
| `FurnitureDecorateSkinID_XXXX` | 主城装饰三件套已解锁皮肤 |

### 节日付费查询模板
```sql
-- 某节日总收入 + 付费人数
SELECT 
  COUNT(DISTINCT uid) AS payer_cnt,
  SUM(CASE WHEN currency_type IN ('usd','TOKEN') THEN actual_charge ELSE pay_price END) AS revenue_usd
FROM v1090.ods_user_order
WHERE pay_status = 1
  AND iap_id IN ('210701','210702',...,'210718')  -- 替换为目标Pack ID列表
  AND dt BETWEEN '2026-01-29' AND '2026-02-15'
;

-- 分Pack收入排名
SELECT 
  iap_id,
  COUNT(DISTINCT uid) AS payer_cnt,
  SUM(CASE WHEN currency_type IN ('usd','TOKEN') THEN actual_charge ELSE pay_price END) AS revenue_usd
FROM v1090.ods_user_order
WHERE pay_status = 1
  AND iap_id LIKE '2107%'   -- 情人节Pack前缀
GROUP BY iap_id
ORDER BY revenue_usd DESC
;
```

### 饱和度查询模板（按资产获取）
```sql
-- 某道具持有人数（占付费玩家比例）
SELECT COUNT(DISTINCT uid) AS holders
FROM v1090.ods_user_asset
WHERE asset_id = 'Item_81001'   -- 替换为目标asset_id
  AND change_type > 0            -- 获得
;
```

### TRINO_HF注意事项
- 默认 catalog 是 iceberg，**不需要** `hive.` 前缀
- 不支持 `LIMIT x OFFSET y` 分页语法
- v1090 视图已内置 game_cd 过滤，SQL 无需再加 WHERE game_cd=1090
- `iap_id` 是 VARCHAR，用字符串比较：`iap_id = '210716'`
- `pay_status` 是 INT，用整型比较：`pay_status = 1`
