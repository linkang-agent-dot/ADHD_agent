# 大麦 App 抢票脚本

通过 ADB + uiautomator2 控制安卓设备上的大麦 App，自动抢票。
适用于"该渠道不支持"只能在 App 内购买的演出。

## 前置准备

### 方案 A：安卓模拟器（推荐 MuMu）

1. 下载安装 [MuMu 模拟器](https://mumu.163.com/)
2. 在模拟器中安装大麦 App
3. 打开模拟器设置 → 开启 ADB 调试
4. 记下 ADB 端口号（MuMu 默认 7555）

### 方案 B：安卓真机（抢票成功率更高）

1. 手机 USB 连电脑
2. 手机设置 → 开发者选项 → 开启 USB 调试
3. 在电脑上安装 [ADB 工具](https://developer.android.com/tools/releases/platform-tools)
4. 运行 `adb devices` 确认识别到手机

### 安装 Python 依赖

```bash
cd ticket_sniper
pip install -r requirements.txt
```

## 使用步骤

### 1. 配置

编辑 `config.yaml`：

```yaml
# 设备地址（MuMu 默认 7555，雷电默认 5555）
device_addr: "127.0.0.1:7555"

# 演出链接（在大麦 App 里 → 分享 → 复制链接）
share_url: "https://m.damai.cn/shows/item.html?itemId=你的ID"

# 开售时间
start_time: "2026-03-15 10:00:00"

# 想抢的票档
wanted_tickets:
  - "580"
  - "380"

ticket_count: 1
```

### 2. 运行

```bash
python snipe.py
```

或命令行传参：

```bash
python snipe.py --ticket "580" --count 2 --time "2026-03-15 10:00:00"
```

### 3. 流程

```
1. 自动连接模拟器/手机
2. 启动大麦 App，关闭弹窗
3. 通过 deeplink 跳转到演出详情页
4. [定时模式] 精确等到开售时间
5. 高频循环：选票档 → 立即购买 → 选购票人 → 提交订单
6. 成功后截图，等你在手机上支付
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `-c` | 配置文件路径 |
| `--url` | 演出分享链接 |
| `--time` | 抢购时间 |
| `--ticket` | 票档关键词 |
| `--count` | 购票数量 |
| `--device` | 设备地址 |

## 注意事项

- **提前登录**：运行前先在模拟器/手机的大麦 App 里登录好账号
- **提前设购票人**：在大麦 App → 我的 → 常用购票人 中添加好
- **模拟器 vs 真机**：模拟器容易触发验证码，真机更稳定
- **ADB 检测**：运行 `adb devices` 确认设备已连接
