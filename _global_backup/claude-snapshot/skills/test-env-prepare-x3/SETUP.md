# 环境准备指南

## 1. igame 凭证

创建 `~/.igame-credentials.json`：

```json
{"token": "xxx", "clientId": "xxx"}
```

获取方式：
1. 打开 https://igame-qa.tap4fun.com 并登录
2. F12 打开 Console
3. 执行 `localStorage.getItem("ark_token")` 获取 token
4. 执行 `localStorage.getItem("ark_clientId")` 获取 clientId
5. 需要有 X3 项目（gameId=1090）的 GM 操作权限，没有的话找管理员申请

token 会过期，过期后重新获取替换即可。

## 2. Python 依赖

```bash
pip install openpyxl asyncssh requests pymongo
```

- `openpyxl` — 配置表查询（查道具 ID、活动 ID 等）
- `asyncssh` — 物理机时间调整（经 JumpServer SSH）
- `requests` — Jenkins API 调用
- `pymongo` — MongoDB 数据查询（查玩家英雄、资源、活动状态等）

GM 执行只用 Python 标准库。

## 3. gdconfig 配置仓库（可选）

配置表查询需要：

```bash
cd x3-project
git clone --depth 1 git@git.tap4fun.com:x3/gdconfig.git gdconfig
```

不需要查配置表可跳过。

gdconfig 不会自动更新。策划新增/修改配置后需要手动 pull：
```bash
cd gdconfig && git pull
```
不过道具 ID、活动 ID 等一般不会频繁变化，只有新增内容时才需要更新。

## 4. Jira 凭证

创建 `~/.jira-credentials.json`：

```json
{"token": "xxx"}
```

获取方式：Jira 右上角头像 → 个人资料 → Personal Access Tokens → 创建新 token。

## 5. Kadmin

无需额外配置，access key 已内置在 `scripts/kadmin_api.py` 中。

## 6. MongoDB（Beta 数据查询）

无需额外配置，连接串已内置在 `scripts/mongo_query.py` 中。需能访问内网 `x3-beta-nlb.a3games.com:27017`。
