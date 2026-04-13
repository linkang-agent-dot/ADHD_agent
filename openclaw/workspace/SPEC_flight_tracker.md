# 携程国际机票价格追踪器 - 技术 SPEC

## 目标

创建一个自动化脚本，每日抓取携程国际机票价格，存储历史数据，生成趋势图表，推送到飞书。

## 功能需求

### 1. 两种运行模式

**模式 A：每日自动推送（cron 触发）**
- 查询 10 条固定热门航线，两个时间窗口
- 生成推送文案 + 趋势图
- 输出文件供推送

**模式 B：按需查询（对话触发）**
- 用户指定目的地和日期范围
- 命令行参数格式：`python ctrip_tracker.py --dest 大阪 --from 2026-04-29 --to 2026-05-05`
- 也支持 `--dest 东京,大阪,曼谷` 多个目的地

### 2. 航线配置

出发地：**成都(CTU)**

固定监控的 10 条热门航线：

| 目的地 | 携程代码 | 国家/地区 |
|--------|----------|-----------|
| 东京 | tyo | 日本 |
| 大阪 | osa | 日本 |
| 曼谷 | bkk | 泰国 |
| 新加坡 | sin | 新加坡 |
| 首尔 | sel | 韩国 |
| 香港 | hkg | 中国香港 |
| 台北 | tpe | 中国台湾 |
| 胡志明市 | sgn | 越南 |
| 吉隆坡 | kul | 马来西亚 |
| 巴厘岛 | dps | 印尼 |

### 3. 时间窗口

每日自动推送查两个范围：
- **30-60 天后**（提前 1-2 个月的价格）
- **60-90 天后**（提前 2-3 个月的价格，早鸟价）

每个时间窗口内，对每条航线找出**最低价及其对应出发日期**。

### 4. 数据抓取方式

使用 Playwright 自动化浏览器访问携程：

```
URL 格式：https://flights.ctrip.com/online/list/oneway-ctu-{目的地代码}?depdate={日期}
```

技术要点：
- `headless=True`
- 自定义 User-Agent（模拟 Chrome）
- 页面加载后等待价格元素出现（`text=¥`），超时 10 秒
- 用正则 `¥(\d{3,5})` 提取价格，过滤 100-30000 范围
- 取页面中的最低价
- **熔断保护**：单条航线超时 15 秒跳过；连续 3 条航线失败则停止整个扫描
- 每条航线查询间隔 2 秒（防反爬）

优化：不需要对每个日期单独打开页面。携程的列表页会显示**日历低价**（页面顶部的日期价格条）。可以一次打开页面，从日历条中提取多个日期的价格。具体实现时可尝试：
1. 先尝试从页面提取日历低价数据（更高效）
2. 如果提取不到，再逐日查询（兜底方案）

### 5. 数据存储

文件路径：`C:\ADHD_agent\openclaw\workspace\flight_data\flight_history.json`

JSON 结构：
```json
{
  "2026-03-25": {
    "东京": {"price": 1780, "dep_date": "2026-05-03", "window": "30-60"},
    "大阪": {"price": 1320, "dep_date": "2026-05-05", "window": "30-60"},
    "东京_early": {"price": 1280, "dep_date": "2026-06-10", "window": "60-90"},
    "大阪_early": {"price": 1350, "dep_date": "2026-06-03", "window": "60-90"}
  },
  "2026-03-24": {
    ...
  }
}
```

- 每天一个 key，记录当天查到的各航线最低价
- `_early` 后缀表示 60-90 天窗口
- 保留最近 30 天数据，自动清理更早的
- 每次运行追加当天数据（如果当天已有则覆盖）

### 6. 趋势图生成

使用 matplotlib 生成折线图：

- 图表大小：12x6 英寸，150 DPI
- X 轴：最近 7 天日期
- Y 轴：价格（¥）
- 每条航线一条线，用不同颜色
- 标注每条线的最低点（价格 + 日期）
- 分两张子图：30-60 天窗口 和 60-90 天窗口
- 中文字体：SimHei 或 Microsoft YaHei
- 输出路径：`C:\ADHD_agent\openclaw\workspace\uploads\flight_trend.png`

如果历史数据不足 7 天，有几天就画几天。第一天运行只有 1 个点，画散点即可。

### 7. 推送文案格式

