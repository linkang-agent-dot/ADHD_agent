# 数据源指南

各数据源的调用方式、限制和注意事项。

## 1. Discord（脚本抓取）

**脚本:** `scripts/fetch_discord.py`
**认证:** TOOLS.md 中的小号 User Token
**限制:** 请求间隔 ≥ 2 秒，防止 rate limit；User Token 调 API 违反 Discord TOS，仅限小号
**输出:** JSON，按频道分组的消息列表

```bash
python3 <SKILL_DIR>/scripts/fetch_discord.py --config <CONFIG> --hours 24 --priority high
```

## 2. App Store（脚本抓取）

**脚本:** `scripts/fetch_appstore.py`
**认证:** 无需，公开 API
**数据源:**
- iTunes Lookup API → 版本号、评分、评分数、更新说明
- App Store RSS → 最新用户评论

```bash
python3 <SKILL_DIR>/scripts/fetch_appstore.py --config <CONFIG> --reviews --country us
```

## 3. Reddit（脚本抓取）

**脚本:** `scripts/fetch_reddit.py`
**认证:** 无需，公开 JSON API
**限制:** 需要 User-Agent header，否则 429

```bash
python3 <SKILL_DIR>/scripts/fetch_reddit.py --config <CONFIG> --hours 24
```

## 4. 礼包码（脚本抓取）

**脚本:** `scripts/fetch_giftcodes.py`
**认证:** 无需
**注意:** 正则提取，可能有误报，需人工确认

```bash
python3 <SKILL_DIR>/scripts/fetch_giftcodes.py --config <CONFIG>
```

## 5. Facebook（脚本抓取，不稳定）

**脚本:** `scripts/fetch_facebook.py`
**认证:** 无需
**注意:** Facebook 反爬严格，经常拿不到内容。备选方案：用 `web_fetch` 工具直接抓页面

```bash
python3 <SKILL_DIR>/scripts/fetch_facebook.py --config <CONFIG>
```

## 6. SensorTower（已有 skill）

**skill:** `sensortower-query`
**用法:** 直接调用 ST skill 的 Python API

```python
import sys
sys.path.insert(0, "/Users/zouhanling/.clawdbot/workspace/skills/sensortower-query/scripts")
from st_api import SensorTowerAPI
api = SensorTowerAPI()

# App 信息（含版本号）
app_info = api.get_app_info(["com.phs.global"])

# 下载量/收入估算
from datetime import datetime, timedelta
start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
sales = api.get_sales_estimates(app_ids=["com.phs.global"], start_date=start, granularity="daily")

# 排名
rankings = api.get_category_rankings(app_ids=["com.phs.global"])
```

## 7. data.ai / App Annie（已有 skill）

**skill:** `appannie-query`
**用法:** 直接调用 AA skill 的 Python API

```python
import sys
sys.path.insert(0, "/Users/zouhanling/.clawdbot/workspace/skills/appannie-query/scripts")
from aa_api import AppAnnieAPI
api = AppAnnieAPI()

# App 详情
details = api.app_details("google-play", "com.phs.global")

# 评分
ratings = api.app_ratings("google-play", "com.phs.global")

# 排名（需要 numeric ID，先转换）
numeric_id = api.package_to_id("google-play", "com.phs.global")
ranks = api.app_ranks("google-play", str(numeric_id), start_date, end_date)
```

## 8. Google Play 商店页（web_fetch）

Google Play 网页版不显示版本号，用 `web_fetch` 只能拿到游戏描述和基本信息。
版本号通过 SensorTower app_info 获取。

## 9. 攻略站（web_fetch）

直接用 `web_fetch` 抓取：
- lastasylumplague.com — 英雄数据、建筑升级
- lastasylum.com — FAQ、礼包码
