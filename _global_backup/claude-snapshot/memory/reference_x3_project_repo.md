---
name: reference-x3-project-repo
description: X3 服务端/客户端代码仓本地路径、目录结构、GitLab API 访问方式，查 X3 代码逻辑时先读这个
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8c95a774-9d05-4760-9550-0dc41ff62e68
---

## X3 代码仓库

| 项 | 值 |
|----|----|
| Remote | `git@git.tap4fun.com:x3/x3-project.git` (HTTPS: `https://git.tap4fun.com/x3/x3-project.git`) |
| **本地仓库根** | `C:\x3-project\` |
| GitLab 项目 ID | `2859` |
| 默认分支 | `dev`（活跃分支跟 [[reference_x3_gdconfig_repo]] 对齐，如 `dev-summer-love-song`） |
| 仓库大小 | 5.66 GB 代码 + 58 GB LFS（资源），66k+ commits |

> 跟 [[reference_x3_gdconfig_repo]] `C:\x3\gdconfig\` 是**两个独立仓**：gdconfig 装配置 xlsx，x3-project 装代码+资源。
> 但 x3-project 里**内嵌了一份 gdconfig**（`C:\x3-project\gdconfig\`，服务端读配置的来源）：pull/merge 时仓库 hook 会自动把它 fast-forward 到同名分支最新（输出 `[gdconfig] fast-forwarded ...; left superproject pointer unstaged`）。所以 pull 完 x3-project，服务端代码+配置都到位，**本地服重启才生效**；改配置仍只推 `C:\x3\gdconfig\`，内嵌这份别手动改。

> **本机 ffmpeg 在这**：`client/Tools/VideoTools/ffmpeg/ffmpeg.exe`（+ffprobe/ffplay；系统 PATH 没有 ffmpeg，处理视频用它）。配套官方压缩工具 `compress_video.py`（crf28/slower/yuv420p 移动端策略）+ 视频提交合规 hook。

## 顶层结构

```
C:\x3-project\
├── client\         Unity 客户端
├── server\         ← C# 服务端，奖励/活动/补发等业务逻辑都在这
├── Tools\
├── docs\
├── x3-docs\        子模块
└── other\
```

## server\ 子目录

| 目录 | 作用 |
|------|------|
| `GameServer\` + `GameServer.Hotfix\` | **玩家逻辑主战场**——活动、奖励、邮件、付费、英雄、舰船、皮肤、家具、引导都在这里 |
| `CenterServer\` + `CenterServer.Hotfix\` | 跨服活动、跨服排行、跨服准备奖励 |
| `MapServer\` + `MapServer.Hotfix\` | 地图/战斗 |
| `ServerCommon\` | 公共 |
| `Libs\`、`LocalPackages\` | 第三方 / 内部包 |

**`.Hotfix` 是热更代码层**，业务逻辑（含活动补发）大都写在这里而不是非 Hotfix 主项目。查代码时优先 grep `*.Hotfix\`。

## 高频路径

| 用途 | 路径 |
|------|------|
| 活动通用元 | `server\GameServer.Hotfix\PlayerMeta\Activity\ActivityMeta.cs` |
| 活动按类型分文件 | `server\GameServer.Hotfix\PlayerMeta\Activity\ActivityMeta.{WishingPool,...}.cs` |
| 邮件 | `server\GameServer.Hotfix\PlayerMeta\MailMeta.cs` |
| 联盟活动 | `server\GameServer.Hotfix\UnionMeta\Activity\UnionActivityMeta.cs` |
| 跨服活动准备奖励 | `server\CenterServer.Hotfix\CrossServerActivityMeta\CrossServerActivityPrepareMeta.cs` |
| 配置读取的 C 类（如 `CActvOnline.I(id)`）| 由 gdconfig 导表生成，源在 gdconfig，运行时在 server |

## 常用查询模式

```bash
# 查活动补发逻辑（关联 ActvOnline.MailID 列）
Grep "cfg.MailID|MailID == 0|MailID <= 0" --path C:\x3-project\server --glob "*.cs"

# 查某 ActvType 走哪些代码分支
Grep "ActivityConst.TRIGGER_TYPE_XXX" --path C:\x3-project\server

# 查具体 Mail ID 是否在代码里硬编码
Grep "\b101109\b" --path C:\x3-project\server --glob "*.cs"

# 查 CActvOnline 字段使用面（配置→代码的反查链）
Grep "CActvOnline\.I|\.MailID|\.ActvType|\.TimeController" --path C:\x3-project\server
```

## GitLab API 访问

- **PAT 已持久化**为环境变量 `GITLAB_TAP4FUN_TOKEN`（Windows User + `~/.bashrc`，scopes: `read_api`+`read_repository`）
- API base：`https://git.tap4fun.com/api/v4/`
- 项目 API 前缀：`/projects/x3%2Fx3-project/`（或用 ID `2859`）
- GitLab 版本 12.10.14（**禁用 basic auth**，必须用 `PRIVATE-TOKEN` header）

```bash
# 列项目 / 读文件 / 查 commit
curl -H "PRIVATE-TOKEN: $GITLAB_TAP4FUN_TOKEN" "https://git.tap4fun.com/api/v4/projects/2859/repository/branches?per_page=20"
curl -H "PRIVATE-TOKEN: $GITLAB_TAP4FUN_TOKEN" "https://git.tap4fun.com/api/v4/projects/2859/repository/files/server%2FGameServer.Hotfix%2FPlayerMeta%2FActivity%2FActivityMeta.cs/raw?ref=dev"
```

`x3/` 组下只有 2 个项目：`x3/gdconfig` + `x3/x3-project`，没有别的服务端仓。

## 已收录的代码侧规律

- [[feedback_x3_actv_mailid_check]] — `ActivityMeta.cs` 有 4 处 `MailID==0` 守卫静默吞奖励，对应 `ActvOnline.MailID` 漏配

## 提交规范（pre-commit hook）

x3-project 仓 `git commit` 时 pre-commit hook 强制 message 格式：
- `X3NEW-描述` — 新需求/新功能
- `X3-{n} 描述` — 关联已有 jira 单号

**违规会被拒**，包括日常用的 `fix: xxx` / `feat: xxx` / 中文项目名（如 "X3夏日恋语 xxx"）都不行。详见 [[workflow_x3_protected_branch_mr]]。

## dev 受保护

不能直接 `git push origin dev`，必须走 feature branch + MR。MR 创建可用 GitLab API 自动化，详见 [[workflow_x3_protected_branch_mr]]。