```
✈️ 成都出发国际机票日报（{月-日}）

📅 1-2个月内（{开始日期}-{结束日期}）低价 Top5：
1. {目的地} ¥{价格} ({出发日期}) {涨跌}  {直飞/中转}
2. ...
3. ...
4. ...
5. ...

📅 2-3个月内（{开始日期}-{结束日期}）低价 Top5：
1. {目的地} ¥{价格} ({出发日期}) {涨跌}  {直飞/中转}
2. ...
3. ...
4. ...
5. ...

📈 趋势：{根据近几天数据的简要分析}
💡 建议：{哪个目的地值得关注}

---每日11:30自动推送
```

涨跌标识规则：
- 与昨天同航线价格比较
- 降价：`↓{差额}`
- 涨价：`↑{差额}`
- 持平（变化 <50）：`→平`
- 无昨日数据：`🆕`

### 8. 脚本入口和参数

脚本路径：`C:\ADHD_agent\openclaw\workspace\ctrip_tracker.py`

```
# 默认模式（cron 用）：查 10 条航线，30-60 天 + 60-90 天
python ctrip_tracker.py

# 自定义查询（对话用）：
python ctrip_tracker.py --dest 大阪 --from 2026-04-29 --to 2026-05-05
python ctrip_tracker.py --dest 东京,大阪,曼谷 --from 2026-06-01 --to 2026-06-15
```

脚本运行后输出：
1. 控制台打印推送文案（供虾哥读取后发飞书）
2. 趋势图保存到 `uploads/flight_trend.png`
3. 历史数据追加到 `flight_data/flight_history.json`

### 9. 依赖

需要安装（如果没有的话）：
- `playwright`（已安装）
- `matplotlib`（如果没有：`pip install matplotlib`）

### 10. 目录结构

```
C:\ADHD_agent\openclaw\workspace\
├── ctrip_tracker.py              # 主脚本（新建）
├── flight_data/
│   └── flight_history.json       # 历史价格数据（自动创建）
└── uploads/
    └── flight_trend.png          # 趋势图（每次覆盖）
```

### 11. Cron 任务更新

更新 `C:\ADHD_agent\openclaw\cron\jobs.json` 中 id 为 `ed08c32f-6c5c-4300-b0fd-e1cd974735fc` 的"国际机票推送"任务：

把 payload.message 改为：
```
请执行以下步骤推送国际机票日报：
1. 运行 exec: python C:\ADHD_agent\openclaw\workspace\ctrip_tracker.py
2. 读取脚本的控制台输出作为推送文案
3. 读取 C:\ADHD_agent\openclaw\workspace\uploads\flight_trend.png 作为趋势图
4. 把文案和趋势图一起发送到飞书
```

### 12. AGENTS.md 规则补充

在 AGENTS.md 的 Tools 部分之前添加：

```markdown
## 机票查询规则

当用户询问机票价格/机票趋势/航班价格时：
1. 使用 exec 运行 `python C:\ADHD_agent\openclaw\workspace\ctrip_tracker.py`
2. 如果用户指定了目的地和日期，加上参数：`--dest 目的地 --from 开始日期 --to 结束日期`
3. 读取脚本输出作为回复内容
4. 如果有趋势图（uploads/flight_trend.png），一起发送
5. **不要自己用 browser 工具去携程网站操作**，直接运行脚本
```

### 13. MEMORY.md 更新

在 MEMORY.md 中添加：

```markdown
## 携程机票追踪器
- 脚本：`C:\ADHD_agent\openclaw\workspace\ctrip_tracker.py`
- 历史数据：`C:\ADHD_agent\openclaw\workspace\flight_data\flight_history.json`
- 趋势图：`C:\ADHD_agent\openclaw\workspace\uploads\flight_trend.png`
- 默认查询：成都出发，10 条热门航线，30-60 天 + 60-90 天窗口
- 自定义用法：`python ctrip_tracker.py --dest 大阪 --from 2026-05-01 --to 2026-05-07`
- Cron：工作日 11:30 自动推送
```

## 实施顺序

1. 先创建 `flight_data/` 目录
2. 写 `ctrip_tracker.py` 主脚本
3. 本地测试一次（选 2 条航线快速验证）
4. 测试通过后更新 cron jobs.json
5. 更新 AGENTS.md 和 MEMORY.md
6. 完成后告诉用户"已完成，可以测试"

## 注意事项

- 所有生成的文件（图片等）必须保存到 `C:\ADHD_agent\openclaw\workspace\uploads\`
- 脚本的 stdout 要用 `sys.stdout.reconfigure(encoding='utf-8')` 处理中文
- matplotlib 中文字体用 `plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']`
- 不要在脚本里直接调飞书 API，只输出文案，由虾哥负责发送
