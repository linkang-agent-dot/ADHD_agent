---
name: ctrip-tracker
description: 携程国际机票价格追踪器维护与操作工具。支持成都出发10条热门航线的价格抓取、直飞过滤、趋势图生成和飞书推送。当用户提到"机票追踪"、"机票脚本"、"ctrip_tracker"、"看看机票"、"机票报错"、"直飞价格"、"成都飞XX价格"时使用。也用于排查脚本抓不到价格、直飞过滤不生效等问题。
---

# 携程机票追踪器 (ctrip_tracker)

## 脚本位置

```
C:\ADHD_agent\openclaw\workspace\ctrip_tracker.py
```

数据目录：
| 用途 | 路径 |
|------|------|
| 历史价格 | `C:\ADHD_agent\openclaw\workspace\flight_data\flight_history.json` |
| 趋势图输出 | `C:\ADHD_agent\openclaw\workspace\uploads\flight_trend.png` |

---

## 常用命令

```powershell
# 快速扫描（10条航线，每窗口1个采样点，~4分钟）
python ctrip_tracker.py --quick

# 完整扫描（所有航线，全日期采样，用于 cron）
python ctrip_tracker.py --full

# 查询特定目的地+日期范围（含转机，最低价）
python ctrip_tracker.py --dest 东京 --from 2026-05-01 --to 2026-06-30

# 查询直飞价格（真正过滤，解析页面「直飞¥」标记）
python ctrip_tracker.py --dest 日本 --from 2026-05-01 --to 2026-06-30 --direct

# 多城市（支持国家别名）
python ctrip_tracker.py --dest 东南亚 --from 2026-05-01 --to 2026-06-30

# 测试单条航线
python ctrip_tracker.py --test 东京
```

**支持的国家别名**：日本（东京+大阪）、泰国（曼谷）、韩国（首尔）、东南亚（曼谷/新加坡/胡志明市/吉隆坡/巴厘岛）

---

## 架构说明

### 价格抓取机制

脚本使用 Playwright（无头 Chrome）抓取携程航班搜索页面，有两种抓取模式：

**模式1：日历栏（默认，含转机最低价）**
- URL 格式：`https://flights.ctrip.com/online/list/oneway-ctu-{code}?depdate={date}`
- 每次加载显示约 7 天日历，解析 `MM-DD 周X\n¥ PRICE` 格式
- 关键正则（注意日期和周之间有空格，¥后有空格）：
  ```python
  r'(\d{2})-(\d{2})\s*[周][一二三四五六日]\s*\n\s*[¥￥]\s*(\d+)'
  ```

**模式2：直飞价格（`--direct` 参数触发）**
- 每个日期单独加载，解析页面顶部「直飞¥XXXX」标记
- 关键正则：`r'直飞[¥￥]\s*(\d+)'`
- 每条航线对日期范围均匀采样 4 个点取最低值
- 注意：`directflight=1` URL 参数不改变日历栏，日历栏永远显示含转机最低价

### 扫描窗口

| 窗口 | 天数范围 | 说明 |
|------|----------|------|
| 1-2个月 | 30-60天后 | 主要窗口 |
| 2-3个月 | 60-90天后 | 早鸟窗口 |

---

## 已知 BUG 与修复记录

### BUG #1：价格解析正则缺少空格（2026-03-31 修复）

**症状**：所有航线显示「未获取到价格」，连续失败后停止扫描。

**根因**：携程页面格式为 `04-26 周日\n¥ 1369`（日期和周之间有空格，¥后有空格），但原始正则没有 `\s*` 处理这些空格。

**修复**：在 `parse_calendar_prices()` 函数中，正则添加 `\s*`：
```python
# ❌ 原来（匹配不到）
r'(\d{2})-(\d{2})[\u5468][一二三四五六日]\s*\n\s*[¥\uffe5](\d+)'

# ✅ 修复后
r'(\d{2})-(\d{2})\s*[\u5468][一二三四五六日]\s*\n\s*[¥\uffe5]\s*(\d+)'
```

**预防**：如果将来又出现所有航线失败，第一步先检查携程页面的实际文本格式是否变化（运行 debug 脚本）。

### BUG #2：`--direct` 参数未真正过滤直飞（2026-03-31 修复）

**症状**：`--direct` 显示的价格仍是含转机的日历最低价。

**根因**：`--direct` 原本只是在输出文本中显示「直飞航空公司」信息标签，不改变抓取逻辑。

**修复**：`--direct` 现在触发 `fetch_direct_price()` 函数，逐日期加载页面解析「直飞¥」标记。详见参考文档。

---

## 排障流程

### 抓不到价格时

1. **先运行 debug 脚本**，看携程返回的实际页面文本格式：

```python
from playwright.sync_api import sync_playwright
import time, re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(locale='zh-CN', timezone_id='Asia/Shanghai')
    page = ctx.new_page()
    page.goto('https://flights.ctrip.com/online/list/oneway-ctu-tyo?depdate=2026-05-03', timeout=25000)
    time.sleep(4)
    text = page.inner_text('body')
    # 找价格片段
    prices = re.findall(r'.{0,30}[¥￥]\s*\d{3,5}.{0,30}', text)
    for p2 in prices[:10]:
        print(repr(p2))
    browser.close()
```

2. 对比实际格式与正则，调整 `parse_calendar_prices()` 中的正则
3. 如果页面完全没有价格，可能是携程触发了反爬（更换 UA 或加长等待时间）

### 直飞显示「无直飞」但实际有直飞

- 检查 `ROUTES` 中该城市的 `direct` 字段是否正确
- 手动打开 URL 确认「直飞¥」标记是否出现

---

## 参考文档

- `references/routes.md` — 10条航线详情和直飞航司信息
- `references/anti-scrape.md` — 携程反爬应对策略
