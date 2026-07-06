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
> - ⚠️**子模块脏时 hook 跳过自动 ff**（2026-06-22 实测）：内嵌 gdconfig 若在某 feature 分支上有未提交改动，pull 主仓时 hook 输出 `[gdconfig] skip auto pull: submodule has uncommitted changes on '<branch>'`，**不会更新子模块**。但这对**本地服部署无影响**——本地服 config 读的是 `client/Assets/Res/Config/ProtoGen/*.bytes`（client 在主仓工作树内，随主仓 pull 一起更新），不读这个内嵌子模块。所以「把某分支部署到本地服」= stash 工作区 WIP → `git pull --ff-only origin <branch>`（带上 client ProtoGen）→ 重编 GameServer.Hotfix+MapServer.Hotfix → stop_gs → 重启，子模块脏不脏无所谓。
> - 🔴**判 X3 配置新不新：看 client ProtoGen `.bytes` 的 robot commit 时间，绝不看 x3-project 记录的 gdconfig 子模块指针**（2026-06-23 实测，差点误判）：x3-project 各分支记录的子模块 SHA（如 `feature/x3-deepsea-art` 和 `origin/dev_festival` 都停在 `dd2941d8`=2026-05-27）是**无人维护的陈旧指针**，与实际部署的配置毫无关系。真实配置 = `client/Assets/Res/Config/ProtoGen/*.bytes`，由 jolt/robot 导表后**独立回写**（commit 尾 `-robot-NNNNN`），跟子模块指针解耦。判新鲜度：`git log -1 --format="%ci %s" <branch> -- client/Assets/Res/Config/ProtoGen/` 看 robot 写入时间；比两分支配置差异 `git diff --stat <A> <B> -- .../ProtoGen/`（差异只在 `i18n/*.bytes`+`AllTableDataMd5.txt`、无 gameplay 表 = 配置表实质一致，只差翻译）。**别拿子模块指针 `dd2941d8` 的日期当"配置停在5/27"——会把今天的配置误判成一个月前的**。

> - 🔴**提交 x3-project 前三条铁律（2026-07-01 实测，一次踩全）**：
>   1. **`git clean` 会删真实源码目录，禁用！** x3-project 有大量**未跟踪但真实的源码目录**（Hero/Card/WeatherSystem/Domain/AVProVideo/Plugins…），`git clean -fd` 会把它们全删=灾难。丢弃噪音**只用 `git restore .`（还原已跟踪的改动），永不 `git clean`**；删任何东西前先 `git clean -nd` 干跑确认。
>   2. **内嵌 gdconfig 脏会拦主仓 commit**：commit 时 hook 报 `[gdconfig] uncommitted gdconfig content changes block x3-project commit; commit/stash/revert inside gdconfig first`。解法=先进 `C:\x3-project\gdconfig` 把改动 commit/stash（若是本功能的 i18n 就在 gdconfig 对应 feature 分支提交）。
>   3. **区分真改 vs CRLF 噪音 + proto 三件套**：mass 改动里很多 `.proto`/`CfgProtos` 是**纯 CRLF 换行噪音**（`git diff <file>` 只有 CRLF 警告、无内容行=噪音可丢）；真功能改动（如 proto 加字段）`git diff` 有 `+/-` 内容行。**改 proto 字段要连带一套提交**：`Config/Proto/X.proto`(源) + `Scripts/.../CfgProtos/X.cs`(生成C#) + `Config/ProtoGen/X.bytes`(编译产物)，三个都带上才一致。
>   4. **merge 冲突多在导表产物+版本文件(2026-07-01 合 dev_festival 实证)**：合分支时冲突文件常是 `client/Assets/Res/Config/ProtoGen/*.bytes`(二进制导表产物)+`ProtoGen/AllTableDataMd5.txt`(校验清单)+`CSShared/Common/Version/VersionControl.cs`(`TABLE_DATA_VERSION`)+`.mcp.json`——**都不是业务代码**。解法：①版本号取**高的**②`.bytes`/`md5`二进制没法手合→**取一侧(手册分支取 ours 保本功能配置)完成合并,push 后 jolt 导表会从 tsv 重新生成 ProtoGen 反映两边完整配置**(导表是这些文件的权威,手合的值只是占位)③`.mcp.json`取内容全的那侧。⚠️完成 merge 提交时**仍会被内嵌 gdconfig 钩子拦**(见上条)——嵌入 gdconfig 常有未跟踪的 `data/*.xlsx`(tsv→xlsx 自动生成残留),`git -C gdconfig clean -fd data/`(dry-run 确认只删生成 xlsx)清掉才能提交 merge。
>   5. **切分支**：无关新任务从**干净基座**建（`git switch -c <new> --no-track origin/dev_festival`，`--no-track` 防误推 dev_festival）；别从功能分支建（会带功能改动污染）。主仓切分支后内嵌 gdconfig 不自动跟随（hook 提示 staying），按需 `git -C gdconfig switch <base>` 手动对齐。

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

## 「拉最新客户端 / 合并两个分叉分支」别本地硬合（2026-06-23 art↔dev_festival 实测血泪）
两个分叉的 x3-project 分支（如 `feature/x3-deepsea-art` ↔ `dev_festival`）**本地 `git merge` 是雷区**：
- **二进制冲突**：生成的 `client/Assets/Res/Config/ProtoGen/i18n/*.bytes`（各分支 robot 导出不一致）+ `VersionControl.cs` 会冲突，二进制 protobuf 没法盲解，解错=客户端配置错乱。
- **LFS 雷**：合并时报 `Encountered N files that should have been pointers, but weren't`（ProtoGen .bytes 被 robot 以原始字节提交、但 .gitattributes 标 LFS）。
- **`git merge --abort` 清不干净**：abort 后工作区残留「被自动合并的 tracked .asset 改动 + 未跟踪的新 png」（pre-merge 明明只有 `M gdconfig`）。**清理只能按显式路径** `git checkout -- <文件>` + `rm <具体未跟踪文件>`；**绝对别在 client/ 跑 `git clean`**——会连 AVProVideo/Domain/WeatherSystem 等**合法的未跟踪 Unity 目录**一起删。
- ✅**正解=让合并发生在远端**（喊大哥/走 MR 在 origin 上把 A 合进 B），本地只做**干净切换**：`git fetch` → 确认 `git rev-list --count origin/B..A == 0`（A 已全进 B）→ `git checkout B && git merge --ff-only origin/B`。ff-only 无冲突、无 LFS 涂抹噩梦。切换后 `M gdconfig` 指针残留是 hook 的正常产物（无害）。
- ⚠️切分支后**本地服(3080)还跑着旧分支的编译** → 客户端配置+服务端代码都变了 → 要 3080 跟上得重编 Hotfix+重启（见 [[workflow_x3_local_server_gm_telnet]] 重启预检：config mtime > dll 必重编）。
