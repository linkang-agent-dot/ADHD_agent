---
name: igame-gm-send
description: 在 iGame 后台执行 GM 指令（toolbox/gm/update，对应 ark/gm-operate/add），支持指定服务器、玩家和参数。触发词：GM 指令、后台发 GM、给玩家执行 GM、multicmd、gm-operate。未指定环境时默认 dev。
---

# iGame GM Update

用于“iGame 后台输入 GM 指令”的场景，直接调用 iGame 网关接口发送 GM。

## Scope

- 仅处理 GM 指令下发，不包含活动部署、导库、封禁等其他能力。
- 默认环境为 `dev`；用户明确说 `beta` 时才用 `beta`。

## Endpoint

| 环境 | 地址 |
|---|---|
| dev（默认） | `https://ms-inner-gateway-dev.tap4fun.com/ark/gm-operate/add` |
| beta | `https://ms-inner-gateway-qa.tap4fun.com/ark/gm-operate/add` |

## 请求体约束（必须）

```json
{
  "operateType": 3,
  "gmCommand": [
    "{ \"server_ids\": [ 402 ], \"cmd\": \"paddassets\", \"players\": [123456], \"args\": [\"11151001\", \"100000\"] }；"
  ]
}
```

- `operateType` 默认 `3`。
- `gmCommand` 是字符串数组；每条为一段 GM JSON 文本，末尾追加 `；`。
- GM JSON 内部字段使用：`server_ids`、`cmd`、`players`、`args`。
- 鉴权来自本地 `C:/Users/linkang/.igame-auth.json`（`token` + `clientId`）。

## 执行步骤

1. 从用户输入提取：`server`、`cmd`、`args`、是否指定 `playerID`、是否指定环境。
2. 未指定环境时，按约定使用 `dev`。
3. 使用脚本发送请求（脚本会自动拼成 `gmCommand` 文本）：

```powershell
python C:/Users/linkang/.claude/skills/igame-gm-send/scripts/send_gm.py --server "402" --players "123456" --cmd "paddassets" --args "11151001,100000" --env dev
```

4. 返回原始响应给用户，并明确成功/失败。

## 常用示例

```powershell
# 给 123456 加 10 万钻石（dev）
python C:/Users/linkang/.claude/skills/igame-gm-send/scripts/send_gm.py --server "402" --players "123456" --cmd "paddassets" --args "11151001,100000" --env dev

# 执行 multicmd d2（dev）
python C:/Users/linkang/.claude/skills/igame-gm-send/scripts/send_gm.py --server "402" --players "123456" --cmd "multicmd" --args "d2" --env dev

# 全服类 GM（不指定玩家）
python C:/Users/linkang/.claude/skills/igame-gm-send/scripts/send_gm.py --server "402" --cmd "coinpush" --args "setmonsterblood,500" --env dev
```

可选参数：

```powershell
# 自定义 operateType
python C:/Users/linkang/.claude/skills/igame-gm-send/scripts/send_gm.py --server "402" --cmd "multicmd" --args "d2" --operate-type 3

# 自定义 auth 文件（默认 C:/Users/linkang/.igame-auth.json）
python C:/Users/linkang/.claude/skills/igame-gm-send/scripts/send_gm.py --server "402" --cmd "multicmd" --args "d2" --auth-file "D:/tmp/igame-auth.json"
```

## 响应判断

- 成功：返回体 `success=true`。
- 失败常见：
  - `401 请登录`（token 过期）
  - `ark_error_10018 没有权限`（账号权限或网关作用域不对）
  - 参数校验错误（GM 文本格式或参数不合法）

## 注意事项

- 仅适用于 `cmdtype=server/player` 的 GM；`cmdtype=client` 需游戏内手动执行。
- 生产风险指令（删号、清档、重置）必须先让用户确认再执行。
