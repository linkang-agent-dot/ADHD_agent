# 全局参考

## 认证

```bash
# 首次: 扫码登录（设备授权码模式，扫码选对应组织）
dws auth login

# Headless 环境（服务器）
dws auth login --device   # 输出授权码，手机扫码确认

# 查看状态
dws auth status

# 退出
dws auth logout
```

登录后自动管理 token 刷新，日常使用无需重复登录。

| Token | 有效期 | 说明 |
|-------|--------|------|
| Access Token | 2 小时 | 调用 API 的凭证，过期自动刷新 |
| Refresh Token | 30 天 | 换新 Access Token，使用后轮转 |

30 天内使用一次即自动续期。

### 双版本认证状态（2026-04-10）

| 版本 | 路径 | 登录组织 | 用途 |
|------|------|----------|------|
| dws.local v1.0.8 | `~/.local/bin/dws.local` | 成都创人所爱科技股份有限公司（tap4fun） | 主力，处理大多数产品 |
| dws PC v0.2.27 | `~/.local/bin/dws.ssh-wrapper.bak` | 成都创人所爱科技股份有限公司（tap4fun） | 补充，处理 doc/drive/mail/minutes/aiapp 等 |

`dws` wrapper 自动路由，无需手动选择版本。

### 认证失败处理
- 命令返回 `AUTH_TOKEN_EXPIRED` / `USER_TOKEN_ILLEGAL` / "Token验证失败" → 执行 `dws auth login` 重新登录
- 若 dws.local 认证失效：`dws.local auth login --device`，扫码选 tap4fun 组织

### Headless 环境 (CI/CD)

```bash
# 导出凭证（PC）
dws auth export credentials.json

# 服务器导入
dws auth import credentials.json
```

> refresh_token 单设备独占，远程刷新后源设备凭证失效。

## 全局标志

| 标志 | 短名 | 说明 | 默认 |
|------|:---:|------|------|
| `--format` | `-f` | 输出格式: json / table / raw | table |
| `--verbose` | `-v` | 详细日志 | false |
| `--debug` | | 调试日志 | false |
| `--yes` | `-y` | 跳过确认提示 | false |
| `--dry-run` | | 预览操作不执行 | false |
| `--timeout` | | HTTP 超时 (秒) | 30 |
| `--token` | | API Token（覆盖配置） | 无 |
| `--mock` | | Mock 数据（开发用） | false |
| `--client-id` | | 覆盖 OAuth Client ID | 无 |
| `--client-secret` | | 覆盖 OAuth Client Secret | 无 |

## 输出格式

### --format json（Agent 必须使用）

```json
{"success": true, "body": {...}}
```

### --format table（默认，人类可读）

```
已创建 AI 表格 "项目管理" (UUID: abc123)

下一步:
  dws aitable base get --base-id abc123
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `DWS_CONFIG_DIR` | 覆盖默认配置目录 |
| `DWS_SERVERS_URL` | 自定义服务发现端点 |
| `DWS_CLIENT_ID` | 覆盖 OAuth Client ID (DingTalk AppKey) |
| `DWS_CLIENT_SECRET` | 覆盖 OAuth Client Secret (DingTalk AppSecret) |

凭证优先级: `--token` > `DWS_CLIENT_ID`/`DWS_CLIENT_SECRET` > OAuth 加密存储 (.data)
