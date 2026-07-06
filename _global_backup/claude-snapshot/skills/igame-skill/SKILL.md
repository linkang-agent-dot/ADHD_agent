---
name: igame-skill
description: 操作 iGame 游戏运营支撑平台，覆盖 32 个模块、1090 个接口。支持服务器导量管理、玩家查询/封号、邮件发送、活动管理、合服、热更、维护挂起、GM 操作等全部运营功能。支持 P2/BA/KOW/X1/X2/X9 全游戏。触发条件：(1) 提到"服务器"、"导量"、"开服"、"停服"、"补量"、"备服"、"合服"、"热更"、"维护"、"审核服"，(2) 提到"玩家"+"封号/解封/查询/订单"，(3) 提到"发邮件"、"GM 操作"、"工具箱"，(4) 提到 P2/X2/X9/KOW/BA + 任意运营操作，(5) 需要查询或操作 iGame 平台任何功能。
---

# iGame Skill

**Skill 路径**: `~/.claude/skills/igame-skill`

认证文件：`~/.igame-auth.json`（Windows: `%USERPROFILE%\.igame-auth.json`）。首次使用或 token 过期（约 10 天）运行：

```bash
bash ./scripts/setup-auth.sh
```

切换游戏：修改认证文件的 `gameId`（P2=1041, X2=1089, X9=1108 等，详见 [references/modules.md](references/modules.md)）。

## 工作流

**Step 1 — 定位接口**

```bash
node ~/.claude/skills/igame-skill/scripts/igame-query.js ls ""                          # 列出 32 个模块
node ~/.claude/skills/igame-skill/scripts/igame-query.js ls "serverMgr"                 # 展开某模块
node ~/.claude/skills/igame-skill/scripts/igame-query.js describe "serverMgr/serverList/getServerList"  # 查参数
```

不确定模块名时先 `ls ""`，再逐级展开。常用接口速查见 [references/modules.md](references/modules.md)。

**Step 2 — 查询**

```powershell
# PowerShell - 使用 ConvertTo-Json 构建参数
$params = @{pageIndex=1; pageSize=20} | ConvertTo-Json -Compress
node ~/.claude/skills/igame-skill/scripts/igame-query.js read "<module/sub/api>" $params
```

**Step 3 — 操作（执行前必须向用户确认）**

```powershell
$params = @{id="2608702"; serverRate=400} | ConvertTo-Json -Compress
node ~/.claude/skills/igame-skill/scripts/igame-query.js write "<module/sub/api>" $params
```

## 示例

```powershell
# 查 P2 导量中的服务器
$params = @{pageIndex=1; pageSize=20; status=5} | ConvertTo-Json -Compress
node ~/.claude/skills/igame-skill/scripts/igame-query.js read "serverMgr/serverList/getServerList" $params

# 改权重（确认后执行）
$params = @{id="2608702"; serverRate=400} | ConvertTo-Json -Compress
node ~/.claude/skills/igame-skill/scripts/igame-query.js write "serverMgr/serverList/setServerRate" $params
```

## 坑位速查

**POST 需要数组 body 的接口**（如 `activity/submit`）：直接把 JSON 数组作为 paramsJson 传入，脚本会原样作为 body 发送，不会被 `buildUrl` 转成 `{"0":{...}}`。

```powershell
# 注意最外层是 '[{...}]' 而不是 '{...}'
$body = '[{"actvType":1,"previewTime":0,"endShowTime":0,"acrossServerRank":1, ...}]'
node ~/.claude/skills/igame-skill/scripts/igame-query.js write "activity/.../submit" $body
```

`activity/submit` 已验证的字段约定：
- `previewTime` / `endShowTime` 用 `0`（不是时间戳）
- `acrossServerRank` = `1`（不是 0）
- 新建活动**不要带 `id` 字段**

若调用报参数结构错误，先确认：CLI 没吞数组外层、body 不是 `{"0":{...}}` 形态。

## 常用接口速查

| 功能 | 接口路径 | 方法 |
|------|----------|------|
| 服务器列表 | serverMgr/serverList/getServerList | GET |
| 设置权重 | serverMgr/serverList/setServerRate | POST |
| 玩家查询 | player/playerInfo/getPlayerInfo | GET |
| 发送邮件 | email/sendEmail/send | POST |
| 活动列表 | activity/activityList/getList | GET |

## X3(1090) 玩家邮件直发（批量补发，不走 UI 上传）

脚本：`scripts/igame_mail_send.py`（等价 UI「发玩家邮件」，POST `/ark/mails/send/players`，prod 网关 webgw-cn，读 `~/.igame-auth.json`）。

```bash
# 从 X3 导入 CSV(GBK 6列,道具列 [ID*数量]) + 多语言内容 构建 payload；缺省 dry-run
python scripts/igame_mail_send.py --csv 补发.csv --content content.json --remark "事由_人数张数_日期"
# content.json = {"ru":{"title":"..","body":".."},"en":{...}}  多语言塞 content 数组即可，不用另导多语言CSV
# 确认无误后加 --send 真发（生产操作，先经用户确认）
python scripts/igame_mail_send.py --status <mailId>   # 2=待审(须人到iGame后台放行) 1=已发送 3=驳回/撤回(终态不会再发,别当派发中傻等;workflow流水: 8提交→7审批通过(须他人)→0发送中→1已发送)
python scripts/igame_mail_send.py --outbox 5          # 发件箱最近5单
```

铁律：①网关 success 只是登记，提交后 status=2 卡审批，**必须有人在 iGame 后台放行**；②判真发出看 `--status` 的 sentAt/to[].failReason；③最终以数仓入账收口；④建议先发 1 人金丝雀单核格式再发全量。字段/坑详见 memory `reference_x3_igame_mail_import.md`。首例实战：20260703 世界杯奖券回收补发（`KB\产出-补发邮件\X3\20260703_世界杯奖券回收补发\`）。
