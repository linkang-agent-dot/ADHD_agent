# 携程反爬应对策略

## 当前防护措施

脚本已内置以下反爬手段：

```python
USER_AGENTS = [6个不同UA轮换]
VIEWPORTS   = [5种屏幕尺寸轮换]
每次请求间隔 = random.uniform(2.0, 4.5) 秒
页面加载后等待 = random.uniform(2.5, 5.0) 秒
```

## 触发反爬的症状

1. 所有航线都返回空页面或跳转到登录页
2. 页面内容没有日期价格，只有基本导航
3. 出现验证码页面

## 应对方法

### 方法1：加长等待时间
在 `fetch_calendar_prices()` 中把 `time.sleep(random.uniform(2.5, 5.0))` 改为更长

### 方法2：更换 User-Agent
往 `USER_AGENTS` 列表里加入更新的 Chrome 版本号

### 方法3：减少并发/增加间隔
把 `scan_all_routes()` 中的 `delay = random.uniform(3.0, 7.0)` 改大

### 方法4：添加 cookies（如已登录携程）
```python
context = browser.new_context(...)
context.add_cookies([{"name": "...", "value": "...", "domain": ".ctrip.com"}])
```

## 注意事项

- 脚本每天只运行一次（cron 11:30），正常不会触发限流
- 如果同一天多次运行 `--quick`，建议间隔 30 分钟以上
